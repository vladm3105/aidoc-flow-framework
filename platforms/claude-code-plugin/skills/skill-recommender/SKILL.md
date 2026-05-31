---
name: skill-recommender
description: Suggest the right aidoc-flow skill for a request by parsing user intent and matching it against the skill catalog with ranked, rationale-backed recommendations.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: []
    version: "0.2.0"
    framework_spec_version: "0.10.0"
    last_updated: "2026-05-23"
---

# skill-recommender

## Purpose

Recommend the appropriate aidoc-flow skill(s) for a request so users don't have
to know the full catalog. Parses intent, matches against the skill set, and
returns ranked recommendations with confidence and rationale.

**Layer**: cross-cutting utility (no artifacts produced or consumed).

## When to Use

**Use when**:

- The user is unsure which skill fits their documentation task.
- Starting a workflow and needing guidance on the next step.
- Discovering which skills cover a given intent.

**Do NOT use when**:

- The user names a specific skill (run it directly).
- The task is non-documentation work.

For full workflow routing, defer to `../doc-flow/SKILL.md`.

## Behavior

### Step 1 — Parse intent

Extract an action and a target from the request.

| Action | Signal keywords |
|--------|-----------------|
| create | create, write, draft, new, add |
| update | update, modify, edit, revise |
| validate | validate, check, verify, audit, review |
| analyze | analyze, examine, inspect |
| plan | plan, roadmap, schedule, organize |

| Target | Keywords | Maps to |
|--------|----------|---------|
| business requirements | business, brd, objectives | `doc-brd` |
| product requirements | product, prd, features, user stories | `doc-prd` |
| formal requirements | ears, when-the-shall | `doc-ears` |
| test scenarios | bdd, gherkin, scenarios | `doc-bdd` |
| architecture decisions | adr, decision | `doc-adr` |
| technical specification | spec, interfaces, data models | `doc-spec` |
| test definitions | tdd, test cases, thresholds | `doc-tdd` |
| implementation plan | iplan, file manifest, execution | `doc-iplan` |
| traceability | trace, links | `trace-check` |
| cross-document validation | validate, consistency | `doc-validator` |
| diagrams | diagram, chart, flow | `charts-flow` |
| roadmap | roadmap, adr implementation | `adr-roadmap` |
| naming / IDs | id, naming, format | `doc-naming` |
| new project | initialize, scaffold, greenfield | `project-init` |
| existing codebase | adopt, brownfield, existing code, reverse-engineer | `project-adopt` |
| tailor the flow to a project | adapt, profile, house style, skip layer, stricter gate, glossary | `project-profile` |
| promote a local adaptation | promote, extract, generalize, upstream, contribute back | `knowledge-extractor` |
| change to a published artifact | change, chg, modify existing, change request | `doc-chg` |
| approval gate | gate, approval, sign-off | `gate-check` |

### Step 2 — Match against the catalog (54 skills)

**Layer families** — each ships four variants: base, `-autopilot` (generate
end-to-end), `-audit` (quality gate), `-fixer` (apply audit fixes):

`doc-brd` · `doc-prd` · `doc-ears` · `doc-bdd` · `doc-adr` · `doc-spec` ·
`doc-tdd` · `doc-iplan` (× {base, -autopilot, -audit, -fixer} = 32 skills).

**Change-management family** — the CHG overlay for editing existing artifacts
(a governance overlay, not a layer), with the same four variants:

`doc-chg` (× {base, -autopilot, -audit, -fixer} = 4 skills).

**Utilities (18)**:

| Skill | Category | Role |
|-------|----------|------|
| `doc-flow` | core-workflow | Workflow orchestrator / routing |
| `project-init` | core-workflow | Scaffold a new project (greenfield) |
| `project-adopt` | utility | Adopt SDD into an existing codebase (brownfield) |
| `project-profile` | utility | Create/maintain the project adaptation profile (`.aidoc/profile.yaml`) |
| `knowledge-extractor` | utility | Draft a promotion proposal from profile + learnings |
| `gate-check` | utility | Run CHG approval gates; prepare sign-off |
| `doc-naming` | utility | ID & naming authority |
| `doc-ref` | utility | Reference (REF) documents |
| `doc-review` | utility | Cross-cutting quality review |
| `doc-validator` | utility | Cross-document validation |
| `trace-check` | utility | Bidirectional traceability |
| `charts-flow` | utility | Mermaid diagrams |
| `adr-roadmap` | utility | Roadmaps from ADRs |
| `context-analyzer` | utility | Project context analysis |
| `quality-advisor` | utility | Quality advice |
| `skill-recommender` | utility | This skill |
| `workflow-optimizer` | utility | Workflow optimization |
| `security-audit` | utility | Security analysis |

### Step 3 — Score and rank

Weight intent match (40%), target match (30%), context fit (20%), and common
sequences (10%). Classify confidence: **High** ≥80%, **Medium** 50–79%,
**Low** <50% (suggest clarification).

### Step 4 — Recommend

Return up to 3 ranked entries, each with `skill`, `confidence`, `rationale`,
and a `next_steps` or `condition`. When the intent is ambiguous, ask one
clarifying question instead of guessing.

```yaml
recommendations:
  - skill: doc-prd
    confidence: 92%
    rationale: "Request mentions 'product requirements' — direct PRD match."
    next_steps: "Run doc-prd to create the PRD."
  - skill: doc-brd
    confidence: 55%
    rationale: "A BRD may be needed upstream if none exists."
    condition: "Use if no BRD covers this feature."
clarification_needed: false
```

## Related Resources

- Workflow routing: `../doc-flow/SKILL.md`
- Project context input: `../context-analyzer/SKILL.md`
- Workflow position awareness: `../workflow-optimizer/SKILL.md`
- Layer registry: `framework/registry/LAYER_REGISTRY.yaml`
