"""Preflight policy integration."""
from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict

import httpx


class SecurityError(RuntimeError):
    """Raised when a security gateway denies a request."""


class PolicyDecision(Enum):
    ALLOW = "allow"
    REDACT = "redact"
    DENY = "deny"


class SecurityGateway:
    def __init__(self, gateway_url: str, timeout: int = 5) -> None:
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=timeout)

    async def preflight_check(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        params_meta = {
            "size": len(json.dumps(params)),
            "keys": list(params.keys()),
            "has_binary": any(isinstance(v, (bytes, bytearray)) for v in params.values()),
        }

        phi_score = await self._quick_phi_score(params)

        response = await self.client.post(
            f"{self.gateway_url}/v0/trust/preflight",
            json={
                "method": method,
                "params_meta": params_meta,
                "phi_score": phi_score,
                "context": {"source": "mcp-bridge", "tenant": "default"},
            },
        )
        result = response.json()

        if result.get("decision") == PolicyDecision.DENY.value:
            raise SecurityError(f"Policy denied: {result.get('reason')}")

        return result

    async def _quick_phi_score(self, params: Dict[str, Any]) -> float:
        text = json.dumps(params).lower()
        phi_indicators = ["ssn", "dob", "mrn", "patient", "diagnosis"]
        score = sum(1 for ind in phi_indicators if ind in text) / len(phi_indicators)
        return min(score * 2, 1.0)

    async def aclose(self) -> None:
        await self.client.aclose()
