---
title: "IPLAN-024 - TASKS Skill Parity + Audit Wrapper"
id: IPLAN-024
date_created: 2026-02-27
last_updated: 2026-02-27
status: planning
owner: ai-agent
tags:
  - implementation-plan
  - layer-11-artifact
  - shared-architecture
  - skills
  - tasks
  - audit-wrapper
  - parity
custom_fields:
  document_type: iplan
  plan_id: IPLAN-024
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-024: TASKS Skill Parity + Audit Wrapper

## 1. Objective

Establish full parity for Layer 11 TASKS skills by introducing a unified `doc-tasks-audit` wrapper and aligning report-contract behavior with existing reviewer/fixer/autopilot workflows.

## 2. Scope

In scope:
- Add `.claude/skills/doc-tasks-audit/SKILL.md`.
- Update `.claude/skills/README.md` audit-wrapper registration to include TASKS.
- Validate report-contract consistency across:
  - `doc-tasks-reviewer`
  - `doc-tasks-fixer`
  - `doc-tasks-autopilot`
  - `doc-tasks-validator`
- Produce evidence report: `tmp/IPLAN-024_validation_evidence_YYYY-MM-DD.md`.

Out of scope:
- Changes to `ai_dev_ssd_flow/11_TASKS/scripts/*` runtime behavior.
- Broad refactors of non-TASKS skills.

## 3. Baseline Findings

1. `11_TASKS` canonical references exist (`TASKS-MVP-TEMPLATE`, schema, rules, guides, scripts).
2. Existing TASKS skill set includes:
   - `doc-tasks`
   - `doc-tasks-autopilot`
   - `doc-tasks-validator`
   - `doc-tasks-reviewer`
   - `doc-tasks-fixer`
3. Gap: no `doc-tasks-audit` skill present.
4. Gap: `.claude/skills/README.md` audit-wrapper list omits TASKS.

## 4. Plan-Level Gaps (Re-Review Controls)

1. **Canonical Drift Risk**
  - Plan references canonical TASKS assets generically but lacks an explicit canonical conformance gate/checklist.
2. **Cross-Workspace Scope Risk**
  - Execution must remain scoped to `/opt/data/ucx_framework` only.
3. **Validation Noise Risk**
  - Scoped grep checks must target touched files only to avoid unrelated legacy findings.
4. **Report-Contract Precedence Risk**
  - Fixer compatibility requires deterministic precedence (`latest`; tie -> `.A_` over `.R_`).
5. **README Discoverability Risk**
  - `doc-tasks-audit` must be listed under audit-wrapper section with Layer 11 coverage text.

## 5. Design Contract

### 5.1 Wrapper Flow

`doc-tasks-audit` sequence:
1. run `doc-tasks-validator`
2. run `doc-tasks-reviewer`
3. normalize findings
4. emit `TASKS-NN.A_audit_report_vNNN.md`
5. optional handoff to `doc-tasks-fixer`

### 5.2 Combined Status

- PASS: validator PASS AND reviewer score meets configured gate AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer score below gate OR blocking/manual-required findings

### 5.3 Report Compatibility

- Preferred fixer input: `TASKS-NN.A_audit_report_vNNN.md`
- Legacy-compatible input: `TASKS-NN.R_review_report_vNNN.md`
- Tie rule: prefer `.A_` over `.R_`

## 6. Implementation Phases

### Phase A0 — TASKS Canonical Conformance Gate

Authoritative references:
- `ai_dev_ssd_flow/11_TASKS/TASKS-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/11_TASKS/TASKS-MVP-TEMPLATE.yaml`
- `ai_dev_ssd_flow/11_TASKS/TASKS_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/11_TASKS/TASKS_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/11_TASKS/TASKS_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/11_TASKS/TASKS_MVP_QUALITY_GATE_VALIDATION.md`
- `ai_dev_ssd_flow/11_TASKS/TASKS_VALIDATION_COMMANDS.md`

Checklist:
1. Confirm Layer-11 TASKS structure and naming assumptions.
2. Confirm report naming compatibility (`.A_` preferred, `.R_` legacy).
3. Confirm validator/reviewer/fixer handoff semantics.
4. Confirm no runtime script behavior change is required.

Acceptance:
- No contradictions between planned TASKS wrapper contract and canonical TASKS references.

### Phase A — Contract Gap Review

- Inspect existing TASKS reviewer/fixer/autopilot contracts.
- Confirm whether score threshold references are explicit and consistent.
- Confirm report naming patterns are versioned.

### Phase B — Implement Wrapper

- Create `.claude/skills/doc-tasks-audit/SKILL.md` using established `doc-*-audit` pattern.
- Include combined status rules and fixer handoff semantics.

### Phase C — Integrate in README

- Add `doc-tasks-audit` in SDD Audit Wrapper Skills list.
- Update purpose text for wrapper coverage to include TASKS (Layer 11).

### Phase D — Validate + Evidence

- Run diagnostics on touched files.
- Run scoped grep checks (touched files only) for:
  - stale `ai_dev_flow` path markers,
  - non-versioned review report naming patterns,
  - missing `.A_audit_report_vNNN.md` references in audit/fixer/reviewer contracts.
- Validate scoped git status in `/opt/data/ucx_framework` only.
- Generate `tmp/IPLAN-024_validation_evidence_YYYY-MM-DD.md`.

## 7. Deliverables

1. New `.claude/skills/doc-tasks-audit/SKILL.md`
2. Updated `.claude/skills/README.md` TASKS audit-wrapper registration
3. Validation evidence report in `tmp/`

## 8. Definition of Done

- `doc-tasks-audit` exists and references validator+reviewer+fixer correctly.
- Wrapper emits `TASKS-NN.A_audit_report_vNNN.md` contract.
- README includes TASKS in audit-wrapper section.
- Touched files are diagnostics-clean (excluding pre-existing repository-wide README style warnings).
- Evidence report generated with scoped checks and results.

## 9. Execution Notes

- Preserve existing TASKS authoring/review logic unless needed for report-contract consistency.
- Keep changes minimal and parity-focused.
