---
skill_id: google-adk
name: Google Agent Development Kit (ADK)
description: Develop agentic software and multi-agent systems using Google ADK in Python
version: 1.0.0
created: 2025-11-13
complexity: 3
---

# Google Agent Development Kit (ADK) Skill

## Purpose

Provide specialized guidance for developing agentic applications and multi-agent systems using Google's Agent Development Kit (ADK). Enable AI assistants to design agents, build tools, orchestrate multi-agent workflows, implement memory/state management, and deploy agent-based applications following code-first development patterns.

## When to Use This Skill

Invoke this skill when:

- Building conversational AI agents with tool integration
- Creating multi-agent orchestration systems
- Developing workflow agents (sequential, parallel, iterative)
- Implementing custom tools for agents
- Designing agent architectures for complex tasks
- Deploying agent applications to production
- Evaluating agent performance and behavior
- Implementing human-in-the-loop patterns

Do NOT use this skill for:

- Generic Python development (use Python-specific skills)
- Simple REST API development (ADK is for agentic systems)
- Frontend development (ADK is backend agent framework)
- Direct LLM API usage without agent orchestration (use LLM provider SDKs)
- Non-Python agent frameworks (LangChain, CrewAI, AutoGPT - different patterns)

## Core ADK Concepts

### Platform Architecture

**Framework Philosophy:**
- **Code-first approach** - Define agents in Python code (not YAML/JSON configs)
- **Model-agnostic** - Optimized for Gemini but supports other LLMs
- **Composable** - Build complex systems from simple agent primitives
- **Observable** - Built-in integration with tracing and monitoring tools

**Supported Languages:**
- **Python** (primary, most mature) - `google-adk` package
- **Go** (available) - `adk-go` repository
- **Java** (available) - `adk-java` repository

**Runtime Environment:**
- Python 3.9+ required
- Agent Engine for deployment (containerized execution)
- Web UI for development/testing (Angular + FastAPI)
- CLI for evaluation and deployment operations

### Agent Types and Hierarchy

**1. LlmAgent** (Dynamic, model-driven)

*Use for:*
- Conversational interfaces
- Decision-making with uncertainty
- Natural language understanding
- Creative tasks (content generation)
- Contextual reasoning

*Characteristics:*
- Uses LLM for decision-making
- Non-deterministic execution
- Tool selection driven by model
- Handles ambiguous inputs

**2. Workflow Agents** (Deterministic, programmatic)

*Sequential Agent:*
- Executes tools in fixed order
- Use for: Multi-step processes with dependencies
- Example: Data pipeline (fetch → transform → load)

*Parallel Agent:*
- Executes multiple tools concurrently
- Use for: Independent operations requiring aggregation
- Example: Multi-source data gathering

*Loop Agent:*
- Repeats execution until condition met
- Use for: Iterative refinement, convergence tasks
- Example: Generator-critic pattern

**3. Custom Agents** (User-defined logic)

*Use for:*
- Domain-specific orchestration
- Complex state machines
- Integration with existing systems
- Specialized execution patterns

**Agent Composition:**
- Agents can contain sub-agents (hierarchical)
- Parent agent coordinates child agents
- Supports multi-level nesting

### Tool Ecosystem

**Tool Categories:**

1. **Built-in Tools**:
   - **Search** - Web search via Google Search API
   - **Code Execution** - Python code interpreter (sandboxed)
   - **Google Cloud tools** - Vertex AI, BigQuery, Cloud Storage

2. **Custom Function Tools**:
   - Python functions wrapped as tools
   - Automatic schema generation from type hints
   - Supports async functions

3. **OpenAPI Tools**:
   - Auto-generate from OpenAPI/Swagger specs
   - HTTP-based service integration

4. **MCP (Model Context Protocol) Tools**:
   - Integration with MCP servers
   - Cross-framework tool sharing

**Tool Attributes:**
- **Name** - Unique identifier
- **Description** - Natural language explanation for LLM
- **Parameters** - JSON schema defining inputs
- **Function** - Execution logic
- **Confirmation** - Optional human-in-the-loop approval

### Memory and State Management

**Session Management:**
- Agent maintains conversation history
- Automatic context window management
- Configurable history retention

**State Persistence:**
- Custom state objects per agent
- Serialization support (JSON, pickle)
- Database integration for long-term storage

