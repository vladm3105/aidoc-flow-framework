"""B7 guard (HERMES-REVIEW-001): Hermes's native BDD authoring/review/remediation
surfaces must teach the structured ``scenarios:`` YAML form (D-0038), not Gherkin.

This is a Hermes-internal assertion over the platform's *private* prompt files, so
it lives here rather than coupling the shared ``tests/conformance/`` suite to one
platform's internals.

It keys on **structural** Gherkin markers only — a ```gherkin fenced block,
a ``Feature:``/``Scenario:``/``Background:`` declaration line, or a standalone
Gherkin scenario-tag line. It deliberately does NOT grep the bare word "Gherkin":
a correct YAML-BDD prompt legitimately says "author ``scenarios:`` YAML, NOT
Gherkin" as an anti-drift instruction, which a bare-token grep would false-positive
on.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]  # platforms/hermes

# Hermes's private BDD surfaces that must teach the YAML-BDD form.
BDD_SURFACES = [
    "prompts/templates/creation/UCC_PROMPT_BDD.md",
    "prompts/templates/review/UCR_PROMPT_BDD.md",
    "prompts/templates/remediation/UCRem_PROMPT_BDD.md",
    "skills/personas/qa_lead.md",
    "prompts/templates/creation/UCC_OUTPUT_SCHEMA.md",
]

# Structural Gherkin markers (NOT the bare word "Gherkin").
_GHERKIN_FENCE = re.compile(r"^\s*```+\s*gherkin\b", re.IGNORECASE | re.MULTILINE)
_GHERKIN_DECL = re.compile(r"^\s*(Feature|Scenario Outline|Scenario|Background):", re.MULTILINE)
# A standalone Gherkin scenario-tag line (retired @-tag convention), e.g.
#   @happy-path @ears:EARS.01.03.c4d8
# `@threshold:...` is legitimate INLINE inside quoted step prose, so it is not
# matched here (this is anchored to the start of a line).
_GHERKIN_TAG_LINE = re.compile(
    r"^\s*@(happy-path|edge-case|error-handling|ears|prd|brd)\b", re.MULTILINE
)


@pytest.mark.parametrize("rel", BDD_SURFACES)
def test_bdd_surface_has_no_structural_gherkin(rel: str) -> None:
    path = ROOT / rel
    assert path.is_file(), f"missing BDD surface: {rel}"
    text = path.read_text(encoding="utf-8")

    fence = _GHERKIN_FENCE.search(text)
    assert fence is None, f"{rel}: contains a ```gherkin fenced block (Gherkin residue)"

    decl = _GHERKIN_DECL.search(text)
    assert decl is None, (
        f"{rel}: contains a Gherkin declaration line "
        f"({decl.group(0).strip() if decl else ''!r}) — author scenarios: YAML instead"
    )

    tag = _GHERKIN_TAG_LINE.search(text)
    assert tag is None, (
        f"{rel}: contains a standalone Gherkin scenario-tag line "
        f"({tag.group(0).strip() if tag else ''!r}) — use the structured "
        f"type:/priority:/ears: fields instead"
    )


@pytest.mark.parametrize("rel", BDD_SURFACES)
def test_bdd_surface_teaches_scenarios_yaml(rel: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    assert "scenarios:" in text, (
        f"{rel}: does not reference the `scenarios:` YAML form — the YAML-BDD "
        f"authoring model must be taught"
    )
