---
title: "IPLAN-020: PTEST Skill Set + Audit Wrapper"
tags:
  - implementation-plan
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-020
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-020: PTEST Skill Set + Audit Wrapper

## 1. Objective

Create a PTEST-specialized Claude skill stack for **Performance Test Specification** workflows, while preserving compatibility with existing `doc-tspec` orchestration.

Target outcome: introduce a dedicated 6-skill PTEST set with audit-first flow:
- `doc-ptest`
- `doc-ptest-autopilot`
- `doc-ptest-validator`
- `doc-ptest-reviewer`
- `doc-ptest-fixer`
- `doc-ptest-audit` (new wrapper)

---

## 2. Scope

### In Scope
- New skill files under `.claude/skills/`:
  - `.claude/skills/doc-ptest/SKILL.md`
  - `.claude/skills/doc-ptest-autopilot/SKILL.md`
  - `.claude/skills/doc-ptest-validator/SKILL.md`
  - `.claude/skills/doc-ptest-reviewer/SKILL.md`
  - `.claude/skills/doc-ptest-fixer/SKILL.md`
  - `.claude/skills/doc-ptest-audit/SKILL.md`
- Skill registry updates:
  - `.claude/skills/README.md`
- Minimal coexistence cross-links between PTEST subtype flow and TSPEC-generic flow.

### Out of Scope
- Changes to canonical template/rules/schema under `ai_dev_ssd_flow/10_TSPEC/PTEST/*`
- Runtime script behavior changes under `ai_dev_ssd_flow/10_TSPEC/scripts/*`
- Broad refactor of existing `doc-tspec*` skill family.
- Allowed cross-link touchpoints only (if needed for coexistence clarity):
  - `.claude/skills/README.md`
  - `.claude/skills/doc-tspec/SKILL.md`
  - `.claude/skills/doc-tspec-autopilot/SKILL.md`

---

## 3. Baseline Findings (From Scratch Audit)

1. No dedicated `doc-ptest*` skill set currently exists in `.claude/skills/`.
2. Current performance testing guidance is embedded in TSPEC-generic skills (`doc-tspec*`).
3. Canonical PTEST assets are available and authoritative:
   - `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md`
   - `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_CREATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_VALIDATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_QUALITY_GATES.md`
4. PTEST template enforces subtype-specific constraints justifying specialization:
   - 6-section structure
   - required PTEST tags include `@sys` and `@spec`
   - focus on performance test categories `[Load]`, `[Stress]`, `[Endurance]`, `[Spike]`
   - required Load Scenario tables in test cases
   - optional/required `execution_profile` for complex scenarios
   - TASKS-Ready threshold `>=90%`

Current diagnostics posture:
- Capability expansion (new skill set), not blocker remediation.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **Overlap Risk with `doc-tspec*`**
   - Must define deterministic routing between PTEST-specific and TSPEC-generic workflows.
2. **Canonical Drift Risk**
   - New PTEST skills must only reference canonical PTEST assets and existing scripts.
3. **Wrapper/Fixer Compatibility Risk**
   - `doc-ptest-fixer` must support:
     - `PTEST-NN.A_audit_report_vNNN.md` (preferred)
     - `PTEST-NN.R_review_report_vNNN.md` (legacy)
4. **Cross-Workspace Scope Risk**
   - Edits/staging must remain scoped to `/opt/data/ucx_framework`.
5. **Metadata/Versioning Risk**
   - All new skills must use normalized `metadata` frontmatter + `versioning_policy`.
6. **README Discoverability Risk**
   - New skills must be visible in reviewer/audit/fixer/autopilot/core sections.
7. **Command Reference Risk**
   - Use canonical script paths only (`validate_ptest.py`, shared validators).
8. **False-Positive Grep Risk**
   - Phase-E regex checks must target skill/README files only (exclude `plans/` and `tmp/`).

---

## 5. Design Approach (Subtype-Specialized)

### 5.1 Target PTEST Topology

- `doc-ptest`: subtype authoring guidance
- `doc-ptest-autopilot`: generate/find/review orchestration
- `doc-ptest-validator`: schema/structure/tag/performance-contract validation
- `doc-ptest-reviewer`: semantic quality and performance-completeness review
- `doc-ptest-fixer`: remediation workflow with deterministic report precedence
- `doc-ptest-audit`: unified validator+reviewer wrapper

### 5.2 Audit Wrapper Contract (`doc-ptest-audit`)

Sequence:
1. run `doc-ptest-validator`
2. run `doc-ptest-reviewer`
3. normalize findings
4. emit `PTEST-NN.A_audit_report_vNNN.md`
5. optional handoff to `doc-ptest-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 Coexistence Contract with TSPEC

- `doc-tspec*` remains canonical multi-subtype path.
- `doc-ptest*` provides subtype-optimized path for performance testing workflows.
- Both may coexist; README must clarify positioning to reduce ambiguity.

### 5.4 Routing Rules (Operational)

Use `doc-ptest*` when:
- authoring/reviewing/fixing PTEST-only artifacts,
- performance thresholds/load profiles are primary.

Use `doc-tspec*` when:
- mixed subtype orchestration is required,
- cross-subtype normalization or batch TSPEC flow is primary.

Fallback rule:
- If `doc-ptest*` yields unresolved blockers, route to `doc-tspec*` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## 6. Implementation Phases

### Phase A0 — PTEST Canonical Conformance Gate

Authoritative references:
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.yaml`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_QUALITY_GATES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_ptest.py`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh`
- `ai_dev_ssd_flow/scripts/validate_cross_document.py`
- `ai_dev_ssd_flow/scripts/validate_tags_against_docs.py`

