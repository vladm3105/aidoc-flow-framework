---
title: "IPLAN-022: STEST Skill Set + Audit Wrapper"
tags:
  - implementation-plan
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-022
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-022: STEST Skill Set + Audit Wrapper

## 1. Objective

Create an STEST-specialized Claude skill stack for **Smoke Test Specification** workflows, while preserving compatibility with existing `doc-tspec` orchestration.

Target outcome: introduce a dedicated 6-skill STEST set with audit-first flow:
- `doc-stest`
- `doc-stest-autopilot`
- `doc-stest-validator`
- `doc-stest-reviewer`
- `doc-stest-fixer`
- `doc-stest-audit` (new wrapper)

---

## 2. Scope

### In Scope
- New skill files under `.claude/skills/`:
  - `.claude/skills/doc-stest/SKILL.md`
  - `.claude/skills/doc-stest-autopilot/SKILL.md`
  - `.claude/skills/doc-stest-validator/SKILL.md`
  - `.claude/skills/doc-stest-reviewer/SKILL.md`
  - `.claude/skills/doc-stest-fixer/SKILL.md`
  - `.claude/skills/doc-stest-audit/SKILL.md`
- Skill registry updates:
  - `.claude/skills/README.md`
- Minimal coexistence cross-links between STEST subtype flow and TSPEC-generic flow.

### Out of Scope
- Changes to canonical template/rules/schema under `ai_dev_ssd_flow/10_TSPEC/STEST/*`
- Runtime script behavior changes under `ai_dev_ssd_flow/10_TSPEC/scripts/*`
- Broad refactor of existing `doc-tspec*` skill family.
- Allowed cross-link touchpoints only (if needed for coexistence clarity):
  - `.claude/skills/README.md`
  - `.claude/skills/doc-tspec/SKILL.md`
  - `.claude/skills/doc-tspec-autopilot/SKILL.md`

---

## 3. Baseline Findings (From Scratch Audit)

1. No dedicated `doc-stest*` skill set currently exists in `.claude/skills/`.
2. Smoke testing guidance currently routes through TSPEC-generic skills (`doc-tspec*`).
3. Canonical STEST assets are available and authoritative:
   - `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md`
   - `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_CREATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_VALIDATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_QUALITY_GATES.md`
4. STEST template enforces subtype-specific constraints justifying specialization:
   - 6-section structure
   - required STEST-specific tags include `@ears`, `@bdd`, `@req`
   - suite timeout budget `<5 minutes` (max 300s)
   - 100% quality gate requirement for deployment smoke validation
   - fail-fast binary pass/fail expectations
   - rollback procedure required for every critical path test

Current diagnostics posture:
- Capability expansion (new skill set), not blocker remediation.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **Overlap Risk with `doc-tspec*`**
   - Must define deterministic routing between STEST-specific and TSPEC-generic workflows.
2. **Canonical Drift Risk**
   - New STEST skills must reference canonical STEST assets and existing scripts only.
3. **Wrapper/Fixer Compatibility Risk**
   - `doc-stest-fixer` must support:
     - `STEST-NN.A_audit_report_vNNN.md` (preferred)
     - `STEST-NN.R_review_report_vNNN.md` (legacy)
4. **Cross-Workspace Scope Risk**
   - Edits/staging must remain scoped to `/opt/data/ucx_framework`.
5. **Metadata/Versioning Risk**
   - All new skills must use normalized `metadata` frontmatter + `versioning_policy`.
6. **README Discoverability Risk**
   - New skills must be visible in reviewer/audit/fixer/autopilot/core sections.
7. **Command Reference Risk**
   - Use canonical script paths only (`validate_stest.py`, shared validators).
8. **False-Positive Grep Risk**
   - Phase-E regex checks must target skill/README files only (exclude `plans/` and `tmp/`).
9. **Deployment Gate Risk**
   - Skills must preserve timeout and rollback obligations and enforce 100% quality-gate framing.

---

## 5. Design Approach (Subtype-Specialized)

### 5.1 Target STEST Topology

- `doc-stest`: subtype authoring guidance
- `doc-stest-autopilot`: generate/find/review orchestration
- `doc-stest-validator`: schema/structure/tag/deployment-smoke validation
- `doc-stest-reviewer`: semantic quality and deployment-readiness review
- `doc-stest-fixer`: remediation workflow with deterministic report precedence
- `doc-stest-audit`: unified validator+reviewer wrapper

### 5.2 Audit Wrapper Contract (`doc-stest-audit`)

Sequence:
1. run `doc-stest-validator`
2. run `doc-stest-reviewer`
3. normalize findings
4. emit `STEST-NN.A_audit_report_vNNN.md`
5. optional handoff to `doc-stest-fixer`

Combined status:
- PASS: validator PASS AND reviewer score = 100 AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

Deployment-gate policy:
- Timeout budget violations, missing rollback procedures, or non-binary pass/fail criteria are `manual_required` or `blocked` and cannot auto-pass.

### 5.3 Coexistence Contract with TSPEC

- `doc-tspec*` remains canonical multi-subtype path.
- `doc-stest*` provides subtype-optimized path for smoke testing workflows.
- Both may coexist; README must clarify positioning.

### 5.4 Routing Rules (Operational)

Use `doc-stest*` when:
- authoring/reviewing/fixing STEST-only artifacts,
- deployment verification and fail-fast smoke validation are primary.

Use `doc-tspec*` when:
- mixed subtype orchestration is required,
- cross-subtype normalization or batch TSPEC flow is primary.

Fallback rule:
- If `doc-stest*` yields unresolved blockers, route to `doc-tspec*` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## 6. Implementation Phases

