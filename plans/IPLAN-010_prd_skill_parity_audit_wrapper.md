---
title: "IPLAN-010: PRD Skill Parity + Audit Wrapper"
tags:
  - implementation-plan
  - layer-2-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-010
  status: draft
  created_date: 2026-02-26
  timezone: America/New_York
---

# IPLAN-010: PRD Skill Parity + Audit Wrapper

## 1. Objective

Bring PRD skill stack to BRD-equivalent operational model by:
- normalizing PRD skill frontmatter/schema compliance,
- removing stale path/rule references,
- introducing a unified `doc-prd-audit` wrapper skill,
- aligning reviewer/fixer/autopilot contracts to the new audit flow.

Target outcome: PRD skills become a 6-skill set (matching BRD pattern) with consistent orchestration, diagnostics, and fixer handoff.

---

## 2. Scope

### In Scope
- `.claude/skills/doc-prd/SKILL.md`
- `.claude/skills/doc-prd-autopilot/SKILL.md`
- `.claude/skills/doc-prd-reviewer/SKILL.md`
- `.claude/skills/doc-prd-fixer/SKILL.md`
- `.claude/skills/doc-prd-validator/SKILL.md` (already partially remediated; re-verify)
- **New file**: `.claude/skills/doc-prd-audit/SKILL.md`
- Skill index registration updates (if required by current registry format):
  - `.claude/skills/README.md`
  - Any PRD skill matrix/readme table files if present

### Out of Scope
- Runtime Python validator behavior changes in `ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py`
- BRD skill edits (already completed in prior cycle)
- EARS/SYS/REQ skill remediation

---

## 3. Baseline Issues (Current)

1. Frontmatter schema violations in 4 PRD skills (`tags`/`custom_fields` at root instead of `metadata`).
2. Stale repo paths (`ai_dev_flow/...`) across `doc-prd` and `doc-prd-autopilot`.
3. Legacy/incorrect rule doc names in references (`PRD_CREATION_RULES.md`, `PRD_VALIDATION_RULES.md` vs `PRD_MVP_*`).
4. No PRD equivalent of BRD unified audit wrapper (`doc-prd-audit`).
5. Placeholder example links causing lint/compile noise in some sections (non-blocking but should be normalized where practical).
6. PRD fixer currently centers on `PRD-NN.R_review_report_vNNN.md`; audit wrapper introduces `.A_` report, so explicit compatibility edits and verification are required.

### 3.1 Pre-Implementation Gaps in This Plan (Resolved)

The initial draft missed several execution controls that are required for safe delivery in this repository:

1. No explicit requirement to update `Version History` / metadata version fields in modified PRD skills.
2. No explicit policy for handling placeholder/example links that trigger skill compile diagnostics.
3. No guardrail to prevent accidental commits of unrelated repository changes during implementation.
4. No explicit search-scope guard for multi-workspace environments (`b-local-docs` + `ucx_framework`).
5. No explicit verification that `doc-prd-fixer` accepts `.A_audit_report` input in addition to `.R_review_report`.
6. No explicit invocation examples proving the new `doc-prd-audit` workflow entry points.

These are now incorporated in Phases B/D/E and the verification checklist.

---

## 4. Design Approach (Mirror BRD Model)

### 4.1 Skill Topology (Target)
- `doc-prd` (authoring)
- `doc-prd-autopilot` (orchestration)
- `doc-prd-validator` (structure/schema checks)
- `doc-prd-reviewer` (semantic/content checks)
- `doc-prd-fixer` (auto/manual remediation)
- `doc-prd-audit` (**new unified validator+reviewer wrapper**)

### 4.2 `doc-prd-audit` Contract (New)
Sequence:
1) run `doc-prd-validator`
2) run `doc-prd-reviewer`
3) normalize findings
4) emit `PRD-NN.A_audit_report_vNNN.md`
5) optional handoff to `doc-prd-fixer`

Combined status rule:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 4.3 Diagram Contract Policy (PRD-specific)
- PRD diagram checks remain **blocking** in canonical policy:
  - `PRD-E023` `PRD-E024` `PRD-E025` `PRD-E026`
