---
title: "IPLAN-019: ITEST Skill Set + Audit Wrapper"
tags:
  - implementation-plan
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-019
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-019: ITEST Skill Set + Audit Wrapper

## 1. Objective

Create an ITEST-specialized Claude skill stack for **Integration Test Specification** workflows, while preserving compatibility with existing `doc-tspec` orchestration.

Target outcome: introduce a dedicated 6-skill ITEST set with audit-first flow:
- `doc-itest`
- `doc-itest-autopilot`
- `doc-itest-validator`
- `doc-itest-reviewer`
- `doc-itest-fixer`
- `doc-itest-audit` (new wrapper)

---

## 2. Scope

### In Scope
- New skill files under `.claude/skills/`:
  - `.claude/skills/doc-itest/SKILL.md`
  - `.claude/skills/doc-itest-autopilot/SKILL.md`
  - `.claude/skills/doc-itest-validator/SKILL.md`
  - `.claude/skills/doc-itest-reviewer/SKILL.md`
  - `.claude/skills/doc-itest-fixer/SKILL.md`
  - `.claude/skills/doc-itest-audit/SKILL.md`
- Skill registry updates:
  - `.claude/skills/README.md`
- Minimal coexistence cross-links between ITEST subtype flow and TSPEC-generic flow.

### Out of Scope
- Changes to canonical template/rules/schema under `ai_dev_ssd_flow/10_TSPEC/ITEST/*`
- Runtime script behavior changes under `ai_dev_ssd_flow/10_TSPEC/scripts/*`
- Broad refactor of existing `doc-tspec*` skill family.
- Allowed cross-link touchpoints only (if needed for coexistence clarity):
  - `.claude/skills/README.md`
  - `.claude/skills/doc-tspec/SKILL.md`
  - `.claude/skills/doc-tspec-autopilot/SKILL.md`

---

## 3. Baseline Findings (From Scratch Audit)

1. No dedicated `doc-itest*` skill set currently exists in `.claude/skills/`.
2. Current integration testing guidance is embedded in TSPEC-generic skills (`doc-tspec*`).
3. Canonical ITEST assets are available and authoritative:
   - `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md`
   - `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_CREATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_VALIDATION_RULES.md`
4. ITEST template enforces subtype-specific constraints justifying specialization:
   - 6-section structure
   - required integration tags include `@ctr` and `@sys`
   - focus on contract compliance, component interaction, sequence/data flow verification
   - TASKS-Ready threshold `>=90%`
   - sequence diagrams for complex interactions

Current diagnostics posture:
- Capability expansion (new skill set), not blocker remediation.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **Overlap Risk with `doc-tspec*`**
   - Must define deterministic routing between ITEST-specific and TSPEC-generic workflows.
2. **Canonical Drift Risk**
   - New ITEST skills must only reference canonical ITEST assets and existing scripts.
3. **Wrapper/Fixer Compatibility Risk**
   - `doc-itest-fixer` must support:
     - `ITEST-NN.A_audit_report_vNNN.md` (preferred)
     - `ITEST-NN.R_review_report_vNNN.md` (legacy)
4. **Cross-Workspace Scope Risk**
   - Edits/staging must remain scoped to `/opt/data/ucx_framework`.
5. **Metadata/Versioning Risk**
   - All new skills must use normalized `metadata` frontmatter + `versioning_policy`.
6. **README Discoverability Risk**
   - New skills must be visible in reviewer/audit/fixer/autopilot/core sections.
7. **Command Reference Risk**
   - Use canonical script paths only (`validate_itest.py`, shared validators).

---

## 5. Design Approach (Subtype-Specialized)

### 5.1 Target ITEST Topology

- `doc-itest`: subtype authoring guidance
- `doc-itest-autopilot`: generate/find/review orchestration
- `doc-itest-validator`: schema/structure/tag validation
- `doc-itest-reviewer`: semantic quality and integration-completeness review
- `doc-itest-fixer`: remediation workflow with deterministic report precedence
- `doc-itest-audit`: unified validator+reviewer wrapper

### 5.2 Audit Wrapper Contract (`doc-itest-audit`)

Sequence:
1. run `doc-itest-validator`
2. run `doc-itest-reviewer`
3. normalize findings
4. emit `ITEST-NN.A_audit_report_vNNN.md`
5. optional handoff to `doc-itest-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 Coexistence Contract with TSPEC

- `doc-tspec*` remains canonical multi-subtype path.
- `doc-itest*` provides subtype-optimized path for integration contract/interaction testing.
- Both may coexist; README must clarify positioning to reduce ambiguity.

### 5.4 Routing Rules (Operational)

Use `doc-itest*` when:
- authoring/reviewing/fixing ITEST-only artifacts,
- contract compliance (`@ctr`) and integration interaction checks are primary.

Use `doc-tspec*` when:
- mixed subtype orchestration is required,
- cross-subtype normalization or batch TSPEC flow is primary.

Fallback rule:
- If `doc-itest*` yields unresolved blockers, route to `doc-tspec*` path while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## 6. Implementation Phases

### Phase A0 — ITEST Canonical Conformance Gate

Authoritative references:
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml`
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_itest.py`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh`
- `ai_dev_ssd_flow/scripts/validate_cross_document.py`
- `ai_dev_ssd_flow/scripts/validate_tags_against_docs.py`

