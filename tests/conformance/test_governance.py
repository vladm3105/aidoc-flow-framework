"""Conformance: ``framework/governance/`` files are present and parseable."""

import re
import unittest

import yaml
from _spec import ARTIFACTS, FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"
CHG = GOVERNANCE / "chg"

# The six CHG gates. Held as a literal so that deleting a gate file shrinks the
# discovered set and fails, rather than silently reducing what is compared.
EXPECTED_GATES = frozenset({"GATE-01", "GATE-03", "GATE-06", "GATE-08", "GATE-CODE", "GATE-SPEC"})

_CODE = re.compile(r"\b(GATE-[A-Z0-9]+)-([EW])(\d{3})\b")

EXPECTED_FILES = [
    "DOC_GOVERNANCE_CORE.md",
    "FRAMEWORK_FEEDBACK_LOG.md",
    "ID_NAMING_STANDARDS.md",
    "TRACEABILITY.md",
    "TAG_SYNTAX.md",
    "DIAGRAM_STANDARDS.md",
    "THRESHOLD_NAMING_RULES.md",
    "SECURITY_REVIEW.md",
    "REVIEW_REMEDIATION_FLOW.md",
    "DEFINITION_OF_DONE.md",
    "REVIEW_TEAM.md",
    "REVIEW_CREWS.yaml",
    "REVIEW_SAGA.md",
    "saga.schema.json",
    "ADAPTATION.md",
    "ADAPTATION_SURFACE.yaml",
    "PROFILE-TEMPLATE.yaml",
    "AUTHORING_STYLE.md",
    "LINT_RULES.md",
    "SEED_CONTRACT.md",
    "DECISIONS.md",
    "README.md",
    "chg/README.md",
    "chg/CHG-TEMPLATE.yaml",
    "chg/CHG-00_index.TEMPLATE.md",
    "chg/gates/GATE-01_BUSINESS_PRODUCT.md",
    "chg/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md",
    "chg/gates/GATE-06_DESIGN_TEST.md",
    "chg/gates/GATE-08_IPLAN.md",
    "chg/gates/GATE-CODE_IMPLEMENTATION.md",
    "chg/gates/GATE-SPEC_FRAMEWORK.md",
    "chg/gates/GATE_ERROR_CATALOG.md",
    "chg/gates/GATE_INTERACTION_DIAGRAM.md",
    "chg/templates/GATE_APPROVAL_FORM.md",
    "chg/templates/POST_MORTEM-TEMPLATE.md",
]


