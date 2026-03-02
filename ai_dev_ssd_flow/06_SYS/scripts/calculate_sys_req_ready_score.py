#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

TEMPLATE_VERSION = "2.1"

SECTIONS_MVP = [
    "Document Control",
    "Executive Summary",
    "Scope",
    "Functional Requirements",
    "Quality Attributes",
    "Interface Specifications",
    "Data Management Requirements",
    "Testing and Validation Requirements",
    "Deployment and Operations Requirements",
    "Compliance and Regulatory Requirements",
    "Acceptance Criteria",
    "Risk Assessment",
    "Traceability",
]

SECTIONS_FULL = [
    "Document Control",
    "Executive Summary",
    "Scope",
    "Functional Requirements",
    "Quality Attributes",
    "Interface Specifications",
    "Data Management Requirements",
    "Testing and Validation Requirements",
    "Deployment and Operations Requirements",
    "Compliance and Regulatory Requirements",
    "Acceptance Criteria",
    "Risk Assessment",
    "Traceability",
    "Implementation Notes",
    "Change History",
]

TRACEABILITY_TAGS = ["@brd:", "@prd:", "@ears:", "@bdd:", "@adr:"]


def get_profile(content: str) -> str:
    match = re.search(r"template_profile:\s*(mvp|full|enterprise|standard)", content, re.IGNORECASE)
    if not match:
        return "mvp"
    profile = match.group(1).lower()
    return "full" if profile in {"full", "enterprise", "standard"} else "mvp"


def is_reserved_or_template(path: Path) -> bool:
    name = path.name.upper()
    if name.startswith("SYS-00"):
        return True
    if "TEMPLATE" in name:
        return True
    return False


def parse_declared_score(content: str):
    if re.search(r"REQ-Ready Score[^\n]*(N/A|NOT APPLICABLE)", content, re.IGNORECASE):
        return None, "na"

    strict_fmt = re.search(r"REQ-Ready Score[^\n]*\[PASS\]\s*(\d+)%\s*\(Target:\s*≥\d+%\)", content)
    if strict_fmt:
        return int(strict_fmt.group(1)), "ok"

    any_match = re.search(r"REQ-Ready Score[^\n]*?(\d+)%", content)
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

    has_h1 = bool(re.search(r"^#\s+SYS-\d{2,}(\.\d+)?:", content, re.MULTILINE))
    score += 10 if has_h1 else 0

    traceability_hits = sum(1 for tag in TRACEABILITY_TAGS if tag in content)
    score += round(20 * (traceability_hits / len(TRACEABILITY_TAGS)))

    has_diagram_contract = bool(re.search(r"^###\s+3\.4\s+System Diagram Contract", content, re.MULTILINE))
    has_required_bridge = all(
        token in content
        for token in ["downstream_c4_l4_owner", "required_sequence_paths", "trust_boundaries"]
    )
    score += 15 if (has_diagram_contract and has_required_bridge) else 0

    has_external_dependencies = bool(re.search(r"^###\s+4\.5\s+External Dependencies", content, re.MULTILINE))
    has_dependency_table = bool(re.search(r"\|\s*Dependency\s*\|\s*Type\s*\|\s*Fallback Strategy\s*\|", content))
    score += 10 if (has_external_dependencies and has_dependency_table) else 0

    has_acceptance_checklist = bool(re.search(r"^-\s*\[\s*[xX]?\s*\]", content, re.MULTILINE))
    score += 10 if has_acceptance_checklist else 0

    return min(score, 100)


def evaluate_file(path: Path) -> int:
    if is_reserved_or_template(path):
        print(f"[SKIP] {path.name} | template v{TEMPLATE_VERSION} | reserved/template SYS score N/A")
        return 0

    content = path.read_text(encoding="utf-8")
    profile = get_profile(content)
    min_score = 85 if profile == "mvp" else 90

    declared, declared_state = parse_declared_score(content)
    computed = compute_score(content, profile)

    if declared_state == "na":
        print(f"[SKIP] {path.name} | template v{TEMPLATE_VERSION} | declared REQ-Ready Score N/A")
        return 0

    if declared_state == "missing":
        print(f"[FAIL] {path.name} | template v{TEMPLATE_VERSION} | missing REQ-Ready Score")
        return 1

    if declared_state == "bad_format":
        print(f"[FAIL] {path.name} | template v{TEMPLATE_VERSION} | REQ-Ready Score format invalid")
        return 1

    status = "PASS" if (computed >= min_score and declared >= min_score) else "FAIL"
    print(
        f"[{status}] {path.name} | template v{TEMPLATE_VERSION} | "
        f"profile={profile} min={min_score}% declared={declared}% computed={computed}%"
    )
    return 0 if status == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute/validate SYS REQ-ready score from SYS-MVP template rules")
    parser.add_argument("path", type=Path, help="SYS file or directory")
    args = parser.parse_args()

    path = args.path
    if not path.exists():
        print(f"[FAIL] Path not found: {path}")
        return 2

    files = [path] if path.is_file() else sorted(path.glob("SYS-*.md"))
    files = [
        f
        for f in files
        if ".A_audit_report" not in f.name
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
