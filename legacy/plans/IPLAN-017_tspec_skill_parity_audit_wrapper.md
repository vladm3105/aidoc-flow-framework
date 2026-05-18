---
title: "IPLAN-017: TSPEC Skill Parity + Audit Wrapper"
tags:
  - implementation-plan
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-017
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-017: TSPEC Skill Parity + Audit Wrapper

## 1. Objective

Bring TSPEC skill stack to BRD-equivalent operational model by:
- normalizing TSPEC skill frontmatter/schema compliance,
- removing stale path/rule/script references,
- introducing a unified `doc-tspec-audit` wrapper skill,
- aligning reviewer/fixer/autopilot contracts to audit-first flow.

Target outcome: TSPEC skills become a 6-skill set (matching BRD/PRD/EARS/BDD/ADR/SYS/REQ/SPEC pattern) with consistent orchestration, diagnostics, and fixer handoff.

---

## 2. Scope

### In Scope
- `.claude/skills/doc-tspec/SKILL.md`
- `.claude/skills/doc-tspec-autopilot/SKILL.md`
- `.claude/skills/doc-tspec-validator/SKILL.md`
- `.claude/skills/doc-tspec-reviewer/SKILL.md`
- `.claude/skills/doc-tspec-fixer/SKILL.md`
- **New file**: `.claude/skills/doc-tspec-audit/SKILL.md`
- Skill index registration updates:
  - `.claude/skills/README.md`

### Out of Scope
- Runtime script behavior changes under `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/*`
- BRD/PRD/EARS/BDD/ADR/SYS/REQ/CTR/SPEC remediation
- TSPEC content rewrites in `docs/10_TSPEC/*`

---

## 3. Baseline Findings (From Scratch Audit)

Observed in current `ucx_framework` TSPEC skills:

1. Frontmatter schema drift: top-level `tags`/`custom_fields` remain in all five TSPEC skill files.
2. No unified TSPEC audit wrapper exists (`doc-tspec-audit` missing).
3. TSPEC fixer/autopilot/reviewer examples are `.R_review_report`-centric without `.A_audit_report` compatibility contract.
4. `doc-tspec-autopilot` still contains stale `ai_dev_flow/scripts/update_traceability_matrix.py` command examples.
5. `doc-tspec-autopilot` review standards still include non-versioned naming (`TSPEC-NN.R_review_report.md`).
6. `doc-tspec-validator` command examples reference non-existent legacy script `ai_dev_flow/scripts/validate_tspec.py`.
7. Canonical 10_TSPEC validator model is type-specific scripts, not monolithic validator script:
   - `validate_utest.py`, `validate_itest.py`, `validate_stest.py`, `validate_ftest.py`, `validate_ptest.py`, `validate_sectest.py`
   - `validate_all_tspec.sh`
   - `validate_tspec_quality_score.sh`
8. `doc-tspec` still references legacy root scripts for validation (`ai_dev_flow/scripts/validate_tags_against_docs.py`, `validate_cross_document.py`).
9. Skills index currently includes audit wrappers through SPEC, not TSPEC.
10. TSPEC layer path is canonical and valid at `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC`.
11. `doc-tspec-reviewer` and `doc-tspec-fixer` contain hardcoded structure-heading language that can drift from canonical TSPEC template contracts (e.g., fixed-count labels like `12/12`).
12. `doc-tspec-autopilot` command and standards sections include stale/non-canonical contract markers that must be normalized before audit-wrapper integration.

Current diagnostics posture:
- Issues are parity/contract/path consistency issues, not parser blockers.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **MVP Conformance Gate Missing by Default**
   - Must verify against canonical `10_TSPEC` templates/rules/scripts before edits.
2. **Cross-workspace Scope Risk**
   - Searches can return both workspace roots; all edits/staging must be scoped to `/opt/data/ucx_framework`.
3. **Audit/Fixer Compatibility Risk**
   - `doc-tspec-fixer` must accept both:
     - `TSPEC-NN.A_audit_report_vNNN.md` (preferred)
     - `TSPEC-NN.R_review_report_vNNN.md` (legacy)
4. **Version/Metadata Drift Risk**
   - Every touched TSPEC skill must update frontmatter metadata and `Version History`.
