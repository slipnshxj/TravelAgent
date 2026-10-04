import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from the_mcp.langchain_tools import load_mcp_tools


tools = load_mcp_tools()

print("========== Dynamic MCP Tool Schema ==========")

for tool in tools:
    print(f"\n名称: {tool.name}")
    print(f"描述: {tool.description}")
    print("参数 Schema:")
    print(tool.args_schema.model_json_schema())