#!/usr/bin/env python3
"""Deterministic preemptive orchestrator for the review-saga lifecycle.

CANONICAL SOURCE: tools/saga_driver.py (edit here).
Vendored byte-identical mirror at platforms/claude-code-plugin/tools/saga_driver.py
is produced by tools/sync-plugin-framework.sh — DO NOT EDIT the vendored copy;
any direct edit there is overwritten on the next sync run. (CLEANUP-PR-A item 3.)

Plays the same role for the Claude Code plugin that `saga_orchestrator.py`
plays for Hermes: drives the create-review-revise loop, validates state
machine transitions against `framework/governance/REVIEW_SAGA.md`, manages
the durable saga.json journal, and dispatches each phase as a separately-
budgeted subprocess.

Invoked by `doc-<layer>-autopilot` SKILLs (thin entry points) via Bash.

Per SAGA-PARITY-001 Phase 2 Amendment 1, this script SUPERSEDES the
cooperative-enforcement pattern in Phase 2's original SKILL prompts -
which empirically failed (2026-06-05 verification: invalid transitions,
non-terminal final status, no subprocess dispatch).

Spec authority: `framework/governance/REVIEW_SAGA.md` and
`framework/governance/saga.schema.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

# Spec authority: framework/governance/REVIEW_SAGA.md "Transition table"
# A conformance test asserts this matches the spec table exactly.
_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "PREPARED": {"FANOUT_STARTED", "PARTIAL_TIMEOUT"},
    "FANOUT_STARTED": {"BRANCH_RUNNING", "PARTIAL_TIMEOUT"},
    "BRANCH_RUNNING": {"BRANCH_COMPLETED", "BRANCH_FAILED", "PARTIAL_TIMEOUT"},
    "BRANCH_FAILED": {"BRANCH_COMPENSATING", "ESCALATED", "BRANCH_COMPLETED"},
    "BRANCH_COMPENSATING": {"BRANCH_RUNNING", "ESCALATED"},
    "BRANCH_COMPLETED": {"FANIN_REDUCED", "PARTIAL_TIMEOUT"},
    "FANIN_REDUCED": {"SYNTHESIZED", "PARTIAL_TIMEOUT"},
    "SYNTHESIZED": {"CLOSED"},
    "ESCALATED": set(),
    "CLOSED": set(),
    "PARTIAL_TIMEOUT": set(),
}

# Per layer, the crew (persona names) drawn from REVIEW_CREWS.yaml.
# Keep in sync with framework/governance/REVIEW_CREWS.yaml.
# Drift is caught by tests/conformance/test_saga_driver_invariants.py
# via test_layer_crews_match_yaml (Pass-4 A7).
_LAYER_CREWS: dict[str, list[str]] = {
    "01_BRD": ["business_analyst", "architect", "auditor", "chaos_engineer", "security_engineer"],
    "02_PRD": [
        "product_owner",
        "architect",
        "tech_lead",
        "chaos_engineer",
        "security_engineer",
        "auditor",
    ],
    "03_EARS": [
        "requirements_specialist",
        "tech_lead",
        "qa_lead",
        "chaos_engineer",
        "security_engineer",
    ],
    "04_BDD": [
        "qa_lead",
        "tech_lead",
        "chaos_engineer",
        "security_engineer",
        "operator",
        "auditor",
    ],
    "05_ADR": [
        "architect",
        "tech_lead",
        "chaos_engineer",
        "security_engineer",
        "operator",
        "auditor",
    ],
    "06_SPEC": [
        "architect",
        "tech_lead",
        "integration_lead",
        "chaos_engineer",
        "security_engineer",
    ],
    "07_TDD": [
        "qa_lead",
        "tech_lead",
        "chaos_engineer",
        "security_engineer",
        "operator",
        "auditor",
    ],
    "08_IPLAN": [
        "tech_lead",
        "architect",
        "operator",
        "integration_lead",
        "auditor",
        "chaos_engineer",
    ],
    "09_CHG": [
        "integration_lead",
        "architect",
        "chaos_engineer",
        "operator",
        "auditor",
        "security_engineer",
    ],
}

# Bumped 1500s -> 3300s (Amendment 1 verification, 2026-06-05): a
# realistic BRD cycle with one fixer pass takes ~40-55 min wall-clock
# (draft ~10 min + audit ~15 min + fixer ~10 min + re-audit ~15 min).
# 1500s only covered the draft+audit happy path and PARTIAL_TIMEOUT'd
# on every fixer cycle.
# Bumped 3300s -> 5100s (SAGA-BUDGET-001, 2026-06-08): BDD-RT-001's
# 3-audit / 2-fixer convergence took 58:38 to PASS — within 1:22 of
# the 3600s harness ceiling. 5100s gives the full ~5-phase chain plus
# the 300s margin below the bumped ORCHESTRATOR_TIMEOUT (5400s) so
# the driver can write its PARTIAL_TIMEOUT state gracefully before the
# wrapper SIGTERMs.
SOFT_DEADLINE_SECONDS = 5100
SUBPROCESS_TIMEOUT_SECONDS = 1800
# Default for the quality-loop iteration cap (REVIEW_REMEDIATION_FLOW.md
# §Iteration cap). Projects can override via the
# `quality_loop_max_iterations` knob in `.aidoc/profile.yaml` (see
# ADAPTATION_SURFACE.yaml). The actual cap used at runtime is computed
# by `_resolve_max_iterations(profile_path)` which loads the profile,
# reads the knob, and falls back to this default if the file is
# missing, malformed, or the field is absent / out of range [1, 10].
MAX_ITERATIONS = 3

# Process exit codes. A caller that chains on success must not proceed on an
# artifact that never passed review, so a saga ending in a non-CLOSED terminal
# state exits non-zero.
#
# Deliberately neither 2 nor 124: argparse spends 2 on a usage error, and 124
# is what `timeout` returns, which `tests/scripts/test-acceptance.sh`
# special-cases as "driver timeout". Reusing either would make failure
# attribution in that harness ambiguous.
EXIT_OK = 0
EXIT_PARTIAL_TIMEOUT = 4
EXIT_ESCALATED = 5
# Returned when the phase subprocess could not be spawned at all (the shell
# convention for command-not-found). Returned by `main` directly, not mapped
# through `_exit_code_for_status`: the saga does end PARTIAL_TIMEOUT, but
# reporting a missing `claude` binary as a resumable deadline would tell the
# operator to retry a run that will fail identically every time.
EXIT_SPAWN_FAILED = 127


# Sentinel: `verdict.json` reported a `content_score` that cannot be read as a
# number. Distinct from `None`, which means it reported none at all — the two
# must not share a gate outcome (see `read_verdict_score`).
SCORE_UNUSABLE = object()

# Terminal states that already represent a run which did not pass review. A
# saga sitting in one of these has nothing left to force.
_FAILURE_TERMINALS = frozenset({"PARTIAL_TIMEOUT", "ESCALATED"})


def _force_partial_timeout(saga: dict, *, scope: str = "run") -> None:
    """Drive the saga to PARTIAL_TIMEOUT from wherever it is.

    No-ops when the saga already sits in a failure terminal: re-forcing
    `PARTIAL_TIMEOUT -> PARTIAL_TIMEOUT` writes a meaningless self-edge, and
    rewriting an `ESCALATED` run as merely timed-out would downgrade a state
    that asks for a human.
    """
    if saga["status"] in _FAILURE_TERMINALS:
        return
    append_transition(
        saga, from_state=saga["status"], to_state="PARTIAL_TIMEOUT", scope=scope, forced=True
    )
    saga["status"] = "PARTIAL_TIMEOUT"


def _exit_code_for_status(status: str) -> int:
    """Map a terminal saga status to the driver's process exit code."""
    if status == "PARTIAL_TIMEOUT":
        return EXIT_PARTIAL_TIMEOUT
    if status == "ESCALATED":
        return EXIT_ESCALATED
    return EXIT_OK


