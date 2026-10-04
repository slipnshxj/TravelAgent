from graph.state import TravelState

def validate_output(
        agent_name:str,
        output:str
)->None:
    if not output:
        raise ValueError(
            f"{agent_name} 输出不能为空"
        )

    if not output.strip():
        raise ValueError(
            f"{agent_name} 输出不能只有空格"
        )

    if len(output)>10000:
        raise ValueError(
            f"{agent_name} 输出过长"
        )

def check_agent_output(
        state:TravelState,
        agent_name:str,
        output:str
)->None:
    validate_output(
        agent_name=agent_name,
        output=output
    )
    print(
        f"[Middleware][Output] "
        f"agent={agent_name} 输出检查通过"
    )