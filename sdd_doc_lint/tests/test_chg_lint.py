"""Unit: CHG governance linter CHG-L006..CHG-L012 (canonical implementation.steps schema).

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
            self.assertTrue(
                any("CHG-L007" in e and "archive_path" in e for e in errors), errors
            )

    def test_null_new_version_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _with_sdd_step(
                _base_chg(), "Governance docs", "framework/archive/CHG-99/x", None
            )
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(
                any("CHG-L007" in e and "new_version" in e for e in errors), errors
            )

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
        (root / "03_EARS" / "EARS-01_x.yaml").write_text(
            yaml.safe_dump(ears), encoding="utf-8"
        )
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
        chg["change_control"]["supersedes"] = [
            "framework/archive/CHG-99/03_EARS/EARS-01_x.yaml"
        ]
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
            path = _write(
                Path(tmp) / "CHG-99.yaml", yaml.safe_dump(self._direct_chg())
            )
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L013" in e], [])
            self.assertTrue(any("CHG-L013" in p for p in passes), passes)

    def test_unscoped_code_manifest_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(
                Path(tmp) / "CHG-99.yaml", yaml.safe_dump(self._unscoped_chg())
            )
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(
                any("CHG-L013" in e and "F2" in e for e in errors), errors
            )

    def test_feedback_without_iplan_names_bugfix_vehicle(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = self._unscoped_chg()
            chg["change_control"]["change_source"] = "feedback"
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(
                any("CHG-L013" in e and "F4" in e for e in errors), errors
            )


if __name__ == "__main__":
    unittest.main()
