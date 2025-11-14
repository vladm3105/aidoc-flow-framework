"""
Google ADK Deployment Configuration Examples

Demonstrates deployment patterns:
- Agent configuration for production
- FastAPI server setup
- Docker containerization
- Cloud Run deployment
"""

import os
import uvicorn
from fastapi import FastAPI
from google.adk.agents import LlmAgent
from google.adk.tools import Tool


# =============================================================================
# Example 1: Production Agent Configuration
# =============================================================================

def create_production_agent() -> LlmAgent:
    """Define agent with production-ready configuration."""
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
    return agent


# =============================================================================
# Example 2: FastAPI Server for Agent Deployment
# =============================================================================

app = FastAPI()


def create_my_agent():
    """Create agent instance (implement based on use case)."""
    return LlmAgent(
        name="api_agent",
        model="gemini-2.0-flash",
        instructions="Handle API requests"
    )


agent = create_my_agent()


@app.post("/invoke")
async def invoke_agent(request: dict):
    """Agent invocation endpoint.

    Args:
        request: Dict with 'message' key

    Returns:
        Dict with 'response' key containing agent output
    """
    response = agent.run(request["message"])
    return {"response": response.content}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)


# =============================================================================
# Example 3: Agent Server with Error Handling
# =============================================================================

from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/invoke_safe")
async def invoke_agent_safe(request: dict):
    """Agent invocation with error handling."""
    try:
        if "message" not in request:
            raise HTTPException(status_code=400, detail="Missing 'message' field")

        response = agent.run(request["message"])

        if not response.success:
            logger.error(f"Agent execution failed: {response.error}")
            raise HTTPException(status_code=500, detail="Agent execution failed")

        return {
            "response": response.content,
            "metadata": {
                "model": agent.model,
                "tokens_used": response.tokens_used
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in agent invocation")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Example 4: Session-Based Agent API
# =============================================================================

from google.adk.session import Session
from typing import Dict

sessions: Dict[str, Session] = {}


@app.post("/session/create")
async def create_session(user_id: str):
    """Create new agent session for user."""
    agent = create_my_agent()
    session = Session(agent=agent, max_history_turns=10)
    sessions[user_id] = session
    return {"session_id": user_id, "status": "created"}


@app.post("/session/invoke")
async def invoke_session(user_id: str, message: str):
    """Invoke agent within existing session."""
    if user_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[user_id]
    response = session.run(message)
    return {"response": response.content}


@app.delete("/session/delete")
async def delete_session(user_id: str):
    """Delete user session."""
    if user_id in sessions:
        del sessions[user_id]
    return {"status": "deleted"}


# =============================================================================
# Example 5: Agent Evaluation Endpoint
# =============================================================================

from google.adk.evaluation import evaluate_agent, Criteria


@app.post("/evaluate")
async def evaluate_agent_endpoint(test_cases: list):
    """Evaluate agent performance on test cases.

    Args:
        test_cases: List of dicts with 'input' and 'expected' keys

    Returns:
        Evaluation results with pass rate and scores
    """
    criteria = [
        Criteria(
            name="accuracy",
            description="Response is factually correct",
            rubric={"score": "1 if accurate, 0 if inaccurate"}
        )
    ]

    results = evaluate_agent(
        agent=agent,
        test_cases=test_cases,
        criteria=criteria,
        evaluator_model="gemini-2.0-flash"
    )

    return {
        "pass_rate": results.pass_rate,
        "avg_score": results.avg_score,
        "details": [
            {
                "input": case.input,
                "score": case.score,
                "feedback": case.feedback
            }
            for case in results.cases
        ]
    }


# =============================================================================
# Example 6: Docker Configuration (Reference)
# =============================================================================

DOCKERFILE_CONTENT = """
# Dockerfile for Google ADK Agent

FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Cloud Run
ENV PORT=8080
EXPOSE 8080

# Run agent server
CMD ["python", "server.py"]
"""


# =============================================================================
# Example 7: Docker Compose Configuration (Reference)
# =============================================================================

DOCKER_COMPOSE_CONTENT = """
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
"""


# =============================================================================
# Example 8: Environment Configuration
# =============================================================================

class Config:
    """Application configuration from environment."""

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    AGENT_NAME: str = os.getenv("AGENT_NAME", "default_agent")
    PORT: int = int(os.getenv("PORT", 8080))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", 10))

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable required")


# =============================================================================
# Example 9: Deployment Resource Requirements (Reference)
# =============================================================================

RESOURCE_REQUIREMENTS = {
    "simple_llm_agent": {
        "cpu": "1 core",
        "memory": "512MB",
        "concurrent_requests": 10
    },
    "workflow_agent": {
        "cpu": "2 cores",
        "memory": "1GB",
        "concurrent_requests": 20
    },
    "multi_agent_small": {
        "cpu": "4 cores",
        "memory": "2GB",
        "concurrent_requests": 10
    },
    "multi_agent_large": {
        "cpu": "8 cores",
        "memory": "4GB",
        "concurrent_requests": 5
    }
}


# =============================================================================
# Example 10: Debugging and Monitoring
# =============================================================================

import logging


def setup_logging():
    """Configure logging for production."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('agent.log'),
            logging.StreamHandler()
        ]
    )

    # Enable ADK debug logging if needed
    adk_logger = logging.getLogger("google.adk")
    adk_logger.setLevel(logging.DEBUG)


@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests."""
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# =============================================================================
# Example 11: Startup and Shutdown Events
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("Starting agent service...")
    Config.validate()
    setup_logging()
    logger.info("Agent service ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    logger.info("Shutting down agent service...")
    # Close database connections, cleanup sessions, etc.
    sessions.clear()
    logger.info("Agent service stopped")


# =============================================================================
# Deployment Commands Reference
# =============================================================================

"""
# Agent Engine (Managed Service)
adk deploy \\
  --agent-file agent.py \\
  --agent-name my_agent \\
  --project-id my-gcp-project \\
  --region us-central1

# Cloud Run Deployment
gcloud run deploy my-agent \\
  --source . \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --set-env-vars GOOGLE_API_KEY=your_key

# Docker Build and Run
docker build -t my-agent .
docker run -p 8080:8080 \\
  -e GOOGLE_API_KEY=your_key \\
  my-agent

# Docker Compose
docker-compose up -d
"""
