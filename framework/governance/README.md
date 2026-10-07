# Governance

## Document Control

| Field | Value |
|---|---|
| Version | 1.5 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.88.4 |


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
Which flow a change takes — HOTFIX (Emergency), CODE2S (Type-R), CODE2C (F4),
SEED2C (F3), DIR2C (F2), or SDD2C (F1) — is routed by
[`CHG_REQUEST_FLOWS.md`](CHG_REQUEST_FLOWS.md) (ratified 0.57.0, CHG-06).

## Documents

| File | Covers |
|------|--------|
| `DOC_GOVERNANCE_CORE.md` | Core governance principles — single source of truth, YAML-first templates, dual-template architecture, immutability, validation baseline. |
| `GOVERNANCE_WORKFLOW_STANDARD.md` | Normative standard establishing the CNCF Serverless Workflow DSL (v0.8 YAML) for modeling, validating, and executing governance flows and multi-agent lifecycle state machines. |
| `IPLAN_WORKFLOW_STANDARD.md` | Normative standard mapping implementation planning, dependency DAGs, parallel phases, and saga rollback compensation to CNCF Serverless Workflow state machines. |
| `WORKTREE_FLOW.md` | Order-guarded worktree isolation, autonomous feature branching, PR watch, and post-merge branch deletion lifecycle rules (§3.8 order guard). |
| `ID_NAMING_STANDARDS.md` | Document IDs, element IDs, traceability tags, and file-naming formats. |
| `TRACEABILITY.md` | The 10-layer traceability chain, necessary-upstream tagging, and readiness gates. |
| `TAG_SYNTAX.md` | `@`-tag form reference: per-layer punctuation, element-vs-document granularity (GD-03), pipe-delimited cardinality, the self-tag / downstream carve-outs, and the `@chg:` provenance back-reference (a non-trace tag; GD-11). |
| `DIAGRAM_STANDARDS.md` | Mermaid-only diagram requirement, C4 + DFD + sequence ownership model, and CNCF workflow state diagram bindings. |
| `THRESHOLD_NAMING_RULES.md` | Naming, boundary, and usage rules for thresholds, limits, and timing parameters. |
| `SECURITY_REVIEW.md` | Safety checks for agent-authored artifacts — secret leakage, prompt-injection, provenance, active-content sanitization. |
| `REVIEW_REMEDIATION_FLOW.md` | The engine-agnostic review→remediation→gate quality loop, its trigger points (`on_author`, `on_gate_fail`, `pre_promotion`, `pre_merge`), and the independent `pre_merge` review gate (judge≠generator, severity classes, escalation). |
| `DEFINITION_OF_DONE.md` | Engine-agnostic completion criteria for an artifact and for a spec change, plus the risk-tiered human-in-loop. |
| `REVIEW_TEAM.md` | The multi-persona review-team model — crews, the shared blackboard, scoring/conflict/gate rules, and create/review/remediate shapes. |
| `REVIEW_CREWS.yaml` | Machine-readable per-layer review crews + scoring weights behind `REVIEW_TEAM.md`. |
| `REVIEW_SAGA.md` | The engine-agnostic saga lifecycle over the create→review→revise loop — state machine, transition table, journal schema, break-circuit policy. |
| `saga.schema.json` | Machine-readable JSON Schema for the saga journal (`saga.json`) behind `REVIEW_SAGA.md`. |
| `SEED_CONTRACT.md` | The `seed/` input tier — versioned input, frozen per version, total per-claim disposition (absorbed/rejected/deferred, `absorbed` pins `seed_version`), BRD as the absorption point, the AI-attribution rule (GOV-021), and the `SEED01`-vs-auditor enforcement split. |
| `ADAPTATION.md` | The project-adaptation surface — how a consuming project adapts the flow without forking. |
| `ADAPTATION_SURFACE.yaml` | Machine-readable closed knob registry behind `ADAPTATION.md`. |
| `PROFILE-TEMPLATE.yaml` | The bootstrap template an engine copies to seed a project's `.aidoc/profile.yaml` (adaptation-knob overrides only). |
| `ENGINE_TELEMETRY.md` | Vendor-neutral engine-telemetry guidance — standard span/attribute names (attempt, usage, cost, gate verdict + CHG/IPLAN correlation IDs), backend-agnostic, no SDK mandated. |
| `AUTHORING_STYLE.md` | Token-efficient authoring rules — eliminations, form enforcement, form preferences, size targets. Audit-enforced. |
| `LINT_RULES.md` | Normative catalog of the deterministic lint rule IDs a conforming linter emits (meaning, severity, defining contract). |
| `DECISIONS.md` | Durable register of decisions about the spec and its governance (spec-affecting decisions graduate here). |
| `submit-feedback` skill (`framework/skills/submit-feedback/`) | The filing workflow for framework friction found while applying the spec (the canonical reference of DOC_GOVERNANCE_CORE Principle 9). |
| `DECISION_WORKFLOW.md` | The decision-making workflow — how governance decisions are proposed, reviewed, and ratified. |
| `MODULE_LAYOUT.md` | The module structure and organization conventions for the framework. |
| `NOTICES.md` | Important notices, deprecations, and breaking changes across framework versions. |
| `SELF_LEARNING.md` | Self-learning governance loop — how the framework captures and applies lessons learned. |
| `CHG_REQUEST_FLOWS.md` | Ratified 0.57.0 (CHG-06), modernized in 0.88.0+ — the classify→route table for change requests across the 6 graph traversal paths (HOTFIX, CODE2S, CODE2C, SEED2C, DIR2C, SDD2C), and the C1/IPLAN-gate ruling. |
| `CI_AUTONOMOUS_PR_STANDARD.md` | Engine-agnostic CI and autonomous change-integration rules — the unified harness, latency tiers, required-check conclusiveness (anti-deadlock), two-pass independent review, merge-conflict authority classes, and anti-blind closure (GD-42). |

