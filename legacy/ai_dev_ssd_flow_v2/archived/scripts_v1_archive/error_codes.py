#!/usr/bin/env python3
"""
DEPRECATED: This module is deprecated as of UCX v1.9.0.

Migration: Use `ucx.validators.common.error_codes` instead.
Removal: This module will be removed in UCX v2.0.0.

See: /opt/data/docs_flow_framework/UCX/docs/QUICK_START.md

--- Original docstring below ---

Standardized Error Code Registry for SDD Document Validation

Pattern: {TYPE}-{SEVERITY}{NNN}
- TYPE: BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TASKS, XDOC, VAL
- SEVERITY: E (Error), W (Warning), I (Info)
- NNN: 001-999

Exit Codes:
- 0: Pass (no errors, no warnings)
- 1: Warnings only
- 2: Errors present
"""

import warnings
warnings.warn(
    "This module is deprecated. Use 'ucx.validators.common.error_codes' instead. "
    "Will be removed in UCX v2.0.0.",
    DeprecationWarning,
    stacklevel=2
)

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional


class Severity(Enum):
    """Validation severity levels."""
    ERROR = "E"      # Critical issue, blocks workflow
    WARNING = "W"    # Needs attention, does not block unless --strict
    INFO = "I"       # Suggestion, never blocks


@dataclass
class ErrorCode:
    """Error code definition with message and remediation."""
    code: str
    message: str
    remediation: str
    severity: Severity

    @property
    def exit_code(self) -> int:
        """Return exit code based on severity."""
        if self.severity == Severity.ERROR:
            return 2
        elif self.severity == Severity.WARNING:
            return 1
        return 0


# =============================================================================
# ERROR CODE REGISTRY
# =============================================================================

