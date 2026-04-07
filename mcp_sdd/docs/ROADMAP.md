# MCP Roadmap

## Overview

This roadmap defines planned documentation and governance milestones for MCP documentation under mcp_sdd/docs.

| Field | Value |
| --- | --- |
| Current Version | 1.21.0 |
| Latest Release | 1.21.0 (API executor, tool surface cleanup — PLAN-031) |
| Previous Release | 1.20.0 (review/remediation quality — PLAN-029) |
| Next Major | 2.0.0 (post-migration governance hardening and policy enforcement) |
| Timezone | America/New_York |

Versioning policy reference:

- policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md

---

## Version Timeline

v1.2.0 -> v1.3.0 (Diagnostics) -> v1.4.0 (Current: MCP Transport) -> v2.0.0

---

## Planned Releases

### v1.1.0 - Migration Core (UCX_v1 to MCP without autopilot)

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Scope | Implement missing MCP runtime capabilities and migrate to MCP-first documentation |

Delivered scope:

- Implement currently missing commands except autopilot: `remediate`, `validate-fix`, `remediate-fix`.
- Add operational command controls for validation and review modes.
- Implement prescreen and diagnostics entry points (`prescreen`, `scan`, `scoring`).
- Publish MCP-first documentation for framework overview and operational flows.
- Remove active MCP runtime-doc dependency on UCX_v1 references.

Outcome summary:

- In-scope commands execute with deterministic output contracts and tests.
- MCP docs are sufficient to operate MCP without consulting UCX_v1 archive docs.
- Migration tracking is recorded in `plans/IPLAN-003_mcp_full_migration_from_ucx_v1.md` and `plans/IPLAN-003_RELEASE_TRACKING.yaml`.

---

### v1.2.0 - Lifecycle Normalization and Command Alignment

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Scope | Normalize active MCP lifecycle command naming, generalize derived-artifact flow semantics, and publish explicit project-initialization guidance |

Delivered scope:

- Normalize active validation command naming to `validate` across runtime, tests, and active documentation.
- Generalize source-protected derived-artifact flow semantics across all SSD document layers.
- Normalize folder-based artifact resolution so downstream stages consume the correct prior artifact.
- Publish explicit project initialization flow documentation for `init`, `create-build`, and `create`.
- Record historical closure in `plans/IPLAN-004_mcp_lifecycle_normalization_and_command_alignment.md`.

Outcome summary:

- Active runtime and architecture docs use MCP-native lifecycle naming.
- Derived artifact naming and source resolution rules are explicit and test-backed.
- Project-specific prompt/template initialization is documented as part of the operational flow.

References:

- plans/IPLAN-004_mcp_lifecycle_normalization_and_command_alignment.md
- architecture/MCP_OPERATIONAL_FLOWS.md
- architecture/MCP_CLI_REFERENCE.md

---

### v1.3.0 - Diagnostics and Governance Refinement

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Scope | Refine diagnostics coverage, operational controls, and release governance evidence |

Planned scope:

- Expand diagnostics and command-control coverage where needed.
- Continue aligning operator and runtime documentation to implemented contracts.
- Strengthen release-history and governance evidence artifacts for future MCP releases.

Implemented scope to date:

- Implement IPLAN-005 baseline command contracts for:
  - `consistency` (lightweight artifact-lineage checks)
  - `preflight` (runtime and environment readiness checks)
- Add preflight fallback parsing and runtime-error exit-contract coverage.
- Complete remediation source-restoration telemetry hardening with present and omitted branch coverage.
- Expand EARS and SPEC TASKS CTR validation parity-depth checks, including negative-path fixtures and EARS folder validation coverage.
- Add deterministic hash-based `finding_id` and `action_id` emission for remediation findings with legacy finding-ID compatibility validation.
- Update runbook, lifecycle flow documentation, and remediation/reporting specs for G3 diagnostics contracts.
- Publish final IPLAN-005 closure tracking and evidence artifacts.
- Normalize monolith-first validation behavior across all layers:
  - file-input validation redirects to canonical source artifact when folder contains a unique canonical source
  - index, appendix, glossary, and section-split markdown inputs resolve to canonical main document under this condition
- Expand review document-mode source assembly across all layers:
  - `review-build` and `review` support `--document` mode to auto-load canonical main plus appendix artifacts
  - `--sections-json` compatibility mode remains available for explicit section payload workflows
- Add cross-layer unit coverage for both validation redirection and review document-mode source assembly.

---

### v1.4.0 - MCP Protocol Transport Layer

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-03-28 |
| Scope | MCP server exposing SDD lifecycle as 19 native tools with per-call executor selection |

