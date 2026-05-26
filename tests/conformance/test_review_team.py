"""Conformance: ``REVIEW_CREWS.yaml`` is well-formed against the spec.

The framework owns the *structure* of the review-team crews (REVIEW_TEAM.md), not
any engine's LLM behaviour: every crew references one of the 8 layers and only the
declared persona set, each layer has an author + a review crew whose weights sum
to 100, and the modes are from the closed set.
"""

import unittest

import yaml
from _spec import ARTIFACTS, FRAMEWORK

CREWS = FRAMEWORK / "governance" / "REVIEW_CREWS.yaml"
MODES = {"independent", "sequential", "single_pass"}


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


if __name__ == "__main__":
    unittest.main()
