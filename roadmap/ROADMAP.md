# docs_flow_framework Roadmap

| Field | Value |
| --- | --- |
| Current Version | 0.20.0 |
| Latest Release | 0.20.0 (SDD v3.2 — 8-layer streamlined framework with C4 mapping) |
| Previous Minor | 0.19.0 (multi-persona mapping support) |
| Next Major | 1.0.0 (full multi-MCP ecosystem with governance and knowledge base) |
| Timezone | America/New_York |

---

## Version Timeline

```text
v0.1.0 ──► v0.2.x ──► v0.3-v0.5 ──► v0.6.0 ──► v0.7.0 ──► v0.8-v0.19 ──► v0.20.0 ──► v1.0.0
  │           │             │            │           │            │              │           │
  │           │             │            │           │            │              │           └─► Multi-MCP
  │           │             │            │           │            │              └─► SDD v3.2 (8-layer, C4 mapping)
  │           │             │            │           │            └─► REQ→SPEC→TSPEC→TASKS unification + UCX features
  │           │             │            │           └─► SYS unification (6 layers, C4 Component)
  │           │             │            └─► ADR unification (decision bridge)
  │           │             └─► PRD + EARS + BDD unification + C4 mapping
  │           └─► BRD unification (v0.2.0) + mcp_sdd naming (v0.2.1)
  └─► MCP transport layer: 19 tools, CLI executor registry, pipeline orchestration
```

---

## Planned Releases

### v1.0.0 — Multi-MCP Ecosystem

| Field | Value |
| --- | --- |
| Status | Future |
| Type | Major |
| Scope | Full ecosystem with governance and knowledge base MCP servers |

Planned scope:

- MCP server: project-governance (versioned change management, CHG gate automation, MCP-level traceability)
- MCP server: project-knowledge — own implementation using SQLite FTS5 + semantic search + frontmatter-aware indexing
- Cross-server orchestration patterns
- Hard contract enforcement and quality gates
- SDD v3 MCP tool adaptation for 8-layer workflow

---

## Completed Releases

### v0.20.0 — SDD v3.2 Streamlined Framework (2026-04-29)

Collapsed from 14 layers to 8 layers with C4 architecture model mapping, TDD and IPLAN artifacts, and 5-gate CHG governance overlay. 39 new files in `ai_dev_flow_v3/`. See changelog/CHANGELOG_v0.20.0.md.

### v0.19.0 — Multi-Persona Mapping Support (2026-04-02)

mcp_sdd v1.12.0: multi-persona mapping support via persona_mappings.yaml. See changelog/CHANGELOG_v0.19.0.md.

---

### v0.18.0 - Unified Report Naming Standard

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | mcp_sdd v1.11.0: unified report naming, sub-framework registry, legacy cleanup |

Delivered scope:

- `{DOC-ID}.{STAGE}.{FORMAT}` naming convention
- Sub-framework codes: sdd, gov, kb
- REPORT_NAMING_STANDARDS.md framework standard
- 1,089 legacy reports deleted from b-local-docs

References:

- mcp_sdd/docs/plans/PLAN-021_sdd_reporting_naming_standard.md
- mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.11.0.md

---

### v0.17.0 - UCX Root Relocation

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | mcp_sdd v1.10.0: relocate UCX from docs/UCX to project root UCX |

Delivered scope:

- Centralized resolve_ucx_root() with backward-compatible fallback
- Auto-migration in sdd_init
- 22 files updated, 2 projects migrated

References:

- mcp_sdd/docs/plans/PLAN-020_ucx_root_relocation.md
- mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.10.0.md

---

### v0.16.0 - Remediation Build Enhancement

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | mcp_sdd v1.9.0: review report parsing for structured remediation findings |

Delivered scope:

- Review report parser (frontmatter + 3 table formats)
- Parsed findings in remediation report (was single pointer)
- Fix prompt: 742 chars → ~10K chars with per-finding actions
- 18 new tests (205 total)

References:

- mcp_sdd/docs/plans/PLAN-019_remediation_build_enhancement.md
- mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.9.0.md

---

### v0.15.0 - YAML Parity and API Consistency

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-04-02 |
| Scope | mcp_sdd v1.8.0: YAML document support across all tools, categorized scoring, API normalization |

Delivered scope:

- YAML source/derived artifact detection in sdd_consistency and sdd_next_action
- Categorized scoring: structural (20pt), cross-section (10pt), warning (5pt)
- Result class .report/.is_valid/.is_ready property aliases
- YAML structure validation in sdd_remediate
- Shared utils/source_files.py collector
- 24 new tests (187 total)

References:

- mcp_sdd/docs/plans/PLAN-018_yaml_parity_and_api_consistency.md
- mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.8.0.md

---

### v0.14.0 - Cross-Section Validation and BRD Template Improvements

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | mcp_sdd v1.7.0: two-tier cross-section validation, YAML document support, BRD template enhancements |

Planned scope:

- Generic cross-section validation rules in `sdd_validate` for all 11 SDD layers (traceability ID existence, readiness score plausibility, diagram registry)
- BRD-specific cross-section rules (ADT propagation, phase alignment, entity consistency, currency scope)
- YAML document support in validation pipeline
- BRD-TEMPLATE.yaml: `diagrams` section, `cross_section_rules` metadata
- BRD-MD-TEMPLATE.md: standardized YAML-to-MD rendering
- DIAGRAM_STANDARDS.md: BRD required diagram list, DFD-L1 standardization
- Extensible pattern for future layer-specific rules (PRD, SPEC)

