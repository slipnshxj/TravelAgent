import time
import inspect
from typing import Awaitable,Callable,Union

from graph.state import TravelState
from middleware.logging import log_agent_start,log_agent_end,log_error
from middleware.permission import check_agent_permissions
from middleware.output import check_agent_output

RunFunc = Callable[[],Union[str,Awaitable[str]]]
async def run_agent_with_middleware(
    state: TravelState,
    agent_name: str,
    action:str,
    run_func: Callable[[],str],
    save_result_func:Callable[[str],None],
)->TravelState:
    """
    统一执行 Agent：

    1. 权限检查
    2. 记录 Agent 开始
    3. 执行业务函数
    4. 检查输出
    5. 保存结果
    6. 记录 Agent 结束
    7. 统一处理异常
    """
    start_time=time.perf_counter()
    try:
        check_agent_permissions(
            state=state,
            agent_name=agent_name,
            action=action,
        )
        log_agent_start(
            agent_name,
            state
        )

        result = run_func()

        if inspect.isawaitable(result):
            result = await result

        check_agent_output(
            state=state,
            agent_name=agent_name,
            output=result,
        )

        save_result_func(result)

        elapsed = time.perf_counter() - start_time

        log_agent_end(
            agent_name,
            state,
            elapsed,
        )
        state["error"]=""
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        print(f"[{agent_name}] ERROR {e}")
        log_error(
            agent_name,
            e,
            elapsed,
        )
        state["error"]=str(e)
    return state