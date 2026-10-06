# Engine Telemetry Guidance

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-02 |
| Author | Framework Maintainer |
| Framework Version | 0.86.1 |

Engine-agnostic recommendations for **how a conforming engine emits
observability telemetry** so that traces from different engines are mutually
intelligible and can be joined on the change records they implement. The
machine-readable record of *what happened* stays the saga journal
(`REVIEW_SAGA.md` + `saga.schema.json`) and the EVAL report — this document
standardizes only the *span/attribute names* an engine uses when it chooses
to emit traces. It mandates no vendor, no backend, and no SDK.

## 1. Status of this guidance

Every statement in §§2–4 is a **SHOULD** or a guardrail **MUST NOT**
conditional on emitting — not an unconditional MUST. An engine that emits
no telemetry still conforms. An engine that emits telemetry SHOULD follow
this document so its traces compare with other engines' traces.

- **Backend-agnostic.** Attribute names below follow the OpenTelemetry
  GenAI semantic conventions where they exist (`gen_ai.*`); the
  `aidoc.*` attributes are framework-defined correlation keys. Any
  OTLP-compatible backend — or no backend at all — satisfies this
  guidance. Telemetry is advisory evidence; it never gates a verdict.
- **No SDK mandated.** An engine MAY use any OpenTelemetry SDK, a
  hand-rolled OTLP emitter, or log-structured spans it converts at
  export time. Conformance is judged on emitted names, never on the
  emitting library.
- **No PII.** Spans carry counts, IDs, and verdicts — never prompt
  text, artifact bodies, or secrets.

## 2. Standard spans and attributes

An emitting engine SHOULD use these span names:

| Span name | One per | Carries |
|-----------|---------|---------|
| `aidoc.attempt` | Authoring or audit attempt (one try at producing or scoring an artifact) | Usage + cost attributes below |
| `aidoc.gate_verdict` | Gate evaluation (one gate decision over an artifact) | Verdict attribute below |

Attribute names on those spans:

| Attribute | Meaning | Example |
|-----------|---------|---------|
| `gen_ai.request.model` | Model identifier behind the attempt | `"example-model-1"` |
| `gen_ai.usage.input_tokens` | Input tokens consumed by the attempt | `1200` |
| `gen_ai.usage.output_tokens` | Output tokens consumed by the attempt | `800` |
| `aidoc.cost_microcents` | Billed cost of the attempt in microcents (integer; absent when unknown — never estimate silently) | `4300` |
| `aidoc.layer` | SDD layer the attempt or verdict concerns | `"SPEC"` |
| `aidoc.verdict` | Gate outcome (`pass`, `pass_with_notes`, `fail`, `blocked`) — on `aidoc.gate_verdict` spans | `"pass"` |

`gen_ai.*` names track the OpenTelemetry GenAI conventions; where that
upstream renames an attribute, the upstream name wins and this table is
updated by a framework-spec change. `aidoc.*` names are stable: renaming
one is a breaking spec change.

## 3. Correlation IDs

Every span an engine emits SHOULD carry the change records it serves, so
traces join across engines on the work — not on engine-local IDs:

| Attribute | Meaning |
|-----------|---------|
| `aidoc.chg_id` | Authorizing CHG (e.g. `"CHG-38"`); absent for pre-CHG seed drafting |
| `aidoc.iplan_id` | Implementing IPLAN (e.g. `"IPLAN-38"`) |
| `aidoc.eval_id` | EVAL document when the span serves an eval cycle |

Engines MUST NOT join on saga-journal internals (saga IDs, journal
offsets): the journal is a local record, not a cross-engine key.

## 4. Emission discipline

- Emit spans **after** the attempt or verdict completes (telemetry
  observes; it never participates in the decision it reports).
- A failed export MUST NOT fail the attempt, the gate, or the run —
  telemetry loss is operational noise, handled engine-locally.
- Sample or drop freely under load; document the sampling policy where
  the backend config lives (engine-local, out of framework scope).

## 5. What this does not cover

- **Saga journaling** (`REVIEW_SAGA.md`, `saga.schema.json`) is
  unchanged: the journal remains the normative local record of the
  create→review→revise loop. Telemetry duplicates none of its
  semantics.
- **EVAL verdict mechanics** are unchanged: verdicts, evidence
  artifacts, and the `Completed → Verified` flow keep their existing
  meaning. A span is not evidence and a verdict needs no span.
- **Cost accounting** is informational: `aidoc.cost_microcents`
  supports evaluation-time comparison, not billing.

## 6. Conformance

Advisory in v1: no deterministic check asserts span names yet. A future
linter check (emitted spans carry the §2–§3 names) is conceivable but
not required by this document.
