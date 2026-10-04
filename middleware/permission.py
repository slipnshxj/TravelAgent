from graph.state import TravelState

AGENT_PERMISSIONS={
    "research": {
        "read_weather",
        "read_attractions",
        "read_budget",
    },
    "planner": {
        "read_research",
        "create_plan",
    },
    "writer": {
        "read_research",
        "read_plan",
        "create_final_answer",
    },
    "supervisor": {
        "route_agent",
    },
}

def check_permissions(
        agent_name:str,
        action:str
)->None:
    permissions=AGENT_PERMISSIONS.get(
        agent_name,
        set()
    )
    if action not in permissions:
        raise PermissionError(
            f"Agent '{agent_name}' "
            f"没有执行 '{action}' 的权限"
        )

def check_agent_permissions(
        state:TravelState,
        agent_name:str,
        action:str
)->None:
    check_permissions(
        agent_name=agent_name,
        action=action
    )
    print(
        f"[Middleware][Permission] "
        f"agent={agent_name} "
        f"action={action} 允许"
    )