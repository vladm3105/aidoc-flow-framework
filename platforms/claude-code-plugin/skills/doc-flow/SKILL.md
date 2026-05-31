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
    version: "0.2.0"
    framework_spec_version: "0.9.1"
    last_updated: "2026-05-27"
    adapts: [active_layers]
---

# doc-flow

## Purpose

Orchestrate the **Specification-Driven Development (SDD) workflow**. `doc-flow`
does not create artifacts itself; it points you at the right skill, explains
how the layers connect, and enforces the rules that keep the chain coherent.

**Layer**: cross-cutting (no upstream; routes into all 8 layers).
**Use the artifact skills for creation** — `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}`,
plus `../doc-ref/SKILL.md` for supplementary docs.

Authoritative spec: `${CLAUDE_PLUGIN_ROOT}/framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` and
`${CLAUDE_PLUGIN_ROOT}/framework/registry/LAYER_REGISTRY.yaml`.

## When to Use

- You are unsure which skill applies to the task at hand.
- You need an overview of the 8-layer flow or where you are in it.
- You are starting a brand-new project — run `../project-init/SKILL.md` **first**
  to scaffold folders, then return here.
- You are adopting SDD into an **existing** codebase — run
  `../project-adopt/SKILL.md` to reverse-engineer baseline artifacts first.
- You are changing an already-published artifact — use the CHG overlay
  (`../doc-chg/SKILL.md`), not the linear flow (see *Change management* below).

For end-to-end generation of a single layer, use that layer's `-autopilot`
skill. For "which skill / where am I / what's next", stay here — see *Find the
right skill, and where you are* below.

## Behavior

### The 8-layer flow

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
| — | Code | Implementation output | — |

Each layer family ships four skills: the **base** (create), `-autopilot`
(generate end-to-end), `-audit` (quality gate → report), and `-fixer`
(apply audit fixes).

### Skill selection

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
| Any stage | Supplementary docs (overview, glossary) | `doc-ref` |
| General guidance | Routing | stay on `doc-flow` |

### Find the right skill, and where you are

`doc-flow` answers "what should I do next?" directly — no separate helper skill.
The table above routes **by layer**; this routes **by action/intent** and reports
position.

**Intent → skill.** Classify the request by action keyword, then target:

| Action keyword | Skill |
|----------------|-------|
| create / draft / write | that layer's base or `-autopilot` (pick the layer from the table above) |
| check / score / audit | that layer's `-audit` |
| fix / remediate | that layer's `-fixer` |
| validate / trace / links / orphans / repair | `../doc-validator/SKILL.md` |
| review prose / typos / terms | `../doc-validator/SKILL.md` (`scope: prose`) |
| change / edit a published artifact | `../doc-chg/SKILL.md` + `../gate-check/SKILL.md` |
| roadmap / phasing | `../adr-roadmap/SKILL.md` |
| scaffold / new project | `../project-init/SKILL.md` |
| adopt / brownfield / reverse-engineer | `../project-adopt/SKILL.md` |
| tailor / profile | `../project-profile/SKILL.md` |
| security / threats | `../security-audit/SKILL.md` |

When the user names a skill, run it directly.

**Where am I.** Scan `docs/<NN>_<X>/` for existing artifacts; read each Document
Control `Status` (most layers `Draft → In Review → Approved`; IPLAN
`Draft → In Progress → Completed`). Map artifacts to the project's **active**
layers (see *Adaptation*), mark each completed / in-progress / ready / blocked,
and report position plus a progress percentage — layers at their terminal status
(`Approved`, or `Completed` for IPLAN) ÷ **active** layers.

**Template-conformance check (mandatory).** For every artifact found, compare it
to its layer's canonical `${CLAUDE_PLUGIN_ROOT}/framework/layers/<NN>_<X>/<TYPE>-TEMPLATE.yaml`:
load the template's top-level section keys, then check the artifact's `##` headings
contain every required section. Report any missing required sections as a
**drift finding** (artifact `Status` notwithstanding), e.g. *"BRD-01 missing 6 of
18 required sections: Implementation Approach, Support & Maintenance, …"*.

Drift findings are first-class — **do not** rationalise them as a "compact"
variant, "documented walkthrough format", or "pinned to lint" exception. There
is **one** template per layer and one canonical section list. Lint passing
(structural subset) does not imply template conformance (full section set). When
drift is found, recommend `doc-<layer>-fixer` (or `doc-<layer>-autopilot` for a
full re-author) to close the gap.

**What's next.** Recommend the next artifact per the cumulative chain (each layer
needs its single-layer prerequisite), over the project's **active** layers only —
never recommend a layer the profile disabled. Prioritize:

- **P0** — a *required* upstream is missing, or the next step is on the critical
  path (the active-layer spine `BRD → PRD → EARS → BDD → ADR → SPEC → TDD →
  IPLAN`, minus any disabled skippable layer).
- **P1** — the next ready layer once the critical path is unblocked.
- **P2** — optional / parallel work (`doc-ref` supplements, extra ADRs beyond the
  decisions already captured).

