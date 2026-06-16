# Definition of Done

Engine-agnostic completion criteria for an SDD **artifact** and for a **change**
to the spec. This is a *light contract*: it names *what must be true* before work
is considered done; it does not prescribe *how* an engine or platform checks it
(coverage tools, CI, labels, and review tooling are platform/ops bindings, not
spec). It complements the readiness gate (`DOC_GOVERNANCE_CORE.md`), the quality
loop (`REVIEW_REMEDIATION_FLOW.md`), and the change gates (`chg/`).

## Artifact-level (any layer, BRD … IPLAN)

An artifact is **Done** when:

- It conforms to its layer **template** and carries the required **traceability
  tags** (`TRACEABILITY.md`) — the cumulative chain is intact upstream.
- It has passed **review** with **no blocking findings** (severity *critical* or
  *medium*; see `REVIEW_REMEDIATION_FLOW.md`), or every blocking finding has been
  remediated and re-reviewed.
- Its **readiness score** meets the layer **gate threshold**.
- The review was **independent of the author** (judge ≠ generator) — an artifact
  is never cleared only by the agent that produced it (mirrors CHG **C1**: no
  self-approval).
- The **documents of record** affected by the work are updated in the same change
  (`DOC_GOVERNANCE_CORE.md` Principle 8).
- Its `status` is **Approved** (per the layer template lifecycle).

## Change-level (a change to the spec)

A change to the framework spec (`framework/**` — templates, governance, registry,
`VERSION`) is **Done** when it has **passed GATE-SPEC** (`chg/gates/GATE-SPEC_FRAMEWORK.md`):
provenance + SemVer impact recorded (`major ⇒ C3`; additive may be C2; never C1),
`VERSION` bumped, `CHANGELOG` updated, every platform's `FRAMEWORK_SPEC_VERSION`
re-declared to match, the **conformance suite green**, and **human approval**
obtained (a validator never grants approval — only a human signs; per GD-01).

## Human-in-the-loop tier

The level of required human sign-off scales with risk:

| Tier | Scope | Human sign-off |
|------|-------|----------------|
| **Routine** | ordinary artifacts/changes outside the spec | the independent review gate is sufficient; a human is required **only on escalation** (the iteration cap is reached without convergence) |
| **Spec / governance** | any change to `framework/**` or a governance standard | **human approval is always required** (GATE-SPEC / GD-01), in addition to the review gate |

This tiering keeps routine work moving on the automated gate while holding
spec-shaping changes to explicit human approval. *(How a platform enacts each
tier — protected-branch rules, required reviewers — is a platform binding, not
part of this contract.)*

## Cross-references

- `REVIEW_REMEDIATION_FLOW.md` — the review→remediation→gate loop, `pre_merge`
  trigger, iteration cap, and severity classes.
- `DOC_GOVERNANCE_CORE.md` — governance principles + the readiness-gate baseline.
- `chg/gates/GATE-SPEC_FRAMEWORK.md` + `DECISIONS.md` (GD-01) — the spec-change gate.
- `TRACEABILITY.md` — the cumulative-tag chain a review checks.