**Context Caching:**
- Reduces token usage for repeated context
- Automatic cache invalidation
- Configurable cache TTL

## Agent Development Methodology

### Planning Phase

**Step 1: Define Agent Purpose**
- Primary objective (single responsibility)
- Input/output format
- Success criteria
- Failure modes

**Step 2: Identify Required Tools**

Decision criteria:
- Use **built-in tools** when available (Search, Code Execution)
- Create **custom functions** for simple operations (<100 lines)
- Use **OpenAPI tools** for existing REST APIs
- Use **MCP tools** for cross-framework compatibility

**Step 3: Select Agent Type**

```
START: What's the agent's decision pattern?
  │
  ├─> Requires natural language reasoning? ─Yes─> LlmAgent ★
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
  └─> Custom orchestration logic?
      └─> Custom Agent ★
```

**Step 4: Design Multi-Agent Architecture** (if needed)

Patterns:
- **Coordinator/Dispatcher** - Central agent routes to specialists
- **Sequential Pipeline** - Output of Agent A → Input of Agent B
- **Parallel Fan-Out/Gather** - Distribute work, aggregate results
- **Hierarchical Decomposition** - Break complex task into subtasks

### Implementation Phase

**Basic LlmAgent Structure:**

```python
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

# Define custom tool
def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name or coordinates

    Returns:
        Weather description
    """
    # Implementation
    return f"Weather in {location}: Sunny, 72°F"

# Create agent
agent = LlmAgent(
    name="weather_assistant",
    model="gemini-2.0-flash",
    instructions="""You are a helpful weather assistant.
    Use the get_weather tool to answer user questions about weather.
    Provide concise, friendly responses.""",
    tools=[Tool.from_function(get_weather)]
)

# Execute
response = agent.run("What's the weather in San Francisco?")
print(response.content)
```

**Sequential Workflow Agent:**

```python
from google.adk.agents import SequentialAgent
from google.adk.tools import Tool

def fetch_data(user_id: str) -> dict:
    """Fetch user data from database."""
    return {"user_id": user_id, "name": "Alice", "score": 85}

def transform_data(data: dict) -> dict:
    """Transform data format."""
    return {
        "id": data["user_id"],
        "display_name": data["name"].upper(),
        "grade": "A" if data["score"] >= 90 else "B"
    }

def save_result(data: dict) -> str:
    """Save transformed data."""
    return f"Saved: {data}"

# Sequential execution: fetch → transform → save
agent = SequentialAgent(
    name="data_pipeline",
    tools=[
        Tool.from_function(fetch_data),
        Tool.from_function(transform_data),
        Tool.from_function(save_result)
    ]
)

result = agent.run({"user_id": "123"})
```

**Parallel Workflow Agent:**

```python
from google.adk.agents import ParallelAgent
from google.adk.tools import Tool

def get_stock_price(symbol: str) -> float:
    """Fetch stock price."""
    return 150.25

def get_company_news(symbol: str) -> list:
    """Fetch company news."""
    return ["News 1", "News 2"]

def get_analyst_ratings(symbol: str) -> dict:
    """Fetch analyst ratings."""
    return {"buy": 5, "hold": 2, "sell": 1}

# Execute all tools in parallel, aggregate results
agent = ParallelAgent(
    name="market_researcher",
    tools=[
        Tool.from_function(get_stock_price),
        Tool.from_function(get_company_news),
        Tool.from_function(get_analyst_ratings)
    ]
)

results = agent.run({"symbol": "GOOGL"})
# Returns: {price: 150.25, news: [...], ratings: {...}}
```

**Loop Workflow Agent:**

```python
from google.adk.agents import LoopAgent
from google.adk.tools import Tool

def generate_content(topic: str, iteration: int) -> str:
    """Generate content draft."""
    return f"Draft {iteration}: Content about {topic}..."

def critique_content(content: str) -> dict:
    """Evaluate content quality.

    Returns:
        dict with 'approved' (bool) and 'feedback' (str)
    """
    score = calculate_quality(content)
    return {
        "approved": score > 0.8,
        "feedback": "Needs more detail" if score < 0.8 else "Approved"
    }

# Loop until critique approves (max 5 iterations)
agent = LoopAgent(
    name="content_generator",
    tools=[
        Tool.from_function(generate_content),
        Tool.from_function(critique_content)
    ],
    max_iterations=5,
    break_condition=lambda result: result.get("approved", False)
)

final_content = agent.run({"topic": "AI agents"})
```

