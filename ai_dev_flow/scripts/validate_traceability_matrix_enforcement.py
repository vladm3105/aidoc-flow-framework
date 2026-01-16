#!/usr/bin/env python3
"""
Traceability Matrix Validation Script

Validates that traceability matrices exist and are complete for all artifact types.

Usage:
    python validate_traceability_matrix_enforcement.py --type PRD
    python validate_traceability_matrix_enforcement.py --all
    python validate_traceability_matrix_enforcement.py --type PRD --strict
"""

import argparse
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Artifact types with traceability matrices
ARTIFACT_TYPES = [
    'BRD', 'PRD', 'EARS', 'BDD', 'ADR', 'SYS',
    'REQ', 'IMPL', 'CTR', 'SPEC', 'TASKS'
]

class TraceabilityValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / 'docs'
        self.errors = []
        self.warnings = []

    def validate_artifact_type(self, artifact_type: str, strict: bool = False) -> bool:
        """Validate traceability matrix for specific artifact type"""
        print(f"\n{'='*60}")
        print(f"Validating {artifact_type} Traceability Matrix")
        print(f"{'='*60}")

        # Check 1: Matrix file exists
        matrix_file = self.docs_dir / artifact_type / f"{artifact_type}-00_TRACEABILITY_MATRIX.md"

        if not matrix_file.exists():
            self.errors.append(f"❌ Matrix file missing: {matrix_file}")
            print(f"❌ FAIL: Matrix file does not exist")
            return False

        print(f"✅ PASS: Matrix file exists: {matrix_file}")

        # Check 2: Matrix contains artifact inventory
        with open(matrix_file, 'r') as f:
            matrix_content = f.read()

        if "## 2. Complete" not in matrix_content:
            self.errors.append(f"❌ Matrix missing Section 2 (Inventory): {matrix_file}")
            return False

        print(f"✅ PASS: Matrix contains inventory section")

        # Check 3: All artifact documents appear in matrix
        artifact_dir = self.docs_dir / artifact_type
        artifact_files = self._get_artifact_files(artifact_dir, artifact_type)

        missing_from_matrix = []
        for artifact_file in artifact_files:
            artifact_id = self._extract_id(artifact_file, artifact_type)
            if artifact_id and artifact_id not in matrix_content:
                missing_from_matrix.append(artifact_id)

        if missing_from_matrix:
            self.errors.append(f"❌ Artifacts missing from matrix: {', '.join(missing_from_matrix)}")
            print(f"❌ FAIL: {len(missing_from_matrix)} artifacts not in matrix")
            for aid in missing_from_matrix:
                print(f"  - {aid}")
            return False

        print(f"✅ PASS: All {len(artifact_files)} artifacts tracked in matrix")

        # Check 4: Upstream section exists (REQUIRED for all except BRD)
        # Note: Upstream is REQUIRED, Downstream is OPTIONAL per traceability rules
        if "## 3. Upstream Traceability" not in matrix_content and "## 5. Upstream Traceability" not in matrix_content and "## 6. Upstream Traceability" not in matrix_content:
            if artifact_type == "BRD":
                # BRD upstream is OPTIONAL (only to other BRDs or business docs)
                self.warnings.append(f"⚠️  BRD matrix missing upstream traceability section (OPTIONAL for BRD)")
                print(f"⚠️  INFO: Upstream traceability section missing (OPTIONAL for BRD)")
            else:
                # All other artifact types require upstream traceability
                self.errors.append(f"❌ Matrix missing upstream traceability section (REQUIRED)")
                print(f"❌ FAIL: Upstream traceability section missing (REQUIRED)")
                return False
        else:
            print(f"✅ PASS: Upstream traceability section exists (REQUIRED)")

        # Check 5: Downstream section exists (OPTIONAL for all artifact types)
        if "## 4. Downstream Traceability" not in matrix_content and "## 6. Downstream Traceability" not in matrix_content and "## 7. Downstream Traceability" not in matrix_content:
            # Downstream is OPTIONAL - only a warning, not an error
            self.warnings.append(f"⚠️  Matrix missing downstream traceability section (OPTIONAL)")
            print(f"⚠️  INFO: Downstream traceability section missing (OPTIONAL - only add when downstream docs exist)")
        else:
            print(f"✅ PASS: Downstream traceability section exists (OPTIONAL)")

        # Check 6: Validate references resolve (strict mode)
        if strict:
            unresolved = self._check_references(matrix_content)
            if unresolved:
                self.errors.append(f"❌ Unresolved references: {', '.join(unresolved[:5])}")
                return False
            print(f"✅ PASS: All references resolve correctly")

        print(f"\n✅ SUCCESS: {artifact_type} traceability matrix valid")
        return True

    def _get_artifact_files(self, directory: Path, artifact_type: str) -> List[Path]:
        """Get all artifact files excluding templates and matrices"""
        if not directory.exists():
            return []

        pattern = f"{artifact_type}-[0-9]*.md"

        files = []
        for f in directory.glob(pattern):
            # Exclude templates, indices, and matrices
            if 'TEMPLATE' not in f.name and '000_index' not in f.name and 'TRACEABILITY_MATRIX' not in f.name:
                files.append(f)
        return files

    def _extract_id(self, file_path: Path, artifact_type: str) -> str:
        """Extract artifact ID from filename"""
        match = re.match(f"{artifact_type}-([0-9]+)", file_path.name)
        return f"{artifact_type}-{match.group(1)}" if match else None

    def _check_references(self, content: str) -> List[str]:
        """Check if all references in matrix resolve"""
        # Extract all [TYPE-NN] style references
        references = re.findall(r'\[([A-Z]+-[0-9]+)\]', content)
        unresolved = []

        for ref in references:
            ref_type = ref.split('-')[0]
            ref_file_pattern = f"{ref}*.md"
            ref_dir = self.docs_dir / ref_type
            if not ref_dir.exists():
                unresolved.append(ref)
                continue
            matching_files = list(ref_dir.glob(ref_file_pattern))
            if not matching_files:
                unresolved.append(ref)

        return unresolved

    def validate_all(self, strict: bool = False) -> bool:
        """Validate traceability matrices for all artifact types"""
        all_valid = True
        for artifact_type in ARTIFACT_TYPES:
            if not self.validate_artifact_type(artifact_type, strict):
                all_valid = False

        return all_valid

    def print_summary(self):
        """Print validation summary"""
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print(f"{'='*60}")

        if not self.errors and not self.warnings:
            print("✅ All traceability matrices valid")
            return True

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        return len(self.errors) == 0

def main():
    parser = argparse.ArgumentParser(description='Validate traceability matrices')
    parser.add_argument('--type', choices=ARTIFACT_TYPES, help='Artifact type to validate')
    parser.add_argument('--all', action='store_true', help='Validate all artifact types')
    parser.add_argument('--strict', action='store_true', help='Strict validation (check all references)')
    parser.add_argument('--project-root', default='.', help='Project root directory')

    args = parser.parse_args()

    if not args.type and not args.all:
        parser.error("Either --type or --all must be specified")

    validator = TraceabilityValidator(args.project_root)

    if args.all:
        success = validator.validate_all(args.strict)
    else:
        success = validator.validate_artifact_type(args.type, args.strict)

    validator.print_summary()

    exit(0 if success else 1)

if __name__ == '__main__':
    main()
