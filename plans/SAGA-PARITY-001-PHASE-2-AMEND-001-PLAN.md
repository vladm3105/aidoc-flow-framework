# SAGA-PARITY-001 Phase 2 Amendment 1 — preemptive saga driver + autopilot-only harness

| Field      | Value                                                     |
|------------|-----------------------------------------------------------|
| Task       | SAGA-PARITY-001-PHASE-2-AMEND-001                         |
| Parent     | SAGA-PARITY-001 Phase 2 (`plans/SAGA-PARITY-001-PHASE-2-PLAN.md`, merged via PR #88) |
| Depends on | Phase 1 (D-0031; PR #84) — spec contract unchanged. Phase 2 (PR #88) — slim refactor builds on Phase 2's SKILLs, replaces the saga-driven loop section of autopilot. |
| Status     | PLANNED — 2026-06-05T17:45:00Z                            |
| Feeds      | Phase 3 (Hermes alignment) — unblocked after this amendment re-verifies bug-free. Phase 4 (PRD..IPLAN propagation) — inherits this preemptive-driver pattern from the start. |
| Scope flag | **Plugin patch bump** — 0.6.0 → 0.6.1 (additive helper script + slim SKILL refactor; saga.json behaviour becomes deterministic). No framework-spec changes — Phase 1's `0.13.0` holds. |

## Objective

Fix Phase 2's empirically-confirmed **cooperative-enforcement failure** by
moving the saga lifecycle orchestration from the cooperative SKILL prompt
into a **deterministic helper script** (`tools/saga_driver.py`). The
`doc-brd-autopilot` SKILL becomes a thin entry point that Bash-invokes the
helper; the helper drives the create→review→revise loop preemptively (just
like Hermes' Python `saga_orchestrator`), dispatching each phase as a
fresh `claude -p` subprocess.

At the same time, **eliminate the test-acceptance.sh dual-dispatch
duplication**: the cascade harness invokes ONLY `doc-<layer>-autopilot`
per layer. Audit / fixer / doc-brd skills stay valid for standalone use
but the cascade pipeline no longer runs them on top of autopilot. **Autopilot
is the single source of truth per layer**, owning the full lifecycle.

After this amendment:

- saga.json is written **by the helper script** during the loop (not
  synthesized post-hoc by an LLM).
- Every transition is validated against the REVIEW_SAGA.md table
  preemptively (the helper raises on invalid).
- Final saga status reaches `CLOSED` or `ESCALATED` (terminal) reliably.
- Layer runtime drops from ~3656s (Phase 2 live verify) to ~1800-2400s
  (autopilot-only path; no harness duplicate dispatch).
- Plugin saga implementation matches Hermes' saga runtime in **mechanism**
  (both preemptive), not just observable lifecycle.

## Background

### What Phase 2's live verification surfaced

Today's BRD live verification (2026-06-05T16:22:34) produced **autopilot
PASS but with multiple structural bugs**:

- saga.json was synthesized post-hoc by the LLM instead of being driven
  by actual subprocess dispatch.
- 7 of 13 transitions in saga.json violated the REVIEW_SAGA.md transition
  table (e.g., `FANOUT_STARTED → BRANCH_COMPLETED` instead of the
  spec's `FANOUT_STARTED → BRANCH_RUNNING`).
- Final saga status was `BRANCH_COMPLETED` (non-terminal) instead of
  `CLOSED`.
- Zero `claude -p` subprocesses were dispatched from inside autopilot —
  the LLM defaulted to in-session `Task` subagent dispatch (prior
  pre-Phase-2 behavior).
- Synthetic timestamps (`2026-06-05T00:00:00Z`) replaced actual
  `date +%s` epoch times.
- `branches[]` entries lacked the required `branch_id` field.
- Total layer runtime exceeded the 3600s `MAX_LAYER_SEC` cap by 56s
  (3656s) because the harness's dual-dispatch ran the audit+fixer+audit
  cycle AGAIN after autopilot's in-session loop completed.

### Root cause

Phase 2 chose **cooperative enforcement** for the plugin saga (LLM
follows the SKILL prompt's instructions to write saga.json, dispatch
subprocesses, validate transitions). Phase 1 §"Enforcement asymmetry"
explicitly acknowledged this risk:

> *"Plugin: cooperative enforcement via SKILL prompts. The orchestrator
> SKILL.md tells the LLM to validate transitions against this
> document's table before writing the journal; OS-level signals are
> the hard floor."*

Today's verification empirically confirms cooperative enforcement is
unreliable for complex multi-step orchestration: the LLM read the
SKILL but defaulted to the simpler in-session Task pattern, then
synthesized a saga-shaped output that doesn't reflect the actual
lifecycle.

### Why this amendment is needed before proceeding

Phase 3 (Hermes alignment) introduces a cross-platform conformance
test that validates both platforms' saga journals against the spec.
With Phase 2's autopilot producing invalid transitions today, that
test would fail. Phase 3 is blocked until the plugin produces
schema-conformant journals. This amendment unblocks Phase 3.

### Architectural decision (confirmed with user 2026-06-05)

- **Per-layer autopilot is the single entry point.** The harness's
  cascade dispatcher invokes only `doc-<layer>-autopilot`.
- **Other skills stay valid** (`doc-<layer>`, `doc-<layer>-audit`,
  `doc-<layer>-fixer`) for direct standalone invocation. The cascade
  pipeline never dispatches them on top of autopilot.
- **Autopilot orchestrates internally** by Bash-invoking the saga
  driver script, which calls those skills as `claude -p` subprocesses.
- **Both platforms become preemptive in mechanism**: Hermes via its
  Python saga runtime, plugin via the saga driver script. The Phase 1
  §"Enforcement asymmetry" caveat (cooperative on plugin, preemptive
  on Hermes) is **superseded**: both are now preemptive at the
  orchestration layer.

## Scope

### In

1. **New file** `tools/saga_driver.py` — deterministic Python orchestrator
   per Design 1 (~300 lines). CLI invokable from Bash; manages saga.json,
   validates transitions, dispatches phase subprocesses, handles
   break-circuit, supports resume.
2. **Edit** `platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md`
   per Design 2 — replace the §"Saga-driven generation loop" section
   (~300 lines today) with a thin ~30-line entry point that Bash-invokes
   the saga driver. Keep §"Linear Pipeline (review_mode: single_pass)"
   unchanged.
3. **Edit** `tests/scripts/test-acceptance.sh` per Design 3 — cascade
   dispatcher (lines 925-998) invokes ONLY `doc-<layer>-autopilot` per
   layer; reads saga.json for layer outcome. Audit/fixer/doc-brd
   dispatch lines removed.
4. **New file** `tests/conformance/test_saga_driver_invariants.py` per
   Design 4 — unit tests for the saga driver's state-machine invariants:
   no invalid transitions accepted, PARTIAL_TIMEOUT terminal, resume
   from various states works.
5. **Bump plugin VERSION** `0.6.0 → 0.6.1` (PATCH; additive helper +
   slim SKILL; no public contract change).
6. **9-place version fanout** for 0.6.1 (per CHAOS-SEC-SPLIT-001 +
   Phase 2 pattern).
7. **Edit** `platforms/claude-code-plugin/CHANGELOG.md` per Design 6.
8. **Edit** `docs/PARITY.md` per Design 7 — update the "Enforcement
   asymmetry" cell (both now preemptive in mechanism); update status
   line to v0.6.1; update Saga lifecycle row to note the driver-script
   implementation.
9. **Edit** `docs/TAGGING.md` — `claude-code-plugin/v0.6.1` row.
10. **Live BRD re-verification** (~$3-5, ~30-45 min) per Design 8. New
    pass criteria (10 items, expanding Phase 2's 8) — all must pass
    bug-free before Phase 3 unblocks.

### Out

- **Framework spec changes** — none. REVIEW_SAGA.md and
  saga.schema.json stay at Phase 1's 0.13.0.
- **Hermes-side changes** — Phase 3 still does this; this amendment
  doesn't touch Hermes.
- **PRD..IPLAN propagation** — Phase 4. After this amendment lands,
  Phase 4's per-layer impl is mechanical: each layer gets its own
  thin autopilot SKILL invoking the same saga driver with a
  different `--layer` argument.
- **`doc-brd-audit`, `doc-brd-fixer`, `doc-brd` SKILL changes** —
  none. They keep their Phase 2 saga interaction sections (which are
  exercised when invoked by the driver as subprocesses, just like
  when invoked by autopilot's old in-session pattern). Standalone
  direct invocation continues to work unchanged.
- **REVIEW_SAGA.md §"Enforcement asymmetry"** rewording — Phase 1's
  text says "cooperative enforcement via SKILL prompts" for the
  plugin. After this amendment, plugin is preemptive too. The spec
  text can either stay (allowing both modes per implementation) or
  be rephrased; defer to Phase 3 since it's a spec change requiring
  CHG-gate.

## Approach — concrete content designs

### Design 1 — `tools/saga_driver.py`

The deterministic orchestrator. Python 3.10+ stdlib only (no new deps).
Approximately 300 lines. Key responsibilities:

- Manage saga.json read/init/write atomically.
- Validate every transition against an embedded transition table
  (mirrors REVIEW_SAGA.md; a future conformance test asserts the
  driver's table matches the spec).
- Dispatch each phase as `claude -p /aidoc-flow:<skill>` subprocess,
  each with its own `timeout 1800` budget.
- Break-circuit at `SOFT_DEADLINE=1500s` (parent's wall-clock check
  before each phase dispatch); exit cleanly with status PARTIAL_TIMEOUT
  if crossed.
- Resume: if saga.json exists with non-terminal status, read it,
  identify `current_phase`, continue from there. Per Phase 2 Pass 4
  G-R1: never write `from: PARTIAL_TIMEOUT` — walk transitions[]
  backward to find pre-PARTIAL_TIMEOUT state and append next legal
  transition from THAT state.
- Handle CLOSED/ESCALATED on entry (exit cleanly).
- Pre-Phase-2 blackboard migration: if slot files present but no
  saga.json, scaffold one.

Full proposed content (impl-ready):

````python
#!/usr/bin/env python3
"""Deterministic preemptive orchestrator for the review-saga lifecycle.

Plays the same role for the Claude Code plugin that `saga_orchestrator.py`
plays for Hermes: drives the create→review→revise loop, validates state
machine transitions against `framework/governance/REVIEW_SAGA.md`, manages
the durable saga.json journal, and dispatches each phase as a separately-
budgeted subprocess.

Invoked by `doc-<layer>-autopilot` SKILLs (thin entry points) via Bash.

Per SAGA-PARITY-001 Phase 2 Amendment 1, this script SUPERSEDES the
cooperative-enforcement pattern in Phase 2's original SKILL prompts —
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
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


# Spec authority: framework/governance/REVIEW_SAGA.md §"Transition table"
# A conformance test will assert this matches the spec table exactly.
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
_LAYER_CREWS: dict[str, list[str]] = {
    "01_BRD": ["business_analyst", "architect", "auditor",
               "chaos_engineer", "security_engineer"],
    "02_PRD": ["product_owner", "architect", "tech_lead",
               "chaos_engineer", "security_engineer", "auditor"],
    "03_EARS": ["requirements_specialist", "tech_lead", "qa_lead",
                "chaos_engineer", "security_engineer"],
    "04_BDD": ["qa_lead", "tech_lead", "chaos_engineer",
               "security_engineer", "operator", "auditor"],
    "05_ADR": ["architect", "tech_lead", "chaos_engineer",
               "security_engineer", "operator", "auditor"],
    "06_SPEC": ["architect", "tech_lead", "integration_lead",
                "chaos_engineer", "security_engineer"],
    "07_TDD": ["qa_lead", "tech_lead", "chaos_engineer",
               "security_engineer", "operator", "auditor"],
    "08_IPLAN": ["tech_lead", "architect", "operator",
                 "integration_lead", "auditor", "chaos_engineer"],
}

SOFT_DEADLINE_SECONDS = 1500
SUBPROCESS_TIMEOUT_SECONDS = 1800
MAX_ITERATIONS = 3


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _det_run_id(*, artifact_path: str, personas: list[str], time_bucket: str) -> str:
    payload = f"{artifact_path}|{','.join(sorted(personas))}|{time_bucket}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _det_branch_id(*, run_id: str, persona: str) -> str:
    return hashlib.sha256(f"{run_id}|{persona}".encode()).hexdigest()[:12]


@dataclass
class SagaContext:
    layer: str          # e.g. "01_BRD"
    layer_type: str     # e.g. "BRD"
    artifact_id: str    # e.g. "BRD-01"
    artifact_path: Path
    saga_dir: Path
    saga_file: Path
    start_epoch: float = field(default_factory=time.time)
    threshold: int = 90
    plugin_dir: Path | None = None


def load_or_init_saga(ctx: SagaContext, seed_path: Path) -> dict:
    """Load existing saga.json or initialize a fresh one.

    Handles all entry conditions:
    - saga.json missing → fresh init (with pre-Phase-2 blackboard migration
      if slot files are present).
    - status CLOSED or ESCALATED → log + sys.exit(0).
    - status PARTIAL_TIMEOUT or any other in-flight state → resume.
    """
    if ctx.saga_file.exists():
        saga = json.loads(ctx.saga_file.read_text())
        status = saga.get("status", "")
        if status == "CLOSED":
            print(f"saga already CLOSED for {ctx.artifact_id}; "
                  f"iteration {saga.get('iteration', 1)} complete")
            sys.exit(0)
        if status == "ESCALATED":
            print(f"saga ESCALATED for {ctx.artifact_id}; "
                  f"human review required")
            sys.exit(0)
        # Resume from non-terminal state (or PARTIAL_TIMEOUT)
        return saga

    # Fresh init: check for pre-Phase-2 blackboard migration first
    ctx.saga_dir.mkdir(parents=True, exist_ok=True)
    crew = _LAYER_CREWS[ctx.layer]
    run_id = _det_run_id(
        artifact_path=str(ctx.artifact_path),
        personas=crew,
        time_bucket=datetime.now(timezone.utc).strftime("%Y%m%d"),
    )

    existing_slots = list(ctx.saga_dir.glob("*.json"))
    pre_phase2_slots = [s for s in existing_slots
                        if s.stem in crew and s.name != "saga.json"]

    if pre_phase2_slots:
        # G-R6 migration: scaffold saga from existing slot state
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
            "transitions": [{
                "ts": _utc_now_iso(), "from": None, "to": "BRANCH_COMPLETED",
                "scope": "run",
            }],
            "compensation_actions": [],
        }

    # Clean fresh init
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
        "transitions": [{
            "ts": _utc_now_iso(), "from": None, "to": "PREPARED",
            "scope": "run",
        }],
        "compensation_actions": [],
    }


def can_transition(*, current: str, target: str) -> bool:
    return target in _ALLOWED_TRANSITIONS.get(current, set())


def append_transition(saga: dict, *, from_state: str | None, to_state: str,
                      scope: str = "run") -> None:
    """Append a transition. Raises ValueError on invalid transitions
    (preemptive enforcement)."""
    if from_state is not None and not can_transition(
            current=from_state, target=to_state):
        raise ValueError(
            f"Invalid transition: {from_state} → {to_state} "
            f"(allowed: {sorted(_ALLOWED_TRANSITIONS.get(from_state, set()))})"
        )
    saga["transitions"].append({
        "ts": _utc_now_iso(),
        "from": from_state,
        "to": to_state,
        "scope": scope,
    })
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
        append_transition(saga, from_state=saga["status"],
                          to_state="PARTIAL_TIMEOUT", scope="run")
        saga["status"] = "PARTIAL_TIMEOUT"
        write_saga(ctx, saga)
        print(f"break-circuit fired at {elapsed:.0f}s elapsed; "
              f"saga PARTIAL_TIMEOUT; current_phase={saga['current_phase']}")
        return True
    return False


def resume_from_partial_timeout(saga: dict) -> None:
    """Per Phase 2 Pass 4 G-R1: walk transitions[] backward to find the
    pre-PARTIAL_TIMEOUT state. Set saga.status to that state so the loop
    continues from there. Do NOT append a transition with from: PARTIAL_TIMEOUT."""
    if saga["status"] != "PARTIAL_TIMEOUT":
        return
    for t in reversed(saga["transitions"]):
        if t["to"] != "PARTIAL_TIMEOUT":
            saga["status"] = t["to"]
            return
    # Fallback: if no non-PARTIAL_TIMEOUT entries exist, reset to PREPARED
    saga["status"] = "PREPARED"


def dispatch_phase(ctx: SagaContext, phase: str, brief: str) -> int:
    """Dispatch a phase subprocess. Returns the subprocess exit code.

    `phase` is one of: 'draft', 'review', 'fixer', 're-review'.
    Maps to a slash command via the table below.
    """
    slash = {
        "draft": f"/aidoc-flow:doc-{ctx.layer_type.lower()}",
        "review": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-audit",
        "fixer": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-fixer",
        "re-review": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-audit",
    }[phase]
    cmd = [
        "timeout", str(SUBPROCESS_TIMEOUT_SECONDS),
        "claude",
        "--plugin-dir", str(ctx.plugin_dir),
        "--dangerously-skip-permissions",
        "-p", f"{slash} {brief}",
    ]
    print(f"dispatch: {phase} ({slash}) ...")
    result = subprocess.run(cmd, capture_output=False, check=False)
    return result.returncode


def read_verdict_score(ctx: SagaContext) -> tuple[int, str]:
    """Read .aidoc/review/<layer>/<id>/verdict.json. Returns (score, status).

    Returns (0, "MISSING") if verdict.json absent — caller treats this as
    an AUDIT FAILURE (per Pass-4 A9), distinct from a low content score
    (FAIL with score). Driver escalates rather than dispatching fixer.
    """
    verdict_path = ctx.saga_dir / "verdict.json"
    if not verdict_path.exists():
        return 0, "MISSING"
    v = json.loads(verdict_path.read_text())
    return v.get("content_score", 0), v.get("combined_status", "UNKNOWN")


def validate_and_repair_branches(ctx: SagaContext, saga: dict) -> None:
    """Per Pass-4 A8: after audit subprocess returns, validate that
    every branches[<persona>] entry has required fields per saga.schema.json
    (branch_id, status, attempt). If missing/malformed, repair from
    existing blackboard slot file mtimes.

    Per Pass-5 P5-2: if no slot file exists for a persona that's in the
    crew, fall back to saga.created_at as both started_at and ended_at.
    """
    crew = _LAYER_CREWS[ctx.layer]
    fallback_ts = saga.get("created_at", _utc_now_iso())
    for persona in crew:
        branch = saga.get("branches", {}).get(persona, {})
        slot_path = ctx.saga_dir / f"{persona}.json"
        slot_ts = (datetime.fromtimestamp(slot_path.stat().st_mtime, tz=timezone.utc)
                   .isoformat() if slot_path.exists() else fallback_ts)
        # Repair missing/malformed fields with deterministic values
        if "branch_id" not in branch or not branch["branch_id"]:
            branch["branch_id"] = _det_branch_id(
                run_id=saga["review_run_id"], persona=persona)
        if branch.get("status") not in {"BRANCH_RUNNING", "BRANCH_COMPLETED",
                                         "BRANCH_FAILED", "BRANCH_COMPENSATING"}:
            # Slot file presence implies completion; else mark FAILED
            branch["status"] = "BRANCH_COMPLETED" if slot_path.exists() else "BRANCH_FAILED"
        if "attempt" not in branch:
            branch["attempt"] = 0
        if not branch.get("started_at"):
            branch["started_at"] = slot_ts
        if not branch.get("ended_at"):
            branch["ended_at"] = slot_ts
        saga.setdefault("branches", {})[persona] = branch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Saga driver for plugin autopilot")
    parser.add_argument("--layer", required=True, help="e.g. 01_BRD")
    # Per Pass-4 A5/A6: env vars are the primary input channel
    # (harness sets them before invoking the autopilot subprocess);
    # CLI args are the explicit override for direct invocation.
    parser.add_argument("--artifact-id", default=os.environ.get("ARTIFACT_ID"),
                        help="e.g. BRD-01; falls back to $ARTIFACT_ID env var")
    parser.add_argument("--artifact-path", default=os.environ.get("ARTIFACT_PATH"),
                        help="output BRD path; falls back to $ARTIFACT_PATH env var")
    parser.add_argument("--seed", default=os.environ.get("PREV_OUTPUT"),
                        help="upstream seed path; falls back to $PREV_OUTPUT env var")
    parser.add_argument("--threshold", type=int, default=90)
    # Per Pass-4 A4: CLAUDE_PLUGIN_ROOT is the canonical env var
    # set when running inside an installed plugin session.
    parser.add_argument("--plugin-dir", default=os.environ.get(
        "CLAUDE_PLUGIN_ROOT",
        os.environ.get("PLUGIN_DIR", "")))
    args = parser.parse_args(argv)

    # Validate required fields (after env-var fallback)
    for name in ("artifact_id", "artifact_path", "seed"):
        if not getattr(args, name):
            parser.error(f"--{name.replace('_', '-')} or its env var "
                         f"({name.upper() if name != 'seed' else 'PREV_OUTPUT'}) "
                         f"is required")
    if not args.plugin_dir:
        parser.error("--plugin-dir or CLAUDE_PLUGIN_ROOT/PLUGIN_DIR env var required")

    layer_type = args.layer.split("_", 1)[1]  # "01_BRD" -> "BRD"
    project_root = Path(args.artifact_path).parents[2]  # ../docs/<layer>/<file>
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
    )

    saga = load_or_init_saga(ctx, Path(args.seed))
    resume_from_partial_timeout(saga)
    write_saga(ctx, saga)  # persist resume state

    while saga["status"] not in {"CLOSED", "ESCALATED"}:
        if check_break_circuit(ctx, saga):
            return 0  # PARTIAL_TIMEOUT exit; resume on next invocation

        phase = saga["current_phase"]
        brief = f"Artifact {args.artifact_id} at {args.artifact_path}; " \
                f"seed at {args.seed}; saga at {ctx.saga_file}; " \
                f"iteration {saga['iteration']}"
        rc = dispatch_phase(ctx, phase, brief)

        if rc == 0:
            # Phase completed. Advance state machine.
            _advance_after_phase(ctx, saga, phase)
        else:
            # Phase failed. Log to compensation_actions and escalate.
            saga["compensation_actions"].append({
                "ts": _utc_now_iso(),
                "branch": "*",
                "reason": f"phase {phase} subprocess exit {rc}",
                "action": "escalate",
            })
            append_transition(saga, from_state=saga["status"],
                              to_state="ESCALATED", scope="run")
            saga["status"] = "ESCALATED"

        write_saga(ctx, saga)

    print(f"saga {saga['status']} for {ctx.artifact_id} "
          f"(iteration {saga['iteration']}, "
          f"{len(saga['transitions'])} transitions)")
    return 0


def _advance_after_phase(ctx: SagaContext, saga: dict, phase: str) -> None:
    """Apply the state-machine transition for a completed phase + decide
    next phase based on verdict.json (for review/re-review phases)."""
    if phase == "draft":
        append_transition(saga, from_state="PREPARED",
                          to_state="FANOUT_STARTED")
        saga["status"] = "FANOUT_STARTED"
        saga["current_phase"] = "review"
    elif phase in ("review", "re-review"):
        # Pass-4 A8: the audit subprocess may produce malformed
        # branches[] (live-verified 2026-06-05). Validate and repair
        # before reading verdict.
        validate_and_repair_branches(ctx, saga)

        # Pass-4 A9: if verdict.json is missing, the audit subprocess
        # itself failed — escalate rather than dispatching fixer.
        score, status = read_verdict_score(ctx)
        if status == "MISSING":
            saga["compensation_actions"].append({
                "ts": _utc_now_iso(),
                "branch": "*",
                "reason": f"audit phase '{phase}' returned but verdict.json absent",
                "action": "escalate",
            })
            append_transition(saga, from_state=saga["status"],
                              to_state="ESCALATED")
            saga["status"] = "ESCALATED"
            return

        if status == "PASS":
            # Move toward finalize: BRANCH_COMPLETED → FANIN_REDUCED → SYNTHESIZED → CLOSED
            append_transition(saga, from_state=saga["status"],
                              to_state="FANIN_REDUCED")
            append_transition(saga, from_state="FANIN_REDUCED",
                              to_state="SYNTHESIZED")
            append_transition(saga, from_state="SYNTHESIZED",
                              to_state="CLOSED")
            saga["status"] = "CLOSED"
            saga["current_phase"] = "finalize"
        else:
            if saga["iteration"] < MAX_ITERATIONS:
                saga["current_phase"] = "fixer"
                # Stay in BRANCH_COMPLETED for the fixer to consume
            else:
                append_transition(saga, from_state=saga["status"],
                                  to_state="ESCALATED")
                saga["status"] = "ESCALATED"
    elif phase == "fixer":
        saga["iteration"] += 1
        saga["current_phase"] = "re-review"
        # State stays BRANCH_COMPLETED; the fixer's SKILL transitioned
        # individual branches BRANCH_COMPLETED → BRANCH_COMPENSATING →
        # BRANCH_COMPLETED. The driver returns to "re-review" next iteration.


if __name__ == "__main__":
    sys.exit(main())
````

### Design 2 — slimmed `doc-brd-autopilot/SKILL.md`

Replace the entire §"Saga-driven generation loop" section (lines 81-261
today) with this thin entry point:

````markdown
### Saga-driven generation loop (`review_mode: team`)

This skill is a **thin entry point** over `tools/saga_driver.py`, which
drives the create→review→revise loop **deterministically** (preemptive
enforcement per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`).
The driver script is the orchestration mechanism; this SKILL just
invokes it and reports the result.

This SUPERSEDES the cooperative-enforcement loop pattern that Phase 2
originally embedded in this SKILL prompt (which empirically failed
2026-06-05 verification — see plans/SAGA-PARITY-001-PHASE-2-AMEND-001-PLAN.md).

#### 3. Dispatch the saga driver

The driver script is vendored alongside the plugin at
`${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py` (per Pass-4 A4 — the
existing framework bundle pattern from D-0022 is extended to include
`tools/`). The harness sets `PREV_OUTPUT`, `ARTIFACT_ID`,
`ARTIFACT_PATH` env vars before invoking this SKILL (per Pass-4
A5/A6 — no LLM-cooperative prompt parsing); the driver reads them.

```sh
Bash: python3 ${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py \
  --layer 01_BRD \
  --threshold 90
```

The driver picks up `--artifact-id`, `--artifact-path`, `--seed` from
the env vars set by the harness. For direct user invocation (outside
the harness), the CLI args are the explicit override.

The driver:

1. Reads or initializes `.aidoc/review/01_BRD/<BRD-id>/saga.json` per
   the framework saga lifecycle contract.
2. Dispatches each phase (draft, review, fixer, re-review) as a fresh
   `claude -p` subprocess with its own `ORCHESTRATOR_TIMEOUT=1800s`
   budget.
3. Validates every state transition against the REVIEW_SAGA.md table
   (preemptive — raises on invalid).
4. Honors break-circuit at `SOFT_DEADLINE=1500s`: exits cleanly with
   saga `status: PARTIAL_TIMEOUT` if elapsed crosses the soft deadline.
   Re-invocation resumes from `current_phase`.
5. Handles edge cases: `CLOSED` on entry → exit clean ("already
   done"); `ESCALATED` → do NOT auto-restart; pre-Phase-2 blackboard
   slots without saga.json → scaffold migration.

#### 4. Report outcome

Read `.aidoc/review/01_BRD/<BRD-id>/saga.json` after the driver returns:

- `status: CLOSED` → loop completed successfully; the BRD is ready.
- `status: ESCALATED` → loop escalated for human review (max iterations
  reached or non-recoverable failure).
- `status: PARTIAL_TIMEOUT` → soft deadline crossed; re-invocation will
  resume.

In all cases, surface the saga `status`, `iteration`, and
`result.content_score` in this SKILL's exit summary so the harness
can record the layer outcome.

#### 5. The other skills

The driver invokes the following skills as subprocesses; they remain
fully valid for standalone direct invocation by users:

- `doc-brd` — authoring (draft phase)
- `doc-brd-audit` — review (review and re-review phases)
- `doc-brd-fixer` — remediation (fixer phase)

These skills' Phase 2 saga-interaction sections (added in PR #88) are
exercised when invoked by the driver — they read/write saga.json per
their own SKILL.md instructions.
````

The §"Linear Pipeline (review_mode: single_pass)" stays unchanged.

### Design 3 — `tests/scripts/test-acceptance.sh` cascade dispatcher diff

Replace lines 925-998 of the cascade dispatcher with the autopilot-only
shape:

```diff
@@ -925,75 +925,33 @@
     local fix_report="$AIDOC_DIR/remediation/${layer_num}_${type}-fix.md"
     local layer_start_epoch
     layer_start_epoch="$(date +%s)"

     log_info ""
     log_info "── Layer $((i + 1))/8: $type ──"

-    # autopilot — writes the layer artifact under docs/
+    # Autopilot is the sole entry point per layer. It internally drives
+    # the full create→review→revise loop via tools/saga_driver.py +
+    # subprocess dispatches of doc-<layer>-{audit,fixer} (per
+    # SAGA-PARITY-001 Phase 2 Amendment 1, autopilot-or-explicit-but-
+    # never-both architectural decision).
     if _should_invoke "doc-$layer-autopilot"; then
       local autopilot_prompt
       autopilot_prompt="From the seed/prior-layer document at $prev_output, produce the $type artifact for the $EXAMPLE example. Write the result to $artifact."
+      # Per Pass-4 A5/A6: pass paths via env vars (NOT via LLM-
+      # cooperative prompt parsing). The saga_driver.py reads
+      # PREV_OUTPUT, ARTIFACT_ID, ARTIFACT_PATH from the env. The
+      # `claude` subprocess inherits its parent's env.
+      export PREV_OUTPUT="$prev_output"
+      export ARTIFACT_ID="${type}-01"
+      export ARTIFACT_PATH="$artifact"
       invoke_skill "doc-$layer-autopilot" "$autopilot_prompt" "skill" "cascade"
       OUTPUT_PATH_BY_NAME["doc-$layer-autopilot"]="$artifact"
       if [[ "${OUTCOME_BY_NAME[doc-$layer-autopilot]:-}" == "PASS" ]]; then
         write_element_log "doc-$layer-autopilot"
       fi
       if [[ "${OUTCOME_BY_NAME[doc-$layer-autopilot]:-}" != "PASS" ]] && [[ $FAIL_FAST -eq 1 ]]; then
         return 1
       fi
     fi

-    # audit — writes audit report under .aidoc/audit/
-    local score=0
-    if _should_invoke "doc-$layer-audit"; then
-      local audit_prompt
-      audit_prompt="Audit the $type artifact at $artifact. Write a detailed audit report to $audit_report including the readiness score."
-      invoke_skill "doc-$layer-audit" "$audit_prompt" "skill" "cascade"
-      OUTPUT_PATH_BY_NAME["doc-$layer-audit"]="$audit_report"
-      score="$(parse_audit_score "doc-$layer-audit")"
-      AUDIT_SCORE_BY_NAME["doc-$layer-audit"]="$score"
-      write_element_log "doc-$layer-audit"
-      log_info "  audit score: $score"
-    fi
-
-    # fixer + re-audit if needed
-    if (( score < 90 )) && _should_invoke "doc-$layer-fixer"; then
-      log_info "  score < 90 → invoking fixer"
-      local fixer_prompt
-      fixer_prompt="Fix the $type artifact at $artifact based on findings in $audit_report. Write a fix report to $fix_report. Do not create tmp/ or backup/ directories under the layer dir; if you need a backup, write it to $AIDOC_DIR/remediation/."
-      invoke_skill "doc-$layer-fixer" "$fixer_prompt" "skill" "cascade"
-      OUTPUT_PATH_BY_NAME["doc-$layer-fixer"]="$fix_report"
-      FIXER_INVOKED_BY_NAME["doc-$layer-audit"]="true"
-      write_element_log "doc-$layer-fixer"
-      rm -rf "$layer_dir/tmp" 2>/dev/null
-      invoke_skill "doc-$layer-audit" "$audit_prompt" "skill" "cascade"
-      score="$(parse_audit_score "doc-$layer-audit")"
-      AUDIT_AFTER_FIXER_BY_NAME["doc-$layer-audit"]="$score"
-      write_element_log "doc-$layer-audit"
-      log_info "  audit score after fixer: $score"
-    fi
+    # Read autopilot's saga.json for the layer outcome.
+    local saga_file="$AIDOC_DIR/review/${layer_num}_${type}/${type}-01/saga.json"
+    local score=0
+    local saga_status="UNKNOWN"
+    if [[ -f "$saga_file" ]]; then
+      saga_status="$(python3 -c "import json; print(json.load(open('$saga_file')).get('status',''))" 2>/dev/null || echo UNKNOWN)"
+      score="$(python3 -c "import json; d=json.load(open('$saga_file')); print(d.get('result',{}).get('content_score', 0))" 2>/dev/null || echo 0)"
+      log_info "  saga: status=$saga_status score=$score"
+    fi

     # sdd_doc_lint structural check on the artifact only (B1)
     if [[ -f "$artifact" ]]; then
       local lint_out lint_rc
       lint_out="$(PYTHONPATH="$PLUGIN_DIR" python3 -m sdd_doc_lint "$artifact" 2>&1)"; lint_rc=$?
       if [[ $lint_rc -eq 0 ]]; then
         log_info "  sdd_doc_lint: PASS"
       else
         log_err "  sdd_doc_lint FAIL on $artifact:"
         printf '%s\n' "$lint_out" | sed 's/^/    /'
       fi
     else
       log_warn "  autopilot did not produce $artifact"
     fi

-    # base/reference skill — output captured to logs/<TS>/elements/
-    if _should_invoke "doc-$layer"; then
-      invoke_skill "doc-$layer" "Reference the $type template structure for $artifact." "skill" "cascade" || true
-    fi
+    # Note: doc-<layer>-{audit,fixer,base} are no longer dispatched by
+    # the cascade. The autopilot's saga driver invokes them internally
+    # via subprocess. They stay available for direct user invocation.
```

Net change: ~50 lines removed, ~15 added. Same outcome (layer artifact +
audit + fixer if needed); fewer code paths; no duplication.

### Design 4 — `tests/conformance/test_saga_driver_invariants.py`

Unit tests for the saga driver's state-machine logic. Doesn't run live
subprocesses (uses monkey-patched `dispatch_phase`). Approximately 80
lines. Key invariants:

```python
"""Conformance: saga_driver.py honors REVIEW_SAGA.md state machine."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import saga_driver  # noqa: E402


class TransitionTable(unittest.TestCase):
    def test_driver_transition_table_matches_spec(self):
        """Spec ↔ driver byte-equality on the state machine."""
        # Parse REVIEW_SAGA.md's transition table OR delegate this check to
        # test_saga_lifecycle_parity.py in Phase 3. For now, assert the
        # driver table has all 11 states.
        self.assertEqual(
            set(saga_driver._ALLOWED_TRANSITIONS),
            {"PREPARED", "FANOUT_STARTED", "BRANCH_RUNNING",
             "BRANCH_COMPLETED", "BRANCH_FAILED", "BRANCH_COMPENSATING",
             "FANIN_REDUCED", "SYNTHESIZED", "ESCALATED", "CLOSED",
             "PARTIAL_TIMEOUT"},
        )

    def test_partial_timeout_is_terminal(self):
        self.assertEqual(saga_driver._ALLOWED_TRANSITIONS["PARTIAL_TIMEOUT"], set())

    def test_invalid_transition_raises(self):
        saga = {"status": "PREPARED", "transitions": [], "updated_at": ""}
        with self.assertRaises(ValueError):
            saga_driver.append_transition(saga, from_state="PREPARED",
                                          to_state="CLOSED")

    def test_can_transition_partial_timeout_from_partial_timeout_blocked(self):
        # G-R1 invariant: nothing transitions FROM PARTIAL_TIMEOUT
        for s in saga_driver._ALLOWED_TRANSITIONS:
            self.assertNotIn(
                "PARTIAL_TIMEOUT",
                # i.e. it's not in any allowed-next set as a from-source
                # (it's only in allowed-next sets as a TARGET)
                saga_driver._ALLOWED_TRANSITIONS["PARTIAL_TIMEOUT"],
            )


class ResumeLogic(unittest.TestCase):
    def test_resume_walks_back_from_partial_timeout(self):
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

    def test_resume_no_op_when_not_partial_timeout(self):
        saga = {"status": "FANOUT_STARTED", "transitions": []}
        saga_driver.resume_from_partial_timeout(saga)
        self.assertEqual(saga["status"], "FANOUT_STARTED")


class LayerCrewsMatchYaml(unittest.TestCase):
    """Pass-4 A7: assert saga_driver._LAYER_CREWS matches
    framework/governance/REVIEW_CREWS.yaml so drift is caught in CI."""

    def test_layer_crews_match_yaml(self):
        import yaml  # PyYAML already a project dep (test_review_team.py)
        crews_path = (Path(__file__).resolve().parents[2]
                      / "framework" / "governance" / "REVIEW_CREWS.yaml")
        data = yaml.safe_load(crews_path.read_text())
        yaml_crews = {
            f"{i+1:02d}_{layer}": set(data["crews"][layer]["review"].keys())
            for i, layer in enumerate(
                ["BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN"])
        }
        for spec_layer, expected_crew in yaml_crews.items():
            driver_crew = set(saga_driver._LAYER_CREWS[spec_layer])
            self.assertEqual(
                driver_crew, expected_crew,
                f"saga_driver._LAYER_CREWS[{spec_layer!r}] drifted from "
                f"REVIEW_CREWS.yaml: driver={driver_crew} yaml={expected_crew}",
            )


if __name__ == "__main__":
    unittest.main()
```

### Design 5 — Plugin VERSION fanout (0.6.0 → 0.6.1)

9-place fanout per Phase 2 pattern. New `tools/saga_driver.py` is the
substantive addition. The 52-skill version sed bumps to `0.6.1`.

### Design 6 — Plugin CHANGELOG entry

```markdown
### Changed — Plugin v0.6.0 → v0.6.1

- **Saga driver script + slimmed autopilot SKILL
  (SAGA-PARITY-001 Phase 2 Amendment 1).** Replaces Phase 2's
  cooperative-enforcement saga loop (which empirically failed
  2026-06-05 verification: invalid transitions, non-terminal status,
  no subprocess dispatch) with a deterministic Python helper script.
  - **New**: `tools/saga_driver.py` — preemptive orchestrator that
    matches Hermes' `saga_orchestrator.py` in role. Drives the
    create→review→revise loop, validates transitions against the
    REVIEW_SAGA.md table, manages saga.json journaling, dispatches
    phases as `claude -p` subprocesses with per-phase budgets.
  - **Slimmed**: `doc-brd-autopilot/SKILL.md` reduces from ~300
    lines to ~50 — thin entry point that Bash-invokes the saga
    driver and reports the result.
  - **Removed**: harness dual-dispatch in `tests/scripts/test-acceptance.sh`.
    The cascade dispatcher now invokes ONLY `doc-<layer>-autopilot`
    per layer; doc-<layer>-audit, doc-<layer>-fixer, doc-<layer>
    are autopilot-internal vocabulary (still standalone-invokable
    for direct user use).
  - **Net behavior**: saga.json is now written DETERMINISTICALLY by
    the driver during the loop, not synthesized post-hoc by an LLM.
    Final status reliably reaches CLOSED or ESCALATED. Layer runtime
    drops from ~3656s (Phase 2 verification) to ~1800-2400s by
    eliminating harness duplicate dispatch.
  - **Hermes parity**: both platforms now preemptive at the
    orchestration layer (Hermes via its `saga_orchestrator`, plugin
    via `saga_driver.py`). The Phase 1 enforcement-asymmetry caveat
    becomes "asymmetric in language (Python vs Python+Bash) but not
    in semantic" — superseded.

  Plugin VERSION: `0.6.0 → 0.6.1`. PATCH bump because the helper
  script is purely additive and the SKILL slim is internal
  refactor; no public contract change. `FRAMEWORK_SPEC_VERSION`
  unchanged at `0.13.0`.
```

### Design 7 — `docs/PARITY.md` updates

```diff
-| Saga lifecycle (D-0031 / framework spec `0.13.0`) | `saga.json` written by autopilot SKILLs at `.aidoc/review/<NN>_<LAYER>/<id>/saga.json`; same state machine + journal schema as Hermes (cooperative enforcement via SKILL prompts). **BRD layer implemented in plugin v0.6.0** (SAGA-PARITY-001 Phase 2); PRD..IPLAN propagation arriving in Phase 4. | Python saga runtime (`saga_orchestrator.py`, `saga_models.py`, `saga_journal.py`); preemptive enforcement |
+| Saga lifecycle (D-0031 / framework spec `0.13.0`) | `saga.json` written by `tools/saga_driver.py` (Python helper script invoked by autopilot SKILL via Bash); same state machine + journal schema as Hermes. **Preemptive enforcement** (Phase 2 Amendment 1, plugin v0.6.1) — matches Hermes' mechanism. BRD layer implemented; PRD..IPLAN propagation arriving in Phase 4. | Python saga runtime (`saga_orchestrator.py`, `saga_models.py`, `saga_journal.py`); preemptive enforcement |
```

Also update the §"Enforcement asymmetry" paragraph at the top of PARITY.md:

```diff
-**Enforcement asymmetry (honest caveat).** Hermes enforces the state
-machine preemptively in Python (`can_transition` raises on invalid
-transitions; runtime owns the journal). The plugin enforces it
-cooperatively (SKILL.md prompts instruct the LLM to validate
-transitions before writing saga.json; OS-level `timeout` is the hard
-floor).
+**Enforcement parity (post-Amendment 1).** Both platforms enforce the
+state machine preemptively. Hermes via its Python runtime
+(`can_transition` raises on invalid; runtime owns the journal). The
+plugin via `tools/saga_driver.py` (Python helper invoked by the
+autopilot SKILL via Bash; same `can_transition` semantics; same
+journal ownership at the script level). The mechanism differs
+(in-process Python vs subprocess Bash + Python script); the
+observable lifecycle is identical. Phase 1's earlier "cooperative
+vs preemptive" caveat is superseded by this Amendment.
```

### Design 8 — Live BRD re-verification (10 pass criteria)

Run:

```sh
bash tests/scripts/test-acceptance.sh url-shortener --live \
     --phase=cascade --from-layer=brd --to-layer=brd --force
```

Pass criteria (expanding Phase 2's 8, all must pass — bug-free
confirmation gate):

1. `saga.json` present + **schema-conformant** (validates against
   `saga.schema.json` including all required fields).
2. 5 lens slot files present (CHAOS-SEC-SPLIT-001 carry-forward).
3. Final saga `status: CLOSED` (terminal happy path). Phase 2
   verification produced `BRANCH_COMPLETED` — this amendment must
   fix that.
4. `transitions[]` contains **only valid transitions** per REVIEW_SAGA.md
   table. The driver's preemptive enforcement raises on invalid, so
   any invalid transition crashes the loop — automatically enforced.
   Phase 2 verification had 7 invalid transitions; this amendment
   must have zero.
5. `verdict.json:lens_scores` map contains both `chaos_engineer` and
   `security_engineer` keys.
6. **Per-phase subprocess invocations visible** in the harness's
   element logs (the saga driver's stdout shows `dispatch: <phase>
   (<slash>) ...`). Phase 2 verification showed 0 subprocesses; this
   amendment must show 3-4 per iteration.
7. No SIGTERM-leaked saga.json. Either saga reaches CLOSED naturally,
   OR reaches PARTIAL_TIMEOUT via break-circuit (graceful exit).
8. No `from: PARTIAL_TIMEOUT` transitions in saga.json (G-R1
   invariant; preemptively enforced by the driver).
9. **Layer runtime ≤ MAX_LAYER_SEC (3600s).** Phase 2 verification
   exceeded by 56s (3656s); this amendment must stay within budget
   by eliminating dual-dispatch.
10. **Harness invokes only autopilot per layer.** Verify by grep on
    the harness log: only `INFO invoking /aidoc-flow:doc-brd-autopilot`
    should appear in the cascade phase (no `doc-brd-audit`,
    `doc-brd-fixer`, `doc-brd` invocations).

Note (Pass-4 A1 correction): the existing `invoke_skill_live` at
`tests/scripts/test-acceptance.sh:420-466` already captures stdout
(combined with stderr via `> "$out_path" 2>&1`) to
`logs/<TS>/elements/<name>.stdout`. **No code change needed** for
criterion 6 — the driver's `dispatch: ...` log lines appear in the
autopilot subprocess's stdout file post-run. The original Pass 3
G-V9 finding (claim that stdout capture needed adding) was wrong.

Pass-4 A3 — CHG cascade out of scope. `tests/scripts/test-acceptance.sh`
lines 1180-1200 dispatch a separate cascade for the CHG layer
(`doc-chg-autopilot`, `doc-chg-audit`, `doc-chg-fixer`,
`doc-chg-audit` re-audit). That dispatcher retains the dual-dispatch
pattern unchanged in this amendment — CHG is a governance overlay
outside the 8-layer SAGA-PARITY-001 scope. A future plan could apply
the same autopilot-only pattern to CHG; not in this amendment.

## Step sequence

1. **Create** `tools/saga_driver.py` per Design 1.
2. **Extend** `tools/sync-plugin-framework.sh` per Pass-4 A4 / Pass-5
   P5-1: append `"tools"` to the `SUBTREES` array (or equivalent rsync
   include) so `tools/saga_driver.py` lands at
   `platforms/claude-code-plugin/tools/saga_driver.py` on every sync.
   The plugin SKILL invokes the driver via
   `${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py`, so the vendored copy
   inside the plugin bundle is mandatory — Claude Code does not see the
   repo-root `tools/` when the plugin is installed standalone.
3. **Edit** `platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md`
   per Design 2 (slim the saga-driven loop section to a thin entry
   point that invokes the bundled `${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py`).
4. **Edit** `tests/scripts/test-acceptance.sh` per Design 3 (cascade
   dispatcher autopilot-only + env-var injection of `PREV_OUTPUT`,
   `ARTIFACT_ID`, `ARTIFACT_PATH`; stdout capture is unchanged — it
   already exists via `invoke_skill_live`).
5. **Create** `tests/conformance/test_saga_driver_invariants.py`
   per Design 4 (includes `test_layer_crews_match_yaml` from A7).
6. **Bump plugin VERSION** 0.6.0 → 0.6.1.
7. **9-place fanout** for 0.6.1 (per CHAOS-SEC-SPLIT + Phase 2
   pattern; 52-skill sed bump).
8. **Edit** plugin CHANGELOG per Design 6.
9. **Edit** `docs/PARITY.md` per Design 7.
10. **Edit** `docs/TAGGING.md` — add `claude-code-plugin/v0.6.1` row.
11. **Run** `tools/sync-plugin-framework.sh` to produce the vendored
    copy of `tools/saga_driver.py` inside the plugin bundle; commit
    the synced file alongside the source.
12. **Pre-commit lint** on all changed files.
13. **Conformance suite** — 101 + 5 new tests in
    `test_saga_driver_invariants.py` (4 originally planned + 1
    `LayerCrewsMatchYaml`) = 106 total.
14. **Live BRD verification** per Design 8 — all 10 pass criteria
    must succeed. Per user instruction, **Phase 3 stays blocked**
    until this verifies bug-free.

## Verification

### Step A — Static lint

Pre-commit `--all-files`. Pass: green.

### Step B — Conformance suite

```sh
env -u LD_LIBRARY_PATH python3 -m unittest discover -s tests/conformance
```

Pass: 105/105 (101 baseline + 4 new in `test_saga_driver_invariants.py`).

### Step C — Saga driver unit tests (standalone)

```sh
python3 -m unittest tests.conformance.test_saga_driver_invariants -v
```

All 4 tests pass.

### Step D — Mock-mode acceptance

```sh
bash tests/scripts/test-acceptance.sh url-shortener --no-live
```

Pass: PASS outcome. Mock mode doesn't exercise the saga driver's
subprocess dispatches; this is a structural regression check.

### Step E — Live BRD verification per Design 8

The bug-free confirmation gate. 10 pass criteria, all must succeed.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Saga driver Python script has bugs that only surface live (e.g., argparse, path resolution, subprocess args) | Step C unit tests catch state-machine bugs; mock-mode regression catches structural; live verification (Step E) catches integration. Plus the driver is ~300 lines Python — small enough to read end-to-end before live runs. |
| R2 | Subprocess invocation of `claude -p` from within Python may have env-inheritance issues (PLUGIN_DIR, PATH, auth) | The harness already does this exact pattern (`test-acceptance.sh:invoke_skill`). The driver inherits the parent process's env via `subprocess.run`. R1 verification confirms. |
| R3 | The autopilot SKILL is now thin — but the `claude -p` invocation of `/aidoc-flow:doc-brd-autopilot` still expects an LLM session. The LLM in that session reads the slim SKILL, then... does nothing useful? It just invokes the script. | Yes, the autopilot session is now a near-no-op — the LLM reads the SKILL, runs one `Bash` command, returns. ~1-3 minutes overhead (LLM startup + tool invocation). Acceptable. Alternative: bypass the SKILL entirely and have the harness invoke `python3 tools/saga_driver.py` directly. Considered; rejected — the SKILL form keeps the `/aidoc-flow:doc-brd-autopilot` slash-command invocation contract that users have come to expect. |
| R4 | The driver's transition table embedded in Python may drift from REVIEW_SAGA.md's table | A conformance test in Phase 3 will assert spec ↔ driver byte-equality. For now, the driver's table mirrors the spec by inspection. R6 below tracks the drift risk. |
| R5 | The driver doesn't update individual `branches[<persona>]` entries (the audit subprocess's SKILL does that). If the audit subprocess doesn't update branches[] per its Phase 2 saga-interaction section, the saga.json will show empty branches{} | The audit's Phase 2 SKILL.md §"Saga interaction" §"During lens fan-out" instructs it to update `branches[<lens>]`. Whether the LLM in the audit subprocess actually does this is the next cooperative-enforcement risk. Live verification will reveal this. If it fails, a follow-up amendment would extend the driver to update branches[] from outside (read slot files, infer state). |
| R6 | The saga driver's `_LAYER_CREWS` mapping drifts from `REVIEW_CREWS.yaml` | Driver hardcodes the 8-layer crews for Phase 2 + Phase 4 use. A conformance test should assert `_LAYER_CREWS` matches REVIEW_CREWS.yaml. Add to Step 4 (Design 4) as a follow-up test, OR rely on the existing `test_review_team.py` to catch crew drift indirectly. |
| R7 | Live verification still fails because the audit/fixer SUBPROCESSES (not autopilot's parent session) suffer the same cooperative-enforcement issues as Phase 2 | The audit + fixer are simpler than autopilot's full loop — each does one phase. Their saga.json interaction is bounded (transition specific branches; check break-circuit once). Cooperative enforcement at this granularity has worked in prior verifications (BRD-RT chain). If it fails, a future amendment converts those skills to use small helper scripts too. |
| R8 | Layer cap (3600s) still exceeded because subprocess dispatch + the driver's wall-clock waiting adds latency | Phase 2 verification was 3656s WITH dual-dispatch. Removing the harness duplication saves ~24 minutes (the audit+fixer+audit phase). Net new runtime: ~1800s autopilot + ~1500s nested subprocess phases via the driver = total ~3300s, comfortably under cap. |
| R9 | Standalone direct invocation of `doc-brd-audit` etc. via slash command stops working because their SKILL.md saga-interaction sections expect saga.json context | Phase 2 Pass 4 G-R5 explicitly handles this: standalone invocation (no saga.json present) skips saga.json writes entirely. Re-confirmed: the audit/fixer SKILLs are backward-compatible with direct invocation. |
| R10 | The driver's `subprocess.run` doesn't capture child stdout to a log file. Element logs won't show the per-phase invocations needed for pass criterion #6 | Design 3 (test-acceptance.sh diff) adds stdout capture for the autopilot subprocess. The driver's stdout (which shows `dispatch: ...` lines) flows through to the parent's stdout. The harness captures it to `logs/<TS>/elements/doc-brd-autopilot.stdout` for post-run inspection. |

## Review log

### Pass 1 — 2026-06-05T17:45:00Z (initial draft)

- Drafted in response to Phase 2 live verification surfacing
  cooperative-enforcement failure + user's confirmation of the
  autopilot-only architectural direction.
- Scope is minimal-but-cohesive: one new Python file (~300 lines),
  one substantially slimmed SKILL.md, one harness cascade diff
  (~50 lines), one new unit test file (~80 lines), plus
  CHANGELOG/PARITY/TAGGING/VERSION updates.
- All Phase 2 SKILL changes (audit/fixer/review-team saga interaction
  sections) STAY — they're invoked via subprocess by the driver.
  Standalone direct invocation also still works.
- The Phase 1 enforcement-asymmetry caveat is conceptually superseded
  by this amendment (both platforms preemptive in mechanism). The
  spec text doesn't need to change — it correctly says "engines MAY
  enforce via different mechanisms" — both are now preemptive, just
  at different layers (Hermes: in-process Python runtime; plugin:
  out-of-process Python script).

### Pass 2 — 2026-06-05T17:45:00Z (self-review, per two-cycle rule)

- **G-V1 — `saga_driver.py` is ~300 lines + needs full coverage**.
  Design 1 shows the full content. Largest single file. Worth a
  careful Pass 3 codebase cross-check.
- **G-V2 — Layer crew table in the driver**. Currently hardcoded
  for all 8 layers. Risk of drift from REVIEW_CREWS.yaml. Added R6
  to track; conformance check is a follow-up.
- **G-V3 — `--artifact-path` parsing assumption**: driver computes
  `project_root = Path(args.artifact_path).parents[2]` (skipping
  docs/<layer>/<file>). If the artifact path doesn't follow that
  convention (e.g., monolithic vs nested folder layout), the
  saga_dir resolution breaks. Worth a small assertion + a clearer
  CLI design (pass `--project-root` explicitly). Add to Pass 3.
- **G-V4 — Default plugin-dir hardcoded to my local path**:
  `/opt/data/aidoc-flow/framework/platforms/claude-code-plugin`.
  This breaks for other users. Should use `os.environ` lookup with
  a fallback derived from the script's own path. Fix in Pass 3.
- **G-V5 — Pass criterion #10 requires harness log grep**. The
  driver's stdout goes to the autopilot subprocess's stdout, which
  the harness now captures (per Design 3). To verify "no
  doc-brd-audit invocations by harness" — grep the harness's main
  log file (not autopilot's subprocess stdout). Different paths.
  Clarify in Design 8.
- **G-V6 — `_advance_after_phase` post-`re-review`**: when verdict is
  FAIL and `iteration < MAX_ITERATIONS`, the driver sets
  `current_phase: fixer` but does NOT append a transition. The
  state stays at the audit's last transitioned state (likely
  BRANCH_COMPLETED). The next iteration's fixer phase will append
  its own transitions. Verified correct.
- **G-V7 — Pass criterion #4** ("transitions[] contains only valid
  transitions") is preemptively enforced by `append_transition()`
  raising ValueError. If the driver crashes mid-loop, the partial
  saga.json may have an inconsistent state but no INVALID transition.
  Good.

### Pass 3 — 2026-06-05T17:45:00Z (codebase cross-check, per two-cycle rule)

- **G-V8 — Verify `tools/` is the right location** for the driver.
  `ls tools/` shows: `build-plugin-mirror.sh`, `bump_version.py`,
  `sdd_doc_lint`, `sync-plugin-framework.sh`. Python scripts already
  live there (`bump_version.py`). `saga_driver.py` fits the
  convention.
- **G-V9 — Verify `test-acceptance.sh:invoke_skill`** captures
  subprocess stdout. Reading the function (lines around 480-540):
  it currently captures stderr but not stdout to a separate file.
  Design 3 needs to explicitly add stdout capture if pass criterion
  #6 requires it. Updated in Pass 3 to clarify.
- **G-V10 — Verify the audit's saga-interaction (Phase 2) writes
  saga.json**. Per `doc-brd-audit/SKILL.md` §"Saga interaction"
  (added in PR #88): the audit reads `.aidoc/review/01_BRD/<BRD-id>/saga.json`
  on entry and writes branches[] + transitions[] entries. Whether
  the LLM in the audit subprocess actually does this is the next
  enforcement risk (R5, R7). The driver doesn't override the audit's
  saga writes — they coexist. If the audit fails to write branches,
  the driver can detect (saga.json has empty branches{} after audit
  subprocess returns) and escalate.
- **G-V11 — Verify `parse_audit_score`** in test-acceptance.sh.
  After Design 3's removal of doc-brd-audit dispatch, the variable
  `$score` is computed from saga.json's `result.content_score`.
  But the saga driver's `_advance_after_phase` writes the verdict's
  `combined_status` to determine PASS/FAIL — it doesn't currently
  COPY content_score into saga.json's top-level result block.
  **Need to update the driver** to populate `saga["result"] =
  {"combined_status": ..., "content_score": ..., ...}` so the
  harness can read it from saga.json. Added to Design 1's
  `_advance_after_phase` logic.
- **G-V12 — Verify `--artifact-id` derivation**. The harness today
  passes `$artifact` (e.g., `docs/01_BRD/BRD-01.md`) but not the
  artifact ID directly. The driver needs both. Design 3's harness
  diff should derive the artifact-id from $artifact (e.g.,
  `BRD-01`) and pass it explicitly via `--artifact-id` (or have
  the driver derive it from --artifact-path). Reading Design 1
  again: the CLI takes both. The harness needs to compute the ID
  and pass it. Clarify in Design 3.
- **G-V13 — Verify lint+conformance impact**. The new Python file
  triggers ruff/bandit. The driver is stdlib-only and follows
  standard idioms. Should lint clean. Verified by reading Design 1
  end-to-end.

**Pass 3 patches folded into Design 1 (G-V11), Design 3 (G-V9, G-V12),
and Design 8 (G-V5).**

### Pass 4 — 2026-06-05T20:30:00Z (post-merge gap-review against codebase)

> **Historical note**: this Pass 4 ran AFTER the plan PR (#89)
> merged. That ordering is the anti-pattern the user spotted later
> the same day; PR #90 amends CLAUDE.md to forbid it going forward
> (all gap-reviews must run BEFORE the plan PR opens). This Pass 4
> is the **last legitimate post-merge amendment** under the
> clarified rule — preserved for traceability of the in-flight
> SAGA-PARITY-001 work. Future plans run all cycles pre-PR.

Post-merge codebase cross-check surfaced **7 gaps** the inline
Pass 1-3 missed. All folded into Designs 1, 2, 3, and 8 via this
amendment.

**Critical (5)**:

- **A1 — Design 3 incorrectly claims stdout capture needs adding.**
  `invoke_skill_live` at `tests/scripts/test-acceptance.sh:420-466`
  already uses `> "$out_path" 2>&1` to capture combined stdout+stderr
  to `logs/<TS>/elements/<name>.stdout`. The Pass 3 G-V9 finding
  was wrong about this. Pass criterion #6 (Design 8) is verifiable
  today without code change. Design 3 amended to remove the "add
  stdout capture" claim.

- **A4 — `saga_driver.py` install-location strategy missing.**
  Design 2's `Bash: python3 ${REPO_ROOT}/tools/saga_driver.py`
  uses an undefined env var. When the plugin is installed standalone
  (Claude Code marketplace), the repo's `tools/` directory is NOT
  available. Resolution: **vendor the script** to
  `platforms/claude-code-plugin/tools/saga_driver.py` (similar to
  D-0022 framework bundle), sync via an extended
  `tools/sync-plugin-framework.sh`. SKILL invocation becomes
  `Bash: python3 ${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py ...`.
  Design 1 + Design 2 amended; sync script extension added to
  Step sequence.

- **A5 / A6 — LLM-cooperative prompt parsing brings back the
  failure mode.** Original Design 2 has the LLM parse the prompt
  text to extract paths (seed, artifact). Same cooperative-
  enforcement risk we're trying to escape. Resolution: **harness
  passes paths via env vars** (`PREV_OUTPUT`, `ARTIFACT_PATH`,
  `ARTIFACT_ID`); driver reads from env (CLI as fallback);
  autopilot SKILL becomes one-line: `Bash:
  PREV_OUTPUT="$PREV_OUTPUT" python3 ${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py
  --layer 01_BRD`. Design 1 + 2 + 3 amended.

- **A8 — Driver doesn't validate or fix audit subprocess's
  `branches[]` writes.** The 2026-06-05 live verification showed
  the audit subprocess wrote synthetic branches without
  `branch_id` and with placeholder timestamps. The driver as
  originally designed doesn't read or fix what the audit wrote.
  Resolution: **driver re-reads saga.json after audit subprocess
  returns** and validates each `branches[<persona>]` entry. If
  malformed (missing `branch_id`, status not in branch-state enum,
  malformed timestamps), the driver REPAIRS from existing slot
  file mtimes (`branch_id` = deterministic hash;
  `started_at` = `ended_at` = slot file mtime). Design 1 amended
  with `validate_and_repair_branches()` helper.

- **A9 — Missing `verdict.json` handling not specified.** Original
  `read_verdict_score` returns `(0, "UNKNOWN")` if verdict.json
  absent. State machine then treats UNKNOWN as FAIL → dispatches
  fixer. But UNKNOWN really means the audit subprocess failed to
  write verdict.json — that's an audit FAILURE, not content-quality
  FAIL. Resolution: **driver ESCALATES if audit completes but
  verdict.json is absent**. Design 1's `_advance_after_phase`
  amended.

**Medium (1)**:

- **A3 — CHG cascade dispatcher (lines 1180-1200 of test-acceptance.sh)
  retains dual-dispatch.** The amendment plan only touches the
  BRD cascade. CHG is OUTSIDE the SAGA-PARITY-001 scope (CHG is a
  governance overlay, not one of the 8 SDD layers). Resolution:
  **document explicitly in Design 3** that CHG is out of scope;
  CHG dispatcher keeps the dual-dispatch pattern unchanged. A
  follow-up plan could apply the same autopilot-only pattern to
  CHG, but that's a separate effort.

**Cosmetic (1)**:

- **A7 — `_LAYER_CREWS` hardcode drift risk not enforced by
  test.** Amendment plan flags this as R6 but the new conformance
  test (Design 4) doesn't actually check `_LAYER_CREWS` matches
  `REVIEW_CREWS.yaml`. Resolution: **Design 4 amended** to add a
  test (`test_layer_crews_match_yaml`) that parses
  `framework/governance/REVIEW_CREWS.yaml` via PyYAML (already a
  project dep per existing `test_review_team.py`) and asserts
  `_LAYER_CREWS[layer]` == YAML's crew for each of the 8 layers.

**Net delta after Pass 4 patches**:

- Design 1 (`saga_driver.py`): adds `validate_and_repair_branches()`;
  ESCALATE on missing verdict.json; reads env vars (PREV_OUTPUT,
  ARTIFACT_PATH, ARTIFACT_ID) with CLI fallback.
- Design 2 (`doc-brd-autopilot/SKILL.md`): invocation uses
  `${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py` (not `${REPO_ROOT}`);
  no LLM-cooperative prompt parsing.
- Design 3 (`tests/scripts/test-acceptance.sh`): removes stale "add
  stdout capture" claim (A1); passes env vars to autopilot
  subprocess; explicitly documents CHG dispatcher unchanged.
- Design 4 (`test_saga_driver_invariants.py`): adds
  `test_layer_crews_match_yaml`.
- Step sequence: adds extending `tools/sync-plugin-framework.sh`
  for the new vendored `tools/saga_driver.py`.

### Pass 5 — 2026-06-05T20:35:00Z (re-review of Pass 4 patches)

Per the two-cycle rule's "Cycle N+1 must always re-validate cycle
N's patches did not introduce new inconsistencies":

- **P5-1**: A4's resolution (vendor script to plugin bundle)
  requires extending `sync-plugin-framework.sh`. Currently the
  sync script copies `framework/{layers,governance,registry}` +
  one root file. Adding a NEW subtree (`tools/`) is structural.
  Need to verify the sync script's `SUBTREES` array extension
  is clean. Design 1's note now includes "extend sync script's
  SUBTREES array to include `tools/`" as part of Step sequence.
- **P5-2**: A8's `validate_and_repair_branches()` reads slot file
  mtimes — but mtimes depend on filesystem and run order. If
  slot files don't exist (e.g., the audit subprocess failed
  before writing them), the repair has no data. Need fallback:
  if no slot file exists, set
  `started_at = ended_at = saga.created_at`. Design 1 amended.
- **P5-3**: A9's resolution sets ESCALATED on missing
  verdict.json. But what if it's a TRANSIENT failure (e.g., audit
  subprocess SIGTERM mid-write)? Should driver retry the audit
  phase before escalating? For Phase 2 Amendment 1, accept
  "missing verdict.json = ESCALATE" as the simple rule; retry
  logic is a follow-up. Documented as a risk (R-A9) in §Risks.
- **P5-4**: A5/A6's env-var passing: confirmed that
  `test-acceptance.sh`'s `invoke_skill_live` calls
  `claude ... -p "..."` with NO env-var passthrough. The harness's
  `claude` subprocess inherits its parent's env automatically.
  So setting env vars in the harness BEFORE the `claude` call
  works. Verified.
- **P5-5**: A7's `test_layer_crews_match_yaml` requires PyYAML.
  Confirmed `tests/conformance/test_review_team.py` already imports
  `yaml` — PyYAML is available in CI. No new dependency.

Pass 5 surfaced one substantive issue (P5-2) folded into Design 1.
P5-1, P5-3, P5-4, P5-5 were verifications, no new patches.

**Plan ready for impl** (this time for real, with Pass 4 + Pass 5
folded in). Under the **clarified** two-cycle rule (PR #90), the
remaining 7 gaps would have been caught pre-PR; this Pass 4
remediation is preserved here as the last legitimate post-merge
amendment for historical traceability.

## Cross-references

### Within this plan family

- **Parent plan**: `plans/SAGA-PARITY-001-PLAN.md` (merged)
- **Phase 1 plan**: `plans/SAGA-PARITY-001-PHASE-1-PLAN.md` (merged)
- **Phase 2 plan**: `plans/SAGA-PARITY-001-PHASE-2-PLAN.md` (merged; SUPERSEDED by this amendment for the autopilot's saga loop)
- **Phase 3 plan (skeleton)**: not yet committed; blocked until this
  amendment verifies bug-free.
- **Phase 4** (after Phase 3): plugin propagation to PRD..IPLAN
  using this amendment's pattern.

### Predecessor decisions

- **D-0031** — promotes the saga lifecycle to spec.
- **D-0005** — original "no saga in plugin" (superseded in scope by
  D-0031).
- **G-R1** (Phase 2 Pass 4) — PARTIAL_TIMEOUT is checkpoint marker
  only; no `from: PARTIAL_TIMEOUT` transitions allowed.
- **Live BRD verification 2026-06-05T16:22:34** — empirical evidence
  that Phase 2's cooperative-enforcement model fails.

### Spec authorities

- `framework/governance/REVIEW_SAGA.md` — the lifecycle contract.
- `framework/governance/saga.schema.json` — the journal schema.
- `framework/governance/REVIEW_TEAM.md` — operational semantics.

### Plugin files modified

- `tools/saga_driver.py` (new)
- `platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md`
  (slimmed)
- `platforms/claude-code-plugin/VERSION` (0.6.0 → 0.6.1)
- `platforms/claude-code-plugin/CHANGELOG.md` (new entry)
- 9-place version fanout + 52-skill sed bump

### Test files modified

- `tests/scripts/test-acceptance.sh` (cascade dispatcher dedup +
  stdout capture)
- `tests/conformance/test_saga_driver_invariants.py` (new)

### Documentation

- `docs/PARITY.md` — Saga lifecycle row updated; Enforcement
  asymmetry caveat superseded.
- `docs/TAGGING.md` — `claude-code-plugin/v0.6.1` row.
