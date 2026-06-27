"""Unit: tools/sdd_doc_lint/trace_graph.py — shared @-tag trace primitives
(CFB-PR-2 DD-1).

Locks in the parsing/locating contract that BOTH the backward walker
(`trace_walk`) and the forward coverage engine depend on — notably the DD-8
multi-`@brd` pipe behavior the coverage predicate's OR-grouping relies on.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from sdd_doc_lint.trace_graph import (  # noqa: E402
    doc_id_from_token,
    emit_tags,
    locate_doc,
)


class DocIdFromToken(unittest.TestCase):
    def test_doc_form_passthrough(self):
        self.assertEqual(doc_id_from_token("BRD-01"), "BRD-01")

    def test_element_form_reduces_to_host_doc(self):
        self.assertEqual(doc_id_from_token("BRD.01.07.6c3f"), "BRD-01")
        self.assertEqual(doc_id_from_token("SPEC.12.05.abcd"), "SPEC-12")

    def test_garbage_is_none(self):
        for tok in ("", "nope", "BRD.01", "BRD.01.07.XYZ", "brd-01"):
            self.assertIsNone(doc_id_from_token(tok), tok)


class EmitTags(unittest.TestCase):
    def test_single_tag(self):
        self.assertEqual(emit_tags("trace: @prd: PRD.01.09.aaaa"), ["PRD.01.09.aaaa"])

    def test_multi_brd_pipe_separated_yields_each(self):
        # DD-8: the value capture terminates on `|`, so a multi-@brd line is
        # parsed as separate tags (the coverage predicate OR-groups them).
        line = "@brd: BRD.01.07.aaaa | @brd: BRD.02.07.bbbb | @prd: PRD.01.09.cccc"
        self.assertEqual(
            emit_tags(line),
            ["BRD.01.07.aaaa", "BRD.02.07.bbbb", "PRD.01.09.cccc"],
        )

    def test_no_tags(self):
        self.assertEqual(emit_tags("plain prose, no tags here"), [])


class LocateDoc(unittest.TestCase):
    def test_resolves_under_layer_folder(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "01_BRD").mkdir()
            f = root / "01_BRD" / "BRD-01.md"
            f.write_text("x", encoding="utf-8")
            self.assertEqual(locate_doc("BRD-01", root), f)

    def test_missing_is_none(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(locate_doc("BRD-99", Path(td)))
            self.assertIsNone(locate_doc("garbage", Path(td)))


if __name__ == "__main__":
    unittest.main()
