"""Unit: the Gherkin→YAML BDD transcoder (YAML-BDD-SCHEMA D-6).

Verifies the parser/emitter engine handles the corpus's Gherkin constructs and —
the load-bearing contract (Pass-2 LB-2) — copies each ``@scenario-id:`` VERBATIM
into ``id:`` so downstream ``@bdd:`` citations stay stable.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import yaml  # noqa: E402
from gherkin_to_bdd_yaml import (  # noqa: E402
    parse_gherkin_feature,
    render_scenarios_yaml,
    transcode_markdown,
)

GHERKIN = """\
@ears:EARS-01 @bdd:BDD-01 @qa-staging-only
Feature: URL Shortener acceptance behaviour
  As a Link Submitter
  I want to shorten public URLs
  So that long links become compact

  Background:
    Given the system is in a ready state
    And the current time is "09:30:00" in "America/New_York"

@scenario-type:success @p0-critical @scenario-id:BDD.01.03.ccd6
@ears:EARS.01.03.5066 @ears:EARS.01.03.bca8
Scenario: Shorten a valid public URL
  Given a Link Submitter with the URL "https://example.com/page"
  When the submitter posts the URL to the API
  Then the API SHALL return a short code WITHIN @threshold:PRD.01.perf.screeningdeadline
  And the API SHALL present "Your short link is ready."
  # spec_trace: SPEC §3 (Interfaces), SPEC §5 (Behavior)
  # split from the former combined scenario

@scenario-type:parameterized @p2-medium @scenario-id:BDD.01.03.abcd
@ears:EARS.01.03.4400
Scenario Outline: Validation accepts valid <input_type>
  Given a valid <input_type> value "<value>"
  When the value is validated
  Then validation SHALL pass

  Examples:
    | input_type | value            |
    | email      | user@example.com |
    | phone      | +1-555-123-4567  |
"""


class TranscoderEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.parsed = parse_gherkin_feature(GHERKIN)
        self.scn = {s["id"]: s for s in self.parsed["scenarios"]}

    def test_feature_name_description_background(self) -> None:
        f = self.parsed["feature"]
        self.assertEqual(f["name"], "URL Shortener acceptance behaviour")
        self.assertIn("As a Link Submitter", f["description"])
        self.assertEqual(len(f["background"]["steps"]), 2)
        # Feature carries NO ears (D-3 — coverage = union of scenarios).
        self.assertNotIn("ears", f)
        self.assertEqual(f.get("tags"), ["@qa-staging-only"])

    def test_scenario_id_copied_verbatim(self) -> None:
        # The load-bearing contract: ids match the source @scenario-id exactly.
        self.assertEqual(set(self.scn), {"BDD.01.03.ccd6", "BDD.01.03.abcd"})

    def test_success_scenario_fields(self) -> None:
        s = self.scn["BDD.01.03.ccd6"]
        self.assertEqual(s["type"], "success")
        self.assertEqual(s["priority"], "p0-critical")
        self.assertEqual(s["ears"], ["EARS.01.03.5066", "EARS.01.03.bca8"])
        self.assertEqual(len(s["given"]), 1)
        self.assertEqual(len(s["when"]), 1)
        self.assertEqual(len(s["then"]), 2)  # Then + And
        self.assertIn("@threshold:PRD.01.perf.screeningdeadline", s["then"][0])
        self.assertEqual(s["spec_trace"], ["SPEC §3 (Interfaces), SPEC §5 (Behavior)"])
        self.assertEqual(s["notes"], ["split from the former combined scenario"])

    def test_outline_examples(self) -> None:
        s = self.scn["BDD.01.03.abcd"]
        self.assertTrue(s.get("outline"))
        self.assertEqual(s["examples"]["headers"], ["input_type", "value"])
        self.assertEqual(len(s["examples"]["rows"]), 2)
        self.assertEqual(s["examples"]["rows"][0], ["email", "user@example.com"])

    def test_render_is_valid_yaml_roundtrip(self) -> None:
        out = render_scenarios_yaml(self.parsed["scenarios"])
        reloaded = yaml.safe_load(out)["scenarios"]
        self.assertEqual(reloaded[0]["id"], "BDD.01.03.ccd6")
        self.assertEqual(reloaded[1]["examples"]["headers"], ["input_type", "value"])

    def test_transcode_markdown_replaces_fence(self) -> None:
        md = (
            "---\ndoc_id: BDD-01\nartifact_type: BDD\n---\n\n## 3. Scenarios\n\n```gherkin\n"
            + GHERKIN
            + "\n```\n"
        )
        out = transcode_markdown(md)
        self.assertNotIn("```gherkin", out)
        self.assertIn("```yaml", out)
        self.assertIn("BDD.01.03.ccd6", out)
        # downstream-citation stability: the id survives the transcode verbatim.
        self.assertIn("id: BDD.01.03.ccd6", out)


if __name__ == "__main__":
    unittest.main()
