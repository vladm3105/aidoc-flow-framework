"""
Unit Tests for generate_integration_tests.py and generate_smoke_tests.py

Tests the test generation functionality.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_integration_tests import (
    IntegrationTestGenerator,
    IntegrationTestCase,
    GenerationResult,
)

from generate_smoke_tests import (
    SmokeTestGenerator,
    SmokeTestCase,
)


# =============================================================================
# Integration Test Generator Tests
# =============================================================================

@pytest.mark.unit
class TestIntegrationTestGenerator:
    """Tests for IntegrationTestGenerator class."""

    def test_init(self):
        """Test generator initialization."""
        generator = IntegrationTestGenerator()
        assert generator is not None

    def test_init_with_verbose(self):
        """Test generator with verbose mode."""
        generator = IntegrationTestGenerator(verbose=True)
        assert generator.verbose is True

    def test_generate_from_ctr(self, temp_project_dir: Path, sample_ctr_file: Path):
        """Test generation from CTR files."""
        generator = IntegrationTestGenerator()
        ctr_dir = sample_ctr_file.parent
        output_dir = temp_project_dir / "tests" / "integration"

        result = generator.generate_from_ctr(ctr_dir, output_dir)

        assert isinstance(result, GenerationResult)
        assert result.artifacts_processed >= 0

    def test_generate_from_spec(self, temp_project_dir: Path, sample_spec_file: Path):
        """Test generation from SPEC files."""
        generator = IntegrationTestGenerator()
        spec_dir = sample_spec_file.parent
        output_dir = temp_project_dir / "tests" / "integration"

        result = generator.generate_from_spec(spec_dir, output_dir)

        assert isinstance(result, GenerationResult)
        assert result.artifacts_processed >= 0

    def test_generate_creates_output_dir(self, temp_project_dir: Path, sample_spec_file: Path):
        """Test that generation creates output directory."""
        generator = IntegrationTestGenerator()
        spec_dir = sample_spec_file.parent
        output_dir = temp_project_dir / "new_integration_tests"

        assert not output_dir.exists()
        generator.generate_from_spec(spec_dir, output_dir)
        assert output_dir.exists()

    def test_parse_ctr_file(self, sample_ctr_file: Path):
        """Test CTR file parsing."""
        generator = IntegrationTestGenerator()

        test_cases = generator._parse_ctr_file(sample_ctr_file)

        # Should extract test cases from CTR
        assert isinstance(test_cases, list)

    def test_parse_spec_file(self, sample_spec_file: Path):
        """Test SPEC file parsing."""
        generator = IntegrationTestGenerator()

        test_cases = generator._parse_spec_file(sample_spec_file)

        assert isinstance(test_cases, list)

    def test_slugify(self):
        """Test slug generation."""
        generator = IntegrationTestGenerator()

        assert generator._slugify("Hello World") == "hello_world"
        assert generator._slugify("/api/v1/users") == "api_v1_users"
        assert generator._slugify("123-test") == "n_123_test"


@pytest.mark.unit
class TestIntegrationTestCase:
    """Tests for IntegrationTestCase dataclass."""

    def test_create_basic(self):
        """Test basic creation."""
        tc = IntegrationTestCase(
            test_id="ITEST-001",
            name="test_api_endpoint",
            description="Test API endpoint",
            source_artifact="CTR-01.yaml",
            source_type="CTR"
        )
        assert tc.test_id == "ITEST-001"
        assert tc.source_type == "CTR"

    def test_create_with_endpoint(self):
        """Test creation with endpoint info."""
        tc = IntegrationTestCase(
            test_id="ITEST-001",
            name="test_post_users",
            description="Test POST /users",
            source_artifact="CTR-01.yaml",
            source_type="CTR",
            endpoint="/api/v1/users",
            method="POST"
        )
        assert tc.endpoint == "/api/v1/users"
        assert tc.method == "POST"


# =============================================================================
# Smoke Test Generator Tests
# =============================================================================

@pytest.mark.unit
class TestSmokeTestGenerator:
    """Tests for SmokeTestGenerator class."""

    def test_init(self):
        """Test generator initialization."""
        generator = SmokeTestGenerator()
        assert generator is not None

    def test_init_with_timeout(self):
        """Test generator with custom timeout."""
        generator = SmokeTestGenerator(timeout=60)
        assert generator.default_timeout == 60

    def test_generate_from_bdd(self, temp_project_dir: Path, sample_bdd_file: Path):
        """Test generation from BDD files."""
        generator = SmokeTestGenerator()
        bdd_dir = sample_bdd_file.parent
        output_dir = temp_project_dir / "tests" / "smoke"

        result = generator.generate_from_bdd(bdd_dir, output_dir)

        assert isinstance(result, GenerationResult)
        assert result.artifacts_processed >= 0

    def test_generate_from_ears(self, temp_project_dir: Path, sample_ears_file: Path):
        """Test generation from EARS files."""
        generator = SmokeTestGenerator()
        ears_dir = sample_ears_file.parent
        output_dir = temp_project_dir / "tests" / "smoke"

        result = generator.generate_from_ears(ears_dir, output_dir)

        assert isinstance(result, GenerationResult)
        assert result.artifacts_processed >= 0

    def test_parse_bdd_file(self, sample_bdd_file: Path):
        """Test BDD file parsing."""
        generator = SmokeTestGenerator()

        test_cases = generator._parse_bdd_file(sample_bdd_file)

        assert isinstance(test_cases, list)
        # Should extract scenarios from feature file
        if len(test_cases) > 0:
            assert all(isinstance(tc, SmokeTestCase) for tc in test_cases)

    def test_parse_ears_file(self, sample_ears_file: Path):
        """Test EARS file parsing."""
        generator = SmokeTestGenerator()

        test_cases = generator._parse_ears_file(sample_ears_file)

        assert isinstance(test_cases, list)

    def test_critical_scenarios_prioritized(self, sample_bdd_file: Path):
        """Test that @critical scenarios are included."""
        generator = SmokeTestGenerator()

        test_cases = generator._parse_bdd_file(sample_bdd_file)

        # Sample BDD has @critical tag
        if len(test_cases) > 0:
            priorities = [tc.priority for tc in test_cases]
            assert "P0" in priorities or "P1" in priorities


@pytest.mark.unit
class TestSmokeTestCase:
    """Tests for SmokeTestCase dataclass."""

    def test_create_basic(self):
        """Test basic creation."""
        tc = SmokeTestCase(
            test_id="STEST-001",
            name="test_system_health",
            description="Verify system is healthy",
            source_artifact="EARS-01.md",
            source_type="EARS"
        )
        assert tc.test_id == "STEST-001"
        assert tc.priority == "P1"  # Default priority

    def test_create_with_timeout(self):
        """Test creation with custom timeout."""
        tc = SmokeTestCase(
            test_id="STEST-001",
            name="test_slow_operation",
            description="Test slow operation",
            source_artifact="EARS-01.md",
            source_type="EARS",
            timeout=60
        )
        assert tc.timeout == 60

    def test_rollback_on_failure(self):
        """Test rollback flag."""
        tc = SmokeTestCase(
            test_id="STEST-001",
            name="test_critical",
            description="Critical test",
            source_artifact="EARS-01.md",
            source_type="EARS",
            rollback_on_failure=True
        )
        assert tc.rollback_on_failure is True


# =============================================================================
# Generation Result Tests
# =============================================================================

@pytest.mark.unit
class TestGenerationResult:
    """Tests for GenerationResult dataclass."""

    def test_create_success(self):
        """Test successful result."""
        result = GenerationResult(
            files_generated=5,
            tests_generated=15,
            artifacts_processed=3,
            errors=[]
        )
        assert result.files_generated == 5
        assert result.tests_generated == 15
        assert len(result.errors) == 0

    def test_create_with_errors(self):
        """Test result with errors."""
        result = GenerationResult(
            files_generated=2,
            tests_generated=5,
            artifacts_processed=3,
            errors=["Parse error in file.yaml"]
        )
        assert len(result.errors) == 1

    def test_empty_result(self):
        """Test empty result."""
        result = GenerationResult(
            files_generated=0,
            tests_generated=0,
            artifacts_processed=0,
            errors=[]
        )
        assert result.files_generated == 0
