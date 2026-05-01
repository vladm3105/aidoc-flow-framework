---
title: "IPLAN-021: SECTEST Skill Set + Audit Wrapper"
tags:
  - implementation-plan
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-021
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-021: SECTEST Skill Set + Audit Wrapper

## 1. Objective

Create a SECTEST-specialized Claude skill stack for **Security Test Specification** workflows, while preserving compatibility with existing `doc-tspec` orchestration.

Target outcome: introduce a dedicated 6-skill SECTEST set with audit-first flow:
- `doc-sectest`
- `doc-sectest-autopilot`
- `doc-sectest-validator`
- `doc-sectest-reviewer`
- `doc-sectest-fixer`
- `doc-sectest-audit` (new wrapper)

---

## 2. Scope

### In Scope
- New skill files under `.claude/skills/`:
  - `.claude/skills/doc-sectest/SKILL.md`
  - `.claude/skills/doc-sectest-autopilot/SKILL.md`
  - `.claude/skills/doc-sectest-validator/SKILL.md`
  - `.claude/skills/doc-sectest-reviewer/SKILL.md`
  - `.claude/skills/doc-sectest-fixer/SKILL.md`
  - `.claude/skills/doc-sectest-audit/SKILL.md`
- Skill registry updates:
  - `.claude/skills/README.md`
- Minimal coexistence cross-links between SECTEST subtype flow and TSPEC-generic flow.

### Out of Scope
- Changes to canonical template/rules/schema under `ai_dev_ssd_flow/10_TSPEC/SECTEST/*`
- Runtime script behavior changes under `ai_dev_ssd_flow/10_TSPEC/scripts/*`
- Broad refactor of existing `doc-tspec*` skill family.
- Allowed cross-link touchpoints only (if needed for coexistence clarity):
  - `.claude/skills/README.md`
  - `.claude/skills/doc-tspec/SKILL.md`
  - `.claude/skills/doc-tspec-autopilot/SKILL.md`

---

## 3. Baseline Findings (From Scratch Audit)

1. No dedicated `doc-sectest*` skill set currently exists in `.claude/skills/`.
2. Security testing guidance currently routes through TSPEC-generic skills (`doc-tspec*`).
3. Canonical SECTEST assets are available and authoritative:
   - `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md`
   - `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml`
   - `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_CREATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_VALIDATION_RULES.md`
   - `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_QUALITY_GATES.md`
4. SECTEST template enforces subtype-specific constraints justifying specialization:
   - 6-section structure
   - required SECTEST tags include `@sec` and `@spec`
   - threat actor / attack vector / control documentation
   - execution profile with safety constraints
   - required categories `[AuthN]`, `[AuthZ]`, `[Input]`, `[Crypto]`, `[Config]`, `[Session]`
   - TASKS-Ready threshold `>=90%`
   - explicit isolated-environment safety rule for security testing

Current diagnostics posture:
- Capability expansion (new skill set), not blocker remediation.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **Overlap Risk with `doc-tspec*`**
   - Must define deterministic routing between SECTEST-specific and TSPEC-generic workflows.
2. **Canonical Drift Risk**
   - New SECTEST skills must reference canonical SECTEST assets and existing scripts only.
3. **Wrapper/Fixer Compatibility Risk**
   - `doc-sectest-fixer` must support:
     - `SECTEST-NN.A_audit_report_vNNN.md` (preferred)
     - `SECTEST-NN.R_review_report_vNNN.md` (legacy)
4. **Cross-Workspace Scope Risk**
   - Edits/staging must remain scoped to `/opt/data/ucx_framework`.
5. **Metadata/Versioning Risk**
   - All new skills must use normalized `metadata` frontmatter + `versioning_policy`.
6. **README Discoverability Risk**
   - New skills must be visible in reviewer/audit/fixer/autopilot/core sections.
7. **Command Reference Risk**
   - Use canonical script paths only (`validate_sectest.py`, shared validators).
