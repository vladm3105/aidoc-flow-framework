#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

TEMPLATE_VERSION = "2.0"

SCENARIO_RE = re.compile(r"^\s*(Scenario:|Scenario Outline:)\s+", re.MULTILINE)
TAG_TYPE_RE = re.compile(r"@scenario-type:(success|optional|recovery|parameterized|error)")
TAG_PRIORITY_RE = re.compile(r"@(p0-critical|p1-high|p2-medium|p3-low)")
TAG_ID_RE = re.compile(r"@scenario-id:BDD\.\d{2,9}\.14\.\d{2,9}")


def get_profile(content: str) -> str:
    match = re.search(r"template_profile:\s*(mvp|full|enterprise|standard)", content, re.IGNORECASE)
    if not match:
        return "mvp"
    profile = match.group(1).lower()
    return "full" if profile in {"full", "enterprise", "standard"} else "mvp"


def parse_declared_score(content: str):
    fmt_match = re.search(r"ADR-Ready Score[^\n]*\[PASS\]\s*(\d+)%\s*\(Target:\s*≥\d+%\)", content)
    if fmt_match:
        return int(fmt_match.group(1)), "ok"

    any_match = re.search(r"ADR-Ready Score[^\n]*?(\d+)%", content)
    if any_match:
        return int(any_match.group(1)), "bad_format"

    return None, "missing"


def extract_scenarios(content: str):
    lines = content.splitlines()
    scenarios = []
    current_tags = []
    current = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@"):
            current_tags.extend(stripped.split())
            continue

        if stripped.startswith("Scenario:") or stripped.startswith("Scenario Outline:"):
            if current:
                scenarios.append(current)
            current = {
                "name": stripped,
                "is_outline": stripped.startswith("Scenario Outline:"),
                "tags": current_tags.copy(),
                "has_given": False,
                "has_when": False,
                "has_then": False,
                "has_examples": False,
            }
            current_tags = []
            continue

        if current:
            if stripped.startswith("Given "):
                current["has_given"] = True
            elif stripped.startswith("When "):
                current["has_when"] = True
            elif stripped.startswith("Then "):
                current["has_then"] = True
            elif stripped.startswith("Examples:"):
                current["has_examples"] = True

    if current:
        scenarios.append(current)
    return scenarios


def compute_score(content: str) -> int:
    score = 0

    feature_ok = all(x in content for x in ["Feature:", "As a ", "I want ", "So that "])
    score += 20 if feature_ok else 0

    trace_ok = all(tag in content for tag in ["@brd:", "@prd:", "@ears:"])
    score += 20 if trace_ok else 0

    scenarios = extract_scenarios(content)
    if scenarios:
        gwt_ok = sum(1 for s in scenarios if s["has_when"] and s["has_then"]) / len(scenarios)
        score += round(20 * gwt_ok)

        tags_ok = 0
        for s in scenarios:
            tags = " ".join(s["tags"])
            has_all = bool(TAG_TYPE_RE.search(tags) and TAG_PRIORITY_RE.search(tags) and TAG_ID_RE.search(tags))
            if has_all:
                tags_ok += 1
        score += round(30 * (tags_ok / len(scenarios)))

        outline_total = sum(1 for s in scenarios if s["is_outline"])
        if outline_total == 0:
            score += 10
        else:
            with_examples = sum(1 for s in scenarios if s["is_outline"] and s["has_examples"])
            score += round(10 * (with_examples / outline_total))

    return min(score, 100)


def evaluate_file(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    profile = get_profile(content)
    min_score = 70 if profile == "mvp" else 90

    declared, declared_state = parse_declared_score(content)
    computed = compute_score(content)

    if declared_state == "missing":
        print(f"[FAIL] {path.name} | template v{TEMPLATE_VERSION} | missing ADR-Ready Score")
        return 1

    if declared_state == "bad_format":
        print(f"[FAIL] {path.name} | template v{TEMPLATE_VERSION} | ADR-Ready Score format invalid")
        return 1

    status = "PASS" if (computed >= min_score and declared >= min_score) else "FAIL"
    print(
        f"[{status}] {path.name} | template v{TEMPLATE_VERSION} | "
        f"profile={profile} min={min_score}% declared={declared}% computed={computed}%"
    )
    return 0 if status == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute/validate BDD ADR-Ready score from BDD-MVP template rules")
    parser.add_argument("path", type=Path, help="BDD file or directory")
    args = parser.parse_args()

    path = args.path
    if not path.exists():
        print(f"[FAIL] Path not found: {path}")
        return 2

    files = [path] if path.is_file() else sorted(path.glob("**/*.feature"))
    files = [f for f in files if "TEMPLATE" not in f.name.upper() and not re.match(r"^BDD-00[_.]", f.name)]

    failures = 0
    for file_path in files:
        failures += evaluate_file(file_path)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
