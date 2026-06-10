"""Conformance: per-layer template §7 Traceability block matches the
necessary-upstream contract (NECESSARY-UPSTREAM-001).

Each layer's `<X>-TEMPLATE.yaml` declares a `traceability:` block with
an `upstream:` mapping listing `<x>_references:` slots. Under the
necessary-upstream contract, each layer's slot set must equal the
`required_tags` declared in `LAYER_REGISTRY.yaml` for that layer — not
the cumulative closure. BRD has no upstream block (root).

The companion test `test_registry.RegistryTraceability.\
test_required_tags_match_necessary_upstream_table` asserts the registry
side of the same invariant; this file asserts the template side.
"""

import re
import unittest

import yaml
from _spec import FRAMEWORK, load_registry, registry_layers

REGISTRY = load_registry()
LAYERS = registry_layers()


def _layer_template_path(layer):
    return FRAMEWORK / layer["folder"] / layer["template"]


def _upstream_reference_slots(template_path):
    """Extract the set of `<x>_references:` slot names declared in a template's
    `traceability.upstream:` block.

    Returns an empty set when the template has no `upstream:` block (BRD)
    or when the template is YAML-loadable but the block is absent.
    """
    text = template_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        return set()
    trace = data.get("traceability") or {}
    if not isinstance(trace, dict):
        return set()
    upstream = trace.get("upstream") or {}
    if not isinstance(upstream, dict):
        return set()
    return {key for key in upstream if key.endswith("_references")}


def _expected_slots(layer):
    """The slot names a layer's §7 block should declare, derived from
    `required_tags` in the registry.

    E.g., `required_tags: [ears, bdd]` → `{"ears_references", "bdd_references"}`.
    """
    return {f"{tag}_references" for tag in layer["required_tags"]}


class NecessaryUpstreamTemplateBlocks(unittest.TestCase):
    """Each layer's §7 Traceability `upstream:` block lists ONLY the
    `<x>_references:` slots corresponding to the layer's `required_tags`.
    """

    def test_template_upstream_slots_match_necessary_upstream(self):
        for layer in LAYERS:
            artifact = layer["artifact"]
            template = _layer_template_path(layer)
            with self.subTest(layer=layer["number"], artifact=artifact):
                self.assertTrue(
                    template.is_file(),
                    f"missing template: {template}",
                )
                actual = _upstream_reference_slots(template)
                expected = _expected_slots(layer)
                self.assertEqual(
                    actual,
                    expected,
                    f"{artifact}-TEMPLATE.yaml §7 upstream slots {sorted(actual)} "
                    f"do not match required_tags-derived expectation {sorted(expected)}",
                )


class TemplateConsistencyWithRegistry(unittest.TestCase):
    """Cross-check: every `<x>_references:` slot in a template's §7 block
    corresponds to a layer's `required_tags` entry (no orphan slots that
    reference layers outside the necessary set).
    """

    KNOWN_LAYER_PREFIXES = {"brd", "prd", "ears", "bdd", "adr", "spec", "tdd", "iplan"}
    SLOT_PATTERN = re.compile(r"^([a-z]+)_references$")

    def test_no_orphan_upstream_slots(self):
        for layer in LAYERS:
            artifact = layer["artifact"]
            template = _layer_template_path(layer)
            required = set(layer["required_tags"])
            with self.subTest(layer=layer["number"], artifact=artifact):
                for slot in _upstream_reference_slots(template):
                    match = self.SLOT_PATTERN.match(slot)
                    self.assertIsNotNone(
                        match,
                        f"{artifact} template §7 slot {slot!r} does not match "
                        f"`<layer>_references` pattern",
                    )
                    prefix = match.group(1)
                    self.assertIn(
                        prefix,
                        self.KNOWN_LAYER_PREFIXES,
                        f"{artifact} template §7 slot {slot!r} references "
                        f"unknown layer prefix {prefix!r}",
                    )
                    self.assertIn(
                        prefix,
                        required,
                        f"{artifact} template §7 slot {slot!r} references "
                        f"layer {prefix!r} which is NOT in required_tags "
                        f"{sorted(required)} — orphan slot",
                    )


if __name__ == "__main__":
    unittest.main()
