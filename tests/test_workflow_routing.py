from graph.workflow import route_after_agent


def test_route_after_research() -> None:
    assert route_after_agent({"research_result": "result", "step_count": 1}) == "planner"


def test_route_after_planner() -> None:
    assert route_after_agent({
        "research_result": "result",
        "plan_result": "plan",
        "step_count": 2,
    }) == "writer"


def test_route_after_writer() -> None:
    assert route_after_agent({
        "research_result": "result",
        "plan_result": "plan",
        "final_result": "final",
        "step_count": 3,
    }) == "FINISH"


def test_error_routes_to_supervisor_before_retry_limit() -> None:
    assert route_after_agent({
        "error": "temporary error",
        "step_count": 2,
    }) == "supervisor"