5. **Index Visibility Gap**
   - `.claude/skills/README.md` audit-wrapper listing must include TSPEC.
6. **Command Reference Drift**
   - TSPEC validation examples must align with existing type-specific scripts in `/ai_dev_ssd_flow/10_TSPEC/scripts/`.
7. **Embedded Example False-Positive Risk**
   - TSPEC skill files include internal examples with `tags:` and `custom_fields:`; only top frontmatter should be migrated.
8. **Precedence Tie-Break Gap**
   - Deterministic report selection required: latest timestamp first; if tied, prefer `.A_` over `.R_`.
9. **Review Standards Compatibility Gap**
   - Autopilot/reviewer/fixer report storage/versioning sections must include audit-first with `.R_` backward compatibility.
10. **Type-Specific Validator Mapping Gap**
   - Plan must map UTEST/ITEST/STEST/FTEST/PTEST/SECTEST examples to corresponding validators to avoid non-existent `validate_tspec.py` references.
11. **Dual TSPEC Contract Gap**
   - TSPEC has two valid structures (aggregator + subtype templates); plan must preserve both and avoid flattening to a single section-count contract.
12. **README Consistency Gap**
   - After adding `doc-tspec-audit`, verify audit-wrapper, core workflow, and autopilot sections remain internally consistent.

---

## 5. Design Approach (Mirror BRD Model)

### 5.1 Target Skill Topology
- `doc-tspec` (authoring)
- `doc-tspec-autopilot` (orchestration)
- `doc-tspec-validator` (structure/schema checks)
- `doc-tspec-reviewer` (semantic/content checks)
- `doc-tspec-fixer` (auto/manual remediation)
- `doc-tspec-audit` (**new unified validator+reviewer wrapper**)

