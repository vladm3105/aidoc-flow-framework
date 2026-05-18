---
title: "IPLAN-014: SYS Skill Parity + Audit Wrapper"
tags:
  - implementation-plan
  - layer-6-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-014
  status: draft
  created_date: 2026-02-27
  timezone: America/New_York
---

# IPLAN-014: SYS Skill Parity + Audit Wrapper

## 1. Objective

Bring SYS skill stack to BRD-equivalent operational model by:
- normalizing SYS skill frontmatter/schema compliance,
- removing stale path/rule/script references,
- introducing a unified `doc-sys-audit` wrapper skill,
- aligning reviewer/fixer/autopilot contracts to audit-first flow.

Target outcome: SYS skills become a 6-skill set (matching BRD/PRD/EARS/BDD/ADR pattern) with consistent orchestration, diagnostics, and fixer handoff.

---

## 2. Scope

### In Scope
- `.claude/skills/doc-sys/SKILL.md`
- `.claude/skills/doc-sys-autopilot/SKILL.md`
- `.claude/skills/doc-sys-validator/SKILL.md`
- `.claude/skills/doc-sys-reviewer/SKILL.md`
- `.claude/skills/doc-sys-fixer/SKILL.md`
- **New file**: `.claude/skills/doc-sys-audit/SKILL.md`
- Skill index registration updates:
  - `.claude/skills/README.md`

### Out of Scope
- Runtime validator/autopilot script behavior changes in `/opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/scripts/*`
- BRD/PRD/EARS/BDD/ADR/REQ skill remediation
- SYS content document rewrites in `docs/06_SYS/*`

---

## 3. Baseline Findings (From Scratch Audit)

Observed in current `ucx_framework` SYS skills:

1. Frontmatter schema drift: top-level `tags`/`custom_fields` remain in all five SYS skill files.
2. Stale path usage: active `ai_dev_flow/` references remain across SYS skills (templates/rules/commands).
3. No unified SYS audit wrapper exists (`doc-sys-audit` missing).
4. SYS fixer/autopilot/reviewer/validator examples are `.R_review_report`-centric without `.A_audit_report` compatibility contract.
5. SYS validator schema/command examples use legacy base paths and non-canonical schema naming.
6. SYS reviewer/fixer include incorrect report folder examples (`docs/SYS/...` instead of `docs/06_SYS/...`).
7. `doc-sys-autopilot` references non-existent comprehensive template (`SYS-TEMPLATE.md`).
8. `doc-sys-autopilot` command examples reference non-existent direct scripts (`sys_autopilot.py`, `req_autopilot.py`).
9. `doc-sys` references legacy rule/schema names (`SYS_CREATION_RULES.md`, `SYS_VALIDATION_RULES.md`, `SYS_SCHEMA.yaml`) instead of current `SYS_MVP_*` canon.
10. Skills index currently exposes BRD/PRD/EARS/BDD/ADR audit wrappers, not SYS.
11. `doc-sys-fixer` upstream contract currently references `SYS-NN.F_fix_report_vNNN.md` as review input (wrong artifact type).
12. `doc-sys-autopilot` Review Document Standards still use non-versioned review filename examples (`SYS-NN.R_review_report.md`).
13. `doc-sys` references section-template files (`SYS-SECTION-0-TEMPLATE.md`, `SYS-SECTION-TEMPLATE.md`) that are not present in current `ai_dev_ssd_flow/06_SYS` artifacts.

Current diagnostics status:
- Existing issues are primarily parity/contract/path consistency, not markdown parser blockers.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **MVP Conformance Gate Missing by Default**
   - Must verify alignment with `/opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS` canonical template/rules/schema before edits.
2. **Cross-workspace Scope Risk**
   - Searches can return both workspaces; all edits/staging must be scoped to `/opt/data/ucx_framework`.
3. **Audit/Fixer Compatibility Risk**
   - `doc-sys-fixer` must accept both report forms:
     - `SYS-NN.A_audit_report_vNNN.md` (preferred)
     - `SYS-NN.R_review_report_vNNN.md` (legacy)
4. **Version/Metadata Drift Risk**
   - Every touched SYS skill must update frontmatter version metadata and `Version History`.
5. **Index Visibility Gap**
   - `.claude/skills/README.md` audit-wrapper listing must include SYS.
6. **Command Reference Drift**
   - Validator examples must point to existing `/opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/scripts/validate_sys.py`.
7. **Embedded Example False-Positive Risk**
   - SYS skill files contain internal markdown examples with `tags:` / `custom_fields:`.
   - Frontmatter migration must only touch top-of-file YAML.
8. **Validator Example Contract Drift**
   - `doc-sys-validator` sample output tree currently shows `.R_` only; examples must reflect audit-wrapper compatibility.
9. **Precedence Tie-Break Gap**
   - Deterministic report selection must be explicit: latest timestamp first; if tied, prefer `.A_` over `.R_`.
