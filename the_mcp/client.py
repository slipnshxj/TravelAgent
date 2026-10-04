import anyio
from mcp import Client,StdioServerParameters

server_parameters = StdioServerParameters(
    command=r"C:\Users\reali\Desktop\agent_object\.venv\Scripts\python.exe",
    args=[
        "-m",
        "the_mcp.server",
    ],
    cwd = r"C:\Users\reali\Desktop\agent_object",
)

async def main():
    async with Client(server_parameters) as client:
        print("--------------MCP----------------")
        tools=await client.list_tools()
        for tool in tools.tools:
            print(f"名称: {tool.name}")
            print(f"描述: {tool.description}")
            print("-" * 50)

if __name__ == "__main__":
    anyio.run(main)