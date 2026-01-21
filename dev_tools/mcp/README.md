# Mock MCP Server (Python)

A Python-based Mock MCP Server for testing AI Agents. It acts as a bridge between your Test Runner and the Agent under test.

## Features
- **MCP Server**: Exposes tools for Agents to request mocks (`get_pending_batches`) and receive data (`provide_batch_mock_data`).
- **WebSocket Bridge**: Allows your Test Runner to register expected mocks and intercept requests in real-time.

## Installation

```bash
uv pip install -r requirements.txt
# OR
pip install .
```

## Usage

### 1. Start the Server
```bash
python server.py
```
This starts:
- MCP Server over Stdio (for the Agent).
- WebSocket Control Plane on `ws://localhost:8765` (for the Test Runner).

### 2. Connect from Test Runner
Connect to `ws://localhost:8765` to listen for `new_request` events.

### 3. Configure Agent
Point your Agent to use this server (e.g., via `python server.py` command).

## API

### MCP Tools
- `get_pending_batches()`: Returns list of pending mock requests.
- `provide_batch_mock_data(batch_id, mocks)`: Submit mock data for a batch.

### WebSocket Events
- **Server -> Client**:
  ```json
  {
    "type": "new_request",
    "batch_id": "...",
    "request": { ... }

## Project Emulation (Scenarios)

You can use a `scenarios.yaml` file to pre-load a set of mock requests. This allows you to emulate project activity (e.g. pending agent requests) without needing a live Test Runner connected via WebSocket.

### 1. Create `scenarios.yaml`
Place a `scenarios.yaml` file in the same directory as `server.py`:

```yaml
scenarios:
  - tool: "fetch_market_data"
    params: 
      symbol: "AAPL"
  - tool: "analyze_sentiment"
    params:
      text: "Market is looking bullish today."
```

### 2. Run Server
When you start the server, it will automatically load these scenarios as "pending batches":

```bash
python server.py
```

### 3. Agent Interaction
When your Agent connects and calls `get_pending_batches()`, it will receive these requests immediately.

