# Implementation Plans (IPLAN)

Implementation plans are session-scoped execution documents that capture analysis, decisions, and concrete change lists applied during development. They sit between the project planning documents and GitHub issues.

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
Draft → Approved → In Progress → Complete

               → Superseded ←
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

## Templates

| Template | Purpose |
|:---------|:--------|
| [IPLAN-TEMPLATE.md](./IPLAN-TEMPLATE.md) | Blank template for creating new IPLANs |

---

## Plan Index

Track your project's IPLANs here. Copy the template row and update for each new plan.

| ID | Title | Phase | Status | Date |
|:---|:------|:------|:-------|:-----|
| _IPLAN-001_ | _{Your first plan}_ | 1 | Draft | _{DATE}_ |

**Status Key**: Draft → Approved → In Progress → Complete (or Superseded)

---

## Related Documents

| Document | Purpose |
|:---------|:--------|
| [GOVERNANCE_RULES.md](../GOVERNANCE_RULES.md) | Operational rules |
| [DEFINITION_OF_DONE.md](../DEFINITION_OF_DONE.md) | Completion checklists |
| [BRANCHING_STRATEGY.md](../BRANCHING_STRATEGY.md) | Git workflow |
| [templates/](../templates/) | Project templates |

---

## Retention

- Keep all plans permanently in the repository (they form an audit trail)
- Mark completed plans as `Complete` but do not delete them
- If a plan is no longer relevant, mark it `Superseded` and link to the replacement
