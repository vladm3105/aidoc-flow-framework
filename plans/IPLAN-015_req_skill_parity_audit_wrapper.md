---
title: "IPLAN-015: REQ Skill Parity + Audit Wrapper"
tags:
  - implementation-plan
  - layer-7-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-015
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-015: REQ Skill Parity + Audit Wrapper

## 1. Objective

Bring REQ skill stack to BRD-equivalent operational model by:
- normalizing REQ skill frontmatter/schema compliance,
- removing stale path/rule/script references,
- introducing a unified `doc-req-audit` wrapper skill,
- aligning reviewer/fixer/autopilot contracts to audit-first flow.

Target outcome: REQ skills become a 6-skill set (matching BRD/PRD/EARS/BDD/ADR/SYS pattern) with consistent orchestration, diagnostics, and fixer handoff.

---

## 2. Scope

### In Scope
- `.claude/skills/doc-req/SKILL.md`
- `.claude/skills/doc-req-autopilot/SKILL.md`
- `.claude/skills/doc-req-validator/SKILL.md`
- `.claude/skills/doc-req-reviewer/SKILL.md`
- `.claude/skills/doc-req-fixer/SKILL.md`
- **New file**: `.claude/skills/doc-req-audit/SKILL.md`
- Skill index registration updates:
  - `.claude/skills/README.md`

### Out of Scope
- Runtime script behavior changes under `/opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/scripts/*`
- BRD/PRD/EARS/BDD/ADR/SYS remediation
- REQ content document rewrites in `docs/07_REQ/*`

---

## 3. Baseline Findings (From Scratch Audit)

Observed in current `ucx_framework` REQ skills:

1. Frontmatter schema drift: top-level `tags`/`custom_fields` remain in all five REQ skill files.
2. Stale path usage: active `ai_dev_flow/` references remain across REQ skills.
3. No unified REQ audit wrapper exists (`doc-req-audit` missing).
4. REQ fixer/autopilot/reviewer/validator examples are `.R_review_report`-centric without `.A_audit_report` compatibility contract.
5. `doc-req-validator` references legacy schema/script names (`ai_dev_flow/REQ/REQ_SCHEMA.yaml`, `validate_req.py`) that do not match current `07_REQ` assets.
6. `doc-req` references legacy rule names (`REQ_CREATION_RULES.md`, `REQ_VALIDATION_RULES.md`) instead of `REQ_MVP_*` canon.
7. `doc-req` references `./ai_dev_flow/scripts/validate_req_template.sh`; canonical script exists at `ai_dev_ssd_flow/07_REQ/scripts/validate_req_template.sh`.
8. `doc-req-reviewer` and `doc-req-fixer` include stale location examples (`docs/REQ/...` instead of `docs/07_REQ/...`).
9. `doc-req-fixer` upstream report contract is malformed (`REQ-NN.R_fix_report_vNNN.md` typo in upstream examples).
10. Skills index currently lists audit wrappers through SYS, not REQ.
11. Repository check confirms only one canonical REQ validation script path for template validation:
   - `ai_dev_ssd_flow/07_REQ/scripts/validate_req_template.sh`
12. Repository check found no direct REQ/SPEC autopilot scripts:
   - no `req_autopilot.py`
   - no `spec_autopilot.py`
13. Canonical section contract confirmed from `REQ-MVP-TEMPLATE.md`:
   - REQ MVP requires **11 sections**.
   - Change History section is intentionally omitted for MVP.
14. Current REQ skills still contain mixed 11/12-section language, which can propagate inconsistent quality-gate behavior.

Current diagnostics status:
- Issues are parity/contract/path consistency issues, not parser blockers.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **MVP Conformance Gate Missing by Default**
   - Must verify alignment with `/opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ` canonical template/rules/schema before edits.
2. **Cross-workspace Scope Risk**
   - Searches can return both workspace roots; all edits/staging must be scoped to `/opt/data/ucx_framework`.
3. **Audit/Fixer Compatibility Risk**
   - `doc-req-fixer` must accept both report forms:
     - `REQ-NN.A_audit_report_vNNN.md` (preferred)
     - `REQ-NN.R_review_report_vNNN.md` (legacy)
