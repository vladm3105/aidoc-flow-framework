---
title: "IPLAN-013: ADR Skill Parity + Audit Wrapper"
tags:
  - implementation-plan
  - layer-5-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-013
  status: draft
  created_date: 2026-02-26
  timezone: America/New_York
---

# IPLAN-013: ADR Skill Parity + Audit Wrapper

## 1. Objective

Bring ADR skill stack to BRD-equivalent operational model by:
- normalizing ADR skill frontmatter/schema compliance,
- removing stale path/rule/script references,
- introducing a unified `doc-adr-audit` wrapper skill,
- aligning reviewer/fixer/autopilot contracts to audit-first flow.

Target outcome: ADR skills become a 6-skill set (matching BRD/PRD/EARS/BDD pattern) with consistent orchestration, diagnostics, and fixer handoff.

---

## 2. Scope

### In Scope
- `.claude/skills/doc-adr/SKILL.md`
- `.claude/skills/doc-adr-autopilot/SKILL.md`
- `.claude/skills/doc-adr-validator/SKILL.md`
- `.claude/skills/doc-adr-reviewer/SKILL.md`
- `.claude/skills/doc-adr-fixer/SKILL.md`
- **New file**: `.claude/skills/doc-adr-audit/SKILL.md`
- Skill index registration updates:
  - `.claude/skills/README.md`

### Out of Scope
- Runtime validator/autopilot script behavior changes in `ai_dev_ssd_flow/05_ADR/scripts/*`
- BRD/PRD/EARS/BDD/SYS/REQ skill remediation
- ADR content document rewrites in `docs/05_ADR/*`

---

## 3. Baseline Findings (From Scratch Audit)

Observed in current `ucx_framework` ADR skills:

1. Frontmatter schema drift: top-level `tags`/`custom_fields` remain in all five ADR skill files.
2. Stale path usage: active `ai_dev_flow/` references remain across ADR skills (templates/rules/commands).
3. No unified ADR audit wrapper exists (`doc-adr-audit` missing).
4. ADR fixer/autopilot/reviewer/validator examples are `.R_review_report`-centric without `.A_audit_report` compatibility contract.
5. ADR validator schema and command references use stale base paths.
6. Skills index currently exposes BRD/PRD/EARS/BDD audit wrappers, not ADR.
7. `doc-adr-autopilot` references a non-existent comprehensive template (`ADR-TEMPLATE.md`).
8. `doc-adr-autopilot` command examples reference non-existent direct scripts (`adr_autopilot.py`, `sys_autopilot.py`).
9. `doc-adr` references legacy rule/schema names (`ADR_CREATION_RULES.md`, `ADR_VALIDATION_RULES.md`, `ADR_SCHEMA.yaml`) that do not match current `ADR_MVP_*` canon.

Current diagnostics status:
- `get_errors` previously reported no blocking parser issues in ADR skills.
- Primary issues are parity/contract/path consistency, not markdown parse stability.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **MVP Conformance Gate Missing by Default**
   - Must verify alignment with `ai_dev_ssd_flow/05_ADR` canonical template/rules/schema before edits.
2. **Cross-workspace Scope Risk**
   - Searches can return both workspaces; all edits/staging must be scoped to `/opt/data/ucx_framework`.
3. **Audit/Fixer Compatibility Risk**
   - `doc-adr-fixer` must accept both report forms:
     - `ADR-NN.A_audit_report_vNNN.md` (preferred)
     - `ADR-NN.R_review_report_vNNN.md` (legacy)
4. **Version/Metadata Drift Risk**
   - Every touched ADR skill must update frontmatter version metadata and `Version History`.
5. **Index Visibility Gap**
   - `.claude/skills/README.md` audit-wrapper listing must include ADR.
6. **Command Reference Drift**
   - Validator command examples must point to existing `ai_dev_ssd_flow/05_ADR/scripts/validate_adr.py` location.
7. **Embedded Example False-Positive Risk**
   - ADR skill files contain internal markdown examples with `tags:` / `custom_fields:`.
   - Frontmatter migration must only touch top-of-file YAML.
