from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.researcher.states import ResearchGraphState

from agents.planner.nodes import create_analysts, human_feedback
from agents.researcher.nodes import (
    initiate_all_interviews,
    write_introduction,
    write_report,
    write_conclusion,
    finalize_report,
)

from agents.interviewer.graph import builder_interview

def builder_reseach():
    interview = builder_interview()
    
    builder = StateGraph(ResearchGraphState)

    builder.add_node(create_analysts)
    builder.add_node(human_feedback)
    builder.add_node("conduct_interview", interview.compile().with_config(run_name="Conduct Interview"))
    builder.add_node(write_introduction)
    builder.add_node(write_report)
    builder.add_node(write_conclusion)
    builder.add_node(finalize_report)

    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")
    builder.add_conditional_edges("human_feedback", initiate_all_interviews, ["create_analysts", "conduct_interview"])
    builder.add_edge("conduct_interview", "write_introduction")
    builder.add_edge("conduct_interview", "write_report")
    builder.add_edge("conduct_interview", "write_conclusion")
    builder.add_edge(["write_introduction", "write_report", "write_conclusion"], "finalize_report")
    builder.add_edge("finalize_report", END)

    return builder

def get_researcher():
    builder = builder_reseach()
    memory = MemorySaver()
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["human_feedback"],
    )
    return graph

researcher = get_researcher()