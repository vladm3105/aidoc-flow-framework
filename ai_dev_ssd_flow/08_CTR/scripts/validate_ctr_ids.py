#!/usr/bin/env python3
"""
CTR ID and Structure Validator

Validates CTR document IDs, naming conventions, and basic template compliance.
Ensures:
- CTR-NN ID format compliance
- Filename matches document ID
- No duplicate CTR-IDs across corpus
- Optional: H1 header matches filename ID

Usage:
    python validate_ctr_ids.py --directory docs/08_CTR
    python validate_ctr_ids.py --ctr-file docs/08_CTR/CTR-01_iam.md
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ValidationResult:
    file_path: Path
    ctr_id: str = ""
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class CTRIDValidator:
    """Validator for CTR document IDs and structure."""

    CTR_ID_PATTERN = r"^CTR-(\d{2,})$"
    FILENAME_PATTERN = r"^CTR-(\d{2,})_[a-z0-9_]+\.(md|yaml)$"

    def __init__(self):
        self.seen_ids: Dict[str, List[Path]] = defaultdict(list)

    def validate_file(self, file_path: Path) -> ValidationResult:
        result = ValidationResult(file_path=file_path)

        # Check filename format
        if not re.match(self.FILENAME_PATTERN, file_path.name):
            result.errors.append(
                f"Invalid filename format: {file_path.name}. "
                "Expected: CTR-NN_descriptive_title.md"
            )
            result.valid = False
            return result

        # Read content
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result.errors.append(f"Failed to read file: {e}")
            result.valid = False
            return result

        # Extract CTR-ID from H1 header or title/frontmatter
        ctr_id = self._extract_ctr_id(content)
        if not ctr_id:
            result.errors.append("CTR-ID not found in document header")
            result.valid = False
            return result

        result.ctr_id = ctr_id

        # Validate CTR-ID format
        if not re.match(self.CTR_ID_PATTERN, ctr_id):
            result.errors.append(
                f"Invalid CTR-ID format: {ctr_id}. Expected: CTR-NN (e.g., CTR-01)"
            )
            result.valid = False
            return result

        # Check filename matches ID
        id_in_filename = file_path.name.split('_')[0]
        if id_in_filename != ctr_id:
            result.errors.append(
                f"Filename ID ({id_in_filename}) does not match document ID ({ctr_id})"
            )
            result.valid = False

        # Duplicate detection
        self.seen_ids[ctr_id].append(file_path)
        if len(self.seen_ids[ctr_id]) > 1:
            result.errors.append(f"Duplicate CTR-ID: {ctr_id} found in multiple files")
            result.valid = False

        return result

    def _extract_ctr_id(self, content: str) -> str:
        # H1 header like: # CTR-01: Title
        patterns = [
            r"^#\s*(CTR-\d{2,})",
            r"^##\s*(CTR-\d{2,})",
            r"^title:\s*\"(CTR-\d{2,})",
        ]
        for pat in patterns:
            m = re.search(pat, content, re.MULTILINE)
            if m:
                return m.group(1)
        return ""

    def validate_directory(self, directory: Path) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        for f in directory.rglob("CTR-*_*.md"):
            if "_index" in f.name or "TEMPLATE" in f.name:
                continue
            results.append(self.validate_file(f))
        return results


def print_report(results: List[ValidationResult]) -> int:
    errors = sum(1 for r in results if r.errors)
    warnings = sum(1 for r in results if r.warnings)
    print("\nCTR ID VALIDATION REPORT\n")
    for r in results:
        status = "✅ PASS" if not r.errors else "❌ FAIL"
        print(f"{status} {r.file_path.name}")
        for e in r.errors:
            print(f"    ❌ ERROR: {e}")
        for w in r.warnings:
            print(f"    ⚠️  WARNING: {w}")
    if errors:
        return 2
    if warnings:
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate CTR IDs and filenames")
    parser.add_argument("--ctr-file", type=Path, help="Path to specific CTR file")
    parser.add_argument("--directory", type=Path, help="Path to CTR directory")
    args = parser.parse_args()

    if not args.ctr_file and not args.directory:
        parser.error("Must specify either --ctr-file or --directory")

    validator = CTRIDValidator()
    results: List[ValidationResult]
    if args.ctr_file:
        results = [validator.validate_file(args.ctr_file)]
    else:
        results = validator.validate_directory(args.directory)

    exit_code = print_report(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
