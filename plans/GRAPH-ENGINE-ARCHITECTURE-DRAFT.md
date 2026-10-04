# Graph-Based SDD Engine — Architecture Description

| Field | Value |
|---|---|
| Status | **DRAFT** — design stage, not reviewed, not approved |
| Scope | v1 authoring engine: autonomous F1 greenfield runs through Verified IPLAN |
| Engine home | Separate new repository (consumes this framework via `.aidoc/` install) |
| Framework version | Pinned per release via `FRAMEWORK_SPEC_VERSION` (see §3) |

## 1. Purpose

Define a graph-based runtime engine — a peer to what the archived Hermes and
Claude plugin were — that **executes** the framework instead of merely
documenting it. Given seed documents plus a change request, the engine
autonomously authors the SDD layer chain, enforces framework checks as inline
transition guards, obtains C3 approval from a qualified approver, and emits a
**Verified IPLAN** as its v1 output. Code execution and EVAL loops are deferred
to v2.

Non-goals for v1: code execution, EVAL, F2/F3/F4 flows, Review Saga automation,
any change to `framework/` itself.

## 2. Locked decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Engine runs **autonomously** from seed + request to Verified IPLAN | Founder directive; human effort concentrated at approval, not authoring |
| D2 | Engine lives in a **separate new repo**, consuming the framework like any consumer project | Keeps `framework/` engine-agnostic; engine is a consumer, not a fork |
| D3 | v1 implements the **F1 greenfield chain first** | Full 10-layer authoring is the concept-proving showcase |
| D4 | **C3 approval required**; approver may be a human **or an independent LLM judge**; **self-approval prohibited** | Preserves the approval gate while keeping runs autonomous |
| D5 | **Seed provided externally** (human or other agent); engine ingests, pins, and freezes it | Engine never authors seed; clear input boundary |
| D6 | Framework consumed via **`.aidoc/` install** at a pinned version | Standard consumer mechanics; upgrades are re-install + re-verify |
| D7 | v1 **stops at Verified IPLAN**; execution deferred to v2 | Bounds v1 to authoring; execution is a separate design problem |

## 3. Relationship to the framework

- The framework spec (`framework/`, templates, `LAYER_REGISTRY.yaml`,
  `sdd_doc_lint/`) is **normative and untouched**. All rule logic stays there.
- The engine reads templates, registry, gates, and lint entry points from its
  installed `.aidoc/` snapshot and declares the pinned
  `FRAMEWORK_SPEC_VERSION` in every run record, so behavior is reproducible
  against a spec snapshot.
- Framework checks (`chg_lint`, `bugfix_lint`, trace utilities, template
  conformance) are invoked as **transition guards**. The engine orchestrates;
  it never reimplements rule logic.
- Framework upgrades propagate as: re-install `.aidoc/` → re-run engine
  parity checks (graph edges ≡ spec transitions) → cut an engine release.

## 4. Architecture overview

```
seed/ + request  ──▶  SEED INGESTION ──▶  SUPERVISOR GRAPH ──▶ APPROVAL GATE ──▶ Verified IPLAN
        (external)      (validate, pin,      (one subgraph         (human or
                         freeze, record       per layer L1–L8,       independent
                         provenance)          author→validate→       LLM judge;
                                              revise loops)          self-approval
                                                                          guard)
                                                 │  ▲
                                                 │  │ guards call into
                                                 ▼  │ .aidoc lint/rules
                                              CHECKS (chg_lint, template
                                              + trace conformance)
                                                 │
                        TELEMETRY EXPORTER ◀─────┘
                        (OTLP → LangFuse; advisory only,
                         never a gate input)
```

### 4.1 Seed ingestion

Validates seed shape (`seed/architecture/`, `seed/agent-surface/`), records
provenance (source identity: human or agent id), pins content hashes, and arms
the **seed-freeze guard**: after the first BRD is authored, any seed change
fails the run (`SEED_CONTRACT.md` R1, enforced mechanically).

### 4.2 Supervisor graph (LangGraph)

Owns F1 chain order and run state: artifact versions per layer, gate verdicts,
retry counts, judge/author identities. It sequences the layer subgraphs
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN, threading each layer's
verified YAML as input context to the next. Bounded retries per layer; on
exhaustion the run transitions to terminal `ESCALATED` with findings attached.

### 4.3 Layer subgraph template (uniform for L1–L8)

