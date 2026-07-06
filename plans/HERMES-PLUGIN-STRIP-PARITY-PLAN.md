# PLUGIN-STRIP-PARITY Plan (H-14) — the plugin's LLM lens is anchored by the author self-claim score; strip where the engine curates the input, disregard-instruct where the lens reads the artifact directly (both plugin modes); clarify the spec (GD-05)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | PLUGIN-STRIP-PARITY (H-14)                    |
| Type           | framework spec-governance (GD-05) + plugin conformance fix |
| Status         | READY — 2026-07-04 (3-agent Pass 2 + independent Pass 3; founder ratification required for PR 1) |
| Depends on     | none (D-0051 fixed the Hermes analog)        |
| Feeds          | closes the `REVIEW_TEAM.md` strip MUST on the plugin (the last unfulfilled surface) |
| Version impact | **Framework MINOR** (`0.32.7 → 0.33.0`, GD-05: sanction a disregard-instruction fallback for lenses that read the artifact directly; **change-level C2; requires human ratification on merge**; GATE-SPEC; re-vendor) + **plugin PATCH** (`0.23.0 → 0.23.1`, honor it). |

## Objective

The `REVIEW_TEAM.md` strip MUST (`:80`) requires engines to remove author
self-assessment fields (`*_ready_score`/`*_score`/`readiness_score`/`audit_score`)
from what each lens sees, so the lens's `lens_score` is not anchored to the author's
claim. Its mechanism clause (`:93`) says "the brief that goes to the lens has the
stripped body" — written assuming the **engine controls the lens input**.

That holds for Hermes (an API completion — D-0051 physically removes the score via
`section_hygiene.py:33` `sub("")`) and for the plugin's **`single_pass`** mode (the
audit skill reads the artifact in its own context — `doc-brd-audit/SKILL.md:169-189` —
so it can strip what it reads). It does **not** hold for the plugin's **team-mode
agentic lens**: the lens is a Claude Code `Task` subagent briefed with the artifact
**path** (`doc-brd-audit/SKILL.md:110`) that it `Read`s from disk (all lens agents
carry `Read`, e.g. `agents/traceability-auditor.md:10`); the on-disk artifact carries
the score (`examples/url-shortener/docs/01_BRD/BRD-01.md:18` `brd_ready_score: 92`, in
all 8 layers). So the team-mode lens **is anchored**, and its "Strip author self-claim
before lens dispatch" prose (`doc-brd-audit/SKILL.md:186`) is **inert and
self-contradictory** — it says "the brief has the stripped body," but the brief carries
a path, and nothing writes a stripped copy.

**The distinction is engine-architecture, not review mode (Pass-3 F1/F2).** Physical
removal is possible **only when a separate actor curates the lens input** so the lens
context never contained the score — true for Hermes alone (Python `sub("")` assembles a
stripped body, a fresh API completion reviews it). The plugin lens **reads the artifact
directly** in *both* modes — team-mode (subagent `Read`s the path) and `single_pass`
(the audit skill reads the artifact into its own review context, `doc-brd-audit/SKILL.md:169`).
Once the score is in that context there is no separate actor to hide it from, so "strip"
degenerates to "disregard." The plugin is an all-LLM engine with **no deterministic
strip step**; its only de-anchor, in every mode, is an explicit, strong **instruction**
to disregard the author self-assessment fields.

That instruction is materially **weaker** than physical removal (a stochastic model can
still read the number), so it is a **constrained fallback** — permitted **only** where
the lens reads the artifact directly (a structural fact about the engine, not a
self-declaration). Sanctioning it in a normative MUST is a **framework governance
decision (GD-05)** requiring human ratification.

## Scope (split into two PRs per the governance ≤3-surface discipline)

### PR 1 — Framework governance (GD-05); **founder ratifies on merge**

- **`framework/governance/DECISIONS.md` — add GD-05** (graduated governance decision;
  Status "Proposed — ratified-on-merge, GATE-SPEC human sign-off", following the GD-03
  precedent). Records: the anchor gap; the capability-based mechanism split; the
  fallback is weaker (not equivalent); the tightened definition; SemVer **minor**,
  change-level **C2**; Authority = `REVIEW_TEAM.md` §strip + `chg/gates/
  GATE-SPEC_FRAMEWORK.md`.
