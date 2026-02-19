import os
import requests
from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from .tools import get_lol_player_stats

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

agent_tools = [get_lol_player_stats]

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
llm_with_tools = llm.bind_tools(agent_tools)

def agent_node(state: AgentState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

tool_node = ToolNode(agent_tools)

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def run_agent(user_input: str, thread_id: str, user_profile=None):
    """
    We'll be calling this function from Django View
    user_profile is instance Profile model of logged in user.
    """

    system_text = "You're an Nexus AI, smart assistent for League of Legends."
    
    if user_profile and user_profile.game_name:
        system_text += f"\nYou're talking to: {user_profile.game_name}#{user_profile.tag_line}."
        system_text += f"\nHis PUUID is: {user_profile.puuid}."
        system_text += "\nIf the user asks about his stats, use his game_name and tag_line."
    else:
        system_text += "\nUser doesn't have his account connected yet."

    config = {"configurable": {"thread_id": thread_id}}
    
    inputs = {
        "messages": [
            SystemMessage(content=system_text),
            HumanMessage(content=user_input)
        ]
    }

    final_response = ""
    
    for event in app.stream(inputs, config=config, stream_mode="values"):
        last_msg = event["messages"][-1]
        if last_msg.type == "ai" and not last_msg.tool_calls:
            final_response = last_msg.content

    return final_response