## CNCF Serverless Workflows (`workflows/`)

The `workflows/` directory contains pure, engine-agnostic CNCF Serverless Workflow v0.8 YAML (`.sw.yaml`) definitions governing multi-agent SDD lifecycles and automated verification runners:

| Workflow File | Layer / Domain | Governs |
|---|---|---|
| `brd-business-validation.sw.yaml` | Layer 01 BRD | Strategic theme ingestion, parallel value stream mapping, quantitative ROI/feasibility scoring, executive steering review callbacks, and invalidation compensation. |
| `prd-feature-decomposition.sw.yaml` | Layer 02 PRD | Product theme ingestion, epic-to-story decomposition, quantitative RICE/WSJF scoring, threshold assertion gating, and scope freeze sagas. |
| `ears-requirements-validation.sw.yaml` | Layer 03 EARS | 5-pattern EARS syntactic verification, cross-cutting constraint extraction, bi-directional traceability graph mapping, and defect escalation. |
| `bdd-acceptance-run.sw.yaml` | Layer 04 BDD | Stateful fixture provisioning, Given/When/Then scenario execution, threshold assertion gating, and saga rollback compensation (`RollbackStatefulChanges`). |
| `adr-decision-analysis.sw.yaml` | Layer 05 ADR | Multi-candidate trade-off analysis, MCDA utility scoring, stakeholder RFC review loops, and architectural invalidation sagas. |
| `spec-choreography-contract.sw.yaml` | Layer 06 SPEC | Distributed component interaction verification, schema compatibility checks, dead-letter routing, and compensating transactions. |
| `tdd-test-execution.sw.yaml` | Layer 07 TDD | Red-Green-Refactor cycle loops, fixture lifecycle isolation, regression test gating, and fixture rollback compensation. |
| `seed-to-module-decomposition.sw.yaml` | Architecture | Triple-Lens decomposition (Structure, Trust Boundaries, Process/Sequence) from Tier 1 Seed Vision into Tier 2 C4-L2 Module Containers. |
| `chg-request-flow.sw.yaml` | Layer 09 CHG | Change request classification across 6 graph traversal paths, gate routing (GATE-01/03/06/08/CODE/SPEC), and landing. |
| `worktree-pr-lifecycle.sw.yaml` | Worktree Flow | Per-task worktree isolation, feature branching, PR review watchdog, conflict resolution, auto-merge, and order-guarded cleanup. |
| `review-remediation-flow.sw.yaml` | Governance | Multi-agent review crew dispatch, shared blackboard scoring, and 3-strike remediation saga. |
| `decision-ratification-flow.sw.yaml` | Governance | Governance decision proposal, multi-agent review, founder sign-off, and lock lifecycle. |
| `eval-verification-run.sw.yaml` | Layer 10 EVAL | Multi-tier test execution, structured error triage, threshold verification, and evidence bundling. |

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
| `framework/VERSION` bumped (archive-tier-only repairs exempt) | Yes | Yes |
| Spec-version pins re-declared | Yes | Yes |
| Conformance suite green | Yes | Yes |
| `CHANGELOG.md` updated (archive-tier-only repairs exempt) | Yes | Yes |
| Human approval | Maintainer + 1 reviewer | Maintainer + 2 reviewers |

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
| `README.md` | Catalog of all adaptation scaffolding templates, execution flow handbooks, and operational blueprints. |

The override contract (`ADAPTATION.md` §10) governs how `.aidoc/project/`
mirrors the framework structure and takes precedence via the discovery rule.
