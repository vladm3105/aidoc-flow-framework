# UCX Framework Skills

This directory contains the **framework default** persona skills for UCX document reviews.

## Skill Loading Priority (v1.8.0+)

Skills are loaded with the following priority:

| Priority | Location | Description |
|----------|----------|-------------|
| 1 | `{project}/docs/UCX/skills/` | Project-specific skills (preferred) |
| 2 | `/UCX/skills/` (this directory) | Framework defaults (fallback) |

**Key Behavior**:
- If a project has `docs/UCX/skills/auditor.md`, that file is used
- If not found, `/UCX/skills/auditor.md` (this file) is used as fallback
- Prompts are project-specific ONLY (no fallback)

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

## Creating Project-Specific Skills

To customize skills for your project:

```bash
# Create project skills directory
mkdir -p {project}/docs/UCX/skills/

# Copy and customize specific skills
cp /opt/data/docs_flow_framework/UCX/skills/auditor.md \
   {project}/docs/UCX/skills/auditor.md

# Edit to add domain-specific knowledge
# Example: Add FinCEN, OFAC focus for fintech
```

## Verification

To verify skills are loaded from the correct location:

```bash
UCX_LOG_LEVEL=DEBUG ucx review brd docs/01_BRD/BRD-01/

# Project skills:
# "Loaded project-specific skill: auditor from .../docs/UCX/skills"

# Framework fallback:
# "Loaded framework skill (fallback): auditor"
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

Part of UCX Framework v1.14.3+
