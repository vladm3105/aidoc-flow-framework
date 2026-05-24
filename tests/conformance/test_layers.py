"""Conformance: ``framework/layers/`` templates and index templates."""

import unittest

import yaml
from _spec import FRAMEWORK, registry_layers

LAYERS = registry_layers()


class LayerFiles(unittest.TestCase):
    def test_layer_triad_present(self):
        """Each layer folder has its template, README, and an index template."""
        for layer in LAYERS:
            folder = FRAMEWORK / layer["folder"]
            artifact = layer["artifact"]
            with self.subTest(layer=layer["number"]):
                self.assertTrue(
                    (folder / layer["template"]).is_file(),
                    f"missing template for {artifact}",
                )
                self.assertTrue(
                    (folder / "README.md").is_file(),
                    f"missing README for {artifact}",
                )
                index_md = folder / f"{artifact}-00_index.TEMPLATE.md"
                index_yaml = folder / f"{artifact}-00_index.TEMPLATE.yaml"
                self.assertTrue(
                    index_md.is_file() or index_yaml.is_file(),
                    f"missing index template for {artifact}",
                )


class LayerTemplateMetadata(unittest.TestCase):
    def test_template_parses_and_metadata_matches_registry(self):
        for layer in LAYERS:
            path = FRAMEWORK / layer["folder"] / layer["template"]
            with self.subTest(layer=layer["number"]):
                with path.open(encoding="utf-8") as fh:
                    document = yaml.safe_load(fh)
                metadata = document.get("metadata", {})
                self.assertEqual(
                    metadata.get("layer"),
                    layer["number"],
                    "template metadata.layer disagrees with the registry",
                )
                self.assertTrue(
                    metadata.get("document_type"),
                    "template metadata.document_type is missing or empty",
                )


if __name__ == "__main__":
    unittest.main()