def _resolve_max_iterations(profile_path: str | Path | None = None) -> int:
    """Resolve the quality-loop iteration cap.

    Reads `.aidoc/profile.yaml` `quality_loop_max_iterations` if present
    and valid (integer in range [1, 10]). Falls back to the
    `MAX_ITERATIONS` default for missing-file / malformed-yaml /
    missing-field / out-of-range values. Never raises — the fallback
    preserves the current pre-CLEANUP-PR-C behavior exactly.
    """
    if profile_path is None:
        profile_path = Path(".aidoc/profile.yaml")
    else:
        profile_path = Path(profile_path)
    try:
        if not profile_path.is_file():
            return MAX_ITERATIONS
        with profile_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError):
        return MAX_ITERATIONS
    if not isinstance(data, dict):
        return MAX_ITERATIONS
    value = data.get("quality_loop_max_iterations")
    if not isinstance(value, int) or value < 1 or value > 10:
        return MAX_ITERATIONS
    return value


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _det_run_id(*, artifact_path: str, personas: list[str], time_bucket: str) -> str:
    payload = f"{artifact_path}|{','.join(sorted(personas))}|{time_bucket}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _det_branch_id(*, run_id: str, persona: str) -> str:
    return hashlib.sha256(f"{run_id}|{persona}".encode()).hexdigest()[:12]


@dataclass
class SagaContext:
    layer: str
    layer_type: str
    artifact_id: str
    artifact_path: Path
    saga_dir: Path
    saga_file: Path
    start_epoch: float = field(default_factory=time.time)
    threshold: int = 90
    plugin_dir: Path | None = None
    # Opt-in only (PLUGIN-PREPROD-001 B2). When false — the default — the
    # dispatched phase subprocess runs under Claude Code's normal permission
    # prompts. The 9 `doc-*-autopilot` SKILLs and the acceptance harness pass
    # `--allow-skip-permissions` explicitly, so the bypass is visible where it
    # is requested rather than hidden in this driver.
    allow_skip_permissions: bool = False


