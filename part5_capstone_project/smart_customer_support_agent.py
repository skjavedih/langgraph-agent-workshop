import os 
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage , AIMessage , SystemMessage
from typing import TypedDict , Annotated
from pydantic import BaseModel , Field
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder , PromptTemplate
import json
from langchain_core.messages import messages_to_dict


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    question: Annotated[str, None]
    intent_classification: Annotated[str, None]
    sales_resolution: Annotated[str, None]
    customer_support_resolution: Annotated[str, None]

model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

class IntentClassification(BaseModel):
    """
    Classify the intent of the user's message.
    """
    intent: Literal["Sales Inquiry", "Technical Support"] = Field(description="The intent of the user's message")

intent_classification_llm = model.with_structured_output(IntentClassification)

class SalesResolution(BaseModel):
    """
    Generate a appropriate response for the user's message depending upon the user question on sales
    """
    response: str = Field(description="The response to the user's message")

sales_resolution_llm = model.with_structured_output(SalesResolution)

class CustomerSupportResolution(BaseModel):
    """
    Generate a appropriate response for the user's message depending upon the user question on customer support
    """
    response: str = Field(description="The response to the user's message")

customer_support_resolution_llm = model.with_structured_output(CustomerSupportResolution)

#define the nodes

#set the initial state
def init(state):
    """
    Initialize the state of the graph.
    """
    return {"messages": [],
            "intent_classification": None,
            "sales_resolution": None,
            "customer_support_resolution": None}


#intent classification node
def classify_intent(state):
    """
    Classify the intent of the user's message.
    """
    user_input = state["messages"][0]

    prompt = PromptTemplate(
        template="""You are a customer support agent. You are given a user's message.
        You need to classify the intent of the user's message {user_input}
        The intent can be either Sales Inquiry or Technical Support.
        Respond in json format with the following keys:
        intent: The intent of the user's message""",
        input_variables=["user_input"],
    )

    intent_chain = prompt | intent_classification_llm
    intent_output = intent_chain.invoke({"user_input": user_input})
    return {"intent_classification": intent_output.intent,
            "messages": [AIMessage(content=intent_output.intent)],
            "question": user_input.content}

#sales resolution node
def sales_resolution(state):
    """
    Generate a response for the user's message.
    """
    user_input = state["messages"][0]
    prompt = PromptTemplate(
        template="""You are a customer support agent. You are given a user's message.
        You need to generate a response for the user's message {user_input}
        The response should be in a friendly and helpful tone.
        Respond in json format with the following keys:
        response: The response to the user's message""",
        input_variables=["user_input"],
    )
    sales_chain = prompt | sales_resolution_llm
    sales_output = sales_chain.invoke({"user_input": user_input})
    return {"sales_resolution": sales_output.response,
            "messages": [AIMessage(content=sales_output.response)]}

#customer support resolution node
def customer_support_resolution(state):
    """
    Generate a response for the user's message.
    """
    user_input = state["messages"][0]
    prompt = PromptTemplate(
        template="""You are a customer support agent. You are given a user's message.
        You need to generate a response for the user's message {user_input}
        The response should be in a friendly and helpful tone.
        Respond in json format with the following keys:
        response: The response to the user's message""",
        input_variables=["user_input"],
    )
    customer_support_chain = prompt | customer_support_resolution_llm
    customer_support_output = customer_support_chain.invoke({"user_input": user_input})
    return {"customer_support_resolution": customer_support_output.response,
            "messages": [AIMessage(content=customer_support_output.response)]}

def route_intent(state):
    """
    Route the user's message to the appropriate resolution node.
    """
    return state["intent_classification"]

#define the workflow

workflow = StateGraph(GraphState)
workflow.add_node("init", init)
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("sales_resolution", sales_resolution)
workflow.add_node("customer_support_resolution", customer_support_resolution)

workflow.add_edge(START, "init")
workflow.add_edge("init", "classify_intent")
workflow.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "Sales Inquiry": "sales_resolution",
        "Technical Support": "customer_support_resolution"
    }
)
workflow.add_edge("sales_resolution", END)
workflow.add_edge("customer_support_resolution", END)
app = workflow.compile()


if __name__ == "__main__":
    result = app.invoke(
        {"messages":[HumanMessage(content="I'm interested in your pricing plans")]}
    )
    #save it in json file
    serializable_result = result.copy()
    serializable_result['messages'] = messages_to_dict(serializable_result['messages'])
    with open("result.json", "w") as f:
        json.dump(serializable_result, f, indent=2)
    print(result)