ERROR_REGISTRY: Dict[str, Tuple[str, str]] = {
    # -------------------------------------------------------------------------
    # General Validation (VAL) - Cross-cutting validation errors
    # -------------------------------------------------------------------------
    "VAL-E001": ("File not found", "Verify file path exists"),
    "VAL-E002": ("Invalid YAML syntax", "Fix YAML formatting errors"),
    "VAL-E003": ("Invalid Markdown structure", "Fix heading hierarchy"),
    "VAL-E004": ("Missing required file", "Create required file"),
    "VAL-E005": ("File encoding error", "Ensure UTF-8 encoding"),
    "VAL-W001": ("File exceeds token limit", "Consider splitting document"),
    "VAL-W002": ("Deprecated format detected", "Update to current format"),
    "VAL-I001": ("Schema validation passed", "No action needed"),
    "VAL-I002": ("All checks passed", "No action needed"),

    # -------------------------------------------------------------------------
    # Cross-Document (XDOC) - Traceability and reference validation
    # -------------------------------------------------------------------------
    "XDOC-E001": ("Referenced ID not found", "Verify upstream document exists"),
    "XDOC-E002": ("Missing cumulative tag", "Add required upstream tag"),
    "XDOC-E003": ("Broken cross-reference", "Fix or remove broken reference"),
    "XDOC-E004": ("Orphan document", "Add upstream traceability link"),
    "XDOC-E005": ("Circular reference detected", "Remove circular dependency"),
    "XDOC-W001": ("Weak traceability", "Consider adding more upstream refs"),

    # -------------------------------------------------------------------------
    # BRD (Layer 1) - Business Requirements Document
    # -------------------------------------------------------------------------
    "BRD-E001": ("Invalid H1 format", "Use format: # BRD-NNN: Title"),
    "BRD-E002": ("Missing Document Control section", "Add Section 0"),
    "BRD-E003": ("Missing required tag 'brd'", "Add @brd tag"),
    "BRD-E004": ("Missing required tag 'layer-1-artifact'", "Add layer tag"),
    "BRD-E005": ("Missing Executive Summary section", "Add Section 1"),
    "BRD-E006": ("Missing required section", "Add missing section per BRD template"),
    "BRD-E007": ("Multiple H1 headings detected", "Use single H1 heading only"),
    "BRD-E008": ("Section numbering not sequential", "Fix section number sequence"),
    "BRD-E009": ("Document Control missing required fields", "Add all required fields to Document Control"),
    "BRD-E010": ("Missing Business Objectives (Section 3)", "Add Section 3 Business Objectives"),
    "BRD-E011": ("Missing Business Requirements (Section 4)", "Add Section 4 Business Requirements"),
    "BRD-E012": ("Missing Traceability (Section 11)", "Add Section 11 Traceability"),
    "BRD-E013": ("Missing Section 7.2 Architecture Decision Requirements", "Add Section 7.2 with 7 ADR topic categories"),
    "BRD-E014": ("Missing mandatory ADR topic category", "Add all 7 mandatory ADR topics"),
    "BRD-E015": ("ADR topic missing required Status field", "Add Status (Selected/Pending/N/A)"),
    "BRD-E016": ("Selected ADR topic missing Alternatives Overview table", "Add Alternatives Overview table"),
    "BRD-E017": ("Selected ADR topic missing Cloud Provider Comparison table", "Add Cloud Provider Comparison table"),
    "BRD-E018": ("N/A ADR topic missing explicit reason", "Add explicit reason for N/A status"),
    "BRD-W001": ("Missing stakeholders section", "Consider adding stakeholders"),
    "BRD-W002": ("Requirements not using BRD.NN.01.SS format", "Use unified 4-segment ID format"),
    "BRD-W003": ("Missing Success Metrics (Section 5)", "Add Section 5 Success Metrics"),
    "BRD-W004": ("PRD-Ready Score below 90%", "Complete requirements to reach 90% score"),
    "BRD-W005": ("Missing Stakeholder Analysis", "Add stakeholder analysis section"),
    "BRD-W006": ("File name does not match format", "Use BRD-NNN_descriptive_name.md format"),
    "BRD-W007": ("ADR topic missing cost estimates", "Add Est. Monthly Cost in Alternatives Overview"),
    "BRD-W008": ("ADR topic missing PRD Requirements field", "Add PRD Requirements for each topic"),
    "BRD-W011": ("Missing BRD advisory diagram tag @diagram: c4-l1", "Add C4-L1 tag or accept advisory warning"),
    "BRD-W012": ("Missing BRD advisory diagram tag @diagram: dfd-l0", "Add DFD-L0 tag or accept advisory warning"),
    "BRD-W013": ("Sequence diagram present without BRD sequence tag", "Add @diagram: sequence-sync|sequence-async|sequence-error"),
    "BRD-W014": ("Diagram intent header missing required fields", "Add diagram_type, level, scope_boundary, upstream_refs, downstream_refs"),
    "BRD-I001": ("Consider adding regulatory compliance requirements", "Review regulatory needs"),
    "BRD-I002": ("Consider adding market analysis context", "Add market context if applicable"),
    "BRD-I003": ("Pending ADR topics should be completed before PRD", "Complete Pending ADR topics"),

    # -------------------------------------------------------------------------
    # PRD (Layer 2) - Product Requirements Document
    # -------------------------------------------------------------------------
    "PRD-E001": ("Invalid H1 format", "Use format: # PRD-NNN: Title"),
    "PRD-E002": ("Missing Document Control section", "Add Section 0"),
    "PRD-E003": ("Missing required tag 'prd'", "Add @prd tag"),
    "PRD-E004": ("Missing required tag 'layer-2-artifact'", "Add layer tag"),
    "PRD-E005": ("Missing cumulative tag @brd:", "Add BRD traceability"),
    "PRD-E006": ("Missing Product Overview section", "Add Section 1"),
    "PRD-E023": ("Missing required PRD diagram tag @diagram: c4-l2", "Add C4-L2 diagram tag in PRD"),
    "PRD-E024": ("Missing required PRD diagram tag @diagram: dfd-l1", "Add DFD-L1 diagram tag in PRD"),
    "PRD-E025": ("Missing required PRD diagram tag @diagram: sequence-*", "Add sequence diagram contract tag"),
    "PRD-E026": ("Sequence diagram lacks exception/alternate path", "Add alt/else branch to sequenceDiagram"),
    "PRD-W001": ("Feature ID not 3-digit format", "Use NNN format for feature IDs"),
    "PRD-W011": ("Diagram intent header missing required fields", "Add diagram_type, level, scope_boundary, upstream_refs, downstream_refs"),
    "PRD-W012": ("Missing PRD diagram tag @diagram: c4-l2 (legacy mode)", "Add C4-L2 diagram tag"),
    "PRD-W013": ("Missing PRD diagram tag @diagram: dfd-l1 (legacy mode)", "Add DFD-L1 diagram tag"),
    "PRD-W014": ("Missing PRD diagram tag @diagram: sequence-* (legacy mode)", "Add sequence diagram contract tag"),
    "PRD-W015": ("Sequence diagram missing exception/alternate path (legacy mode)", "Add alt/else branch to sequenceDiagram"),

    # -------------------------------------------------------------------------
    # EARS (Layer 3) - Event-Action-Response-State (Engineering Requirements)
    # -------------------------------------------------------------------------
    "EARS-E001": ("Invalid EARS pattern", "Use WHEN-THE-SHALL-WITHIN format"),
    "EARS-E002": ("Missing requirement ID", "Add EARS.NN.TT.SS format ID"),
    "EARS-E003": ("Missing required tag 'ears'", "Add @ears tag"),
    "EARS-E004": ("Missing required tag 'layer-3-artifact'", "Add layer tag"),
    "EARS-E005": ("Missing cumulative tags", "Add @brd and @prd tags"),
    "EARS-W001": ("Ambiguous requirement", "Clarify requirement language"),
    "EARS-W002": ("Missing priority field", "Add priority (MUST/SHOULD/MAY)"),

    # -------------------------------------------------------------------------
    # BDD (Layer 4) - Behavior-Driven Development
    # -------------------------------------------------------------------------
    "BDD-E001": ("Missing Feature keyword", "Start file with 'Feature:'"),
    "BDD-E002": ("Missing Scenario/Scenario Outline", "Add scenario definition"),
    "BDD-E003": ("Invalid Given/When/Then structure", "Fix step syntax"),
    "BDD-E004": ("Invalid file extension", "Use .feature extension"),
    "BDD-E005": ("Missing cumulative tags", "Add @brd, @prd, @ears tags"),
    "BDD-E006": ("Missing Background section", "Add Background for shared steps"),
    "BDD-W001": ("Step definition syntax issue", "Review step wording"),
    "BDD-W002": ("Missing Examples table", "Add Examples for Scenario Outline"),

    # -------------------------------------------------------------------------
    # ADR (Layer 5) - Architecture Decision Record
    # -------------------------------------------------------------------------
    "ADR-E001": ("Invalid H1 format", "Use format: # ADR-NNN: Title"),
    "ADR-E002": ("Missing Context section", "Add Section 4 with subsections"),
    "ADR-E003": ("Missing Decision section", "Add Section 5 with subsections"),
    "ADR-E004": ("Missing Consequences section", "Add Section 7"),
    "ADR-E005": ("Missing architecture diagram", "Add Mermaid diagram in Section 8"),
    "ADR-E006": ("Missing required tag 'adr'", "Add @adr tag"),
    "ADR-E007": ("Missing required tag 'layer-5-artifact'", "Add layer tag"),
    "ADR-W001": ("Invalid status value", "Use: Proposed/Accepted/Deprecated/Superseded"),
    "ADR-W002": ("Missing alternatives section", "Document considered alternatives"),

    # -------------------------------------------------------------------------
    # SYS (Layer 6) - System Requirements
    # -------------------------------------------------------------------------
    "SYS-E001": ("Invalid H1 format", "Use format: # SYS-NNN: Title"),
    "SYS-E002": ("Missing required tag 'sys'", "Add @sys tag"),
    "SYS-E003": ("Missing required tag 'layer-6-artifact'", "Add layer tag"),
    "SYS-E004": ("Missing cumulative tags", "Add @brd through @adr tags"),
    "SYS-E005": ("Missing Functional Requirements section", "Add FR section"),
    "SYS-E006": ("Missing interface definitions", "Add interface specifications"),
    "SYS-W001": ("Missing Quality Attributes section", "Add NFR section"),
    "SYS-W002": ("Missing constraints section", "Document system constraints"),

    # -------------------------------------------------------------------------
    # REQ (Layer 7) - Atomic Requirements
    # -------------------------------------------------------------------------
    "REQ-E001": ("Invalid requirement ID format", "Use REQ.NN.TT.SS format"),
    "REQ-E002": ("Missing required tag 'req'", "Add @req tag"),
    "REQ-E003": ("Missing required tag 'layer-7-artifact'", "Add layer tag"),
    "REQ-E004": ("Missing acceptance criteria", "Add testable criteria"),
    "REQ-E005": ("Missing traceability section", "Add upstream/downstream refs"),
    "REQ-E006": ("Invalid priority value", "Use MUST/SHOULD/MAY"),
    "REQ-W001": ("Missing rationale", "Document requirement rationale"),
    "REQ-W002": ("Weak acceptance criteria", "Add measurable criteria"),

    # -------------------------------------------------------------------------
# -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # CTR (Layer 9) - Contracts
    # -------------------------------------------------------------------------
    "CTR-E001": ("Invalid contract ID format", "Use CTR.NN.TT.SS format"),
    "CTR-E002": ("Missing YAML companion file", "Create .yaml schema file"),
    "CTR-E003": ("Missing required tag 'ctr'", "Add @ctr tag"),
    "CTR-E004": ("Missing required tag 'layer-9-artifact'", "Add layer tag"),
    "CTR-E005": ("Schema validation failed", "Fix YAML schema errors"),
    "CTR-W001": ("Missing version field", "Add contract version"),

    # -------------------------------------------------------------------------
    # SPEC (Layer 10) - Technical Specifications
    # -------------------------------------------------------------------------
    "SPEC-E001": ("Invalid file extension", "Use .yaml extension"),
    "SPEC-E002": ("Invalid YAML syntax", "Fix YAML formatting"),
    "SPEC-E003": ("Missing spec_version field", "Add spec_version field"),
    "SPEC-E004": ("ID mismatch with filename", "Match id field to filename"),
    "SPEC-E005": ("Missing cumulative tags", "Add @brd through @req tags"),
    "SPEC-E006": ("Missing required sections", "Add all required SPEC sections"),
    "SPEC-W001": ("Missing interfaces section", "Add interface definitions"),
    "SPEC-W002": ("Missing error handling", "Document error scenarios"),

    # -------------------------------------------------------------------------
    # TASKS (Layer 11) - Task Breakdown
    # -------------------------------------------------------------------------
    "TASKS-E001": ("Invalid H1 format", "Use format: # TASKS-NNN: Title"),
    "TASKS-E002": ("Missing required tag 'tasks'", "Add @tasks tag"),
    "TASKS-E003": ("Missing required tag 'layer-11-artifact'", "Add layer tag"),
    "TASKS-E004": ("Missing SPEC reference", "Add @spec traceability"),
    "TASKS-E005": ("Invalid task ID format", "Use TASKS.NN.TT.SS format"),
    "TASKS-W001": ("Missing dependency links", "Add task dependencies"),
    "TASKS-W002": ("Missing acceptance criteria", "Add task completion criteria"),

    # -------------------------------------------------------------------------
    # TSPEC (Layer 10) - Test Specifications
    # -------------------------------------------------------------------------
    "TSPEC-E001": ("Invalid test type", "Use UTEST/ITEST/STEST/FTEST/PTEST/SECTEST"),
    "TSPEC-E002": ("Missing Document Control section", "Add Section 1"),
    "TSPEC-E003": ("Missing Test Scope section", "Add Section 2"),
    "TSPEC-E004": ("Missing Test Case Index", "Add Section 3"),
    "TSPEC-E005": ("Missing Test Case Details", "Add Section 4"),
    "TSPEC-E006": ("Missing Coverage Matrix", "Add Section 5"),
    "TSPEC-E007": ("Missing Traceability section", "Add Section 6"),
    "TSPEC-E008": ("Invalid element ID format", "Use TSPEC.NN.TT.SS format"),
    "TSPEC-E009": ("TASKS-Ready score below threshold", "Increase test coverage"),
    "TSPEC-E010": ("Missing required cumulative tag", "Add all 9 cumulative tags"),
    "TSPEC-E030": ("TSPEC not in nested folder", "Move to TYPE-NN_{slug}/ folder"),
    "TSPEC-E031": ("Folder name doesn't match ID", "Rename folder to match TSPEC ID"),
    "TSPEC-E032": ("File name doesn't match folder", "Rename file to match folder"),
    "TSPEC-E033": ("TSPEC not in correct type subdirectory", "Move to correct TYPE/ folder"),

    # UTEST-specific
    "UTEST-E001": ("REQ coverage below 90%", "Add tests for uncovered REQs"),
    "UTEST-E002": ("Missing I/O table", "Add Input/Output table to test case"),
    "UTEST-E003": ("Missing pseudocode", "Add GIVEN/WHEN/THEN pseudocode"),
    "UTEST-E004": ("Missing error cases", "Add error condition table"),
    "UTEST-E005": ("Invalid test category", "Use [Logic], [State], [Validation], [Edge]"),
    "UTEST-W001": ("Low pseudocode coverage", "Add pseudocode to complex tests"),
    "UTEST-W002": ("Missing @req reference", "Add @req tag to test case"),

    # ITEST-specific
    "ITEST-E001": ("CTR coverage below 90%", "Add tests for uncovered contracts"),
    "ITEST-E002": ("Missing sequence diagram", "Add sequence diagram for complex flows"),
    "ITEST-E003": ("Missing @ctr reference", "Add @ctr tag to integration test"),
    "ITEST-W001": ("Weak integration coverage", "Add more component interaction tests"),

    # STEST-specific
    "STEST-E001": ("Critical path not covered", "Add smoke test for critical path"),
    "STEST-E002": ("Timeout exceeds 5 minutes", "Optimize smoke test execution time"),
    "STEST-E003": ("Missing rollback test", "Add deployment rollback test"),
    "STEST-E004": ("STEST score not 100%", "STEST must achieve 100% coverage"),

    # FTEST-specific
    "FTEST-E001": ("SYS coverage below 90%", "Add tests for uncovered system requirements"),
    "FTEST-E002": ("Missing threshold reference", "Add @threshold tag for quantitative test"),
    "FTEST-W001": ("Incomplete functional coverage", "Add end-to-end scenario tests"),

    # PTEST-specific
    "PTEST-E001": ("Missing load scenario", "Add load test scenario"),
    "PTEST-E002": ("Missing performance threshold", "Add @threshold tag with target metrics"),
    "PTEST-E003": ("Invalid performance metric", "Use standard metrics (latency, throughput, etc.)"),
    "PTEST-W001": ("Below 85% TASKS-Ready", "Complete performance test specification"),

    # SECTEST-specific
    "SECTEST-E001": ("Missing threat scenario", "Add security threat scenario"),
    "SECTEST-E002": ("Missing control validation", "Add security control test"),
    "SECTEST-E003": ("Below 90% TASKS-Ready", "Complete security test specification"),
    "SECTEST-W001": ("Incomplete OWASP coverage", "Add tests for OWASP Top 10"),

    # -------------------------------------------------------------------------
    # Section File Validation (SEC) - Section count and structure validation
    # -------------------------------------------------------------------------
    "SEC-E001": ("Section count mismatch", "Update total_sections to match actual section files"),
    "SEC-E002": ("Missing section file", "Create missing section file or update total_sections"),
    "SEC-E003": ("Missing Section 0 file", "Create Section 0 with document control and index"),
    "SEC-W001": ("Section file gap detected", "Sections should be consecutive (1, 2, 3...)"),

    # -------------------------------------------------------------------------
    # Cross-Reference Accuracy (XREF) - Section reference validation
    # -------------------------------------------------------------------------
    "XREF-E001": ("Section number mismatch", "Referenced section number differs from target"),
    "XREF-E002": ("Section title mismatch", "Referenced section title differs from target"),
    "XREF-E003": ("Anchor not found in target", "Target document missing referenced anchor"),
    "XREF-W001": ("Fuzzy title match", "Section title has minor differences from reference"),

    # -------------------------------------------------------------------------
    # ID Pattern Consistency (IDPAT) - ID format validation
    # -------------------------------------------------------------------------
    "IDPAT-E001": ("Inconsistent document ID format", "Use consistent format: TYPE-NN+ (2+ digits)"),
    "IDPAT-E002": ("Inconsistent element ID format", "Use TYPE.NN.TT.SS format for all element IDs"),
    "IDPAT-E003": ("Mixed ID notation", "Do not mix hyphen (TYPE-NN) and dot (TYPE.NN) formats"),
    "IDPAT-W001": ("Legacy ID format detected", "Consider updating to unified 4-segment format"),

    # -------------------------------------------------------------------------
    # Diagram Consistency (DIAG) - Mermaid diagram validation
    # -------------------------------------------------------------------------
    "DIAG-E001": ("Diagram-text component mismatch", "Diagram components not mentioned in prose"),
    "DIAG-E002": ("Missing diagram for architecture section", "Add Mermaid diagram per DIAGRAM_STANDARDS.md"),
    "DIAG-W001": ("Diagram count differs from text claim", "Text states N components, diagram shows M"),
    "DIAG-W002": ("Node label not referenced in text", "Diagram node not mentioned in surrounding prose"),

    # -------------------------------------------------------------------------
    # Terminology Consistency (TERM) - Glossary and acronym validation
    # -------------------------------------------------------------------------
    "TERM-E001": ("Conflicting term definition", "Same term defined differently in glossary vs text"),
    "TERM-E002": ("Undefined acronym", "Acronym used without definition in document"),
    "TERM-W001": ("Inconsistent term usage", "Term used with variant spellings/capitalizations"),
    "TERM-W002": ("Missing glossary entry", "Technical term used but not in glossary"),
    "TERM-W003": ("Legacy term usage: 'Easy Approach to Requirements Syntax'",
                  "Use 'Event-Action-Response-State (Engineering Requirements)' except in citations"),

    # -------------------------------------------------------------------------
    # Timezone Validation (TZ) - Timezone format validation
    # -------------------------------------------------------------------------
    "TZ-E001": ("Non-standard timezone format", "Use ET (America/New_York) format, not EST/EDT"),
    "TZ-W001": ("Ambiguous timezone abbreviation", "Specify IANA timezone: America/New_York"),

    # -------------------------------------------------------------------------
    # Date Validation (DATE) - Date consistency validation
    # -------------------------------------------------------------------------
    "DATE-E001": ("Future document date", "Document date cannot be future date"),
    "DATE-E002": ("Timeline inconsistency", "Timeline dates conflict with document creation date"),
    "DATE-W001": ("Missing date metadata", "Add created/updated dates to frontmatter"),

    # -------------------------------------------------------------------------
    # Element Code Validation (ELEM) - Element type code validation
    # -------------------------------------------------------------------------
    "ELEM-E001": ("Undefined element type code", "Element code NN not in element type table"),
    "ELEM-W001": ("Undocumented custom code", "Custom element code requires documentation"),

    # -------------------------------------------------------------------------
    # Count Validation (COUNT) - Stated vs itemized count validation
    # -------------------------------------------------------------------------
    "COUNT-E001": ("Count mismatch", "Stated count N differs from itemized count M"),
    "COUNT-W001": ("Missing count verification", "Large list without stated total for verification"),

    # -------------------------------------------------------------------------
    # Forward Reference Validation (FWDREF) - SDD layer-aware reference validation
    # -------------------------------------------------------------------------
    "FWDREF-E001": ("Specific downstream ID in upstream doc", "PRD cannot reference specific ADR/SYS/REQ numbers"),
    "FWDREF-E002": ("Non-existent downstream reference", "Referenced downstream document does not exist"),
    "FWDREF-W001": ("Downstream count claim", "Avoid stating exact counts of future documents"),
}


