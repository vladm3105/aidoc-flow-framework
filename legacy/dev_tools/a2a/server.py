import asyncio
import yaml
import os
import json
import logging
import re
from typing import Any, Dict, List, Optional, Pattern, Tuple
from uuid import uuid4

from fastapi import FastAPI, Request, HTTPException, WebSocket, Response
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-a2a")

app = FastAPI(title="Mock A2A Server")

# --- Data Models ---

class Scenario(BaseModel):
    method: str
    path: str
    response: Dict[str, Any] # status, body, headers
    latency: Optional[int] = 0 # ms

# --- State Management ---

class ServerState:
    def __init__(self):
        self.scenarios: List[Dict[str, Any]] = []
        # Store compiled regex patterns: (scenario_index, regex_pattern)
        self.compiled_paths: List[Tuple[int, Pattern]] = []
        self.pending_requests: List[Dict[str, Any]] = [] 
        self.control_ws: Optional[WebSocket] = None

    def compile_path(self, path: str) -> Pattern:
        # Convert /users/{id} -> ^/users/(?P<id>[^/]+)$
        # Escape existing regex chars first? Assuming simple paths for now.
        # Check if it has {param}
        if '{' in path and '}' in path:
            regex_path = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', path)
            return re.compile(f"^{regex_path}$")
        return re.compile(f"^{re.escape(path)}$")

    def load_scenarios(self, filename: str = "scenarios.yaml"):
        # Helper to find absolute path
        if not os.path.isabs(filename):
             filename = os.path.join(os.path.dirname(__file__), filename)

        if not os.path.exists(filename):
            logger.error(f"No scenarios.yaml found at {filename}")
            return
        
        try:
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)
                self.scenarios = data.get("scenarios", [])
                
                # Compile regexes
                self.compiled_paths = []
                for i, s in enumerate(self.scenarios):
                    path = s.get("path")
                    if path:
                        pattern = self.compile_path(path)
                        self.compiled_paths.append((i, pattern))

                logger.info(f"Loaded {len(self.scenarios)} scenarios from {filename}")
        except Exception as e:
            logger.error(f"Failed to load scenarios: {e}")

    async def match_request(self, method: str, path: str, body: Any = None) -> Tuple[Optional[Dict[str, Any]], Dict[str, str]]:
        # Returns (ResponseDef, PathParams)
        
        for i, pattern in self.compiled_paths:
            s = self.scenarios[i]
            s_method = s.get("method").upper()
            
            if s_method == method.upper():
                match = pattern.match(path)
                if match:
                    return s, match.groupdict()
        
        logger.warning(f"No match for {method} {path}")
        return None, {}

    async def log_request(self, method: str, path: str, body: Any):
        req_id = str(uuid4())
        record = {
            "id": req_id,
            "method": method,
            "path": path,
            "body": body
        }
        self.pending_requests.append(record)
        
        # Notify Control Plane
        if self.control_ws:
            try:
                await self.control_ws.send_json({
                    "type": "request_received",
                    "request": record
                })
            except Exception:
                self.control_ws = None
    
    def template_response(self, data: Any, params: Dict[str, str]) -> Any:
        # Recursively replace {var} in strings
        if isinstance(data, str):
            try:
                return data.format(**params)
            except KeyError:
                return data # Graceful fallback
        elif isinstance(data, dict):
            return {k: self.template_response(v, params) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.template_response(i, params) for i in data]
        return data

state = ServerState()

# --- Routes ---

@app.on_event("startup")
async def startup_event():
    state.load_scenarios()

@app.websocket("/ws/control")
async def control_websocket(websocket: WebSocket):
    await websocket.accept()
    state.control_ws = websocket
    logger.info("Control plane connected")
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        logger.info("Control plane disconnected")
        state.control_ws = None

@app.get("/_sys/pending")
async def get_pending():
    return state.pending_requests

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(path: str, request: Request):
    """
    Catch-all for all API traffic. Matches against scenarios.
    """
    method = request.method
    normalized_path = "/" + path if not path.startswith("/") else path
    
    try:
        body = await request.json()
    except Exception:
        body = None 
        
    await state.log_request(method, normalized_path, body)
    
    scenario, params = await state.match_request(method, normalized_path, body)
    
    if scenario:
        # 1. Latency
        latency = scenario.get("latency", 0)
        if latency > 0:
            await asyncio.sleep(latency / 1000.0)

        # 2. Response Def
        response_def = scenario.get("response", {})
        status = response_def.get("status", 200)
        resp_body = response_def.get("body", {})
        
        # 3. Templating
        final_body = state.template_response(resp_body, params)

        return Response(
            content=json.dumps(final_body),
            status_code=status,
            media_type="application/json"
        )
    
    raise HTTPException(status_code=404, detail=f"No mock defined for {method} {normalized_path}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8002, reload=True)
