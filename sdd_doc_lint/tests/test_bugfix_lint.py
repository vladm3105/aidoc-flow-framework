"""Unit: bugfix IPLAN linter BGF-01..BGF-07 (CHG-05, #656/#657).

Red-first: written before sdd_doc_lint/bugfix_lint.py exists. Fixtures are
built inline in temp dirs (minter + parent checks need a directory listing),
mirroring test_chg_lint.py's _base_chg pattern.

Run: python3 -m unittest discover -s sdd_doc_lint/tests
"""

import re
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


def _codes(errors):
    """Sorted BGF-NN prefixes among error strings (isolation assertions)."""
    out = set()
    for e in errors:
        m = re.match(r"(BGF-\d+)", e)
        if m:
            out.add(m.group(1))
    return sorted(out)


class NamingAndMinter(unittest.TestCase):
    def test_clean_name_passes(self):
        with tempfile.TemporaryDirectory() as td:
            errors, warnings, passes = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", _bugfix_doc())
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])
            self.assertTrue(passes, "clean fixture should record passes, not pass vacuously")

    def test_bad_name_fires_bgf01(self):
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05.yaml", _bugfix_doc())
            self.assertTrue(any(e.startswith("BGF-01") for e in errors))

    def test_wrong_minter_fires_bgf02(self):
        with tempfile.TemporaryDirectory() as td:
            doc = _bugfix_doc()
            doc["doc_id"] = "IPLAN-09"
            doc["document_control"]["iplan_id"] = "IPLAN-09"
            errors, _, _ = _lint(Path(td), "IPLAN-09_bugfix_03_slug.yaml", doc)
            self.assertEqual(_codes(errors), ["BGF-02"])

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
        fourth = _parent_doc()
        fourth["doc_id"] = "IPLAN-04"
        fourth["document_control"]["iplan_id"] = "IPLAN-04"
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(
                Path(td),
                "IPLAN-05_bugfix_03_slug.yaml",
                _bugfix_doc(),
                siblings={
                    "IPLAN-03_slug.yaml": _parent_doc(subtype="bugfix"),
                    "IPLAN-04_other.yaml": fourth,
                },
            )
            self.assertEqual(_codes(errors), ["BGF-07"])

    def test_active_parent_fires_bgf07(self):
        fourth = _parent_doc()
        fourth["doc_id"] = "IPLAN-04"
        fourth["document_control"]["iplan_id"] = "IPLAN-04"
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(
                Path(td),
                "IPLAN-05_bugfix_03_slug.yaml",
                _bugfix_doc(),
                siblings={
                    "IPLAN-03_slug.yaml": _parent_doc(status="In Progress"),
                    "IPLAN-04_other.yaml": fourth,
                },
            )
            self.assertEqual(_codes(errors), ["BGF-07"])