def get_error(code: str) -> Optional[ErrorCode]:
    """
    Retrieve error code definition.

    Args:
        code: Error code string (e.g., 'VAL-E001')

    Returns:
        ErrorCode object or None if not found
    """
    if code not in ERROR_REGISTRY:
        return None

    message, remediation = ERROR_REGISTRY[code]

    # Parse severity from code
    severity_char = code.split("-")[1][0]
    severity = {
        "E": Severity.ERROR,
        "W": Severity.WARNING,
        "I": Severity.INFO
    }.get(severity_char, Severity.ERROR)

    return ErrorCode(
        code=code,
        message=message,
        remediation=remediation,
        severity=severity
    )


def format_error(code: str, context: str = "") -> str:
    """
    Format error for output.

    Args:
        code: Error code string
        context: Optional context (e.g., filename, line number)

    Returns:
        Formatted error string
    """
    error = get_error(code)
    if not error:
        return f"[UNKNOWN] {code}: Unknown error code"

    severity_label = {
        Severity.ERROR: "ERROR",
        Severity.WARNING: "WARNING",
        Severity.INFO: "INFO"
    }[error.severity]

    if context:
        return f"[{severity_label}] {code}: {error.message} ({context}) - {error.remediation}"
    return f"[{severity_label}] {code}: {error.message} - {error.remediation}"


