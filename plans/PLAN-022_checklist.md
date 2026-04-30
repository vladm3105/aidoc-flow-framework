# PLAN-022 Executable Checklist: Multi-Persona Mappings for UCX Tools

**Plan**: `plans/PLAN-022_multi_persona_mappings.md` (v4)
**Created**: 2026-04-02
**Status**: Not Started

---

## Phase 1: Config & Persona Assets (Steps 1-2)

### Step 1: Create `persona_mappings.yaml`
- [ ] 1.1 Create `mcp_ucx/skills/persona_mappings.yaml` with full YAML content from plan
- [ ] 1.2 Verify all 10 creation doctypes present (brd, prd, ears, bdd, adr, sys, req, spec, ctr, tspec)
- [ ] 1.3 Verify all 10 review doctypes present
- [ ] 1.4 Verify `remediation._default` entry present with `loading: adaptive`
- [ ] 1.5 Cross-check: every persona name in YAML has a matching `.md` file in `mcp_ucx/skills/personas/` (except `content_strategist` — Step 2)

### Step 2: Create `content_strategist.md` persona
- [ ] 2.1 Create `mcp_ucx/skills/personas/content_strategist.md`
- [ ] 2.2 Include: role description, core principles, anti-patterns, category tagging (`[CAT:functional]`, `[CAT:quality]`, `[CAT:compliance]`), scoring weights
- [ ] 2.3 Follow format of existing personas (e.g., `ux_strategist.md`)
- [ ] 2.4 Re-run Step 1.5 cross-check — all 15 persona names now resolve

---

## Phase 2: Loader & Contracts (Steps 3-5)

### Step 3: Add loader functions and YAML validation
- [ ] 3.1 Add `PersonaMappingError` exception class to `mcp_ucx/src/mcp_server/skills/project_ucx_loader.py`
- [ ] 3.2 Add `load_persona_mapping(*, project_root: Path) -> dict` function
- [ ] 3.3 Add `_validate_persona_mapping(mapping: dict, project_root: Path) -> None` function
  - [ ] Validates `version` key exists
  - [ ] Validates each entry has `personas` as non-empty list of strings
  - [ ] Cross-references persona names against existing `.md` files
  - [ ] Raises `PersonaMappingError` with descriptive messages on failure
- [ ] 3.4 Wire `_validate_persona_mapping()` call inside `load_persona_mapping()` after `yaml.safe_load()`
- [ ] 3.5 Add `load_multi_persona_files(*, project_root: Path, personas: list[str]) -> list[tuple[str, str]]`
- [ ] 3.6 Add `import yaml` if not already present
- [ ] 3.7 Keep `load_project_persona_file()` as internal helper (no signature change)

### Step 4: Update public API re-export
- [ ] 4.1 Edit `mcp_ucx/src/mcp_server/skills/__init__.py`
- [ ] 4.2 Remove `load_project_persona_file` from public exports
- [ ] 4.3 Add `load_persona_mapping`, `load_multi_persona_files`, `PersonaMappingError` to exports

### Step 5: Update `PromptMetadataSidecar`
- [ ] 5.1 Edit `mcp_ucx/src/mcp_server/models/context_engineering_contracts.py`
- [ ] 5.2 Replace `persona: str` field with `personas: list[str]`
- [ ] 5.3 Add `persona_count: int` field
- [ ] 5.4 Add `persona_token_estimate: int` field
- [ ] 5.5 Add `persona_token_warning: str | None` field
- [ ] 5.6 Update validation: `if not metadata.personas: errors.append("personas is required")`
- [ ] 5.7 Update serialization to emit all 4 new fields in JSON output

---

## Phase 3: Context Builder (Steps 6-12)

### Step 6: Update dataclasses
- [ ] 6.1 Edit `mcp_ucx/src/mcp_server/prompts/context_builder.py`
- [ ] 6.2 `PromptAssembly`: replace `persona_text: str` with `persona_texts: list[str]` + `persona_names: list[str]`
- [ ] 6.3 `CreationAssembly`: replace `persona_text: str` with `persona_texts: list[str]` + `persona_names: list[str]`

