from typing import Annotated

from langchain_tavily import TavilySearch
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.types import Command, interrupt

from langchain_core.messages import HumanMessage
import uuid

from dotenv import load_dotenv
load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

memory = MemorySaver()

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

search_tool = TavilySearch(max_results=2)
tool_list = [search_tool, human_assistance]
llm_with_tools = model.bind_tools(tool_list)

def tool_calling_llm(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


workflow  = StateGraph(State)
workflow.add_node("llm_with_tools", tool_calling_llm)
workflow.add_node("tools", ToolNode(tools=tool_list))

workflow.add_edge(START, "llm_with_tools")
workflow.add_conditional_edges(
    "llm_with_tools",
    tools_condition,
)
workflow.add_edge("tools", "llm_with_tools")

app_human = workflow.compile(checkpointer=memory)


if __name__ == "__main__":
    thread_id = "1"
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    print("Human-in-the-Loop Agent is running.")
    print("Type your query, or 'exit'/'quit' to end the session.")

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Ending conversation.")
            break

        initial_messages = [HumanMessage(content=user_input)]

        try:
            print("---")
            events = app_human.stream(
                {"messages": initial_messages}, 
                config,
                stream_mode="values",
            )
            for event in events:
                if "messages" in event:
                    event["messages"][-1].pretty_print()

        except Exception as e:
            if "Interrupt" in e.__class__.__name__:
                print("\n--- HUMAN INTERVENTION REQUIRED ---")
                
                # The query from the `human_assistance` tool is in the exception arguments
                interrupt_query = e.args[0].get("query", "No query provided.")
                print(f"AI is asking: {interrupt_query}")
                
                human_feedback = input("Your response: ")

                # Resume the graph with the human's input
                # We wrap it in a dictionary to match what the tool expects: `return human_response["data"]`
                resume_command = Command(resume={"data": human_feedback})
                
                print("---")
                resume_events = app_human.stream(
                    None,  # No new messages, just resuming
                    config,
                    resume=resume_command,
                    stream_mode="values",
                )
                for event in resume_events:
                    if "messages" in event:
                        event["messages"][-1].pretty_print()
            else:
                print(f"\nAn unexpected error occurred: {e}")
                break
