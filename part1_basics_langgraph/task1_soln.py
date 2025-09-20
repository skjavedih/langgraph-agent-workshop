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

# To stream the output of the app
def stream_output(app, input):
    for output in app.stream(input):
        for key,value in output.items():
            print(f"here is output from {key}")
            print("_______")
            print(value)
            print("\n")

def classify_intent(state:State):
    """
    This function will classify the intent of the message
    """
    user_query = state["messages"][0].content

    intent_classifier_template = ChatPromptTemplate(
        [
        ('system', 'You have to classify the intent of the message. This can be either question, feedback, help, complaint, or other. Return the intent as a string.'),
        ('human', '{query}')
        ])

    intent_classifier_chain = intent_classifier_template | model

    result = intent_classifier_chain.invoke({'query': user_query})

    return {"messages": [result.content]}

def respond_to_intent(state:State):
    """
    This function will respond to the intent of the message
    """
    user_query = state["messages"][0].content
    intent = state["messages"][-1].content

    response_template = ChatPromptTemplate(
        [
        ('system', 'You are an intelligent assistant. You will respond to the user based on their message and its classified intent. Return the response as a string.'),
        ('human', 'User message: {query}\nClassified intent: {intent}')
        ])

    response_chain = response_template | model

    result = response_chain.invoke({
        'query': user_query,
        'intent': intent
    })

    return {"messages": [result.content]}


def sentiment_classifier(state:State):
    """
    This function will classify the sentiment of the message
    """
    user_query = state["messages"][0].content

    sentiment_classifier_template = ChatPromptTemplate(
        [
        ('system','You are a sentiment classifier. You will be given a message and you will need to classify the sentiment of the message. The sentiment can be positive, negative or neutral. Return the sentiment as a string.'),
        ('human','{query}')
        ])

    sentiment_classifier_chain = sentiment_classifier_template | model

    result = sentiment_classifier_chain.invoke({'query':user_query})

    return {"messages": [result.content]}



graph = StateGraph(State)
graph.add_node("classify_intent", classify_intent)
graph.add_node("respond_to_intent", respond_to_intent)

graph.add_edge(START, "classify_intent")
graph.add_edge("classify_intent", "respond_to_intent")
graph.add_edge("respond_to_intent", END)

app = graph.compile()

if __name__ == "__main__":
    # result = app.invoke({"messages": "I have to go to citycenter mall. can you tell me the shortest route to reach there?"})
    result = app.invoke({"messages": "I am not happy with the product. I want to return it."})
    print(result)

    # stream_output(app, {"messages": "I am not happy with the product. I want to return it."})