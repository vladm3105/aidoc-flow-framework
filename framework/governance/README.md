# Governance

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.53.0 |


Engine-agnostic governance standards for the SDD framework. These documents
define the rules that every artifact and platform must conform to, independent
of which engine executes the workflow.

## Document Lifecycle

Every governance document carries a **Document Control** block (GD-24) with:
Version, Status, Last Updated, Author, and Framework Version. This tracks
document freshness and authorship across framework versions. The convention
uses a `## Document Control` Markdown table placed after the first heading.

Changes to any governance document follow the CHG overlay — specifically
**GATE-SPEC** for changes to `framework/` itself. The process:
classify → archive originals → update → verify → record in CHG. See
[`layers/09_CHG/`](../layers/09_CHG/) for the full change management layer.

## Documents

| File | Covers |
|------|--------|
| `DOC_GOVERNANCE_CORE.md` | Core governance principles — single source of truth, YAML-first templates, immutability, validation baseline. |
| `ID_NAMING_STANDARDS.md` | Document IDs, element IDs, traceability tags, and file-naming formats. |
| `TRACEABILITY.md` | The 10-layer traceability chain, necessary-upstream tagging, and readiness gates. |
| `TAG_SYNTAX.md` | `@`-tag form reference: per-layer punctuation, element-vs-document granularity (GD-03), pipe-delimited cardinality, the self-tag / downstream carve-outs, and the `@chg:` provenance back-reference (a non-trace tag; GD-11). |
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
| `DECISION_WORKFLOW.md` | The decision-making workflow — how governance decisions are proposed, reviewed, and ratified. |
| `MODULE_LAYOUT.md` | The module structure and organization conventions for the framework. |
| `NOTICES.md` | Important notices, deprecations, and breaking changes across framework versions. |
| `SELF_LEARNING.md` | Self-learning governance loop — how the framework captures and applies lessons learned. |

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

### Framework self-changes (GATE-SPEC)

When modifying `framework/` itself (templates, governance, registry, VERSION),
the change routes through **GATE-SPEC** — the meta gate. Requirements:

| Criterion | C2 | C3 |
|-----------|----|----|
| Provenance documented | Yes | Yes |
| SemVer impact classified | Yes | Yes |
| Change level ≥ C2 | Yes | Yes (major ⇒ C3) |
| `framework/VERSION` bumped | Yes | Yes |
| Both platforms re-declare `FRAMEWORK_SPEC_VERSION` | Yes | Yes |
| Conformance suite green | Yes | Yes |
| `CHANGELOG.md` updated | Yes | Yes |
| Human approval | Maintainer + 1 platform owner | Maintainer + both platform owners |

All framework changes also require:
1. **Archive** originals to `archive/{CHG-ID}/` before modification
2. **Document Control** blocks updated (version bump, last_updated, framework_version)
3. **GD entry** in `DECISIONS.md` for significant decisions

## `.aidoc/` Governance (`aidoc/`)

The `aidoc/` directory holds the governance documents for the `.aidoc/` project
override layer — the contract that defines how projects customize the framework
without forking.

| File | Covers |
|------|--------|
| `AIDOC.md` | Canonical reference for the `.aidoc/` project override layer — directory structure, discovery rule, symlink convention. |
| `AIDOC-SCAFFOLD-TEMPLATE.md` | Template for bootstrapping a new project's `.aidoc/` directory. |

The override contract (`ADAPTATION.md` §10) governs how `.aidoc/project/`
mirrors the framework structure and takes precedence via the discovery rule.
