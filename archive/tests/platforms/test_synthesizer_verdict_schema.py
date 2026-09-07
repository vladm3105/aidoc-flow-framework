"""Conformance: synthesizer verdict.json output schema.

The synthesizer agent's output contract (platforms/claude-code-plugin/
agents/synthesizer.md §"Field semantics" for `findings[]`) requires
every finding in `verdict.json` to carry a `check` field — the playbook
citation the finding survived on (either canonical `C\\d+` or
`beyond-checklist:<tag>` form).

Surfaced by SPEC-RT-001 live cascade (2026-06-09): the synthesizer for
that run dropped the `check` field from verdict.json findings despite
lens slots carrying it correctly. The output schema in
agents/synthesizer.md previously did not list `check` as a required
field; downstream consumers (fixers, traceability matrices,
observability dashboards) read findings[*].check and got nothing.

This test enforces the now-explicit contract: every finding in every
committed verdict.json under examples/<name>/.aidoc/review/ must carry
a syntactically valid `check` value.
"""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# Canonical check id (per playbook §"Required evidence checks" headings)
# OR beyond-checklist with a non-empty principle tag.
_CHECK_ID_RE = re.compile(r"^(C\d+|beyond-checklist:[A-Za-z0-9_.\-]+)$")


def _collect_verdict_files() -> list[Path]:
    """Find every COMMITTED verdict.json under examples/<name>/.aidoc/review/.

    Uses `git ls-files` so the test validates repo invariants, not local
    working-tree artifacts (cascade outputs in progress may be untracked).
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "examples/*/.aidoc/review/**/verdict.json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    paths = [REPO_ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()]
    return sorted(p for p in paths if p.exists())


def _synthesizer_contract_text() -> str:
    p = REPO_ROOT / "platforms" / "claude-code-plugin" / "agents" / "synthesizer.md"
    return p.read_text(encoding="utf-8")


class SynthesizerVerdictSchema(unittest.TestCase):
    """Verdict.json findings must carry `check` per synthesizer contract."""

    def test_synthesizer_contract_lists_check_as_required(self):
        """agents/synthesizer.md must list `check` in the findings[] schema."""
        text = _synthesizer_contract_text()
        # The example JSON block under §"verdict.json" must show check
        self.assertIn('"check"', text, "synthesizer contract missing check in example JSON")
        # Field semantics paragraph must call out check as required
        self.assertRegex(
            text,
            r"`check`.*(playbook|citation|hard contract)",
            "synthesizer contract Field semantics must describe check field",
        )

    def test_every_committed_verdict_findings_carry_check(self):
        """Every finding in every synthesizer-produced verdict.json must have a `check` value.

        Synthetic verdicts (hand-rolled by the harness for STY03 auto-
        remediation per AUTO-REMEDIATE-001) are exempt — they bypass the
        synthesizer agent entirely and carry their own `synthetic: true`
        marker.
        """
        files = _collect_verdict_files()
        self.assertTrue(files, "no verdict.json files found under examples/")

        for verdict_path in files:
            with self.subTest(verdict=str(verdict_path.relative_to(REPO_ROOT))):
                data = json.loads(verdict_path.read_text(encoding="utf-8"))
                if data.get("synthetic") is True:
                    continue  # hand-rolled synthetic verdict; not synthesizer output
                findings = data.get("findings", [])
                if not findings:
                    continue  # empty findings array is acceptable
                for i, f in enumerate(findings):
                    fid = f.get("id", f"<no-id-at-index-{i}>")
                    self.assertIn(
                        "check",
                        f,
                        f"{verdict_path.name} finding[{i}] id={fid!r} missing required `check` field",
                    )
                    check_val = f["check"]
                    self.assertIsInstance(
                        check_val,
                        str,
                        f"finding {fid!r} check must be string, got {type(check_val)}",
                    )
                    self.assertRegex(
                        check_val,
                        _CHECK_ID_RE,
                        f"finding {fid!r} check={check_val!r} not in C\\d+ or beyond-checklist:<tag> form",
                    )

    def test_synthesizer_example_json_check_matches_regex(self):
        """The example verdict.json in the contract must use a valid check id."""
        text = _synthesizer_contract_text()
        # Extract the `"check": "..."` line(s) from the example JSON block
        matches = re.findall(r'"check":\s*"([^"]+)"', text)
        self.assertTrue(matches, "synthesizer contract example JSON has no check field")
        for val in matches:
            self.assertRegex(
                val,
                _CHECK_ID_RE,
                f"synthesizer contract example check={val!r} doesn't match canonical form",
            )


if __name__ == "__main__":
    unittest.main()
