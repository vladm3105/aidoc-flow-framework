import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

import websockets
from websockets.server import WebSocketServerProtocol
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-mcp")

# --- Data Models (Same as before) ---

class MockRequest(BaseModel):
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class MockResponse(BaseModel):
    request_id: str
    result: Any
    is_error: bool = False

class Batch(BaseModel):
    id: str
    requests: List[MockRequest]

# --- State Management (Same as before) ---

import yaml
import os

# --- State Management (Same as before) ---

class ServerState:
    def __init__(self):
        self.pending_batches: Dict[str, Batch] = {}
        self.mock_responses: Dict[str, MockResponse] = {}
        self.test_runner_ws: Optional[WebSocketServerProtocol] = None
        
    async def register_runner(self, ws: WebSocketServerProtocol):
        self.test_runner_ws = ws
        logger.info("Test runner connected")

    async def add_request(self, tool_name: str, arguments: Dict[str, Any], initial_response: Any = None) -> str:
        req_id = str(uuid4())
        batch_id = str(uuid4())
        
        req = MockRequest(id=req_id, tool_name=tool_name, arguments=arguments)
        self.pending_batches[batch_id] = Batch(id=batch_id, requests=[req])
        
        # If we have a pre-defined response (from scenarios.yaml), store it immediately
        # so when the agent calls provide_batch_mock_data, it might be a no-op or verification step.
        # WAIT. The Agent CALLS `provide_batch_mock_data` to PROVIDE data.
        # But if we are EMULATING connectivity, we want the Agent to SEE the request.
        # Then the Agent provides data because it thinks it's real.
        # The `initial_response` in yaml is actually what we expect the Agent to Produce? 
        # OR is it that we want to auto-respond?
        # NO. The Agent is the one being tested.
        # We inject a REQUEST (e.g. "Fetch Market Data").
        # The Agent sees it, fetches real data (or whatever logic it has), and calls `provide_batch_mock_data`.
        # So `scenarios.yaml` just needs to inject REQUESTS.
        
        logger.info(f"Added pending request: {tool_name} (ID: {req_id})")
        
        if self.test_runner_ws:
             await self.test_runner_ws.send(json.dumps({
                 "type": "new_request",
                 "batch_id": batch_id,
                 "request": req.model_dump()
             }))
        
        return req_id

    def add_response(self, response: MockResponse):
        logger.info(f"Received response for {response.request_id}")
        self.mock_responses[response.request_id] = response
    
    def load_scenarios(self, filename: str = "scenarios.yaml"):
        if not os.path.exists(filename):
            logger.info("No scenarios.yaml found.")
            return

        try:
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)
                scenarios = data.get("scenarios", [])
                for s in scenarios:
                    tool = s.get("tool")
                    args = s.get("params", {})
                    # We can't await here in sync method, so we just modify dict directly
                    # reusing logic from add_request but synchronous
                    req_id = str(uuid4())
                    batch_id = str(uuid4())
                    req = MockRequest(id=req_id, tool_name=tool, arguments=args)
                    self.pending_batches[batch_id] = Batch(id=batch_id, requests=[req])
                    logger.info(f"Loaded scenario: {tool}")
        except Exception as e:
            logger.error(f"Failed to load scenarios: {e}")

state = ServerState()

# --- MCP Server Setup ---

app = Server("mock-mcp-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_pending_batches",
            description="Retrieve all pending batches of requests that need mocking.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="provide_batch_mock_data",
            description="Provide mock data for a specific batch.",
            inputSchema={
                "type": "object",
                "required": ["batch_id", "mocks"],
                "properties": {
                    "batch_id": {"type": "string"},
                    "mocks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "request_id": {"type": "string"},
                                "result": {"type": "object"}, # or any
                                "is_error": {"type": "boolean"}
                            }
                        }
                    }
                },
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "get_pending_batches":
        batches = [batch.model_dump() for batch in state.pending_batches.values()]
        return [types.TextContent(type="text", text=json.dumps(batches))]
    
    elif name == "provide_batch_mock_data":
        batch_id = arguments.get("batch_id")
        mocks = arguments.get("mocks", [])
        
        if batch_id not in state.pending_batches:
            return [types.TextContent(type="text", text=f"Error: Batch {batch_id} not found")]

        # Remove from pending
        del state.pending_batches[batch_id]

        # In a real impl, we'd send these BACK to the WebSocket so the runner can resume.
        # For this MVP, we just ack.
        return [types.TextContent(type="text", text="Mocks received")]
    
    raise ValueError(f"Unknown tool: {name}")

# --- WebSocket Server ---

async def ws_handler(websocket): 
    await state.register_runner(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "inject_request":
                tool_name = data.get("tool_name")
                arguments = data.get("arguments", {})
                await state.add_request(tool_name, arguments)
                # We don't send request_id back in this simple version unless needed
                await websocket.send(json.dumps({
                    "type": "request_injected"
                }))
    except Exception as e:
        logger.error(f"WS Error: {e}")
    finally:
        state.test_runner_ws = None

async def run_ws():
    async with websockets.serve(ws_handler, "localhost", 8765):
        await asyncio.Future() # run forever

# --- Main Entrypoint ---

async def main():
    # Load scenarios on startup
    state.load_scenarios()

    # Run MCP server and WebSocket server concurrently
    
    async def run_mcp():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    # We use gather to run both
    await asyncio.gather(
        run_ws(),
        run_mcp()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
