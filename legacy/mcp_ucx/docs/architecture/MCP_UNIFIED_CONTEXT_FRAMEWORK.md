# UCX — Unified Context eXcelerator

> **Aliases**: `ucx`, `mcp_ucx`, `sdd-lifecycle`. Package directory: `mcp_ucx/`. The legacy `UCX_v1` archive is a historical predecessor, not the current system.

| Field | Value |
| --- | --- |
| Canonical Name | UCX (Unified Context eXcelerator) |
| Status | Active |
| Version | 1.4 |
| Date | 2026-04-07 |
| Scope | AI agent orchestration platform — per-project context management, persona assembly, and executor pipelines for any AI agent |

---

## 1. Purpose

UCX is an AI agent orchestration platform that creates and manages context for AI agents (Claude Code, Gemini CLI, GitHub Copilot, Codex, OpenRouter) in respect to each project's needs. It provides per-project customized personas, prompts, templates, and validation rules consumed uniformly by any agent through MCP tools or CLI.

UCX serves as the unified wrapper for agent skills and prompts — skills are project-specific, not agent-specific. Any AI agent calls UCX to get the right context for a specific project.

Implementation complexity: 3/5.

### 1.1 Architecture Layers

| Layer | Status | Purpose |
| --- | --- | --- |
| Context Engine | Active | Per-project personas, prompts, templates, layer assets |
| Deterministic QA | Active | Validators, scoring, consistency checks, link validation |
| Executor Registry | Active | Pluggable AI agents: Claude, Gemini, Codex, OpenRouter via CLI and API executors |
| Workflows/Pipelines | Planned | Chained agent tasks for continuous development and automated bug fixing |

---

## 2. Framework Boundaries

In scope:

- deterministic CLI orchestration for create, review, validate, validate-fix, remediate, remediate --fix, prescreen, scan, scoring, and clean
- project-local asset loading from `UCX`
- schema-governed JSON/TXT artifact generation under `.ucx/<stage>`
- operator runbook and policy controls under `mcp/docs`
- per-project context assembly for any AI agent (agent-agnostic prompt delivery)
- pluggable executor registry for CLI and API agents

Out of scope:

- autopilot orchestration loops (planned for workflows/pipelines layer)
- non-deterministic automatic content rewriting of source files
- legacy archive runtime dependencies

---

## 3. Canonical Runtime Surface

Primary command groups:

- create: `create-build`
- review: `review-build`, `review`
- validate: `validate`, `validate-fix`
- remediation: `remediate`, `remediate --fix`
- maintenance: `clean`
- diagnostics: `prescreen`, `scan`, `scoring`

Primary implementation paths:

- `mcp_ucx/src/mcp_server/cli/main.py`
- `mcp_ucx/src/mcp_server/review/runner.py`
- `mcp_ucx/src/mcp_server/validation/runner.py`
- `mcp_ucx/src/mcp_server/remediation/runner.py`
- `mcp_ucx/src/mcp_server/prescreening/runner.py`
- `mcp_ucx/src/mcp_server/scan/runner.py`
- `mcp_ucx/src/mcp_server/scoring/runner.py`

---

## 4. Skills and Persona Architecture

### 4.1 Project Isolation Model

UCX uses a project isolation model for all AI skills assets. Skills are project-specific, not agent-specific — each project receives independent copies at initialization time. Any AI agent (Claude, Gemini, Copilot, Codex) calls UCX to get the right personas, prompts, and templates for that specific project. The runtime operates exclusively with project-specific files.

**Initialization** (`sdd_init`):

| Framework Source | Project Destination | Contents |
| --- | --- | --- |
| `mcp_ucx/skills/personas/` | `{project}/UCX/skills/personas/` | 15 persona definition files |
| `mcp_ucx/skills/persona_mappings.yaml` | `{project}/UCX/skills/persona_mappings.yaml` | Per-doctype, per-phase persona sequence configuration |
| `mcp_ucx/skills/layer_aliases/` | `{project}/UCX/skills/layer_aliases/` | Layer alias mappings |
| `mcp_ucx/prompts/templates/creation/` | `{project}/UCX/prompts/templates/creation/` | UCC creation prompt templates |
| `mcp_ucx/prompts/templates/review/` | `{project}/UCX/prompts/templates/review/` | UCR review prompt templates |
| `mcp_ucx/prompts/templates/remediation/` | `{project}/UCX/prompts/templates/remediation/` | UCRem remediation prompt templates |
| `mcp_ucx/templates/` + `ucx_flow_v3/` | `{project}/UCX/templates/` | Document templates and layer-specific schemas |

