from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

def save_user_memory(
    user_id:str,
    category:str,
    key:str,
    value
):
    store.put(
        ("users",user_id,category),
        key,
        {
            "value":value
        }
    )

def get_user_memory(
    user_id:str,
    category:str,
    key:str,
):
    result = store.get(
        ("users",user_id,category),
        key,
    )
    if result is None:
        return None
    return result.value

def get_user_memories(
        user_id:str,
        category:str
):
    memories = store.search(
        ("users",user_id,category)
    )
    return {
        memory.key:memory.value
        for memory in memories
    }