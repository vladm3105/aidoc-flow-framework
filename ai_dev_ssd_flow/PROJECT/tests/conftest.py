"""
Shared pytest fixtures for PROJECT model tests.

These fixtures provide test data, mock objects, and common utilities
for testing the SDD Project Model v2.2 scripts.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock

import pytest
import yaml


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_tasks_yaml() -> Dict[str, Any]:
    """Sample TASKS YAML data."""
    return {
        'metadata': {
            'id': 'TASKS-01',
            'title': 'Test Tasks',
            'version': '1.0',
            'spec_reference': 'SPEC-01',
            'sprint': 'Sprint 1.0',
            'phase': 'P1',
            'traceability': {
                'brd': 'BRD-01',
                'prd': 'PRD-01',
            },
        },
        'tasks': [
            {
                'id': 'TASKS-01.01.01',
                'title': 'Test task 1',
                'description': 'First test task',
                'traceability': {
                    'brd': 'BRD-01:FR-01',
                    'prd': 'PRD-01:PRD.01.01',
                    'spec': 'SPEC-01',
                },
                'acceptance_criteria': ['Criterion 1', 'Criterion 2'],
                'size': 'M',
                'priority': 'P0',
                'dependencies': [],
            },
            {
                'id': 'TASKS-01.01.02',
                'title': 'Test task 2',
                'description': 'Second test task',
                'traceability': {
                    'brd': 'BRD-01:FR-02',
                    'spec': 'SPEC-01',
                },
                'acceptance_criteria': ['Criterion A'],
                'size': 'S',
                'priority': 'P1',
                'dependencies': ['TASKS-01.01.01'],
            },
        ],
        'summary': {
            'total_tasks': 2,
            'by_priority': {'P0': 1, 'P1': 1},
            'by_size': {'S': 1, 'M': 1},
        },
    }


@pytest.fixture
def sample_tasks_file(temp_dir, sample_tasks_yaml) -> Path:
    """Create a sample TASKS YAML file."""
    tasks_file = temp_dir / 'TASKS-01.yaml'
    with open(tasks_file, 'w') as f:
        yaml.dump(sample_tasks_yaml, f)
    return tasks_file


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample project configuration."""
    return {
        'project': {
            'name': 'Test Project',
            'repo': 'test-owner/test-repo',
            'board_number': 1,
            'sdd_root': 'docs/',
        },
        'validation': {
            'strict_mode': True,
            'coverage_threshold': 85,
        },
        'drift_check': {
            'max_age_days': 14,
            'excluded_patterns': ['docs/generated/*'],
        },
        'quality_gates': {
            'GATE-01': {
                'name': 'Business Requirements Gate',
                'layers': [1, 2, 3, 4],
                'threshold': 90,
            },
            'GATE-05': {
                'name': 'Architecture Gate',
                'layers': [5, 6, 7, 8],
                'threshold': 90,
            },
            'GATE-09': {
                'name': 'Implementation Specification Gate',
                'layers': [9, 10, 11],
                'threshold': 90,
            },
            'GATE-12': {
                'name': 'Code Implementation Gate',
                'layers': [12, 13, 14],
                'threshold': 85,
            },
        },
        'work_types': {
            'new_feature': {'layers': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'description': 'Full SDD flow'},
            'bug_fix': {'layers': [11], 'description': 'TASKS only'},
        },
        'sprint_0_checklist': [
            {'id': '0.1', 'task': 'Test task', 'output': 'Output', 'blocks': ['0.2']},
            {'id': '0.2', 'task': 'Another task', 'output': 'Result', 'blocks': []},
        ],
    }


@pytest.fixture
def sample_config_file(temp_dir, sample_config) -> Path:
    """Create a sample config file."""
    config_file = temp_dir / 'project_model.yaml'
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    return config_file


@pytest.fixture
def sample_docs_structure(temp_dir) -> Path:
    """Create a sample documentation structure."""
    docs_dir = temp_dir / 'docs'
    docs_dir.mkdir()

    # Create sample BRD
    brd_dir = docs_dir / 'BRD'
    brd_dir.mkdir()
    (brd_dir / 'BRD-01.md').write_text("""# BRD-01: Test BRD

## Business Context
Test context

## Business Objectives
- Objective 1

## Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Test requirement | P0 |

## Success Metrics
- Metric 1
""")

    # Create sample PRD
    prd_dir = docs_dir / 'PRD'
    prd_dir.mkdir()
    (prd_dir / 'PRD-01.md').write_text("""# PRD-01: Test PRD

## Product Overview
Test product

## Product Requirements
@brd: BRD-01:FR-01

## User Stories
- US-01: As a user...
""")

    # Create sample ADR
    adr_dir = docs_dir / 'ADR'
    adr_dir.mkdir()
    (adr_dir / 'ADR-01.md').write_text("""# ADR-01: Test Decision

## Context
Test context

## Decision
We will...

## Consequences
- Positive: ...
- Negative: ...
""")

    return docs_dir


@pytest.fixture
def mock_github():
    """Create a mock GitHub client."""
    mock = MagicMock()
    mock.get_repo.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_github_issue():
    """Create a mock GitHub issue."""
    issue = MagicMock()
    issue.number = 1
    issue.title = "Test Issue"
    issue.node_id = "I_test123"
    issue.labels = []
    return issue


@pytest.fixture
def env_with_token(monkeypatch):
    """Set GITHUB_TOKEN environment variable."""
    monkeypatch.setenv('GITHUB_TOKEN', 'test_token_12345')