10. **Review Document Standards Compatibility Gap**
   - Autopilot/reviewer/fixer report storage/versioning sections must include audit-first with legacy reviewer compatibility.
11. **Autopilot Script Existence Gap**
   - Repository does not contain `ai_dev_ssd_flow/**/sys_autopilot.py` or `ai_dev_ssd_flow/**/req_autopilot.py`.
   - Plan must replace those script examples with valid alternatives (skill-invocation examples and/or existing script paths only).
12. **Template/Schema Name Drift Gap**
   - Repository does not contain `SYS-TEMPLATE.md` or `SYS_SCHEMA.yaml` in `ai_dev_ssd_flow/06_SYS/`.
   - References must standardize to `SYS-MVP-TEMPLATE.md` and `SYS_MVP_SCHEMA.yaml`.
13. **Path Hygiene Gap**
   - All report location examples and command path examples must use `docs/06_SYS/...` (not `docs/SYS/...`).
14. **Audit Wrapper Index Drift Gap**
   - README currently lists `doc-brd-audit, doc-prd-audit, doc-ears-audit, doc-bdd-audit, doc-adr-audit`; Phase D must append `doc-sys-audit`.
15. **Fixer Upstream Artifact Contract Gap**
   - `doc-sys-fixer` must consume audit/review report as upstream evidence, not fix report artifacts.
   - Upstream example must be `SYS-NN.A_audit_report_vNNN.md` (preferred) / `SYS-NN.R_review_report_vNNN.md` (legacy).
16. **Review Filename Versioning Gap**
   - SYS review-report references must consistently use `_vNNN` versioned naming in autopilot/reviewer/fixer standards sections.
17. **Section Template Reference Gap**
   - SYS guidance must not point to non-existent section-template files.
   - Replace with canonical SYS MVP references and/or remove unsupported template pointers.

---

## 5. Design Approach (Mirror BRD Model)

### 5.1 Target Skill Topology
- `doc-sys` (authoring)
- `doc-sys-autopilot` (orchestration)
- `doc-sys-validator` (structure/schema checks)
- `doc-sys-reviewer` (semantic/content checks)
- `doc-sys-fixer` (auto/manual remediation)
- `doc-sys-audit` (**new unified validator+reviewer wrapper**)

### 5.2 `doc-sys-audit` Contract (New)
Sequence:
1) run `doc-sys-validator`
2) run `doc-sys-reviewer`
3) normalize findings
4) emit `SYS-NN.A_audit_report_vNNN.md`
5) optional handoff to `doc-sys-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 SYS Policy Alignment
- Preserve existing SYS quality/threshold policy from current validator/reviewer contracts.
- Do not invent new blocking code families unless current SYS validator/reviewer already define them.

---

## 6. Implementation Phases

### Phase A0 — MVP SYS Conformance Gate
Authoritative sources (must be treated as canonical):
- `/opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/SYS-MVP-TEMPLATE.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/SYS_MVP_CREATION_RULES.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/SYS_MVP_VALIDATION_RULES.md`
- `/opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/SYS_MVP_SCHEMA.yaml`

Checklist:
1. Structure model alignment (15-section SYS MVP conventions).
2. Readiness threshold language alignment (>=90% where applicable).
3. Nested-folder/path conventions alignment.
4. Rule/schema/template filename alignment.

Acceptance:
- No contradictions between SYS skills and canonical SYS MVP references.

### Phase A — Frontmatter Normalization
Files:
- `doc-sys`, `doc-sys-autopilot`, `doc-sys-validator`, `doc-sys-reviewer`, `doc-sys-fixer`

Actions:
- Move root `tags`/`custom_fields` into `metadata`.
- Preserve semantic values; normalize only top frontmatter.

Acceptance:
- No frontmatter schema errors in SYS skill files.

### Phase B — Path/Rules/Command Reference Normalization
Files:
- `doc-sys`, `doc-sys-autopilot`, `doc-sys-validator` (plus reviewer/fixer where needed)

Actions:
- Replace active `ai_dev_flow/` references with `ai_dev_ssd_flow/`.
- Ensure SYS rule/schema references use MVP filenames (`SYS_MVP_*`).
- Normalize validator examples to existing `ai_dev_ssd_flow/06_SYS/scripts/validate_sys.py`.
- Remove/replace non-existent `SYS-TEMPLATE.md` and `SYS_SCHEMA.yaml` references with canonical SYS MVP artifacts.
- Remove/replace non-existent `sys_autopilot.py` and `req_autopilot.py` command examples with valid invocation patterns.
- Correct report location examples from `docs/SYS/...` to `docs/06_SYS/...`.
- Correct fixer upstream contract examples that incorrectly reference `F_fix_report` as input.
- Remove/replace non-existent `SYS-SECTION-0-TEMPLATE.md` and `SYS-SECTION-TEMPLATE.md` references.

Acceptance:
- No stale active `ai_dev_flow/` paths in SYS skill guidance.
- No references remain to non-existent SYS artifacts/scripts (`SYS-TEMPLATE.md`, `SYS_SCHEMA.yaml`, `sys_autopilot.py`, `req_autopilot.py`).

### Phase C — Add `doc-sys-audit`
File:
- Create `.claude/skills/doc-sys-audit/SKILL.md`

Actions:
- Mirror `doc-brd-audit` structure and contract style.
- Bind to SYS validator/reviewer findings.
- Define output contract: `SYS-NN.A_audit_report_vNNN.md`.
- Include invocation examples for direct audit and fixer handoff.

Acceptance:
- New wrapper passes diagnostics and references only existing SYS skills.

### Phase D — Integrate Wrapper Contracts
Files:
- `doc-sys-autopilot/SKILL.md`
- `doc-sys-validator/SKILL.md`
- `doc-sys-reviewer/SKILL.md`
- `doc-sys-fixer/SKILL.md`
- `.claude/skills/README.md`

Actions:
- Add wrapper usage guidance (audit-first flow).
- Update fixer input contract to support `.A_` + `.R_` with deterministic precedence.
- Normalize validator/reviewer/autopilot examples to audit-wrapper-compatible report handling.
- Normalize Review Document Standards filename examples to versioned form (`*_vNNN`).
- Update versions/history metadata in all touched files.
- Register `doc-sys-audit` in audit-wrapper index listing.

Acceptance:
- Coherent path: `autopilot -> audit -> fixer` documented.
- Validator/reviewer/fixer examples are compatible with audit-wrapper flow.
- Precedence rule explicit: latest timestamp, then `.A_` over `.R_`.
- Fixer upstream contract references only audit/review reports as inputs (never fix reports).
- README audit-wrapper aggregate includes `doc-sys-audit`.

### Phase E — Validation and Evidence
Actions:
- Run diagnostics on all six SYS skills.
- Run scoped grep checks for:
  - stale paths,
  - legacy rule/schema names,
  - non-existent script/template names,
  - `.A_` / `.R_` compatibility,
  - audit wrapper indexing.
- Enforce scoped git add and file list verification before commit.

Acceptance:
- No schema errors in touched SYS skills.
- No stale active references.
- Wrapper created, integrated, discoverable.

---

## 7. Verification Commands

```bash
# Stale path scan
rg -n "ai_dev_flow/" .claude/skills/doc-sys*/SKILL.md

