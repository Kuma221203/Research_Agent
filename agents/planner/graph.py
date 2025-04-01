from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from agents.planner.states import GenerateAnalystsState
from agents.planner.nodes import create_analysts, human_feedback, should_continue

def builder_plan():
  builder = StateGraph(GenerateAnalystsState)

  builder.add_node("create_analysts", create_analysts)
  builder.add_node("human_feedback", human_feedback)

  builder.add_edge(START, "create_analysts")
  builder.add_edge("create_analysts", "human_feedback")
  builder.add_conditional_edges("human_feedback", should_continue, ["create_analysts", END])

  return builder_plan

def get_planner():
  builder = builder_plan()
  memory = MemorySaver()
  return builder.compile(checkpointer=memory, interrupt_before=["human_feedback"])

planner = get_planner()