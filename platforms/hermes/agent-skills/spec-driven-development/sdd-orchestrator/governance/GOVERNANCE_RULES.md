# Governance Rules

**Framework**: Specification-Driven Development (SDD)

## 1. Canonical Flow

All active governance workflows align to:

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

- Artifact registry: `framework/registry/LAYER_REGISTRY.yaml`
- Governance core: `framework/governance/DOC_GOVERNANCE_CORE.md`
- CHG overlay: `framework/governance/chg/`

## 2. Security Posture

- Use Workload Identity Federation or equivalent short-lived credentials.
- Do not store service-account key files, plaintext secrets, or credential dumps in repository history.
- Keep production control actions human-gated.

## 2a. GitHub Actions Baseline

- Default CI/CD baseline uses GitHub-hosted runners (`runs-on: ubuntu-latest`).
- Marketplace actions are allowed when pinned to stable major versions and reviewed.
- Self-hosted runners are optional for workloads requiring custom tooling, network access, or compliance isolation.

## 2b. Plan Types and Storage (Mandatory)

Use three distinct plan types with explicit storage boundaries:

| Plan Type | Scope | Location | Retention |
|---|---|---|---|
| Document-layer IPLAN | SDD Layer-8 implementation bridge from document flow to code execution | Project document lifecycle output (`docs/IPLAN/`, `UCX/08_IPLAN/`, or equivalent) | Permanent |
| Permanent development plan | Project development and operations planning, including implementation sequencing for approved IPLAN scope | `plans/` (or `governance/plans/` in governance-template repos) | Permanent |
| Temporary plan | Bug fixes, document corrections, and minor one-off work with no long-term tracking requirement | `tmp/` | Disposable |

Operational rules:

- Keep document-layer IPLAN, permanent development plans, and temporary plans separated by directory.
- Do not store temporary plans in `plans/`.
- Promote a temporary plan into `plans/` when scope expands to new functionality, cross-cutting dependencies, or multi-session execution.
- Treat `plans/` as project history and audit context; do not delete permanent plans.

## 3. AI Workflow

### Planning-First Governance Gate (Mandatory)

No implementation work starts without approved planning artifacts.

Required planning sequence:

1. Analyze provided information, constraints, dependencies, and existing context.
2. Create planning roadmap for the target scope.
3. Create planning document index for required plan artifacts.
4. Define changelog plan for the scope (what changes will be tracked and where).
5. Review planning artifacts for gaps and resolve or explicitly defer gaps.
6. Create and refine required execution plan artifact(s):
   - document-layer IPLAN (`IPLAN-NNN_{slug}.md`) for SDD layer delivery when applicable
   - permanent development plan (`PLAN-NNN_{slug}.md`, preferred) under `plans/` or `governance/plans/`
7. Record explicit plan approval (human reviewer or independent LLM-as-judge session).

Hard gate rules:

- No document creation, testing, or coding begins before the planning gate is approved.
- No issue is transitioned to `ai:in-progress` before planning approval exists.

### Labels

`ai:ready -> ai:in-progress -> ai:review-requested`

- Only `ai:ready` issues are eligible for autonomous execution agents.
- Do not use `ai:approved` or `ai:rejected`; approval is represented by transition into `ai:ready` and PR review state.

### Round-Based PR Governance (Mandatory)

For every autonomous execution PR, run this gate sequence:

1. `sdd_validate` (deterministic structure and naming rules)
2. `sdd_review` (UCX persona content review)
3. `sdd_remediate` (UCX persona remediation guidance/application)
4. post-remediation `sdd_validate`
5. Hermes final blocker-gap/inconsistency review (non-deep-content)

If any blocking check fails, run a second round with the same sequence.

If Round 2 fails, escalation status becomes `REQUIRED`, merge is blocked, and human review is mandatory.

### Issue Processing Workflow (Mandatory)

Before coding, agents must:

1. Complete issue analysis.
2. Create planning roadmap artifact for the issue scope.
3. Create planning index for required plan artifacts.
4. Define changelog plan for the issue scope.
5. Review planning artifacts for gaps and resolve or defer with rationale.
6. Create required plan artifact(s) (document-layer IPLAN and/or permanent development plan).
7. Refine plan artifact(s) and ensure acceptance criteria mapping.
8. Record explicit approval for the plan set.
9. Transition issue to `ai:in-progress`.

