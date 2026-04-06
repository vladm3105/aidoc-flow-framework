"""BRD-specific cross-section validation rules.

Runs only when ``doc_type == "brd"``.  Called from ``runner.py`` with
parsed YAML data (or raw markdown content for the MD fallback).

Rules implemented
-----------------
BRD-XS-001  ADT Decision Propagation
BRD-XS-002  Phase Alignment
BRD-XS-004  Entity Consistency
BRD-XS-005  Currency Scope Consistency (conditional)
"""

from __future__ import annotations

import json
import re


# ── Helpers ──────────────────────────────────────────────────────────

_GENERIC_WORDS: frozenset[str] = frozenset({
    "the", "and", "for", "but", "with", "from", "that", "this",
    "are", "was", "not", "has", "had", "its", "can", "may", "will",
    "all", "any", "our", "use", "via", "per", "etc", "yet",
})

_KNOWN_CURRENCIES: set[str] = {
    "USD", "MXN", "UZS", "USDC", "EUR", "GBP", "BRL", "COP",
    "ARS", "PEN", "CLP",
}

_CURRENCY_KEYWORDS: tuple[str, ...] = (
    "currency", "precision", "rounding", "USD", "MXN", "USDC",
)


def _serialize(section: object) -> str:
    """Serialize an arbitrary section value to a search-friendly string."""
    return json.dumps(section, default=str)


# ── BRD-XS-001: ADT Decision Propagation ────────────────────────────