### Testing Phase

**Web UI Testing:**

```bash
# Start API server
adk api_server --port 8000

# Start web UI (separate terminal)
cd adk-web
npm install
npm start
# Access: http://localhost:4200
```

**Programmatic Testing:**

```python
# Unit test for agent
def test_weather_agent():
    agent = create_weather_agent()
    response = agent.run("Weather in NYC?")
    assert "weather" in response.content.lower()
    assert response.success is True

# Integration test with mock tools
def test_pipeline_agent():
    agent = create_pipeline_agent(mock_tools=True)
    result = agent.run({"input": "test_data"})
    assert result["status"] == "completed"
```

**Evaluation Framework:**

```python
from google.adk.evaluation import evaluate_agent

# Criteria-based evaluation
results = evaluate_agent(
    agent=my_agent,
    test_cases=[
        {"input": "What's 2+2?", "expected_output": "4"},
        {"input": "Explain quantum computing", "criteria": "mentions_qubits"}
    ],
    evaluator_model="gemini-2.0-flash"
)

print(f"Pass rate: {results.pass_rate}")
print(f"Average score: {results.avg_score}")
```

## Tool Development

### Custom Function Tools

**Basic Tool:**

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
    return {
        "tax": round(tax, 2),
        "total": round(amount + tax, 2)
    }

# Convert to ADK tool (auto-generates schema from type hints)
tax_tool = Tool.from_function(calculate_tax)
```

**Async Tool:**

```python
import asyncio
from google.adk.tools import Tool

