# Review, Remediation & Gate Flow

The layer flow (BRD → … → IPLAN) describes how artifacts are **created**. This
document models the orthogonal **quality loop** every artifact passes through —
review, remediation, and gating — and names the **trigger points** where an
engine may attach that loop. It is an engine-agnostic **light contract**: it
defines *what* happens and *when*, and what an engine must surface; it does not
prescribe *how* an engine implements the checks.

## The quality loop

Each artifact moves through this loop before it is allowed to drive the
downstream layer:

```text
Draft ─▶ Review ─▶ (findings + readiness score)
             │
             ├─ score ≥ gate ─▶ Gate pass ─▶ Approved ─▶ downstream
             │
             └─ score < gate ─▶ Remediate ─▶ (re-review) ─┐
                                    ▲                      │
                                    └──────────────────────┘
```

- **Review** produces *findings* (concrete, located issues) and a *readiness
  score* against the layer's gate threshold (the existing readiness gate —
  e.g. ≥ 90/100 before downstream generation).
- **Remediation** applies fixes for the findings, then the artifact is
  re-reviewed. The loop repeats until the gate passes.
- **Gate** is the existing readiness/CHG checkpoint — this document does **not**
  change gate thresholds or the change-management gates; it names the review and
  remediation *stages* that feed them.

This loop is layer-agnostic: it applies identically to every artifact (BRD …
IPLAN), using that layer's own template, required tags, and threshold.

### Iteration cap

The loop's *"repeats until the gate passes"* clause carries an implicit
upper bound: a saga that never converges cannot run forever. The framework
declares a **default iteration cap of 3** review→remediate cycles. At the
cap, the saga transitions to `PARTIAL_TIMEOUT` (per `REVIEW_SAGA.md`),
emits the artifact + saga journal as deliverables, and surfaces the
unresolved findings in the audit report. The cap is **not** a quality
gate (gate passage still requires the score), it is a non-convergence
guard.

The cap is **tunable per project** via the
`quality_loop.max_iterations` knob in `ADAPTATION_SURFACE.yaml`. Range
1-10; default 3. Engines reading the knob must:

1. Load the runtime profile (`.aidoc/profile.yaml`).
2. Read `quality_loop.max_iterations` if present.
3. Fall back to the default (3) if the field is missing, malformed,
   or the file is absent.
4. Treat values outside the 1-10 range as malformed (use default).

This cap is the documented stopping criterion that complements the
gate threshold: gate decides *did we converge?*, cap decides *did we
spend too long trying?*.

## Trigger points

A trigger point is a named moment in a project's lifecycle where an engine may
run part of the loop. The four canonical points:

| Trigger | Fires when | Loop action |
|---------|------------|-------------|
| `on_author` | An artifact is created or edited | Review the artifact → findings + readiness score |
| `on_gate_fail` | A review scores below the gate threshold | Enter remediation, then re-review |
| `pre_promotion` | Before generating/authoring the downstream layer | The gate must pass (review is current and ≥ threshold) |
| `pre_merge` | An artifact enters shared history (integration / pull request) | Run the review gate over the changed artifacts |

`on_author` and `pre_merge` are the two *automatable* points (an engine may fire
them without a human asking); `on_gate_fail` and `pre_promotion` are loop/flow
control that map to existing capabilities (remediation and the readiness gate).

## Light conformance contract

For each trigger point an engine **supports**, it MUST surface:

1. **Findings** — the concrete, located issues (not just a pass/fail).
2. **Readiness score** — the artifact's score against the layer gate threshold.
3. **Remediation path** — how to fix the findings (which capability the user or
   agent invokes next).

What an engine is **free** to choose:

- *How* a point is checked — a deterministic structural check, an LLM review, a
  server-side validator, or a combination.
- *Which* points it automates vs leaves on-demand (an engine need not support
  all four; it declares which it does).
- *Severity/blocking* behavior — e.g. an advisory write-time nudge vs a blocking
  integration gate.

Each engine **documents its own mapping** of trigger points → capabilities (in
that engine's own documentation, not here — this spec names the points; the
engines bind them).

> **Structural vs semantic.** A deterministic check (ID/tag forms, required
> sections, traceability presence) can run at `on_author`/`pre_merge` cheaply and
> repeatably; the full readiness *score* is a semantic judgment. An engine may
> use the deterministic check as a fast gate and defer the semantic score to its
> review capability — both are valid ways to satisfy the contract.

## Relationship to existing governance

- **Readiness gate (≥ threshold):** the `Gate` stage. Unchanged.
- **Change management (CHG gates):** govern *changes* to existing artifacts; the
  `pre_merge` trigger is where an engine runs the relevant gate on a change set.
- **`status` lifecycle** (Draft / In Review / Approved, per the layer templates):
  the loop's stages correspond to these statuses — `Review` ↔ In Review,
  `Gate pass` ↔ Approved.

## Cross-references

- `DOC_GOVERNANCE_CORE.md` — governance principles and the readiness-gate baseline.
- `TRACEABILITY.md` — the cumulative-tag chain a review checks.
- `chg/` — the change-management overlay (the `pre_merge`/gate machinery for changes).
- `../README.md` — the layer flow these artifacts are created in.