### Step 7: Complete `PERSONA_CATEGORY_MAP` (all 15 personas)
- [ ] 7.1 Add `product_owner` entry: `("functional", "quality", "compliance")`
- [ ] 7.2 Add `business_analyst` entry: `("functional", "compliance", "quality")`
- [ ] 7.3 Add `strategist` entry: `("functional", "quality", "risk")`
- [ ] 7.4 Add `requirements_specialist` entry: `("functional", "technical", "compliance")`
- [ ] 7.5 Add `ux_strategist` entry: `("functional", "quality")`
- [ ] 7.6 Add `qa_lead` entry: `("functional", "technical", "quality", "risk")`
- [ ] 7.7 Add `fact_checker` entry: `("compliance", "quality", "functional")`
- [ ] 7.8 Add `content_strategist` entry: `("functional", "quality", "compliance")`
- [ ] 7.9 Verify total: 15 entries in map (7 existing + 8 new)

### Step 8: Add persona resolution, formatting, and token warning
- [ ] 8.1 Add `_resolve_personas(project_root, personas, doc_type, phase)` with `PersonaMappingError` on missing entries
- [ ] 8.2 Add `_format_persona_block(persona_pairs: list[tuple[str, str]]) -> str`
- [ ] 8.3 Add `TOKEN_WARNING_THRESHOLD = 10_000` constant
- [ ] 8.4 Add token warning logic: compute via `estimate_tokens()`, return warning string or None

### Step 9: Update `map_sections_for_persona` → `map_sections_for_personas`
- [ ] 9.1 Rename function to `map_sections_for_personas`
- [ ] 9.2 Change signature: `persona: str` → `personas: list[str]`
- [ ] 9.3 Implement union of all persona categories
- [ ] 9.4 Update caller in `assemble_project_review_prompt()`
- [ ] 9.5 Update caller in `assemble_project_creation_prompt()`

### Step 10: Update `discover_relevant_snippets`
- [ ] 10.1 Change signature: `persona: str` → `personas: list[str]`
- [ ] 10.2 Implement union keywords from all personas
- [ ] 10.3 Update caller in `assemble_project_review_prompt()`
- [ ] 10.4 Update caller in `assemble_project_creation_prompt()`

### Step 11: Update `build_prompt_bundle`
- [ ] 11.1 Change signature: `persona: str` → `personas: list[str]`
- [ ] 11.2 Construct `PromptMetadataSidecar` with `personas=personas`, `persona_count=len(personas)`
- [ ] 11.3 Add `persona_token_estimate` and `persona_token_warning` to sidecar construction

### Step 12: Update assembly functions
- [ ] 12.1 Update `assemble_project_creation_prompt()`: use `_resolve_personas()`, `_format_persona_block()`
- [ ] 12.2 Populate `persona_texts` and `persona_names` on `CreationAssembly`
- [ ] 12.3 Update `assemble_project_review_prompt()`: same changes
- [ ] 12.4 Populate `persona_texts` and `persona_names` on `PromptAssembly`
- [ ] 12.5 Remove all single `load_project_persona_file()` calls from both assembly functions

---

## Phase 4: Exports & Tool Dispatch (Steps 13-14b)

### Step 13: Update `prompts/__init__.py` exports
- [ ] 13.1 Edit `mcp_ucx/src/mcp_server/prompts/__init__.py`
- [ ] 13.2 Replace `map_sections_for_persona` export with `map_sections_for_personas`

### Step 14: Update tool schemas and dispatch
- [ ] 14.1 Edit `mcp_ucx/src/mcp_server/tool_registry.py`
- [ ] 14.2 `sdd_create_build`: replace `persona` with `personas` array (schema: line 239, required: line 248)
- [ ] 14.3 `sdd_create`: replace `persona` with `personas` array (schema: line 258, required: line 269)
- [ ] 14.4 `sdd_review`: replace `persona` with `personas` array (schema: line 279, required: line 291)
- [ ] 14.5 `sdd_run_lifecycle` (schema: line 224): replace `persona` with `personas`. No dispatch change — `_handle_lifecycle_pipeline()` (line 883) forwards all args to stage handlers; per-phase resolution happens in each stage's `_resolve_personas()`
- [ ] 14.6 `sdd_remediate` (line 313): add optional `personas` array param
- [ ] 14.7 `sdd_remediate_fix` (line 331): add optional `personas` array param
- [ ] 14.8 Confirm `sdd_validate_fix` (line 295) does NOT get personas param
- [ ] 14.9 Update `sdd_create_build` dispatch (line 737): `arguments.get("personas")` instead of `arguments["persona"]`
- [ ] 14.10 Update `sdd_create` dispatch (line 762): `arguments.get("personas")` instead of `arguments["persona"]`
- [ ] 14.11 Update `sdd_review` dispatch (line 796): `arguments.get("personas")` instead of `arguments["persona"]`
- [ ] 14.12 Update `sdd_remediate` dispatch (line 832): extract `arguments.get("personas")`
- [ ] 14.13 Update `sdd_remediate_fix` dispatch (line 856): extract `arguments.get("personas")`
- [ ] 14.14 Verify `_handle_lifecycle_pipeline()` (line 883) needs NO changes — it forwards args unchanged