**Update mode** (`sdd_init --update`):

- Syncs stale templates and prompts with latest framework versions.
- `persona_mappings.yaml` is project-owned and protected from overwrite. Use `--update-mappings` to explicitly reset it.
- `PROTECTED_PROJECT_FILES` in `scaffold.py` defines the protected set.

**Runtime contract**:

1. Framework scaffold sources (`mcp_ucx/skills/`, `mcp_ucx/prompts/templates/`) are never loaded by the runtime directly.
2. All MCP tools resolve personas, prompts, and templates exclusively from the active project's `UCX/` directory.
3. If project-specific files are absent, the runtime raises `ProjectSkillsNotFound` with actionable resolution guidance. No fallback to framework defaults occurs.
4. Preflight checks (`sdd_preflight`) run a persona mapping health check when `persona_mappings.yaml` is present: verifies all referenced persona `.md` files exist and reports missing doctypes compared to framework defaults.

### 4.2 Multi-Persona System

UCX uses a multi-persona mapping system. Each tool call loads one or more personas as a list, not a single persona. The `persona_mappings.yaml` file defines per-doctype, per-phase persona sequences.

**Persona resolution** (2-tier priority):

1. Explicit `personas` parameter on the tool call or CLI (highest priority).
2. `persona_mappings.yaml` lookup by `(doc_type, phase)` pair (default).

There is no single `persona` parameter. All tools and CLI commands accept only `personas` (list/array).

Each persona is a Markdown file defining role-specific domain knowledge injected into LLM prompts at assembly time. Personas contain: role description, core principles, anti-patterns to flag, review focus areas, review questions, scoring weights per layer, and category tags.

Complete persona registry (15):

| Persona | Role | Category | Finding Prefix |
| --- | --- | --- | --- |
| `architect` | System Architect — scalability, CAP theorem, SPOF | technical | ARCH |
| `auditor` | Compliance Auditor — regulatory, security | compliance | AUD |
| `tech_lead` | Tech Lead — implementation, idempotency | technical | TL |
| `strategist` | Business Strategist — economics, unit economics | functional | STR |
| `chaos_engineer` | Chaos Engineer — failure modes, edge cases | risk | CE |
| `operator` | DevOps/SRE — observability, deployment | operations | OP |
| `integration_lead` | Integration Lead — API versions, webhooks | integration | IL |
| `product_owner` | Product Owner — MVP scope, user personas | functional | PO |
| `business_analyst` | Business Analyst — requirements, traceability | functional | BA |
| `fact_checker` | Fact Checker — cross-validation | quality | FC |
| `chairperson` | Chairperson — synthesis, scoring | quality | REM |
| `qa_lead` | QA Lead — testability, BDD | quality | QA |
| `requirements_specialist` | Requirements Specialist — EARS, REQ formal requirements | functional | RS |
| `ux_strategist` | UX Strategist — PRD, UX-focused requirements | functional | UX |
| `judge` | Judge — high-stakes approvals, external audit | compliance | JDG |

During remediation, personas use adaptive loading: domain personas are loaded only when review findings match their registered categories.

### 4.2.1 Persona Management Tools

Three MCP tools for inspecting and modifying project-specific persona-to-layer mappings:

| MCP Tool | CLI Command | Purpose |
| --- | --- | --- |
| `sdd_personas_show` | `personas-show` | Display persona assignments per phase/doctype |
| `sdd_personas_set` | `personas-set` | Update persona list for a phase+doctype with validation |
| `sdd_personas_diff` | `personas-diff` | Compare project mappings against framework defaults |

`sdd_personas_set` validates that all referenced persona `.md` files exist before writing. It preserves the YAML header comments and uses flow-style lists to match the canonical format. After writing, it invalidates the mtime-based persona mapping cache. Supports `_default` as doc_type for remediation fallback entries.

`persona_mappings.yaml` is project-owned after initialization. The `PROTECTED_PROJECT_FILES` mechanism in `scaffold.py` prevents `sdd_init --update` from overwriting it.

### 4.3 Prompt Assembly Pipeline

LLM-dependent tools (`sdd_create`, `sdd_review`, `sdd_remediate` with `fix=true`) assemble prompts from multiple project-local sources:

