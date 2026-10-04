from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os


load_dotenv(override=True)

class LLM:
    def __init__(self):
        self.model = init_chat_model(
            model="deepseek-v4-flash",
            model_provider="deepseek",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
            temperature=0,
            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            }
    )

