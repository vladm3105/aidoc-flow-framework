"""Finding-check schema enforcement for the synthesizer agent.

Per LAYER-PLAYBOOKS-001 design: every finding produced by a lens MUST cite
either a playbook checklist check (e.g. "C1") or a beyond-checklist
principle ("beyond-checklist:<tag>"). Findings without a valid citation
are discarded.

Stdlib-only; no external dependencies.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

BEYOND_PREFIX = "beyond-checklist:"


def filter_findings(
    findings: Iterable[dict],
    valid_check_ids: set[str],
) -> tuple[list[dict], list[dict]]:
    """Split findings into (kept, discarded).

    Kept: finding has 'check' field that is either in `valid_check_ids` or
    begins with the beyond-checklist prefix.
    Discarded: every other finding, with a 'reason' field added:
      - 'no_check_citation': finding has no 'check' field
      - 'unknown_check': finding's check id is not in `valid_check_ids`
        and is not a beyond-checklist citation
    """
    kept: list[dict] = []
    discarded: list[dict] = []
    for finding in findings:
        check = finding.get("check")
        if check is None:
            discarded.append({**finding, "reason": "no_check_citation"})
            continue
        if check.startswith(BEYOND_PREFIX):
            kept.append(finding)
            continue
        if check in valid_check_ids:
            kept.append(finding)
            continue
        discarded.append({**finding, "reason": "unknown_check"})
    return kept, discarded


def emit_coverage(findings: Iterable[dict]) -> dict:
    """Return verdict.playbook_coverage shape: {<check_id>: <count>, ..., 'beyond_checklist': <n>}."""
    counts: Counter[str] = Counter()
    for finding in findings:
        check = finding.get("check")
        if check is None:
            continue
        if check.startswith(BEYOND_PREFIX):
            counts["beyond_checklist"] += 1
        else:
            counts[check] += 1
    return dict(counts)
