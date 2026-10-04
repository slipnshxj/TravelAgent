import anyio

from the_mcp.runtime import MCPRuntime
from the_mcp.registry import MCPToolRegistry


async def main():

    async with MCPRuntime() as runtime:

        registry = MCPToolRegistry(
            runtime
        )

        tools = await registry.initialize()

        print(
            "========== MCP Tool Registry =========="
        )

        for tool in tools:

            print(f"\n名称: {tool.name}")
            print(
                f"描述: {tool.description}"
            )
            print(
                "Schema:"
            )
            print(
                tool.args_schema.model_json_schema()
            )

        weather_tool = next(
            tool
            for tool in tools
            if tool.name == "mcp_weather"
        )

        print(
            "\n========== Async Tool Call =========="
        )

        result = await weather_tool.ainvoke(
            {
                "city": "东京"
            }
        )

        print(result)


if __name__ == "__main__":
    anyio.run(main)