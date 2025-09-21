"""Core orchestration for the MCP ⇄ AIP bridge."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from .translator import ProtocolTranslator
from .store import BridgeStore, TxStatus
from .crypto import sign_message
from .security import SecurityGateway, SecurityError


class MCPAIPBridge:
    """Main bridge coordinator."""

    def __init__(
        self,
        store: BridgeStore,
        *,
        translator: Optional[ProtocolTranslator] = None,
        security: Optional[SecurityGateway] = None,
        signer_privkey_b64: Optional[str] = None,
    ) -> None:
        self.store = store
        self.translator = translator or ProtocolTranslator()
        self.security = security
        self.signer_privkey_b64 = signer_privkey_b64
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

            tx = await self.store.upsert_bridge_tx(
                mcp_id=mcp_id,
                thread_id=thread_id,
                method=method,
                status=TxStatus.QUEUED,
            )

            if self.security:
                await self._run_preflight(method, params)

            translation = await self.translator.mcp_to_uir(method, params)

            response = {
                "id": mcp_id,
                "thread_id": thread_id,
                "success": translation.success,
                "uir": translation.uir,
                "data": translation.data,
            }
            if translation.error:
                response["error"] = translation.error

            if self.signer_privkey_b64:
                response = sign_message(self.signer_privkey_b64, response)

            await self.store.update_bridge_tx(
                tx_id=tx["id"],
                status=TxStatus.ACKED,
                aip_msg_id=response.get("id"),
            )

            self._response_cache[mcp_id] = response
            return response

    async def _lookup_cached_response(self, mcp_id: str) -> Optional[Dict[str, Any]]:
        duplicate = await self.store.check_duplicate(mcp_id)
        if duplicate and mcp_id in self._response_cache:
            return self._response_cache[mcp_id]
        return None

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
