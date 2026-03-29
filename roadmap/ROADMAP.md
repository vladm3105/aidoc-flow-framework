# docs_flow_framework Roadmap

| Field | Value |
| --- | --- |
| Current Version | 0.6.0 |
| Latest Release | 0.6.0 (ADR template unification — 5 layers complete) |
| Next Minor | 0.7.0 (API executors via LiteLLM, MCP progress notifications) |
| Next Major | 1.0.0 (full multi-MCP ecosystem with governance and knowledge base) |
| Timezone | America/New_York |

---

## Version Timeline

```text
v0.1.0 ──► v0.2.x ──► v0.3.0 ──► v0.4.0 ──► v0.5.0 ──► v0.6.0 (Current) ──► v0.7.0 ──► v1.0.0
  │           │           │           │           │           │                     │           │
  │           │           │           │           │           │                     │           └─► Multi-MCP
  │           │           │           │           │           │                     └─► API executors
  │           │           │           │           │           └─► ADR unification (5 layers complete)
  │           │           │           │           └─► BDD template unification
  │           │           │           └─► EARS template unification
  │           │           └─► PRD template unification + C4 model mapping
  │           └─► BRD unification (v0.2.0) + mcp_sdd naming (v0.2.1)
  └─► MCP transport layer: 19 tools, CLI executor registry, pipeline orchestration
```

---

## Planned Releases

### v0.7.0 - API Executors and Progress Notifications

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

### v1.0.0 - Multi-MCP Ecosystem

| Field | Value |
| --- | --- |
| Status | Future |
| Type | Major |
| Scope | Full ecosystem with governance and knowledge base MCP servers |

Planned scope:

- MCP server: project-governance (GitHub Projects tasks, IPLANs, governance rules)
- MCP server: project-knowledge — own implementation using SQLite FTS5 + semantic search + frontmatter-aware indexing, built on existing `project_knowledge/mcp/server.py` foundation (concept inspired by markdown-vault-mcp, dependency rejected due to project maturity risk)
- Cross-server orchestration patterns
- Hard contract enforcement and quality gates

---

## Completed Releases

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