Delivered scope:

- MCP server entry point (`mcp_sdd/src/mcp_server/server.py`) over stdio transport, server name `sdd-lifecycle`
- Executor package (`mcp_sdd/src/mcp_server/executor/`): open registry with CLI and API type system, async subprocess runner, LiteLLM API stub, type-based dispatcher
- Tool registry (`mcp_sdd/src/mcp_server/tool_registry.py`): 20 tools (12 deterministic, 2 orchestration, 6 LLM-dependent)
- Packaging: `mcp_sdd/pyproject.toml` with `mcp-sdd` console script
- Registration: `.mcp.json` for Claude Code auto-discovery
- Tests: 33 new tests in `mcp_sdd/tests/unit/test_server.py`, all passing
- Validated against b-local project (BRD create, validate, pipeline)

References:

- plans/PLAN-001_mcp_protocol_transport_layer.md (repo-level plan)
- changelog/CHANGELOG_v0.1.0.md (repo-level changelog)

---

### v1.5.0 - Link Validation Tool and Executor Write Fixes

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-03-30 |
| Scope | New sdd_validate_links tool and CLI executor write-mode fixes |

Delivered scope:

- New tool: `sdd_validate_links` (20th tool, 12th deterministic) — validates markdown links and anchor references
- Executor fixes: Claude Code `--dangerously-skip-permissions`, Codex `--full-auto` for non-interactive file writes
- Tool count: 19 → 20 (12 deterministic, 2 orchestration, 6 LLM-dependent)
- 18 new unit tests (186 total, 0 regressions)
- Standalone `scripts/validate_doc_links.py` replaced by MCP tool

References:

- changelog/CHANGELOG_v0.12.1.md (repo-level changelog)

---

### v1.6.0 - 3-Segment Element ID Migration

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-03-31 |
| Scope | Element IDs from TYPE.NN.TT.hash to TYPE.NN.hash |

Delivered scope:

- All 11 templates: format, guidance, examples updated to 3-segment
- Prompt templates: UCC_PROMPT_PRD "4-segment" instruction removed
- Validation regex: `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$`
- Element type code table deprecated
- AUTOPILOT directory archived

---

### v1.7.0 - Cross-Section Validation and BRD Template Improvements

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | Two-tier cross-section validation in sdd_validate, YAML document support, BRD template enhancements |

Planned scope:

- Tier 1 (generic, all layers): Traceability ID existence validation (SDD-XS-001), readiness score plausibility check (SDD-XS-002), diagram registry presence (SDD-XS-003)
- Tier 2 (BRD-specific): ADT decision propagation (BRD-XS-001), phase alignment (BRD-XS-002), entity consistency (BRD-XS-004), currency scope consistency (BRD-XS-005)
- YAML document support in `sdd_validate` — validates `.yaml` BRDs alongside existing `.md` path (completed in v1.8.0; review pipeline YAML support delivered in v1.19.0)
- BRD-TEMPLATE.yaml updates: `diagrams` section, `cross_section_rules` metadata
- New BRD-MD-TEMPLATE.md for standardized YAML-to-MD rendering
- DIAGRAM_STANDARDS.md: BRD required diagram list, DFD-L1 standardization
- New modules: `validation/cross_section.py`, `validation/brd_rules.py`
- Pattern established for future layer-specific rules (`prd_rules.py`, `spec_rules.py`)

References:

- plans/PLAN-016_cross_section_validation.md

---

### v1.8.0 - YAML Parity and API Consistency

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | YAML document support across all tools, categorized scoring, result class API normalization |

Delivered scope:

- YAML source/derived artifact detection in `sdd_consistency` and `sdd_next_action`
- Categorized scoring: structural (20pt), cross-section (10pt), warning (5pt)
- Result class `.report`/`.is_valid`/`.is_ready` property aliases (6 classes)
- YAML structure validation in `sdd_remediate` (required keys, empty sections, element IDs)
- Shared `utils/source_files.py` collector
- 24 new tests (187 total)

References:

- plans/PLAN-018_yaml_parity_and_api_consistency.md

---

### v1.9.0 - Remediation Build Enhancement

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | Review report parsing in sdd_remediate for structured remediation findings |

Delivered scope:

- Review report parser (frontmatter + 3 table formats)
- Parsed findings replace single "review linked" pointer in remediation report
- 50-finding cap, review_summary in report output
- Fix prompt: 742 chars → ~10K chars with per-finding actions
- 18 new tests (205 total)

References:

- plans/PLAN-019_remediation_build_enhancement.md

---

