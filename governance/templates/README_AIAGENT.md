# AI Agent Rules

Universal rules for **any AI assistant** working on this project: GitHub Copilot, {AI_TOOL_NAME} Code, Gemini, Cursor, GPT, or other agents.

> **Tool-specific config**: {AI_TOOL_NAME} Code users also follow [CLAUDE.md](CLAUDE.md) for MCP server and session-specific instructions.

---

## 1. Read Before You Code

Before making any changes, read these files in order:

1. **This file** (`README_AIAGENT.md`) — Universal rules (you are here)
2. **[GOVERNANCE_RULES.md](governance/GOVERNANCE_RULES.md)** — Operational policies, naming conventions, security posture
3. **[PROJECT_PLAN.md](governance/PROJECT_PLAN.md) Section 2** — Current state: what is done, what is next
4. **[governance/plans/README.md](governance/plans/README.md)** — Active implementation plans (IPLAN index)

When tasks involve retrieval, MCP, or knowledge indexing, also read:

5. **[ucx_knowledge/README.md](ucx_knowledge/README.md)** — UCX Knowledge Base setup and operations

Knowledge operation modes:
- **File-only mode**: use direct file reads/search; no DB/MCP runtime.
- **Indexed mode**: start `ucx_knowledge` DB + MCP for RAG/Graph retrieval.

Do **NOT** invent process rules, naming conventions, or workflow patterns. If a rule is missing from governance docs, flag it to the human reviewer. Do not create ad-hoc rules.

---

## 2. Project Context

