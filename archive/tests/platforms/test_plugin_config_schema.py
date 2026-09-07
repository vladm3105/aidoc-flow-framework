"""Conformance: the plugin's optional config schema is internally consistent
(PLUGIN-USER-COMMANDS).

Three commands edit `.claude/aidoc-flow.config.yaml` —
`/aidoc-flow:configure`, `/aidoc-flow:budget`, `/aidoc-flow:model` — and one
reference doc (`docs/CONFIG.md`) is the single source of truth for the
schema's keys and enum values. This test fails CI if the doc and any of the
three command files drift apart on:

* The eight canonical SDD layer names (`BRD | PRD | EARS | BDD | ADR | SPEC |
  TDD | IPLAN`) — used by `skip_layers`, `budget.profile_per_layer`,
  `model.per_layer`.
* The `budget.profile` enum (`max | standard | min`).
* The `model.precheck` enum (`warn | silent | block`).
* The `review_hook` enum (`on | off | verbose`).
* The presence of the top-level keys the schema documents.
"""

import re
import unittest

import yaml
from _spec import REPO_ROOT

PLUGIN = REPO_ROOT / "platforms" / "claude-code-plugin"
CONFIG_DOC = PLUGIN / "docs" / "CONFIG.md"
COMMANDS = PLUGIN / "commands"

LAYERS = {"BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN"}
BUDGET_PROFILES = {"max", "standard", "min"}
MODEL_PRECHECK = {"warn", "silent", "block"}
REVIEW_HOOK = {"on", "off", "verbose"}

EXPECTED_TOP_KEYS = {
    "schema",
    "docs_root",
    "work_plans_dir",
    "skip_layers",
    "output_language",
    "review_hook",
    "budget",
    "model",
}


def _extract_yaml_block(text: str) -> dict:
    """Pull the first ```yaml fenced block out of a markdown file and parse it."""
    m = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    if not m:
        raise AssertionError("docs/CONFIG.md has no ```yaml schema block")
    return yaml.safe_load(m.group(1))


class PluginConfigSchema(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CONFIG_DOC.is_file(), f"missing {CONFIG_DOC}")
        self.doc_text = CONFIG_DOC.read_text(encoding="utf-8")
        self.schema = _extract_yaml_block(self.doc_text)

    def test_schema_parses_and_has_expected_keys(self):
        self.assertIsInstance(self.schema, dict, "config schema must be a YAML mapping")
        missing = EXPECTED_TOP_KEYS - set(self.schema.keys())
        self.assertFalse(missing, f"config schema missing keys: {sorted(missing)}")

    def test_schema_defaults_are_documented(self):
        self.assertEqual(self.schema.get("schema"), 1, "schema version must be 1")
        self.assertEqual(self.schema.get("docs_root"), "docs/")
        self.assertEqual(self.schema.get("work_plans_dir"), "work_plans/")
        self.assertEqual(self.schema.get("skip_layers"), [])
        self.assertEqual(self.schema.get("output_language"), "en")
        self.assertEqual(self.schema.get("review_hook"), "on")

        budget = self.schema.get("budget") or {}
        self.assertEqual(budget.get("profile"), "standard")
        self.assertEqual(budget.get("profile_per_layer"), {})

        model = self.schema.get("model") or {}
        self.assertEqual(model.get("default"), "claude-sonnet-4-6")
        self.assertEqual(model.get("per_layer"), {})
        self.assertEqual(model.get("precheck"), "warn")

    def test_doc_lists_canonical_layer_names(self):
        for layer in sorted(LAYERS):
            self.assertIn(
                layer,
                self.doc_text,
                f"docs/CONFIG.md must reference canonical layer {layer}",
            )

    def test_doc_lists_budget_profile_enum(self):
        for value in sorted(BUDGET_PROFILES):
            self.assertIn(value, self.doc_text, f"docs/CONFIG.md missing budget profile '{value}'")

    def test_doc_lists_model_precheck_enum(self):
        for value in sorted(MODEL_PRECHECK):
            self.assertIn(value, self.doc_text, f"docs/CONFIG.md missing precheck mode '{value}'")

    def test_doc_lists_review_hook_enum(self):
        for value in sorted(REVIEW_HOOK):
            self.assertIn(
                value, self.doc_text, f"docs/CONFIG.md missing review_hook mode '{value}'"
            )

    def test_budget_command_uses_documented_enum(self):
        cmd = COMMANDS / "budget.md"
        self.assertTrue(cmd.is_file(), f"missing {cmd}")
        text = cmd.read_text(encoding="utf-8")
        for value in BUDGET_PROFILES:
            self.assertIn(value, text, f"commands/budget.md missing profile value '{value}'")

    def test_model_command_uses_documented_enum(self):
        cmd = COMMANDS / "model.md"
        self.assertTrue(cmd.is_file(), f"missing {cmd}")
        text = cmd.read_text(encoding="utf-8")
        for value in MODEL_PRECHECK:
            self.assertIn(value, text, f"commands/model.md missing precheck value '{value}'")

    def test_configure_command_references_config_doc(self):
        cmd = COMMANDS / "configure.md"
        self.assertTrue(cmd.is_file(), f"missing {cmd}")
        text = cmd.read_text(encoding="utf-8")
        self.assertIn(
            "aidoc-flow.config.yaml",
            text,
            "commands/configure.md must reference the config file",
        )


if __name__ == "__main__":
    unittest.main()