References:

- mcp_sdd/docs/plans/PLAN-016_cross_section_validation.md
- mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.7.0.md

---

### v0.13.0 - API Executors and Progress Notifications

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | LiteLLM API executor implementation and MCP progress reporting |

Planned scope:

- Implement api_runner.py with litellm.acompletion() as universal gateway
- Support 100+ LLM providers: OpenAI, Anthropic, Google, Azure, Bedrock, Ollama, local models
- MCP progress notifications for long-running executor calls
- Configurable timeout per tool call

---

---
### v0.13.0 (2026-03-31)

3-segment element IDs: TYPE.NN.hash replaces TYPE.NN.TT.hash. Element type codes deprecated (YAML keys provide context). All templates, prompts, skills, and framework docs updated. AUTOPILOT archived. See changelog/CHANGELOG_v0.13.0.md.

### v0.12.1 (2026-03-30)

Framework cleanup + sdd_validate_links tool (20th MCP tool). Archived deprecated infrastructure (validation scripts, automation, schema docs). Fixed ~130 stale references across 30+ active docs. CLI executor configs fixed for non-interactive file writes (Claude Code, Codex). See changelog/CHANGELOG_v0.12.1.md.

### v0.12.0 (2026-03-30)

TASKS template unification — FINAL LAYER. All 11 SDD layers unified. Session handoff protocol for stateless MCP calls. Full 10-layer upstream chain verification. 11 unified YAML templates in mcp_sdd. See changelog/CHANGELOG_v0.12.0.md.

### v0.11.0 (2026-03-30)

TSPEC template unification. Parent aggregator for 6 test subtypes (UTEST, ITEST, STEST, FTEST, PTEST, SECTEST). 10 layers unified. See changelog/CHANGELOG_v0.11.0.md.

### v0.10.0 (2026-03-29)

SPEC template unification. C4 Code level complete — all four C4 levels unified. SPEC orchestrator routes to 5 subtypes (CSPEC, DSPEC, UXSPEC, RISKSPEC, PROCSPEC). See changelog/CHANGELOG_v0.10.0.md.

### v0.9.0 (2026-03-29)

CTR template unification. Dual-file contracts (.md + .yaml OpenAPI). First CTR template added to mcp_sdd. ADR-CTR policy refs updated. See changelog/CHANGELOG_v0.9.0.md.

### v0.8.0 (2026-03-29)

REQ template unification. All 7 mcp_sdd templates now unified YAML — no `*-MVP-TEMPLATE.*` files remain. Atomic single-testable-concept requirement principle. See changelog/CHANGELOG_v0.8.0.md.

### v0.7.0 (2026-03-29)

SYS template unification. First C4 Component level layer. Consolidated 6 SYS files into `SYS-TEMPLATE.yaml` (437 lines, 12 sections + glossary). Six quality attribute categories with measurable metrics. Diagram tags: c4-l3, dfd-l3. See changelog/CHANGELOG_v0.7.0.md.

### v0.6.0 (2026-03-29)

ADR template unification. Consolidated 6 ADR files into single `ADR-TEMPLATE.yaml` (466 lines, 10 sections + glossary + lifecycle appendix). ADR serves as decision bridge between Container (PRD) and Component (SYS). Originating topic points to PRD Section 14. Active ADR instances kept in directory. See changelog/CHANGELOG_v0.6.0.md for details.

### v0.5.0 (2026-03-29)

BDD template unification. Consolidated BDD `.feature` + `.yaml` dual-file into single `BDD-TEMPLATE.yaml` (365 lines, 5 sections). Gherkin syntax embedded in `_example` fields. Four SDD layers unified: BRD (Context), PRD (Container), EARS (transition), BDD (transition). See changelog/CHANGELOG_v0.5.0.md for details.

### v0.4.0 (2026-03-29)

EARS template unification. Consolidated 6 EARS files into single `EARS-TEMPLATE.yaml` (387 lines, 5 sections + glossary). Incorporated PRD EARS appendix content (timing profiles, boundary values). Split BRD downstream EARS/BDD into separate entries. See changelog/CHANGELOG_v0.4.0.md for details.

### v0.3.0 (2026-03-29)

PRD template unification + C4 model mapping. Consolidated 6 PRD files into single `PRD-TEMPLATE.yaml` (605 lines, 15 sections). Added C4 architecture model mapping to BRD and PRD templates (Context→Container→Component→Code). EARS appendix preserved for Layer 3 migration. See changelog/CHANGELOG_v0.3.0.md for details.

### v0.2.1 (2026-03-29)

MCP SDD template naming migration. Updated 5 source files (10 occurrences) to support unified `{ARTIFACT}-TEMPLATE.yaml` naming with backward-compatible fallback to legacy `{ARTIFACT}-MVP-TEMPLATE.*`. Added resolution helper, 4 migration tests. See changelog/CHANGELOG_v0.2.1.md for details.

### v0.2.0 (2026-03-28)

BRD template unification. Consolidated 4 BRD files (dual templates + creation rules + validation rules) into single `BRD-TEMPLATE.yaml` with embedded authoring guidance, hash-based element IDs, and streamlined 15-section structure. See changelog/CHANGELOG_v0.2.0.md for details.

### v0.1.0 (2026-03-28)

MCP protocol transport layer. See changelog/CHANGELOG_v0.1.0.md for details.

---

## Constraints

- This roadmap covers the docs_flow_framework repository only
- Project-specific roadmaps (ibmcp, b_local, trading) live in their own repos
- Release sequencing can change based on implementation outcomes