Checklist:
1. Confirm 6-section PTEST contract and heading conventions.
2. Confirm required tags (`@sys`, `@spec`) and cumulative tags.
3. Confirm TASKS-Ready threshold and SYS-coverage framing.
4. Confirm Load Scenario table requirements and performance metric thresholds.
5. Confirm `execution_profile` guidance for complex scenarios.
6. Confirm canonical validator/script references.

Acceptance:
- No contradictions between planned PTEST skills and canonical PTEST references.

### Phase A — Create Core PTEST Skills (`doc-ptest`, `doc-ptest-autopilot`)

Files:
- `.claude/skills/doc-ptest/SKILL.md`
- `.claude/skills/doc-ptest-autopilot/SKILL.md`

Actions:
- Define PTEST-specific authoring contracts and examples.
- Define autopilot generate/find/review flow aligned to PTEST naming/path rules.
- Include explicit relationship with `doc-tspec` (coexistence, not replacement).

Acceptance:
- Core skills parse cleanly and reference canonical PTEST assets only.

### Phase B — Create QA Skills (`doc-ptest-validator`, `doc-ptest-reviewer`, `doc-ptest-fixer`)

Files:
- `.claude/skills/doc-ptest-validator/SKILL.md`
- `.claude/skills/doc-ptest-reviewer/SKILL.md`
- `.claude/skills/doc-ptest-fixer/SKILL.md`

Actions:
- Implement subtype validation/review checks aligned to PTEST contract requirements.
- Define fixer auto/manual boundaries and deterministic report precedence.
- Ensure examples use versioned report names and canonical script paths.

Acceptance:
- QA contracts are internally consistent and audit-wrapper ready.

### Phase C — Add Unified Wrapper (`doc-ptest-audit`)

File:
- `.claude/skills/doc-ptest-audit/SKILL.md`

Actions:
- Mirror established `doc-*-audit` wrapper structure.
- Define combined output contract and fixer handoff semantics.
- Include invocation examples for direct audit and remediation handoff.

Acceptance:
- Wrapper references only existing PTEST validator/reviewer/fixer skills.

### Phase D — Skills Index and Integration

File:
- `.claude/skills/README.md`

Actions:
- Register new PTEST skills in reviewer/audit/fixer/autopilot/core sections.
- Add PTEST audit wrapper to audit-wrapper listing.
- Add explicit routing guidance for `doc-ptest*` vs `doc-tspec*`.

Acceptance:
- Discoverability complete and routing guidance non-conflicting.

### Phase E — Validation and Evidence

Actions:
- Run diagnostics on all six new PTEST skills + README updates.
- Run scoped grep checks against `.claude/skills/doc-ptest*/SKILL.md` and `.claude/skills/README.md` only:
  - stale path markers (`ai_dev_flow`),
  - non-versioned review report naming,
  - `PTEST-NN.R_review_report.md` (non-versioned) patterns,
  - missing `PTEST-NN.A_audit_report_vNNN.md` examples in audit/fixer contracts,
  - missing audit-wrapper references,
  - non-canonical validator references.
- Validate scoped git status in `/opt/data/ucx_framework` only.
- Generate evidence bundle: `tmp/IPLAN-020_validation_evidence_YYYY-MM-DD.md`.

Acceptance:
- No parser/diagnostic blockers in touched files.
- Drift regex checks pass for touched PTEST skills.
- Change set is scoped to PTEST skill-set introduction and README integration.

---

## 7. Deliverables

1. New PTEST 6-skill pack under `.claude/skills/doc-ptest*/`.
2. New wrapper: `.claude/skills/doc-ptest-audit/SKILL.md`.
3. Updated `.claude/skills/README.md` with PTEST registrations.
4. Validation evidence report.

---

## 8. Definition of Done

- All six `doc-ptest*` skills created with normalized metadata schema and version history.
- PTEST contracts aligned to canonical PTEST template/rules/schema/scripts.
- Audit-first remediation path documented: `autopilot -> audit -> fixer`.
- Fixer report precedence explicit (`latest timestamp`; tie => `.A_` over `.R_`).
- README includes PTEST discoverability and routing guidance.
- Evidence bundle generated: `tmp/IPLAN-020_validation_evidence_YYYY-MM-DD.md`.
- Diagnostics and drift checks pass for all touched files.

---

## 9. Execution Notes

- This plan introduces a subtype-specialized PTEST stack and does not deprecate TSPEC-generic skills.
- If MVP scope reduction is needed, execute Phase A + C first (core + wrapper), then Phase B (full QA specialization).
- Rollout fallback: if partial adoption causes ambiguity, keep `doc-tspec*` as primary and treat `doc-ptest*` as opt-in until routing guidance and validation evidence are confirmed.
