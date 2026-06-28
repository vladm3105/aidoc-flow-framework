"""Unit: the dual-mode BDD YAML parse path (YAML-BDD-SCHEMA PR-2).

A migrated BDD doc carries scenarios as a ```yaml ``scenarios:`` block. The
linter must read its trace from the structured ``ears`` lists (not ``@ears:``
tags) — feeding build_edge_graph (verbatim synthetic edges), REFGRAN01,
TRACE-RES-001, and TAG01 — plus a structural ``BDD-SCHEMA-001`` check. A doc
with no scenarios block falls back to the legacy Gherkin ``@``-tag path.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import yaml  # noqa: E402
from sdd_doc_lint import (  # noqa: E402
    _check_ref_granularity,
    _check_trace_resolution,
    _load_registry,
    build_edge_graph,
    lint_text,
)

LAYERS, DOC_RE, ELEM_RE = _load_registry(None)


def _scn(ears, sid="BDD.01.03.ccd6", **kw):
    s = {
        "id": sid,
        "name": "Shorten a valid URL",
        "type": "success",
        "priority": "p0-critical",
        "ears": ears,
        "given": ["a precondition"],
        "when": ["an action"],
        "then": ["an outcome"],
    }
    s.update(kw)
    return s


def _bdd(scenarios, doc_id="BDD-01"):
    block = yaml.safe_dump({"scenarios": scenarios}, sort_keys=False, allow_unicode=True)
    text = (
        f"---\ndoc_id: {doc_id}\nartifact_type: BDD\n---\n\n"
        f"## 3. Scenario Structure\n\n```yaml\n{block}```\n"
    )
    return (f"{doc_id}.md", text)


def _ears(*ids, doc_id="EARS-01"):
    body = "\n".join(f"- {i}: a requirement." for i in ids)
    return (
        f"{doc_id}.md",
        f"---\ndoc_id: {doc_id}\nartifact_type: EARS\n---\n\n## 4. Reqs\n{body}\n",
    )


def _codes(findings, code):
    return [f for f in findings if f.code == code]


class BddYamlMode(unittest.TestCase):
    # --- REFGRAN via verbatim synthetic edges (LB-3) -------------------------
    def test_refgran_fires_on_doc_form_ears(self):
        corpus = [_ears("EARS.01.03.aaaa"), _bdd([_scn(["EARS-01"])])]
        f = _check_ref_granularity(corpus, "gate-code")
        self.assertEqual([(x.code, x.severity) for x in f], [("REFGRAN01", "error")])

    def test_refgran_silent_on_element_form(self):
        corpus = [_ears("EARS.01.03.aaaa"), _bdd([_scn(["EARS.01.03.aaaa"])])]
        self.assertEqual(_check_ref_granularity(corpus, "gate-code"), [])

    # --- build_edge_graph emits verbatim synthetic edges --------------------
    def test_synthetic_edges_verbatim(self):
        corpus = [_ears("EARS.01.03.aaaa"), _bdd([_scn(["EARS.01.03.aaaa", "EARS.01.03.bbbb"])])]
        g = build_edge_graph(corpus)
        bdd_edges = {e.cited_token for e in g.edges if e.citer_doc == "BDD-01"}
        self.assertEqual(bdd_edges, {"EARS.01.03.aaaa", "EARS.01.03.bbbb"})
        # ...and they resolve to the EARS host doc for COV reach.
        self.assertEqual({e.cited_doc for e in g.edges if e.citer_doc == "BDD-01"}, {"EARS-01"})

    # --- TRACE-RES-001 over scenario ears -----------------------------------
    def test_trace_res_fires_on_unresolved_ears(self):
        corpus = [_ears("EARS.01.03.aaaa"), _bdd([_scn(["EARS.01.03.ffff"])])]  # ffff not declared
        f = _check_trace_resolution(corpus, LAYERS, DOC_RE, ELEM_RE)
        self.assertTrue(_codes(f, "TRACE-RES-001"))

    def test_trace_res_silent_on_resolved_ears(self):
        corpus = [_ears("EARS.01.03.aaaa"), _bdd([_scn(["EARS.01.03.aaaa"])])]
        self.assertEqual(
            _codes(_check_trace_resolution(corpus, LAYERS, DOC_RE, ELEM_RE), "TRACE-RES-001"), []
        )

    # --- TAG01 satisfied from scenario ears (no @ears tag) ------------------
    def test_tag01_satisfied_from_scenario_ears(self):
        _, text = _bdd([_scn(["EARS.01.03.aaaa"])])
        f = lint_text(text, "BDD", "BDD-01.md", LAYERS, DOC_RE, ELEM_RE)
        self.assertEqual(_codes(f, "TAG01"), [])

    # --- BDD-SCHEMA-001 structural -----------------------------------------
    def test_schema_missing_required_field(self):
        bad = _scn(["EARS.01.03.aaaa"])
        del bad["when"]
        _, text = _bdd([bad])
        f = lint_text(text, "BDD", "BDD-01.md", LAYERS, DOC_RE, ELEM_RE)
        msgs = [x.message for x in _codes(f, "BDD-SCHEMA-001")]
        self.assertTrue(any("'when'" in m for m in msgs), msgs)

    def test_schema_invalid_type_and_priority(self):
        _, text = _bdd([_scn(["EARS.01.03.aaaa"], type="bogus", priority="p9-ultra")])
        msgs = " ".join(
            x.message
            for x in _codes(
                lint_text(text, "BDD", "BDD-01.md", LAYERS, DOC_RE, ELEM_RE), "BDD-SCHEMA-001"
            )
        )
        self.assertIn("invalid type", msgs)
        self.assertIn("invalid priority", msgs)

    def test_schema_malformed_block(self):
        text = (
            "---\ndoc_id: BDD-01\nartifact_type: BDD\n---\n\n## 3. Scenario Structure\n\n"
            "```yaml\nscenarios:\n  - id: BDD.01.03.ccd6\n  bad-indent: [unbalanced\n```\n"
        )
        f = lint_text(text, "BDD", "BDD-01.md", LAYERS, DOC_RE, ELEM_RE)
        self.assertTrue(_codes(f, "BDD-SCHEMA-001"))

    def test_no_double_report_refgran_vs_schema(self):
        # A well-formed doc-form ears: REFGRAN fires (granularity), but
        # BDD-SCHEMA-001 must NOT also flag ears (structural only).
        _, text = _bdd([_scn(["EARS-01"])])
        f = lint_text(text, "BDD", "BDD-01.md", LAYERS, DOC_RE, ELEM_RE)
        self.assertEqual(_codes(f, "BDD-SCHEMA-001"), [])

    # --- Dual-mode: legacy Gherkin still works ------------------------------
    def test_legacy_gherkin_still_satisfies_tag01_and_no_schema(self):
        text = (
            "---\ndoc_id: BDD-01\nartifact_type: BDD\n---\n\n## 3. Scenario Structure\n\n"
            "```gherkin\n@ears:EARS.01.03.aaaa\nScenario: x\n```\n"
        )
        f = lint_text(text, "BDD", "BDD-01.md", LAYERS, DOC_RE, ELEM_RE)
        self.assertEqual(_codes(f, "TAG01"), [])
        self.assertEqual(_codes(f, "BDD-SCHEMA-001"), [])


if __name__ == "__main__":
    unittest.main()
