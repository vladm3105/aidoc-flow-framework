---
title: "IPLAN-009 BRD→PRD Diagram Contract Transition"
tags:
  - implementation-plan
  - layer-1-artifact
  - layer-2-artifact
  - diagram-contract
  - shared-architecture
custom_fields:
  plan_id: IPLAN-009
  transition_type: brd-to-prd-diagram-origin
  status: draft
  created_at: 2026-02-26T16:25:00-05:00
  timezone: America/New_York
---

# IPLAN-009: Exact Change Set for Safe BRD→PRD Diagram-Contract Transition

## 1) Objective

Move C4/DFD/Sequence diagram contract origin from BRD (Layer 1) to PRD (Layer 2) while preserving compatibility for existing BRDs and avoiding validator/reviewer code drift.

## 2) Scope

In scope:
- Framework rules and templates in `ai_dev_ssd_flow/01_BRD` and `ai_dev_ssd_flow/02_PRD`
- Framework skills in `.claude/skills/doc-brd*` and `.claude/skills/doc-prd*`
- Runtime validators in:
  - `ai_dev_ssd_flow/01_BRD/scripts/validate_brd.py`
  - `ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py`

Out of scope:
- Existing project artifacts under `b-local-docs/docs-v2.0/*`
- Non-BRD/PRD layers (EARS/BDD/ADR/SYS/REQ) except reference-link updates to PRD IDs

## 3) Baseline (Current State)

- BRD template/rules currently declare mandatory BRD diagram contract (`c4-l1`, `dfd-l0`) and scoring impact.
- PRD template already has mandatory PRD diagram contract (`c4-l2`, `dfd-l1`, `sequence-*`).
- Both `validate_brd.py` and `validate_prd.py` run diagram checks, but currently emit generic warning codes (`BRD-W001`, `PRD-W001`) for missing tags/intent.
- BRD reviewer/fixer already has diagram-specific code family (`REV-DC001..004`), PRD reviewer has `REV-DC001..003`, PRD fixer lacks explicit REV-DC fix mapping.

Baseline constraints to preserve:
- Shared error registry is centralized at `ai_dev_ssd_flow/scripts/error_codes.py` and must be updated with any new BRD/PRD codes.
- Schema code catalogs in `BRD_MVP_SCHEMA.yaml` and `PRD_MVP_SCHEMA.yaml` must stay synchronized with validator/runtime code usage.
- `validate_prd.py` currently overloads `PRD-W001` for multiple warnings; transition must normalize this to avoid ambiguity.

## 4) Target Policy

- BRD: diagram contract is optional/informational (non-blocking).
- PRD: diagram contract is mandatory and blocking.
- Score ownership:
  - Remove diagram deductions/penalties from BRD PRD-Ready score.
  - Add/retain diagram readiness deductions in PRD readiness scoring (SYS-Ready and/or EARS-Ready as defined below).

## 5) Exact File-Level Change Set

## 5.1 Layer-1 (BRD) Rules/Templates

1) `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md`
- In section `3.4.3 Required Diagram Contract (MVP)`:
  - Rename header to: `3.4.3 Optional Business Visualization (Transition Policy)`
  - Replace “For BRD, include both” with “BRD diagrams are optional and non-blocking; canonical design contract starts in PRD”.
  - Keep examples as optional reference, remove “Required declaration block”.

2) `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md`
- In CHECK 13–18 scoring section:
  - Remove diagram-related deductions from BRD PRD-Ready formula categories.
  - Add policy note: “Diagram completeness evaluated at PRD Layer (CHECK PRD-DIAG-*)”.
- In CHECK 21 (Workflow Diagrams):
  - Keep as non-blocking recommendation only.
  - Remove language implying mandatory C4/DFD tags at BRD.
- Add transition note at overview:
  - `BRD Diagram Enforcement Mode: advisory`
  - `PRD Diagram Enforcement Mode: blocking`

3) `ai_dev_ssd_flow/01_BRD/BRD_MVP_QUALITY_GATE_VALIDATION.md`
- In `CORPUS-06: Visualization Coverage`:
  - Change intent from “contract required” to “advisory visibility”.
  - Keep outputs as INFO only.
  - Add explicit pointer: “Blocking checks live in PRD CORPUS-06 and PRD validator codes PRD-E023..PRD-E026”.

