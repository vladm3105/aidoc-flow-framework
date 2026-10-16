"""Conformance: Native SDD Property Graph Schema (CHG-108).

Validates:
1. `framework/governance/sdd-graph.schema.json` exists and defines the native property graph contract.
2. Canonical starter templates (`INITIATIVE-GRAPH-TEMPLATE.yaml`, `EXECUTION-GRAPH-TEMPLATE.yaml`)
   conform to the schema.
3. Node types, edge relations, and metadata attributes satisfy the ontology rules.
4. Negative fixtures (malformed kinds, invalid edge types, missing required attributes) are
   strictly rejected.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml
from _spec import FRAMEWORK, REPO_ROOT

SCHEMA_PATH = FRAMEWORK / "governance" / "sdd-graph.schema.json"
INITIATIVE_TEMPLATE = FRAMEWORK / "templates" / "INITIATIVE-GRAPH-TEMPLATE.yaml"
EXECUTION_TEMPLATE = FRAMEWORK / "templates" / "EXECUTION-GRAPH-TEMPLATE.yaml"

# Standalone validator supporting Draft-07 subset for zero-dependency test execution
def _type_ok(val: object, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(val, dict)
    if expected_type == "array":
        return isinstance(val, list)
    if expected_type == "string":
        return isinstance(val, str)
    if expected_type == "boolean":
        return isinstance(val, bool)
    if expected_type == "integer":
        return isinstance(val, int) and not isinstance(val, bool)
    if expected_type == "number":
        return isinstance(val, (int, float)) and not isinstance(val, bool)
    if expected_type == "null":
        return val is None
    return True


def validate_schema(instance: object, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(instance, one) for one in types):
            return [f"{path}: expected {t}, got {type(instance).__name__}"]

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")

    if isinstance(instance, str):
        pat = schema.get("pattern")
        if pat and not re.search(pat, instance):
            errors.append(f"{path}: {instance!r} does not match pattern {pat!r}")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property '{req}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                errors.extend(validate_schema(instance[key], subschema, f"{path}.{key}"))
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}))
            for k in instance:
                if k not in allowed:
                    errors.append(f"{path}: unexpected property '{k}'")

    if isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors.extend(validate_schema(item, item_schema, f"{path}[{i}]"))

    return errors


class TestSddGraphSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assertTrue(SCHEMA_PATH.is_file(), f"Schema missing: {SCHEMA_PATH}")
        with SCHEMA_PATH.open("r", encoding="utf-8") as f:
            cls.schema = json.load(f)

    def test_schema_metadata(self) -> None:
        """Verify schema header and required top-level properties."""
        self.assertEqual(self.schema.get("title"), "Native SDD Graph Schema")
        self.assertIn("schema_version", self.schema.get("required", []))
        self.assertIn("slice_id", self.schema.get("required", []))
        self.assertIn("metadata", self.schema.get("required", []))
        self.assertIn("nodes", self.schema.get("required", []))
        self.assertIn("edges", self.schema.get("required", []))

    def test_initiative_template_validates(self) -> None:
        """Verify INITIATIVE-GRAPH-TEMPLATE.yaml satisfies sdd-graph.schema.json."""
        self.assertTrue(INITIATIVE_TEMPLATE.is_file())
        with INITIATIVE_TEMPLATE.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        errors = validate_schema(data, self.schema)
        self.assertEqual(errors, [], f"Template validation errors: {errors}")

    def test_execution_template_validates(self) -> None:
        """Verify EXECUTION-GRAPH-TEMPLATE.yaml satisfies sdd-graph.schema.json."""
        self.assertTrue(EXECUTION_TEMPLATE.is_file())
        with EXECUTION_TEMPLATE.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        errors = validate_schema(data, self.schema)
        self.assertEqual(errors, [], f"Template validation errors: {errors}")

    def test_valid_minimal_graph(self) -> None:
        """Verify a valid minimal property graph slice."""
        minimal = {
            "schema_version": "2.0-graph",
            "slice_id": "INIT-test-slice-01",
            "metadata": {
                "author": "Agent Test",
                "last_updated": "2026-10-16",
                "status": "Active",
                "framework_version": "0.92.0",
            },
            "nodes": [
                {
                    "id": "BRD.01.01.a1b2",
                    "type": "business_objective",
                    "title": "Minimal Initiative",
                    "properties": {
                        "status": "Approved",
                        "summary": "Valid test initiative",
                    },
                },
                {
                    "id": "PRD.02.01.c3d4",
                    "type": "product_capability",
                    "title": "Minimal Requirement",
                    "properties": {
                        "status": "Approved",
                        "summary": "Valid requirement",
                    },
                },
            ],
            "edges": [
                {
                    "from": "BRD.01.01.a1b2",
                    "to": "PRD.02.01.c3d4",
                    "relation": "decomposes_to",
                }
            ],
        }
        errors = validate_schema(minimal, self.schema)
        self.assertEqual(errors, [])

    def test_reject_invalid_schema_version(self) -> None:
        """Reject graphs with invalid schema_version."""
        invalid = {
            "schema_version": "1.0.0",
            "slice_id": "INIT-01",
            "metadata": {
                "author": "Tester",
                "last_updated": "2026-10-16",
                "status": "Active",
                "framework_version": "0.92.0",
            },
            "nodes": [],
            "edges": [],
        }
        errors = validate_schema(invalid, self.schema)
        self.assertTrue(any("schema_version" in e for e in errors))

    def test_reject_invalid_node_type(self) -> None:
        """Reject unrecognized node types."""
        invalid = {
            "schema_version": "2.0-graph",
            "slice_id": "INIT-test-01",
            "metadata": {
                "author": "Tester",
                "last_updated": "2026-10-16",
                "status": "Active",
                "framework_version": "0.92.0",
            },
            "nodes": [
                {
                    "id": "BRD.01.01.a1b2",
                    "type": "invalid_node_type",
                    "title": "Bad Node",
                }
            ],
            "edges": [],
        }
        errors = validate_schema(invalid, self.schema)
        self.assertTrue(any("invalid_node_type" in e for e in errors))

    def test_reject_invalid_edge_relation(self) -> None:
        """Reject unrecognized edge relations."""
        invalid = {
            "schema_version": "2.0-graph",
            "slice_id": "INIT-test-01",
            "metadata": {
                "author": "Tester",
                "last_updated": "2026-10-16",
                "status": "Active",
                "framework_version": "0.92.0",
            },
            "nodes": [],
            "edges": [
                {
                    "from": "A",
                    "to": "B",
                    "relation": "invalid_relation",
                }
            ],
        }
        errors = validate_schema(invalid, self.schema)
        self.assertTrue(any("invalid_relation" in e for e in errors))

    def test_reject_missing_required_slice_id(self) -> None:
        """Reject graphs missing required slice_id."""
        invalid = {
            "schema_version": "2.0-graph",
            "metadata": {
                "author": "Tester",
                "last_updated": "2026-10-16",
                "status": "Active",
                "framework_version": "0.92.0",
            },
            "nodes": [],
            "edges": [],
        }
        errors = validate_schema(invalid, self.schema)
        self.assertTrue(any("missing required property 'slice_id'" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
