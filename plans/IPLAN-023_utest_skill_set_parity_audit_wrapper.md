---
title: "IPLAN-023: UTEST Skill Set + Audit Wrapper"
tags:
  - implementation-plan
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-023
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-023: UTEST Skill Set + Audit Wrapper

## 1. Objective

Create a UTEST-specialized Claude skill stack for **Unit Test Specification** workflows, while preserving compatibility with existing `doc-tspec` orchestration.

Target outcome: introduce a dedicated 6-skill UTEST set with audit-first flow:
- `doc-utest`
- `doc-utest-autopilot`
- `doc-utest-validator`
- `doc-utest-reviewer`
- `doc-utest-fixer`
- `doc-utest-audit` (new wrapper)

---

## 2. Scope

### In Scope
- New skill files under `.claude/skills/`:
  - `.claude/skills/doc-utest/SKILL.md`
  - `.claude/skills/doc-utest-autopilot/SKILL.md`
  - `.claude/skills/doc-utest-validator/SKILL.md`
  - `.claude/skills/doc-utest-reviewer/SKILL.md`
  - `.claude/skills/doc-utest-fixer/SKILL.md`
  - `.claude/skills/doc-utest-audit/SKILL.md`
- Skill registry updates:
  - `.claude/skills/README.md`
- Minimal coexistence cross-links between UTEST subtype flow and TSPEC-generic flow.

### Out of Scope
- Changes to canonical template/rules/schema under `ai_dev_ssd_flow/10_TSPEC/UTEST/*`
- Runtime script behavior changes under `ai_dev_ssd_flow/10_TSPEC/scripts/*`
- Broad refactor of existing `doc-tspec*` skill family.
- Allowed cross-link touchpoints only (if needed for coexistence clarity):
  - `.claude/skills/README.md`
  - `.claude/skills/doc-tspec/SKILL.md`
  - `.claude/skills/doc-tspec-autopilot/SKILL.md`

---

## 3. Baseline Findings (From Scratch Audit)

1. No dedicated `doc-utest*` skill set currently exists in `.claude/skills/`.
2. Unit-testing guidance currently routes through TSPEC-generic skills (`doc-tspec*`).
3. Canonical UTEST assets are available and authoritative:
   - `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md`
   - `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_CREATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_VALIDATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_QUALITY_GATES.md`
4. UTEST template enforces subtype-specific constraints justifying specialization:
   - 6-section structure
   - required UTEST tags include `@req` and `@spec`
   - required categories `[Logic]`, `[State]`, `[Validation]`, `[Edge]`
   - Input/Output tables for all test cases
   - pseudocode requirement for complex test logic
   - TASKS-Ready threshold `>=90%`

Current diagnostics posture:
- Capability expansion (new skill set), not blocker remediation.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **Overlap Risk with `doc-tspec*`**
   - Must define deterministic routing between UTEST-specific and TSPEC-generic workflows.
2. **Canonical Drift Risk**
   - New UTEST skills must reference canonical UTEST assets and existing scripts only.
3. **Wrapper/Fixer Compatibility Risk**
   - `doc-utest-fixer` must support:
     - `UTEST-NN.A_audit_report_vNNN.md` (preferred)
     - `UTEST-NN.R_review_report_vNNN.md` (legacy)
4. **Cross-Workspace Scope Risk**
   - Edits/staging must remain scoped to `/opt/data/ucx_framework`.
5. **Metadata/Versioning Risk**
   - All new skills must use normalized `metadata` frontmatter + `versioning_policy`.
6. **README Discoverability Risk**
   - New skills must be visible in reviewer/audit/fixer/autopilot/core sections.
7. **Command Reference Risk**
   - Use canonical script paths only (`validate_utest.py`, shared validators).
8. **False-Positive Grep Risk**
   - Phase-E regex checks must target skill/README files only (exclude `plans/` and `tmp/`).

---

## 5. Design Approach (Subtype-Specialized)

### 5.1 Target UTEST Topology

- `doc-utest`: subtype authoring guidance
- `doc-utest-autopilot`: generate/find/review orchestration
- `doc-utest-validator`: schema/structure/tag/unit-test-contract validation
- `doc-utest-reviewer`: semantic quality and REQ-coverage review
- `doc-utest-fixer`: remediation workflow with deterministic report precedence
- `doc-utest-audit`: unified validator+reviewer wrapper

### 5.2 Audit Wrapper Contract (`doc-utest-audit`)

Sequence:
1. run `doc-utest-validator`
2. run `doc-utest-reviewer`
3. normalize findings
4. emit `UTEST-NN.A_audit_report_vNNN.md`
5. optional handoff to `doc-utest-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 Coexistence Contract with TSPEC

- `doc-tspec*` remains canonical multi-subtype path.
- `doc-utest*` provides subtype-optimized path for unit-testing workflows.
- Both may coexist; README must clarify positioning.

### 5.4 Routing Rules (Operational)

Use `doc-utest*` when:
- authoring/reviewing/fixing UTEST-only artifacts,
- REQ-level unit logic/state/validation/edge checks are primary.

Use `doc-tspec*` when:
- mixed subtype orchestration is required,
- cross-subtype normalization or batch TSPEC flow is primary.

Fallback rule:
- If `doc-utest*` yields unresolved blockers, route to `doc-tspec*` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## 6. Implementation Phases

### Phase A0 — UTEST Canonical Conformance Gate

Authoritative references:
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.yaml`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_QUALITY_GATES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_utest.py`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh`
- `ai_dev_ssd_flow/scripts/validate_cross_document.py`
- `ai_dev_ssd_flow/scripts/validate_tags_against_docs.py`

