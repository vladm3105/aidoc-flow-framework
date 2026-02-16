"""
Unit tests for raci_generator.py script.

Tests RACI matrix generation and validation.
TASKS Reference: TASKS-05.02.05
"""

import pytest
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from raci_generator import (
    RACIParser,
    RACIMatrixGenerator,
    RACIValidator,
    Role,
    Activity,
    RACIMatrix,
)


class TestRACIParser:
    """Tests for RACIParser class."""

    def test_load_default_roles(self):
        """Test loading default roles."""
        parser = RACIParser()
        roles = parser.load_roles()

        assert len(roles) >= 6
        role_names = [r.name for r in roles]
        assert 'Project Lead' in role_names
        assert 'Developer' in role_names
        assert 'QA Lead' in role_names

    def test_load_default_activities(self):
        """Test loading default activities."""
        parser = RACIParser()
        activities = parser.load_activities()

        assert len(activities) >= 10
        activity_names = [a.name for a in activities]
        assert 'BRD creation' in activity_names
        assert 'SPEC creation' in activity_names
        assert 'TASKS creation' in activity_names

    def test_load_default_assignments(self):
        """Test loading default assignments."""
        parser = RACIParser()
        assignments = parser.load_assignments()

        # Check BRD creation assignments
        brd_assign = assignments.get('BRD creation', {})
        assert brd_assign.get('Project Lead') == 'A'
        assert brd_assign.get('Product Manager') == 'R'

    def test_activities_have_layers(self):
        """Test that activities have layer assignments."""
        parser = RACIParser()
        activities = parser.load_activities()

        tier1 = [a for a in activities if 'Tier 1' in a.category]
        assert len(tier1) >= 4  # BRD, PRD, EARS, BDD


class TestRACIMatrixGenerator:
    """Tests for RACIMatrixGenerator class."""

    def test_generate_matrix(self):
        """Test generating RACI matrix."""
        parser = RACIParser()
        generator = RACIMatrixGenerator(parser)

        roles = parser.load_roles()
        activities = parser.load_activities()
        assignments = parser.load_assignments()

        matrix = generator.generate_matrix(roles, activities, assignments)

        assert isinstance(matrix, RACIMatrix)
        assert len(matrix.roles) >= 6
        assert len(matrix.activities) >= 10
        assert len(matrix.assignments) >= 10

    def test_export_markdown(self):
        """Test exporting matrix as markdown."""
        parser = RACIParser()
        generator = RACIMatrixGenerator(parser)

        roles = parser.load_roles()
        activities = parser.load_activities()
        assignments = parser.load_assignments()
        matrix = generator.generate_matrix(roles, activities, assignments)

        md = generator.export_markdown(matrix)

        assert '# RACI Matrix' in md
        assert '| Activity |' in md
        assert 'Project Lead' in md
        assert 'A' in md  # Accountable
        assert 'R' in md  # Responsible

    def test_export_csv(self):
        """Test exporting matrix as CSV."""
        parser = RACIParser()
        generator = RACIMatrixGenerator(parser)

        roles = parser.load_roles()
        activities = parser.load_activities()
        assignments = parser.load_assignments()
        matrix = generator.generate_matrix(roles, activities, assignments)

        csv_content = generator.export_csv(matrix)

        lines = csv_content.strip().split('\n')
        assert len(lines) >= 11  # Header + activities
        assert 'Activity' in lines[0]
        assert 'Project Lead' in lines[0]


class TestRACIValidator:
    """Tests for RACIValidator class."""

    def test_validate_single_accountable_valid(self):
        """Test validation passes with single accountable."""
        validator = RACIValidator()
        matrix = RACIMatrix(
            roles=[Role('Lead'), Role('Dev')],
            activities=[Activity('Task 1')],
            assignments={'Task 1': {'Lead': 'A', 'Dev': 'R'}},
        )

        errors = validator.validate_single_accountable(matrix)
        assert len(errors) == 0

    def test_validate_single_accountable_missing(self):
        """Test validation fails with no accountable."""
        validator = RACIValidator()
        matrix = RACIMatrix(
            roles=[Role('Lead'), Role('Dev')],
            activities=[Activity('Task 1')],
            assignments={'Task 1': {'Lead': 'R', 'Dev': 'C'}},
        )

        errors = validator.validate_single_accountable(matrix)
        assert len(errors) == 1
        assert 'no Accountable' in errors[0]

    def test_validate_single_accountable_multiple(self):
        """Test validation fails with multiple accountable."""
        validator = RACIValidator()
        matrix = RACIMatrix(
            roles=[Role('Lead'), Role('Manager')],
            activities=[Activity('Task 1')],
            assignments={'Task 1': {'Lead': 'A', 'Manager': 'A'}},
        )

        errors = validator.validate_single_accountable(matrix)
        assert len(errors) == 1
        assert 'multiple Accountable' in errors[0]

    def test_validate_has_responsible(self):
        """Test validation for responsible role."""
        validator = RACIValidator()
        matrix = RACIMatrix(
            roles=[Role('Lead'), Role('Dev')],
            activities=[Activity('Task 1')],
            assignments={'Task 1': {'Lead': 'A', 'Dev': 'I'}},
        )

        errors = validator.validate_has_responsible(matrix)
        assert len(errors) == 1
        assert 'no Responsible' in errors[0]

    def test_validate_no_gaps(self):
        """Test validation for empty rows."""
        validator = RACIValidator()
        matrix = RACIMatrix(
            roles=[Role('Lead'), Role('Dev')],
            activities=[Activity('Task 1'), Activity('Task 2')],
            assignments={
                'Task 1': {'Lead': 'A', 'Dev': 'R'},
                'Task 2': {},  # Empty
            },
        )

        warnings = validator.validate_no_gaps(matrix)
        assert len(warnings) == 1
        assert 'Task 2' in warnings[0]

    def test_generate_warnings_comprehensive(self):
        """Test comprehensive warning generation."""
        parser = RACIParser()
        generator = RACIMatrixGenerator(parser)

        roles = parser.load_roles()
        activities = parser.load_activities()
        assignments = parser.load_assignments()
        matrix = generator.generate_matrix(roles, activities, assignments)

        validator = RACIValidator()
        warnings = validator.generate_warnings(matrix)

        # Default matrix should be valid
        assert len(warnings) == 0
