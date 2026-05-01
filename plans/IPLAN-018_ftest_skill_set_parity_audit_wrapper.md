---
title: "IPLAN-018: FTEST Skill Set + Audit Wrapper"
tags:
  - implementation-plan
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-018
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-018: FTEST Skill Set + Audit Wrapper

## 1. Objective

Create an FTEST-specialized Claude skill stack (mirroring BRD-style parity model) for **Functional Test Specification** workflows, while preserving compatibility with existing `doc-tspec` orchestration.

Target outcome: introduce a dedicated 6-skill FTEST set with unified audit-first flow:
- `doc-ftest`
- `doc-ftest-autopilot`
- `doc-ftest-validator`
- `doc-ftest-reviewer`
- `doc-ftest-fixer`
- `doc-ftest-audit` (new wrapper)

---

## 2. Scope

### In Scope
- New skill files under `.claude/skills/`:
  - `.claude/skills/doc-ftest/SKILL.md`
  - `.claude/skills/doc-ftest-autopilot/SKILL.md`
  - `.claude/skills/doc-ftest-validator/SKILL.md`
  - `.claude/skills/doc-ftest-reviewer/SKILL.md`
  - `.claude/skills/doc-ftest-fixer/SKILL.md`
  - `.claude/skills/doc-ftest-audit/SKILL.md`
- Skill registry update:
  - `.claude/skills/README.md`
- Contract compatibility references between FTEST stack and TSPEC stack.

### Out of Scope
- Changes to canonical template/rules/schema files under `ai_dev_ssd_flow/10_TSPEC/FTEST/*`
- Runtime script behavior changes under `ai_dev_ssd_flow/10_TSPEC/scripts/*`
- Broad refactor of existing `doc-tspec*` skill family.
- Allowed cross-link touchpoints only (if needed for coexistence clarity):
   - `.claude/skills/README.md`
   - `.claude/skills/doc-tspec/SKILL.md`
   - `.claude/skills/doc-tspec-autopilot/SKILL.md`

---

## 3. Baseline Findings (From Scratch Audit)

1. No dedicated `doc-ftest*` skill set currently exists in `.claude/skills/`.
2. Current test-spec workflow is TSPEC-generic (`doc-tspec*`) covering all subtypes (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST).
3. FTEST canonical source exists and is explicit in:
   - `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.md`
   - `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_SCHEMA.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_CREATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_VALIDATION_RULES.md`
4. FTEST template enforces subtype-specific constraints that justify specialization:
   - 6-section structure
   - required tags include `@sys` and `@threshold`
   - focus on system quality attributes
   - TASKS-Ready threshold `>=90%`
   - nested folder requirement: `FTEST-NN_{slug}/FTEST-NN_{slug}.md`

Current diagnostics posture:
- This is a capability expansion task (new skills), not remediation of parser blockers.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **Overlap Risk with `doc-tspec*`**
   - Avoid duplicate/conflicting ownership; define FTEST stack as subtype-specialized, not TSPEC replacement.
2. **Canonical-Source Drift Risk**
   - FTEST skills must reference only `ai_dev_ssd_flow/10_TSPEC/FTEST/*` canonical artifacts.
3. **Wrapper/Fixer Contract Risk**
   - `doc-ftest-fixer` must support both:
     - `FTEST-NN.A_audit_report_vNNN.md` (preferred)
     - `FTEST-NN.R_review_report_vNNN.md` (legacy)
4. **Cross-Workspace Scope Risk**
   - Changes and staging must remain scoped to `/opt/data/ucx_framework`.
5. **Metadata/Versioning Drift Risk**
   - All new skills must use normalized `metadata` frontmatter + `versioning_policy`.
6. **README Discoverability Risk**
   - Add FTEST skills in reviewer/audit/fixer and core workflow sections with consistent layer labeling.
7. **Validation Command Drift Risk**
   - Use canonical script references only (e.g., `validate_ftest.py`, `validate_all_tspec.sh`, `validate_tspec_quality_score.sh`, shared cross-doc/tag validators where applicable).

---

## 5. Design Approach (Mirror BRD Pattern, Subtype-Specialized)

### 5.1 Target FTEST Topology

- `doc-ftest`: authoring workflow for FTEST documents only
- `doc-ftest-autopilot`: generation/review-or-find flow for FTEST subtype
- `doc-ftest-validator`: schema/structure/contract checks for FTEST subtype
- `doc-ftest-reviewer`: semantic quality review for FTEST subtype
- `doc-ftest-fixer`: remediation with deterministic report precedence
- `doc-ftest-audit`: unified validator + reviewer wrapper

### 5.2 Audit Wrapper Contract (`doc-ftest-audit`)

