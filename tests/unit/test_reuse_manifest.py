"""Unit: REUSE-MANIFEST-001 — satisfied-by-reference.

- `_reuse_map` reads the `reuse:` frontmatter block (default `authored`).
- COV01/COV02 skip a `referenced` host doc (exempt from coverage).
- `_check_reuse` emits one REUSE01 advisory per referenced doc + REUSE02 target
  validation (in-repo + commit-pinned; URL/unpinned/unresolvable → error).
- Full-prefix rule: a referenced doc's upstream tags resolve against in-repo
  prefix copies (no TRACE-RES-001); an absent upstream stays a finding.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root  # noqa: E402

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import _reuse_map, lint_path  # noqa: E402


def _doc(doc_id, artifact_type, body, reuse=None):
    fm = f"doc_id: {doc_id}\nartifact_type: {artifact_type}\n"
    if reuse:
        fm += "reuse:\n  state: " + reuse[0] + "\n"
        if reuse[1] is not None:
            fm += f"  target: {reuse[1]}\n"
    return (f"{doc_id}.md", f"---\n{fm}---\n\n{body}\n")


def _codes(findings):
    return [f.code for f in findings]


def _write_and_lint(corpus, **kw):
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        for rel, text in corpus:
            (tdp / rel).write_text(text, encoding="utf-8")
        return lint_path(tdp, **kw)


class ReuseMap(unittest.TestCase):
    def test_referenced_and_default(self):
        corpus = [
            _doc("PRD-01", "PRD", "body", reuse=("referenced", "PRD-09@abc1234")),
            _doc("EARS-01", "EARS", "body"),
        ]
        m = _reuse_map(corpus)
        self.assertEqual(m["PRD-01"], ("referenced", "PRD-09@abc1234"))
        self.assertEqual(m["EARS-01"], ("authored", ""))


class CoverageEscape(unittest.TestCase):
    def test_referenced_brd_fr_escapes_cov01(self):
        # An authored BRD whose FR reaches no PRD/SPEC → COV01 error. The SAME
        # BRD marked referenced → no COV01 (exempt) + a REUSE01 advisory.
        fr_body = "## 7. Functional Requirements\n\n- **BRD.01.07.aaaa — F** (P1): x."
        base = [
            _doc("SPEC-99", "SPEC", "standalone"),
            _doc("IPLAN-99", "IPLAN", "standalone"),
        ]
        authored = _codes(_write_and_lint([_doc("BRD-01", "BRD", fr_body)] + base))
        self.assertIn("COV01", authored)
        referenced = _codes(
            _write_and_lint(
                [_doc("BRD-01", "BRD", fr_body, reuse=("referenced", "BRD-09@abc1234"))] + base
            )
        )
        self.assertNotIn("COV01", referenced)
        self.assertIn("REUSE01", referenced)

    def test_referenced_ears_escapes_cov02(self):
        ears_body = "## 3. Requirements\n\n- EARS.01.03.aaaa: a requirement."
        base = [_doc("SPEC-99", "SPEC", "real spec, cites nothing")]
        authored = _codes(
            _write_and_lint([_doc("EARS-01", "EARS", ears_body)] + base, mode="gate-code")
        )
        self.assertIn("COV02", authored)
        referenced = _codes(
            _write_and_lint(
                [_doc("EARS-01", "EARS", ears_body, reuse=("referenced", "EARS-09@abc1234"))]
                + base,
                mode="gate-code",
            )
        )
        self.assertNotIn("COV02", referenced)
        self.assertIn("REUSE01", referenced)


class TargetValidation(unittest.TestCase):
    def _reuse_findings(self, target):
        corpus = [
            _doc("PRD-01", "PRD", "## 1. x\n\nbody", reuse=("referenced", target)),
            _doc("PRD-09", "PRD", "## 1. x\n\nbody"),  # a resolvable target ref
        ]
        return [f for f in _write_and_lint(corpus) if f.code == "REUSE02"]

    def test_url_target_rejected(self):
        self.assertTrue(self._reuse_findings("https://example.com/prd"))

    def test_unpinned_target_rejected(self):
        self.assertTrue(self._reuse_findings("PRD-09"))  # no @commit

    def test_unresolvable_ref_rejected(self):
        self.assertTrue(self._reuse_findings("PRD-77@abc1234"))  # not in corpus

    def test_valid_pinned_in_repo_target_ok(self):
        self.assertEqual(self._reuse_findings("PRD-09@abc1234"), [])  # resolves


class FullPrefix(unittest.TestCase):
    def test_referenced_upstream_resolves_absent_flags(self):
        # BRD + PRD both referenced; the PRD's @brd resolves to the in-repo BRD
        # element (no TRACE-RES-001). A referenced doc citing an ABSENT upstream
        # element still fires TRACE-RES-001 (incomplete reuse).
        brd = _doc(
            "BRD-01",
            "BRD",
            "- **BRD.01.07.aaaa**: a requirement.",
            reuse=("referenced", "BRD-09@abc1234"),
        )
        prd_ok = _doc(
            "PRD-01",
            "PRD",
            "@brd: BRD.01.07.aaaa\n\n- **PRD.01.09.bbbb**: a feature.",
            reuse=("referenced", "PRD-09@abc1234"),
        )
        codes_ok = _codes(_write_and_lint([brd, prd_ok]))
        self.assertNotIn("TRACE-RES-001", codes_ok)

        prd_absent = _doc(
            # well-formed hex id, but BRD-99 is absent → TRACE-RES-001 (not ID03)
            "PRD-02",
            "PRD",
            "@brd: BRD.99.07.aaaa\n\n- **PRD.02.09.cccc**: a feature.",
            reuse=("referenced", "PRD-09@abc1234"),
        )
        codes_absent = _codes(_write_and_lint([brd, prd_absent]))
        self.assertIn("TRACE-RES-001", codes_absent)


if __name__ == "__main__":
    unittest.main()
