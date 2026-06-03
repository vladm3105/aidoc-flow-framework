# PROFILE-DELTA-001 Plan — Project Profile as Override-Only Delta

| Field      | Value                                       |
|------------|---------------------------------------------|
| Task       | PROFILE-DELTA-001                           |
| Depends on | D-0019 (ADAPT), BRD-RT-001 (merged)         |
| Status     | PLANNED — 2026-06-03T14:14:42Z              |
| Feeds      | Per-layer review-team follow-ups (PRD-RT, EARS-RT, …) — they'll consume the resolved profile via the same mode-resolution rule |

## Objective

Make `.aidoc/profile.yaml` a **project-specific override delta** instead
of a verbatim copy of the framework default. Today's bootstrap copies
`framework/governance/REVIEW_CREWS.yaml` byte-for-byte into the project
— producing a 60-line file where every line is potentially an
override or a stale default, with no way to distinguish them. After
this PR, `.aidoc/profile.yaml` carries only the keys the project chose
to override; every unset key falls through to framework defaults via a
documented precedence chain (framework defaults < user-global seed <
project profile, per `framework/governance/ADAPTATION.md`).

This unblocks two things the current design forecloses:

1. **Safe framework default evolution** — if `REVIEW_CREWS.yaml`
   re-weights a crew or adds a persona in v0.12 / v0.13, existing
   projects pick up the change automatically instead of staying frozen
   at the v0.11 snapshot.
2. **Readable profiles** — a future contributor opens
   `.aidoc/profile.yaml` and sees only what's been customized; the
   framework defaults are sourced where they belong.

## Scope

**In:**

- New file `framework/governance/PROFILE-TEMPLATE.yaml` — the
  override-only skeleton used as the bootstrap source.
- `tests/scripts/test-acceptance.sh:60` — switch
  `DEFAULT_PROFILE_SRC` from `REVIEW_CREWS.yaml` to the new template.
- Fallback chain in the suite's persona-list extraction (script
  lines 1245-1268) — read crews from the project profile if present,
  else from `framework/governance/REVIEW_CREWS.yaml`.
- Mode-resolution prompt clarification in `doc-brd-audit/SKILL.md`,
  `doc-brd-fixer/SKILL.md`, `doc-brd-autopilot/SKILL.md`,
  `doc-brd/SKILL.md` — extend "Read review_mode from `.aidoc/profile.yaml`"
  to "Read `review_mode` from `.aidoc/profile.yaml`; if absent, use the
  framework default."
- Replace `examples/url-shortener/.aidoc/profile.yaml` with the
  skeleton (matching the new bootstrap shape).
- New conformance test
  `tests/conformance/test_profile_schema.py` validating any project
  profile against the closed `ADAPTATION_SURFACE.yaml` knob set (any
  key outside the surface is a violation).
- Framework spec bump **0.11.2 → 0.11.3** (patch, additive — new
  template file, no schema change). Propagates across the standard ~59
  sync points (VERSION + FRAMEWORK_SPEC_VERSION × 2 + 52 plugin skills'
  `framework_spec_version` + conformance assertions).
- Plugin v0.4.1 → v0.4.2.
- Plugin CHANGELOG entry under `[Unreleased] → Changed`.
- Project CHANGELOG entry under `[Unreleased] → Added` for the new
  template file, and under `Changed` for the spec bump.
- New `DECISIONS.md` entry **D-0025** — Project profile is a delta, not
  a snapshot.

**Out:**

- Full layered config-merge engine with user-global seed file (Option A
  from the gap-analysis discussion). Over-engineered for current scale;
  the override-only skeleton + framework-default fallback is sufficient.
- Per-layer review-team wiring for PRD..IPLAN — separate follow-ups
  (PRD-RT-001 etc.), they'll consume the resolved profile transparently.
- `framework/governance/REVIEW_CREWS.yaml` content changes — the file
  stays as the engine-agnostic default; only the *role* of the file as
  the bootstrap source changes (it's no longer copied; it's the
  fallback target).
- Hermes-side profile mechanics — Hermes already implements adaptation
  via its own runtime; this PR is plugin/acceptance-suite-side.
- Caching follow-up (`REVIEW-TEAM-RUNNER-CACHING-001`) — separate
  v0.4.2/0.4.3 work; profile-delta and caching are independent
  optimisations on the same plugin v0.4.x stream.

## Approach

### Why this is a framework spec change (GATE-SPEC trigger)

Adding `PROFILE-TEMPLATE.yaml` to `framework/governance/` is additive
content under the spec root. Per the project's `framework/`-as-contract
rule, any file added under `framework/**` is a spec change. GATE-SPEC
applies — version bump, CHANGELOG, all 52 plugin skills'
`framework_spec_version` resync.

