"""Unit: hooks/ch-gate-check.sh matches indented statuses portably and reads
staged content, not HEAD, for the bug-fix hint (#690).

The hook runs against throwaway fixture repos, never the real tree: each case
builds a fresh `git init` repo with a staged code file plus a fixture CHG, so
no dirty-tree skip is needed.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / "hooks" / "ch-gate-check.sh"

_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@test",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@test",
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, env=_ENV, check=True, capture_output=True)


def _fixture(status_body: str, staged_extra: dict[str, str] | None = None) -> Path:
    """A repo with a staged .py file and a fixture CHG under 09_CHG/."""
    tmp = Path(tempfile.mkdtemp(prefix="chgate-"))
    _git(tmp, "init", "-q")
    _git(tmp, "commit", "-q", "--allow-empty", "-m", "previous commit")
    chg_dir = tmp / "framework" / "layers" / "09_CHG"
    chg_dir.mkdir(parents=True)
    (chg_dir / "CHG-01_fixture.yaml").write_text(status_body, encoding="utf-8")
    (tmp / "a.py").write_text("print(1)\n", encoding="utf-8")
    _git(tmp, "add", "a.py", str(chg_dir / "CHG-01_fixture.yaml"))
    for name, body in (staged_extra or {}).items():
        (tmp / name).write_text(body, encoding="utf-8")
        _git(tmp, "add", name)
    return tmp


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(HOOK)], cwd=repo, env=_ENV, capture_output=True, text=True, check=False
    )


class ChGateCheckTests(unittest.TestCase):
    def test_indented_in_progress_matches(self):
        """An indented `status: In-Progress` arms the gate (#690: no GNU `\\s`)."""
        repo = _fixture("change_control:\n  status: In-Progress\n")
        result = _run(repo)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Active CHG found", result.stdout)

    def test_indented_approved_matches(self):
        repo = _fixture('change_control:\n  status: "Approved"\n')
        result = _run(repo)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Active CHG found", result.stdout)

    def test_staged_bugfix_vehicle_noted(self):
        """A staged CHG naming a bug-fix vehicle draws the verify note (#690).

        The old code grepped HEAD (the *previous* commit) at pre-commit time,
        so this path could never fire as intended.
        """
        repo = _fixture("change_control:\n  status: Draft\nparent_iplan: IPLAN-03\n")
        result = _run(repo)
        self.assertEqual(result.returncode, 0)
        self.assertIn("bug-fix vehicle", result.stdout)

    def test_plain_draft_suggests_exception(self):
        repo = _fixture("change_control:\n  status: Draft\n")
        result = _run(repo)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Exception: bug fixes on active IPLANs", result.stdout)


if __name__ == "__main__":
    unittest.main()