def load_or_init_saga(ctx: SagaContext, seed_path: Path) -> dict:
    """Load existing saga.json or initialize a fresh one.

    Entry conditions handled here:
    - saga.json missing -> fresh init (pre-Phase-2 blackboard migration
      if slot files are present).
    - status CLOSED -> log + sys.exit(0); ESCALATED -> log +
      sys.exit(EXIT_ESCALATED), since that artifact never passed review.
    - status PARTIAL_TIMEOUT or any other in-flight state -> resume.
    """
    if ctx.saga_file.exists():
        saga = json.loads(ctx.saga_file.read_text())
        status = saga.get("status", "")
        if status == "CLOSED":
            print(
                f"saga already CLOSED for {ctx.artifact_id}; "
                f"iteration {saga.get('iteration', 1)} complete"
            )
            sys.exit(0)
        if status == "ESCALATED":
            # Non-zero for the same reason main's return is (M4): the artifact
            # never passed review, so a caller chaining on success must not
            # proceed just because this invocation had nothing left to do.
            print(f"saga ESCALATED for {ctx.artifact_id}; human review required")
            sys.exit(EXIT_ESCALATED)
        return saga

    ctx.saga_dir.mkdir(parents=True, exist_ok=True)
    crew = _LAYER_CREWS[ctx.layer]
    run_id = _det_run_id(
        artifact_path=str(ctx.artifact_path),
        personas=crew,
        time_bucket=datetime.now(UTC).strftime("%Y%m%d"),
    )

    existing_slots = list(ctx.saga_dir.glob("*.json"))
    pre_phase2_slots = [s for s in existing_slots if s.stem in crew and s.name != "saga.json"]

    if pre_phase2_slots:
        branches = {}
        for slot in pre_phase2_slots:
            branches[slot.stem] = {
                "branch_id": _det_branch_id(run_id=run_id, persona=slot.stem),
                "status": "BRANCH_COMPLETED",
                "attempt": 0,
                "started_at": _utc_now_iso(),
                "ended_at": _utc_now_iso(),
            }
        return {
            "review_run_id": run_id,
            "artifact_id": ctx.artifact_id,
            "layer": ctx.layer,
            "personas_requested": crew,
            "status": "BRANCH_COMPLETED",
            "iteration": 1,
            "current_phase": "re-review",
            "created_at": _utc_now_iso(),
            "updated_at": _utc_now_iso(),
            "branches": branches,
            "transitions": [
                {
                    "ts": _utc_now_iso(),
                    "from": None,
                    "to": "BRANCH_COMPLETED",
                    "scope": "run",
                }
            ],
            "compensation_actions": [],
            "events": [],
        }

    return {
        "review_run_id": run_id,
        "artifact_id": ctx.artifact_id,
        "layer": ctx.layer,
        "personas_requested": crew,
        "status": "PREPARED",
        "iteration": 1,
        "current_phase": "draft",
        "created_at": _utc_now_iso(),
        "updated_at": _utc_now_iso(),
        "branches": {},
        "transitions": [
            {
                "ts": _utc_now_iso(),
                "from": None,
                "to": "PREPARED",
                "scope": "run",
            }
        ],
        "compensation_actions": [],
        "events": [],
    }


def can_transition(*, current: str, target: str) -> bool:
    return target in _ALLOWED_TRANSITIONS.get(current, set())


def append_transition(
    saga: dict, *, from_state: str | None, to_state: str, scope: str = "run", forced: bool = False
) -> None:
    """Append a transition. Raises ValueError on invalid transitions
    (preemptive enforcement).

    `forced=True` records an edge the transition table does not allow instead
    of raising, stamping it `forced: true` so a journal reader can tell a
    reconciled edge from a legal one. It exists for the recovery paths that
    must reach `PARTIAL_TIMEOUT` from *any* non-terminal state — three of
    which (`BRANCH_FAILED`, `BRANCH_COMPENSATING`, `SYNTHESIZED`) cannot reach
    it legally, so an unforced call there raises and wedges the saga
    permanently (PLUGIN-PREPROD-001 B3a). Use it only where the alternative is
    an uncaught raise; `can_transition` itself stays strict.

    **A forced edge may only target `PARTIAL_TIMEOUT`.** Forcing toward a
    failure terminal is safe in the worst case — it fails a run that might
    have passed. Forcing toward `CLOSED` (or along the chain that reaches it)
    inverts that: it would report success for a saga the transition table says
    could not have got there, which is precisely the "reports PASS on reviews
    that never ran" defect this driver's fixes exist to remove. Anything
    wanting a forced success has a journal inconsistency to surface, not to
    paper over.
    """
    if forced and to_state != "PARTIAL_TIMEOUT":
        raise ValueError(
            f"forced transitions may only target PARTIAL_TIMEOUT, not {to_state}: "
            "forcing toward a success state would report a pass the state "
            "machine says was unreachable"
        )
    if from_state is not None and not can_transition(current=from_state, target=to_state):
        if not forced:
            raise ValueError(
                f"Invalid transition: {from_state} -> {to_state} "
                f"(allowed: {sorted(_ALLOWED_TRANSITIONS.get(from_state, set()))})"
            )
        entry = {
            "ts": _utc_now_iso(),
            "from": from_state,
            "to": to_state,
            "scope": scope,
            "forced": True,
        }
        saga["transitions"].append(entry)
        saga["updated_at"] = _utc_now_iso()
        return
    saga["transitions"].append(
        {
            "ts": _utc_now_iso(),
            "from": from_state,
            "to": to_state,
            "scope": scope,
        }
    )
    saga["updated_at"] = _utc_now_iso()


def append_event(saga: dict, kind: str, **extra) -> None:
    """Append a non-state-changing diagnostic event to saga.events[].

    Distinct from saga.transitions (which records state-machine moves
    validated against _ALLOWED_TRANSITIONS) and from saga.compensation_actions
    (which records compensation/error-handling actions). Events are pure
    orchestration observability — fixer dispatch + completion, subprocess
    exit codes, anything else worth diagnosing.

    Surfaced as a gap in SPEC-RT-001 live cascade (2026-06-09): saga claimed
    `iteration: 3` but the journal recorded only one audit cycle's transitions
    because fixer dispatch+completion left no journal trace. With this field
    populated, a journal reader can answer "how many fixer cycles ran and what
    was the outcome of each" without guessing from elapsed-time math.
    """
    saga.setdefault("events", []).append({"ts": _utc_now_iso(), "kind": kind, **extra})
    saga["updated_at"] = _utc_now_iso()


def write_saga(ctx: SagaContext, saga: dict) -> None:
    """Atomic write: temp file + rename."""
    tmp = ctx.saga_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(saga, indent=2))
    tmp.replace(ctx.saga_file)


def check_break_circuit(ctx: SagaContext, saga: dict) -> bool:
    """Return True if soft deadline crossed; saga.json is updated with
    PARTIAL_TIMEOUT and caller should exit."""
    elapsed = time.time() - ctx.start_epoch
    if elapsed > SOFT_DEADLINE_SECONDS:
        _force_partial_timeout(saga)
        write_saga(ctx, saga)
        print(
            f"break-circuit fired at {elapsed:.0f}s elapsed; "
            f"saga PARTIAL_TIMEOUT; current_phase={saga['current_phase']}"
        )
        return True
    return False


