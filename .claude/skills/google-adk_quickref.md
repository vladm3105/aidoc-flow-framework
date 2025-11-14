# Google ADK - Quick Reference

**Skill ID:** google-adk
**Version:** 1.0.0
**Purpose:** Rapid guidance for building agentic applications with Google ADK in Python

## Quick Start

```bash
# Install
pip install google-adk

# Invoke skill
/skill google-adk

# Common requests
- "Create a conversational agent with tool integration"
- "Build a multi-agent system for data processing"
- "Design a sequential workflow agent"
- "Implement human-in-the-loop pattern"
- "Deploy agent to Cloud Run"
```

## What This Skill Does

1. Analyze agentic application requirements
2. Select appropriate agent type (LlmAgent, Sequential, Parallel, Loop, Custom)
3. Design agent architecture (single vs multi-agent)
4. Implement custom tools and integrations
5. Configure memory and state management
6. Provide deployment guidance
7. Implement evaluation and testing strategies

## Core Concepts at a Glance

### Agent Types

| Type | Purpose | When to Use | Complexity |
|------|---------|-------------|------------|
| **LlmAgent** | Dynamic, LLM-driven | Conversational, reasoning tasks | 2 |
| **Sequential Agent** | Fixed-order execution | Data pipelines, multi-step workflows | 2 |
| **Parallel Agent** | Concurrent execution | Independent operations, aggregation | 3 |
| **Loop Agent** | Iterative refinement | Generator-critic, convergence tasks | 3 |
| **Custom Agent** | User-defined logic | Domain-specific orchestration | 3 |
| **Multi-Agent** | Coordinated agents | Complex task decomposition | 4-5 |

### Tool Types

| Type | Use Case | Complexity |
|------|----------|------------|
| **Custom Function** | Python functions wrapped as tools | 2 |
| **OpenAPI** | Auto-generated from API specs | 2 |
| **MCP** | Cross-framework tool sharing | 3 |
| **Built-in** | Search, Code Execution, Google Cloud | 1 |

## Agent Type Decision Tree

```
START: What's the agent's decision pattern?
  │
  ├─> Requires natural language reasoning?
  │   └─> LlmAgent ★
  │
  ├─> Fixed sequence of steps?
  │   └─> Sequential Workflow Agent ★
  │
  ├─> Independent parallel operations?
  │   └─> Parallel Workflow Agent ★
  │
  ├─> Iterative refinement needed?
  │   └─> Loop Workflow Agent ★
  │
  ├─> Custom orchestration logic?
  │   └─> Custom Agent ★
  │
  └─> Multiple specialized agents?
      ├─> Routing to specialists? ─> Coordinator/Dispatcher ★
      ├─> Sequential stages? ─> Sequential Pipeline ★
      ├─> Parallel aggregation? ─> Fan-Out/Gather ★
      └─> Task decomposition? ─> Hierarchical ★
```

## Common Patterns

### Pattern 1: Simple Conversational Agent

```python
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

def get_weather(location: str) -> str:
    """Get current weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

agent = LlmAgent(
    name="weather_assistant",
    model="gemini-2.0-flash",
    instructions="You are a helpful weather assistant.",
    tools=[Tool.from_function(get_weather)]
)

response = agent.run("What's the weather in NYC?")
```

**Complexity:** 2

### Pattern 2: Sequential Data Pipeline

```python
from google.adk.agents import SequentialAgent

def fetch_data(id: str) -> dict:
    """Fetch data from source."""
    return {"id": id, "value": 100}

def transform_data(data: dict) -> dict:
    """Transform data."""
    return {"id": data["id"], "processed": data["value"] * 2}

def save_data(data: dict) -> str:
    """Save to database."""
    return f"Saved: {data}"

agent = SequentialAgent(
    name="data_pipeline",
    tools=[
        Tool.from_function(fetch_data),
        Tool.from_function(transform_data),
        Tool.from_function(save_data)
    ]
)

result = agent.run({"id": "123"})
```

**Complexity:** 2

