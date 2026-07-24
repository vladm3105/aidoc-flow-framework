"""Conformance: ACC01 — BDD-scenario -> TDD-test-case acceptance pairing
(SEED-ABSORPTION-001 / GD-08), and the `acceptance_layers` registry/linter sync.

Part C. ACC01 is **case-scoped**: a BDD scenario is paired only when a TDD test
case or §3 mapping entry names it (a `@bdd:` citation co-located with a TDD
test-case element id). A scenario cited only in the TDD §7 traceability block —
a bare list of `@bdd:` tokens — does NOT pair. This is the proof the vacuous-pass
loophole is closed: appending scenario IDs to one traceability line cannot
silence ACC01 (that is exactly what a document-scoped rule would have allowed).
"""

import sys
import unittest

from _spec import REPO_ROOT, load_registry

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import ACCEPTANCE_LAYERS, _check_acceptance_pairing  # noqa: E402

# A BDD doc declaring two scenarios, and a TDD doc that pairs ONE via a §3
# mapping row (co-located with a TDD test-case id) and lists BOTH in its §7
# traceability block. Under a document-scoped rule both would pass; under ACC01
# only the mapped one pairs.
BDD_DOC = """---
doc_id: BDD-01
artifact_type: BDD
---
# BDD-01

```yaml
scenarios:
  - id: BDD.01.03.aaaa
    name: paired via a §3 mapping row
    type: success
    priority: p1-high
    ears: "@ears: EARS.01.03.1111"
    given: g
    when: w
    then: t
  - id: BDD.01.03.bbbb
    name: listed only in the traceability block
    type: success
    priority: p1-high
    ears: "@ears: EARS.01.03.2222"
    given: g
    when: w
    then: t
```
"""

TDD_DOC = """---
doc_id: TDD-01
artifact_type: TDD
---
# TDD-01

## 3. Test Mapping

| Scenario | Behavior | Unit |
|---|---|---|
| @bdd: BDD.01.03.aaaa | paired one | `TDD.01.04.1a2c` |

## 7. Traceability

- @bdd: BDD.01.03.aaaa @bdd: BDD.01.03.bbbb
"""


# A TDD authored in the framework's own structured-YAML form (TDD-TEMPLATE.yaml):
# the `bdd_ref` carrier sits on its own line, NOT co-located with the `id:`
# test-case element id. Scenario aaaa is genuinely paired via bdd_ref; bbbb is
# only in the traceability block.
TDD_STRUCTURED = """---
doc_id: TDD-01
artifact_type: TDD
---
# TDD-01

```yaml
test_mapping:
  scenarios:
    - bdd_scenario: "@bdd: BDD.01.03.aaaa"
      description: paired via a structured mapping entry
e2e_tests:
  cases:
    - id: "TDD.01.04.1a2c"
      bdd_ref: "@bdd: BDD.01.03.aaaa"
```

## 7. Traceability

- @bdd: BDD.01.03.aaaa @bdd: BDD.01.03.bbbb
"""


def _corpus():
    return [("04_BDD/BDD-01.md", BDD_DOC), ("07_TDD/TDD-01.md", TDD_DOC)]


def _structured_corpus():
    return [("04_BDD/BDD-01.md", BDD_DOC), ("07_TDD/TDD-01.md", TDD_STRUCTURED)]


class Acc01Pairing(unittest.TestCase):
    def _acc01(self, mode="build"):
        return [f for f in _check_acceptance_pairing(_corpus(), mode) if f.code == "ACC01"]

    def test_traceability_only_scenario_is_unpaired(self):
        """The scenario named only in the §7 traceability block yields ACC01 —
        the loophole is closed."""
        offenders = {f.message.split("'")[1] for f in self._acc01()}
        self.assertIn(
            "BDD.01.03.bbbb", offenders, "traceability-block-only scenario should fire ACC01"
        )

    def test_mapping_named_scenario_does_not_fire(self):
        """The scenario named by a §3 mapping entry (co-located with a TDD
        test-case id) does NOT fire ACC01."""
        offenders = {f.message.split("'")[1] for f in self._acc01()}
        self.assertNotIn("BDD.01.03.aaaa", offenders, "mapping-paired scenario must not fire ACC01")

    def test_exactly_one_offender(self):
        self.assertEqual(len(self._acc01()), 1)

    def test_mode_split_mirrors_cov02(self):
        """Warning in build, error in gate-code."""
        self.assertTrue(all(f.severity == "warning" for f in self._acc01("build")))
        self.assertTrue(all(f.severity == "error" for f in self._acc01("gate-code")))

    def test_no_tdd_no_op(self):
        """No real TDD doc → ACC01 is silent (single-file on_author BDD runs)."""
        self.assertEqual(_check_acceptance_pairing([("04_BDD/BDD-01.md", BDD_DOC)]), [])

    def test_structured_yaml_carrier_pairs(self):
        """A TDD in the framework's structured-YAML form pairs via the
        `bdd_scenario`/`bdd_ref` carrier fields even though the `@bdd:` value is
        NOT co-located with a TDD test-case id on the same line. Regression: the
        line-only co-location heuristic false-fired on the template's own shape."""
        offenders = {
            f.message.split("'")[1]
            for f in _check_acceptance_pairing(_structured_corpus())
            if f.code == "ACC01"
        }
        self.assertNotIn("BDD.01.03.aaaa", offenders, "structured bdd_ref pairing missed")
        # bbbb is still only in the traceability block → still fires (loophole closed).
        self.assertIn("BDD.01.03.bbbb", offenders)


class AcceptanceLayersRegistry(unittest.TestCase):
    def test_registry_declares_acceptance_layers(self):
        block = load_registry().get("acceptance_layers")
        self.assertIsInstance(
            block, dict, "registry/LAYER_REGISTRY.yaml must declare an acceptance_layers map"
        )

    def test_lint_constant_matches_registry(self):
        block = load_registry().get("acceptance_layers") or {}
        registry_norm = {k: tuple(v) for k, v in block.items()}
        lint_norm = {k: tuple(v) for k, v in ACCEPTANCE_LAYERS.items()}
        self.assertEqual(
            lint_norm,
            registry_norm,
            "sdd_doc_lint.ACCEPTANCE_LAYERS drifted from registry acceptance_layers",
        )

    def test_realizing_layers_untouched(self):
        """acceptance_layers is additive — realizing_layers must be unchanged
        (mutating it would break the pinned COV02 corpus assertion)."""
        self.assertEqual(
            load_registry().get("realizing_layers"),
            {"BRD": ["PRD"], "EARS": ["BDD", "SPEC", "TDD"], "BDD": ["SPEC", "TDD"]},
        )

    def test_acc01_is_catalogued(self):
        catalog = (REPO_ROOT / "framework" / "governance" / "LINT_RULES.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`ACC01`", catalog, "ACC01 not documented in LINT_RULES.md")


if __name__ == "__main__":
    unittest.main()
