"""Unit: every TYPE-TEMPLATE.yaml is parseable and structurally sound."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import ARTIFACTS, template_path

REQUIRED_TOP_KEYS = {"metadata"}


class TemplateYamlTests(unittest.TestCase):
    def test_every_template_parses(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                with template_path(name).open(encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                self.assertIsInstance(data, dict, f"{name}: template root not a mapping")

    def test_every_template_carries_required_top_keys(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                with template_path(name).open(encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                missing = REQUIRED_TOP_KEYS - set(data)
                self.assertFalse(missing, f"{name}: missing top keys: {missing}")

    def test_every_section_with_size_target_has_positive_integer(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                with template_path(name).open(encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                offenders = []
                for section_key, section in data.items():
                    if isinstance(section, dict) and "_size_target" in section:
                        tgt = section["_size_target"]
                        if not (isinstance(tgt, int) and tgt > 0):
                            offenders.append((section_key, tgt))
                self.assertFalse(offenders, f"{name}: bad _size_target values: {offenders}")


if __name__ == "__main__":
    unittest.main()