The bump is **patch** (0.11.2 → 0.11.3): the change is purely additive,
no schema breakage, no rule changes. A plugin pinned to spec 0.11.2
continues to work — the new template just isn't visible to it.

### Precedence chain (codified in ADAPTATION.md)

`ADAPTATION.md` already documents:

> Effective precedence: `framework defaults < user-global seed < project profile`.

This plan operationalises the chain. Each adaptation knob has a
resolution order:

1. Read from `.aidoc/profile.yaml` if the key is set.
2. Else, read from `~/.aidoc/profile.yaml` (user-global seed) — **not
   implemented in this PR**, but the fallback path leaves room for it.
3. Else, read from the framework default
   (`framework/governance/REVIEW_CREWS.yaml` for crews,
   `framework/governance/ADAPTATION_SURFACE.yaml` for knob ranges).

In this PR, step 2 is a documented future hook; the engine reads
profile → framework default with no user-global layer.

### The new template (illustrative — final shape TBD during impl)

`framework/governance/PROFILE-TEMPLATE.yaml`:

```yaml
# Project profile — overrides for framework defaults.
# Unset/commented keys fall through to:
#   - framework/governance/REVIEW_CREWS.yaml (crews + weights + default_mode)
#   - framework/governance/ADAPTATION_SURFACE.yaml (knob ranges)
# Authority: framework/governance/ADAPTATION.md

metadata:
  schema_version: "1.0.0"
  project_name: "<your project>"

# === Adaptation knobs (uncomment to override) ===

# review_mode: team           # team | single_pass — default team at gates
# audit_threshold: 90         # raise-only — must be >= framework default
# active_layers: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
# section_toggles:
#   brd:
#     executive_summary: false   # toggle off optional BRD §2
# glossary: {}

# === Per-layer crew override (full structure if needed) ===
# Falls through to REVIEW_CREWS.yaml when unset. Override only when the
# project genuinely needs a different crew or weights.
# crews:
#   BRD:
#     review: {architect: 40, business_analyst: 30, auditor: 20, adversary: 10}
```

### Fallback semantics for the acceptance suite

`tests/scripts/test-acceptance.sh:1244-1268` currently extracts personas
from the project profile only. Refactor to a fallback chain:

```bash
# Pseudocode:
personas = read_from_profile($PROFILE_FILE, "personas")
if not personas:
  personas = read_from_framework("REVIEW_CREWS.yaml", "personas")
```

Implementation: extend the existing Python YAML parse to fall back to
`framework/governance/REVIEW_CREWS.yaml` when the project profile lacks
a `personas:` block (or a `crews:` block, depending on which key the
suite needs).

### Skill mode-resolution refinement

The doc-brd-* skills currently say "Resolve `review_mode` from
`.aidoc/profile.yaml`. Default `team` at gates." Extend to:

```
Resolve `review_mode` from `.aidoc/profile.yaml`; if unset, use the
framework default (`team` at gates per the precedence chain in
${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md). Same fallback
applies to every adaptation knob (audit_threshold, section_toggles,
active_layers).
```

This is a doc-only refinement — the skill text already implies the
default; this codifies the fallback rule.

## Step sequence

1. **Create `framework/governance/PROFILE-TEMPLATE.yaml`** — the
   override-only skeleton (see Approach above for the illustrative
   shape; final keys verified against `ADAPTATION_SURFACE.yaml`).
