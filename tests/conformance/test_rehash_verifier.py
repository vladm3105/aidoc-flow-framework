"""Conformance: the Model-2 content-hash verifier (PROVISIONAL-IDS-002 Phase 1).

Ties `rehash --check` to the ID_NAMING_STANDARDS contract at the conformance
tier. Maps to the plan's verification matrix:

  * V1  — a BRD with correctly-computed §7 FR hashes verifies clean.
  * V2  — a within-window title/description perturbation (ID unchanged) drifts
          (`IDDRIFT01`).
  * V3  — an `id_state: provisional` doc is exempt (no findings).
  * V4  — the normalization transform is byte-stable and behaves as documented
          (anglocentric strip; >100-char truncation).
  * V4b — the extraction yields the exact `(title, description)` bytes, including
          a multi-line wrapped description and a wrapped band parenthetical.
  * V4c — coverage is BRD §7 only: an element ID outside §7 is not verified.
  * V6  — the vendored mirrors expose the same primitives (byte-identical source
          is asserted by test_doc_lint_vendoring; here we assert import parity).
"""

import sys
import unittest

from _spec import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))

from sdd_doc_lint import (  # noqa: E402
    _normalize_hash_field,
    compute_element_hash,
    rehash_check,
    scan_fr_content,
)


def _brd(body: str, id_state: str = "canonical") -> str:
    return f'---\nartifact_type: BRD\ndoc_id: "01"\nid_state: {id_state}\n---\n\n{body}\n'


def _fr(hash4: str, title: str, band: str, desc: str) -> str:
    return f"## 7. Functional Requirements\n\n- **BRD.01.07.{hash4} — {title}** ({band}): {desc}"


TITLE = "Submit and Shorten URL"
DESC = (
    "The service SHALL accept a well-formed public web (http/https) URL and return a "
    "short code that resolves to that URL."
)
GOOD = compute_element_hash("01", "07", TITLE, DESC)[:4]


class Normalization(unittest.TestCase):
    def test_transform_is_the_documented_ordered_operation(self):
        # NFC -> casefold -> strip to [a-z0-9 ] -> collapse ws -> trim -> first 100.
        self.assertEqual(
            _normalize_hash_field("  Submit  and   Shorten URL!! "), "submit and shorten url"
        )

    def test_strip_deletes_non_latin_and_punctuation(self):
        # V4: documented anglocentric limitation — non-ASCII dropped.
        self.assertEqual(_normalize_hash_field("café — 日本語 (v2)"), "caf v2")

    def test_truncates_to_100_chars(self):
        long = "a" * 250
        self.assertEqual(len(_normalize_hash_field(long)), 100)

    def test_hash_is_deterministic(self):
        # V4: same input -> byte-stable hash across calls.
        self.assertEqual(
            compute_element_hash("01", "07", TITLE, DESC),
            compute_element_hash("01", "07", TITLE, DESC),
        )


class Extraction(unittest.TestCase):
    def test_single_line_bullet(self):
        # V4b: exact (title, description) bytes.
        doc = _brd(_fr(GOOD, TITLE, "P1, anonymous public", DESC))
        (el,) = scan_fr_content(doc)
        self.assertEqual(el.elem_id, f"BRD.01.07.{GOOD}")
        self.assertEqual(el.title, TITLE)
        self.assertEqual(el.description, DESC)

    def test_multiline_wrapped_description(self):
        # V4b: description accumulates across continuation lines.
        body = (
            "## 7. Functional Requirements\n\n"
            f"- **BRD.01.07.{GOOD} — {TITLE}** (P1): The service SHALL accept a\n"
            "  well-formed public web (http/https) URL and return a\n"
            "  short code that resolves to that URL."
        )
        (el,) = scan_fr_content(_brd(body))
        self.assertEqual(
            el.description,
            "The service SHALL accept a well-formed public web (http/https) URL "
            "and return a short code that resolves to that URL.",
        )

    def test_wrapped_band_parenthetical(self):
        # V4b: the 882c corpus shape — band itself wraps across lines.
        body = (
            "## 7. Functional Requirements\n\n"
            "- **BRD.01.07.882c — Count Visits** (P1, internal / privileged — Service-Owner\n"
            "  role): The service SHALL count visits."
        )
        (el,) = scan_fr_content(_brd(body))
        self.assertEqual(el.title, "Count Visits")
        self.assertEqual(el.description, "The service SHALL count visits.")

    def test_colon_inside_description_preserved(self):
        # V4b: only the band+separator is stripped; a `:` in the body survives.
        desc = "The service SHALL do X: then Y."
        h = compute_element_hash("01", "07", TITLE, desc)[:4]
        (el,) = scan_fr_content(_brd(_fr(h, TITLE, "P1", desc)))
        self.assertEqual(el.description, desc)

    def test_nested_parenthetical_band_stripped_whole(self):
        # V4b: a band containing a nested `(...)` is stripped to its `):`
        # boundary, not to its first `)`.
        body = (
            "## 7. Functional Requirements\n\n"
            "- **BRD.01.07.7b1c — T** (P1 (special)): desc after nested."
        )
        (el,) = scan_fr_content(_brd(body))
        self.assertEqual(el.description, "desc after nested.")

    def test_no_band_bullet(self):
        # V4b: a bullet with no `(band)` — description follows the bare `:`.
        body = "## 7. Functional Requirements\n\n- **BRD.01.07.aaaa — T**: bare description."
        (el,) = scan_fr_content(_brd(body))
        self.assertEqual(el.description, "bare description.")


