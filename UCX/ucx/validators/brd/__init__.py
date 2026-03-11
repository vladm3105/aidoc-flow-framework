"""Unified BRD Validator module.

Provides comprehensive BRD validation with tiered checks:
- Tier 1 (Core, blocking): Structure, metadata, element codes, quality gates
- Tier 2 (Advisory, non-blocking): Links, references, diagrams

Version: 1.9.2 (introduced in 1.9.0)

CLI Usage:
    ucx validate brd docs/01_BRD/BRD-01/
    ucx validate brd docs/01_BRD/BRD-01/ --tier1-only
    ucx validate brd docs/01_BRD/BRD-01/ --strict --format json

Python Usage:
    from ucx.validators.brd import UnifiedBRDValidator

    validator = UnifiedBRDValidator()
    result = validator.validate(Path("docs/01_BRD/BRD-01/"))

    # For pre-commit (fast, blocking checks only)
    result = validator.validate(Path("docs/01_BRD/BRD-01/"), tier1_only=True)

    # Check results
    if result.has_tier1_errors:
        print(f"Failed: {len(result.tier1_errors)} errors")
    else:
        print(f"Passed: {result.status}")

Exit Codes:
    0 = All checks passed
    1 = Warnings only (Tier 2)
    2 = Errors present (Tier 1)
"""

import re
from pathlib import Path
from typing import List, Optional

# Pattern for supplementary BRD files (BRD-00_* or BRD-00.*)
# These are glossary, index, integration matrix files - not actual BRD documents
SUPPLEMENTARY_FILE_PATTERN = re.compile(r"^BRD-00[_.]")

from ucx.validators.common.result import (
    UnifiedValidationResult,
    ValidationIssue,
    ValidationTier,
)
from ucx.validators.common.file_utils import (
    collect_source_files,
    is_section_based_layout,
    get_main_document,
    count_tokens_estimate,
)
from ucx.validators.common.frontmatter import parse_frontmatter, validate_custom_fields
from ucx.validators.brd.schema import (
    REQUIRED_CUSTOM_FIELDS,
    REQUIRED_TAGS,
    FORBIDDEN_TAG_PATTERNS,
    SECTION_PROFILES,
    LEGACY_STATUS_VALUES,
)
from ucx.validators.brd.element_codes import validate_element_codes
from ucx.validators.brd.structure import validate_structure
from ucx.validators.brd.metadata import validate_metadata
from ucx.validators.brd.quality_gate import validate_quality_gates
# Tier 2 validators (shared)
from ucx.validators.common.links import validate_links
from ucx.validators.common.references import validate_forward_references
from ucx.validators.common.diagrams import validate_diagrams


