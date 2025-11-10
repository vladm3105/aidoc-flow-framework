#!/usr/bin/env python3
"""
Validate Traceability Matrix Against Actual Documents

This script validates a traceability matrix by comparing its contents against
actual document files in the repository. It checks for consistency, completeness,
and identifies discrepancies.

Usage:
    python validate_traceability_matrix.py --matrix TRACEABILITY_MATRIX_ADR.md --input ../adrs/

Features:
- Validates document counts match actual files
- Checks all cross-references resolve to real documents
- Verifies coverage percentages are accurate
- Identifies orphaned documents (not in matrix)
- Detects broken links and missing references
- Generates validation report with issues and recommendations

Author: AI-Driven SDD Framework
Version: 1.0.0
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


class ValidationIssue:
    """Represents a validation issue found in the matrix"""

    SEVERITY_CRITICAL = "CRITICAL"
    SEVERITY_ERROR = "ERROR"
    SEVERITY_WARNING = "WARNING"
    SEVERITY_INFO = "INFO"

    def __init__(self, severity: str, category: str, message: str, location: str = ""):
        self.severity = severity
        self.category = category
        self.message = message
        self.location = location

    def __repr__(self):
        return f"[{self.severity}] {self.category}: {self.message} ({self.location})"


class TraceabilityMatrixValidator:
    """Validates traceability matrices against actual documents"""

    SUPPORTED_TYPES = [
        'BRD', 'PRD', 'EARS', 'BDD', 'ADR', 'SYS',
        'REQ', 'IMPL', 'CTR', 'SPEC', 'TASKS'
    ]

    def __init__(self, matrix_path: str, input_dir: str, strict: bool = False):
        """
        Initialize the validator

        Args:
            matrix_path: Path to traceability matrix file to validate
            input_dir: Directory containing actual documents
            strict: Enable strict validation (treat warnings as errors)
        """
        self.matrix_path = Path(matrix_path).resolve()
        self.input_dir = Path(input_dir).resolve()
        self.strict = strict
        self.issues: List[ValidationIssue] = []
        self.doc_type = self._detect_doc_type()

        # Extracted data
        self.matrix_doc_ids: Set[str] = set()
        self.matrix_metadata: Dict[str, Dict] = {}
        self.actual_doc_ids: Set[str] = set()
        self.actual_files: Dict[str, Path] = {}

        if not self.matrix_path.exists():
            raise FileNotFoundError(f"Matrix file not found: {self.matrix_path}")

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

    def _detect_doc_type(self) -> str:
        """
        Detect document type from matrix filename

        Returns:
            Document type (BRD, PRD, ADR, etc.)
        """
        filename = self.matrix_path.name

        for doc_type in self.SUPPORTED_TYPES:
            if doc_type in filename.upper():
                return doc_type

        raise ValueError(f"Cannot detect document type from matrix filename: {filename}")

    def scan_actual_documents(self):
        """Scan input directory for actual document files"""
        print(f"Scanning actual documents in: {self.input_dir}")

        # Pattern: TYPE-NNN_slug.ext or TYPE-NNN-YY_slug.ext
        pattern = re.compile(rf'{self.doc_type}-(\d{{3,4}}(?:-\d{{2,3}})?)[_-].*\.(md|feature|yaml)$')

        # Recursively search for matching files
        for filepath in self.input_dir.rglob('*'):
            if not filepath.is_file():
                continue

            match = pattern.match(filepath.name)
            if match:
                doc_id = f"{self.doc_type}-{match.group(1)}"
                self.actual_doc_ids.add(doc_id)
                self.actual_files[doc_id] = filepath

        print(f"Found {len(self.actual_doc_ids)} actual {self.doc_type} documents")

    def parse_matrix_inventory(self):
        """Parse document inventory from traceability matrix"""
        print(f"Parsing matrix inventory from: {self.matrix_path}")

        try:
            with open(self.matrix_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find inventory table (Section 2)
            inventory_section = re.search(
                r'##\s+2\.\s+Complete.*?Inventory(.*?)(?:##|\Z)',
                content, re.DOTALL | re.IGNORECASE
            )

            if not inventory_section:
                self.issues.append(ValidationIssue(
                    ValidationIssue.SEVERITY_CRITICAL,
                    "Missing Section",
                    "Cannot find 'Complete Inventory' section (Section 2)",
                    "Matrix structure"
                ))
                return

            inventory_text = inventory_section.group(1)

            # Extract table rows (skip header and separator)
            table_rows = re.findall(
                rf'\|\s*({self.doc_type}-\d{{3,4}}(?:-\d{{2,3}})?)\s*\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|',
                inventory_text
            )

            for row in table_rows:
                doc_id = row[0].strip()
                self.matrix_doc_ids.add(doc_id)

                self.matrix_metadata[doc_id] = {
                    'title': row[1].strip(),
                    'category': row[2].strip(),
                    'status': row[3].strip(),
                    'date': row[4].strip(),
                    'upstream': row[5].strip(),
                    'downstream': row[6].strip()
                }

            print(f"Found {len(self.matrix_doc_ids)} documents in matrix inventory")

        except Exception as e:
            self.issues.append(ValidationIssue(
                ValidationIssue.SEVERITY_CRITICAL,
                "Parse Error",
                f"Error parsing matrix file: {e}",
                str(self.matrix_path)
            ))

    def validate_document_counts(self):
        """Validate that document counts match between matrix and actual files"""
        print("Validating document counts...")

        matrix_count = len(self.matrix_doc_ids)
        actual_count = len(self.actual_doc_ids)

        if matrix_count != actual_count:
            self.issues.append(ValidationIssue(
                ValidationIssue.SEVERITY_ERROR,
                "Count Mismatch",
                f"Matrix lists {matrix_count} documents but found {actual_count} actual files",
                "Document inventory"
            ))

    def validate_document_existence(self):
        """Validate that all documents in matrix exist as actual files"""
        print("Validating document existence...")

        # Documents in matrix but not in filesystem
        missing_docs = self.matrix_doc_ids - self.actual_doc_ids

        for doc_id in missing_docs:
            self.issues.append(ValidationIssue(
                ValidationIssue.SEVERITY_ERROR,
                "Missing Document",
                f"Document {doc_id} listed in matrix but file not found",
                "Document inventory"
            ))

        # Documents in filesystem but not in matrix
        orphaned_docs = self.actual_doc_ids - self.matrix_doc_ids

        for doc_id in orphaned_docs:
            filepath = self.actual_files[doc_id]
            self.issues.append(ValidationIssue(
                ValidationIssue.SEVERITY_WARNING,
                "Orphaned Document",
                f"Document {doc_id} exists but not listed in matrix",
                str(filepath.relative_to(self.input_dir))
            ))

    def validate_cross_references(self):
        """Validate that all cross-references in matrix resolve to real documents"""
        print("Validating cross-references...")

        # Extract all document IDs from upstream/downstream columns
        all_referenced_ids = set()

        for doc_id, metadata in self.matrix_metadata.items():
            # Extract upstream references
            upstream_text = metadata.get('upstream', '')
            upstream_ids = re.findall(r'([A-Z]+-\d+(?:-\d+)?)', upstream_text)

            # Extract downstream references
            downstream_text = metadata.get('downstream', '')
            downstream_ids = re.findall(r'([A-Z]+-\d+(?:-\d+)?)', downstream_text)

            all_referenced_ids.update(upstream_ids)
            all_referenced_ids.update(downstream_ids)

        # Check if referenced documents exist (for same document type)
        same_type_refs = {ref for ref in all_referenced_ids if ref.startswith(self.doc_type)}

        for ref_id in same_type_refs:
            if ref_id not in self.actual_doc_ids:
                self.issues.append(ValidationIssue(
                    ValidationIssue.SEVERITY_WARNING,
                    "Broken Reference",
                    f"Cross-reference to {ref_id} but document does not exist",
                    "Upstream/Downstream links"
                ))

    def validate_statistics(self):
        """Validate that statistics in matrix match actual data"""
        print("Validating statistics...")

        try:
            with open(self.matrix_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract claimed total documents
            total_match = re.search(
                r'\*\*Total\s+' + self.doc_type + r'\s+Tracked\*\*:\s*(\d+)',
                content, re.IGNORECASE
            )

            if total_match:
                claimed_total = int(total_match.group(1))
                actual_total = len(self.actual_doc_ids)

                if claimed_total != actual_total:
                    self.issues.append(ValidationIssue(
                        ValidationIssue.SEVERITY_ERROR,
                        "Statistics Mismatch",
                        f"Matrix claims {claimed_total} total documents but found {actual_total}",
                        "Section 1.1 Statistics"
                    ))

            # Extract coverage percentages and validate
            upstream_cov_match = re.search(
                r'\*\*Upstream Coverage\*\*:\s*([\d.]+)%',
                content, re.IGNORECASE
            )

            if upstream_cov_match:
                claimed_upstream = float(upstream_cov_match.group(1))

                # Calculate actual upstream coverage
                docs_with_upstream = 0
                for metadata in self.matrix_metadata.values():
                    if metadata.get('upstream', 'None').strip() not in ['None', 'N/A', '']:
                        docs_with_upstream += 1

                actual_upstream = (docs_with_upstream / len(self.matrix_doc_ids) * 100) if self.matrix_doc_ids else 0

                # Allow 1% tolerance for rounding
                if abs(claimed_upstream - actual_upstream) > 1.0:
                    self.issues.append(ValidationIssue(
                        ValidationIssue.SEVERITY_WARNING,
                        "Statistics Mismatch",
                        f"Claimed upstream coverage {claimed_upstream}% differs from actual {actual_upstream:.1f}%",
                        "Section 1.1 Statistics"
                    ))

        except Exception as e:
            self.issues.append(ValidationIssue(
                ValidationIssue.SEVERITY_WARNING,
                "Validation Error",
                f"Error validating statistics: {e}",
                "Statistics section"
            ))

    def validate_metadata_completeness(self):
        """Validate that all documents have complete metadata"""
        print("Validating metadata completeness...")

        for doc_id, metadata in self.matrix_metadata.items():
            # Check for missing title
            if not metadata.get('title') or metadata['title'] == 'Untitled':
                self.issues.append(ValidationIssue(
                    ValidationIssue.SEVERITY_WARNING,
                    "Incomplete Metadata",
                    f"Document {doc_id} has missing or placeholder title",
                    "Document inventory"
                ))

            # Check for unknown status
            if metadata.get('status', '').lower() == 'unknown':
                self.issues.append(ValidationIssue(
                    ValidationIssue.SEVERITY_INFO,
                    "Incomplete Metadata",
                    f"Document {doc_id} has unknown status",
                    "Document inventory"
                ))

            # Check for missing date
            if not metadata.get('date') or metadata['date'] == 'N/A':
                self.issues.append(ValidationIssue(
                    ValidationIssue.SEVERITY_INFO,
                    "Incomplete Metadata",
                    f"Document {doc_id} has missing date",
                    "Document inventory"
                ))

    def validate_matrix_structure(self):
        """Validate that matrix has required sections"""
        print("Validating matrix structure...")

        required_sections = [
            r'##\s+1\.\s+Overview',
            r'##\s+2\.\s+Complete.*?Inventory',
            r'##\s+3\.\s+.*?Traceability',
            r'##\s+4\.\s+.*?Traceability',
        ]

        try:
            with open(self.matrix_path, 'r', encoding='utf-8') as f:
                content = f.read()

            for section_pattern in required_sections:
                if not re.search(section_pattern, content, re.IGNORECASE):
                    self.issues.append(ValidationIssue(
                        ValidationIssue.SEVERITY_WARNING,
                        "Missing Section",
                        f"Required section not found: {section_pattern}",
                        "Matrix structure"
                    ))

        except Exception as e:
            self.issues.append(ValidationIssue(
                ValidationIssue.SEVERITY_ERROR,
                "Validation Error",
                f"Error validating matrix structure: {e}",
                str(self.matrix_path)
            ))

    def generate_report(self) -> str:
        """
        Generate validation report

        Returns:
            Formatted validation report string
        """
        # Count issues by severity
        severity_counts = defaultdict(int)
        for issue in self.issues:
            severity_counts[issue.severity] += 1

        # Build report
        report = "# Traceability Matrix Validation Report\n\n"
        report += "## Validation Summary\n\n"
        report += f"- **Matrix File**: {self.matrix_path.name}\n"
        report += f"- **Document Type**: {self.doc_type}\n"
        report += f"- **Input Directory**: {self.input_dir}\n"
        report += f"- **Validation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"- **Strict Mode**: {'Enabled' if self.strict else 'Disabled'}\n\n"

        report += "## Issue Summary\n\n"
        report += f"- **Total Issues**: {len(self.issues)}\n"
        report += f"- **Critical**: {severity_counts[ValidationIssue.SEVERITY_CRITICAL]}\n"
        report += f"- **Errors**: {severity_counts[ValidationIssue.SEVERITY_ERROR]}\n"
        report += f"- **Warnings**: {severity_counts[ValidationIssue.SEVERITY_WARNING]}\n"
        report += f"- **Info**: {severity_counts[ValidationIssue.SEVERITY_INFO]}\n\n"

        # Overall status
        if severity_counts[ValidationIssue.SEVERITY_CRITICAL] > 0:
            status = "❌ FAILED (Critical issues found)"
        elif severity_counts[ValidationIssue.SEVERITY_ERROR] > 0:
            status = "❌ FAILED (Errors found)"
        elif self.strict and severity_counts[ValidationIssue.SEVERITY_WARNING] > 0:
            status = "❌ FAILED (Warnings in strict mode)"
        elif severity_counts[ValidationIssue.SEVERITY_WARNING] > 0:
            status = "🟡 PASSED WITH WARNINGS"
        else:
            status = "✅ PASSED"

        report += f"**Overall Status**: {status}\n\n"

        # Document counts
        report += "## Document Counts\n\n"
        report += f"- **Matrix Inventory**: {len(self.matrix_doc_ids)} documents\n"
        report += f"- **Actual Files**: {len(self.actual_doc_ids)} documents\n"
        report += f"- **Match**: {'✅ Yes' if len(self.matrix_doc_ids) == len(self.actual_doc_ids) else '❌ No'}\n\n"

        # Issues by category
        if self.issues:
            report += "## Issues by Category\n\n"

            issues_by_category = defaultdict(list)
            for issue in self.issues:
                issues_by_category[issue.category].append(issue)

            for category in sorted(issues_by_category.keys()):
                report += f"### {category}\n\n"

                for issue in issues_by_category[category]:
                    icon = {
                        ValidationIssue.SEVERITY_CRITICAL: "🔴",
                        ValidationIssue.SEVERITY_ERROR: "❌",
                        ValidationIssue.SEVERITY_WARNING: "⚠️",
                        ValidationIssue.SEVERITY_INFO: "ℹ️"
                    }.get(issue.severity, "•")

                    report += f"{icon} **[{issue.severity}]** {issue.message}\n"
                    if issue.location:
                        report += f"   - Location: {issue.location}\n"
                    report += "\n"

        else:
            report += "## Validation Results\n\n"
            report += "✅ No issues found. Matrix is valid and consistent with actual documents.\n\n"

        # Recommendations
        if self.issues:
            report += "## Recommendations\n\n"

            if severity_counts[ValidationIssue.SEVERITY_CRITICAL] > 0 or severity_counts[ValidationIssue.SEVERITY_ERROR] > 0:
                report += "1. **Regenerate Matrix**: Critical errors suggest matrix is out of sync. Run:\n"
                report += f"   ```bash\n"
                report += f"   python scripts/generate_traceability_matrix.py --type {self.doc_type} --input {self.input_dir} --output {self.matrix_path}\n"
                report += f"   ```\n\n"

            if severity_counts[ValidationIssue.SEVERITY_WARNING] > 0:
                report += "2. **Review Warnings**: Address warnings to improve matrix quality\n"
                report += "3. **Update Metadata**: Ensure all documents have complete metadata in Section 7\n\n"

        report += "---\n\n"
        report += "*Generated by validate_traceability_matrix.py*\n"

        return report

    def validate(self) -> bool:
        """
        Run complete validation

        Returns:
            True if validation passes, False otherwise
        """
        print(f"Validating traceability matrix: {self.matrix_path.name}")
        print(f"Document type: {self.doc_type}")
        print(f"Input directory: {self.input_dir}\n")

        # Run all validation checks
        self.scan_actual_documents()
        self.parse_matrix_inventory()
        self.validate_matrix_structure()
        self.validate_document_counts()
        self.validate_document_existence()
        self.validate_cross_references()
        self.validate_statistics()
        self.validate_metadata_completeness()

        # Generate report
        report = self.generate_report()

        # Print report
        print("\n" + "="*80)
        print(report)
        print("="*80 + "\n")

        # Determine pass/fail
        critical_count = sum(1 for issue in self.issues if issue.severity == ValidationIssue.SEVERITY_CRITICAL)
        error_count = sum(1 for issue in self.issues if issue.severity == ValidationIssue.SEVERITY_ERROR)
        warning_count = sum(1 for issue in self.issues if issue.severity == ValidationIssue.SEVERITY_WARNING)

        if critical_count > 0 or error_count > 0:
            return False

        if self.strict and warning_count > 0:
            return False

        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate traceability matrix against actual documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate ADR matrix
  python validate_traceability_matrix.py --matrix TRACEABILITY_MATRIX_ADR.md --input ../adrs/

  # Strict validation (warnings = errors)
  python validate_traceability_matrix.py --matrix TRACEABILITY_MATRIX_REQ.md --input ../reqs/ --strict

  # Validate with custom output
  python validate_traceability_matrix.py --matrix matrix.md --input ../specs/ --output validation_report.md
        """
    )

    parser.add_argument(
        '--matrix',
        required=True,
        help='Path to traceability matrix file to validate'
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Input directory containing actual documents'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict mode (treat warnings as errors)'
    )

    parser.add_argument(
        '--output',
        help='Output file for validation report (optional, prints to stdout if not specified)'
    )

    args = parser.parse_args()

    try:
        validator = TraceabilityMatrixValidator(
            matrix_path=args.matrix,
            input_dir=args.input,
            strict=args.strict
        )

        is_valid = validator.validate()

        # Save report if output specified
        if args.output:
            report = validator.generate_report()
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Validation report saved: {args.output}")

        # Return appropriate exit code
        return 0 if is_valid else 1

    except Exception as e:
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
