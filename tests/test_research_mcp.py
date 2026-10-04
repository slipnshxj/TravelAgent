import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.research_agent import create_research_agent


agent = create_research_agent(None)


result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "查询东京的天气和旅游景点，优先使用 MCP 工具。"
        }
    ]
})


print("\n========== Research Agent Result ==========")
print(result)