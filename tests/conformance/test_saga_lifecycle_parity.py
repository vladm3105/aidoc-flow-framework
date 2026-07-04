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


class SagaRealJournalConformance(unittest.TestCase):
    """A **real** Hermes saga journal — written by the actual journal code
    (`create_saga_journal`/`update_run_status`/`set_branch_state` serializing
    `asdict(SagaRunState)`), with `artifact_id`/`layer` derived by the actual
    orchestrator helpers (`_extract_doc_id`/`normalize_layer`) — validates against
    `saga.schema.json`.

    This is the guard that would have caught H-12: the Phase-1 fixture tests above
    validate hand-authored journals, which carried the 4 required fields the real
    `SagaRunState` was missing. This drives the real serialization + transition
    recording, so on pre-fix `main` it fails (`artifact_id`/`layer`/`iteration`/
    `transitions` absent). HERMES-SAGA-JOURNAL-CONFORMANCE (H-12).
    """

    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        sys.path.insert(0, str(_REPO_ROOT / "platforms" / "hermes" / "src"))
        from mcp_server.review.playbook_loader import normalize_layer
        from mcp_server.review.saga_journal import (
            create_saga_journal,
            load_saga_journal,
            set_branch_state,
            update_run_status,
        )
        from mcp_server.review.saga_models import SagaBranchState, SagaRunState
        from mcp_server.review.saga_orchestrator import _extract_doc_id

        cls._normalize_layer = staticmethod(normalize_layer)
        cls._extract_doc_id = staticmethod(_extract_doc_id)
        cls._SagaRunState = SagaRunState
        cls._SagaBranchState = SagaBranchState
        cls._create = staticmethod(create_saga_journal)
        cls._update = staticmethod(update_run_status)
        cls._set_branch = staticmethod(set_branch_state)
        cls._load = staticmethod(load_saga_journal)

    def _drive_real_journal(self, *, out_dir: Path, doc_type: str, layer, doc_dir: str):
        """Build a SagaRunState exactly as the orchestrator does, then walk a full
        lifecycle through the real journal functions. Returns the on-disk journal."""
        from pathlib import Path as _P

        document_path = _P(doc_dir)
        artifact_id = self._extract_doc_id(document_path=document_path, doc_type=doc_type)
        # F1: layer derives from the (required) doc_type when --layer is omitted.
        _, layer_dir = self._normalize_layer(layer or doc_type)
        run = self._SagaRunState(
            review_run_id="realrun000001",  # 13 chars ≥ minLength 12
            document_path=str(document_path),
            document_fingerprint=f"{doc_type}:3:1",
            personas_requested=["architect", "auditor"],
            artifact_id=artifact_id,
            layer=layer_dir,
            iteration=1,
        )
        journal_path = self._create(output_dir=out_dir, run=run)
        # Run-scope walk (each step is an allowed transition).
        for target in ("FANOUT_STARTED", "BRANCH_RUNNING"):
            self._update(journal_path=journal_path, target=target)
        # Branch-scope transitions: a branch runs then completes.
        for status in ("BRANCH_RUNNING", "BRANCH_COMPLETED"):
            self._set_branch(
                journal_path=journal_path,
                branch=self._SagaBranchState(
                    branch_id="b0000000abcd", persona="architect", status=status
                ),
            )
        for target in ("BRANCH_COMPLETED", "FANIN_REDUCED", "SYNTHESIZED", "CLOSED"):
            self._update(journal_path=journal_path, target=target)
        return json.loads(journal_path.read_text(encoding="utf-8")), journal_path

    def _assert_conforms(self, data: dict, ctx: str):
        errors = validate(data, self.schema)
        self.assertEqual(errors, [], f"{ctx}: real journal fails saga.schema.json: {errors}")
        # transitions replay the state machine; each `scope` matches the schema pattern.
        scope_re = re.compile(r"^(run|branch:[a-z_]+)$")
        self.assertTrue(data["transitions"], f"{ctx}: no transitions recorded")
        for tr in data["transitions"]:
            self.assertTrue(scope_re.match(str(tr["scope"])), f"{ctx}: bad scope {tr['scope']!r}")
            self.assertEqual(
                set(tr.keys()), {"ts", "from", "to", "scope"}, f"{ctx}: extra transition keys"
            )

    def test_real_lifecycle_journal_validates(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            data, _ = self._drive_real_journal(
                out_dir=Path(td),
                doc_type="brd",
                layer="01_BRD",
                doc_dir="/p/docs/01_BRD/BRD-01/",
            )
        self._assert_conforms(data, "lifecycle")
        self.assertEqual(data["artifact_id"], "BRD-01")
        self.assertEqual(data["layer"], "01_BRD")
        # the seed + run + branch transitions are all present
        self.assertEqual(
            data["transitions"][0],
            {"ts": data["transitions"][0]["ts"], "from": None, "to": "PREPARED", "scope": "run"},
        )
        self.assertTrue(any(t["scope"] == "branch:architect" for t in data["transitions"]))

    def test_layer_omitted_derives_from_doc_type(self):
        # V2b / F1: --layer omitted (None) → layer still enum-valid via doc_type.
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            data, _ = self._drive_real_journal(
                out_dir=Path(td),
                doc_type="brd",
                layer=None,
                doc_dir="/p/docs/01_BRD/BRD-01/",
            )
        self.assertEqual(data["layer"], "01_BRD")
        self.assertIn(data["layer"], self.schema["properties"]["layer"]["enum"])
        self._assert_conforms(data, "layer-omitted")

    def test_chg_review_journal_validates(self):
        # V4: a real CHG-review journal (layer 09_CHG) validates (enum extended).
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            data, _ = self._drive_real_journal(
                out_dir=Path(td),
                doc_type="chg",
                layer=None,
                doc_dir="/p/docs/09_CHG/CHG-01/",
            )
        self.assertEqual(data["layer"], "09_CHG")
        self.assertEqual(data["artifact_id"], "CHG-01")
        self._assert_conforms(data, "chg")


if __name__ == "__main__":
    unittest.main()