### Pattern 3: Parallel Data Gathering

```python
from google.adk.agents import ParallelAgent

def get_price(symbol: str) -> float:
    """Fetch stock price."""
    return 150.25

def get_news(symbol: str) -> list:
    """Fetch news."""
    return ["News 1", "News 2"]

def get_ratings(symbol: str) -> dict:
    """Fetch analyst ratings."""
    return {"buy": 5, "hold": 2}

agent = ParallelAgent(
    name="market_researcher",
    tools=[
        Tool.from_function(get_price),
        Tool.from_function(get_news),
        Tool.from_function(get_ratings)
    ]
)

# Executes all tools in parallel
results = agent.run({"symbol": "GOOGL"})
```

**Complexity:** 3

### Pattern 4: Iterative Refinement (Loop)

```python
from google.adk.agents import LoopAgent

def generate_content(topic: str) -> str:
    """Generate content draft."""
    return f"Content about {topic}..."

def evaluate_content(content: str) -> dict:
    """Evaluate quality. Approve if score > 8."""
    score = calculate_score(content)
    return {
        "approved": score > 8,
        "feedback": "Needs improvement" if score <= 8 else "Good"
    }

agent = LoopAgent(
    name="content_generator",
    tools=[
        Tool.from_function(generate_content),
        Tool.from_function(evaluate_content)
    ],
    max_iterations=5,
    break_condition=lambda result: result.get("approved", False)
)

final_content = agent.run({"topic": "AI agents"})
```

**Complexity:** 3

### Pattern 5: Multi-Agent Coordinator

```python
from google.adk.agents import LlmAgent

# Specialized agents
weather_agent = LlmAgent(
    name="weather_specialist",
    tools=[weather_tool],
    instructions="Provide weather information"
)

finance_agent = LlmAgent(
    name="finance_specialist",
    tools=[stock_tools],
    instructions="Provide financial data"
)

# Coordinator routes to specialists
coordinator = LlmAgent(
    name="coordinator",
    agents=[weather_agent, finance_agent],
    instructions="""Route queries to appropriate specialist:
    - Weather questions → weather_specialist
    - Finance questions → finance_specialist"""
)

response = coordinator.run("What's the weather in NYC and GOOGL stock price?")
```

**Complexity:** 4

### Pattern 6: Human-in-the-Loop

```python
from google.adk.tools import Tool, ConfirmationMode

def delete_account(user_id: str) -> str:
    """Delete user account (IRREVERSIBLE)."""
    # Deletion logic
    return f"Deleted account {user_id}"

# Require human approval
delete_tool = Tool.from_function(
    delete_account,
    confirmation_mode=ConfirmationMode.ALWAYS
)

agent = LlmAgent(
    name="account_manager",
    tools=[delete_tool],
    instructions="Manage accounts. Get approval for deletions."
)

# Agent will pause for human confirmation
response = agent.run("Delete account user_123")
```

**Complexity:** 3

## Tool Development Quick Reference

### Custom Function Tool

```python
from google.adk.tools import Tool
from typing import Optional

def calculate_tax(amount: float, rate: float = 0.08) -> dict:
    """Calculate tax on an amount.

    Args:
        amount: Base amount in dollars
        rate: Tax rate as decimal (default: 0.08)

    Returns:
        dict with 'tax' and 'total' keys
    """
    tax = amount * rate
    return {"tax": round(tax, 2), "total": round(amount + tax, 2)}

# Convert to ADK tool
tax_tool = Tool.from_function(calculate_tax)
```

### Async Tool

```python
import httpx
from google.adk.tools import Tool

async def fetch_data(user_id: str) -> dict:
    """Fetch data from async API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()

# ADK handles async automatically
data_tool = Tool.from_function(fetch_data)
```

### OpenAPI Tool

```python
from google.adk.tools import Tool

# Auto-generate from OpenAPI spec
api_tools = Tool.from_openapi(
    spec_url="https://api.example.com/openapi.json",
    tool_filter=["getUserById", "createUser"]  # Optional filter
)

agent = LlmAgent(name="api_agent", tools=api_tools)
```