- Intent header warning remains:
  - `PRD-W011`
- Audit report must include dedicated `Diagram Contract Findings` section.

---

## 5. Implementation Plan

### Phase A0 — MVP PRD Template Conformance Gate (NEW)
Authoritative sources:
- `ai_dev_ssd_flow/02_PRD/PRD-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/02_PRD/PRD_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/02_PRD/PRD_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/02_PRD/PRD_MVP_SCHEMA.yaml`

Files to inspect:
- `doc-prd/SKILL.md`
- `doc-prd-autopilot/SKILL.md`
- `doc-prd-validator/SKILL.md`
- `doc-prd-reviewer/SKILL.md`
- `doc-prd-fixer/SKILL.md`

Checklist:
1. Section model alignment (21-section MVP references and wording).
2. Readiness threshold alignment (`>=90%` language and scoring references).
3. Nested folder rule alignment for PRD examples/commands.
4. Diagram contract policy alignment (`PRD-E023..PRD-E026`, `PRD-W011`).
5. Rule/schema file references match current MVP filenames.

Acceptance:
- No contradictions between PRD skill guidance and MVP PRD template/rules/schema.
- Any intentional deviations are documented in-skill with rationale.

### Phase A — Frontmatter + Structural Compliance
Files:
- `doc-prd/SKILL.md`
- `doc-prd-autopilot/SKILL.md`
- `doc-prd-reviewer/SKILL.md`
- `doc-prd-fixer/SKILL.md`

Actions:
- Move `tags` and `custom_fields` under `metadata`.
- Keep semantic values unchanged unless obsolete.
- Ensure consistent metadata key ordering with repository convention.

Acceptance:
- `get_errors` shows no skill-frontmatter schema errors for all five PRD skills.

### Phase B — Reference Path + Rule Name Normalization
Files:
- `doc-prd/SKILL.md`
- `doc-prd-autopilot/SKILL.md`
- `doc-prd-validator/SKILL.md` (re-verify)

Actions:
- Replace `ai_dev_flow/` references with `ai_dev_ssd_flow/`.
- Replace outdated rule docs:
  - `PRD_CREATION_RULES.md` -> `PRD_MVP_CREATION_RULES.md`
  - `PRD_VALIDATION_RULES.md` -> `PRD_MVP_VALIDATION_RULES.md`
- Normalize command examples to correct script locations.
- Normalize placeholder/example links that trigger compile diagnostics:
  - convert unresolved markdown links to plain text examples where link resolution is not required,
  - or point examples to existing repository paths only.

Acceptance:
- No `ai_dev_flow/` paths remain in PRD skill files (except intentional historical notes, if explicitly labeled).
- All referenced PRD rules/templates resolve to current filenames.

### Phase C — Add `doc-prd-audit` Skill
File:
- **Create** `.claude/skills/doc-prd-audit/SKILL.md`

Actions:
- Derive structure from `doc-brd-audit`.
- Replace BRD-specific semantics with PRD equivalents.
- Add PRD diagram blocking gate language and combined report contract.
- Include legacy compatibility for reviewer/fixer report ingestion (`.A_` + `.R_`).
- Add explicit invocation examples for:
  - direct audit (`/doc-prd-audit <prd-path>`)
  - fixer with audit report (`/doc-prd-fixer PRD-NN --review-report PRD-NN.A_audit_report_vNNN.md`)

Acceptance:
- New file passes skill schema checks.
- New skill references only existing PRD skills and current paths.

### Phase D — Integrate Audit into PRD Skill Ecosystem
Files:
- `doc-prd-autopilot/SKILL.md`
- `doc-prd-fixer/SKILL.md`
- `doc-prd-reviewer/SKILL.md`
- `.claude/skills/README.md` (and PRD-specific index tables if present)

Actions:
- Add `doc-prd-audit` usage guidance where orchestration summary exists.
- Clarify when to call audit wrapper vs direct validator/reviewer.
- Register skill in skills index/listing.
- Update `Version History` entries and metadata (`version`, `last_updated`) for all touched PRD skill files.
- Update fixer contract text to prefer latest of:
  - `PRD-NN.A_audit_report_vNNN.md`
  - `PRD-NN.R_review_report_vNNN.md`
  with deterministic precedence when both exist.

