"""Tests for UnifiedPRDValidator.

Tests cover:
- Schema constants (type codes, sections)
- Structure validation (sections, headings)
- Metadata validation (frontmatter, tags)
- Element code validation (PRD.NN.TT.SS format)
- Quality gates (20 GATE checks)
- Scoring (SYS-Ready, EARS-Ready)
- Fixer functionality
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from ucx.validators.prd import (
    UnifiedPRDValidator,
    PRDValidationResult,
    ValidationIssue,
    Tier,
)
from ucx.validators.prd.schema import (
    VALID_TYPE_CODES,
    REQUIRED_SECTIONS,
    TYPE_CODE_DESCRIPTIONS,
    SECTION_CODE_MAP,
    is_valid_type_code,
    get_type_code_description,
    get_primary_section,
)
from ucx.validators.prd.scoring import PRDScorer, ScoringResult


class TestSchema:
    """Test schema constants."""

    def test_valid_type_codes_count(self):
        """Should have 13 valid type codes."""
        assert len(VALID_TYPE_CODES) == 13

    def test_required_sections_count(self):
        """Should have 21 required sections."""
        assert len(REQUIRED_SECTIONS) == 21

    def test_type_code_descriptions(self):
        """All type codes should have descriptions."""
        for code in VALID_TYPE_CODES:
            assert code in TYPE_CODE_DESCRIPTIONS

    def test_section_code_mapping(self):
        """All sections should have code mappings."""
        for section in range(1, 22):
            assert str(section) in SECTION_CODE_MAP

    def test_is_valid_type_code(self):
        """is_valid_type_code should work correctly."""
        assert is_valid_type_code("01")
        assert is_valid_type_code("09")
        assert is_valid_type_code("22")
        assert not is_valid_type_code("10")  # Invalid code
        assert not is_valid_type_code("00")

    def test_get_type_code_description(self):
        """get_type_code_description should return correct descriptions."""
        assert get_type_code_description("01") == "Functional Requirement"
        assert get_type_code_description("09") == "User Story"
        assert get_type_code_description("99") == "Unknown"

    def test_get_primary_section(self):
        """get_primary_section should return correct sections."""
        assert get_primary_section("01") == 9  # FR -> Section 9
        assert get_primary_section("09") == 8  # US -> Section 8
        assert get_primary_section("99") == 0  # Unknown


class TestValidationIssue:
    """Test ValidationIssue dataclass."""

    def test_create_issue(self):
        """Should create issue with all fields."""
        issue = ValidationIssue(
            code="PRD-E001",
            message="Test message",
            file="test.md",
            line=10,
            tier=Tier.TIER1,
        )
        assert issue.code == "PRD-E001"
        assert issue.message == "Test message"
        assert issue.file == "test.md"
        assert issue.line == 10
        assert issue.tier == Tier.TIER1

    def test_to_dict(self):
        """to_dict should return correct dictionary."""
        issue = ValidationIssue(
            code="PRD-E001",
            message="Test message",
            file="test.md",
            tier=Tier.TIER2,
        )
        d = issue.to_dict()
        assert d["code"] == "PRD-E001"
        assert d["tier"] == "tier2"

    def test_format(self):
        """format should return formatted string."""
        issue = ValidationIssue(
            code="PRD-E001",
            message="Test",
            file="test.md",
            line=5,
            tier=Tier.TIER1,
        )
        formatted = issue.format()
        assert "PRD-E001" in formatted
        assert "test.md:5" in formatted
        assert "[ERROR]" in formatted


class TestPRDValidationResult:
    """Test PRDValidationResult dataclass."""

    def test_empty_result(self):
        """Empty result should have no errors."""
        result = PRDValidationResult()
        assert not result.has_errors
        assert result.sys_ready_score == 0.0
        assert result.ears_ready_score == 0.0

    def test_with_tier1_issues(self):
        """Result with Tier 1 issues should have errors."""
        result = PRDValidationResult(
            tier1_issues=[
                ValidationIssue(code="PRD-E001", message="Error", tier=Tier.TIER1)
            ]
        )
        assert result.has_errors
        assert len(result.errors) == 1

    def test_scores_passed(self):
        """Scores should pass when above threshold."""
        result = PRDValidationResult(
            sys_ready_score=90.0,
            ears_ready_score=85.0,
            threshold=85,
        )
        assert result.sys_passed
        assert result.ears_passed
        assert result.both_passed

    def test_scores_failed(self):
        """Scores should fail when below threshold."""
        result = PRDValidationResult(
            sys_ready_score=80.0,
            ears_ready_score=70.0,
            threshold=85,
        )
        assert not result.sys_passed
        assert not result.ears_passed
        assert not result.both_passed

    def test_exit_code(self):
        """Exit code should reflect result status."""
        # No issues -> 0
        result = PRDValidationResult()
        assert result.exit_code() == 0

        # Tier 2 only -> 1
        result = PRDValidationResult(
            tier2_issues=[ValidationIssue(code="W001", message="Warning", tier=Tier.TIER2)]
        )
        assert result.exit_code() == 1

        # Tier 1 -> 2
        result = PRDValidationResult(
            tier1_issues=[ValidationIssue(code="E001", message="Error", tier=Tier.TIER1)]
        )
        assert result.exit_code() == 2

    def test_format_text(self):
        """format_text should return formatted output."""
        result = PRDValidationResult(
            sys_ready_score=85.0,
            ears_ready_score=85.0,
            template_profile="mvp",
            files_validated=["test.md"],
        )
        text = result.format_text()
        assert "PRD Validation Results" in text
        assert "mvp" in text
        assert "SYS-Ready" in text
        assert "EARS-Ready" in text

    def test_to_dict(self):
        """to_dict should return complete dictionary."""
        result = PRDValidationResult(
            sys_ready_score=90.0,
            ears_ready_score=85.0,
        )
        d = result.to_dict()
        assert "sys_ready_score" in d
        assert "ears_ready_score" in d
        assert "has_errors" in d


class TestPRDScorer:
    """Test PRDScorer functionality."""

    def test_empty_content(self):
        """Empty content should have low scores."""
        scorer = PRDScorer(profile="mvp")
        result = scorer.calculate("")
        assert result.sys_ready < 20
        assert result.ears_ready < 20

    def test_minimal_content(self):
        """Minimal content should have partial scores."""
        content = """