## Memory & State Quick Reference

### Session Management

```python
from google.adk.session import Session

session = Session(
    agent=my_agent,
    max_history_turns=10  # Retain last 10 exchanges
)

# Multi-turn conversation
response1 = session.run("What's the capital of France?")
response2 = session.run("What's its population?")  # Knows "it" = Paris
```

### State Persistence

```python
from dataclasses import dataclass

@dataclass
class UserState:
    user_id: str
    preferences: dict
    interactions: int

class StatefulAgent:
    def __init__(self):
        self.agent = LlmAgent(...)
        self.states = {}  # In-memory storage

    def run(self, user_id: str, message: str):
        if user_id not in self.states:
            self.states[user_id] = UserState(
                user_id=user_id,
                preferences={},
                interactions=0
            )

        state = self.states[user_id]
        state.interactions += 1

        return self.agent.run(
            f"User preferences: {state.preferences}\nMessage: {message}"
        )
```

## Deployment Quick Guide

### Agent Engine (Managed)

```bash
# Install CLI
pip install google-adk[cli]

# Authenticate
adk auth login

# Deploy
adk deploy \
  --agent-file agent.py \
  --agent-name my_agent \
  --project-id my-gcp-project \
  --region us-central1

# Returns: https://my-agent-{hash}.run.app
```

### Cloud Run

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
EXPOSE 8080
CMD ["python", "server.py"]
```

```bash
# Deploy
gcloud run deploy my-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Docker (Self-Hosted)

```yaml
# docker-compose.yml
version: '3.8'
services:
  agent:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    restart: unless-stopped
```

```bash
docker-compose up -d
```

## Evaluation Quick Guide

### Criteria-Based

```python
from google.adk.evaluation import evaluate_agent, Criteria

criteria = [
    Criteria(
        name="accuracy",
        description="Response is factually correct",
        rubric={"score": "1 if accurate, 0 if not"}
    )
]

results = evaluate_agent(
    agent=my_agent,
    test_cases=[
        {"input": "What's 2+2?", "expected": "4"},
        {"input": "Explain AI", "criteria": ["accuracy"]}
    ],
    criteria=criteria,
    evaluator_model="gemini-2.0-flash"
)

print(f"Pass rate: {results.pass_rate}")
```

### User Simulation

```python
from google.adk.evaluation import UserSimulator

simulator = UserSimulator(
    agent=customer_service_agent,
    user_goals=["Get refund for order #123"],
    turns_per_goal=5
)

results = simulator.run()
print(f"Success rate: {results.success_rate}")
```

## Web UI Testing

```bash
# Start API server
adk api_server --port 8000

# Start web UI (separate terminal)
cd adk-web
npm install
npm start

# Access: http://localhost:4200
```

## Complexity Ratings

| Task | Rating | Description |
|------|--------|-------------|
| Simple LlmAgent | 2 | Basic conversational agent |
| Sequential workflow | 2 | Fixed-order execution |
| Parallel workflow | 3 | Concurrent operations |
| Loop workflow | 3 | Iterative refinement |
| Custom agent | 3 | User-defined logic |
| Multi-agent coordinator (2-3) | 4 | Agent routing |
| Sequential pipeline (3+) | 4 | Chained agents |
| Hierarchical (>5 agents) | 5 | Complex nesting |
| Custom tool | 2 | Python function wrapper |
| OpenAPI tool | 2 | Auto-generated |
| MCP tool | 3 | Cross-framework |
| Agent Engine deployment | 2 | Managed service |
| Self-hosted deployment | 3 | Docker/containers |
| Advanced evaluation | 4 | Custom criteria |

## Best Practices Checklist

**Agent Design:**
- [ ] Clear, specific instructions with examples
- [ ] Single responsibility per agent
- [ ] Tool descriptions guide LLM selection
- [ ] Error handling in all tools
- [ ] Input validation on user-facing tools

