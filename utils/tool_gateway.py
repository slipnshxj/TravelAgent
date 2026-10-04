from the_mcp.runtime import MCPRuntime


def _normalize_content(content) -> str:
    if isinstance(content, list):
        return "\n".join(
            getattr(item, "text", str(item)) for item in content
        )
    return str(content)


async def list_tools() -> list[dict]:
    async with MCPRuntime() as runtime:
        tools = await runtime.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "inputSchema": tool.input_schema,
            }
            for tool in tools
        ]


async def invoke_tool(tool_name: str, arguments: dict) -> dict:
    async with MCPRuntime() as runtime:
        result = await runtime.call_tool(tool_name, arguments)
        return {
            "content": _normalize_content(result.content),
            "isError": bool(getattr(result, "isError", False)),
        }