4. **Version/Metadata Drift Risk**
   - Every touched REQ skill must update frontmatter metadata and `Version History`.
5. **Index Visibility Gap**
   - `.claude/skills/README.md` audit-wrapper listing must include REQ.
6. **Command Reference Drift**
   - Validation examples must point to existing scripts in `/opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/scripts/`.
7. **Embedded Example False-Positive Risk**
   - REQ skill files include internal markdown examples containing `tags:` / `custom_fields:`; only top frontmatter should be migrated.
8. **Precedence Tie-Break Gap**
   - Deterministic report selection must be explicit: latest timestamp first; if tied, prefer `.A_` over `.R_`.
9. **Review Document Standards Compatibility Gap**
   - Autopilot/reviewer/fixer report storage/versioning sections must include audit-first with legacy reviewer compatibility.
10. **Script Existence Gap**
   - No direct `req_autopilot.py` / `spec_autopilot.py` scripts exist; examples must use skill invocation and existing script paths only.
11. **Path Hygiene Gap**
   - All report-location examples and command examples must use `docs/07_REQ/...` (not `docs/REQ/...`).
12. **Legacy Rule/Schema Name Drift Gap**
   - Replace legacy `REQ_SCHEMA.yaml`, `REQ_CREATION_RULES.md`, `REQ_VALIDATION_RULES.md` references with current `REQ_MVP_*` assets.
13. **Atomic-ID Contract Gap**
   - REQ layer uses both module and atomic identifiers; audit/fixer contracts must explicitly support:
     - module-level: `REQ-NN.*`
     - atomic-level: `REQ-NN-SSS.*`
14. **Review Filename Versioning Gap**
   - Existing examples include non-versioned names (`REQ-NN.R_review_report.md`, `REQ-NN-SSS.R_review_report.md`); all standards/examples must use `_vNNN`.
15. **Dual-Template Synchronization Gap**
   - Canonical REQ template exists in both `.md` and `.yaml`; guidance must avoid contradictory references and preserve dual-format consistency where referenced.
16. **Legacy Framework-Doc Path Gap**
   - Autopilot contains legacy references to `ai_dev_flow` framework guide paths; these must be normalized or replaced with valid current references.
17. **Section-Count Contract Drift Gap**
   - REQ skills currently conflict on required section count (11-section MVP vs 12-section REQ v3.0 language).
   - Plan must resolve to one canonical contract based on `ai_dev_ssd_flow/07_REQ/REQ-MVP-TEMPLATE.md` and apply consistently across authoring/autopilot/validator/reviewer/fixer.
   - Canonical target: **11-section MVP**, with no Change History section requirement.
18. **Section-Template Existence Gap**
   - REQ skills reference `REQ-SECTION-0-TEMPLATE.md` / `REQ-SECTION-TEMPLATE.md`, but these files are absent in `ai_dev_ssd_flow/07_REQ/`.
   - References must be removed/replaced with valid REQ MVP guidance.

---

## 5. Design Approach (Mirror BRD Model)

### 5.1 Target Skill Topology
- `doc-req` (authoring)
- `doc-req-autopilot` (orchestration)
- `doc-req-validator` (structure/schema checks)
- `doc-req-reviewer` (semantic/content checks)
- `doc-req-fixer` (auto/manual remediation)
- `doc-req-audit` (**new unified validator+reviewer wrapper**)

### 5.2 `doc-req-audit` Contract (New)
Sequence:
1) run `doc-req-validator`
2) run `doc-req-reviewer`
3) normalize findings
4) emit audit report using REQ-compatible ID forms:
   - `REQ-NN.A_audit_report_vNNN.md` (module-level)
   - `REQ-NN-SSS.A_audit_report_vNNN.md` (atomic-level)
5) optional handoff to `doc-req-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 REQ Policy Alignment
- Preserve existing REQ quality/threshold policy from current validator/reviewer contracts.
- Do not invent new blocking code families unless current REQ validator/reviewer already define them.

---

## 6. Implementation Phases

### Phase A0 — MVP REQ Conformance Gate
Authoritative sources (canonical):
- `/opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ-MVP-TEMPLATE.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ_MVP_CREATION_RULES.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ_MVP_VALIDATION_RULES.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ_MVP_SCHEMA.yaml`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/scripts/validate_req_template.sh`

