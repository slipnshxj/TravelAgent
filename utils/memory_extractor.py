import json
from llm import LLM

class MemoryExtractor:
    def __init__(self):
        self.llm=LLM()
    def extract(self,user_message:str)->list:
        prompt = f"""
        你负责从用户消息中提取值得长期记忆的信息。

        只有满足以下条件的信息才提取：

        1. 用户长期的偏好
        2. 用户长期的习惯
        3. 用户明确表示喜欢或不喜欢的事情
        4. 未来任务中可能继续使用的信息

        不要提取：

        1. 当前一次性的任务
        2. 当前天气
        3. 当前地点
        4. 当前日期
        5. 临时需求

        用户消息：

        {user_message}

        如果没有值得记忆的信息，返回：

        []

        否则返回 JSON 数组。

        每个元素必须包含：

        category
        key
        value

        category 只能是：

        preference
        dislike
        habit
        personal_context

        不要解释。
        """

        result = self.llm.model.invoke(prompt)
        content = result.content.strip()
        try:
            memories = json.loads(content)
        except json.JSONDecodeError:
            return []

        return memories
