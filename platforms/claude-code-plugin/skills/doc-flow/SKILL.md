---
name: doc-flow
description: Orchestrate the 8-layer SDD workflow - recommend the right skill for an intent, detect the current position and next steps, explain the BRD→…→Code flow, and enforce the upstream-artifact policy. Use when unsure what to do or which skill to run next.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: core-workflow
    upstream_artifacts: []
    downstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.4.0"
    framework_spec_version: "0.11.2"
    last_updated: "2026-05-27"
    adapts: [active_layers]
---

# doc-flow

## Purpose

Route the **Specification-Driven Development (SDD) workflow**: point at the
right skill for the task, report current position, enforce the
upstream-artifact policy. `doc-flow` never creates artifacts itself — the
artifact skills do.

**Layer**: cross-cutting (no upstream; routes into all 8 layers).
**Authoritative spec**: `${CLAUDE_PLUGIN_ROOT}/framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`.

## When to Use

| Situation | Action |
|-----------|--------|
| Unsure which skill applies | Use `doc-flow` (this) |
| Brand-new project | `../project-init/SKILL.md` first, then `doc-flow` |
| Adopting SDD into existing code | `../project-adopt/SKILL.md` first |
| Editing a published artifact | `../doc-chg/SKILL.md` — not the linear flow |
| Single-layer end-to-end generation | that layer's `-autopilot` |

## The 8-layer flow

```
BRD (1) → PRD (2) → EARS (3) → BDD (4) → ADR (5) → SPEC (6) → TDD (7) → IPLAN (8) → Code
```

| Layer | Artifact | Purpose | Base skill |
|-------|----------|---------|-----------|
| 1 | BRD | Business requirements | `doc-brd` |
| 2 | PRD | Product requirements & KPIs | `doc-prd` |
| 3 | EARS | Formal WHEN-THE-SHALL requirements | `doc-ears` |
| 4 | BDD | Gherkin test scenarios | `doc-bdd` |
| 5 | ADR | Architecture decisions | `doc-adr` |
| 6 | SPEC | Technical specifications | `doc-spec` |
| 7 | TDD | Test-case definitions & thresholds | `doc-tdd` |
| 8 | IPLAN | Executable implementation plan | `doc-iplan` |

Each layer ships **four** skills: base (create), `-autopilot` (end-to-end),
`-audit` (gate report), `-fixer` (apply audit fixes).

## Skill selection

| You have | You need | Use |
|----------|----------|-----|
| Nothing | Business requirements | `doc-brd` |
| BRD | Product requirements | `doc-prd` |
| PRD | Formal requirements | `doc-ears` |
| EARS | Test scenarios | `doc-bdd` |
| BDD | Architecture decisions | `doc-adr` |
| ADR | Technical specifications | `doc-spec` |
| SPEC | Test-case definitions | `doc-tdd` |
| TDD | Implementation plan | `doc-iplan` |
| IPLAN | Code | Implement |
| Any stage | Supplementary docs | `doc-ref` |

**Intent → skill** (when the layer is clear, pick by verb):

| Action | Skill |
|--------|-------|
| create / draft | layer's base or `-autopilot` |
| audit / score | layer's `-audit` |
| fix / remediate | layer's `-fixer` |
| validate / trace / links / orphans | `../doc-validator/SKILL.md` |
| change a published artifact | `../doc-chg/SKILL.md` + `../gate-check/SKILL.md` |
| roadmap / phasing | `../adr-roadmap/SKILL.md` |
| scaffold / new project | `../project-init/SKILL.md` |
| adopt / brownfield | `../project-adopt/SKILL.md` |
| tailor / profile | `../project-profile/SKILL.md` |
| security / threats | `../security-audit/SKILL.md` |

When the user names a skill, run it directly.

## Where you are & what's next

**Where you are.** Scan `docs/<NN>_<X>/` for artifacts; read each Document
Control `Status` (most layers `Draft → In Review → Approved`; IPLAN
`Draft → In Progress → Completed`). Map to the project's **active** layers
(see *Adaptation*); report position + progress = terminal-status artifacts ÷
active layers.

**Template-conformance check (mandatory).** For every artifact found, load
`${CLAUDE_PLUGIN_ROOT}/framework/layers/<NN>_<X>/<TYPE>-TEMPLATE.yaml` and
verify every required top-level section appears as a `##` heading. Report
missing sections as **drift findings** (`Status` notwithstanding), e.g.
*"BRD-01 missing 6 of 18 required sections: …"*. **Do not** rationalise
drift as a "compact" variant, "documented walkthrough", or "lint-pinned"
exception — one template, one canonical section list. Lint passing is the
structural subset, not full template conformance. Recommend
`doc-<layer>-fixer` (or `-autopilot` for a re-author) to close gaps.