### Step 14b: Implement adaptive remediation persona filtering
- [ ] 14b.1 Add `MANDATORY_REMEDIATION_PERSONAS = {"chaos_engineer", "chairperson"}` constant
- [ ] 14b.2 Add `_filter_adaptive_personas(mapping_personas, review_report_categories) -> list[str]`
- [ ] 14b.3 Add review report category parser: extract `[CAT:xxx]` tags from report text
- [ ] 14b.4 Wire into `sdd_remediate` dispatch: when mapping has `loading: adaptive`, apply filter before loading persona files
- [ ] 14b.5 Ensure mandatory personas always included regardless of findings

---

## Phase 5: Runner & CLI (Steps 15-16)

### Step 15: Update runner (3 functions)
- [ ] 15.1 Edit `mcp_ucx/src/mcp_server/review/runner.py`
- [ ] 15.2 Update `run_project_review_build()` (line 30): `persona: str` → `personas: list[str] | None`
- [ ] 15.3 Update `run_project_creation_build()` (line 101): `persona: str` → `personas: list[str] | None`
- [ ] 15.4 Update `run_project_creation_artifact()` (line 148): `persona: str` → `personas: list[str] | None`
- [ ] 15.5 Pass `personas` through to assembly functions in all three

### Step 16: Update CLI
- [ ] 16.1 Edit `mcp_ucx/src/mcp_server/cli/main.py`
- [ ] 16.2 `review-build` (line 41): replace `--persona` with `--personas`, `nargs="+"`, `default=None`
- [ ] 16.3 `review` (line 65): replace `--persona` with `--personas`, `nargs="+"`, `default=None`
- [ ] 16.4 `create-build` (line 86): replace `--persona` with `--personas`, `nargs="+"`, `default=None`
- [ ] 16.5 `create` (line 102): replace `--persona` with `--personas`, `nargs="+"`, `default=None`
- [ ] 16.6 Update handler for `review-build`/`review` (line 393): `args.personas` instead of `args.persona`
- [ ] 16.7 Update handler for `create-build` (line 443): `args.personas` instead of `args.persona`
- [ ] 16.8 Update handler for `create` (line 483): `args.personas` instead of `args.persona`

---

## Phase 6: Scaffold & Prompt Templates (Steps 17-18)

### Step 17: Add to scaffold
- [ ] 17.1 Edit `mcp_ucx/src/mcp_server/skills/scaffold.py`
- [ ] 17.2 Add `(Path("skills/persona_mappings.yaml"), Path("UCX/skills/persona_mappings.yaml"))` to `CANONICAL_SCAFFOLD_MAPPINGS`

### Step 18: Clean prompt templates (31 files)

#### Creation templates (11 files)
- [ ] 18.1 `UCC_PROMPT_BRD.md` — remove "Author Personas" section (lines 21-49), add runtime injection note
- [ ] 18.2 `UCC_PROMPT_BRD_PROJECT.md` — remove hardcoded persona list
- [ ] 18.3 `UCC_PROMPT_PRD.md` — remove persona list (lines 315-327)
- [ ] 18.4 `UCC_PROMPT_EARS.md` — remove persona list (lines 20-43)
- [ ] 18.5 `UCC_PROMPT_BDD.md` — remove persona list (lines 21-42)
- [ ] 18.6 `UCC_PROMPT_ADR.md` — remove persona list (lines 21-47)
- [ ] 18.7 `UCC_PROMPT_SYS.md` — remove persona list (lines 21-42)
- [ ] 18.8 `UCC_PROMPT_REQ.md` — remove persona list (lines 21-37)
- [ ] 18.9 `UCC_PROMPT_SPEC.md` — remove persona list (lines 21-42)
- [ ] 18.10 `UCC_PROMPT_CTR.md` — remove persona list (lines 21-37)
- [ ] 18.11 `UCC_PROMPT_TSPEC.md` — remove persona list (lines 21-37)