Checklist:
1. Confirm 6-section ITEST contract and heading conventions.
2. Confirm required tags (`@ctr`, `@sys`) and cumulative tags.
3. Confirm TASKS-Ready threshold and CTR/SYS coverage framing.
4. Confirm sequence diagram requirement for complex interactions.
5. Confirm canonical validator/script references.

Acceptance:
- No contradictions between planned ITEST skills and canonical ITEST references.

### Phase A — Create Core ITEST Skills (`doc-itest`, `doc-itest-autopilot`)

Files:
- `.claude/skills/doc-itest/SKILL.md`
- `.claude/skills/doc-itest-autopilot/SKILL.md`

Actions:
- Define ITEST-specific authoring contracts and examples.
- Define autopilot generate/find/review flow aligned to ITEST naming/path rules.
- Include explicit relationship with `doc-tspec` (coexistence, not replacement).

Acceptance:
- Core skills parse cleanly and reference canonical ITEST assets only.

### Phase B — Create QA Skills (`doc-itest-validator`, `doc-itest-reviewer`, `doc-itest-fixer`)

Files:
- `.claude/skills/doc-itest-validator/SKILL.md`
- `.claude/skills/doc-itest-reviewer/SKILL.md`
- `.claude/skills/doc-itest-fixer/SKILL.md`

Actions:
- Implement subtype validation/review checks aligned to ITEST contract requirements.
- Define fixer auto/manual boundaries and deterministic report precedence.
- Ensure examples use versioned report names and canonical script paths.

Acceptance:
- QA contracts are internally consistent and audit-wrapper ready.

### Phase C — Add Unified Wrapper (`doc-itest-audit`)

File:
- `.claude/skills/doc-itest-audit/SKILL.md`

Actions:
- Mirror established `doc-*-audit` wrapper structure.
- Define combined output contract and fixer handoff semantics.
- Include invocation examples for direct audit and remediation handoff.

Acceptance:
- Wrapper references only existing ITEST validator/reviewer/fixer skills.

### Phase D — Skills Index and Integration

File:
- `.claude/skills/README.md`

Actions:
- Register new ITEST skills in reviewer/audit/fixer/autopilot/core sections.
- Add ITEST audit wrapper to audit-wrapper listing.
- Add explicit routing guidance for `doc-itest*` vs `doc-tspec*`.

Acceptance:
- Discoverability complete and routing guidance non-conflicting.

### Phase E — Validation and Evidence

Actions:
- Run diagnostics on all six new ITEST skills + README updates.
- Run scoped grep checks for:
  - stale path markers (`ai_dev_flow`),
  - non-versioned review report naming,
  - `ITEST-NN.R_review_report.md` (non-versioned) patterns,
  - missing `ITEST-NN.A_audit_report_vNNN.md` examples in audit/fixer contracts,
  - missing audit-wrapper references,
  - non-canonical validator references.
- Validate scoped git status in `/opt/data/ucx_framework` only.

Acceptance:
- No parser/diagnostic blockers in touched files.
- Drift regex checks pass for touched ITEST skills.
- Change set is scoped to ITEST skill-set introduction and README integration.

---

## 7. Deliverables

1. New ITEST 6-skill pack under `.claude/skills/doc-itest*/`.
2. New wrapper: `.claude/skills/doc-itest-audit/SKILL.md`.
3. Updated `.claude/skills/README.md` with ITEST registrations.
4. Validation evidence report.

---

## 8. Definition of Done

- All six `doc-itest*` skills created with normalized metadata schema and version history.
- ITEST contracts aligned to canonical ITEST template/rules/schema/scripts.
- Audit-first remediation path documented: `autopilot -> audit -> fixer`.
- Fixer report precedence explicit (`latest timestamp`; tie => `.A_` over `.R_`).
- README includes ITEST discoverability and routing guidance.
- Evidence bundle generated: `tmp/IPLAN-019_validation_evidence_YYYY-MM-DD.md`.
- Diagnostics and drift checks pass for all touched files.

---

## 9. Execution Notes

- This plan introduces a subtype-specialized ITEST stack and does not deprecate TSPEC-generic skills.
- If MVP scope reduction is needed, execute Phase A + C first (core + wrapper), then Phase B (full QA specialization).
- Rollout fallback: if partial adoption causes ambiguity, keep `doc-tspec*` as primary and treat `doc-itest*` as opt-in until routing guidance and validation evidence are confirmed.
