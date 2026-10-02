"""Unit: TAG01 lifts the ``tdd`` tag for docs-only IPLANs (GD-46, #872).

A docs-only IPLAN (manifest with no code/test bindings) declares
``tdd_consistency.status: not-applicable`` and goes green without a
borrowed ``@tdd`` tag. The exemption is single-signal (status only —
subtype plays no role in the guard) and ``@spec:`` stays required.
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


def _iplan(*, subtype: str, status: str, spec: bool, tdd: bool) -> str:
    lines = [
        "doc_id: IPLAN-99",
        "document_control:",
        f"  subtype: {subtype}",
    ]
    if spec:
        lines.append('source_spec: "@spec: SPEC-01"')
    if tdd:
        lines.append('"@tdd: TDD-01.04.4816"')
    lines += [
        "tdd_consistency:",
        f"  status: {status}",
    ]
    return "\n".join(lines) + "\n"


def _tag01(text: str, artifact: str = "IPLAN", rel: str = "IPLAN-99.yaml") -> list:
    layers, doc_re, elem_re = _load_registry(None)
    findings = lint_text(text, artifact, rel, layers, doc_re, elem_re)
    return [f for f in findings if f.code == "TAG01"]


class Tag01NaExemption(unittest.TestCase):
    def test_na_iplan_green_without_tdd_tag(self) -> None:
        text = _iplan(subtype="docs", status="not-applicable", spec=True, tdd=False)
        self.assertEqual(_tag01(text), [])

    def test_verified_without_tdd_tag_still_red(self) -> None:
        # Negative control: the exemption is the N/A status, not the subtype.
        text = _iplan(subtype="docs", status="verified", spec=True, tdd=False)
        codes = _tag01(text)
        self.assertEqual(len(codes), 1)
        self.assertIn("@tdd:", codes[0].message)

    def test_code_iplan_without_tdd_tag_still_red(self) -> None:
        text = _iplan(subtype="code_build", status="in_progress", spec=True, tdd=False)
        codes = _tag01(text)
        self.assertEqual(len(codes), 1)
        self.assertIn("@tdd:", codes[0].message)

    def test_na_iplan_still_requires_spec_tag(self) -> None:
        text = _iplan(subtype="docs", status="not-applicable", spec=False, tdd=False)
        codes = _tag01(text)
        self.assertEqual(len(codes), 1)
        self.assertIn("@spec:", codes[0].message)

    def test_full_tags_unchanged(self) -> None:
        text = _iplan(subtype="code_build", status="verified", spec=True, tdd=True)
        self.assertEqual(_tag01(text), [])

    def test_subtype_plays_no_role(self) -> None:
        # Single-signal pin: code_build + not-applicable also goes green.
        text = _iplan(subtype="code_build", status="not-applicable", spec=True, tdd=False)
        self.assertEqual(_tag01(text), [])

    def test_normalised_variant_exempts(self) -> None:
        # Case/whitespace leniency matches the id_state convention in lint_text.
        text = _iplan(subtype="docs", status=" Not-Applicable ", spec=True, tdd=False)
        self.assertEqual(_tag01(text), [])

    def test_missing_consistency_block_still_red(self) -> None:
        text = 'doc_id: IPLAN-99\nsource_spec: "@spec: SPEC-01"\n'
        codes = _tag01(text)
        self.assertEqual(len(codes), 1)
        self.assertIn("@tdd:", codes[0].message)

    def test_non_dict_consistency_still_red(self) -> None:
        text = 'doc_id: IPLAN-99\nsource_spec: "@spec: SPEC-01"\ntdd_consistency: not-applicable\n'
        codes = _tag01(text)
        self.assertEqual(len(codes), 1)
        self.assertIn("@tdd:", codes[0].message)

    def test_eval_na_block_still_requires_tdd(self) -> None:
        # IPLAN-only guard: other layers never read the exemption.
        text = (
            "doc_id: EVAL-99\n"
            'source_spec: "@spec: SPEC-01"\n'
            '"@ears: EARS-01"\n'
            '"@bdd: BDD-01"\n'
            '"@iplan: IPLAN-99"\n'
            "tdd_consistency:\n"
            "  status: not-applicable\n"
        )
        codes = _tag01(text, artifact="EVAL", rel="EVAL-99.yaml")
        self.assertEqual(len(codes), 1)
        self.assertIn("@tdd:", codes[0].message)


if __name__ == "__main__":
    unittest.main()
