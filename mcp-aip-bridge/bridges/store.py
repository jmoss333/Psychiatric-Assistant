
"""Transaction log + deterministic threading."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import NAMESPACE_URL, uuid5

try:
    import asyncpg  # type: ignore
except ImportError:  # pragma: no cover
    asyncpg = None  # type: ignore


class TxStatus(Enum):
    QUEUED = "queued"
    SENT = "sent"
    ACKED = "acked"
    ERROR = "error"


class BridgeStore:
    def __init__(self, db_url: str) -> None:
        self.db_url = db_url
        self.pool: Optional[Any] = None
        self._in_memory = False
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._id_counter = 0
        self._lock = asyncio.Lock()

    async def init(self) -> None:
        if self.db_url.startswith("memory://") or asyncpg is None:
            self._in_memory = True
            return
        try:
            self.pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=5)  # type: ignore[attr-defined]
            await self._create_tables()
        except Exception:
            self._in_memory = True
            self.pool = None

    async def _create_tables(self) -> None:
        if self._in_memory or not self.pool or asyncpg is None:
            return
        async with self.pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bridge_tx (
                    id SERIAL PRIMARY KEY,
                    mcp_id TEXT UNIQUE NOT NULL,
                    thread_id TEXT NOT NULL,
                    aip_msg_id TEXT,
                    status TEXT NOT NULL,
                    method TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    error_detail TEXT,
                    retry_count INT DEFAULT 0,
                    response_json JSONB
                );
                CREATE INDEX IF NOT EXISTS idx_bridge_tx_status ON bridge_tx(status);
                CREATE INDEX IF NOT EXISTS idx_bridge_tx_thread ON bridge_tx(thread_id);
                """
            )

    def thread_for(self, method: str, mcp_id: str) -> str:
        return str(uuid5(NAMESPACE_URL, f"mcp:{method}:{mcp_id}"))

    async def upsert_bridge_tx(
        self,
        *,
        mcp_id: str,
        thread_id: str,
        method: str,
        status: TxStatus,
    ) -> Dict[str, Any]:
        if self._in_memory or not self.pool or asyncpg is None:
            async with self._lock:
                existing = self._memory_store.get(mcp_id)
                if existing:
                    existing["status"] = status.value
                    existing["retry_count"] += 1
                    existing["updated_at"] = datetime.now(timezone.utc)
                    return existing
                self._id_counter += 1
                record = {
                    "id": self._id_counter,
                    "mcp_id": mcp_id,
                    "thread_id": thread_id,
                    "aip_msg_id": None,
                    "status": status.value,
                    "method": method,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "error_detail": None,
                    "retry_count": 0,
                    "response_json": None,
                }
                self._memory_store[mcp_id] = record
                return record

        async with self.pool.acquire() as conn:  # type: ignore[union-attr]
            row = await conn.fetchrow(
                """
                INSERT INTO bridge_tx (mcp_id, thread_id, method, status)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (mcp_id)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    updated_at = NOW(),
                    retry_count = bridge_tx.retry_count + 1
                RETURNING *
                """,
                mcp_id,
                thread_id,
                method,
                status.value,
            )
            return dict(row)

    async def update_bridge_tx(
        self,
        *,
        tx_id: int,
        status: TxStatus,
        aip_msg_id: Optional[str] = None,
        error_detail: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self._in_memory or not self.pool or asyncpg is None:
            async with self._lock:
                for record in self._memory_store.values():
                    if record["id"] == tx_id:
                        record["status"] = status.value
                        record["updated_at"] = datetime.now(timezone.utc)
                        if aip_msg_id:
                            record["aip_msg_id"] = aip_msg_id
                        record["error_detail"] = error_detail
                        if response is not None:
                            record["response_json"] = response
                        return
                raise KeyError(f"Transaction {tx_id} not found")

        async with self.pool.acquire() as conn:  # type: ignore[union-attr]
            await conn.execute(
                """
                UPDATE bridge_tx
                   SET status = $1,
                       aip_msg_id = COALESCE($2, aip_msg_id),
                       response_json = COALESCE($3, response_json),
                       error_detail = $4,
                       updated_at = NOW()
                 WHERE id = $5
                """,
                status.value,
                aip_msg_id,
                response,
                error_detail,
                tx_id,
            )

    async def check_duplicate(self, mcp_id: str) -> Optional[Dict[str, Any]]:
        if self._in_memory or not self.pool or asyncpg is None:
            async with self._lock:
                record = self._memory_store.get(mcp_id)
                if record and record["status"] == TxStatus.ACKED.value:
                    return record
                return None

        async with self.pool.acquire() as conn:  # type: ignore[union-attr]
            row = await conn.fetchrow(
                "SELECT * FROM bridge_tx WHERE mcp_id = $1 AND status = $2",
                mcp_id,
                TxStatus.ACKED.value,
            )
            return dict(row) if row else None