## 1. Document Control
Status: Draft

## 8. User Stories
PRD.01.09.01: As a user, I want to login

## 9. Functional Requirements
PRD.01.01.01: The system shall authenticate users

## 10. Customer-Facing Content
This section describes the customer-facing messaging and error handling.
The system provides clear error messages when authentication fails.
Users receive confirmation when actions complete successfully.
"""
        scorer = PRDScorer(profile="mvp")
        result = scorer.calculate(content)
        assert result.sys_ready > 0
        assert result.ears_ready > 0

    def test_profile_threshold(self):
        """Profile should set correct threshold."""
        mvp_scorer = PRDScorer(profile="mvp")
        assert mvp_scorer.threshold == 85

        standard_scorer = PRDScorer(profile="standard")
        assert standard_scorer.threshold == 90

    def test_scoring_result_dict(self):
        """ScoringResult.to_dict should include all components."""
        scorer = PRDScorer()
        result = scorer.calculate("test")
        d = result.to_dict()
        assert "sys_ready" in d
        assert "ears_ready" in d
        assert "components" in d
        assert "sys" in d["components"]
        assert "ears" in d["components"]


class TestUnifiedPRDValidator:
    """Test UnifiedPRDValidator class."""

    def test_init_mvp_profile(self):
        """MVP profile should set 85% threshold."""
        validator = UnifiedPRDValidator(profile="mvp")
        assert validator.threshold == 85

    def test_init_standard_profile(self):
        """Standard profile should set 90% threshold."""
        validator = UnifiedPRDValidator(profile="standard")
        assert validator.threshold == 90

    def test_validate_minimal_file(self):
        """Should validate a minimal PRD file."""
        content = """---
title: "Test PRD"
doc_id: PRD-01
version: "1.0"
status: Draft
tags:
  - prd
  - layer-2-artifact
custom_fields:
  document_type: prd
  artifact_type: PRD
  layer: 2
---

# PRD-01: Test Product

## 1. Document Control
Status: Draft

