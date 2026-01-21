import asyncio
import sys
import subprocess
import json
import websockets
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Constants
SERVER_SCRIPT = "/opt/data/docs_flow_framework/dev_tools/mcp/server.py"
WS_URI = "ws://localhost:8765"

async def verify():
    print("Starting Main Verification Logic...")
    
    # 1. Start Server Process (Stdio)
    # The server runs WS in background, so we need to give it a moment to spin up WS before we connect? 
    # Actually, verify logic: getting it running as a subprocess for MCP client usage is tricky if we also want 
    # to access the generic WS port it opens.
    # But `stdio_client` launches the process. So that process will ALSO start the WS server.
    
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("MCP Client Connected!")

            # 2. Connect to WebSocket (Control Plane)
            # Give it a second to bind port
            await asyncio.sleep(2) 
            
            try:
                async with websockets.connect(WS_URI) as ws:
                    print("WebSocket Connected!")
                    
                    # 3. List tools to verify server is responsive
                    tools = await session.list_tools()
                    print(f"Tools found: {[t.name for t in tools.tools]}")
                    assert "get_pending_batches" in [t.name for t in tools.tools]
                    
                    # Simulating the lifecycle:
                    # Ideally we want to TRIGGER a request. 
                    # But the 'server.py' implementation shows 'add_request' is internal state logic.
                    # Wait, how does the Agent TRIGGER a request in this Mock Server?
                    # Ah, in the original 'mock-mcp', the *Test Runner* intercepts an HTTP call and sends it to the server?
                    # Or does the Agent call a tool that *is* the mock?
                    # Reading logic: The Agent is the one calling `get_pending_batches`. 
                    # The `add_request` usually happens because the Test Runner (proxying the real API) caught something.
                    
                    # So in this test, we need to manually trigger `add_request` via WS? 
                    # Or does `server.py` expose a way to inject requests?
                    # Looking at `server.py`: `add_request` is an async method on `ServerState`.
                    # But it's not exposed via MCP. It's internal.
                    # AND it's not exposed via WS yet in my implementation (I left "pass" in ws_handler).
                    
                    
                    # 4. Inject a request via WebSocket
                    print("Injecting request via WebSocket...")
                    await ws.send(json.dumps({
                        "type": "inject_request",
                        "tool_name": "fetch_user",
                        "arguments": {"id": 123}
                    }))
                    
                    # Wait for confirmation or just proceed (server sends request_injected)
                    response = await ws.recv()
                    print(f"WS Response: {response}")
                    
                    # 5. Verify Agent sees it via MCP
                    pending = await session.call_tool("get_pending_batches", {})
                    print(f"Pending Batches: {pending.content}")
                    content_json = json.loads(pending.content[0].text)
                    assert len(content_json) > 0
                    batch_id = content_json[0]['id']
                    print(f"Found Batch ID: {batch_id}")
                    
                    # 6. Agent provides mock data
                    print("Agent providing mock data...")
                    await session.call_tool("provide_batch_mock_data", {
                        "batch_id": batch_id,
                        "mocks": [{
                            "request_id": content_json[0]['requests'][0]['id'],
                            "result": {"username": "test_user"},
                            "is_error": False
                        }]
                    })
                    print("Mock data provided.")
                    
                    # 7. (Optional) In a real scenario, the WS would receive the data back.
                    # But for now, verifying the MCP interaction is enough.
                    
                    print("Verification Successful!")
                    
            except ConnectionRefusedError:
                print("Failed to connect to WebSocket. Server might not be running correctly.")
                sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify())
