# Governance

Engine-agnostic governance standards for the SDD framework. These documents
define the rules that every artifact and platform must conform to, independent
of which engine executes the workflow.

## Documents

| File | Covers |
|------|--------|
| `DOC_GOVERNANCE_CORE.md` | Core governance principles — single source of truth, YAML-first templates, immutability, validation baseline. |
| `ID_NAMING_STANDARDS.md` | Document IDs, element IDs, traceability tags, and file-naming formats. |
| `TRACEABILITY.md` | The 8-layer traceability chain, necessary-upstream tagging, and readiness gates. |
| `TAG_SYNTAX.md` | `@`-tag form reference: per-layer punctuation, element-vs-document granularity (GD-03), pipe-delimited cardinality, and the self-tag / downstream carve-outs. |
| `DIAGRAM_STANDARDS.md` | Mermaid-only diagram requirement and the C4 + DFD + sequence ownership model. |
| `THRESHOLD_NAMING_RULES.md` | Naming, boundary, and usage rules for thresholds, limits, and timing parameters. |
| `SECURITY_REVIEW.md` | Safety checks for agent-authored artifacts — secret leakage, prompt-injection, provenance, active-content sanitization. |
| `REVIEW_REMEDIATION_FLOW.md` | The engine-agnostic review→remediation→gate quality loop, its trigger points (`on_author`, `on_gate_fail`, `pre_promotion`, `pre_merge`), and the independent `pre_merge` review gate (judge≠generator, severity classes, escalation). |
| `DEFINITION_OF_DONE.md` | Engine-agnostic completion criteria for an artifact and for a spec change, plus the risk-tiered human-in-loop. |
| `REVIEW_TEAM.md` | The multi-persona review-team model — crews, the shared blackboard, scoring/conflict/gate rules, and create/review/remediate shapes. |
| `REVIEW_CREWS.yaml` | Machine-readable per-layer review crews + scoring weights behind `REVIEW_TEAM.md`. |
| `REVIEW_SAGA.md` | The engine-agnostic saga lifecycle over the create→review→revise loop — state machine, transition table, journal schema, break-circuit policy. |
| `saga.schema.json` | Machine-readable JSON Schema for the saga journal (`saga.json`) behind `REVIEW_SAGA.md`. |
| `SEED_CONTRACT.md` | The `seed/` input tier — frozen historical input, total per-claim disposition (absorbed/rejected/deferred), BRD as the absorption point, and the `SEED01`-vs-auditor enforcement split. |
| `ADAPTATION.md` | The project-adaptation surface — how a consuming project adapts the flow without forking. |
| `ADAPTATION_SURFACE.yaml` | Machine-readable closed knob registry behind `ADAPTATION.md`. |
| `PROFILE-TEMPLATE.yaml` | The bootstrap template an engine copies to seed a project's `.aidoc/profile.yaml` (adaptation-knob overrides only). |
| `AUTHORING_STYLE.md` | Token-efficient authoring rules — eliminations, form enforcement, form preferences, size targets. Audit-enforced. |
| `LINT_RULES.md` | Normative catalog of the deterministic lint rule IDs a conforming linter emits (meaning, severity, defining contract). |
| `DECISIONS.md` | Durable register of decisions about the spec and its governance (spec-affecting decisions graduate here). |
| `FRAMEWORK_FEEDBACK_LOG.md` | The empirical-feedback register — friction found while applying the spec to real projects (the canonical reference of DOC_GOVERNANCE_CORE Principle 9). |

## CHG Overlay (`chg/`)

The `chg/` directory holds the Change Management overlay — a governance overlay
for managing changes to existing artifacts (gate definitions, the CHG template,
approval and post-mortem companions). It also carries **GATE-SPEC**, the *meta*
gate that governs changes to the `framework/` spec itself (CHG-D1).

CHG is **spec-only** in the framework: the spec defines the gates and their
checks; each consuming platform implements the enforcement against this shared
contract (a record validator for the record-level checks, continuous
integration for the diff-aware and suite checks, protected-branch review for the
human approval). This model is recorded formally as **GD-01** in `DECISIONS.md`.