8. **Validator Example Contract Drift**
   - `doc-adr-validator` sample output trees currently show `.R_` only; examples must reflect audit-wrapper era compatibility.
9. **Precedence Tie-Break Gap**
   - Deterministic report selection must be explicit: latest timestamp first; if tied, prefer `.A_` over `.R_`.
10. **Review Document Standards Compatibility Gap**
   - Autopilot/reviewer/fixer sections that document report storage/versioning must include audit-first with legacy reviewer compatibility.
11. **Script Location Ambiguity Gap**
   - `validate_adr.py` is confirmed under `ai_dev_ssd_flow/05_ADR/scripts/`.
   - Plan must avoid generic rewrites to non-existent script locations.
12. **Audit Wrapper Index Drift Gap**
   - README currently lists `doc-brd-audit, doc-prd-audit, doc-ears-audit, doc-bdd-audit`; Phase D must explicitly append `doc-adr-audit`.
13. **Autopilot Script Existence Gap**
   - Repository does not contain `ai_dev_ssd_flow/**/adr_autopilot.py` or `ai_dev_ssd_flow/**/sys_autopilot.py`.
   - Phase B must replace these Python-path examples with valid alternatives (skill-invocation examples and/or existing script paths only).
14. **Template/Schema Name Drift Gap**
   - Repository does not contain `ADR-TEMPLATE.md` or `ADR_SCHEMA.yaml` in `ai_dev_ssd_flow/05_ADR/`.
   - Phase B must standardize references to `ADR-MVP-TEMPLATE.md` and `ADR_MVP_SCHEMA.yaml` only.

---

## 5. Design Approach (Mirror BRD Model)

### 5.1 Target Skill Topology
- `doc-adr` (authoring)
- `doc-adr-autopilot` (orchestration)
- `doc-adr-validator` (structure/schema checks)
- `doc-adr-reviewer` (semantic/content checks)
- `doc-adr-fixer` (auto/manual remediation)
- `doc-adr-audit` (**new unified validator+reviewer wrapper**)

