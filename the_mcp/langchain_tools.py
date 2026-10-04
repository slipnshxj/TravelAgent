import anyio
import asyncio
from concurrent.futures import ThreadPoolExecutor

from langchain_core.tools import StructuredTool
from pydantic import create_model
from the_mcp.runtime import MCPRuntime

def _build_args_schema(mcp_tool):
    """
    根据 MCP Tool 的 input_schema
    动态创建 Pydantic 参数模型
    """
    properties=mcp_tool.input_schema.get(
        "properties",
        {}
    )
    required = mcp_tool.input_schema.get(
        "properties",
        {}
    )
    required=mcp_tool.input_schema.get(
        "required",
        []
    )
    fields = {}
    for name,schema in properties.items():
        schema_type=schema.get("type","string")
        if schema_type == "string":
            python_type = str
        elif schema_type == "integer":
            python_type = int
        elif schema_type == "number":
            python_type = float
        elif schema_type == "boolean":
            python_type = bool
        else:
            python_type = dict
        if name in required:
            fields[name]=(
                python_type,
                ...
            )
        else:
            fields[name]=(
                python_type,
                None
            )
    return create_model(
        f"{mcp_tool.name}Args",
        **fields,
    )

async def _load_mcp_tools():
    """
    在同一个 MCP Runtime 中：

    1. 发现工具
    2. 创建 LangChain Tools
    """

    async with MCPRuntime() as runtime:
        mcp_tool = await runtime.list_tools()
        langchain_tools = []
        for tool in mcp_tool:
            langchain_tools.append(
                _create_langchain_tool(tool)
            )

    return langchain_tools

def _create_langchain_tool(mcp_tool):
    tool_name = mcp_tool.name

    async def call_tool_async(**kwargs):
        async with MCPRuntime() as runtime:
            result = await runtime.call_tool(
                tool_name,
                kwargs,
            )
            return str(result.content)

    def call_tool(**kwargs):
        async def run():
            return await call_tool_async(**kwargs)

        return _run_in_new_event_loop(run)

    return StructuredTool.from_function(
        func=call_tool,
        coroutine=call_tool_async,
        name=f"mcp_{tool_name}",
        description=mcp_tool.description or "",
        args_schema=_build_args_schema(mcp_tool),
    )

def _run_in_new_event_loop(async_function):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return anyio.run(async_function)

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(anyio.run, async_function).result()


def load_mcp_tools():
    return _run_in_new_event_loop(_load_mcp_tools)
