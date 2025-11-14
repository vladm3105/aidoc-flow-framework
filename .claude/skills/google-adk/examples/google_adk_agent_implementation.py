"""
Google ADK Agent Implementation Examples

Demonstrates agent creation patterns for different use cases:
- LlmAgent (conversational)
- Sequential Workflow Agent (ordered steps)
- Parallel Workflow Agent (concurrent execution)
- Loop Workflow Agent (iterative refinement)
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import Tool


# =============================================================================
# Example 1: Basic LlmAgent with Custom Tool
# =============================================================================

def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name or coordinates

    Returns:
        Weather description
    """
    # Implementation would call actual weather API
    return f"Weather in {location}: Sunny, 72°F"


def create_weather_assistant() -> LlmAgent:
    """Create a basic weather assistant agent."""
    agent = LlmAgent(
        name="weather_assistant",
        model="gemini-2.0-flash",
        instructions="""You are a helpful weather assistant.
        Use the get_weather tool to answer user questions about weather.
        Provide concise, friendly responses.""",
        tools=[Tool.from_function(get_weather)]
    )
    return agent


# Example usage:
# response = agent.run("What's the weather in San Francisco?")
# print(response.content)


# =============================================================================
# Example 2: Sequential Workflow Agent (Data Pipeline)
# =============================================================================

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


def create_data_pipeline() -> SequentialAgent:
    """Create sequential pipeline: fetch → transform → save."""
    agent = SequentialAgent(
        name="data_pipeline",
        tools=[
            Tool.from_function(fetch_data),
            Tool.from_function(transform_data),
            Tool.from_function(save_result)
        ]
    )
    return agent


# Example usage:
# result = agent.run({"user_id": "123"})


# =============================================================================
# Example 3: Parallel Workflow Agent (Market Research)
# =============================================================================

def get_stock_price(symbol: str) -> float:
    """Fetch stock price."""
    return 150.25


def get_company_news(symbol: str) -> list:
    """Fetch company news."""
    return ["News 1", "News 2"]


def get_analyst_ratings(symbol: str) -> dict:
    """Fetch analyst ratings."""
    return {"buy": 5, "hold": 2, "sell": 1}


def create_market_researcher() -> ParallelAgent:
    """Create parallel market research agent."""
    agent = ParallelAgent(
        name="market_researcher",
        tools=[
            Tool.from_function(get_stock_price),
            Tool.from_function(get_company_news),
            Tool.from_function(get_analyst_ratings)
        ]
    )
    return agent


# Example usage:
# results = agent.run({"symbol": "GOOGL"})
# Returns: {price: 150.25, news: [...], ratings: {...}}


# =============================================================================
# Example 4: Loop Workflow Agent (Content Generator-Critic)
# =============================================================================

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


def calculate_quality(content: str) -> float:
    """Placeholder for quality calculation."""
    return 0.75  # Example score


def create_content_generator() -> LoopAgent:
    """Create loop agent for iterative content generation."""
    agent = LoopAgent(
        name="content_generator",
        tools=[
            Tool.from_function(generate_content),
            Tool.from_function(critique_content)
        ],
        max_iterations=5,
        break_condition=lambda result: result.get("approved", False)
    )
    return agent


# Example usage:
# final_content = agent.run({"topic": "AI agents"})


# =============================================================================
# Example 5: Session Management (Multi-turn Conversation)
# =============================================================================

from google.adk.session import Session


def create_stateful_session():
    """Create agent session with conversation history."""
    agent = create_weather_assistant()
    session = Session(
        agent=agent,
        max_history_turns=10  # Retain last 10 exchanges
    )
    return session


# Example usage - multi-turn conversation:
# session = create_stateful_session()
# response1 = session.run("What's the capital of France?")
# response2 = session.run("What's its population?")  # Knows "it" = Paris
# response3 = session.run("Tell me about its history")  # Knows "its" = Paris
