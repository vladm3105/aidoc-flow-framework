# PLAN-014 Executable Checklist

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

**Status**: Not Started
**Plan**: [PLAN-014_3segment_element_id_migration.md](./PLAN-014_3segment_element_id_migration.md)

---

## Phase 1: Standards Authority

- [ ] `ucx_flow_v3/ID_NAMING_STANDARDS.md` — replace 4-segment with 3-segment format
- [ ] `ucx_flow_v3/ID_NAMING_STANDARDS.md` — update regex to `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$`
- [ ] `ucx_flow_v3/ID_NAMING_STANDARDS.md` — deprecate element type code table (01-99)
- [ ] `ucx_flow_v3/ID_NAMING_STANDARDS.md` — remove Section-to-Element-Code Mapping
- [ ] `ucx_flow_v3/ID_NAMING_STANDARDS.md` — update all examples to 3-segment
- [ ] `ucx_flow_v3/VALIDATION_STANDARDS.md` — update IDPAT-E002, IDPAT-E003, IDPAT-W001
- [ ] `ucx_flow_v3/VALIDATION_STANDARDS.md` — deprecate ELEM-E001/W001
- [ ] `ucx_flow_v3/LAYER_REGISTRY.yaml` — update `id_patterns.element` regex

## Phase 1.5: Archive AUTOPILOT

- [ ] Move `ucx_flow_v3/AUTOPILOT/` → `ucx_flow_v3/archived/AUTOPILOT_v1_archive/`

## Phase 2a: Primary Templates (11 files)

- [ ] `mcp_ucx/templates/BRD-TEMPLATE.yaml` — format → `{doc_type}.{doc_id}.{hash}`, update examples
- [ ] `mcp_ucx/templates/PRD-TEMPLATE.yaml` — same
- [ ] `mcp_ucx/templates/EARS-TEMPLATE.yaml` — same
- [ ] `mcp_ucx/templates/BDD-TEMPLATE.yaml` — same
- [ ] `mcp_ucx/templates/ADR-TEMPLATE.yaml` — same
- [ ] `mcp_ucx/templates/SYS-TEMPLATE.yaml` — same
- [ ] `mcp_ucx/templates/REQ-TEMPLATE.yaml` — same
- [ ] `mcp_ucx/templates/CTR-TEMPLATE.yaml` — same
- [ ] `mcp_ucx/templates/SPEC-TEMPLATE.yaml` — same + update `element_ids:` section
- [ ] `mcp_ucx/templates/TSPEC-TEMPLATE.yaml` — same
- [ ] `mcp_ucx/templates/TASKS-TEMPLATE.yaml` — same
- [ ] Fix any non-hex hash examples (e.g., `g7k2` → valid hex like `a7f3`)

## Phase 2b: Mirror Templates (11 files)

- [ ] Copy `mcp_ucx/templates/BRD-TEMPLATE.yaml` → `ucx_flow_v3/01_BRD/`
- [ ] Copy `mcp_ucx/templates/PRD-TEMPLATE.yaml` → `ucx_flow_v3/02_PRD/`
- [ ] Copy `mcp_ucx/templates/EARS-TEMPLATE.yaml` → `ucx_flow_v3/03_EARS/`
- [ ] Copy `mcp_ucx/templates/BDD-TEMPLATE.yaml` → `ucx_flow_v3/04_BDD/`
- [ ] Copy `mcp_ucx/templates/ADR-TEMPLATE.yaml` → `ucx_flow_v3/05_ADR/`
- [ ] Copy `mcp_ucx/templates/SYS-TEMPLATE.yaml` → `ucx_flow_v3/06_SYS/`
- [ ] Copy `mcp_ucx/templates/REQ-TEMPLATE.yaml` → `ucx_flow_v3/07_REQ/`
- [ ] Copy `mcp_ucx/templates/CTR-TEMPLATE.yaml` → `ucx_flow_v3/08_CTR/`
- [ ] Copy `mcp_ucx/templates/SPEC-TEMPLATE.yaml` → `ucx_flow_v3/09_SPEC/`
- [ ] Copy `mcp_ucx/templates/TSPEC-TEMPLATE.yaml` → `ucx_flow_v3/10_TSPEC/`
- [ ] Copy `mcp_ucx/templates/TASKS-TEMPLATE.yaml` → `ucx_flow_v3/11_TASKS/`

