"""Parity: both runners' review reports validate against one shared schema.

AGENT-TEAM Phase 3 (deterministic half). The Hermes saga and the Claude Code
plugin review-team are two runners of the same `framework/governance/REVIEW_TEAM.md`
model; their **unified review reports** must share one structure. This test
validates committed sample report fixtures from *both* runners against the shared
`fixtures/review/review_report.schema.json` and checks they share the report shape.

Live LLM runs are not CI-deterministic, so the end-to-end "same artifact → identical
report" comparison is a documented **manual** procedure (see `docs/PARITY.md`); this
test is the deterministic schema/shape half.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures" / "review"
SCHEMA_PATH = FIXTURES / "review_report.schema.json"
RUNNER_FIXTURES = ("hermes_BRD-01_report.json", "plugin_BRD-01_report.json")

_FINDING_REQUIRED = {"id", "priority", "location", "message", "recommendation"}


def _type_ok(value: object, t: str) -> bool:
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def validate(instance: object, schema: dict, path: str = "$") -> list[str]:
    """Dependency-free check of the JSON-Schema subset this contract uses
    (type, required, properties, items, enum, minimum, maximum)."""
    errors: list[str] = []
    t = schema.get("type")
    if t and not _type_ok(instance, t):
        return [f"{path}: expected {t}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")
    if t == "object" and isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required '{req}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                errors.extend(validate(instance[key], subschema, f"{path}.{key}"))
    if t == "array" and isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, item_schema, f"{path}[{i}]"))
    return errors


class ReviewReportParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.reports = {
            name: json.loads((FIXTURES / name).read_text(encoding="utf-8"))
            for name in RUNNER_FIXTURES
        }

    def test_each_runner_fixture_validates(self):
        for name, report in self.reports.items():
            with self.subTest(fixture=name):
                self.assertEqual(validate(report, self.schema), [], name)

    def test_runners_share_report_structure(self):
        reports = list(self.reports.values())
        base_keys = set(reports[0])
        base_cov = set(reports[0]["coverage"])
        base_gate = set(reports[0]["gate"])
        for name, r in self.reports.items():
            with self.subTest(fixture=name):
                self.assertEqual(set(r), base_keys, f"{name}: top-level keys diverge")
                self.assertEqual(set(r["coverage"]), base_cov, f"{name}: coverage keys diverge")
                self.assertEqual(set(r["gate"]), base_gate, f"{name}: gate keys diverge")
                for i, finding in enumerate(r["findings"]):
                    self.assertTrue(
                        _FINDING_REQUIRED <= set(finding), f"{name}: finding[{i}] missing keys"
                    )

    def test_gate_is_deterministic_floor(self):
        # passed == structural floor AND no unresolved P0/P1; the score never gates.
        for name, r in self.reports.items():
            with self.subTest(fixture=name):
                g = r["gate"]
                self.assertEqual(g["passed"], g["structural_pass"] and g["no_blocking"], name)


if __name__ == "__main__":
    unittest.main()
