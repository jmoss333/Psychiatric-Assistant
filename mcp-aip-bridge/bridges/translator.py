"""Enhanced protocol translation with UIR converters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TranslationResult:
    """Structured outcome of translating an MCP request."""

    success: bool
    schema: str
    body: Dict[str, Any]
    uir: Optional[str] = None
    uir_data: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
    safety_tags: Optional[List[str]] = None
    error: Optional[str] = None


class ProtocolTranslator:
    """Translate MCP tool invocations into AIP-friendly payloads."""

    def __init__(self, *, schema_mappings: Optional[Dict[str, str]] = None) -> None:
        self.schema_mappings = schema_mappings or {
            "tools/filesystem/read": "mcp.tools/filesystem/read.v0",
            "tools/github/create_pr": "mcp.tools/github/create_pr.v0",
            "tools/postgres/query": "mcp.tools/postgres/query.v0",
            "tools/http/fetch": "mcp.tools/http/fetch.v0",
        }
        self.uir_converters = {
            "tools/filesystem/read": self._fs_read_to_evidence,
            "tools/github/create_pr": self._github_pr_to_plan,
            "tools/postgres/query": self._db_query_to_evidence,
            "tools/http/fetch": self._http_to_evidence,
        }

    async def mcp_to_uir(self, method: str, params: Dict[str, Any]) -> TranslationResult:
        """Convert an MCP method call into a UIR-friendly payload."""

        converter = self.uir_converters.get(method)
        if converter:
            return await converter(params)

        return TranslationResult(
            success=True,
            schema=self.schema_mappings.get(method, self._default_schema(method)),
            body=params,
            uir="generic.v0",
            confidence=0.5,
            safety_tags=["mcp:translated"],
        )

    async def _fs_read_to_evidence(self, params: Dict[str, Any]) -> TranslationResult:
        """Filesystem read → evidence.v0."""

        path = params.get("path", "")
        return TranslationResult(
            success=True,
            schema=self.schema_mappings["tools/filesystem/read"],
            body={"path": path},
            uir="evidence.v0",
            uir_data={
                "items": [
                    {
                        "type": "blob",
                        "uri": f"file://{path}" if path else None,
                        "content": params.get("content"),
                        "confidence": 1.0,
                    }
                ]
            },
            confidence=0.95,
            safety_tags=["mcp:translated"],
        )

    async def _github_pr_to_plan(self, params: Dict[str, Any]) -> TranslationResult:
        """GitHub PR creation → plan.v0."""

        return TranslationResult(
            success=True,
            schema=self.schema_mappings["tools/github/create_pr"],
            body={
                "title": params.get("title"),
                "body": params.get("body"),
                "branch": params.get("branch"),
                "base": params.get("base", "main"),
            },
            uir="plan.v0",
            uir_data={
                "steps": [
                    {
                        "id": "validate-branch",
                        "agent": "git.validator",
                        "inputs": {"branch": params.get("branch")},
                        "constraints": ["must_exist:true"],
                    },
                    {
                        "id": "create-pr",
                        "agent": "github.pr",
                        "inputs": {
                            "title": params.get("title"),
                            "body": params.get("body"),
                            "base": params.get("base", "main"),
                            "head": params.get("branch"),
                        },
                        "outs": ["pr.url", "pr.number"],
                    },
                ]
            },
            confidence=0.9,
            safety_tags=["mcp:translated", "plan:generated"],
        )

    async def _db_query_to_evidence(self, params: Dict[str, Any]) -> TranslationResult:
        """Database query → evidence.v0."""

        return TranslationResult(
            success=True,
            schema=self.schema_mappings["tools/postgres/query"],
            body={
                "query": params.get("query"),
                "params": params.get("params"),
            },
            uir="evidence.v0",
            uir_data={
                "items": [
                    {
                        "type": "table",
                        "rows": params.get("rows", []),
                        "columns": params.get("columns", []),
                        "confidence": 0.9,
                    }
                ]
            },
            confidence=0.9,
            safety_tags=["mcp:translated"],
        )

    async def _http_to_evidence(self, params: Dict[str, Any]) -> TranslationResult:
        """HTTP fetch → evidence.v0."""

        response = params.get("response", {})
        return TranslationResult(
            success=True,
            schema=self.schema_mappings["tools/http/fetch"],
            body={
                "url": params.get("url"),
                "method": params.get("method", "GET"),
            },
            uir="evidence.v0",
            uir_data={
                "items": [
                    {
                        "type": "citation",
                        "source": params.get("url"),
                        "content": response.get("body", ""),
                        "source_meta": {
                            "status": response.get("status"),
                            "headers": response.get("headers", {}),
                        },
                        "confidence": 0.95,
                    }
                ]
            },
            confidence=0.9,
            safety_tags=["mcp:translated"],
        )

    def _default_schema(self, method: str) -> str:
        sanitized = method.replace("/", ".")
        if not sanitized.startswith("mcp."):
            sanitized = f"mcp.{sanitized}"
        if not sanitized.endswith(".v0"):
            sanitized = f"{sanitized}.v0"
        return sanitized