## 5.2 Layer-2 (PRD) Rules/Templates

4) `ai_dev_ssd_flow/02_PRD/PRD-MVP-TEMPLATE.md`
- In `9.4 Required Diagram Contract (MVP)`:
  - Keep mandatory status.
  - Add explicit minimal acceptance:
    - one `c4-l2`
    - one `dfd-l1`
    - one `sequence-*` with alternate/error branch
    - intent header keys (`diagram_type`, `level`, `scope_boundary`, `upstream_refs`, `downstream_refs`)

5) `ai_dev_ssd_flow/02_PRD/PRD_MVP_VALIDATION_RULES.md`
- Add dedicated PRD diagram checks section (new check group after structural checks):
  - `CHECK D1`: missing `@diagram: c4-l2` (error)
  - `CHECK D2`: missing `@diagram: dfd-l1` (error)
  - `CHECK D3`: missing `@diagram: sequence-*` (error)
  - `CHECK D4`: sequence exists but no exception/alternate path (error)
  - `CHECK D5`: missing intent header fields (warning)
- Add scoring impact statement:
  - Diagram noncompliance reduces EARS-Ready and SYS-Ready contribution in architecture/readiness component.

6) `ai_dev_ssd_flow/02_PRD/PRD_MVP_QUALITY_GATE_VALIDATION.md`
- In `CORPUS-06: Visualization Coverage`:
  - Upgrade from INFO-only guidance to blocking gate language.
  - Add pass criteria table with explicit fail conditions tied to PRD-E023..PRD-E026.

## 5.3 Skill Files (Framework)

7) `.claude/skills/doc-brd/SKILL.md`
- Downgrade BRD diagram contract from mandatory to advisory.
- Keep BRD examples for business communication only.

8) `.claude/skills/doc-brd-validator/SKILL.md`
- Reclassify BRD diagram findings:
  - `BRD-E022/E023/E024` -> warnings (or deprecate and replace with BRD-W011/W012/W013).
- Add migration note: canonical enforcement moved to `doc-prd-validator`.

9) `.claude/skills/doc-brd-reviewer/SKILL.md`
- Reclassify `REV-DC001/002` from Error -> Warning for BRD only.
- Keep `REV-DC003/004` as warning/info.
- Add text: “Do not block BRD on diagram contract in transition mode.”

10) `.claude/skills/doc-brd-fixer/SKILL.md`
- Keep fix rules for REV-DC codes but mark phase as optional remediation.
- Do not auto-upgrade missing BRD diagrams as blocking fix.

11) `.claude/skills/doc-brd-audit/SKILL.md`
- Update combined gate logic:
  - BRD diagram findings recorded but non-blocking.
  - Final pass/fail should ignore BRD diagram misses by default.
  - Optional strict behavior only if explicit audit flag is introduced (`audit_strict_diagrams: true`).

12) `.claude/skills/doc-prd/SKILL.md`
- Add explicit “PRD Diagram Contract (MANDATORY)” block aligned with PRD template and DIAGRAM_STANDARDS.

13) `.claude/skills/doc-prd-validator/SKILL.md`
- Add explicit error-code documentation for PRD diagram contract (see mapping section).
- Update workflow step order to include diagram checks before final score validation.

14) `.claude/skills/doc-prd-reviewer/SKILL.md`
- Keep `REV-DC001..003` as blocking in PRD reviewer outcome.
- Add strict statement that missing sequence exception path is fail condition.

15) `.claude/skills/doc-prd-fixer/SKILL.md`
- Add missing REV-DC mapping table:
  - `REV-DC001`: add missing tags (`c4-l2`,`dfd-l1`,`sequence-*`)
  - `REV-DC002`: patch sequence diagram with error/alternate branch
  - `REV-DC003`: add missing intent header keys
- Add minimal-edit rule (avoid changing non-diagram sections).

16) `.claude/skills/doc-prd-autopilot/SKILL.md`
- Add Phase-4 quality gate item:
  - “Fail generation if PRD-E023..PRD-E026 present”.
