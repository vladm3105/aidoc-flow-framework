"""Pytest fixtures for UCX tests."""

import pytest
from pathlib import Path
from ucx.config.settings import UCXConfig
from ucx.ai.mock import MockAIClient


@pytest.fixture
def config():
    """Provide default UCX configuration."""
    return UCXConfig(
        model="mock",
        max_iterations=2,
        min_score=90,
    )


@pytest.fixture
def mock_ai_client():
    """Provide mock AI client for testing without API calls."""
    client = MockAIClient()

    # Add default responses
    client.add_response("review", """
# UCR Review Report

## Executive Summary
Document reviewed with minor issues.

## Findings
- P0-1: Missing compliance section
- P1-1: Unclear requirement
- P2-1: Could improve formatting

Score: 75/100
""")

    client.add_response("create", """---
title: Generated BRD
doc_id: BRD-01
version: "1.0"
status: draft
---

# Business Requirements Document

## 1. Executive Summary
This document describes business requirements.

## 2. Business Context
...
""")

    client.add_response("remediate", """
# UCRem Fix Report

## Fix Proposals

```yaml
fix_id: FIX-P0-01
source_finding: P0-1
priority: P0
confidence: auto-safe
target_file: "BRD-01.md"
target_section: "5.0"
fix_type: add_section
fix_action:
  section_number: "5.1"
  heading: "Compliance Requirements"
  content: "Compliance section content"
rationale: Missing required compliance section
validated_by:
  - Auditor Fixer
  - Architect Fixer
```
""")

    return client


@pytest.fixture
def sample_brd(tmp_path):
    """Create sample BRD for testing."""
    brd_path = tmp_path / "BRD-01.md"
    brd_path.write_text("""---
title: Sample BRD
doc_id: BRD-01
version: "1.0"
status: draft
---

# Business Requirements Document

## 1. Executive Summary

This is a sample BRD for testing purposes.

## 2. Business Context

The business context for this project.

## 3. Requirements

BRD.01.01.01 - First requirement

## 4. Constraints

System constraints go here.
""")
    return brd_path


@pytest.fixture
def sample_review_report(tmp_path):
    """Create sample review report."""
    report_path = tmp_path / "BRD_UCR_REVIEW.md"
    report_path.write_text("""
# UCR Review Report

## Executive Summary
Document reviewed.

## Critical Findings (P0)
- P0-1: Missing section

## High Priority Findings (P1)
- P1-1: Incomplete requirement
- P1-2: Unclear constraint

## Enhancement Recommendations (P2)
- P2-1: Improve formatting

Score: 72/100
""")
    return report_path


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure."""
    # Create directories
    (tmp_path / "docs" / "00_REF").mkdir(parents=True)
    (tmp_path / "docs" / "01_BRD").mkdir(parents=True)

    # Create reference doc
    ref_doc = tmp_path / "docs" / "00_REF" / "spec.md"
    ref_doc.write_text("# Reference Specification\n\nSample content.")

    return tmp_path