Each layer runs `author → validate → revise`:

- **author**: drafts the layer YAML from the pinned `.aidoc` template, citing
  upstream element IDs per the layer's `required_tags`.
- **validate**: runs template conformance, upstream-trace resolution, and the
  layer's gate criteria. All findings are structured (rule id + location).
- **revise**: re-prompts the author with findings attached. Loop bounded by
  OQ-3 retry budget; success advances the supervisor, exhaustion escalates.

Layer 8 (IPLAN) replaces generic authoring with the **IPLAN compiler** (§4.4).

### 4.4 IPLAN compiler

Compiles the verified upstream chain (SPEC test definitions, TDD cases, trace
graph) into an IPLAN carrying manifest, implementation steps, and verification
commands; self-validates against the IPLAN template and the IPLAN-gate
equivalent (manifest covers every touched file, test cases present) before
the run may advance to approval.

### 4.5 Approval gate

The run cannot emit its output until a qualified approval is recorded:

- Approver ∈ {human, independent LLM judge}; **author identity ≠ judge
  identity** enforced by guard (§6, G-APR-01).
- The judge receives the full verified chain + IPLAN and returns accept /
  reject-with-findings. Rejection routes back to the affected layer subgraph
  (see OQ-2).
- Both the judge verdict and (for human approval) the sign-off are recorded in
  the run journal and carried into the output's approval record.

### 4.6 Run store and journal

Each run gets an isolated directory (see OQ-4) holding: input manifest (seed
hashes, request, framework version), per-layer artifacts with versions,
structured validation findings per attempt, approval record, and the final
Verified IPLAN. The journal on disk is the **durable record**; the LangGraph
checkpointer is ephemeral resume state only — on any disagreement, disk wins.

### 4.7 Telemetry exporter

Maps node executions to `ENGINE_TELEMETRY.md` spans (`aidoc.attempt`,
`aidoc.gate_verdict`, `aidoc.*` correlation attributes) and exports via OTLP
to LangFuse. Spans carry IDs, counts, and verdicts only — no prompt text,
artifact bodies, or secrets. Telemetry never feeds back into a gate verdict.

## 5. v1 output: the Verified IPLAN handoff contract

The engine emits the full verified layer chain plus the Verified IPLAN.
"Verified" at v1 means: template-conformant, trace-complete against upstream
IDs, gate-passing, and C3-approved. It explicitly does **not** mean
implemented or EVAL-passed — implementation evidence arrives with v2. The
handoff package MUST carry: framework version pin, seed hashes + provenance,
per-layer versions, approval record (approver identity + verdict), and the
finding history, so a v2 executor or human can reproduce and trust the result.

## 6. Guard catalog (v1)

| ID | Guard | Framework source |
|---|---|---|
| G-SEE-01 | Seed immutable after first BRD (hash-pinned) | `SEED_CONTRACT.md` R1 |
| G-CHN-01 | Layers authored in registry order; no layer skipped | `LAYER_REGISTRY.yaml` (`downstream`) |
| G-TRC-01 | Every `required_tags` reference resolves to an existing upstream element | `TRACEABILITY.md`, trace utilities |
| G-IPLAN-01 | IPLAN manifest covers every touched file; test cases present | IPLAN gate (§3.13) |
| G-APR-01 | Approver identity ≠ any author identity on the run (no self-approval) | D4; cf. `09_CHG/README.md` §C3 |
| G-APR-02 | No output emitted without a recorded accept verdict | D4; CHG lifecycle |
| G-TEL-01 | No prompt/artifact/secret content in telemetry spans | `ENGINE_TELEMETRY.md` |

## 7. Open questions

### OQ-1 — Judge-independence criterion

What makes an LLM judge "independent" of the author: a separate session with
the same model, a different model, or a different model family?

- **Recommendation:** require a **different model identity** (different model
  id and a fresh session with no shared context) at v1, recorded in the
  verdict provenance. Same-model separate-session is too easy to game and
  hard to audit; different-family is stronger but constrains deployments.
  Revisit toward stricter (family separation) if judge-failure analysis
  warrants it.

### OQ-2 — Judge disagreement handling

When the judge rejects, does the run revise-and-resubmit to the same judge,
route to a second judge, or escalate to a human?

