# Mock A2A Server (HTTP/REST)

A specialized Mock Server for testing **Agent-to-Agent (A2A)** communication over HTTP. It mocks REST endpoints defined in a configuration file.

## Features
- **Generic Protocol**: Works for any HTTP-based agent communication.
- **Scenario Matching**: Responses matches against `scenarios.yaml` based on Method and Path.
- **Control Plane**: WebSocket visibility into received requests (TODO integration).

## Installation

```bash
uv pip install -r requirements.txt
```

## Usage

### 1. Configure Scenarios
Edit `scenarios.yaml`. You can use exact paths or dynamic patterns.

#### Exact Match
```yaml
  - method: "GET"
    path: "/api/v1/market/status"
    response:
      status: 200
      body: { "is_open": true }
```

#### Dynamic Match & Latency (v2)
Use `{param}` in paths to capture values, and use `{param}` in response bodies to echo them back.
Add `latency` (in ms) to simulate network delay.

```yaml
  - method: "GET"
    path: "/users/{user_id}"
    latency: 500  # Simulate 500ms delay
    response:
      status: 200
      body: 
        id: "{user_id}"
        message: "Hello user {user_id}"
```

### 2. Run Server


```bash
python server.py
# Listen on http://localhost:8000
```

### 3. Point Agents
Configure your Agents to send A2A requests to `http://localhost:8000`.

## API

- **Any Path**: Matches against scenarios.
- `GET /_sys/pending`: View log of received requests.
- `WS /ws/control`: Real-time stream of received requests.
