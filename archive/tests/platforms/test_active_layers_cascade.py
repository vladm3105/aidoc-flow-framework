"""Conformance: the reference linter honors the ``active_layers`` adaptation
cascade (ACTIVE-LAYERS-CASCADE-001 / H-16).

When a project's ``.aidoc/profile.yaml`` disables a *skippable* layer (BDD/ADR),
the ``cascade_rule`` (``framework/governance/ADAPTATION_SURFACE.yaml``) requires the
lint to stop demanding that layer's upstream tag (TAG01) on downstream layers.
"""

import sys
import tempfile
import unittest
from pathlib import Path

from _spec import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import (  # noqa: E402
    SKIPPABLE_LAYERS,
    _apply_active_layers_cascade,
    compute_disabled_skippable,
    lint_path,
    load_active_layers,
)

_ADR = """---
doc_id: ADR-01
artifact_type: ADR
tags: [adr]
---
# ADR-01

@ears: EARS.01.03.aaaa
"""


def _tag01_for(findings, tag):
    return [f for f in findings if f.code == "TAG01" and f"@{tag}:" in f.message]


class DisabledSetComputation(unittest.TestCase):
    def test_skippable_is_bdd_adr_lowercase(self):
        self.assertEqual(SKIPPABLE_LAYERS, frozenset({"bdd", "adr"}))

    def test_none_knob_disables_nothing(self):
        self.assertEqual(compute_disabled_skippable(None), frozenset())

    def test_disable_bdd(self):
        active = frozenset({"brd", "prd", "ears", "adr", "spec", "tdd", "iplan"})
        self.assertEqual(compute_disabled_skippable(active), frozenset({"bdd"}))

    def test_mandatory_omission_is_ignored(self):
        # omitting a mandatory layer (prd) must not disable it — only skippable count
        active = frozenset({"brd", "ears", "bdd", "adr", "spec", "tdd", "iplan"})
        self.assertEqual(compute_disabled_skippable(active), frozenset())


class LoadActiveLayers(unittest.TestCase):
    def _write(self, body):
        d = Path(tempfile.mkdtemp())
        (d / ".aidoc").mkdir()
        (d / ".aidoc" / "profile.yaml").write_text(body, encoding="utf-8")
        return d / ".aidoc" / "profile.yaml"

    def test_parses_and_lowercases(self):
        self.assertEqual(
            load_active_layers(self._write("active_layers: [BRD, PRD, ADR]\n")),
            frozenset({"brd", "prd", "adr"}),
        )

    def test_absent_knob_is_none(self):
        self.assertIsNone(load_active_layers(self._write("glossary: {}\n")))

    def test_malformed_is_none(self):
        self.assertIsNone(load_active_layers(self._write("active_layers: not-a-list\n")))


class CascadeView(unittest.TestCase):
    def test_empty_disabled_returns_same_object(self):
        layers = {"ADR": {"required_tags": ["ears", "bdd"]}}
        self.assertIs(_apply_active_layers_cascade(layers, frozenset()), layers)

    def test_subtracts_without_mutating_input(self):
        layers = {
            "ADR": {"required_tags": ["ears", "bdd"]},
            "SPEC": {"required_tags": ["ears", "bdd", "adr"]},
        }
        eff = _apply_active_layers_cascade(layers, frozenset({"bdd"}))
        self.assertEqual(eff["ADR"]["required_tags"], ["ears"])
        self.assertEqual(eff["SPEC"]["required_tags"], ["ears", "adr"])
        # input untouched
        self.assertEqual(layers["ADR"]["required_tags"], ["ears", "bdd"])
        self.assertEqual(layers["SPEC"]["required_tags"], ["ears", "bdd", "adr"])


class FunctionalCascade(unittest.TestCase):
    """End-to-end: an ADR requiring @bdd is flagged with BDD active, clean without."""

    def _adr_corpus(self):
        d = Path(tempfile.mkdtemp())
        (d / "docs" / "05_ADR").mkdir(parents=True)
        (d / "docs" / "05_ADR" / "ADR-01_test.md").write_text(_ADR, encoding="utf-8")
        return d / "docs"

    def test_bdd_demanded_when_active(self):
        findings = lint_path(self._adr_corpus())
        self.assertTrue(_tag01_for(findings, "bdd"), "ADR should demand @bdd: when BDD is active")

    def test_bdd_not_demanded_when_disabled(self):
        findings = lint_path(self._adr_corpus(), disabled_skippable=frozenset({"bdd"}))
        self.assertEqual(
            _tag01_for(findings, "bdd"), [], "disabled BDD must not be demanded on ADR"
        )
        # @ears: is present, so no residual ears TAG01 either — and the ADR still lints
        self.assertEqual(_tag01_for(findings, "ears"), [])


if __name__ == "__main__":
    unittest.main()
