from graph.state import TravelState

ALLOWED_DECISIONS={
    "research",
    "planner",
    "writer",
    "FINISH"
}

def normalize_decision(decision:str)->str:
    """
    清洗并验证Supervisor的原始输出
    """
    decision=decision.strip().lower()
    if decision == "finish":
        return "FINISH"

    if decision in{
        "research",
        "planner",
        "writer"
    }:
        return decision

    raise ValueError(
        f"Supervisor 返回了非法决策: {decision}"
    )

def validate_decision(state:TravelState,decision:str)->str:
    """
    检查 Supervisor 当前的决策
    是否符合当前系统状态。
    """

    if decision == "planner" and not state["research_result"]:
        return "research"

    if decision == "writer" and not state["plan_result"]:
        return "planner"

    if decision == "FINISH" and not state["final_result"]:
        return "writer"

    return decision