- **Recommendation:** **revise-and-resubmit to the same judge, bounded** (e.g.
  max 2 resubmissions), then **escalate to a human** with the full finding
  history. Same-judge resubmission preserves context; the bound prevents
  author↔judge oscillation; human escalation keeps a person at the end of
  every contested path. Second-judge routing adds complexity without a proven
  need at v1.

### OQ-3 — Retry budgets and escalation semantics

How many author→validate→revise cycles per layer, and what exactly does
`ESCALATED` contain and allow?

- **Recommendation:** **3 attempts per layer** (1 initial + 2 revises), then
  `ESCALATED`. The escalation record carries: layer, all attempts' findings,
  upstream versions consumed, and a resume pointer so a human-fixed artifact
  can re-enter validation without re-running the chain. Keep the budget
  configurable per deployment, default 3.

### OQ-4 — Run-artifact layout

What directory layout do runs use inside the engine repo (or its run store)?

- **Recommendation:** content-addressed run directories,
  `runs/<date>/<run-id>/` with fixed subpaths (`input/`, `layers/`,
  `findings/`, `approval/`, `output/`), `run-id` derived from
  request-hash + framework-version + timestamp. Fixed subpaths let v2
  executors and auditors navigate any run blind; content addressing keeps
  re-runs comparable.

### OQ-5 — Supported LLM runtime(s)

Which model providers does the engine support at v1 — one pinned provider,
several via an abstraction, or bring-your-own-key to any OpenAI-compatible API?

- **Recommendation:** a **small provider interface** (complete-with-schema +
  usage-report) with **one reference implementation** (whichever provider the
  team operates first) at v1. The interface keeps the door open; a single
  reference keeps v1 shippable. Judge-vs-author model separation (OQ-1) is
  enforced at the identity layer, orthogonal to provider count.

### OQ-6 — LangFuse hosting

Self-hosted LangFuse, LangFuse Cloud, or OTLP-to-anything with LangFuse as one
option?

- **Recommendation:** export **OTLP to a configurable endpoint**, document
  LangFuse (self-hosted first) as the reference backend. The engine depends
  only on the OTLP mapping, never on LangFuse APIs — consistent with the
  framework's backend-agnostic telemetry stance and keeps PII-sensitive
  deployments self-contained.

## 8. Conformance and risk notes

- **AI-approver extension.** The current framework spec permits AI verdicts at
  review gates, never at approval gates (GATE-SPEC-E004; cf. #784). Engine v1
  accepting LLM-judge C3 approvals is therefore an **engine-level extension**:
  document it as such in the engine repo, mark conformance scope explicitly,
  and optionally propose a framework governance change (bounded AI-approver
  tier) as follow-up work. Do not silently treat judge approval as
  spec-conformant.
- **Checkpointer precedence.** LangGraph checkpointers invite treating resume
  state as truth. The run journal on disk is truth; the checkpointer is a
  cache. State this in the engine's top-level README, not just here.
- **Semantic misclassification.** Guards enforce syntax (shapes, traces,
  identities); a well-formed but wrong artifact still passes them. The judge
  (OQ-1/OQ-2) is the only semantic backstop at v1 — size judge prompts and
  budgets accordingly.
- **Cost control.** Autonomous multi-layer runs with revise loops consume
  significant tokens. The supervisor SHOULD enforce a per-run token/cost cap
  with graceful `ESCALATED` on breach (telemetry already carries the usage
  attributes to implement this).

## 9. v2 outlook (out of scope, recorded for continuity)

Code execution per Verified IPLAN; EVAL cycles and live closeout; F2/F3/F4
flows; Review Saga automation; learning loops over run corpora. Each needs its
own design pass — this document intentionally does not draft them.

## Appendix A — References

- `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` — the 10-layer flow
- `framework/governance/CHG_REQUEST_FLOWS.md` — F1–F4 router
- `framework/governance/SEED_CONTRACT.md` — seed lifecycle (R1 freeze rule)
- `framework/governance/ENGINE_TELEMETRY.md` — span/attribute standard
- `framework/governance/REVIEW_SAGA.md` + `saga.schema.json` — lifecycle
  state-machine precedent
- `framework/layers/09_CHG/README.md` — CHG lifecycle, C3 approval rule
- `framework/registry/LAYER_REGISTRY.yaml` — layer order and trace fan-in
- `sdd_doc_lint/` — guard implementations (`chg_lint.py`, `bugfix_lint.py`,
  `trace_graph.py`)
