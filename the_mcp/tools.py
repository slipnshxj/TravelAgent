def get_weather(city: str) -> dict:
    weather_data = {
        "东京": {
            "temperature": 26,
            "condition": "晴天",
            "suggestion": "适合城市观光",
        },
        "北京": {
            "temperature": 24,
            "condition": "多云",
            "suggestion": "适合户外活动",
        },
        "上海": {
            "temperature": 27,
            "condition": "小雨",
            "suggestion": "建议携带雨具",
        },
    }

    return weather_data.get(
        city,
        {
            "temperature": None,
            "condition": "暂无数据",
            "suggestion": "暂无天气数据",
        },
    )


def search_attractions(city: str) -> list[dict]:
    attractions_data = {
        "东京": [
            {
                "name": "浅草寺",
                "type": "历史景点",
            },
            {
                "name": "上野公园",
                "type": "城市公园",
            },
            {
                "name": "东京站",
                "type": "城市地标",
            },
        ],
        "北京": [
            {
                "name": "故宫",
                "type": "历史景点",
            },
            {
                "name": "颐和园",
                "type": "园林景点",
            },
        ],
    }

    return attractions_data.get(city, [])


def calculate_budget(
    days: int,
    daily_budget: float,
) -> dict:
    return {
        "days": days,
        "daily_budget": daily_budget,
        "total_budget": days * daily_budget,
    }

def hotel(city: str) -> list[dict]:
    hotel_data = {
        "东京": [
            {"name": "东京站酒店", "price": 1200},
            {"name": "新宿酒店", "price": 900},
        ],
        "北京": [
            {"name": "王府井酒店", "price": 800},
        ],
    }
    return hotel_data.get(city, [])