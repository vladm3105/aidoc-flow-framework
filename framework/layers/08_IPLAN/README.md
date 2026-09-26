# 08_IPLAN — Implementation Plan

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.61.6 |


## C4 Model Position

IPLAN is part of the **Implementation Bridge** (L7-L8, no C4 level). It is the execution bridge between TDD and source code. C4-L4 (Code) diagrams belong to the source code layer, not to IPLAN documents.

## Purpose

Mandatory execution layer bridging TDD (L7) to source code. One IPLAN per SPEC component. Each IPLAN declares the file creation order (test-first from TDD), provides executable bash commands, tracks session progress across stateless executor calls, and maintains an audit trail from specification to delivered files.

IPLAN is Layer 8 of the unified SDD chain. The chain is initiated by modules/seed for new features, or by CHG requests for all changes. The execution model is the same in both cases.

## Index registry vs document schema

The `08_IPLAN/` directory holds **two distinct schemas**, so a naive "validate
every `IPLAN-*.yaml`" glob will misfire:

- **`IPLAN-00_index.yaml`** — `document_type: iplan-registry`. A registry of the
  permanent IPLANs; it carries **no `document_control`** and declares no element
  IDs or trace tags.
- **`IPLAN-NN_{slug}.yaml`** — `document_type: iplan-document`. The execution
  manifests, with full `document_control` + `@spec`/`@tdd` lineage.

**Validation:** `sdd_doc_lint` already special-cases index docs — it exempts
`artifact_type: *-INDEX` from the document-schema, trace-resolution, and element
checks. So the registry is validated as a registry, the documents as documents;
do not apply the `iplan-document` schema to `IPLAN-00_index`.

## Development/Work Plans (markdown)

Distinct from BOTH YAML artifacts above is the **development/work plan** — the markdown plan-of-record an agent writes in a repository's `plans/` directory before a change, covering objective, scope, approach, task sequence, verification, and review trail. Its structure, the work-type applicability rules, and the review discipline are specified in [PLAN_STANDARD.md](PLAN_STANDARD.md); the copy-paste working instance is the repository's `plans/PLAN-TEMPLATE.md`.

A development plan is a *design-and-review record* read by a reviewer to approve a change; the YAML IPLAN artifact is an *execution manifest* consumed by an agent step-by-step. A development plan may spawn an IPLAN as one of its tasks, but the two are not interchangeable. Adding this standard changes neither YAML artifact.

## Design Decisions

- **Mandatory layer** — one IPLAN per TDD/SPEC component, created when TDD reaches IPLAN-Ready >=90/100.
- **Test-first file order** — file_manifest declares test files before implementation files (TDD principle inherited from L7).
- **Session handoff protocol** — solves the stateless executor problem: each session reads the previous session's state, identifies the next incomplete step, and continues without regenerating completed work.
- **Implementation contracts embedded** — Type interfaces, exception hierarchies, and state machines live in the IPLAN (no separate contract files).
- **Code inventory for audit trail** — one entry per `file_manifest` path, seeded `planned` at Draft, then set to `created` / `modified` with session attribution and verification status.
- **Verified status is immutable** — once an IPLAN reaches Verified, it cannot be changed. CHG required for modifications.

## IPLAN Subtypes

`document_control.subtype` selects which section set an IPLAN carries
(`code_build | deploy | combined | audit_fix | bugfix`; default `combined` for
pre-0.19.1 IPLANs). `combined` stays the default — removing it would be a
breaking instance-format change; a future `devops` direction (infrastructure +
cutover under one umbrella) is noted but not adopted.

- **code_build** — new features from SPEC/TDD. File order: TDD test-first.
- **deploy** — cutover with rollback/smoke/canary/observability.
- **combined** — both sets (default).
- **audit_fix** — audit-driven fixes, ordered by severity (P0→P1→P2), not by
  TDD. Upstream is audit findings, so `source_spec` names the findings
  reference, `file_manifest[].tdd_ref` is not used, each entry carries
  `severity: P0/P1/P2/P3`, and `traceability.upstream` cites
  `audit_references`. Use for integration-readiness, security-review, and
  code-review findings. Do NOT use for new SPEC features (use `code_build`),
  and do NOT use for post-completion field defects (use `bugfix`).
- **bugfix** — post-completion defect repair parented on a closed IPLAN
  (Completed, merged-at-Completed with VERIFY pending, or Verified) via
  `parent_iplan` + `source_chg`. The manifest is scope-limited to repair
  files; the parent plan is never touched. See `IPLAN-TEMPLATE.yaml`
  `document_control` guidance for the normative step order, rollback markers,
  naming pattern, and no-fix-on-fix rule.

## IPLAN Baseline

| Area | IPLAN |
|---|---|
| Upstream contract | TDD + SPEC |
| Execution tracking | File manifest with status markers |
| Scope ownership | Execution-only (business scope remains in upstream docs) |
| Sequencing model | File-by-file test-first creation order |
| Validation reporting | `validation_results` per session handoff entry |

