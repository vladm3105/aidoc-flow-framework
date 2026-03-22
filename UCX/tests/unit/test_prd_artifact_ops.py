"""Unit tests for ucx.validators.prd.artifact_ops (PLAN-012)."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ucx.validators.prd.artifact_ops import (
    VALIDATION_COPY_SUFFIX,
    REMEDIATED_COPY_SUFFIX,
    PROCESSING_STAGES,
    append_derivation_history_row,
    create_remediated_copy,
    create_validation_copy,
    extract_prd_identity_fields,
    identify_prd_artifact_stage,
    inject_processing_stage_metadata,
    is_prd_validation_report,
    is_source_prd,
    parse_prd_frontmatter,
    prd_remediated_copy_name,
    prd_validation_copy_name,
    prd_validation_report_name,
)


# ---------------------------------------------------------------------------
# Naming helpers
# ---------------------------------------------------------------------------

class TestNamingHelpers:
    def test_validation_report_name(self):
        assert prd_validation_report_name("PRD-01") == "PRD-01_validation_report.md"

    def test_validation_report_name_multi_digit(self):
        assert prd_validation_report_name("PRD-12") == "PRD-12_validation_report.md"

    def test_validation_copy_name_basic(self):
        assert prd_validation_copy_name("PRD-01_platform_architecture") == (
            "PRD-01_platform_architecture_validation"
        )

    def test_remediated_copy_name_from_source(self):
        assert prd_remediated_copy_name("PRD-01_platform_architecture") == (
            "PRD-01_platform_architecture_remediated"
        )

    def test_remediated_copy_name_from_validation(self):
        # Must strip the _validation suffix before adding _remediated
        assert prd_remediated_copy_name("PRD-01_platform_architecture_validation") == (
            "PRD-01_platform_architecture_remediated"
        )

    def test_validation_copy_name_rejects_derived_stem(self):
        # Source stem must not already carry a stage suffix
        with pytest.raises(ValueError):
            prd_validation_copy_name("PRD-01_platform_architecture_validation")


# ---------------------------------------------------------------------------
# Stage identification
# ---------------------------------------------------------------------------

class TestStageIdentification:
    def test_source_file(self):
        p = Path("PRD-01_platform_architecture.md")
        assert identify_prd_artifact_stage(p) == "source"

    def test_validation_file(self):
        p = Path("PRD-01_platform_architecture_validation.md")
        assert identify_prd_artifact_stage(p) == "validation-fixed"

    def test_remediated_file(self):
        p = Path("PRD-01_platform_architecture_remediated.md")
        assert identify_prd_artifact_stage(p) == "remediated"

    def test_is_source_prd(self):
        assert is_source_prd(Path("PRD-01_foo.md")) is True
        assert is_source_prd(Path("PRD-01_foo_validation.md")) is False
        assert is_source_prd(Path("PRD-01_foo_remediated.md")) is False

    def test_is_prd_validation_report(self):
        assert is_prd_validation_report(Path("PRD-01_validation_report.md")) is True
        assert is_prd_validation_report(Path("PRD-12_validation_report.md")) is True
        assert is_prd_validation_report(Path("PRD-01_platform_architecture.md")) is False


# ---------------------------------------------------------------------------
# Frontmatter parsing + identity extraction
# ---------------------------------------------------------------------------

_SOURCE_FRONTMATTER = textwrap.dedent("""\
    ---
    doc_id: PRD-01
    version: 0.2.0
    title: "Platform Architecture"
    tags:
      - prd
    custom_fields:
      document_type: prd
      layer: 2
    ---

    # Body text here
""")

_DERIVED_FRONTMATTER = textwrap.dedent("""\
    ---
    doc_id: PRD-01
    version: 0.2.0
    title: "Platform Architecture"
    tags:
      - prd
    custom_fields:
      document_type: prd
      layer: 2
      processing_stage: validation-fixed
      source_doc_id: PRD-01
      source_version: 0.2.0
      derived_from: PRD-01_platform_architecture.md
    ---

    # Body text here
