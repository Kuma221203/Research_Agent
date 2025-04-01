from typing import TypedDict, List, Annotated
from operator import add
from agents.planner.states import Analyst

class ResearchGraphState(TypedDict):
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]
    sections: Annotated[list, add]
    introduction: str
    content: str
    conclusion: str
    final_report: str