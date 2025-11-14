#!/usr/bin/env python3
"""
Documentation Consistency Validation Script

Checks for:
- Broken markdown links
- Layer number reference consistency
- Template reference validity
- Deprecated terminology usage

Usage:
    python3 validate_documentation_consistency.py [directory]

    If no directory specified, validates ./ai_dev_flow
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

class DocumentationValidator:
    """Validates AI Dev Flow documentation consistency"""

    def __init__(self, base_dir: str = "./ai_dev_flow"):
        self.base_dir = Path(base_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

        # Deprecated terms to check for
        self.deprecated_terms = {
            "TASKS_PLANS": "Use 'IPLAN' instead",
            "CONTRACTS/": "Use 'CTR/' instead",
            "Implementation Plans (Layer 8)": "Use 'Implementation Specifications (IMPL) - Layer 8'",
            "Implementation Plans (Layer 12)": "Use 'Implementation Work Plans (IPLAN) - Layer 12'",
        }

        # Valid layer numbers
        self.valid_layers = set(range(0, 16))  # Layers 0-15

    def validate_markdown_links(self) -> int:
        """Check all markdown links resolve to existing files"""
        print("\n=== Validating Markdown Links ===")
        issue_count = 0

        # Pattern to match markdown links: [text](path) or [text](path#anchor)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

        for md_file in self.base_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                for match in link_pattern.finditer(content):
                    link_text = match.group(1)
                    link_path = match.group(2)

                    # Skip external links (http/https) and anchors only
                    if link_path.startswith(('http://', 'https://', '#', 'mailto:')):
                        continue

                    # Extract file path (remove anchor if present)
                    file_path = link_path.split('#')[0]
                    if not file_path:  # Anchor-only link
                        continue

                    # Resolve relative path
                    target_path = (md_file.parent / file_path).resolve()

                    if not target_path.exists():
                        self.errors.append(f"Broken link in {md_file.relative_to(self.base_dir)}: [{link_text}]({link_path})")
                        issue_count += 1

            except Exception as e:
                self.errors.append(f"Error reading {md_file}: {e}")
                issue_count += 1

        if issue_count == 0:
            print("✓ All markdown links valid")
        else:
            print(f"✗ Found {issue_count} broken links")

        return issue_count

    def check_layer_references(self) -> int:
        """Verify layer number references match formal 0-15 scheme"""
        print("\n=== Checking Layer References ===")
        issue_count = 0

        # Pattern to match "Layer N" or "Layer NN" references
        layer_pattern = re.compile(r'Layer\s+(\d+)', re.IGNORECASE)

        for md_file in self.base_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                for match in layer_pattern.finditer(content):
                    layer_num = int(match.group(1))
                    if layer_num not in self.valid_layers:
                        self.errors.append(f"Invalid layer number in {md_file.relative_to(self.base_dir)}: Layer {layer_num} (valid: 0-15)")
                        issue_count += 1

            except Exception as e:
                self.errors.append(f"Error reading {md_file}: {e}")
                issue_count += 1

        if issue_count == 0:
            print("✓ All layer references valid (0-15)")
        else:
            print(f"✗ Found {issue_count} invalid layer references")

        return issue_count

    def validate_template_refs(self) -> int:
        """Check template references in README files match actual files"""
        print("\n=== Validating Template References ===")
        issue_count = 0

        # Pattern to match template references
        template_pattern = re.compile(r'\[([A-Z]+-TEMPLATE[^\]]*)\]\(([^)]+)\)')

        for readme_file in self.base_dir.rglob("README.md"):
            try:
                content = readme_file.read_text(encoding='utf-8')
                for match in template_pattern.finditer(content):
                    template_name = match.group(1)
                    template_path = match.group(2)

                    # Resolve relative path
                    target_path = (readme_file.parent / template_path).resolve()

                    if not target_path.exists():
                        self.errors.append(f"Missing template in {readme_file.relative_to(self.base_dir)}: {template_name} -> {template_path}")
                        issue_count += 1

            except Exception as e:
                self.errors.append(f"Error reading {readme_file}: {e}")
                issue_count += 1

        if issue_count == 0:
            print("✓ All template references valid")
        else:
            print(f"✗ Found {issue_count} broken template references")

        return issue_count

    def check_deprecated_terms(self) -> int:
        """Find usage of deprecated terminology"""
        print("\n=== Checking Deprecated Terms ===")
        issue_count = 0

        for md_file in self.base_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                for term, replacement in self.deprecated_terms.items():
                    if term in content:
                        occurrences = content.count(term)
                        self.warnings.append(f"Deprecated term '{term}' in {md_file.relative_to(self.base_dir)} ({occurrences} occurrences) - {replacement}")
                        issue_count += 1

            except Exception as e:
                self.errors.append(f"Error reading {md_file}: {e}")

        if issue_count == 0:
            print("✓ No deprecated terms found")
        else:
            print(f"⚠ Found {issue_count} deprecated term usages")

        return issue_count

    def check_mermaid_diagrams(self) -> int:
        """Check for Mermaid diagrams and verify they have clarification notes"""
        print("\n=== Checking Mermaid Diagram Clarifications ===")
        issue_count = 0

        clarification_text = "Note on Diagram Labels"

        for md_file in self.base_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')

                # Check if file has Mermaid diagrams
                if '```mermaid' in content:
                    # Check if clarification note exists nearby
                    if clarification_text not in content:
                        self.warnings.append(f"Mermaid diagram in {md_file.relative_to(self.base_dir)} missing layer numbering clarification note")
                        issue_count += 1

            except Exception as e:
                self.errors.append(f"Error reading {md_file}: {e}")

        if issue_count == 0:
            print("✓ All Mermaid diagrams have clarification notes")
        else:
            print(f"⚠ Found {issue_count} Mermaid diagrams without clarifications")

        return issue_count

    def run_validation(self) -> bool:
        """Run all validation checks"""
        print(f"Validating documentation in: {self.base_dir.absolute()}")
        print("=" * 60)

        total_errors = 0
        total_warnings = 0

        # Run all checks
        total_errors += self.validate_markdown_links()
        total_errors += self.check_layer_references()
        total_errors += self.validate_template_refs()
        total_warnings += self.check_deprecated_terms()
        total_warnings += self.check_mermaid_diagrams()

        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")
            return True
        else:
            print(f"\n❌ Validation completed with {len(self.errors)} errors and {len(self.warnings)} warnings")
            return False

def main():
    """Main entry point"""
    # Get directory from command line or use default
    directory = sys.argv[1] if len(sys.argv) > 1 else "./ai_dev_flow"

    validator = DocumentationValidator(directory)
    success = validator.run_validation()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
