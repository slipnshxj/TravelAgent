from utils.memory_repository import get_memories

def build_memory_context(
        user_id:str,
        limit:int=20
)->str:
    memories=get_memories(
        user_id=user_id,
        limit=limit
    )
    if not memories:
        return "暂无历史记忆"

    lines=[]

    for memory in memories:
        category=memory[2]
        content=memory[3]
        lines.append(
            f"- [{category}] {content}"
        )
    return "\n".join(lines)