def resume_from_partial_timeout(saga: dict) -> None:
    """Per Phase 2 Pass 4 G-R1: walk transitions[] backward to find the
    pre-PARTIAL_TIMEOUT state. Set saga.status to that state so the loop
    continues from there. Do NOT append a transition with from: PARTIAL_TIMEOUT.

    Only **run-scoped** transitions are candidates: `transitions[]` interleaves
    run-scope and `branch:<lens>`-scope entries, so an unscoped walk can adopt
    a branch terminal (e.g. `BRANCH_FAILED` for one lens) as the whole run's
    status (PLUGIN-PREPROD-001 B3c).

    The `"run"` default is load-bearing, not stylistic. Scope-less entries are
    real — the audit SKILL's LLM writes transitions straight into `saga.json`,
    and `reconcile_post_audit` already reads `scope` defensively for that
    reason. Under a bare `t.get("scope") == "run"` any such journal would find
    no candidate and restart the saga at `PREPARED`.
    """
    if saga["status"] != "PARTIAL_TIMEOUT":
        return
    for t in reversed(saga["transitions"]):
        if t.get("scope", "run") == "run" and t["to"] != "PARTIAL_TIMEOUT":
            saga["status"] = t["to"]
            return
    saga["status"] = "PREPARED"


def _timeout_wrapper() -> list[str]:
    """Return the argv prefix that bounds a phase subprocess, if one exists.

    `timeout` is GNU coreutils: present on Linux, absent from a stock macOS,
    where Homebrew's coreutils installs it as `gtimeout`. Probe rather than
    assume — an unconditional `timeout` prefix makes every dispatch fail with
    a spawn error on macOS. Callers fall back to `subprocess.run(timeout=…)`
    when this returns empty (PLUGIN-PREPROD-001 M3).
    """
    for name in ("timeout", "gtimeout"):
        found = shutil.which(name)
        if found:
            return [found, str(SUBPROCESS_TIMEOUT_SECONDS)]
    return []


def _reload_saga_in_place(ctx: SagaContext, saga: dict) -> bool:
    """Refresh `saga` from disk, preserving the caller's dict identity.

    The dispatched subprocess writes its own per-branch transitions and status
    directly to `saga.json`. Mutating in place (rather than rebinding) means
    every holder of the dict — including the caller that passed it in — sees
    the child's work instead of a stale pre-dispatch snapshot.

    Returns False when the journal is unreadable, having first copied it aside
    as `saga.corrupt.json`. Swallowing that case silently would be the B3b
    clobber all over again: the caller would go on to write its stale
    pre-dispatch snapshot over the child's work *and* over the evidence of why
    the child failed, and nothing downstream could tell. The caller must treat
    False as a failed phase.
    """
    if not ctx.saga_file.exists():
        return True
    try:
        on_disk = json.loads(ctx.saga_file.read_text())
        if not isinstance(on_disk, dict):
            raise ValueError(f"saga.json is not a JSON object: {ctx.saga_file}")
    except (OSError, ValueError) as exc:
        quarantine = ctx.saga_file.with_name("saga.corrupt.json")
        try:
            shutil.copy2(ctx.saga_file, quarantine)
            preserved = f" preserved at {quarantine}"
        except OSError:
            preserved = " (could not be preserved)"
        print(
            f"saga.json is unreadable after the subprocess returned ({exc}); "
            f"the subprocess's work cannot be recovered and must not be "
            f"overwritten. Corrupt file{preserved}.",
            file=sys.stderr,
        )
        return False
    saga.clear()
    saga.update(on_disk)
    return True


def dispatch_phase(ctx: SagaContext, phase: str, brief: str, saga: dict | None = None) -> int:
    """Dispatch a phase subprocess. Returns the subprocess exit code.

    `phase` is one of: 'draft', 'review', 'fixer', 're-review'.

    If `saga` is provided, stamps `dispatch:<phase>` and `complete:<phase>`
    events to saga.events[] for orchestration observability (SPEC-RT-001
    2026-06-09 gap — fixer dispatch + completion previously left no
    journal trace).

    The completion event is appended to the saga **as the subprocess left it on
    disk**, not to the pre-dispatch in-memory copy. Writing the stale copy back
    clobbered every transition, branch update and status change the child made
    (PLUGIN-PREPROD-001 B3b) — the caller's later reload then read the driver's
    own overwrite and could not tell.
    """
    slash = {
        "draft": f"/aidoc-flow:doc-{ctx.layer_type.lower()}",
        "review": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-audit",
        "fixer": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-fixer",
        "re-review": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-audit",
    }[phase]
    claude_argv = [
        "claude",
        "--plugin-dir",
        str(ctx.plugin_dir),
    ]
    if ctx.allow_skip_permissions:
        claude_argv.append("--dangerously-skip-permissions")
    claude_argv += ["-p", f"{slash} {brief}"]

    wrapper = _timeout_wrapper()
    cmd = wrapper + claude_argv
    run_kwargs: dict = {"capture_output": False, "check": False}
    if not wrapper:
        run_kwargs["timeout"] = SUBPROCESS_TIMEOUT_SECONDS

    print(f"dispatch: {phase} ({slash}) ...")
    if saga is not None:
        append_event(saga, f"dispatch:{phase}", iteration=saga.get("iteration"), slash=slash)
        write_saga(ctx, saga)

    error: str | None = None
    try:
        returncode = subprocess.run(cmd, **run_kwargs).returncode
    except subprocess.TimeoutExpired:
        # Match GNU `timeout`'s exit code so both wrapper paths report a
        # deadline the same way to every caller.
        returncode = 124
        error = f"phase {phase} exceeded {SUBPROCESS_TIMEOUT_SECONDS}s"
    except (FileNotFoundError, PermissionError) as exc:
        # The dispatch event is already journalled. Returning without a
        # completion event would leave a journal claiming work that never
        # started, so record the failed spawn explicitly.
        #
        # Name `claude` rather than cmd[0]: when a wrapper is in use, cmd[0]
        # is the resolved timeout path that `shutil.which` just proved exists,
        # so blaming it points at the one binary that is definitely present.
        returncode = EXIT_SPAWN_FAILED
        error = f"could not spawn {claude_argv[0]!r}: {exc}"
        print(f"dispatch failed: {error}", file=sys.stderr)

    if saga is not None:
        if not _reload_saga_in_place(ctx, saga) and returncode == 0:
            # An unreadable journal is a failed phase even when the child
            # exited 0 — main must not advance the state machine on it.
            returncode = 1
            error = "saga.json unreadable after the subprocess returned"
        extra = {"error": error} if error else {}
        append_event(
            saga,
            f"complete:{phase}",
            iteration=saga.get("iteration"),
            exit_code=returncode,
            **extra,
        )
        write_saga(ctx, saga)
    return returncode