async def fetch_user_data(user_id: str) -> dict:
    """Fetch user data from async API.

    Args:
        user_id: User identifier

    Returns:
        User data dictionary
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()

# ADK handles async execution automatically
user_tool = Tool.from_function(fetch_user_data)
```

**Tool with Confirmation (HITL):**

```python
from google.adk.tools import Tool, ConfirmationMode

def send_email(to: str, subject: str, body: str) -> str:
    """Send email to recipient.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body text

    Returns:
        Confirmation message
    """
    # Send email implementation
    return f"Email sent to {to}"

# Require human approval before execution
email_tool = Tool.from_function(
    send_email,
    confirmation_mode=ConfirmationMode.ALWAYS
)
```

### OpenAPI Tools

**From OpenAPI Spec:**

```python
from google.adk.tools import Tool

# Load from OpenAPI specification
api_tools = Tool.from_openapi(
    spec_url="https://api.example.com/openapi.json",
    tool_filter=["getUserById", "createUser"]  # Optional: select specific operations
)

agent = LlmAgent(
    name="user_manager",
    tools=api_tools,
    instructions="Manage users via the API"
)
```

### MCP Tool Integration

**Connect to MCP Server:**

```python
from google.adk.tools.mcp import MCPToolkit

# Connect to MCP server
mcp_tools = MCPToolkit.from_server("http://localhost:3000")

agent = LlmAgent(
    name="mcp_agent",
    tools=mcp_tools.get_tools(),
    instructions="Use MCP tools to complete tasks"
)
```

## Multi-Agent Orchestration

### Pattern 1: Coordinator/Dispatcher

**Use case:** Route user requests to specialized agents

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
    instructions="Provide financial data and analysis"
)

# Coordinator agent
coordinator = LlmAgent(
    name="coordinator",
    agents=[weather_agent, finance_agent],
    instructions="""You are a coordinator that routes user requests:
    - Weather questions → weather_specialist
    - Finance questions → finance_specialist
    Choose the appropriate specialist agent for each query."""
)

response = coordinator.run("What's the weather in NYC and GOOGL stock price?")
```

**Complexity:** 4

### Pattern 2: Sequential Pipeline

**Use case:** Multi-stage processing with dependencies

```python
# Research agent (stage 1)
researcher = LlmAgent(
    name="researcher",
    tools=[search_tool],
    instructions="Research topics and gather information"
)

# Writer agent (stage 2)
writer = LlmAgent(
    name="writer",
    tools=[],
    instructions="Write articles based on research data"
)

# Editor agent (stage 3)
editor = LlmAgent(
    name="editor",
    tools=[],
    instructions="Edit and improve articles"
)

# Pipeline: research → write → edit
def content_pipeline(topic: str) -> str:
    research = researcher.run(f"Research: {topic}")
    draft = writer.run(f"Write article using: {research.content}")
    final = editor.run(f"Edit this article: {draft.content}")
    return final.content

article = content_pipeline("Quantum Computing")
```

**Complexity:** 3

### Pattern 3: Parallel Fan-Out/Gather

**Use case:** Aggregate results from multiple sources

```python
from google.adk.agents import ParallelAgent, LlmAgent

# Create specialist agents for different data sources
technical_analyst = LlmAgent(
    name="technical_analyst",
    tools=[chart_analysis_tool],
    instructions="Analyze technical indicators"
)

fundamental_analyst = LlmAgent(
    name="fundamental_analyst",
    tools=[financial_data_tool],
    instructions="Analyze company fundamentals"
)

sentiment_analyst = LlmAgent(
    name="sentiment_analyst",
    tools=[news_sentiment_tool],
    instructions="Analyze market sentiment"
)

# Parallel execution of all analysts
market_analyzer = ParallelAgent(
    name="market_analyzer",
    agents=[technical_analyst, fundamental_analyst, sentiment_analyst]
)

# Aggregation agent
synthesizer = LlmAgent(
    name="synthesizer",
    instructions="""Synthesize multiple analyst reports into
    a single investment recommendation."""
)

# Execute
analysis = market_analyzer.run({"symbol": "GOOGL"})
recommendation = synthesizer.run(f"Synthesize: {analysis}")
```

**Complexity:** 4

### Pattern 4: Hierarchical Decomposition

**Use case:** Break complex tasks into manageable subtasks

```python
# Leaf agents (task executors)
code_generator = LlmAgent(
    name="code_generator",
    tools=[code_execution_tool],
    instructions="Generate Python code"
)

test_generator = LlmAgent(
    name="test_generator",
    tools=[],
    instructions="Generate unit tests"
)

doc_generator = LlmAgent(
    name="doc_generator",
    tools=[],
    instructions="Generate documentation"
)

# Mid-level coordinator
dev_coordinator = LlmAgent(
    name="dev_coordinator",
    agents=[code_generator, test_generator],
    instructions="Coordinate code and test generation"
)

# Top-level orchestrator
project_manager = LlmAgent(
    name="project_manager",
    agents=[dev_coordinator, doc_generator],
    instructions="""Manage complete feature implementation:
    1. Generate code and tests via dev_coordinator
    2. Generate documentation via doc_generator
    3. Ensure all components are complete"""
)

result = project_manager.run("Implement user authentication feature")
```

**Complexity:** 5

### Pattern 5: Generator-Critic (Loop Agent)

**Use case:** Iterative refinement with feedback

```python
# Generator agent
generator = LlmAgent(
    name="content_generator",
    instructions="Generate blog posts on given topics"
)

# Critic agent
critic = LlmAgent(
    name="content_critic",
    instructions="""Evaluate blog posts for:
    - Clarity (1-10)
    - Accuracy (1-10)
    - Engagement (1-10)
    Return score and feedback. Approve if average >= 8."""
)

# Loop until critic approves
def generate_quality_content(topic: str, max_attempts: int = 5) -> str:
    for attempt in range(max_attempts):
        draft = generator.run(f"Write about: {topic}")
        evaluation = critic.run(f"Evaluate: {draft.content}")

        if evaluation.get("approved"):
            return draft.content

        # Refine based on feedback
        generator.instructions += f"\nFeedback: {evaluation.get('feedback')}"

    return draft.content  # Return best attempt

final_post = generate_quality_content("AI Ethics")
```

**Complexity:** 4

### Pattern 6: Human-in-the-Loop (HITL)

**Use case:** Critical decisions require human approval

```python
from google.adk.tools import Tool, ConfirmationMode

# High-risk action requiring approval
def delete_user_account(user_id: str, reason: str) -> str:
    """Delete user account (IRREVERSIBLE).

    Args:
        user_id: User identifier
        reason: Reason for deletion

    Returns:
        Confirmation message
    """
    # Deletion logic
    return f"Deleted account {user_id}"

delete_tool = Tool.from_function(
    delete_user_account,
    confirmation_mode=ConfirmationMode.ALWAYS
)

agent = LlmAgent(
    name="account_manager",
    tools=[delete_tool],
    instructions="""Manage user accounts.
    For account deletion, present the request to user for approval."""
)

# Agent will pause and request human confirmation before executing
response = agent.run("Delete account user_123 due to policy violation")
```

**Complexity:** 3

## Memory and State Management

### Session Management

**Basic Session:**

```python
from google.adk.session import Session

# Create session with conversation history
session = Session(
    agent=my_agent,
    max_history_turns=10  # Retain last 10 exchanges
)

# Multi-turn conversation
response1 = session.run("What's the capital of France?")
response2 = session.run("What's its population?")  # Knows "it" = Paris
response3 = session.run("Tell me about its history")  # Knows "its" = Paris
```

### State Persistence

**Custom State Object:**

```python
from dataclasses import dataclass
from typing import List

@dataclass
class UserState:
    user_id: str
    preferences: dict
    conversation_topics: List[str]
    total_interactions: int

# Agent with persistent state
class StatefulAgent:
    def __init__(self):
        self.agent = LlmAgent(...)
        self.states = {}  # In-memory state storage

    def run(self, user_id: str, message: str):
        # Load or create state
        if user_id not in self.states:
            self.states[user_id] = UserState(
                user_id=user_id,
                preferences={},
                conversation_topics=[],
                total_interactions=0
            )

        state = self.states[user_id]

        # Update state
        state.total_interactions += 1
        state.conversation_topics.append(extract_topic(message))

        # Run agent with state context
        response = self.agent.run(
            f"User preferences: {state.preferences}\n"
            f"Previous topics: {state.conversation_topics}\n"
            f"Message: {message}"
        )

        return response
```

**Database Persistence:**

```python
import json
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AgentState(Base):
    __tablename__ = 'agent_states'
    user_id = Column(String, primary_key=True)
    state_data = Column(Text)  # JSON-serialized state

# Save state
def save_state(user_id: str, state: dict):
    engine = create_engine('postgresql://...')
    session = Session(engine)

    record = session.query(AgentState).filter_by(user_id=user_id).first()
    if record:
        record.state_data = json.dumps(state)
    else:
        record = AgentState(user_id=user_id, state_data=json.dumps(state))
        session.add(record)

    session.commit()

# Load state
def load_state(user_id: str) -> dict:
    engine = create_engine('postgresql://...')
    session = Session(engine)
    record = session.query(AgentState).filter_by(user_id=user_id).first()
    return json.loads(record.state_data) if record else {}
```

## Deployment Options

### Agent Engine (Managed Service)

**Deploy to Agent Engine:**

```bash
# Install ADK CLI
pip install google-adk[cli]

# Authenticate
adk auth login

# Deploy agent
adk deploy \
  --agent-file agent.py \
  --agent-name my_agent \
  --project-id my-gcp-project \
  --region us-central1

# Get endpoint
# Output: https://my-agent-{hash}.run.app
```

**Agent Configuration:**

```python
# agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

# Define agent for deployment
agent = LlmAgent(
    name="production_agent",
    model="gemini-2.0-flash",
    tools=[...],
    instructions="...",
    config={
        "temperature": 0.7,
        "max_output_tokens": 2048,
        "timeout_seconds": 60
    }
)
```

### Cloud Run Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for Cloud Run
ENV PORT=8080
EXPOSE 8080

# Run agent server
CMD ["python", "server.py"]
```

**server.py:**

```python
from fastapi import FastAPI
from google.adk.agents import LlmAgent
import uvicorn
import os

app = FastAPI()
agent = create_my_agent()

@app.post("/invoke")
async def invoke_agent(request: dict):
    response = agent.run(request["message"])
    return {"response": response.content}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

**Deploy:**

```bash
# Build and deploy to Cloud Run
gcloud run deploy my-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Docker Containerization

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - AGENT_NAME=my_agent
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**Self-hosted (non-GCP):**

```bash
# Run with Docker
docker build -t my-agent .
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=your_key \
  my-agent
```

### Resource Requirements

| Agent Complexity | CPU | RAM | Concurrent Requests |
|------------------|-----|-----|---------------------|
| Simple LlmAgent | 1 core | 512MB | 10 |
| Workflow Agent | 2 cores | 1GB | 20 |
| Multi-Agent (3-5 agents) | 4 cores | 2GB | 10 |
| Complex Multi-Agent (>5) | 8 cores | 4GB | 5 |

## Evaluation and Testing

### Criteria-Based Evaluation

```python
from google.adk.evaluation import evaluate_agent, Criteria

# Define evaluation criteria
criteria = [
    Criteria(
        name="factual_accuracy",
        description="Response contains factually correct information",
        rubric={"score": "1 if accurate, 0 if inaccurate"}
    ),
    Criteria(
        name="helpfulness",
        description="Response directly addresses user query",
        rubric={"score": "1-5 scale based on relevance"}
    )
]

# Evaluate agent
results = evaluate_agent(
    agent=my_agent,
    test_cases=[
        {"input": "What's the capital of France?", "expected": "Paris"},
        {"input": "Explain photosynthesis", "criteria": ["factual_accuracy"]}
    ],
    criteria=criteria,
    evaluator_model="gemini-2.0-flash"
)

print(f"Pass rate: {results.pass_rate}")
for case in results.cases:
    print(f"{case.input}: {case.score}/5 - {case.feedback}")
```

### User Simulation Evaluation

```python
from google.adk.evaluation import UserSimulator

# Simulate user interactions
simulator = UserSimulator(
    agent=customer_service_agent,
    user_goals=[
        "Get refund for order #12345",
        "Track shipment for order #67890"
    ],
    turns_per_goal=5
)

results = simulator.run()

# Analyze results
print(f"Goal completion rate: {results.success_rate}")
print(f"Average turns to completion: {results.avg_turns}")
```

## Best Practices

### Agent Instruction Writing

**Effective Instructions:**

```python
# GOOD: Clear, specific, structured
instructions = """You are a customer service assistant for TechCorp.

