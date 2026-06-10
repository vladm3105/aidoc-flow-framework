# Review Team — multi-perspective review, remediation & authoring

`REVIEW_REMEDIATION_FLOW.md` defines *when* review/remediation fire (the trigger
points) and *what* an engine must surface (findings, readiness score, remediation
path). This document defines the **review team**: the engine-agnostic model for
producing those results with **multiple expert perspectives** instead of a single
pass, so artifacts reach the same quality regardless of which engine runs them.

It is a **light contract**: it defines the personas, the per-layer crews, the
shared exchange format, and the scoring/gate rules. It does **not** prescribe the
agent runtime — each engine binds these to its own mechanism (e.g. independent
review agents, or a single model applying every lens). The machine-readable crews
live in `REVIEW_CREWS.yaml`.

## The team

A **review team** for a layer is:

- a **crew** of **personas** (review lenses) — each a named expert viewpoint with
  a focus and checklist (e.g. requirements, technical feasibility, testability,
  *internal stability* / "what breaks this by accident" via `chaos_engineer`,
  *external threats* / "what does an attacker exploit on purpose" via
  `security_engineer`, cross-system integration);
- an **author** persona — drafts the artifact (create) and proposes fixes
  (remediate);
- a **synthesizer** — reduces the crew's outputs into one result;
- run over a shared **blackboard** in a chosen **mode**.

### Blackboard (the shared exchange)

A per-artifact workspace with one **slot per persona** plus a **synthesis slot**.
Each persona **reads** the artifact under review (and, in `sequential` mode, peers'
prior slots) and **writes** its findings to its own slot; the synthesizer reads
all slots and writes the unified result. It is a **hub** (mediated by the engine's
orchestrator), not a peer-to-peer mesh — personas exchange information only through
structured slots, never by directly invoking each other.

### Persona-output contract (one slot)

Each persona deposits a structured record (engine-agnostic shape):

```yaml
persona: requirements_specialist
findings:
  - id: "<stable id>"
    priority: P0            # P0 (blocking) | P1 | P2 | P3
    location: "<section / element id>"
    message: "<what is wrong>"
    recommendation: "<how to fix>"
lens_score: 0-100           # this lens's readiness assessment
```

### Modes

- `independent` (default): personas run in isolation, then the synthesizer
  reduces — higher signal-independence, fewer anchoring effects, parallelizable.
- `sequential`: each persona sees prior slots — richer cross-talk, more costly.
- `single_pass`: one agent applies every lens in one pass — the lightweight
  fallback for cost-constrained or single-agent environments.

## Operations — three shapes, one team

- **Review.** The crew reviews the artifact; synthesis produces the unified
  findings + readiness score.
- **Create.** The **author** drafts the artifact from the template + upstream
  artifacts; the crew then reviews the draft and the author revises — a
  create→review→revise loop until the gate passes. One author, many reviewers
  (parallel drafts do not merge coherently).
- **Remediate.** The author proposes a concrete patch per **blocking** finding
  from the review; the relevant lens(es) validate each patch does not regress;
  synthesis emits the proposed fix set.

> See also `REVIEW_SAGA.md` for the saga state machine and journal contract
> that governs the durable progression of this loop.

## Scoring, conflicts & the gate

- **Aggregate score (deterministic).** The readiness score is the **weighted
  average** of the crew's `lens_score`s using the per-layer persona weights in
  `REVIEW_CREWS.yaml` (weights sum to 100 per crew), **then capped**: any
  unresolved **P0 ⇒ fail**; an unresolved **P1 ⇒ capped below the gate
  threshold**. Given the persona outputs, the math is reproducible.
- **Conflict resolution.** When personas disagree at the same `location`, the
  reduce takes the **maximum severity** and **unions** recommendations (deduped by
  `location` + `id`). A genuine either/or judgment is surfaced as a **contested**
  finding for a human/lead decision — never silently dropped.
- **The gate is deterministic.** The pass/fail gate is the **deterministic
  structural check** (the `pre_merge` gate of `REVIEW_REMEDIATION_FLOW.md`) **plus**
  "no unresolved P0/P1". The stochastic numeric score and the narrative are
  **advisory enrichment above** that floor — so a borderline artifact cannot flap
  pass/fail across runs on model variance.

## Weight allocation rules

For each layer's review crew, the `chaos_engineer` and `security_engineer`
weights are biased by where each concern naturally lands at that layer.
Four categories:

