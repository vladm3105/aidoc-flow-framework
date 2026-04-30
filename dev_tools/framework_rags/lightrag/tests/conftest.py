"""Pytest configuration for LightRAG tests."""

import os
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_research_doc():
    """Sample research document for testing."""
    return """# PayPal Q3 2025 Earnings Analysis

## Summary

PayPal Holdings (PYPL) reported Q3 2025 earnings with a revenue miss of 3%.
The company's CEO Dan Schulman announced a strategic pivot to focus on
cryptocurrency integration.

## Key Findings

1. Revenue: $7.2B (missed estimate of $7.4B)
2. Active accounts: 435M (+5% YoY)
3. TPV growth: 12% year-over-year

## Analyst Reactions

- Goldman Sachs downgraded from Buy to Hold
- Morgan Stanley maintained Overweight rating
- JPMorgan raised price target to $85

## Risk Assessment

Primary risks identified:
- Increasing competition from Apple Pay and Google Pay
- Regulatory concerns in EU regarding BNPL products
- Currency headwinds affecting international revenue
"""


@pytest.fixture
def entity_types():
    """Expected entity types from sample doc."""
    return {
        "organization": ["PayPal", "Goldman Sachs", "Morgan Stanley", "JPMorgan", "Apple", "Google"],
        "person": ["Dan Schulman"],
        "metric": ["$7.2B", "435M", "12%", "$85"],
        "event": ["Q3 2025 earnings"],
        "finding": ["revenue miss", "strategic pivot"],
        "risk": ["competition", "regulatory concerns", "currency headwinds"],
    }


@pytest.fixture
def mock_env(monkeypatch):
    """Set mock environment variables for testing."""
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "testpass")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
