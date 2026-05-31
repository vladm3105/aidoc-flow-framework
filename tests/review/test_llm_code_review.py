"""Review: spawn an LLM code-reviewer agent on the current diff."""

import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REVIEW_ENABLED = os.environ.get("REVIEW") == "1"
HAS_CLAUDE = shutil.which("claude") is not None


@unittest.skipUnless(
    REVIEW_ENABLED and HAS_CLAUDE, "review tier disabled (set REVIEW=1; claude CLI required)"
)
class LlmCodeReviewTests(unittest.TestCase):
    BLOCKING_LINE_PATTERN = r"^SEVERITY:\s*(BLOCKER|CRITICAL)\b"

    def test_reviewer_emits_no_blocking_findings(self):
        runner = Path(__file__).resolve().parent / "run-claude-review.sh"
        r = subprocess.run(["bash", str(runner)], capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr)
        offenders = re.findall(self.BLOCKING_LINE_PATTERN, r.stdout, flags=re.MULTILINE)
        self.assertFalse(
            offenders,
            f"LLM reviewer surfaced {len(offenders)} blocking findings:\n{r.stdout}",
        )