#### Review templates (10 files)
- [ ] 18.12 `UCR_PROMPT_BRD.md` — remove "Personas Applied" lines
- [ ] 18.13 `UCR_PROMPT_PRD.md` — remove persona list
- [ ] 18.14 `UCR_PROMPT_EARS.md` — remove persona list
- [ ] 18.15 `UCR_PROMPT_BDD.md` — remove persona list
- [ ] 18.16 `UCR_PROMPT_ADR.md` — remove persona list
- [ ] 18.17 `UCR_PROMPT_SYS.md` — remove persona list
- [ ] 18.18 `UCR_PROMPT_REQ.md` — remove persona list
- [ ] 18.19 `UCR_PROMPT_SPEC.md` — remove persona list
- [ ] 18.20 `UCR_PROMPT_CTR.md` — remove persona list
- [ ] 18.21 `UCR_PROMPT_TSPEC.md` — remove persona list

#### Remediation templates (10 files)
- [ ] 18.22 `UCRem_PROMPT_BRD.md` — remove hardcoded fixer persona list
- [ ] 18.23 `UCRem_PROMPT_PRD.md` — remove hardcoded fixer persona list
- [ ] 18.24 `UCRem_PROMPT_EARS.md` — remove hardcoded persona refs
- [ ] 18.25 `UCRem_PROMPT_BDD.md` — remove hardcoded persona refs
- [ ] 18.26 `UCRem_PROMPT_ADR.md` — remove hardcoded persona refs
- [ ] 18.27 `UCRem_PROMPT_SYS.md` — remove hardcoded persona refs
- [ ] 18.28 `UCRem_PROMPT_REQ.md` — remove hardcoded persona refs
- [ ] 18.29 `UCRem_PROMPT_SPEC.md` — remove hardcoded persona refs
- [ ] 18.30 `UCRem_PROMPT_CTR.md` — remove hardcoded persona refs
- [ ] 18.31 `UCRem_PROMPT_TSPEC.md` — remove hardcoded persona refs

#### All templates: keep
- [ ] 18.32 Verify collaboration protocol instructions preserved in all creation templates
- [ ] 18.33 Verify category tagging and output format preserved in all review templates
- [ ] 18.34 Verify remediation procedures preserved in all remediation templates
- [ ] 18.35 Add `<!-- Personas injected at runtime from persona_mappings.yaml -->` note to each

---

## Phase 7: Tests (Step 19)

### Step 19a: `tests/unit/test_project_ucx_loader.py`
- [ ] 19a.1 Update existing test to use `load_multi_persona_files()` with multiple personas
- [ ] 19a.2 Add test: `load_persona_mapping()` with valid YAML
- [ ] 19a.3 Add test: `load_persona_mapping()` raises on missing file
- [ ] 19a.4 Add test: `_validate_persona_mapping()` raises on malformed YAML (missing `personas` key)
- [ ] 19a.5 Add test: `_validate_persona_mapping()` raises on invalid persona name (no `.md` file)

### Step 19b: `tests/unit/test_cli_main.py`
- [ ] 19b.1 Update all 7 test functions: `--persona architect` → `--personas architect tech_lead`
- [ ] 19b.2 Add test: `--personas` accepts multiple space-separated values
- [ ] 19b.3 Add test: omitting `--personas` does not error (optional param)

### Step 19c: `tests/unit/test_review_runner.py`
- [ ] 19c.1 Update `run_project_review_build` call: `persona=` → `personas=`
- [ ] 19c.2 Update `run_project_creation_build` call: `persona=` → `personas=`
- [ ] 19c.3 Create multiple persona `.md` files in test fixtures

