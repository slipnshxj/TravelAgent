from typing import TypedDict
step_count:int = 0
class TravelState(TypedDict):
    user_id: str
    user_query:str
    user_message:str

    research_result: str
    plan_result: str
    final_result: str

    current_agent: str
    step_count:int

    error:str