from utils.memory_context import build_memory_context


def main():
    context = build_memory_context("test_user")

    print("当前长期记忆：")
    print(context)


if __name__ == "__main__":
    main()
    