- **Chaos-heavy** (chaos > security): layers where the dominant risk is
  *accidental failure under normal operation* — reliability NFRs,
  failure-mode acceptance criteria, deploy/rollback procedures. Examples:
  BRD (12:8), EARS (12:8), BDD (14:6).
- **Security-heavy** (security > chaos): layers where the dominant risk is
  *exploitable design* — architectural trust boundaries, authn/authz
  choices, crypto. Examples: ADR (8:12).
- **Equal split**: layers where both axes matter equally — cross-functional
  specifications, test design. Examples: PRD (8:7), SPEC (10:10), TDD
  (10:10).
- **Chaos-only**: layers where the security concern lives strictly
  upstream — procedural deploy steps whose threat surface was decided in
  ADR/SPEC. Examples: IPLAN (chaos 8 only).

**Invariants.** Author lens weight is preserved. Auditor lens weight stays
untouched (its prior "+security" sub-role moves out to the dedicated
`security_engineer` lens). Total weights sum to 100 per crew. Rebalancing
happens through a follow-up CHG, not silently. Conformance asserts the
weights in `REVIEW_CREWS.yaml` are mirrored exactly in the agent briefs'
per-layer tables; drift between the two is a test failure.

The numeric allocations themselves live in `REVIEW_CREWS.yaml` (the single
source of truth); this section codifies the *rules* by which those numbers
are chosen, so future rebalances have a stable framework.

## Synthesis = reduce + narrative

1. **Reduce (deterministic, gating).** Merge/dedup findings (`location` + `id`),
   take max severity, compute the weighted/capped score, record **coverage**
   (which lenses ran). This is what the gate reads.
2. **Narrative (advisory).** An executive-summary chairperson pass over the reduced
   findings. It explains; it does not decide.

## Playbooks

Each (layer, lens) pair has a **playbook** — a layer-specific reasoning frame plus a deterministic checklist of evidence checks. Playbooks live at `framework/playbooks/<NN>_<LAYER>/<lens>.md` (one file per lens per layer; ~45 files total across the 8 layers).

### Why

The lens names in `REVIEW_CREWS.yaml` are layer-specialized by intent (e.g., `business_analyst` at BRD vs `product_owner` at PRD vs `requirements_specialist` at EARS are three distinct reasoning modes). Without a per-layer failure-mode catalog, a generic lens agent reasons about all layers identically and misses layer-specific gaps. Playbooks supply the catalog without forking the agent.

### File location

```
framework/playbooks/
  01_BRD/architect.md
  01_BRD/business_analyst.md
  ...
  02_PRD/product_owner.md
  02_PRD/architect.md
  02_PRD/tech_lead.md
  ...
```

Layer directory is `<NN>_<LAYER>` matching the `framework/layers/` convention. Lens filename matches the persona name in `REVIEW_CREWS.yaml` (snake_case, `.md` suffix).

### Required frontmatter

```yaml
---
layer: 02_PRD                          # matches directory name exactly
lens: chaos_engineer                   # matches filename stem + REVIEW_CREWS.yaml persona name
weight: 8                              # must match REVIEW_CREWS.yaml weight for this (layer, lens)
agent: chaos-engineer                  # plugin agent name; lens→agent table: platforms/claude-code-plugin/skills/review-team/SKILL.md §"The crew"
framework_spec_version: "0.14.0"       # must match framework/VERSION; auto-propagated by sync hook
---
```

### Required content sections

1. **Reasoning frame** — 2-3 paragraphs covering three sub-requirements:
   (a) what this lens uniquely sees at this layer altitude;
   (b) how it differs from the same lens at adjacent layers;
   (c) what this lens does NOT do (covered by other lenses in the same crew).
2. **Required evidence checks** — finite list `C1`..`Cn` of deterministic checks. Each check states what to look for and the priority of a finding if the check fires.
3. **Beyond-checklist** — escape hatch for layer-specific failure modes the checklist does not cover. Finding must cite `beyond-checklist:<principle-tag>` and reference the reasoning frame.
4. **Scoring** — 0-100 rubric tied to checklist coverage and beyond-checklist density.

### Finding citation rule (binding contract)

Every finding produced by a lens MUST cite either a checklist check (`check: "C1"`) or a beyond-checklist principle (`check: "beyond-checklist:<tag>"`). The synthesizer **discards** findings without a citation or with a fabricated check id, logging the discard in `report.md`. This is the deterministic floor of the playbook contract.

