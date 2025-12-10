#!/usr/bin/env python3
"""
EARS Document Validator v2.0

Comprehensive validator for EARS documents against EARS_VALIDATION_RULES.md.
Validates metadata, structure, EARS syntax, cross-references, and formatting.

Usage:
    python validate_ears.py [--path PATH] [--verbose] [--fix-suggestions]

Examples:
    python validate_ears.py                                    # Validate all EARS docs
    python validate_ears.py --path docs/EARS/EARS-006.md       # Validate single file
    python validate_ears.py --verbose                          # Show all checks
    python validate_ears.py --fix-suggestions                  # Show fix commands
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple
from collections import Counter

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


class ValidationResult(NamedTuple):
    """Single validation result."""
    file: str
    rule: str
    severity: str  # 'error' or 'warning'
    message: str
    line: int = 0
    fix_suggestion: str = ""


class EarsValidator:
    """Validates EARS documents against comprehensive schema rules."""

    # === METADATA RULES ===
    REQUIRED_TAGS = ["ears", "layer-3-artifact"]
    FORBIDDEN_TAG_PATTERNS = [
        r"^ears-requirements$",
        r"^ears-formal-requirements$",
        r"^ears-document$",
        r"^ears-\d{3}$",
    ]
    REQUIRED_CUSTOM_FIELDS = ["document_type", "artifact_type", "layer", "priority", "development_status"]
    REQUIRED_DOCUMENT_TYPE = "ears"
    REQUIRED_ARTIFACT_TYPE = "EARS"
    REQUIRED_LAYER = 3

    # === STRUCTURE RULES ===
    REQUIRED_SECTIONS = [
        "Document Control",
        "Purpose",
        "Traceability",
    ]

    # === EARS SYNTAX PATTERNS ===
    EARS_PATTERNS = {
        "event_driven": r"WHEN\s+.+?\s+THE\s+.+?\s+SHALL\s+",
        "state_driven": r"WHILE\s+.+?\s+THE\s+.+?\s+SHALL\s+",
        "unwanted": r"IF\s+.+?\s+THE\s+.+?\s+SHALL\s+",
        "ubiquitous": r"THE\s+.+?\s+SHALL\s+",
    }

    # === REQUIREMENT ID PATTERN ===
    # Correct: #### EARS.030.001: Title
    # Incorrect: #### Event-001: Title, #### State-001: Title
    CORRECT_REQ_ID_PATTERN = r"^####\s+EARS[.-](\d{3})[.-](\d{3}):\s+.+"
    INCORRECT_REQ_ID_PATTERNS = [
        r"^####\s+Event-\d+:\s+",
        r"^####\s+State-\d+:\s+",
        r"^####\s+Unwanted-\d+:\s+",
        r"^####\s+Ubiquitous-\d+:\s+",
    ]

    # === TABLE SYNTAX ===
    MALFORMED_TABLE_SEPARATOR = r"\|-+\|\s*\|$"

    # === TRACEABILITY ===
    SOURCE_DOC_PATTERN = r"@prd:\s*PRD-\d{3}"
    TRACEABILITY_TAG_PATTERN = r"@(prd|brd|ears|threshold|entity):\s*\S+"

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[ValidationResult] = []

    def validate_file(self, file_path: Path) -> list[ValidationResult]:
        """Validate a single EARS file."""
        self.results = []

        if not file_path.exists():
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E000",
                severity="error",
                message=f"File not found: {file_path}"
            ))
            return self.results

        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Extract document ID from filename
        doc_id_match = re.search(r"EARS-(\d{3})", file_path.name)
        doc_id = doc_id_match.group(1) if doc_id_match else None

        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)
        if frontmatter is None:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E001",
                severity="error",
                message="Missing or invalid YAML frontmatter"
            ))
            return self.results

        # === METADATA VALIDATIONS ===
        self._validate_tags(file_path, frontmatter)
        self._validate_custom_fields(file_path, frontmatter)

        # === STRUCTURE VALIDATIONS ===
        self._validate_required_sections(file_path, content)
        self._validate_section_numbering(file_path, content)
        self._validate_document_control(file_path, content)
        self._validate_single_h1(file_path, content)

        # === TABLE SYNTAX VALIDATIONS ===
        self._validate_table_syntax(file_path, lines)

        # === REQUIREMENT ID VALIDATIONS ===
        self._validate_requirement_ids(file_path, lines, doc_id)

        # === EARS SYNTAX VALIDATIONS ===
        self._validate_ears_syntax(file_path, content)
        self._validate_atomic_requirements(file_path, content)
        self._validate_measurable_constraints(file_path, content)

        # === TRACEABILITY VALIDATIONS ===
        self._validate_source_document(file_path, content)
        self._validate_traceability_format(file_path, content)
        self._validate_brd_tag_presence(file_path, content)

        # === BDD-READY SCORE ===
        self._validate_bdd_ready_score(file_path, content)

        # === STATUS vs BDD-READY SCORE CONSISTENCY ===
        self._validate_status_bdd_consistency(file_path, content)

        # === AUTHOR STANDARDIZATION ===
        self._validate_author(file_path, content)

        # === BLOCK QUOTE TAGS (E050) ===
        self._validate_no_block_quote_tags(file_path, content)

        return self.results

    def _extract_frontmatter(self, content: str) -> dict | None:
        """Extract YAML frontmatter from markdown content."""
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None

    # === METADATA VALIDATORS ===

    def _validate_tags(self, file_path: Path, frontmatter: dict) -> None:
        """Validate required and forbidden tags."""
        tags = frontmatter.get("tags", [])

        # Check required tags
        for required_tag in self.REQUIRED_TAGS:
            if required_tag not in tags:
                self.results.append(ValidationResult(
                    file=str(file_path),
                    rule="E002",
                    severity="error",
                    message=f"Missing required tag: '{required_tag}'",
                    fix_suggestion=f"Add '  - {required_tag}' to tags section"
                ))

        # Check forbidden patterns
        for tag in tags:
            for pattern in self.FORBIDDEN_TAG_PATTERNS:
                if re.match(pattern, tag):
                    self.results.append(ValidationResult(
                        file=str(file_path),
                        rule="E003",
                        severity="error",
                        message=f"Forbidden tag pattern: '{tag}'",
                        fix_suggestion=f"Replace '{tag}' with 'ears'"
                    ))

    def _validate_custom_fields(self, file_path: Path, frontmatter: dict) -> None:
        """Validate custom_fields completeness and values."""
        custom_fields = frontmatter.get("custom_fields", {})

        # Check for missing custom_fields entirely
        if not custom_fields:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E004",
                severity="error",
                message="Missing custom_fields section in frontmatter",
                fix_suggestion="Add custom_fields with document_type, artifact_type, layer, priority, development_status"
            ))
            return

        # Check document_type
        doc_type = custom_fields.get("document_type")
        if doc_type != self.REQUIRED_DOCUMENT_TYPE:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E005",
                severity="error",
                message=f"Invalid document_type: '{doc_type}' (expected: 'ears')",
                fix_suggestion="Set document_type: ears"
            ))

        # Check artifact_type
        artifact_type = custom_fields.get("artifact_type")
        if artifact_type != self.REQUIRED_ARTIFACT_TYPE:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E006",
                severity="error",
                message=f"Missing or invalid artifact_type: '{artifact_type}' (expected: 'EARS')",
                fix_suggestion="Set artifact_type: EARS"
            ))

        # Check layer
        layer = custom_fields.get("layer")
        if layer != self.REQUIRED_LAYER:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E007",
                severity="error",
                message=f"Missing or invalid layer: '{layer}' (expected: 3)",
                fix_suggestion="Set layer: 3"
            ))

        # Check architecture_approaches format (must be array)
        if "architecture_approach" in custom_fields:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E008",
                severity="error",
                message="Using 'architecture_approach' (singular) instead of 'architecture_approaches' (array)",
                fix_suggestion="Change to: architecture_approaches: [value]"
            ))

        arch = custom_fields.get("architecture_approaches")
        if arch is not None and not isinstance(arch, list):
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E008",
                severity="error",
                message=f"architecture_approaches must be array, got: {type(arch).__name__}",
                fix_suggestion="Change to: architecture_approaches: [value]"
            ))

    # === STRUCTURE VALIDATORS ===

    def _validate_required_sections(self, file_path: Path, content: str) -> None:
        """Validate required sections exist."""
        for section in self.REQUIRED_SECTIONS:
            pattern = rf"^##\s+(\d+\.\s+)?{re.escape(section)}"
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                self.results.append(ValidationResult(
                    file=str(file_path),
                    rule="E010",
                    severity="error",
                    message=f"Missing required section: '{section}'",
                    fix_suggestion=f"Add '## N. {section}' section"
                ))

    def _validate_section_numbering(self, file_path: Path, content: str) -> None:
        """Validate section numbers are sequential and don't start with 0."""
        section_pattern = r"^## (\d+)\. "
        sections = re.findall(section_pattern, content, re.MULTILINE)

        if not sections:
            return

        section_nums = [int(s) for s in sections]

        # Check for section starting with 0
        if section_nums and section_nums[0] == 0:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E011",
                severity="error",
                message="Section numbering starts with 0 (should start with 1)",
                fix_suggestion="Change '## 0. Document Control' to '## Document Control' or renumber from 1"
            ))

        # Check for duplicates
        if len(section_nums) != len(set(section_nums)):
            duplicates = [num for num, count in Counter(section_nums).items() if count > 1]
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E012",
                severity="error",
                message=f"Duplicate section numbers: {duplicates}",
                fix_suggestion="Renumber sections sequentially"
            ))

    def _validate_document_control(self, file_path: Path, content: str) -> None:
        """Validate Document Control section has required fields."""
        # Check for table format vs list format
        if re.search(r"## 0\. Document Control", content):
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E013",
                severity="error",
                message="Non-standard Document Control format: '## 0. Document Control' with list format",
                fix_suggestion="Use '## Document Control' with table format (| Item | Details |)"
            ))

    def _validate_single_h1(self, file_path: Path, content: str) -> None:
        """Validate document has exactly one H1."""
        h1_matches = re.findall(r"^# .+$", content, re.MULTILINE)
        if len(h1_matches) > 1:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="W001",
                severity="warning",
                message=f"Multiple H1 headings detected ({len(h1_matches)} found)",
                fix_suggestion="Keep only the title as H1, convert others to H2"
            ))

    # === TABLE SYNTAX VALIDATORS ===

    def _validate_table_syntax(self, file_path: Path, lines: list[str]) -> None:
        """Validate Markdown table syntax."""
        for i, line in enumerate(lines, 1):
            # Check for malformed table separator (trailing | |)
            if re.search(self.MALFORMED_TABLE_SEPARATOR, line):
                self.results.append(ValidationResult(
                    file=str(file_path),
                    rule="E020",
                    severity="error",
                    message=f"Malformed table separator at line {i}: trailing '| |'",
                    line=i,
                    fix_suggestion="Remove trailing '| |' from table separator line"
                ))

    # === REQUIREMENT ID VALIDATORS ===

    def _validate_requirement_ids(self, file_path: Path, lines: list[str], doc_id: str) -> None:
        """Validate requirement ID format matches EARS-{DocID}-{Num}: Title pattern."""
        incorrect_count = 0
        correct_count = 0
        found_ids = []

        for i, line in enumerate(lines, 1):
            # Check for incorrect patterns
            for pattern in self.INCORRECT_REQ_ID_PATTERNS:
                if re.match(pattern, line):
                    incorrect_count += 1
                    if incorrect_count <= 3:  # Limit to first 3 examples
                        self.results.append(ValidationResult(
                            file=str(file_path),
                            rule="E030",
                            severity="error",
                            message=f"Non-standard requirement ID format at line {i}: '{line.strip()[:50]}...'",
                            line=i,
                            fix_suggestion=f"Change to: #### EARS-{doc_id}-NNN: Title"
                        ))

            # Count correct patterns and collect IDs for uniqueness check
            match = re.match(self.CORRECT_REQ_ID_PATTERN, line)
            if match:
                correct_count += 1
                req_id = f"EARS-{match.group(1)}-{match.group(2)}"
                found_ids.append((req_id, i))

        # Summary if many incorrect
        if incorrect_count > 3:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E030",
                severity="error",
                message=f"Total {incorrect_count} requirement IDs using non-standard format (Event-N, State-N)",
                fix_suggestion=f"Convert all to: #### EARS-{doc_id}-NNN: Title"
            ))

        # E042: Check for duplicate IDs
        self._validate_requirement_id_uniqueness(file_path, found_ids)

    def _validate_requirement_id_uniqueness(self, file_path: Path, found_ids: list[tuple[str, int]]) -> None:
        """Validate each requirement ID is unique within the document (E042)."""
        seen_ids = {}
        duplicates = []

        for req_id, line_num in found_ids:
            if req_id in seen_ids:
                duplicates.append((req_id, seen_ids[req_id], line_num))
            else:
                seen_ids[req_id] = line_num

        if duplicates:
            for req_id, first_line, dup_line in duplicates[:3]:  # Limit to first 3
                self.results.append(ValidationResult(
                    file=str(file_path),
                    rule="E042",
                    severity="error",
                    message=f"Duplicate requirement ID '{req_id}' at line {dup_line} (first seen at line {first_line})",
                    line=dup_line,
                    fix_suggestion="Renumber duplicate IDs sequentially"
                ))

            if len(duplicates) > 3:
                self.results.append(ValidationResult(
                    file=str(file_path),
                    rule="E042",
                    severity="error",
                    message=f"Total {len(duplicates)} duplicate requirement IDs found",
                    fix_suggestion="Run ID conversion script to fix all duplicates"
                ))

    # === EARS SYNTAX VALIDATORS ===

    def _validate_ears_syntax(self, file_path: Path, content: str) -> None:
        """Validate EARS statements follow WHEN-THE-SHALL-WITHIN patterns."""
        # Count EARS keyword usage
        shall_count = len(re.findall(r"\bSHALL\b", content))
        when_count = len(re.findall(r"\bWHEN\b", content))
        the_count = len(re.findall(r"\bTHE\b", content))

        if shall_count == 0:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="W010",
                severity="warning",
                message="No EARS 'SHALL' statements found",
                fix_suggestion="Add requirements using EARS patterns: WHEN/WHILE/IF [condition] THE [system] SHALL [action]"
            ))

    def _validate_atomic_requirements(self, file_path: Path, content: str) -> None:
        """Validate requirements don't have excessive 'and' clauses."""
        # Find all SHALL statements
        all_shall = re.findall(r"SHALL\s+[^.]+\.", content, re.IGNORECASE)
        total_requirements = len(all_shall)

        # Find SHALL statements with 3+ 'and' clauses (highly compound)
        highly_compound_pattern = r"SHALL\s+[^.]+\s+and\s+[^.]+\s+and\s+[^.]+\s+and\s+"
        highly_compound = re.findall(highly_compound_pattern, content, re.IGNORECASE)

        # Only warn if >20% of requirements are highly compound (3+ ands)
        if total_requirements > 0 and len(highly_compound) > total_requirements * 0.2:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="W011",
                severity="warning",
                message=f"Found {len(highly_compound)} highly compound requirements (3+ 'and' clauses) out of {total_requirements} total",
                fix_suggestion="Consider splitting compound requirements into atomic statements"
            ))

    def _validate_measurable_constraints(self, file_path: Path, content: str) -> None:
        """Validate WITHIN clauses have measurable values."""
        within_count = len(re.findall(r"\bWITHIN\b", content, re.IGNORECASE))
        # Count WITHIN clauses with measurable values:
        # 1. Explicit numeric values anywhere in the WITHIN clause (e.g., "WITHIN processing time <5 seconds")
        # 2. Threshold references (e.g., "WITHIN @threshold:PRD.035.timeout.api")
        # 3. Percentage values (e.g., "WITHIN 99.9% SLA boundaries")
        # Match WITHIN followed by content containing numbers, <, >, or @threshold before the next period
        measurable_with_numbers = len(re.findall(r"WITHIN[^.]*?(\d+|@threshold:)", content, re.IGNORECASE))

        if within_count > 0 and measurable_with_numbers < within_count * 0.5:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="W012",
                severity="warning",
                message=f"Only {measurable_with_numbers}/{within_count} WITHIN clauses have measurable values",
                fix_suggestion="Add specific time/measurement values or @threshold: references to WITHIN clauses"
            ))

    # === TRACEABILITY VALIDATORS ===

    def _validate_source_document(self, file_path: Path, content: str) -> None:
        """Validate Source Document uses @prd: prefix."""
        source_doc_match = re.search(
            r"\|\s*\*\*Source Document\*\*\s*\|\s*([^|]+)\s*\|",
            content
        )

        if source_doc_match:
            value = source_doc_match.group(1).strip()
            if not re.search(self.SOURCE_DOC_PATTERN, value):
                # Check if it's just PRD-NNN without @prd:
                if re.search(r"PRD-\d{3}", value) and "@prd:" not in value:
                    self.results.append(ValidationResult(
                        file=str(file_path),
                        rule="E040",
                        severity="error",
                        message=f"Source Document missing @prd: prefix: '{value}'",
                        fix_suggestion="Change to: @prd: PRD-NNN"
                    ))

    def _validate_traceability_format(self, file_path: Path, content: str) -> None:
        """Validate traceability tags use pipe separators for inline format.

        Note: Both inline pipe format and list format are valid:
        - Inline: **Traceability**: @brd: X | @prd: Y | @threshold: Z
        - List format with bullets is also valid (no pipes needed)
        """
        # Find inline traceability lines (single line with multiple tags)
        traceability_lines = re.findall(r"\*\*Traceability\*\*:\s*(@[^-\n].+)", content)

        for trace_line in traceability_lines:
            # Only check inline format (not list format which starts with -)
            if trace_line.strip().startswith("-"):
                continue  # List format is valid without pipes

            # Count tags in inline format
            tags = re.findall(self.TRACEABILITY_TAG_PATTERN, trace_line)
            if len(tags) > 1:
                # Check for pipe separators in inline format
                if "|" not in trace_line:
                    self.results.append(ValidationResult(
                        file=str(file_path),
                        rule="E041",
                        severity="error",
                        message="Inline traceability tags missing pipe separators between multiple tags",
                        fix_suggestion="Add ' | ' between tags: @brd: X | @prd: Y | @threshold: Z"
                    ))
                    break  # Only report once per file

    def _validate_brd_tag_presence(self, file_path: Path, content: str) -> None:
        """Validate traceability section includes @brd tag (E043 - warning level)."""
        # Check if document has any traceability section
        if "Traceability" not in content and "References" not in content:
            return  # Skip if no traceability section at all

        # Check for @brd: anywhere in traceability or references sections
        has_brd_tag = bool(re.search(r"@brd:\s*BRD-\d{3}", content))

        if not has_brd_tag:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E043",
                severity="warning",
                message="Missing @brd: tag in traceability/references section",
                fix_suggestion="Add @brd: BRD-NNN reference to trace back to source BRD"
            ))

    # === BDD-READY SCORE VALIDATOR ===

    def _validate_bdd_ready_score(self, file_path: Path, content: str) -> None:
        """Validate BDD-Ready Score format."""
        # Skip for reserved documents (N/A is acceptable)
        if re.search(r"BDD-Ready Score.*?N/A", content, re.IGNORECASE):
            return  # Reserved documents don't need numeric BDD score

        # Look for BDD-Ready Score in Document Control
        bdd_pattern = r"BDD-Ready Score.*?(\d+%)"
        match = re.search(bdd_pattern, content)

        if not match:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="W020",
                severity="warning",
                message="Missing BDD-Ready Score in Document Control",
                fix_suggestion="Add: | **BDD-Ready Score** | ✅ NN% (Target: ≥90%) |"
            ))
        else:
            # Check format includes emoji and target
            full_pattern = r"✅\s*\d+%\s*\(Target:\s*≥\d+%\)"
            if not re.search(full_pattern, content):
                self.results.append(ValidationResult(
                    file=str(file_path),
                    rule="W021",
                    severity="warning",
                    message="BDD-Ready Score format incomplete (missing ✅ or target)",
                    fix_suggestion="Use format: ✅ NN% (Target: ≥90%)"
                ))

    # === STATUS vs BDD-READY CONSISTENCY ===

    def _validate_status_bdd_consistency(self, file_path: Path, content: str) -> None:
        """Validate document status matches BDD-Ready score thresholds (E052)."""
        # Extract BDD-Ready score
        bdd_match = re.search(r"BDD-Ready Score.*?(\d+)%", content)
        if not bdd_match:
            return  # Skip if no BDD score

        bdd_score = int(bdd_match.group(1))

        # Extract document status
        status_match = re.search(r"\|\s*\*\*Status\*\*\s*\|\s*([^|]+)\s*\|", content)
        if not status_match:
            return  # Skip if no status found

        status = status_match.group(1).strip()

        # Determine expected status
        if bdd_score >= 90:
            expected = "Approved"
        elif bdd_score >= 70:
            expected = "In Review"
        else:
            expected = "Draft"

        # Check consistency
        if status != expected and status != "Reserved":  # Allow "Reserved" for placeholder docs
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E052",
                severity="warning",
                message=f"Status '{status}' inconsistent with BDD-Ready score {bdd_score}% (expected: '{expected}')",
                fix_suggestion=f"Change status to: {expected}"
            ))

    # === AUTHOR STANDARDIZATION ===

    def _validate_author(self, file_path: Path, content: str) -> None:
        """Validate author is standard 'BeeLocal Engineering Team' (E051)."""
        author_match = re.search(r"\|\s*\*\*Author\*\*\s*\|\s*([^|]+)\s*\|", content)
        if not author_match:
            return  # Skip if no author field

        author = author_match.group(1).strip()
        standard_author = "BeeLocal Engineering Team"

        if author != standard_author:
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E051",
                severity="warning",
                message=f"Non-standard author: '{author}'",
                fix_suggestion=f"Change to: {standard_author}"
            ))

    # === BLOCK QUOTE TAGS ===

    def _validate_no_block_quote_tags(self, file_path: Path, content: str) -> None:
        """Validate traceability uses standard format, not block quote tags (E050)."""
        if re.search(r">\s*\*\*Tags\*\*:", content):
            self.results.append(ValidationResult(
                file=str(file_path),
                rule="E050",
                severity="error",
                message="Using block quote '> **Tags**:' format instead of standard '**Traceability**:'",
                fix_suggestion="Change '> **Tags**:' to '**Traceability**:' and use pipe separators"
            ))

    # === DIRECTORY VALIDATION ===

    def validate_directory(self, dir_path: Path) -> list[ValidationResult]:
        """Validate all EARS files in a directory."""
        all_results = []

        for md_file in sorted(dir_path.glob("EARS-*.md")):
            if md_file.name == "EARS-000_index.md":
                continue  # Skip index file
            results = self.validate_file(md_file)
            all_results.extend(results)

        return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Validate EARS documents against comprehensive schema rules (v2.0)"
    )
    parser.add_argument(
        "--path",
        type=str,
        default="docs/EARS",
        help="Path to EARS file or directory"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all validation checks"
    )
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Show fix suggestions for each issue"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Show only summary counts by rule"
    )

    args = parser.parse_args()

    validator = EarsValidator(verbose=args.verbose)
    path = Path(args.path)

    if path.is_file():
        results = validator.validate_file(path)
    elif path.is_dir():
        results = validator.validate_directory(path)
    else:
        print(f"ERROR: Path not found: {path}")
        sys.exit(1)

    # Group results by severity
    errors = [r for r in results if r.severity == "error"]
    warnings = [r for r in results if r.severity == "warning"]

    # Print results
    print(f"\n{'='*70}")
    print("EARS VALIDATION REPORT v2.0")
    print(f"{'='*70}\n")

    if not results:
        print("✅ All EARS documents passed validation!")
        sys.exit(0)

    if args.summary_only:
        # Count by rule
        error_counts = Counter(r.rule for r in errors)
        warning_counts = Counter(r.rule for r in warnings)

        print("ERROR SUMMARY BY RULE:")
        for rule, count in sorted(error_counts.items()):
            print(f"  [{rule}]: {count} occurrences")
        print()
        print("WARNING SUMMARY BY RULE:")
        for rule, count in sorted(warning_counts.items()):
            print(f"  [{rule}]: {count} occurrences")
    else:
        if errors:
            print(f"❌ ERRORS ({len(errors)}):\n")
            # Group by file
            files_with_errors = {}
            for r in errors:
                fname = Path(r.file).name
                if fname not in files_with_errors:
                    files_with_errors[fname] = []
                files_with_errors[fname].append(r)

            for fname, file_errors in sorted(files_with_errors.items()):
                print(f"  📄 {fname}")
                for r in file_errors:
                    line_info = f" (line {r.line})" if r.line else ""
                    print(f"    [{r.rule}]{line_info} {r.message}")
                    if args.fix_suggestions and r.fix_suggestion:
                        print(f"      💡 {r.fix_suggestion}")
                print()

        if warnings:
            print(f"⚠️  WARNINGS ({len(warnings)}):\n")
            files_with_warnings = {}
            for r in warnings:
                fname = Path(r.file).name
                if fname not in files_with_warnings:
                    files_with_warnings[fname] = []
                files_with_warnings[fname].append(r)

            for fname, file_warnings in sorted(files_with_warnings.items()):
                print(f"  📄 {fname}")
                for r in file_warnings:
                    print(f"    [{r.rule}] {r.message}")
                    if args.fix_suggestions and r.fix_suggestion:
                        print(f"      💡 {r.fix_suggestion}")
                print()

    # Rule reference
    print(f"{'='*70}")
    print("RULE REFERENCE:")
    print("  E002-E008: Metadata/Tags    E010-E013: Structure")
    print("  E020: Table Syntax          E030: Requirement IDs")
    print("  E040-E041: Traceability     E042: ID Uniqueness")
    print("  E043/W: @brd Tag Presence   W010-W012: EARS Syntax")
    print("  W020-W021: BDD-Ready Score  W001: Multiple H1")
    print("  E050: Block Quote Tags      E051: Author Standard")
    print("  E052: Status-BDD Mismatch")
    print(f"{'='*70}")
    print(f"Summary: {len(errors)} errors, {len(warnings)} warnings")
    print(f"{'='*70}")

    # Exit with error code if there are errors
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
