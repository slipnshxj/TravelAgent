from __future__ import annotations

import asyncio
from typing import Any

from core.config import settings


async def list_tools(gateway) -> list[dict[str, Any]]:
    return await asyncio.wait_for(
        gateway.list_tools(),
        timeout=settings.tool_timeout_seconds,
    )


async def invoke_tool(
    gateway,
    name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    return await asyncio.wait_for(
        gateway.invoke_tool(name, arguments),
        timeout=settings.tool_timeout_seconds,
    )