def read_verdict_score(ctx: SagaContext) -> tuple[int | float | None | object, str]:
    """Read .aidoc/review/<layer>/<id>/verdict.json. Returns (score, status).

    Returns (None, "MISSING") if verdict.json absent - caller treats this as
    an AUDIT FAILURE (per Pass-4 A9), distinct from a low content score
    (FAIL with score). Driver escalates rather than dispatching fixer.

    Three score outcomes, and conflating any two of them breaks the
    `--threshold` gate in one direction or the other:

    * a number (`int` or `float`) — gate on it.
    * `None`, when the verdict reports **no** `content_score`. Some layers
      have no numeric readiness score *by design*: CHG says so in its own
      `content_score_note` and gates on `combined_status` plus
      `blocking_findings_count`. Coercing that absence to 0 would fail every
      threshold and drive such a layer to the iteration cap.
    * `SCORE_UNUSABLE`, when the key **is** present but cannot be read as a
      number. `verdict.json` is written by an LLM-driven audit skill, so
      `92.5` and `"88"` are ordinary — but `true`, `null` or `"n/a"` are not
      scores. Treating those as "no score supplied" would silently disable
      the gate, which is the most likely way this gate fails in practice.
    """
    verdict_path = ctx.saga_dir / "verdict.json"
    if not verdict_path.exists():
        return None, "MISSING"
    v = json.loads(verdict_path.read_text())
    if not isinstance(v, dict):
        raise ValueError(f"verdict.json is not a JSON object: {verdict_path}")
    if "content_score" not in v or v["content_score"] is None:
        return None, v.get("combined_status", "UNKNOWN")
    raw = v["content_score"]
    score: int | float | object
    if isinstance(raw, bool):
        score = SCORE_UNUSABLE
    elif isinstance(raw, (int, float)):
        score = raw
    elif isinstance(raw, str):
        try:
            score = float(raw)
        except ValueError:
            score = SCORE_UNUSABLE
        else:
            print(
                f"verdict content_score was the string {raw!r}; read as {score}",
                file=sys.stderr,
            )
    else:
        score = SCORE_UNUSABLE
    if score is SCORE_UNUSABLE:
        print(
            f"verdict content_score is present but unusable ({raw!r}); "
            f"treating the run as not converged",
            file=sys.stderr,
        )
    return score, v.get("combined_status", "UNKNOWN")


def _invalidate_verdict(ctx: SagaContext, iteration: int) -> None:
    """Move verdict.json aside so a stale PASS cannot be read as current.

    The audit subprocess is not guaranteed to rewrite it — a crashed or
    non-team-mode audit leaves the previous iteration's file in place, which
    `read_verdict_score` would then read as the current verdict
    (PLUGIN-PREPROD-001 M5).

    Rotated rather than deleted. The file holds the `blocking_findings` that
    motivated this fixer pass, and the runs that most need it are exactly the
    ones where the next audit never writes a replacement: a human arriving at
    the resulting PARTIAL_TIMEOUT would otherwise find an empty review
    directory — neither the failing verdict nor a new one.
    """
    verdict = ctx.saga_dir / "verdict.json"
    if verdict.exists():
        verdict.replace(ctx.saga_dir / f"verdict.iter{iteration}.json")


def validate_and_repair_branches(ctx: SagaContext, saga: dict) -> None:
    """Per Pass-4 A8: after audit subprocess returns, validate that every
    branches[<persona>] entry has required fields per saga.schema.json
    (branch_id, status, attempt). If missing/malformed, repair from existing
    blackboard slot file mtimes.

    Per Pass-5 P5-2: if no slot file exists for a persona that's in the
    crew, fall back to saga.created_at as both started_at and ended_at.
    """
    crew = _LAYER_CREWS[ctx.layer]
    fallback_ts = saga.get("created_at", _utc_now_iso())
    for persona in crew:
        branch = saga.get("branches", {}).get(persona, {})
        slot_path = ctx.saga_dir / f"{persona}.json"
        if slot_path.exists():
            slot_ts = datetime.fromtimestamp(slot_path.stat().st_mtime, tz=UTC).isoformat()
        else:
            slot_ts = fallback_ts
        if "branch_id" not in branch or not branch["branch_id"]:
            branch["branch_id"] = _det_branch_id(run_id=saga["review_run_id"], persona=persona)
        if branch.get("status") not in {
            "BRANCH_RUNNING",
            "BRANCH_COMPLETED",
            "BRANCH_FAILED",
            "BRANCH_COMPENSATING",
        }:
            branch["status"] = "BRANCH_COMPLETED" if slot_path.exists() else "BRANCH_FAILED"
        if "attempt" not in branch:
            branch["attempt"] = 0
        if not branch.get("started_at"):
            branch["started_at"] = slot_ts
        if not branch.get("ended_at"):
            branch["ended_at"] = slot_ts
        saga.setdefault("branches", {})[persona] = branch


