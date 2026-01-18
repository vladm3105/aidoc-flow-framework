#!/usr/bin/env python3
"""
Validate Documentation Path References

Checks:
- Broken markdown links (space characters, invalid syntax)
- Missing referenced files
- Case mismatches in file references
- Incorrect relative path depths
- Non-existent directories in paths

Severity Levels:
- HIGH: Broken links, missing files, space characters in links
- MEDIUM: Case mismatches, incorrect path depths
- LOW: Warnings, suggestions

Usage:
    python validate_documentation_paths.py [--strict]

Options:
    --strict    Exit with non-zero status if HIGH or MEDIUM issues found
"""

import argparse
import os
import re
import sys
from pathlib import Path
import os
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Issue:
    """Represents a validation issue"""
    severity: Severity
    file_path: str
    line_number: int
    issue_type: str
    description: str
    suggestion: str = ""


class DocumentationPathValidator:
    """Validates path references in markdown documentation"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.issues: List[Issue] = []

        # Directories to exclude from scanning
        self.exclude_dirs = {'.git', '.claude', 'work_plans', 'archived', '__pycache__', 'node_modules'}

        # Known missing files that are intentional (placeholders, examples)
        self.intentional_missing = {
            'example.md', 'placeholder.md', '{project_root}',
            '{file}', '{artifact}', 'XXX', 'NNN', 'PPP', 'YYY',
            'path#anchor', 'file_name', 'some_api', 'some_feature'
        }

        # Patterns for placeholder IDs in examples
        self.placeholder_patterns = [
            r'BRD-\d{3}',  # BRD-01, BRD-002, etc.
            r'PRD-\d{3}',
            r'REQ-\d{3}',
            r'ADR-\d{3}',
            r'SPEC-\d{3}',
            r'EARS-\d{3}',
            r'SYS-\d{3}',
            r'CTR-\d{3}',
            r'BDD-\d{3}',
            r'IMPL-\d{3}',
            r'TASKS-\d{3}',
        ]

    def validate_all(self) -> List[Issue]:
        """Run all validation checks"""
        print(f"Scanning documentation in: {self.root_dir}")

        # Find all markdown files
        md_files = self._find_markdown_files()
        print(f"Found {len(md_files)} markdown files")

        # Validate each file
        for md_file in md_files:
            self._validate_file(md_file)

        return self.issues

    def _find_markdown_files(self) -> List[Path]:
        """Find all markdown files, excluding certain directories"""
        md_files = []

        for root, dirs, files in os.walk(self.root_dir):
            # Remove excluded directories from search
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith('.md'):
                    md_files.append(Path(root) / file)

        return md_files

    def _validate_file(self, file_path: Path):
        """Validate all path references in a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            self.issues.append(Issue(
                severity=Severity.HIGH,
                file_path=str(file_path.relative_to(self.root_dir)),
                line_number=0,
                issue_type="FILE_READ_ERROR",
                description=f"Failed to read file: {e}"
            ))
            return

        # Ignore regions and code fences
        ignore = False
        in_code_block = False

        for line_num, line in enumerate(lines, start=1):
            # Toggle validator ignore markers
            if '<!-- VALIDATOR:IGNORE-LINKS-START -->' in line:
                ignore = True
            if '<!-- VALIDATOR:IGNORE-LINKS-END -->' in line:
                ignore = False
                continue

            # Toggle fenced code block state
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue

            if ignore or in_code_block:
                continue

            # Check for markdown links
            self._check_markdown_links(file_path, line_num, line)

    def _check_markdown_links(self, file_path: Path, line_num: int, line: str):
        """Check markdown links for various issues"""
        # Pattern: [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        for match in re.finditer(link_pattern, line):
            link_text = match.group(1)
            link_path = match.group(2)

            # Skip external URLs
            if link_path.startswith(('http://', 'https://', 'mailto:', '#')):
                continue

            # Check for space characters in path (HIGH severity)
            if re.search(r'\(\s*\.\.\s+/', line[match.start():match.end()]):
                self.issues.append(Issue(
                    severity=Severity.HIGH,
                    file_path=str(file_path.relative_to(self.root_dir)),
                    line_number=line_num,
                    issue_type="SPACE_IN_LINK",
                    description=f"Space character in link path: '{link_path}'",
                    suggestion=f"Remove space: change '(.. /' to '(../'"
                ))

            # Skip placeholder paths
            if self._is_placeholder_path(link_path):
                continue

            # Resolve the path
            self._check_path_exists(file_path, line_num, link_path, link_text)

    def _is_placeholder_path(self, path: str) -> bool:
        """Check if path is an intentional placeholder"""
        path_lower = path.lower()

        # Check for common placeholders
        if any(placeholder in path for placeholder in self.intentional_missing):
            return True

        # Check for variable patterns
        if '{' in path or '}' in path:
            return True

        # Check for template patterns like XXX-NNN
        if re.search(r'XXX|NNN|PPP|YYY', path):
            return True

        # Check for placeholder ID patterns (BRD-01, REQ-03, etc.)
        for pattern in self.placeholder_patterns:
            if re.search(pattern, path):
                return True

        # Check if path contains common example keywords
        if any(keyword in path_lower for keyword in ['example', '_file', 'some_', 'your_']):
            return True

        return False

    def _check_path_exists(self, source_file: Path, line_num: int,
                          link_path: str, link_text: str):
        """Check if referenced path exists"""
        # Remove anchor fragments
        path_without_anchor = link_path.split('#')[0]

        if not path_without_anchor:
            return  # Link is just an anchor

        # Resolve relative path
        if path_without_anchor.startswith('/'):
            # Absolute path from project root
            target_path = self.root_dir / path_without_anchor.lstrip('/')
        else:
            # Relative path from source file
            target_path = (source_file.parent / path_without_anchor).resolve()

        # Check if path exists
        if not target_path.exists():
            # Check for case mismatch (MEDIUM severity)
            if self._has_case_mismatch(target_path):
                self.issues.append(Issue(
                    severity=Severity.MEDIUM,
                    file_path=str(source_file.relative_to(self.root_dir)),
                    line_number=line_num,
                    issue_type="CASE_MISMATCH",
                    description=f"Case mismatch in path: '{link_path}'",
                    suggestion="Check filename case (e.g., BRD-MVP-TEMPLATE.md vs brd-mvp-template.md)"
                ))
            else:
                self.issues.append(Issue(
                    severity=Severity.HIGH,
                    file_path=str(source_file.relative_to(self.root_dir)),
                    line_number=line_num,
                    issue_type="MISSING_FILE",
                    description=f"Referenced file not found: '{link_path}' (resolved to: {target_path})",
                    suggestion=f"Verify the file exists or update the link"
                ))

    def _has_case_mismatch(self, target_path: Path) -> bool:
        """Check if file exists with different case"""
        if not target_path.parent.exists():
            return False

        target_name_lower = target_path.name.lower()

        try:
            for existing_file in target_path.parent.iterdir():
                if existing_file.name.lower() == target_name_lower:
                    return True
        except Exception:
            pass

        return False

    def report(self, strict: bool = False) -> int:
        """Print validation report and return exit code"""
        # Group issues by severity
        high_issues = [i for i in self.issues if i.severity == Severity.HIGH]
        medium_issues = [i for i in self.issues if i.severity == Severity.MEDIUM]
        low_issues = [i for i in self.issues if i.severity == Severity.LOW]

        # Print summary
        print("\n" + "="*80)
        print("DOCUMENTATION PATH VALIDATION REPORT")
        print("="*80)
        print(f"\nTotal Issues Found: {len(self.issues)}")
        print(f"  HIGH:   {len(high_issues)}")
        print(f"  MEDIUM: {len(medium_issues)}")
        print(f"  LOW:    {len(low_issues)}")

        # Print HIGH severity issues
        if high_issues:
            print("\n" + "-"*80)
            print("HIGH SEVERITY ISSUES")
            print("-"*80)
            for issue in high_issues:
                self._print_issue(issue)

        # Print MEDIUM severity issues
        if medium_issues:
            print("\n" + "-"*80)
            print("MEDIUM SEVERITY ISSUES")
            print("-"*80)
            for issue in medium_issues:
                self._print_issue(issue)

        # Print LOW severity issues
        if low_issues:
            print("\n" + "-"*80)
            print("LOW SEVERITY ISSUES")
            print("-"*80)
            for issue in low_issues:
                self._print_issue(issue)

        # Print success message if no issues
        if not self.issues:
            print("\n✅ No issues found! All documentation paths are valid.")

        print("\n" + "="*80)

        # Determine exit code
        if strict and (high_issues or medium_issues):
            print("\n❌ VALIDATION FAILED (strict mode)")
            return 1
        elif high_issues:
            print("\n⚠️  HIGH severity issues found - please fix")
            return 1
        else:
            print("\n✅ VALIDATION PASSED")
            return 0

    def _print_issue(self, issue: Issue):
        """Print a single issue"""
        print(f"\n{issue.file_path}:{issue.line_number}")
        print(f"  [{issue.severity.value}] {issue.issue_type}")
        print(f"  {issue.description}")
        if issue.suggestion:
            print(f"  💡 Suggestion: {issue.suggestion}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate documentation path references",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with non-zero status if HIGH or MEDIUM issues found'
    )
    parser.add_argument(
        '--root',
        type=str,
        default=None,
        help='Root directory to scan (default: script directory parent)'
    )

    args = parser.parse_args()

    # Determine root directory
    if args.root:
        root_dir = Path(args.root)
    else:
        # Prefer explicit env var, then discover by walking up from script dir
        env_root = os.environ.get("AI_DEV_FLOW_ROOT")
        if env_root and Path(env_root).exists():
            root_dir = Path(env_root)
        else:
            script_dir = Path(__file__).resolve().parent
            candidates = [script_dir, script_dir.parent, script_dir.parent.parent]
            sentinels = {"BRD", "PRD", "EARS", "BDD", "ADR", "SYS", "REQ", "CTR", "SPEC", "TASKS"}
            def has_sentinels(p: Path) -> bool:
                try:
                    return all((p / s).exists() for s in sentinels)
                except Exception:
                    return False
            root_dir = None
            for c in candidates:
                if has_sentinels(c):
                    root_dir = c
                    break
            if root_dir is None:
                root_dir = script_dir.parent  # fallback

    if not root_dir.exists():
        print(f"Error: Root directory not found: {root_dir}")
        return 1

    # Run validation
    validator = DocumentationPathValidator(str(root_dir))
    validator.validate_all()

    # Print report and exit
    exit_code = validator.report(strict=args.strict)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
