from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class ReducedFinding:
    finding_id: str
    action_id: str
    priority: str
    category: str
    personas: list[str]
    message: str
    target_layer: str
    recommended_action: str
    provenance: list[dict[str, str]]
    content_hash: str
    check: str = ""  # playbook check citation (HERMES-PARITY-PHASE-2); preserved verbatim


def _stable_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _normalize_record(record: dict[str, object]) -> dict[str, str]:
    return {
        "priority": str(record.get("priority", "P2")),
        "category": str(record.get("category", "general")),
        "persona": str(record.get("persona", "unknown")),
        "message": str(record.get("message", "")).strip(),
        "target_layer": str(record.get("target_layer", "spec")),
        "recommended_action": str(record.get("recommended_action", "")).strip(),
        "branch_id": str(record.get("branch_id", "")),
        "parse_status": str(record.get("parse_status", "unknown")),
        "check": str(record.get("check", "")).strip(),
    }


def _identity_hash(normalized: dict[str, str]) -> str:
    key = "|".join(
        [
            normalized["message"],
            normalized["target_layer"],
            normalized["recommended_action"],
        ]
    )
    return _stable_hash(key)


_PRIORITY_ORDER: dict[str, int] = {
    "P0": 0,
    "P1": 1,
    "P2": 2,
    "P3": 3,
}


def _is_better_candidate(current: dict[str, str], candidate: dict[str, str]) -> bool:
    current_rank = _PRIORITY_ORDER.get(current.get("priority", "P3"), 9)
    candidate_rank = _PRIORITY_ORDER.get(candidate.get("priority", "P3"), 9)
    if candidate_rank != current_rank:
        return candidate_rank < current_rank

    current_category = current.get("category", "")
    candidate_category = candidate.get("category", "")
    if candidate_category != current_category:
        return candidate_category < current_category

    return candidate.get("branch_id", "") < current.get("branch_id", "")


def reduce_persona_findings(records: list[dict[str, object]]) -> list[ReducedFinding]:
    grouped: dict[str, dict[str, object]] = {}
    for rec in records:
        n = _normalize_record(rec)
        content_hash = _identity_hash(n)
        if content_hash not in grouped:
            grouped[content_hash] = {
                "best": n,
                "personas": {n["persona"]},
                "message": n["message"],
                "target_layer": n["target_layer"],
                "recommended_action": n["recommended_action"],
                "provenance": [
                    {
                        "branch_id": n["branch_id"],
                        "persona": n["persona"],
                        "priority": n["priority"],
                        "category": n["category"],
                        "parse_status": n["parse_status"],
                    }
                ],
                "content_hash": content_hash,
            }
        else:
            row = grouped[content_hash]
            row["personas"].add(n["persona"])
            row["provenance"].append(
                {
                    "branch_id": n["branch_id"],
                    "persona": n["persona"],
                    "priority": n["priority"],
                    "category": n["category"],
                    "parse_status": n["parse_status"],
                }
            )
            best = row["best"]
            if isinstance(best, dict) and _is_better_candidate(best, n):
                row["best"] = n

    reduced: list[ReducedFinding] = []
    for content_hash in sorted(grouped.keys()):
        row = grouped[content_hash]
        best = row["best"]
        assert isinstance(best, dict)
        provenance = sorted(
            [p for p in row["provenance"] if isinstance(p, dict)],
            key=lambda item: (
                str(item.get("branch_id", "")),
                str(item.get("persona", "")),
            ),
        )
        finding_suffix = content_hash[:10]
        reduced.append(
            ReducedFinding(
                finding_id=f"{best['priority']}-{finding_suffix}",
                action_id=f"ACT-{content_hash[:12]}",
                priority=str(best["priority"]),
                category=str(best["category"]),
                personas=sorted(list(row["personas"])),
                message=str(row["message"]),
                target_layer=str(row["target_layer"]),
                recommended_action=str(row["recommended_action"]),
                provenance=[
                    {
                        "branch_id": str(item.get("branch_id", "")),
                        "persona": str(item.get("persona", "")),
                        "priority": str(item.get("priority", "P2")),
                        "category": str(item.get("category", "general")),
                        "parse_status": str(item.get("parse_status", "unknown")),
                    }
                    for item in provenance
                ],
                content_hash=str(row["content_hash"]),
                check=str(best.get("check", "")),
            )
        )
    return reduced
