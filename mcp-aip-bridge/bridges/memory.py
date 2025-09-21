"""Memory synchronization helpers."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional


class MemorySync:
    """In-memory synchronization façade used by the bridge."""

    def __init__(self, *, ttl: int = 3600) -> None:
        self.ttl = ttl
        self._lock = asyncio.Lock()
        self._store: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._store.get(key)

    async def set(self, key: str, value: Dict[str, Any]) -> None:
        async with self._lock:
            self._store[key] = value

    async def purge(self) -> None:
        async with self._lock:
            self._store.clear()
