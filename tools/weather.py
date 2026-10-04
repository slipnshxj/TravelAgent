from langchain_core.tools import tool

@tool()
def get_weather(city:str)->str:
    """天气查询"""
    try:
        weather_data={
            "东京": "晴天，25°C",
            "京都": "多云，23°C",
            "大阪": "小雨，21°C",
        }
        if city == "测试故障":
            raise RuntimeError("暂不可用")

        return weather_data.get(
            city,
            "暂不可用"
        )
    except Exception as e:
        print(f"错误日志:{e}")
        return "error weather data"