class GovernanceFiles(unittest.TestCase):
    def test_expected_files_present(self):
        for relative in EXPECTED_FILES:
            with self.subTest(file=relative):
                self.assertTrue(
                    (GOVERNANCE / relative).is_file(),
                    f"missing governance file: {relative}",
                )

    def test_no_project_adaptation_artifacts_in_framework(self):
        """A consuming project's adaptation profile/learnings must never be
        committed under framework/ — the spec ships the contract, not project
        data (ADAPTATION.md; D-0013)."""
        leaked = [
            p.relative_to(FRAMEWORK).as_posix()
            for p in FRAMEWORK.rglob("*")
            if p.is_file() and (".aidoc" in p.parts or p.name in ("profile.yaml", "learnings.md"))
        ]
        self.assertEqual(leaked, [], f"project adaptation artifacts under framework/: {leaked}")

    def test_no_unexpected_files(self):
        found = {p.relative_to(GOVERNANCE).as_posix() for p in GOVERNANCE.rglob("*") if p.is_file()}
        self.assertEqual(found, set(EXPECTED_FILES))

    def test_chg_template_parses(self):
        with (GOVERNANCE / "chg" / "CHG-TEMPLATE.yaml").open(encoding="utf-8") as fh:
            self.assertIsNotNone(yaml.safe_load(fh))

    def test_spec_gate_is_wired(self):
        """GATE-SPEC (the framework-spec change gate, CHG-D1) is declared
        consistently across the gate def, the error catalog, and the CHG
        template enums."""
        catalog = (GOVERNANCE / "chg" / "gates" / "GATE_ERROR_CATALOG.md").read_text(
            encoding="utf-8"
        )
        for code in ("GATE-SPEC-E001", "GATE-SPEC-E002", "GATE-SPEC-E003", "GATE-SPEC-E004"):
            self.assertIn(code, catalog, f"error catalog missing {code}")

        template = (GOVERNANCE / "chg" / "CHG-TEMPLATE.yaml").read_text(encoding="utf-8")
        self.assertIn("GATE-SPEC", template, "CHG-TEMPLATE does not mention GATE-SPEC")
        self.assertIn("spec", template, "CHG-TEMPLATE does not declare the 'spec' change_source")
        self.assertIn("semver_impact", template, "CHG-TEMPLATE missing semver_impact field")

    def test_adaptation_surface_is_well_formed(self):
        """The adaptation surface parses, declares a closed unique knob set,
        and the mandatory/skippable layer split partitions a subset of the 8
        artifacts (ADAPTATION.md)."""
        with (GOVERNANCE / "ADAPTATION_SURFACE.yaml").open(encoding="utf-8") as fh:
            surface = yaml.safe_load(fh)
        names = [k["name"] for k in surface["knobs"]]
        self.assertTrue(names, "no knobs declared")
        self.assertEqual(len(names), len(set(names)), f"duplicate knob names: {names}")

        mandatory = set(surface["layers"]["mandatory"])
        skippable = set(surface["layers"]["skippable"])
        self.assertEqual(mandatory & skippable, set(), "layer is both mandatory and skippable")
        self.assertLessEqual(
            mandatory | skippable,
            set(ARTIFACTS),
            "adaptation layer split references an unknown artifact",
        )


def _codes(text: str, gate: str, kind: str) -> set:
    """Every ``GATE-<gate>-<kind>NNN`` id mentioned in ``text``.

    Codes belonging to *other* gates are ignored, so a gate document that
    cross-references a neighbour's code does not pollute that neighbour's set.
    """
    return {f"{g}-{k}{n}" for g, k, n in _CODE.findall(text) if g == gate and k == kind}


def _fillable_codes(form: str, gate: str, kind: str) -> set:
    """Codes the approval form offers as a *fillable item*, not merely mentions.

    A prose mention is not a check: the form's whole function is to be filled
    in, so an id that appears only in a sentence leaves the check unperformed
    exactly as an absent id does. Both of the form's item shapes carry an empty
    checkbox — the E-code table cell (``| GATE-03-E008: … | [ ] Pass / …``) and
    the W-code list item (``- [ ] GATE-SPEC-W003: …``) — so requiring ``[ ]`` on
    the line matches either without anchoring on which one.
    """
    fillable = "\n".join(line for line in form.splitlines() if "[ ]" in line)
    return _codes(fillable, gate, kind)