### v1.10.0 - UCX Root Relocation

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | Relocate UCX from docs/UCX/ to project root UCX/ |

Delivered scope:

- All UCX paths relocated from `docs/UCX/` to `UCX/`
- Centralized `resolve_ucx_root()` with backward-compatible fallback
- Auto-migration in `sdd_init` (detects and moves `docs/UCX/` → `UCX/`)
- 22 files updated (~100 path references)
- 2 projects migrated (docs_flow_framework, b-local-docs)

References:

- plans/PLAN-020_ucx_root_relocation.md

---

### v1.11.0 - Unified Report Naming Standard

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | Unified report naming: {DOC-ID}.{STAGE}.{FORMAT} |

Delivered scope:

- Report naming convention with sub-framework registry (sdd, gov, kb)
- `extract_doc_id()` helper, `REPORT_PATTERN`/`DERIVED_COPY_PATTERN` regex
- Derived copies: `_validate_copy`/`_remediate_copy` (renamed to `_validated`/`_remediate_copy` in v1.13.0)
- Standards document: `REPORT_NAMING_STANDARDS.md`
- 1,089 legacy reports deleted (clean break)

References:

- plans/PLAN-021_sdd_reporting_naming_standard.md

---

### v1.12.0 - Multi-Persona Mapping Support

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | Multi-persona mapping support via persona_mappings.yaml (PLAN-022) |

Delivered scope:

- `persona_mappings.yaml` — machine-readable per-doctype, per-phase persona sequences
- 15-persona category map (expanded from 7)
- Multi-persona prompt assembly with token budget tracking
- Tool schema migration: `persona` (string) → `personas` (array, optional)
- CLI migration: `--persona` → `--personas` (optional, `nargs="+"`)
- YAML schema validation with persona name cross-references
- 31 prompt templates cleaned of hardcoded persona lists

References:

- plans/PLAN-022_multi_persona_mappings.md

---

### v1.13.0 - Merge sdd_validate_fix into sdd_validate

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | Merge sdd_validate_fix into sdd_validate, artifact naming changes (PLAN-023) |

Delivered scope:

- `sdd_validate_fix` merged into `sdd_validate` — one tool runs validation + creates fix artifacts when errors found
- `sdd_validate_fix` retained as deprecated alias (routes to `sdd_validate`)
- Pipeline flow simplified: validate → review → remediate → remediate_fix (no separate validate_fix step)
- `sdd_next_action`: "validated" goes directly to "review" (no intermediate "validate_fix" step)
- New response fields: `is_valid` (bool), `fix_generated` (bool), `passed` always True (for pipeline)
- Tool count: 20 → 19 (12 deterministic, 1 orchestration, 6 LLM-dependent)
- Artifact naming changes:
  - `{id}.ucx.validate.json/.txt` — initial validation report (unchanged per PLAN-021)
  - `*_validate_copy.*` → `*_validated.*` (derived copy suffix)
  - `{id}.ucx.validate_fix.json/.txt` — unchanged (fix metadata + instructions)

References:

- plans/PLAN-023_merge_validate_tools.md

---

### v1.14.0 - Executor Simplification and PLAN-021 Naming Compliance

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-03 |
| Scope | Simplify CLI executor prompt delivery; fix validation report naming to comply with PLAN-021 |

Delivered scope:

- CLI executor prompt delivery unified: all executors use positional arguments (removed stdin fallback, `prompt_mode` branching, temp file creation)
- Removed `prompt_file` from `ExecutorResult`, `PROMPT_SIZE_THRESHOLD` constant, `tempfile` import
- Fixed validation report naming: `{id}.ucx.validate_review.json/.txt` → `{id}.ucx.validate.json/.txt` per PLAN-021 stage code table
- Updated `REPORT_PATTERN` regex, `_inspect_document_folder` detection, `consistency/runner.py` lookup
- Updated architecture docs, changelogs, roadmap for consistency

References:

- PLAN-021 (reporting naming standard)
- CHANGELOG/CHANGELOG_v1.14.0.md

---

### v1.15.0 - Persona Optimization

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-03 |
| Scope | Optimize persona mappings across creation, review, and remediation phases (PLAN-024, PLAN-025) |

Delivered scope:

- Review phase: max 5 personas per layer (BRD 11→5, PRD 10→5, ADR 7→5, SYS 6→5, BDD 6→5)
- Creation phase: coverage gap fixes (7 layers updated), PRD 7→6
- Remediation phase: `_default` 6→5 (drop integration_lead)
- 5 review prompt templates rewritten to match new persona sections
- 10 remediation templates updated (removed Integration Fixer)
- `UCRem_PERSONAS.md` rewritten (6→5 fixers)
- Deprecated legacy review files deleted (`UCX/review/UCR_*_PROJECT.md`)
- Category coverage verified: 7/7 across most layers, 4 accepted gaps documented
- Total persona slots: 113 → 105

