"""Unit: bugfix IPLAN linter BGF-01..BGF-07 (CHG-05, #656/#657).

Red-first: written before sdd_doc_lint/bugfix_lint.py exists. Fixtures are
built inline in temp dirs (minter + parent checks need a directory listing),
mirroring test_chg_lint.py's _base_chg pattern.

Run: python3 -m unittest discover -s sdd_doc_lint/tests
"""

import tempfile
import unittest
from pathlib import Path

import yaml

from sdd_doc_lint import bugfix_lint


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def _parent_doc(status="Verified", subtype="combined"):
    return {
        "doc_id": "IPLAN-03",
        "document_control": {
            "iplan_id": "IPLAN-03",
            "subtype": subtype,
            "status": status,
        },
    }


def _bugfix_doc(**overrides):
    doc = {
        "doc_id": "IPLAN-05",
        "document_control": {
            "iplan_id": "IPLAN-05",
            "subtype": "bugfix",
            "status": "In Progress",
            "parent_iplan": "IPLAN-03",
            "source_chg": "CHG-05",
        },
        "file_manifest": {
            "files": [
                {"path": "src/fix.py", "order": 1, "status": "DONE"},
            ]
        },
        "execution_commands": {
            "implementation": [
                "Apply the fix to src/fix.py",
                "Add regression test tests/test_fix.py",
                "Confirm rollback readiness (revert commit)",
                "Land the parent revision entry in IPLAN-03",
            ]
        },
        "rollback_procedure": {
            "steps": [{"step": "Revert the fix commit", "reversible": True}],
            "resolution": [{"item": "fix commit", "marker": "DONE"}],
        },
    }
    doc["document_control"].update(overrides.pop("document_control", {}))
    doc.update(overrides)
    return doc


def _lint(tmp: Path, name: str, doc: dict, siblings: dict | None = None):
    if siblings is None:
        fourth = _parent_doc()
        fourth["doc_id"] = "IPLAN-04"
        fourth["document_control"]["iplan_id"] = "IPLAN-04"
        siblings = {
            "IPLAN-03_slug.yaml": _parent_doc(),
            "IPLAN-04_other.yaml": fourth,
        }
    for sname, sdoc in siblings.items():
        _write(tmp / sname, yaml.safe_dump(sdoc))
    target = _write(tmp / name, yaml.safe_dump(doc))
    (tmp / "src").mkdir(exist_ok=True)
    (tmp / "src" / "fix.py").write_text("x = 1\n")
    return bugfix_lint.lint_bugfix(target)


class NamingAndMinter(unittest.TestCase):
    def test_clean_name_passes(self):
        with tempfile.TemporaryDirectory() as td:
            errors, warnings, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", _bugfix_doc())
            self.assertEqual(errors, [])

    def test_bad_name_fires_bgf01(self):
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05.yaml", _bugfix_doc())
            self.assertTrue(any(e.startswith("BGF-01") for e in errors))

    def test_wrong_minter_fires_bgf02(self):
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(
                Path(td),
                "IPLAN-09_bugfix_03_slug.yaml",
                _bugfix_doc(document_control={"iplan_id": "IPLAN-09"}),
            )
            self.assertTrue(any(e.startswith("BGF-02") for e in errors))

    def test_id_mismatch_fires_bgf03(self):
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(
                Path(td),
                "IPLAN-05_bugfix_03_slug.yaml",
                _bugfix_doc(document_control={"iplan_id": "IPLAN-06"}),
            )
            self.assertTrue(any(e.startswith("BGF-03") for e in errors))


class OrderAndRollback(unittest.TestCase):
    def test_reordered_steps_fire_bgf04(self):
        doc = _bugfix_doc()
        doc["execution_commands"]["implementation"] = [
            "Land the parent revision entry in IPLAN-03",
            "Apply the fix to src/fix.py",
        ]
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertTrue(any(e.startswith("BGF-04") for e in errors))

    def test_missing_rollback_fires_bgf05(self):
        doc = _bugfix_doc()
        del doc["rollback_procedure"]
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertTrue(any(e.startswith("BGF-05") for e in errors))

    def test_pending_marker_fires_bgf05(self):
        doc = _bugfix_doc()
        doc["rollback_procedure"]["resolution"] = [{"item": "fix commit", "marker": "PENDING"}]
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertTrue(any(e.startswith("BGF-05") for e in errors))


class ManifestAndParent(unittest.TestCase):
    def test_missing_done_file_fires_bgf06(self):
        doc = _bugfix_doc()
        doc["file_manifest"]["files"] = [{"path": "src/absent.py", "order": 1, "status": "DONE"}]
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertTrue(any(e.startswith("BGF-06") for e in errors))

    def test_bugfix_parent_fires_bgf07(self):
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(
                Path(td),
                "IPLAN-05_bugfix_03_slug.yaml",
                _bugfix_doc(),
                siblings={"IPLAN-03_slug.yaml": _parent_doc(subtype="bugfix")},
            )
            self.assertTrue(any(e.startswith("BGF-07") for e in errors))

    def test_active_parent_fires_bgf07(self):
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(
                Path(td),
                "IPLAN-05_bugfix_03_slug.yaml",
                _bugfix_doc(),
                siblings={"IPLAN-03_slug.yaml": _parent_doc(status="In Progress")},
            )
            self.assertTrue(any(e.startswith("BGF-07") for e in errors))


if __name__ == "__main__":
    unittest.main()