""")


class TestFrontmatterParsing:
    def test_parse_basic(self):
        fm = parse_prd_frontmatter(_SOURCE_FRONTMATTER)
        assert fm["doc_id"] == "PRD-01"
        assert str(fm["version"]) == "0.2.0"

    def test_parse_missing_frontmatter(self):
        assert parse_prd_frontmatter("# No frontmatter") == {}

    def test_extract_identity_source(self):
        fields = extract_prd_identity_fields(_SOURCE_FRONTMATTER)
        assert fields["doc_id"] == "PRD-01"
        assert fields["version"] == "0.2.0"
        assert fields["processing_stage"] is None
        assert fields["derived_from"] is None

    def test_extract_identity_derived(self):
        fields = extract_prd_identity_fields(_DERIVED_FRONTMATTER)
        assert fields["processing_stage"] == "validation-fixed"
        assert fields["derived_from"] == "PRD-01_platform_architecture.md"


# ---------------------------------------------------------------------------
# Metadata injection
# ---------------------------------------------------------------------------

class TestInjectProcessingStageMetadata:
    def test_injects_stage_fields(self):
        result = inject_processing_stage_metadata(
            _SOURCE_FRONTMATTER,
            processing_stage="validation-fixed",
            source_doc_id="PRD-01",
            source_version="0.2.0",
            derived_from="PRD-01_platform_architecture.md",
        )
        fm = parse_prd_frontmatter(result)
        cf = fm["custom_fields"]
        assert cf["processing_stage"] == "validation-fixed"
        assert cf["source_doc_id"] == "PRD-01"
        assert cf["source_version"] == "0.2.0"
        assert cf["derived_from"] == "PRD-01_platform_architecture.md"
        assert cf["development_status"] == "active"

    def test_preserves_existing_custom_fields(self):
        result = inject_processing_stage_metadata(
            _SOURCE_FRONTMATTER,
            processing_stage="validation-fixed",
            source_doc_id="PRD-01",
            source_version="0.2.0",
            derived_from="PRD-01_platform_architecture.md",
        )
        fm = parse_prd_frontmatter(result)
        # document_type and layer should not be lost
        assert fm["custom_fields"]["document_type"] == "prd"
        assert fm["custom_fields"]["layer"] == 2

    def test_invalid_stage_raises(self):
        with pytest.raises(ValueError, match="Invalid processing_stage"):
            inject_processing_stage_metadata(
                _SOURCE_FRONTMATTER,
                processing_stage="unknown",
                source_doc_id="PRD-01",
                source_version="0.2.0",
                derived_from="x.md",
            )

    def test_remediated_stage(self):
        result = inject_processing_stage_metadata(
            _DERIVED_FRONTMATTER,
            processing_stage="remediated",
            source_doc_id="PRD-01",
            source_version="0.2.0",
            derived_from="PRD-01_platform_architecture_validation.md",
        )
        fm = parse_prd_frontmatter(result)
        assert fm["custom_fields"]["processing_stage"] == "remediated"

    def test_no_frontmatter_gets_minimal_injected(self):
        bare_content = "# No frontmatter\n\nBody here.\n"
        result = inject_processing_stage_metadata(
            bare_content,
            processing_stage="validation-fixed",
            source_doc_id="PRD-01",
            source_version="0.1.0",
            derived_from="PRD-01_foo.md",
        )
        assert result.startswith("---\n")
        fm = parse_prd_frontmatter(result)
        assert fm["custom_fields"]["processing_stage"] == "validation-fixed"


# ---------------------------------------------------------------------------
# Provenance row appending
# ---------------------------------------------------------------------------

_CONTENT_WITH_HISTORY_TABLE = textwrap.dedent("""\
    ---
    doc_id: PRD-01
    version: 0.2.0
    ---

    ## Revision History

    | Version | Date | Author | Description |
    |---------|------|--------|-------------|
    | 0.1.0 | 2025-01-01 | Human | Initial draft |

    ## Section 1

    Content here.
""")

_CONTENT_WITHOUT_HISTORY_TABLE = textwrap.dedent("""\
    ---
    doc_id: PRD-01
    version: 0.2.0
    ---

    # No history table here

    Content.