## Phase 2c: Layer READMEs (11 files)

- [ ] `ucx_flow_v3/01_BRD/README.md` — update element ID examples
- [ ] `ucx_flow_v3/02_PRD/README.md` — same
- [ ] `ucx_flow_v3/03_EARS/README.md` — same
- [ ] `ucx_flow_v3/04_BDD/README.md` — same
- [ ] `ucx_flow_v3/05_ADR/README.md` — same
- [ ] `ucx_flow_v3/06_SYS/README.md` — same
- [ ] `ucx_flow_v3/07_REQ/README.md` — same
- [ ] `ucx_flow_v3/08_CTR/README.md` — same
- [ ] `ucx_flow_v3/09_SPEC/README.md` — same
- [ ] `ucx_flow_v3/10_TSPEC/README.md` — same
- [ ] `ucx_flow_v3/11_TASKS/README.md` — same

## Phase 3: SPEC Subtype Files (16 files)

### Schema + template files

- [ ] `09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml` — `element_id_format` → 3-segment
- [ ] `09_SPEC/CSPEC/CSPEC-MVP-TEMPLATE.yaml` — update ID examples
- [ ] `09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml` — same
- [ ] `09_SPEC/DSPEC/DSPEC-MVP-TEMPLATE.yaml` — same
- [ ] `09_SPEC/UXSPEC/UXSPEC_MVP_SCHEMA.yaml` — same
- [ ] `09_SPEC/UXSPEC/UXSPEC-MVP-TEMPLATE.yaml` — same
- [ ] `09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml` — same
- [ ] `09_SPEC/RISKSPEC/RISKSPEC-MVP-TEMPLATE.yaml` — same
- [ ] `09_SPEC/PROCSPEC/PROCSPEC_MVP_SCHEMA.yaml` — same
- [ ] `09_SPEC/PROCSPEC/PROCSPEC-MVP-TEMPLATE.yaml` — same

### Index + creation rules files

- [ ] `09_SPEC/PROCSPEC/PROCSPEC-00_index.md` — update ID examples
- [ ] `09_SPEC/PROCSPEC/PROCSPEC_MVP_CREATION_RULES.md` — update ID format
- [ ] `09_SPEC/RISKSPEC/RISKSPEC-00_index.md` — same
- [ ] `09_SPEC/RISKSPEC/RISKSPEC_MVP_CREATION_RULES.md` — same
- [ ] `09_SPEC/UXSPEC/UXSPEC-00_index.md` — same
- [ ] `09_SPEC/UXSPEC/UXSPEC_MVP_CREATION_RULES.md` — same

## Phase 4: mcp_ucx Prompt Templates (11 files)

### Creation prompts

- [ ] `mcp_ucx/prompts/templates/creation/UCC_PROMPT_BRD.md` — update ID format
- [ ] `mcp_ucx/prompts/templates/creation/UCC_PROMPT_PRD.md` — **HIGH**: remove "4-segment" instruction
- [ ] `mcp_ucx/prompts/templates/creation/UCC_PROMPT_EARS.md` — update ID examples
- [ ] `mcp_ucx/prompts/templates/creation/UCC_PROMPT_BDD.md` — update ID examples
- [ ] `mcp_ucx/prompts/templates/creation/UCC_PROMPT_TSPEC.md` — update ID examples
- [ ] `mcp_ucx/prompts/templates/creation/UCC_OUTPUT_SCHEMA.md` — update output format

### Review prompts

- [ ] `mcp_ucx/prompts/templates/review/UCR_PROMPT_BRD.md` — update ID refs

