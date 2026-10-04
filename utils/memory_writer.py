from utils.memory_repository import save_memory

def write_memories(
        user_id:str,
        memories:list,
):
    for memory in memories:
        if not isinstance(memory, dict):
            continue

        category = memory.get("category")
        content = memory.get("content")

        if content is None:
            key = memory.get("key")
            value = memory.get("value")
            if key is not None and value is not None:
                content = f"{key}: {value}"

        if not category or not content:
            continue

        save_memory(
            user_id=user_id,
            category=category,
            content=content,
            importance=memory.get("importance", 1),
            source=memory.get(
                "source",
                "conversation"
            )
        )