def reconcile_post_audit(ctx: SagaContext, saga: dict) -> None:
    """Backfill saga.transitions[] + walk saga.status when the audit SKILL's
    LLM skipped per-branch transition stamping.

    The audit SKILL prompt asks the LLM to do two writes per branch event:
    (1) update branches[<lens>] dict, (2) append a transition entry to
    saga.transitions[]. LLM stochasticity can produce (1) reliably while
    skipping (2) — observed in SPEC-RT-001 live cascade (2026-06-09): 5
    lenses transitioned to BRANCH_COMPLETED in the branches dict across 3
    audit cycles, but 0 of the 15 expected per-branch transitions stamped
    in transitions[]. Same byte-identical SKILL prompt worked correctly on
    ADR (35 transitions stamped).

    This function runs after every audit subprocess returns and reconciles
    the journal: if branches[<lens>].status is a terminal branch state but
    the matching `branch:<lens>` transition is absent from transitions[],
    backfill it (marked `reconciled: true`). Then advance saga.status from
    FANOUT_STARTED through BRANCH_RUNNING to BRANCH_COMPLETED at run scope
    when all branches are terminal — using the allowed-transition graph,
    so the existing PASS code path (line ~466: BRANCH_COMPLETED →
    FANIN_REDUCED) can fire correctly instead of trying the illegal
    FANOUT_STARTED → FANIN_REDUCED jump.

    Architecturally: this moves saga-state-machine bookkeeping from
    LLM-driven (cooperative; fragile under stochasticity) to driver-driven
    (preemptive; deterministic) — the same principle SAGA-PARITY-001
    Phase 2 Amendment 1 applied to the outer create-review-revise loop.
    """
    branches = saga.get("branches", {})
    if not branches:
        return  # nothing to reconcile

    transitions = saga.setdefault("transitions", [])
    seen_branch_transitions: set[tuple[str, str]] = {
        (t["scope"], t["to"]) for t in transitions if t.get("scope", "").startswith("branch:")
    }

    for lens, branch in branches.items():
        scope = f"branch:{lens}"
        status = branch.get("status", "BRANCH_RUNNING")
        # Backfill FANOUT_STARTED -> BRANCH_RUNNING if missing
        if (scope, "BRANCH_RUNNING") not in seen_branch_transitions:
            transitions.append(
                {
                    "ts": branch.get("started_at") or _utc_now_iso(),
                    "from": "FANOUT_STARTED",
                    "to": "BRANCH_RUNNING",
                    "scope": scope,
                    "reconciled": True,
                }
            )
        # Backfill BRANCH_RUNNING -> <terminal> if missing
        if status != "BRANCH_RUNNING" and (scope, status) not in seen_branch_transitions:
            transitions.append(
                {
                    "ts": branch.get("ended_at") or _utc_now_iso(),
                    "from": "BRANCH_RUNNING",
                    "to": status,
                    "scope": scope,
                    "reconciled": True,
                }
            )

    # Walk run-level status from FANOUT_STARTED through to BRANCH_COMPLETED
    # via the allowed-transition graph, but only when every crew branch
    # has reached a terminal state AND at least one branch completed successfully.
    # If all branches failed (or none completed), do not advance to BRANCH_COMPLETED (#469).
    terminal_branch_states = {"BRANCH_COMPLETED", "BRANCH_FAILED"}
    all_branches_terminal = bool(branches) and all(
        b.get("status") in terminal_branch_states for b in branches.values()
    )
    any_branch_completed = any(b.get("status") == "BRANCH_COMPLETED" for b in branches.values())
    if all_branches_terminal and any_branch_completed and saga["status"] == "FANOUT_STARTED":
        append_transition(saga, from_state="FANOUT_STARTED", to_state="BRANCH_RUNNING", scope="run")
        saga["status"] = "BRANCH_RUNNING"
        append_transition(
            saga, from_state="BRANCH_RUNNING", to_state="BRANCH_COMPLETED", scope="run"
        )
        saga["status"] = "BRANCH_COMPLETED"
    saga["updated_at"] = _utc_now_iso()


def _meets_threshold(ctx: SagaContext, score: int | float | None | object) -> bool:
    """Whether a PASS verdict clears the caller's `--threshold` gate.

    `None` (no score reported) is **not** gated — see `read_verdict_score` for
    why CHG depends on that. `SCORE_UNUSABLE` (a score reported but
    unreadable) **fails** the gate: an unreadable score is a broken audit, and
    failing closed is the only safe reading of one.
    """
    if score is None:
        return True
    if score is SCORE_UNUSABLE:
        return False
    return score >= ctx.threshold


