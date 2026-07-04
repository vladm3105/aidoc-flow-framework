"""HERMES-PARITY-PHASE-2: playbook loader + finding_filter (citation floor)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.review.finding_filter import emit_coverage, filter_findings  # noqa: E402
from mcp_server.review.playbook_loader import (  # noqa: E402
    Playbook,
    is_crew_lens,
    load_playbook,
    normalize_layer,
)

_REPO_ROOT = ROOT.resolve().parents[1]  # platforms/hermes -> repo root
_BRD_LENSES = ["architect", "business_analyst", "auditor", "chaos_engineer", "security_engineer"]
_PRD_LENSES = [
    "product_owner",
    "architect",
    "tech_lead",
    "chaos_engineer",
    "security_engineer",
    "auditor",
]


class TestNormalizeLayer:
    def test_short_and_dir_forms(self):
        assert normalize_layer("brd") == ("BRD", "01_BRD")
        assert normalize_layer("01_BRD") == ("BRD", "01_BRD")
        assert normalize_layer("PRD") == ("PRD", "02_PRD")


class TestLoadPlaybook:
    @pytest.mark.parametrize(
        "layer,lens", [("brd", ln) for ln in _BRD_LENSES] + [("prd", ln) for ln in _PRD_LENSES]
    )
    def test_crew_lens_playbook_loads_with_checks(self, layer, lens):
        pb = load_playbook(layer, lens)
        assert isinstance(pb, Playbook)
        assert pb.content
        # every real playbook has at least one C-check
        assert pb.check_ids, f"{layer}/{lens} parsed no C-checks"
        assert all(c.startswith("C") for c in pb.check_ids)

    @pytest.mark.parametrize("persona", ["fact_checker", "chairperson"])
    def test_non_crew_persona_returns_none(self, persona):
        # fact_checker + chairperson are BRD branch personas with NO playbook —
        # they must be skipped (None), never BRANCH_FAILED.
        assert load_playbook("brd", persona) is None
        assert is_crew_lens("brd", persona) is False

    def test_crew_membership(self):
        assert is_crew_lens("brd", "architect") is True
        assert is_crew_lens("prd", "product_owner") is True
        assert is_crew_lens("brd", "product_owner") is False  # PRD lens, not BRD


class TestFindingFilter:
    def test_discard_uncited_keep_cited(self):
        valid = {"C1", "C2"}
        findings = [
            {"message": "cited", "check": "C1"},
            {"message": "beyond", "check": "beyond-checklist:reliability"},
            {"message": "uncited"},  # no check
            {"message": "bogus", "check": "C9"},  # unknown id
        ]
        kept, discarded = filter_findings(findings, valid)
        assert [f["message"] for f in kept] == ["cited", "beyond"]
        reasons = {f["message"]: f["reason"] for f in discarded}
        assert reasons == {"uncited": "no_check_citation", "bogus": "unknown_check"}

    def test_emit_coverage(self):
        findings = [
            {"check": "C1"},
            {"check": "C1"},
            {"check": "C3"},
            {"check": "beyond-checklist:x"},
            {"message": "no-check"},
        ]
        assert emit_coverage(findings) == {"C1": 2, "C3": 1, "beyond_checklist": 1}


class TestFindingFilterVendorDrift:
    def test_hermes_finding_filter_is_byte_identical_to_plugin(self):
        hermes = (SRC / "mcp_server" / "review" / "finding_filter.py").read_bytes()
        plugin = (
            _REPO_ROOT / "platforms" / "claude-code-plugin" / "tools" / "finding_filter.py"
        ).read_bytes()
        assert hermes == plugin, "vendored finding_filter.py drifted from the plugin canonical copy"


class TestAllLayerPlaybookCoverage:
    """HERMES-PARITY-PHASE-3 (H-5/H-10): every REVIEW_CREWS.yaml crew lens — all 8
    lifecycle layers + the CHG overlay — resolves a playbook with Cn ids. Locks in
    the Phase-2 layer-agnostic injection payoff."""

    def _crews(self):
        import yaml

        data = yaml.safe_load((_REPO_ROOT / "framework/governance/REVIEW_CREWS.yaml").read_text())
        return data["crews"]

    def test_all_lifecycle_layers_plus_chg_resolve(self):
        crews = self._crews()
        expected_layers = {"BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN", "CHG"}
        assert expected_layers <= set(crews), f"missing crews: {expected_layers - set(crews)}"
        failures = []
        for layer, crew in crews.items():
            for lens in crew["review"]:
                pb = load_playbook(layer, lens)
                if pb is None or not pb.check_ids:
                    failures.append(f"{layer}/{lens}")
        assert not failures, f"crew lenses with no resolvable playbook: {failures}"
