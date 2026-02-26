#!/usr/bin/env python3
"""Fail if BRD skill versions drift from BRD template schema_version."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SKILLS = (
    "doc-brd",
    "doc-brd-audit",
    "doc-brd-validator",
    "doc-brd-reviewer",
    "doc-brd-fixer",
    "doc-brd-autopilot",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Cannot read {path}: {exc}")
        raise SystemExit(2)


def extract_md_schema_version(template_md: Path) -> str:
    text = read_text(template_md)
    match = re.search(r"schema_version:\s*\"([^\"]+)\"", text)
    if not match:
        print(f"ERROR: schema_version not found in {template_md}")
        raise SystemExit(2)
    return match.group(1)


def extract_yaml_schema_version(template_yaml: Path) -> str:
    text = read_text(template_yaml)
    match = re.search(r"^\s*schema_version:\s*\"([^\"]+)\"\s*$", text, re.MULTILINE)
    if not match:
        print(f"ERROR: metadata.schema_version not found in {template_yaml}")
        raise SystemExit(2)
    return match.group(1)


def extract_frontmatter_value(skill_file: Path, key: str) -> str | None:
    text = read_text(skill_file)
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not fm_match:
        print(f"ERROR: Frontmatter block not found in {skill_file}")
        raise SystemExit(2)

    frontmatter = fm_match.group(1)
    match = re.search(rf"^\s*{re.escape(key)}:\s*\"([^\"]+)\"\s*$", frontmatter, re.MULTILINE)
    return match.group(1) if match else None


def validate(repo_root: Path) -> int:
    template_md = repo_root / "ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md"
    template_yaml = repo_root / "ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.yaml"

    expected_md = extract_md_schema_version(template_md)
    expected_yaml = extract_yaml_schema_version(template_yaml)

    if expected_md != expected_yaml:
        print("FAIL: Template schema version mismatch between MD and YAML")
        print(f"  MD   : {expected_md}")
        print(f"  YAML : {expected_yaml}")
        return 1

    expected = expected_md
    print(f"Template schema_version: {expected}")

    failures: list[str] = []

    for skill in SKILLS:
        skill_file = repo_root / f".claude/skills/{skill}/SKILL.md"
        if not skill_file.exists():
            failures.append(f"Missing skill file: {skill_file}")
            continue

        version = extract_frontmatter_value(skill_file, "version")
        if version is None:
            failures.append(f"Missing frontmatter version in {skill_file}")
            continue

        if version != expected:
            failures.append(
                f"Version mismatch in {skill}: expected {expected}, found {version}"
            )

        policy = extract_frontmatter_value(skill_file, "versioning_policy")
        if policy is None:
            failures.append(f"Missing versioning_policy in {skill}")

    if failures:
        print("FAIL: Skill/template version drift detected")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PASS: All BRD skills match BRD template schema_version")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to repository root (default: current directory)",
    )
    args = parser.parse_args()
    return validate(Path(args.repo_root).resolve())


if __name__ == "__main__":
    sys.exit(main())
