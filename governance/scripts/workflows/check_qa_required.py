#!/usr/bin/env python3
"""Determine if a development issue requires QA testing."""

import argparse
import json
import re
from pathlib import Path


# File patterns that don't require QA testing
NON_FUNCTIONAL_PATTERNS = [
    r"\.md$",                    # Markdown files (docs)
    r"README",                   # README files
    r"CHANGELOG",                # Changelog
    r"LICENSE",                  # License files
    r"\.txt$",                   # Text files
    r"\.gitignore$",             # Git ignore
    r"\.editorconfig$",          # Editor config
    r"\.prettierrc",             # Prettier config
    r"\.eslintrc",               # ESLint config
    r"pyproject\.toml$",         # Python project config (unless deps change)
    r"\.pre-commit-config",      # Pre-commit config
    r"docs/",                    # Documentation directory
    r"governance/",              # Governance docs
    r"\.github/ISSUE_TEMPLATE",  # Issue templates
    r"\.github/PULL_REQUEST_TEMPLATE",  # PR templates
]

# File patterns that always require QA testing
FUNCTIONAL_PATTERNS = [
    r"\.py$",                    # Python source
    r"\.js$",                    # JavaScript
    r"\.ts$",                    # TypeScript
    r"\.tsx$",                   # TypeScript React
    r"\.jsx$",                   # JavaScript React
    r"\.go$",                    # Go
    r"\.rs$",                    # Rust
    r"\.java$",                  # Java
    r"\.sql$",                   # SQL
    r"\.yaml$",                  # YAML configs (may be infra)
    r"\.yml$",                   # YAML configs
    r"\.json$",                  # JSON configs
    r"Dockerfile",               # Docker
    r"docker-compose",           # Docker compose
    r"terraform",                # Terraform
    r"\.tf$",                    # Terraform files
    r"requirements.*\.txt$",     # Python requirements
    r"package\.json$",           # Node package
    r"Cargo\.toml$",             # Rust cargo
    r"go\.mod$",                 # Go modules
]


def is_functional_change(files: list[str]) -> tuple[bool, str]:
    """Determine if the changed files represent functional changes."""
    if not files:
        return False, "No files changed"

    functional_files = []
    non_functional_files = []

    for file in files:
        # Check if it matches non-functional patterns
        is_non_functional = any(
            re.search(pattern, file, re.IGNORECASE)
            for pattern in NON_FUNCTIONAL_PATTERNS
        )

        if is_non_functional:
            non_functional_files.append(file)
            continue

        # Check if it matches functional patterns
        is_functional = any(
            re.search(pattern, file, re.IGNORECASE)
            for pattern in FUNCTIONAL_PATTERNS
        )

        if is_functional:
            functional_files.append(file)
        else:
            # Unknown pattern - assume functional to be safe
            functional_files.append(file)

    if functional_files:
        return True, f"Functional files changed: {', '.join(functional_files[:5])}"

    return False, f"Only non-functional files changed: {', '.join(non_functional_files[:5])}"


def main():
    parser = argparse.ArgumentParser(
        description="Determine if QA testing is required"
    )
    parser.add_argument("--pr-number", required=True, help="PR number")
    parser.add_argument(
        "--files", required=True, help="Comma-separated list of changed files"
    )
    parser.add_argument(
        "--output-file", required=True, type=Path, help="Output JSON file"
    )
    args = parser.parse_args()

    files = [f.strip() for f in args.files.split(",") if f.strip()]
    qa_required, reason = is_functional_change(files)

    result = {
        "pr_number": args.pr_number,
        "qa_required": qa_required,
        "reason": reason,
        "files_analyzed": len(files),
    }

    args.output_file.write_text(json.dumps(result, indent=2))
    print(f"QA required: {qa_required}")
    print(f"Reason: {reason}")


if __name__ == "__main__":
    main()