Surface parallel-work opportunities (independent tracks with no shared
prerequisite) and name the skill to run for each.

**Context scan.** Before authoring in an existing project, inventory the corpus
and build a traceability snapshot: rank candidate upstream documents for the
target type by directness, topic match, recency, and `Approved` status, and
collect project vocabulary (titles, section headers, glossary terms) so the new
document reuses real IDs and consistent terminology.

### Utility skills

- **`../project-init/SKILL.md`** — scaffold a new project (run before any layer).
- **`../project-adopt/SKILL.md`** — adopt SDD into an existing codebase (brownfield).
- **`../project-profile/SKILL.md`** — tailor the flow to this project (optional; sets `.aidoc/profile.yaml`).
- **`../doc-naming/SKILL.md`** — ID / naming authority (`TYPE-NN`, `TYPE.NN.SS.xxxx`).
- **`../doc-ref/SKILL.md`** — free-format reference documents (BRD-REF / ADR-REF).
- **`../doc-validator/SKILL.md`** — cross-document validation, bidirectional
  traceability (with optional repair), and prose/terminology review.
- **`../review-team/SKILL.md`** — multi-persona review-team mode for the
  `-audit`/`-fixer`/`-autopilot` operations at gates (crew → blackboard → scored
  report); `single_pass` fallback otherwise.
- **`../quality-advisor/SKILL.md`** — real-time authoring guidance for a single document.
- **`../charts-flow/SKILL.md`** — Mermaid diagrams and file management.
- **`../adr-roadmap/SKILL.md`** — implementation roadmaps from ADRs.
- **`../security-audit/SKILL.md`** — security review (OWASP/CWE, STRIDE).

### Change management (editing existing artifacts)

Changes to already-published artifacts use the **CHG overlay**, not the linear
flow:

- **`../doc-chg/SKILL.md`** (+ `-autopilot` / `-audit` / `-fixer`) — author and
  validate a change record; classifies the change level (C1–C3 / Emergency) and
  routes it to the right approval gate.
- **`../gate-check/SKILL.md`** — run the approval gate (GATE-01/03/06/08/CODE,
  or **GATE-SPEC** for a change to the `framework/` spec itself) for the change's
  affected layers and prepare the sign-off form (a human approves — the skill
  never does).

### Upstream-artifact policy (mandatory)

Do **NOT** invent missing upstream artifacts. If a required upstream is absent,
**skip** the downstream functionality and report it — every artifact must trace
to a real business/product justification.

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with its exact ID |
| Required upstream missing | Skip; report; advise creating it first |
| Optional upstream missing | Use `null` in the tag |
| Not applicable | Omit the tag |

### Validation model

The framework is spec-only — it ships no runtime scripts. Each skill **is** the
validator: it applies a declarative checklist against the layer `README.md` and
`${CLAUDE_PLUGIN_ROOT}/framework/governance/`. After each artifact, run that layer's `-audit`; before
moving on, confirm the cumulative upstream tags are present (PRD→1 … IPLAN→7).

## Adaptation

Read the project adaptation profile (`.aidoc/profile.yaml`) before reporting
position or recommending next steps. Honor this skill's declared knob
`active_layers`: treat a disabled skippable layer (BDD / ADR) as **not part of
the flow** — exclude it from the critical path, the progress denominator, and
next-step recommendations (never suggest authoring it, and don't count it
against completion). Ignore unknown / out-of-surface keys; absent a profile, use
the full 8-layer flow. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Reading bundled files

Skills reference the plugin's vendored spec as `${CLAUDE_PLUGIN_ROOT}/framework/…`.
`CLAUDE_PLUGIN_ROOT` is an **environment variable** Claude Code sets to the
plugin's install directory — it is **not** a literal folder named
`${CLAUDE_PLUGIN_ROOT}`, and it does not auto-expand inside this prose. To open a
bundled file, resolve it first:

- In a shell the variable expands, so read it directly, e.g.
  `cat "$CLAUDE_PLUGIN_ROOT/framework/registry/LAYER_REGISTRY.yaml"`; or run
  `echo "$CLAUDE_PLUGIN_ROOT"` to get the path and then read it.
- If the variable is unset in the current context, the `framework/` bundle ships
  at the plugin root **beside `skills/`** — locate the plugin install directory
  and read `framework/…` relative to it.

Never try to open the path with the literal `${CLAUDE_PLUGIN_ROOT}` text in it.

## Related Resources

- Spec guide: `${CLAUDE_PLUGIN_ROOT}/framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- Layer registry: `${CLAUDE_PLUGIN_ROOT}/framework/registry/LAYER_REGISTRY.yaml`
- ID standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Traceability: `${CLAUDE_PLUGIN_ROOT}/framework/governance/TRACEABILITY.md`
- Governance core: `${CLAUDE_PLUGIN_ROOT}/framework/governance/DOC_GOVERNANCE_CORE.md`
- Per-layer guidance: `${CLAUDE_PLUGIN_ROOT}/framework/layers/NN_<X>/README.md`
