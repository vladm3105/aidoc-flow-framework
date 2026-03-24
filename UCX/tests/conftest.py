"""Shared pytest fixtures for UCX v2 test suite."""

from __future__ import annotations

import pytest

from ucx.config.settings import UCXSettings
from ucx.mcp.server import create_server


@pytest.fixture
def settings() -> UCXSettings:
    """Return UCXSettings with deterministic test values."""
    return UCXSettings(
        ai_model="claude-3-7-sonnet-20250219",
        ai_api_key=None,
        ai_max_tokens=1024,
        max_fix_iterations=2,
        log_level="DEBUG",
        log_format="text",
    )


@pytest.fixture
def mcp_server(settings: UCXSettings):
    """Return a configured FastMCP server instance."""
    return create_server(settings)


@pytest.fixture
def sample_brd_content() -> str:
    """Minimal valid BRD document text for validator tests."""
    return (
        "---\n"
        "doc_id: BRD-01\n"
        "artifact_type: brd\n"
        "version: 1.0\n"
        "title: Sample BRD\n"
        "---\n\n"
        "# BRD-01: Sample Business Requirements\n\n"
        "## BRD.01.01 Introduction\n\n"
        "This document defines business requirements.\n"
    )


@pytest.fixture
def sample_prd_content() -> str:
    """Minimal valid PRD document text for validator tests."""
    return (
        "---\n"
        "doc_id: PRD-01\n"
        "artifact_type: prd\n"
        "version: 1.0\n"
        "title: Sample PRD\n"
        "---\n\n"
        "# PRD-01: Sample Product Requirements\n\n"
        "## PRD.01.01 Introduction\n\n"
        "This document defines product requirements.\n"
    )