### Remediation prompts

- [ ] `mcp_ucx/prompts/templates/remediation/UCRem_PROMPT_BRD.md` — update ID refs
- [ ] `mcp_ucx/prompts/templates/remediation/UCRem_PROMPT_PRD.md` — update ID refs
- [ ] `mcp_ucx/prompts/templates/remediation/UCRem_PROMPT_EARS.md` — update ID refs
- [ ] `mcp_ucx/prompts/templates/remediation/UCRem_PROMPT_ADR.md` — update ID refs

## Phase 5: Framework Documentation (~26 files)

- [ ] `ucx_flow_v3/README.md` — element ID table, examples
- [ ] `ucx_flow_v3/QUICK_REFERENCE.md` — element format row
- [ ] `ucx_flow_v3/TRACEABILITY.md` — tag format, cross-ref examples
- [ ] `ucx_flow_v3/METADATA_TAGGING_GUIDE.md` — dot notation
- [ ] `ucx_flow_v3/COMPLETE_TAGGING_EXAMPLE.md` — usage examples
- [ ] `ucx_flow_v3/CUMULATIVE_TAG_REFERENCE.md` — validation logic
- [ ] `ucx_flow_v3/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` — `@artifact-type` format
- [ ] `ucx_flow_v3/AI_ASSISTANT_RULES.md` — XDOC-006, examples
- [ ] `ucx_flow_v3/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md` — feature ID format
- [ ] `ucx_flow_v3/TRACEABILITY_SETUP.md` — format references
- [ ] `ucx_flow_v3/TESTING_STRATEGY_TDD.md` — 9x `BRD.01.01.01`
- [ ] `ucx_flow_v3/METADATA_VS_TRACEABILITY.md` — 6 mixed IDs
- [ ] `ucx_flow_v3/THRESHOLD_NAMING_RULES.md` — `@threshold:` format
- [ ] `ucx_flow_v3/01_BRD/BRD-00_GLOSSARY.md` — 1 ID ref
- [ ] `ucx_flow_v3/METADATA_CORE_MATRIX.md` — check for ID refs
- [ ] `ucx_flow_v3/AI_TOOL_OPTIMIZATION_GUIDE.md` — 1 ID ref
- [ ] `ucx_flow_v3/PROJECT_SETUP_GUIDE.md` — 1 ID ref
- [ ] `ucx_flow_v3/PROJECT/PROJECT_MODEL.md` — 23 ID refs
- [ ] `ucx_flow_v3/FINANCIAL_DOMAIN_CONFIG.md` — 9 ID refs
- [ ] `ucx_flow_v3/10_TSPEC/TSPEC-00_index.md` — 6 ID refs
- [ ] `ucx_flow_v3/09_SPEC/CSPEC/CSPEC-00_index.md` — 5 ID refs
- [ ] `ucx_flow_v3/09_SPEC/CSPEC/CSPEC_MVP_CREATION_RULES.md` — 5 ID refs
- [ ] `ucx_flow_v3/05_ADR/ADR-00_ai_powered_documentation_assistant_architecture.md` — 5 ID refs
- [ ] `ucx_flow_v3/09_SPEC/DSPEC/DSPEC-00_index.md` — 4 ID refs
- [ ] `ucx_flow_v3/09_SPEC/DSPEC/DSPEC_MVP_CREATION_RULES.md` — 4 ID refs
- [ ] `ucx_flow_v3/MVP_WORKFLOW_GUIDE.md` — check for ID refs

## Phase 6: Claude Code Skills (~41 files)

### High priority

