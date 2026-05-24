# Permanent Development Plans (PLAN)

This directory stores permanent project development plans used to coordinate and track implementation work across sessions.

These plans are not the same artifact as SDD document-layer IPLAN (Layer 8). Use the following taxonomy:

| Plan Type | Purpose | Location | Retention |
|---|---|---|---|
| Document-layer IPLAN | SDD implementation bridge from TDD/SPEC to code | Project SDD lifecycle output (`docs/IPLAN/`, `UCX/08_IPLAN/`, or equivalent) | Permanent |
| Permanent development plan | Operational project development planning and execution history | `plans/` (this directory) | Permanent |
| Temporary plan | Bug fixes and minor corrections with no long-term tracking value | `tmp/` | Disposable |

---

## When to Create a Permanent Development Plan

| Trigger | Example |
|:--------|:--------|
| Pre-sprint issue review | Review issues before sprint start, capture corrections |
| Dependency or ordering change | Reorder tasks based on new information |
| Technical investigation result | Spike or research that changes approach |
| Mid-sprint scope adjustment | Descope, split, or add tasks during execution |
| Cross-phase coordination | Changes that affect multiple phases |
| Incident or blocker resolution | Document workaround and follow-up actions |

Do **not** create a permanent development plan for:

- Single-issue fixes with no cross-cutting impact
- Routine code reviews or PR feedback
- Changes already captured in an ADR

For those cases, use a temporary plan in `tmp/` when planning is still needed.

---

## Naming Convention

Preferred naming:

```
PLAN-NNN_{descriptive_slug}.md
```

Compatibility naming (existing repositories may still use this pattern):

```
IPLAN-NNN_{descriptive_slug}.md
```

| Component | Rule | Example |
|:----------|:-----|:--------|
| Prefix | Preferred: `PLAN` (legacy: `IPLAN`) | `PLAN`, `IPLAN` |
| Number | Sequential, zero-padded to 3 digits | `001`, `002`, `015` |
| Slug | Lowercase, hyphens, describes the action | `phase1-issue-review` |
| Extension | Always `.md` | `.md` |

Full example: `PLAN-003_mcp-server-dependency-reorder.md`

---

## Required Frontmatter

Every permanent development plan starts with these fields:

```markdown
# PLAN-NNN: Title

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
                     (by PLAN-NNN)
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
| [IPLAN-TEMPLATE.md](./IPLAN-TEMPLATE.md) | Blank execution-plan template (supports both preferred `PLAN-*` and legacy `IPLAN-*` naming) |

---

## Plan Index

Track your project's permanent development plans here. Copy the template row and update for each new plan.

| ID | Title | Phase | Status | Date |
|:---|:------|:------|:-------|:-----|
| _PLAN-001_ | _{Your first plan}_ | 1 | Draft | _{DATE}_ |

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

- Keep all permanent development plans in the repository (they form development history and audit context)
- Mark completed plans as `Complete` but do not delete them
- If a plan is no longer relevant, mark it `Superseded` and link to the replacement
- Keep temporary plans out of this directory; store them under `tmp/`
