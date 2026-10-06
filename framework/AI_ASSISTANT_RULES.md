# AI Assistant Rules

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.3 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.88.1 |


## Template Usage

- **Dual-Template Selection (GD-51 through GD-61)**:
  - **Standard Templates (`layers/0X_TYPE/TYPE-TEMPLATE.yaml`)**: Use for straightforward, atomic, or linear artifacts where declarative specification without execution graph state transitions is sufficient.
  - **Workflow Templates (`layers/0X_TYPE/TYPE-SWF-TEMPLATE.yaml`)**: Use when the artifact models complex state transitions, multi-branch parallel operations, automated evaluation runners, distributed choreography contracts, or saga compensation rollbacks. These templates follow the **Hybrid Envelope Architecture** (`subtype: workflow`), preserving full structural schema compliance (`STRUCT01-10`) with `sdd_doc_lint` while housing an embedded CNCF Serverless Workflow v0.8 YAML state machine (`workflow_definition`).
- **Normative Workflow Standards**: When authoring workflow-enabled artifacts or understanding layer state machines, consult `framework/governance/GOVERNANCE_WORKFLOW_STANDARD.md` and the per-layer specification standard `layers/0X_TYPE/TYPE_WORKFLOW_STANDARD.md`.
- Fill placeholder fields (`[text]`, `xxxx`) with actual values.
- Do not remove `_guidance`, `_note`, `_example`, or `_antipatterns` fields — they are ignored by validators but provide context.

## Traceability Rules

- Every element must be traceable to an upstream artifact.
- Cite only the layer's **necessary upstream** (its `required_tags` in `LAYER_REGISTRY.yaml`) — NOT the full `@brd → … → @iplan` chain. Deeper lineage is transitive (one hop per layer). Emitting tags for absent upstream layers is trace fabrication (forbidden since NECESSARY-UPSTREAM-001).
- Downstream references are declared as placeholders until artifacts exist.
- Never create circular references.

## Layer Generation Order

```
1.  BRD  — business requirements, objectives, scope
2.  PRD  — product features, user stories (from BRD)
3.  EARS — formal WHEN-THE-SHALL-WITHIN requirements (from PRD)
4.  BDD  — Given-When-Then scenarios with spec_trace to SPEC (from EARS)
5.  ADR  — architecture decisions (from EARS + BDD)
6.  SPEC — component interfaces, data models, behavior contracts (from EARS + BDD + ADR)
7.  TDD  — test case definitions with inputs/outputs/edge cases (from EARS + BDD + ADR + SPEC)
8.  IPLAN — file manifest, bash commands, session handoff (from SPEC + TDD)
9.  CHG  — change management overlay: gates, versioning, audit trail (governance overlay, operational namespace 09 — outside the sequential lifecycle, not outside the numbering)
10. EVAL — evaluation & QA governance: test strategy, coverage matrices (from EARS + BDD + TDD + IPLAN)
11. Code — implementation from IPLAN
```

## EARS Syntax Distinction Invariant

When authoring Layer 03 (EARS) requirements or downstream mappings, AI assistants MUST enforce the structural distinction between operating states and error triggers:

- **`WHILE <precondition>` (State-Driven Requirements):** MUST be used exclusively for normal, continuous, or steady operating states (e.g., `WHILE the user session is authenticated and active, the system SHALL display the workspace dashboard`).
- **`IF <trigger>` (Unwanted Behavior / Fault Conditions):** MUST be used exclusively for event-driven errors, unexpected faults, rate limits, or exception triggers (e.g., `IF the database connection times out after 5000ms, the system SHALL retry with exponential backoff`).
- **Anti-pattern:** Using `IF` for normal operating states (e.g., `*IF user is logged in...`) or `WHILE` for transient error bursts violates the EARS grammar and confuses downstream BDD scenario generators.

## TDD Enforcement

When generating code from IPLAN:
1. Generate test files FIRST (from TDD Sections 3-4 test mappings and cases)
2. Run tests — they MUST fail (no implementation exists)
3. Generate implementation files
4. Run tests — they MUST pass
5. Refactor — keep tests green

## Development Completion Rule

A development IPLAN is **Completed** when:
- Source code is authored, committed, and tests pass
- Terraform modules, Helm charts, CI/CD workflow files, schema DDL, and deployment scripts are authored and committed
- `pre-commit run --all-files` passes with no errors

A development IPLAN is **NOT** blocked by:
- `terraform apply` not yet executed
- `atlas migrate apply` not yet run against the target environment
- Acceptance/soak testing not yet performed
- Image not yet built or deployed to a registry

These operator-only execution steps belong to a separate deployment plan. When closing a development IPLAN, register any deployment-handoff obligations in the IPLAN registry's `deferred_items` before flipping `Completed`.

## Hook and Verification-Bypass Prohibition

AI agents MUST NOT bypass verification gates:

- Never pass `--no-verify` (or any equivalent skip flag) on any `git` invocation (`commit`, `push`, `merge`, rebase).
- Never disable, uninstall, or route around configured hooks (`pre-commit`, `pre-push`, `hooks/`), and never document a bypass path as a recommended workflow.
- Auto-merge only when every required check is green. Boundary detection (`REVIEW_REMEDIATION_FLOW.md` audit-trail check) is the backstop, not the permission.

If a hook blocks legitimate work, fix the underlying cause or escalate to the human — the hook is never the problem to route around.

## IPLAN Status Lifecycle

