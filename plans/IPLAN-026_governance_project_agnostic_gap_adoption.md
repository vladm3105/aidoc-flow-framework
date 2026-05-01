---
title: "IPLAN-026: Governance Gap Adoption (Project-Agnostic)"
id: IPLAN-026
date_created: 2026-02-27
last_updated: 2026-02-27
status: planning
owner: ai-agent
tags:
  - implementation-plan
  - governance
  - project-agnostic
  - framework
  - gap-remediation
custom_fields:
  document_type: iplan
  plan_id: IPLAN-026
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-026: Governance Gap Adoption (Project-Agnostic)

## 1. Objective

Update `ucx_framework/governance` by incorporating missing governance capabilities identified in `AI-cost-monitoring/governance`, while preserving framework neutrality (no project-specific org, board, issue, cloud, or repo assumptions).

## 2. Comparison Basis

Source governance (project):
- `/opt/data/techtrend/AI-cost-monitoring/governance`

Target governance (framework):
- `/opt/data/ucx_framework/governance`

Baseline method:
1. File inventory diff (`*.md`) between source and target governance trees.
2. Semantic review of candidate documents.
3. Classification into **Adopt**, **Adapt**, or **Exclude** based on project-agnostic criteria.

## 3. Key Gap Findings

### 3.1 Missing Capabilities in Framework Governance

1. **Operational security checklist artifact**
   - Present in project: `SECURITY_CHECKLIST.md`
   - Missing in framework governance as a ready-to-use governance doc/template.

2. **Troubleshooting runbook artifact**
   - Present in project: `TROUBLESHOOTING.md`
   - Missing in framework governance as a reusable framework guide/template.

3. **AI-first project setup variant at governance layer**
   - Present in project: `GITHUB_PROJECT_SETUP_AI_FIRST.md`
   - Framework currently has `github/GITHUB_PROJECT_SETUP.md` and templates, but lacks explicit AI-first variant parity doc.

4. **AI PR review environment setup supplement**
   - Present in project: `AI_PR_Review/GCP_SETUP.md`
   - Framework AI PR review docs exist, but no dedicated cloud-setup supplement at parity level.

### 3.2 Not True Gaps (Already Covered in Framework)

1. `ROADMAP.md`, `PROJECT_PLAN.md`, `PROJECT_KICKOFF_PLAN.md`
   - Framework coverage exists through templates:
     - `governance/templates/ROADMAP-TEMPLATE.md`
     - `governance/templates/PROJECT_PLAN-TEMPLATE.md`
     - `governance/templates/PROJECT_KICKOFF_PLAN-TEMPLATE.md`
   - Action: do not copy project instances; retain template-first approach.

2. GitHub docs at root path in project (`GITHUB_*`)
   - Framework coverage exists under `governance/github/`.
   - Action: avoid duplicate content; consider compatibility pointers only.

### 3.3 Plan-Level Gaps Identified (Pre-Implementation Review)

1. **Canonical Path Ambiguity**
   - Risk: creating parallel docs in both governance root and `governance/github/` or `governance/AI_PR_Review/` without explicit canonical ownership.
   - Required control: declare one canonical path per artifact and allow pointer text only in non-canonical locations.

2. **Template vs Runtime Doc Ambiguity**
   - Risk: adding only templates or only runtime governance docs for security/troubleshooting, causing incomplete adoption.
   - Required control: define required pair policy (`governance/<doc>.md` + `governance/templates/<doc>-TEMPLATE.md`) before edits.

3. **Acceptance Criteria Under-Specification**
   - Risk: phase acceptance checks currently verify existence and neutrality but not minimum content contract.
   - Required control: add minimum section contract for each new doc family (checklists, diagnostics, recovery, references).

4. **Validation Specificity Gap**
   - Risk: “project-specific leakage checks” are defined broadly and may miss hardcoded values.
   - Required control: define explicit leak patterns and a required link/integrity pass over touched docs.

5. **Index Integration Scope Gap**
   - Risk: plan mentions “relevant README files” without enumerating exact integration points.
   - Required control: enumerate required integration files to avoid discoverability drift.

