#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

TEMPLATE_VERSION = "2.0"

SECTIONS_MVP = ["Document Control", "Requirements Logic"]
SECTIONS_FULL = ["Document Control", "Purpose", "Traceability", "Requirements Logic"]


def get_profile(content: str) -> str:
    match = re.search(r"template_profile:\s*(mvp|full|enterprise|standard)", content, re.IGNORECASE)
    if not match:
        return "mvp"
    profile = match.group(1).lower()
    return "full" if profile in {"full", "enterprise", "standard"} else "mvp"


def parse_declared_score(content: str):
    if re.search(r"(BDD-Ready Score|ADR-Ready Score).*N/A", content, re.IGNORECASE):
        return None, "na"

    fmt_match = re.search(r"(BDD-Ready Score|ADR-Ready Score).*\[PASS\]\s*(\d+)%\s*\(Target:\s*≥\d+%\)", content)
    if fmt_match:
        return int(fmt_match.group(2)), "ok"

    any_match = re.search(r"(BDD-Ready Score|ADR-Ready Score)[^\n]*?(\d+)%", content)
    if any_match:
        return int(any_match.group(2)), "bad_format"

    return None, "missing"


def compute_score(content: str, profile: str) -> int:
    score = 0

    required = SECTIONS_MVP if profile == "mvp" else SECTIONS_FULL
    section_hits = sum(1 for section in required if re.search(rf"^##\s+(\d+\.\s+)?{re.escape(section)}", content, re.MULTILINE | re.IGNORECASE))
    score += round(30 * (section_hits / len(required)))

    has_syntax = bool(re.search(r"\b(WHEN|WHILE|IF|THE)\b.+\bTHE\b.+\bSHALL\b", content, re.IGNORECASE))
    score += 30 if has_syntax else 0

    has_brd = bool(re.search(r"@brd:\s*BRD\.\d{2,}", content))
    has_prd = bool(re.search(r"@prd:\s*PRD\.\d{2,}", content))
    score += 20 if (has_brd and has_prd) else 0

    has_within_measure = bool(re.search(r"WITHIN[^.]*?(\d+|@threshold:)", content, re.IGNORECASE))
    score += 20 if has_within_measure else 0

    return min(score, 100)


def evaluate_file(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    profile = get_profile(content)
    min_score = 70 if profile == "mvp" else 90

    declared, declared_state = parse_declared_score(content)
    computed = compute_score(content, profile)

    if declared_state == "na":
        print(f"[SKIP] {path.name} | template v{TEMPLATE_VERSION} | reserved score N/A")
        return 0

    if declared_state == "missing":
        print(f"[FAIL] {path.name} | template v{TEMPLATE_VERSION} | missing BDD-Ready Score")
        return 1

    if declared_state == "bad_format":
        print(f"[FAIL] {path.name} | template v{TEMPLATE_VERSION} | BDD-Ready Score format invalid")
        return 1

    status = "PASS" if (computed >= min_score and declared >= min_score) else "FAIL"
    print(
        f"[{status}] {path.name} | template v{TEMPLATE_VERSION} | "
        f"profile={profile} min={min_score}% declared={declared}% computed={computed}%"
    )
    return 0 if status == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute/validate EARS BDD-Ready score from EARS-MVP template rules")
    parser.add_argument("path", type=Path, help="EARS file or directory")
    args = parser.parse_args()

    path = args.path
    if not path.exists():
        print(f"[FAIL] Path not found: {path}")
        return 2

    files = [path] if path.is_file() else sorted(path.glob("EARS-*.md"))
    files = [f for f in files if f.name != "EARS-00_index.md" and ".A_audit_report" not in f.name and ".R_review_report" not in f.name and ".F_fix_report" not in f.name and ".V_validation_report" not in f.name]

    failures = 0
    for file_path in files:
        failures += evaluate_file(file_path)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