### Acceptance Criteria Sync (Mandatory)

- Verify each linked-issue acceptance criterion before requesting review.
- Update issue checkboxes only after evidence-based verification.

### Linked Issue Verification in PR Review (Mandatory)

- PR review must validate implementation against linked issue acceptance criteria.

### Issue PR Link (Mandatory)

- Linked issue must contain direct PR reference (PR number and URL) for auditability.

### Issue Review History (Mandatory)

- Post review and re-review outcomes back to the linked issue.

## 4. Naming Conventions

- Branches: `feature/{slug}`, `bugfix/{slug}`, `hotfix/{slug}`, `ai/{issue}-{slug}`
- Document-layer plans: `IPLAN-NNN_{slug}.md`
- Permanent development plans: `PLAN-NNN_{slug}.md` (preferred; legacy repository-specific patterns allowed)
- Temporary plans: `tmp/TMP-PLAN-YYYY-MM-DD_{slug}.md`
- Issues: `[P{phase}-{task}] {title}` where applicable

## 5. Agent Operating Model

1. Hermes is the control-plane agent for planning, governance, and lifecycle progression from BRD through IPLAN.
2. Execution agents (Claude Code, Codex, OpenCode, or equivalent) implement scope for issues in `ai:ready`, create PRs, and run delivery workflows.
3. Hermes performs round-based PR governance, merge-time escalation decisions, and post-deployment validation using observability evidence.

## 6. Document Maintenance

- Keep governance docs aligned with active workflow behavior.
- Update cross-references when section names or anchors change.
- Mark deprecated patterns explicitly and provide replacement guidance.
- Validate links in context: framework docs in repo context, template docs in scaffolded project context.

## 7. Layer Model (single-path, no depth tiers)

There are **no** Lite/Standard/Full depth tiers. The flow is a single path over the
8 layers — BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code — with **CHG** as a
governance overlay applied to changes (not a tier). Every layer present is required to
converge; the framework does not offer a reduced-artifact profile.

Which upstream a given layer must realize is governed by the **necessary-upstream
contract** (NECESSARY-UPSTREAM-001, framework spec `0.15.2` → `0.16.0`): a layer traces
only the upstream layers that actually exist in the project — not a fixed tier and not a
cumulative redeclaration of every upstream layer. See
`framework/governance/TRACEABILITY.md` and `REVIEW_TEAM.md` §"Necessary upstream +
transitive trace". The flow operates across the **MVP → PROD → NEW MVP** lifecycle.

Legacy SYS/REQ/CTR/TSPEC/TASKS layers are deprecated for active governance.

## 8. Issue Source and Traceability

Issues may originate from v3 artifacts. When issue label `source:sdd` is present:

1. Issue includes trace tags (`@brd`, `@prd`, `@ears`, `@adr`, `@spec`, `@tdd`)
2. Issue references upstream artifact IDs
3. IPLAN references the issue and upstream IDs for execution traceability

## 9. Production Issue-Fix Loop

1. Observability stack detects incident/regression signals.
2. Hermes triages severity and impact, then opens/updates GitHub issue with traceability and acceptance criteria.
3. Human/policy approval moves issue into executable queue (`ai:ready`).
4. Hermes completes planning-first governance artifacts and approval for the issue scope.
5. Execution agent performs fix -> PR according to approved plans.
6. Hermes runs Round 1 PR governance gates (`sdd_validate` -> `sdd_review` -> `sdd_remediate` -> post-remediation `sdd_validate` -> final blocker-gap check).
7. If Round 1 fails, Hermes runs Round 2 with the same sequence.
8. If Round 2 fails, Hermes escalates to human review and blocks merge.
9. If gates pass, PR merges and linked issue closes.
10. Hermes validates post-deployment evidence and opens follow-up issue(s) when required.

## Deprecated Compatibility

- Legacy TASKS-sync tooling is deprecated.
- Legacy framework root references are not allowed in active governance docs.
- Any retained compatibility alias must include a deprecation note and removal criteria.
