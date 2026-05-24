# ADAPT Plan — Project adaptation overlay + knowledge extractor

| Field      | Value                          |
|------------|--------------------------------|
| Task       | ADAPT (ADAPT-0 prereq · ADAPT-A overlay · ADAPT-B bridge) |
| Depends on | D-0012, D-0013, CHG overlay (`framework/governance/chg/`), P3-T7 (`doc-chg` + `gate-check`), **ROADMAP CHG-D1 (spec-change gate — currently unbuilt; see ADAPT-0)** |
| Status     | PLANNED (Pass 3/4; ADAPT-0 resolved = defer) — 2026-05-23T17:30:00Z |
| Feeds      | A future `D-0019` (resolved decisions) · the post-v1.0 domain-profile / IPLAN-corpus direction (D-0012 R2) |

## Objective

Give a *consuming* project a bounded way to adapt how the SDD skills behave —
without forking the framework — and a manual, developer-triggered path to
**promote** locally-proven adaptations to the correct governance owner. Two
layers, one contract:

- **Layer 1 — the overlay.** A project declares a small, closed set of
  preferences in a version-controlled profile; skills (including the
  quality-gate variants) read it at authoring/audit time. Project-local;
  affects nobody else.
- **Layer 2 — the bridge.** A `knowledge-extractor` skill, run on demand, mines
  the profile + a learnings log, classifies what looks generalizable, and
  **routes each candidate to the governance path that actually owns the target**
  (Gap-1/2 fix): a change to the **`framework/` spec** is a CHG candidate; a
  change to **plugin skill guidance** is an ordinary platform PR. It only
  *drafts and routes* — it never edits, never auto-PRs, never approves.

## Governance model (the correction that drives this revision)

`docs/PROJECT.md` §6 is explicit about who governs what post-cutover:

- **`framework/` spec changes** (templates, governance, registry) → the gated
  **CHG process**. *But the spec-change CHG gate is itself unbuilt* (ROADMAP
  CHG-D1, "Not built during migration"). The existing gates (`GATE-01…CODE`)
  and `CHG-TEMPLATE.yaml` `change_source` values model the **8-layer artifact
  chain in a consuming project**, not spec changes — so there is no gate to run
  for a spec change today.
- **Platform-internal changes** (plugin skills, Hermes server) → *"ordinary
  SemVer + changelog + PR review — the gated process is **not** applied to a
  platform's own commits."*