### Step 19d: `tests/unit/test_scaffold_init.py`
- [ ] 19d.1 Add assertion: `(project_root / "UCX/skills/persona_mappings.yaml").exists()`
- [ ] 19d.2 Add test: `persona_mappings.yaml` not overwritten on re-scaffold

### Step 19e: `tests/unit/test_reporting_contracts.py`
- [ ] 19e.1 Update `source_expert` references if they consume persona metadata
- [ ] 19e.2 Verify persona → personas field change in contract assertions

### Step 19f: `tests/integration/test_creation_prompt_builder.py`
- [ ] 19f.1 Update all `persona="architect"` calls → `personas=["architect", "tech_lead"]`
- [ ] 19f.2 Assert `assembly.persona_names == ["architect", "tech_lead"]`
- [ ] 19f.3 Assert `len(assembly.persona_texts) == 2`
- [ ] 19f.4 Update sidecar assertions: `"personas": ["architect", "tech_lead"]`
- [ ] 19f.5 Update CLI integration tests: `--persona` → `--personas`

### Step 19g: `tests/integration/test_prompt_context_builder.py`
- [ ] 19g.1 Update `build_prompt_bundle(persona=...)` → `personas=[...]`
- [ ] 19g.2 Rename test: `test_map_sections_for_persona_*` → `test_map_sections_for_personas_*`
- [ ] 19g.3 Update sidecar assertion: `'"persona":` → `'"personas":`
- [ ] 19g.4 Update validation assertion: `"persona is required"` → `"personas is required"`
- [ ] 19g.5 Add test: union category mapping with multiple personas includes all categories

### Step 19h: Create `tests/unit/test_persona_mappings.py` (new file)
- [ ] 19h.1 Create file
- [ ] 19h.2 Test `_resolve_personas()` with explicit override list
- [ ] 19h.3 Test `_resolve_personas()` with mapping config fallback
- [ ] 19h.4 Test `_resolve_personas()` with `_default` fallback for remediation
- [ ] 19h.5 Test `_resolve_personas()` raises `PersonaMappingError` for missing phase
- [ ] 19h.6 Test `_resolve_personas()` raises `PersonaMappingError` for missing doctype with no `_default`
- [ ] 19h.7 Test all 15 persona names in YAML resolve to existing `.md` files
- [ ] 19h.8 Test `_format_persona_block()` with 1 persona (no wrapper)
- [ ] 19h.9 Test `_format_persona_block()` with 3 personas
- [ ] 19h.10 Test `_format_persona_block()` with 11 personas
- [ ] 19h.11 Test `_filter_adaptive_personas()` keeps mandatory + matching domain personas
- [ ] 19h.12 Test `_filter_adaptive_personas()` with no matching findings keeps only mandatory
- [ ] 19h.13 Test token warning emitted when persona text exceeds threshold

### Step 19i: Verify non-modified persona consumers (3 files)
- [ ] 19i.1 `preflight/runner.py` (lines 156-162): confirm `personas` directory check still works (directory name unchanged)
- [ ] 19i.2 `remediation/review_parser.py` (line 41): confirm `source_expert: str` field unchanged — this is the input the adaptive filter (Step 14b) reads from
- [ ] 19i.3 `reporting/contracts.py` (lines 430, 439-440): review legacy `"persona"` key in report parsing — document as known legacy format, no change needed in v1.12.0

### Run tests
- [ ] 19.RUN Run full test suite: `cd mcp_ucx && python -m pytest tests/ -v`
- [ ] 19.VERIFY All tests pass (0 failures)

---

## Phase 8: UCX Architecture Documentation (Steps 20-22)

### Step 20a: `MCP_PERSONA_DESIGN_GUIDE.md`
- [ ] 20a.1 Document multi-persona architecture (2-tier resolution)
- [ ] 20a.2 Document `persona_mappings.yaml` config format and location
- [ ] 20a.3 Update runtime source policy: single-load → multi-load via mapping
- [ ] 20a.4 Add complete persona taxonomy table (all 15 personas with category mappings)
- [ ] 20a.5 Update persona output contract for multi-persona prompts
- [ ] 20a.6 Document `mode` field as metadata-only in v1.0

