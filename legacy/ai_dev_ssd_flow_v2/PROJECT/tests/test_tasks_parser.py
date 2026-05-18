"""
Unit tests for TasksParser class.

Tests TASKS YAML parsing and traceability validation.
TASKS Reference: TASKS-05.01.01
"""

import pytest
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from tasks_to_github import TasksParser, TaskElement, TasksMetadata


class TestTasksParser:
    """Tests for TasksParser class."""

    def test_load_yaml(self, sample_tasks_file):
        """Test loading YAML file."""
        parser = TasksParser()
        data = parser.load_yaml(sample_tasks_file)

        assert 'metadata' in data
        assert 'tasks' in data
        assert data['metadata']['id'] == 'TASKS-01'

    def test_extract_tasks(self, sample_tasks_yaml):
        """Test extracting tasks from YAML data."""
        parser = TasksParser()
        tasks = parser.extract_tasks(sample_tasks_yaml)

        assert len(tasks) == 2
        assert isinstance(tasks[0], TaskElement)
        assert tasks[0].id == 'TASKS-01.01.01'
        assert tasks[0].title == 'Test task 1'
        assert tasks[0].size == 'M'
        assert tasks[0].priority == 'P0'

    def test_extract_metadata(self, sample_tasks_yaml):
        """Test extracting metadata from YAML data."""
        parser = TasksParser()
        metadata = parser.extract_metadata(sample_tasks_yaml)

        assert isinstance(metadata, TasksMetadata)
        assert metadata.id == 'TASKS-01'
        assert metadata.spec_reference == 'SPEC-01'
        assert metadata.sprint == 'Sprint 1.0'

    def test_validate_traceability_valid(self, sample_tasks_yaml):
        """Test traceability validation with valid tags."""
        parser = TasksParser()
        tasks = parser.extract_tasks(sample_tasks_yaml)

        # First task has both brd and spec
        assert parser.validate_traceability(tasks[0]) is True

    def test_validate_traceability_missing_brd(self):
        """Test traceability validation with missing BRD."""
        parser = TasksParser()
        task = TaskElement(
            id='TASKS-01.01.01',
            title='Test',
            traceability={'spec': 'SPEC-01'},  # Missing brd
        )
        assert parser.validate_traceability(task) is False

    def test_validate_traceability_missing_spec(self):
        """Test traceability validation with missing SPEC."""
        parser = TasksParser()
        task = TaskElement(
            id='TASKS-01.01.01',
            title='Test',
            traceability={'brd': 'BRD-01:FR-01'},  # Missing spec
        )
        assert parser.validate_traceability(task) is False

    def test_task_element_defaults(self):
        """Test TaskElement default values."""
        task = TaskElement(id='TEST-01', title='Test')

        assert task.description == ''
        assert task.traceability == {}
        assert task.acceptance_criteria == []
        assert task.size == 'M'
        assert task.priority == 'P1'
        assert task.dependencies == []

    def test_extract_tasks_with_dependencies(self, sample_tasks_yaml):
        """Test extracting tasks preserves dependencies."""
        parser = TasksParser()
        tasks = parser.extract_tasks(sample_tasks_yaml)

        # Second task depends on first
        assert tasks[1].dependencies == ['TASKS-01.01.01']

    def test_extract_tasks_inherits_metadata_phase(self, sample_tasks_yaml):
        """Test that tasks inherit phase from metadata."""
        parser = TasksParser()
        tasks = parser.extract_tasks(sample_tasks_yaml)

        assert tasks[0].phase == 'P1'
        assert tasks[1].phase == 'P1'
