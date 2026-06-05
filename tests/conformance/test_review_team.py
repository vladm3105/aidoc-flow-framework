"""Conformance: ``REVIEW_CREWS.yaml`` is well-formed against the spec.

The framework owns the *structure* of the review-team crews (REVIEW_TEAM.md), not
any engine's LLM behaviour: every crew references one of the 8 layers and only the
declared persona set, each layer has an author + a review crew whose weights sum
to 100, and the modes are from the closed set.

Includes the CHAOS-SEC-SPLIT-001 invariants (D-0030): every layer except IPLAN
carries both `chaos_engineer` and `security_engineer` lenses; IPLAN carries
`chaos_engineer` only; the lens-to-agent mapping in
``review-team/SKILL.md`` covers both new lenses; and the per-layer weight tables
in ``chaos-engineer.md`` + ``security-engineer.md`` match REVIEW_CREWS.yaml
exactly (cross-place rationale consistency — REVIEW_CREWS.yaml is the single
source of truth).
"""

import re
import unittest
from pathlib import Path

import yaml
from _spec import ARTIFACTS, FRAMEWORK

CREWS = FRAMEWORK / "governance" / "REVIEW_CREWS.yaml"
MODES = {"independent", "sequential", "single_pass"}

REPO_ROOT = FRAMEWORK.parent
PLUGIN_AGENTS = REPO_ROOT / "platforms" / "claude-code-plugin" / "agents"
REVIEW_TEAM_SKILL = (
    REPO_ROOT / "platforms" / "claude-code-plugin" / "skills" / "review-team" / "SKILL.md"
)


def _parse_weight_table(path: Path, lens_name: str) -> dict[str, int]:
    """Parse the per-layer weight table from an agent brief.

    Looks for a markdown table with rows shaped like ``| BRD | 12 | ... |`` where
    the first column is a layer code (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN) and the
    second is the integer weight. Returns {layer: weight}.
    """
    text = path.read_text(encoding="utf-8")
    layers = set(ARTIFACTS)
    weights: dict[str, int] = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*([A-Z]+)\s*\|\s*(\d+)\s*\|", line)
        if m and m.group(1) in layers:
            weights[m.group(1)] = int(m.group(2))
    if not weights:
        raise AssertionError(f"{path}: no per-layer weight table rows found for {lens_name}")
    return weights


class ReviewCrews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(CREWS.read_text(encoding="utf-8"))
        cls.personas = set(cls.data["personas"])
        cls.crews = cls.data["crews"]

    def test_personas_unique_and_nonempty(self):
        names = self.data["personas"]
        self.assertTrue(names, "no personas declared")
        self.assertEqual(len(names), len(set(names)), f"duplicate personas: {names}")

    def test_default_mode_valid(self):
        self.assertIn(self.data["default_mode"], MODES)

    def test_crews_cover_exactly_the_eight_layers(self):
        self.assertEqual(set(self.crews), set(ARTIFACTS), "crews must map exactly the 8 layers")

    def test_each_crew_is_well_formed(self):
        for layer, crew in self.crews.items():
            with self.subTest(layer=layer):
                self.assertIn(
                    crew["author"], self.personas, f"{layer}: unknown author {crew['author']!r}"
                )
                review = crew["review"]
                self.assertTrue(review, f"{layer}: empty review crew")
                unknown = set(review) - self.personas
                self.assertEqual(unknown, set(), f"{layer}: unknown review personas {unknown}")
                self.assertEqual(
                    sum(review.values()),
                    100,
                    f"{layer}: review weights must sum to 100 (got {sum(review.values())})",
                )
                if "mode" in crew:
                    self.assertIn(crew["mode"], MODES, f"{layer}: bad mode {crew['mode']!r}")

    # CHAOS-SEC-SPLIT-001 (D-0030) invariants below ----------------------------

    def test_no_adversary_persona_remains(self):
        """The legacy `adversary` lens is removed; partition into chaos+security."""
        self.assertNotIn(
            "adversary",
            self.personas,
            "D-0030: `adversary` lens must be partitioned into "
            "`chaos_engineer` + `security_engineer`",
        )

    def test_new_lenses_are_registered(self):
        for name in ("chaos_engineer", "security_engineer"):
            self.assertIn(
                name,
                self.personas,
                f"D-0030: `{name}` must be in the personas registry",
            )

    def test_chaos_security_lens_presence_per_layer(self):
        """Every layer except IPLAN has both new lenses; IPLAN has chaos only.

        Catches G8 (the asymmetric IPLAN choice) regressing silently — if a
        future PR adds security_engineer to IPLAN, that's a real change that
        deserves its own decision; this test flags the drift.
        """
        for layer, crew in self.crews.items():
            review = crew["review"]
            with self.subTest(layer=layer):
                self.assertIn(
                    "chaos_engineer",
                    review,
                    f"D-0030: {layer} review crew must include `chaos_engineer`",
                )
                if layer == "IPLAN":
                    self.assertNotIn(
                        "security_engineer",
                        review,
                        "D-0030: IPLAN is chaos-only (security lives upstream in ADR/SPEC)",
                    )
                else:
                    self.assertIn(
                        "security_engineer",
                        review,
                        f"D-0030: {layer} review crew must include `security_engineer`",
                    )

    def test_lens_to_agent_mapping_has_both_new_rows(self):
        text = REVIEW_TEAM_SKILL.read_text(encoding="utf-8")
        for row in (
            "| `chaos_engineer` | `chaos-engineer` |",
            "| `security_engineer` | `security-engineer` |",
        ):
            self.assertIn(
                row,
                text,
                f"D-0030: review-team/SKILL.md must declare mapping row: {row}",
            )
        self.assertNotIn(
            "| `adversary` |",
            text,
            "D-0030: legacy `adversary` mapping row must be removed",
        )

    def test_agent_brief_weights_match_review_crews(self):
        """Cross-place consistency: agent briefs' per-layer tables match REVIEW_CREWS.yaml.

        This is the load-bearing rationale-propagation check (Pass 4 of the
        CHAOS-SEC-SPLIT-001 plan). REVIEW_CREWS.yaml is the single source of
        truth; the briefs read it. If a future edit changes one without the
        other, this test fails.
        """
        chaos_weights = _parse_weight_table(PLUGIN_AGENTS / "chaos-engineer.md", "chaos_engineer")
        security_weights = _parse_weight_table(
            PLUGIN_AGENTS / "security-engineer.md", "security_engineer"
        )
        for layer, crew in self.crews.items():
            review = crew["review"]
            with self.subTest(layer=layer, lens="chaos_engineer"):
                expected = review.get("chaos_engineer")
                self.assertIsNotNone(
                    expected,
                    f"{layer}: chaos_engineer weight missing in REVIEW_CREWS.yaml",
                )
                self.assertEqual(
                    chaos_weights.get(layer),
                    expected,
                    f"D-0030: chaos-engineer.md {layer} weight ({chaos_weights.get(layer)!r}) "
                    f"!= REVIEW_CREWS.yaml ({expected})",
                )
            if layer != "IPLAN":
                with self.subTest(layer=layer, lens="security_engineer"):
                    expected = review.get("security_engineer")
                    self.assertEqual(
                        security_weights.get(layer),
                        expected,
                        f"D-0030: security-engineer.md {layer} weight "
                        f"({security_weights.get(layer)!r}) != REVIEW_CREWS.yaml ({expected})",
                    )


if __name__ == "__main__":
    unittest.main()
