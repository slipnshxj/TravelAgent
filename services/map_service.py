from __future__ import annotations

import asyncio
import re

import httpx

from core.config import settings

MAP_KEYWORD_PATTERNS = (
    re.compile(
        r"(?:帮我)?(?:找一下|查找|搜索|定位|标注|显示)(?:一下)?"
        r"(?:在地图上)?(.+?)"
        r"(?:的位置|在哪里|在哪儿|的地址|地图)?$"
    ),
    re.compile(r"^(.{2,40}?)(?:在哪里|在哪儿|的位置|的地址)$"),
    re.compile(r"(?:去|到|前往)(.{2,40}?)(?:旅游|旅行|游玩|玩|攻略|路线)?$"),
)


def extract_map_keyword(message: str) -> str | None:
    for pattern in MAP_KEYWORD_PATTERNS:
        match = pattern.search(message.strip())
        if not match:
            continue
        keyword = match.group(1).strip()
        keyword = re.sub(r"^(?:一下|这个|那个|位于|在)+", "", keyword)
        keyword = re.sub(
            r"(?:的位置|位置|地方|景点|地址|地图)$",
            "",
            keyword,
        ).strip("，。！？?.,!? ")
        if 2 <= len(keyword) <= 40:
            return keyword
    return None


async def search_map_places(
    keywords: str,
    city: str | None = None,
    limit: int = 5,
) -> dict:
    if not settings.amap_rest_api_key:
        return {"pois": []}

    params = {
        "key": settings.amap_rest_api_key,
        "keywords": keywords,
        "offset": limit,
        "page": 1,
        "extensions": "base",
    }
    if city:
        params["city"] = city

    last_error: Exception | None = None
    async with httpx.AsyncClient(timeout=settings.amap_timeout_seconds) as client:
        for attempt in range(settings.amap_max_retries + 1):
            try:
                response = await client.get(
                    "https://restapi.amap.com/v3/place/text",
                    params=params,
                )
                response.raise_for_status()
                result = response.json()
                if result.get("status") != "1":
                    raise RuntimeError(result.get("info", "高德地点搜索失败"))
                return result
            except (httpx.TimeoutException, httpx.TransportError) as error:
                last_error = error
                if attempt < settings.amap_max_retries:
                    await asyncio.sleep(0.5 * (2**attempt))
    raise RuntimeError(f"高德地点搜索失败：{last_error}")


def normalize_map_targets(result: dict, limit: int = 5) -> list[dict]:
    targets = []
    for poi in result.get("pois", [])[:limit]:
        if not poi.get("location"):
            continue
        targets.append(
            {
                "name": poi.get("name", ""),
                "address": poi.get("address", "") or poi.get("pname", ""),
                "location": poi["location"],
            }
        )
    return targets


async def build_map_context(message: str) -> dict:
    keyword = extract_map_keyword(message)
    if not keyword:
        return {"keyword": None, "targets": [], "error": ""}
    try:
        result = await search_map_places(keyword)
        return {
            "keyword": keyword,
            "targets": normalize_map_targets(result),
            "error": "",
        }
    except Exception as error:
        return {
            "keyword": keyword,
            "targets": [],
            "error": f"地图定位失败：{error}",
        }
