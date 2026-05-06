# {AI_TOOL_NAME} Code Project Instructions

## Session Start Protocol

Before starting any implementation or governance work, read these files in order:
1. `README_AIAGENT.md` — Universal AI agent rules (applies to all AI tools)
2. `governance/GOVERNANCE_RULES.md` — Operational rules (naming, security, AI workflow)
3. `governance/PROJECT_PLAN.md` §2 (Current State Analysis) — What's done, what's next
4. `governance/plans/README.md` — Permanent development plan index and plan taxonomy

Do NOT invent process rules, naming conventions, or workflow patterns. If uncertain, consult the governance docs above. If a rule is missing, flag it — do not create ad-hoc rules.

## AI Operating Rules

### Never Do
- Use Slack — Teams/Email only per governance policy
- Use service account JSON keys (`GCP_SA_KEY`) — Workload Identity Federation only
- Use `ai:approved` or `ai:rejected` labels (they do not exist)
- Use `services.delete` for Cloud Run remediation (scale-to-0 only)
- Create issues in component repos (all issues in home repo only)
- Force-push to `main` or commit directly (all changes via PR)
- Invent naming conventions — check §4 of GOVERNANCE_RULES.md
- Use unreviewed workflow actions without version pinning — marketplace actions are allowed when pinned and reviewed (see GOVERNANCE_RULES.md §2a)

