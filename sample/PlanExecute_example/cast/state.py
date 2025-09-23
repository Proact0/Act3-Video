from typing import TypedDict, Optional


class PlanExecuteState(TypedDict):
    prompt: str
    plan: Optional[str]
    result: Optional[str]
