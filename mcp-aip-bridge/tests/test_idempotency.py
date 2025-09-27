import pytest

from bridges.core import MCPAIPBridge
from bridges.memory import MemorySync
from bridges.store import BridgeStore, TxStatus


@pytest.mark.asyncio
async def test_duplicate_request_handling():
    """Ensure duplicate MCP requests are handled idempotently."""

    store = BridgeStore("memory://idempotency")
    await store.init()

    bridge = MCPAIPBridge(store=store, memory=MemorySync())

    mcp_req = {
        "jsonrpc": "2.0",
        "method": "tools/github/create_pr",
        "params": {"title": "Test PR"},
        "id": "dup-test-001",
    }

    result1 = await bridge.handle_mcp_request(mcp_req)
    assert result1["request_id"] == "dup-test-001"
    assert result1["content"]["schema"] == "mcp.tools/github/create_pr.v0"

    result2 = await bridge.handle_mcp_request(mcp_req)
    assert result2 == result1

    tx = await store.check_duplicate("dup-test-001")
    assert tx is not None
    assert tx["status"] == TxStatus.ACKED.value
    assert tx["retry_count"] == 0
    assert tx["response_json"]["msg_id"] == result1["msg_id"]
