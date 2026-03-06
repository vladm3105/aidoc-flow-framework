#!/usr/bin/env python3
"""TASKS (Code Generation Plan) Validator v2.0 (2026-03-06)

Python validator for TASKS documents (Layer 10 artifacts).
Implements 14 comprehensive checks based on bash validator v1.0.

Validates TASKS documents against:
- TASKS-TEMPLATE.md structure
- AI Dev Flow SDD framework standards
- Layer 10 artifact requirements
- Code generation task structure
- Implementation Contracts (Section 7-8)
- Phase hierarchy and dependencies

Usage:
    python validate_tasks.py <TASKS_FILE> [OPTIONS]

    Options:
      --verbose          Show detailed validation output
      --json             Output results in JSON format
      --corpus-mode      Enable corpus-level validation (cross-references)
      --base-path PATH   Base path for corpus-level validation
      --no-color         Disable colored output
      --version          Show validator version
      --help             Show this help message

Examples:
    # Basic validation
    python validate_tasks.py docs/TASKS/TASKS-001_gateway_service.md

    # Verbose output
    python validate_tasks.py TASKS-001.md --verbose

    # JSON output
    python validate_tasks.py TASKS-001.md --json

    # Corpus-level validation
    python validate_tasks.py TASKS-001.md --corpus-mode --base-path /opt/data/project/docs

Exit Codes:
    0: Pass (no errors, no warnings)
    1: Pass with warnings (no errors, warnings present)
    2: Fail (errors present)

Author: Claude (TSPEC v2.0 team)
Based on: validate_tasks.sh v1.0 (563 lines, 13 checks)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import error code modules
try:
    from tasks_error_codes import HAS_ERROR_CODES, get_statistics
    from tasks_error_code_helpers import (
        format_error,
        format_warning,
        format_info,
        calculate_exit_code,
        format_summary,
        count_by_severity,
    )
    from tasks_ast_parser import ContractValidator
    HAS_AST_PARSER = True
except ImportError as e:
    print(f"WARNING: Cannot import required modules: {e}")
    print("Ensure tasks_error_codes, tasks_error_code_helpers, and tasks_ast_parser are available")
    HAS_AST_PARSER = False

# Try to import YAML parser
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("WARNING: PyYAML not installed. Frontmatter validation will be limited.")
    print("Install with: pip install PyYAML")


# ============================================================================
# CONSTANTS
# ============================================================================

VERSION = "2.0.0"
RELEASE_DATE = "2026-03-06"
SCRIPT_NAME = "validate_tasks.py"

# Filename pattern: TASKS-NNN_descriptive_slug.md
FILENAME_PATTERN = re.compile(r'^TASKS-[0-9]{2,}_[a-z0-9_]+\.md$')

# Required document control fields
REQUIRED_DOC_CONTROL_FIELDS = [
    "TASKS ID",
    "Title",
    "Status",
    "Version",
    "Created",
    "Last Updated",
    "Author",
    "Parent SPEC",
    "Complexity",
]

# Valid status enum values
VALID_STATUS_VALUES = ["Draft", "Ready", "In Progress", "Completed", "Blocked"]

# Required sections
REQUIRED_SECTIONS = [
    "## 1. Overview",
    "## 2. Phase",
    "## 3. Dependencies",
    "## 4. Acceptance Criteria",
    "## Traceability",
]

# Required traceability tags (Layer 10 minimum)
REQUIRED_TAGS = ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req", "@spec"]
OPTIONAL_TAGS = ["@ctr"]

# Token size thresholds
TOKEN_SIZE_OPTIMAL_KB = 100
TOKEN_SIZE_WARNING_KB = 200

# Deprecated element ID patterns
DEPRECATED_ID_PATTERNS = [
    r'^### (FR|QA|AC|BC|BO)-[0-9]{3}:',
    r'TASKS-[0-9]{3}-[0-9]{2}',
]

# Unified element ID pattern: TASKS.NN.TT.SS
UNIFIED_ID_PATTERN = re.compile(r'TASKS\.[0-9]{2,9}\.[0-9]{2,9}\.[0-9]{2,9}')


# ============================================================================
# VALIDATOR CLASS
# ============================================================================

class TasksValidator:
    """TASKS document validator with 14 comprehensive checks.

    Implements validation logic from bash validator v1.0 (563 lines).
    Provides error code integration, JSON output, and corpus-level validation.

    Phase 1 (Current): Checks 1-6 (core validator)
    Phase 2 (Future): Checks 7-11 (advanced validation)
    Phase 3 (Future): Checks 9, 12 (TASKS-specific features with AST/corpus)
    Phase 4 (Future): Enhanced features (dependency graph, testing)
    """

    def __init__(
        self,
        file_path: str,
        corpus_mode: bool = False,
        base_path: Optional[Path] = None,
        verbose: bool = False,
    ):
        """Initialize TASKS validator.

        Args:
            file_path: Path to TASKS file
            corpus_mode: Enable corpus-level validation (cross-references)
            base_path: Base path for corpus-level validation (default: parent.parent of file)
            verbose: Enable verbose output
        """
        self.file_path = Path(file_path)
        self.corpus_mode = corpus_mode
        self.base_path = base_path or self.file_path.parent.parent
        self.verbose = verbose

        # Read file content
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        self.content = self.file_path.read_text(encoding='utf-8')
        self.lines = self.content.splitlines()

        # Parse frontmatter
        self.frontmatter = self._parse_frontmatter()

        # Issue collectors
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

        # Validation results
        self.results: Dict = {}

    def validate(self) -> Dict:
        """Run all 14 validation checks.

        Returns:
            Validation results dictionary

        Raises:
            Exception: If critical validation error occurs
        """
        # Phase 1: Core validator (Checks 1-6)
        self._check_01_filename_format()
        self._check_02_frontmatter_validation()
        self._check_03_document_control_table()
        self._check_04_required_sections()
        self._check_05_phase_structure()
        self._check_06_task_detail_validation()

        # Phase 2: Advanced validation (Checks 7-8, 10-11)
        self._check_07_dependencies_validation()
        self._check_08_acceptance_criteria()
        self._check_10_element_id_format()
        self._check_11_traceability_tags()

        # Phase 3: TASKS-specific features (Checks 9, 12)
        self._check_09_implementation_contracts()
        self._check_12_cross_reference_validation()

        # Phase 4: Enhanced features (Checks 13, 14)
        self._check_13_code_generation_readiness()
        self._check_14_token_size_validation()

        # Generate results
        return self._generate_report()

    # ========================================================================
    # PHASE 1: CORE VALIDATOR (CHECKS 1-6)
    # ========================================================================

    def _check_01_filename_format(self) -> None:
        """CHECK 1: Validate filename format.

        Pattern: TASKS-NNN_descriptive_slug.md
        Example: TASKS-001_gateway_service.md

        Error Codes:
        - TASKS-E001: Invalid filename format
        """
        filename = self.file_path.name

        if not FILENAME_PATTERN.match(filename):
            if HAS_ERROR_CODES:
                self.errors.append(format_error("TASKS-E001", filename=filename))
            else:
                self.errors.append(f"Invalid filename format: {filename}")

    def _check_02_frontmatter_validation(self) -> None:
        """CHECK 2: Validate YAML frontmatter structure and fields.

        Required Fields:
        - artifact_type: TASKS
        - layer: 10
        - parent_spec: SPEC-NNN

        Warning Fields:
        - layer-10-artifact tag (should be present)

        Error Codes:
        - TASKS-E002: Missing YAML frontmatter
        - TASKS-E003: Invalid artifact_type
        - TASKS-E004: Invalid layer
        - TASKS-E005: Missing parent_spec
        - TASKS-W001: Missing layer-10-artifact tag
        """
        if not self.frontmatter:
            if HAS_ERROR_CODES:
                self.errors.append(format_error("TASKS-E002"))
            else:
                self.errors.append("Missing YAML frontmatter")
            return

        # Check artifact_type
        artifact_type = self.frontmatter.get("artifact_type")
        if artifact_type != "TASKS":
            if HAS_ERROR_CODES:
                self.errors.append(format_error("TASKS-E003", value=artifact_type or "missing"))
            else:
                self.errors.append(f"Invalid artifact_type: {artifact_type} (must be TASKS)")

        # Check layer
        layer = self.frontmatter.get("layer")
        if layer != 10:
            if HAS_ERROR_CODES:
                self.errors.append(format_error("TASKS-E004", value=layer or "missing"))
            else:
                self.errors.append(f"Invalid layer: {layer} (must be 10)")

        # Check parent_spec
        parent_spec = self.frontmatter.get("parent_spec")
        if not parent_spec:
            if HAS_ERROR_CODES:
                self.errors.append(format_error("TASKS-E005"))
            else:
                self.errors.append("Missing parent_spec field")

        # Check tags
        tags = self.frontmatter.get("tags", [])
        if "layer-10-artifact" not in tags:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W001"))
            else:
                self.warnings.append("Missing layer-10-artifact tag")

    def _check_03_document_control_table(self) -> None:
        """CHECK 3: Validate Document Control table.

        Required Fields:
        - TASKS ID, Title, Status, Version, Created, Last Updated,
          Author, Parent SPEC, Complexity

        Status Enum:
        - Draft | Ready | In Progress | Completed | Blocked

        Error Codes:
        - TASKS-E006: Missing document control field
        - TASKS-W002: Invalid status enum value
        """
        for field in REQUIRED_DOC_CONTROL_FIELDS:
            # Case-insensitive search for field
            pattern = re.compile(rf'\b{re.escape(field)}\b', re.IGNORECASE)
            if not pattern.search(self.content):
                if HAS_ERROR_CODES:
                    self.errors.append(format_error("TASKS-E006", field=field))
                else:
                    self.errors.append(f"Missing document control field: {field}")

        # Check status enum value
        status_match = re.search(
            r'Status.*\|.*(Draft|Ready|In Progress|Completed|Blocked)',
            self.content,
            re.IGNORECASE
        )
        if not status_match:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W002", status="unknown"))
            else:
                self.warnings.append("Status should be: Draft | Ready | In Progress | Completed | Blocked")

    def _check_04_required_sections(self) -> None:
        """CHECK 4: Validate required section headers.

        Required Sections:
        - ## 1. Overview
        - ## 2. Phase
        - ## 3. Dependencies
        - ## 4. Acceptance Criteria
        - ## Traceability

        Error Codes:
        - TASKS-E007: Missing required section
        """
        for section in REQUIRED_SECTIONS:
            if section not in self.content:
                if HAS_ERROR_CODES:
                    self.errors.append(format_error("TASKS-E007", section=section))
                else:
                    self.errors.append(f"Missing required section: {section}")

    def _check_05_phase_structure(self) -> None:
        """CHECK 5: Validate phase hierarchy structure.

        Hierarchy:
        - Phases: ### Phase N: [Name]
        - Tasks: #### TASK-NNN: [Description]
        - Checkboxes: - [x] or - [ ]

        Thresholds:
        - Phases: ≥1 (error if 0)
        - Tasks: ≥1 (warning if 0)
        - Checkboxes: ≥1 (warning if 0)

        Error Codes:
        - TASKS-E008: No phases defined
        - TASKS-W003: No TASK-NNN items found
        - TASKS-W004: No task checkboxes found
        - TASKS-E035: Duplicate task IDs
        - TASKS-W032: Phase numbering not sequential
        - TASKS-W033: Phase has no TASK-NNN items
        """
        # Count phases
        phase_matches = re.findall(r'^### Phase (\d+):', self.content, re.MULTILINE)
        phase_count = len(phase_matches)

        if phase_count == 0:
            if HAS_ERROR_CODES:
                self.errors.append(format_error("TASKS-E008"))
            else:
                self.errors.append("No phases defined (expected ≥1)")
        else:
            # Check phase numbering sequence
            phase_nums = [int(p) for p in phase_matches]
            expected = list(range(1, phase_count + 1))
            if phase_nums != expected:
                if HAS_ERROR_CODES:
                    self.warnings.append(format_warning("TASKS-W032", sequence=str(phase_nums)))
                else:
                    self.warnings.append(f"Phase numbering not sequential: {phase_nums}")

        # Count tasks
        task_matches = re.findall(r'^#### (TASK-\d+):', self.content, re.MULTILINE)
        task_count = len(task_matches)

        if task_count == 0:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W003"))
            else:
                self.warnings.append("No TASK-NNN items found (expected ≥1)")
        else:
            # Check for duplicate task IDs
            duplicates = [t for t in set(task_matches) if task_matches.count(t) > 1]
            if duplicates:
                if HAS_ERROR_CODES:
                    self.errors.append(format_error("TASKS-E035", duplicates=", ".join(duplicates)))
                else:
                    self.errors.append(f"Duplicate task IDs: {', '.join(duplicates)}")

        # Count checkboxes
        checkbox_count = self.content.count("[x]") + self.content.count("[ ]")
        if checkbox_count == 0:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W004"))
            else:
                self.warnings.append("No task checkboxes found (expected ≥1)")

    def _check_06_task_detail_validation(self) -> None:
        """CHECK 6: Validate task field structure.

        Required Task Fields:
        - Input: (per task)
        - Output: (per task)
        - Acceptance: (per task)

        File References:
        - Backtick-wrapped file paths

        Error Codes:
        - TASKS-W005: Missing Input field
        - TASKS-W006: Missing Output field
        - TASKS-W007: Missing Acceptance field
        - TASKS-W008: No file references found
        """
        # Count task fields (case-insensitive)
        input_count = len(re.findall(r'Input:', self.content, re.IGNORECASE))
        output_count = len(re.findall(r'Output:', self.content, re.IGNORECASE))
        acceptance_count = len(re.findall(r'Acceptance:', self.content, re.IGNORECASE))

        if input_count == 0:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W005"))
            else:
                self.warnings.append("Missing 'Input:' field in task details")

        if output_count == 0:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W006"))
            else:
                self.warnings.append("Missing 'Output:' field in task details")

        if acceptance_count == 0:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W007"))
            else:
                self.warnings.append("Missing 'Acceptance:' field in task details")

        # Check for file references
        file_ref_pattern = re.compile(r'`[a-z_/]+\.(py|ts|js|yaml|json|md)`')
        file_refs = file_ref_pattern.findall(self.content)
        if not file_refs:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W008"))
            else:
                self.warnings.append("No file references found")

    # ========================================================================
    # PHASE 2: ADVANCED VALIDATION (CHECKS 7-8, 10-11)
    # ========================================================================

    def _check_07_dependencies_validation(self) -> None:
        """CHECK 7: Validate dependencies documentation.

        Validates:
        - Upstream dependencies section present
        - Downstream dependencies section present
        - Blocking relationships documented

        Error Codes:
        - TASKS-W009: Missing upstream dependencies
        - TASKS-W010: Missing downstream dependencies
        - TASKS-W011: No blocking relationships documented
        """
        # Check for upstream dependencies
        if not re.search(r'upstream', self.content, re.IGNORECASE):
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W009"))
            else:
                self.warnings.append("Missing upstream dependencies section")

        # Check for downstream dependencies
        if not re.search(r'downstream', self.content, re.IGNORECASE):
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W010"))
            else:
                self.warnings.append("Missing downstream dependencies section")

        # Check for blocking relationships
        blocking_pattern = r'blocks|blocked by|depends on'
        if not re.search(blocking_pattern, self.content, re.IGNORECASE):
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W011"))
            else:
                self.warnings.append("No blocking relationships documented")

    def _check_08_acceptance_criteria(self) -> None:
        """CHECK 8: Validate acceptance criteria.

        Validates:
        - Test coverage targets (unit/integration/e2e with percentages)
        - BDD scenario references (BDD-NNN)
        - Completion criteria keywords

        Error Codes:
        - TASKS-W012: No test coverage targets
        - TASKS-W013: No BDD scenario references
        - TASKS-W014: No completion criteria documented
        """
        # Check for test coverage targets
        coverage_pattern = r'(unit|integration|e2e|coverage).*[0-9]+%'
        if not re.search(coverage_pattern, self.content, re.IGNORECASE):
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W012"))
            else:
                self.warnings.append("No test coverage targets found")

        # Check for BDD scenario references
        bdd_refs = re.findall(r'BDD-\d+', self.content)
        if not bdd_refs:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W013"))
            else:
                self.warnings.append("No BDD scenario references found")

        # Check for completion criteria
        completion_pattern = r'definition of done|completion criteria|done when'
        if not re.search(completion_pattern, self.content, re.IGNORECASE):
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W014"))
            else:
                self.warnings.append("No completion criteria documented")

    def _check_10_element_id_format(self) -> None:
        """CHECK 10: Validate element ID format.

        Validates:
        - No deprecated element ID formats (FR-001, QA-001, AC-001, BC-001, BO-001)
        - No old TASKS-NNN-YY format
        - Counts unified format IDs (TASKS.NN.TT.SS)

        Error Codes:
        - TASKS-E009: Deprecated element ID format found
        """
        deprecated_found = False

        # Check for deprecated patterns
        for pattern in DEPRECATED_ID_PATTERNS:
            matches = re.findall(pattern, self.content, re.MULTILINE)
            if matches:
                deprecated_found = True
                if HAS_ERROR_CODES:
                    self.errors.append(format_error("TASKS-E009", pattern=pattern))
                else:
                    self.errors.append(f"Deprecated element ID format found: {pattern}")

        # Count unified format IDs (informational)
        unified_matches = UNIFIED_ID_PATTERN.findall(self.content)
        if self.verbose and unified_matches:
            unified_count = len(unified_matches)
            print(f"  Unified format element IDs found: {unified_count}")

    def _check_11_traceability_tags(self) -> None:
        """CHECK 11: Validate traceability tags (Layer 10).

        Required Tags (8):
        - @brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec

        Optional Tags:
        - @ctr

        Validates:
        - All 8 required tags present
        - No empty tag values

        Error Codes:
        - TASKS-E010: Missing required traceability tag
        - TASKS-E011: Empty tag value
        """
        tag_count = 0

        # Check required tags
        for tag in REQUIRED_TAGS:
            # Pattern: @tag: VALUE or - `@tag: VALUE`
            pattern = rf'^{tag}:|^\- `{tag}:'
            if re.search(pattern, self.content, re.MULTILINE):
                tag_count += 1
            else:
                if HAS_ERROR_CODES:
                    self.errors.append(format_error("TASKS-E010", tag=tag))
                else:
                    self.errors.append(f"Missing required traceability tag: {tag}")

        # Check optional tags (count if present)
        for tag in OPTIONAL_TAGS:
            pattern = rf'^{tag}:|^\- `{tag}:'
            if re.search(pattern, self.content, re.MULTILINE):
                tag_count += 1

        # Check for empty tags
        empty_tag_pattern = r'@[a-z]+:\s*$'
        empty_tags = re.findall(empty_tag_pattern, self.content, re.MULTILINE)
        if empty_tags:
            for tag in empty_tags:
                if HAS_ERROR_CODES:
                    self.errors.append(format_error("TASKS-E011", tag=tag.strip()))
                else:
                    self.errors.append(f"Empty tag value found: {tag.strip()}")

        # Report total tag count
        if self.verbose:
            print(f"  Total traceability tags: {tag_count}")

    # ========================================================================
    # PHASE 3: TASKS-SPECIFIC FEATURES (CHECKS 9, 12)
    # ========================================================================

    def _check_09_implementation_contracts(self) -> None:
        """CHECK 9: Validate Implementation Contracts (Section 7-8).

        Uses AST parsing to validate:
        - Protocol interfaces (typing.Protocol)
        - TypedDict schemas (typing.TypedDict)
        - Pydantic models (pydantic.BaseModel)
        - Dataclasses (@dataclass)
        - Exception hierarchies
        - State machines (Enum with VALID_TRANSITIONS)

        Error Codes:
        - TASKS-E020: Invalid Protocol definition
        - TASKS-E021: Invalid TypedDict schema
        - TASKS-E022: Invalid BaseModel schema
        - TASKS-E023: Invalid dataclass definition
        - TASKS-E024: Missing method signatures in Protocol
        - TASKS-W015: Missing return type hints
        - TASKS-W022: Exception missing error_code
        - TASKS-W023: State enum missing VALID_TRANSITIONS
        - TASKS-W024: Pydantic model missing validators
        - TASKS-I001: No embedded contracts found
        """
        if not HAS_AST_PARSER:
            self.warnings.append("AST parser not available - skipping contract validation")
            return

        # Use ContractValidator
        contract_validator = ContractValidator(self.content, verbose=self.verbose)
        results = contract_validator.validate_all_contracts()

        # Merge results
        self.errors.extend(results['errors'])
        self.warnings.extend(results['warnings'])
        self.info.extend(results['info'])

    def _check_12_cross_reference_validation(self) -> None:
        """CHECK 12: Validate cross-document references (corpus-level).

        Validates (if corpus_mode enabled):
        - Parent SPEC file exists
        - Parent SPEC CODE-Ready score >= 90%
        - Referenced REQ files exist
        - Referenced ADR files exist

        Error Codes:
        - TASKS-E012: Parent SPEC file not found
        - TASKS-W025: Parent SPEC CODE-Ready score < 90%
        - TASKS-W026: Referenced REQ not found
        - TASKS-W027: Referenced ADR not found
        """
        if not self.corpus_mode:
            # Corpus mode not enabled, skip cross-reference validation
            return

        # Validate parent SPEC exists
        parent_spec = self.frontmatter.get("parent_spec")
        if parent_spec:
            spec_dir = self.base_path / "09_SPEC"
            if spec_dir.exists():
                spec_files = list(spec_dir.glob(f"{parent_spec}*.yaml"))

                if not spec_files:
                    if HAS_ERROR_CODES:
                        self.errors.append(format_error("TASKS-E012", spec_id=parent_spec))
                    else:
                        self.errors.append(f"Parent SPEC file not found: {parent_spec}")
                else:
                    # Check CODE-Ready score
                    spec_content = spec_files[0].read_text()
                    score_match = re.search(r'code_ready_score:\s*(\d+)', spec_content)
                    if score_match:
                        score = int(score_match.group(1))
                        if score < 90:
                            if HAS_ERROR_CODES:
                                self.warnings.append(format_warning(
                                    "TASKS-W025",
                                    spec_id=parent_spec,
                                    score=score
                                ))
                            else:
                                self.warnings.append(
                                    f"Parent SPEC {parent_spec} CODE-Ready score < 90%: {score}%"
                                )

        # Validate REQ references
        req_refs = set(re.findall(r'REQ-\d+', self.content))
        if req_refs:
            req_dir = self.base_path / "07_REQ"
            if req_dir.exists():
                for req_id in req_refs:
                    req_files = list(req_dir.glob(f"{req_id}*.md"))
                    if not req_files:
                        if HAS_ERROR_CODES:
                            self.warnings.append(format_warning("TASKS-W026", req_id=req_id))
                        else:
                            self.warnings.append(f"Referenced REQ not found: {req_id}")

        # Validate ADR references
        adr_refs = set(re.findall(r'ADR-\d+', self.content))
        if adr_refs:
            adr_dir = self.base_path / "05_ADR"
            if adr_dir.exists():
                for adr_id in adr_refs:
                    adr_files = list(adr_dir.glob(f"{adr_id}*.md"))
                    if not adr_files:
                        if HAS_ERROR_CODES:
                            self.warnings.append(format_warning("TASKS-W027", adr_id=adr_id))
                        else:
                            self.warnings.append(f"Referenced ADR not found: {adr_id}")

    # ========================================================================
    # PHASE 4: ENHANCED FEATURES (CHECKS 13-14)
    # ========================================================================

    def _check_13_code_generation_readiness(self) -> None:
        """CHECK 13: Validate code generation readiness.

        Validates:
        - Module/file/class/function structure documented
        - Import/dependency information present
        - Error handling approach documented

        Error Codes:
        - TASKS-W018: Missing code structure elements
        - TASKS-W019: Missing import/dependency information
        - TASKS-W020: Missing error handling documentation
        """
        # Check for module/file structure
        structure_pattern = r'module|file|class|function'
        if not re.search(structure_pattern, self.content, re.IGNORECASE):
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W018"))
            else:
                self.warnings.append("Missing code structure elements")

        # Check for import/dependency information
        import_pattern = r'import|dependency|require'
        if not re.search(import_pattern, self.content, re.IGNORECASE):
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W019"))
            else:
                self.warnings.append("Missing import/dependency information")

        # Check for error handling
        error_pattern = r'error|exception|handle'
        if not re.search(error_pattern, self.content, re.IGNORECASE):
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W020"))
            else:
                self.warnings.append("Missing error handling documentation")

    def _check_14_token_size_validation(self) -> None:
        """CHECK 14: Validate token size.

        Thresholds:
        - Optimal: <100KB
        - Warning: 100-200KB
        - Error: >200KB

        Error Codes:
        - TASKS-W021: File size exceeds 200KB optimal
        """
        # Get file size in KB
        file_size = len(self.content.encode('utf-8'))
        file_kb = file_size // 1024

        if file_kb > TOKEN_SIZE_WARNING_KB:
            if HAS_ERROR_CODES:
                self.warnings.append(format_warning("TASKS-W021", size_kb=file_kb))
            else:
                self.warnings.append(
                    f"File size {file_kb}KB exceeds 200KB optimal"
                )
        elif file_kb > TOKEN_SIZE_OPTIMAL_KB and self.verbose:
            print(f"  File size {file_kb}KB - consider optimization")

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _parse_frontmatter(self) -> Dict:
        """Parse YAML frontmatter from document.

        Returns:
            Dictionary of frontmatter fields

        Note:
            If PyYAML not available, returns empty dict
        """
        if not HAS_YAML:
            return {}

        # Extract frontmatter between --- delimiters
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', self.content, re.DOTALL)
        if not match:
            return {}

        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def _generate_report(self) -> Dict:
        """Generate validation report.

        Returns:
            Dictionary with validation results
        """
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        info_count = len(self.info)
        exit_code = calculate_exit_code(error_count, warning_count)

        self.results = {
            "file": str(self.file_path),
            "validator_version": VERSION,
            "timestamp": RELEASE_DATE,
            "phase": "Complete (All 14 Checks)",
            "checks_implemented": 14,
            "checks_total": 14,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "counts": {
                "errors": error_count,
                "warnings": warning_count,
                "info": info_count,
            },
            "exit_code": exit_code,
            "status": "FAIL" if exit_code == 2 else "PASS WITH WARNINGS" if exit_code == 1 else "PASS",
        }

        return self.results


# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_header():
    """Print validator header."""
    print("=" * 70)
    print(f"TASKS Validator v{VERSION}")
    print("=" * 70)
    print(f"Complete Validator (All 14 Checks Implemented)")
    print(f"Error Codes: {get_statistics()['total_codes']} codes available")
    print()


def print_results(validator: TasksValidator, use_color: bool = True):
    """Print validation results in human-readable format.

    Args:
        validator: Validator instance with results
        use_color: Enable colored output
    """
    results = validator.results

    print(f"File: {results['file']}")
    print(f"Status: {results['status']}")
    print()

    # Print errors
    if results['errors']:
        print("ERRORS:")
        for error in results['errors']:
            print(f"  {error}")
        print()

    # Print warnings
    if results['warnings']:
        print("WARNINGS:")
        for warning in results['warnings']:
            print(f"  {warning}")
        print()

    # Print info
    if results['info']:
        print("INFO:")
        for info_msg in results['info']:
            print(f"  {info_msg}")
        print()

    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if use_color:
        print(format_summary(results['counts']['errors'], results['counts']['warnings'], results['counts']['info']))
    else:
        print(f"Errors: {results['counts']['errors']} | Warnings: {results['counts']['warnings']} | Info: {results['counts']['info']}")
    print(f"Exit Code: {results['exit_code']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TASKS (Code Generation Plan) Validator v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {SCRIPT_NAME} docs/TASKS/TASKS-001_gateway_service.md
  {SCRIPT_NAME} TASKS-001.md --verbose
  {SCRIPT_NAME} TASKS-001.md --json
  {SCRIPT_NAME} TASKS-001.md --corpus-mode --base-path /opt/data/project/docs

Exit Codes:
  0: Pass (no errors, no warnings)
  1: Pass with warnings
  2: Fail (errors present)
        """
    )

    parser.add_argument("file", help="Path to TASKS file")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--corpus-mode", action="store_true", help="Enable corpus-level validation")
    parser.add_argument("--base-path", type=str, help="Base path for corpus-level validation")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    args = parser.parse_args()

    # Initialize validator
    try:
        validator = TasksValidator(
            file_path=args.file,
            corpus_mode=args.corpus_mode,
            base_path=Path(args.base_path) if args.base_path else None,
            verbose=args.verbose,
        )
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Run validation
    if not args.json:
        print_header()

    results = validator.validate()

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(validator, use_color=not args.no_color)

    return results['exit_code']


if __name__ == "__main__":
    sys.exit(main())
