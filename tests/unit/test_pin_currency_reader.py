"""Unit: the pin-currency reader's parse and reconcile scripts.

Covers `scripts/read-pin-currency-log.sh` and
`scripts/reconcile-pin-currency-issue.sh` (PIN-CURRENCY-NO-READER).

Neither script may need network, `gh` or auth: this module is loaded into the
conformance suite by `tests/conformance/test_repo_scripts.py`, and that suite
runs on EVERY commit via an `always_run` pre-commit hook. A test here that
reached the network would fail an offline contributor's commit.

The reconcile's `gh` calls are served by a stub installed on PATH, per canon's
own `GH="${GH:-gh}"` injection point. The stub applies the real `jq` to its
canned response, so the script's exact-title compare is genuinely exercised
rather than stubbed past.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
READ = REPO_ROOT / "scripts" / "read-pin-currency-log.sh"
RECONCILE = REPO_ROOT / "scripts" / "reconcile-pin-currency-issue.sh"

TITLE = "CI canon drift — stale @ci/v* pins"

# The ten callers the measured run reported stale, in the parser's sorted form.
STALE_SET = ",".join(
    f"{name}@ci/v2.14.0"
    for name in sorted(
        [
            "ai-review.yml",
            "audit-trail.yml",
            "auto-merge-ai-prs.yml",
            "composition.yml",
            "docs-sync.yml",
            "labeler.yml",
            "links.yml",
            "pre-commit.yml",
            "secret-scan.yml",
            "standards-drift.yml",
        ]
    )
)

# A `gh` stand-in. Records every invocation, serves a canned `issue list`
# through the real jq, and can be told to fail a labelled `issue create`.
GH_STUB = r"""#!/usr/bin/env bash
printf '%s\n' "$*" >> "$GH_CALLS"
# Capture every --body-file payload so tests can assert on generated CONTENT,
# not just on the call sequence. The script deletes these via its own trap.
prev=""
for a in "$@"; do
  if [ "$prev" = "--body-file" ] && [ -f "$a" ]; then
    cat "$a" >> "$GH_BODIES"
    printf '\n===BODY-BOUNDARY===\n' >> "$GH_BODIES"
  fi
  prev="$a"
