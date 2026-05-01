---
title: "IPLAN-016: SPEC Skill Parity + Audit Wrapper"
tags:
  - implementation-plan
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-016
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-016: SPEC Skill Parity + Audit Wrapper

## 1. Objective

Bring the SPEC skill stack to BRD-equivalent operational model by:
- normalizing SPEC skill frontmatter/schema compliance,
- removing stale path/rule/script references,
- introducing a unified `doc-spec-audit` wrapper skill,
- aligning reviewer/fixer/autopilot contracts to audit-first flow.

Target outcome: SPEC skills become a 6-skill set (matching BRD/PRD/EARS/BDD/ADR/SYS/REQ pattern) with consistent orchestration, diagnostics, and fixer handoff.

---

## 2. Scope

### In Scope
- `.claude/skills/doc-spec/SKILL.md`
- `.claude/skills/doc-spec-autopilot/SKILL.md`
- `.claude/skills/doc-spec-validator/SKILL.md`
- `.claude/skills/doc-spec-reviewer/SKILL.md`
- `.claude/skills/doc-spec-fixer/SKILL.md`
- **New file**: `.claude/skills/doc-spec-audit/SKILL.md`
- Skill index registration updates:
  - `.claude/skills/README.md`

### Out of Scope
- Runtime script behavior changes under `/opt/data/ucx_framework/ai_dev_ssd_flow/09_SPEC/scripts/*`
- BRD/PRD/EARS/BDD/ADR/SYS/REQ/CTR remediation
- SPEC content rewrites in `docs/09_SPEC/*`

---

## 3. Baseline Findings (From Scratch Audit)

Observed in current `ucx_framework` SPEC skills:

1. Frontmatter schema drift: top-level `tags`/`custom_fields` remain in all five SPEC skill files.
2. Stale path usage in `doc-spec`: active `ai_dev_flow/09_SPEC/*` and `ai_dev_flow/scripts/*` references remain.
3. No unified SPEC audit wrapper exists (`doc-spec-audit` missing).
4. SPEC fixer/autopilot/reviewer examples are `.R_review_report`-centric without `.A_audit_report` compatibility contract.
5. `doc-spec` references legacy rule/schema names (`SPEC_CREATION_RULES.md`, `SPEC_VALIDATION_RULES.md`, `SPEC_SCHEMA.yaml`) instead of current `SPEC_MVP_*` canon.
6. `doc-spec` still points to `docs/SPEC/*` in multiple examples instead of `docs/09_SPEC/*`.
7. `doc-spec` states validation script is under development while canonical SPEC validators already exist in `ai_dev_ssd_flow/09_SPEC/scripts/`.
8. `doc-spec-reviewer` contains structure language drift (`12/12` heading vs documented 13-section check model).
9. `doc-spec-fixer` upstream review contract is `.R_` only; no preferred `.A_` contract.
10. Skills index currently includes audit wrappers through REQ, not SPEC.
11. User request referenced `/ai_dev_ssd_flow/08_SPEC`; canonical SPEC layer in this repository is `/ai_dev_ssd_flow/09_SPEC`.
12. `doc-spec-autopilot` has significant legacy drift and is NOT source-compatible without remediation:
   - legacy `ai_dev_flow/scripts/*` command examples,
   - `docs/SPEC/*` path examples,
   - non-versioned review report naming examples.
13. Skills index layer label drift exists: `doc-spec` is listed as Layer 10 in README, but SPEC is Layer 9.

Current diagnostics posture:
- Issues are parity/contract/path consistency issues, not parser blockers.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **Layer Path Alignment Gap**
   - Plan execution must use canonical SPEC location `ai_dev_ssd_flow/09_SPEC` (not `08_SPEC`).
2. **MVP Conformance Gate Missing by Default**
   - Must verify against canonical template/rules/schema/scripts before edits.
3. **Cross-workspace Scope Risk**
   - Searches can return both workspace roots; all edits/staging must be scoped to `/opt/data/ucx_framework`.
4. **Audit/Fixer Compatibility Risk**
   - `doc-spec-fixer` must accept both:
     - `SPEC-NN.A_audit_report_vNNN.md` (preferred)
     - `SPEC-NN.R_review_report_vNNN.md` (legacy)
