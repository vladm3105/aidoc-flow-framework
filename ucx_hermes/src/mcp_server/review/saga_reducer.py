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
    provenance: dict[str, str]
    content_hash: str


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
    }


def _identity_hash(normalized: dict[str, str]) -> str:
    key = "|".join(
        [
            normalized["priority"],
            normalized["category"],
            normalized["message"],
            normalized["target_layer"],
            normalized["recommended_action"],
        ]
    )
    return _stable_hash(key)


def reduce_persona_findings(records: list[dict[str, object]]) -> list[ReducedFinding]:
    grouped: dict[str, dict[str, object]] = {}
    for rec in records:
        n = _normalize_record(rec)
        content_hash = _identity_hash(n)
        if content_hash not in grouped:
            grouped[content_hash] = {
                "priority": n["priority"],
                "category": n["category"],
                "personas": {n["persona"]},
                "message": n["message"],
                "target_layer": n["target_layer"],
                "recommended_action": n["recommended_action"],
                "provenance": {
                    "branch_id": n["branch_id"],
                    "persona": n["persona"],
                },
                "content_hash": content_hash,
            }
        else:
            grouped[content_hash]["personas"].add(n["persona"])

    reduced: list[ReducedFinding] = []
    for content_hash in sorted(grouped.keys()):
        row = grouped[content_hash]
        finding_suffix = content_hash[:10]
        reduced.append(
            ReducedFinding(
                finding_id=f"{row['priority']}-{finding_suffix}",
                action_id=f"ACT-{content_hash[:12]}",
                priority=str(row["priority"]),
                category=str(row["category"]),
                personas=sorted(list(row["personas"])),
                message=str(row["message"]),
                target_layer=str(row["target_layer"]),
                recommended_action=str(row["recommended_action"]),
                provenance={
                    "branch_id": str(row["provenance"]["branch_id"]),
                    "persona": str(row["provenance"]["persona"]),
                },
                content_hash=str(row["content_hash"]),
            )
        )
    return reduced
