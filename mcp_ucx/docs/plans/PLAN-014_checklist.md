# PLAN-014 Executable Checklist

**Status**: Not Started
**Plan**: [PLAN-014_3segment_element_id_migration.md](./PLAN-014_3segment_element_id_migration.md)

---

## Phase 1: Standards Authority

- [ ] `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` — replace 4-segment with 3-segment format
- [ ] `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` — update regex to `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$`
- [ ] `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` — deprecate element type code table (01-99)
- [ ] `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` — remove Section-to-Element-Code Mapping
- [ ] `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` — update all examples to 3-segment
- [ ] `ai_dev_ssd_flow/VALIDATION_STANDARDS.md` — update IDPAT-E002, IDPAT-E003, IDPAT-W001
- [ ] `ai_dev_ssd_flow/VALIDATION_STANDARDS.md` — deprecate ELEM-E001/W001
- [ ] `ai_dev_ssd_flow/LAYER_REGISTRY.yaml` — update `id_patterns.element` regex

## Phase 1.5: Archive AUTOPILOT

- [ ] Move `ai_dev_ssd_flow/AUTOPILOT/` → `ai_dev_ssd_flow/archived/AUTOPILOT_v1_archive/`

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

- [ ] Copy `mcp_ucx/templates/BRD-TEMPLATE.yaml` → `ai_dev_ssd_flow/01_BRD/`
- [ ] Copy `mcp_ucx/templates/PRD-TEMPLATE.yaml` → `ai_dev_ssd_flow/02_PRD/`
- [ ] Copy `mcp_ucx/templates/EARS-TEMPLATE.yaml` → `ai_dev_ssd_flow/03_EARS/`
- [ ] Copy `mcp_ucx/templates/BDD-TEMPLATE.yaml` → `ai_dev_ssd_flow/04_BDD/`
- [ ] Copy `mcp_ucx/templates/ADR-TEMPLATE.yaml` → `ai_dev_ssd_flow/05_ADR/`
- [ ] Copy `mcp_ucx/templates/SYS-TEMPLATE.yaml` → `ai_dev_ssd_flow/06_SYS/`
- [ ] Copy `mcp_ucx/templates/REQ-TEMPLATE.yaml` → `ai_dev_ssd_flow/07_REQ/`
- [ ] Copy `mcp_ucx/templates/CTR-TEMPLATE.yaml` → `ai_dev_ssd_flow/08_CTR/`
- [ ] Copy `mcp_ucx/templates/SPEC-TEMPLATE.yaml` → `ai_dev_ssd_flow/09_SPEC/`
- [ ] Copy `mcp_ucx/templates/TSPEC-TEMPLATE.yaml` → `ai_dev_ssd_flow/10_TSPEC/`
- [ ] Copy `mcp_ucx/templates/TASKS-TEMPLATE.yaml` → `ai_dev_ssd_flow/11_TASKS/`

## Phase 2c: Layer READMEs (11 files)

- [ ] `ai_dev_ssd_flow/01_BRD/README.md` — update element ID examples
- [ ] `ai_dev_ssd_flow/02_PRD/README.md` — same
- [ ] `ai_dev_ssd_flow/03_EARS/README.md` — same
- [ ] `ai_dev_ssd_flow/04_BDD/README.md` — same
- [ ] `ai_dev_ssd_flow/05_ADR/README.md` — same
- [ ] `ai_dev_ssd_flow/06_SYS/README.md` — same
- [ ] `ai_dev_ssd_flow/07_REQ/README.md` — same
- [ ] `ai_dev_ssd_flow/08_CTR/README.md` — same
- [ ] `ai_dev_ssd_flow/09_SPEC/README.md` — same
- [ ] `ai_dev_ssd_flow/10_TSPEC/README.md` — same
- [ ] `ai_dev_ssd_flow/11_TASKS/README.md` — same

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

- [ ] `ai_dev_ssd_flow/README.md` — element ID table, examples
- [ ] `ai_dev_ssd_flow/QUICK_REFERENCE.md` — element format row
- [ ] `ai_dev_ssd_flow/TRACEABILITY.md` — tag format, cross-ref examples
- [ ] `ai_dev_ssd_flow/METADATA_TAGGING_GUIDE.md` — dot notation
- [ ] `ai_dev_ssd_flow/COMPLETE_TAGGING_EXAMPLE.md` — usage examples
- [ ] `ai_dev_ssd_flow/CUMULATIVE_TAG_REFERENCE.md` — validation logic
- [ ] `ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` — `@artifact-type` format
- [ ] `ai_dev_ssd_flow/AI_ASSISTANT_RULES.md` — XDOC-006, examples
- [ ] `ai_dev_ssd_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md` — feature ID format
- [ ] `ai_dev_ssd_flow/TRACEABILITY_SETUP.md` — format references
- [ ] `ai_dev_ssd_flow/TESTING_STRATEGY_TDD.md` — 9x `BRD.01.01.01`
- [ ] `ai_dev_ssd_flow/METADATA_VS_TRACEABILITY.md` — 6 mixed IDs
- [ ] `ai_dev_ssd_flow/THRESHOLD_NAMING_RULES.md` — `@threshold:` format
- [ ] `ai_dev_ssd_flow/01_BRD/BRD-00_GLOSSARY.md` — 1 ID ref
- [ ] `ai_dev_ssd_flow/METADATA_CORE_MATRIX.md` — check for ID refs
- [ ] `ai_dev_ssd_flow/AI_TOOL_OPTIMIZATION_GUIDE.md` — 1 ID ref
- [ ] `ai_dev_ssd_flow/PROJECT_SETUP_GUIDE.md` — 1 ID ref
- [ ] `ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md` — 23 ID refs
- [ ] `ai_dev_ssd_flow/FINANCIAL_DOMAIN_CONFIG.md` — 9 ID refs
- [ ] `ai_dev_ssd_flow/10_TSPEC/TSPEC-00_index.md` — 6 ID refs
- [ ] `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC-00_index.md` — 5 ID refs
- [ ] `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_CREATION_RULES.md` — 5 ID refs
- [ ] `ai_dev_ssd_flow/05_ADR/ADR-00_ai_powered_documentation_assistant_architecture.md` — 5 ID refs
- [ ] `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC-00_index.md` — 4 ID refs
- [ ] `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_CREATION_RULES.md` — 4 ID refs
- [ ] `ai_dev_ssd_flow/MVP_WORKFLOW_GUIDE.md` — check for ID refs

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
- [ ] Verify `ai_dev_ssd_flow/README.md` uses 3-segment (updated Phase 5)
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

- [ ] Run: `grep -rP '[A-Z]{2,8}\.\d{2,}\.\d{2,}\.[0-9a-f]{2,}' ai_dev_ssd_flow/ mcp_ucx/ .claude/ --include='*.md' --include='*.yaml' | grep -v archive | grep -v v1_archive` → 0 matches
- [ ] Validate all 11 template YAML files: `python -c "import yaml; ..."`
- [ ] Run `python -m pytest tests/` — all pass
- [ ] Dry-run `sdd_create` for BRD — 3-segment IDs in output
- [ ] Run `sdd_validate_links` on `ai_dev_ssd_flow/` — no broken links
- [ ] Verify regex: `BRD.02.8cf7` → PASS, `RISKSPEC.01.a1b2` → PASS, `BRD.02.01.8cf7` → REJECT
- [ ] Commit and push all changes
