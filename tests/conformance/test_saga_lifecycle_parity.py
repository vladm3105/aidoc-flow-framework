"""Parity: the committed saga fixtures conform to the one spec state machine (FRAMEWORK-ONLY).

CLEANUP-001 Decisions 5/6: ``tools/saga_driver.py`` and ``platforms/hermes``
were deleted with their trees (deliberate — both runners are gone). The
four platform-table classes below (``SagaTransitionTableParity`` cross-check,
``SagaRealJournalConformance`` live-journal drive, ``SagaTransitionInvariant``
Hermes edge guard) tested driver code, not framework data, so they retire with
their subjects — their tripwires fail if ``tools/`` or ``platforms/`` returns
without them. What stays is the framework-side contract: the ``SPEC_TRANSITIONS``
pin (hard-coded from ``REVIEW_SAGA.md`` prose, exactly as before), the committed
sample journals validating against ``saga.schema.json``, and the schema-vs-
registry ``artifact_id`` pattern lockstep (#444). Per R4 no guard is weakened —
driver guards retire with drivers, data guards stay on data.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "saga"
_SCHEMA_PATH = _REPO_ROOT / "framework" / "governance" / "saga.schema.json"

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


class RetiredPlatformTransitionTableParity(unittest.TestCase):
    """Retired with the runners (CLEANUP-001): both transition tables are gone.

    The ``SPEC_TRANSITIONS`` pin above stays as the hard-coded mirror of
    ``REVIEW_SAGA.md`` prose; the driver-vs-spec comparisons move with the
    drivers. ``test_spec_table_matches_schema_enum`` keeps the framework-side
    half live: the pin and the schema must agree on the eleven states."""

    def test_spec_table_matches_schema_enum(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            set(SPEC_TRANSITIONS),
            set(schema["properties"]["status"]["enum"]),
            "SPEC_TRANSITIONS pin diverged from saga.schema.json status enum — "
            "one of the two framework-side saga surfaces drifted",
        )

    def test_tools_are_gone(self) -> None:
        self.assertFalse(
            (_REPO_ROOT / "tools").exists(),
            "tools/ is back — resurrect the plugin table half with saga_driver",
        )

    def test_platforms_are_gone(self) -> None:
        self.assertFalse(
            (_REPO_ROOT / "platforms").exists(),
            "platforms/ is back — resurrect the Hermes table half with saga_models",
        )


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


class RetiredSagaRealJournalConformance(unittest.TestCase):
    """Retired with Hermes (CLEANUP-001): the journal writer code is gone.

    This class drove the REAL ``mcp_server.review`` journal functions
    (``create_saga_journal``/``update_run_status``/``set_branch_state``) — not
    hand-authored fixtures — so it tested platform code. The committed-fixture
    parity above stays; this tripwire fails if ``platforms/`` returns without
    the live-journal guard."""

    def test_platforms_are_gone(self) -> None:
        self.assertFalse(
            (_REPO_ROOT / "platforms").exists(),
            "platforms/ is back — resurrect SagaRealJournalConformance with the journal code",
        )


class SagaIdPatternLockstep(unittest.TestCase):
    """#444: the schema's `artifact_id` pattern must equal the registry's
    `id_patterns.document` pattern — the schema once rejected registry-valid
    3+ digit IDs (``{2}`` vs ``{2,}``) and nothing asserted the lockstep the
    schema's own description demanded. REVIEW_SAGA.md quotes the registry
    pattern verbatim as authoritative; ID_NAMING_STANDARDS.md agrees with the
    registry; only the schema was narrower."""

    def test_artifact_id_pattern_matches_registry_document_pattern(self):
        import yaml

        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        schema_pattern = schema["properties"]["artifact_id"]["pattern"]
        registry = yaml.safe_load(
            (_REPO_ROOT / "framework" / "registry" / "LAYER_REGISTRY.yaml").read_text(
                encoding="utf-8"
            )
        )
        registry_pattern = registry["id_patterns"]["document"]
        self.assertEqual(
            schema_pattern,
            registry_pattern.replace("\\d", "[0-9]"),
            "saga.schema.json artifact_id and LAYER_REGISTRY.yaml id_patterns.document "
            "diverged — documents valid at one surface are rejected at the other",
        )


class RetiredSagaTransitionInvariant(unittest.TestCase):
    """Retired with Hermes (CLEANUP-001): ``saga_models.transition_run_status`` is gone.

    The D-0050 residual (illegal edge raises, legal edge succeeds) tested the
    Hermes state-machine enforcement, not framework data. Resurrect with the
    Hermes mirror; the framework-side table pin lives in
    ``RetiredPlatformTransitionTableParity`` above."""

    def test_platforms_are_gone(self) -> None:
        self.assertFalse(
            (_REPO_ROOT / "platforms").exists(),
            "platforms/ is back — resurrect SagaTransitionInvariant with saga_models",
        )


if __name__ == "__main__":
    unittest.main()