### 5.2 `doc-tspec-audit` Contract (New)
Sequence:
1) run `doc-tspec-validator`
2) run `doc-tspec-reviewer`
3) normalize findings
4) emit `TSPEC-NN.A_audit_report_vNNN.md`
5) optional handoff to `doc-tspec-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 TSPEC Policy Alignment
- Preserve existing TSPEC quality/threshold policy from current validator/reviewer contracts.
- Do not introduce new blocking error-code families unless already defined in TSPEC validator/reviewer references.

---

## 6. Implementation Phases

### Phase A0 — MVP TSPEC Conformance Gate
Authoritative sources (canonical):
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/TSPEC-MVP-TEMPLATE.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/TSPEC-MVP-TEMPLATE.yaml`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/README.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/validate_utest.py`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/validate_itest.py`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/validate_stest.py`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/validate_ftest.py`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/validate_ptest.py`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/validate_sectest.py`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh`

Checklist:
1. Structure-model alignment (TSPEC section conventions by test type).
    - Enforce dual contract:
       - Aggregator contract from `TSPEC-MVP-TEMPLATE.md`
       - Subtype contracts from `UTEST/ITEST/STEST/FTEST/PTEST/SECTEST` templates
2. Readiness threshold alignment (type-specific TASKS/IMPL-ready scoring where applicable).
3. Nested-folder/path conventions alignment.
4. Rule/template/script filename alignment.
5. Resolve section-count and structure wording to remain consistent with the dual TSPEC contract (aggregator + subtype templates) across all touched TSPEC skills.

Acceptance:
- No contradictions between TSPEC skills and canonical `10_TSPEC` references.

### Phase A — Frontmatter Normalization
Files:
- `doc-tspec`, `doc-tspec-autopilot`, `doc-tspec-validator`, `doc-tspec-reviewer`, `doc-tspec-fixer`

Actions:
- Move root `tags`/`custom_fields` into `metadata`.
- Preserve semantic values; normalize only top frontmatter.
- Add `versioning_policy` aligned with TSPEC MVP template/schema references.

Acceptance:
- No frontmatter schema errors in touched TSPEC skill files.

### Phase B — Path/Rules/Command Reference Normalization
Files:
- `doc-tspec`, `doc-tspec-autopilot`, `doc-tspec-validator` (plus reviewer/fixer where needed)

Actions:
- Replace stale `ai_dev_flow/` references with `ai_dev_ssd_flow/`.
- Replace non-existent `validate_tspec.py` examples with type-specific validator examples.
- Normalize report naming examples to `_vNNN` format.
- Update traceability/update command examples to existing script locations.
- Normalize structure-count headings to template-consistent wording (avoid hardcoded `12/12` labels unless explicitly authoritative).
- Resolve section-count/coverage-language drift to canonical model from Phase A0.

Acceptance:
- No stale `ai_dev_flow` paths in touched TSPEC skill guidance.
- No references remain to non-existent TSPEC scripts.
- All touched files reference existing TSPEC scripts and assets.

### Phase C — Add `doc-tspec-audit`
File:
- Create `.claude/skills/doc-tspec-audit/SKILL.md`

Actions:
- Mirror `doc-brd-audit` structure and contract style.
- Bind to TSPEC validator/reviewer findings.
- Define output contract: `TSPEC-NN.A_audit_report_vNNN.md`.
- Include invocation examples for direct audit and fixer handoff.

Acceptance:
- New wrapper passes diagnostics and references only existing TSPEC skills.

### Phase D — Integrate Wrapper Contracts
Files:
- `doc-tspec-autopilot/SKILL.md`
- `doc-tspec-validator/SKILL.md`
- `doc-tspec-reviewer/SKILL.md`
- `doc-tspec-fixer/SKILL.md`
- `.claude/skills/README.md`

Actions:
- Add wrapper usage guidance (audit-first flow).
- Update fixer input contract to support `.A_` + `.R_` with deterministic precedence.
- Normalize reviewer/autopilot/validator examples to audit-wrapper-compatible report handling.
- Normalize Review Document Standards filename examples to versioned form (`*_vNNN`).
- Update versions/history metadata in all touched files.
- Register `doc-tspec-audit` in audit-wrapper index listing.
- Verify README consistency across audit-wrapper + autopilot + core workflow sections after insertion.

Acceptance:
- Coherent path: `autopilot -> audit -> fixer` documented.
- Precedence rule explicit: latest timestamp, then `.A_` over `.R_`.
- README audit-wrapper aggregate includes `doc-tspec-audit`.

### Phase E — Validation and Evidence
Actions:
- Run diagnostics on all six TSPEC skills.
- Run scoped grep checks for:
  - stale paths,
  - non-existent script references,
   - stale traceability-update command references,
  - report contract compatibility,
  - non-versioned `TSPEC-NN.R_review_report.md` examples,
  - audit-wrapper index coverage.
- Validate scoped git status for `/opt/data/ucx_framework` only.

Acceptance:
- No parser/diagnostic blockers in touched files.
- Drift regex checks pass for touched TSPEC skills.
- Explicit stale-marker checks pass:
   - no legacy `ai_dev_flow/scripts/update_traceability_matrix.py` references,
   - no non-versioned `TSPEC-NN.R_review_report.md` references,
   - no legacy `validate_tspec.py` references.
- Change set scoped to TSPEC skill parity + wrapper integration.

---

## 7. Deliverables

1. Updated TSPEC skill set with normalized metadata and canonical references.
2. New `.claude/skills/doc-tspec-audit/SKILL.md` wrapper.
3. Updated `.claude/skills/README.md` audit-wrapper listing.
4. Validation evidence bundle (diagnostics + grep drift checks).

---

## 8. Definition of Done

- All five existing TSPEC skills updated with:
  - normalized frontmatter metadata,
  - canonical `10_TSPEC` paths/rules/scripts,
  - audit-compatible reviewer/fixer contracts.
- `doc-tspec-audit` created and documented.
- README includes TSPEC audit wrapper.
- No stale path/contract references remain in touched TSPEC skill files.
- Scoped diagnostics pass for touched files.

---

## 9. Execution Notes

- **Repository scope**: `/opt/data/ucx_framework` only.
- **Do not modify** runtime validator/autopilot scripts unless separately requested.
- **Do not stage** unrelated files from `/opt/data/b-local/b-local-docs`.
- **Timezone standard** for report examples and plan metadata: `America/New_York`.

---

## 10. Suggested Commit Message (When Executing)

`feat(skills): implement IPLAN-017 TSPEC parity and audit wrapper`