Acceptance:
- Documentation shows coherent invocation path: `autopilot -> audit -> fixer` (or direct reviewer/validator when needed).
- `doc-prd-fixer` contract explicitly supports both `.A_` and `.R_` inputs.

### Phase E — Validation + Evidence
Actions:
- Run diagnostics on all six PRD skills.
- Run grep-based consistency checks:
  - stale paths
  - outdated rule names
  - diagram code references
  - MVP PRD template conformance checks
- Enforce execution-scope guardrails:
  - all searches/edits must target `/opt/data/ucx_framework` only,
  - use path-scoped staging when committing (`git add <explicit paths>`),
  - verify `git diff --name-only` matches expected PRD-skill-only scope before commit.
- Produce short remediation summary report.

Acceptance:
- No schema errors in PRD skills.
- No stale path/rule references.
- PRD audit wrapper documented and indexed.
- No unresolved placeholder-link diagnostics remain in PRD skills unless intentionally retained and documented.

---

## 6. Verification Commands

```bash
# Skill schema diagnostics
# (via IDE problems / get_errors API)

# Stale path scan
rg -n "ai_dev_flow/" .claude/skills/doc-prd*/SKILL.md

# Rule naming scan
rg -n "PRD_CREATION_RULES.md|PRD_VALIDATION_RULES.md" .claude/skills/doc-prd*/SKILL.md

# Placeholder/example unresolved link scan (diagnostic-prone patterns)
rg -n "\(\.\.\.|\(#\.\.\.\)|\]\(\.{3}\)" .claude/skills/doc-prd*/SKILL.md

# Verify fixer supports audit + review report forms
rg -n "A_audit_report|R_review_report|--review-report" .claude/skills/doc-prd-fixer/SKILL.md .claude/skills/doc-prd-audit/SKILL.md

# Verify audit registration in skills index
rg -n "doc-prd-audit" .claude/skills/README.md

# Diagram contract code coverage scan
rg -n "PRD-E023|PRD-E024|PRD-E025|PRD-E026|PRD-W011" .claude/skills/doc-prd*/SKILL.md

# MVP PRD conformance scans
rg -n "21 sections|>=90%|nested folder|PRD_MVP_CREATION_RULES|PRD_MVP_VALIDATION_RULES|PRD_MVP_SCHEMA|PRD-MVP-TEMPLATE" .claude/skills/doc-prd*/SKILL.md
rg -n "PRD-E023|PRD-E024|PRD-E025|PRD-E026|PRD-W011" .claude/skills/doc-prd*/SKILL.md

# Audit wrapper existence
ls .claude/skills/doc-prd-audit/SKILL.md

# Commit scope guard
git diff --name-only
```

---

## 7. Risks and Controls

| Risk | Impact | Control |
|---|---|---|
| Over-editing non-PRD skills | Scope creep | Restrict edits to PRD skill set + index references only |
| Breaking existing user-facing examples | Medium | Keep examples, only normalize paths/filenames |
| Audit wrapper semantic drift from BRD | Medium | Reuse BRD-audit skeleton and replace only artifact-specific rules |
| Inconsistent diagram policy wording | High | Enforce PRD blocking language tied to `PRD-E023..E026` |

---

## 8. Deliverables

1. Remediated PRD skill files (5 existing).
2. New `.claude/skills/doc-prd-audit/SKILL.md`.
3. Updated skills index/README entries.
4. Validation evidence summary (no schema errors + no stale path/rule refs).

---

## 9. Definition of Done

- PRD skills are parity-aligned with BRD operational model (including audit wrapper).
- All PRD skill files pass schema diagnostics.
- `doc-prd-audit` is discoverable and documented.
- PRD diagram contract policy is consistently documented as blocking in PRD context.
- Touched PRD skill files have updated version metadata/history entries.
- `doc-prd-fixer` can consume both `.A_audit_report` and `.R_review_report` inputs per documented contract.
- Commit contains only intended PRD skill files (path-scoped verification passed).
- Changes are committed with a focused scope.