### 5.2 `doc-adr-audit` Contract (New)
Sequence:
1) run `doc-adr-validator`
2) run `doc-adr-reviewer`
3) normalize findings
4) emit `ADR-NN.A_audit_report_vNNN.md`
5) optional handoff to `doc-adr-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 ADR Policy Alignment
- Preserve existing ADR quality/threshold policy from current validator/reviewer contracts.
- Do not invent new blocking code families unless existing validator/reviewer contract already defines them.

---

## 6. Implementation Phases

### Phase A0 — MVP ADR Conformance Gate
Authoritative sources:
- `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/05_ADR/ADR_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/05_ADR/ADR_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/05_ADR/ADR_MVP_SCHEMA.yaml`

Checklist:
1. Structure model alignment (11-section ADR MVP conventions).
2. Readiness threshold language alignment (>=90% where applicable).
3. Nested-folder/path conventions alignment.
4. Rule/schema/template filename alignment.

Acceptance:
- No contradictions between ADR skills and canonical ADR MVP references.

### Phase A — Frontmatter Normalization
Files:
- `doc-adr`, `doc-adr-autopilot`, `doc-adr-validator`, `doc-adr-reviewer`, `doc-adr-fixer`

Actions:
- Move root `tags`/`custom_fields` into `metadata`.
- Preserve semantic values; normalize only top frontmatter.

Acceptance:
- No frontmatter schema errors in ADR skill files.

### Phase B — Path/Rules/Command Reference Normalization
Files:
- `doc-adr`, `doc-adr-autopilot`, `doc-adr-validator` (plus reviewer/fixer where needed)

Actions:
- Replace active `ai_dev_flow/` references with `ai_dev_ssd_flow/`.
- Ensure ADR rule references use MVP filenames (`ADR_MVP_*`).
- Normalize script command examples to real script locations.
- Remove/replace non-existent `ADR-TEMPLATE.md` and `ADR_SCHEMA.yaml` references with canonical ADR MVP artifacts.
- Remove/replace non-existent `adr_autopilot.py` and `sys_autopilot.py` command examples with valid invocation patterns.

Acceptance:
- No stale active `ai_dev_flow/` paths in ADR skill guidance.
- No references remain to non-existent ADR artifacts/scripts (`ADR-TEMPLATE.md`, `ADR_SCHEMA.yaml`, `adr_autopilot.py`, `sys_autopilot.py`).

### Phase C — Add `doc-adr-audit`
File:
- Create `.claude/skills/doc-adr-audit/SKILL.md`

Actions:
- Mirror `doc-brd-audit` structure and contract style.
- Bind to ADR validator/reviewer findings.
- Define output contract: `ADR-NN.A_audit_report_vNNN.md`.
- Include invocation examples for direct audit and fixer handoff.

Acceptance:
- New wrapper passes diagnostics and references only existing ADR skills.

### Phase D — Integrate Wrapper Contracts
Files:
- `doc-adr-autopilot/SKILL.md`
- `doc-adr-validator/SKILL.md`
- `doc-adr-reviewer/SKILL.md`
- `doc-adr-fixer/SKILL.md`
- `.claude/skills/README.md`

Actions:
- Add wrapper usage guidance (audit-first flow).
- Update fixer input contract to support `.A_` + `.R_` with deterministic precedence.
- Normalize validator/reviewer/autopilot examples to audit-wrapper-compatible report handling.
- Normalize validator command examples to `ai_dev_ssd_flow/05_ADR/scripts/validate_adr.py`.
- Update versions/history metadata in all touched files.
- Register `doc-adr-audit` in audit-wrapper index listing.

Acceptance:
- Coherent path: `autopilot -> audit -> fixer` documented.
- Validator/reviewer/fixer examples are compatible with audit-wrapper flow.
- Precedence rule explicit: latest timestamp, then `.A_` over `.R_`.
- Validator script paths resolve to actual repository locations under `ai_dev_ssd_flow/05_ADR/scripts/`.
- README audit-wrapper aggregate includes `doc-adr-audit`.

### Phase E — Validation and Evidence
Actions:
- Run diagnostics on all six ADR skills.
- Run scoped grep checks for:
  - stale paths,
  - legacy rule names,
  - `.A_` / `.R_` compatibility,
  - audit wrapper indexing.
- Enforce scoped git add and file list verification before commit.

Acceptance:
- No schema errors in touched ADR skills.
- No stale active references.
- Wrapper created, integrated, discoverable.

---

## 7. Verification Commands

```bash
# Stale path scan
rg -n "ai_dev_flow/" .claude/skills/doc-adr*/SKILL.md

# Legacy ADR rule-name scan
rg -n "ADR_CREATION_RULES.md|ADR_VALIDATION_RULES.md|ADR_SCHEMA.yaml|ADR-TEMPLATE.md" .claude/skills/doc-adr*/SKILL.md

# Non-existent direct script reference scan
rg -n "adr_autopilot.py|sys_autopilot.py" .claude/skills/doc-adr*/SKILL.md

# Wrapper/report compatibility scan
rg -n "A_audit_report|R_review_report|--review-report" \
  .claude/skills/doc-adr-fixer/SKILL.md \
  .claude/skills/doc-adr-autopilot/SKILL.md \
  .claude/skills/doc-adr-validator/SKILL.md \
  .claude/skills/doc-adr-audit/SKILL.md

# Index registration
rg -n "doc-adr-audit" .claude/skills/README.md

# Review-document standards compatibility scan
rg -n "Review Document Standards|R_review_report|A_audit_report" .claude/skills/doc-adr*/SKILL.md

# Validator script-path sanity scan
rg -n "validate_adr.py|validate_adr_quality_score.sh" .claude/skills/doc-adr*/SKILL.md

# Canonical ADR artifact existence sanity check
ls ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md ai_dev_ssd_flow/05_ADR/ADR_MVP_SCHEMA.yaml

# Commit scope guard
git diff --name-only
```

---

## 8. Execution Notes

- Workspace has two roots; all operations must target `/opt/data/ucx_framework`.
- Use explicit file-path staging for commit.
- Keep changes surgical; do not alter runtime scripts in this plan.