1. **Persona files** — loaded from `{project}/UCX/skills/personas/{persona}.md` for each persona in the resolved list
2. **Phase template** — loaded from `{project}/UCX/prompts/templates/{phase}/{template}.md`
3. **Actionable rules** — deterministic rules injected by the assembly engine
4. **Layer assets** — `*-TEMPLATE.*` and `*_MVP_SCHEMA.yaml` from `{project}/UCX/templates/layers/{layer}/`
5. **Bundle metadata** — JSON inspection and sidecar metadata for diagnostics

During review, document sections are categorized (functional, compliance, risk, technical, integration, quality, operations, metadata) and mapped to the persona's focus areas. Each persona receives only the sections relevant to its domain.

### 4.4 Executor Integration

UCX's executor system is the key enabler for multi-agent support. Assembled prompts can be executed via registered executors, making UCX agent-agnostic:

- **CLI executors**: External tools (Claude Code, Codex, Gemini CLI, GitHub Copilot) invoked via subprocess with the prompt passed as a positional argument
- **API executors**: LLM API providers (Claude, GPT-4, OpenRouter) invoked via LiteLLM. OpenRouter is a built-in executor with native support in the executor registry.

All CLI executors use the same delivery mechanism: the prompt text is appended as a positional argument to the executor command. There is no stdin or file-based fallback.

If no executor is specified, the tool returns the assembled prompt text for manual use by any agent or API call.

Non-MCP agents access UCX via CLI parity: every MCP tool has a CLI equivalent (`python -m mcp_server.cli.main <command>`), so agents without MCP support can still use the context engine.

### 4.5 Default Project Resolution

Tools that require `project` resolve it from a 4-level fallback chain before dispatch:

| Priority | Source | Scope |
| --- | --- | --- |
| 1 | Explicit `project` argument | Per call |
| 2 | `sdd_set_project` session override | Per MCP server process |
| 3 | `SDD_DEFAULT_PROJECT` env var | Per shell/environment |
| 4 | `executors.json` `default_project` field | Per config file |

Injection happens in `handle_tool()` before `configure_logging`, guarded by `_PROJECT_TOOLS` frozenset. Non-project tools (`sdd_scan`, `sdd_consistency`) are not affected. `_handle_lifecycle_pipeline` calls `_dispatch()` with the already-injected `arguments` dict.

### 4.6 Project Environment Isolation

Each project can provide a `.env` file at the project root containing API keys and provider credentials. The environment manager (`env_manager.py`) loads these automatically when executors are invoked.

| Aspect | Behavior |
| --- | --- |
| Loading | `dotenv_values()` — parses `.env` without modifying `os.environ` |
| Caching | mtime-based per project root — reload only when file changes |
| Merge order | `os.environ` < `config.env` < `project_env` (.env wins) |
| Blocked vars | `PATH`, `HOME`, `PYTHONPATH`, `LD_LIBRARY_PATH`, `LD_PRELOAD`, `SHELL`, `USER`, `IFS` |
| Missing `.env` | Returns empty dict — executor inherits parent environment |
| Inspection | `sdd_env_show` / `env-show` — reports keys only, never values |
| Preflight | Reports `env_key_count`, `env_keys`, `env_blocked_vars` |

Multi-project safety: each `--project` argument resolves to an independent cache entry. Switching between projects within a session loads the correct `.env` automatically.

---

## 5. Contract Rules

1. Command behavior must be deterministic for identical inputs.
2. Source-protected fix flow is the default behavior.
3. Output artifact locations use `.ucx/<stage>` conventions.
4. Test-backed command behavior is required for release acceptance.
5. Documentation must track runtime behavior in the same change set.
6. Framework scaffold sources are used only by `sdd_init`; they are never loaded at runtime.

---

## 6. Failure Modes

| Failure Mode | Detection | Required Response |
| --- | --- | --- |
| Missing project assets | loader validation | fail command with actionable path guidance |
| Invalid payload shape | parse/contract stage | fail command with deterministic error output |
| Required schema violations | validation stage | non-zero validation result with report artifacts |
| Output write failure | artifact write stage | fail command with I/O error |

---

## 7. References

- `mcp_ucx/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
- `mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
- `mcp_ucx/docs/specs/SPEC-008_mcp_output_schema_contracts.md`
- `mcp_ucx/docs/policies/MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md`
