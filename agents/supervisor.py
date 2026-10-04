from langchain.agents import create_agent
from schemas.supervisor import SupervisorDecision
from llm import LLM
llm=LLM()


def create_supervisor_agent(model):


    supervisor_agent = create_agent(
        model=model.model,
        tools=[],
        system_prompt="""
你是旅行规划项目的 Supervisor。

你负责协调：

research
planner
writer

根据当前状态决定下一步。

规则：

1. 没有 research_result → research
2. 有 research_result，没有 plan_result → planner
3. 有 plan_result，没有 final_result → writer
4. 有 final_result → FINISH
"""
    )
    return supervisor_agent