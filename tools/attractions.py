from langchain_core.tools import tool
@tool()
def search_attractions(city: str) -> str:
    """
    查询城市的热门旅游景点。
    """
    attractions = {
        "东京": "浅草寺、东京塔、明治神宫、涩谷",
        "京都": "清水寺、金阁寺、伏见稻荷大社、二条城",
        "大阪": "大阪城、道顿堀、通天阁、环球影城",
    }
    print("tool: search_attractions")
    return attractions.get(
        city,
        "error，没有这个城市"
    )