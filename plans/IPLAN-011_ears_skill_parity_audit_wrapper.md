---
title: "IPLAN-011: EARS Skill Parity + Audit Wrapper"
tags:
  - implementation-plan
  - layer-3-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-011
  status: draft
  created_date: 2026-02-26
  timezone: America/New_York
---

# IPLAN-011: EARS Skill Parity + Audit Wrapper

## 1. Objective

Bring EARS skill stack to BRD/PRD-equivalent operational model by:
- normalizing EARS skill frontmatter/schema compliance,
- removing stale path/rule references,
- introducing a unified `doc-ears-audit` wrapper skill,
- aligning reviewer/fixer/autopilot contracts to audit-first flow.

Target outcome: EARS skills become a 6-skill set (matching BRD/PRD pattern) with consistent orchestration, diagnostics, and fixer handoff.

---

## 2. Scope

### In Scope
- `.claude/skills/doc-ears/SKILL.md`
- `.claude/skills/doc-ears-autopilot/SKILL.md`
- `.claude/skills/doc-ears-validator/SKILL.md`
- `.claude/skills/doc-ears-reviewer/SKILL.md`
- `.claude/skills/doc-ears-fixer/SKILL.md`
- **New file**: `.claude/skills/doc-ears-audit/SKILL.md`
- Skill index registration updates:
  - `.claude/skills/README.md`

### Out of Scope
- Runtime validator behavior changes in `ai_dev_ssd_flow/03_EARS/scripts/*`
- BRD/PRD/SYS/REQ skill remediation
- EARS content document rewrites in `docs/03_EARS/*`

---

## 3. Baseline Findings (From Scratch Audit)

Observed in current `ucx_framework` EARS skills:

1. Frontmatter schema drift: top-level `tags`/`custom_fields` still present in all five EARS skill files (expected `metadata.tags` and `metadata.custom_fields`).
2. Stale path usage: multiple `ai_dev_flow/` references remain, especially in `doc-ears-autopilot`, `doc-ears-validator`, and parts of `doc-ears`.
3. Legacy standards path references remain in `doc-ears` (ID/threshold naming docs still under `ai_dev_flow`).
4. No unified EARS audit wrapper exists (`doc-ears-audit` missing).
5. EARS fixer/autopilot contracts are review-report centric (`EARS-NN.R_review_report_vNNN.md`) with no `.A_audit_report` compatibility contract.
6. Skills index does not expose EARS audit wrapper path because wrapper does not yet exist.

Current diagnostics status:
- `get_errors` reports no blocking parser errors in current EARS skills.
- Primary issues are parity/contract/path consistency, not syntax.

---

## 4. Plan-Level Gap Review (Fresh)

This section captures gaps that can invalidate implementation if omitted.

1. **MVP Conformance Gate Missing by Default**
   - Must explicitly verify alignment with `03_EARS` canonical files before edits.
2. **Cross-workspace Scope Risk**
   - Searches can hit both `b-local-docs` and `ucx_framework`; all edits/staging must be path-scoped to `ucx_framework`.
3. **Audit/Fixer Compatibility Risk**
   - `doc-ears-fixer` must explicitly support both report forms:
     - `EARS-NN.A_audit_report_vNNN.md` (preferred)
     - `EARS-NN.R_review_report_vNNN.md` (legacy)
4. **Version/Metadata Drift Risk**
   - Every touched EARS skill must update both frontmatter version metadata and `Version History`.
5. **Index Visibility Gap**
   - `README` needs explicit audit-wrapper mention; otherwise capability remains undiscoverable.
6. **Command Reference Drift**
   - Script examples in autopilot/validator must point to current `ai_dev_ssd_flow` paths.
7. **Embedded Example False-Positive Risk**
  - EARS skill files contain internal markdown examples with `tags:` / `custom_fields:` blocks.
  - Frontmatter migration must be limited to top-of-file YAML only; do not rewrite embedded examples.
8. **Review Document Standards Compatibility Gap**
  - Autopilot/reviewer/fixer sections referencing review report storage/versioning must be updated to include audit-report precedence while preserving legacy review-report compatibility.
9. **Validator Example Contract Drift**
  - `doc-ears-validator` includes sample output trees and references to review reports that may remain `.R_`-only.
  - Plan must normalize validator examples to reflect audit-wrapper era compatibility (preferred `.A_`, legacy `.R_`).
10. **Precedence Tie-Break Gap**
  - "Deterministic precedence" must be explicit for equal-version/equal-day cases.
  - Rule required: latest timestamp first; if equivalent, prefer `.A_audit_report` over `.R_review_report`.

These controls are integrated into phases A0, B, D, and E below.

---

## 5. Design Approach (Mirror BRD/PRD Model)

### 5.1 Target Skill Topology
- `doc-ears` (authoring)
- `doc-ears-autopilot` (orchestration)
- `doc-ears-validator` (structure/schema checks)
- `doc-ears-reviewer` (semantic/content checks)
- `doc-ears-fixer` (auto/manual remediation)
- `doc-ears-audit` (**new unified validator+reviewer wrapper**)

