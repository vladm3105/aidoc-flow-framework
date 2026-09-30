"""Conformance: the CI & autonomous change-integration standard (#815).

`framework/governance/CI_AUTONOMOUS_PR_STANDARD.md` (CHG-26, 0.68.0 MINOR)
codifies the six engine-neutral invariants upstreamed from the downstream
enterprise standard. This guard pins:

- presence: the doc exists and is registered in the governance census
  (`test_governance.py` EXPECTED_FILES);
- document control: a GD-24 block whose Framework Version tracks
  `framework/VERSION`;
- completeness: all six invariant headings are present;
- engine-neutrality (D-0013 / GD-06): no platform-mechanics tokens —
  GitHub Actions, Taskfile/go-task, scanner/product names, CLI merge
  commands, trigger path filters, or downstream repo paths may appear.
  Platform bindings belong in consumer adaptation profiles, not the spec.
"""

import re
import unittest

import yaml

from _spec import FRAMEWORK

DOC = FRAMEWORK / "governance" / "CI_AUTONOMOUS_PR_STANDARD.md"

# Mechanics that belong in a consumer's adaptation profile, never in the
# engine-agnostic spec. Each entry is a literal substring; matches are
# case-sensitive except where noted inline.
FORBIDDEN = (
    "GitHub Actions",
    "Taskfile",
    "go-task",
    "Playwright",
    "trivy",
    "gitleaks",
    "atlas",
    "LiteLLM",
    "ai-review.yml",
    "CODEOWNERS",
    "b-local-privy",
    "aidoc-flow-local-ci",
    "gh pr merge",
    "--auto",
    "paths:",
    "paths-ignore",
)

INVARIANTS = (
    "Single unified verification harness",
    "Concentric verification latency budgets",
    "Required checks report conclusively",
    "Two-pass independent review",
    "Merge-conflict authority classes",
    "Anti-blind closure",
)


class CiAutonomousPrStandard(unittest.TestCase):
    def test_doc_exists(self):
        self.assertTrue(DOC.is_file(), f"missing standard doc: {DOC}")

    def test_document_control_tracks_version(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^## Document Control", "no GD-24 block")
        current = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        match = re.search(
            r"^\|\s*Framework Version\s*\|\s*(\S+?)\s*\|",
            text,
            re.MULTILINE,
        )
        self.assertIsNotNone(match, "no Framework Version row")
        self.assertEqual(match.group(1), current, "Framework Version lags VERSION")

    def test_six_invariants_present(self):
        text = DOC.read_text(encoding="utf-8")
        for invariant in INVARIANTS:
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, text, f"invariant missing: {invariant}")

    def test_engine_neutral(self):
        text = DOC.read_text(encoding="utf-8")
        hits = [token for token in FORBIDDEN if token in text]
        self.assertEqual(
            hits,
            [],
            f"platform-mechanics tokens leaked into the engine-agnostic spec: {hits}",
        )

    def test_adaptation_surface_covers_ci_bindings(self):
        # #817: the standard tells consumers to bind ceilings, runners,
        # workflows, and branch policies in their adaptation profile. The
        # closed surface must declare that knob and ADAPTATION.md must
        # document it — otherwise the pointer names a binding place that
        # does not exist.
        with (FRAMEWORK / "governance" / "ADAPTATION_SURFACE.yaml").open(
            encoding="utf-8"
        ) as fh:
            surface = yaml.safe_load(fh)
        names = [k["name"] for k in surface["knobs"]]
        self.assertIn(
            "ci_bindings",
            names,
            "standard points consumers at the adaptation profile, "
            "but the surface declares no CI-binding knob",
        )
        entry = next(k for k in surface["knobs"] if k["name"] == "ci_bindings")
        self.assertEqual(
            entry["type"], "map[string, string]", "ci_bindings retyped"
        )
        self.assertLessEqual(
            set(entry["consumers"]),
            set(surface["consumer_roles"]),
            "ci_bindings points at an undeclared consumer role",
        )
        self.assertEqual(entry["default"], "{}", "ci_bindings default drifted")
        adaptation = (FRAMEWORK / "governance" / "ADAPTATION.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "ci_bindings",
            adaptation,
            "surface declares ci_bindings but ADAPTATION.md documents no such knob",
        )

    def test_review_team_disambiguation(self):
        # The #815 triage anchor: REVIEW_TEAM.md "conflict resolution" is
        # lens-verdict reconciliation, NOT merge-conflict authority. The
        # standard must state the disambiguation so readers do not conflate
        # Invariant 5 with the lens machinery.
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("REVIEW_TEAM.md", text, "no REVIEW_TEAM.md cross-reference")
        self.assertRegex(
            text,
            r"(?i)must not be conflated|disjoint from|different concept",
            "no lens-vs-merge conflict disambiguation",
        )


if __name__ == "__main__":
    unittest.main()