**Your responsibilities:**
1. Answer product questions using the product_catalog tool
2. Process returns using the process_return tool
3. Escalate complex issues to human agents

**Tone:** Professional, empathetic, concise

**Constraints:**
- Never promise refunds >$500 without approval
- Collect order ID before processing returns
- Verify customer identity before sharing account details

**Examples:**
User: "I want to return my laptop"
You: "I can help with that. May I have your order ID?"
"""

# BAD: Vague, unstructured
instructions = "Help customers with their problems. Be nice."
```

### Tool Design Principles

**1. Single Responsibility:**

```python
# GOOD: Focused tool
def get_user_email(user_id: str) -> str:
    """Get user's email address."""
    return db.query_email(user_id)

# BAD: Multiple responsibilities
def get_user_info(user_id: str, include_orders: bool, include_preferences: bool):
    """Get various user information."""  # Too broad
```

**2. Descriptive Naming:**

```python
# GOOD: Clear action and object
def send_password_reset_email(user_email: str) -> bool:
    """Send password reset email to user."""
    pass

# BAD: Ambiguous
def reset(email: str) -> bool:
    """Reset something."""  # What is being reset?
```

**3. Type Hints:**

```python
from typing import List, Dict, Optional

# GOOD: Complete type annotations
def analyze_sentiment(text: str, language: Optional[str] = "en") -> Dict[str, float]:
    """Analyze text sentiment.

    Args:
        text: Input text to analyze
        language: Language code (default: "en")

    Returns:
        Dictionary with 'positive', 'negative', 'neutral' scores
    """
    return {"positive": 0.8, "negative": 0.1, "neutral": 0.1}
