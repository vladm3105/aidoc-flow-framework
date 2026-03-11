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

## Available Skills

| Skill | Role | Focus |
|-------|------|-------|
| `architect.md` | System Architect | Scalability, CAP theorem, SPOF |
| `auditor.md` | Compliance Auditor | Regulatory, security, compliance |
| `tech_lead.md` | Tech Lead | Implementation, state machines, idempotency |
| `strategist.md` | Business Strategist | Economics, unit economics, float |
| `devils_advocate.md` | Devil's Advocate | Edge cases, failure modes |
| `operator.md` | DevOps/SRE | Observability, deployment, runbooks |
| `integration_expert.md` | Integration Lead | API versions, webhooks, circuit breakers |
| `product_owner.md` | Product Owner | MVP scope, user personas |
| `business_analyst.md` | Business Analyst | Requirements quality, traceability |
| `fact_checker.md` | Fact Checker | Cross-validation, false positives |
| `chairperson.md` | Chairperson | Synthesis, scoring, final verdict |
| `qa_lead.md` | QA Lead | Testability, BDD syntax |
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

## Version

Part of UCX Framework v1.8.0+