class GateCheckIdParity(unittest.TestCase):
    """Every gate's check ids agree across all three surfaces that carry them.

    A gate's checks are stated in three places, and a practitioner reads only the
    last of them:

    * the gate definition — ``chg/gates/GATE-<X>_*.md``
    * the shared error catalog — ``chg/gates/GATE_ERROR_CATALOG.md``
    * the approval form actually filled in — ``chg/templates/GATE_APPROVAL_FORM.md``

    The invariant is **set equality**, and it is directional in neither sense: a
    code present in the definition but absent from the form is a check nobody
    performs, and a code present in the form but absent from the definition is a
    check with no criteria. Both fail here.

    Regression cover: #433 (``GATE-03-E008`` missing from the form) and its second
    instance (``GATE-SPEC-W003``, likewise absent). Both are Security-category —
    E008 being the only one of GATE-03's two the form omitted, E002 already being
    present — and both entered their gate definition and the catalog in
    ``817d9a1a`` without reaching the form. That commit also edited this file, to
    add ``SECURITY_REVIEW.md`` to ``EXPECTED_FILES``: the suite was touched in the
    same change that introduced the drift and could not see it, because a
    file-existence list is not a cross-document check. The original census
    compared five gates and E-codes only, and so would have passed over the
    second; this compares six gates across both kinds.

    The form side compares *fillable items* rather than mentions (see
    ``_fillable_codes``), because deleting a code's row and mentioning the code
    in prose reproduces #433's failure mode exactly — the check goes unperformed
    — while leaving the id present. That mutant was measured passing against an
    earlier draft of this guard, which is why the distinction exists.

    **Two limits, both established by mutation rather than assumed.**

    1. On the *definition and catalog* sides the comparison is over ids mentioned
       anywhere in the document, not over table structure. Each states a code more
       than once — check table, error-catalog section, resolution heading — so
       deleting ``GATE-03-E008``'s row from ``GATE-03``'s §3.1 check table leaves
       the id present at its §7.1 row and its ``## GATE-03-E008 Resolution``
       heading, and this test passes; the same holds for
       ``GATE_ERROR_CATALOG.md`` §3.1 against its §9.1. Out of scope
       deliberately: anchoring on rows would make the check positional across six
       heterogeneous documents, and this direction is the benign one — the code
       still resolves in the catalog and the form, so the check is still
       performed. **Line numbers are named by section here, not by digit**: an
       earlier draft cited ``:240`` for that resolution heading and the E007 fix
       in this same change moved it to ``:243``.
    2. Only ``E`` and ``W`` are compared. ``GATE_ERROR_CATALOG.md:24`` also
       defines ``I`` (Info), and ``_CODE`` matches exactly three digits. No
       ``I``-code and no code of another width exists today, so nothing is
       unguarded now — but a future one would be invisible here rather than
       caught, and that is a scope limit, not coverage.
    """

    def _gate_files(self):
        found = {}
        for path in sorted((CHG / "gates").glob("GATE-*.md")):
            gate = path.name.split("_", 1)[0]
            # Two files sharing a gate prefix would otherwise collapse silently,
            # leaving the roster test green while only one of them is compared.
            self.assertNotIn(gate, found, f"two documents claim {gate}: {path.name}")
            found[gate] = path
        return found

    def test_gate_roster_is_complete(self):
        self.assertEqual(
            set(self._gate_files()), set(EXPECTED_GATES), "CHG gate document roster changed"
        )

    def test_check_ids_agree_across_definition_catalog_and_form(self):
        catalog = (CHG / "gates" / "GATE_ERROR_CATALOG.md").read_text(encoding="utf-8")
        form = (CHG / "templates" / "GATE_APPROVAL_FORM.md").read_text(encoding="utf-8")

        for gate, path in sorted(self._gate_files().items()):
            definition = path.read_text(encoding="utf-8")
            for kind in ("E", "W"):
                with self.subTest(gate=gate, kind=kind):
                    in_definition = _codes(definition, gate, kind)
                    self.assertTrue(in_definition, f"{gate}: no {kind}-codes found in {path.name}")
                    self.assertEqual(
                        in_definition,
                        _codes(catalog, gate, kind),
                        f"{gate} {kind}-codes disagree between {path.name} and "
                        "GATE_ERROR_CATALOG.md",
                    )
                    self.assertEqual(
                        in_definition,
                        _fillable_codes(form, gate, kind),
                        f"{gate} {kind}-codes disagree between {path.name} and "
                        "GATE_APPROVAL_FORM.md — compared against the form's "
                        "*fillable* items only, since a code mentioned in prose "
                        "is a check nobody performs",
                    )


class GovernanceFilesNoOrphans(unittest.TestCase):
    """Any new file under framework/governance/ must be added to EXPECTED_FILES."""

    def test_no_orphan_governance_files(self):
        actual = {p.name for p in GOVERNANCE.iterdir() if p.is_file()}
        expected = set(EXPECTED_FILES)
        new_in_dir = actual - expected
        self.assertFalse(
            new_in_dir,
            "Governance file(s) on disk but not in EXPECTED_FILES: "
            f"{sorted(new_in_dir)}. Add them to the list (and document in CHANGELOG).",
        )


if __name__ == "__main__":
    unittest.main()