### Phase A0 — STEST Canonical Conformance Gate

Authoritative references:
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.yaml`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_QUALITY_GATES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_stest.py`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh`
- `ai_dev_ssd_flow/scripts/validate_cross_document.py`
- `ai_dev_ssd_flow/scripts/validate_tags_against_docs.py`

Checklist:
1. Confirm 6-section STEST contract and heading conventions.
2. Confirm required tags (`@ears`, `@bdd`, `@req`) and cumulative tags.
3. Confirm 100% quality-gate requirement and deployment-smoke framing.
4. Confirm timeout budget (`<=300s`) and fail-fast binary pass/fail rules.
5. Confirm rollback procedure requirements for each critical path test.
6. Confirm canonical validator/script references.

Acceptance:
- No contradictions between planned STEST skills and canonical STEST references.

### Phase A — Create Core STEST Skills (`doc-stest`, `doc-stest-autopilot`)

Files:
- `.claude/skills/doc-stest/SKILL.md`
- `.claude/skills/doc-stest-autopilot/SKILL.md`

Actions:
- Define STEST-specific authoring contracts and examples.
- Define autopilot generate/find/review flow aligned to STEST naming/path rules.
- Define explicit autopilot input contract:
  - `STEST-NN` (self type): review existing,
  - `EARS-NN` or `BDD-NN` or `REQ-NN`: generate if missing, else review existing `STEST-NN`,
  - optional `SPEC-NN`: include deployment-target consistency checks when present.
- Include explicit relationship with `doc-tspec` (coexistence, not replacement).

Acceptance:
- Core skills parse cleanly and reference canonical STEST assets only.

### Phase B — Create QA Skills (`doc-stest-validator`, `doc-stest-reviewer`, `doc-stest-fixer`)

Files:
- `.claude/skills/doc-stest-validator/SKILL.md`
- `.claude/skills/doc-stest-reviewer/SKILL.md`
- `.claude/skills/doc-stest-fixer/SKILL.md`

Actions:
- Implement subtype validation/review checks aligned to STEST contract requirements.
- Define fixer auto/manual boundaries and deterministic report precedence.
- Ensure examples use versioned report names and canonical script paths.

Acceptance:
- QA contracts are internally consistent and audit-wrapper ready.

### Phase C — Add Unified Wrapper (`doc-stest-audit`)

File:
- `.claude/skills/doc-stest-audit/SKILL.md`

Actions:
- Mirror established `doc-*-audit` wrapper structure.
- Define combined output contract and fixer handoff semantics.
- Include invocation examples for direct audit and remediation handoff.

Acceptance:
- Wrapper references only existing STEST validator/reviewer/fixer skills.

### Phase D — Skills Index and Integration

File:
- `.claude/skills/README.md`

Actions:
- Register new STEST skills in reviewer/audit/fixer/autopilot/core sections.
- Add STEST audit wrapper to audit-wrapper listing.
- Add explicit routing guidance for `doc-stest*` vs `doc-tspec*`.

Acceptance:
- Discoverability complete and routing guidance non-conflicting.

### Phase E — Validation and Evidence

Actions:
- Run diagnostics on all six new STEST skills + README updates.
- Run scoped grep checks against `.claude/skills/doc-stest*/SKILL.md` and `.claude/skills/README.md` only:
  - stale path markers (`ai_dev_flow`),
  - non-versioned review report naming,
  - `STEST-NN.R_review_report.md` (non-versioned) patterns,
  - missing `STEST-NN.A_audit_report_vNNN.md` examples in audit/fixer contracts,
  - missing audit-wrapper references,
  - non-canonical validator references,
  - missing timeout/rollback/100%-gate requirements in authoring/review contracts,
   - missing binary pass/fail wording for critical path expectations,
   - missing explicit deployment gate phrases (`max 300s` or `<=300s`, `Target: 100%` or `100% quality gate`, `every test must have rollback procedure`).
- Validate scoped git status in `/opt/data/ucx_framework` only.
- Generate evidence bundle: `tmp/IPLAN-022_validation_evidence_YYYY-MM-DD.md`.

Acceptance:
- No parser/diagnostic blockers in touched files.
- Drift regex checks pass for touched STEST skills.
- Deployment-gate markers are present (timeout, rollback, 100% gate, binary pass/fail).
- Change set is scoped to STEST skill-set introduction and README integration.

---

## 7. Deliverables

1. New STEST 6-skill pack under `.claude/skills/doc-stest*/`.
2. New wrapper: `.claude/skills/doc-stest-audit/SKILL.md`.
3. Updated `.claude/skills/README.md` with STEST registrations.
4. Validation evidence report.

---

## 8. Definition of Done

- All six `doc-stest*` skills created with normalized metadata schema and version history.
- STEST contracts aligned to canonical STEST template/rules/schema/scripts.
- Audit-first remediation path documented: `autopilot -> audit -> fixer`.
- Fixer report precedence explicit (`latest timestamp`; tie => `.A_` over `.R_`).
- README includes STEST discoverability and routing guidance.
- Evidence bundle generated: `tmp/IPLAN-022_validation_evidence_YYYY-MM-DD.md`.
- Diagnostics and drift checks pass for all touched files.

---

## 9. Execution Notes

- This plan introduces a subtype-specialized STEST stack and does not deprecate TSPEC-generic skills.
- If MVP scope reduction is needed, execute Phase A + C first (core + wrapper), then Phase B (full QA specialization).
- Rollout fallback: if partial adoption causes ambiguity, keep `doc-tspec*` as primary and treat `doc-stest*` as opt-in until routing guidance and validation evidence are confirmed.
