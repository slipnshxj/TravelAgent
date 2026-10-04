from __future__ import annotations

import asyncio
import uuid
from typing import Any

from core.config import settings
from services.map_service import build_map_context


async def run_travel_workflow(user_id: str, message: str) -> dict[str, Any]:
    from graph.workflow import graph

    initial_state = {
        "user_id": user_id,
        "user_query": message,
        "current_agent": "",
        "research_result": "",
        "plan_result": "",
        "final_result": "",
        "error": "",
        "step_count": 0,
    }
    result = await asyncio.wait_for(
        graph.ainvoke(initial_state),
        timeout=settings.chat_timeout_seconds,
    )
    return {
        "researchResult": result.get("research_result", ""),
        "planResult": result.get("plan_result", ""),
        "finalResult": result.get("final_result", ""),
        "error": result.get("error", ""),
    }


async def handle_chat(
    user_id: str,
    message: str,
    conversation_id: str | None = None,
) -> dict[str, Any]:
    map_task = asyncio.create_task(build_map_context(message))
    try:
        result = await run_travel_workflow(user_id, message)
    except asyncio.TimeoutError as error:
        result = {
            "researchResult": "",
            "planResult": "",
            "finalResult": "",
            "error": f"对话处理超时：{error}",
        }
    finally:
        map_context = await map_task
    return {
        "conversationId": conversation_id or str(uuid.uuid4()),
        "mapKeyword": map_context["keyword"],
        "mapTargets": map_context["targets"],
        "mapError": map_context["error"],
        **result,
    }
