from langchain.agents import create_agent
# from the_mcp.langchain_tools import load_mcp_tools
from llm import LLM

llm=LLM()

def create_research_agent(model,tools = None):
    if tools is None:
        tools=[]
    research_agent=create_agent(
        model=model,
        tools=tools,
        system_prompt="""
你是一名旅行研究专家。

你的任务是：
1. 分析用户的旅行需求
2. 搜索相关旅游信息
3. 收集景点、交通、美食等信息
4. 整理成结构化的研究结果

你拥有以下工具：

1. mcp_weather
   通过 MCP 协议查询城市天气。

2. mcp_attractions
   通过 MCP 协议查询城市旅游景点。

3. mcp_budget
   通过 MCP 协议计算旅行预算。

4. mcp_hotel
   通过 MCP 协议查询城市酒店。

需要查询外部信息时，自主决定是否调用搜索工具。
调用工具时必须使用真正的工具调用机制，不要把工具调用语法写在正文中。
"""
    )
    return research_agent
