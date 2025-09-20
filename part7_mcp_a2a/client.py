# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()


model = ChatOpenAI(model="gpt-4.1", temperature=0)

server_params = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py fileß
    args=["/Users/sumanpaul/Documents/ds_projects/study/langgraph_course/src/mcp/math_server.py"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 7) x 12?"})
            print(agent_response['messages'][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
