"""Enhanced protocol translation with UIR converters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class TranslationResult:
    success: bool
    data: Dict[str, Any]
    uir: Optional[str] = None
    error: Optional[str] = None


class ProtocolTranslator:
    def __init__(self) -> None:
        self.uir_converters = {
            "tools/filesystem/read": self._fs_read_to_evidence,
            "tools/github/create_pr": self._github_pr_to_plan,
            "tools/postgres/query": self._db_query_to_evidence,
            "tools/http/fetch": self._http_to_evidence,
        }

    async def mcp_to_uir(self, method: str, params: Dict[str, Any]) -> TranslationResult:
        """Convert MCP tool call to UIR format."""

        converter = self.uir_converters.get(method)
        if converter:
            return await converter(params)

        return TranslationResult(success=True, data=params, uir="generic.v0")

    async def _fs_read_to_evidence(self, params: Dict[str, Any]) -> TranslationResult:
        return TranslationResult(
            success=True,
            uir="evidence.v0",
            data={
                "items": [
                    {
                        "type": "blob",
                        "uri": f"file://{params.get('path')}",
                        "content": params.get("content", ""),
                        "confidence": 1.0,
                    }
                ]
            },
        )

    async def _github_pr_to_plan(self, params: Dict[str, Any]) -> TranslationResult:
        return TranslationResult(
            success=True,
            uir="plan.v0",
            data={
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
        )

    async def _db_query_to_evidence(self, params: Dict[str, Any]) -> TranslationResult:
        return TranslationResult(
            success=True,
            uir="evidence.v0",
            data={
                "items": [
                    {
                        "type": "table",
                        "rows": params.get("rows", []),
                        "columns": params.get("columns", []),
                        "confidence": 0.9,
                    }
                ]
            },
        )

    async def _http_to_evidence(self, params: Dict[str, Any]) -> TranslationResult:
        response = params.get("response", {})
        return TranslationResult(
            success=True,
            uir="evidence.v0",
            data={
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
        )
