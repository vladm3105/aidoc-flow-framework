"""Unit: tools/trace_walk.py — transitive @-tag walker."""

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACE_WALK = REPO_ROOT / "tools" / "trace_walk.py"


def _write_fixture_corpus(td: Path) -> None:
    """Build a 4-layer fixture corpus that the walker can traverse:
    TDD-01 → BDD-01 → EARS-01 → PRD-01 (no BRD intentionally, so TDD's
    direct-upstream BDD chain reaches PRD via EARS only)."""
    (td / "docs" / "02_PRD").mkdir(parents=True)
    (td / "docs" / "03_EARS").mkdir(parents=True)
    (td / "docs" / "04_BDD").mkdir(parents=True)
    (td / "docs" / "07_TDD").mkdir(parents=True)
    (td / "docs" / "02_PRD" / "PRD-01.md").write_text(
        textwrap.dedent(
            """
            ---
            doc_id: PRD-01
            ---
            # PRD-01
            """
        ).strip()
        + "\n"
    )
    (td / "docs" / "03_EARS" / "EARS-01.md").write_text(
        textwrap.dedent(
            """
            ---
            doc_id: EARS-01
            ---
            # EARS-01
            @prd: PRD-01
            """
        ).strip()
        + "\n"
    )
    (td / "docs" / "04_BDD" / "BDD-01.md").write_text(
        textwrap.dedent(
            """
            ---
            doc_id: BDD-01
            ---
            # BDD-01
            @ears: EARS-01
            """
        ).strip()
        + "\n"
    )
    (td / "docs" / "07_TDD" / "TDD-01.md").write_text(
        textwrap.dedent(
            """
            ---
            doc_id: TDD-01
            ---
            # TDD-01
            @bdd: BDD-01
            """
        ).strip()
        + "\n"
    )


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TRACE_WALK)] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


class TraceWalk(unittest.TestCase):
    def test_walk_emits_all_ancestors(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            _write_fixture_corpus(td_path)
            result = _run(["TDD-01"], cwd=td_path)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            ancestors = {
                line.split("--[hop-")[1].split("]--> ")[1].strip()
                for line in result.stdout.splitlines()
                if "hop-" in line
            }
            # TDD-01 reaches BDD-01 (hop 1), EARS-01 (hop 2), PRD-01 (hop 3)
            self.assertEqual(ancestors, {"BDD-01", "EARS-01", "PRD-01"})

    def test_walk_to_filter_excludes_layers_below_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            _write_fixture_corpus(td_path)
            result = _run(["TDD-01", "--to", "BDD"], cwd=td_path)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            # With --to BDD, only ancestors at-or-above BDD survive.
            # BDD-01 (layer 4) ✓; EARS-01 (3) and PRD-01 (2) drop.
            ancestors = {
                line.split("--[hop-")[1].split("]--> ")[1].strip()
                for line in result.stdout.splitlines()
                if "hop-" in line
            }
            self.assertEqual(ancestors, {"BDD-01"})

    def test_unresolved_tag_returns_nonzero(self):
        """Broken trace chain → exit 1 + UNRESOLVED message."""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            (td_path / "docs" / "07_TDD").mkdir(parents=True)
            (td_path / "docs" / "07_TDD" / "TDD-01.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    doc_id: TDD-01
                    ---
                    # TDD-01
                    @bdd: BDD-99
                    """
                ).strip()
                + "\n"
            )
            result = _run(["TDD-01"], cwd=td_path)
            self.assertEqual(
                result.returncode, 1, msg=f"stdout={result.stdout} stderr={result.stderr}"
            )
            self.assertIn("UNRESOLVED", result.stderr)
            self.assertIn("BDD-99", result.stderr)

    def test_malformed_artifact_id_returns_2(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            (td_path / "docs").mkdir()
            result = _run(["not-an-id"], cwd=td_path)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
