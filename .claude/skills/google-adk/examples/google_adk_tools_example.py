"""
Google ADK Custom Tools Implementation Examples

Demonstrates tool development patterns:
- Basic function tools
- Async tools
- Tools with confirmation (HITL)
- OpenAPI tool integration
- MCP tool integration
"""

from google.adk.tools import Tool, ConfirmationMode
from typing import Optional
import asyncio
import httpx


# =============================================================================
# Example 1: Basic Custom Function Tool
# =============================================================================

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


# =============================================================================
# Example 2: Async Tool for API Calls
# =============================================================================

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


# =============================================================================
# Example 3: Tool with Human-in-the-Loop Confirmation
# =============================================================================

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


# =============================================================================
# Example 4: Tool with Input Validation and Error Handling
# =============================================================================

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


def sanitize_html(text: str) -> str:
    """Remove potentially dangerous HTML tags."""
    # Simple implementation - would use library like bleach in production
    return text.replace("<script>", "").replace("</script>", "")


# =============================================================================
# Example 5: Tool with Retry Logic
# =============================================================================

from tenacity import retry, stop_after_attempt, wait_exponential
import requests


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_external_data(url: str) -> dict:
    """Fetch data with automatic retry on failure."""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


# =============================================================================
# Example 6: Tool with Rate Limiting
# =============================================================================

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


# =============================================================================
# Example 7: OpenAPI Tool Integration
# =============================================================================

from google.adk.agents import LlmAgent


def create_api_agent():
    """Create agent with OpenAPI tools."""
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
    return agent


# =============================================================================
# Example 8: MCP Tool Integration
# =============================================================================

from google.adk.tools.mcp import MCPToolkit


def create_mcp_agent():
    """Create agent with MCP server tools."""
    # Connect to MCP server
    mcp_tools = MCPToolkit.from_server("http://localhost:3000")

    agent = LlmAgent(
        name="mcp_agent",
        tools=mcp_tools.get_tools(),
        instructions="Use MCP tools to complete tasks"
    )
    return agent


# =============================================================================
# Example 9: Tool with Graceful Error Handling
# =============================================================================

def fetch_stock_price(symbol: str) -> str:
    """Fetch stock price with error handling."""
    try:
        # Simulate API call
        price = api.get_price(symbol)
        return f"${price}"
    except APIError as e:
        return f"Unable to fetch price: {e.message}"
    except Exception as e:
        return "Service temporarily unavailable"


class APIError(Exception):
    """Custom API error class."""
    pass


# Mock api object for example
class API:
    def get_price(self, symbol: str) -> float:
        return 150.25


api = API()


# =============================================================================
# Example 10: Async Parallel Tool Execution
# =============================================================================

async def fetch_price(symbol: str) -> float:
    """Async price fetch."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/price/{symbol}")
        return response.json()["price"]


def create_portfolio_analyzer():
    """Create agent with async tools for parallel execution."""
    # Agent automatically handles parallel execution
    agent = LlmAgent(
        name="portfolio_analyzer",
        tools=[Tool.from_function(fetch_price)],
        instructions="Fetch prices for multiple stocks in parallel"
    )
    return agent


# When agent calls fetch_price for ["GOOGL", "AAPL", "MSFT"],
# ADK executes them concurrently


# =============================================================================
# Tool Design Best Practices
# =============================================================================

# GOOD: Focused tool with single responsibility
def get_user_email(user_id: str) -> str:
    """Get user's email address."""
    return db.query_email(user_id)


# BAD: Multiple responsibilities (avoid this)
def get_user_info(user_id: str, include_orders: bool, include_preferences: bool):
    """Get various user information."""
    # Too broad - split into separate tools
    pass


# GOOD: Clear action and object naming
def send_password_reset_email(user_email: str) -> bool:
    """Send password reset email to user."""
    pass


# BAD: Ambiguous naming (avoid this)
def reset(email: str) -> bool:
    """Reset something."""  # What is being reset?
    pass


# GOOD: Complete type annotations
from typing import List, Dict


def analyze_sentiment(text: str, language: Optional[str] = "en") -> Dict[str, float]:
    """Analyze text sentiment.

    Args:
        text: Input text to analyze
        language: Language code (default: "en")

    Returns:
        Dictionary with 'positive', 'negative', 'neutral' scores
    """
    return {"positive": 0.8, "negative": 0.1, "neutral": 0.1}


# Mock db object for examples
class DB:
    def query_email(self, user_id: str) -> str:
        return f"user{user_id}@example.com"


db = DB()