### 5.2 `doc-ears-audit` Contract (New)
Sequence:
1) run `doc-ears-validator`
2) run `doc-ears-reviewer`
3) normalize findings
4) emit `EARS-NN.A_audit_report_vNNN.md`
5) optional handoff to `doc-ears-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 EARS Policy Alignment
- Preserve existing EARS quality/threshold policy from current validator/reviewer contracts.
- Do not invent new blocking code families without validator contract evidence.

---

## 6. Implementation Phases

### Phase A0 — MVP EARS Conformance Gate
Authoritative sources:
- `ai_dev_ssd_flow/03_EARS/EARS-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/03_EARS/EARS_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/03_EARS/EARS_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/03_EARS/EARS_MVP_SCHEMA.yaml`

Checklist:
1. Section model and required headings alignment.
2. Readiness threshold language alignment (`>=90%` where applicable).
3. Nested-folder/path conventions alignment.
4. Rule/schema/template filename alignment.

Acceptance:
- No contradiction between EARS skills and canonical EARS MVP references.

### Phase A — Frontmatter Normalization
Files:
- `doc-ears`, `doc-ears-autopilot`, `doc-ears-validator`, `doc-ears-reviewer`, `doc-ears-fixer`

Actions:
- Move root `tags`/`custom_fields` into `metadata`.
- Preserve semantic values; only normalize structure.

Acceptance:
- No frontmatter schema errors in EARS skill files.

### Phase B — Path/Rules/Command Reference Normalization
Files:
- `doc-ears`, `doc-ears-autopilot`, `doc-ears-validator` (plus reviewer/fixer where needed)

Actions:
- Replace `ai_dev_flow/` with `ai_dev_ssd_flow/` where references are active guidance.
- Ensure all EARS rule references use MVP filenames.
- Normalize script command paths in examples.

Acceptance:
- No stale active `ai_dev_flow/` paths in EARS skill guidance.

### Phase C — Add `doc-ears-audit`
File:
- Create `.claude/skills/doc-ears-audit/SKILL.md`

Actions:
- Mirror proven `doc-brd-audit`/`doc-prd-audit` wrapper design.
- Bind to EARS validator/reviewer findings.
- Define output contract: `EARS-NN.A_audit_report_vNNN.md`.
- Include invocation examples for direct audit and fixer handoff.

Acceptance:
- New wrapper passes diagnostics and references only existing EARS skills.

### Phase D — Integrate Wrapper Contracts
Files:
- `doc-ears-autopilot/SKILL.md`
- `doc-ears-validator/SKILL.md`
- `doc-ears-fixer/SKILL.md`
- `doc-ears-reviewer/SKILL.md`
- `.claude/skills/README.md`

Actions:
- Add wrapper usage guidance (audit-first flow).
- Update fixer input contract to support `.A_` + `.R_` reports with deterministic precedence.
- Normalize validator output examples to show `.A_audit_report` preferred with `.R_review_report` as legacy-compatible.
- Update versions/history metadata in all touched files.
- Register `doc-ears-audit` in index, including audit-wrapper aggregate listing currently showing BRD/PRD wrappers.

Acceptance:
- Coherent path: `autopilot -> audit -> fixer` documented.
- Validator/reviewer/fixer examples are report-format compatible with audit-wrapper flow.
- Fixer explicitly supports both report formats.
- Precedence rule is explicit: latest timestamp, then `.A_` over `.R_` on ties.

### Phase E — Validation and Evidence
Actions:
- Run diagnostics on all six EARS skills.
- Run scoped grep checks for:
  - stale paths,
  - legacy rule names,
  - `.A_` / `.R_` compatibility,
  - audit wrapper indexing.
- Enforce scoped git add and file list verification before commit.

Acceptance:
- No schema errors in touched EARS skills.
- No stale active references.
- Wrapper created, integrated, and discoverable.

---

## 7. Verification Commands

```bash
# Stale path scan
rg -n "ai_dev_flow/" .claude/skills/doc-ears*/SKILL.md

# Legacy EARS rule-name scan
rg -n "EARS_CREATION_RULES.md|EARS_VALIDATION_RULES.md" .claude/skills/doc-ears*/SKILL.md

# Wrapper/report compatibility scan
rg -n "A_audit_report|R_review_report|--review-report" \
  .claude/skills/doc-ears-fixer/SKILL.md \
  .claude/skills/doc-ears-autopilot/SKILL.md \
  .claude/skills/doc-ears-validator/SKILL.md \
  .claude/skills/doc-ears-audit/SKILL.md

# Index registration
rg -n "doc-ears-audit" .claude/skills/README.md

# Review-document standards compatibility scan
rg -n "Review Document Standards|R_review_report|A_audit_report" .claude/skills/doc-ears*/SKILL.md

# Commit scope guard
git diff --name-only
```

---

## 8. Execution Notes

- Workspace has two roots; all operations must target `/opt/data/ucx_framework`.
- Use explicit file-path staging for commit.
- Keep changes surgical; do not alter runtime scripts in this plan.
