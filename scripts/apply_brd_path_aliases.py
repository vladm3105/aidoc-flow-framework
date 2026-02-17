#!/usr/bin/env python3
"""
Apply deterministic BRD path alias replacements with a safe dry-run mode.

Default behavior is dry-run. Use --apply to write changes.
"""

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path


DEFAULT_MAPPINGS = [
    ("BRD-03_security_compliance_regulatory_framework", "BRD-03_security_compliance"),
    ("BRD-03_security_compliance_regulatory", "BRD-03_security_compliance"),
    ("BRD-06_b2c_user_onboarding_kyc", "BRD-06_b2c_progressive_kyc_onboarding"),
    ("BRD-09_remittance_transaction_us_uzbekistan", "BRD-09_remittance_transaction_us_to_uzbekistan"),
    ("BRD-01_platform_architecture_technology_stack", "BRD-01_platform_architecture"),
    ("BRD-04_data_model_ledger_double_entry_accounting", "BRD-04_data_model_ledger"),
    ("BRD-25_transaction_orchestrator_agent/", "BRD-25_transaction_orchestrator_agent_payment_fsm/"),
    ("../BRD-000_GLOSSARY.md", "/docs-site/docs/BRD/BRD-000_GLOSSARY.md"),
    ("../BRD-000_index.md", "/docs-site/docs/BRD/BRD-000_index.md"),
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


def run(root: Path, mappings: list[tuple[str, str]], apply: bool) -> ReplacementSummary:
    md_files = sorted(root.rglob("*.md"))
    changes: list[FileChange] = []
    total_replacements = 0

    for file_path in md_files:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
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
        files_scanned=len(md_files),
        files_changed=len(changes),
        total_replacements=total_replacements,
        changes=[asdict(c) for c in changes],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply BRD path alias replacements")
    parser.add_argument("--root", default="docs/BRD", help="Root folder to process")
    parser.add_argument("--mapping-csv", help="Optional CSV containing source_pattern,target_pattern")
    parser.add_argument("--apply", action="store_true", help="Write updates (default is dry-run)")
    parser.add_argument("--output", help="Write JSON report to this file")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root not found or not a directory: {root}")

    mappings = DEFAULT_MAPPINGS
    if args.mapping_csv:
        mappings = load_mapping_csv(Path(args.mapping_csv))

    summary = run(root=root, mappings=mappings, apply=args.apply)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")

    print(json.dumps({
        "mode": summary.mode,
        "files_scanned": summary.files_scanned,
        "files_changed": summary.files_changed,
        "total_replacements": summary.total_replacements,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
