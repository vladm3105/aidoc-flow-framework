"""Unit: CHG governance linter CHG-L001..CHG-L014 (canonical implementation.steps schema).

Adapted from #653 (`tests/unit/test_chg_lint.py` on the donor branch
`fix/chg-lint-archive-lifecycle`), which targets the donor's top-level
`sdd_lifecycle:` / `artifacts_modified:` schema. The canonical schema nests
both under `implementation:` — `steps` entries with `phase: sdd_lifecycle`
carrying free-text `artifact` fields, plus `artifacts_modified` — so the
donor helpers (`_base_chg`, `_with_sdd_entry`) are rebuilt here and the
traceability tests drive `_traceable_docs_from_steps` (layer codes +
EARS-/BDD- stems recovered from step text).

L011 (CHG-L011 / GOV-017) coverage:
- cited ID resolves in-tree via --sdd-root → pass, no error
- fabricated ID with verifiable tree → CHG-L011 error
- no --sdd-root → warning, never error
- lifecycle names a doc missing under --sdd-root → warning, unchecked

Run: python3 -m unittest discover -s sdd_doc_lint/tests
"""

import tempfile
import unittest
from pathlib import Path

import yaml

from sdd_doc_lint import chg_lint


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def _base_chg(**overrides):
    doc = {
        "id": "CHG-99",
        "change_control": {
            "chg_id": "CHG-99",
            "status": "Approved",
            "change_level": "C2",
            "date_approved": "2026-09-17T00:00:00",
            "supersedes": [],
        },
        "gate_approval": {
            "gate": "GATE-06",
            "approver": "Self",
            "approval_date": "2026-09-17T00:00:00",
        },
        "change_description": {"what": "x", "why": "x", "trigger": "x"},
        "implementation": {
            "steps": [
                {
                    "step": "Create IPLAN-99",
                    "artifact": "IPLAN-99",
                    "phase": "iplan_creation",
                    "status": "Completed",
                }
            ],
            "artifacts_modified": [
                {"id": "IPLAN-99", "file": "framework/archive/CHG-99/IPLAN-99.yaml"}
            ],
        },
    }
    doc.update(overrides)
    return doc


def _with_sdd_step(chg, artifact, archive_path, new_version, status="Completed"):
    chg["implementation"]["steps"].insert(
        0,
        {
            "step": f"Rewrite {artifact}",
            "artifact": artifact,
            "phase": "sdd_lifecycle",
            "status": status,
            "archive_path": archive_path,
            "new_version": new_version,
        },
    )
    return chg


class LifecycleCompletenessTests(unittest.TestCase):
    def test_artifacts_without_lifecycle_steps_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            chg["implementation"]["artifacts_modified"] = chg["implementation"][
                "artifacts_modified"
            ] + [{"id": "GOV-DOCS", "file": "framework/governance/LINT_RULES.md"}]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L006" in e for e in errors), errors)

    def test_iplan_only_needs_no_lifecycle_steps(self):
        # Canonical L006 fires on ANY artifacts_modified entry without
        # lifecycle steps — so an IPLAN-only CHG carries no artifacts at all.
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            chg["implementation"]["artifacts_modified"] = []
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L006" in e], [])
            self.assertTrue(any("CHG-L006" in p for p in passes))


class EntryMetadataTests(unittest.TestCase):
    def test_null_archive_path_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _with_sdd_step(_base_chg(), "Governance docs", None, "0.54.0")
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L007" in e and "archive_path" in e for e in errors), errors)

    def test_null_new_version_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _with_sdd_step(_base_chg(), "Governance docs", "framework/archive/CHG-99/x", None)
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L007" in e and "new_version" in e for e in errors), errors)

    def test_iplan_create_needs_no_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(_base_chg()))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L007" in e], [])


class SupersedesTests(unittest.TestCase):
    def _archived(self, chg, archive):
        _with_sdd_step(chg, "Governance docs", archive, "0.54.0")
        chg["change_control"]["supersedes"] = [archive]
        return chg

    def test_supersedes_lists_every_archived_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = "framework/archive/CHG-99/LINT_RULES.md"
            chg = self._archived(_base_chg(), archive)
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L010" in e], [])
            self.assertTrue(any("CHG-L010" in p for p in passes))

    def test_missing_supersedes_entry_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _with_sdd_step(
                _base_chg(), "Governance docs", "framework/archive/CHG-99/x", "0.54.0"
            )
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L010" in e for e in errors), errors)


