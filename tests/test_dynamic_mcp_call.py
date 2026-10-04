import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from the_mcp.langchain_tools import load_mcp_tools


tools = load_mcp_tools()

print("========== Dynamic MCP Tool Call ==========")

for tool in tools:
    print(f"{tool.name} -> {tool.args_schema.model_json_schema()}")


weather_tool = next(
    tool for tool in tools
    if tool.name == "mcp_weather"
)

attractions_tool = next(
    tool for tool in tools
    if tool.name == "mcp_attractions"
)

budget_tool = next(
    tool for tool in tools
    if tool.name == "mcp_budget"
)


print("\n========== Weather ==========")
print(
    weather_tool.invoke(
        {
            "city": "东京"
        }
    )
)


print("\n========== Attractions ==========")
print(
    attractions_tool.invoke(
        {
            "city": "东京"
        }
    )
)


print("\n========== Budget ==========")
print(
    budget_tool.invoke(
        {
            "days": 3,
            "daily_budget": 500,
        }
    )
)