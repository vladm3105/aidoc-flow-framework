---
title: "IPLAN-012: BDD Skill Parity + Audit Wrapper"
tags:
  - implementation-plan
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: iplan
  plan_id: IPLAN-012
  status: draft
  created_date: 2026-02-26
  timezone: America/New_York
---

# IPLAN-012: BDD Skill Parity + Audit Wrapper

## 1. Objective

Bring BDD skill stack to BRD-equivalent operational model by:
- normalizing BDD skill frontmatter/schema compliance,
- removing stale path/rule/script references,
- introducing a unified `doc-bdd-audit` wrapper skill,
- aligning reviewer/fixer/autopilot contracts to audit-first flow.

Target outcome: BDD skills become a 6-skill set (matching BRD/PRD/EARS pattern) with consistent orchestration, diagnostics, and fixer handoff.

---

## 2. Scope

### In Scope
- `.claude/skills/doc-bdd/SKILL.md`
- `.claude/skills/doc-bdd-autopilot/SKILL.md`
- `.claude/skills/doc-bdd-validator/SKILL.md`
- `.claude/skills/doc-bdd-reviewer/SKILL.md`
- `.claude/skills/doc-bdd-fixer/SKILL.md`
- **New file**: `.claude/skills/doc-bdd-audit/SKILL.md`
- Skill index registration updates:
  - `.claude/skills/README.md`

### Out of Scope
- Runtime validator/autopilot script behavior changes in `ai_dev_ssd_flow/04_BDD/scripts/*`
- BRD/PRD/EARS/ADR/SYS/REQ skill remediation
- BDD content document rewrites in `docs/04_BDD/*`

---

## 3. Baseline Findings (From Scratch Audit)

Observed in current `ucx_framework` BDD skills:

1. Frontmatter schema drift: top-level `tags`/`custom_fields` remain in all five BDD skill files.
2. Stale path usage: many active `ai_dev_flow/` references remain (notably in `doc-bdd-autopilot` and `doc-bdd-validator`).
3. Partial standards drift: `doc-bdd` still references `ai_dev_flow/ID_NAMING_STANDARDS.md`.
4. No unified BDD audit wrapper exists (`doc-bdd-audit` missing).
5. BDD fixer/autopilot/reviewer/validator examples are `.R_review_report`-centric without `.A_audit_report` compatibility contract.
6. Skills index currently exposes only BRD/PRD/EARS audit wrappers, not BDD.

Current diagnostics status:
- `get_errors` reports no blocking parser errors in current BDD skills.
- Primary issues are parity/contract/path consistency, not syntax.

---

## 4. Plan-Level Gaps (Pre-Implementation Controls)

1. **MVP Conformance Gate Missing by Default**
   - Must verify alignment with `ai_dev_ssd_flow/04_BDD` canonical template/rules/schema before edits.
2. **Cross-workspace Scope Risk**
   - Searches can return both workspaces; all edits/staging must be scoped to `/opt/data/ucx_framework`.
3. **Audit/Fixer Compatibility Risk**
   - `doc-bdd-fixer` must accept both report forms:
     - `BDD-NN.A_audit_report_vNNN.md` (preferred)
     - `BDD-NN.R_review_report_vNNN.md` (legacy)
4. **Version/Metadata Drift Risk**
   - Every touched BDD skill must update frontmatter version metadata and `Version History`.
5. **Index Visibility Gap**
   - `.claude/skills/README.md` audit-wrapper listing must include BDD.
6. **Command Reference Drift**
   - Autopilot/validator command examples must point to existing `ai_dev_ssd_flow` locations.
7. **Embedded Example False-Positive Risk**
   - BDD skill files contain internal markdown examples with `tags:` / `custom_fields:`.
   - Frontmatter migration must only touch top-of-file YAML.
8. **Validator Example Contract Drift**
   - `doc-bdd-validator` sample output trees currently show `.R_` only; examples must reflect audit-wrapper era compatibility.
9. **Precedence Tie-Break Gap**
   - Deterministic report selection must be explicit: latest timestamp first; if tied, prefer `.A_` over `.R_`.
10. **Review Document Standards Compatibility Gap**
   - Autopilot/reviewer/fixer sections that document report storage/versioning must include audit-first with legacy reviewer compatibility.
11. **Script Location Ambiguity Gap**
   - BDD validator scripts are confirmed under `ai_dev_ssd_flow/04_BDD/scripts/`.
   - Plan must avoid generic `ai_dev_ssd_flow/scripts/validate_bdd.py` rewrites and enforce actual path usage.
12. **BDD Docs vs Test Artifacts Path Gap**
   - Validator examples currently mix `docs/04_BDD/*` and `tests/bdd/features/*`.
   - Plan must preserve valid dual-context examples while eliminating stale `ai_dev_flow` base paths.
13. **Audit Wrapper Index Drift Gap**
   - README currently lists `doc-brd-audit, doc-prd-audit, doc-ears-audit`; Phase D must explicitly append `doc-bdd-audit` to this aggregate line.

---

## 5. Design Approach (Mirror BRD Model)

### 5.1 Target Skill Topology
- `doc-bdd` (authoring)
- `doc-bdd-autopilot` (orchestration)
- `doc-bdd-validator` (structure/schema checks)
- `doc-bdd-reviewer` (semantic/content checks)
- `doc-bdd-fixer` (auto/manual remediation)
- `doc-bdd-audit` (**new unified validator+reviewer wrapper**)

### 5.2 `doc-bdd-audit` Contract (New)
Sequence:
1) run `doc-bdd-validator`
2) run `doc-bdd-reviewer`
3) normalize findings
4) emit `BDD-NN.A_audit_report_vNNN.md`
5) optional handoff to `doc-bdd-fixer`