class TraceabilityTests(unittest.TestCase):
    def _tree(self, tmp: Path) -> Path:
        root = Path(tmp) / "sdd"
        (root / "03_EARS").mkdir(parents=True)
        ears = {
            "id": "EARS-01",
            "requirements": {
                "ubiquitous": [
                    {"id": "EARS.01.03.8e4b", "statement": "THE x SHALL y."},
                ]
            },
        }
        (root / "03_EARS" / "EARS-01_x.yaml").write_text(yaml.safe_dump(ears), encoding="utf-8")
        return root

    def _citing_chg(self, cited_id: str):
        chg = _base_chg()
        chg["change_description"]["what"] = f"Adds {cited_id}"
        _with_sdd_step(
            chg,
            "03_EARS snapshot EARS-01_x",
            "framework/archive/CHG-99/03_EARS/EARS-01_x.yaml",
            "1.1",
        )
        chg["change_control"]["supersedes"] = ["framework/archive/CHG-99/03_EARS/EARS-01_x.yaml"]
        return chg

    def test_cited_id_resolves_in_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            path = _write(
                Path(tmp) / "CHG-99.yaml",
                yaml.safe_dump(self._citing_chg("EARS.01.03.8e4b")),
            )
            errors, _, passes = chg_lint.lint_chg(path, root)
            self.assertEqual([e for e in errors if "CHG-L011" in e], [])
            self.assertTrue(any("CHG-L011" in p for p in passes))

    def test_fabricated_id_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            path = _write(
                Path(tmp) / "CHG-99.yaml",
                yaml.safe_dump(self._citing_chg("EARS.01.03.ffff")),
            )
            errors, _, _ = chg_lint.lint_chg(path, root)
            self.assertTrue(
                any("CHG-L011" in e and "EARS.01.03.ffff" in e for e in errors),
                errors,
            )

    def test_missing_sdd_root_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(
                Path(tmp) / "CHG-99.yaml",
                yaml.safe_dump(self._citing_chg("EARS.01.03.8e4b")),
            )
            errors, warnings, _ = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L011" in e], [])
            self.assertTrue(any("CHG-L011" in w for w in warnings), warnings)

    def test_missing_lifecycle_file_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "sdd"
            (root / "03_EARS").mkdir(parents=True)
            path = _write(
                Path(tmp) / "CHG-99.yaml",
                yaml.safe_dump(self._citing_chg("EARS.01.03.8e4b")),
            )
            errors, warnings, _ = chg_lint.lint_chg(path, root)
            self.assertEqual([e for e in errors if "CHG-L011" in e], [])
            self.assertTrue(any("CHG-L011" in w for w in warnings), warnings)


class StatusLifecycleTests(unittest.TestCase):
    """CHG-L001/L002 (#668): single approver owner; Proposed C3 drafts pass."""

    def _c3_approved_no_approver(self):
        chg = _base_chg()
        chg["change_control"]["change_level"] = "C3"
        chg["change_control"]["status"] = "Approved"
        chg["gate_approval"]["approver"] = None
        return chg

    def test_proposed_c3_draft_is_green(self):
        # GOV-012 permits null approver while Proposed.
        with tempfile.TemporaryDirectory() as tmp:
            chg = self._c3_approved_no_approver()
            chg["change_control"]["status"] = "Proposed"
            chg["change_control"].pop("date_approved", None)
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L001" in e], [])
            self.assertEqual([e for e in errors if "CHG-L002" in e], [])
            self.assertTrue(any("CHG-L002" in p and "Proposed" in p for p in passes), passes)

    def test_approver_reported_once_under_l002(self):
        # The defect is double-reported under two codes; L002 is sole owner.
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(
                Path(tmp) / "CHG-99.yaml",
                yaml.safe_dump(self._c3_approved_no_approver()),
            )
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L001" in e], [])
            self.assertTrue(any("CHG-L002" in e for e in errors), errors)


class ScopePhaseTests(unittest.TestCase):
    """CHG-L003 (#668): missing phase errors; no keyword heuristic."""

    def test_step_without_phase_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            chg["implementation"]["steps"].append(
                {"step": "Do the thing", "artifact": "Docs", "status": "Completed"}
            )
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, warnings, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L003" in e and "no phase" in e for e in errors), errors)
            self.assertEqual([w for w in warnings if "CHG-L003" in w], [])

    def test_sdd_title_with_code_word_is_green(self):
        # "Implement SDD lifecycle" is a governance step, not a code step.
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            chg["implementation"]["steps"].insert(
                0,
                {
                    "step": "Implement SDD lifecycle",
                    "artifact": "Governance docs",
                    "phase": "sdd_lifecycle",
                    "status": "Completed",
                    "archive_path": "framework/archive/CHG-99/x",
                    "new_version": "0.54.0",
                },
            )
            chg["change_control"]["supersedes"] = ["framework/archive/CHG-99/x"]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, warnings, _ = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L003" in e], [])
            self.assertEqual([w for w in warnings if "CHG-L003" in w], [])


