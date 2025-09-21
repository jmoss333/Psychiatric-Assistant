import pytest

from bridges.security import PolicyDecision, SecurityError, SecurityGateway


class _MockResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class _MockClient:
    def __init__(self, payload):
        self._payload = payload
        self.calls = []

    async def post(self, url, json):
        self.calls.append((url, json))
        return _MockResponse(self._payload)

    async def aclose(self):
        return None


@pytest.mark.asyncio
async def test_preflight_allow_flow(monkeypatch):
    gateway = SecurityGateway("http://gateway")
    mock_client = _MockClient({"decision": PolicyDecision.ALLOW.value})
    monkeypatch.setattr(gateway, "client", mock_client)

    result = await gateway.preflight_check("tools/http/fetch", {"url": "http://example"})
    assert result["decision"] == PolicyDecision.ALLOW.value
    await gateway.aclose()


@pytest.mark.asyncio
async def test_preflight_denied(monkeypatch):
    gateway = SecurityGateway("http://gateway")
    mock_client = _MockClient({"decision": PolicyDecision.DENY.value, "reason": "blocked"})
    monkeypatch.setattr(gateway, "client", mock_client)

    with pytest.raises(SecurityError):
        await gateway.preflight_check("tools/http/fetch", {"url": "http://example"})
    await gateway.aclose()


@pytest.mark.asyncio
async def test_phi_score_detection():
    gateway = SecurityGateway("http://gateway")
    score = await gateway._quick_phi_score({"note": "Patient DOB: 01/01/2020"})
    assert score > 0
    await gateway.aclose()
