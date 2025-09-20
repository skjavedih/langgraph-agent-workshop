# Part 1: Basics of LangGraph

This folder contains introductory examples and a notebook to help you get started with the basics of building workflows using Langgraph

## Contents

- **1_simple_workflow.py**  
  Demonstrates how to define a simple workflow graph with two nodes:
  1. `greet_user`: Greets the user using their input.
  2. `convert_to_uppercase`: Converts the greeting message to uppercase.
  
  The workflow is defined using `StateGraph`, and the script shows how to invoke the workflow with a sample input.

- **2_llm_function.py**  
  Extends the previous example by integrating an LLM (OpenAI GPT-4.1-mini) into the workflow:
  1. `get_response_from_llm`: Sends the user's message to the LLM and stores the response.
  2. `convert_to_uppercase`: Converts the LLM's response to uppercase.
  
  This script demonstrates how to use an LLM as a node in a LangGraph workflow.

- **session1_basics_langgraph.ipynb**  
  An interactive Jupyter notebook that walks through:
  - Setting up the environment and loading dependencies.
  - Defining utility functions for displaying graphs and streaming output.
  - Step-by-step construction of simple workflow graphs.
  - Integrating LLMs into workflows.
  - Visualizing and experimenting with the workflow graph interactively.

- ** How to Add Keys.
1. Open API keys - 
  • Go to open api site -https://platform.openai.com/api-keys 
  • Next Loged in or sign up with your google account.
  • Then create your API key by cliking on the create key button.

2. How to get TAVILY_API_KEY 
  • Visit https://app.tavily.com/ and create an account.
	•	Log in and go to your dashboard to generate or view your API key.
	•	Set this key as the environment variable `TAVILY_API_KEY` for secure usage in applications.

  Why It Is Required
	•	The TAVILY_API_KEY allows secure usage of Tavily’s Search API, which is designed specifically for AI 
    agents and Retrieval-Augmented Generation (RAG) workflows.
	•	It enables programmatic access to web search and contextual content extraction, letting AI tools like   
    LangGraph or LangChain execute real-time and accurate web searches as part of their logic.
	•	The API key verifies identity and usage limits, ensuring private and authorized operations.
    Thus, the TAVILY_API_KEY is essential for integrating real-time search and retrieval capabilities into AI-powered apps, including LangGraph projects

3. How to get Google key

## Getting Started


1. **Run the scripts**  

   - To run the simple workflow:

     ```
        python part1_basics_langgraph/1_simple_workflow.py
     ```

   - To run the LLM workflow:
     ```
        python part1_basics_langgraph/2_llm_function.py
     ```

2. **Explore the notebook**  
   - Open `session1_basics_langgraph.ipynb` in Jupyter or VSCode to interactively explore and modify the workflows.

## Concepts Demonstrated

- **State Management:** Using Python dictionaries and `TypedDict` to manage workflow state.
- **Workflow Graphs:** Building and connecting nodes using LangGraph's `StateGraph`.
- **Node Functions:** Creating modular functions for each step in the workflow.
- **LLM Integration:** Calling an LLM as part of a workflow node.
- **Visualization:** (In the notebook) Visualizing the workflow graph and streaming outputs.


