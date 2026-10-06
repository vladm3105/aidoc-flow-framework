"""Conformance: the seed contract (GD-08) — the ``SEED_CONTRACT.md`` doc and the
BRD ``seed_disposition:`` carrier that enforces it.

Part A of SEED-ABSORPTION-001. Guards two surfaces:

* the normative contract doc exists, is indexed in ``governance/README.md``, and
  names all three rules (frozen input / total disposition / BRD absorption point);
* the BRD template's ``seed_disposition:`` §16 carrier ships ``_required: false``
  (so it is non-breaking for BRDs authored before it) and its ``_example`` rows
  use only the three legal dispositions.
"""

import unittest

import yaml
from _spec import FRAMEWORK

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

    def test_mvp_skeleton_is_tombstone(self):
        """The retired MVP file is a tombstone pointer, not a template (#666)."""
        doc = yaml.safe_load(BRD_MVP_TEMPLATE.read_text(encoding="utf-8")) or {}
        self.assertEqual(set(doc), {"tombstone"}, f"MVP file regained content: {sorted(doc)}")
        self.assertEqual(doc["tombstone"]["status"], "retired")
        self.assertEqual(doc["tombstone"]["canonical_template"], "./BRD-TEMPLATE.yaml")


_BRD_HEAD = (
    "---\ndoc_id: BRD-01\nartifact_type: BRD\n---\n# BRD-01\n"
    "- **BRD.01.07.be48 — Code Uniqueness**: every code is unique.\n"
)


def _brd_with_ledger(ledger_yaml: str) -> list[tuple[str, str]]:
    return [("01_BRD/BRD-01.md", f"{_BRD_HEAD}\n```yaml\n{ledger_yaml}\n```\n")]


_SEED_V2 = 'document_control:\n  document_id: SEED-auth\n  version: "2.0"\n  status: Approved\n'


def _pinned_row(version: str) -> str:
    return (
        "seed_disposition:\n"
        "  - claim: uniqueness\n"
        "    disposition: absorbed\n"
        "    brd_elements: [BRD.01.07.be48]\n"
        f'    seed_version: "{version}"\n'
    )


class Seed01VersionPin(unittest.TestCase):
    """GD-36: `absorbed` rows pin the seed version they were absorbed from."""

    def _codes(self, corpus):
        return [f.code for f in _check_seed_disposition(corpus)]

    def test_pin_match_passes(self):
        corpus = _brd_with_ledger(_pinned_row("2.0"))
        corpus.append(("seed/architecture/auth.md", _SEED_V2))
        self.assertEqual(self._codes(corpus), [])

    def test_stale_pin_is_error(self):
        """A row pinned to an archived seed version fails until re-pointed."""
        corpus = _brd_with_ledger(_pinned_row("2.0"))
        corpus.append(("seed/architecture/auth.md", _SEED_V2.replace('"2.0"', '"1.0"')))
        self.assertEqual(self._codes(corpus), ["SEED01"])

    def test_unpinned_row_passes_as_before(self):
        """Pre-pin corpora stay green — pins are required only for rows
        authored or re-pointed after a supersede."""
        corpus = _brd_with_ledger(
            "seed_disposition:\n"
            "  - claim: uniqueness\n"
            "    disposition: absorbed\n"
            "    brd_elements: [BRD.01.07.be48]\n"
        )
        corpus.append(("seed/architecture/auth.md", _SEED_V2))
        self.assertEqual(self._codes(corpus), [])

    def test_absent_seed_file_skips(self):
        """A pinned row with no seed file in the corpus cannot be judged —
        skip, never fail."""
        self.assertEqual(self._codes(_brd_with_ledger(_pinned_row("2.0"))), [])


