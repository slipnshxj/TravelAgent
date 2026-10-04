import asyncio
import inspect

async def timeout_async(func,timeout_seconds=25):
    result = func()
    if inspect.isawaitable(result):
        return await asyncio.wait_for(
            result,
            timeout=timeout_seconds
        )
    return result