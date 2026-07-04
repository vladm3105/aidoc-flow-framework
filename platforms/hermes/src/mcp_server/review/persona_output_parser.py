from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256

_REQUIRED_FINDING_FIELDS: tuple[str, ...] = (
    "priority",
    "category",
    "message",
    "recommended_action",
    "target_layer",
)


def _normalize_priority(value: object) -> str:
    priority = str(value or "P2").upper().strip()
    if priority in {"P0", "P1", "P2", "P3"}:
        return priority
    return "P2"


def _coerce_findings(raw: object) -> list[dict[str, str]]:
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        return []

    findings: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        # `recommendation` is the framework field name; `recommended_action` the engine's.
        recommended_action = str(
            item.get("recommended_action") or item.get("recommendation") or ""
        ).strip()
        finding = {
            "priority": _normalize_priority(item.get("priority")),
            "category": str(item.get("category", "general")).strip() or "general",
            "message": str(item.get("message", "")).strip(),
            "recommended_action": recommended_action,
            "target_layer": str(item.get("target_layer", "spec")).strip() or "spec",
            # Framework persona-output fields (REVIEW_TEAM.md):
            "location": str(item.get("location", "")).strip(),
            "id": str(item.get("id", "")).strip(),
        }
        if not finding["message"]:
            continue
        # Playbook check citation (HERMES-PARITY-PHASE-2). Included ONLY when the lens
        # actually cited a check — an absent key (not "") is how the citation floor
        # (`finding_filter`, `emit_coverage`) recognises an uncited finding.
        check_val = str(item.get("check", "")).strip()
        if check_val:
            finding["check"] = check_val
        findings.append(finding)
    return findings


def _extract_json_block(text: str) -> str | None:
    fenced_match = re.search(
        r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.IGNORECASE | re.DOTALL
    )
    if fenced_match:
        return fenced_match.group(1)

    start_obj = text.find("{")
    end_obj = text.rfind("}")
    if start_obj >= 0 and end_obj > start_obj:
        return text[start_obj : end_obj + 1]

    start_arr = text.find("[")
    end_arr = text.rfind("]")
    if start_arr >= 0 and end_arr > start_arr:
        return text[start_arr : end_arr + 1]
    return None


def _coerce_lens_score(payload: object) -> float | None:
    """Extract the persona's top-level ``lens_score`` (0-100) if present."""
    if not isinstance(payload, dict) or "lens_score" not in payload:
        return None
    try:
        value = float(payload["lens_score"])
    except (TypeError, ValueError):
        return None
    return max(0.0, min(100.0, value))


def _stable_finding_id(persona: str, location: str, message: str) -> str:
    return sha256(f"{persona}|{location}|{message}".encode()).hexdigest()[:8]


@dataclass(frozen=True)
class PersonaParseResult:
    findings: list[dict[str, str]]
    parse_status: str
    lens_score: float | None = None


def parse_persona_output(
    *,
    output_text: str,
    persona: str,
    branch_id: str,
    attempt: int,
    default_layer: str,
) -> PersonaParseResult:
    text = output_text.strip()

    parse_order: list[tuple[str, str | None]] = [
        ("strict_json", text),
        ("structured_block", _extract_json_block(text)),
    ]

    for parse_status, candidate in parse_order:
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        lens_score = _coerce_lens_score(payload)
        if isinstance(payload, dict):
            candidate_findings = payload.get("findings", payload)
        else:
            candidate_findings = payload

        findings = _coerce_findings(candidate_findings)
        if findings:
            normalized: list[dict[str, str]] = []
            for finding in findings:
                location = finding.get("location", "")
                finding_id = finding.get("id") or _stable_finding_id(
                    persona, location, finding.get("message", "")
                )
                normalized.append(
                    {
                        **finding,
                        "target_layer": finding.get("target_layer", default_layer) or default_layer,
                        "location": location,
                        "id": finding_id,
                        "persona": persona,
                        "branch_id": branch_id,
                        "attempt": str(attempt),
                        "parse_status": parse_status,
                    }
                )
            return PersonaParseResult(
                findings=normalized, parse_status=parse_status, lens_score=lens_score
            )

    fallback_message = "Branch output was not machine-parseable JSON; fallback finding emitted"
    fallback = {
        "priority": "P1",
        "category": "parser",
        "message": fallback_message,
        "recommended_action": "Return strict JSON with required finding fields for persona branch outputs.",
        "target_layer": default_layer,
        "location": "",
        "id": _stable_finding_id(persona, "", fallback_message),
        "persona": persona,
        "branch_id": branch_id,
        "attempt": str(attempt),
        "parse_status": "fallback",
    }
    return PersonaParseResult(findings=[fallback], parse_status="fallback", lens_score=None)