done
if [ "${1:-}" = issue ] && [ "${2:-}" = list ]; then
  jqexpr=""
  while [ $# -gt 0 ]; do [ "$1" = "--jq" ] && jqexpr="${2:-}"; shift; done
  if [ -n "$jqexpr" ]; then jq -r "$jqexpr" < "$GH_LIST_JSON"; else cat "$GH_LIST_JSON"; fi
  exit 0
fi
if [ "${1:-}" = issue ] && [ "${2:-}" = create ]; then
  if [ "${GH_FAIL_LABELLED_CREATE:-0}" = 1 ] && [[ "$*" == *--label* ]]; then
    echo "could not add label: 'ci' not found" >&2
    exit 1
  fi
  echo "https://github.com/vladm3105/aidoc-flow-framework/issues/999"
  exit 0
fi
exit 0
"""


def run_parse(log: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(READ), str(log)],
        capture_output=True,
        text=True,
        check=False,
    )


def parse_kv(stdout: str) -> dict[str, str]:
    out = {}
    for line in stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            out[key] = value
    return out


class ParseLogTests(unittest.TestCase):
    """Eight cases: four verdicts that exit 0, four shapes that must exit non-zero."""

    def test_stale_log_yields_ten_files_and_the_canon_token(self):
        result = run_parse(FIXTURES / "standards_drift_stale.log")
        self.assertEqual(result.returncode, 0, result.stderr)
        kv = parse_kv(result.stdout)
        self.assertEqual(kv["verdict"], "stale")
        self.assertEqual(kv["stale_count"], "10")
        self.assertEqual(kv["canon"], "ci/v2.15.0")
        self.assertEqual(kv["stale_files"], STALE_SET)
        self.assertIn("8 drift", kv["drift_summary"])

    def test_clean_log_yields_clean_and_no_files(self):
        result = run_parse(FIXTURES / "standards_drift_clean.log")
        self.assertEqual(result.returncode, 0, result.stderr)
        kv = parse_kv(result.stdout)
        self.assertEqual(kv["verdict"], "clean")
        self.assertEqual(kv["stale_count"], "0")
        self.assertEqual(kv["canon"], "ci/v2.15.0")
        self.assertEqual(kv["stale_files"], "")

    def test_skipped_log_is_not_an_error(self):
        """Canon's documented `::notice::` skip is a real, benign log shape."""
        result = run_parse(FIXTURES / "standards_drift_skipped.log")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(parse_kv(result.stdout)["verdict"], "skipped")

    def test_unresolved_is_not_swallowed_by_skipped(self):
        """An unresolved log has no verdict line either, so `skipped` would
        match it. The check order is what keeps them distinct."""
        result = run_parse(FIXTURES / "standards_drift_unresolved.log")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(parse_kv(result.stdout)["verdict"], "unresolved")

    def test_truncated_log_exits_non_zero(self):
        """A log with no evidence the drift script ran must FAIL, not parse as
        a benign `skipped` — absence of signal is the failure mode this whole
        workflow exists to remove."""
        with tempfile.TemporaryDirectory() as tmp:
            garbage = Path(tmp) / "truncated.log"
            garbage.write_text("job\tstep\t2026-07-27T10:23:42.0000000Z Cleaning up\n")
            result = run_parse(garbage)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("check-standards-drift", result.stderr)

    def test_log_truncated_mid_run_exits_non_zero(self):
        """The regression guard for the reader's worst failure mode. The drift
        script emits an OPENING `check-standards-drift: repo=… tier=…` header
        and a `cannot check <family>` warning per unreadable family, all under
        the same prefix and all well before the pin-currency section. A gate
        that only proved the script STARTED would report `skipped` — exit 0,
        green run — on a truncated download of a run with ten stale pins. The
        window is real: `workflow_run: completed` fires while the log archive
        is still assembling, and a partial archive is non-empty."""
        full = (FIXTURES / "standards_drift_stale.log").read_text().splitlines(True)
        opening = next(i for i, ln in enumerate(full) if "check-standards-drift: repo=" in ln)
        pin = next(i for i, ln in enumerate(full) if "pin-currency: auditing" in ln)
        self.assertLess(opening, pin, "fixture no longer has the opening header")
        for cut in (opening + 1, pin):
            with self.subTest(truncated_at=cut):
                with tempfile.TemporaryDirectory() as tmp:
                    log = Path(tmp) / "partial.log"
                    log.write_text("".join(full[:cut]))
                    result = run_parse(log)
                self.assertNotEqual(
                    result.returncode, 0, f"truncation at {cut} parsed as a verdict"
                )

    def test_contradictory_verdict_lines_exit_non_zero(self):
        """Both a stale count and `all pins current` cannot be true of one run;
        guessing which to honour would either open or close the issue wrongly."""
        source = (FIXTURES / "standards_drift_stale.log").read_text()
        both = source.replace(
            "pin-currency: 10 stale pin(s)",
            "pin-currency: all pins current ✅\npin-currency: 10 stale pin(s)",
        )
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "both.log"
            log.write_text(both)
            result = run_parse(log)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contradictory", result.stderr)

    def test_malformed_canon_token_exits_non_zero(self):
        """A `curl` that returns an error page instead of failing makes canon's
        ver_cmp fall through to equal and print `all pins current` — a false
        clean. Honouring it would close the tracking issue on a transient."""
        source = (FIXTURES / "standards_drift_clean.log").read_text()
        poisoned = source.replace("against canon ci/v2.15.0", "against canon <!DOCTYPE html>")
        self.assertNotEqual(source, poisoned, "fixture shape changed")
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "poisoned.log"
            log.write_text(poisoned)
            result = run_parse(log)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed", result.stderr)


class ReconcileIssueTests(unittest.TestCase):
    """Ten cases: six reconciliation scenarios, the label fallback, and three
    that assert generated body CONTENT rather than the call sequence."""

    @classmethod
    def setUpClass(cls):
        if shutil.which("jq") is None:
            raise unittest.SkipTest("jq not available")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        stub = self.bin / "gh"
        stub.write_text(GH_STUB)
        stub.chmod(0o755)
        self.calls = self.tmp / "calls.txt"
        self.calls.touch()
        self.bodies = self.tmp / "bodies.txt"
        self.bodies.touch()
        self.addCleanup(self._tmp.cleanup)

    def written_bodies(self) -> list[str]:
        raw = self.bodies.read_text()
        return [b for b in raw.split("===BODY-BOUNDARY===") if b.strip()]

    def list_json(self, issues) -> Path:
        path = self.tmp / "list.json"
        path.write_text(json.dumps(issues))
        return path

    def open_issue_fixture(self) -> list:
        return json.loads((FIXTURES / "gh_stub_issue_open.json").read_text())

    def reconcile(self, verdict_kv: str, issues, dry_run=True, fail_label=False):
        env = dict(os.environ)
        env.update(
            {
                "GH": str(self.bin / "gh"),
                "GH_CALLS": str(self.calls),
                "GH_BODIES": str(self.bodies),
                "GH_LIST_JSON": str(self.list_json(issues)),
                "GH_FAIL_LABELLED_CREATE": "1" if fail_label else "0",
                "PATH": f"{self.bin}:{env.get('PATH', '')}",
            }
        )
        cmd = [
            "bash",
            str(RECONCILE),
            "--repo",
            "vladm3105/aidoc-flow-framework",
            "--run-url",
            "https://github.com/vladm3105/aidoc-flow-framework/actions/runs/1",
            "--assignee",
            "vladm3105",
        ]
        if dry_run:
            cmd.append("--dry-run")
        result = subprocess.run(
            cmd, input=verdict_kv, capture_output=True, text=True, check=False, env=env
        )
        return result, self.calls.read_text()

    @staticmethod
    def stale_kv(count=10, files=STALE_SET) -> str:
        return (
            f"verdict=stale\nstale_count={count}\ncanon=ci/v2.15.0\n"
            f"stale_files={files}\ndrift_summary=8 drift, 4 fetch/scope error(s), "
            "0 pin error(s) (warning-only)\n"
        )

    def test_stale_with_no_prior_issue_creates_and_assigns(self):
        result, calls = self.reconcile(self.stale_kv(), [])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("issue create", result.stdout)
        self.assertIn("--label ci", result.stdout)
        self.assertIn("--add-assignee vladm3105", result.stdout)
        self.assertNotIn("issue comment", result.stdout)
        # The lookup's flags are load-bearing and easy to "tidy away" later, so
        # they are asserted rather than left to the stub to ignore. Dropping
        # `--limit 200` ages the tracking issue off page 1 and opens a
        # duplicate; dropping `--state all` breaks the reopen contract.
        self.assertIn("--state all", calls)
        self.assertIn("--limit 200", calls)
        self.assertIn("--json number,title,state,body", calls)

    def test_stale_with_unchanged_set_edits_silently(self):
        result, _ = self.reconcile(self.stale_kv(), self.open_issue_fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("issue edit 412", result.stdout)
        self.assertNotIn("issue comment", result.stdout)
        self.assertNotIn("issue create", result.stdout)

    def test_generated_body_round_trips_through_the_state_reader(self):
        """The body this script writes must be readable by the block parser it
        reads with. Nothing else proves the writer and reader agree — if the
        fence name or a key drifted, every previous-verdict field would come
        back empty and the reader would comment on EVERY run, with the rest of
        the suite still green."""
        first, _ = self.reconcile(self.stale_kv(), [], dry_run=False)
        self.assertEqual(first.returncode, 0, first.stderr)
        generated = self.written_bodies()[0]
        self.assertIn("```pin-currency-state", generated)

        # The GFM table must be terminated by a blank line, or the remedy
        # paragraph below it is absorbed into the table as junk rows.
        table_end = generated.index("| `standards-drift.yml` | `ci/v2.14.0` |")
        after = generated[table_end:].split("\n", 1)[1]
        self.assertTrue(after.startswith("\n"), "no blank line terminates the table")
        self.assertIn("--repin", generated)

        # Feed it straight back as the stored body: identical verdict, so the
        # comment trigger must NOT fire.
        issues = [{"number": 412, "title": TITLE, "state": "OPEN", "body": generated}]
        second, _ = self.reconcile(self.stale_kv(), issues)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("updated silently", second.stdout)
        self.assertNotIn("issue comment", second.stdout)

    def test_stamp_preserves_the_state_block_and_appends_when_absent(self):
        """A stamp-only week must not regenerate the body: that would clear the
        stored stale set, so the next identical `stale` reading would look like
        clean → stale and emit a spurious comment."""
        kv = (
            "verdict=unresolved\nstale_count=0\ncanon=\nstale_files=\n"
            "drift_summary=8 drift, 4 fetch/scope error(s), 0 pin error(s)\n"
        )
        result, _ = self.reconcile(kv, self.open_issue_fixture(), dry_run=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        stamped = self.written_bodies()[0]
        self.assertIn(f"stale_files={STALE_SET}", stamped)
        self.assertIn("stale_count=10", stamped)
        self.assertEqual(stamped.count("last verified "), 1)
        self.assertNotIn("last verified 2026-07-27T10:30:00Z", stamped)

        # And when the line has been hand-edited away, it must be APPENDED —
        # not silently skipped while the notice claims the stamp succeeded.
        self.bodies.write_text("")
        issues = self.open_issue_fixture()
        for issue in issues:
            if issue["title"] == TITLE:
                issue["body"] = issue["body"].replace("last verified 2026-07-27T10:30:00Z\n", "")
        result, _ = self.reconcile(kv, issues, dry_run=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        appended = self.written_bodies()[0]
        self.assertEqual(appended.count("last verified "), 1)
        self.assertIn(f"stale_files={STALE_SET}", appended)

    def test_stale_with_changed_count_edits_and_comments(self):
        """A count moving 10 → 15 must notify. Without this the change would be
        a silent body edit, which defeats having an assignee at all."""
        grown = STALE_SET + ",codeql.yml@ci/v2.14.0"
        result, _ = self.reconcile(self.stale_kv(count=11, files=grown), self.open_issue_fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("issue edit 412", result.stdout)
        self.assertIn("issue comment 412", result.stdout)

    def test_stale_with_closed_issue_reopens_rather_than_recreating(self):
        """The stale → clean → stale cycle recurs once per canon release, so
        create-on-stale would produce one issue per release, not one issue."""
        issues = self.open_issue_fixture()
        for issue in issues:
            if issue["title"] == TITLE:
                issue["state"] = "CLOSED"
        result, _ = self.reconcile(self.stale_kv(), issues)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("issue reopen 412", result.stdout)
        self.assertIn("issue comment 412", result.stdout)
        self.assertNotIn("issue create", result.stdout)

    def test_clean_with_open_issue_closes_and_comments(self):
        kv = (
            "verdict=clean\nstale_count=0\ncanon=ci/v2.15.0\nstale_files=\n"
            "drift_summary=0 drift, 0 fetch/scope error(s), 0 pin error(s)\n"
        )
        result, _ = self.reconcile(kv, self.open_issue_fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("issue close 412", result.stdout)
        self.assertIn("issue comment 412", result.stdout)

    def test_no_generated_markdown_contains_an_escaped_backtick(self):
        r"""These strings are built by `printf` inside SINGLE quotes, where a
        backslash before a backtick is a literal backslash rather than an
        escape — so it renders as `\` to a human reading the issue. Caught on
        issue #393's real close comment during post-merge verification; every
        comment and body path is swept here so it cannot come back in one of
        the branches the others do not exercise."""
        clean_kv = (
            "verdict=clean\nstale_count=0\ncanon=ci/v2.15.0\nstale_files=\n"
            "drift_summary=0 drift, 0 fetch/scope error(s), 0 pin error(s)\n"
        )
        closed = self.open_issue_fixture()
        for issue in closed:
            if issue["title"] == TITLE:
                issue["state"] = "CLOSED"
        for label, kv, issues in (
            ("close", clean_kv, self.open_issue_fixture()),
            ("create", self.stale_kv(), []),
            ("silent-edit", self.stale_kv(), self.open_issue_fixture()),
            ("reopen", self.stale_kv(), closed),
            # The changed-set comment is a SEPARATE printf from the reopen one,
            # and it is the most frequent commenting path — it fires on every
            # canon release that shifts the set. Sweeping the other four leaves
            # it a mutation survivor.
            (
                "changed-set",
                self.stale_kv(count=11, files=STALE_SET + ",codeql.yml@ci/v2.14.0"),
                self.open_issue_fixture(),
            ),
        ):
            with self.subTest(path=label):
                self.bodies.write_text("")
                result, _ = self.reconcile(kv, issues, dry_run=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                written = "".join(self.written_bodies())
                self.assertNotIn("\\`", written, f"{label} path emits an escaped backtick")

    def test_silent_verdicts_stamp_without_touching_state(self):
        """`skipped` and `unresolved` must not open, close or reopen anything —
        but they still stamp, so the READER's own staleness is visible in the
        artifact it maintains."""
        for verdict in ("skipped", "unresolved"):
            with self.subTest(verdict=verdict):
                self.calls.write_text("")
                kv = (
                    f"verdict={verdict}\nstale_count=0\ncanon=\nstale_files=\n"
                    "drift_summary=8 drift, 4 fetch/scope error(s), 0 pin error(s)\n"
                )
                result, _ = self.reconcile(kv, self.open_issue_fixture())
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("issue edit 412", result.stdout)
                for forbidden in ("issue close", "issue reopen", "issue create"):
                    self.assertNotIn(forbidden, result.stdout)

        # The steady state: creation happens only on `stale`, so a silent
        # verdict normally finds no artifact to stamp. That is a no-op, not an
        # error — the stamp's visibility claim is scoped to an issue that exists.
        with self.subTest(verdict="skipped", issue="absent"):
            self.calls.write_text("")
            kv = (
                "verdict=skipped\nstale_count=0\ncanon=\nstale_files=\n"
                "drift_summary=8 drift, 4 fetch/scope error(s), 0 pin error(s)\n"
            )
            result, _ = self.reconcile(kv, [])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("nothing to stamp", result.stdout)
            self.assertNotIn("issue edit", result.stdout)

    def test_labelled_create_failure_still_produces_an_issue(self):
        """An unknown label makes `gh issue create` error, and this runs
        unattended. The retry drops the LABEL only — never the create itself,
        which `|| true` would have done."""
        result, calls = self.reconcile(self.stale_kv(), [], dry_run=False, fail_label=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        creates = [c for c in calls.splitlines() if c.startswith("issue create")]
        self.assertEqual(len(creates), 2, calls)
        self.assertIn("--label ci", creates[0])
        self.assertNotIn("--label", creates[1])
        self.assertIn("::warning::", result.stdout + result.stderr)
        # This is the only test that reaches the REAL post-create assignee
        # branch — the dry-run test above is satisfied by a printed literal, so
        # without this assertion R8's notification path has no coverage on the
        # code that actually ships.
        self.assertTrue(
            any(
                c.startswith("issue edit") and "--add-assignee vladm3105" in c
                for c in calls.splitlines()
            ),
            calls,
        )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(0 if unittest.main(exit=False).result.wasSuccessful() else 1)