def _check_adt_propagation(
    yaml_data: dict[str, object],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    adr_topics = yaml_data.get("adr_topics", {})
    if not isinstance(adr_topics, dict):
        passes.append("BRD-XS-001: adr_topics section absent (skipped)")
        return

    topics: list[object] = adr_topics.get("topics", [])  # type: ignore[assignment]
    if not isinstance(topics, list) or not topics:
        passes.append("BRD-XS-001: No ADT topics found (skipped)")
        return

    impl_serialized = _serialize(
        yaml_data.get("implementation_approach", {}),
    ).lower()
    cost_serialized = _serialize(
        yaml_data.get("cost_benefit", {}),
    ).lower()

    propagated_count = 0

    for topic in topics:
        if not isinstance(topic, dict):
            continue

        topic_title: str = str(topic.get("title", topic.get("topic", "unknown")))
        alternatives: list[object] = topic.get("alternatives", [])  # type: ignore[assignment]
        if not isinstance(alternatives, list):
            continue

        # Find the selected alternative.
        selected_name: str | None = None
        for alt in alternatives:
            if not isinstance(alt, dict):
                continue
            rationale = str(alt.get("rationale", ""))
            if rationale.strip().lower().startswith("selected"):
                selected_name = str(alt.get("option", ""))
                break

        if not selected_name:
            continue

        missing_sections: list[str] = []
        if selected_name.lower() not in impl_serialized:
            missing_sections.append("implementation_approach")
        if selected_name.lower() not in cost_serialized:
            missing_sections.append("cost_benefit")

        if missing_sections:
            for section_name in missing_sections:
                warnings.append(
                    f"BRD-XS-001: ADT '{topic_title}' selected "
                    f"'{selected_name}' not found in {section_name}"
                )
        else:
            propagated_count += 1

    if propagated_count > 0:
        passes.append(
            f"BRD-XS-001: {propagated_count} ADT decision(s) propagated "
            f"to implementation_approach and cost_benefit"
        )


# ── BRD-XS-002: Phase Alignment ─────────────────────────────────────

def _check_phase_alignment(
    yaml_data: dict[str, object],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    scope_phases_raw = (
        yaml_data
        .get("project_scope", {})  # type: ignore[union-attr]
    )
    if isinstance(scope_phases_raw, dict):
        scope_phases_raw = (
            scope_phases_raw
            .get("phasing", {})
        )
    if isinstance(scope_phases_raw, dict):
        scope_phases_raw = scope_phases_raw.get("phases", [])
    if not isinstance(scope_phases_raw, list):
        scope_phases_raw = []

    impl_phases_raw = (
        yaml_data
        .get("implementation_approach", {})  # type: ignore[union-attr]
    )
    if isinstance(impl_phases_raw, dict):
        impl_phases_raw = impl_phases_raw.get("phases", {})
    if isinstance(impl_phases_raw, dict):
        impl_phases_raw = impl_phases_raw.get("items", [])
    if not isinstance(impl_phases_raw, list):
        impl_phases_raw = []

    def _normalize_phase(phase_str: str) -> str:
        """Normalize phase names for comparison.

        Extracts the 'Phase N' prefix so that 'Phase 1: Core Ledger' and
        'Phase 1' are treated as the same phase.
        """
        m = re.match(r"(Phase\s+\d+)", phase_str, re.IGNORECASE)
        return m.group(1) if m else phase_str

    scope_phase_ids: list[str] = []
    for item in scope_phases_raw:
        if isinstance(item, dict) and "phase" in item:
            scope_phase_ids.append(str(item["phase"]))

    impl_phase_ids: list[str] = []
    for item in impl_phases_raw:
        if isinstance(item, dict) and "phase" in item:
            impl_phase_ids.append(str(item["phase"]))

    if not scope_phase_ids and not impl_phase_ids:
        passes.append("BRD-XS-002: Phase section not present (skipped)")
        return

    # Compare counts first (using raw lists)
    if len(scope_phase_ids) != len(impl_phase_ids):
        errors.append(
            f"BRD-XS-002: Phase count mismatch — scope has "
            f"{len(scope_phase_ids)}, implementation has {len(impl_phase_ids)}"
        )
        return

    # Compare normalized phase identifiers
    scope_normalized = {_normalize_phase(p) for p in scope_phase_ids}
    impl_normalized = {_normalize_phase(p) for p in impl_phase_ids}

    if scope_normalized == impl_normalized:
        passes.append(
            f"BRD-XS-002: {len(scope_phase_ids)} scope phase(s) aligned "
            f"with implementation phases"
        )
        return

    missing_from_impl = scope_normalized - impl_normalized
    extra_in_impl = impl_normalized - scope_normalized

    if missing_from_impl:
        errors.append(
            f"BRD-XS-002: Phases in scope but missing from "
            f"implementation: {sorted(missing_from_impl)}"
        )
    if extra_in_impl:
        errors.append(
            f"BRD-XS-002: Phases in implementation but missing from "
            f"scope: {sorted(extra_in_impl)}"
        )
    if len(scope_phase_ids) != len(impl_phase_ids):
        errors.append(
            f"BRD-XS-002: Phase count mismatch — scope has "
            f"{len(scope_phase_ids)}, implementation has "
            f"{len(impl_phase_ids)}"
        )


# ── BRD-XS-004: Entity Consistency ──────────────────────────────────

def _extract_stakeholder_entities(yaml_data: dict[str, object]) -> list[str]:
    """Extract organizational entity names from the top-level stakeholders section.

    Extracts partner/vendor names from ``name`` fields whose ``role`` indicates
    an external or partner relationship.  Individual person names (CEO, CTO)
    are not expected to appear in functional requirements, so they are excluded.
    """
    stakeholders = yaml_data.get("stakeholders", {})
    if not isinstance(stakeholders, dict):
        return []

    _PARTNER_ROLE_KEYWORDS = ("partner", "vendor", "provider", "supplier", "external")

    entities: list[str] = []
    for group_key in ("decision_makers", "key_contributors"):
        group: list[object] = stakeholders.get(group_key, [])  # type: ignore[assignment]
        if not isinstance(group, list):
            continue
        for entry in group:
            if not isinstance(entry, dict):
                continue
            role = str(entry.get("role", "")).lower()
            # Only extract names from partner/vendor roles.
            if not any(kw in role for kw in _PARTNER_ROLE_KEYWORDS):
                continue
            name_val = entry.get("name", "")
            if isinstance(name_val, str):
                for part in re.split(r"[,/]", name_val):
                    candidate = part.strip()
                    if (
                        len(candidate) >= 3
                        and not candidate.islower()
                        and candidate.lower() not in _GENERIC_WORDS
                    ):
                        entities.append(candidate)
    return entities


def _extract_problem_entities(yaml_data: dict[str, object]) -> list[str]:
    """Extract organization/product names from business_objectives.problem_statement.

    Scans ``current_workarounds`` for parenthesized entity names (e.g. vendor
    names).  Free-text audience descriptions in ``affected_stakeholders`` are
    excluded — they describe user segments, not entities that should appear in
    functional requirements.
    """
    biz_obj = yaml_data.get("business_objectives", {})
    if not isinstance(biz_obj, dict):
        return []

    problem_stmt = biz_obj.get("problem_statement", {})
    if not isinstance(problem_stmt, dict):
        return []

    entities: list[str] = []
    # Extract from current_workarounds — more likely to mention vendor names.
    workarounds: list[object] = problem_stmt.get("current_workarounds", [])  # type: ignore[assignment]
    if isinstance(workarounds, list):
        for item in workarounds:
            text = str(item) if item else ""
            for match in re.findall(r"\(([^)]+)\)", text):
                for part in re.split(r"[,/]", match):
                    candidate = part.strip()
                    if (
                        len(candidate) >= 3
                        and not candidate.islower()
                        and candidate.lower() not in _GENERIC_WORDS
                        # Skip numeric descriptions like "5-8% fees".
                        and not re.match(r"^[\d$%~<>.\-\s]+", candidate)
                    ):
                        entities.append(candidate)
    return entities


def _check_entity_consistency(
    yaml_data: dict[str, object],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    entities = _extract_stakeholder_entities(yaml_data) + _extract_problem_entities(yaml_data)

    if not entities:
        passes.append("BRD-XS-004: No entities extracted (skipped)")
        return

    # Build search corpus from downstream sections.
    corpus_parts: list[str] = []
    for key in ("functional_requirements", "introduction", "project_scope"):
        section = yaml_data.get(key, {})
        corpus_parts.append(_serialize(section).lower())
    corpus = " ".join(corpus_parts)

    missing: list[str] = []
    for entity in entities:
        if entity.lower() not in corpus:
            missing.append(entity)

    if missing:
        for name in missing:
            warnings.append(
                f"BRD-XS-004: Entity '{name}' from stakeholders/"
                f"business_objectives not found in "
                f"functional_requirements/introduction/project_scope"
            )
    else:
        passes.append(
            f"BRD-XS-004: All {len(entities)} entity reference(s) "
            f"found in downstream sections"
        )


# ── BRD-XS-005: Currency Scope Consistency (conditional) ─────────────

def _check_currency_consistency(
    yaml_data: dict[str, object],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    # mandatory_conditions can be top-level or nested under project_scope
    mandatory = yaml_data.get("mandatory_conditions")
    if mandatory is None:
        scope = yaml_data.get("project_scope")
        if isinstance(scope, dict):
            mandatory = scope.get("mandatory_conditions")
    if mandatory is None:
        passes.append("BRD-XS-005: No currency scope detected (skipped)")
        return

    mandatory_str = _serialize(mandatory)

    # Check for currency-related keywords.
    has_currency_keyword = any(
        kw.lower() in mandatory_str.lower() for kw in _CURRENCY_KEYWORDS
    )
    if not has_currency_keyword:
        passes.append("BRD-XS-005: No currency scope detected (skipped)")
        return

    # Extract currency codes from mandatory_conditions.
    raw_codes_mandatory = set(re.findall(r"\b([A-Z]{3,4})\b", mandatory_str))
    mandatory_currencies = raw_codes_mandatory & _KNOWN_CURRENCIES

    # Extract currency codes from functional_requirements.
    fr_section = yaml_data.get("functional_requirements", {})
    fr_str = _serialize(fr_section)
    raw_codes_fr = set(re.findall(r"\b([A-Z]{3,4})\b", fr_str))
    fr_currencies = raw_codes_fr & _KNOWN_CURRENCIES

    # Codes in mandatory_conditions but missing from FR.
    missing = mandatory_currencies - fr_currencies
    if missing:
        for code in sorted(missing):
            warnings.append(
                f"BRD-XS-005: Currency '{code}' in mandatory_conditions "
                f"but not referenced in functional_requirements"
            )
    else:
        passes.append(
            f"BRD-XS-005: All {len(mandatory_currencies)} currency "
            f"code(s) covered in functional_requirements"
        )


# ── Public API ───────────────────────────────────────────────────────

def run_brd_cross_section_checks(
    *,
    yaml_data: dict[str, object],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """BRD-specific cross-section consistency validation (YAML BRDs only)."""
    _check_adt_propagation(yaml_data, errors, warnings, passes)
    _check_phase_alignment(yaml_data, errors, warnings, passes)
    _check_entity_consistency(yaml_data, errors, warnings, passes)
    _check_currency_consistency(yaml_data, errors, warnings, passes)


def run_brd_cross_section_checks_md(
    *,
    content: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """BRD cross-section checks for MD-format BRDs (regex-based, limited).

    Only BRD-XS-002 (phase count) is feasible via regex.  The remaining
    rules require structured YAML data and are skipped with info messages.
    """
    passes.append("BRD-XS-001: Requires YAML data (skipped for MD)")
    passes.append("BRD-XS-004: Requires YAML data (skipped for MD)")
    passes.append("BRD-XS-005: Requires YAML data (skipped for MD)")

    # BRD-XS-002 MD fallback: compare phase heading counts.
    # Split content around "Implementation" heading to separate scope vs impl.
    scope_section = ""
    impl_section = ""

    impl_split = re.split(
        r"^(#{1,3}\s+.*[Ii]mplementation.*$)",
        content,
        maxsplit=1,
        flags=re.MULTILINE,
    )
    if len(impl_split) >= 3:
        scope_section = impl_split[0]
        impl_section = impl_split[1] + impl_split[2]
    else:
        # Cannot reliably separate sections.
        passes.append(
            "BRD-XS-002: Cannot identify scope/implementation "
            "sections in MD (skipped)"
        )
        return

    scope_phase_count = len(re.findall(r"Phase\s+\d+", scope_section))
    impl_phase_count = len(re.findall(r"Phase\s+\d+", impl_section))

    if scope_phase_count == 0 and impl_phase_count == 0:
        passes.append("BRD-XS-002: No phase headings found in MD (skipped)")
        return

    if scope_phase_count != impl_phase_count:
        warnings.append(
            f"BRD-XS-002: Phase count mismatch in MD — scope mentions "
            f"{scope_phase_count} phase(s), implementation mentions "
            f"{impl_phase_count}"
        )
    else:
        passes.append(
            f"BRD-XS-002: {scope_phase_count} phase reference(s) "
            f"consistent between scope and implementation sections"
        )