Combined status:
- PASS: validator PASS AND reviewer >= threshold AND no blocking/manual-required findings
- FAIL: validator FAIL OR reviewer < threshold OR blocking/manual-required findings

### 5.3 BDD Policy Alignment
- Preserve existing BDD quality/threshold policy from current validator/reviewer contracts.
- Do not invent new blocking code families unless existing validator/reviewer contract already defines them.

---

## 6. Implementation Phases

### Phase A0 — MVP BDD Conformance Gate
Authoritative sources:
- `ai_dev_ssd_flow/04_BDD/BDD-MVP-TEMPLATE.feature`
- `ai_dev_ssd_flow/04_BDD/BDD_MVP_CREATION_RULES.md`
- `ai_dev_ssd_flow/04_BDD/BDD_MVP_VALIDATION_RULES.md`
- `ai_dev_ssd_flow/04_BDD/BDD_MVP_SCHEMA.yaml`

Checklist:
1. Structure model alignment (MVP feature/scenario conventions).
2. Readiness threshold language alignment (>=90% where applicable).
3. Nested-folder/path conventions alignment.
4. Rule/schema/template filename alignment.

Acceptance:
- No contradictions between BDD skills and canonical BDD MVP references.

### Phase A — Frontmatter Normalization
Files:
- `doc-bdd`, `doc-bdd-autopilot`, `doc-bdd-validator`, `doc-bdd-reviewer`, `doc-bdd-fixer`

Actions:
- Move root `tags`/`custom_fields` into `metadata`.
- Preserve semantic values; normalize only top frontmatter.

Acceptance:
- No frontmatter schema errors in BDD skill files.

### Phase B — Path/Rules/Command Reference Normalization
Files:
- `doc-bdd`, `doc-bdd-autopilot`, `doc-bdd-validator` (plus reviewer/fixer where needed)

Actions:
- Replace active `ai_dev_flow/` references with `ai_dev_ssd_flow/`.
- Ensure BDD rule references use MVP filenames.
- Normalize script command examples to real script locations.

Acceptance:
- No stale active `ai_dev_flow/` paths in BDD skill guidance.

### Phase C — Add `doc-bdd-audit`
File:
- Create `.claude/skills/doc-bdd-audit/SKILL.md`

Actions:
- Mirror `doc-brd-audit` structure and contract style.
- Bind to BDD validator/reviewer findings.
- Define output contract: `BDD-NN.A_audit_report_vNNN.md`.
- Include invocation examples for direct audit and fixer handoff.

Acceptance:
- New wrapper passes diagnostics and references only existing BDD skills.

### Phase D — Integrate Wrapper Contracts
Files:
- `doc-bdd-autopilot/SKILL.md`
- `doc-bdd-validator/SKILL.md`
- `doc-bdd-reviewer/SKILL.md`
- `doc-bdd-fixer/SKILL.md`
- `.claude/skills/README.md`

Actions:
- Add wrapper usage guidance (audit-first flow).
- Update fixer input contract to support `.A_` + `.R_` with deterministic precedence.
- Normalize validator/reviewer/autopilot examples to audit-wrapper-compatible report handling.
- Normalize validator command examples to `ai_dev_ssd_flow/04_BDD/scripts/validate_bdd.py`.
- Preserve and validate both `docs/04_BDD/*` and `tests/bdd/features/*` examples where semantically intended.
- Update versions/history metadata in all touched files.
- Register `doc-bdd-audit` in audit-wrapper index listing.

Acceptance:
- Coherent path: `autopilot -> audit -> fixer` documented.
- Validator/reviewer/fixer examples are compatible with audit-wrapper flow.
- Precedence rule explicit: latest timestamp, then `.A_` over `.R_`.
- Validator script paths resolve to actual repository locations under `ai_dev_ssd_flow/04_BDD/scripts/`.
- README audit-wrapper aggregate includes `doc-bdd-audit`.

### Phase E — Validation and Evidence
Actions:
- Run diagnostics on all six BDD skills.
- Run scoped grep checks for:
  - stale paths,
  - legacy rule names,
  - `.A_` / `.R_` compatibility,
  - audit wrapper indexing.
- Enforce scoped git add and file list verification before commit.

Acceptance:
- No schema errors in touched BDD skills.
- No stale active references.
- Wrapper created, integrated, discoverable.

---

## 7. Verification Commands

```bash
# Stale path scan
rg -n "ai_dev_flow/" .claude/skills/doc-bdd*/SKILL.md

# Legacy BDD rule-name scan
rg -n "BDD_CREATION_RULES.md|BDD_VALIDATION_RULES.md" .claude/skills/doc-bdd*/SKILL.md

# Wrapper/report compatibility scan
rg -n "A_audit_report|R_review_report|--review-report" \
  .claude/skills/doc-bdd-fixer/SKILL.md \
  .claude/skills/doc-bdd-autopilot/SKILL.md \
  .claude/skills/doc-bdd-validator/SKILL.md \
  .claude/skills/doc-bdd-audit/SKILL.md

# Index registration
rg -n "doc-bdd-audit" .claude/skills/README.md

# Review-document standards compatibility scan
rg -n "Review Document Standards|R_review_report|A_audit_report" .claude/skills/doc-bdd*/SKILL.md

# Validator script-path sanity scan
rg -n "validate_bdd.py|validate_bdd_suite.py|tests/bdd/features" .claude/skills/doc-bdd*/SKILL.md

# Commit scope guard
git diff --name-only
```

---

## 8. Execution Notes

- Workspace has two roots; all operations must target `/opt/data/ucx_framework`.
- Use explicit file-path staging for commit.
- Keep changes surgical; do not alter runtime scripts in this plan.