```

### Error Handling

**Graceful Degradation:**

```python
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

def fetch_stock_price(symbol: str) -> str:
    """Fetch stock price with error handling."""
    try:
        price = api.get_price(symbol)
        return f"${price}"
    except APIError as e:
        return f"Unable to fetch price: {e.message}"
    except Exception as e:
        return "Service temporarily unavailable"

# Agent continues even if tool fails
agent = LlmAgent(
    name="stock_agent",
    tools=[Tool.from_function(fetch_stock_price)],
    instructions="If stock price unavailable, inform user and suggest alternatives"
)
```

**Retry Logic:**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_external_data(url: str) -> dict:
    """Fetch data with automatic retry on failure."""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()
```

### Security and Safety

**Input Validation:**

```python
import re

def send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Send email with input validation."""
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, recipient):
        return "Invalid email address"

    # Sanitize inputs
    subject = subject[:200]  # Limit length
    body = sanitize_html(body)  # Remove script tags, etc.

    send_email(recipient, subject, body)
    return f"Email sent to {recipient}"
```

**Rate Limiting:**

```python
from functools import wraps
from time import time, sleep

def rate_limit(calls_per_minute: int):
    """Decorator to rate limit tool execution."""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time() - last_called[0]
            if elapsed < min_interval:
                sleep(min_interval - elapsed)
            last_called[0] = time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_minute=10)
def call_external_api(query: str) -> dict:
    """API call with rate limiting."""
    return requests.get(f"https://api.example.com?q={query}").json()
```

