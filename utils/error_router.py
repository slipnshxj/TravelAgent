from graph.state import TravelState

def route_after_agent(state:TravelState)->str:
    """
    根据 Agent 执行结果决定下一步。
    """
    if state.get("error"):
        print(
            f"[Error Router] 检测到错误："
            f"{state['error']}"
        )
        if state["step_count"]>=8:
            print("[Error Router] 错误次数过多，直接生成兜底答案")
            return "writer"

        print("[Error Router] 返回 Supervisor 重新决策")
        return "supervisor"

    if not state.get("research_result"):
        return "research"
    if not state.get("plan_result"):
        return "planner"
    if not state.get("final_result"):
        return "writer"
    return "FINISH"
