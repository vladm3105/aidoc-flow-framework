#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

TEMPLATE_VERSION = "1.1"

SECTIONS_MVP = [
    "Document Control",
    "Context",
    "Decision",
    "Alternatives Considered",
    "Consequences",
    "Architecture Flow",
    "Implementation Assessment",
    "Verification",
    "Traceability",
    "Related Decisions",
]

SECTIONS_FULL = [
    "Document Control",
    "Position in Development Workflow",
    "Status",
    "Context",
    "Decision",
    "Requirements Satisfied",
    "Consequences",
    "Architecture Flow",
    "Implementation Assessment",
    "Impact Analysis",
]

TRACEABILITY_TAGS = ["@brd:", "@prd:", "@ears:", "@bdd:"]


def get_profile(content: str) -> str:
    match = re.search(r"template_profile:\s*(mvp|full|enterprise|standard)", content, re.IGNORECASE)
    if not match:
        return "mvp"
    profile = match.group(1).lower()
    return "full" if profile in {"full", "enterprise", "standard"} else "mvp"


def is_ref_or_reserved(path: Path, content: str) -> bool:
    name = path.name.upper()
    if name.startswith("ADR-REF-"):
        return True
    if name.startswith("ADR-00"):
        return True
    if re.search(r"\bADR-REF\b", content):
        return True
    return False


def parse_declared_score(content: str):
    if re.search(r"SYS-Ready Score[^\n]*(N/A|NOT APPLICABLE)", content, re.IGNORECASE):
        return None, "na"

    percent_fmt = re.search(r"SYS-Ready Score[^\n]*\[PASS\]\s*(\d+)%\s*\(Target:\s*≥\d+%\)", content)
    if percent_fmt:
        return int(percent_fmt.group(1)), "ok"

    frac_fmt = re.search(r"SYS-Ready Score[^\n]*\b(\d{1,3})\s*/\s*100\b", content, re.IGNORECASE)
    if frac_fmt:
        return int(frac_fmt.group(1)), "ok"

    any_match = re.search(r"SYS-Ready Score[^\n]*?(\d{1,3})%", content)
    if any_match:
        return int(any_match.group(1)), "bad_format"

    return None, "missing"


def compute_score(content: str, profile: str) -> int:
    score = 0

    required = SECTIONS_MVP if profile == "mvp" else SECTIONS_FULL
    section_hits = sum(
        1
        for section in required
        if re.search(rf"^##\s+(\d+\.\s+)?{re.escape(section)}", content, re.MULTILINE | re.IGNORECASE)
    )
    score += round(35 * (section_hits / len(required)))

    has_h1 = bool(re.search(r"^#\s+ADR-\d{2,}(\.\d{2})?:", content, re.MULTILINE))
    score += 10 if has_h1 else 0

    traceability_hits = sum(1 for tag in TRACEABILITY_TAGS if tag in content)
    score += round(25 * (traceability_hits / len(TRACEABILITY_TAGS)))

    has_diagram = "```mermaid" in content
    has_diagram_tag = bool(re.search(r"@diagram:\s*c4-l3", content, re.IGNORECASE))
    has_sequence_tag = bool(re.search(r"@diagram:\s*sequence", content, re.IGNORECASE))
    score += 15 if has_diagram else 0
    score += 10 if (has_diagram_tag and has_sequence_tag) else 0

    has_verification = bool(re.search(r"^##\s+(\d+\.\s+)?Verification", content, re.MULTILINE | re.IGNORECASE))
    has_checklist = bool(re.search(r"^-\s*\[\s*[xX]?\s*\]", content, re.MULTILINE))
    score += 5 if (has_verification and has_checklist) else 0

    return min(score, 100)


def evaluate_file(path: Path) -> int:
    content = path.read_text(encoding="utf-8")

    if is_ref_or_reserved(path, content):
        print(f"[SKIP] {path.name} | template v{TEMPLATE_VERSION} | reserved/ref ADR score N/A")
        return 0

    profile = get_profile(content)
    min_score = 70 if profile == "mvp" else 90

    declared, declared_state = parse_declared_score(content)
    computed = compute_score(content, profile)

    if declared_state == "na":
        print(f"[SKIP] {path.name} | template v{TEMPLATE_VERSION} | declared SYS-Ready Score N/A")
        return 0

    if declared_state == "missing":
        print(f"[FAIL] {path.name} | template v{TEMPLATE_VERSION} | missing SYS-Ready Score")
        return 1

    if declared_state == "bad_format":
        print(f"[FAIL] {path.name} | template v{TEMPLATE_VERSION} | SYS-Ready Score format invalid")
        return 1

    status = "PASS" if (computed >= min_score and declared >= min_score) else "FAIL"
    print(
        f"[{status}] {path.name} | template v{TEMPLATE_VERSION} | "
        f"profile={profile} min={min_score}% declared={declared}% computed={computed}%"
    )
    return 0 if status == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute/validate ADR SYS-Ready score from ADR-MVP template rules")
    parser.add_argument("path", type=Path, help="ADR file or directory")
    args = parser.parse_args()

    path = args.path
    if not path.exists():
        print(f"[FAIL] Path not found: {path}")
        return 2

    files = [path] if path.is_file() else sorted(path.glob("ADR-*.md"))
    files = [
        f for f in files
        if "TEMPLATE" not in f.name.upper()
        and ".A_audit_report" not in f.name
        and ".R_review_report" not in f.name
        and ".F_fix_report" not in f.name
        and ".V_validation_report" not in f.name
    ]

    failures = 0
    for file_path in files:
        failures += evaluate_file(file_path)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