### Step 20b: `MCP_CLI_REFERENCE.md`
- [ ] 20b.1 Replace `--persona` with `--personas` in all command signatures
- [ ] 20b.2 Update all usage examples
- [ ] 20b.3 Document `nargs="+"` behavior and interaction with `persona_mappings.yaml`

### Step 20c: `MCP_OPERATIONAL_FLOWS.md`
- [ ] 20c.1 Update creation workflow diagram to show multi-persona loading
- [ ] 20c.2 Update review workflow diagram to show multi-persona loading
- [ ] 20c.3 Document `persona_mappings.yaml` in directory structure section

### Step 20d: `MCP_OPERATOR_RUNBOOK.md`
- [ ] 20d.1 Update error handling section for multi-persona failures
- [ ] 20d.2 Add `PersonaMappingError` troubleshooting entry
- [ ] 20d.3 Document `persona_mappings.yaml` troubleshooting

### Step 20e: `MCP_RUNTIME_ARCHITECTURE.md`
- [ ] 20e.1 Update runtime loading sequence to show multi-persona resolution
- [ ] 20e.2 Document 2-tier resolution priority diagram

### Step 20f: `MCP_UNIFIED_CONTEXT_FRAMEWORK.md`
- [ ] 20f.1 Update UCX framework description to reflect multi-persona as core capability
- [ ] 20f.2 Document `persona_mappings.yaml` as canonical persona config source

### Step 21: Update UCX specification documents (7 files)
- [ ] 21a SPEC-002 (review scoring): update `persona: str` → `personas: list[str]` in contract (11 refs)
- [ ] 21b SPEC-003 (creation validation): update persona references
- [ ] 21c SPEC-004 (reporting lineage): update persona field in metadata
- [ ] 21d SPEC-005 (source input): update persona reference
- [ ] 21e SPEC-006 (creation flow): update persona parameter
- [ ] 21f SPEC-007 (review/remediation): update persona parameter
- [ ] 21g SPEC-001 (core architecture): update persona reference

### Step 22: Update standalone persona definition files
- [ ] 22a `mcp_ucx/prompts/templates/creation/UCC_PERSONAS.md` — add `persona_mappings.yaml` authority note, remove hardcoded per-doctype lists
- [ ] 22b `mcp_ucx/prompts/templates/remediation/UCRem_PERSONAS.md` — add `persona_mappings.yaml` authority note, remove hardcoded matrix
- [ ] 22c Mirror 22a to `UCX/prompts/templates/creation/UCC_PERSONAS.md`
- [ ] 22d Mirror 22b to `UCX/prompts/templates/remediation/UCRem_PERSONAS.md`

---

## Phase 9: README & SDD Framework Docs (Steps 23-25)

### Step 23: Update README files
- [ ] 23a `README.md` (project root) — add multi-persona support to feature list
- [ ] 23b `mcp_ucx/docs/README.md` — update overview, add `persona_mappings.yaml` to directory structure
- [ ] 23c `mcp_ucx/skills/README.md` — document `persona_mappings.yaml`, add `content_strategist.md` to listing

### Step 24: Update SDD framework documentation
- [ ] 24a `ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` — update UCX tool description
- [ ] 24b `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` — update persona metadata field

### Step 25: UCX/ directory mirror sync
- [ ] 25.1 Copy `mcp_ucx/skills/persona_mappings.yaml` → `UCX/skills/persona_mappings.yaml`
- [ ] 25.2 Copy `mcp_ucx/skills/personas/content_strategist.md` → `UCX/skills/personas/content_strategist.md`
- [ ] 25.3 Mirror all 11 updated `UCC_PROMPT_*.md` to `UCX/prompts/templates/creation/`
- [ ] 25.4 Mirror all 10 updated `UCR_PROMPT_*.md` to `UCX/prompts/templates/review/`
- [ ] 25.5 Mirror all 10 updated `UCRem_PROMPT_*.md` to `UCX/prompts/templates/remediation/`
- [ ] 25.6 Verify no stale `--persona` (singular) references remain: `grep -r "persona[^s]" UCX/ --include="*.md" | grep -v persona_mappings | grep -v "persona " | grep -- "--persona "`

---

## Phase 10: Changelog & Roadmap (Steps 26-29)

