from graph.workflow import graph
import asyncio
import argparse
import os

from dotenv import load_dotenv
load_dotenv(override=True)

DEFAULT_USER_ID = "memory_test_user"

def parse_args():
    parser = argparse.ArgumentParser(
        description="旅行规划 Agent"
    )
    parser.add_argument(
        "--user_id",
        default=None,
        help="指定用户 ID，优先级最高"
    )
    return parser.parse_args()

def resolve_user_id(user_id_arg:str | None)->str:
    if user_id_arg:
        print(f"[Config] 使用命令行用户 ID：{user_id_arg}")
        return user_id_arg
    env_user_id = os.getenv("AGENT_USER_ID")
    if env_user_id:
        print(f"[Config] 使用环境变量 AGENT_USER_ID：{env_user_id}")
        return env_user_id
    while True:
        user_id = input(
            f"请输入用户 ID（直接回车使用 {DEFAULT_USER_ID}）："
        ).strip()
        if not user_id:
            print(f"[Config] 使用默认用户 ID：{DEFAULT_USER_ID}")
            return DEFAULT_USER_ID
        if " " in user_id:
            print("用户 ID 不能包含空格，请重新输入")
            continue
        return user_id

async def run_test(user_id: str, user_query: str):
    print("\n" + "=" * 60)
    print(f"用户 ID：{user_id}")
    print(f"用户请求：{user_query}")
    print("=" * 60)

    initial_state = {
        "user_id": user_id,
        "user_query": user_query,
        "current_agent": "",
        "research_result": "",
        "plan_result": "",
        "final_result": "",
        "error": "",
        "step_count": 0,
    }

    result = await graph.ainvoke(initial_state)

    print("\n" + "=" * 60)
    print("最终执行结果")
    print("=" * 60)

    print("current_agent：", result.get("current_agent"))
    print("research_result：", result.get("research_result"))
    print("plan_result：", result.get("plan_result"))
    print("final_result：", result.get("final_result"))
    print("error：", result.get("error"))
    print("step_count：", result.get("step_count"))

    return result


async def main():
    args = parse_args()
    user_id = resolve_user_id(args.user_id)

    while True:
        user_query = input("\n请输入用户请求，输入 q 退出：").strip()

        if user_query.lower() == "q":
            break

        if not user_query:
            print("请求不能为空")
            continue

        await run_test(
            user_id=user_id,
            user_query=user_query,
        )

if __name__ == "__main__":
    asyncio.run(main())