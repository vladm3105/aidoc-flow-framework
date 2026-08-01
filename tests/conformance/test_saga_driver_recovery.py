"""Conformance: saga_driver.py recovery, disclosure and exit-code contract.

Locks the PLUGIN-PREPROD-001 PR 3 findings:

* **B2** — the `--dangerously-skip-permissions` bypass is opt-in
  (`--allow-skip-permissions`) and absent from the dispatched command by
  default.
* **B3a** — the four unconditional `PARTIAL_TIMEOUT` transitions use the
  forced path, so a saga in a state that cannot reach `PARTIAL_TIMEOUT`
  terminates and journals instead of raising.
* **B3b** — `dispatch_phase` does not clobber transitions the dispatched
  subprocess wrote to `saga.json`.
* **B3c** — the resume walk considers run-scoped transitions only.
* **M3** — the GNU `timeout` wrapper is probed for, not assumed, and a
  failed spawn cannot leave a journalled dispatch that never happened.
* **M4** — a saga that ends `PARTIAL_TIMEOUT` or `ESCALATED` exits
  non-zero, with a code that is neither 2 (argparse) nor 124 (`timeout`).
* **M5** — `verdict.json` is invalidated before every audit dispatch.
* **L2** — `--threshold` gates the PASS verdict when the audit reported a
  `content_score`, and is inert when it did not.

No live subprocess is spawned; `subprocess.run` and `dispatch_phase` are
stubbed. The live cascade exercises the real dispatch separately.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "tools"))
import saga_driver  # noqa: E402  (path injection above is intentional)


def _ctx(root: Path, **kwargs) -> saga_driver.SagaContext:
    saga_dir = root / ".aidoc" / "review" / "01_BRD" / "BRD-01"
    saga_dir.mkdir(parents=True, exist_ok=True)
    defaults = dict(
        layer="01_BRD",
        layer_type="BRD",
        artifact_id="BRD-01",
        artifact_path=root / "docs" / "01_BRD" / "BRD-01.md",
        saga_dir=saga_dir,
        saga_file=saga_dir / "saga.json",
        plugin_dir=root / "plugin",
    )
    defaults.update(kwargs)
    return saga_driver.SagaContext(**defaults)


def _saga(status: str, **kwargs) -> dict:
    saga = {
        "review_run_id": "r1",
        "artifact_id": "BRD-01",
        "layer": "01_BRD",
        "status": status,
        "iteration": 1,
        "current_phase": "review",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "branches": {},
        "transitions": [
            {"ts": "2026-01-01T00:00:00+00:00", "from": None, "to": status, "scope": "run"}
        ],
        "compensation_actions": [],
        "events": [],
    }
    saga.update(kwargs)
    return saga


class PermissionBypassIsOptIn(unittest.TestCase):
    """B2: the bypass ships off and is requested at the invocation site."""

    def _dispatched_cmd(self, **ctx_kwargs) -> list[str]:
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td), **ctx_kwargs)
            with mock.patch.object(saga_driver.subprocess, "run") as run:
                run.return_value = mock.Mock(returncode=0)
                saga_driver.dispatch_phase(ctx, "draft", "brief")
            return list(run.call_args.args[0])

    def test_bypass_absent_by_default(self):
        self.assertNotIn("--dangerously-skip-permissions", self._dispatched_cmd())

    def test_bypass_present_when_opted_in(self):
        cmd = self._dispatched_cmd(allow_skip_permissions=True)
        self.assertIn("--dangerously-skip-permissions", cmd)

    def test_flag_is_accepted_by_the_parser(self):
        parser = saga_driver.build_parser()
        args = parser.parse_args(
            [
                "--layer",
                "01_BRD",
                "--artifact-id",
                "BRD-01",
                "--artifact-path",
                "a/b/c/d.md",
                "--seed",
                "s.md",
                "--plugin-dir",
                "p",
                "--allow-skip-permissions",
            ]
        )
        self.assertTrue(args.allow_skip_permissions)

    def test_flag_defaults_off(self):
        parser = saga_driver.build_parser()
        args = parser.parse_args(
            [
                "--layer",
                "01_BRD",
                "--artifact-id",
                "BRD-01",
                "--artifact-path",
                "a/b/c/d.md",
                "--seed",
                "s.md",
                "--plugin-dir",
                "p",
            ]
        )
        self.assertFalse(args.allow_skip_permissions)


class ForcedTransitionsDoNotWedge(unittest.TestCase):
    """B3a: PARTIAL_TIMEOUT is reachable from every non-terminal state via
    the forced path, and the forced edge is journalled as such."""

    UNREACHABLE = ["BRANCH_FAILED", "BRANCH_COMPENSATING", "SYNTHESIZED"]

    def test_forced_transition_records_instead_of_raising(self):
        for state in self.UNREACHABLE:
            with self.subTest(state=state):
                saga = _saga(state)
                saga_driver.append_transition(
                    saga, from_state=state, to_state="PARTIAL_TIMEOUT", forced=True
                )
                last = saga["transitions"][-1]
                self.assertEqual(last["to"], "PARTIAL_TIMEOUT")
                self.assertTrue(last.get("forced"))

    def test_unforced_transition_still_raises(self):
        """The preemptive validation is unchanged for ordinary callers."""
        saga = _saga("BRANCH_FAILED")
        with self.assertRaises(ValueError):
            saga_driver.append_transition(
                saga, from_state="BRANCH_FAILED", to_state="PARTIAL_TIMEOUT"
            )

    def test_break_circuit_from_unreachable_state(self):
        for state in self.UNREACHABLE:
            with self.subTest(state=state), tempfile.TemporaryDirectory() as td:
                ctx = _ctx(Path(td))
                saga = _saga(state, current_phase="review")
                with mock.patch.object(saga_driver, "SOFT_DEADLINE_SECONDS", -1):
                    self.assertTrue(saga_driver.check_break_circuit(ctx, saga))
                self.assertEqual(saga["status"], "PARTIAL_TIMEOUT")
                self.assertEqual(json.loads(ctx.saga_file.read_text())["status"], "PARTIAL_TIMEOUT")

    def test_iteration_cap_from_branch_failed(self):
        """A saga at BRANCH_FAILED hitting the cap terminates and journals."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            (ctx.saga_dir / "verdict.json").write_text(
                json.dumps({"combined_status": "FAIL", "content_score": 40})
            )
            saga = _saga("BRANCH_FAILED", iteration=99)
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertEqual(saga["status"], "PARTIAL_TIMEOUT")
            self.assertTrue(saga["transitions"][-1].get("forced"))

    def test_missing_verdict_from_unreachable_state(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            saga = _saga("BRANCH_FAILED")
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertEqual(saga["status"], "PARTIAL_TIMEOUT")

    def test_subprocess_failure_from_unreachable_state(self):
        """The fourth call site: main's non-zero subprocess branch."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ctx = _ctx(root)
            ctx.saga_file.write_text(json.dumps(_saga("BRANCH_FAILED")))
            rc = _run_main(root, dispatch_rc=1)
            self.assertEqual(json.loads(ctx.saga_file.read_text())["status"], "PARTIAL_TIMEOUT")
            self.assertEqual(rc, saga_driver.EXIT_PARTIAL_TIMEOUT)


class DispatchPreservesSubprocessJournal(unittest.TestCase):
    """B3b: the post-subprocess write must not clobber what the child wrote."""

    def test_subprocess_transitions_survive_dispatch(self):
        """The audit subprocess loads saga.json, stamps its own per-branch
        transitions and status, and writes it back. None of that may be lost
        to the driver's post-dispatch write."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            saga = _saga("FANOUT_STARTED")
            ctx.saga_file.write_text(json.dumps(saga))

            def fake_run(cmd, **kwargs):
                child = json.loads(ctx.saga_file.read_text())
                child["status"] = "BRANCH_COMPLETED"
                child["branches"] = {
                    "architect": {"branch_id": "b1", "status": "BRANCH_COMPLETED", "attempt": 0}
                }
                child["transitions"].append(
                    {
                        "ts": "2026-01-01T00:01:00+00:00",
                        "from": "BRANCH_RUNNING",
                        "to": "BRANCH_COMPLETED",
                        "scope": "branch:architect",
                    }
                )
                ctx.saga_file.write_text(json.dumps(child))
                return mock.Mock(returncode=0)

            with mock.patch.object(saga_driver.subprocess, "run", side_effect=fake_run):
                saga_driver.dispatch_phase(ctx, "review", "brief", saga=saga)

            on_disk = json.loads(ctx.saga_file.read_text())
            self.assertEqual(on_disk["status"], "BRANCH_COMPLETED")
            self.assertIn("architect", on_disk["branches"])
            scopes = [t.get("scope") for t in on_disk["transitions"]]
            self.assertIn("branch:architect", scopes)
            kinds = [e["kind"] for e in on_disk["events"]]
            self.assertIn("dispatch:review", kinds)
            self.assertIn("complete:review", kinds)

    def test_corrupt_child_journal_is_not_overwritten_silently(self):
        """A child that dies mid-write leaves unreadable JSON. Swallowing that
        and writing the stale snapshot back is the B3b clobber again — and it
        destroys the evidence of why the child failed."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            saga = _saga("FANOUT_STARTED")
            ctx.saga_file.write_text(json.dumps(saga))

            def fake_run(cmd, **kwargs):
                ctx.saga_file.write_text('{"status": "BRANCH_COMPLETED", "transi')
                return mock.Mock(returncode=0)

            with mock.patch.object(saga_driver.subprocess, "run", side_effect=fake_run):
                rc = saga_driver.dispatch_phase(ctx, "review", "brief", saga=saga)

            self.assertNotEqual(rc, 0, "an unreadable journal is a failed phase")
            quarantine = ctx.saga_dir / "saga.corrupt.json"
            self.assertTrue(quarantine.exists(), "corrupt journal was destroyed")
            self.assertEqual(quarantine.read_text(), '{"status": "BRANCH_COMPLETED", "transi')

    def test_child_write_is_authoritative(self):
        """A child that rewrites saga.json wholesale — rather than loading it
        first — still wins. Its `events` list replaces the driver's, dropping
        the `dispatch:` stamp; that is the accepted consequence of treating
        the child's write as authoritative, not a clobber to undo."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            saga = _saga("FANOUT_STARTED")
            ctx.saga_file.write_text(json.dumps(saga))
            fabricated = _saga("BRANCH_COMPLETED")

            def fake_run(cmd, **kwargs):
                ctx.saga_file.write_text(json.dumps(fabricated))
                return mock.Mock(returncode=0)

            with mock.patch.object(saga_driver.subprocess, "run", side_effect=fake_run):
                saga_driver.dispatch_phase(ctx, "review", "brief", saga=saga)

            on_disk = json.loads(ctx.saga_file.read_text())
            self.assertEqual(on_disk["status"], "BRANCH_COMPLETED")
            self.assertEqual([e["kind"] for e in on_disk["events"]], ["complete:review"])

    def test_caller_dict_reflects_disk_after_dispatch(self):
        """The in-memory dict the caller holds is reconciled with disk, so a
        caller that does not reload cannot act on a stale status."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            saga = _saga("FANOUT_STARTED")
            ctx.saga_file.write_text(json.dumps(saga))

            def fake_run(cmd, **kwargs):
                ctx.saga_file.write_text(json.dumps(_saga("BRANCH_COMPLETED")))
                return mock.Mock(returncode=0)

            with mock.patch.object(saga_driver.subprocess, "run", side_effect=fake_run):
                saga_driver.dispatch_phase(ctx, "review", "brief", saga=saga)
            self.assertEqual(saga["status"], "BRANCH_COMPLETED")


class TerminalChainToleratesSubprocessState(unittest.TestCase):
    """B3b sequencing: preserving the child's status un-masks a latent raise on
    the PASS terminal chain when that status cannot reach FANIN_REDUCED.

    Not raising is necessary but not sufficient — the run must also not
    *close*. A PASS arriving on a journal that records no completed fan-in is
    evidence the audit is broken, and walking it to CLOSED would report
    success for a review the state machine says cannot have finished.
    """

    def test_pass_from_unreachable_state_does_not_close(self):
        for state in ("BRANCH_FAILED", "BRANCH_COMPENSATING", "ESCALATED"):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as td:
                ctx = _ctx(Path(td))
                (ctx.saga_dir / "verdict.json").write_text(
                    json.dumps({"combined_status": "PASS", "content_score": 95})
                )
                saga = _saga(state)
                saga_driver._advance_after_phase(ctx, saga, "review")
                self.assertNotEqual(saga["status"], "CLOSED")
                self.assertNotEqual(saga_driver._exit_code_for_status(saga["status"]), 0)

    def test_escalation_is_never_rewritten_as_success(self):
        """The concrete regression: an audit that escalates and also writes a
        PASS verdict must not have its escalation erased."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            (ctx.saga_dir / "verdict.json").write_text(
                json.dumps({"combined_status": "PASS", "content_score": 99})
            )
            saga = _saga("ESCALATED")
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertEqual(saga["status"], "ESCALATED")

    def test_forced_transitions_may_only_target_partial_timeout(self):
        """The invariant behind the two tests above: forcing toward a success
        state would report a pass the transition table says was unreachable."""
        saga = _saga("ESCALATED")
        for target in ("FANIN_REDUCED", "SYNTHESIZED", "CLOSED", "BRANCH_COMPLETED"):
            with self.subTest(target=target):
                with self.assertRaises(ValueError):
                    saga_driver.append_transition(
                        saga, from_state="ESCALATED", to_state=target, forced=True
                    )

    def test_pass_from_legal_state_still_closes(self):
        for state in ("BRANCH_COMPLETED", "FANIN_REDUCED", "SYNTHESIZED"):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as td:
                ctx = _ctx(Path(td))
                (ctx.saga_dir / "verdict.json").write_text(
                    json.dumps({"combined_status": "PASS", "content_score": 95})
                )
                saga = _saga(state)
                saga_driver._advance_after_phase(ctx, saga, "review")
                self.assertEqual(saga["status"], "CLOSED")

    def test_gate_failure_on_a_terminal_saga_does_not_exit_zero(self):
        """The child left the saga CLOSED but the verdict did not converge:
        the gate must not fire into a run that then reports success."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td), threshold=90)
            (ctx.saga_dir / "verdict.json").write_text(
                json.dumps({"combined_status": "PASS", "content_score": 40})
            )
            saga = _saga("CLOSED")
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertEqual(saga["status"], "PARTIAL_TIMEOUT")
            self.assertNotEqual(saga_driver._exit_code_for_status(saga["status"]), 0)


class ResumeIsRunScoped(unittest.TestCase):
    """B3c: a branch-scoped terminal must not become the run status."""

    def test_branch_scoped_transitions_ignored(self):
        saga = {
            "status": "PARTIAL_TIMEOUT",
            "transitions": [
                {"from": None, "to": "PREPARED", "scope": "run"},
                {"from": "PREPARED", "to": "FANOUT_STARTED", "scope": "run"},
                {"from": "FANOUT_STARTED", "to": "BRANCH_RUNNING", "scope": "branch:architect"},
                {"from": "BRANCH_RUNNING", "to": "BRANCH_FAILED", "scope": "branch:architect"},
                {"from": "FANOUT_STARTED", "to": "PARTIAL_TIMEOUT", "scope": "run"},
            ],
        }
        saga_driver.resume_from_partial_timeout(saga)
        self.assertEqual(saga["status"], "FANOUT_STARTED")

    def test_scopeless_transitions_default_to_run(self):
        """Claim 48: the existing fixture carries no `scope` keys, and the
        audit SKILL's LLM writes scope-less transitions directly."""
        saga = {
            "status": "PARTIAL_TIMEOUT",
            "transitions": [
                {"from": None, "to": "PREPARED"},
                {"from": "PREPARED", "to": "FANOUT_STARTED"},
                {"from": "FANOUT_STARTED", "to": "BRANCH_RUNNING"},
                {"from": "BRANCH_RUNNING", "to": "PARTIAL_TIMEOUT"},
            ],
        }
        saga_driver.resume_from_partial_timeout(saga)
        self.assertEqual(saga["status"], "BRANCH_RUNNING")

    def test_falls_back_to_prepared_when_no_run_scoped_entry(self):
        saga = {
            "status": "PARTIAL_TIMEOUT",
            "transitions": [
                {"from": "BRANCH_RUNNING", "to": "BRANCH_FAILED", "scope": "branch:auditor"},
                {"from": None, "to": "PARTIAL_TIMEOUT", "scope": "run"},
            ],
        }
        saga_driver.resume_from_partial_timeout(saga)
        self.assertEqual(saga["status"], "PREPARED")