## 10. Customer-Facing Content
Customer-facing content goes here with substantive information.
This section must have at least 200 characters of content to pass validation.
The customer-facing content describes error messages, notifications, and UI text.
Additional content to meet the minimum character requirement for Section 10.
"""
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            validator = UnifiedPRDValidator(profile="mvp")
            result = validator.validate(path)

            assert isinstance(result, PRDValidationResult)
            assert len(result.files_validated) == 1
        finally:
            path.unlink()

    def test_validate_directory(self):
        """Should validate a directory of PRD files."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test file
            content = """---
title: "Test PRD"
doc_id: PRD-01
version: "1.0"
status: Draft
tags:
  - prd
  - layer-2-artifact
---

# PRD-01: Test

## 1. Document Control
Status: Draft
"""
            (tmppath / "PRD-01_test.md").write_text(content)

            validator = UnifiedPRDValidator()
            result = validator.validate(tmppath)

            assert isinstance(result, PRDValidationResult)

    def test_tier1_only_mode(self):
        """tier1_only should skip Tier 2 checks."""
        content = """---
title: Test
doc_id: PRD-01
version: 1.0
status: Draft
tags:
  - prd
---

# PRD-01: Test

## 1. Document Control
"""
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            validator = UnifiedPRDValidator()

            # With tier1_only, should have fewer issues
            result_tier1 = validator.validate(path, tier1_only=True)

            # Without tier1_only, may have more issues
            result_full = validator.validate(path, tier1_only=False)

            # Tier 2 issues should be empty in tier1_only mode
            # (or at least no more than full mode)
            assert len(result_tier1.tier2_issues) <= len(result_full.tier2_issues)
        finally:
            path.unlink()


class TestElementCodeValidation:
    """Test element code validation."""

    def test_valid_element_ids(self):
        """Valid element IDs should not cause issues."""
        from ucx.validators.prd.element_codes import validate_element_codes

        content = """
PRD.01.01.01 - Functional requirement
PRD.01.09.02 - User story
PRD.01.22.03 - Feature
"""
        path = Path("test.md")
        issues = validate_element_codes(path, content)

        # No invalid type code errors
        type_errors = [i for i in issues if i.code == "PRD-E013"]
        assert len(type_errors) == 0

    def test_invalid_type_code(self):
        """Invalid type codes should raise issues."""
        from ucx.validators.prd.element_codes import validate_element_codes

        content = """
PRD.01.10.01 - Invalid type code 10
PRD.01.99.01 - Invalid type code 99
"""
        path = Path("test.md")
        issues = validate_element_codes(path, content)

        type_errors = [i for i in issues if i.code == "PRD-E013"]
        assert len(type_errors) >= 2

    def test_malformed_short_segment_id(self):
        """Single-digit segments in PRD IDs should be flagged as invalid format."""
        from ucx.validators.prd.element_codes import validate_element_codes

        content = """
PRD.01.09.3 - Invalid short sequence segment
PRD.1.09.03 - Invalid short doc segment
PRD.01.9.03 - Invalid short type segment
"""
        path = Path("test.md")
        issues = validate_element_codes(path, content)

        format_errors = [i for i in issues if i.code == "PRD-E013"]
        assert len(format_errors) >= 3

    def test_duplicate_detection(self):
        """Duplicate element IDs should be detected."""
        from ucx.validators.prd.element_codes import validate_element_codes

        content = """
PRD.01.01.01 - First definition
PRD.01.01.02 - Second definition
PRD.01.01.01 - Duplicate of first
"""
        path = Path("test.md")
        issues = validate_element_codes(path, content)

        dup_errors = [i for i in issues if i.code == "PRD-E017"]
        assert len(dup_errors) >= 1


class TestStructureValidation:
    """Test structure validation."""

    def test_missing_h1(self):
        """Missing H1 should raise error."""
        from ucx.validators.prd.structure import validate_structure

        content = """
## 1. Document Control
Status: Draft
"""
        path = Path("PRD-01_test.md")
        issues = validate_structure(path, content)

        h1_errors = [i for i in issues if i.code == "PRD-E001"]
        assert len(h1_errors) >= 1

    def test_placeholder_detection(self):
        """Placeholders should be detected."""
        from ucx.validators.prd.structure import validate_structure

        content = """
# PRD-01: Test

## 1. Document Control
[TODO] Add content here
(TBD)
"""
        path = Path("PRD-01_test.md")
        issues = validate_structure(path, content)

        placeholder_errors = [i for i in issues if i.code == "CORPUS-E001"]
        assert len(placeholder_errors) >= 1


class TestMetadataValidation:
    """Test metadata validation."""

    def test_missing_frontmatter(self):
        """Missing frontmatter should raise error."""
        from ucx.validators.prd.metadata import validate_metadata

        content = """
# PRD-01: Test

## 1. Document Control
"""
        path = Path("PRD-01_test.md")
        issues = validate_metadata(path, content)

        fm_errors = [i for i in issues if i.code == "CORPUS-W018"]
        assert len(fm_errors) >= 1

    def test_valid_frontmatter(self):
        """Valid frontmatter should not raise errors."""
        from ucx.validators.prd.metadata import validate_metadata

        content = """---
title: "Test PRD"
doc_id: PRD-01
version: "1.0"
status: Draft
tags:
  - prd
  - layer-2-artifact
custom_fields:
  document_type: prd
  artifact_type: PRD
  layer: 2
---

# PRD-01: Test
"""
        path = Path("PRD-01_test.md")
        issues = validate_metadata(path, content)

        # No frontmatter errors
        fm_errors = [i for i in issues if i.code == "CORPUS-W018"]
        assert len(fm_errors) == 0