class Seed01PerFileResolution(unittest.TestCase):
    """#723: rows naming `seed_file:` resolve against THAT file, not the set."""

    def _codes(self, corpus):
        return [f.code for f in _check_seed_disposition(corpus)]

    def _two_seed_corpus(self, ledger_yaml: str):
        corpus = _brd_with_ledger(ledger_yaml)
        corpus.append(("seed/architecture/auth.md", _SEED_V2.replace('"2.0"', '"1.0"')))
        corpus.append(("seed/architecture/billing.md", _SEED_V2))
        return corpus

    def _file_row(self, seed_file: str, version: str) -> str:
        return (
            "seed_disposition:\n"
            "  - claim: uniqueness\n"
            "    disposition: absorbed\n"
            "    brd_elements: [BRD.01.07.be48]\n"
            f"    seed_file: {seed_file}\n"
            f'    seed_version: "{version}"\n'
        )

    def test_stale_pin_against_named_file_is_error(self):
        """A row pinned to the archived version fails even though ANOTHER
        seed file in the corpus carries the pinned version — the mask #723
        reports."""
        corpus = self._two_seed_corpus(self._file_row("seed/architecture/billing.md", "1.0"))
        self.assertEqual(self._codes(corpus), ["SEED01"])

    def test_current_pin_against_named_file_passes(self):
        corpus = self._two_seed_corpus(self._file_row("seed/architecture/billing.md", "2.0"))
        self.assertEqual(self._codes(corpus), [])

    def test_row_without_seed_file_keeps_set_membership(self):
        """Rows authored before the field keep the legacy behavior: any
        corpus seed carrying the pin satisfies it."""
        corpus = self._two_seed_corpus(_pinned_row("2.0"))
        self.assertEqual(self._codes(corpus), [])

    def test_legacy_message_names_no_single_version(self):
        """The set-membership diagnostic reports the whole corpus set instead
        of an arbitrary `sorted(...)[0]` that may belong to another file."""
        corpus = self._two_seed_corpus(_pinned_row("9.9"))
        findings = _check_seed_disposition(corpus)
        self.assertEqual([f.code for f in findings], ["SEED01"])
        self.assertIn("1.0", findings[0].message)
        self.assertIn("2.0", findings[0].message)

    def test_named_but_absent_file_skips(self):
        """A `seed_file:` naming no corpus file cannot be judged — skip."""
        corpus = _brd_with_ledger(self._file_row("seed/architecture/gone.md", "1.0"))
        corpus.append(("seed/architecture/auth.md", _SEED_V2))
        self.assertEqual(self._codes(corpus), [])


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


class SeedTemplateContract(unittest.TestCase):
    """GD-49: canonical SEED-TEMPLATE.md existence, frontmatter schema, and guidance."""

    def test_template_exists(self):
        self.assertTrue(
            (FRAMEWORK / "templates" / "SEED-TEMPLATE.md").is_file(),
            "framework/templates/SEED-TEMPLATE.md is missing",
        )

    def test_template_document_control(self):
        text = (FRAMEWORK / "templates" / "SEED-TEMPLATE.md").read_text(encoding="utf-8")
        parts = text.split("---")
        self.assertGreaterEqual(len(parts), 3, "SEED-TEMPLATE.md missing YAML frontmatter")
        data = yaml.safe_load(parts[1])
        self.assertIn("document_control", data)
        dc = data["document_control"]
        for key in (
            "document_id",
            "version",
            "status",
            "author",
            "framework_version",
            "supersedes",
            "revision_history",
        ):
            self.assertIn(key, dc, f"SEED-TEMPLATE.md document_control missing {key}")

    def test_template_version_within_regex_limit(self):
        """Line distance between document_control: and version: must be <= 12 lines for SEED01 regex."""
        lines = (
            (FRAMEWORK / "templates" / "SEED-TEMPLATE.md").read_text(encoding="utf-8").splitlines()
        )
        dc_idx = None
        ver_idx = None
        for i, line in enumerate(lines):
            if "document_control:" in line:
                dc_idx = i
            elif dc_idx is not None and "version:" in line:
                ver_idx = i
                break
        self.assertIsNotNone(dc_idx, "document_control: not found")
        self.assertIsNotNone(ver_idx, "version: not found")
        self.assertLessEqual(ver_idx - dc_idx, 12, "version: is >12 lines below document_control:")

    def test_gd49_recorded(self):
        decisions = (GOVERNANCE / "DECISIONS.md").read_text(encoding="utf-8")
        self.assertIn("## GD-49", decisions, "GD-49 not recorded in governance/DECISIONS.md")

    def test_decision_workflow_reconciled(self):
        """GD-36 reconciliation: DECISION_WORKFLOW.md must not contain 'Frozen after first BRD'."""
        text = (GOVERNANCE / "DECISION_WORKFLOW.md").read_text(encoding="utf-8")
        self.assertNotIn("Frozen after first BRD", text)


if __name__ == "__main__":
    unittest.main()
