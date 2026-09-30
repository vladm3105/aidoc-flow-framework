"""Conformance: self-learn governance carries no direct-write exemption (CHG-17)
and no vendor-coupled machinery (CHG-18)."""

import re
import unittest

from _spec import FRAMEWORK

SELF_LEARNING = FRAMEWORK / "governance" / "SELF_LEARNING.md"
FRAMEWORK_SKILL = FRAMEWORK / "skills" / "self-learn" / "SKILL.md"

# Language of the removed solo-project exemption (CHG-17 purged it).
EXEMPTION_PATTERNS = [
    re.compile(r"writes directly to governance documents for solo projects"),
    re.compile(r"requiring a CHG record[\s\S]*adds unnecessary latency"),
    re.compile(r"Rules for direct governance updates"),
    re.compile(r"revert to the\nCHG-mediated process"),
]

# Language the authorization routing must carry instead.
REQUIRED_PATTERNS = [
    re.compile(r"authorizing CHG"),
    re.compile(r"In-Progress IPLAN"),
    re.compile(r"no exemption", re.IGNORECASE),
    re.compile(r"self-approved C3"),
]


class SelfLearnAuthorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SELF_LEARNING.read_text(encoding="utf-8")

    def test_no_direct_write_exemption(self):
        for pattern in EXEMPTION_PATTERNS:
            with self.subTest(pattern=pattern.pattern[:50]):
                self.assertIsNone(
                    pattern.search(self.text),
                    f"exemption language still present: {pattern.pattern[:60]}",
                )

    def test_chg_iplan_routing_present(self):
        for pattern in REQUIRED_PATTERNS:
            with self.subTest(pattern=pattern.pattern[:50]):
                self.assertIsNotNone(
                    pattern.search(self.text),
                    f"authorization routing missing: {pattern.pattern[:60]}",
                )


# Vendor-coupled harness paths/schemas must not appear in the shared
# framework skill copy (CHG-18) — harness artifacts are best-effort inputs
# resolved at runtime, never hardcoded names. Each pattern below is proven to
# fire on the archived pre-change copy (CHG-18 probe: 4/4); session.post and
# learn-inject never occurred in the skill file, so they are not pinned here —
# the spec mentions them only as illustrative e.g.-framed examples.
DECOUPLING_PATTERNS = [
    re.compile(r"history_fts"),
    re.compile(r"tool_input"),
    re.compile(r"checkpoint\.md"),
    re.compile(r"checkpoint §7/§8"),
]

# The Tier model + learning/ folder decision must be present (CHG-18).
TIER_PATTERNS = [
    re.compile(r"Two-Tier Project Knowledge Architecture"),
    re.compile(r"Tier 1"),
    re.compile(r"Tier 2"),
    re.compile(r"\.aidoc/learning/learnings\.md"),
]


class SelfLearnDecoupling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = FRAMEWORK_SKILL.read_text(encoding="utf-8")
        cls.spec = SELF_LEARNING.read_text(encoding="utf-8")

    def test_no_vendor_coupled_tokens_in_framework_skill(self):
        for pattern in DECOUPLING_PATTERNS:
            with self.subTest(pattern=pattern.pattern[:50]):
                self.assertIsNone(
                    pattern.search(self.skill),
                    f"coupled token still present: {pattern.pattern[:60]}",
                )

    def test_tier_model_present(self):
        for pattern in TIER_PATTERNS:
            with self.subTest(pattern=pattern.pattern[:50]):
                self.assertIsNotNone(
                    pattern.search(self.spec),
                    f"tier marker missing: {pattern.pattern[:60]}",
                )


if __name__ == "__main__":
    unittest.main()