""")


class TestAppendDerivationHistoryRow:
    def test_appends_to_existing_table(self):
        result = append_derivation_history_row(
            _CONTENT_WITH_HISTORY_TABLE,
            version="0.2.0",
            date="2025-06-01T00:00:00Z",
            author="UCX Validation Fixer",
            description="Validation-fixed copy",
        )
        assert "| 0.2.0 | 2025-06-01T00:00:00Z | UCX Validation Fixer | Validation-fixed copy |" in result
        # Original row should still be there
        assert "| 0.1.0 | 2025-01-01 | Human | Initial draft |" in result

    def test_appends_at_end_when_no_table(self):
        result = append_derivation_history_row(
            _CONTENT_WITHOUT_HISTORY_TABLE,
            version="0.2.0",
            date="2025-06-01T00:00:00Z",
            author="UCX",
            description="Fallback append",
        )
        assert "| 0.2.0 | 2025-06-01T00:00:00Z | UCX | Fallback append |" in result


# ---------------------------------------------------------------------------
# Copy creator functions
# ---------------------------------------------------------------------------

class TestCreateValidationCopy:
    def test_creates_validation_copy(self, tmp_path):
        source_file = tmp_path / "PRD-01_platform_architecture.md"
        source_file.write_text(_SOURCE_FRONTMATTER, encoding="utf-8")

        output_path, content = create_validation_copy(
            source_file,
            source_doc_id="PRD-01",
            source_version="0.2.0",
            derivation_date="2025-06-01T00:00:00Z",
        )

        assert output_path.name == "PRD-01_platform_architecture_validation.md"
        assert output_path.parent == tmp_path

        fm = parse_prd_frontmatter(content)
        cf = fm["custom_fields"]
        assert cf["processing_stage"] == "validation-fixed"
        assert cf["source_doc_id"] == "PRD-01"
        assert cf["derived_from"] == "PRD-01_platform_architecture.md"

    def test_validation_report_referenced_in_history(self, tmp_path):
        source_file = tmp_path / "PRD-01_platform_architecture.md"
        source_file.write_text(_CONTENT_WITH_HISTORY_TABLE, encoding="utf-8")

        _, content = create_validation_copy(
            source_file,
            source_doc_id="PRD-01",
            source_version="0.2.0",
            derivation_date="2025-06-01T00:00:00Z",
        )
        assert "PRD-01_validation_report.md" in content


class TestCreateRemediatedCopy:
    def test_creates_remediated_copy(self, tmp_path):
        # Write a _validation PRD first
        val_file = tmp_path / "PRD-01_platform_architecture_validation.md"
        val_file.write_text(_DERIVED_FRONTMATTER, encoding="utf-8")

        output_path, content = create_remediated_copy(
            val_file,
            source_doc_id="PRD-01",
            source_version="0.2.0",
            remediation_report_name="PRD-01_validation_remediation_report_v001.md",
            derivation_date="2025-06-02T00:00:00Z",
        )

        assert output_path.name == "PRD-01_platform_architecture_remediated.md"

        fm = parse_prd_frontmatter(content)
        cf = fm["custom_fields"]
        assert cf["processing_stage"] == "remediated"
        assert cf["derived_from"] == "PRD-01_platform_architecture_validation.md"

    def test_remediation_report_referenced_in_history(self, tmp_path):
        val_file = tmp_path / "PRD-01_platform_architecture_validation.md"
        val_file.write_text(_CONTENT_WITH_HISTORY_TABLE, encoding="utf-8")

        _, content = create_remediated_copy(
            val_file,
            source_doc_id="PRD-01",
            source_version="0.2.0",
            remediation_report_name="PRD-01_validation_remediation_report_v001.md",
            derivation_date="2025-06-02T00:00:00Z",
        )
        assert "PRD-01_validation_remediation_report_v001.md" in content


# ---------------------------------------------------------------------------
# PROCESSING_STAGES constant sanity
# ---------------------------------------------------------------------------

class TestConstants:
    def test_processing_stages_set(self):
        assert "source" in PROCESSING_STAGES
        assert "validation-fixed" in PROCESSING_STAGES
        assert "remediated" in PROCESSING_STAGES

    def test_suffixes(self):
        assert VALIDATION_COPY_SUFFIX == "_validation"
        assert REMEDIATED_COPY_SUFFIX == "_remediated"