| Field | Value |
|:------|:------|
| Project | {PROJECT_NAME} |
| Prefix | `{PROJECT_PREFIX}` |
| Organization | {GITHUB_ORG} |
| GitHub Enterprise | `{GITHUB_HOST}` |
| Home Cloud | GCP |
| Home Repo | `{REPO_NAME}` (docs, governance, issues, and all component code) |
| Code Dirs | Component code under `components/` |
| Project Board | [#{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER}) |
| Timezone | EST ({TIMEZONE}) for all schedules and timestamps |

### Repository Architecture

This is a **monorepo** project. All documentation, governance, and component source code live in this single repository under `components/`:

| Component | Phase | Purpose |
|:----------|:-----:|:--------|
| `components/{SERVICE_NAME}` | 1 | GCP budget alerts + auto-remediation |
| `components/infrastructure` | 2 | Terraform modules |
| `components/mcp-servers` | 3 | MCP servers (data access) |
| `components/agents` | 4 | AI agents (Google ADK) |
| `components/frontend` | 5 | Next.js + CopilotKit |

---

## 3. Prohibited Actions

These are **hard rules**. Violation requires immediate correction.

| Rule | Reason |
|:-----|:-------|
| Do not use Slack | Project uses Microsoft Teams and Email only |
| Do not use service account JSON keys (`GCP_SA_KEY`) | Workload Identity Federation only (ADR-002) |
| Do not use `ai:approved` or `ai:rejected` labels | These labels do not exist in this project |
| Do not use `services.delete` for Cloud Run | Scale-to-0 only (destructive action, irreversible) |
| Do not create issues in component repos | All issues tracked in the home repo |
| Do not force-push to `main` | All changes via PR, minimum 1 review |
| Do not invent naming conventions | Check [GOVERNANCE_RULES.md Section 4](governance/GOVERNANCE_RULES.md#4-naming-conventions) |
| Do not commit secrets or credentials | No `.env`, API keys, tokens, or SA key files |
| Do not delete governance docs or plans | Mark as `Superseded`, never delete |
| Do not skip tests to unblock a PR | Fix the tests instead |
| Do not use marketplace actions in GitHub Actions workflows | GitHub Connect is unreliable on GHES v3.12.4. Use inline shell commands instead. See [GOVERNANCE_RULES.md §2a](governance/GOVERNANCE_RULES.md#2a-no-marketplace-actions-mandatory) |

---

## 4. Required Practices

These must be followed in all AI-generated work.

### Git & GitHub

| Practice | Detail |
|:---------|:-------|
| GitHub Enterprise host | Always use `{GITHUB_HOST}` (not github.com) |
| `gh` CLI prefix | `GH_HOST={GITHUB_HOST} gh ...` |
| Co-author attribution | All AI commits include: `Co-Authored-By: <Agent Name> <noreply@provider.com>` |
| Branch protection | Never commit directly to `main`. Create a PR. |
| PR linked to issue | Use `Closes #N` in PR body |
| PR reviewer required | Auto-assigned via [CODEOWNERS](.github/CODEOWNERS); fallback: assign from [CONTRIBUTING.md §Reviewers](CONTRIBUTING.md#reviewer-roster). At least 1 reviewer per PR. |
| On-demand PR review | Use formal GitHub Reviews API with fix-and-verify loop. See [AI_AGENT_REVIEW_WORKFLOW.md](governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md) |
| Issue dependencies | Use `Blocks #X`, `Depends on #Y`, `Closes #Z` in issue body text |

### AI Label Lifecycle

```
ai:ready  →  ai:in-progress  →  ai:review-requested  →  PR merge
```

| Label | Set By | Meaning |
|:------|:-------|:--------|
| `ai:ready` | Human | Task is specified and ready for AI work |
| `ai:in-progress` | AI/Automation | AI is actively working |
| `ai:review-requested` | AI/Automation | AI work complete, human review needed |

There are **no** `ai:approved` or `ai:rejected` labels. PR approval status handles this.

### Issue Status Sync (Mandatory)

When changing an issue's AI label, **always also update the issue's Status on Project Board [#{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER})**. Labels and board status are two separate systems — one does not update the other. See [GOVERNANCE_RULES.md §3](governance/GOVERNANCE_RULES.md#3-ai-workflow) for option IDs and the GraphQL mutation.

### Issue Processing Workflow (Mandatory)

When picking up a GitHub issue labeled `ai:ready`, follow this **4-phase workflow** before writing any implementation code:

| Phase | Action | Output |
|:------|:-------|:-------|
| **1. Issue Analysis** | Read issue body, acceptance criteria, linked issues, related docs, existing code | Full understanding of scope and constraints |
| **2. Create Plan** | Create `governance/plans/IPLAN-NNN_{slug}.md` with steps, AC mapping, risks | Implementation plan file |
| **3. Review & Refine** | Re-read plan, identify gaps, verify all ACs are mapped, improve | Refined plan (status: Approved) |
| **4. Transition** | Execute Pre-Implementation Checklist below | Ready to code |

**Full details**: [GOVERNANCE_RULES.md §3 Issue Processing Workflow](governance/GOVERNANCE_RULES.md#issue-processing-workflow-mandatory)

**Do NOT skip phases.** Rushing to implementation without analysis and planning produces lower-quality work and causes rework.

### Pre-Implementation Checklist (Mandatory)

**After completing the Issue Processing Workflow above**, execute all of these steps in sequence, in the same turn:

1. **Change label**: `ai:ready` → `ai:in-progress`
2. **Update board status** → In Progress via GraphQL mutation (see [GOVERNANCE_RULES.md §3](governance/GOVERNANCE_RULES.md#3-ai-workflow) for option IDs)
3. **Create branch**: `ai/{issue}-{slug}` from `main`

**Never start implementation while the issue is still labeled `ai:ready`.** The transition to `ai:in-progress` + board "In Progress" is the gate for starting work.

### Post-PR Checklist (Mandatory)

**Immediately after creating a PR** (`gh pr create`), execute all of these steps in sequence, in the same turn:

1. **Verify** each acceptance criterion in the linked issue (read files, run tests, query APIs) — never blind-mark
2. **Check off** verified criteria in the issue body (`- [ ]` → `- [x]`)
3. **Change label**: `ai:in-progress` → `ai:review-requested`
4. **Update board status** → In Review via GraphQL mutation (see [GOVERNANCE_RULES.md §3](governance/GOVERNANCE_RULES.md#3-ai-workflow) for option IDs)
5. **Post PR link** as comment on the linked issue (PR#, URL, branch, date)

**Never leave an issue in `ai:in-progress` after a PR has been created.** The transition to `ai:review-requested` is part of PR creation, not a separate step.

**On-demand AI review note**: If performing on-demand AI review with fix loop, also post conclusion comment and apply `ai:review-passed` or `ai:review-failed` PR label per [AI_AGENT_REVIEW_WORKFLOW.md §7d-8](governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md).

### Document Sync

After completing a sprint or any significant/breaking change, review and update:
- [ROADMAP.md](governance/ROADMAP.md) — Phase dates, statuses, dependencies
- [RELEASE_PROCESS.md](governance/RELEASE_PROCESS.md) — Release workflow, tooling conventions
- [PROJECT_PLAN.md](governance/PROJECT_PLAN.md) — Task statuses, schedule, gap analysis

---

## 5. Naming Conventions

| Entity | Pattern | Example |
|:-------|:--------|:--------|
| Repos | `{PROJECT_PREFIX}-{component}` | `{PROJECT_PREFIX}-{SERVICE_NAME}` |
| Feature branches | `feature/{name}` | `feature/budget-alerts` |
| Bugfix branches | `bugfix/{name}` | `bugfix/threshold-calc` |
| Hotfix branches | `hotfix/{name}` | `hotfix/pubsub-retry` |
| AI branches | `ai/{issue}-{name}` | `ai/24-costguarded-llm` |
| Issues | `[P{phase}-{task_id}] {title}` | `[P1-1.0] Create repo` |
| GCP resources | `{PROJECT_PREFIX}-{env}-{resource}` | `{GCP_PROJECT_DEV}-cloud-run` |
| Implementation plans | `IPLAN-NNN_{slug}.md` | `IPLAN-001_phase1-issue-review.md` |
| MCP servers | `{function}-tt-{PROJECT_PREFIX}` | `github-{PROJECT_PREFIX}-{PROJECT_PREFIX}` |
| Sprints | `Sprint N.M` | `Sprint 2.1` |

---

## 6. Security Rules

| Rule | Detail | Reference |
|:-----|:-------|:----------|
| Authentication | Workload Identity Federation (WIF) for all GCP auth | ADR-002 |
| CI/CD secrets | `GCP_PROJECT_ID`, `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT` only | Never `GCP_SA_KEY` |
| Branch protection | `main` is protected. No force-push. Minimum 1 PR review. | BRANCHING_STRATEGY.md |
| AI trust boundary | AI has **no access** to: SA keys, API tokens, production databases, customer data, billing credentials | ROLES_AND_TOOLS.md |
| Service remediation | Scale-to-0 only. Never `services.delete`. | GCP-COST-GUARD.md |
| Communication | Teams/Email only. Alternative: {COMMUNICATION_TOOL_ALT} webhooks or integrations. | GOVERNANCE_RULES.md Section 1 |

---

## 7. Code Standards

### Python (Backend, Agents, MCP Servers)

| Standard | Tool/Config |
|:---------|:------------|
| Formatter | `ruff format` |
| Linter | `ruff check` |
| Type checker | `mypy --strict` |
| Tests | `pytest` with coverage |
| Security | `bandit` static analysis |
| Python version | 3.11+ |

### TypeScript (Frontend)

| Standard | Tool/Config |
|:---------|:------------|
| Framework | Next.js |
| Linter | ESLint |
| Tests | Jest / Playwright |
| Node version | 18+ |

### General

- Write unit tests for all new functions
- Do not introduce OWASP Top 10 vulnerabilities (SQLi, XSS, command injection)
- Validate at system boundaries (user input, external APIs), trust internal code
- Prefer simple, minimal changes over over-engineering
- Do not add features, refactor, or "improve" beyond what was requested

---

## 8. AI Suitability by Task Size

| Size | AI Role | Human Role |
|:-----|:--------|:-----------|
| XS/S | Autonomous | Review only |
| M | Autonomous with checkpoints | Review + test |
| L | AI-assisted | Leads implementation |
| XL | Human-led | AI provides research/scaffolding |

---

## 8.1 Document Review

Document review and validation is handled by mcp_ucx tools:

- **Validation**: `sdd_validate` — structural and schema compliance checks
- **Link validation**: `sdd_validate_links` — markdown link integrity
- **Review**: `sdd_review` — LLM-powered semantic review
- **Remediation**: `sdd_remediate` — automated fix application
- **Full lifecycle**: `sdd_run_lifecycle` — create → validate → review → fix pipeline

---

## 9. Implementation Plans (IPLAN)

When making cross-cutting changes, dependency reorders, or sprint corrections, create an implementation plan:

- **Location**: `governance/plans/IPLAN-NNN_{slug}.md`
- **Index**: [governance/plans/README.md](governance/plans/README.md)
- **Lifecycle**: Draft → Approved → In Progress → Complete → Superseded
- **Current next ID**: Check the plan index for the latest number

Required frontmatter:
```markdown
# IPLAN-NNN: Title

**Phase**: N (or "Cross-phase")
**Status**: Draft | Approved | In Progress | Complete | Superseded
**Created**: YYYY-MM-DD
**Issues**: #X-#Y or list of affected issues
**Epic**: #N (parent epic)
**Applies Before**: When this plan must be executed by
```

---

## 10. Quick Reference Links

| I need to... | Read |
|:-------------|:-----|
| Process a GitHub issue | [GOVERNANCE_RULES.md §3 Issue Processing Workflow](governance/GOVERNANCE_RULES.md#issue-processing-workflow-mandatory) |
| Check completion criteria | [DEFINITION_OF_DONE.md](governance/DEFINITION_OF_DONE.md) |
| Find operational rules | [GOVERNANCE_RULES.md](governance/GOVERNANCE_RULES.md) |
| Know which branch to create | [BRANCHING_STRATEGY.md](governance/BRANCHING_STRATEGY.md) |
| Tag and release a component | [RELEASE_PROCESS.md](governance/RELEASE_PROCESS.md) |
| Understand human vs AI split | [ROLES_AND_TOOLS.md](governance/ROLES_AND_TOOLS.md) |
| Find task specs and schedule | [PROJECT_PLAN.md](governance/PROJECT_PLAN.md) |
| See phase timeline | [ROADMAP.md](governance/ROADMAP.md) |
| Find architecture decisions | [docs/adr/](docs/adr/) (8 ADRs) |
| Read technical specs | [docs/core/](docs/core/) (8 specs) |
| See execution corrections | [governance/plans/](governance/plans/) (IPLAN index) |
| Understand Phase 1 | [GCP-COST-GUARD.md](docs/GCP-COST-GUARD.md) |
| Run UCX Knowledge Base | [ucx_knowledge/README.md](ucx_knowledge/README.md) |
| Configure KB databases | [ucx_knowledge/docker-compose.db.yml](ucx_knowledge/docker-compose.db.yml) |
| Use KB MCP tools | [ucx_knowledge/mcp/README.md](ucx_knowledge/mcp/README.md) |
| Validate documents | mcp_ucx `sdd_validate` and `sdd_validate_links` tools |

---

## 11. Context Durability

AI assistants lose context as sessions grow. These practices prevent rule drift:

| Practice | Implementation |
|:---------|:---------------|
| Read-first protocol | Read this file and GOVERNANCE_RULES.md before starting work |
| No ad-hoc rules | Consult governance docs, not memory. Missing rules are flagged, not invented. |
| Single source of truth | Each rule lives in ONE canonical location. Cross-references use links, not copies. |
| Plan audit trail | IPLANs capture deviations so future sessions understand why things changed |

**When adding new rules**, follow this hierarchy:
1. Add the rule to its canonical governance doc
2. If critical "never/always", add a one-liner to this file (Section 3 or 4)
3. If it gates completion, add a checklist item to DEFINITION_OF_DONE.md

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.9 | {DATE} | SDD v3.2 in `ucx_flow_v3/` is the active governance baseline |
| 1.8 | {DATE} | Added mandatory Issue Processing Workflow (4-phase: analyze → plan → review/refine → implement) — AI agents must create IPLAN before coding |
| 1.7 | {DATE} | Added on-demand AI review note to Post-PR Checklist — conclusion comment + PR label per AI_AGENT_REVIEW_WORKFLOW.md §7d-8 |
| 1.6 | {DATE} | Consolidated acceptance criteria sync and PR link into mandatory Post-PR Checklist — all 5 steps must execute immediately after PR creation |
| 1.5 | {DATE} | Added prohibited marketplace actions rule — all workflows must be self-contained due to unreliable GitHub Connect on GHES v3.12.4 |
| 1.4 | {DATE} | Added on-demand PR review reference — formal GitHub Reviews API with fix-and-verify loop |
| 1.3 | {DATE} | Added mandatory Acceptance Criteria Sync rule — AI must check off criteria before requesting review |
| 1.2 | {DATE} | Added mandatory PR reviewer assignment rule — AI must assign reviewer from CONTRIBUTING.md maintainers list |
| 1.1 | {DATE} | Added mandatory Issue Status Sync rule — AI must update Project Board status alongside labels |
| 1.0 | {DATE} | Initial creation — universal AI agent rules extracted from CLAUDE.md and GOVERNANCE_RULES.md |
