from mcp.server import MCPServer
from the_mcp.tools import get_weather,search_attractions,calculate_budget,hotel as get_hotels

mcp=MCPServer(
    "travel_tools",
    instructions="提供旅行规划相关工具。",
)

@mcp.tool()
def weather(city:str)->dict:
    """
    查询指定城市的天气
    """
    return get_weather(city)

@mcp.tool()
def attractions(city:str)->list[dict]:
    """
    查询指定城市的旅游景点。
    """
    return search_attractions(city)

@mcp.tool()
def budget(days:int,daily_budget:float)->dict:
    """
    根据旅行天数和每日预算计算总预算。
    """
    return calculate_budget(
        days=days,
        daily_budget=daily_budget
    )

@mcp.tool()
def hotel(city:str)->list[dict]:
    """查询指定城市的酒店"""
    return get_hotels(city)


if __name__=="__main__":
    mcp.run()
