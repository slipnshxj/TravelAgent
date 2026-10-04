from utils.supervisor_validator import normalize_decision, validate_decision


def make_state(**overrides):
    state = {
        "research_result": "",
        "plan_result": "",
        "final_result": "",
    }
    state.update(overrides)
    return state


def test_normalize_decision():
    assert normalize_decision(" finish ") == "FINISH"
    assert normalize_decision("Research") == "research"


def test_validate_decision_corrects_premature_finish():
    state = make_state(
        research_result="research result",
        plan_result="plan result",
    )

    assert validate_decision(state, "FINISH") == "writer"


def test_validate_decision_corrects_missing_prerequisites():
    assert validate_decision(make_state(), "planner") == "research"
    assert validate_decision(
        make_state(research_result="research result"),
        "writer",
    ) == "planner"


def test_validate_decision_keeps_valid_decision():
    state = make_state(
        research_result="research result",
        plan_result="plan result",
        final_result="final result",
    )

    assert validate_decision(state, "FINISH") == "FINISH"
