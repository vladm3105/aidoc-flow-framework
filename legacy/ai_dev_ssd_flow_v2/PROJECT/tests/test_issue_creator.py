"""
Unit tests for GitHubIssueCreator and IssueFormatter classes.

Tests GitHub issue creation and formatting.
TASKS Reference: TASKS-05.01.02
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from tasks_to_github import GitHubIssueCreator, IssueFormatter, TaskElement, TasksMetadata


class TestIssueFormatter:
    """Tests for IssueFormatter class."""

    def test_format_title(self):
        """Test issue title formatting."""
        formatter = IssueFormatter()
        task = TaskElement(
            id='TASKS-01.02.03',
            title='Implement feature X',
            phase='P1',
        )

        title = formatter.format_title(task)
        assert title == '[P1-TASKS-01.02.03] Implement feature X'

    def test_format_title_with_phase_override(self):
        """Test title formatting with phase override."""
        formatter = IssueFormatter()
        task = TaskElement(id='TASKS-01.02.03', title='Test', phase='P1')

        title = formatter.format_title(task, phase='P2')
        assert title == '[P2-TASKS-01.02.03] Test'

    def test_format_body_includes_traceability(self):
        """Test body includes traceability section."""
        formatter = IssueFormatter()
        task = TaskElement(
            id='TASKS-01.01.01',
            title='Test',
            traceability={'brd': 'BRD-01:FR-01', 'prd': 'PRD-01:PRD.01.01'},
        )

        body = formatter.format_body(task)
        assert '## Traceability' in body
        assert '@brd' in body
        assert 'BRD-01:FR-01' in body

    def test_format_body_includes_acceptance_criteria(self):
        """Test body includes acceptance criteria."""
        formatter = IssueFormatter()
        task = TaskElement(
            id='TASKS-01.01.01',
            title='Test',
            acceptance_criteria=['Criterion 1', 'Criterion 2'],
        )

        body = formatter.format_body(task)
        assert '## Acceptance Criteria' in body
        assert '- [ ] Criterion 1' in body
        assert '- [ ] Criterion 2' in body

    def test_format_body_includes_implementation_notes(self):
        """Test body includes implementation notes."""
        formatter = IssueFormatter()
        task = TaskElement(
            id='TASKS-01.01.01',
            title='Test',
            implementation_notes='Use pattern X',
        )

        body = formatter.format_body(task)
        assert '## Implementation Notes' in body
        assert 'Use pattern X' in body

    def test_format_body_includes_metadata(self):
        """Test body includes spec reference from metadata."""
        formatter = IssueFormatter()
        task = TaskElement(id='TASKS-01.01.01', title='Test')
        metadata = TasksMetadata(
            id='TASKS-01',
            title='Tasks',
            version='1.0',
            spec_reference='SPEC-05',
            sprint='Sprint 2.1',
            phase='P1',
        )

        body = formatter.format_body(task, metadata)
        assert '@spec' in body
        assert 'SPEC-05' in body

    def test_format_labels(self):
        """Test label generation."""
        formatter = IssueFormatter()
        task = TaskElement(
            id='TASKS-01.01.01',
            title='Test',
            size='L',
            priority='P0',
            phase='P2',
        )

        labels = formatter.format_labels(task)
        assert 'ai:ready' in labels
        assert 'source:sdd' in labels
        assert 'size:L' in labels
        assert 'priority:P0' in labels
        assert 'phase:P2' in labels

    def test_format_labels_defaults(self):
        """Test default labels."""
        formatter = IssueFormatter()
        task = TaskElement(id='TEST', title='Test')

        labels = formatter.format_labels(task)
        assert 'ai:ready' in labels
        assert 'source:sdd' in labels


class TestGitHubIssueCreator:
    """Tests for GitHubIssueCreator class."""

    @patch('tasks_to_github.Github')
    def test_init(self, mock_github):
        """Test GitHubIssueCreator initialization."""
        creator = GitHubIssueCreator('owner/repo', 'test_token')

        mock_github.assert_called_once_with('test_token')
        mock_github.return_value.get_repo.assert_called_once_with('owner/repo')

    @patch('tasks_to_github.Github')
    def test_create_issue(self, mock_github, mock_github_issue):
        """Test issue creation."""
        mock_repo = MagicMock()
        mock_repo.create_issue.return_value = mock_github_issue
        mock_github.return_value.get_repo.return_value = mock_repo

        creator = GitHubIssueCreator('owner/repo', 'test_token')
        task = TaskElement(
            id='TASKS-01.01.01',
            title='Test Task',
            traceability={'brd': 'BRD-01', 'spec': 'SPEC-01'},
        )

        issue = creator.create_issue(task)

        mock_repo.create_issue.assert_called_once()
        call_kwargs = mock_repo.create_issue.call_args.kwargs
        assert 'TASKS-01.01.01' in call_kwargs['title']
        assert 'Test Task' in call_kwargs['title']

    @patch('tasks_to_github.Github')
    def test_find_existing_issue_found(self, mock_github, mock_github_issue):
        """Test finding existing issue."""
        mock_github.return_value.search_issues.return_value = [mock_github_issue]
        mock_github_issue.title = '[P1-TASKS-01.01.01] Test'

        creator = GitHubIssueCreator('owner/repo', 'test_token')
        result = creator.find_existing_issue('TASKS-01.01.01')

        assert result == mock_github_issue

    @patch('tasks_to_github.Github')
    def test_find_existing_issue_not_found(self, mock_github):
        """Test finding non-existent issue."""
        mock_github.return_value.search_issues.return_value = []

        creator = GitHubIssueCreator('owner/repo', 'test_token')
        result = creator.find_existing_issue('TASKS-99.99.99')

        assert result is None