8. **False-Positive Grep Risk**
   - Phase-E regex checks must target skill/README files only (exclude `plans/` and `tmp/`).
9. **Safety Framing Risk**
   - Skill content must preserve the template’s isolated-environment safety constraints and avoid operational misuse guidance.

---

## 5. Design Approach (Subtype-Specialized)

### 5.1 Target SECTEST Topology

- `doc-sectest`: subtype authoring guidance
- `doc-sectest-autopilot`: generate/find/review orchestration
- `doc-sectest-validator`: schema/structure/tag/security-contract validation
- `doc-sectest-reviewer`: semantic quality and security-completeness review
- `doc-sectest-fixer`: remediation workflow with deterministic report precedence
- `doc-sectest-audit`: unified validator+reviewer wrapper

### 5.2 Audit Wrapper Contract (`doc-sectest-audit`)

Sequence:
1. run `doc-sectest-validator`
2. run `doc-sectest-reviewer`
3. normalize findings
4. emit `SECTEST-NN.A_audit_report_vNNN.md`
5. optional handoff to `doc-sectest-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

Unsafe-guidance policy:
- Any guidance that enables operational misuse, production-targeted testing, or exploit execution steps is classified as `manual_required` or `blocked` and cannot auto-pass.

### 5.3 Coexistence Contract with TSPEC

- `doc-tspec*` remains canonical multi-subtype path.
- `doc-sectest*` provides subtype-optimized path for security testing workflows.
- Both may coexist; README must clarify positioning.

### 5.4 Routing Rules (Operational)

Use `doc-sectest*` when:
- authoring/reviewing/fixing SECTEST-only artifacts,
- security requirements and control validation are primary.

Use `doc-tspec*` when:
- mixed subtype orchestration is required,
- cross-subtype normalization or batch TSPEC flow is primary.

Fallback rule:
- If `doc-sectest*` yields unresolved blockers, route to `doc-tspec*` while preserving report compatibility (`.A_` preferred, `.R_` legacy).

---

## 6. Implementation Phases

### Phase A0 — SECTEST Canonical Conformance Gate

Authoritative references:
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.yaml`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_QUALITY_GATES.md`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_sectest.py`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh`
- `ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh`
- `ai_dev_ssd_flow/scripts/validate_cross_document.py`
- `ai_dev_ssd_flow/scripts/validate_tags_against_docs.py`

Checklist:
1. Confirm 6-section SECTEST contract and heading conventions.
2. Confirm required tags (`@sec`, `@spec`) and cumulative tags.
3. Confirm TASKS-Ready threshold and security-coverage framing.
4. Confirm threat scenario and security controls requirements.
5. Confirm execution profile safety constraints for isolated environments.
6. Confirm canonical validator/script references.

Acceptance:
- No contradictions between planned SECTEST skills and canonical SECTEST references.

### Phase A — Create Core SECTEST Skills (`doc-sectest`, `doc-sectest-autopilot`)

Files:
- `.claude/skills/doc-sectest/SKILL.md`
- `.claude/skills/doc-sectest-autopilot/SKILL.md`

Actions:
- Define SECTEST-specific authoring contracts and examples.
- Define autopilot generate/find/review flow aligned to SECTEST naming/path rules.
- Define explicit autopilot input contract:
   - `SECTEST-NN` (self type): review existing,
   - `SYS-NN` or `SPEC-NN`: generate if missing, else review existing `SECTEST-NN`,
   - optional `CTR-NN`: include contract-alignment checks when present.
- Include explicit relationship with `doc-tspec` (coexistence, not replacement).

Acceptance:
- Core skills parse cleanly and reference canonical SECTEST assets only.

### Phase B — Create QA Skills (`doc-sectest-validator`, `doc-sectest-reviewer`, `doc-sectest-fixer`)

Files:
- `.claude/skills/doc-sectest-validator/SKILL.md`
- `.claude/skills/doc-sectest-reviewer/SKILL.md`
- `.claude/skills/doc-sectest-fixer/SKILL.md`

Actions:
- Implement subtype validation/review checks aligned to SECTEST contract requirements.
- Define fixer auto/manual boundaries and deterministic report precedence.
- Ensure examples use versioned report names and canonical script paths.

Acceptance:
- QA contracts are internally consistent and audit-wrapper ready.

### Phase C — Add Unified Wrapper (`doc-sectest-audit`)

File:
- `.claude/skills/doc-sectest-audit/SKILL.md`

Actions:
- Mirror established `doc-*-audit` wrapper structure.
- Define combined output contract and fixer handoff semantics.
- Include invocation examples for direct audit and remediation handoff.

Acceptance:
- Wrapper references only existing SECTEST validator/reviewer/fixer skills.

### Phase D — Skills Index and Integration

File:
- `.claude/skills/README.md`

Actions:
- Register new SECTEST skills in reviewer/audit/fixer/autopilot/core sections.
- Add SECTEST audit wrapper to audit-wrapper listing.
- Add explicit routing guidance for `doc-sectest*` vs `doc-tspec*`.

Acceptance:
- Discoverability complete and routing guidance non-conflicting.

### Phase E — Validation and Evidence

Actions:
- Run diagnostics on all six new SECTEST skills + README updates.
- Run scoped grep checks against `.claude/skills/doc-sectest*/SKILL.md` and `.claude/skills/README.md` only:
  - stale path markers (`ai_dev_flow`),
  - non-versioned review report naming,
  - `SECTEST-NN.R_review_report.md` (non-versioned) patterns,
  - missing `SECTEST-NN.A_audit_report_vNNN.md` examples in audit/fixer contracts,
  - missing audit-wrapper references,
  - non-canonical validator references,
   - missing isolated-environment safety constraints in authoring/review contracts,
   - missing explicit safety warning phrases (`isolated environments only`, `Never run security tests against production systems`),
   - presence of unsafe guidance markers (`against production`, `exploit execution`, `offensive payload execution`).
- Validate scoped git status in `/opt/data/ucx_framework` only.
- Generate evidence bundle: `tmp/IPLAN-021_validation_evidence_YYYY-MM-DD.md`.

Acceptance:
- No parser/diagnostic blockers in touched files.
- Drift regex checks pass for touched SECTEST skills.
- No unsafe-guidance markers in touched SECTEST skills; safety warning phrases present in authoring/review contracts.
- Change set is scoped to SECTEST skill-set introduction and README integration.

---

## 7. Deliverables

1. New SECTEST 6-skill pack under `.claude/skills/doc-sectest*/`.
2. New wrapper: `.claude/skills/doc-sectest-audit/SKILL.md`.
3. Updated `.claude/skills/README.md` with SECTEST registrations.
4. Validation evidence report.

---

## 8. Definition of Done

- All six `doc-sectest*` skills created with normalized metadata schema and version history.
- SECTEST contracts aligned to canonical SECTEST template/rules/schema/scripts.
- Audit-first remediation path documented: `autopilot -> audit -> fixer`.
- Fixer report precedence explicit (`latest timestamp`; tie => `.A_` over `.R_`).
- README includes SECTEST discoverability and routing guidance.
- Evidence bundle generated: `tmp/IPLAN-021_validation_evidence_YYYY-MM-DD.md`.
- Diagnostics and drift checks pass for all touched files.

---

## 9. Execution Notes

- This plan introduces a subtype-specialized SECTEST stack and does not deprecate TSPEC-generic skills.
- If MVP scope reduction is needed, execute Phase A + C first (core + wrapper), then Phase B (full QA specialization).
- Rollout fallback: if partial adoption causes ambiguity, keep `doc-tspec*` as primary and treat `doc-sectest*` as opt-in until routing guidance and validation evidence are confirmed.