def list_codes_by_type(artifact_type: str) -> Dict[str, Tuple[str, str]]:
    """
    List all error codes for a specific artifact type.

    Args:
        artifact_type: Artifact type prefix (e.g., 'BRD', 'PRD')

    Returns:
        Dictionary of matching error codes
    """
    return {
        code: details
        for code, details in ERROR_REGISTRY.items()
        if code.startswith(f"{artifact_type}-")
    }


def calculate_exit_code(errors: list, warnings: list, strict: bool = False) -> int:
    """
    Calculate exit code based on validation results.

    Args:
        errors: List of error codes found
        warnings: List of warning codes found
        strict: If True, treat warnings as errors

    Returns:
        Exit code (0=pass, 1=warnings, 2=errors)
    """
    if errors:
        return 2
    if warnings and strict:
        return 2
    if warnings:
        return 1
    return 0


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="SDD Document Validation Error Code Registry"
    )
    parser.add_argument(
        "--list",
        metavar="TYPE",
        help="List all codes for artifact type (e.g., BRD, PRD, VAL)"
    )
    parser.add_argument(
        "--lookup",
        metavar="CODE",
        help="Look up specific error code (e.g., VAL-E001)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="List all error codes"
    )

    args = parser.parse_args()

    if args.lookup:
        error = get_error(args.lookup)
        if error:
            print(f"Code: {error.code}")
            print(f"Severity: {error.severity.name}")
            print(f"Message: {error.message}")
            print(f"Remediation: {error.remediation}")
            print(f"Exit Code: {error.exit_code}")
        else:
            print(f"Unknown error code: {args.lookup}")
            sys.exit(1)

    elif args.list:
        codes = list_codes_by_type(args.list.upper())
        if codes:
            print(f"\n{args.list.upper()} Error Codes:")
            print("-" * 60)
            for code, (message, remediation) in sorted(codes.items()):
                print(f"{code}: {message}")
                print(f"  Fix: {remediation}")
        else:
            print(f"No codes found for type: {args.list}")
            sys.exit(1)

    elif args.all:
        print("\nSDD Validation Error Codes")
        print("=" * 60)
        current_type = ""
        for code in sorted(ERROR_REGISTRY.keys()):
            code_type = code.split("-")[0]
            if code_type != current_type:
                current_type = code_type
                print(f"\n{current_type}:")
                print("-" * 40)
            message, _ = ERROR_REGISTRY[code]
            print(f"  {code}: {message}")

    else:
        # Print summary
        types = set(code.split("-")[0] for code in ERROR_REGISTRY.keys())
        print(f"Error Code Registry: {len(ERROR_REGISTRY)} codes across {len(types)} types")
        print(f"Types: {', '.join(sorted(types))}")
        print("\nUse --help for options")