```
Draft → Approved → In Progress → Completed → Verified
                                                   ↑
                                                   │ (Final/Finite)
                                                   │
                                          Cannot be changed
                                          (Need CHG + new IPLAN)
```

| Status | Meaning | Allowed Transitions |
|--------|---------|---------------------|
| `Draft` | IPLAN created, not yet approved | → Approved |
| `Approved` | IPLAN authorized to proceed | → In Progress |
| `In Progress` | Implementation underway | → Completed |
| `Completed` | Implementation done, awaiting validation | → Verified |
| `Verified` | Validation passed, **FINAL/FINITE** status | **None** (immutable) |

## Verified IPLAN Immutability Rule

Once an IPLAN reaches `Verified` status, it becomes **immutable**:
- No fields may be modified
- No files may be added or removed
- Status cannot be changed back

To modify a Verified IPLAN:
1. Create a CHG record documenting the need for changes
2. Create a NEW IPLAN (IPLAN-NN+1) that references the original
3. The original IPLAN remains in `Verified` status as historical record

## Validation Workflow (Completed → Verified)

Validation runs as EVAL cycles (canon: `layers/08_IPLAN/README.md`):

1. All `file_manifest` entries reach `DONE` + `verified: true`
2. Document status flips to `Completed`
3. Author (or reuse) the owning EVAL document (`EVAL-{NN}/EVAL-{NN}.yaml`)
4. Run eval cycle 1 (`initial_eval`); record `EVAL-{NN}-RPT-001.yaml` (`EVAL-REPORT-TEMPLATE.yaml`)
5. If findings exist:
   a. Repair via a scoped `bugfix`-subtype IPLAN (`parent_iplan` + `source_chg`)
   b. Fix all critical findings
   c. Re-run the next cycle (`bug_fix_verification`)
6. When all findings resolved:
   a. Mark original IPLAN as `Verified` (FINAL/FINITE)
   b. Close the bugfix IPLAN per its rollback/resolution markers

## IPLAN Session Handoff

Each AI agent session follows this protocol:
1. Read `session_handoff.sessions` — identify the last session's state
2. Check `file_manifest.files` — find next NOT_STARTED or PARTIAL file
3. Read `partial_work` description if resuming a PARTIAL step
4. Continue from that point — do NOT regenerate completed work
5. Update file status after completion or session end
6. Append to `session_handoff.sessions` with next_session_directive

## Issue Validation Before Work

Re-validate any picked-up issue live before acting on it — an issue may
already be fixed, stale, inapplicable, or declined since it was filed:

1. Read it back (`gh issue view`): still OPEN, and nothing in the comments,
   linked PRs, or newer issues supersedes, declines, or already resolves it.
2. Check the target branch: the defect is still reproducible (or the gap
   still present) there — not fixed by an intervening change.
3. If it is fixed, stale, inapplicable, or declined: report that with
   evidence and stop. Do not implement, do not "improve around" it.

Keep every change safe for the existing code: no behavior change beyond the
issue's scope, no weakened checks, suites green before the PR. A change that
breaks compatibility or is otherwise significant needs a CHG first — create
it and follow the CHG procedure (`framework/governance/CHG_REQUEST_FLOWS.md`,
`framework/governance/chg/`) before any implementation, not alongside it.

## What NOT to Reference

- Non-active layer artifacts in current authoring workflows
- Legacy subtype taxonomies when generating active artifacts

## CHG Gates — When to Reference

CHG gates are a governance overlay, outside normal layer authoring. During
routine layer work (authoring BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN),
you do NOT need to reference CHG gates.

**However**, when authoring a CHG record itself, `layers/09_CHG/` IS the
contract: `CHG-TEMPLATE.yaml` is the primary artifact, `templates/GATE_APPROVAL_FORM.md`
its companion, and `gates/GATE-*.md` define the checks. See especially
`gates/GATE-CODE_IMPLEMENTATION.md` §6.2 for a bubble-up. The CHG creation
checklist (§3.4 of `DOC_GOVERNANCE_CORE.md`) is a MANDATORY PROCESS GATE —
complete it BEFORE writing any CHG document.

## Delegation and concurrency pointers

- **Subagent Prompt ID Grounding Invariant:** When dispatching subagents or delegating
  tasks across layers, prompts MUST pass literal upstream element IDs (e.g. `BRD-001`,
  `PRD-F01`, `REQ-042`, `SPEC-DATA-01`, `IPLAN Step 3.2`) and exact file paths.
  Never summarize or omit upstream IDs. Subagent deliverables must cite those exact IDs
  in their traceability metadata without hallucinating new schemes.
- **Delegation integrity** (`NOTICES.md` Rule 1–2 harden): pass real upstream
  IDs in delegation prompts; after landing, re-validate every cited ID with a
  `grep -F` against its source file plus a `sort | uniq -d` duplicate check.
- **Concurrency traps** (`NOTICES.md` §Concurrency traps): verify-3 on
  subagent landings, no whole-tree git operations with live agents, confirm
  layer detection before trusting a clean lint, force-verify governed
  archives with `git ls-files` / `git check-ignore -v`.
- **§3.13 gate restatement:** the IPLAN Gate requires an `In Progress` IPLAN
  (referencing the authorizing CHG, files listed in its manifest) BEFORE any
  code file is written. The only exempt path is CHG→SDD→IPLAN bootstrap
  authoring itself — creating the governance records is not "code".
