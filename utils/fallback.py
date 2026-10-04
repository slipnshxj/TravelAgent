import inspect

async def fallback_async(primary_func,fallback_func):
    try:
        result = primary_func()
        if inspect.isawaitable(result):
            return await result
    except Exception as e:
        print(f"[Fallback] 主方案失败:{e}")
        print("[Fallback] 使用备用方案")
        result = fallback_func()
        if inspect.isawaitable(result):
            return await result
        return result