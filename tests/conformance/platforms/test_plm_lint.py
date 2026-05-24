"""Conformance: the Claude Code plugin's skill corpus carries no legacy
12-layer SDD fingerprints — it conforms to the framework's 8-layer model
(BRD·PRD·EARS·BDD·ADR·SPEC·TDD·IPLAN). Promoted from the PLM migration gate
(see plans/PLM-PLAN.md); enforces the whole corpus via plm_lint.scan(all)."""

import importlib.util
import pathlib
import unittest

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("plm_lint", _HERE / "plm_lint.py")
plm_lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(plm_lint)


class PluginLayerModelConformanceTests(unittest.TestCase):
    def test_plugin_has_no_legacy_12layer_fingerprints(self):
        if not plm_lint.SKILLS.exists():
            self.skipTest("claude-code-plugin skills absent")
        hits, _ = plm_lint.scan(enforce_all=True)
        self.assertEqual(
            hits,
            [],
            "legacy 12-layer fingerprints remain in the plugin "
            "(skills/agents/commands):\n  "
            + "\n  ".join(f"{disp}:{line}: [{label}] {frag!r}" for disp, line, label, frag in hits),
        )
