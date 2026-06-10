"""Conformance: ``framework/registry/LAYER_REGISTRY.yaml`` self-consistency."""

import re
import unittest

from _spec import ARTIFACTS, FRAMEWORK, load_registry, registry_layers

REGISTRY = load_registry()
LAYERS = registry_layers()

REQUIRED_LAYER_KEYS = {
    "number",
    "artifact",
    "name",
    "folder",
    "extensions",
    "required_tags",
    "can_reference",
    "error_prefix",
    "optional",
    "description",
    "template",
    "downstream",
}


class RegistryStructure(unittest.TestCase):
    def test_top_level_keys(self):
        for key in ("metadata", "layers", "layer_groups", "c4_mapping", "id_patterns"):
            self.assertIn(key, REGISTRY)

    def test_exactly_eight_layers(self):
        self.assertEqual(len(LAYERS), 8)

    def test_layer_numbers_are_dense_one_to_eight(self):
        self.assertEqual([layer["number"] for layer in LAYERS], list(range(1, 9)))

    def test_total_layers_metadata_matches(self):
        self.assertEqual(REGISTRY["metadata"]["total_layers"], len(LAYERS))

    def test_each_layer_has_required_keys(self):
        for layer in LAYERS:
            with self.subTest(layer=layer.get("number")):
                missing = REQUIRED_LAYER_KEYS - set(layer)
                self.assertEqual(missing, set(), f"missing keys: {missing}")

    def test_artifacts_in_canonical_order(self):
        self.assertEqual([layer["artifact"] for layer in LAYERS], ARTIFACTS)

    def test_error_prefix_matches_artifact(self):
        for layer in LAYERS:
            with self.subTest(layer=layer["number"]):
                self.assertEqual(layer["error_prefix"], layer["artifact"])


class RegistryTraceability(unittest.TestCase):
    def test_downstream_chain(self):
        for i, layer in enumerate(LAYERS):
            expected = [LAYERS[i + 1]["artifact"]] if i + 1 < len(LAYERS) else ["CODE"]
            with self.subTest(layer=layer["number"]):
                self.assertEqual(layer["downstream"], expected)

    def test_required_tags_match_necessary_upstream_table(self):
        """Each layer declares ONLY the upstream layers its evaluation reads.

        Under the necessary-upstream contract (NECESSARY-UPSTREAM-001),
        lineage to layers further upstream is discoverable transitively
        through the @-tag chain, not via cumulative redeclaration.
        """
        expected_required_tags = {
            "BRD": [],
            "PRD": ["brd"],
            "EARS": ["prd"],
            "BDD": ["ears"],
            "ADR": ["ears", "bdd"],
            "SPEC": ["ears", "bdd", "adr"],
            "TDD": ["ears", "bdd", "adr", "spec"],
            "IPLAN": ["spec", "tdd"],
        }
        for layer in LAYERS:
            artifact = layer["artifact"]
            with self.subTest(layer=layer["number"], artifact=artifact):
                self.assertEqual(layer["required_tags"], expected_required_tags[artifact])

    def test_can_reference_matches_required_tags(self):
        for layer in LAYERS:
            with self.subTest(layer=layer["number"]):
                self.assertEqual(
                    layer["can_reference"],
                    [tag.upper() for tag in layer["required_tags"]],
                )


class RegistryFilesystem(unittest.TestCase):
    def test_folder_and_template_resolve(self):
        for layer in LAYERS:
            with self.subTest(layer=layer["number"]):
                template = FRAMEWORK / layer["folder"] / layer["template"]
                self.assertTrue(template.is_file(), f"missing template: {template}")


class RegistryLayerGroups(unittest.TestCase):
    def test_every_layer_in_exactly_one_group(self):
        grouped = []
        for group in REGISTRY["layer_groups"].values():
            grouped.extend(group["layers"])
        self.assertEqual(len(grouped), len(set(grouped)), "a layer is in two groups")
        self.assertEqual(sorted(grouped), list(range(1, 9)))


class RegistryC4Mapping(unittest.TestCase):
    def test_c4_artifacts_are_known(self):
        known = set(ARTIFACTS) | {"CODE"}
        for name, entry in REGISTRY["c4_mapping"].items():
            artifacts = []
            if "artifact" in entry:
                artifacts.append(entry["artifact"])
            artifacts.extend(entry.get("artifacts", []))
            for artifact in artifacts:
                with self.subTest(c4_level=name, artifact=artifact):
                    self.assertIn(artifact, known)


class RegistryIdPatterns(unittest.TestCase):
    def test_id_patterns_compile(self):
        for name, pattern in REGISTRY["id_patterns"].items():
            with self.subTest(pattern=name):
                re.compile(pattern)


if __name__ == "__main__":
    unittest.main()
