"""Core orchestration for the MCP ⇄ AIP bridge."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, Optional
from uuid import uuid4

from .crypto import sign_message
from .memory import MemorySync
from .metrics import MetricsExporter
from .security import SecurityError, SecurityGateway
from .store import BridgeStore, TxStatus
from .translator import ProtocolTranslator, TranslationResult


class MCPAIPBridge:
    """Main bridge coordinator."""

    def __init__(
        self,
        store: BridgeStore,
        *,
        translator: Optional[ProtocolTranslator] = None,
        security: Optional[SecurityGateway] = None,
        signer_privkey_b64: Optional[str] = None,
        memory: Optional[MemorySync] = None,
        metrics: Optional[MetricsExporter] = None,
        aip_version: str = "0.1",
    ) -> None:
        self.store = store
        self.translator = translator or ProtocolTranslator()
        self.security = security
        self.signer_privkey_b64 = signer_privkey_b64
        self.memory = memory
        self.metrics = metrics
        self.aip_version = aip_version

        self._response_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming MCP request and return an AIP-style response."""

        mcp_id = request.get("id")
        if not mcp_id:
            raise ValueError("MCP request missing 'id'")

        async with self._lock:
            cached = await self._lookup_cached_response(mcp_id)
            if cached is not None:
                return cached

            method = request.get("method", "")
            params = request.get("params", {})
            thread_id = self.store.thread_for(method, mcp_id)

            if self.security:
                await self._run_preflight(method, params)

            tx = await self.store.upsert_bridge_tx(
                mcp_id=mcp_id,
                thread_id=thread_id,
                method=method,
                status=TxStatus.QUEUED,
            )

            translation, _ = await self._translate(method, params)

            response = self._build_response(
                mcp_id=mcp_id,
                thread_id=thread_id,
                translation=translation,
            )

            status = TxStatus.ACKED if translation.success else TxStatus.ERROR
            await self.store.update_bridge_tx(
                tx_id=tx["id"],
                status=status,
                aip_msg_id=response.get("msg_id"),
                response=response,
                error_detail=translation.error,
            )

            await self._store_response(mcp_id, response)

            if translation.success:
                return response
            raise RuntimeError(translation.error or "Translation failed")

    async def _translate(self, method: str, params: Dict[str, Any]) -> tuple[TranslationResult, float]:
        start = perf_counter()
        translation = await self.translator.mcp_to_uir(method, params)
        latency = perf_counter() - start
        if self.metrics:
            self.metrics.record_translation(method, translation.success, latency)
        return translation, latency

    def _build_response(
        self,
        *,
        mcp_id: str,
        thread_id: str,
        translation: TranslationResult,
    ) -> Dict[str, Any]:
        msg_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        content: Dict[str, Any] = {
            "schema": translation.schema,
            "body": translation.body,
        }
        if translation.uir:
            content["uir"] = translation.uir
        if translation.uir_data:
            content["uir_data"] = translation.uir_data

        response: Dict[str, Any] = {
            "msg_id": msg_id,
            "thread_id": thread_id,
            "ts": timestamp,
            "aip_version": self.aip_version,
            "type": "TASK",
            "request_id": mcp_id,
            "content": content,
            "trust": {
                "confidence": translation.confidence,
                "safety_tags": translation.safety_tags or ["mcp:translated"],
            },
        }

        if translation.error:
            response.setdefault("error", translation.error)

        if self.signer_privkey_b64:
            response = sign_message(self.signer_privkey_b64, response)

        return response

    async def _lookup_cached_response(self, mcp_id: str) -> Optional[Dict[str, Any]]:
        if self.memory:
            cached = await self.memory.get(mcp_id)
            if cached is not None:
                return cached

        if cached_local := self._response_cache.get(mcp_id):
            return cached_local

        duplicate = await self.store.check_duplicate(mcp_id)
        if duplicate:
            cached_response = duplicate.get("response_json")
            if cached_response:
                await self._store_response(mcp_id, cached_response)
                return cached_response
        return None

    async def _store_response(self, mcp_id: str, response: Dict[str, Any]) -> None:
        if self.memory:
            await self.memory.set(mcp_id, response)
        else:
            self._response_cache[mcp_id] = response

    async def _run_preflight(self, method: str, params: Dict[str, Any]) -> None:
        if not self.security:
            return
        try:
            await self.security.preflight_check(method, params)
        except SecurityError:
            raise

    async def close(self) -> None:
        if self.security and hasattr(self.security, "aclose"):
            await self.security.aclose()
