"""Unit: CHG lifecycle linter (CHG-L006..L009 / GOV-014..GOV-017).

Run: python3 -m unittest tests.unit.test_chg_lint -v   (from repo root)
"""

import tempfile
import textwrap
import unittest
from pathlib import Path

import yaml

from scripts import chg_lint


def _write(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content), encoding="utf-8")
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
            "approver": "Self (C3 — Technical Lead)",
            "approval_date": "2026-09-17T00:00:00",
        },
        "implementation": {"steps": [{"title": "Create IPLAN-99", "phase": "iplan_creation"}]},
        "artifacts_modified": [{"path": "docs/sdd/08_IPLAN/IPLAN-99.yaml"}],
        "sdd_lifecycle": [
            {
                "layer": "08_IPLAN",
                "document": "IPLAN-99",
                "action": "create",
                "archive_path": None,
                "new_version": "1.0",
                "changes": "x",
            }
        ],
    }
    doc.update(overrides)
    return doc


def _with_sdd_entry(chg, layer, document, archive_path, new_version, changes="x"):
    chg["artifacts_modified"] = chg.get("artifacts_modified", []) + [
        {"path": f"docs/sdd/{layer}/{document}.yaml"}
    ]
    chg["sdd_lifecycle"] = chg.get("sdd_lifecycle", []) + [
        {
            "layer": layer,
            "document": document,
            "action": "extend",
            "archive_path": archive_path,
            "new_version": new_version,
            "changes": changes,
        }
    ]
    return chg


class LifecycleCompletenessTests(unittest.TestCase):
    def test_lifecycle_lists_every_modified_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            _with_sdd_entry(
                chg,
                "03_EARS",
                "EARS-01_x",
                "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml",
                "1.1",
            )
            chg["change_control"]["supersedes"] = [
                "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml"
            ]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L006" in e], [])
            self.assertTrue(any("CHG-L006" in p for p in passes))

    def test_missing_lifecycle_entry_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            chg["artifacts_modified"] = chg.get("artifacts_modified", []) + [
                {"path": "docs/sdd/03_EARS/EARS-09_orphan.yaml"}
            ]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L006" in e and "EARS-09_orphan" in e for e in errors), errors)


class LifecycleMetadataTests(unittest.TestCase):
    def _chg_with_entry(self, entry):
        chg = _base_chg()
        chg["artifacts_modified"] = chg.get("artifacts_modified", []) + [
            {"path": "docs/sdd/03_EARS/EARS-01_x.yaml"}
        ]
        chg["sdd_lifecycle"] = chg.get("sdd_lifecycle", []) + [entry]
        return chg

    def test_null_archive_path_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = {
                "layer": "03_EARS",
                "document": "EARS-01_x",
                "action": "extend",
                "archive_path": None,
                "new_version": "1.1",
                "changes": "x",
            }
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(self._chg_with_entry(entry)))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L007" in e and "archive_path" in e for e in errors), errors)

    def test_null_new_version_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = {
                "layer": "03_EARS",
                "document": "EARS-01_x",
                "action": "extend",
                "archive_path": "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml",
                "new_version": None,
                "changes": "x",
            }
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(self._chg_with_entry(entry)))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L007" in e and "new_version" in e for e in errors), errors)

    def test_unknown_layer_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = {
                "layer": "02_PRD",
                "document": "PRD-01_x",
                "action": "extend",
                "archive_path": "docs/sdd/09-CHG/archive/CHG-99/02_PRD/PRD-01_x.yaml",
                "new_version": "1.1",
                "changes": "x",
            }
            chg = _base_chg()
            chg["artifacts_modified"] = chg.get("artifacts_modified", []) + [
                {"path": "docs/sdd/02_PRD/PRD-01_x.yaml"}
            ]
            chg["sdd_lifecycle"] = chg.get("sdd_lifecycle", []) + [entry]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L007" in e and "02_PRD" in e for e in errors), errors)

    def test_iplan_create_needs_no_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L007" in e], [])


class SupersedesTests(unittest.TestCase):
    def test_supersedes_lists_every_archived_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml"
            chg = _base_chg()
            _with_sdd_entry(chg, "03_EARS", "EARS-01_x", archive, "1.1")
            chg["change_control"]["supersedes"] = [archive]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L008" in e], [])
            self.assertTrue(any("CHG-L008" in p for p in passes))

    def test_missing_supersedes_entry_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg(
                artifacts_modified=[{"path": "docs/sdd/03_EARS/EARS-01_x.yaml"}],
                sdd_lifecycle=[
                    {
                        "layer": "03_EARS",
                        "document": "EARS-01_x",
                        "action": "extend",
                        "archive_path": "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml",
                        "new_version": "1.1",
                        "changes": "x",
                    }
                ],
            )
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path)
            self.assertTrue(any("CHG-L008" in e for e in errors), errors)


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

    def test_cited_id_resolves_in_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            chg = _base_chg()
            _with_sdd_entry(
                chg,
                "03_EARS",
                "EARS-01_x",
                "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml",
                "1.1",
                changes="Adds EARS.01.03.8e4b",
            )
            chg["change_control"]["supersedes"] = [
                "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml"
            ]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, passes = chg_lint.lint_chg(path, root)
            self.assertEqual([e for e in errors if "CHG-L009" in e], [])
            self.assertTrue(any("CHG-L009" in p for p in passes))

    def test_fabricated_id_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            chg = _base_chg()
            _with_sdd_entry(
                chg,
                "03_EARS",
                "EARS-01_x",
                "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml",
                "1.1",
                changes="Adds EARS.01.03.ffff",
            )
            chg["change_control"]["supersedes"] = [
                "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml"
            ]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, _, _ = chg_lint.lint_chg(path, root)
            self.assertTrue(
                any("CHG-L009" in e and "EARS.01.03.ffff" in e for e in errors), errors
            )

    def test_missing_sdd_root_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            chg = _base_chg()
            _with_sdd_entry(
                chg,
                "03_EARS",
                "EARS-01_x",
                "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml",
                "1.1",
                changes="Adds EARS.01.03.8e4b",
            )
            chg["change_control"]["supersedes"] = [
                "docs/sdd/09-CHG/archive/CHG-99/03_EARS/EARS-01_x.yaml"
            ]
            path = _write(Path(tmp) / "CHG-99.yaml", yaml.safe_dump(chg))
            errors, warnings, _ = chg_lint.lint_chg(path)
            self.assertEqual([e for e in errors if "CHG-L009" in e], [])
            self.assertTrue(any("CHG-L009" in w for w in warnings), warnings)


if __name__ == "__main__":
    unittest.main()
