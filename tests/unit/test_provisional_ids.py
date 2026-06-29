"""Unit: PROVISIONAL-IDS-001 — provisional ID-state + PH01 lowercase fix.

- `PH01` now flags BARE lowercase `xxxx` via `(?<!\\.)\\bx{3,}\\b`, while leaving a
  full-element-id hash segment (`BRD.01.07.xxxx`, always `.`-preceded) to ID03 —
  no double-report (Pass-2 F4).
- `id_state: provisional` in frontmatter emits one doc-level `PROV01` advisory;
  `canonical`/absent is silent; an unknown value is flagged.
- The regex-valid `0000` provisional literal matches `ELEM_FORM` + `_FR_BULLET`,
  while `xxxx` matches neither.
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root  # noqa: E402

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import _PLACEHOLDERS, lint_path  # noqa: E402
from sdd_doc_lint.trace_graph import ELEM_FORM  # noqa: E402

_FR_BULLET = re.compile(r"^\s*-\s+\*\*([A-Z]+\.[0-9]+\.[0-9]+\.[a-f0-9]+)\s+[—–-]\s+[^*]+\*\*")
# The PH01 lowercase pattern is the last entry added to _PLACEHOLDERS.
_PH_LOWER = re.compile(r"(?<!\.)\bx{3,}\b")


def _doc(doc_id, artifact_type, body, extra_fm=""):
    fm = f"doc_id: {doc_id}\nartifact_type: {artifact_type}\n{extra_fm}"
    return (f"{doc_id}.md", f"---\n{fm}---\n\n{body}\n")


def _codes(findings):
    return [f.code for f in findings]


class Ph01Lowercase(unittest.TestCase):
    def test_lowercase_pattern_is_registered(self):
        self.assertIn(_PH_LOWER.pattern, [p.pattern for p in _PLACEHOLDERS])

    def test_look_behind_behaviour(self):
        # Bare runs caught; element-id hash segment and valid hashes/ordinals not.
        self.assertEqual(_PH_LOWER.findall("placeholder: xxxx"), ["xxxx"])
        self.assertEqual(_PH_LOWER.findall('hash: "xxxx"'), ["xxxx"])
        self.assertEqual(_PH_LOWER.findall("- **BRD.01.07.xxxx — F** (P1): x."), [])
        self.assertEqual(_PH_LOWER.findall("a7f3"), [])
        self.assertEqual(_PH_LOWER.findall("BRD.01.07.0001"), [])
        self.assertEqual(_PH_LOWER.findall("xx"), [])  # {3,} floor

    def _lint(self, body, extra_fm=""):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            rel, text = _doc("BRD-01", "BRD", body, extra_fm)
            (tdp / rel).write_text(text, encoding="utf-8")
            return lint_path(tdp)

    def test_bare_lowercase_xxxx_flagged_by_ph01(self):
        codes = _codes(self._lint("Some field: xxxx leftover."))
        self.assertIn("PH01", codes)

    def test_full_element_id_xxxx_is_id03_only_not_ph01(self):
        # The element-id hash segment is ID03's domain; PH01 must NOT also fire.
        findings = self._lint("## 7. Functional Requirements\n\n- **BRD.01.07.xxxx — F** (P1): x.")
        ph01 = [f for f in findings if f.code == "PH01"]
        id03 = [f for f in findings if f.code == "ID03"]
        self.assertEqual(ph01, [], [f.message for f in ph01])
        self.assertTrue(id03, "expected ID03 on the malformed element id")


class ProvisionalState(unittest.TestCase):
    def _lint(self, extra_fm):
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            rel, text = _doc("BRD-01", "BRD", "## 1. Document Control\n\nbody.", extra_fm)
            (tdp / rel).write_text(text, encoding="utf-8")
            return [f for f in lint_path(tdp) if f.code == "PROV01"]

    def test_provisional_emits_one_advisory(self):
        prov = self._lint("id_state: provisional\n")
        self.assertEqual(len(prov), 1)
        self.assertEqual(prov[0].severity, "warning")
        self.assertIn("canonicalize", prov[0].message)

    def test_canonical_is_silent(self):
        self.assertEqual(self._lint("id_state: canonical\n"), [])

    def test_absent_is_silent(self):
        self.assertEqual(self._lint(""), [])

    def test_unknown_state_flagged(self):
        prov = self._lint("id_state: draft\n")
        self.assertEqual(len(prov), 1)
        self.assertIn("unknown id_state", prov[0].message)


class ProvisionalFormValidity(unittest.TestCase):
    def test_0000_and_ordinal_are_elem_form_valid_xxxx_is_not(self):
        self.assertTrue(ELEM_FORM.match("BRD.01.07.0000"))
        self.assertTrue(ELEM_FORM.match("BRD.01.07.0001"))
        self.assertFalse(ELEM_FORM.match("BRD.01.07.xxxx"))

    def test_0000_is_fr_scanner_visible_xxxx_is_not(self):
        self.assertTrue(_FR_BULLET.match("- **BRD.01.07.0000 — Feature** (P1): a thing."))
        self.assertIsNone(_FR_BULLET.match("- **BRD.01.07.xxxx — Feature** (P1): a thing."))

    def test_duplicate_0000_definition_trips_hash01(self):
        # Two element DEFINITIONS with the same 0000 → HASH01 (uniqueness applies
        # regardless of id_state) — forces distinct ordinals. HASH01 recognizes
        # the definition shapes `- **ID**`, `## ID`, and YAML `id:` (NOT the BRD
        # FR-bullet `- **ID — title**`, a separate pre-existing case).
        body = "- **BRD.01.07.0000**: first.\n- **BRD.01.07.0000**: second."
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            rel, text = _doc("BRD-01", "BRD", body, "id_state: provisional\n")
            (tdp / rel).write_text(text, encoding="utf-8")
            self.assertIn("HASH01", _codes(lint_path(tdp)))


if __name__ == "__main__":
    unittest.main()