References:

- plans/PLAN-024 (review phase optimization)
- plans/PLAN-025 (creation/remediation optimization)
- CHANGELOG/CHANGELOG_v1.15.0.md

---

### v1.16.0 - Persona Management Tools

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-05 |
| Scope | Persona management MCP tools, scaffold update mode, BRD template refinement |

Delivered scope:

- 3 new MCP tools: `sdd_personas_show`, `sdd_personas_set`, `sdd_personas_diff`
- 3 new CLI commands: `personas-show`, `personas-set`, `personas-diff`
- `sdd_init --update` mode: sync stale project UCX files with framework source
- `sdd_init --update-mappings`: explicit reset of protected `persona_mappings.yaml`
- `PROTECTED_PROJECT_FILES` mechanism prevents accidental overwrite of project-owned configs
- Preflight persona mapping health check (missing files, missing doctypes)
- BRD `executive_summary` demoted to optional (derived section, generated on demand)
- BRD-XS-004 entity consistency rule rewritten to use `stakeholders`/`business_objectives`
- `executive_summary` removed from BRD required keys in remediation runner
- 22 MCP tools total (was 19)
- 295 tests pass (21 new tests)

References:

- PLAN-026 (persona management tools)
- CHANGELOG/CHANGELOG_v1.16.0.md

---

### v1.17.0 - Project Environment Management

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-06 |
| Scope | Auto-load project .env for executors, secure inspection tool, enhanced preflight |

Delivered scope:

- New module: `mcp_sdd/src/mcp_server/env_manager.py` — `.env` loading with mtime-based cache, system variable blocklist, BOM handling, permission warnings
- New MCP tool: `sdd_env_show` — show project .env keys without exposing values
- New CLI command: `env-show` — text/JSON output of .env key inventory
- Executor env merge chain: `os.environ` < `config.env` < `project_env` (.env wins, except blocked vars)
- `project_env` parameter threaded through `run_cli_executor` → `run_executor` → `_maybe_run_executor`
- Enhanced preflight: reports `env_key_count`, `env_keys`, `env_blocked_vars`
- Security: `BLOCKED_ENV_VARS` frozenset (PATH, HOME, PYTHONPATH, etc.), file permission warning, None value filtering
- Dependency: `python-dotenv>=1.0.0`
- 23 MCP tools total (was 22)
- 314 tests pass (19 new tests)

References:

- PLAN-027 (project environment management)
- CHANGELOG/CHANGELOG_v1.17.0.md

---

### v1.18.0 - Default Project Resolution

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-06 |
| Scope | Session/config default project, token-efficient tool calls (PLAN-027 Phase 2) |

Delivered scope:

- New module: `mcp_sdd/src/mcp_server/project_context.py` — session state, config default, 4-level resolve chain
- New MCP tools: `sdd_set_project`, `sdd_get_project` (25 tools total)
- New CLI command: `get-project`
- `_PROJECT_TOOLS` injection in `handle_tool()` — before `configure_logging`, guarded by schema
- `executors.json` migrated to object format with backward-compat array shim
- `SDD_DEFAULT_PROJECT` env var fallback for all CLI `--project` arguments
- Token savings: ~650-750 tokens per 15-call session
- 337 tests pass (23 new tests)

References:

- PLAN-027 Phase 2 (default project resolution)
- CHANGELOG/CHANGELOG_v1.18.0.md

---

### v1.19.0 - Review YAML Document Support

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-06 |
| Scope | YAML document support in review pipeline document collection (PLAN-028) |

Delivered scope:

- Review pipeline document collection extended to `.yaml` and `.yml` files alongside `.md`
- YAML-first precedence: when both `.yaml` and `.md` canonical sources exist, YAML wins
- `_LEGACY.md` files excluded from candidate list (prevents multi-match failures)
- Appendix detection simplified to name-based matching only (removed `.18[_.]` fallback)
- Function renames: `_list_review_markdown_candidates` → `_list_review_document_candidates`, `_collect_review_markdown_files` → `_collect_review_document_files`
- 16 new tests (353 total)

References:

- plans/PLAN-028_review_yaml_document_support.md
- CHANGELOG/CHANGELOG_v1.19.0.md

---

### v1.20.0 - Review/Remediation Pipeline Quality

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-06 |
| Scope | Review accuracy improvements, remediation prompt enrichment, post-fix quality gates (PLAN-029) |

