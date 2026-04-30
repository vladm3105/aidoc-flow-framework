# UCX Framework Skills — Canonical Scaffold Source

This directory contains the **canonical scaffold source** for persona skills. These files are copied into each project during `sdd_init` and are **never loaded by the runtime directly**.

## Project Isolation Model (v1.8.0+)

UCX uses a **project isolation** model with no runtime fallback to framework defaults.

### Initialization (`sdd_init`)

`sdd_init --project <path>` copies all personas, prompts, templates, and layer assets from this framework directory into the project's `{project}/UCX/` directory. Existing files are never overwritten (idempotent).

| Framework Source | Project Destination |
|---|---|
| `mcp_ucx/skills/personas/` | `{project}/UCX/skills/personas/` |
| `mcp_ucx/skills/layer_aliases/` | `{project}/UCX/skills/layer_aliases/` |
| `mcp_ucx/prompts/templates/creation/` | `{project}/UCX/prompts/templates/creation/` |
| `mcp_ucx/prompts/templates/review/` | `{project}/UCX/prompts/templates/review/` |
| `mcp_ucx/prompts/templates/remediation/` | `{project}/UCX/prompts/templates/remediation/` |
| `mcp_ucx/templates/` + `ai_dev_ssd_flow/` layers | `{project}/UCX/templates/` |

### Runtime Loading

At runtime, all MCP tools resolve personas, prompts, and templates **exclusively from the project's UCX directory**:

- `{project}/UCX/skills/personas/{persona}.md`
- `{project}/UCX/prompts/templates/{phase}/{template}.md`
- `{project}/UCX/templates/layers/{layer}/`

**No fallback to framework defaults occurs.** If required project-specific files are missing, the runtime raises `ProjectSkillsNotFound` with the message: *"Run mcp init --project {project_root} to create project-specific files."*

### Customization

After initialization, each project owns its UCX assets independently. Teams can customize personas, prompts, and templates in `{project}/UCX/` without affecting other projects or the framework source.

## Persona Mappings

`persona_mappings.yaml` defines the default persona list for each doc-type. When `personas` is omitted from a create-build or review-build command, the runtime resolves the applicable persona list from this file. Each entry maps a doc-type key to an ordered list of persona identifiers.

Location (framework scaffold source): `mcp_ucx/skills/persona_mappings.yaml`
Location (project runtime): `{project}/UCX/skills/persona_mappings.yaml`

## Available Skills (12 Core Personas)

| Skill | Role | Focus | Finding Prefix |
|-------|------|-------|----------------|
| `architect.md` | System Architect | Scalability, CAP theorem, SPOF | ARCH |
| `auditor.md` | Compliance Auditor | Regulatory, security, compliance | AUD |
| `tech_lead.md` | Tech Lead | Implementation, state machines, idempotency | TL |
| `strategist.md` | Business Strategist | Economics, unit economics, float | STR |
| `chaos_engineer.md` | Chaos Engineer | Failure modes, edge cases, fault injection | CE |
| `operator.md` | DevOps/SRE | Observability, deployment, runbooks | OP |
| `integration_lead.md` | Integration Lead | API versions, webhooks, circuit breakers | IL |
| `product_owner.md` | Product Owner | MVP scope, user personas | PO |
| `business_analyst.md` | Business Analyst | Requirements quality, traceability | BA |
| `fact_checker.md` | Fact Checker | Cross-validation, false positives | FC |
| `chairperson.md` | Chairperson | Synthesis, scoring, final verdict | REM |
| `qa_lead.md` | QA Lead | Testability, BDD syntax, test coverage | QA |

**Extended Personas** (not in VALID_PERSONAS, available as templates):
| Skill | Role | Focus |
|-------|------|-------|
| `content_strategist.md` | Content Strategist | Documentation clarity, audience alignment, terminology consistency |
| `requirements_specialist.md` | Requirements Specialist | EARS/INCOSE syntax |
| `ux_strategist.md` | UX Strategist | User journeys, accessibility |

## Skill File Structure

Each skill file should contain:

```markdown
# {Role} Domain Knowledge

## Role
Brief description of the persona's role.

## Core Principles / Focus Areas
Domain-specific knowledge and guidelines.

## Common Anti-Patterns to Flag
What this persona should look for.

## Review Focus
- Bullet points of review focus areas

## Review Questions
1. Key questions to answer
2. ...

## Scoring Weight (optional)
- BRD: X%
- PRD: X%

## Tags
- phase: ucr
- doc_types: [brd, prd, ...]
- priority: high
```

## Customizing Project Skills

After running `sdd_init`, customize skills in the project's own UCX directory:

```bash
# Initialize project (copies all framework defaults to project)
mcp init --project /path/to/project

# Edit project-specific personas
# Example: Add FinCEN, OFAC focus for fintech auditor
vi /path/to/project/UCX/skills/personas/auditor.md
```

Do not edit files in `mcp_ucx/skills/personas/` for project-specific changes. Edit only the project copy under `{project}/UCX/skills/personas/`.

## Verification

```bash
UCX_LOG_LEVEL=DEBUG ucx review brd docs/01_BRD/BRD-01/

# Expected: loads from project UCX
# "Loaded project-specific skill: auditor from .../UCX/skills/personas"

# If project assets missing:
# "ProjectSkillsNotFound: Run mcp init --project ... to create project-specific files."
```

## Finding ID Format (v1.13.0+)

All persona findings must use the canonical format: `PREFIX-P0-NNN`

| Persona | Prefix | Example |
|---------|--------|---------|
| Architect | ARCH | `ARCH-P0-001` |
| Auditor | AUD | `AUD-P0-001` |
| Tech Lead | TL | `TL-P1-001` |
| Chaos Engineer | CE | `CE-P0-001` |
| QA Lead | QA | `QA-P1-001` |
| Chairperson | REM | `REM-P0-001` |

**Format rules**:
- `PREFIX`: 2-4 character persona abbreviation
- `P0/P1/P2`: Priority level
- `NNN`: 3-digit sequence (001-999)

See `chairperson.md` and `operator.md` for examples with explicit Finding ID tables.

## Version History

- **v1.14.3**: Added `qa_lead` persona, renamed `devils_advocate` to `chaos_engineer`
- **v1.13.0**: Finding ID format, context engineering

## Architectural Contract

These rules are normative (from IPLAN-001):

1. `mcp_ucx/skills/` and `mcp_ucx/prompts/templates/` are the canonical scaffold source used by `sdd_init` to create project-specific UCX files; they are never loaded by the runtime directly.
2. At runtime, the MCP resolves all skills, personas, and prompt templates exclusively from the active project's UCX directory.
3. If project-specific skills, personas, or prompt templates are absent at runtime, the MCP raises `ProjectSkillsNotFound`. No fallback to MCP bundled templates occurs.

Part of UCX Framework v1.14.3+
