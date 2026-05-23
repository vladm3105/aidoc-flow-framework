# ADAPT Plan — Project adaptation overlay + knowledge extractor

| Field      | Value                          |
|------------|--------------------------------|
| Task       | ADAPT (ADAPT-A overlay · ADAPT-B bridge) |
| Depends on | D-0012 (domain profiles post-v1.0), D-0013 (single source of truth), CHG overlay (`framework/governance/chg/`), P3-T7 (`doc-chg` family + `gate-check`) |
| Status     | PLANNED — 2026-05-23T14:30:00Z |
| Feeds      | A future `D-0019` (resolved decisions) · the post-v1.0 domain-profile / IPLAN-corpus direction (D-0012 R2) |

## Objective

Give a *consuming* project a bounded way to adapt how the SDD skills behave —
without forking the framework — and a manual, developer-triggered path to
**promote** locally-proven adaptations back up into the canonical skills. Two
layers, one contract:

- **Layer 1 — the overlay.** A project (and optionally a developer) declares a
  small, closed set of preferences; skills read them at authoring time. Stays
  project-local; affects nobody else.
- **Layer 2 — the bridge.** A `knowledge-extractor` skill, run on demand, mines
  the overlay + a learnings log, classifies what looks generalizable, and emits
  a **CHG change proposal** against the relevant skill's guidance — routed
  through the existing `gate-check` + conformance path. It never edits the
  framework directly and never auto-applies.

The whole feature reuses governance machinery that already exists
(`framework/governance/chg/`, `doc-chg`, `gate-check`); the new surface is one
spec doc plus two skills.

## Scope

**In (ADAPT-A — overlay):**
- `framework/governance/ADAPTATION.md` — the engine-agnostic **adaptation
  surface**: a *closed* set of knobs skills may honor, with precedence rules.
- `project-profile` plugin skill — maintains the overlay files.
- A standard **"consult the profile"** clause + an `adapts:` frontmatter field
  added to the **8 layer base skills** (`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}`).
- Two profile scopes: `~/.aidoc/profile.yaml` (developer, all projects) layered
  under `.aidoc/profile.yaml` (this project).
- Conformance checks for the surface (closed-set integrity, `adapts ⊆ surface`,
  engine isolation, no leakage of project artifacts into `framework/`).

**In (ADAPT-B — bridge):**
- `.aidoc/learnings.md` **entry-shape convention** (locked now; see Approach).
- `knowledge-extractor` plugin skill — emits CHG proposals against **skill
  guidance only**.
- Conformance check that an emitted proposal carries provenance and matches the
  `CHG-TEMPLATE.yaml` shape so `gate-check` can consume it.

**Out (explicitly deferred):**
- Extractor targeting **templates** (`framework/layers/`) or **governance**
  docs — skill guidance only in v1; higher-blast-radius targets stay manual.
- **Automatic** capture of learnings and **automatic** application of
  promotions — both are developer-triggered by design.
- **Hermes-side runtime honoring** of the profile — the surface spec is shared
  and engine-agnostic; the plugin implements it first. Hermes conformance to the
  surface is a tracked follow-up, not this task.