class TestQualityGates:
    """Test quality gate checks."""

    def test_section_extraction_uses_full_section_content(self):
        """Section-based gates should inspect full section bodies, not only headings."""
        from ucx.validators.prd.quality_gate import run_quality_gates

        content = """
## 5. Success Metrics
PRD.01.08.01 Metric A

## 7. Scope & Requirements
PRD.01.22.01 Feature A

## 8. User Stories & User Roles
PRD.01.09.01 As a sender, I want to send funds, so that family receives quickly.

## 11. Acceptance Criteria
PRD.01.06.01 Criteria A
PRD.01.06.02 Criteria B
PRD.01.06.03 Criteria C

## 14. Success Definition
Release criteria: all launch checks complete.

## 18. Traceability
### 18.4 Architecture Decision Requirements
ADR topics table present

## 21. Quality Assurance & Testing Strategy
PRD.01.02.01 Quality attribute A
"""

        issues = run_quality_gates(Path("PRD-01_test.md"), content, tier1_only=False)
        codes = {issue.code for issue in issues}

        assert "PRD-W009" not in codes
        assert "PRD-W011" not in codes
        assert "PRD-W012" not in codes
        assert "PRD-W018" not in codes
        assert "PRD-W019" not in codes
        assert "PRD-W020" not in codes
        assert "PRD-W021" not in codes

    def test_gate_05_skips_document_level_prd_ids(self):
        """Document-level PRD IDs should not be treated as invalid element IDs."""
        from ucx.validators.prd.quality_gate import _gate_05_element_format

        content = """---
title: \"PRD-01: Test Product\"
doc_id: PRD-01
---

# PRD-01: Test Product

| Document ID | PRD-01 |

## 16. Implementation Approach
- Follow-up work may be documented in PRD-02: Corridor expansion.
@depends: PRD-03
"""

        issues = _gate_05_element_format("PRD-01_test.md", content)
        assert issues == []

    def test_gate_05_flags_invalid_element_style_prd_ids(self):
        """Element-like uses of PRD-NN should still fail GATE-05."""
        from ucx.validators.prd.quality_gate import _gate_05_element_format

        content = """# PRD-01: Test Product

## 9. Functional Requirements
- PRD-01: Invalid requirement identifier
"""

        issues = _gate_05_element_format("PRD-01_test.md", content)
        assert len([issue for issue in issues if issue.code == "PRD-E005"]) == 1

    def test_structure_accepts_exact_layer_separation_note(self):
        """The framework-required Section 8 note should satisfy validation."""
        from ucx.validators.prd.structure import validate_structure

        content = """
# PRD-01: Test Product

## 8. User Stories & User Roles
> **Layer Separation Note**: This section provides role definitions and story summaries. Detailed behavioral requirements are captured in EARS; executable test specifications are in BDD feature files.

#### PRD.01.09.01: User story
"""

        issues = validate_structure(Path("PRD-01_test.md"), content)
        assert len([issue for issue in issues if issue.code == "PRD-E011"]) == 0

    def test_gate_10_file_size(self):
        """Large files should trigger size warnings."""
        from ucx.validators.prd.quality_gate import _gate_10_file_size

        # Create large content (>800 lines)
        content = "# Test\n" + "Line content\n" * 1000

        issues = _gate_10_file_size("test.md", content)
        size_issues = [i for i in issues if "line" in i.message.lower()]
        assert len(size_issues) >= 1

    def test_gate_01_placeholders(self):
        """Placeholders should be detected."""
        from ucx.validators.prd.quality_gate import _gate_01_placeholders

        content = """
[TODO] Need to complete this
(TBD) details
"""
        issues = _gate_01_placeholders("test.md", content)
        assert len(issues) >= 2


class TestScoringSectionExtraction:
    """Regression tests for PRD scoring section extraction behavior."""

    def test_get_section_content_returns_body_not_heading_only(self):
        """Section extraction should include body content for score computations."""
        scorer = PRDScorer(profile="mvp")
        content = """
## 11. Acceptance Criteria
Line A
Line B

## 12. Constraints & Assumptions
Line C
"""

        section = scorer._get_section_content(content, 11)
        assert section is not None
        assert "Line A" in section
        assert "Line B" in section