The original plan routed *skill-guidance* changes through CHG — backwards on
both counts (skill guidance is the non-CHG path; the CHG path it leaned on
isn't built). The corrected model:

| Promotion target | Owner | Path | Reach | Built? |
|---|---|---|---|---|
| `framework/` template / governance / registry | framework spec | **CHG** (needs spec-gate) | both platforms | **No — needs CHG-D1** |
| plugin skill guidance / checklist | plugin platform | **ordinary PR** | plugin only | Yes |

So the extractor must **classify each candidate by target owner** and route
accordingly. v1 fully wires the **platform-PR path** (no unbuilt dependency);
the **spec→CHG path** is designed but **gated on ADAPT-0 / CHG-D1** — until that
lands, spec-level candidates are emitted as *CHG drafts a human cannot yet run a
gate on*, and the extractor says so plainly. This is an honest v1 limit: v1
promotions reach the plugin only; cross-platform reach waits for the spec-gate.

## Scope

**ADAPT-0 — prerequisite decision — RESOLVED 2026-05-23 (user): defer (option b).**
The choice was (a) **build the CHG spec-change gate** (CHG-D1: a `spec`/`meta`
`change_source` + a `GATE-SPEC` definition under `framework/governance/chg/gates/`)
so spec-level promotions have a real gate, or (b) **defer the spec path** — ship
ADAPT-B with the platform-PR path only and leave spec promotion as a documented
follow-up. **Decided: (b).** Rationale: smaller; unblocks the useful majority
(local adaptation + plugin-level promotion); lets CHG-D1 be designed on its own
merits rather than rushed under this task. Consequences: v1 promotions reach the
**plugin only** (Hermes waits for CHG-D1); spec-level candidates are still
*drafted* by the extractor but stamped "blocked — needs CHG-D1". ADAPT-A's own
spec doc (itself a framework-spec change) lands under interim PR-review controls,
recorded as `D-0019`. Building CHG-D1 is now an explicit out-of-scope follow-up.

**ADAPT-A — the overlay (in):**

- `framework/governance/ADAPTATION.md` (prose spec) **+ `ADAPTATION_SURFACE.yaml`**
  — a **machine-readable closed knob registry** (Gap-7 fix), analogous to
  `registry/LAYER_REGISTRY.yaml`. Conformance reads the YAML, not prose.
- The 5 knobs, redefined against the real models (see Approach): `active_layers`,
  `section_toggles`, `audit_threshold`, `id_format`, `glossary`.
- `project-profile` plugin skill — maintains the **project** profile
  (`.aidoc/profile.yaml`, version-controlled) and *materializes* any
  user-global seed into it (Gap-8 fix).
- The standard **consult-clause** + `adapts:` frontmatter on the adapting set —
  **not just the 8 base skills** (Gap-4 fix). The set is every skill that
  authors or checks layer structure:
  - layer **base** + **autopilot** + **audit** (×8) — audit/autopilot must be
    profile-aware or they false-fail adapted docs;
  - **fixer** (×8) — inherits via the audit report, but carries `adapts:` so it
    won't reintroduce a toggled-off section;
  - **`trace-check`** — must skip cross-refs to disabled layers (Gap-5);
  - **`project-init`** + **`project-adopt`** — scaffold only `active_layers`
    (Gap-6).
- Conformance checks (see Verification).

**ADAPT-B — the bridge (in):**

- `.aidoc/learnings.md` entry-shape convention (locked; see Approach) + a
  lightweight, best-effort **capture path** (Gap-9).
- `knowledge-extractor` plugin skill — classifies + routes + drafts:
  platform-PR path fully wired; spec→CHG path emits a CHG draft + the CHG-D1
  blocker note.
- Conformance check that a *platform-PR* draft is well-formed and a *spec* draft
  carries provenance + is flagged as CHG-D1-blocked.

**Out (deferred):**

- **Executing** either path (auto-PR / auto-CHG) — extractor drafts only.
- **Hermes runtime honoring** of the profile — surface spec is shared and
  engine-agnostic; plugin implements first; Hermes conformance is a tracked
  `docs/PARITY.md` follow-up.
- **Cross-project corpus** generalizability ("contradicted by other projects")
  — manual judgment in v1; only the signal shape is locked now.
- Building **CHG-D1's spec-gate** itself, if ADAPT-0 picks (b).

## Approach

### The promotion gradient

```
1. Correction in a session                    (ephemeral)
2. Logged learning   .aidoc/learnings.md       (project-local, raw signal)
3. Profile rule      .aidoc/profile.yaml        (project-local, changes skill behavior)
4. Promotion candidate   ← knowledge-extractor flags + classifies by owner
5a. framework/ spec change  → CHG draft → (CHG-D1 gate) → both platforms     [v1: drafted, gate pending]
5b. plugin skill change     → ordinary PR → review/merge → plugin only        [v1: fully wired]
```

### Where artifacts live

| Artifact | Location | Owner |
|---|---|---|
| Surface spec (prose) | `framework/governance/ADAPTATION.md` | framework |
| Surface registry (machine-readable) | `framework/governance/ADAPTATION_SURFACE.yaml` | framework |
| Project profile | `.aidoc/profile.yaml` (version-controlled) | consuming project |
| User-global seed | `~/.aidoc/profile.yaml` | consuming developer |
| Learnings log | `.aidoc/learnings.md` | consuming project |
| `project-profile`, `knowledge-extractor` skills | `platforms/claude-code-plugin/skills/<name>/` | plugin |

`.aidoc/` never enters this repo; `framework/` ships only the spec + registry,
skills ship only guidance + example snippets. A conformance leakage check
guards `framework/` (Gap from D-0013).

### The adaptation surface — narrow, closed, redefined (5 knobs)

Each knob is declared in `ADAPTATION_SURFACE.yaml` with `name`, `type`,
`constraint`, and `runtime_scope`. Skills honor only what's listed and ignore
unknown keys.

1. **`active_layers`** — which of the 8 layers are in play. **Constraint:** only
   layers in the registry's `skippable` set may be disabled; mandatory layers
   that anchor the chain cannot (Gap-5). `trace-check`, `-audit`, and
   `project-init`/`-adopt` consult this so they neither scaffold, demand a
   ref to, nor flag a disabled layer.
2. **`section_toggles`** — per-layer optional sections on/off, restricted to the
   template's declared-*optional* set; required sections are not toggleable.
3. **`audit_threshold`** — the layer-audit **quality-gate score** (the real
   model: `doc-*-audit` Tier-1, default **90**). **Constraint: raise-only** —
   a profile may set it `≥` the framework default, never lower (Gap-3;
   preserves CLAUDE.md "never weaken a check"). The CHG *gate-approval* model
   has no score and is untouched.
4. **`id_format`** — choice among conventions already allowed by
   `ID_NAMING_STANDARDS.md`; never a new scheme.
5. **`glossary`** — preferred-term substitutions. **Mechanics (Gap-11):**
   applied to **generated prose only**; audits do **not** enforce terminology
   in v1 (advisory at most). The one knob a user-global seed may carry.

`ADAPTATION_SURFACE.yaml` also carries `schema_version` (Gap-10); the profile
records the `schema_version` it targets.

### Scopes + reproducibility (Gap-8 fix — refines the earlier precedence rule)

The earlier "defaults < user-global < project at runtime" breaks CI/audit
reproducibility (`~/.aidoc` is absent in CI, so the same repo audits
differently). Refinement, preserving both scopes:

- **Runtime (skills, including audits/gates) read the project profile only** —
  fully version-controlled → reproducible everywhere.
- **User-global is an authoring-time *seed*.** `project-profile`, when creating
  or refreshing `.aidoc/profile.yaml`, merges the user-global seed in
  (project value wins on conflict) and **materializes** the result into the
  committed project profile. Same precedence semantics (defaults < user-global
  < project), merge moved to authoring time.
- A same-knob project-vs-seed override is still logged as a learnings entry with
  `conflict: true` (negative generalizability signal).

### Learnings entry shape + capture (Gap-9)

Shape locked (one YAML list item per learning in `.aidoc/learnings.md`):

```yaml
- ts: 2026-05-23T16:40:00Z      # ISO 8601 UTC
  layer: EARS                    # layer name | "utility:<name>" | "cross"
  knob: section_toggles.security # surface path, or "none" (not yet a knob)
  default: <framework default>
  chosen: <project value>
  rationale: <why>
  recurrence: 1                  # bumped when same (layer,knob,chosen) recurs
  scope: project                 # project | user-global
  conflict: false                # true if project overrode the user-global seed
```

**Capture path (best-effort, no runtime code):** (a) `project-profile` offers a
"log a learning" action; (b) the adapting skills, when they *apply* a profile
override or take a user correction, are instructed to append an entry and bump
`recurrence` if a matching one exists. v1 is honest that `recurrence` is
best-effort, not authoritative — it weights, not decides.

### Extractor flow (ADAPT-B) — classify, route, draft

1. Read project profile + `.aidoc/learnings.md`; diff against framework
   defaults → active deviations.
2. **Classify generalizability** (manual judgment; `recurrence` weights up,
   `conflict` weights down). Idiosyncratic items stay local — the skill says so.
3. **Classify target owner** for each generalizable item:
   - touches a template / governance rule / the registry → **framework spec**;
   - touches how a *skill* guides authoring → **plugin skill**.
4. **Route + draft:**
   - spec target → a **CHG draft** shaped to `CHG-TEMPLATE.yaml` with provenance,
     plus an explicit **"blocked on CHG-D1 spec-gate"** banner (v1 cannot run a
     gate for it);
   - skill target → a **PR-ready change description** (file, before/after,
     provenance) — *not* a CHG record, per §6.
5. A **human** takes the draft into the right path. The skill never executes or
   approves.

### Governance of this feature itself

ADAPTATION.md + the registry are a framework-spec change → bump
`framework/VERSION` `0.1.0 → 0.2.0` and the matching plugin
`FRAMEWORK_SPEC_VERSION` (kept equal; version check compares them). Post-cutover
this *wants* CHG, but that's the unbuilt spec-gate — ADAPT-0 records landing it
under interim PR-review controls (or sequences CHG-D1 first).

## Step sequence

**ADAPT-0** — resolve the spec-gate prerequisite (recommend defer = option b);
record as `D-0019`; note ADAPT-A's interim-controls landing.

**ADAPT-A — overlay**

1. Write `ADAPTATION.md` + `ADAPTATION_SURFACE.yaml` (5 knobs, constraints,
   `runtime_scope`, `schema_version`, consult-clause wording, required/skippable
   layer sets). Link from `governance/README.md`; reference the `skippable` set
   from `registry/LAYER_REGISTRY.yaml`.
2. Add `adapts:` + consult-clause to the **adapting set**: layer base + autopilot
   - audit + fixer (×8), `trace-check`, `project-init`, `project-adopt`. Each
   declares only the knobs it honors (e.g. audit → `section_toggles`,
   `active_layers`, `audit_threshold`).
3. Author `project-profile/SKILL.md` (utility; interviews/infers → writes the
   project profile; materializes the user-global seed; builds on
   `context-analyzer`, doesn't duplicate its scan).
4. Update `SKILL_AUTHORING.md` (utility list; correct the stale "(46)" count —
   now 52 + 2 = **54**; document `adapts:` as a new optional frontmatter field),
   `skill-recommender` intent map, plugin `README`, `doc-flow` cross-links.
5. Add conformance checks (Verification). Bump `framework/VERSION` +
   `FRAMEWORK_SPEC_VERSION` → `0.2.0`.
6. **Verify**; **Land** (one logical commit; `CHANGELOG.md` project+plugin;
   `ROADMAP.md`; tick `MIGRATION_TODO.md`; record `D-0019`).

**ADAPT-B — bridge**
7. Add the learnings convention + capture path to `ADAPTATION.md`.
8. Author `knowledge-extractor/SKILL.md` (classify → route by owner → draft;
   platform-PR path wired, spec→CHG path drafted + CHG-D1-blocked banner).
9. Add conformance check (proposal well-formedness + provenance + routing).
10. Wire cross-links (`doc-chg`, `gate-check`, `skill-recommender`, README).
11. **Verify**; **Land** as in step 6.

## Verification

Nothing is "done" until all pass.

1. `python3 -m unittest discover -s tests/conformance` — full suite green
   (currently 32; grows by the checks below).
2. `python3 tests/conformance/platforms/plm_lint.py --all` — clean (new + edited
   skills carry no legacy fingerprints).
3. **Surface registry parses** and is a closed set; every `adapts:` knob across
   all skills ∈ the registry (Gap-7). No false negative — an off-surface knob
   must fail. Reads `ADAPTATION_SURFACE.yaml`, not prose.
4. **Consult-clause presence** on every skill in the adapting set that declares
   `adapts:`.
5. **Raise-only threshold** (Gap-3): the registry constrains `audit_threshold`
   to `≥` framework default; a fixture profile setting it lower must be rejected
   by the documented validation.
6. **Audit profile-awareness, no false positive** (Gap-4, manual walk-through —
   no runtime): fixture with an *optional* section toggled off + that section
   absent → profile-aware `-audit` does **not** raise a Tier-1 structure
   failure; a *required* section absent → it still does.
7. **Trace-check / active_layers** (Gap-5, walk-through): with a *skippable*
   layer disabled, trace-check does not demand a ref to it; disabling a
   *mandatory* layer is rejected at profile-validation.
8. **Engine isolation** (extend `test_engine_isolation.py`): `ADAPTATION.md` +
   `ADAPTATION_SURFACE.yaml` carry no engine names (case-insensitive, like PC4).
9. **No leakage** (Gap/D-0013): no `.aidoc/profile.yaml` or `.aidoc/learnings.md`
   committed under `framework/`.
10. **Version match** (`test_version_declaration.py`): post-bump
    `FRAMEWORK_SPEC_VERSION` == `framework/VERSION` == `0.2.0`.
11. **Extractor routing** (ADAPT-B, walk-through): a spec-target fixture yields a
    CHG draft carrying provenance **and** the CHG-D1-blocked banner; a
    skill-target fixture yields a PR-ready description (file + before/after +
    provenance) and **no** CHG record. Replaces the earlier (incorrect) "force
    everything into CHG shape" check.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Profile as prompt-injection vector (untrusted project input). | Closed declarative registry; skills honor only `adapts:`⊆surface, ignore unknown keys; conformance asserts the bound (V3). Data, not behavior. |
| R2 | Extractor promotes idiosyncratic knowledge. | Manual judgment + `recurrence`/`conflict` weighting; spec drafts still pass through CHG (when built) + a human; skill drafts through PR review. Never auto-applies. |
| R3 | Surface creep erodes the single contract. | Closed registry; adding a knob is itself a spec change (CHG, once built). Start at 5. |
| R4 | Parity drift — plugin honors profile, Hermes doesn't; spec promotions reach both, skill promotions only the plugin. | Surface spec is engine-agnostic + shared; plugin first, Hermes a tracked `docs/PARITY.md` follow-up; v1 honestly documents that skill-path promotions are plugin-only. |
| R5 | `.aidoc/` artifacts leak into `framework/`. | Leakage conformance check (V9); `.aidoc/` documented as consuming-project-owned. |
| R6 | Consult-clause is prose — no runtime guarantee. | Accepted: matches the declarative model; conformance checks existence, the engine honors it like any instruction. |
| R7 | Spec-version bump mismatch. | Bump both files one commit; V10 catches drift. |
| R8 | **ADAPT-B's spec path depends on the unbuilt CHG-D1 spec-gate.** | ADAPT-0 decides defer-vs-build; v1 ships the platform-PR path (no dependency) and emits spec drafts with an explicit blocked banner — no silent half-feature. |
| R9 | User-global breaks audit reproducibility in CI. | Runtime reads project scope only; user-global is an authoring-time seed materialized into the committed project profile (Approach §Scopes). |
| R10 | Disabling a mid-chain layer breaks traceability. | `active_layers` limited to a registry `skippable` set; mandatory layers can't be disabled; trace-check/audit are profile-aware (V7). |

## Review log

### Pass 1 — 2026-05-23T15:05:00Z

- Precedence under-specified → added merge order + conflict logging.
- `adapts:` could drift from surface → added closed-set integrity check.
- Missed that `ADAPTATION.md` is itself a spec change → added version-bump note.
- Leakage risk → added conformance check.
- Locked the learnings entry schema.

### Pass 2 — 2026-05-23T15:40:00Z

- Pinned the extractor↔CHG handoff shape (later found wrong — see Pass 3).
- Tightened the threshold knob to "advisory only" (later found wrong — Pass 3).
- Noted the stale skill count (→ 54).

### Pass 3 — 2026-05-23T16:40:00Z (gap review — codebase-grounded)

Eleven gaps found by checking the plan against the actual CHG/audit code;
folded as follows:

- **G1/G2 (critical) — governance inversion.** `docs/PROJECT.md` §6: CHG governs
  **`framework/` spec** changes; platform (skill) changes are **ordinary PRs, not
  CHG**; and the spec-change CHG gate is **unbuilt** (CHG-D1). The plan had routed
  *skill guidance* (the non-CHG thing) through CHG, leaning on a gate that
  doesn't exist. **Rewrote the promotion model**: extractor classifies by target
  owner and routes spec→CHG / skill→PR; added **ADAPT-0** to resolve the
  unbuilt-gate dependency (recommend defer); reframed Objective/Scope; added
  R8; replaced the CHG-shape check with the routing check (V11).
- **G3 (critical) — `audit_threshold` mapped backwards.** Real model
  (`doc-brd-audit:48,68,75`): the numeric score (default 90) is **Tier-1
  blocking**, not advisory; CHG gates have no score. Redefined the knob as the
  layer-audit score, **raise-only** (V5), preserving "never weaken a check."
- **G4 — deferring variants is incorrect, not just incomplete.** A profile-blind
  `-audit` Tier-1-fails an adapted doc for a toggled-off section.
  **Brought audit + autopilot + fixer into the adapting set** (V6).
- **G5 — `active_layers` had no traceability rule.** Added a registry
  `skippable`/mandatory split + profile-aware `trace-check` (V7, R10).
- **G6 — `project-init`/`project-adopt` integration missing.** Added them to the
  adapting set (scaffold only active layers).
- **G7 — surface unparseable.** Added machine-readable `ADAPTATION_SURFACE.yaml`;
  conformance reads it (V3).
- **G8 — user-global breaks CI reproducibility.** Refined scopes: runtime reads
  project profile only; user-global is an authoring-time seed materialized into
  the committed profile (R9).
- **G9 — capture undefined though `recurrence` drives the test.** Added a
  best-effort capture path; `recurrence` weights, doesn't decide.
- **G10 — schema versioning.** Added `schema_version` to registry + profile.
- **G11 — glossary mechanics.** Pinned: generated prose only; audits don't
  enforce terminology in v1.

### Pass 4 — 2026-05-23T17:10:00Z

- Re-read end-to-end against the corrected governance model. The adapting-set
  expansion (G4) and the routing split (G1/G2) are now internally consistent:
  every skill that *checks structure* (audit/autopilot/trace-check) consults the
  same knobs the *authoring* skills honor, so adapted docs pass their own gate.
- Confirmed no verification check is a false positive: V6/V7/V11 are
  manual walk-throughs (no runtime exists to execute), explicitly labelled.
- One residual judgement call was surfaced for the user: the ADAPT-0 spec-gate
  direction. **Resolved 2026-05-23 (user): defer = option b** — v1 ships the
  platform-PR promotion path; spec→CHG is a documented follow-up gated on
  CHG-D1. Reflected in ADAPT-0 + Scope/R4/R8.
- No further findings; plan is stable and ready to implement.
