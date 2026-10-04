from langchain.agents import create_agent

from llm import LLM

llm=LLM()

def create_planner_agent(model):
    planner_agent=create_agent(
        model=llm.model,
        tools=[],
        system_prompt="""
你是一名旅行规划专家。

你的任务是根据：
1. 用户需求
2. Research Agent 提供的信息

制定合理的旅行计划。

需要进行计算时，可以使用你拥有的工具。

输出清晰的每日行程安排。
"""
    )
    return planner_agent