"""Conformance: the seed contract (GD-08) — the ``SEED_CONTRACT.md`` doc and the
BRD ``seed_disposition:`` carrier that enforces it.

Part A of SEED-ABSORPTION-001. Guards two surfaces:

* the normative contract doc exists, is indexed in ``governance/README.md``, and
  names all three rules (frozen input / total disposition / BRD absorption point);
* the BRD template's ``seed_disposition:`` §16 carrier ships ``_required: false``
  (so it is non-breaking for BRDs authored before it) and its ``_example`` rows
  use only the three legal dispositions.
"""

import sys
import unittest

import yaml
from _spec import FRAMEWORK, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import _check_seed_disposition  # noqa: E402

GOVERNANCE = FRAMEWORK / "governance"
SEED_CONTRACT = GOVERNANCE / "SEED_CONTRACT.md"
BRD_TEMPLATE = FRAMEWORK / "layers" / "01_BRD" / "BRD-TEMPLATE.yaml"
BRD_MVP_TEMPLATE = FRAMEWORK / "layers" / "01_BRD" / "BRD-MVP-TEMPLATE.yaml"

_LEGAL_DISPOSITIONS = {"absorbed", "rejected", "deferred"}


class SeedContractDoc(unittest.TestCase):
    def test_contract_exists(self):
        self.assertTrue(SEED_CONTRACT.is_file(), "framework/governance/SEED_CONTRACT.md is missing")

    def test_contract_is_indexed(self):
        readme = (GOVERNANCE / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "SEED_CONTRACT.md", readme, "SEED_CONTRACT.md not indexed in governance/README.md"
        )

    def test_contract_names_all_three_rules(self):
        text = SEED_CONTRACT.read_text(encoding="utf-8").lower()
        # Rule 1 frozen input, Rule 2 total disposition, Rule 3 BRD absorption point.
        self.assertIn("frozen", text, "contract does not name the frozen-input rule")
        self.assertIn(
            "total disposition", text, "contract does not name the total-disposition rule"
        )
        self.assertIn(
            "absorption point", text, "contract does not name the BRD-absorption-point rule"
        )
        for disposition in _LEGAL_DISPOSITIONS:
            self.assertIn(
                disposition, text, f"contract does not name the '{disposition}' disposition"
            )

    def test_gd08_recorded(self):
        decisions = (GOVERNANCE / "DECISIONS.md").read_text(encoding="utf-8")
        self.assertIn("## GD-08", decisions, "GD-08 not recorded in governance/DECISIONS.md")


