"""Unit: every pre-push-stage hook has a CI invoker.

Regression cover for CHG-24 #798: the pre-push validation hook declared
`stages: [pre-push` in `.pre-commit-config.yaml` while CI ran only bare
`pre-commit run --all-files` (pre-commit stage), so the gate never fired
outside local pushes. A pre-push hook without a CI invocation is a
documented guarantee that nothing enforces.
"""

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def pre_push_hook_ids():
    with CONFIG.open(encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    ids = []
    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []):
            if "pre-push" in (hook.get("stages") or []):
                ids.append(hook["id"])
    return ids


def workflow_texts():
    return {path.name: path.read_text(encoding="utf-8") for path in WORKFLOWS.glob("*.yml")}


class HookStageCoverageTests(unittest.TestCase):
    def test_pre_push_hook_runs_test_suites(self):
        # #818: the pre-push gate must run the same suites CI runs
        # (CI_AUTONOMOUS_PR_STANDARD.md Invariant 1) — a linters-only hook
        # lets suite failures escape to a full CI round-trip. Comments are
        # stripped first so the test pins executable invocation, not a prose
        # mention in the scope header.
        text = (REPO_ROOT / "hooks" / "pre_push_check.sh").read_text(encoding="utf-8")
        code = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
        self.assertRegex(
            code,
            r"python3\s+-m\s+unittest\s+discover",
            "pre_push_check.sh never invokes the unittest entry point",
        )
        for suite in ("tests/conformance", "tests/unit", "sdd_doc_lint/tests"):
            with self.subTest(suite=suite):
                self.assertIn(
                    suite,
                    code,
                    f"pre_push_check.sh never invokes {suite}",
                )

    def test_pre_push_stage_invoked_in_ci(self):
        ids = pre_push_hook_ids()
        self.assertTrue(ids, "no pre-push-stage hook declared")
        texts = workflow_texts()
        invokers = [
            name for name, text in texts.items() if "--hook-stage" in text and "pre-push" in text
        ]
        self.assertTrue(
            invokers,
            f"pre-push hooks {ids} have no CI invoker "
            "(want a workflow running `pre-commit run --hook-stage pre-push`)",
        )


if __name__ == "__main__":
    unittest.main()
