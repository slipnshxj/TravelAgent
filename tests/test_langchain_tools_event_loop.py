import anyio

from the_mcp import langchain_tools


def test_load_mcp_tools_inside_running_event_loop(monkeypatch) -> None:
    async def fake_load_mcp_tools():
        return ["weather"]

    monkeypatch.setattr(
        langchain_tools,
        "_load_mcp_tools",
        fake_load_mcp_tools,
    )

    async def run_test():
        return langchain_tools.load_mcp_tools()

    assert anyio.run(run_test) == ["weather"]