- Add report block “Diagram Contract Compliance: PASS/FAIL”.

## 5.4 Runtime Validator Script Changes

17) `ai_dev_ssd_flow/01_BRD/scripts/validate_brd.py`
- Function: `validate_diagram_contract(content, result)`
- Replace current behavior:
  - From: all misses reported as `BRD-W001`
  - To: advisory-only dedicated warnings:
    - `BRD-W011`: missing `@diagram: c4-l1`
    - `BRD-W012`: missing `@diagram: dfd-l0`
    - `BRD-W013`: sequence diagram found without `@diagram: sequence-*`
    - `BRD-W014`: missing intent header fields
- Do not raise errors from BRD diagram checks.

18) `ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py`
- Function: `validate_diagram_contract(content, result)`
- Replace current behavior:
  - From: all misses reported as `PRD-W001`
  - To: blocking error family + one warning:
    - `PRD-E023`: missing `@diagram: c4-l2`
    - `PRD-E024`: missing `@diagram: dfd-l1`
    - `PRD-E025`: missing `@diagram: sequence-*`
    - `PRD-E026`: sequence diagram lacks explicit alternate/error path
    - `PRD-W011`: missing diagram intent header fields
- Ensure sequence-path check parses `alt/else` branches in Mermaid `sequenceDiagram` blocks.

19) `ai_dev_ssd_flow/scripts/error_codes.py`
- Add/normalize codes in centralized registry:
  - BRD advisory codes: `BRD-W011..BRD-W014`
  - PRD blocking diagram codes: `PRD-E023..PRD-E026`
  - PRD intent warning: `PRD-W011`
- Preserve existing meanings of legacy codes; do not reassign previously documented semantics.

20) `ai_dev_ssd_flow/01_BRD/BRD_MVP_SCHEMA.yaml`
- Extend `error_messages` map with `BRD-W011..BRD-W014`.
- Keep BRD diagram checks explicitly non-blocking in schema guidance.

21) `ai_dev_ssd_flow/02_PRD/PRD_MVP_SCHEMA.yaml`
- Extend `error_messages` map with `PRD-E023..PRD-E026` and `PRD-W011`.
- Add note that PRD diagram contract failures are blocking in transition target mode.

22) Validator wiring for compatibility switch
- `validate_brd.py`: read `custom_fields.diagram_enforcement_origin` from frontmatter.
  - `brd`: legacy behavior (retain existing BRD diagram checks)
  - `prd` (default): advisory-only BRD diagram checks
- `validate_prd.py`: read same switch.
  - `brd`: PRD diagram checks warning-only (legacy)
  - `prd` (default): PRD diagram checks blocking (`PRD-E023..026`)
- If field missing/invalid, default to `prd` and emit one info/warning note.

## 6) Validation Code Mapping (Old → New)

| Domain | Old Code | New Code | Severity | Action |
|---|---|---|---|---|
| BRD script | `BRD-W001` (diagram missing) | `BRD-W011` | Warning | Advisory only |
| BRD script | `BRD-W001` (diagram missing) | `BRD-W012` | Warning | Advisory only |
| BRD script | `BRD-W001` (sequence tag missing) | `BRD-W013` | Warning | Advisory only |
| BRD script | `BRD-W001` (intent missing) | `BRD-W014` | Warning | Advisory only |
| PRD script | `PRD-W001` (missing c4-l2) | `PRD-E023` | Error | Blocking |
| PRD script | `PRD-W001` (missing dfd-l1) | `PRD-E024` | Error | Blocking |
| PRD script | `PRD-W001` (missing sequence-*) | `PRD-E025` | Error | Blocking |
| PRD script | N/A | `PRD-E026` | Error | Blocking |
| PRD script | `PRD-W001` (intent missing) | `PRD-W011` | Warning | Non-blocking |
| BRD reviewer | `REV-DC001` | `REV-DC001` | Warning (changed) | Non-blocking |
| BRD reviewer | `REV-DC002` | `REV-DC002` | Warning (changed) | Non-blocking |
| PRD reviewer | `REV-DC001` | `REV-DC001` | Error | Blocking |
| PRD reviewer | `REV-DC002` | `REV-DC002` | Error | Blocking |
| PRD reviewer | `REV-DC003` | `REV-DC003` | Warning | Non-blocking |

