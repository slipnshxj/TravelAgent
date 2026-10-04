from typing import Any

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    importance: int = Field(default=1, ge=1, le=10)
    source: str = Field(default="manual", max_length=100)


class MemoryArchive(BaseModel):
    archived: bool = True


class ToolInvoke(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, max_length=100)