def _advance_after_phase(ctx: SagaContext, saga: dict, phase: str) -> None:
    """Apply the state-machine transition for a completed phase + decide
    next phase based on verdict.json (for review/re-review phases)."""
    if phase == "draft":
        current_st = saga.get("status", "PREPARED")
        append_transition(saga, from_state=current_st, to_state="FANOUT_STARTED")
        saga["status"] = "FANOUT_STARTED"
        saga["current_phase"] = "review"
    elif phase in ("review", "re-review"):
        validate_and_repair_branches(ctx, saga)
        reconcile_post_audit(ctx, saga)

        score, status = read_verdict_score(ctx)
        if status == "MISSING":
            # B7-class fix (extended; 2026-06-07 Phase 4 PRD verification).
            # Per spec _ALLOWED_TRANSITIONS, ESCALATED is reachable only from
            # BRANCH_FAILED or BRANCH_COMPENSATING. At MISSING-verdict time the
            # saga is typically still at FANOUT_STARTED (audit ran but did
            # not fan out / write verdict.json — e.g., legacy single-pass
            # audit subprocess that hasn't been team-mode-wired yet). From
            # FANOUT_STARTED, ESCALATED is illegal; PARTIAL_TIMEOUT is the
            # non-CLOSED terminal that carries the right semantics
            # ("resumable; needs human review / team-mode wiring for this
            # layer") for the harness B2 assertion.
            #
            # PARTIAL_TIMEOUT is NOT reachable from every non-terminal state —
            # BRANCH_FAILED, BRANCH_COMPENSATING and SYNTHESIZED cannot reach
            # it, and this branch runs after reconcile_post_audit, which can
            # leave the saga in any of them. Hence forced=True: without it the
            # recovery path itself raises and wedges the saga permanently
            # (PLUGIN-PREPROD-001 B3a).
            saga["compensation_actions"].append(
                {
                    "ts": _utc_now_iso(),
                    "branch": "*",
                    "reason": (
                        f"audit phase '{phase}' returned but verdict.json absent "
                        f"(audit SKILL may not be team-mode-wired for layer "
                        f"{ctx.layer})"
                    ),
                    "action": "partial_timeout",
                }
            )
            _force_partial_timeout(saga)
            return

        if status == "PASS" and not _meets_threshold(ctx, score):
            # L2: --threshold was accepted and ignored. A PASS whose reported
            # content_score is below the caller's gate is not a pass; fall
            # through to the fixer/cap branch below.
            print(
                f"verdict PASS but content_score {score} < threshold "
                f"{ctx.threshold}; treating as not converged"
            )
            status = "FAIL"

        if status != "PASS" and saga["status"] in {"CLOSED"} | _FAILURE_TERMINALS:
            # The audit subprocess left the saga terminal, but the verdict
            # says this run did not converge. Without this, the fixer branch
            # below would set current_phase on a CLOSED saga, main's loop
            # guard would see a terminal status, and the run would exit 0 —
            # the gate firing and the run reporting success in one breath.
            _force_partial_timeout(saga)
            return

        if status == "PASS":
            # Walk run-scope state to CLOSED. The audit subprocess's
            # synthesizer typically advances status to FANIN_REDUCED via
            # its own saga-interaction code path (B6 verification
            # 2026-06-05 confirmed this), so we may already be partway
            # along the chain. Append only the transitions still needed
            # to reach CLOSED — appending a no-op (e.g. FANIN_REDUCED ->
            # FANIN_REDUCED) would raise ValueError.
            #
            # The entry state is whatever the audit subprocess left on disk
            # (B3b stopped the driver clobbering it), so it need not be one
            # from which FANIN_REDUCED is legal. That inconsistency is NOT
            # absorbed: a PASS arriving on a journal that records no completed
            # fan-in is evidence the audit is broken, not evidence the
            # document is good. Forcing the edge here would walk the saga to
            # CLOSED and exit 0 — e.g. an audit that wrote `status: ESCALATED`
            # and a PASS verdict would have its escalation silently rewritten
            # as success. Surface it as unconverged instead.
            terminal_chain = ("FANIN_REDUCED", "SYNTHESIZED", "CLOSED")
            if saga["status"] not in terminal_chain:
                if not can_transition(current=saga["status"], target="FANIN_REDUCED"):
                    print(
                        f"verdict PASS but saga is at {saga['status']}, from which "
                        f"FANIN_REDUCED is unreachable — the audit reported a pass on a "
                        f"journal recording no completed fan-in. Treating as not "
                        f"converged; inspect {ctx.saga_file}.",
                        file=sys.stderr,
                    )
                    saga["compensation_actions"].append(
                        {
                            "ts": _utc_now_iso(),
                            "branch": "*",
                            "reason": (f"PASS verdict from non-fan-in state {saga['status']}"),
                            "action": "partial_timeout",
                        }
                    )
                    _force_partial_timeout(saga)
                    return
                append_transition(saga, from_state=saga["status"], to_state="FANIN_REDUCED")
                saga["status"] = "FANIN_REDUCED"
            if saga["status"] == "FANIN_REDUCED":
                append_transition(saga, from_state="FANIN_REDUCED", to_state="SYNTHESIZED")
                saga["status"] = "SYNTHESIZED"
            if saga["status"] == "SYNTHESIZED":
                append_transition(saga, from_state="SYNTHESIZED", to_state="CLOSED")
                saga["status"] = "CLOSED"
            saga["current_phase"] = "finalize"
        else:
            if saga["iteration"] < _resolve_max_iterations():
                saga["current_phase"] = "fixer"
            else:
                # B7 (2026-06-05 Amendment 1 verification): per spec
                # _ALLOWED_TRANSITIONS, ESCALATED is reachable only from
                # BRANCH_FAILED or BRANCH_COMPENSATING. At max iterations
                # we're typically at BRANCH_COMPLETED or FANIN_REDUCED
                # (audit completed but verdict FAIL), neither of which
                # allows direct -> ESCALATED. Use PARTIAL_TIMEOUT as the
                # non-CLOSED terminal. Harness treats both as FAIL.
                # Forced for the same reason as the MISSING branch above:
                # PARTIAL_TIMEOUT is not reachable from every non-terminal
                # state, and BRANCH_FAILED is a live entry state here
                # (PLUGIN-PREPROD-001 B3a).
                _force_partial_timeout(saga)
    elif phase == "fixer":
        saga["iteration"] += 1
        saga["current_phase"] = "re-review"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Saga driver for plugin autopilot")
    parser.add_argument("--layer", required=True, help="e.g. 01_BRD")
    parser.add_argument(
        "--artifact-id",
        default=os.environ.get("ARTIFACT_ID"),
        help="e.g. BRD-01; falls back to $ARTIFACT_ID",
    )
    parser.add_argument(
        "--artifact-path",
        default=os.environ.get("ARTIFACT_PATH"),
        help="output path; falls back to $ARTIFACT_PATH",
    )
    parser.add_argument(
        "--seed",
        default=os.environ.get("PREV_OUTPUT"),
        help="upstream seed; falls back to $PREV_OUTPUT",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=90,
        help=(
            "minimum content_score a PASS verdict must report to close the "
            "saga; verdicts that report no score are not gated"
        ),
    )
    parser.add_argument(
        "--plugin-dir",
        default=os.environ.get("CLAUDE_PLUGIN_ROOT", os.environ.get("PLUGIN_DIR", "")),
    )
    parser.add_argument(
        "--allow-skip-permissions",
        action="store_true",
        help=(
            "run each dispatched phase subprocess with "
            "--dangerously-skip-permissions, so it can write files without "
            "prompting. Required for unattended autopilot runs; off by default "
            "because it disables Claude Code's permission prompts for every "
            "subprocess this driver spawns."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    for name in ("artifact_id", "artifact_path", "seed"):
        if not getattr(args, name):
            env_name = "PREV_OUTPUT" if name == "seed" else name.upper()
            parser.error(f"--{name.replace('_', '-')} or ${env_name} required")
    if not args.plugin_dir:
        parser.error("--plugin-dir or $CLAUDE_PLUGIN_ROOT/$PLUGIN_DIR required")

    layer_type = args.layer.split("_", 1)[1]
    project_root = Path(args.artifact_path).parents[2]
    saga_dir = project_root / ".aidoc" / "review" / args.layer / args.artifact_id

    ctx = SagaContext(
        layer=args.layer,
        layer_type=layer_type,
        artifact_id=args.artifact_id,
        artifact_path=Path(args.artifact_path),
        saga_dir=saga_dir,
        saga_file=saga_dir / "saga.json",
        threshold=args.threshold,
        plugin_dir=Path(args.plugin_dir),
        allow_skip_permissions=args.allow_skip_permissions,
    )

    saga = load_or_init_saga(ctx, Path(args.seed))
    resume_from_partial_timeout(saga)
    write_saga(ctx, saga)

    while saga["status"] not in {"CLOSED", "ESCALATED", "PARTIAL_TIMEOUT"}:
        if check_break_circuit(ctx, saga):
            return _exit_code_for_status(saga["status"])

        phase = saga["current_phase"]
        if phase in ("review", "re-review"):
            _invalidate_verdict(ctx, saga["iteration"])
        brief = (
            f"Artifact {args.artifact_id} at {args.artifact_path}; "
            f"seed at {args.seed}; saga at {ctx.saga_file}; "
            f"iteration {saga['iteration']}"
        )
        rc = dispatch_phase(ctx, phase, brief, saga=saga)

        # B6 (2026-06-05 Amendment 1 verification): the dispatched
        # subprocess (audit / fixer / re-audit) writes its own per-branch
        # transitions and updates saga.status directly to saga.json on
        # disk. The driver's in-memory `saga` dict is stale at this
        # point — writing it back would overwrite the subprocess's work.
        # Reload from disk before advancing the state machine.
        if ctx.saga_file.exists():
            saga = json.loads(ctx.saga_file.read_text())

        if rc == 0:
            _advance_after_phase(ctx, saga, phase)
        else:
            # B7 (2026-06-05 Amendment 1 verification): per spec
            # _ALLOWED_TRANSITIONS, ESCALATED is reachable only from
            # BRANCH_FAILED or BRANCH_COMPENSATING. On a subprocess
            # failure (claude API limit, network, timeout, etc.) the
            # saga is usually at PREPARED / FANOUT_STARTED / BRANCH_RUNNING
            # / BRANCH_COMPLETED, none of which allow direct -> ESCALATED.
            # PARTIAL_TIMEOUT connotes "non-CLOSED terminal, resumable on
            # next invocation" — the right semantics for a transient
            # external failure. Harness treats both ESCALATED and
            # PARTIAL_TIMEOUT as FAIL. forced=True because the reloaded
            # status is whatever the subprocess left behind, which may be
            # one of the three states PARTIAL_TIMEOUT is not reachable
            # from (PLUGIN-PREPROD-001 B3a).
            reason = f"phase {phase} subprocess exit {rc}"
            if rc == EXIT_SPAWN_FAILED:
                reason = f"phase {phase} subprocess could not be spawned"
            elif rc == 124 and not ctx.allow_skip_permissions:
                # A phase that ran to the full deadline with the permission
                # bypass off is far more likely to have been sitting on an
                # unanswerable prompt than to have been slow.
                reason += " (permission prompts are on; --allow-skip-permissions was not passed)"
            saga["compensation_actions"].append(
                {
                    "ts": _utc_now_iso(),
                    "branch": "*",
                    "reason": reason,
                    "action": "partial_timeout",
                }
            )
            _force_partial_timeout(saga)

            if rc == EXIT_SPAWN_FAILED:
                # An environment defect, not a resumable deadline. Reporting
                # it through EXIT_PARTIAL_TIMEOUT would tell the operator the
                # run can simply be retried, and every retry would fail
                # identically.
                print(
                    f"phase {phase} could not be spawned — this is an environment "
                    f"defect, not a resumable timeout. Verify `claude` is on PATH.",
                    file=sys.stderr,
                )
                write_saga(ctx, saga)
                return EXIT_SPAWN_FAILED

        write_saga(ctx, saga)

    print(
        f"saga {saga['status']} for {ctx.artifact_id} "
        f"(iteration {saga['iteration']}, "
        f"{len(saga['transitions'])} transitions)"
    )
    return _exit_code_for_status(saga["status"])


if __name__ == "__main__":
    sys.exit(main())