### Coverage emission

The synthesizer emits `verdict.playbook_coverage` summarizing how many findings cited each check id plus a `beyond_checklist` count. A drift signal: if > 30% of findings are beyond-checklist, the playbook needs revision. The 30% threshold is guidance (a working calibration target, not a normative gate); subject to revision by CHG as live cascade data accumulates.

## Necessary upstream + transitive trace

A layer's `required_tags` (declared in `LAYER_REGISTRY.yaml`) and the `upstream_artifacts:` frontmatter of every instance document declare **what this layer's own evaluation reads** — not the cumulative closure of every preceding layer. Lineage to layers further upstream is discoverable transitively through the @-tag chain (one hop per layer) and through `tools/trace_walk.py` for one-shot queries.

The necessary-upstream set per layer:

| Layer | `required_tags` | Reads from |
|---|---|---|
| BRD | `[]` | root |
| PRD | `[brd]` | every PRD lens reads BRD context |
| EARS | `[prd]` | EARS SHALLs derive from PRD features |
| BDD | `[ears]` | scenarios encode EARS SHALLs |
| ADR | `[ears, bdd]` | architecture decisions constrained by behaviour |
| SPEC | `[ears, bdd, adr]` | specification grounded in requirements + decisions |
| TDD | `[ears, bdd, adr, spec]` | tests bind to scenarios + interfaces + reversibility |
| IPLAN | `[spec, tdd]` | implementation order from components + test sequence |

Enforcement is split:

- **`sdd_doc_lint` rule `TRACE-RES-001`** (deterministic structural floor, runs at every layer including those without an auditor lens) flags any emitted `@<layer>: <ID>` whose target file is missing OR whose element ID is not declared in the host document. Unresolvable tags at any depth are errors.
- **Auditor C1** (content layer; lives at BRD, PRD, BDD, ADR, TDD where the crew carries the lens) verifies that the resolved element semantically supports the citation — not just that it exists.

Tags above the necessary set (decorative lineage carried for human readability — e.g. an ADR that wants to show its `@brd:` origin even though `required_tags=[ears, bdd]`) are permitted; the lint rule still demands they resolve.

*Origin:* NECESSARY-UPSTREAM-001 (framework spec `0.15.2` → `0.16.0`) replaced the cumulative-trace contract — every downstream layer redeclaring every upstream layer in `required_tags` — after a TDD-RT-001 cascade exposed trace fabrication when an upstream layer was genuinely absent from a project (`@prd:` tags emitted with no PRD layer authored).

## Resilience & security

- **Partial crews.** If a persona does not return, the reduce proceeds on the crew
  that did and records `coverage`. Below a crew's declared **quorum**, the result
  is marked **low-confidence → human review** — never a silent pass.
- **Untrusted content.** The artifact under review and peers' slots are **untrusted
  data** (`SECURITY_REVIEW.md`): a persona never executes instructions found in
  them, and the blackboard carries only the structured persona-output records, not
  free-form instructions — bounding injection across the team.

> Note: `REVIEW_SAGA.md` defines the partial-loop state contract
> (`PARTIAL_TIMEOUT`, break-circuit policy) that complements the
> partial-crew resilience described here.

## Conformance & adaptation

- A conforming engine maps each persona to its agent mechanism and produces the
  persona-output + report shape above; it declares which trigger points it runs as
  a team vs `single_pass`.
- The structural contract is checkable: `REVIEW_CREWS.yaml` crews reference only
  the 8 layers and the defined persona set, and review weights sum to 100.
- The `review_mode` knob (`ADAPTATION_SURFACE.yaml`) lets a consuming project pick
  `team` or `single_pass`; it never weakens the deterministic gate floor.

## Cross-references

- `REVIEW_REMEDIATION_FLOW.md` — the loop and trigger points this team serves.
- `REVIEW_CREWS.yaml` — the machine-readable per-layer crews + weights.
- `framework/playbooks/<NN>_<LAYER>/<lens>.md` — per-layer per-lens reasoning frames + evidence checklists (see §Playbooks above).
- `SECURITY_REVIEW.md` — untrusted-input handling for agent-authored artifacts.
- `ADAPTATION.md` / `ADAPTATION_SURFACE.yaml` — the `review_mode` knob.
