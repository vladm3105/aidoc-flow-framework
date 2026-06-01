"""Deterministic acceptance: Layer 8 — IPLAN."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


def _is_test_entry(path: str) -> bool:
    """Per task spec: entries whose path starts with 'tests/' or 'test_'."""
    name = path.strip()
    return name.startswith("tests/") or name.startswith("test_")


class LayerIplanTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 8
    LAYER_NAME = "IPLAN"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "IPLAN-01_golden.yaml"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_file_manifest_lists_tests_before_implementation(self):
        with self.golden.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        files = (data.get("file_manifest") or {}).get("files") or []
        self.assertGreaterEqual(
            len(files),
            2,
            "IPLAN-01 §file_manifest: expected >=2 files (tests + implementation)",
        )
        seen_non_test = False
        for entry in files:
            path = str(entry.get("path", ""))
            if _is_test_entry(path):
                self.assertFalse(
                    seen_non_test,
                    f"IPLAN-01 §file_manifest: test entry '{path}' appears after a "
                    "non-test entry; tests must precede implementation files",
                )
            else:
                seen_non_test = True
        # And require at least one of each so the ordering claim is meaningful.
        self.assertTrue(
            any(_is_test_entry(str(e.get("path", ""))) for e in files),
            "IPLAN-01 §file_manifest: no test entries found",
        )
        self.assertTrue(
            seen_non_test,
            "IPLAN-01 §file_manifest: no implementation (non-test) entries found",
        )

    def test_first_session_has_next_session_directive(self):
        with self.golden.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        sessions = (data.get("session_handoff") or {}).get("sessions") or []
        self.assertGreaterEqual(
            len(sessions),
            1,
            "IPLAN-01 §session_handoff: expected at least one session entry",
        )
        directive = sessions[0].get("next_session_directive")
        self.assertTrue(
            isinstance(directive, str) and directive.strip(),
            f"IPLAN-01 §session_handoff: sessions[0].next_session_directive must be a "
            f"non-empty string (got {directive!r})",
        )


if __name__ == "__main__":
    unittest.main()
