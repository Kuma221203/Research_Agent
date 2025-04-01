from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import END

from agents.planner.prompts import analyst_instructions
from agents.planner.states import Perspectives
from agents.planner.states import GenerateAnalystsState

from utils.helpers import llm

def create_analysts(state: GenerateAnalystsState):
  topic = state["topic"]
  max_analysts = state["max_analysts"]
  human_analyst_feedback = state.get("human_analyst_feedback", "")

  system_message = analyst_instructions.format(
    topic=topic,  
    max_analysts=max_analysts, 
    human_analyst_feedback=human_analyst_feedback
  )

  structured_llm = llm.with_structured_output(Perspectives)
  response = structured_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate the set of analysts.")])
  return {"analysts": response.analysts}

def human_feedback(state: GenerateAnalystsState):
  pass

def should_continue(state: GenerateAnalystsState):
  human_analyst_feedback = state.get("human_analyst_feedback", None)
  if human_analyst_feedback:
    return "create_analysts"
  return END