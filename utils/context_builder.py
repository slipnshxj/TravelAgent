from graph.state import TravelState
from utils.memory_context import build_memory_context



def builder_supervisor_context(state:TravelState,memory_context:str):
    return f"""
你是旅行规划项目的 Supervisor，负责决定下一步执行哪个Agent。

用户历史偏好：

{memory_context} 

用户当前需求：

{state["user_query"]}

Research Agent 的结果：

{state.get("research_result","")}

用户历史长期记忆：

{memory_context}

Planner Agent 的结果：

{state.get("plan_result")}

Writer Agent 的结果：

{state.get("final_result")}

当前错误：

{state.get("error","")}

请判断下一步应该执行哪个 Agent。

只能返回：

research
planner
writer
FINISH

不要解释。
"""


def builder_research_context(state):
    return f"""
用户需求：

{state["user_query"]}

注意事项：

禁止自己虚构预算，可以提供假设并且标明
"""



def builder_planner_context(state):
    return f"""
    用户需求：

    {state["user_query"]}

    Research Agent 的研究结果：

    {state["research_result"]}
    """



def builder_writer_context(state):
    return f"""
    用户需求：

    {state["user_query"]}

    Research Agent 的研究结果：

    {state["research_result"]}

    Planner Agent 的旅行计划：

    {state["plan_result"]}
    """