### Always Do
- Prefix `gh` commands with `GH_HOST={GITHUB_HOST}`
- Use EST ({TIMEZONE}) for all schedules and timestamps
- Follow AI label lifecycle: `ai:ready` → `ai:in-progress` → `ai:review-requested` → PR merge
- Treat Hermes as control plane and coding agents as execution plane for approved `ai:ready` issues
- **When changing a label, also update the issue's Status on Project Board #{PROJECT_BOARD_NUMBER}** — labels and board status are separate systems (see GOVERNANCE_RULES.md §3 for option IDs and GraphQL mutation)
- Include `Co-Authored-By: {AI_TOOL_NAME} <{AI_TOOL_EMAIL}>` in commits
- **Assign at least one reviewer on every PR** from [CONTRIBUTING.md §Reviewer Roster](CONTRIBUTING.md#reviewer-roster) (`--reviewer <username>`)
- Create permanent development plans as `governance/plans/PLAN-NNN_{slug}.md` (preferred; check plans/README.md for next ID)
- Use document-layer IPLAN (`IPLAN-NNN_{slug}.md`) only for SDD Layer-8 bridge artifacts
- **After every PR review, cross-post review summary to the linked issue** for audit trail (see GOVERNANCE_RULES.md §3 Issue Review History)
- **After on-demand AI PR review**: post conclusion comment and apply `ai:review-passed` or `ai:review-failed` label (see AI_AGENT_REVIEW_WORKFLOW.md §7d-8)
- After completing a sprint or significant change: review ROADMAP.md, RELEASE_PROCESS.md, PROJECT_PLAN.md
- Redirect stderr when piping `gh api graphql` to Python: `2>/dev/null` or `> file && python3`

### Issue Processing Workflow (Mandatory — execute when picking up any `ai:ready` issue)

When processing a GitHub issue, follow this 5-phase workflow **before writing any implementation code**:

```
Phase 1: Issue Analysis
   Read issue body, acceptance criteria, comments
   Read linked/dependent issues (Depends on #X, Blocks #Y)
   Read related governance docs, ADRs, specs
   Review existing code that will be modified

Phase 2: Create Planning Package
   Create planning roadmap for issue scope
   Create planning index listing required plan artifacts
   Define changelog plan for issue scope

Phase 3: Review Planning Gaps
   Re-read planning package as if seeing it for the first time
   Identify gaps: missing artifacts, dependencies, unclear actions
   Resolve gaps or defer with explicit rationale

Phase 4: Create Implementation Plan
   Create required plan artifact(s):
   - governance/plans/PLAN-NNN_{slug}.md (preferred permanent development plan)
   - document-layer IPLAN (`IPLAN-NNN_{slug}.md`) when SDD Layer-8 artifact is required
   Document: scope, steps, acceptance criteria mapping
   Include: risks, edge cases, testing approach

Phase 5: Review & Refine Plan
   Re-read plan as if seeing it for the first time
   Identify gaps: missing steps, unclear actions
   Verify: every acceptance criterion has a mapped step
   Update plan with improvements

   Record explicit plan approval (human reviewer or independent LLM-as-judge session)

Transition to Implementation
   Execute Pre-Implementation Checklist below only after approval
```

**Full details**: See [GOVERNANCE_RULES.md §3 Issue Processing Workflow](governance/GOVERNANCE_RULES.md#issue-processing-workflow-mandatory)

### Pre-Implementation Checklist (Mandatory — execute after completing Issue Processing Workflow)

Do all of these steps in sequence, in the same turn, before any code changes:

1. **Change label**: `ai:ready` → `ai:in-progress`
2. **Update board status** → In Progress (option ID `{BOARD_OPTION_IN_PROGRESS}`) via GraphQL mutation
3. **Create branch**: `ai/{issue}-{slug}` from `main`

**Never start implementation while the issue is still labeled `ai:ready`.** The transition to `ai:in-progress` + board "In Progress" is the gate for starting work.
**Never transition to implementation before the planning package and IPLAN are approved.**

### Post-PR Checklist (Mandatory — execute immediately after `gh pr create`)

Do all of these steps in sequence, in the same turn, right after creating a PR:

1. **Verify** each acceptance criterion in the linked issue (read files, run tests, query APIs) — never blind-mark
2. **Check off** verified criteria in the issue body (`- [ ]` → `- [x]`)
3. **Change label**: `ai:in-progress` → `ai:review-requested`
4. **Update board status** → In Review (option ID `{BOARD_OPTION_IN_REVIEW}`) via GraphQL mutation
5. **Post PR link** as comment on the linked issue (PR#, URL, branch, date)

**Never leave an issue in `ai:in-progress` after a PR has been created.** The transition to `ai:review-requested` + board "In Review" is part of PR creation, not a separate step.

**Note**: The automated CI AI review workflow (`ai-review-reusable.yml`) automatically posts a conclusion comment and applies `ai:review-passed` or `ai:review-failed` PR labels. No manual steps needed for automated reviews.

### Naming Conventions (Quick Reference)
- Repos: `{PROJECT_PREFIX}-{component}`
- Branches: `feature/{name}`, `bugfix/{name}`, `hotfix/{name}`, `ai/{issue}-{name}`
- Issues: `[P{phase}-{task_id}] {title}`
- GCP resources: `{PROJECT_PREFIX}-{env}-{resource}`
- Permanent development plans: `PLAN-NNN_{slug}.md` (preferred)
- Document-layer plans: `IPLAN-NNN_{slug}.md`
- Issue dependencies: `Blocks #X`, `Depends on #Y`, `Closes #Z` in body text

## MCP Server Policy

**IMPORTANT**: Use ONLY MCP servers defined in `{LOCAL_PROJECT_PATH}/{REPO_NAME}/.mcp.json`.

**DO NOT** use global MCP servers from parent directories (e.g., `/opt/data/.mcp.json`).

### Allowed MCP Servers

| Server | Purpose |
|--------|---------|
| `github-{PROJECT_PREFIX}` | GitHub Enterprise ({GITHUB_HOST}) |
| `git` | Git operations |
| `filesystem` | Project file access |
| `memory` | Session persistence |
| `sequential-thinking` | Complex reasoning |
| `fetch` | HTTP requests |
| `time` | Time utilities |
| `context7` | Documentation lookup |
| `postgres` | PostgreSQL database |
| `sqlite` | SQLite local database |
| `playwright` | Browser automation |
| `project-knowledge-tt-{PROJECT_PREFIX}` | UCX KB retrieval/graph tools (enabled when project initializes `ucx_kb`) |
| `aws` | AWS access |
| `teams` | Microsoft Teams |

`project-knowledge-tt-{PROJECT_PREFIX}` usage contract:

- Register by default from project template.
- Activate indexed KB flows only after project-level `ucx_kb` initialization is complete.
- If unavailable, continue file-only workflows and lifecycle gates.

## Project Context

- **Project**: {PROJECT_NAME}
- **Prefix**: `{PROJECT_PREFIX}`
- **Organization**: {GITHUB_ORG}
- **GitHub Enterprise**: {GITHUB_HOST}
- **Home Cloud**: GCP

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `governance/` | Project governance docs (setup, strategy, roadmap) |
| `governance/plans/` | Permanent development plans (`PLAN-*`, legacy `IPLAN-*`) |
| `docs/` | Technical documentation, ADRs, specs |
| `components/` | Component code ({SERVICE_NAME}, mcp-servers, agents, frontend, infrastructure) |
| `.mcp.json` | Development/governance MCP servers |

## GitHub Workflow

### Tool Strategy

| Tool | Type | When to Use |
|:-----|:-----|:------------|
| **GitHub MCP** (`github-{PROJECT_PREFIX}`) | Primary | Issues, PRs, branches, files, workflows |
| **gh CLI** | Fallback | Projects V2, labels, milestones, GraphQL |

### MCP Tools (Primary)

Use `ToolSearch` to load GitHub MCP tools before calling:

```python
# Load GitHub MCP tools first
ToolSearch(query="+github issue")

# Then call the tools
mcp__github-{PROJECT_PREFIX}__list_issues(owner="{GITHUB_ORG}", repo="{REPO_NAME}", labels=["ai:ready"])
mcp__github-{PROJECT_PREFIX}__issue_write(method="update", owner="...", repo="...", issue_number=123, labels=["ai:in-progress"])
mcp__github-{PROJECT_PREFIX}__create_pull_request(owner="...", repo="...", title="...", head="...", base="main")
mcp__github-{PROJECT_PREFIX}__add_issue_comment(owner="...", repo="...", issue_number=123, body="...")
```

### gh CLI (Fallback)

For operations not supported by MCP (Projects V2, labels, GraphQL):

```bash
# Always prefix with GH_HOST
GH_HOST={GITHUB_HOST} gh issue list --label "ai:ready"
GH_HOST={GITHUB_HOST} gh api graphql -f query='mutation {...}'
GH_HOST={GITHUB_HOST} gh label create "name" --color "hex"
```

### MCP vs CLI Decision

| Operation | Use MCP | Use gh CLI |
|:----------|:-------:|:----------:|
| Issue CRUD | [PASS] | |
| PR CRUD | [PASS] | |
| Create branch | [PASS] | |
| Push files (multi-file) | [PASS] | |
| Projects V2 board status | | [PASS] |
| Labels CRUD | | [PASS] |
| GraphQL mutations | | [PASS] |

### Project Board

- **Board**: [#{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER})
- **PR Review**: Follow [MANUAL_REVIEW_GUIDE.md](governance/AI_PR_Review/MANUAL_REVIEW_GUIDE.md) and [AI_AGENT_REVIEW_WORKFLOW.md](governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md)

## Communication

- **{COMMUNICATION_TOOL} only** - Alternative: {COMMUNICATION_TOOL_ALT}
- Use `teams` MCP server for Microsoft Teams integration

## References

- [README_AIAGENT.md](README_AIAGENT.md) - **Universal AI agent rules (all AI tools)**
- [GOVERNANCE_RULES.md](governance/GOVERNANCE_RULES.md) - Operational rules and quick reference index
- [DEFINITION_OF_DONE.md](governance/DEFINITION_OF_DONE.md) - Completion checklists
- [GITHUB_TOOLS_SETUP.md](governance/GITHUB_TOOLS_SETUP.md) - GitHub MCP and CLI setup
- [GITHUB_PROJECT_SETUP.md](governance/GITHUB_PROJECT_SETUP.md) - AI-optimized project workflow
- [REPOSITORY_STRATEGY.md](governance/REPOSITORY_STRATEGY.md) - Monorepo architecture
- [GITHUB_WORKFLOWS.md](governance/GITHUB_WORKFLOWS.md) - All GitHub Actions workflow documentation
- [MANUAL_REVIEW_GUIDE.md](governance/AI_PR_Review/MANUAL_REVIEW_GUIDE.md) - Manual AI PR review using local assistants
