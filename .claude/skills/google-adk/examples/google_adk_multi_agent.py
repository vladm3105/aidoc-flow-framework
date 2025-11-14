"""
Google ADK Multi-Agent Orchestration Patterns

Demonstrates advanced multi-agent patterns:
- Coordinator/Dispatcher
- Sequential Pipeline
- Parallel Fan-Out/Gather
- Hierarchical Decomposition
- Generator-Critic Loop
- Human-in-the-Loop (HITL)
"""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import Tool, ConfirmationMode


# =============================================================================
# Pattern 1: Coordinator/Dispatcher
# Complexity: 4
# =============================================================================

def create_coordinator_system():
    """Route user requests to specialized agents."""

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

    return coordinator


# Example usage:
# response = coordinator.run("What's the weather in NYC and GOOGL stock price?")


# =============================================================================
# Pattern 2: Sequential Pipeline
# Complexity: 3
# =============================================================================

def create_content_pipeline():
    """Multi-stage content creation: research → write → edit."""

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

    return content_pipeline


# Example usage:
# pipeline = create_content_pipeline()
# article = pipeline("Quantum Computing")


# =============================================================================
# Pattern 3: Parallel Fan-Out/Gather
# Complexity: 4
# =============================================================================

def create_market_analysis_system():
    """Aggregate results from multiple analyst agents."""

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

    return market_analyzer, synthesizer


# Example usage:
# analyzer, synthesizer = create_market_analysis_system()
# analysis = analyzer.run({"symbol": "GOOGL"})
# recommendation = synthesizer.run(f"Synthesize: {analysis}")


# =============================================================================
# Pattern 4: Hierarchical Decomposition
# Complexity: 5
# =============================================================================

def create_project_management_system():
    """Break complex tasks into manageable subtasks."""

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

    return project_manager


# Example usage:
# pm = create_project_management_system()
# result = pm.run("Implement user authentication feature")


# =============================================================================
# Pattern 5: Generator-Critic (Loop Agent)
# Complexity: 4
# =============================================================================

def create_quality_content_system():
    """Iterative refinement with feedback loop."""

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

    return generate_quality_content


# Example usage:
# generator = create_quality_content_system()
# final_post = generator("AI Ethics")


# =============================================================================
# Pattern 6: Human-in-the-Loop (HITL)
# Complexity: 3
# =============================================================================

def create_account_management_agent():
    """Critical decisions require human approval."""

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

    return agent


# Example usage:
# agent = create_account_management_agent()
# Agent will pause and request human confirmation before executing
# response = agent.run("Delete account user_123 due to policy violation")


# =============================================================================
# Pattern 7: State Management with Custom Agent
# =============================================================================

from dataclasses import dataclass
from typing import List


@dataclass
class UserState:
    user_id: str
    preferences: dict
    conversation_topics: List[str]
    total_interactions: int


class StatefulAgent:
    """Agent with persistent state management."""

    def __init__(self):
        self.agent = LlmAgent(
            name="personalized_assistant",
            instructions="Provide personalized assistance based on user history"
        )
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


def extract_topic(message: str) -> str:
    """Extract main topic from message."""
    # Simple implementation - would use NLP in production
    return message[:50]


# Example usage:
# agent = StatefulAgent()
# response1 = agent.run("user_123", "Tell me about Python")
# response2 = agent.run("user_123", "What about web frameworks?")
# State preserved across interactions


# =============================================================================
# Pattern 8: Database-Backed State Persistence
# =============================================================================

import json
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session as DBSession

Base = declarative_base()


class AgentState(Base):
    """Database model for agent state."""
    __tablename__ = 'agent_states'
    user_id = Column(String, primary_key=True)
    state_data = Column(Text)  # JSON-serialized state


def save_state(user_id: str, state: dict):
    """Persist agent state to database."""
    engine = create_engine('postgresql://user:pass@localhost/db')
    session = DBSession(engine)

    record = session.query(AgentState).filter_by(user_id=user_id).first()
    if record:
        record.state_data = json.dumps(state)
    else:
        record = AgentState(user_id=user_id, state_data=json.dumps(state))
        session.add(record)

    session.commit()


def load_state(user_id: str) -> dict:
    """Load agent state from database."""
    engine = create_engine('postgresql://user:pass@localhost/db')
    session = DBSession(engine)
    record = session.query(AgentState).filter_by(user_id=user_id).first()
    return json.loads(record.state_data) if record else {}


# =============================================================================
# Mock Tools for Examples
# =============================================================================

class MockTool:
    """Placeholder for example tools."""
    pass


weather_tool = MockTool()
stock_tools = MockTool()
search_tool = MockTool()
chart_analysis_tool = MockTool()
financial_data_tool = MockTool()
news_sentiment_tool = MockTool()
code_execution_tool = MockTool()
