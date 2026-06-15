# IPLAN Ecosystem — Roles, Pipeline & Contract Divergence

> Cross-repo reference note. The IPLAN concept spans three sibling repos in the
> `aidoc-flow` family. This note records each repo's intended role, the pipeline
> between them, and the known divergence in how each currently defines an IPLAN.
> An identical copy lives in all three repos (see **Cross-references** below).
>
> **You are here: `aidoc-flow-framework` — the IPLAN _author_ (SDD Layer 8).**

## Roles

| Repo                               | Role                | Responsibility (authoritative doc)                                                                                                                                                |
| ---------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `aidoc-flow-framework` (SDD)       | **Authors** IPLANs  | Layer 8 — turns SPEC/TDD into an approved implementation plan (`IPLAN-NN`). Template: `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`.                                            |
| `aidoc-flow-iplanic`               | **Manages** IPLANs  | Control plane — import, immutable hash-bound versioning, validation, approval, executor dispatch, completion gate, signed evidence. Standard: `docs/standards/IPLAN-STANDARD.md`. |
| `iplan-runner` (IOPS)              | **Executes** IPLANs | Remote execution worker — runs the plan, produces an append-only ledger + independent gate + handover receipt, emits signed facts. Intake: `framework/intake/INTAKE_CONTRACT.md`. |

Intended pipeline:

```text
framework (author) → iplanic (manage / version / dispatch / gate)
                   → IOPS (execute) → iplanic (record evidence, gate completion)
```

> **iplanic is optional — the executor is local-first.** IOPS can run an approved
> IPLAN straight from the framework (file intake) with a fully local, signed,
> append-only ledger + independent gate + handover, and never contact iplanic
> (**standalone** mode, including fully **offline**). iplanic dispatch
> (`intake --payload`) and evidence relay (`emit-events`) are **additive** — used
> when iplanic manages the lifecycle as the system-of-record. The two hops
> through iplanic above describe the **with-iplanic** mode; standalone is just
> `framework (author) → IOPS (execute, local ledger / gate / handover)`. See
> iplan-runner's README "Operating modes".

## Authoritative IPLAN docs per repo

- **framework:** `framework/layers/08_IPLAN/` — `README.md`, `IPLAN-TEMPLATE.yaml`,
  `IPLAN-00_index.TEMPLATE.yaml`.
- **iplanic:** `docs/standards/IPLAN-STANDARD.md`, `IPLAN-DEFINITIONS.md`,
  `IPLAN-MANAGEMENT.md`; `docs/PROTOCOLS.md`; `schemas/iplan-*.schema.json`,
  `task.schema.json`, `execution-event.schema.json`; `docs/standards/templates/`.
- **IOPS:** `framework/intake/INTAKE_CONTRACT.md` + `IPLAN-INTAKE-TEMPLATE.yaml`;
  `framework/execution/` (ledger / verify / chain / audit); `framework/handover/`;
  `plans/PLAN-013_iplanic-remote-executor-conformance.md` (IOPS↔iplanic gap analysis).

## Contract divergence (as of 2026-06-07)

All three stamp `document_type: iplan-document`, but the shapes differ:

| Aspect          | framework L8 (author)                           | iplanic (manage)                                                | IOPS (execute)                                       |
| --------------- | ----------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------- |
| schema_version  | 1.0                                             | 1.3-draft                                                       | intake 1.0                                           |
| sections        | 6                                               | 13                                                              | 4 (its own `iplan-intake`)                           |
| unit of work    | `file_manifest` (files)                         | `step → work_order → todo`                                      | flat `task_graph`                                    |
| executor ctx    | —                                               | `executor_context` (forbidden_paths, mcp_tools, secrets_policy) | `isolation_scope.allowed_roots`                      |
| readiness       | "IPLAN-Ready ≥90" (TDD-layer score, not in doc) | `verification.exec_ready_score` + EXEC-Ready gate               | `intake_control.exec_ready_score ≥ 90`               |
| completion gate | — (status only)                                 | `completion_gate` (Iplanic-owned)                               | ledger well-formedness veto                          |
| resume          | `session_handoff.sessions[]`                    | `handoff` + `navigation`                                        | `run_state` + idempotent `resume`                    |
| identity        | `iplan_id`, `source_spec`                       | org/project/iplan/plan_version/run/task/step/executor + aliases | client/project/allowed_roots, source_iplan, agent_id |
| TMP-IPLAN       | yes (bugfix, 7-day, disposable)                 | yes (first-class: return_gate, promotion)                       | none                                                 |
| signing         | —                                               | ed25519 / hmac-sha256 (execution-event, evidence seal)          | hmac-sha256 over a hash-chained ledger               |

Two consequences:

1. **iplanic has evolved beyond the framework template it names as upstream.**
   iplanic's 13-section standard (step/work_order/todo, executor_context,
   completion_gate, runtime task payload, chains, evidence bundles, protocols) is a
   far richer artifact than the framework's 6-section L8 template. They share the
   name and a few concepts (file ordering, traceability/lineage, TMP-IPLAN,
   session/handoff) but not the structure.
2. **IOPS consumes an assumed SDD shape that matches neither real template.** Its
   default ingest mapping reads `document_control.iplan_id` (matches L8), but
   `exec_ready.score`, `tasks[]`, and `isolation_scope` are not in the framework L8
   template (L8 has no `exec_ready` block, uses `file_manifest` not `tasks`, and has
   no `isolation_scope`) nor in iplanic's top-level shape. IOPS's
   `examples/IPLAN-EXAMPLE.yaml` is an idealized SDD-IPLAN, not the real L8 format.

## Interop status

- **Conceptually:** author → manage → execute is the agreed model.
- **Operationally:** the handoffs are not wired. IOPS↔iplanic conformance is
  _planned only_ (IOPS `plans/PLAN-013`, unimplemented) and targets just the
  runtime-executor surface (payload intake, signed event shape, executor_context) —
  not the document/chain/lifecycle parts of iplanic's standard. The
  framework↔iplanic document formats are not reconciled.

## Open question / next step

End-to-end interop needs a single canonical IPLAN contract. Options:

1. Declare **iplanic's IPLAN-STANDARD the canonical Layer 8** and regenerate the
   framework L8 template + IOPS intake mapping from it.
2. Keep the framework L8 template canonical for authoring; have iplanic define an
   explicit **import/normalization** from L8 → its richer internal model (iplanic
   already has an import pipeline + `iplan-import-result` schema).
3. Pin IOPS's intake to iplanic's **dispatched task payload** (per PLAN-013) rather
   than an assumed authoring shape, against whichever format becomes canonical.

Recommended: **option 2** (least disruptive) — keep L8 as the authoring format,
make iplanic's import the formal bridge, and have IOPS consume iplanic's dispatched
task payload rather than an assumed authoring shape.

## Cross-references

This note is mirrored (identically) in all three repos:

- `aidoc-flow-framework` → `framework/layers/08_IPLAN/IPLAN-ECOSYSTEM.md`  ← _this file_
- `aidoc-flow-iplanic` → `docs/standards/IPLAN-ECOSYSTEM.md`
- `iplan-runner` → `docs/IPLAN-ECOSYSTEM.md`
