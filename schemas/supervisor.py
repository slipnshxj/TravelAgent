from typing import Literal
from pydantic import BaseModel

class SupervisorDecision(BaseModel):

    next:Literal[
        "research",
        "planner",
        "writer",
        "FINISH"
    ]