5. **Version/Metadata Drift Risk**
   - Every touched SPEC skill must update frontmatter metadata and `Version History`.
6. **Index Visibility Gap**
   - `.claude/skills/README.md` audit-wrapper listing must include SPEC.
7. **Command Reference Drift**
   - Validation examples must align to existing scripts:
     - `validate_spec.py`
     - `validate_spec_implementation_readiness.py`
     - `validate_spec_quality_score.sh`
8. **Embedded Example False-Positive Risk**
   - SPEC skill files include internal markdown/yaml examples containing `tags:` and `custom_fields:`; only top frontmatter should be migrated.
9. **Precedence Tie-Break Gap**
   - Deterministic report selection required: latest timestamp first; if tied, prefer `.A_` over `.R_`.
10. **Section-Contract Drift Gap**
   - Ensure `doc-spec`, `autopilot`, `validator`, `reviewer`, and `fixer` reference one canonical section model based on `SPEC-MVP-TEMPLATE` and schema/rules.
11. **Legacy Path Hygiene Gap**
   - Replace `docs/SPEC/` with `docs/09_SPEC/` across all touched examples.
12. **Review Document Standards Compatibility Gap**
   - Autopilot/reviewer/fixer report storage/versioning sections must include audit-first with `.R_` backward compatibility.
13. **README Layer Label Gap**
   - `.claude/skills/README.md` must align `doc-spec` to Layer 9 (currently shown as Layer 10).
14. **Autopilot Script-Reference Gap**
   - Remove/replace legacy `spec_autopilot.py` examples with valid skill-invocation patterns and existing script references only.

---

## 5. Design Approach (Mirror BRD Model)

### 5.1 Target Skill Topology
- `doc-spec` (authoring)
- `doc-spec-autopilot` (orchestration)
- `doc-spec-validator` (structure/schema checks)
- `doc-spec-reviewer` (semantic/content checks)
- `doc-spec-fixer` (auto/manual remediation)
- `doc-spec-audit` (**new unified validator+reviewer wrapper**)

### 5.2 `doc-spec-audit` Contract (New)
Sequence:
1) run `doc-spec-validator`
2) run `doc-spec-reviewer`
3) normalize findings
4) emit `SPEC-NN.A_audit_report_vNNN.md`
5) optional handoff to `doc-spec-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 SPEC Policy Alignment
- Preserve existing SPEC quality/threshold policy from current validator/reviewer contracts.
- Do not introduce new blocking error-code families unless already defined in SPEC validator/reviewer references.

---

## 6. Implementation Phases

### Phase A0 — MVP SPEC Conformance Gate
Authoritative sources (canonical):
- `/opt/data/ucx_framework/ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.yaml`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/09_SPEC/SPEC_MVP_VALIDATION_RULES.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/09_SPEC/SPEC_MVP_SCHEMA.yaml`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/09_SPEC/scripts/validate_spec.py`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/09_SPEC/scripts/validate_spec_implementation_readiness.py`

Checklist:
1. Structure-model alignment (SPEC MVP section conventions).
   - Canonical contract: SPEC MVP has **8 required sections** plus optional appendices as defined in `SPEC-MVP-TEMPLATE.md`.
2. Readiness threshold alignment (TASKS-ready >=90% where applicable).
3. Nested-folder/path conventions alignment.
4. Rule/schema/template filename alignment.
5. Resolve section-count wording to one canonical model used consistently across all touched skills.

Acceptance:
- No contradictions between SPEC skills and canonical `09_SPEC` references.

### Phase A — Frontmatter Normalization
Files:
- `doc-spec`, `doc-spec-autopilot`, `doc-spec-validator`, `doc-spec-reviewer`, `doc-spec-fixer`

Actions:
- Move root `tags`/`custom_fields` into `metadata`.
- Preserve semantic values; normalize only top frontmatter.
- Add `versioning_policy` aligned with SPEC MVP template/schema references.

Acceptance:
- No frontmatter schema errors in touched SPEC skill files.

### Phase B — Path/Rules/Command Reference Normalization
Files:
- `doc-spec`, `doc-spec-autopilot`, `doc-spec-validator` (plus reviewer/fixer where needed)