- **`framework/governance/REVIEW_TEAM.md` — clarify the strip section** (`:76-93`):
  - **Primary mechanism (unchanged):** an engine that **curates the lens input** (a
    separate actor assembles the body the lens receives, so the lens context never held
    the score) strips the fields — e.g. Hermes's Python strip + fresh API completion.
  - **Constrained fallback (new):** where the **lens reads the artifact directly** (it
    is handed a path / shares the reading context, so the engine cannot keep the score
    out of the lens context — e.g. an all-LLM agentic reviewer), the engine satisfies
    the de-anchor requirement via an **explicit, strong instruction**: the lens MUST NOT
    read, cite, or weight the author self-assessment fields when forming its
    `lens_score`. This is a **weaker fallback**, permitted **only** under the
    reads-directly structural condition — not a self-declarable escape from the primary
    strip.
  - Keep the canonical field list + the anchor-effect rationale.
- **Framework `0.32.7 → 0.33.0`** via `bump_version.py` (VERSION + FSV pins + re-vendor
  `REVIEW_TEAM.md` to `platforms/claude-code-plugin/framework/governance/` + 104
  frontmatter + FSV hard-pin auto-synced by `sync-version-refs.sh:218`) + root
  `CHANGELOG.md`. GATE-SPEC.
- **Governance surfaces: 2** (GD-05 + REVIEW_TEAM.md) — within the ≤3 limit. The GD-05
  entry is itself the change record (per GD-03; no separate CHG artifact file).

### PR 2 — Plugin (consumer); routine, follows PR 1

- **9 audit SKILLs** (`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan,chg}-audit/SKILL.md`):
  - **Team-mode Fan-out brief (uniform):** add a bullet (alongside the artifact-path
    bullet at `:110`) instructing the lens subagent to disregard the author
    self-assessment fields when forming its `lens_score`.
  - **Strip-section replacement:** replace the inert "Strip author self-claim before
    lens dispatch" prose with the reads-directly framing: **both** modes de-anchor via
    a **disregard instruction** (team-mode: in the subagent brief; `single_pass`: in the
    in-context review instructions) — the plugin has no deterministic strip step, so
    neither mode "physically strips" (Pass-3 F1). **`doc-chg-audit` is bespoke** — its
    section adds a `gate_ready` author-asserted-boolean bullet (`:233`) + a trailing
    `### No-findings rationale` subsection; edit it distinctly (the other 8 are
    byte-identical — one uniform replacement).
- **9 fixer SKILLs** (`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan,chg}-fixer/SKILL.md`)
  (Pass-3 F3): the fixer dispatches lens subagents via its **own inline briefs** — the
  responsible-lens re-review + the patch-validation subagent that emits a `lens_score`
  (`doc-brd-fixer:92-96`) — not through `review-team`. Add the same disregard
  instruction to those inline dispatch briefs.
- **`review-team/SKILL.md`** (`:151`): add the disregard guidance to its shared lens
  dispatch too — defensive coverage for any consumer routed through it (the load-bearing
  fixer/autopilot coverage is the fixer inline briefs above + the audit SKILLs, since
  the fixer uses inline briefs and autopilot routes through `doc-*-audit`).
- **`agents/traceability-auditor.md:58`** — **qualify** (not remove) the readiness line:
  *as a fan-out lens* disregard the author's self-claimed score; *as the standalone
  project-integrity gate* check the **recomputed** score against threshold (the gate is
  recomputed fresh — `doc-brd-audit/SKILL.md:40` fresh-audit policy — never read from
  the self-claim). Distinguish the dual role.
- Plugin `0.23.0 → 0.23.1`; plugin CHANGELOG; `plans/DECISIONS.md` D-0052 (records the
  plugin impl, references GD-05); H-14 closed in `HERMES-BACKLOG.md`; HANDOFF; PARITY.

**Out of scope (deferred):**

- **A stripped working copy** (Option A) — rejected: leaky for an agentic lens, more
  surface, new artifacts.
- **`security-audit`** — computes its own score, no lens fan-out, no anchored surface
  (verified). Untouched.