2. **Framework spec bump** via `tools/bump_version.py 0.11.3` — handles
   the 59-file fanout (`framework/VERSION`,
   `platforms/{hermes,claude-code-plugin}/FRAMEWORK_SPEC_VERSION`, 52
   plugin skills' `framework_spec_version`). Verify the script handles
   the new template file (probably doesn't need to touch it; the script
   only touches version-pinned files).
3. **Acceptance suite changes** (`tests/scripts/test-acceptance.sh`):
   - Line 60: `DEFAULT_PROFILE_SRC` → new template path.
   - Lines 1244-1268: persona-list extraction gets a fallback chain
     (profile → REVIEW_CREWS.yaml).
4. **Update `examples/url-shortener/.aidoc/profile.yaml`** to the new
   skeleton (5-10 lines of metadata + commented-out knobs, no crews
   copy).
5. **Skill mode-resolution refinements** (the 4 doc-brd-* skills):
   one-paragraph clarification on the fallback chain. Add a short
   sentence to `review-team/SKILL.md` mentioning the same precedence.
6. **New conformance test**
   `tests/conformance/test_profile_schema.py`:
   - Validates that any `.aidoc/profile.yaml` in `examples/*/` only
     contains keys defined in `framework/governance/ADAPTATION_SURFACE.yaml`
     (closed-surface check).
   - Validates that the new `PROFILE-TEMPLATE.yaml` parses as YAML and
     contains only commented-out knobs (no hard-coded values).
7. **Plugin version bump** 0.4.1 → 0.4.2 (`VERSION` +
   `plugin.json` + `marketplace.json` + 52 skills' `version:` field +
   plugin README + root README + `docs/PARITY.md` +
   `docs/TAGGING.md` (new tag row) + `SKILL_AUTHORING.md`).
8. **Plugin CHANGELOG entry** at
   `platforms/claude-code-plugin/CHANGELOG.md` under
   `[Unreleased] → Changed`.
9. **Project CHANGELOG entry** at root `CHANGELOG.md` under
   `[Unreleased] → Changed` for the spec bump 0.11.2 → 0.11.3, with a
   sub-bullet citing the new template file.
10. **DECISIONS.md entry D-0025** at `plans/DECISIONS.md` recording
    "Project profile is a delta, not a snapshot."
11. **Verify** (see Verification section below).
12. **Land** — single PR. Update plugin CHANGELOG and project
    CHANGELOG. No `ROADMAP.md` update needed.

## Verification

Cheap-to-expensive ladder. Steps 1-4 are free / quick.

1. **Static lint + conformance** (free, < 30s):

   ```sh
   env -u LD_LIBRARY_PATH pre-commit run --files \
     framework/governance/PROFILE-TEMPLATE.yaml \
     framework/VERSION \
     platforms/claude-code-plugin/VERSION \
     platforms/claude-code-plugin/.claude-plugin/plugin.json \
     .claude-plugin/marketplace.json \
     tests/scripts/test-acceptance.sh \
     tests/conformance/test_profile_schema.py \
     examples/url-shortener/.aidoc/profile.yaml \
     CHANGELOG.md \
     platforms/claude-code-plugin/CHANGELOG.md \
     plans/DECISIONS.md
   python3 -m unittest discover -s tests/conformance -v
   ```

   Pass criteria: all hooks green; **94/94 tests pass** (existing 91 +
   new `test_profile_schema.py` adds 3).

2. **Schema validation of the new template** (free):

   ```sh
   python3 -c "import yaml; yaml.safe_load(open('framework/governance/PROFILE-TEMPLATE.yaml'))"
   python3 -c "import yaml; yaml.safe_load(open('examples/url-shortener/.aidoc/profile.yaml'))"
   ```

   Pass criteria: both parse cleanly as YAML.

3. **Fallback-chain check** (free):

   Delete `examples/url-shortener/.aidoc/profile.yaml` temporarily, run
   the suite in dry-run mode to confirm bootstrap copies the new
   template (not REVIEW_CREWS.yaml):

   ```sh
   rm examples/url-shortener/.aidoc/profile.yaml
   bash tests/scripts/test-acceptance.sh url-shortener --no-live 2>&1 | grep "project profile"
   ```

   Pass criteria: bootstrap message names the new template file;
   resulting profile is ≤ 30 lines (skeleton-sized, not the 60-line
   REVIEW_CREWS.yaml copy).

4. **Mock-mode acceptance** (free, < 1 min):

   ```sh
   bash tests/scripts/test-acceptance.sh url-shortener --no-live
   ```

   Pass criteria: 7 PASS / 0 FAIL / 44 SKIP / 51 total — identical to
   the BRD-RT-001 baseline. Confirms no regression on the
   deterministic path.

5. **Single-layer team-mode live run** (~$2-3, ~10 min):

   ```sh
   bash tests/scripts/test-acceptance.sh url-shortener --live \
        --phase=cascade --from-layer=brd --to-layer=brd
   ```

   Pass criteria: same as BRD-RT-001 Verification step 4 — 4 slot
   files at `.aidoc/review/01_BRD/BRD-01_*/`, `report.md` present,
   `coverage.quorum_met=true`, audit score ≥ 90. Plus a new assertion:
   the audit's combined report shows the **fallback path** in its
   metadata block (because the example profile has no `review_mode`
   override, the framework default `team` is in effect).

6. **Override-respect check** (~$2, ~10 min):

   Edit `examples/url-shortener/.aidoc/profile.yaml` to set
   `review_mode: single_pass`, re-run step 5. Pass criteria: the audit
   runs in single_pass (no `.aidoc/review/` slots), confirming the
   project override beats the framework default.

7. **Full cascade** (~$15-25) — defer; same shape as BRD-RT-001's
   step 7.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Breaking existing projects that have a populated `.aidoc/profile.yaml` (full REVIEW_CREWS.yaml copy from the BRD-RT-001 era) | Backward-compat: if a profile has `crews:` or `personas:` keys, honor them as overrides. Fallback only kicks in when the keys are absent. No migration required for existing projects |
| R2 | Conformance test for the closed surface flags every existing project profile as non-conformant | The closed surface (`ADAPTATION_SURFACE.yaml`) already lists `review_mode, audit_threshold, section_toggles, active_layers, glossary`. The current url-shortener profile contains `metadata, default_mode, personas, crews` — these will need to be either added to the surface as legal pass-through keys, or migrated out. Test should error softly with a deprecation warning, not hard-fail, in v0.11.3; promote to hard-fail in v0.12 |
| R3 | Spec bump 0.11.2 → 0.11.3 triggers GATE-SPEC ceremony (59-file fanout) | The `tools/bump_version.py` script handles this fanout automatically. Same as every prior spec bump (0.11.0 → 0.11.1, 0.11.1 → 0.11.2) |
| R4 | New `tests/conformance/test_profile_schema.py` adds more friction to project authoring | Keep the schema check soft (warn, don't fail) on first land; promote to hard-fail in a later spec version after projects have migrated |
| R5 | Profile-fallback chain has multiple resolution points (script + 4 skills + future per-layer audit skills) — drift risk if any one forgets to fall back | Centralize the resolution in a documented sentence ("Read X from `.aidoc/profile.yaml`; if unset, use framework default") and reuse it verbatim across all skill mode-resolution sections. Single source of truth in `ADAPTATION.md` |
| R6 | The Caching follow-up (`REVIEW-TEAM-RUNNER-CACHING-001`) and this one both want to be v0.4.2 | Land this as v0.4.2 first (simpler, no Python runner, no SDK dependency); land caching as v0.4.3. Reverse order would force re-touching all 52 skills' version field twice |

## Review log

### Pass 1 — 2026-06-03T14:14:42Z

Initial draft from the gap-analysis discussion in this session.
Findings folded back into the sections above:

- Framework spec bump is required (adding a file under `framework/`
  triggers GATE-SPEC). Status: documented as expected, version bump
  0.11.2 → 0.11.3 (patch, additive).
- The fallback chain semantics need to be implemented in BOTH the
  acceptance suite (script Python YAML parse) AND the doc-brd-* skill
  mode-resolution prompts. Both surface points enumerated in Step
  sequence.
- Backward-compat: existing projects with a full REVIEW_CREWS.yaml
  copy in their `.aidoc/profile.yaml` must continue to work without
  migration. R1 captures this; the implementation just treats present
  keys as overrides (no behavior change for them) and adds fallback
  for absent keys.
- The closed-surface conformance check is a real friction risk for
  existing projects — added R2 with soft-warn / promote-later
  mitigation strategy.
- Verification step 6 ("override-respect check") is the key
  end-to-end test: confirms a project override actually beats the
  framework default. Added as a distinct cheap step (~$2).

### Pass 2 — 2026-06-03T14:14:42Z

Re-read whole plan. No new findings.

- **Verification calibration**: every pass criterion in steps 1-6
  maps to a specific transformation rule in Step sequence:
  - PROFILE-TEMPLATE.yaml creation (Step 1) → "skeleton ≤ 30 lines"
    (Verification 3)
  - Acceptance suite changes (Step 3) → "bootstrap message names new
    template" (Verification 3)
  - Skill mode-resolution refinement (Step 5) → "audit report shows
    fallback path in metadata" (Verification 5)
  - DEFAULT_PROFILE_SRC change (Step 3) → "no regression on
    deterministic baseline" (Verification 4)
  - Override semantics (whole architecture) → "single_pass override
    beats team default" (Verification 6)
- **Scope check**: every "Out:" item has a clear deferral target.
- **Risks check**: 6 risks identified; R1 (backward-compat) and R2
  (closed-surface friction) are the load-bearing ones. R6
  (sequencing with caching follow-up) is a coordination concern, not
  a technical risk.
- **Spec-bump check**: the 0.11.2 → 0.11.3 bump is documented
  consistently across Step sequence (Step 2 + Step 9) and is purely
  patch (additive file, no schema break, no rule change).

Plan ready for implementation when BRD-RT-001 is verified end-to-end
via a live cascade run (currently the only outstanding step from
that PR is Verification step 4 — single-layer team-mode live run).