Checklist:
1. Confirm 6-section UTEST contract and heading conventions.
2. Confirm required tags (`@req`, `@spec`) and cumulative tags.
3. Confirm TASKS-Ready threshold and REQ-coverage framing.
4. Confirm Input/Output table requirement for all test cases.
5. Confirm pseudocode guidance for complex logic.
6. Confirm canonical validator/script references.

Acceptance:
- No contradictions between planned UTEST skills and canonical UTEST references.

### Phase A — Create Core UTEST Skills (`doc-utest`, `doc-utest-autopilot`)

Files:
- `.claude/skills/doc-utest/SKILL.md`
- `.claude/skills/doc-utest-autopilot/SKILL.md`

Actions:
- Define UTEST-specific authoring contracts and examples.
- Define autopilot generate/find/review flow aligned to UTEST naming/path rules.
- Define explicit autopilot input contract:
  - `UTEST-NN` (self type): review existing,
  - `REQ-NN` or `SPEC-NN`: generate if missing, else review existing `UTEST-NN`,
  - optional `CTR-NN`: include contract-alignment checks when present.
- Include explicit relationship with `doc-tspec` (coexistence, not replacement).

Acceptance:
- Core skills parse cleanly and reference canonical UTEST assets only.

### Phase B — Create QA Skills (`doc-utest-validator`, `doc-utest-reviewer`, `doc-utest-fixer`)

Files:
- `.claude/skills/doc-utest-validator/SKILL.md`
- `.claude/skills/doc-utest-reviewer/SKILL.md`
- `.claude/skills/doc-utest-fixer/SKILL.md`

Actions:
- Implement subtype validation/review checks aligned to UTEST contract requirements.
- Define fixer auto/manual boundaries and deterministic report precedence.
- Ensure examples use versioned report names and canonical script paths.

Acceptance:
- QA contracts are internally consistent and audit-wrapper ready.

### Phase C — Add Unified Wrapper (`doc-utest-audit`)

File:
- `.claude/skills/doc-utest-audit/SKILL.md`

Actions:
- Mirror established `doc-*-audit` wrapper structure.
- Define combined output contract and fixer handoff semantics.
- Include invocation examples for direct audit and remediation handoff.

Acceptance:
- Wrapper references only existing UTEST validator/reviewer/fixer skills.

### Phase D — Skills Index and Integration

File:
- `.claude/skills/README.md`

Actions:
- Register new UTEST skills in reviewer/audit/fixer/autopilot/core sections.
- Add UTEST audit wrapper to audit-wrapper listing.
- Add explicit routing guidance for `doc-utest*` vs `doc-tspec*`.

Acceptance:
- Discoverability complete and routing guidance non-conflicting.

### Phase E — Validation and Evidence

Actions:
- Run diagnostics on all six new UTEST skills + README updates.
- Run scoped grep checks against `.claude/skills/doc-utest*/SKILL.md` and `.claude/skills/README.md` only:
  - stale path markers (`ai_dev_flow`),
  - non-versioned review report naming,
  - `UTEST-NN.R_review_report.md` (non-versioned) patterns,
  - missing `UTEST-NN.A_audit_report_vNNN.md` examples in audit/fixer contracts,
  - missing audit-wrapper references,
  - non-canonical validator references,
  - missing IO-table/pseudocode/REQ-coverage requirements in authoring/review contracts.
- Validate scoped git status in `/opt/data/ucx_framework` only.
- Generate evidence bundle: `tmp/IPLAN-023_validation_evidence_YYYY-MM-DD.md`.

Acceptance:
- No parser/diagnostic blockers in touched files.
- Drift regex checks pass for touched UTEST skills.
- UTEST gate markers are present (IO tables, pseudocode guidance, REQ coverage).
- Change set is scoped to UTEST skill-set introduction and README integration.

---

## 7. Deliverables

1. New UTEST 6-skill pack under `.claude/skills/doc-utest*/`.
2. New wrapper: `.claude/skills/doc-utest-audit/SKILL.md`.
3. Updated `.claude/skills/README.md` with UTEST registrations.
4. Validation evidence report.

---

## 8. Definition of Done

- All six `doc-utest*` skills created with normalized metadata schema and version history.
- UTEST contracts aligned to canonical UTEST template/rules/schema/scripts.
- Audit-first remediation path documented: `autopilot -> audit -> fixer`.
- Fixer report precedence explicit (`latest timestamp`; tie => `.A_` over `.R_`).
- README includes UTEST discoverability and routing guidance.
- Evidence bundle generated: `tmp/IPLAN-023_validation_evidence_YYYY-MM-DD.md`.
- Diagnostics and drift checks pass for all touched files.

---

## 9. Execution Notes

- This plan introduces a subtype-specialized UTEST stack and does not deprecate TSPEC-generic skills.
- If MVP scope reduction is needed, execute Phase A + C first (core + wrapper), then Phase B (full QA specialization).
- Rollout fallback: if partial adoption causes ambiguity, keep `doc-tspec*` as primary and treat `doc-utest*` as opt-in until routing guidance and validation evidence are confirmed.
