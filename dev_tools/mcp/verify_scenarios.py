import asyncio
import sys
import subprocess
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Constants
SERVER_SCRIPT = "/opt/data/docs_flow_framework/dev_tools/mcp/server.py"

async def verify_scenarios():
    print("Starting Scenario Verification...")
    
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("MCP Client Connected!")

            # Check if scenarios were auto-loaded
            pending = await session.call_tool("get_pending_batches", {})
            content = pending.content[0].text
            print(f"Pending Batches: {content}")
            
            batches = json.loads(content)
            
            # Expect 2 batches from scenarios.yaml
            if len(batches) >= 2:
                print("SUCCESS: Scenarios loaded correctly.")
                tools = [b['requests'][0]['tool_name'] for b in batches]
                print(f"Loaded Scenario Tools: {tools}")
                assert "fetch_market_data" in tools
                assert "analyze_sentiment" in tools
            else:
                print("FAILURE: Scenarios not loaded.")
                sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify_scenarios())
