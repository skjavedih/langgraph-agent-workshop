import os
from dotenv import load_dotenv
load_dotenv()

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict


model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

# define the state

from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages:Annotated[list,add_messages]

def greet_user(state:State):
    """
    this function will greet the user with a message
    """
    user_message = state["messages"][0].content
    return {"messages" : [f"Hello {user_message}!"]}


def convert_to_uppercase(state:State):
    """
    This function will convert the input word in the state to uppercase
    """
    last_message = state["messages"][-1].content
    return {"messages" : [last_message.upper()]}



graph = StateGraph(State)
graph.add_node("greet_user", greet_user)
graph.add_node("convert_to_uppercase", convert_to_uppercase)

graph.add_edge(START, "greet_user")
graph.add_edge("greet_user", "convert_to_uppercase")
graph.add_edge("convert_to_uppercase", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"messages":"Javed"})
    print(result)
    print("*******************")
    print(result["messages"][-1].content)