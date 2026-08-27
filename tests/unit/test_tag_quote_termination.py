"""Unit: a trace tag ending a quoted YAML scalar must resolve (LINT-TAG-QUOTE-001).

`TAG`/`_TAG` captured `[^\\s|]+`, which terminates on whitespace or a pipe but NOT on
a quote. A tag closing a quoted scalar therefore glommed the closing `"` into the
value, failed the anchored `ELEM_FORM`/`DOC_FORM` check, and was **silently dropped**
from the edge graph — no finding, no edge, no resolution check.

The framework's own layer templates prescribe exactly that form (47 occurrences across
the eight canonical `<X>-TEMPLATE.yaml` files), so the defect reaches any corpus authored to template.
`_THRESHOLD` already carries the same exclusion for the same bug class; this locks it
for the trace tags. See issue #542.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from sdd_doc_lint import (  # noqa: E402
    _TAG,
    _TAG_QUOTED_VALUE,
    build_edge_graph,  # noqa: E402
    lint_path,
)
from sdd_doc_lint.trace_graph import ELEM_FORM, TAG, doc_id_from_token  # noqa: E402

_IPLAN = """---
doc_id: IPLAN-01
artifact_type: IPLAN
layer: 8
---

file_manifest:
  files:
    - path: tests/unit/test_auth.py
      {carrier}
"""


def _values(line: str, pattern) -> list[str]:
    return [m.group(2) for m in pattern.finditer(line)]


class TagQuoteTermination(unittest.TestCase):
    """The value capture must stop at a quote, for both tag regexes."""

    DOUBLE = '      tdd_ref: "@tdd: TDD.01.04.aaaa"'
    SINGLE = "      tdd_ref: '@tdd: TDD.01.04.aaaa'"

    def test_double_quoted_scalar_yields_a_valid_element_id(self):
        for name, pattern in (("trace_graph.TAG", TAG), ("sdd_doc_lint._TAG", _TAG)):
            with self.subTest(regex=name):
                vals = _values(self.DOUBLE, pattern)
                self.assertEqual(vals, ["TDD.01.04.aaaa"], f"{name} glommed the quote")
                self.assertTrue(ELEM_FORM.match(vals[0]))
                self.assertEqual(doc_id_from_token(vals[0]), "TDD-01")

    def test_single_quoted_scalar_yields_a_valid_element_id(self):
        """Excluding only `"` would leave the single-quoted YAML form broken."""
        for name, pattern in (("trace_graph.TAG", TAG), ("sdd_doc_lint._TAG", _TAG)):
            with self.subTest(regex=name):
                vals = _values(self.SINGLE, pattern)
                self.assertEqual(vals, ["TDD.01.04.aaaa"], f"{name} glommed the quote")
                self.assertTrue(ELEM_FORM.match(vals[0]))

    def test_pipe_delimited_multi_tag_is_unchanged(self):
        """DD-8: a pipe-separated line still yields one match per tag, all valid."""
        line = '      tdd_ref: "@tdd: TDD.01.04.aaaa | @tdd: TDD.01.04.bbbb"'
        self.assertEqual(_values(line, TAG), ["TDD.01.04.aaaa", "TDD.01.04.bbbb"])

    def test_unquoted_form_still_resolves(self):
        """The regression must not narrow the pre-existing unquoted behaviour."""
        line = "- `TDD.01.04.3c7f` bdd_ref @bdd: BDD.01.03.9b90 — e2e"
        self.assertEqual(_values(line, TAG), ["BDD.01.03.9b90"])

    def test_quoted_tag_records_a_trace_edge(self):
        """The behavioural consequence: a quoted citation reaches the edge graph.

        Asserts the *classification* (an edge to the cited element exists), not a
        downstream finding count — a finding count has more than one possible cause.
        """
        corpus = [("docs/08_IPLAN/IPLAN-01.yaml", _IPLAN.format(carrier=self.DOUBLE.strip()))]
        graph = build_edge_graph(corpus)
        cited = {e.cited_token for e in graph.edges if e.citer_doc == "IPLAN-01"}
        self.assertIn("TDD.01.04.aaaa", cited)

    def test_quote_is_excluded_by_the_pattern_not_by_a_caller(self):
        """Guards the *direction* of the fix, not one worked example.

        Assert the character class itself, so a later refactor cannot regress to a
        trailing-optional-quote pattern (which re-introduces the glomming) or to a
        caller-side strip (which pairs but records no edge) and stay green.
        """
        for name, pattern in (("trace_graph.TAG", TAG), ("sdd_doc_lint._TAG", _TAG)):
            with self.subTest(regex=name):
                self.assertIn(
                    r"[^\s|'\"]",
                    pattern.pattern,
                    f"{name}: the quote exclusion must live in the value character "
                    "class itself. A trailing optional-quote suffix, or a "
                    "caller-side strip, would satisfy a looser check while "
                    "leaving the edge graph broken.",
                )


class QuoteLedValueIsReportedNotDropped(unittest.TestCase):
    """The narrowed class must not fail OPEN on the mirror-image input.

    Excluding quotes means a value that *begins* with a quote matches no `_TAG`
    at all. Before the fix that shape produced a visible `ID01`; without a guard
    the fix would silently drop it — the same failure it exists to remove, one
    input shape over. Found in pre-push review, not by the original tests.
    """

    QUOTE_LED = ["  - @adr: 'ADR-01'", '  - @adr: "ADR-01"']

    def test_tag_regex_deliberately_does_not_match(self):
        for line in self.QUOTE_LED:
            with self.subTest(line=line):
                self.assertEqual(list(_TAG.finditer(line)), [])

    def test_the_guard_catches_what_the_tag_regex_drops(self):
        for line in self.QUOTE_LED:
            with self.subTest(line=line):
                self.assertTrue(_TAG_QUOTED_VALUE.search(line))

    def test_id01_is_emitted_so_the_fix_cannot_fail_open(self):
        """Assert the *classification* through the real entry point.

        A quote-led tag must surface as ID01 exactly as it did pre-fix. Asserting
        the code rather than a finding count: a count has more than one possible
        cause, so it can pass for the wrong reason.
        """
        import tempfile

        doc = (
            "---\ndoc_id: ADR-01\nartifact_type: ADR\nlayer: 5\n---\n\n"
            "# ADR-01\n\n- @adr: 'ADR-02'\n"
        )
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "05_ADR"
            root.mkdir()
            (root / "ADR-01.md").write_text(doc, encoding="utf-8")
            codes = {f.code for f in lint_path(root)}
        self.assertIn(
            "ID01",
            codes,
            "a quote-led tag value was dropped silently instead of reported "
            f"malformed; codes seen: {sorted(codes)}",
        )


if __name__ == "__main__":
    unittest.main()
