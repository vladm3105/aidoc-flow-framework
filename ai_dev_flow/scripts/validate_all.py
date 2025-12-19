#!/usr/bin/env python3
"""
Unified Document Validation Orchestrator for SDD Framework

Coordinates all artifact validators, aggregates results, and generates reports.

Usage:
    python validate_all.py <docs_dir> [options]
    python validate_all.py /path/to/docs --all
    python validate_all.py /path/to/docs --layer BRD
    python validate_all.py /path/to/docs --all --strict --report markdown

Exit Codes:
    0 = Pass (no errors, no warnings)
    1 = Warnings only
    2 = Errors present
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from error_codes import (
    ERROR_REGISTRY,
    Severity,
    calculate_exit_code,
    format_error,
    get_error,
)


# =============================================================================
# VALIDATOR REGISTRY
# =============================================================================

@dataclass
class ValidatorConfig:
    """Configuration for a document validator."""
    script: str
    script_type: str  # "python" or "shell"
    implemented: bool
    layer: int
    description: str


VALIDATOR_REGISTRY: Dict[str, ValidatorConfig] = {
    "BRD": ValidatorConfig(
        script="validate_brd_template.sh",
        script_type="shell",
        implemented=True,
        layer=1,
        description="Business Requirements Document validator"
    ),
    "PRD": ValidatorConfig(
        script="validate_prd.py",
        script_type="python",
        implemented=True,
        layer=2,
        description="Product Requirements Document validator"
    ),
    "EARS": ValidatorConfig(
        script="validate_ears.py",
        script_type="python",
        implemented=True,
        layer=3,
        description="EARS requirements syntax validator"
    ),
    "BDD": ValidatorConfig(
        script="validate_bdd.py",
        script_type="python",
        implemented=True,
        layer=4,
        description="BDD feature file validator"
    ),
    "ADR": ValidatorConfig(
        script="validate_adr.py",
        script_type="python",
        implemented=True,
        layer=5,
        description="Architecture Decision Record validator"
    ),
    "SYS": ValidatorConfig(
        script="validate_sys.py",
        script_type="python",
        implemented=True,
        layer=6,
        description="System Requirements validator"
    ),
    "REQ": ValidatorConfig(
        script="validate_req_template.sh",
        script_type="shell",
        implemented=True,
        layer=7,
        description="Atomic Requirements validator"
    ),
    "IMPL": ValidatorConfig(
        script="validate_impl.sh",
        script_type="shell",
        implemented=True,
        layer=8,
        description="Implementation Approach validator"
    ),
    "CTR": ValidatorConfig(
        script="validate_ctr.sh",
        script_type="shell",
        implemented=True,
        layer=9,
        description="Contract validator"
    ),
    "SPEC": ValidatorConfig(
        script="validate_spec.py",
        script_type="python",
        implemented=True,
        layer=10,
        description="Technical Specification validator"
    ),
    "TASKS": ValidatorConfig(
        script="validate_tasks.sh",
        script_type="shell",
        implemented=True,
        layer=11,
        description="Task breakdown validator"
    ),
    "IPLAN": ValidatorConfig(
        script="validate_iplan.sh",
        script_type="shell",
        implemented=True,
        layer=12,
        description="Implementation Plan validator"
    ),
}

# Cross-document validators (not layer-specific)
CROSS_VALIDATORS = {
    "XDOC": ValidatorConfig(
        script="validate_cross_document.py",
        script_type="python",
        implemented=True,
        layer=0,
        description="Cross-document traceability validator"
    ),
    "LINKS": ValidatorConfig(
        script="validate_links.py",
        script_type="python",
        implemented=True,
        layer=0,
        description="Link integrity validator"
    ),
    "TAGS": ValidatorConfig(
        script="validate_tags_against_docs.py",
        script_type="python",
        implemented=True,
        layer=0,
        description="Tag compliance validator"
    ),
}


# =============================================================================
# VALIDATION RESULT TYPES
# =============================================================================

@dataclass
class ValidationIssue:
    """Single validation issue."""
    code: str
    message: str
    file: str
    line: Optional[int] = None
    severity: Severity = Severity.ERROR

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "severity": self.severity.name
        }


@dataclass
class ValidatorResult:
    """Result from running a single validator."""
    validator: str
    success: bool
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    info: List[ValidationIssue] = field(default_factory=list)
    execution_time: float = 0.0
    skipped: bool = False
    skip_reason: str = ""

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def to_dict(self) -> dict:
        return {
            "validator": self.validator,
            "success": self.success,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "execution_time": self.execution_time,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason
        }


@dataclass
class ValidationReport:
    """Aggregated validation report."""
    docs_dir: str
    timestamp: str
    results: List[ValidatorResult] = field(default_factory=list)
    total_errors: int = 0
    total_warnings: int = 0
    validators_run: int = 0
    validators_skipped: int = 0

    def to_dict(self) -> dict:
        return {
            "docs_dir": self.docs_dir,
            "timestamp": self.timestamp,
            "summary": {
                "total_errors": self.total_errors,
                "total_warnings": self.total_warnings,
                "validators_run": self.validators_run,
                "validators_skipped": self.validators_skipped,
                "status": "PASS" if self.total_errors == 0 else "FAIL"
            },
            "results": [r.to_dict() for r in self.results]
        }


# =============================================================================
# VALIDATOR EXECUTION
# =============================================================================

def find_docs_for_layer(docs_dir: Path, layer_type: str) -> List[Path]:
    """
    Find all documents for a specific layer type.

    Args:
        docs_dir: Base documentation directory
        layer_type: Layer type (BRD, PRD, etc.)

    Returns:
        List of matching document paths
    """
    docs = []

    # Check standard locations
    layer_dirs = [
        docs_dir / layer_type,
        docs_dir / "docs" / layer_type,
        docs_dir / layer_type.lower(),
    ]

    for layer_dir in layer_dirs:
        if layer_dir.exists():
            # Match files based on type
            if layer_type == "BDD":
                docs.extend(layer_dir.glob("**/*.feature"))
            elif layer_type == "SPEC":
                docs.extend(layer_dir.glob("**/*.yaml"))
                docs.extend(layer_dir.glob("**/*.yml"))
            else:
                docs.extend(layer_dir.glob(f"**/{layer_type}-*.md"))
                docs.extend(layer_dir.glob(f"**/{layer_type.lower()}-*.md"))

    return docs


def run_validator(
    config: ValidatorConfig,
    docs_dir: Path,
    target_files: Optional[List[Path]] = None,
    verbose: bool = False
) -> ValidatorResult:
    """
    Execute a validator script.

    Args:
        config: Validator configuration
        docs_dir: Documentation directory
        target_files: Specific files to validate (optional)
        verbose: Enable verbose output

    Returns:
        ValidatorResult with issues found
    """
    import time
    start_time = time.time()

    script_path = SCRIPT_DIR / config.script

    # Check if validator is implemented
    if not config.implemented:
        return ValidatorResult(
            validator=config.script,
            success=True,
            skipped=True,
            skip_reason="Validator not yet implemented"
        )

    # Check if script exists
    if not script_path.exists():
        return ValidatorResult(
            validator=config.script,
            success=False,
            skipped=True,
            skip_reason=f"Script not found: {script_path}"
        )

    # Build command
    if config.script_type == "python":
        cmd = [sys.executable, str(script_path), str(docs_dir)]
    else:
        cmd = ["bash", str(script_path), str(docs_dir)]

    if target_files:
        cmd.extend([str(f) for f in target_files])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        execution_time = time.time() - start_time

        # Parse output for issues
        errors = []
        warnings = []
        info = []

        for line in result.stdout.splitlines() + result.stderr.splitlines():
            line = line.strip()
            if not line:
                continue

            # Parse error code format: [SEVERITY] CODE: message
            if line.startswith("[ERROR]") or "-E" in line:
                errors.append(ValidationIssue(
                    code=extract_code(line),
                    message=line,
                    file=str(docs_dir),
                    severity=Severity.ERROR
                ))
            elif line.startswith("[WARNING]") or "-W" in line:
                warnings.append(ValidationIssue(
                    code=extract_code(line),
                    message=line,
                    file=str(docs_dir),
                    severity=Severity.WARNING
                ))
            elif line.startswith("[INFO]") or "-I" in line:
                info.append(ValidationIssue(
                    code=extract_code(line),
                    message=line,
                    file=str(docs_dir),
                    severity=Severity.INFO
                ))

        return ValidatorResult(
            validator=config.script,
            success=result.returncode == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            execution_time=execution_time
        )

    except subprocess.TimeoutExpired:
        return ValidatorResult(
            validator=config.script,
            success=False,
            errors=[ValidationIssue(
                code="VAL-E004",
                message="Validator timed out after 5 minutes",
                file=str(docs_dir),
                severity=Severity.ERROR
            )],
            execution_time=300.0
        )
    except Exception as e:
        return ValidatorResult(
            validator=config.script,
            success=False,
            errors=[ValidationIssue(
                code="VAL-E001",
                message=f"Validator execution failed: {str(e)}",
                file=str(docs_dir),
                severity=Severity.ERROR
            )]
        )


def extract_code(line: str) -> str:
    """Extract error code from output line."""
    import re
    # Match patterns like VAL-E001, BRD-W002, etc.
    match = re.search(r'([A-Z]+-[EWI]\d{3})', line)
    return match.group(1) if match else "VAL-E001"


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_text_report(report: ValidationReport) -> str:
    """Generate plain text report."""
    lines = [
        "=" * 60,
        "SDD DOCUMENT VALIDATION REPORT",
        "=" * 60,
        f"Directory: {report.docs_dir}",
        f"Timestamp: {report.timestamp}",
        "",
        "SUMMARY",
        "-" * 40,
        f"Status: {'PASS' if report.total_errors == 0 else 'FAIL'}",
        f"Errors: {report.total_errors}",
        f"Warnings: {report.total_warnings}",
        f"Validators Run: {report.validators_run}",
        f"Validators Skipped: {report.validators_skipped}",
        ""
    ]

    if report.total_errors > 0 or report.total_warnings > 0:
        lines.append("ISSUES")
        lines.append("-" * 40)

        for result in report.results:
            if result.errors or result.warnings:
                lines.append(f"\n{result.validator}:")
                for error in result.errors:
                    lines.append(f"  [ERROR] {error.code}: {error.message}")
                for warning in result.warnings:
                    lines.append(f"  [WARN]  {warning.code}: {warning.message}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def generate_markdown_report(report: ValidationReport) -> str:
    """Generate Markdown report."""
    status_emoji = "✅" if report.total_errors == 0 else "❌"

    lines = [
        "# SDD Document Validation Report",
        "",
        f"**Directory**: `{report.docs_dir}`",
        f"**Timestamp**: {report.timestamp}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Status | {status_emoji} {'PASS' if report.total_errors == 0 else 'FAIL'} |",
        f"| Errors | {report.total_errors} |",
        f"| Warnings | {report.total_warnings} |",
        f"| Validators Run | {report.validators_run} |",
        f"| Validators Skipped | {report.validators_skipped} |",
        ""
    ]

    if report.total_errors > 0 or report.total_warnings > 0:
        lines.append("## Issues Found")
        lines.append("")

        for result in report.results:
            if result.errors or result.warnings:
                lines.append(f"### {result.validator}")
                lines.append("")
                if result.errors:
                    lines.append("**Errors:**")
                    for error in result.errors:
                        lines.append(f"- `{error.code}`: {error.message}")
                if result.warnings:
                    lines.append("")
                    lines.append("**Warnings:**")
                    for warning in result.warnings:
                        lines.append(f"- `{warning.code}`: {warning.message}")
                lines.append("")

    # Add validator status table
    lines.append("## Validator Status")
    lines.append("")
    lines.append("| Validator | Status | Errors | Warnings | Time |")
    lines.append("|-----------|--------|--------|----------|------|")

    for result in report.results:
        if result.skipped:
            status = "⏭️ Skipped"
        elif result.success and result.error_count == 0:
            status = "✅ Pass"
        else:
            status = "❌ Fail"

        lines.append(
            f"| {result.validator} | {status} | "
            f"{result.error_count} | {result.warning_count} | "
            f"{result.execution_time:.2f}s |"
        )

    return "\n".join(lines)


def generate_json_report(report: ValidationReport) -> str:
    """Generate JSON report."""
    return json.dumps(report.to_dict(), indent=2)


# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

def validate_all(
    docs_dir: Path,
    layers: Optional[List[str]] = None,
    include_cross: bool = True,
    strict: bool = False,
    verbose: bool = False
) -> ValidationReport:
    """
    Run all validators on documentation directory.

    Args:
        docs_dir: Path to documentation directory
        layers: Specific layers to validate (None = all)
        include_cross: Include cross-document validators
        strict: Treat warnings as errors
        verbose: Enable verbose output

    Returns:
        Aggregated validation report
    """
    report = ValidationReport(
        docs_dir=str(docs_dir),
        timestamp=datetime.now().isoformat()
    )

    # Determine which validators to run
    validators_to_run = {}

    if layers:
        for layer in layers:
            layer_upper = layer.upper()
            if layer_upper in VALIDATOR_REGISTRY:
                validators_to_run[layer_upper] = VALIDATOR_REGISTRY[layer_upper]
            else:
                print(f"Warning: Unknown layer type: {layer}")
    else:
        validators_to_run = VALIDATOR_REGISTRY.copy()

    if include_cross:
        validators_to_run.update(CROSS_VALIDATORS)

    # Run each validator
    for name, config in sorted(validators_to_run.items(), key=lambda x: x[1].layer):
        if verbose:
            print(f"Running {name} validator...")

        result = run_validator(config, docs_dir, verbose=verbose)
        report.results.append(result)

        if result.skipped:
            report.validators_skipped += 1
        else:
            report.validators_run += 1

        report.total_errors += result.error_count
        report.total_warnings += result.warning_count

    return report


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SDD Document Validation Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_all.py /path/to/docs --all
  python validate_all.py /path/to/docs --layer BRD --layer PRD
  python validate_all.py /path/to/docs --all --strict --report markdown
  python validate_all.py /path/to/docs --all --report json > report.json
        """
    )

    parser.add_argument(
        "docs_dir",
        type=Path,
        help="Documentation directory to validate"
    )
    parser.add_argument(
        "--layer",
        action="append",
        dest="layers",
        metavar="TYPE",
        help="Validate specific layer(s) (e.g., BRD, PRD). Can be repeated."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="validate_all",
        help="Validate all layers"
    )
    parser.add_argument(
        "--no-cross",
        action="store_true",
        help="Skip cross-document validators"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--report",
        choices=["text", "markdown", "json"],
        default="text",
        help="Report format (default: text)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="Write report to file instead of stdout"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--list-validators",
        action="store_true",
        help="List available validators and exit"
    )

    args = parser.parse_args()

    # List validators mode
    if args.list_validators:
        print("\nAvailable Validators:")
        print("-" * 60)
        print(f"{'Type':<8} {'Layer':<6} {'Status':<12} {'Description'}")
        print("-" * 60)
        for name, config in sorted(VALIDATOR_REGISTRY.items(), key=lambda x: x[1].layer):
            status = "Implemented" if config.implemented else "Planned"
            print(f"{name:<8} {config.layer:<6} {status:<12} {config.description}")
        print("\nCross-Document Validators:")
        for name, config in CROSS_VALIDATORS.items():
            status = "Implemented" if config.implemented else "Planned"
            print(f"{name:<8} {'N/A':<6} {status:<12} {config.description}")
        return 0

    # Validate inputs
    if not args.docs_dir.exists():
        print(f"Error: Directory not found: {args.docs_dir}")
        return 2

    if not args.validate_all and not args.layers:
        print("Error: Specify --all or --layer TYPE")
        parser.print_help()
        return 2

    # Run validation
    layers = args.layers if args.layers else None
    report = validate_all(
        docs_dir=args.docs_dir,
        layers=layers,
        include_cross=not args.no_cross,
        strict=args.strict,
        verbose=args.verbose
    )

    # Generate report
    if args.report == "markdown":
        output = generate_markdown_report(report)
    elif args.report == "json":
        output = generate_json_report(report)
    else:
        output = generate_text_report(report)

    # Output report
    if args.output:
        args.output.write_text(output)
        if args.verbose:
            print(f"Report written to: {args.output}")
    else:
        print(output)

    # Return exit code
    return calculate_exit_code(
        errors=[r for r in report.results if r.errors],
        warnings=[r for r in report.results if r.warnings],
        strict=args.strict
    )


if __name__ == "__main__":
    sys.exit(main())