Checklist:
1. Structure-model alignment (REQ MVP section conventions).
2. Resolve and lock canonical section-count contract (11 vs 12) from template authority.
3. Enforce canonical MVP outcome: 11 sections, Change History omitted.
2. Readiness threshold alignment (>=90% where applicable).
3. Nested-folder/path conventions alignment.
4. Rule/schema/template filename alignment.

Acceptance:
- No contradictions between REQ skills and canonical REQ MVP references.

### Phase A — Frontmatter Normalization
Files:
- `doc-req`, `doc-req-autopilot`, `doc-req-validator`, `doc-req-reviewer`, `doc-req-fixer`

Actions:
- Move root `tags`/`custom_fields` into `metadata`.
- Preserve semantic values; normalize only top frontmatter.

Acceptance:
- No frontmatter schema errors in REQ skill files.

### Phase B — Path/Rules/Command Reference Normalization
Files:
- `doc-req`, `doc-req-autopilot`, `doc-req-validator` (plus reviewer/fixer where needed)

Actions:
- Replace active `ai_dev_flow/` references with `ai_dev_ssd_flow/`.
- Ensure REQ rule/schema references use MVP filenames (`REQ_MVP_*`).
- Normalize validation examples to existing 07_REQ scripts (`validate_req_template.sh`, `validate_req_spec_readiness.py`, `validate_req_quality_score.sh`) where applicable.
- Remove/replace non-existent references (`REQ_SCHEMA.yaml`, `validate_req.py`, direct `req_autopilot.py` / `spec_autopilot.py` examples).
- Correct report location examples from `docs/REQ/...` to `docs/07_REQ/...`.
- Correct fixer upstream report-contract typos (`R_fix_report` -> audit/review report).
- Remove/replace references to non-existent section-template files (`REQ-SECTION-0-TEMPLATE.md`, `REQ-SECTION-TEMPLATE.md`).
- Normalize section-count language to a single canonical requirement derived from REQ MVP template.
- Remove/replace any REQ guidance that mandates Change History as a required MVP section.

Acceptance:
- No stale active `ai_dev_flow/` paths in REQ skill guidance.
- No references remain to non-existent REQ artifacts/scripts (`validate_req.py`, `req_autopilot.py`, `spec_autopilot.py`).
- No references remain to absent REQ section-template files.
- Section-count contract is internally consistent across all touched REQ skills.
- All touched REQ skills consistently enforce 11-section MVP language.

### Phase C — Add `doc-req-audit`
File:
- Create `.claude/skills/doc-req-audit/SKILL.md`

Actions:
- Mirror `doc-brd-audit` structure and contract style.
- Bind to REQ validator/reviewer findings.
- Define output contract for both REQ ID forms:
   - `REQ-NN.A_audit_report_vNNN.md`
   - `REQ-NN-SSS.A_audit_report_vNNN.md`
- Include invocation examples for direct audit and fixer handoff.

Acceptance:
- New wrapper passes diagnostics and references only existing REQ skills.

### Phase D — Integrate Wrapper Contracts
Files:
- `doc-req-autopilot/SKILL.md`
- `doc-req-validator/SKILL.md`
- `doc-req-reviewer/SKILL.md`
- `doc-req-fixer/SKILL.md`
- `.claude/skills/README.md`

Actions:
- Add wrapper usage guidance (audit-first flow).
- Update fixer input contract to support `.A_` + `.R_` with deterministic precedence.
- Normalize reviewer/autopilot/validator examples to audit-wrapper-compatible report handling.
- Normalize Review Document Standards filename examples to versioned form (`*_vNNN`).
- Normalize examples to support module-level and atomic-level REQ ID forms.
- Align template/schema references with canonical dual-template set (`REQ-MVP-TEMPLATE.md` + `REQ-MVP-TEMPLATE.yaml`, `REQ_MVP_SCHEMA.yaml`).
- Update versions/history metadata in all touched files.
- Register `doc-req-audit` in audit-wrapper index listing.

