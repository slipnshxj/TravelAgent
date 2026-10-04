from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.logging import configure_logging
from core.metrics import metrics
from middleware.audit import AuditMiddleware
from middleware.authentication import ApiAuthenticationMiddleware
from middleware.observability import ObservabilityMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.security import SecurityHeadersMiddleware
from schemas.api import ChatRequest, MemoryArchive, MemoryCreate, ToolInvoke
from services import map_service, tool_service
from services.chat_service import run_travel_workflow
from services.map_service import (
    build_map_context,
    extract_map_keyword,
    normalize_map_targets,
    search_map_places,
)
from services.memory_service import (
    archive_memory,
    delete_memory,
    list_memories,
    list_memory_users,
    memory_to_dict,
    save_memory,
)
from utils import tool_gateway

logger = configure_logging(settings)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Travel agent web API with memory, tools, and AMap integration.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
if settings.api_auth_token:
    app.add_middleware(ApiAuthenticationMiddleware, token=settings.api_auth_token)
app.add_middleware(
    RateLimitMiddleware,
    enabled=settings.rate_limit_enabled,
    requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ObservabilityMiddleware, logger=logger)
app.add_middleware(AuditMiddleware, log_dir=settings.log_dir)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict:
    return {
        "defaultUserId": settings.default_user_id,
        "amapConfigured": bool(settings.amap_js_key),
    }


@app.get("/api/users")
def users() -> dict:
    return {"users": list_memory_users()}


@app.get("/api/memories")
def memories(
    user_id: str = Query(min_length=1, max_length=100),
    category: str | None = None,
    include_archived: bool = False,
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    rows = list_memories(
        user_id=user_id,
        category=category,
        include_archived=include_archived,
        limit=limit,
    )
    return {"memories": [memory_to_dict(row) for row in rows]}


@app.post("/api/memories", status_code=201)
def create_memory(payload: MemoryCreate) -> dict:
    memory_id = save_memory(
        user_id=payload.user_id,
        category=payload.category,
        content=payload.content,
        importance=payload.importance,
        source=payload.source,
    )
    return {"id": memory_id}


@app.patch("/api/memories/{memory_id}/archive")
def archive_memory_endpoint(
    memory_id: int,
    user_id: str = Query(min_length=1, max_length=100),
    payload: MemoryArchive | None = None,
) -> dict:
    archived = payload.archived if payload else True
    if not archive_memory(user_id, memory_id, archived):
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"id": memory_id, "archived": archived}


@app.delete("/api/memories/{memory_id}")
def delete_memory_endpoint(
    memory_id: int,
    user_id: str = Query(min_length=1, max_length=100),
) -> dict:
    if not delete_memory(user_id, memory_id):
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"id": memory_id, "deleted": True}


@app.post("/api/conversations")
def new_conversation() -> dict:
    return {
        "conversationId": str(uuid.uuid4()),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/tools")
async def tools() -> dict:
    return {"tools": await tool_service.list_tools(tool_gateway)}


@app.post("/api/tools/{tool_name}/invoke")
async def invoke_tool_endpoint(tool_name: str, payload: ToolInvoke) -> dict:
    return await tool_service.invoke_tool(tool_gateway, tool_name, payload.arguments)


@app.get("/api/map/config")
def map_config() -> dict:
    js_key = os.getenv("AMAP_JS_KEY", "")
    return {
        "configured": bool(js_key),
        "jsKey": js_key,
        "securityJsCode": os.getenv("AMAP_SECURITY_JS_CODE", ""),
        "version": "2.0",
        "center": [116.397428, 39.90923],
        "zoom": 11,
    }


@app.get("/api/map/places")
async def map_places(
    keywords: str = Query(min_length=1),
    city: str | None = None,
) -> dict:
    if not settings.amap_rest_api_key:
        raise HTTPException(status_code=503, detail="AMAP_REST_API_KEY is not configured")
    return await map_service.search_map_places(keywords, city)


@app.post("/api/chat")
async def chat(payload: ChatRequest) -> dict:
    map_task = asyncio.create_task(build_map_context(payload.message))
    try:
        result = await run_travel_workflow(payload.user_id, payload.message)
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
        "conversationId": payload.conversation_id or str(uuid.uuid4()),
        "mapKeyword": map_context["keyword"],
        "mapTargets": map_context["targets"],
        "mapError": map_context["error"],
        **result,
    }


@app.get("/metrics")
def prometheus_metrics() -> Response:
    if not settings.metrics_enabled:
        raise HTTPException(status_code=404, detail="Metrics are disabled")
    return Response(content=metrics.render(), media_type="text/plain")


app.mount("/", StaticFiles(directory="web", html=True), name="web")
