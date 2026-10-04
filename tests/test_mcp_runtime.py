import anyio

from the_mcp.runtime import MCPRuntime


async def main():

    async with MCPRuntime() as runtime:

        print("========== MCP Runtime ==========")

        tools = await runtime.list_tools()

        for tool in tools:
            print(
                f"{tool.name}: "
                f"{tool.description}"
            )

        print("\n========== Call Weather ==========")

        result = await runtime.call_tool(
            "weather",
            {
                "city": "东京"
            },
        )

        print(result.content)

        print("\n========== Call Attractions ==========")

        result = await runtime.call_tool(
            "attractions",
            {
                "city": "东京"
            },
        )

        print(result.content)


if __name__ == "__main__":
    anyio.run(main)