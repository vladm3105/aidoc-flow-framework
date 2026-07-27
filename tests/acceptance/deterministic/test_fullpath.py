"""Deterministic full-path acceptance: BRD-01 → IPLAN-01 chain."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import (  # noqa: E402
    FIXTURES_ROOT,
    assert_lint_matches_manifest,
    assert_no_orphan_manifests,
    headings,
    subtype_of,
    template_sections,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS  # noqa: E402

CHAIN = FIXTURES_ROOT / "fullpath" / "golden_chain"
BROKEN_CHAIN = FIXTURES_ROOT / "fullpath" / "broken_chain"


class FullpathChainTests(unittest.TestCase):
    def test_chain_lint_passes(self):
        """The chain must be gate-clean and emit exactly its pinned warnings."""
        assert_lint_matches_manifest(self, CHAIN)

    def test_no_orphan_expected_warnings_manifests(self):
        """Every manifest must point at a target that still exists."""
        assert_no_orphan_manifests(self)

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
                # Pass the artifact's subtype so `_required_when_subtype:`
                # sections (CLEANUP-PR-E item 17, IPLAN) filter correctly.
                expected = template_sections(name, subtype=subtype_of(artifact))
                missing = [s for s in expected if s not in set(headings(artifact))]
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


class FullpathBrokenChainTests(unittest.TestCase):
    """The broken-chain fixture exists and is structurally distinct from golden."""

    def test_broken_chain_exists(self):
        self.assertTrue(BROKEN_CHAIN.is_dir(), "broken_chain/ missing")
        for idx, name in enumerate(ARTIFACTS, start=1):
            folder = BROKEN_CHAIN / f"{idx:02d}_{name}"
            self.assertTrue(folder.is_dir(), f"{folder}: missing")

    def test_broken_chain_contains_deliberately_broken_marker(self):
        prd = next((BROKEN_CHAIN / "02_PRD").glob("PRD-01_golden.*"))
        text = prd.read_text(encoding="utf-8")
        self.assertIn(
            "BRD.01.99.deaf",
            text,
            "broken_chain/PRD-01 lost its broken-cascade marker",
        )
