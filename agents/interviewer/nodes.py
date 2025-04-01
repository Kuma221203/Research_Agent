from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from langchain_core.messages import get_buffer_string
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from agents.interviewer.prompts import ( 
    question_instructions, 
    search_instructions, 
    answer_instructions, 
    section_writer_instructions
)
from agents.interviewer.states import SearchQuery, InterviewState

from utils.helpers import llm

tavily_search = TavilySearchResults(max_results=3)

def generate_question(state: InterviewState):
    analyst = state["analyst"]
    message = state["messages"]
    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)] + message)
    return {"messages": [question]}

def search_web(state: InterviewState):
    # Search web
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)] + state["messages"])

    # Search
    search_docs = tavily_search.invoke(search_query.search_query)

    # Format
    formatted_search_docs = "\n\n--\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"context": [formatted_search_docs]}

def search_wikipedia(state: InterviewState):
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)] + state['messages'])

    search_docs = WikipediaLoader(query=search_query.search_query, load_max_docs=2).load()
    formatted_search_docs = "\n\n--\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"context": [formatted_search_docs]}

def generate_answer(state: InterviewState):
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]
    system_message = answer_instructions.format(goals=analyst.persona, context=context)
    answer = llm.invoke([SystemMessage(content=system_message)] + messages)
    answer.name = "expert"
    return {"messages": [answer]}

def save_interview(state:InterviewState):
    messages = state["messages"]
    interview = get_buffer_string(messages)
    return {"interview": interview}

def route_messages(state: InterviewState, name: str = "expert"):
    messages = state["messages"]
    max_num_turns =state.get("max_num_turns", 2)
    num_responses = len(
        [m for m in messages if isinstance(m, AIMessage) and m.name == name]
    )

    if num_responses >= max_num_turns:
        return "save_interview" 

    last_question = messages[-2]
    if "Thank you so much for your help" in last_question.content:
        return "save_interview"
    
    return "ask_question"

def write_section(state: InterviewState):
    # interview = state["interview"]
    context = state["context"]
    analyst = state["analyst"]

    # Write section using either the gathered source docs from interview (context) or the interview itself (interview)
    system_message = section_writer_instructions.format(focus=analyst.description)
    response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content=f"Use this source to write your section: {context}")])
    return {"sections": [response.content]}