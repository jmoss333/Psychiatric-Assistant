import pytest

from bridges.translator import ProtocolTranslator


@pytest.mark.asyncio
async def test_filesystem_translation_to_uir():
    translator = ProtocolTranslator()
    params = {"path": "/tmp/example.txt", "content": "hello"}

    result = await translator.mcp_to_uir("tools/filesystem/read", params)

    assert result.success is True
    assert result.uir == "evidence.v0"
    assert result.data["items"][0]["uri"] == "file:///tmp/example.txt"


@pytest.mark.asyncio
async def test_unknown_method_uses_generic_translator():
    translator = ProtocolTranslator()
    params = {"foo": "bar"}

    result = await translator.mcp_to_uir("tools/custom", params)

    assert result.uir == "generic.v0"
    assert result.data == params