Sequence:
1. run `doc-ftest-validator`
2. run `doc-ftest-reviewer`
3. normalize findings
4. emit `FTEST-NN.A_audit_report_vNNN.md`
5. optional handoff to `doc-ftest-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 Coexistence Contract with TSPEC

- `doc-tspec*` remains canonical multi-type path.
- `doc-ftest*` provides subtype-optimized path for functional quality-attribute testing.
- Both may coexist; README must clarify positioning to reduce operator confusion.

### 5.4 Routing Rules (Operational)

Use `doc-ftest*` when:
- authoring/reviewing/fixing FTEST-only artifacts,
- FTEST subtype constraints (`@sys`, `@threshold`, quality-attribute checks) are primary.

Use `doc-tspec*` when:
- mixed TSPEC subtype orchestration is required (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST),
- cross-subtype normalization or shared TSPEC batch workflow is primary.

Fallback rule:
- If `doc-ftest*` yields unresolved blockers, route to `doc-tspec*` path and preserve report compatibility (`.A_` preferred, `.R_` legacy).

---

## 6. Implementation Phases

### Phase A0 — FTEST Canonical Conformance Gate

Authoritative references:
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.yaml`
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_ftest.py`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh`
- `ai_dev_ssd_flow/scripts/validate_cross_document.py`
- `ai_dev_ssd_flow/scripts/validate_tags_against_docs.py`

Checklist:
1. Confirm 6-section FTEST contract and heading conventions.
2. Confirm required subtype tags (`@sys`, `@threshold`) and cumulative tags.
3. Confirm TASKS-Ready threshold and SYS-coverage framing.
4. Confirm nested-folder path contract for FTEST docs.
5. Confirm canonical validator/script references.

Acceptance:
- No contradictions between planned FTEST skills and canonical FTEST template/rules/schema.

### Phase A — Create Core FTEST Skills (`doc-ftest`, `doc-ftest-autopilot`)

Files:
- `.claude/skills/doc-ftest/SKILL.md`
- `.claude/skills/doc-ftest-autopilot/SKILL.md`

Actions:
- Define FTEST-only authoring guidance, examples, and quality gates.
- Define autopilot flow (generate/find/review) aligned to FTEST naming/location contracts.
- Include explicit relationship with `doc-tspec` (coexistence, not replacement).

Acceptance:
- Core skills parse cleanly and reference only canonical FTEST assets.

### Phase B — Create QA Skills (`doc-ftest-validator`, `doc-ftest-reviewer`, `doc-ftest-fixer`)

Files:
- `.claude/skills/doc-ftest-validator/SKILL.md`
- `.claude/skills/doc-ftest-reviewer/SKILL.md`
- `.claude/skills/doc-ftest-fixer/SKILL.md`

Actions:
- Implement FTEST-specific validation/review checks mapped to template constraints.
- Define fixer auto/manual boundaries and deterministic report precedence.
- Ensure examples use versioned report filenames and canonical scripts.

Acceptance:
- QA skill contracts are internally consistent and audit-wrapper ready.

### Phase C — Add Unified Wrapper (`doc-ftest-audit`)

File:
- `.claude/skills/doc-ftest-audit/SKILL.md`

Actions:
- Mirror proven wrapper structure from existing `doc-*-audit` skills.
- Define combined output and handoff contract for fixer.
- Include invocation examples for direct audit + remediation.

Acceptance:
- Wrapper references existing FTEST validator/reviewer/fixer skills only.

### Phase D — Skills Index and Integration

File:
- `.claude/skills/README.md`

Actions:
- Register new FTEST skills in appropriate sections.
- Add FTEST audit wrapper to audit-wrapper listing.
- Keep layer and workflow descriptions consistent.
- Add explicit routing guidance for `doc-ftest*` vs `doc-tspec*` in README skill descriptions.

Acceptance:
- FTEST skills are discoverable and classification is internally consistent.
- Routing guidance is explicit and non-conflicting across README and skill contracts.

### Phase E — Validation and Evidence

Actions:
- Run diagnostics on all six new FTEST skills + README updates.
- Run scoped grep checks for:
   - stale path/script markers (`ai_dev_flow`),
   - non-versioned review report naming,
   - `FTEST-NN.R_review_report.md` (non-versioned) patterns,
   - missing `FTEST-NN.A_audit_report_vNNN.md` examples in audit/fixer contracts,
   - missing audit-wrapper references,
   - non-canonical validator references.
- Validate scoped git status in `/opt/data/ucx_framework` only.

Acceptance:
- No parser/diagnostic blockers in touched files.
- Drift regex checks pass for touched FTEST skills.
- Change set is scoped to FTEST skill-set introduction and README integration.

---

## 7. Deliverables

1. New FTEST 6-skill pack under `.claude/skills/doc-ftest*/`.
2. New unified wrapper: `.claude/skills/doc-ftest-audit/SKILL.md`.
3. Updated `.claude/skills/README.md` with FTEST registrations.
4. Validation evidence (diagnostics + grep drift checks).

---

## 8. Definition of Done

- All six `doc-ftest*` skills created with normalized metadata schema and version history.
- FTEST contract aligned to canonical FTEST template/rules/schema/scripts.
- Audit-first remediation path documented: `autopilot -> audit -> fixer`.
- Fixer report precedence explicit (`latest timestamp`, tie => `.A_` over `.R_`).
- README includes FTEST skill and audit-wrapper discoverability.
- Evidence bundle generated: `tmp/IPLAN-018_validation_evidence_YYYY-MM-DD.md`.
- Diagnostics and drift checks pass for all touched files.

---

## 9. Execution Notes

- This plan intentionally introduces a subtype-specialized FTEST stack; it does not deprecate TSPEC-generic skills.
- If scope needs reduction for MVP, execute Phase A + C first (core + wrapper), then Phase B (full QA specialization).
- Rollout fallback: if partial adoption causes operator ambiguity, retain `doc-tspec*` as primary path and treat `doc-ftest*` as opt-in until routing guidance and validation evidence are confirmed.
