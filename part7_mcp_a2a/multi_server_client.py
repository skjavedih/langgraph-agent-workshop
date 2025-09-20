
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
from dotenv import load_dotenv

load_dotenv()
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4.1", temperature=0)

async def main():
    client = MultiServerMCPClient(
        connections={
            "math": {
                "command": "python",
                "args": [
                    "/Users/sumanpaul/Documents/ds_projects/study/langgraph_course/src/mcp/math_server.py"
                ],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )

    tools = await client.get_tools()
    agent = create_react_agent(model, tools)
    math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
    print(f"Math response: {math_response['messages'][-1].content}")
    
    weather_response = await agent.ainvoke({"messages": "what is the weather in nyc?"})
    print(f"Weather response: {weather_response['messages'][-1].content}")
    # Remove the client.stop() line - it doesn't exist for this client

if __name__ == "__main__":
    asyncio.run(main())