Acceptance:
- Coherent path: `autopilot -> audit -> fixer` documented.
- Validator/reviewer/fixer examples compatible with audit-wrapper flow.
- Precedence rule explicit: latest timestamp, then `.A_` over `.R_`.
- Audit/review contracts cover both REQ ID forms (`REQ-NN` and `REQ-NN-SSS`).
- README audit-wrapper aggregate includes `doc-req-audit`.

### Phase E — Validation and Evidence
Actions:
- Run diagnostics on all six REQ skills.
- Run scoped grep checks for:
  - stale paths,
  - legacy rule/schema names,
  - non-existent script names,
  - `.A_` / `.R_` compatibility,
  - audit-wrapper indexing.
- Enforce scoped git add and file-list verification before commit.

Acceptance:
- No schema errors in touched REQ skills.
- No stale active references.
- Wrapper created, integrated, discoverable.

---

## 7. Verification Commands

```bash
# Stale path scan
rg -n "ai_dev_flow/" .claude/skills/doc-req*/SKILL.md

# Legacy REQ rule/schema-name scan
rg -n "REQ_CREATION_RULES.md|REQ_VALIDATION_RULES.md|REQ_SCHEMA.yaml|validate_req.py" .claude/skills/doc-req*/SKILL.md

# Section-template and section-count drift scan
rg -n "REQ-SECTION-0-TEMPLATE|REQ-SECTION-TEMPLATE|11 sections|12 sections" .claude/skills/doc-req*/SKILL.md

# Change History requirement drift scan (MVP should not require it as a numbered section)
rg -n "Change History.*required|Required.*Change History|all 12 sections" .claude/skills/doc-req*/SKILL.md

# Non-existent direct script reference scan
rg -n "req_autopilot.py|spec_autopilot.py" .claude/skills/doc-req*/SKILL.md

# Wrapper/report compatibility scan
rg -n "A_audit_report|R_review_report|--review-report" \
  .claude/skills/doc-req-fixer/SKILL.md \
  .claude/skills/doc-req-autopilot/SKILL.md \
  .claude/skills/doc-req-validator/SKILL.md \
  .claude/skills/doc-req-audit/SKILL.md

# Fixer upstream contract typo scan
rg -n "R_fix_report|Upstream\*\*:.*fix_report" .claude/skills/doc-req-fixer/SKILL.md

# Atomic/module ID contract scan
rg -n "REQ-NN-SSS|REQ-NN\.R_review_report|REQ-NN-SSS\.R_review_report|REQ-NN\.A_audit_report|REQ-NN-SSS\.A_audit_report" .claude/skills/doc-req*/SKILL.md

# Location hygiene scan
rg -n "docs/REQ/" .claude/skills/doc-req*/SKILL.md

# Review filename versioning scan
rg -n "R_review_report\.md|A_audit_report\.md" .claude/skills/doc-req*/SKILL.md

# Index registration
rg -n "doc-req-audit" .claude/skills/README.md

# Canonical REQ artifact existence sanity check
ls /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ-MVP-TEMPLATE.md \
   /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ-MVP-TEMPLATE.yaml \
   /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ_MVP_SCHEMA.yaml \
   /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/scripts/validate_req_template.sh

# Additional REQ script presence (informational)
ls /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/scripts/validate_req_quality_score.sh \
   /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/scripts/validate_req_spec_readiness.py

# Canonical section-contract evidence (must indicate 11-section MVP)
rg -n "11 sections required|Change History section is intentionally omitted|11 sections - this is the standard REQ MVP template structure" \
   /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ-MVP-TEMPLATE.md

# Section-template existence check (informational; expected absent in current baseline)
for f in \
   /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ-SECTION-0-TEMPLATE.md \
   /opt/data/ucx_framework/ai_dev_ssd_flow/07_REQ/REQ-SECTION-TEMPLATE.md; do
   [[ -e "$f" ]] && echo "present: $f" || echo "absent: $f"
done

# Commit scope guard
git diff --name-only
```

---

## 8. Execution Notes

- Workspace has two roots; scope all operations to `/opt/data/ucx_framework`.
- Use explicit file-path staging for commit.
- Keep edits surgical; do not modify runtime scripts in this plan.
