from mcp import Client,StdioServerParameters

server_parameters = StdioServerParameters(
    command = r"C:\Users\reali\Desktop\agent_object\.venv\Scripts\python.exe",
    args=[
        "-m",
        "the_mcp.server"
    ],
    cwd = r"C:\Users\reali\Desktop\agent_object"
)

class MCPRuntime:
    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = Client(server_parameters)
        await self.client.__aenter__()
        return self

    async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback
    ):
        if self.client is not None:
            await self.client.__aexit__(
                exc_type,
                exc_value,
                traceback
            )

    async def list_tools(self):
        if self.client is None:
            raise RuntimeError(
                "MCPRuntime 尚未启动"
            )
        result = await self.client.list_tools()
        return result.tools

    async def call_tool(
            self,
            tool_name:str,
            arguments:dict
    ):
        if self.client is None:
            raise RuntimeError(
                "MCPRuntime 尚未启动"
            )
        return await self.client.call_tool(
            tool_name,
            arguments
        )