### 6.1 Code Allocation Guardrail (No-Collision Rule)

- Do not reuse any existing `PRD-W00x` code for new diagram semantics.
- Reserve transition additions in this plan as:
  - BRD advisory: `BRD-W011`, `BRD-W012`, `BRD-W013`, `BRD-W014`
  - PRD blocking: `PRD-E023`, `PRD-E024`, `PRD-E025`, `PRD-E026`
  - PRD advisory: `PRD-W011`
- Update all three layers together in one patch set:
  1. validator script emission
  2. centralized error registry
  3. schema `error_messages` catalogs

## 7) Safe Transition Controls

### 7.1 Compatibility Window

Add temporary frontmatter switch (default = transition-safe):

```yaml
custom_fields:
  diagram_enforcement_origin: prd   # values: brd | prd
```

Behavior:
- `brd`: legacy mode (old behavior, temporary use only)
- `prd`: new behavior (target default)

Implementation requirement:
- Enforce this switch in both runtime validators and document it in both validator skills.

### 7.2 Non-Breaking Rollout Order

1. Update rules/templates first.
2. Update skill docs and reviewer/fixer mappings.
3. Update validator scripts and error code docs.
4. Run corpus validation in dry-run mode and compare pass/fail delta.
5. Flip default origin to `prd`.
6. Remove legacy `brd` mode after one release cycle.

### 7.3 Regression Guardrail

Add two smoke checks to CI:
- BRD missing C4/DFD should return warnings only.
- PRD missing C4/DFD/sequence should return errors and fail.

Add two additional smoke checks:
- PRD sequence diagram without `alt/else` branch should fail `PRD-E026`.
- PRD missing diagram intent keys should warn `PRD-W011` but not fail.

Fixture requirement:
- Create explicit test fixtures under `ai_dev_ssd_flow/tmp/diagram_transition_fixtures/` for reproducible checks.

## 8) Acceptance Criteria

- BRD validators/reviewers no longer block on missing diagram contract.
- PRD validators/reviewers block on missing `c4-l2`, `dfd-l1`, `sequence-*`, and missing sequence exception branch.
- PRD fixer can remediate REV-DC findings.
- BRD PRD-Ready score no longer includes diagram deductions.
- PRD readiness scoring includes diagram compliance contribution.
- Error codes emitted by scripts match centralized registry and schema catalogs with no collisions.
- Compatibility switch (`diagram_enforcement_origin`) changes behavior deterministically in both validators.

## 9) Execution Checklist (Operator)

```bash
# 1) Update docs/skills per Sections 5.1-5.3
# 2) Update validators + centralized registry + schema catalogs
# 3) Validate syntax on targeted fixtures (avoid whole-folder noise)
python3 ai_dev_ssd_flow/01_BRD/scripts/validate_brd.py ai_dev_ssd_flow/tmp/diagram_transition_fixtures/BRD-no-diagrams.md --verbose
python3 ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py ai_dev_ssd_flow/tmp/diagram_transition_fixtures/PRD-missing-c4.md --verbose
python3 ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py ai_dev_ssd_flow/tmp/diagram_transition_fixtures/PRD-missing-sequence.md --verbose
python3 ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py ai_dev_ssd_flow/tmp/diagram_transition_fixtures/PRD-seq-no-alt.md --verbose
python3 ai_dev_ssd_flow/02_PRD/scripts/validate_prd.py ai_dev_ssd_flow/tmp/diagram_transition_fixtures/PRD-missing-intent.md --verbose
```

## 10) Implementation Caveats

- BRD `PRD-Ready` deduction model currently focuses on contamination/structure dimensions; diagram deductions are documentation-level, not enforced in `validate_brd.py` runtime logic.
- Therefore, BRD scoring update is primarily rules/documentation alignment unless additional BRD scoring code is introduced.

## 11) Notes

- This plan is framework-only and does not modify project artifacts.
- Use `IPLAN-009` as the implementation reference in follow-up patch sessions.