**Tool Development:**
- [ ] Complete type hints
- [ ] Descriptive docstrings
- [ ] JSON-serializable return values
- [ ] Graceful error handling
- [ ] Rate limiting for external APIs

**Multi-Agent:**
- [ ] Clear agent boundaries and responsibilities
- [ ] Explicit routing logic
- [ ] Avoid circular dependencies
- [ ] Limit nesting depth (≤3 levels)

**Production:**
- [ ] Evaluation pass rate ≥80%
- [ ] Response time <30 seconds
- [ ] High-risk actions require HITL
- [ ] Logging and tracing enabled
- [ ] Resource limits configured

## Common Issues

| Issue | Cause | Quick Fix |
|-------|-------|-----------|
| Agent doesn't call tool | Vague description | Add specific, detailed tool docstring |
| Infinite loop | No break condition | Set `max_iterations` and `break_condition` |
| Tool execution fails | Unhandled exception | Add try/except, return error message |
| Slow response | Sequential calls | Use ParallelAgent or async tools |
| Context limit exceeded | Long history | Set `max_history_turns=10` |
| Deployment fails | Missing deps | Run `pip freeze > requirements.txt` |

## When NOT to Use Google ADK

**Avoid ADK when:**
- Simple script would suffice (use Python directly)
- No agent orchestration needed (use LLM SDK directly)
- Real-time <100ms latency required
- Extensive custom UI needed (ADK is backend only)
- Team unfamiliar with agent concepts
- Use case doesn't benefit from tool integration

**Alternative approaches:**
- Simple automation → Python scripts
- Complex business logic → Application code
- Real-time → Event-driven architecture
- Custom UI → Full-stack framework
- Different agent framework → LangChain, CrewAI, AutoGPT

## Resource Requirements

| Agent Type | CPU | RAM | Concurrent Requests |
|------------|-----|-----|---------------------|
| Simple LlmAgent | 1 core | 512MB | 10 |
| Workflow Agent | 2 cores | 1GB | 20 |
| Multi-Agent (3-5) | 4 cores | 2GB | 10 |
| Complex (>5 agents) | 8 cores | 4GB | 5 |

## Multi-Agent Orchestration Patterns

| Pattern | Use Case | Agents | Complexity |
|---------|----------|--------|------------|
| **Coordinator/Dispatcher** | Route to specialists | 1 coordinator + N specialists | 4 |
| **Sequential Pipeline** | Multi-stage processing | 3+ agents in sequence | 4 |
| **Parallel Fan-Out/Gather** | Aggregate multiple sources | N parallel + 1 aggregator | 4 |
| **Hierarchical** | Task decomposition | 5+ nested agents | 5 |
| **Generator-Critic** | Iterative refinement | 2 agents in loop | 4 |
| **Human-in-the-Loop** | Critical decisions | 1 agent + approval tools | 3 |

## Agent Instruction Template

```python
instructions = """You are a [ROLE] assistant for [ORGANIZATION].

**Your responsibilities:**
1. [Primary task using tool_name]
2. [Secondary task]
3. [Escalation criteria]

**Tone:** [Professional/Friendly/Concise]

**Constraints:**
- [Limit 1: e.g., Never promise refunds >$X]
- [Limit 2: e.g., Always verify identity]
- [Limit 3: e.g., Collect required info before action]

**Examples:**
User: "[Example query]"
You: "[Example response]"
"""
```

## References

**Official Docs:**
- Main: https://google.github.io/adk-docs/
- Python SDK: https://github.com/google/adk-python
- Examples: https://github.com/google/adk-samples
- Web UI: https://github.com/google/adk-web

**Installation:**
```bash
pip install google-adk
pip install google-adk[cli]  # With CLI tools
```

**Related Skills:**
- Workflow automation → `n8n`
- API design → `api-design-architect`
- Cloud deployment → `cloud-devops-expert`
- Documentation → `doc-flow`

---

**Quick Reference Version:** 1.0.0
**Full Skill:** `.claude/skills/google-adk/SKILL.md`
**Last Updated:** 2025-11-13