Delivered scope:

- Remediate-fix prompt: 4-line generic → 6-step fix strategy with FWDREF handling, section ordering, substantive content rules
- Document content embedding in remediate-fix prompt (50K char cap)
- Phased finding groups (P0→P1→P2) in executor prompt
- Priority-sorted 50-finding cap (P0 never dropped)
- `recommended_action` truncation increased from 300 to 2000 chars
- `fact_checker` persona added to default BRD review sequence (catches scope misunderstandings)
- Auditor: APPLICABILITY CHECK guard — verifies regulation relevance before P0 classification
- Chairperson: Applicability Veto (4th synthesis principle) — excludes out-of-scope findings from scoring
- Post-fix validation: auto-run `sdd_validate` on derived copy after `remediate_fix` in pipeline
- New `verify_remediation_quality()` function: detects cosmetic FWDREF renames, stub sections, low content delta

References:

- plans/PLAN-029_review_remediation_quality.md
- CHANGELOG/CHANGELOG_v1.20.0.md

---

### v1.21.0 - API Executor and Tool Surface Cleanup

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-07 |
| Scope | LiteLLM API executor, sdd_remediate_fix absorption, sdd_clean tool (PLAN-030, PLAN-031) |

Delivered scope:

- Versioned remediation copies: `_remediate_v{N}` naming preserves all iterations (PLAN-030)
- API executor via LiteLLM: 100+ LLM providers including OpenRouter, Claude API, OpenAI, Gemini
- Built-in OpenRouter executor entry (`api/openrouter`)
- API executors upgraded from stub to active status
- `sdd_remediate_fix` absorbed into `sdd_remediate` as `fix=true` mode with optional `remediation_report` parameter
- New `sdd_clean` maintenance tool: prunes obsolete stage artifacts with configurable `keep` count and `dry_run` safety
- `sdd_run_lifecycle` gains `clean_before` parameter for clean-slate pipeline runs
- `sdd_next_action` updated: recommends `remediate --fix` instead of standalone `remediate_fix`
- `litellm` added as optional dependency (`pip install mcp_sdd[api]`)

References:

- plans/PLAN-030_versioned_remediation_copies.md
- plans/PLAN-031_api_executor_and_tool_surface.md

---

### v2.0.0 - Governance Expansion and Hard Enforcement

| Field | Value |
| --- | --- |
| Status | Future |
| Type | Major |
| Scope | Contract-governance expansion and strict release enforcement |

Planned scope:

- Introduce stronger contract-governance rules for documentation updates tied to runtime module changes.
- Define stricter evidence requirements for release readiness with explicit blocker categories.
- Consolidate policy and compliance artifacts into a normalized release reporting model.

Potential breaking considerations:

- Stronger mandatory gate enforcement may require process updates for documentation maintainers.
- Release checklist format changes may require downstream automation updates.

---

## Completed Releases

### v1.0.1 (2026-03-25)

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Patch |
| Summary | Script-based validation command and stage output path normalization |

Delivered:

- Added `validate` CLI command for script-based structural validation against layer schema/template assets.
- Added validation runner package under `mcp_sdd/src/mcp_server/validation/` with JSON/TXT report outputs.
- Standardized stage output root from `.ucx_create` to `.ucx` and validation stage from `validation` to `validate`.
- Updated CLI reference and test coverage for new command and stage-path behavior.
- Defined UCX_v1 compatibility command contracts in MCP CLI and docs:
  - `review` alias for `review-build`
  - Reserved `remediate`, `remediate-fix`, and `validate-fix` commands with explicit not-implemented status

References:

- architecture/MCP_CLI_REFERENCE.md
- CHANGELOG/CHANGELOG_v1.0.0.md

---

### v1.0.0 (2026-03-24)

| Field | Value |
| --- | --- |
| Status | Released |
| Type | Major |
| Summary | Initial MCP documentation program baseline |

Delivered:

- L0-L9 artifacts for architecture, specs, policies, runbook, and traceability.
- Reconciliation log and coverage matrix with PASS status.
- Compliance report updates and plan closure evidence for IPLAN-002.
- Initial changelog release record in CHANGELOG/CHANGELOG_v1.0.0.md.

References:

- plans/IPLAN-002_mcp_docs_full_layer_coverage.md
- plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md
- CHANGELOG/CHANGELOG_v1.0.0.md

---

## Constraints

- This roadmap covers documentation scope under mcp_sdd/docs.
- Runtime feature changes are out of scope unless separately approved and tracked.
- Release sequencing can change based on reconciliation outcomes and policy updates.