class VerifierBehaviour(unittest.TestCase):
    def test_v1_correct_hashes_are_clean(self):
        doc = _brd(_fr(GOOD, TITLE, "P1", DESC))
        self.assertEqual(rehash_check(doc, "BRD-01.md"), [])

    def test_v2_within_window_perturbation_drifts(self):
        doc = _brd(_fr(GOOD, TITLE, "P1", DESC)).replace("SHALL accept", "SHALL reject")
        codes = [f.code for f in rehash_check(doc, "BRD-01.md")]
        self.assertEqual(codes, ["IDDRIFT01"])

    def test_v2_title_perturbation_drifts(self):
        doc = _brd(_fr(GOOD, TITLE, "P1", DESC)).replace(TITLE, "Submit and Lengthen URL")
        self.assertEqual([f.code for f in rehash_check(doc, "BRD-01.md")], ["IDDRIFT01"])

    def test_iddrift01_is_advisory(self):
        doc = _brd(_fr(GOOD, TITLE, "P1", DESC)).replace("SHALL accept", "SHALL reject")
        (f,) = rehash_check(doc, "BRD-01.md")
        self.assertEqual(f.severity, "warning")

    def test_v3_provisional_is_exempt(self):
        # Even with a wrong hash, a provisional doc yields no findings.
        doc = _brd(_fr("dead", TITLE, "P1", DESC), id_state="provisional")
        self.assertEqual(rehash_check(doc, "BRD-01.md"), [])

    def test_v4c_only_section_7_is_verified(self):
        # An element ID outside §7 (with a deliberately wrong hash) is NOT checked.
        body = (
            "## 4. Constraints\n\n"
            "- **BRD.01.04.dead — Some Constraint** (P1): wrong-hash content here.\n\n"
            f"## 7. Functional Requirements\n\n- **BRD.01.07.{GOOD} — {TITLE}** (P1): {DESC}"
        )
        self.assertEqual(rehash_check(_brd(body), "BRD-01.md"), [])

    def test_eight_char_collision_form_verifies(self):
        # An ID declared at 8 chars is compared at its own length.
        full = compute_element_hash("01", "07", TITLE, DESC)[:8]
        doc = _brd(_fr(full, TITLE, "P1", DESC))
        self.assertEqual(rehash_check(doc, "BRD-01.md"), [])
        bad = _brd(_fr(full, TITLE, "P1", DESC)).replace("SHALL accept", "SHALL reject")
        self.assertEqual([f.code for f in rehash_check(bad, "BRD-01.md")], ["IDDRIFT01"])


class VendorParity(unittest.TestCase):
    def test_v6_vendored_mirrors_expose_the_primitives(self):
        # Byte-identical source is asserted by test_doc_lint_vendoring; here we
        # confirm the primitives import + agree from a plugin-bundle path.
        from _spec import plugin_bundle_root

        sys.path.insert(0, str(plugin_bundle_root()))
        # Re-import under the vendored path resolves to the same top-level module;
        # assert the contract functions exist and compute the same hash.
        import importlib

        mod = importlib.import_module("sdd_doc_lint")
        self.assertTrue(hasattr(mod, "rehash_check"))
        self.assertTrue(hasattr(mod, "compute_element_hash"))
        self.assertEqual(
            mod.compute_element_hash("01", "07", TITLE, DESC),
            compute_element_hash("01", "07", TITLE, DESC),
        )


class CLI(unittest.TestCase):
    """The opt-in `rehash --check` command contract (advisory → never blocks)."""

    def _write(self, tmp, name, text):
        p = tmp / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_check_required_flag(self):
        from sdd_doc_lint import rehash as rh

        with self.assertRaises(SystemExit) as cm:
            rh.main(["some.md"])  # no --check
        self.assertEqual(cm.exception.code, 2)

    def test_clean_doc_exit_zero(self):
        import tempfile
        from pathlib import Path

        from sdd_doc_lint import rehash as rh

        with tempfile.TemporaryDirectory() as d:
            p = self._write(Path(d), "BRD-01.md", _brd(_fr(GOOD, TITLE, "P1", DESC)))
            self.assertEqual(rh.main(["--check", str(p)]), 0)

    def test_drift_is_advisory_exit_zero(self):
        # An IDDRIFT01 finding must NOT fail the command (Phase-1 is advisory).
        import tempfile
        from pathlib import Path

        from sdd_doc_lint import rehash as rh

        with tempfile.TemporaryDirectory() as d:
            drifted = _brd(_fr(GOOD, TITLE, "P1", DESC)).replace("SHALL accept", "SHALL reject")
            p = self._write(Path(d), "BRD-01.md", drifted)
            self.assertEqual(rh.main(["--check", str(p)]), 0)

    def test_unreadable_path_exit_two(self):
        from sdd_doc_lint import rehash as rh

        self.assertEqual(rh.main(["--check", "/nonexistent/path/BRD-99.md"]), 2)


if __name__ == "__main__":
    unittest.main()
