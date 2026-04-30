# PLAN-034: Governance Migration to SDD v3.2

**Date**: 2026-04-30
**Status**: Draft
**Priority**: High
**Scope**: `/opt/data/ucx_framework/governance` -> align with `/opt/data/ucx_framework/ucx_flow_v3`

## Objective

Migrate governance documentation, templates, and governance-side automation references from legacy SDD (`ai_dev_ssd_flow`, TASKS/TSPEC/SYS/REQ/CTR-centric flows) to SDD v3.2 (`ucx_flow_v3`, BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code).

## Review Findings (Current State)

The governance directory currently contains mixed versions (v3 references and legacy references). Migration requires consistency updates across core docs, bridge docs, setup docs, templates, and selected scripts.

### Critical Gaps

1. **Core governance model mismatch**
   - `governance/README.md`, `governance/GOVERNANCE_RULES.md`, `governance/SDD_DEPTH_GUIDE.md`, `governance/AI_ISSUE_LIFECYCLE.md` still describe TASKS-based and 15-layer flows.

2. **Bridge documents are version-inconsistent**
   - `governance/TASKS_IPLAN_BRIDGE.md` uses TASKS Layer 11 as central bridge.
   - `governance/TSPEC_BDD_QA_BRIDGE.md` uses TSPEC Layer 10 structures and `test_registry.yaml` mapping.
   - `governance/CHG_GOVERNANCE_BRIDGE.md` uses gate mapping tied to legacy layer numbering.

3. **Path drift to old framework root**
   - Multiple files still reference `ai_dev_ssd_flow/...` paths instead of `ucx_flow_v3/...`.

4. **Workflow and script references not v3-normalized**
   - Governance docs and script guidance still assume TASKS-generated issue flow and old layer aliases.

## Target Governance Baseline (v3.2)

- Canonical chain: `BRD -> PRD -> EARS -> BDD -> ADR -> SPEC -> TDD -> IPLAN -> Code`
- Canonical registry: `ucx_flow_v3/LAYER_REGISTRY.yaml`
- Canonical governance core: `ucx_flow_v3/DOC_GOVERNANCE_CORE.md`
- CHG overlay: `ucx_flow_v3/CHG/` with gates `GATE-01`, `GATE-03`, `GATE-06`, `GATE-08`, `GATE-CODE`
- YAML-first policy for SDD artifacts; Markdown in governance remains allowed for process guidance and runbooks

## Migration Workstreams

### Workstream 1: Core Governance Documentation Alignment

Update foundational governance documents to v3.2 chain and terminology.

**Files**:
- `governance/README.md`
- `governance/GOVERNANCE_RULES.md`
- `governance/SDD_DEPTH_GUIDE.md`
- `governance/AI_ISSUE_LIFECYCLE.md`

**Required changes**:
- Replace legacy layer tables with v3 layer map.
- Remove SYS/REQ/CTR/TSPEC/TASKS as active layers.
- Replace TASKS-generated issue flow language with IPLAN-driven execution planning language.
- Update all framework root links from `ai_dev_ssd_flow` to `ucx_flow_v3`.
- Keep governance workflow labels and GitHub board flow intact unless they depend on removed artifacts.

### Workstream 2: Bridge Document Refactor

Refactor bridge documentation so governance-to-SDD integration uses v3 artifacts only.

**Files**:
- `governance/TASKS_IPLAN_BRIDGE.md` (rewrite to v3 bridge semantics)
- `governance/TSPEC_BDD_QA_BRIDGE.md` (replace TSPEC model with TDD+BDD-to-QA mapping)
- `governance/CHG_GOVERNANCE_BRIDGE.md` (update to v3 CHG gate model)

**Required changes**:
- Replace TASKS references with TDD/IPLAN execution contracts.
- Replace TSPEC registry examples with TDD test case mapping references.
- Re-map CHG gates to v3 gate names and layer ranges.

### Workstream 3: Setup and Template Surface Update

Normalize onboarding and template docs that propagate governance guidance into downstream repositories.

**Primary files**:
- `governance/setup/SETUP_GUIDE.md`
- `governance/setup/CONFIG.md`
- `governance/templates/sdd_config.yaml`
- `governance/templates/README_AIAGENT.md`
- `governance/plans/IPLAN-TEMPLATE.md`

