import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from the_mcp.langchain_tools import (
    mcp_weather,
    mcp_attractions,
    mcp_budget,
)


print("========== Weather ==========")
print(
    mcp_weather.invoke({
        "city": "东京"
    })
)

print("\n========== Attractions ==========")
print(
    mcp_attractions.invoke({
        "city": "东京"
    })
)

print("\n========== Budget ==========")
print(
    mcp_budget.invoke({
        "days": 3,
        "daily_budget": 500,
    })
)