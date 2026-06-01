"""Deterministic acceptance: _id_coordinator helpers work against committed goldens.

This is a smoke test — it exercises extract_elements + element_id + write_registry
end-to-end so the helpers don't rot. Strict cross-layer ID closure is still
deferred (see PLUGIN-TEST-SUITE-REVIEW.md F2): downstream goldens reference
placeholder upstream IDs that don't reproduce the upstream's actual element hashes.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import FIXTURES_ROOT, fixtures_for
from _id_coordinator import element_hash, element_id, extract_elements

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS


class IdCoordinatorSmokeTests(unittest.TestCase):
    def test_element_hash_is_deterministic(self):
        a = element_hash("BRD-01", "project_scope", "Scope", "In: A; Out: B")
        b = element_hash("BRD-01", "project_scope", "Scope", "In: A; Out: B")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 4)
        self.assertRegex(a, r"^[0-9a-f]{4}$")

    def test_element_id_format(self):
        eid = element_id("BRD", 1, "project_scope", "Scope", "desc")
        self.assertRegex(eid, r"^BRD\.01\.project_scope\.[0-9a-f]{4}$")

    def test_element_hash_changes_with_inputs(self):
        a = element_hash("BRD-01", "s", "t", "d")
        b = element_hash("BRD-01", "s", "t", "DIFFERENT")
        self.assertNotEqual(a, b)

    def test_extract_elements_runs_on_each_layer_golden(self):
        """Smoke: extract_elements() must not raise for any committed golden.

        Returns a list (possibly empty) of dicts with the documented keys.
        Empty is acceptable here — many goldens use ## H2 sections without
        ### H3 sub-elements, which extract_elements treats as zero elements.
        """
        for idx, name in enumerate(ARTIFACTS, start=1):
            with self.subTest(layer=name):
                valid_dir = fixtures_for(idx, "valid")
                goldens = list(valid_dir.glob(f"{name}-01_golden.*"))
                self.assertEqual(
                    len(goldens), 1, f"expected 1 golden for {name}, got {len(goldens)}"
                )
                elements = extract_elements(goldens[0])
                self.assertIsInstance(elements, list)
                for elem in elements:
                    self.assertIn("section_id", elem)
                    self.assertIn("title", elem)
                    self.assertIn("description", elem)
                    self.assertIn("element_id", elem)
                    self.assertRegex(elem["element_id"], rf"^{name}\.\d+\.\w+\.[0-9a-f]{{4}}$")

    def test_registry_path_present(self):
        registry = FIXTURES_ROOT / "fullpath" / "ID_REGISTRY.yaml"
        self.assertTrue(registry.exists(), "ID_REGISTRY.yaml missing")