**Required changes**:
- Ensure generated defaults point to `ucx_flow_v3`.
- Update example layer chains and references to TDD/IPLAN.
- Remove stale TASKS/TSPEC/SYS/REQ/CTR defaults from template text and comments.

### Workstream 4: Governance Script/Workflow Reference Cleanup

Review governance-side scripts and workflow docs for obsolete artifact references.

**Primary files**:
- `governance/github/GITHUB_WORKFLOWS.md`
- `governance/github/WORKFLOW_INTEGRATION.md`
- `governance/scripts/workflows/sync_tasks_from_issues.py`
- `governance/scripts/workflows/execute_qa_tests.py`
- `governance/scripts/apply_doc_path_aliases.py`

**Required changes**:
- If scripts are still required, migrate naming and path conventions to v3.
- If scripts are legacy-only, mark explicitly deprecated and remove from active runbooks.
- Ensure workflow docs do not prescribe removed layers or removed template paths.

### Workstream 5: Deprecation and Compatibility Policy

Introduce explicit migration semantics for legacy references.

**Actions**:
- Mark legacy terms and files as `Deprecated` where retained for transition.
- Add a compatibility note defining what remains supported during migration.
- Add a hard cutoff criterion for removal of legacy aliases.

## Acceptance Criteria

1. No governance docs in active guidance reference `ai_dev_ssd_flow/`.
2. No active governance flow describes SYS/REQ/CTR/TSPEC/TASKS as required layers.
3. All core governance docs present the v3 chain exactly as `BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`.
4. Bridge docs map QA and CHG to v3 artifacts and v3 gate names.
5. Setup/templates propagate v3 defaults for new project scaffolds.
6. Legacy-only scripts/docs are either migrated or clearly marked deprecated.
7. Validation scan passes with zero matches for legacy framework root in active files.

## Validation Procedure

Run these checks after edits:

```bash
rg "ai_dev_ssd_flow" governance/
rg "\bSYS\b|\bREQ\b|\bCTR\b|\bTSPEC\b|\bTASKS\b" governance/*.md governance/**/*.md
rg "BRD.*PRD.*EARS.*BDD.*ADR.*SPEC.*TDD.*IPLAN" governance/README.md governance/GOVERNANCE_RULES.md governance/SDD_DEPTH_GUIDE.md governance/AI_ISSUE_LIFECYCLE.md
```

Interpretation:
- First query: zero matches in active docs (deprecated docs may be excluded by path policy).
- Second query: matches only where terms are explicitly labeled deprecated or historical.
- Third query: required v3 chain present in all four core docs.

## Risks and Failure Modes

| Risk | Failure Mode | Mitigation |
|------|--------------|------------|
| Partial migration | Mixed guidance causes conflicting execution patterns | Enforce Workstream 1 before any release |
| Script drift | Automation expects legacy IDs/paths | Add migration wrappers or deprecation notes per script |
| Bridge regression | QA and CHG procedures lose traceability links | Validate bridge docs against `LAYER_REGISTRY.yaml` and CHG gate docs |
| Template propagation lag | New repos are scaffolded with legacy defaults | Prioritize Workstream 3 before rollout |

## Complexity and Resource Impact

- **Implementation complexity**: 4/5 (cross-document semantic migration with process coupling)
- **Primary resources**: documentation edits, workflow reference verification, regex-based consistency checks
- **Operational constraints**: preserve existing approved governance policies not related to SDD layer model

## Execution Order

1. Workstream 1 (core docs)
2. Workstream 2 (bridge docs)
3. Workstream 3 (setup/templates)
4. Workstream 4 (scripts/workflow references)
5. Workstream 5 (deprecation policy and final validation)

## Dependencies

- `ucx_flow_v3/README.md`
- `ucx_flow_v3/LAYER_REGISTRY.yaml`
- `ucx_flow_v3/DOC_GOVERNANCE_CORE.md`
- `ucx_flow_v3/QUICK_REFERENCE.md`
- Existing readiness context in `plans/PLAN-033_mcp_ucx_v3_readiness.md`

## Gap Closure Addendum

This addendum closes gaps identified during plan review.

### A. Expanded Migration Inventory

In addition to files already listed in Workstreams 1-4, include the following:

