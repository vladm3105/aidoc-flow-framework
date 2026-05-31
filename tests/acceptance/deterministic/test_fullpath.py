"""Deterministic full-path acceptance: BRD-01 → IPLAN-01 chain."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import FIXTURES_ROOT, headings, run_lint, template_sections  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS  # noqa: E402

CHAIN = FIXTURES_ROOT / "fullpath" / "golden_chain"


class FullpathChainTests(unittest.TestCase):
    def test_chain_lint_passes(self):
        rc, findings = run_lint(CHAIN)
        self.assertEqual(rc, 0, f"fullpath chain lint failed:\n{findings}")
        self.assertEqual([], findings, f"chain emitted findings:\n{findings}")

    def test_every_layer_has_one_artifact(self):
        for idx, name in enumerate(ARTIFACTS, start=1):
            with self.subTest(layer=name):
                folder = CHAIN / f"{idx:02d}_{name}"
                hits = list(folder.glob(f"{name}-01*"))
                self.assertEqual(len(hits), 1, f"{folder}: expected 1 artifact, got {len(hits)}")

    def test_every_layer_has_required_sections(self):
        for idx, name in enumerate(ARTIFACTS, start=1):
            with self.subTest(layer=name):
                folder = CHAIN / f"{idx:02d}_{name}"
                artifact = next(folder.glob(f"{name}-01*"))
                missing = [s for s in template_sections(name) if s not in set(headings(artifact))]
                self.assertFalse(missing, f"{name}-01: missing required sections: {missing}")

    def test_forward_tag_closure(self):
        """Every @<upstream>: tag in a downstream artifact names an upstream layer
        that exists in the chain. (Strict element-ID match deferred to Phase 13.)"""
        for idx in range(2, 9):
            name = ARTIFACTS[idx - 1]
            folder = CHAIN / f"{idx:02d}_{name}"
            artifact = next(folder.glob(f"{name}-01*"))
            text = artifact.read_text(encoding="utf-8")
            for upstream_idx in range(1, idx):
                upstream_name = ARTIFACTS[upstream_idx - 1]
                tag = f"@{upstream_name.lower()}:"
                if tag in text:
                    # Confirm the upstream layer folder exists in the chain
                    self.assertTrue(
                        (CHAIN / f"{upstream_idx:02d}_{upstream_name}").exists(),
                        f"{name}-01 has {tag} but layer {upstream_name} missing from chain",
                    )