class IplanReferenceTests(unittest.TestCase):
    """CHG-L004/GOV-019 (#668): canon steps-scan; missing reference errors."""

    def _stripped(self):
        chg = _base_chg()
        chg["implementation"]["steps"] = []
        chg["implementation"]["artifacts_modified"] = [
            {"id": "HOOK", "file": "hooks/sync-version-refs.sh"}
        ]
        return chg

    def test_iplan_creation_step_counts_as_reference(self):
        # Top-level sdd_lifecycle list and artifacts_modified carry no IPLAN —
        # the canon steps-scan alone must satisfy L004.
        with tempfile.TemporaryDirectory() as tmp:
            chg = self._stripped()
            chg["implementation"]["steps"] = [
                {
                    "step": "Create IPLAN-99",
                    "artifact": "IPLAN-99",
                    "phase": "iplan_creation",
                    "status": "Completed",
                }
            ]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L004" in e], [])
            self.assertTrue(any("CHG-L004" in p for p in passes), passes)

    def test_missing_reference_is_gov019_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(self._stripped()))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L004" in e and "GOV-019" in e for e in errors), errors)

    def test_bugfix_iplan_id_in_artifacts_counts(self):
        # CHG-05 interplay: a bugfix-flavored doc referencing its IPLAN via
        # artifacts_modified satisfies L004 through the id branch.
        with tempfile.TemporaryDirectory() as tmp:
            chg = self._stripped()
            chg["implementation"]["artifacts_modified"] = [
                {
                    "id": "IPLAN-10_bugfix_09_slug",
                    "file": "framework/archive/CHG-99/IPLAN-10_bugfix_09_slug.yaml",
                }
            ]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L004" in e], [])
            self.assertTrue(any("CHG-L004" in p for p in passes), passes)

    def test_reconciliation_source_passes_guards(self):
        # CHG-04 interplay: the reconciliation source value trips neither
        # the IPLAN guard nor the flow guard on a referenced shape.
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            chg["change_control"]["change_source"] = "reconciliation"
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L004" in e], [])
            self.assertEqual([e for e in errors if "CHG-L013" in e], [])


class FlowMisclassificationTests(unittest.TestCase):
    """CHG-L013 (GOV-018): C1-direct shape passes; unscoped code manifests error."""

    def _direct_chg(self):
        chg = _base_chg()
        chg["change_control"]["change_source"] = "direct"
        chg["change_control"]["change_level"] = "C1"
        chg["implementation"]["artifacts_modified"] = [
            {"id": "HOOK", "file": "hooks/sync-version-refs.sh"}
        ]
        return chg

    def _unscoped_chg(self):
        chg = _base_chg()
        chg["implementation"]["steps"] = []
        chg["implementation"]["artifacts_modified"] = [
            {"id": "HOOK", "file": "hooks/sync-version-refs.sh"}
        ]
        return chg

    def test_c1_direct_shape_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(self._direct_chg()))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L013" in e], [])
            self.assertTrue(any("CHG-L013" in p for p in passes), passes)

    def test_unscoped_code_manifest_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(self._unscoped_chg()))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L013" in e and "F2" in e for e in errors), errors)

    def test_feedback_without_iplan_names_bugfix_vehicle(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = self._unscoped_chg()
            chg["change_control"]["change_source"] = "feedback"
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L013" in e and "F4" in e for e in errors), errors)


class SeedModuleLifecycleTests(unittest.TestCase):
    """CHG-L014 (GOV-020): F3 seed/module touches need lifecycle coverage; other flows pass."""

    def _f3_module_chg(self):
        chg = _base_chg()
        chg["change_control"]["change_source"] = "midstream"
        chg["implementation"]["artifacts_modified"] = [
            {"id": "MODULE-12-README", "file": "docs/modules/MODULE-12_observability/README.md"},
            {"id": "IPLAN-99", "file": "framework/archive/CHG-99/IPLAN-99.yaml"},
        ]
        return chg

    def test_covered_f3_touches_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = self._f3_module_chg()
            chg["module_lifecycle"] = [
                {
                    "module": "MODULE-12_observability/README.md",
                    "action": "sync",
                    "archive_path": "docs/sdd/09-CHG/archive/CHG-99/modules/MODULE-12_observability_README.md",
                    "new_version": "1.0",
                    "changes": "health-check section",
                }
            ]
            chg["seed_scope"] = {"decision": "no-change", "rationale": "seed checked", "checked": []}
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L014" in e], [])
            self.assertTrue(any("CHG-L014" in p for p in passes), passes)

    def test_uncovered_module_touch_is_gov020_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(self._f3_module_chg()))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L014" in e and "GOV-020" in e for e in errors), errors)

    def test_direct_source_passes_through(self):
        # F3-only boundary: a direct-source CHG touching modules trips no L014.
        with tempfile.TemporaryDirectory() as tmp:
            chg = self._f3_module_chg()
            chg["change_control"]["change_source"] = "direct"
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L014" in e], [])


if __name__ == "__main__":
    unittest.main()