- `governance/templates/sdd_config.yaml` (legacy layer numbers and TASKS/TSPEC/SYS/REQ/CTR defaults)
- `governance/github/LABEL_REGISTRY.yaml` (`source:sdd` description still TASKS-specific)
- `governance/setup/PRECOMMIT_HOOK_LIBRARY_CONSUMER_GUIDE.md` (legacy framework path references)
- `governance/templates/pre-commit-config.framework-library.yaml` (legacy script entry paths)
- `governance/templates/qa/01-testing-strategy.md` (TSPEC guide path)
- `governance/scripts/setup_project_hybrid.sh` (legacy path/alias assumptions if present)
- `governance/scripts/setup-ai-pr-review-labels.sh` (legacy SDD wording if present)

### B. Active vs Deprecated Policy (Explicit)

Define artifact status before edits:

- **Active**: all files under `governance/` except files placed in an explicit `deprecated/` path or marked with a frontmatter/status header containing `Deprecated`.
- **Deprecated**: files retained only for transition, must include a deprecation banner with replacement path and removal milestone.
- **Validation rule**: zero legacy root/path references allowed in Active files.

### C. TASKS Sync Tooling Decision (Required)

Resolve one path for `sync_tasks_from_issues.py` and related workflow docs:

1. **Migrate** to IPLAN/TDD-aware sync logic and rename workflow/script accordingly, or
2. **Deprecate** as legacy and remove from active governance runbooks.

No partial state is allowed in final migration acceptance.

### D. Label Registry Normalization

Update `governance/github/LABEL_REGISTRY.yaml` source label text to remove TASKS dependency.

- Current: `Issue generated from SDD TASKS`
- Target: `Issue generated from SDD artifacts (v3 chain)`

### E. Pre-commit and Setup Path Normalization

Normalize framework path references in setup and pre-commit templates from `ai_dev_ssd_flow` to `ucx_flow_v3` where applicable. If a legacy path must remain for compatibility, mark it deprecated and document removal criteria.

### F. Expanded Validation Gates

Replace the narrow validation procedure with multi-surface checks:

```bash
rg "ai_dev_ssd_flow" governance/
rg "\bSYS\b|\bREQ\b|\bCTR\b|\bTSPEC\b|\bTASKS\b" governance/ --glob "*.md" --glob "*.yaml" --glob "*.yml"
rg "BRD.*PRD.*EARS.*BDD.*ADR.*SPEC.*TDD.*IPLAN" governance/README.md governance/GOVERNANCE_RULES.md governance/SDD_DEPTH_GUIDE.md governance/AI_ISSUE_LIFECYCLE.md
rg "sync[-_]tasks|tasks_to_github" governance/github governance/scripts governance/setup governance/templates
```

Interpretation:

- Query 1: zero matches in Active files.
- Query 2: matches only in explicitly Deprecated content.
- Query 3: required v3 chain present in all 4 core docs.
- Query 4: all TASKS-sync references are either migrated to v3 equivalents or explicitly deprecated.

### G. Operational Verification Gate

Add a migration completion gate requiring runbook and script operability checks:

- Verify governance docs no longer direct users to removed layer artifacts.
- Verify referenced scripts still exist and match documented names.
- Verify any retained compatibility aliases are documented in deprecation notes.

### H. Changelog and Roadmap Update

After migration completion:

- Add a release-scoped changelog entry under `changelog/` for governance v3 migration.
- Update `roadmap/ROADMAP.md` with migration milestone completion and any deferred legacy cleanup milestone.

## Revised Acceptance Criteria (Supersedes Prior Section)

1. Zero `ai_dev_ssd_flow` references in Active governance files.
2. No Active governance artifact treats SYS/REQ/CTR/TSPEC/TASKS as required layers.
3. `README`, `GOVERNANCE_RULES`, `SDD_DEPTH_GUIDE`, and `AI_ISSUE_LIFECYCLE` all include the v3 chain `BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`.
4. Bridge docs (`TASKS_IPLAN_BRIDGE`, `TSPEC_BDD_QA_BRIDGE`, `CHG_GOVERNANCE_BRIDGE`) are rewritten to v3 semantics and gate names.
5. Setup/template/config files (`setup/`, `templates/`, `github/LABEL_REGISTRY.yaml`) propagate v3 defaults and wording.
6. TASKS sync workflow/script references are fully migrated or explicitly deprecated with banner and replacement.
7. Expanded validation gates (Section F) pass.
8. Operational verification gate (Section G) passes.
9. Changelog and roadmap updates are completed (Section H).
