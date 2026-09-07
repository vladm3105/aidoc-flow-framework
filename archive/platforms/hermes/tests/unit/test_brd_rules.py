"""Unit tests for BRD-specific cross-section validation rules."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.validation.brd_rules import (  # noqa: E402
    run_brd_cross_section_checks,
    run_brd_cross_section_checks_md,
)

# ── Helpers ──────────────────────────────────────────────────────────


def _run(yaml_data: dict) -> tuple[list[str], list[str], list[str]]:
    """Run BRD cross-section checks and return (errors, warnings, passes)."""
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_brd_cross_section_checks(
        yaml_data=yaml_data,
        errors=errors,
        warnings=warnings,
        passes=passes,
    )
    return errors, warnings, passes


# ── BRD-XS-001: ADT Decision Propagation ─────────────────────────────


def test_adt_propagation_passes():
    """ADT selected option found in both implementation_approach and cost_benefit."""
    data = {
        "adr_topics": {
            "topics": [
                {
                    "title": "Ledger Engine",
                    "alternatives": [
                        {"option": "Custom PostgreSQL", "rationale": "Selected"},
                    ],
                },
            ],
        },
        "implementation_approach": {"description": "Uses Custom PostgreSQL for ledger"},
        "cost_benefit": {"analysis": "Custom PostgreSQL reduces cost"},
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert not warnings
    assert any("BRD-XS-001" in p and "propagated" in p for p in passes)


def test_adt_propagation_warns_missing_from_cost():
    """ADT selected option missing from cost_benefit triggers a warning."""
    data = {
        "adr_topics": {
            "topics": [
                {
                    "title": "Ledger Engine",
                    "alternatives": [
                        {"option": "Custom PostgreSQL", "rationale": "Selected"},
                    ],
                },
            ],
        },
        "implementation_approach": {"description": "Custom PostgreSQL based"},
        "cost_benefit": {"analysis": "Modern Treasury pricing model"},
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert any("cost_benefit" in w for w in warnings)


def test_adt_propagation_case_insensitive():
    """Case-insensitive matching for ADT selected option."""
    data = {
        "adr_topics": {
            "topics": [
                {
                    "title": "Ledger Engine",
                    "alternatives": [
                        {"option": "Custom PostgreSQL Ledger", "rationale": "Selected"},
                    ],
                },
            ],
        },
        "implementation_approach": {"description": "custom postgresql ledger design"},
        "cost_benefit": {"analysis": "custom postgresql ledger cost"},
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert not warnings
    assert any("BRD-XS-001" in p and "propagated" in p for p in passes)


def test_adt_propagation_skips_no_topics():
    """No adr_topics key results in a skip pass message."""
    data = {
        "implementation_approach": {"description": "something"},
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert not warnings
    assert any("BRD-XS-001" in p and "skipped" in p for p in passes)


# ── BRD-XS-002: Phase Alignment ──────────────────────────────────────


def test_phase_alignment_passes():
    """Matching phases in scope and implementation pass validation."""
    data = {
        "project_scope": {
            "phasing": {
                "phases": [
                    {"phase": "Phase 1"},
                    {"phase": "Phase 2"},
                    {"phase": "Phase 3"},
                ],
            },
        },
        "implementation_approach": {
            "phases": {
                "items": [
                    {"phase": "Phase 1"},
                    {"phase": "Phase 2"},
                    {"phase": "Phase 3"},
                ],
            },
        },
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert any("BRD-XS-002" in p and "aligned" in p for p in passes)


def test_phase_alignment_errors_count_mismatch():
    """Different phase counts between scope and implementation raise errors."""
    data = {
        "project_scope": {
            "phasing": {
                "phases": [{"phase": f"Phase {i}"} for i in range(1, 6)],
            },
        },
        "implementation_approach": {
            "phases": {
                "items": [{"phase": f"Phase {i}"} for i in range(1, 5)],
            },
        },
    }
    errors, warnings, passes = _run(data)
    assert any("BRD-XS-002" in e and "mismatch" in e for e in errors)


def test_phase_alignment_errors_name_mismatch():
    """Same count but different phase names raise errors."""
    data = {
        "project_scope": {
            "phasing": {
                "phases": [
                    {"phase": "Alpha"},
                    {"phase": "Beta"},
                ],
            },
        },
        "implementation_approach": {
            "phases": {
                "items": [
                    {"phase": "Alpha"},
                    {"phase": "Gamma"},
                ],
            },
        },
    }
    errors, warnings, passes = _run(data)
    assert any("BRD-XS-002" in e for e in errors)
    assert any("Beta" in e or "Gamma" in e for e in errors)


def test_phase_alignment_skips_missing_section():
    """No implementation_approach key results in a skip."""
    data = {
        "project_scope": {"phasing": {"phases": []}},
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert any("BRD-XS-002" in p and "skipped" in p for p in passes)


# ── BRD-XS-004: Entity Consistency ───────────────────────────────────


def test_entity_consistency_passes():
    """Partner entity from stakeholders found in functional_requirements passes."""
    data = {
        "stakeholders": {
            "decision_makers": [
                {"role": "Partner Teams", "name": "Bridge"},
            ],
        },
        "functional_requirements": {"items": "Bridge payment processing"},
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert any("BRD-XS-004" in p and "found" in p for p in passes)


def test_entity_consistency_warns_stale():
    """Partner entity absent from downstream sections warns."""
    data = {
        "stakeholders": {
            "decision_makers": [
                {"role": "Partner Teams", "name": "Bridge, Sardine"},
            ],
        },
        "functional_requirements": {"items": "Bridge integration only"},
        "introduction": {},
        "project_scope": {},
    }
    errors, warnings, passes = _run(data)
    assert any("Sardine" in w for w in warnings)


def test_entity_consistency_skips_no_entities():
    """No partner stakeholders or workaround entities results in a skip."""
    data = {
        "stakeholders": {
            "decision_makers": [
                {"role": "Executive Leadership", "name": "CEO"},
            ],
        },
        "functional_requirements": {"items": "something"},
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert any("BRD-XS-004" in p and "skipped" in p for p in passes)


# ── BRD-XS-005: Currency Scope Consistency ────────────────────────────


def test_currency_passes_superset():
    """FR currencies are a superset of mandatory_conditions currencies."""
    data = {
        "mandatory_conditions": {
            "precision": "2 decimal places",
            "currencies": "USD, UZS required",
        },
        "functional_requirements": {
            "items": "Support USD, UZS, MXN, USDC transfers",
        },
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert not warnings
    assert any("BRD-XS-005" in p and "covered" in p for p in passes)


def test_currency_warns_missing():
    """Currency in mandatory_conditions but absent from FR warns."""
    data = {
        "mandatory_conditions": {
            "precision": "2 decimal places",
            "currencies": "UZS required",
        },
        "functional_requirements": {
            "items": "Support USD, MXN, USDC transfers",
        },
    }
    errors, warnings, passes = _run(data)
    assert any("UZS" in w for w in warnings)


def test_currency_skips_no_precision():
    """No mandatory_conditions key results in skip pass message."""
    data = {
        "functional_requirements": {
            "items": "Support USD transfers",
        },
    }
    errors, warnings, passes = _run(data)
    assert not errors
    assert not warnings
    assert any("BRD-XS-005" in p and "skipped" in p for p in passes)


# ── MD Fallback ───────────────────────────────────────────────────────


def test_md_fallback_runs_without_crash():
    """MD fallback executes without raising exceptions."""
    content = (
        "# BRD Document\n"
        "## Scope\n"
        "Phase 1 setup\nPhase 2 rollout\n"
        "## Implementation Approach\n"
        "Phase 1 setup\nPhase 2 rollout\n"
    )
    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    run_brd_cross_section_checks_md(
        content=content,
        errors=errors,
        warnings=warnings,
        passes=passes,
    )
    assert any("BRD-XS-001" in p for p in passes)
    assert any("BRD-XS-002" in p for p in passes)
    assert any("BRD-XS-004" in p for p in passes)
    assert any("BRD-XS-005" in p for p in passes)
