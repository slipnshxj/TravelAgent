from langchain_core.tools import StructuredTool
from pydantic import create_model

class MCPToolRegistry:
    def __init__(self,runtime):
        self.runtime = runtime
        self.tools = []
    def _build_args_schema(self,mcp_tool):
        properties = mcp_tool.input_schema.get(
            "properties",
            {}
        )
        required = mcp_tool.input_schema.get(
            "required",
            []
        )
        fields = {}
        for name,schema in properties.items():
            schema_type = schema.get("type","string")
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
                fields[name] = (
                    python_type,
                    ...
                )
            else:
                fields[name] = (
                    python_type,
                    None
                )
        return create_model(
            f"{mcp_tool.name}Args",
            **fields,
        )
    def _make_tool(self,mcp_tool,args_schema):
        tool_name = mcp_tool.name
        async def call_tool(**kwargs):
            result = await self.runtime.call_tool(
                tool_name,
                kwargs
            )
            return str(result.content)
        return StructuredTool.from_function(
            coroutine=call_tool,
            name=f"mcp_{tool_name}",
            description=mcp_tool.description or "",
            args_schema=args_schema,
        )

    async def initialize(self):
        mcp_tools = await self.runtime.list_tools()
        for mcp_tool in mcp_tools:
            args_schema = self._build_args_schema(mcp_tool)
            tool = self._make_tool(
                mcp_tool,
                args_schema
            )
            self.tools.append(tool)
        return self.tools