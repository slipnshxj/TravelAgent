from graph.state import TravelState

def log_input(state:TravelState)->None:
    print(
        f"[Middleware][Input] "
        f"user_id={state['user_id']} "
        f"query={state['user_query']}"
    )

def log_agent_start(
        agent_name:str,
        state:TravelState
)->None:
    print(
        f"[Middleware][Agent Start] "
        f"agent={agent_name} "
        f"step={state['step_count']}"
    )

def log_agent_end(
        agent_name:str,
        state:TravelState,
        elapsed:float=0,
)->None:
    print(
        f"[Middleware][Agent End] "
        f"agent={agent_name} "
        f"step={state['step_count']}"
        f"耗时={elapsed:.2f}s "
    )

def log_error(
        component: str,
        error: Exception,
        elapsed:float=0
)->None:
    print(
        f"[Middleware][ERROR] "
        f"component={component} "
        f"耗时={elapsed:.2f}s "
        f"error={error}"
    )