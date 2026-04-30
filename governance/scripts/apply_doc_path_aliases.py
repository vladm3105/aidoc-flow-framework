#!/usr/bin/env python3
"""
Apply deterministic documentation path alias replacements with a safe dry-run mode.

Generalizes path corrections across the ucx_framework, including:
- SDD artifacts (BRD, PRD, REQ, ADR, SPEC, etc.)
- Governance documentation
- AI project flow documents

Default behavior is dry-run. Use --apply to write changes.
"""

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path


# Default mappings for ucx_framework
# Format: (old_pattern, new_pattern)
DEFAULT_MAPPINGS = [
    # Governance consolidation (IPLAN-004)
    ("ai_project_issues_flow/governance/AI_PR_Review/", "governance/AI_PR_Review/"),
    ("ai_project_issues_flow/governance/GOVERNANCE_RULES.md", "governance/GOVERNANCE_RULES.md"),
    ("ai_project_issues_flow/governance/BRANCHING_STRATEGY.md", "governance/BRANCHING_STRATEGY.md"),
    ("ai_project_issues_flow/governance/DEFINITION_OF_DONE.md", "governance/DEFINITION_OF_DONE.md"),
    ("ai_project_issues_flow/governance/RELEASE_PROCESS.md", "governance/RELEASE_PROCESS.md"),
    ("ai_project_issues_flow/governance/REPOSITORY_STRATEGY.md", "governance/REPOSITORY_STRATEGY.md"),
    ("ai_project_issues_flow/governance/ROLES_AND_TOOLS.md", "governance/ROLES_AND_TOOLS.md"),
    ("ai_project_issues_flow/governance/HOME_REPO.md", "governance/HOME_REPO.md"),
    ("ai_project_issues_flow/governance/GITHUB_TOOLS_SETUP.md", "governance/github/GITHUB_TOOLS_SETUP.md"),
    ("ai_project_issues_flow/governance/GITHUB_WORKFLOWS.md", "governance/github/GITHUB_WORKFLOWS.md"),
    ("ai_project_issues_flow/governance/GITHUB_PROJECT_SETUP_AI_FIRST.md", "governance/github/GITHUB_PROJECT_SETUP.md"),
    ("ai_project_issues_flow/governance/ghes_runner/", "governance/github/ghes_runner/"),
    ("ai_project_issues_flow/governance/plans/README.md", "governance/plans/README.md"),
    ("ai_project_issues_flow/governance/plans/IPLAN-TEMPLATE.md", "governance/plans/IPLAN-TEMPLATE.md"),

    # SDD artifact path standardization
    ("ai_dev_flow/", "ucx_flow_v3/"),

    # Template path corrections
    ("ai_project_issues_flow/templates/CONTRIBUTING.md", "CONTRIBUTING.md"),
    ("ai_project_issues_flow/templates/README_AIAGENT.md", "README_AIAGENT.md"),
]


@dataclass
class FileChange:
    file_path: str
    replacements: list


@dataclass
class ReplacementSummary:
    mode: str
    files_scanned: int
    files_changed: int
    total_replacements: int
    changes: list


def load_mapping_csv(mapping_csv: Path) -> list[tuple[str, str]]:
    """Load custom mappings from CSV file."""
    mappings: list[tuple[str, str]] = []
    with mapping_csv.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"source_pattern", "target_pattern"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("CSV must include source_pattern,target_pattern columns")
        for row in reader:
            source = (row.get("source_pattern") or "").strip()
            target = (row.get("target_pattern") or "").strip()
            if source:
                mappings.append((source, target))
    return mappings


def run(root: Path, mappings: list[tuple[str, str]], apply: bool,
        extensions: list[str] = None) -> ReplacementSummary:
    """Scan files and apply replacements."""
    if extensions is None:
        extensions = [".md", ".yml", ".yaml"]

    all_files = []
    for ext in extensions:
        all_files.extend(root.rglob(f"*{ext}"))
    all_files = sorted(set(all_files))

    changes: list[FileChange] = []
    total_replacements = 0

    for file_path in all_files:
        # Skip node_modules and other common excludes
        if any(part in file_path.parts for part in ["node_modules", ".git", "__pycache__", "venv"]):
            continue

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, IOError):
            continue

        updated = text
        replacement_items = []

        for source, target in mappings:
            count = updated.count(source)
            if count > 0:
                updated = updated.replace(source, target)
                replacement_items.append({
                    "source_pattern": source,
                    "target_pattern": target,
                    "count": count,
                })
                total_replacements += count

        if replacement_items:
            if apply:
                file_path.write_text(updated, encoding="utf-8")
            changes.append(FileChange(str(file_path), replacement_items))

    return ReplacementSummary(
        mode="apply" if apply else "dry-run",
        files_scanned=len(all_files),
        files_changed=len(changes),
        total_replacements=total_replacements,
        changes=[asdict(c) for c in changes],
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply documentation path alias replacements for ucx_framework"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root folder to process (default: current directory)"
    )
    parser.add_argument(
        "--mapping-csv",
        help="Optional CSV containing source_pattern,target_pattern columns"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write updates (default is dry-run)"
    )
    parser.add_argument(
        "--output",
        help="Write JSON report to this file"
    )
    parser.add_argument(
        "--extensions",
        default=".md,.yml,.yaml",
        help="Comma-separated file extensions to process (default: .md,.yml,.yaml)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed changes"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root not found or not a directory: {root}")

    mappings = DEFAULT_MAPPINGS
    if args.mapping_csv:
        mappings = load_mapping_csv(Path(args.mapping_csv))

    extensions = [ext.strip() for ext in args.extensions.split(",")]
    summary = run(root=root, mappings=mappings, apply=args.apply, extensions=extensions)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")

    # Print summary
    print(json.dumps({
        "mode": summary.mode,
        "files_scanned": summary.files_scanned,
        "files_changed": summary.files_changed,
        "total_replacements": summary.total_replacements,
    }, indent=2))

    if args.verbose and summary.changes:
        print("\nChanges:")
        for change in summary.changes:
            print(f"  {change['file_path']}:")
            for r in change['replacements']:
                print(f"    {r['source_pattern']} -> {r['target_pattern']} ({r['count']}x)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
