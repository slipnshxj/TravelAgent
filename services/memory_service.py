from __future__ import annotations

from repositories.memory_repository import (
    archive_memory,
    delete_memory,
    list_memories,
    list_memory_users,
    save_memory,
)


def memory_to_dict(memory: tuple) -> dict:
    return {
        "id": memory[0],
        "user_id": memory[1],
        "category": memory[2],
        "content": memory[3],
        "importance": memory[4],
        "source": memory[5],
        "is_active": memory[6],
        "created_at": memory[7],
        "updated_at": memory[8],
    }


__all__ = [
    "archive_memory",
    "delete_memory",
    "list_memories",
    "list_memory_users",
    "memory_to_dict",
    "save_memory",
]