### Step 26: Create mcp_ucx changelog
- [ ] 26.1 Create `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.12.0.md`
- [ ] 26.2 Include Added, Changed, Removed sections per plan
- [ ] 26.3 Document backward compatibility note

### Step 27: Update mcp_ucx roadmap
- [ ] 27.1 Edit `mcp_ucx/docs/ROADMAP.md`
- [ ] 27.2 Add v1.12.0 entry with multi-persona mapping milestone
- [ ] 27.3 Mark PLAN-022 as completed

### Step 28: Create framework changelog
- [ ] 28.1 Create `changelog/CHANGELOG_v0.19.0.md`
- [ ] 28.2 Reference UCX v1.12.0 multi-persona feature
- [ ] 28.3 Summary of documentation updates

### Step 29: Update framework roadmap
- [ ] 29.1 Edit `roadmap/ROADMAP.md`
- [ ] 29.2 Add v0.19.0 entry referencing UCX v1.12.0
- [ ] 29.3 Update timeline diagram and version table

---

## Final Validation

### Code & Runtime
- [ ] V1 `sdd_create_build` for BRD loads all 5 creation personas from mapping
- [ ] V2 `sdd_review` for BRD loads all 11 review personas from mapping
- [ ] V3 `sdd_remediate` loads remediation personas from `_default` mapping
- [ ] V4 Adaptive loading filters domain personas by review report categories
- [ ] V5 `sdd_remediate_fix` accepts optional `personas` param
- [ ] V6 `sdd_run_lifecycle` forwards `personas` to stage handlers; each stage resolves from mapping independently
- [ ] V7 Explicit `personas` param overrides `persona_mappings.yaml` on all tools
- [ ] V8 Missing persona `.md` file raises `ProjectSkillsNotFound`
- [ ] V9 Missing `persona_mappings.yaml` raises `ProjectSkillsNotFound`
- [ ] V10 Malformed YAML raises `PersonaMappingError` with descriptive message
- [ ] V11 Invalid persona name in YAML caught at load time
- [ ] V12 Missing phase or doctype (no `_default`) raises `PersonaMappingError`
- [ ] V13 `sdd_init` scaffolds `persona_mappings.yaml` to `UCX/skills/`
- [ ] V14 Sidecar includes `personas`, `persona_count`, `persona_token_estimate`, `persona_token_warning`
- [ ] V15 Token warning emitted when combined persona text exceeds 10,000 tokens
- [ ] V16 All 15 persona names in YAML resolve to existing `.md` files
- [ ] V17 Section union mapping includes categories from all loaded personas
- [ ] V18 `discover_relevant_snippets` uses union keywords from all personas
- [ ] V19 31 prompt templates cleaned of hardcoded persona lists
- [ ] V20 CLI `--personas` accepts multiple space-separated values
- [ ] V21 `PERSONA_CATEGORY_MAP` covers all 15 personas
- [ ] V22 `mode` field in YAML is metadata-only — not read by runtime

### Tests
- [ ] V23 All 7 existing test files pass after migration
- [ ] V24 New `test_persona_mappings.py` covers resolution, formatting, validation, adaptive filter
- [ ] V25 Full test suite passes: `python -m pytest tests/ -v` → 0 failures
- [ ] V25b `preflight/runner.py` personas directory check still passes
- [ ] V25c `reporting/contracts.py` legacy persona format documented as known

### Documentation
- [ ] V26 All 6 architecture docs updated
- [ ] V27 All 7 SPEC files updated with `personas: list[str]` contract
- [ ] V28 `UCC_PERSONAS.md` and `UCRem_PERSONAS.md` reference `persona_mappings.yaml`
- [ ] V29 3 README files updated
- [ ] V30 SDD framework docs updated
- [ ] V31 UCX/ mirror synced (33+ files)
- [ ] V32 No stale `--persona` (singular) in any documentation

### Changelog & Roadmap
- [ ] V33 `CHANGELOG_v1.12.0.md` created
- [ ] V34 mcp_ucx `ROADMAP.md` updated
- [ ] V35 `CHANGELOG_v0.19.0.md` created
- [ ] V36 Framework `ROADMAP.md` updated

### Final
- [ ] V37 Update PLAN-022 status: Draft → Completed
- [ ] V38 Commit all changes with descriptive message
