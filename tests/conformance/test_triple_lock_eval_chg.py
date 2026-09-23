"""Conformance: triple-lock EVAL/CHG rows ship together (P1-6/P1-7, #671/#669).

Registry ↔ governance ↔ schema must change in one pass. Pins the EVAL/CHG
rows filled by CHG-08: schema layer enum, naming prefixes/lifecycles/filename
rows, governance scope, traceability chain/table. Deliberately NOT pinned:
`acceptance_layers` stays `{BDD: [TDD]}` by design (ACC01 is case-scoped
BDD→TDD pairing; EVAL coverage rides `realizing_layers` BDD→EVAL plus the
EVAL-COV rules — see `test_acceptance_pairing.py`).
"""

import json
import unittest

import yaml
from _spec import FRAMEWORK

GOV = FRAMEWORK / "governance"
SCHEMA = GOV / "saga.schema.json"
NAMING = GOV / "ID_NAMING_STANDARDS.md"
CORE = GOV / "DOC_GOVERNANCE_CORE.md"
TRACE = GOV / "TRACEABILITY.md"
REGISTRY = FRAMEWORK / "registry" / "LAYER_REGISTRY.yaml"

EXPECTED_LAYERS = {
    "01_BRD",
    "02_PRD",
    "03_EARS",
    "04_BDD",
    "05_ADR",
    "06_SPEC",
    "07_TDD",
    "08_IPLAN",
    "09_CHG",
    "10_EVAL",
}


class TripleLockRows(unittest.TestCase):
    def test_schema_layer_enum_is_complete(self):
        """saga.schema.json layer enum names all 10 layers."""
        enum = json.loads(SCHEMA.read_text(encoding="utf-8"))["properties"]["layer"]["enum"]
        self.assertEqual(set(enum), EXPECTED_LAYERS)

    def test_registry_has_chg_eval_rows(self):
        """Registry declares CHG + EVAL layer rows with templates."""
        rows = {
            layer["artifact"]: layer
            for layer in yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))["layers"]
        }
        for artifact, template in (
            ("CHG", "CHG-TEMPLATE.yaml"),
            ("EVAL", "EVAL-TEMPLATE.yaml"),
        ):
            with self.subTest(artifact=artifact):
                self.assertIn(artifact, rows)
                self.assertEqual(rows[artifact]["template"], template)

    def test_naming_prefixes_lifecycles_filenames(self):
        """ID standard carries CHG/EVAL prefixes, lifecycles, bugfix row."""
        text = NAMING.read_text(encoding="utf-8")
        self.assertIn("| CHG | CHG | CHG-01 |", text)
        self.assertIn("| EVAL | EVAL | EVAL-01 |", text)
        self.assertIn("`Completed` | `Verified`", text)
        self.assertIn("CHG Lifecycle (Layer 9)", text)
        self.assertIn("IPLAN-{NEW}_bugfix_{FIXED}_{slug}.yaml", text)
        self.assertIn("EVAL-{NN}-RPT-{NNN}.yaml", text)

    def test_governance_scope_covers_l10(self):
        """DOC_GOVERNANCE_CORE scope note includes layer 10."""
        self.assertIn("layers 1-10", _text(CORE))

    def test_traceability_names_eval(self):
        """Traceability chain, upstream block, and table all carry EVAL."""
        text = _text(TRACE)
        self.assertIn("EVAL (L10)", text)
        self.assertIn("Layer 10 (EVAL): @ears @bdd @tdd @iplan", text)
        self.assertIn("| EVAL | @ears, @bdd, @tdd, @iplan | Code |", text)


def _text(path):
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