## TDD-case carrier (`tdd_ref`)

A file-manifest entry MAY name the TDD test cases it builds:

```yaml
- path: tests/unit/test_auth.py
  order: 1
  status: NOT_STARTED
  tdd_ref: "@tdd: TDD.01.04.aaaa | @tdd: TDD.01.04.bbbb"
```

Three rules govern it:

1. **The value is the tag, and it must be quoted.** YAML treats a leading `@` as a
   reserved indicator, so an unquoted value fails to parse. Several cases may share one
   scalar, pipe-delimited.
2. **The key and the tag share one line.** This mirrors the TDD layer's own
   `bdd_scenario:` / `bdd_ref:` carriers. A downstream check reads both from a single
   line, so **a citation listed only in the traceability block is not a build record** —
   that is the whole point of the carrier.
3. **Optional per entry.** A package initialiser or a config file legitimately realizes
   no test case. Completeness is judged from the TDD side — every declared test case
   should be named by some entry — not by requiring every entry to name a case.

The carrier is a field-name token, so it is not tied to one serialization: the same
rule applies wherever the manifest is rendered.

## Session Handoff Protocol

Each AI agent session reads the IPLAN in this order:

1. **Read session_handoff.sessions** — identify the last session's state
2. **Check file_manifest.files** — find next NOT_STARTED or PARTIAL file
3. **Read partial_work** description if resuming a PARTIAL step
4. **Continue from that point** — do NOT regenerate completed work
5. **Update file status** after completion or session end
6. **Append to session_handoff.sessions** with next_session_directive

**A Draft IPLAN carries `sessions: []`** — the trail is retrospective, appended by
each session as it ends, so at Draft there is nothing to record and step 1 falls
straight through to step 2. Writing a session entry while authoring asserts work
that has not happened. This is deliberately *unlike* the code inventory above,
which **is** seeded at Draft: that seed is derived from a set already known (one
entry per `file_manifest` path), whereas nobody knows the future sessions.
(GD-26; regressed and restored by CLEANUP-001.)

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
| `Completed` | Implementation done, awaiting validation (validatable, NOT terminal) | → Verified |
| `Verified` | Validation passed, **FINAL/FINITE** status | **None** (immutable) |

`Completed` is validatable, not terminal: the VERIFY window is still open (see
Validation Workflow below). A `Completed` plan merged before VERIFY keeps an
explicit open VERIFY obligation (index `validated_by` pending). Only `Verified`
is terminal. **Active** plans are `Draft | Approved | In Progress` — the §3.13
bug-fix exception covers active plans only. A defect found in closed output
(`Completed` past its window, or `Verified`) is repaired by a scoped `bugfix`
IPLAN parented on the closed plan (never by reopening it); recording lands in
the bugfix IPLAN + the authorizing CHG + the index.

## Validation Workflow (Completed → Verified)

Validation runs as EVAL cycles (CHG-08 #662 — the legacy create-IPLAN-VERIFY
flow below is superseded):

1. All `file_manifest` entries reach `DONE` + `verified: true`
2. Document status flips to `Completed`
3. Author (or reuse) the owning EVAL document (`EVAL-{NN}/EVAL-{NN}.yaml`)
4. Run eval cycle 1 (`initial_eval`) from `execution_commands.validation`;
   record `EVAL-{NN}/reports/EVAL-{NN}-RPT-001.yaml` (EVAL-REPORT-TEMPLATE)
5. If findings exist:
   a. Repair via a scoped `bugfix`-subtype IPLAN (`parent_iplan` + `source_chg`)
   b. Fix all critical findings
   c. Re-run the next cycle (`bug_fix_verification`)
6. When all findings resolved:
   a. Mark original IPLAN as `Verified` (FINAL/FINITE)
   b. Close the bugfix IPLAN per its rollback/resolution markers

## Verified IPLAN Immutability Rule

Once an IPLAN reaches `Verified` status, it becomes **immutable**:
- No fields may be modified
- No files may be added or removed
- Status cannot be changed back

To modify a Verified IPLAN:
1. Create a CHG record documenting the need for changes
2. Create a NEW IPLAN (IPLAN-NN+1) that references the original
3. The original IPLAN remains in `Verified` status as historical record

## Template

| File | Purpose |
|------|---------|
| `IPLAN-TEMPLATE.yaml` | **Default** — full template with embedded authoring guidance. Self-documenting for AI agents. |
| `IPLAN-VERIFY-TEMPLATE.yaml` | **Legacy validation** — superseded by the EVAL-RPT flow (CHG-08 #662); retained for existing readers. New validation authors EVAL-RPT reports; repairs use the `bugfix` subtype. |

**Downstream**: [10_EVAL](../10_EVAL/) — Evaluation & QA Governance

## Registry

For the authoritative plan registry (statuses, execution path, deferred items, cross-plan obligations, status history), see [IPLAN-00_index.TEMPLATE.yaml](IPLAN-00_index.TEMPLATE.yaml).