6. **Fallback Path Drift Risk (`CLOUD_SETUP.md` vs `GCP_SETUP.md`)**
   - Risk: dual-target naming can create future duplication.
   - Required control: choose one canonical filename before implementation and add naming rationale in evidence.

## 4. Project-Agnostic Constraints (Mandatory)

All adopted content must:
1. Remove project-specific identifiers:
   - org/user/repo names
   - concrete project board IDs and option IDs
   - issue/PR numbers
   - hard-coded cloud project IDs
2. Replace with placeholders or neutral guidance.
3. Preserve reusable mechanics (workflow, checks, validation logic).
4. Keep cloud guidance generic (GCP/AWS/Azure-neutral where feasible).
5. Avoid introducing assumptions about a single communication platform beyond existing configurable placeholders.

## 5. Adoption Matrix

| Source (AI-cost-monitoring) | Target (ucx_framework) | Disposition | Rationale |
|---|---|---|---|
| `governance/SECURITY_CHECKLIST.md` | `governance/SECURITY_CHECKLIST.md` + `governance/templates/SECURITY_CHECKLIST-TEMPLATE.md` | **Adapt** | High reusable value; convert to placeholders and framework references |
| `governance/TROUBLESHOOTING.md` | `governance/TROUBLESHOOTING.md` + `governance/templates/TROUBLESHOOTING-TEMPLATE.md` | **Adapt** | High reusable operational value; remove project-specific host/org/resource IDs |
| `governance/GITHUB_PROJECT_SETUP_AI_FIRST.md` | `governance/github/GITHUB_PROJECT_SETUP_AI_FIRST.md` | **Adapt** | AI-first workflow parity needed in framework docs |
| `governance/AI_PR_Review/GCP_SETUP.md` | `governance/AI_PR_Review/CLOUD_SETUP.md` (or `GCP_SETUP.md` with placeholders) | **Adapt** | Useful setup material; must generalize naming and secrets |
| `governance/ROADMAP.md` | no direct copy | **Exclude** | Framework already uses roadmap template model |
| `governance/PROJECT_PLAN.md` | no direct copy | **Exclude** | Framework already uses plan template model |
| `governance/PROJECT_KICKOFF_PLAN.md` | no direct copy | **Exclude** | Framework already uses kickoff template model |

## 6. Scope

### In Scope
- Add missing governance docs/templates that are reusable and project-agnostic.
- Add/adjust governance indexes and quick-reference links to surface new docs.
- Ensure cross-links resolve within `ucx_framework/governance` structure.

### Out of Scope
- Migrating project-specific plans from `AI-cost-monitoring/governance/plans/`.
- Embedding project board option IDs, concrete issue numbers, or repo host specifics.
- Replacing template-driven project planning model with concrete sample project plans.

## 7. Implementation Phases

### Phase A0 — Canonical Conformance Gate

References:
- `governance/README.md`
- `governance/GOVERNANCE_RULES.md`
- `governance/templates/*`
- `governance/github/*`
- `governance/AI_PR_Review/*`

Checklist:
1. Confirm current governance information architecture and path conventions.
2. Confirm placeholder conventions (`{PLACEHOLDER}` style) for project-agnostic docs.
3. Confirm no duplicate single-source docs will be created across root vs subfolders.
4. Decide canonical filename for AI PR review setup supplement (`CLOUD_SETUP.md` preferred; `GCP_SETUP.md` only if explicitly justified).
5. Decide template/runtime pair policy for new security and troubleshooting artifacts.

Acceptance:
- Pathing and placeholder conventions are explicitly enforced before edits.
- Canonical filename and template/runtime pair policy are recorded in implementation evidence.

### Phase A — Create Missing Reusable Artifacts

Actions:
1. Add template counterparts first:
   - `governance/templates/SECURITY_CHECKLIST-TEMPLATE.md`
   - `governance/templates/TROUBLESHOOTING-TEMPLATE.md`