class TimeoutWrapperIsProbed(unittest.TestCase):
    """M3: `timeout` is GNU coreutils and absent on a stock macOS."""

    def _cmd_and_kwargs(self, which_map):
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            with mock.patch.object(saga_driver.shutil, "which", side_effect=which_map.get):
                with mock.patch.object(saga_driver.subprocess, "run") as run:
                    run.return_value = mock.Mock(returncode=0)
                    saga_driver.dispatch_phase(ctx, "draft", "brief")
            return list(run.call_args.args[0]), run.call_args.kwargs

    def test_gnu_timeout_used_when_present(self):
        cmd, kwargs = self._cmd_and_kwargs({"timeout": "/usr/bin/timeout"})
        self.assertEqual(cmd[0], "/usr/bin/timeout")
        self.assertIsNone(kwargs.get("timeout"))

    def test_gtimeout_fallback(self):
        cmd, kwargs = self._cmd_and_kwargs({"gtimeout": "/opt/homebrew/bin/gtimeout"})
        self.assertEqual(cmd[0], "/opt/homebrew/bin/gtimeout")

    def test_python_timeout_when_neither_present(self):
        cmd, kwargs = self._cmd_and_kwargs({})
        self.assertEqual(cmd[0], "claude")
        self.assertEqual(kwargs.get("timeout"), saga_driver.SUBPROCESS_TIMEOUT_SECONDS)

    def test_python_timeout_expiry_maps_to_124(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            saga = _saga("PREPARED")
            ctx.saga_file.write_text(json.dumps(saga))
            with mock.patch.object(saga_driver.shutil, "which", return_value=None):
                with mock.patch.object(
                    saga_driver.subprocess,
                    "run",
                    side_effect=saga_driver.subprocess.TimeoutExpired("claude", 1),
                ):
                    rc = saga_driver.dispatch_phase(ctx, "draft", "brief", saga=saga)
            self.assertEqual(rc, 124)

    def test_failed_spawn_journals_completion(self):
        """A dispatch event with no completion event is a journal that claims
        work which never happened."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td))
            saga = _saga("PREPARED")
            ctx.saga_file.write_text(json.dumps(saga))
            with mock.patch.object(
                saga_driver.subprocess, "run", side_effect=FileNotFoundError("claude")
            ):
                rc = saga_driver.dispatch_phase(ctx, "draft", "brief", saga=saga)
            self.assertNotEqual(rc, 0)
            kinds = [e["kind"] for e in json.loads(ctx.saga_file.read_text())["events"]]
            self.assertIn("complete:draft", kinds)


class ExitCodesAreMeaningful(unittest.TestCase):
    """M4: a caller chaining on success must not proceed on an artifact that
    never passed review."""

    def test_codes_are_distinct_and_unambiguous(self):
        codes = {saga_driver.EXIT_PARTIAL_TIMEOUT, saga_driver.EXIT_ESCALATED}
        self.assertNotIn(0, codes)
        self.assertNotIn(2, codes, "2 is argparse's usage error")
        self.assertNotIn(124, codes, "124 is `timeout`, which the harness special-cases")
        self.assertEqual(len(codes), 2)

    def test_status_mapping(self):
        self.assertEqual(saga_driver._exit_code_for_status("CLOSED"), 0)
        self.assertEqual(
            saga_driver._exit_code_for_status("PARTIAL_TIMEOUT"),
            saga_driver.EXIT_PARTIAL_TIMEOUT,
        )
        self.assertEqual(saga_driver._exit_code_for_status("ESCALATED"), saga_driver.EXIT_ESCALATED)

    def test_break_circuit_return_is_non_zero(self):
        """Claim 49: the `return 0` taken straight after the break circuit is
        the single most likely way a run ends non-CLOSED."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with mock.patch.object(saga_driver, "SOFT_DEADLINE_SECONDS", -1):
                rc = _run_main(root, dispatch_rc=0)
            self.assertEqual(rc, saga_driver.EXIT_PARTIAL_TIMEOUT)

    def test_already_escalated_saga_exits_non_zero(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ctx = _ctx(root)
            ctx.saga_file.write_text(json.dumps(_saga("ESCALATED")))
            with self.assertRaises(SystemExit) as cm:
                _run_main(root, dispatch_rc=0)
            self.assertEqual(cm.exception.code, saga_driver.EXIT_ESCALATED)

    def test_unspawnable_subprocess_is_not_reported_as_resumable(self):
        """A missing `claude` binary is an environment defect. Reporting it as
        PARTIAL_TIMEOUT tells the operator to retry a run that will fail
        identically every time."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            def stub(ctx_, phase, brief, saga=None):
                return saga_driver.EXIT_SPAWN_FAILED

            rc = _run_main(root, dispatch_stub=stub)
            self.assertEqual(rc, saga_driver.EXIT_SPAWN_FAILED)
            self.assertNotEqual(rc, saga_driver.EXIT_PARTIAL_TIMEOUT)
            saga = json.loads((root / ".aidoc/review/01_BRD/BRD-01/saga.json").read_text())
            self.assertEqual(saga["status"], "PARTIAL_TIMEOUT")
            self.assertIn(
                "could not be spawned",
                saga["compensation_actions"][-1]["reason"],
            )

    def test_already_closed_saga_still_exits_zero(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ctx = _ctx(root)
            ctx.saga_file.write_text(json.dumps(_saga("CLOSED")))
            with self.assertRaises(SystemExit) as cm:
                _run_main(root, dispatch_rc=0)
            self.assertEqual(cm.exception.code, 0)

    def test_closed_run_exits_zero(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ctx = _ctx(root)
            ctx.saga_file.write_text(json.dumps(_saga("FANOUT_STARTED", current_phase="review")))
            rc = _run_main(root, dispatch_rc=0)
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(ctx.saga_file.read_text())["status"], "CLOSED")


class VerdictIsInvalidatedBetweenIterations(unittest.TestCase):
    """M5: a stale PASS must not be read as current."""

    def test_verdict_unlinked_before_audit_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ctx = _ctx(root)
            ctx.saga_file.write_text(json.dumps(_saga("FANOUT_STARTED", current_phase="review")))
            verdict = ctx.saga_dir / "verdict.json"
            verdict.write_text(json.dumps({"combined_status": "PASS", "content_score": 99}))

            seen: list[bool] = []

            def stub(ctx_, phase, brief, saga=None):
                seen.append(verdict.exists())
                verdict.write_text(json.dumps({"combined_status": "PASS", "content_score": 95}))
                return 0

            _run_main(root, dispatch_stub=stub)
            self.assertEqual(seen, [False], "stale verdict.json survived into the audit")
            self.assertTrue(
                (ctx.saga_dir / "verdict.iter1.json").exists(),
                "the superseded verdict was deleted, not rotated — its "
                "blocking_findings are what a human needs at the resulting "
                "PARTIAL_TIMEOUT",
            )
            self.assertEqual(
                json.loads((ctx.saga_dir / "verdict.iter1.json").read_text())["content_score"],
                99,
            )

    def test_verdict_kept_for_non_audit_phases(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ctx = _ctx(root)
            ctx.saga_file.write_text(json.dumps(_saga("PREPARED", current_phase="draft")))
            verdict = ctx.saga_dir / "verdict.json"
            verdict.write_text(json.dumps({"combined_status": "PASS", "content_score": 99}))

            seen: list[bool] = []

            def stub(ctx_, phase, brief, saga=None):
                if phase == "draft":
                    seen.append(verdict.exists())
                    saga_ = json.loads(ctx.saga_file.read_text())
                    saga_["status"] = "PARTIAL_TIMEOUT"
                    ctx.saga_file.write_text(json.dumps(saga_))
                    return 1
                return 0

            _run_main(root, dispatch_stub=stub)
            self.assertEqual(seen, [True])


class ThresholdIsHonored(unittest.TestCase):
    """L2: the flag string must survive (claim 52) and must not be inert."""

    def test_flag_still_accepted(self):
        parser = saga_driver.build_parser()
        args = parser.parse_args(
            [
                "--layer",
                "01_BRD",
                "--artifact-id",
                "BRD-01",
                "--artifact-path",
                "a/b/c/d.md",
                "--seed",
                "s.md",
                "--plugin-dir",
                "p",
                "--threshold",
                "90",
            ]
        )
        self.assertEqual(args.threshold, 90)

    def test_pass_below_threshold_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td), threshold=90)
            (ctx.saga_dir / "verdict.json").write_text(
                json.dumps({"combined_status": "PASS", "content_score": 71})
            )
            saga = _saga("BRANCH_COMPLETED", iteration=1)
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertNotEqual(saga["status"], "CLOSED")
            self.assertEqual(saga["current_phase"], "fixer")

    def test_pass_at_threshold_closes(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td), threshold=90)
            (ctx.saga_dir / "verdict.json").write_text(
                json.dumps({"combined_status": "PASS", "content_score": 90})
            )
            saga = _saga("BRANCH_COMPLETED")
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertEqual(saga["status"], "CLOSED")

    def test_scoreless_pass_is_not_gated(self):
        """CHG has no numeric readiness score by design — see the
        `content_score_note` in the CHG verdict of the example corpus. A
        verdict that reports no score must not be gated to death."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td), threshold=90)
            (ctx.saga_dir / "verdict.json").write_text(
                json.dumps({"combined_status": "PASS", "content_score_advisory": 95})
            )
            saga = _saga("BRANCH_COMPLETED")
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertEqual(saga["status"], "CLOSED")

    def test_float_score_is_gated(self):
        """`92.5` is an ordinary thing for an LLM-written verdict to contain.
        An int-only reader silently disables the gate on it."""
        for raw, closes in ((95.0, True), (88.5, False), (90.0, True)):
            with self.subTest(score=raw), tempfile.TemporaryDirectory() as td:
                ctx = _ctx(Path(td), threshold=90)
                (ctx.saga_dir / "verdict.json").write_text(
                    json.dumps({"combined_status": "PASS", "content_score": raw})
                )
                saga = _saga("BRANCH_COMPLETED")
                saga_driver._advance_after_phase(ctx, saga, "review")
                self.assertEqual(saga["status"] == "CLOSED", closes)

    def test_numeric_string_score_is_gated(self):
        for raw, closes in (("95", True), ("71", False)):
            with self.subTest(score=raw), tempfile.TemporaryDirectory() as td:
                ctx = _ctx(Path(td), threshold=90)
                (ctx.saga_dir / "verdict.json").write_text(
                    json.dumps({"combined_status": "PASS", "content_score": raw})
                )
                saga = _saga("BRANCH_COMPLETED")
                saga_driver._advance_after_phase(ctx, saga, "review")
                self.assertEqual(saga["status"] == "CLOSED", closes)

    def test_unusable_score_fails_closed(self):
        """A score that is present but unreadable means a broken audit. It
        must NOT take the same ungated path as a verdict reporting none."""
        for raw in (True, "n/a", [], {}):
            with self.subTest(score=raw), tempfile.TemporaryDirectory() as td:
                ctx = _ctx(Path(td), threshold=90)
                (ctx.saga_dir / "verdict.json").write_text(
                    json.dumps({"combined_status": "PASS", "content_score": raw})
                )
                saga = _saga("BRANCH_COMPLETED")
                saga_driver._advance_after_phase(ctx, saga, "review")
                self.assertNotEqual(saga["status"], "CLOSED")

    def test_unusable_score_is_classified_as_unusable(self):
        """Assert the classification, not just the outcome. `true` happens to
        fail a threshold of 90 by comparing as 1, so an outcome-only assertion
        passes even when bool is wrongly accepted as a score."""
        for raw in (True, False, "n/a", [], {}):
            with self.subTest(score=raw), tempfile.TemporaryDirectory() as td:
                ctx = _ctx(Path(td), threshold=90)
                (ctx.saga_dir / "verdict.json").write_text(
                    json.dumps({"combined_status": "PASS", "content_score": raw})
                )
                score, _ = saga_driver.read_verdict_score(ctx)
                self.assertIs(score, saga_driver.SCORE_UNUSABLE)
                self.assertFalse(saga_driver._meets_threshold(ctx, score))

    def test_a_true_score_cannot_pass_a_low_threshold(self):
        """The case an outcome-only test cannot see: `true` compares as 1, so
        with a threshold of 1 an accepted bool would close the saga."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td), threshold=1)
            (ctx.saga_dir / "verdict.json").write_text(
                json.dumps({"combined_status": "PASS", "content_score": True})
            )
            saga = _saga("BRANCH_COMPLETED")
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertNotEqual(saga["status"], "CLOSED")

    def test_explicit_null_score_is_treated_as_absent(self):
        """`"content_score": null` is how an audit says "no numeric score",
        so it belongs with the absent case, not the unusable one."""
        with tempfile.TemporaryDirectory() as td:
            ctx = _ctx(Path(td), threshold=90)
            (ctx.saga_dir / "verdict.json").write_text(
                json.dumps({"combined_status": "PASS", "content_score": None})
            )
            saga = _saga("BRANCH_COMPLETED")
            saga_driver._advance_after_phase(ctx, saga, "review")
            self.assertEqual(saga["status"], "CLOSED")


def _run_main(root: Path, *, dispatch_rc: int = 0, dispatch_stub=None):
    """Drive `main` against a scratch tree with dispatch stubbed out."""
    artifact = root / "docs" / "01_BRD" / "BRD-01.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("# BRD-01\n")
    seed = root / "seed.md"
    seed.write_text("seed\n")
    saga_file = root / ".aidoc" / "review" / "01_BRD" / "BRD-01" / "saga.json"
    verdict = saga_file.parent / "verdict.json"

    def default_stub(ctx_, phase, brief, saga=None):
        current = json.loads(saga_file.read_text())
        if dispatch_rc == 0:
            current["status"] = "BRANCH_COMPLETED"
            saga_file.write_text(json.dumps(current))
            verdict.write_text(json.dumps({"combined_status": "PASS", "content_score": 95}))
        return dispatch_rc

    with mock.patch.object(saga_driver, "dispatch_phase", dispatch_stub or default_stub):
        return saga_driver.main(
            [
                "--layer",
                "01_BRD",
                "--artifact-id",
                "BRD-01",
                "--artifact-path",
                str(artifact),
                "--seed",
                str(seed),
                "--plugin-dir",
                str(root / "plugin"),
                "--threshold",
                "90",
            ]
        )


if __name__ == "__main__":
    unittest.main()
