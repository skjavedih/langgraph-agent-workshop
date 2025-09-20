import os
from dotenv import load_dotenv
load_dotenv()

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

class State(TypedDict):
    messages:Annotated[list,add_messages]

def get_response_from_llm(state: State):
    """
    This function will get the response from the LLM
    """
    user_input = state["messages"][0].content
    response = model.invoke(user_input).content
    return {"messages": [response]}


def convert_to_uppercase(state:State):
    """
    This function will convert the message to uppercase
    """
    response_from_llm = state["messages"][-1].content
    uppercase_output = response_from_llm.upper()
    
    return {"messages": [uppercase_output]}

# define the workflow

workflow = StateGraph(State)
workflow.add_node("LLM_response" , get_response_from_llm)
workflow.add_node("Uppercase_converter" , convert_to_uppercase)
workflow.add_edge(START , "LLM_response")
workflow.add_edge("LLM_response" , "Uppercase_converter")
workflow.add_edge("Uppercase_converter" , END)
app = workflow.compile()


if __name__ == "__main__":
    result = app.invoke({"messages": "Hello, how are you?"})
    print(result["messages"][-1].content)