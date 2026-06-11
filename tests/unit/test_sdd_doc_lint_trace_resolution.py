"""Unit: TRACE-RES-001 fires on every unresolvable ``@<layer>: <ID>`` tag.

The lint rule runs uniformly at every layer (including layers without an
auditor lens — EARS, SPEC, IPLAN) so the necessary-upstream contract's
"every emitted tag must resolve" invariant has a deterministic structural
floor. See NECESSARY-UPSTREAM-001-PLAN.md Task 4b.
"""

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


def _run_lint(corpus: dict[str, str]) -> list[dict]:
    """Run sdd_doc_lint over a transient corpus and return JSON findings."""
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for rel, body in corpus.items():
            target = td_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "sdd_doc_lint", td, "--format=json"],
            env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            check=False,
        )
        return json.loads(result.stdout or "[]")


def _brd_doc(doc_id: str = "BRD-01", body_id: str = "BRD.01.07.aaaa") -> str:
    return textwrap.dedent(
        f"""
        ---
        doc_id: "{doc_id}"
        artifact_type: BRD
        layer: 1
        ---
        # {doc_id}

        @brd: {doc_id}

        ## §7 Objective {body_id}
        """
    ).strip()


def _prd_doc(
    doc_id: str = "PRD-01",
    brd_ref: str = "BRD-01",
    body_id: str = "PRD.01.09.bbbb",
) -> str:
    return textwrap.dedent(
        f"""
        ---
        doc_id: "{doc_id}"
        artifact_type: PRD
        layer: 2
        ---
        # {doc_id}

        @prd: {doc_id} @brd: {brd_ref}

        ## §9 Feature {body_id}
        """
    ).strip()