class WarningPaths(unittest.TestCase):
    def test_no_siblings_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as td:
            errors, warnings, _ = _lint(
                Path(td), "IPLAN-05_bugfix_03_slug.yaml", _bugfix_doc(), siblings={}
            )
            self.assertEqual(errors, [])
            self.assertTrue(any("BGF-02" in w for w in warnings))

    def test_empty_manifest_warns(self):
        doc = _bugfix_doc()
        doc["file_manifest"]["files"] = []
        with tempfile.TemporaryDirectory() as td:
            errors, warnings, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertEqual(errors, [])
            self.assertTrue(any("BGF-06" in w for w in warnings))

    def test_missing_parent_warns(self):
        with tempfile.TemporaryDirectory() as td:
            fourth = _parent_doc()
            fourth["doc_id"] = "IPLAN-04"
            fourth["document_control"]["iplan_id"] = "IPLAN-04"
            errors, warnings, _ = _lint(
                Path(td),
                "IPLAN-05_bugfix_09_slug.yaml",
                _bugfix_doc(document_control={"parent_iplan": "IPLAN-09"}),
                siblings={"IPLAN-04_other.yaml": fourth},
            )
            self.assertEqual(errors, [])
            self.assertTrue(any("BGF-07" in w for w in warnings))

    def test_non_bugfix_subtype_warns_only(self):
        doc = _bugfix_doc()
        doc["document_control"]["subtype"] = "combined"
        with tempfile.TemporaryDirectory() as td:
            target = tmp_target(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            errors, warnings, _ = bugfix_lint.lint_bugfix(target)
            self.assertEqual(errors, [])
            self.assertTrue(warnings)

    def test_missing_source_chg_warns(self):
        doc = _bugfix_doc()
        del doc["document_control"]["source_chg"]
        with tempfile.TemporaryDirectory() as td:
            errors, warnings, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertEqual(errors, [])
            self.assertTrue(any("source_chg" in w for w in warnings))

    def test_missing_ids_warns(self):
        doc = _bugfix_doc()
        del doc["doc_id"]
        del doc["document_control"]["iplan_id"]
        with tempfile.TemporaryDirectory() as td:
            errors, warnings, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertEqual(_codes(errors), [])
            self.assertTrue(any("BGF-03" in w for w in warnings))


def tmp_target(tmp: Path, name: str, doc: dict) -> Path:
    target = tmp / name
    target.write_text(yaml.safe_dump(doc), encoding="utf-8")
    return target


class CrashPaths(unittest.TestCase):
    def test_empty_file_errors(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "IPLAN-05_bugfix_03_slug.yaml"
            target.write_text("", encoding="utf-8")
            errors, _, _ = bugfix_lint.lint_bugfix(target)
            self.assertTrue(any(e.startswith("BGF-00") for e in errors))

    def test_list_yaml_errors(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "IPLAN-05_bugfix_03_slug.yaml"
            target.write_text("- just\n- a\n- list\n", encoding="utf-8")
            errors, _, _ = bugfix_lint.lint_bugfix(target)
            self.assertTrue(any(e.startswith("BGF-00") for e in errors))

    def test_missing_file_errors_without_crash(self):
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = bugfix_lint.lint_bugfix(Path(td) / "IPLAN-05_bugfix_03_slug.yaml")
            self.assertTrue(errors)

    def test_directory_errors_without_crash(self):
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = bugfix_lint.lint_bugfix(Path(td))
            self.assertTrue(errors)

    def test_string_resolution_errors(self):
        doc = _bugfix_doc()
        doc["rollback_procedure"]["resolution"] = "DONE"
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertEqual(_codes(errors), ["BGF-05"])

    def test_typo_marker_errors(self):
        doc = _bugfix_doc()
        doc["rollback_procedure"]["resolution"] = [{"item": "fix commit", "marker": "DON"}]
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertEqual(_codes(errors), ["BGF-05"])

    def test_markerless_entry_errors(self):
        doc = _bugfix_doc()
        doc["rollback_procedure"]["resolution"] = [{"item": "fix commit"}]
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertEqual(_codes(errors), ["BGF-05"])

    def test_string_implementation_warns_not_crashes(self):
        doc = _bugfix_doc()
        doc["execution_commands"]["implementation"] = "Apply the fix"
        with tempfile.TemporaryDirectory() as td:
            errors, warnings, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertEqual(_codes(errors), [])
            self.assertTrue(any("BGF-04" in w for w in warnings))


class SubstringGuard(unittest.TestCase):
    def test_fixture_hotfix_prefix_do_not_fire(self):
        doc = _bugfix_doc()
        doc["execution_commands"]["implementation"] = [
            "Land the parent revision entry in IPLAN-03",
            "Add fixture data for the hotfix prefix check",
        ]
        with tempfile.TemporaryDirectory() as td:
            errors, _, _ = _lint(Path(td), "IPLAN-05_bugfix_03_slug.yaml", doc)
            self.assertEqual(_codes(errors), [])


if __name__ == "__main__":
    unittest.main()