class UnifiedBRDValidator:
    """
    Unified BRD validator with tiered checks.

    Tier 1 (Core, blocking):
    - Element codes (BRD.NN.TT.SS format)
    - Structure (sections, H1, file naming)
    - Metadata (frontmatter, custom_fields, tags)
    - Quality gates (errors only: placeholders, downstream refs, duplicates)

    Tier 2 (Advisory, non-blocking):
    - Links validation
    - Forward references
    - Diagram consistency
    - Quality gates (warnings: glossary, counts, cost format)
    """

    def __init__(
        self,
        strict: bool = False,
        verbose: bool = False,
    ):
        """
        Initialize validator.

        Args:
            strict: Treat warnings as errors
            verbose: Enable verbose output
        """
        self.strict = strict
        self.verbose = verbose

    def validate(
        self,
        doc_path: Path,
        tier1_only: bool = False,
    ) -> UnifiedValidationResult:
        """
        Run validation checks.

        Args:
            doc_path: Path to BRD document or directory
            tier1_only: If True, run only Tier 1 (blocking) checks

        Returns:
            UnifiedValidationResult with all issues
        """
        result = UnifiedValidationResult(doc_path=doc_path)

        # Collect source files
        files = collect_source_files(doc_path, "*.md", exclude_companions=True)
        if not files:
            result.add_issue(
                "VAL-E004",
                file_path=doc_path,
                context="No BRD files found",
                tier=ValidationTier.TIER1,
            )
            return result

        # Detect layout type
        is_section_layout = is_section_based_layout(doc_path)
        result.metadata["is_section_layout"] = is_section_layout
        result.metadata["file_count"] = len(files)

        # Validate each file
        for file_path in files:
            # Check section layout per file (based on file's parent directory)
            file_section_layout = is_section_based_layout(file_path.parent)

            # For section-based layouts, determine if this is the index file
            is_index_file = False
            if file_section_layout:
                # Index file pattern: TYPE-NN.0_*.md
                is_index_file = re.match(r"^[A-Z]+-\d+\.0_", file_path.name) is not None

            self._validate_file(
                file_path, result, tier1_only,
                is_section_layout=file_section_layout,
                is_index_file=is_index_file,
            )

        # Add checks run
        result.checks_run = [
            "element_codes",
            "structure",
            "metadata",
            "quality_gate_tier1",
        ]
        if not tier1_only:
            result.checks_run.extend([
                "links",
                "references",
                "diagrams",
                "quality_gate_tier2",
            ])

        return result

    def _validate_file(
        self,
        file_path: Path,
        result: UnifiedValidationResult,
        tier1_only: bool,
        is_section_layout: bool = False,
        is_index_file: bool = False,
    ) -> None:
        """
        Validate a single BRD file.

        Args:
            file_path: Path to file
            result: Result to populate
            tier1_only: If True, skip Tier 2 checks
            is_section_layout: True if document uses section-based layout
            is_index_file: True if this is the index file (*.0_*.md)
        """
        # Skip supplementary files (BRD-00_GLOSSARY, BRD-00_INTEGRATION_MATRIX, etc.)
        if SUPPLEMENTARY_FILE_PATTERN.match(file_path.name):
            return

        # Read content
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            result.add_issue(
                "VAL-E005",
                file_path=file_path,
                context=str(e),
                tier=ValidationTier.TIER1,
            )
            return

        # Detect if template
        is_template = "TEMPLATE" in file_path.name.upper()

        # Parse frontmatter
        fm_result = parse_frontmatter(content, str(file_path))
        if not fm_result.is_valid:
            for error in fm_result.errors:
                result.add_issue(
                    "VAL-E002",
                    file_path=file_path,
                    context=error,
                    tier=ValidationTier.TIER1,
                )
            return

        # Determine template profile
        profile = "standard"
        custom_fields = fm_result.data.get("custom_fields", {})
        if "template_profile" in custom_fields:
            profile = custom_fields["template_profile"]
        elif "template_variant" in custom_fields:
            profile = custom_fields["template_variant"]

        # Run Tier 1 checks on ALL files (index and section files)
        # Section files use relaxed requirements (fewer required fields)
        validate_metadata(
            content=content,
            frontmatter=fm_result,
            file_path=file_path,
            result=result,
            is_template=is_template,
            is_section_file=is_section_layout and not is_index_file,
        )

        # Structure validation only on index files (sections have different structure)
        if not is_section_layout or is_index_file:
            validate_structure(
                content=content,
                file_path=file_path,
                result=result,
                profile=profile,
                is_section_layout=is_section_layout,
            )

        # Element codes validation runs on all files
        validate_element_codes(
            content=content,
            file_path=file_path,
            result=result,
        )

        # Quality gates run on all files but adapted for section-based layout
        validate_quality_gates(
            content=content,
            file_path=file_path,
            result=result,
            tier1_only=tier1_only,
            frontmatter=fm_result,
        )

        # Tier 2 checks (skip if tier1_only)
        if not tier1_only:
            # Link validation (traceability section focus)
            validate_links(
                content=content,
                file_path=file_path,
                result=result,
                traceability_only=True,  # Focus on traceability section links
            )

            # Forward reference validation
            validate_forward_references(
                content=content,
                file_path=file_path,
                result=result,
                search_paths=[file_path.parent, file_path.parent.parent],
            )

            # Diagram consistency validation
            validate_diagrams(
                content=content,
                file_path=file_path,
                result=result,
            )

        # Add pass for valid file
        if not result.has_tier1_errors:
            result.add_pass(f"{file_path.name}: Basic validation passed")


__all__ = [
    "UnifiedBRDValidator",
]
