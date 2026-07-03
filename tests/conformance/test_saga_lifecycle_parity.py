"""Parity: both runners' review sagas conform to the one spec state machine.

`framework/governance/REVIEW_SAGA.md` is the transition-table authority and
`framework/governance/saga.schema.json` is the journal schema. This test enforces
what `docs/PARITY.md` describes (previously an over-claim — the test + fixtures did
not exist):

  * both platforms' `_ALLOWED_TRANSITIONS` equal the spec transition table
    (incl. the `PARTIAL_TIMEOUT` break-circuit state), and
  * a committed sample journal from each runner validates against the shared
    `saga.schema.json`.

The spec transition table is markdown prose (terminal rows read `(terminal)`), so
it is HARD-CODED here as `SPEC_TRANSITIONS` — a deliberate second source of truth,
exactly as `test_saga_driver_invariants.py` already does for the plugin. That
sibling test carries the detailed plugin-driver invariants; this test's net-new job
is the *Hermes* table + the cross-platform fixture parity.

HERMES-PARITY-PHASE-1 (D-0045).
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "saga"
_SCHEMA_PATH = _REPO_ROOT / "framework" / "governance" / "saga.schema.json"

# --- import both platforms' transition tables (module-level constants) ---
sys.path.insert(0, str(_REPO_ROOT / "tools"))
sys.path.insert(0, str(_REPO_ROOT / "platforms" / "hermes" / "src" / "mcp_server" / "review"))
import saga_driver  # noqa: E402  (plugin reference; path injection intentional)
import saga_models  # noqa: E402  (Hermes; imports only stdlib)

# The REVIEW_SAGA.md transition table, hard-coded (the markdown is prose, not
# machine-parseable). Source authority: framework/governance/REVIEW_SAGA.md.
SPEC_TRANSITIONS: dict[str, set[str]] = {
    "PREPARED": {"FANOUT_STARTED", "PARTIAL_TIMEOUT"},
    "FANOUT_STARTED": {"BRANCH_RUNNING", "PARTIAL_TIMEOUT"},
    "BRANCH_RUNNING": {"BRANCH_COMPLETED", "BRANCH_FAILED", "PARTIAL_TIMEOUT"},
    "BRANCH_FAILED": {"BRANCH_COMPENSATING", "ESCALATED", "BRANCH_COMPLETED"},
    "BRANCH_COMPENSATING": {"BRANCH_RUNNING", "ESCALATED"},
    "BRANCH_COMPLETED": {"FANIN_REDUCED", "PARTIAL_TIMEOUT"},
    "FANIN_REDUCED": {"SYNTHESIZED", "PARTIAL_TIMEOUT"},
    "SYNTHESIZED": {"CLOSED"},
    "ESCALATED": set(),
    "CLOSED": set(),
    "PARTIAL_TIMEOUT": set(),
}


def _type_ok(value: object, t: str) -> bool:
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "null":
        return value is None
    return True


def validate(instance: object, schema: dict, path: str = "$") -> list[str]:
    """Dependency-free check of the JSON-Schema subset this contract uses
    (type incl. union lists, required, properties, items, enum, minimum,
    maximum, minLength, minItems, pattern)."""
    errors: list[str] = []
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(instance, one) for one in types):
            return [f"{path}: expected {t}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: len {len(instance)} < minLength {schema['minLength']}")
        pat = schema.get("pattern")
        if pat and not re.search(pat, instance):
            errors.append(f"{path}: {instance!r} does not match pattern {pat!r}")
    if isinstance(instance, int) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")
    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required '{req}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                errors.extend(validate(instance[key], subschema, f"{path}.{key}"))
        extra = schema.get("additionalProperties")
        if isinstance(extra, dict):
            declared = set(schema.get("properties", {}))
            for key, val in instance.items():
                if key not in declared:
                    errors.extend(validate(val, extra, f"{path}.{key}"))
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: {len(instance)} items < minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, item_schema, f"{path}[{i}]"))
    return errors


class SagaTransitionTableParity(unittest.TestCase):
    """Both platforms' `_ALLOWED_TRANSITIONS` must equal the spec table."""

    def test_hermes_table_matches_spec(self):
        self.assertEqual(
            saga_models._ALLOWED_TRANSITIONS,
            SPEC_TRANSITIONS,
            "Hermes saga_models._ALLOWED_TRANSITIONS diverges from REVIEW_SAGA.md "
            "(missing PARTIAL_TIMEOUT?).",
        )

    def test_plugin_table_matches_spec(self):
        self.assertEqual(
            saga_driver._ALLOWED_TRANSITIONS,
            SPEC_TRANSITIONS,
            "plugin saga_driver._ALLOWED_TRANSITIONS diverges from REVIEW_SAGA.md.",
        )

    def test_both_platforms_agree(self):
        self.assertEqual(
            saga_models._ALLOWED_TRANSITIONS,
            saga_driver._ALLOWED_TRANSITIONS,
            "Hermes and plugin saga transition tables disagree.",
        )

    def test_partial_timeout_terminal_both(self):
        # G-R1: PARTIAL_TIMEOUT is terminal-this-process on both platforms.
        self.assertEqual(saga_models._ALLOWED_TRANSITIONS.get("PARTIAL_TIMEOUT"), set())
        self.assertEqual(saga_driver._ALLOWED_TRANSITIONS.get("PARTIAL_TIMEOUT"), set())


class SagaJournalFixtureParity(unittest.TestCase):
    """A sample journal from each runner validates against the shared schema."""

    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

    def _validate_fixture(self, name: str):
        data = json.loads((_FIXTURES / name).read_text(encoding="utf-8"))
        errors = validate(data, self.schema)
        self.assertEqual(errors, [], f"{name} fails saga.schema.json: {errors}")
        # every recorded `to`/`from` state is a known saga status
        states = set(self.schema["properties"]["status"]["enum"])
        for tr in data["transitions"]:
            self.assertIn(tr["to"], states, f"{name}: unknown transition target {tr['to']!r}")
            if tr.get("from") is not None:
                self.assertIn(
                    tr["from"], states, f"{name}: unknown transition source {tr['from']!r}"
                )

    def test_plugin_fixture_validates(self):
        self._validate_fixture("plugin_BRD-01_saga.json")

    def test_hermes_fixture_validates(self):
        self._validate_fixture("hermes_BRD-01_saga.json")

    def test_fixtures_share_shape(self):
        plugin = json.loads((_FIXTURES / "plugin_BRD-01_saga.json").read_text(encoding="utf-8"))
        hermes = json.loads((_FIXTURES / "hermes_BRD-01_saga.json").read_text(encoding="utf-8"))
        required = set(self.schema["required"])
        self.assertTrue(required <= plugin.keys() and required <= hermes.keys())
        self.assertEqual(plugin["layer"], hermes["layer"])
        self.assertEqual(plugin["artifact_id"], hermes["artifact_id"])


if __name__ == "__main__":
    unittest.main()
