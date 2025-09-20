import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Annotated

# Initialize LLM
model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

# Define State
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 1. Calculate BMI
def calculate_bmi(weight_kg, height_cm):
    """
    Calculate BMI and return category.
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 24.9:
        category = "Normal weight"
    elif bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obese"
    
    return f"Your BMI is {bmi:.2f}, which falls in the '{category}' category."

# 2. Calculate Daily Calorie Needs
def calculate_calories(weight_kg, height_cm, age, gender="male"):
    """
    Calculate daily calorie needs using Mifflin-St Jeor Equation.
    """
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    return f"Estimated daily calorie requirement: {round(bmr)} kcal."

tool_list = [calculate_bmi, calculate_calories]
llm_with_tools = model.bind_tools(tool_list)


def tool_calling_llm(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

from langgraph.prebuilt import ToolNode, tools_condition

# Workflow Setup
workflow = StateGraph(State)
workflow.add_node("llm_with_tools", tool_calling_llm)
workflow.add_node("tools", ToolNode(tool_list))
workflow.add_edge(START, "llm_with_tools")
workflow.add_conditional_edges(
    "llm_with_tools",
      tools_condition
      )
workflow.add_edge("tools", "llm_with_tools")
app = workflow.compile()

if __name__ == "__main__":
    user_query = "I am 30 male, 160 cm tall and weigh 75 kg. Calculate my BMI and daily calorie needs."
    result = app.invoke({"messages": user_query})
    print(result["messages"][-1].content)

    for m in result['messages']:
        m.pretty_print()
