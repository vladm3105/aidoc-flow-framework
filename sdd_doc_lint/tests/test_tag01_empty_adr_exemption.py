"""Unit: TAG01 lifts upstream tags for empty ADR indexes (GD-46 precedent, #1041).

A freshly scaffolded ADR index (`adrs: []`, `technologies: []`) has no
records, so there is nothing to trace upstream — the emptiness names the
waived contract at its own point. The exemption is dual-signal (both lists
empty); any records without tags stay red, and other artifacts never read it.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Resolve the sdd_doc_lint package from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sdd_doc_lint import (  # noqa: E402
    _load_registry,
    lint_text,
)


def _adr(*, adrs: str, technologies: str = "[]", tags: bool) -> str:
    lines = [
        "metadata:",
        '  framework_version: "9.9.9"',
        "total_adrs: 0",
        f"adrs: {adrs}",
        f"technologies: {technologies}",
        "backlog: []",
    ]
    if tags:
        lines += ['"@ears: EARS-01"', '"@bdd: BDD-01"']
    return "\n".join(lines) + "\n"


def _tag01(text: str, artifact: str = "ADR", rel: str = "ADR-00_index.yaml") -> list:
    layers, doc_re, elem_re = _load_registry(None)
    findings = lint_text(text, artifact, rel, layers, doc_re, elem_re)
    return [f for f in findings if f.code == "TAG01"]


class Tag01EmptyAdrExemption(unittest.TestCase):
    def test_empty_index_green_without_tags(self) -> None:
        self.assertEqual(_tag01(_adr(adrs="[]", tags=False)), [])

    def test_nonempty_index_without_tags_still_red(self) -> None:
        # Negative control: the exemption is the empty registry, not the layer.
        codes = _tag01(_adr(adrs="[{id: ADR-01}]", tags=False))
        self.assertEqual(len(codes), 2)
        self.assertIn("@ears:", codes[0].message)
        self.assertIn("@bdd:", codes[1].message)

    def test_populated_technologies_without_tags_still_red(self) -> None:
        # Technology records carry authorizing decisions: traceability applies.
        codes = _tag01(_adr(adrs="[]", technologies="[{name: pg}]", tags=False))
        self.assertEqual(len(codes), 2)

    def test_index_with_tags_unchanged(self) -> None:
        self.assertEqual(_tag01(_adr(adrs="[{id: ADR-01}]", tags=True)), [])

    def test_missing_adrs_key_still_red(self) -> None:
        # Fail-safe: no explicit empty list, no exemption.
        text = 'metadata:\n  framework_version: "9.9.9"\n'
        codes = _tag01(text)
        self.assertEqual(len(codes), 2)

    def test_other_artifact_unaffected(self) -> None:
        # ADR-only guard: an `adrs: []` key means nothing to other layers.
        text = "doc_id: SPEC-99\nadrs: []\n"
        codes = _tag01(text, artifact="SPEC", rel="SPEC-99.yaml")
        self.assertTrue(len(codes) > 0)


if __name__ == "__main__":
    unittest.main()