class BrdSeedDispositionCarrier(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(BRD_TEMPLATE.read_text(encoding="utf-8"))

    def test_section_present(self):
        self.assertIn(
            "seed_disposition",
            self.doc,
            "BRD-TEMPLATE.yaml is missing the seed_disposition: carrier (GD-08)",
        )

    def test_section_is_optional(self):
        """Ships ``_required: false`` — else every already-authored BRD emits a
        STRUCT01 error and the BRD golden acceptance test breaks (plan Part A)."""
        self.assertIs(
            self.doc["seed_disposition"].get("_required"),
            False,
            "seed_disposition: must ship `_required: false` (additive / non-breaking)",
        )

    def test_total_sections_bumped(self):
        self.assertEqual(
            self.doc["metadata"]["total_sections"],
            16,
            "total_sections must move 15 -> 16 when seed_disposition: §16 is appended",
        )

    def test_example_rows_use_only_legal_dispositions(self):
        example = self.doc["seed_disposition"].get("_example")
        self.assertIsInstance(example, list, "seed_disposition._example must be a list of rows")
        self.assertTrue(example, "seed_disposition._example must carry at least one sample row")
        for row in example:
            self.assertIn(
                row.get("disposition"),
                _LEGAL_DISPOSITIONS,
                f"_example row uses an illegal disposition: {row.get('disposition')!r}",
            )
            # Real hex element IDs only in the sample — never a templated placeholder.
            for elem in row.get("brd_elements", []) or []:
                self.assertRegex(
                    elem,
                    r"^BRD\.\d{2,}\.\d{2,}\.[a-f0-9]{4,8}$",
                    f"_example absorbed row must cite a real BRD element id, got {elem!r}",
                )

    def test_mvp_skeleton_has_seed_disposition_row(self):
        mvp = BRD_MVP_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(
            "seed_disposition",
            mvp,
            "BRD-MVP-TEMPLATE.yaml is missing the seed_disposition skeleton row",
        )


_BRD_HEAD = (
    "---\ndoc_id: BRD-01\nartifact_type: BRD\n---\n# BRD-01\n"
    "- **BRD.01.07.be48 — Code Uniqueness**: every code is unique.\n"
)


def _brd_with_ledger(ledger_yaml: str) -> list[tuple[str, str]]:
    return [("01_BRD/BRD-01.md", f"{_BRD_HEAD}\n```yaml\n{ledger_yaml}\n```\n")]


class Seed01Lint(unittest.TestCase):
    def _codes(self, corpus):
        return [f.code for f in _check_seed_disposition(corpus)]

    def test_absent_ledger_is_silent(self):
        """The carrier is optional (`_required: false`) — a BRD with no ledger
        block emits nothing (non-breaking for pre-contract corpora)."""
        self.assertEqual(_check_seed_disposition([("01_BRD/BRD-01.md", _BRD_HEAD)]), [])

    def test_well_formed_ledger_passes(self):
        corpus = _brd_with_ledger(
            "seed_disposition:\n"
            "  - claim: uniqueness\n"
            "    disposition: absorbed\n"
            "    brd_elements: [BRD.01.07.be48]\n"
            "  - claim: vanity codes\n"
            "    disposition: rejected\n"
            "    rationale: not in scope\n"
            "  - claim: rate limiting\n"
            "    disposition: deferred\n"
            "    rationale: later\n"
            "    target_cycle: BRD-02\n"
        )
        self.assertEqual(self._codes(corpus), [])

    def test_malformed_block(self):
        self.assertEqual(self._codes(_brd_with_ledger("seed_disposition: not-a-list")), ["SEED01"])

    def test_invalid_disposition(self):
        corpus = _brd_with_ledger("seed_disposition:\n  - claim: x\n    disposition: maybe\n")
        self.assertEqual(self._codes(corpus), ["SEED01"])

    def test_absorbed_target_must_resolve(self):
        """An `absorbed` row naming an element that is declared nowhere (only in
        its own ledger row) must not self-resolve — SEED01 fires."""
        corpus = _brd_with_ledger(
            "seed_disposition:\n"
            "  - claim: bogus\n"
            "    disposition: absorbed\n"
            "    brd_elements: [BRD.01.07.9999]\n"
        )
        self.assertEqual(self._codes(corpus), ["SEED01"])

    def test_absorbed_needs_an_element(self):
        corpus = _brd_with_ledger("seed_disposition:\n  - claim: x\n    disposition: absorbed\n")
        self.assertEqual(self._codes(corpus), ["SEED01"])

    def test_non_string_claim_is_reported_not_crashing(self):
        """A non-string YAML scalar for `claim` (e.g. unquoted `42`) must be
        REPORTED as malformed, never crash the lint run (regression: _bdd_line_of
        did `token in line` on the raw value)."""
        corpus = _brd_with_ledger(
            "seed_disposition:\n  - claim: 42\n    disposition: absorbed\n"
            "    brd_elements: [BRD.01.07.be48]\n"
        )
        # No exception, and the malformed claim is surfaced.
        self.assertIn("SEED01", self._codes(corpus))

    def test_deferred_needs_target_cycle(self):
        corpus = _brd_with_ledger(
            "seed_disposition:\n  - claim: x\n    disposition: deferred\n    rationale: later\n"
        )
        self.assertEqual(self._codes(corpus), ["SEED01"])

    def test_seed01_is_catalogued(self):
        catalog = (GOVERNANCE / "LINT_RULES.md").read_text(encoding="utf-8")
        self.assertIn("`SEED01`", catalog, "SEED01 not documented in LINT_RULES.md")


if __name__ == "__main__":
    unittest.main()