2. Add `governance/SECURITY_CHECKLIST.md` (framework runtime guidance).
3. Add `governance/TROUBLESHOOTING.md` (framework runtime guidance).
4. Enforce minimum content contracts:
   - Security checklist: pre-commit, pre-PR, review, deployment checks + tool references.
   - Troubleshooting: symptom/diagnosis/recovery pattern + escalation and references.

Acceptance:
- Both new governance docs and templates exist with no project-specific hardcoding.
- New docs satisfy minimum content contracts defined in this phase.

### Phase B — AI-First Setup Parity Docs

Actions:
1. Add `governance/github/GITHUB_PROJECT_SETUP_AI_FIRST.md` as framework-neutral variant.
2. Add AI PR review setup supplement:
   - preferred: `governance/AI_PR_Review/CLOUD_SETUP.md` (cloud-neutral)
   - fallback: `governance/AI_PR_Review/GCP_SETUP.md` with placeholders and cloud notes.

Acceptance:
- AI-first setup and PR-review setup parity exists without project coupling.
- One canonical filename is used for AI PR review setup supplement (no duplicate cloud setup files).

### Phase C — Index + Rules Integration

Actions:
1. Update `governance/README.md`:
   - directory structure section
   - core documentation table
   - quick navigation sections
2. Update `governance/GOVERNANCE_RULES.md` quick-reference table to include:
   - `SECURITY_CHECKLIST.md`
   - `TROUBLESHOOTING.md`
   - AI-first setup doc path
3. Update any relevant README files under `governance/AI_PR_Review/` and `governance/github/`.
4. Minimum required integration points:
   - `governance/README.md`
   - `governance/GOVERNANCE_RULES.md`
   - `governance/AI_PR_Review/README.md`
   - `governance/github/GITHUB_PROJECT_SETUP.md` (pointer to AI-first variant)

Acceptance:
- New artifacts are discoverable from primary governance entry points.

### Phase D — Consistency and Validation

Actions:
1. Run diagnostics on touched files.
2. Run scoped grep checks on touched files only for:
   - project-specific names (`USDA-AI-Innovation-Hub`, `AI-Cloud-Cost-Monitoring`, `aiocto`, concrete board IDs)
   - host-specific hardcoding where placeholders are expected
   - broken internal governance links
3. Required leakage pattern set:
   - `USDA-AI-Innovation-Hub|AI-Cloud-Cost-Monitoring|aiocto|github\.techtrend\.us`
   - `MDk6UHJvamVjdFYy|MDI2OlByb2plY3RWMl` (board/field ID signatures)
4. Validate cross-links from all newly added governance docs to existing governance paths.
5. Produce evidence report:
   - `tmp/IPLAN-026_validation_evidence_2026-02-27.md`

Acceptance:
- Touched files pass diagnostics and project-specific leakage checks.
- Link integrity is verified for all newly added/updated governance docs.

## 8. Deliverables

1. `plans/IPLAN-026_governance_project_agnostic_gap_adoption.md` (this plan)
2. New/updated governance docs in `ucx_framework/governance` per Phases A-C.
3. Validation evidence report in `ucx_framework/tmp/`.

## 9. Definition of Done

- Missing reusable governance capabilities are added to framework governance.
- Added content is project-agnostic and placeholderized.
- Governance index/rules reference all new docs.
- No unresolved high-severity broken links or hardcoded project-specific leakage in touched files.
- Validation evidence generated.

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Over-importing project-specific details | Reduces framework reusability | Enforce placeholder and exclusion checks in Phase D |
| Duplicate docs across root/subfolder paths | Long-term drift risk | Keep single canonical location + add pointers only |
| Scope creep into project plans/IPLAN history | Delays delivery | Explicitly exclude project plan migration |
| Inconsistent terminology across governance docs | Confusion for adopters | Run cross-doc terminology pass before completion |

## 11. Execution Notes

- Prefer adapting existing framework style/structure over direct copy.
- Keep changes minimal and additive.
- Preserve existing approved governance mechanics; add missing capabilities only.
