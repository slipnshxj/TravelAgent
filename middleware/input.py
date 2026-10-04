from graph.state import TravelState

def validate_input(state:TravelState)->None:
    user_query=state["user_query"]
    if not user_query:
        raise ValueError(
            "用户搜索不能为空"
        )
    if len(user_query)>2000:
        raise ValueError(
            "用户不能超过2000个字符"
        )