- Re-verifying Hermes — D-0051 already satisfies the MUST via physical removal (the
  spec's primary mechanism, unchanged).

## Approach / Design (GD-05 / D-0052)

### The mechanism split is engine-architecture, not review mode (Pass-3 F1/F2)

De-anchoring has two mechanisms of **unequal strength**, selected by a **structural
fact about the engine** (not the review mode, and not self-declared):

1. **Physical removal (primary, strong):** available **only when a separate actor
   curates the lens input** so the lens context never contained the score — Hermes
   (Python strips the body, a fresh API completion reviews it). Stays the default MUST.
2. **Disregard instruction (constrained fallback, weaker):** required when **the lens
   reads the artifact directly** (handed a path, or sharing the reading context), so the
   engine cannot keep the score out of the lens context. Weaker (a stochastic model can
   still read the number) → the instruction must be strong (name the fields; forbid
   reading, citing, or weighting them).

The plugin is an **all-LLM engine with no deterministic strip step**, and its lens
**reads the artifact directly in every mode** — team-mode (subagent `Read`s the path)
*and* `single_pass` (the audit skill reads the artifact into its own review context).
So the plugin uses the disregard instruction **in both modes**; there is no plugin path
where physical removal applies. (An earlier draft wrongly claimed `single_pass`
"physically strips" — Pass-3 F1 corrected it: reading the body into context is exactly
what makes removal impossible thereafter.) GD-05's precondition — "the lens reads the
artifact directly vs. receives an engine-curated input" — is a mechanical architecture
test, so the fallback is not a self-declared escape hatch.

### Why this needs GD-05 + human ratification (not a bare version bump)

Editing a normative MUST's compliance surface is a governance decision. Precedents:
GD-02 (added the `pre_merge` strength contract to `REVIEW_REMEDIATION_FLOW.md`) and
GD-03 (added the reference-granularity clause to `ID_NAMING_STANDARDS.md`) — both
recorded as **GD-NN**, both **SemVer minor + C2**, both ratified by human sign-off on
merge (a `framework/**` change). This change is the same class (broadens what satisfies
a MUST) → **GD-05, MINOR `0.33.0`, C2, founder ratifies**. PR 1 is therefore
**excluded from auto-merge**.

### GATE-SPEC reconciliation (Pass-3 F4/F5)

Per the GD-01 precedent (`framework/governance/DECISIONS.md:162-163` — "Recording this
decision was itself a spec change and passed GATE-SPEC (its VERSION/CHANGELOG bump +
green conformance are the evidence)"), the **GD-05 entry + the framework VERSION/
CHANGELOG bump + green conformance ARE the CHG record** — no separate CHG artifact or
`GATE_APPROVAL_FORM.md` file is created; the GATE-SPEC §5.1 "CHG document created" and
"human approval" items are satisfied by the GD-05 entry and the protected-branch human
sign-off on the `framework/**` PR. The change injects new **agent-facing** instruction
text (lens-brief guidance), which triggers advisory **GATE-SPEC-W003** (agent-facing
spec change → recommend a `SECURITY_REVIEW.md` note); W003 is warning-only — the
disregard-instruction wording is trivially safe (it only tells a lens to ignore a
numeric self-claim; no capability/tool/permission change), noted here in lieu of a
separate assessment.

### Not already handled (advisory from review)

The 9 audit SKILLs already carry "Do NOT echo the self-claimed score"
(`doc-brd-audit:163-167`) — but that governs the **skill's own stdout/report**, a
different actor from the **lens subagent's** `lens_score` (the MUST's target). The gap
is real; the existing instruction does not close it.

### No conformance-test coverage (state plainly)

No shared conformance test asserts the strip MUST (only Hermes-internal unit tests).
So the plugin gap was invisible to CI, and the plan's "conformance stays green" checks
are trivially green — they confirm no regression, not that the mechanism works. The
real validation is the grep checks (V1-V3) + human review of the instruction wording.

### Versioning

`bump_version.py 0.33.0` bumps framework VERSION + both FSV pins + re-vendors
`REVIEW_TEAM.md` + auto-syncs the FSV hard-pin (`test_plugin_release_metadata.py:139`
via `sync-version-refs.sh:218` — same mechanism verified in H-12). Plugin VERSION
bumped separately in PR 2.

## File structure

### PR 1 (governance)

| Path | Change |
| ---- | ------ |
| `framework/governance/DECISIONS.md` | add **GD-05** (the graduated decision + change record) |
| `framework/governance/REVIEW_TEAM.md` | strip section (`:76-93`): primary-strip + constrained disregard-fallback clause |
| `framework/VERSION` (→ `0.33.0`) + FSV pins + re-vendored `platforms/claude-code-plugin/framework/governance/REVIEW_TEAM.md` + 104 frontmatter + hard-pin + root `CHANGELOG.md` | `bump_version.py` (GATE-SPEC) |

### PR 2 (plugin)

| Path | Change |
| ---- | ------ |
| `platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md` (8) | uniform: disregard brief-bullet + strip-section reframe (both modes = disregard instruction; no "physical strip") |
| `platforms/claude-code-plugin/skills/doc-chg-audit/SKILL.md` | bespoke: same, preserving the `gate_ready` bullet + trailing subsection |
| `platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan,chg}-fixer/SKILL.md` (9) | add the disregard instruction to the inline lens-dispatch briefs (patch-validation subagent emits a `lens_score`, `doc-brd-fixer:92-96`) |
| `platforms/claude-code-plugin/skills/review-team/SKILL.md` | add disregard guidance to the shared lens fan-out (defensive) |
| `platforms/claude-code-plugin/agents/traceability-auditor.md` | qualify the readiness line (recomputed gate vs lens disregard; dual role) |
| `platforms/claude-code-plugin/VERSION` (→ `0.23.1`) + plugin `CHANGELOG.md` + `plans/DECISIONS.md` (D-0052) + `plans/HERMES-BACKLOG.md` (H-14) + `plans/HANDOFF.md` + `docs/PARITY.md` | version + docs |

## Implementation sequence

### PR 1 — Task 1: GD-05 + spec clause — [SPEC/GOVERNANCE]

- Add GD-05 to `framework/governance/DECISIONS.md`; add the capability-split clause to
  `REVIEW_TEAM.md`. `bump_version.py 0.33.0`. GATE-SPEC. **Open for founder ratification;
  do NOT auto-merge.**

### PR 2 — Task 2: plugin SKILLs — [CODE/SKILL] (after PR 1 merges)

- 9 audit SKILLs (chg bespoke) + **9 fixer SKILLs** (inline dispatch briefs) +
  `review-team/SKILL.md` + `traceability-auditor.md`. Uniform disregard brief-bullet;
  strip-section reframe (both modes = disregard instruction, no "physical strip").

### PR 2 — Task 3: version + docs

- Plugin `0.23.1`; plugin CHANGELOG; D-0052; H-14 closed; HANDOFF; PARITY.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | grep the 9 audit + 9 fixer SKILLs + `review-team/SKILL.md` for the disregard instruction | present in all lens-dispatch briefs | plugin fix (Pass-3 F3) |
| V2 | grep the 9 audit for the old inert "the brief that goes to the lens … has the stripped body" | absent (replaced) | contradiction removed |
| V3 | each audit SKILL's `single_pass` section | de-anchors via a disregard instruction (NOT "physical strip"); covers the in-context read | Pass-3 F1 both-modes |
| V4 | `doc-chg-audit` strip section | `gate_ready` disregard + trailing `### No-findings rationale` subsection intact | G2 bespoke |
| V5 | `REVIEW_TEAM.md` strip section | primary-strip (curated-input) + constrained fallback (reads-directly) clause; de-anchor MUST intact | GD-05 / F2 |
| V6 | `framework/governance/DECISIONS.md` | GD-05 present (Status/Decision/Consequences C2/Authority) | governance record |
| V7 | `traceability-auditor.md:58` readiness line | qualified: lens disregards the author score; standalone gate uses the recomputed score | F5 |
| V8 | `python tests/chg/spec_gate.py --base main` (PR 1) | pass (VERSION + CHANGELOG) | GATE-SPEC |
| V9 | `python -m pytest tests/conformance -q` | green (bundle byte-identity; FSV pins == 0.33.0) | no regression |

## Docs to update

- [ ] `framework/governance/DECISIONS.md` — GD-05 (PR 1)
- [ ] root `CHANGELOG.md` — framework `0.32.7 → 0.33.0` (PR 1)
- [ ] `platforms/claude-code-plugin/CHANGELOG.md` — `[0.23.1]` (PR 2)
- [ ] `plans/DECISIONS.md` — D-0052 (PR 2, references GD-05)
- [ ] `plans/HERMES-BACKLOG.md` — H-14 closed (PR 2)
- [ ] `plans/HANDOFF.md` + `docs/PARITY.md` — both platforms now satisfy the MUST (Hermes: physical strip, curated input; plugin: disregard instruction in both modes, direct-read lens)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | The disregard fallback is weaker than physical removal | accepted | it is the **only** de-anchor for a direct-read lens (the plugin is all-LLM, no strip step; a stripped copy is leaky); GD-05 frames it honestly as a constrained fallback + mandates strong wording; physical strip stays the primary MUST where the engine curates the lens input (Hermes) |
| R2 | "FS-access constraint" is still self-declarable | med | GD-05 defines it as a lens that **requires** tool/FS access to the artifact for its function; the fallback is not a general option — reviewers gate the wording |
| R3 | Splitting lets PR 1's spec land before PR 2 honors it | low | governance-first is the sanctioned pattern; brief inconsistency; PR 2 follows immediately |
| R4 | `doc-chg-audit` bespoke edit drifts | med | V4 checks the `gate_ready` + subsection; edit chg distinctly, not via the uniform replacement |
| R5 | Missing a lens path (fixer/autopilot) | low | `review-team/SKILL.md` is the shared fan-out for all three; covered (G1); V1 greps it |
| R6 | Framework MINOR mis-set / GATE-SPEC gaps | low | GD-05 carries SemVer+C2 per GD-03; `bump_version.py` handles pins + hard-pin; V8 |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The strip MUST: strip author self-claim before passing to each lens subagent (both modes) | `MUST strip` | framework/governance/REVIEW_TEAM.md:80 |
| 2  | The mechanism clause presumes the engine controls the brief ("stripped body") | `stripped body` | framework/governance/REVIEW_TEAM.md:93 |
| 3  | The plugin team-mode lens brief passes the artifact PATH (not a body) | `absolute artifact path` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:110 |
| 4  | The plugin audit SKILL carries an inert "Strip author self-claim before lens dispatch" section | `Strip author self-claim before lens dispatch` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:186 |
| 5  | `single_pass` mode: the skill reads the artifact into its own review context (so the score is in-context → disregard instruction, not physical strip) | `single_pass mode (fallback)` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:169 |
| 6  | The lens agent has `Read` (it reads the on-disk artifact) | `Read` | platforms/claude-code-plugin/agents/traceability-auditor.md:10 |
| 7  | The on-disk artifact carries the author score the lens reads | `brd_ready_score: 92` | examples/url-shortener/docs/01_BRD/BRD-01.md:18 |
| 8  | `review-team/SKILL.md` is a shared fan-out with no strip guidance (defensive coverage) | `dispatch each lens as a` | platforms/claude-code-plugin/skills/review-team/SKILL.md:151 |
| 8b | The fixer dispatches a patch-validation lens subagent emitting a `lens_score` (its own inline brief; missed surface) | `lens_score` | platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md:96 |
| 9  | `doc-chg-audit` strip section is bespoke (adds a `gate_ready` author-boolean) | `gate_ready` | platforms/claude-code-plugin/skills/doc-chg-audit/SKILL.md:233 |
| 10 | The auditor lens also checks readiness scores (must be qualified, not removed) | `Readiness scores` | platforms/claude-code-plugin/agents/traceability-auditor.md:58 |
| 11 | The audit skill recomputes the gate fresh (so disregard doesn't break the gate) | `Fresh-audit policy` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:40 |
| 12 | GD-03 precedent: additive normative clarification = SemVer minor, change-level C2, ratified-on-merge | `GD-03` | framework/governance/DECISIONS.md:58 |
| 13 | Latest graduated governance decision is GD-04 → next is GD-05 | `GD-04` | framework/governance/DECISIONS.md:16 |
| 14 | `REVIEW_TEAM.md` is vendored to the plugin bundle (framework change re-vendors) | `Review Team` | platforms/claude-code-plugin/framework/governance/REVIEW_TEAM.md:1 |
| 15 | The FSV hard-pin is auto-synced by `sync-version-refs.sh` (refutes the "manual bump" concern) | `replace_in_file` | scripts/sync-version-refs.sh:218 |
| 16 | Current framework spec is `0.32.7` (→ `0.33.0` MINOR) | `0.32.7` | framework/VERSION:1 |
| 17 | Current plugin version is `0.23.0` (→ `0.23.1` PATCH) | `0.23.0` | platforms/claude-code-plugin/VERSION:1 |
| 18 | Most recent project decision is D-0051 → next free is D-0052 | `D-0051` | plans/DECISIONS.md:13 |
| 19 | H-14 is the open backlog entry for this gap | `### H-14` | plans/HERMES-BACKLOG.md:430 |

## Review log

### Pass 1 — 2026-07-04 — self-review (original draft; superseded)

Original draft under-scoped both the governance (treated the spec edit as a bare
version bump) and the surface (only the 9 audit SKILLs' step-4 briefs). See Pass 2.

### Pass 2 — 2026-07-04 — independent (3-agent parallel per OPS-0067)

Three fresh-context reviewers. **Citations 0 inaccuracies; premise fully substantiated.**
8 load-bearing findings, all folded into the reshape above:

- **F1 — GD-05 graduation + human ratification required** (not a D-NN note + bump);
  precedents GD-02/GD-03; the GD-NN entry is itself the change record (no separate CHG
  file). PR 1 excluded from auto-merge.
- **F2 — MINOR + C2, not PATCH** (broadens a MUST's compliance surface → additive
  normative content; framework `0.33.0`).
- **F3 — "equivalent" is dishonest;** the disregard instruction is a **weaker fallback**
  for lenses that require FS access — reframed as a capability-based split (physical
  strip primary; instruction constrained fallback).
- **F4 — "agentic lens" undefined ⇒ escape hatch;** tightened to "requires FS/tool
  access to the artifact" + strong wording. Also: no conformance test asserts the MUST
  (stated plainly).
- **F5 — traceability-auditor: qualify (not remove) + dual role** (lens disregard vs
  recomputed standalone gate).
- **G1 — `review-team/SKILL.md` (shared fan-out for fixer/autopilot) uncovered** —
  added to scope.
- **G2 — `doc-chg-audit` strip section not byte-identical** (`gate_ready` + trailing
  subsection) — bespoke edit, not the uniform replacement.
- **G4 — `single_pass` under-covered** — it reads in-context, so it must **physically
  strip** (the primary mechanism is available there), not merely reframe as a brief
  instruction; else it violates "both modes."
- **G3 REFUTED** — FSV hard-pin auto-synced (`sync-version-refs.sh:218`), as in H-12.
- Advisory: distinguish the existing "don't echo score" (skill stdout) from the lens
  de-anchor. Minor: strip-MUST line is `:80` (title/prose corrected).

### Pass 3 — 2026-07-04 — independent (fresh-context) re-review of the reshaped 2-PR plan

Confirmed the governance framing (GD-05, MINOR/C2, ratification, split), all 19
citations, the 8-audit byte-identity + chg-bespoke, and the 2-PR boundary. **3
load-bearing findings, all folded:**

- **F1 — "single_pass physically strips" is FALSE.** The plugin is all-LLM with no
  deterministic strip; once the score is in the review context there is no separate
  actor to hide it from, so both modes are instruction-based. → Reframed the mechanism
  split from **mode-based** to **engine-architecture-based** (curated-input engine →
  physical strip; direct-read lens → disregard); both plugin modes use the disregard
  instruction; rewrote V3 (disregard, not physical strip).
- **F2 — precondition should be "reads directly vs curated input"** (a structural,
  non-self-declarable fact), not "requires FS access." → Adopted in the GD-05 /
  REVIEW_TEAM.md clause + design; tightens the escape-hatch risk (R2).
- **F3 — the 9 `doc-*-fixer` SKILLs' inline lens-dispatch briefs are uncovered**
  (`doc-brd-fixer:96` emits a `lens_score`; `review-team` doesn't reach them; autopilot
  routes through audit). → Added the 9 fixer SKILLs to the plugin surface; `review-team`
  kept as defensive; V1 greps audit + fixer + review-team. Ledger row 8b added.
- **F4/F5 (minor, folded):** GATE-SPEC reconciliation stated per the GD-01 precedent
  (the GD-05 entry + VERSION/CHANGELOG + green conformance ARE the CHG record; human
  sign-off = protected-branch review) + a `GATE-SPEC-W003` agent-facing note (the
  disregard wording is trivially safe). **F6:** V7 retargeted to the actual `:58`
  wording.
- Confirmed: SemVer MINOR+C2, 2-PR split, ledger, uniform/bespoke surface.

### Pass 4 — 2026-07-04 — self-review (re-validate the Pass-3 fold)

The reframe is internally consistent: the mechanism is now architecture-based
(curated-input → strip; direct-read → disregard), which correctly places **both** plugin
modes + the fixer inline-brief lenses in the disregard bucket and keeps Hermes on
physical strip; the GD-05 precondition matches; V3/V5/V7 align; the fixer surface (9
SKILLs) closes F3. No plugin path physically strips (correct — no deterministic strip
step exists). No new gaps.

**Result:** ready (for founder ratification of PR 1)
