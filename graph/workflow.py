from langgraph.graph import StateGraph,START,END
from graph.state import TravelState

from agents.research_agent import create_research_agent
from agents.planner_agent import create_planner_agent
from agents.writer_agent import create_writer_agent
from the_mcp.langchain_tools import load_mcp_tools

from utils.context_builder import builder_planner_context,builder_writer_context
from utils.memory_extractor import MemoryExtractor
from utils.memory_writer import write_memories
from utils.retry import retry_async
from utils.fallback import fallback_async
from utils.timeout import timeout_async
from utils.error_router import route_after_agent

from middleware.input import validate_input
from middleware.logging import log_input,log_agent_start,log_agent_end,log_error
from middleware.runner import run_agent_with_middleware
from llm import LLM

model=LLM()
research_tools = load_mcp_tools()
research_agent = create_research_agent(
    model.model,
    tools=research_tools,
)
planner_agent = create_planner_agent(model)
writer_agent = create_writer_agent(model)

MAX_STEPS=10

def supervisor_node(state: TravelState):
    state["step_count"]+=1
    print(
        f"[Workflow] 当前步骤:"
        f" {state['step_count']}/{MAX_STEPS}"
    )
    if state["step_count"]>=MAX_STEPS:
        print("[Workflow] 达到最大协调次数，直接生成最终答案")
        state["current_agent"]="writer"
        return state

    if state.get("final_result"):
        decision = "FINISH"
    elif state.get("plan_result"):
        decision = "writer"
    elif state.get("research_result"):
        decision = "planner"
    else:
        decision = "research"

    state["current_agent"]=decision
    print(f"[Supervisor] {decision}")
    return state

async def research_node(state: TravelState):
    async def run_research():
        result=await research_agent.ainvoke({
            "messages":[
                {
                    "role":"user",
                    "content":state["user_query"]
                }
            ]
        })
        return result["messages"][-1].content

    async def run_research_with_stability():
        return await fallback_async(
            primary_func=lambda:
            retry_async(
                lambda:timeout_async(
                    run_research,
                    timeout_seconds=10
                ),
                max_retries=3,
                delay=1
            ),
            fallback_func=lambda:
            fallback_research(state)
        )
    def save_research_result(result):
        state["research_result"]=result

    return await run_agent_with_middleware(
        state=state,
        agent_name="research",
        action="read_weather",
        run_func=run_research_with_stability,
        save_result_func=save_research_result
    )

async def planner_node(state: TravelState):
    def run_planner():
        prompt=builder_planner_context(state)
        result=planner_agent.invoke({
            "messages":[
                {
                    "role":"user",
                    "content":prompt
                }
            ]
        })
        return result["messages"][-1].content
    def save_plan_result(result):
        state["plan_result"]=result
    return await run_agent_with_middleware(
        state=state,
        agent_name="planner",
        action="create_plan",
        run_func=run_planner,
        save_result_func=save_plan_result
    )

async def writer_node(state: TravelState):
    def run_writer():
        prompt=builder_writer_context(state)
        result=writer_agent.invoke({
            "messages":[
                {
                    "role":"user",
                    "content":prompt
                }
            ]
        })
        return result["messages"][-1].content
    def save_final_result(result):
        state["final_result"]=result
    state = await run_agent_with_middleware(
        state=state,
        agent_name="writer",
        action="create_final_answer",
        run_func=run_writer,
        save_result_func=save_final_result
    )
    if state.get("error") and not state.get("final_result"):
        state["final_result"] = (
            "抱歉，最终答案生成暂时失败。"
            "以下是目前已收集到的信息：\n\n"
            f"用户需求：{state.get('user_query', '')}\n\n"
            f"研究结果：{state.get('research_result', '暂无')}\n\n"
            f"规划结果：{state.get('plan_result', '暂无')}"
        )
        state["error"] = ""
    return state

def memory_writer_node(state: TravelState):
    memory_extractor = MemoryExtractor()
    memories=memory_extractor.extract(
        state["user_query"]
    )
    if memories:
        write_memories(
            user_id=state["user_id"],
            memories=memories,
        )
        print( f"[Memory] 保存了 {len(memories)} 条记忆")
    else:
        print("[Memory] 没有发现需要保存的长期记忆")
    return state

def input_middleware_node(state: TravelState):
    print("[Middleware] Input Check")
    validate_input(state)
    log_input(state)
    return state

def router_supervisor(state:TravelState):
    decision=state.get("current_agent","")
    if state.get("step_count",0)>=10:
        if state.get("final_result"):
            return "FINISH"
        return "writer"
    if decision=="FINISH":
        if state.get("final_result"):
            return "FINISH"
        return "writer"
    if decision in {"research","planner","writer"}:
        return decision
    return "research"


def fallback_research(state:TravelState):
    print("[Fallback Research] 使用备用方案")
    return """
由于实时研究服务暂时不可用，
无法获取最新的外部旅行信息。

请基于已有知识完成基础旅行规划。

注意：
以上研究结果不包含实时天气、实时营业时间
以及实时价格信息。
出行前请再次确认相关信息。
"""

builder=StateGraph(TravelState)

builder.add_node(
    "supervisor",
    supervisor_node
)
builder.add_node(
    "research_agent",
    research_node
)
builder.add_node(
    "planner_agent",
    planner_node
)
builder.add_node(
    "writer_agent",
    writer_node
)
builder.add_node(
    "memory_writer",
    memory_writer_node
)
builder.add_node(
    "input_middleware",
    input_middleware_node
)

builder.add_edge(
    START,
    "input_middleware",
)
builder.add_edge(
    "input_middleware",
    "memory_writer",
)
builder.add_edge(
    "memory_writer",
    "supervisor",
)
builder.add_conditional_edges(
    "supervisor",
    router_supervisor,
    {
        "research":"research_agent",
        "planner":"planner_agent",
        "writer":"writer_agent",
        "FINISH":END
    }
)
builder.add_conditional_edges(
    "research_agent",
    route_after_agent,
    {
        "research": "research_agent",
        "planner": "planner_agent",
        "writer": "writer_agent",
        "supervisor": "supervisor",
        "FINISH": END,
    },
)

builder.add_conditional_edges(
    "planner_agent",
    route_after_agent,
    {
        "research": "research_agent",
        "planner": "planner_agent",
        "writer": "writer_agent",
        "supervisor": "supervisor",
        "FINISH": END,
    },
)

builder.add_conditional_edges(
    "writer_agent",
    route_after_agent,
    {
        "research": "research_agent",
        "planner": "planner_agent",
        "writer": "writer_agent",
        "supervisor": "supervisor",
        "FINISH": END,
    },
)

graph=builder.compile()