- [ ] `.claude/skills/doc-naming/SKILL.md` (24 occurrences)
- [ ] `.claude/skills/doc-naming_quickref.md` (20 occurrences)
- [ ] `.claude/skills/doc-brd/SKILL.md`
- [ ] `.claude/skills/doc-brd-autopilot/SKILL.md`
- [ ] `.claude/skills/doc-spec/SKILL.md`
- [ ] `.claude/skills/doc-spec-autopilot/SKILL.md`
- [ ] `.claude/skills/doc-tasks/SKILL.md`
- [ ] `.claude/skills/doc-tasks-autopilot/SKILL.md`
- [ ] `.claude/skills/doc-sys/SKILL.md`
- [ ] `.claude/skills/doc-sys-autopilot/SKILL.md`
- [ ] `.claude/skills/doc-tspec/SKILL.md`
- [ ] `.claude/skills/doc-tspec-autopilot/SKILL.md`
- [ ] `.claude/skills/doc-ctr/SKILL.md`

### Medium priority

- [ ] `.claude/skills/trace-check/SKILL.md`
- [ ] `.claude/skills/doc-flow/SKILL.md`
- [ ] `.claude/skills/doc-flow/SHARED_CONTENT.md`
- [ ] `.claude/skills/doc-req/SKILL.md`
- [ ] `.claude/skills/doc-req-autopilot/SKILL.md`
- [ ] `.claude/skills/doc-adr/SKILL.md`
- [ ] `.claude/skills/doc-adr-autopilot/SKILL.md`

### Agents

- [ ] `.claude/agents/requirements-analyst.md` — 9 occurrences

### All remaining doc-* skills

- [ ] Batch grep + replace across all remaining `.claude/skills/*/SKILL.md` files

## Phase 7: mcp_ucx Persona Skills

- [ ] Check `mcp_ucx/skills/personas/*.md` (14 files) — update if any ID format refs

## Phase 8: mcp_ucx Source & Tests

- [ ] `mcp_ucx/src/mcp_server/validation/runner.py` — update element ID regex if present
- [ ] `mcp_ucx/src/mcp_server/tool_registry.py` — check for ID format refs
- [ ] `mcp_ucx/tests/unit/test_auth_example.py` — update `@brd: BRD.01.01.01` → 3-segment
- [ ] Grep all test files for remaining 4-segment patterns

## Phase 9: Governance & Root Docs

- [ ] `README.md` (root) — update element ID format
- [ ] `README_AIAGENT.md` — check for ID format refs
- [ ] Grep `governance/` for element ID references

## Phase 10: Changelog & Roadmap

### SDD Framework

- [ ] Verify `ucx_flow_v3/README.md` uses 3-segment (updated Phase 5)
- [ ] Verify `README.md` (root) uses 3-segment (updated Phase 9)
- [ ] CREATE `changelog/CHANGELOG_v0.13.0.md`
- [ ] UPDATE `roadmap/ROADMAP.md` — v0.12.1 → v0.13.0

### mcp_ucx Documentation

- [ ] UPDATE `mcp_ucx/docs/README.md` — add v1.6.0 changelog entry
- [ ] Check `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md` for ID examples
- [ ] Check `mcp_ucx/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md` for ID format
- [ ] Check `mcp_ucx/skills/README.md` for ID format refs

### mcp_ucx Changelog & Roadmap

- [ ] UPDATE `mcp_ucx/docs/ROADMAP.md` — v1.5.0 → v1.6.0
- [ ] CREATE `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.6.0.md`

## Phase 11: Final Review

- [ ] Run: `grep -rP '[A-Z]{2,8}\.\d{2,}\.\d{2,}\.[0-9a-f]{2,}' ucx_flow_v3/ mcp_ucx/ .claude/ --include='*.md' --include='*.yaml' | grep -v archive | grep -v v1_archive` → 0 matches
- [ ] Validate all 11 template YAML files: `python -c "import yaml; ..."`
- [ ] Run `python -m pytest tests/` — all pass
- [ ] Dry-run `sdd_create` for BRD — 3-segment IDs in output
- [ ] Run `sdd_validate_links` on `ucx_flow_v3/` — no broken links
- [ ] Verify regex: `BRD.02.8cf7` → PASS, `RISKSPEC.01.a1b2` → PASS, `BRD.02.01.8cf7` → REJECT
- [ ] Commit and push all changes
