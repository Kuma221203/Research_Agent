from langgraph.types import Send
from langchain_core.messages import HumanMessage, SystemMessage

from agents.researcher.states import ResearchGraphState
from agents.researcher.prompts import (
    report_writer_instructions,
    intro_conclusion_instructions,
)
from utils.helpers import llm


def initiate_all_interviews(state: ResearchGraphState):
    human_analyst_feedback = state["human_analyst_feedback"]
    if human_analyst_feedback:
        return "create_analysts"
    else:
        topic = state["topic"]
        return [
            Send("conduct_interview", 
                {
                    "analyst": analyst,
                    "messages": [HumanMessage(
                        content=f"So you said you were writing an article on {topic}?"
                    )]
                }
            ) for analyst in state["analysts"]
        ]

def write_report(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    system_message = report_writer_instructions.format(topic=topic, context=formatted_str_sections)
    response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content=f"Write a report based upon these memos.")])
    return {"content": response.content}

def write_introduction(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    system_message = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)
    response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Write the report introduction.")])
    return {"introduction": response.content}

def write_conclusion(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    system_message = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)
    response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Write the report conclusion.")])
    return {"conclusion": response.content}

def finalize_report(state: ResearchGraphState):
    content = state["content"]
    if content.startswith("## Insights"):
        content = content.strip("## Insights")
    
    if "## Sources" in content:
        try:
            content, sources = content.split("## Sources")
        except:
            sources = None
    else:
        sources = None

    final_report = state["introduction"] + "\n\n--\n\n" + content + "\n\n--\n\n" + state["conclusion"]
    if sources:
        final_report += "\n\n ## Sources" + sources
    
    return {"final_report": final_report}