**What's next.** Recommend the next artifact per the cumulative chain
(each layer needs its prerequisite). Prioritise:

- **P0** — required upstream missing OR next step on the critical-path spine.
- **P1** — next ready layer once P0 is unblocked.
- **P2** — optional / parallel work (extra ADRs, `doc-ref` supplements).

Surface parallel-work opportunities (independent tracks with no shared
prerequisite); name the skill to run for each.

**Context scan (before authoring).** Rank candidate upstream documents for
the target type by directness, topic match, recency, and `Approved` status;
collect project vocabulary (titles, headings, glossary) so the new document
reuses real IDs and consistent terms.

## Utility skills

| Skill | Use for |
|-------|---------|
| `../project-init/SKILL.md` | Scaffold a new project (run before any layer) |
| `../project-adopt/SKILL.md` | Adopt SDD into an existing codebase (brownfield) |
| `../project-profile/SKILL.md` | Tailor the flow (optional; sets `.aidoc/profile.yaml`) |
| `../doc-naming/SKILL.md` | ID / naming authority (`TYPE-NN`, `TYPE.NN.SS.xxxx`) |
| `../doc-ref/SKILL.md` | Free-format reference documents (BRD-REF / ADR-REF) |
| `../doc-validator/SKILL.md` | Cross-document validation + bidirectional traceability + prose review |
| `../review-team/SKILL.md` | Multi-persona review mode for audits / fixers / autopilots |
| `../quality-advisor/SKILL.md` | Real-time authoring guidance for a single document |
| `../charts-flow/SKILL.md` | Mermaid diagrams and file management |
| `../adr-roadmap/SKILL.md` | Implementation roadmaps from ADRs |
| `../security-audit/SKILL.md` | Security review (OWASP/CWE, STRIDE) |

## Change management

Changes to already-published artifacts use the **CHG overlay**, not the
linear flow. `../doc-chg/SKILL.md` (+ `-autopilot` / `-audit` / `-fixer`)
classifies the change (C1–C3 / Emergency) and routes it to the right gate;
`../gate-check/SKILL.md` runs the gate (GATE-01/03/06/08/CODE, or
**GATE-SPEC** for `framework/` spec changes) and prepares the sign-off
form. A human approves — the skill never does.

## Upstream-artifact policy

Do **NOT** invent missing upstream artifacts. Every artifact must trace to
a real business/product justification.

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with its exact ID |
| Required upstream missing | Skip; report; advise creating it first |
| Optional upstream missing | `null` in the tag |
| Not applicable | Omit the tag |

## Validation model

Each skill **is** the validator (no runtime code). After each artifact,
run that layer's `-audit`; before moving on, confirm cumulative upstream
tags are present (PRD→1 … IPLAN→7).

## Adaptation

Read `.aidoc/profile.yaml`. Honor `active_layers`: a disabled skippable
layer (BDD / ADR) is excluded from the critical path, the progress
denominator, and next-step recommendations. Ignore unknown keys; absent
a profile, use the full 8-layer flow.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Reading bundled files

Skill paths use `${CLAUDE_PLUGIN_ROOT}/framework/…`. `CLAUDE_PLUGIN_ROOT`
is an **env var** Claude Code sets at install — never a literal folder
name. In a shell it expands (`cat "$CLAUDE_PLUGIN_ROOT/framework/…"`); if
unset, the `framework/` bundle ships beside `skills/` at the plugin root.
Never open the literal `${CLAUDE_PLUGIN_ROOT}` text.

## Related Resources

- Spec guide: `${CLAUDE_PLUGIN_ROOT}/framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- Layer registry: `${CLAUDE_PLUGIN_ROOT}/framework/registry/LAYER_REGISTRY.yaml`
- ID standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Traceability: `${CLAUDE_PLUGIN_ROOT}/framework/governance/TRACEABILITY.md`
- Governance core: `${CLAUDE_PLUGIN_ROOT}/framework/governance/DOC_GOVERNANCE_CORE.md`
- Authoring style: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`
- Per-layer guidance: `${CLAUDE_PLUGIN_ROOT}/framework/layers/NN_<X>/README.md`
