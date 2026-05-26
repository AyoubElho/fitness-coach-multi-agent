from typing import TypedDict, List, Optional, Annotated
from langchain_core.messages import BaseMessage
from operator import add

class FitnessState(TypedDict):

    messages: Annotated[List[BaseMessage], add]

    user_request: str

    user_profile: Optional[str]

    workout_plan: Optional[str]

    nutrition_plan: Optional[str]

    progress_milestones: Optional[str]
    plan_approved: Optional[bool]

    next_agent: Optional[str]