- **Multi-project corpus** cross-checking ("contradicted by other projects'
  profiles") — the generalizability test is manual in v1; we only lock the
  *signal shape* now so that test is possible later.
- The `-autopilot`/`-audit`/`-fixer` variants reading the profile — base skills
  first; variants inherit in a later pass if it proves out.

## Approach

### The promotion gradient (mental model)

```
1. Correction in a session                    (ephemeral)
2. Logged learning   .aidoc/learnings.md       (project-local, raw signal)
3. Profile rule      .aidoc/profile.yaml        (project-local, changes skill behavior)
4. Promotion candidate   ← knowledge-extractor flags it as generalizable
5. Framework change  → CHG proposal → gate-check → conformance → canonical skill
                                                     (benefits every project)
```

Each step up is more durable, wider-reaching, and more gated. Steps 2–3 are
project-local and cheap. The 3→5 jump is the manual extractor and is the only
place framework content changes — always via a *proposal*, never a direct edit.

### Where artifacts live

| Artifact | Location | Owner |
|---|---|---|
| Adaptation surface spec | `framework/governance/ADAPTATION.md` | framework (engine-agnostic) |
| Developer profile | `~/.aidoc/profile.yaml` | consuming developer |
| Project profile | `.aidoc/profile.yaml` | consuming project |
| Learnings log | `.aidoc/learnings.md` | consuming project |
| `project-profile` skill | `platforms/claude-code-plugin/skills/project-profile/` | plugin |
| `knowledge-extractor` skill | `platforms/claude-code-plugin/skills/knowledge-extractor/` | plugin |

The `.aidoc/` files live in the **consuming** project, never in this repo.
`framework/` ships only the *spec* (`ADAPTATION.md`) and the skills ship only
the authoring guidance + example snippets. A conformance check guards against an
actual `.aidoc/` profile/learnings file being committed under `framework/`.

### The adaptation surface — narrow, closed (v1)

`ADAPTATION.md` enumerates exactly these knobs; anything else is out of bounds
and skills ignore it:

1. `active_layers` — which of the 8 layers are in play (skip/keep).
2. `section_toggles` — per-layer optional sections on/off (within the
   template's declared-optional set only; required sections cannot be toggled).
3. `audit_thresholds` — numeric tuning of advisory (Tier-2) gate values; the
   blocking `gate_ready` criteria themselves are **not** tunable.
4. `id_format` — choice among ID conventions already allowed by
   `ID_NAMING_STANDARDS.md` (never a new scheme).
5. `glossary` — domain-term substitutions / preferred terminology.

The surface is deliberately **declarative data**, not behavior: a profile can
flip a documented switch or supply a term, never rewrite a skill's logic. This
keeps it conformance-compatible and closes the prompt-injection door (a profile
is untrusted project input).

### How skills read the profile (no runtime code)

The framework ships no executable code (D-0013, SKILL_AUTHORING §4 "the skill is
the validator"). The mechanism is therefore an instruction clause every adapting
skill carries, plus an `adapts:` frontmatter list naming the knobs it honors:

```yaml
  custom_fields:
    ...
    adapts: [active_layers, section_toggles, glossary]   # ⊆ ADAPTATION.md surface
```

Body clause (standard wording, distilled from `ADAPTATION.md`):
> Before applying defaults, merge the adaptation profile (framework defaults <
> `~/.aidoc/profile.yaml` < `.aidoc/profile.yaml`). Honor only the knobs listed
> in this skill's `adapts:`; ignore any unknown or out-of-surface key.

Conformance asserts the clause is present and that `adapts ⊆ surface` — it does
not (cannot) execute it.

### Precedence + conflict logging

Merge order: **framework defaults < user-global < project**. When the project
profile overrides the user-global value for the *same* knob, that is a per-project
deviation from the developer's own habit — recorded as a learnings entry with
`conflict: true`. The extractor treats a conflict as *negative* evidence for
generalizability (a habit the developer themselves overrode here is less likely
to be universally right).

### Learnings entry shape (locked now)

Locked so the future "recurs and isn't contradicted elsewhere" test needs no
reformat. One YAML list item per learning in `.aidoc/learnings.md`:

```yaml
- ts: 2026-05-23T14:30:00Z      # ISO 8601 UTC
  layer: EARS                    # layer name | "utility:<name>" | "cross"
  knob: section_toggles.security # surface path, or "none" (not yet a knob)
  default: <framework default value>
  chosen: <value the project used instead>
  rationale: <why the deviation>
  recurrence: 1                  # times observed; bumped on repeat
  scope: project                 # project | user-global
  conflict: false                # true if project overrode user-global
```

### Knowledge-extractor flow (ADAPT-B, skill-guidance-only)

1. Read user-global + project profiles + `.aidoc/learnings.md`.
2. Diff against framework defaults → the set of active deviations.
3. Classify each: **generalizable** vs **project-idiosyncratic**. v1 = manual
   judgment, aided by `recurrence` (higher = stronger) and `conflict` (true =
   weaker). Idiosyncratic items stay local; the skill says so explicitly.
4. For each generalizable item, emit a **CHG proposal** via the `doc-chg`
   family targeting the relevant **skill's guidance/checklist** — shaped to
   `framework/governance/chg/CHG-TEMPLATE.yaml`, carrying provenance (the
   learnings entries + profile keys that motivated it).
5. Hand the proposal to `gate-check` → conformance must pass → a **human**
   adopts. The skill never writes framework files and never approves.

### Governance note (this feature governs itself)

Adding `ADAPTATION.md` to `framework/governance/` is itself a **framework spec
change**. Per CLAUDE.md / `docs/PROJECT.md` §6 the gated CHG process returns
post-cutover to govern exactly this. So landing ADAPT-A:
- bumps `framework/VERSION` `0.1.0 → 0.2.0` and the matching
  `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` (kept equal — the
  conformance version check compares them);
- is itself a fitting first real exercise of the CHG path the extractor will
  later feed. (Nice symmetry, not a hard requirement for the draft.)

## Step sequence

**ADAPT-A — the overlay**
1. Write `framework/governance/ADAPTATION.md` (closed surface, precedence,
   profile schema, the standard consult-clause wording). Link it from
   `framework/governance/README.md`.
2. Add the `adapts:` field + consult-clause to the 8 layer base skills.
3. Author `platforms/claude-code-plugin/skills/project-profile/SKILL.md`
   (utility; interviews/infers → writes both-scope profiles; builds on
   `context-analyzer` output rather than duplicating its scan).
4. Update `SKILL_AUTHORING.md` (utility list + skill count; `adapts:` is a new
   optional frontmatter field) and `skill-recommender` / plugin `README` /
   `doc-flow` cross-links.
5. Add conformance checks (see Verification). Bump `framework/VERSION` +
   `FRAMEWORK_SPEC_VERSION` to `0.2.0`.
6. **Verify** (below).
7. **Land:** one logical commit; `CHANGELOG.md` (project + plugin) +
   `ROADMAP.md`; tick `plans/MIGRATION_TODO.md`; record `D-0019`.

**ADAPT-B — the bridge**
8. Add the `.aidoc/learnings.md` entry-shape convention to `ADAPTATION.md`.
9. Author `knowledge-extractor/SKILL.md` (utility; the flow above; output ⊆
   `CHG-TEMPLATE.yaml`).
10. Add conformance check for proposal provenance + CHG-shape.
11. Wire cross-links (`doc-chg`, `gate-check`, `skill-recommender`, README).
12. **Verify**; **Land** as in step 7.

## Verification

Nothing is "done" until all pass. Concrete, runnable:

1. `python3 -m unittest discover -s tests/conformance` — full suite green
   (currently 32; grows by the new checks below).
2. `python3 tests/conformance/platforms/plm_lint.py --all` — clean (no legacy
   fingerprints in the two new skills or the edited base skills).
3. **Surface closed-set integrity** (new check): every knob name referenced by
   any skill's `adapts:` ∈ the closed set enumerated in `ADAPTATION.md`. No
   false negative — a skill declaring an off-surface knob must fail.
4. **Consult-clause presence** (new check): each of the 8 layer base skills that
   declares `adapts:` contains the standard clause text.
5. **Engine isolation** (extend `test_engine_isolation.py`): `ADAPTATION.md`
   carries no engine names (`hermes`, `claude code`, `mcp`, …) — it is
   engine-agnostic spec. Case-insensitive scan, same as PC4.
6. **No leakage** (new check): no `.aidoc/profile.yaml` / `.aidoc/learnings.md`
   committed anywhere under `framework/` (project artifacts must not enter the
   spec). Guards D-0013.
7. **Version match** (existing `test_version_declaration.py`): after the bump,
   `FRAMEWORK_SPEC_VERSION` still equals `framework/VERSION` (both `0.2.0`).
8. **Extractor output shape** (ADAPT-B, new check): a fixture profile+learnings,
   walked through the extractor's documented steps by hand, yields a proposal
   skeleton whose required keys are a superset of `CHG-TEMPLATE.yaml`'s required
   keys (so `gate-check` can consume it). Manual walk-through — no runtime.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Profile becomes a prompt-injection vector (untrusted project input steering a skill). | Closed declarative surface; skills honor only `adapts:`⊆surface and ignore unknown keys; conformance asserts the bound (V3). No behavior, only data. |
| R2 | Extractor promotes idiosyncratic knowledge as if general. | Manual judgment gate + `recurrence`/`conflict` signals; proposal must pass `gate-check` + conformance; a human adopts. Never auto-applies. |
| R3 | Surface creep erodes the "single contract." | Surface is a closed set in `ADAPTATION.md`; adding a knob is itself a CHG-governed spec change, not an ad-hoc edit. Start with 5 knobs. |
| R4 | Parity drift — plugin honors the profile, Hermes does not. | The surface spec is engine-agnostic and shared; plugin implements first; Hermes conformance to it is a tracked follow-up (noted in `docs/PARITY.md`), not silently skipped. |
| R5 | Project `.aidoc/` artifacts leak into `framework/` (violates D-0013). | Conformance leakage check (V6); `.aidoc/` is documented as consuming-project-owned. |
| R6 | The "consult-clause" is just prose — no guarantee a skill obeys at runtime. | Accepted: matches the framework's declarative model (skills are instructions, not code). Conformance checks the clause *exists*; honoring it is the engine's job, same as every other skill instruction. |
| R7 | Spec-version bump ripples (the version check compares two files). | Bump both `framework/VERSION` and `FRAMEWORK_SPEC_VERSION` in the same commit; V7 catches a mismatch. |

## Review log

> ≥2 passes required before this plan may be implemented (D-0007). Each pass:
> re-read whole plan, list findings, fold fixes back above.

### Pass 1 — 2026-05-23T15:05:00Z

- **Precedence under-specified.** First draft named both scopes but not what
  happens when the *same* knob is set in both. Added explicit merge order
  (defaults < user-global < project) **and** conflict logging as extractor
  signal — folded into Approach §"Precedence + conflict logging".
- **`adapts:` could drift from the surface.** Nothing stopped a skill from
  declaring a knob `ADAPTATION.md` doesn't define. Added the closed-set
  integrity check (V3) with an explicit no-false-negative note.
- **Missed that `ADAPTATION.md` is itself a framework spec change.** Added the
  governance note (version bump `0.1.0→0.2.0` on both files; CHG-governed
  post-cutover) + R7 + V7.
- **Leakage risk to `framework/`.** Clarified `.aidoc/` is consuming-project-
  owned and added the leakage conformance check (V6, guards D-0013).
- **Learnings shape not pinned.** Per the cheap-now/expensive-later concern,
  locked the YAML entry schema (ts/layer/knob/default/chosen/rationale/
  recurrence/scope/conflict) in Approach.

### Pass 2 — 2026-05-23T15:40:00Z

- **Extractor↔CHG contract.** The flow said "emit a CHG proposal" but didn't
  pin the handoff shape, so `gate-check` consumption was unverified. Added V8
  (proposal required-keys ⊇ `CHG-TEMPLATE.yaml` required-keys, manual
  walk-through) and the explicit "shaped to `CHG-TEMPLATE.yaml`" wording in the
  flow step 4.
- **Threshold knob ambiguity.** "audit_thresholds" could be read as letting a
  profile weaken the blocking gate. Tightened §surface item 3: advisory (Tier-2)
  values only; `gate_ready` blocking criteria are not tunable — keeps the
  conformance-never-weakened rule (CLAUDE.md) intact.
- **Skill count.** Noted SKILL_AUTHORING.md's "(46)" header is already stale
  (52 after P3-T7); ADAPT adds 2 → 54. Folded into step 4 as an update target
  rather than a silent count drift.
- No further findings; surface, precedence, verification, and risks are
  internally consistent. Plan is stable and ready to implement on approval.
