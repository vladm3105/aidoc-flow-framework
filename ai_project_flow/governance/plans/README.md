# Implementation Plans (IPLAN)

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)

Implementation plans are session-scoped execution documents that capture analysis, decisions, and concrete change lists applied during development. They sit between the static [PROJECT_PLAN.md](../PROJECT_PLAN.md) (what to build) and GitHub issues (tracking units).

---

## When to Create a Plan

| Trigger | Example |
|:--------|:--------|
| Pre-sprint issue review | Review issues before sprint start, capture corrections |
| Dependency or ordering change | Reorder tasks based on new information |
| Technical investigation result | Spike or research that changes approach |
| Mid-sprint scope adjustment | Descope, split, or add tasks during execution |
| Cross-phase coordination | Changes that affect multiple phases |
| Incident or blocker resolution | Document workaround and follow-up actions |

Do **not** create a plan for:
- Single-issue fixes with no cross-cutting impact
- Routine code reviews or PR feedback
- Changes already captured in an ADR

---

## Naming Convention

```
IPLAN-NNN_{descriptive_slug}.md
```

| Component | Rule | Example |
|:----------|:-----|:--------|
| Prefix | Always `IPLAN` | `IPLAN` |
| Number | Sequential, zero-padded to 3 digits | `001`, `002`, `015` |
| Slug | Lowercase, hyphens, describes the action | `phase1-issue-review` |
| Extension | Always `.md` | `.md` |

Full example: `IPLAN-003_mcp-server-dependency-reorder.md`

---

## Required Frontmatter

Every plan starts with these fields:

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

## Lifecycle

```
Draft ──→ Approved ──→ In Progress ──→ Complete
                │                         │
                └──→ Superseded ←─────────┘
                     (by IPLAN-NNN)
```

| Status | Meaning |
|:-------|:--------|
| **Draft** | Analysis in progress, not yet reviewed |
| **Approved** | Reviewed and accepted, ready to execute |
| **In Progress** | Changes are being applied to issues/code |
| **Complete** | All checklist items done, no open actions |
| **Superseded** | Replaced by a newer plan (link to replacement) |

Update the status field in the plan file as it progresses.

---

## Plan Structure

Recommended sections (adapt per plan type):

| Section | Purpose |
|:--------|:--------|
| **Purpose** | One paragraph: what this plan addresses |
| **Findings** | Numbered list of issues found (with severity) |
| **Corrected Dependency Graph** | Before/after if dependencies changed |
| **Revised Schedule** | Updated daily/sprint schedule if timing changed |
| **Change Execution Checklist** | Concrete `- [ ]` items to apply |
| **Version History** | Track revisions to the plan itself |

The checklist is the most important section. Each item must be independently actionable and reference a specific GitHub issue or file.

---

## Plan Templates

Use these templates as starting points for your implementation plans:

| Template | Purpose | Use When |
|:---------|:--------|:---------|
| [IPLAN-TEMPLATE.md](IPLAN-TEMPLATE.md) | Blank template | Creating any new IPLAN |
| [IPLAN-001_phase-issue-review.md](IPLAN-001_phase-issue-review.md) | Pre-sprint issue audit | Starting a new phase/sprint |
| [IPLAN-002_ai-pr-review-workflow.md](IPLAN-002_ai-pr-review-workflow.md) | AI review setup | Configuring AI code review |
| [IPLAN-003_phase-gated-deployment.md](IPLAN-003_phase-gated-deployment.md) | Deployment pipeline | Setting up CI/CD environments |

## Plan Index

Track your project's IPLANs here. Copy the template row and update for each new plan.

| ID | Title | Phase | Status | Date |
|:---|:------|:------|:-------|:-----|
| IPLAN-001 | _{Your first plan}_ | 1 | Draft | {DATE} |
| IPLAN-002 | _{Your second plan}_ | 1 | Draft | {DATE} |
| ... | ... | ... | ... | ... |

**Status Key**: Draft → Approved → In Progress → Complete (or Superseded)

---

## Relationship to Other Governance Docs

```
ROADMAP.md          ← What to build (phases, timeline)
  │
PROJECT_PLAN.md     ← How to build it (tasks, specs, schedule)
  │
governance/plans/   ← Execution adjustments (this directory)
  │
GitHub Issues       ← Tracking units (updated per plan checklists)
```

Plans do not replace or duplicate PROJECT_PLAN.md. They document **deviations and corrections** applied during execution. If a plan results in significant PROJECT_PLAN changes, update PROJECT_PLAN.md and reference the IPLAN that drove the change.

### Governance Document Sync Rule

After completing an IPLAN (or after every sprint/significant change), review and update:
- **[ROADMAP.md](../ROADMAP.md)** — Phase dates, statuses, dependencies
- **[RELEASE_PROCESS.md](../RELEASE_PROCESS.md)** — Release workflow, tooling conventions
- **[PROJECT_PLAN.md](../PROJECT_PLAN.md)** — Task statuses, schedule, gap analysis

This keeps governance docs close to reality at all times. See [DEFINITION_OF_DONE.md](../DEFINITION_OF_DONE.md) for the full review checklist.

---

## AI Context Durability

This project uses an AI-first development approach. AI assistants lose context as sessions grow due to context window limits. These practices prevent rule drift and inconsistency:

| Practice | Implementation |
|:---------|:---------------|
| **Auto-loaded guardrails** | `README_AIAGENT.md` (universal, all agents) + `CLAUDE.md` (Claude-specific) — always in context at session start |
| **Read-first protocol** | `CLAUDE.md` instructs AI to read GOVERNANCE_RULES.md and PROJECT_PLAN.md §2 before starting work |
| **No ad-hoc rules** | AI must consult governance docs, not invent conventions. Missing rules are flagged, not created. |
| **Single source of truth** | Each rule lives in ONE canonical location. Cross-references use links, not copies. |
| **Compact references** | GOVERNANCE_RULES.md Quick Reference provides "I need to → Read this" lookup |
| **Session memory** | `~/.claude/projects/.../memory/MEMORY.md` persists key IDs and learnings across sessions |
| **Plan audit trail** | IPLANs capture deviations so future sessions can understand why things changed |

When adding new rules, follow this hierarchy:
1. Add the rule to its canonical doc (GOVERNANCE_RULES.md, BRANCHING_STRATEGY.md, etc.)
2. If it's a critical "never do" or "always do", add a one-liner to README_AIAGENT.md (and CLAUDE.md if Claude-specific)
3. If it affects sprint/phase completion, add a checklist item to DEFINITION_OF_DONE.md

---

## Retention

- Keep all plans permanently in the repository (they form an audit trail)
- Mark completed plans as `Complete` but do not delete them
- If a plan is no longer relevant, mark it `Superseded` and link to the replacement