### Performance Optimization

**Async Tools for Parallelization:**

```python
import asyncio
from google.adk.tools import Tool

async def fetch_price(symbol: str) -> float:
    """Async price fetch."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/price/{symbol}")
        return response.json()["price"]

# Agent automatically handles parallel execution
agent = LlmAgent(
    name="portfolio_analyzer",
    tools=[Tool.from_function(fetch_price)],
    instructions="Fetch prices for multiple stocks in parallel"
)

# When agent calls fetch_price for ["GOOGL", "AAPL", "MSFT"],
# ADK executes them concurrently
```

## Quality Gates

### Definition of Done: Agents

An agent is production-ready when:

1. **Functionality:**
   - ✓ Agent completes primary objective on test cases
   - ✓ Tool execution succeeds with valid inputs
   - ✓ Error handling covers expected failure modes
   - ✓ Multi-turn conversations maintain context

2. **Performance:**
   - ✓ Response time <5 seconds for simple queries
   - ✓ Response time <30 seconds for complex workflows
   - ✓ Evaluation pass rate ≥80% on criteria
   - ✓ Resource usage within deployment limits

3. **Safety:**
   - ✓ Input validation on all tools
   - ✓ High-risk actions require confirmation (HITL)
   - ✓ No hardcoded credentials or API keys
   - ✓ Rate limiting on external API calls

4. **Observability:**
   - ✓ Logging configured for debugging
   - ✓ Tracing enabled for multi-agent workflows
   - ✓ Evaluation metrics tracked
   - ✓ Error alerts configured

5. **Documentation:**
   - ✓ Agent purpose and capabilities documented
   - ✓ Tool descriptions clear and accurate
   - ✓ Example usage provided
   - ✓ Known limitations documented

### Definition of Done: Tools

A tool is production-ready when:

1. **Interface:**
   - ✓ Function has type hints for all parameters
   - ✓ Docstring explains purpose, args, returns
   - ✓ Parameter descriptions guide LLM selection
   - ✓ Return values are JSON-serializable

2. **Reliability:**
   - ✓ Error handling with informative messages
   - ✓ Input validation prevents invalid operations
   - ✓ Timeout configured for long-running operations
   - ✓ Retry logic for transient failures

3. **Testing:**
   - ✓ Unit tests cover success cases
   - ✓ Unit tests cover error cases
   - ✓ Integration tests with agent execution
   - ✓ Performance benchmarks for expensive operations

## Error Handling Guide

### Common Issues and Resolutions

**Issue: Agent doesn't call the right tool**
- **Cause:** Tool description unclear or ambiguous
- **Resolution:**
  ```python
  # BAD: Vague description
  def process(data):
      """Process data."""  # Too generic

  # GOOD: Specific description
  def validate_email_format(email: str) -> bool:
      """Check if email address matches valid format (user@domain.com).

      Use this tool ONLY to validate email syntax, not to verify
      if email exists or is deliverable."""
  ```

**Issue: Agent loops indefinitely**
- **Cause:** No termination condition in Loop Agent
- **Resolution:**
  ```python
  # Add max_iterations and explicit break condition
  agent = LoopAgent(
      tools=[...],
      max_iterations=10,  # Hard limit
      break_condition=lambda result: result.get("completed", False)
  )
  ```

