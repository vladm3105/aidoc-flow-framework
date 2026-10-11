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
                index_yaml = folder / f"{artifact}-00_index.TEMPLATE.yaml"
                self.assertTrue(
                    index_yaml.is_file(),
                    f"missing YAML index template for {artifact} (GD-75)",
                )

    def test_no_mvp_templates_exist(self):
        """All 8 legacy *-MVP-TEMPLATE.yaml tombstones removed in CHG-89 (GD-76).

        Asserts that zero MVP templates exist anywhere under framework/layers/.
        """
        mvp_files = sorted(p.relative_to(FRAMEWORK).as_posix() for p in FRAMEWORK.glob("layers/*/*-MVP-TEMPLATE.*"))
        self.assertEqual(
            [],
            mvp_files,
            f"MVP templates must not exist in framework/layers/ (GD-76): {mvp_files}",
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
