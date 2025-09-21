import asyncio

import pytest

from bridges.core import MCPAIPBridge
from bridges.store import BridgeStore, TxStatus


@pytest.mark.asyncio
async def test_duplicate_request_handling():
    """Ensure duplicate MCP requests are handled idempotently."""

    store = BridgeStore("postgresql://test@localhost/test")
    await store.init()

    bridge = MCPAIPBridge(store=store)

    mcp_req = {
        "jsonrpc": "2.0",
        "method": "tools/github/create_pr",
        "params": {"title": "Test PR"},
        "id": "dup-test-001",
    }

    result1 = await bridge.handle_mcp_request(mcp_req)
    assert result1["id"] == "dup-test-001"

    result2 = await bridge.handle_mcp_request(mcp_req)
    assert result2 == result1

    tx = await store.check_duplicate("dup-test-001")
    assert tx is not None
    assert tx["status"] == TxStatus.ACKED.value
    assert tx["retry_count"] == 0
