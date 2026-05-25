"""Conformance: the EARS layer states ONE statement model (FRWK-REVIEW #4b).

Locks the five canonical EARS patterns + the `THE … SHALL` grammar across the
template, README, and index so they cannot silently diverge again (the drift
#4b fixed, where the template said "four", the index said "five" in a non-EARS
`… THEN …` form, and the platforms had drifted to 5- and 6-pattern variants).

Canonical EARS (decision D1 = A): Ubiquitous, Event-driven (WHEN),
State-driven (WHILE), Optional (WHERE), Unwanted (IF) — the response clause is
always `THE [component] SHALL …`, never a `THEN` connective. `WITHIN [timing]`
is a documented framework extension. "Complex" is composition of the base
patterns, not a sixth type.
"""

import re
import unittest

import yaml
from _spec import FRAMEWORK

EARS = FRAMEWORK / "layers" / "03_EARS"
TEMPLATE = EARS / "EARS-TEMPLATE.yaml"
README = EARS / "README.md"
INDEX = EARS / "EARS-00_index.TEMPLATE.md"

# The five canonical pattern names (token check, case-insensitive).
PATTERN_TOKENS = ("ubiquitous", "event", "state", "optional", "unwanted")
# Structured block keys the template must carry under `requirements`.
TEMPLATE_BLOCKS = (
    "event_driven",
    "state_driven",
    "optional_feature",
    "unwanted_behavior",
    "ubiquitous",
)
# `THEN` immediately introducing a bracketed response = the non-EARS connective
# (e.g. "WHEN [trigger] THEN [response]"). Descriptive mentions like
# "'THEN' as the response connective" or "(no `THEN`)" carry no `THEN [`.
_BAD_THEN = re.compile(r"THEN\s*\[")


class EarsModel(unittest.TestCase):
    def test_template_defines_five_pattern_blocks(self):
        doc = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
        reqs = doc.get("requirements", {})
        missing = [b for b in TEMPLATE_BLOCKS if b not in reqs]
        self.assertEqual(missing, [], f"EARS template missing pattern blocks: {missing}")

    def test_prose_files_name_all_five_patterns(self):
        for f in (README, INDEX):
            text = f.read_text(encoding="utf-8").lower()
            missing = [t for t in PATTERN_TOKENS if t not in text]
            self.assertEqual(
                missing,
                [],
                f"{f.name} does not name all five EARS patterns; missing: {missing}",
            )
            self.assertIn("where [", text, f"{f.name} missing the Optional/WHERE pattern grammar")

    def test_no_then_connective(self):
        bad = []
        for f in (TEMPLATE, README, INDEX):
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if _BAD_THEN.search(line):
                    bad.append(f"{f.name}:{i}")
        self.assertEqual(
            bad,
            [],
            "EARS uses 'THE [component] SHALL [response]', never a 'THEN [response]' "
            f"connective; found: {bad}",
        )


if __name__ == "__main__":
    unittest.main()
