import os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import Annotated, Optional, Literal
from typing_extensions import TypedDict
from typing import List
from langgraph.graph.message import AnyMessage, add_messages
from prompts import AGENT_SYSTEM_PROMPT
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()
# Create MCP client for Multiple Server
async def get_mcp_tools():
    client = MultiServerMCPClient({
        "Arxiv MCP Tool":{
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http"
        }
    })

    return await client.get_tools()

# Avaliable MCP tools
tools = asyncio.run(get_mcp_tools())
print("Loaded tools:", tools)

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER_FOR_CHAT")
MODEL_NAME = os.getenv("MODEL_NAME_FOR_CHAT")
llm = init_chat_model(
    MODEL_PROVIDER+":"+MODEL_NAME,
    temperature=0.2

)


# State for the graph
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# Chat function that invokes the LLM with tools
async def chat(state: State):
    recent_messages = state["messages"]
    # print(recent_messages)
    all_messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + recent_messages
    llm_with_tools = llm.bind_tools(tools)
    response = await llm_with_tools.ainvoke(all_messages)
    return {"messages": [response]}



def build_graph():

    checkpointer = MemorySaver()
    builder = StateGraph(State)

    # Add nodes
    builder.add_node("chat_bot", chat)
    builder.add_node("tools", ToolNode(tools))

    # Add conditional edges based on whether tool should be invoked
    builder.add_edge(START, "chat_bot")
    builder.add_conditional_edges("chat_bot", tools_condition, {"tools": "tools", END:END})
    builder.add_edge("tools", "chat_bot")

    return builder.compile(checkpointer=checkpointer)

async def run_chat_loop():

    graph_memory_update = build_graph()

    config = {
        "configurable":
        {"thread_id":"chebrolu"}
    }
    
    state = {"messages": []}
    print("💬 Start chatting with the AI (type 'exit' to quit)\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            break
        
        async for event in graph_memory_update.astream({"messages": [HumanMessage(content=user_input)]}, config):
            for value in event.values():
                print("Assistant: -------------------------------\n", value["messages"][-1].content)
        


if __name__ == "__main__":
    
    asyncio.run(run_chat_loop())