Actions:
- Replace stale `ai_dev_flow/` references with `ai_dev_ssd_flow/`.
- Standardize rule/schema references to `SPEC_MVP_*`.
- Replace `docs/SPEC/*` with `docs/09_SPEC/*`.
- Update validator command examples to existing `09_SPEC/scripts/*` commands.
- Remove wording that claims SPEC validation tooling is unavailable when scripts are present.
- Remove/replace legacy `spec_autopilot.py` command examples with valid `/doc-spec-autopilot ...` usage.
- Normalize report naming examples to `_vNNN` format.
- Resolve section-count language drift to canonical model from Phase A0.

Acceptance:
- No stale `ai_dev_flow` paths in touched SPEC skill guidance.
- No stale `docs/SPEC` paths in touched SPEC skill guidance.
- All touched files reference existing SPEC scripts and assets.

### Phase C — Add `doc-spec-audit`
File:
- Create `.claude/skills/doc-spec-audit/SKILL.md`

Actions:
- Mirror `doc-brd-audit` structure and contract style.
- Bind to SPEC validator/reviewer findings.
- Define output contract: `SPEC-NN.A_audit_report_vNNN.md`.
- Include invocation examples for direct audit and fixer handoff.

Acceptance:
- New wrapper passes diagnostics and references only existing SPEC skills.

### Phase D — Integrate Wrapper Contracts
Files:
- `doc-spec-autopilot/SKILL.md`
- `doc-spec-validator/SKILL.md`
- `doc-spec-reviewer/SKILL.md`
- `doc-spec-fixer/SKILL.md`
- `.claude/skills/README.md`

Actions:
- Add wrapper usage guidance (audit-first flow).
- Update fixer input contract to support `.A_` + `.R_` with deterministic precedence.
- Normalize reviewer/autopilot/validator examples to audit-wrapper-compatible report handling.
- Normalize Review Document Standards filename examples to versioned form (`*_vNNN`).
- Correct skills index layer label for `doc-spec` to Layer 9.
- Update versions/history metadata in all touched files.
- Register `doc-spec-audit` in audit-wrapper index listing.

Acceptance:
- Coherent path: `autopilot -> audit -> fixer` documented.
- Precedence rule explicit: latest timestamp, then `.A_` over `.R_`.
- README audit-wrapper aggregate includes `doc-spec-audit`.

### Phase E — Validation and Evidence
Actions:
- Run diagnostics on all six SPEC skills.
- Run scoped grep checks for:
  - stale paths,
  - legacy rule/schema names,
  - report contract compatibility,
   - legacy `spec_autopilot.py` command references,
   - legacy `docs/SPEC/` path references,
   - non-versioned `SPEC-NN.R_review_report.md` examples,
  - audit-wrapper index coverage.
- Validate scoped git status for `/opt/data/ucx_framework` only.

Acceptance:
- No parser/diagnostic blockers in touched files.
- Drift regex checks pass for touched SPEC skills.
- Change set scoped to SPEC skill parity + wrapper integration.

---

## 7. Deliverables

1. Updated SPEC skill set with normalized metadata and canonical references.
2. New `.claude/skills/doc-spec-audit/SKILL.md` wrapper.
3. Updated `.claude/skills/README.md` audit-wrapper listing.
4. Validation evidence bundle (diagnostics + grep drift checks).

---

## 8. Definition of Done

- All five existing SPEC skills updated with:
  - normalized frontmatter metadata,
  - canonical `09_SPEC` paths/rules/scripts,
  - audit-compatible reviewer/fixer contracts.
- `doc-spec-audit` created and documented.
- README includes SPEC audit wrapper.
- No stale path/contract references remain in touched SPEC skill files.
- Scoped diagnostics pass for touched files.

---

## 9. Execution Notes

- **Repository scope**: `/opt/data/ucx_framework` only.
- **Do not modify** runtime validator/autopilot scripts unless separately requested.
- **Do not stage** unrelated files from `/opt/data/b-local/b-local-docs`.
- **Timezone standard** for report examples and plan metadata: `America/New_York`.

---

## 10. Suggested Commit Message (When Executing)

`feat(skills): implement IPLAN-016 SPEC parity and audit wrapper`
