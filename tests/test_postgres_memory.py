from utils.memory_repository import save_memory, get_memories


def main():
    user_id = "test_user"

    print("开始写入记忆...")

    save_memory(
        user_id=user_id,
        category="preference",
        content="food: 喜欢川菜",
        importance=5,
        source="test",
    )

    save_memory(
        user_id=user_id,
        category="preference",
        content="travel_style: 喜欢慢节奏旅行",
        importance=5,
        source="test",
    )

    save_memory(
        user_id=user_id,
        category="habit",
        content="planning: 习惯提前规划行程",
        importance=5,
        source="test",
    )

    print("记忆写入完成")
    print()

    memories = get_memories(user_id)

    print("查询结果：")

    for memory in memories:
        print(
            {
                "id": memory[0],
                "user_id": memory[1],
                "category": memory[2],
                "content": memory[3],
                "importance": memory[4],
                "source": memory[5],
            }
        )


if __name__ == "__main__":
    main()