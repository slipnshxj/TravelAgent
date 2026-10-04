import asyncio
import inspect


async def retry_async(
        func,
        max_retries=3,
        delay=1
):
    for attempt in range(max_retries):
        try:
            result = func()
            if inspect.isawaitable(result):
                return await result
            return result

        except Exception as e:
            print(f"[Retry]第{attempt+1}次失败:{e}")
            if attempt == max_retries - 1:
                raise

            await asyncio.sleep(delay)
