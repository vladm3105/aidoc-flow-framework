# 08_IPLAN — TODO (retired / historical gap audit)

> **This file is retired and preserved for historical reference only. Do not add entries to it.**
> All active tasks and defects are tracked on the **[GitHub issue tracker](https://github.com/vladm3105/aidoc-flow-framework/issues)**.

---

Status: open items from the 2026-06-09 IPLAN layer review session.
Origin: discussion of IPLAN-TEMPLATE.yaml language-coupling (→
`plans/IPLAN-LANG-001-PLAN.md`, plan ready, not yet implemented) followed by an
adversarial fresh-context audit of the layer against proposed
execution-management requirements. All file:line citations were verified
against source during that session.

## Context facts (verified 2026-06-09)

- **No project has ever reached Layer 8.** `examples/url-shortener/docs/`
  stops at `06_SPEC`; every `doc-iplan-autopilot` acceptance-log entry is
  `outcome: SKIP`. No IPLAN has ever been executed end-to-end. All
  execution-management additions below are therefore designed against zero
  runtime evidence until a first real run exists.
- Capability classification of the current template
  (`IPLAN-TEMPLATE.yaml`):

  | Capability | State | Evidence |
  | --- | --- | --- |
  | Task completion marking | EXISTS | `file_manifest.files[].status` markers + `verified` flag (template :62-77); enforced by Hermes `iplan_rules.py:70-71` |
  | Session-summary logging | EXISTS | `session_handoff.sessions[]` (template :137-150); `traceability.code_inventory` (:167-176) |
  | Per-command execution logging | MISSING | no field for command output / error text / failed-attempt history; only 3 booleans + free text |
  | Re-runnability (clean interruption) | EXISTS | resume protocol README:54-57, template :127-130 (`PARTIAL` path) |
  | Re-runnability (crash) | DEFECT | see Named defect 1 |
  | Post-execution retrospective | MISSING | per-session `validation_results` only (:147-150); index `on_plan_completed` updates counters only (`IPLAN-00_index.TEMPLATE.yaml:160-163`) |
  | Plan-level parallelism | EXISTS | index `parallel_with[]` (:42) + `execution_path.tiers` (:64-89) |
  | Intra-plan parallelism (multiple agents, one IPLAN) | MISSING | no claim/lease field; `session_count` assumes serial sessions (:51); single YAML updated in place → concurrent read-modify-write loses updates |

## Named defects (evidence-backed; design now or with first Layer-8 run)

1. **`IN_PROGRESS` orphan hole (crash recovery).** The resume protocol
   instructs successors to pick the next `NOT_STARTED` or `PARTIAL` file —
   `IN_PROGRESS` is not in the search (README:54-57; template :127-130;
   restated in plugin `doc-iplan/SKILL.md:100-106`). A session that crashes
   after flipping a file to `IN_PROGRESS` but before writing its handoff
   entry orphans that file permanently: no staleness rule, no reclaim
   semantics, no specified write ordering (when to flip status relative to
   doing the work and appending the session entry). Fix is a few protocol
   lines: an `IN_PROGRESS`-stale reclaim rule + explicit write ordering, in
   README §Session Handoff Protocol and template Section 5 `_guidance`.
2. **Hermes ↔ template contract break: `iplan_ready_score`.** Hermes
   `check_iplan_readiness_score` errors when
   `document_control.iplan_ready_score` is missing
   (`platforms/hermes/src/mcp_server/validation/iplan_rules.py:30-32`), but
   the template's `document_control` (:39-51) defines no such field; neither
   does the acceptance golden fixture. A template-conforming IPLAN fails
   Hermes validation today. Belongs on `plans/HERMES-BACKLOG.md` (Hermes
   parity), not in a template change.

## Backlog (no named issue yet — do NOT design until a real Layer-8 run surfaces the need)

Per the minimal-and-realistic-plans convention (CLAUDE.md §Durable
conventions), these stay one-liners until an end-to-end IPLAN execution
names and sizes them:

- Per-command execution logging (command output / error capture per session).
- Post-execution retrospective section (manifest deviations, deferred items
  closed, lessons; completion gate analog of `doc-iplan-audit`, which today
  only gates pre-code).
- Intra-plan claim/lease mechanism for concurrent agents — requires solving
  single-file write contention (lost-update races on one YAML), not just a
  `claimed_by` field.
- Heterogeneous agent/model routing per task — per-file/per-task complexity
  or capability hints so an orchestrator can route simple files to a cheap
  model and complex ones to a strong model + matching skills. Embryonic
  hooks exist (`session_handoff.sessions[].agent`, document-level
  `complexity: 1-5`). Likely split: the *hint* lives in IPLAN, the routing
  logic lives in the platform (manifest/engine split). Depends on the
  intra-plan parallelism item.

## SemVer impact notes (verified against consumers)

- A new **required** top-level section = framework spec **MINOR**: must
  update `metadata.total_sections: 6` (template :16), five section
  enumerations in plugin `doc-iplan/SKILL.md` (:77, :80, :127, :144, :192),
  `doc-iplan-autopilot/SKILL.md:74`, `doc-iplan-fixer/SKILL.md:53`, and
  3 acceptance golden fixtures (`tests/acceptance/_harness.py:24-32` treats
  every top-level key as required by default). `doc-iplan-audit` enumerates
  dynamically and auto-adapts.
- New **optional fields** on existing sections (e.g. lease/routing hints on
  manifest entries) are additive ≈ **PATCH**: Hermes `IPLAN-002` errors only
  on missing fields; acceptance checks only ordering/directive; neither
  rejects extra keys.

## Decisions already taken (do not reopen without new evidence)

- **No design-review governance in IPLAN** (Review log / Claim ledger): that
  rigor lives upstream (BRD…SPEC) and in the markdown development plan —
  `PLAN_STANDARD.md` §Scope and boundary. IPLAN stays a lean execution
  manifest; its governance is execution-evidence (`verified`,
  `validation_results`, `code_inventory`).
- **Review-pass minimum stays 2.** Empirics across 65 plans with review
  logs: 42 converged at 2 passes, 13 at 3, 5 at 4, 4 at 5, 1 at 6. The
  zero-findings stop-condition already extends to 3-6 passes when content
  demands; a floor of 3 adds ritual passes to the ~65% that converge at 2.
- **`execution_commands` category keys (`setup`/`implementation`/
  `validation`) are a validated contract** (`iplan_rules.py:104`) — already
  language-neutral; do not rename.

## Sequencing recommendation

1. Implement `plans/IPLAN-LANG-001-PLAN.md` (de-Python template example
   content; spec PATCH 0.15.2 → 0.15.3). Plan is ready (3 review passes,
   17 verified citations).
2. Fix Named defect 1 (small spec-text change) — standalone or folded into
   the first Layer-8 end-to-end plan.
3. Record Named defect 2 on `plans/HERMES-BACKLOG.md`.
4. **Drive an example project (url-shortener) through 07_TDD → 08_IPLAN →
   execution.** This first real run converts the backlog items from
   speculation into named, sized issues.
5. Only then design execution-management additions, sized to what the run
   actually surfaced.
