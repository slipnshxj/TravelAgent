from langchain_core.tools import tool


@tool()
def calculate_budget(days:int,daily_budget:float)->str:
    """
    根据旅行天数和每日预算计算总预算。

    参数：
        days: 旅行天数
        daily_budget: 每天预算
    """
    total = days * daily_budget
    return f"{days}天旅行预计预算为{total:.2f}元"