class TraceResolutionFloor(unittest.TestCase):
    def test_clean_corpus_emits_no_trace_res_findings(self):
        """Every emitted tag resolves → no TRACE-RES-001 findings."""
        corpus = {
            "docs/01_BRD/BRD-01.md": _brd_doc(),
            "docs/02_PRD/PRD-01.md": _prd_doc(),
        }
        findings = _run_lint(corpus)
        codes = [f["code"] for f in findings]
        self.assertNotIn("TRACE-RES-001", codes, f"unexpected: {codes}")

    def test_tag_referencing_missing_doc_fires_trace_res(self):
        """``@brd: BRD-99`` with no BRD-99 in corpus → TRACE-RES-001."""
        corpus = {
            "docs/02_PRD/PRD-01.md": _prd_doc(brd_ref="BRD-99"),
        }
        findings = _run_lint(corpus)
        trace_findings = [f for f in findings if f["code"] == "TRACE-RES-001"]
        self.assertTrue(
            trace_findings,
            f"expected TRACE-RES-001 for missing BRD-99, got {findings}",
        )
        self.assertIn("BRD-99", trace_findings[0]["message"])

    def test_tag_referencing_unknown_element_fires_trace_res(self):
        """Element-form tag whose host doc exists but lacks the cited id."""
        prd_with_bad_elem_ref = textwrap.dedent(
            """
            ---
            doc_id: "PRD-01"
            artifact_type: PRD
            layer: 2
            ---
            # PRD-01

            @prd: PRD-01

            ## §9
            Trace via @brd: BRD.01.07.ffff (well-formed id, but not declared in BRD-01).
            """
        ).strip()
        corpus = {
            "docs/01_BRD/BRD-01.md": _brd_doc(),  # declares BRD.01.07.aaaa only
            "docs/02_PRD/PRD-01.md": prd_with_bad_elem_ref,
        }
        findings = _run_lint(corpus)
        trace_findings = [f for f in findings if f["code"] == "TRACE-RES-001"]
        self.assertTrue(
            trace_findings,
            f"expected TRACE-RES-001 for missing BRD.01.07.ffff, got {findings}",
        )
        self.assertIn("BRD.01.07.ffff", trace_findings[0]["message"])

    def test_downstream_tag_skipped(self):
        """Downstream pointer (e.g. SPEC-01 → @tdd: TDD-01) skipped.

        Forward references to layers further downstream are informational
        tooling pointers, not upstream lineage. The necessary-upstream
        contract is about UPSTREAM resolution; downstream tags may legitimately
        point at artifacts that don't exist yet (cascade may not have run
        the downstream layer). TRACE-RES-FIXUP-001 Bug 1.
        """
        spec_with_downstream_ref = textwrap.dedent(
            """
            ---
            doc_id: "SPEC-01"
            artifact_type: SPEC
            layer: 6
            ---
            # SPEC-01

            @spec: SPEC-01

            ## §6 Downstream
            TDD document: @tdd: TDD-01 (forward pointer; TDD layer not yet generated).
            """
        ).strip()
        corpus = {
            "docs/06_SPEC/SPEC-01.md": spec_with_downstream_ref,
        }
        findings = _run_lint(corpus)
        trace_findings = [
            f for f in findings if f["code"] == "TRACE-RES-001" and "@tdd:" in f["message"]
        ]
        self.assertFalse(
            trace_findings,
            f"downstream @tdd tag should be skipped, got {trace_findings}",
        )

    def test_self_tag_skipped(self):
        """Self-tag (artifact citing its own doc id) skipped.

        E.g. SPEC-01 emits `@spec: SPEC-01` as a self-identification marker;
        this is not an upstream citation and doesn't need resolution.
        TRACE-RES-FIXUP-001 Bug 1.
        """
        spec_with_only_self_tag = textwrap.dedent(
            """
            ---
            doc_id: "SPEC-01"
            artifact_type: SPEC
            layer: 6
            ---
            # SPEC-01

            Self-tag: @spec: SPEC-01

            ## §1 Document Control
            """
        ).strip()
        corpus = {
            "docs/06_SPEC/SPEC-01.md": spec_with_only_self_tag,
        }
        findings = _run_lint(corpus)
        trace_findings = [f for f in findings if f["code"] == "TRACE-RES-001"]
        self.assertFalse(
            trace_findings,
            f"self-tag should be skipped, got {trace_findings}",
        )

    def test_sibling_reference_not_skipped(self):
        """Same-layer cross-doc reference (e.g. SPEC-02 → @spec: SPEC-01) still resolves.

        Sibling references are real upstream lineage within a layer (a SPEC
        amending or building on another SPEC), not self-tags. The skip rule
        must use doc_id equality (exact match), not layer equality.
        TRACE-RES-FIXUP-001 Bug 1 / Fix 1 sibling-NOT-skipped case.
        """
        spec_02_referencing_missing_sibling = textwrap.dedent(
            """
            ---
            doc_id: "SPEC-02"
            artifact_type: SPEC
            layer: 6
            ---
            # SPEC-02

            @spec: SPEC-02

            ## §4 Builds on
            Extends @spec: SPEC-01 (sibling — must resolve to an existing SPEC-01 doc).
            """
        ).strip()
        corpus = {
            "docs/06_SPEC/SPEC-02.md": spec_02_referencing_missing_sibling,
            # SPEC-01 intentionally absent → sibling reference should fire TRACE-RES-001
        }
        findings = _run_lint(corpus)
        trace_findings = [
            f for f in findings if f["code"] == "TRACE-RES-001" and "SPEC-01" in f["message"]
        ]
        self.assertTrue(
            trace_findings,
            f"sibling reference to missing SPEC-01 should fire TRACE-RES-001, got {findings}",
        )

    def test_index_document_skipped(self):
        """Index docs (artifact_type ending '-INDEX') are excluded from TRACE-RES."""
        index_doc = textwrap.dedent(
            """
            ---
            doc_id: "BRD-00_index"
            artifact_type: BRD-INDEX
            layer: 1
            ---
            # Index

            @brd: BRD-99
            """
        ).strip()
        corpus = {
            "docs/01_BRD/BRD-00_index.md": index_doc,
            "docs/01_BRD/BRD-01.md": _brd_doc(),
        }
        findings = _run_lint(corpus)
        # The index doc references BRD-99 (missing) but should be skipped.
        # Any TRACE-RES finding from the index doc would be a bug.
        index_findings = [
            f for f in findings if f["code"] == "TRACE-RES-001" and "BRD-00_index" in f["path"]
        ]
        self.assertFalse(
            index_findings,
            f"index doc should be skipped, got {index_findings}",
        )


if __name__ == "__main__":
    unittest.main()