**Issue: "Tool execution failed" errors**
- **Cause:** Tool raises unhandled exception
- **Resolution:**
  ```python
  def robust_tool(param: str) -> str:
      try:
          result = risky_operation(param)
          return f"Success: {result}"
      except SpecificError as e:
          return f"Operation failed: {e.message}"
      except Exception as e:
          logger.error(f"Unexpected error in robust_tool: {e}")
          return "Temporary service error, please try again"
  ```

**Issue: Agent response is too slow**
- **Cause:** Sequential tool calls when parallelization possible
- **Resolution:**
  ```python
  # Use Parallel Agent or async tools
  agent = ParallelAgent(
      tools=[tool1, tool2, tool3]  # Execute concurrently
  )
  ```

**Issue: Context limit exceeded**
- **Cause:** Conversation history too long
- **Resolution:**
  ```python
  session = Session(
      agent=my_agent,
      max_history_turns=10,  # Limit history
      context_window_tokens=30000  # Set explicit limit
  )
  ```

**Issue: Deployment fails on Cloud Run**
- **Cause:** Missing dependencies or environment variables
- **Resolution:**
  ```bash
  # Ensure requirements.txt is complete
  pip freeze > requirements.txt

  # Set required environment variables
  gcloud run deploy my-agent \
    --set-env-vars GOOGLE_API_KEY=your_key,AGENT_CONFIG=prod
  ```

### Debugging Strategies

**1. Enable verbose logging:**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("google.adk")
logger.setLevel(logging.DEBUG)
```

**2. Test tools independently:**

```python
# Test tool without agent
tool = Tool.from_function(my_function)
result = my_function("test_input")
print(f"Tool output: {result}")
```

**3. Use web UI for interactive debugging:**

```bash
adk api_server --debug
# Access UI at http://localhost:4200
# View tool calls, agent reasoning, response generation
```

**4. Inspect agent execution trace:**

```python
response = agent.run("test query", return_trace=True)
print(response.trace)  # Shows all tool calls and decisions
```

## Complexity Ratings

| Task | Rating | Description |
|------|--------|-------------|
| Simple LlmAgent with tools | 2 | Basic conversational agent |
| Sequential Workflow Agent | 2 | Fixed-order tool execution |
| Parallel Workflow Agent | 3 | Concurrent operations |
| Loop Workflow Agent | 3 | Iterative refinement |
| Custom Agent | 3 | User-defined orchestration |
| Coordinator/Dispatcher (2-3 agents) | 4 | Multi-agent routing |
| Sequential Pipeline (3+ agents) | 4 | Chained agent execution |
| Hierarchical Multi-Agent (>5 agents) | 5 | Complex nested architecture |
| Custom tool development | 2 | Python function wrapper |
| OpenAPI tool integration | 2 | Auto-generated from spec |
| MCP tool integration | 3 | Cross-framework tools |
| Deployment to Agent Engine | 2 | Managed deployment |
| Self-hosted Docker deployment | 3 | Container orchestration |
| Advanced evaluation framework | 4 | Custom criteria and simulation |

## References

### Official Documentation
- **Main docs:** https://google.github.io/adk-docs/
- **Python SDK:** https://github.com/google/adk-python
- **Examples:** https://github.com/google/adk-samples
- **Web UI:** https://github.com/google/adk-web

### Python SDK Resources
- **Installation:** `pip install google-adk`
- **API Reference:** https://google.github.io/adk-docs/api/python/
- **Quickstart Guide:** https://google.github.io/adk-docs/quickstart/

### Additional Languages
- **Go SDK:** https://github.com/google/adk-go
- **Java SDK:** https://github.com/google/adk-java

### Community Resources
- **GitHub Discussions:** https://github.com/google/adk-python/discussions
- **Issue Tracker:** https://github.com/google/adk-python/issues

### Related Skills
- For workflow automation: Use `n8n` skill
- For API design: Use `api-design-architect` skill
- For cloud deployment: Use `cloud-devops-expert` skill
- For Python development: Use Python-specific skills
- For LLM integration: Use model provider SDKs (OpenAI, Anthropic, etc.)

---

**Version:** 1.0.0
**Last Updated:** 2025-11-13
**Complexity Rating:** 3 (Moderate - requires agent architecture knowledge)
**Estimated Learning Time:** 10-15 hours for proficiency
