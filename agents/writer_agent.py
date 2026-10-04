from langchain.agents import create_agent
from llm import LLM
llm=LLM()
def create_writer_agent(model):
    writer_agent=create_agent(
        model=llm.model,
        tools=[],
        system_prompt="""
你是一名旅行内容整理专家。

你的任务是根据研究结果和旅行计划，
整理成用户可以直接阅读的最终旅行方案。

要求：
1. 结构清晰
2. 信息完整
3. 语言自然
4. 给出必要的注意事项
"""
    )
    return writer_agent