# Legacy SYS rule/schema-name scan
rg -n "SYS_CREATION_RULES.md|SYS_VALIDATION_RULES.md|SYS_SCHEMA.yaml|SYS-TEMPLATE.md|SYS-SECTION-0-TEMPLATE.md|SYS-SECTION-TEMPLATE.md" .claude/skills/doc-sys*/SKILL.md

# Non-existent direct script reference scan
rg -n "sys_autopilot.py|req_autopilot.py" .claude/skills/doc-sys*/SKILL.md

# Wrapper/report compatibility scan
rg -n "A_audit_report|R_review_report|--review-report" \
  .claude/skills/doc-sys-fixer/SKILL.md \
  .claude/skills/doc-sys-autopilot/SKILL.md \
  .claude/skills/doc-sys-validator/SKILL.md \
  .claude/skills/doc-sys-audit/SKILL.md

# Fixer upstream contract sanity scan (must not use F_fix as upstream report)
rg -n "Upstream\*\*:.*F_fix_report|source_review: SYS-NN\.F_fix_report" .claude/skills/doc-sys-fixer/SKILL.md

# Location hygiene scan
rg -n "docs/SYS/" .claude/skills/doc-sys*/SKILL.md

# Review filename versioning scan
rg -n "R_review_report\.md|A_audit_report\.md" .claude/skills/doc-sys*/SKILL.md

# Index registration
rg -n "doc-sys-audit" .claude/skills/README.md

# Validator script-path sanity scan
rg -n "validate_sys.py|validate_sys_quality_score.sh" .claude/skills/doc-sys*/SKILL.md

# Canonical SYS artifact existence sanity check
ls /opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/SYS-MVP-TEMPLATE.md \
   /opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/SYS_MVP_SCHEMA.yaml \
   /opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/scripts/validate_sys.py

# Optional section-template existence check (informational)
for f in \
   /opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/SYS-SECTION-0-TEMPLATE.md \
   /opt/data/ucx_framework/ai_dev_ssd_flow/06_SYS/SYS-SECTION-TEMPLATE.md; do
   [[ -e "$f" ]] && echo "present: $f" || echo "absent: $f"
done

# Commit scope guard
git diff --name-only
```

---

## 8. Execution Notes

- Workspace has two roots; all operations must target `/opt/data/ucx_framework`.
- Use explicit file-path staging for commit.
- Keep changes surgical; do not alter runtime scripts in this plan.
