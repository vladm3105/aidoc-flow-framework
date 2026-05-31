"""Unit: each sdd_doc_lint check fires only on its target fixture."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root

FIXTURES = Path(__file__).resolve().parent / "lint_fixtures"

CASES = [
    ("sty01", {"STY01"}),
    ("sty02", {"STY02"}),
    ("sty03", {"STY03"}),
    ("hash01", {"HASH01"}),
    ("csc01", {"CSC01"}),
    ("stale01", {"STALE01"}),
    ("fm01", {"FM01"}),
    ("dg02", {"DG02"}),
    ("th02", {"TH02"}),
    ("struct01", {"STRUCT01"}),
    ("clean", set()),
]


def run_lint_json(fixture_dir: Path) -> list[dict]:
    result = subprocess.run(
        [sys.executable, "-m", "sdd_doc_lint", str(fixture_dir), "--format=json"],
        env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    return json.loads(result.stdout or "[]")


class LintCheckMatrixTests(unittest.TestCase):
    def test_each_fixture_emits_exactly_its_expected_codes(self):
        for dirname, expected_codes in CASES:
            with self.subTest(fixture=dirname):
                fixture_dir = FIXTURES / dirname
                findings = run_lint_json(fixture_dir)
                emitted = {f["code"] for f in findings}
                spurious = emitted - expected_codes
                missing = expected_codes - emitted
                self.assertFalse(
                    missing,
                    f"{dirname}: missing codes {missing}; emitted: {emitted}",
                )
                self.assertFalse(
                    spurious,
                    f"{dirname}: spurious codes {spurious}; emitted: {emitted}",
                )


if __name__ == "__main__":
    unittest.main()
