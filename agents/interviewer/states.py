from typing import Annotated
from pydantic import BaseModel, Field
from operator import add
from langgraph.graph import MessagesState
from agents.planner.states import Analyst

class InterviewState(MessagesState):
    max_num_turns: int
    context: Annotated[list, add]
    analyst: Analyst
    interview: str
    sections: list

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")