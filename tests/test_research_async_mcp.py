import anyio

from llm import LLM
from agents.research_agent import create_research_agent
from the_mcp.runtime import MCPRuntime
from the_mcp.registry import MCPToolRegistry


async def main():

    model = LLM()

    async with MCPRuntime() as runtime:

        registry = MCPToolRegistry(runtime)

        tools = await registry.initialize()

        research_agent = create_research_agent(
            model.model,
            tools=tools,
        )

        print(
            "========== Async Research Agent =========="
        )

        result = await research_agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "查询东京的天气和旅游景点，"
                            "并说明适合怎样安排。"
                        ),
                    }
                ]
            }
        )

        print("\n========== Research Result ==========")

        print(
            result["messages"][-1].content
        )


if __name__ == "__main__":
    anyio.run(main)