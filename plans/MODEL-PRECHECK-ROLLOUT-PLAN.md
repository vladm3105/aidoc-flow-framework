# MODEL-PRECHECK-ROLLOUT Plan — surface `model.*` recommendations at interactive drafting entry points

| Field          | Value |
| -------------- | ----- |
| Task           | MODEL-PRECHECK-ROLLOUT |
| Type           | feature |
| Status         | PLANNED — 2026-06-21T00:00:00Z |
| Depends on     | PLUGIN-USER-COMMANDS (merged 2026-06-14) — introduced the `model.*` keys |
| Feeds          | — |
| Version impact | Claude Code plugin MINOR (`0.20.1 → 0.21.0`); no framework spec change |

## Objective

PLUGIN-USER-COMMANDS introduced `model.default` / `model.per_layer` /
`model.precheck` in the optional `.claude/aidoc-flow.config.yaml` and the
`/aidoc-flow:model` command that edits them — but **no skill consults them**.
`commands/model.md` documents that `precheck` is the mode "`doc-*` skills
consult … when … about to draft," yet that consult step does not exist. This
plan closes the honesty gap by surfacing the per-layer model recommendation at
the **interactive drafting entry points** so a human can switch model before
authoring a layer.

**It does NOT pretend to *compare* against the session model.** A running skill
cannot read its own session-model id (verified: `commands/model.md` states the
plugin runs "on whatever model the session is currently on" and cannot read or
switch it). So the precheck **prints the recommendation** + the exact `/model`
switch command and lets the human decide — no false "mismatch" claim. (Design
decisions D1–D4 below; superseded the original compare-based design after the
Pass 4 independent review found it unworkable in the default execution path.)

## Scope

**In:**

- A standardized **Model precheck** block added to the **drafting** entry
  points: the 8 `-autopilot` skills (the interactive cascade entry) and the 8
  base `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}` skills (standalone
  interactive drafting). 16 skills.
- The block reads `.claude/aidoc-flow.config.yaml` if present, resolves the
  recommended model (`model.per_layer.<LAYER>` → else `model.default`), and
  **prints one notice line** with the `/model <rec>` switch command. Behaviour
  keyed by `model.precheck`: `warn` (print + proceed, default) · `silent`
  (print nothing) · `block` (print + require an explicit "proceed"
  acknowledgement before drafting — interactive only).
- A one-line saga-driver change (`saga_driver.py`) stamping its headless
  subprocesses with `AIDOC_SAGA=1`, plus a guard clause in the **base** block
  that **suppresses the notice when that env var is set** (so the headless
  `draft` subprocess emits no pointless notice and `block` never pauses a
  non-interactive run). Autopilot needs no guard — the driver never dispatches
  autopilot; the user always invokes it interactively.
- One conformance test asserting the 16 skills carry the block + reference the
  canonical config keys, and that the autopilot block precedes the
  saga-driver invocation.
- Docs of record updated.

**Out of scope (deferred):**

- `doc-*-audit` / `doc-*-fixer` precheck (16 skills). The recommendation is
  about *drafting* quality; audit/fixer review and patch. Lower value, and they
  are the skills most often dispatched headless. The same guarded block drops
  in trivially later if direct interactive audit/fixer use shows a gap. Parked.
- Any *comparison* of recommended vs current model — impossible to do reliably
  (no session-model read); explicitly replaced by print-and-let-human-decide.
- Auto-switching the model — impossible (documented caveat in `commands/model.md`).
- `budget.*` precheck; any new config key/enum or `/aidoc-flow:model` change.

## Approach / Design

### D1 — Print the recommendation; never compare (resolves Pass-4 F3)

A skill has no reliable way to read its own session-model id, so a
"recommended ≠ current → warn" design is a near-permanent no-op. Instead the
block **always prints the per-layer recommendation** and the copy-paste
`/model <rec>` command; the human compares. This is fully implementable and
honest, and matches CONFIG.md's "advisory" framing.

### D2 — Print mechanism removes the headless-deadlock risk (resolves Pass-4 F2)

The original block-based design could deadlock a cascade because the saga
driver runs the drafting skill as a headless `claude -p` subprocess
(`saga_driver.py:387-401`) with no interactive user. A **print never blocks**,
so the deadlock evaporates. The only residual concern is *noise* — a notice
printed inside a `draft` subprocess is pointless. D3 handles that.

### D3 — Headless guard via an explicit driver stamp

The driver's `subprocess.run` (`saga_driver.py:406`) passes no custom `env`, so
today nothing distinguishes a headless saga subprocess from a standalone
interactive run. This plan adds `env={**os.environ, "AIDOC_SAGA": "1"}` to that
call. The **base** skill's block begins: "if the `AIDOC_SAGA` env var is set
(`printenv AIDOC_SAGA`), skip this section." Result: headless `draft`
subprocesses stay quiet; standalone interactive `doc-brd` prints the notice.
Autopilot is never dispatched headless, so its block needs no guard.

### D4 — `precheck` semantics under the print model

- `warn` (default): print the notice line, then proceed.
- `silent`: print nothing, proceed.
- `block`: print the notice plus a one-line "Confirm you want to draft on the
  current model, or run `/model <rec>` first." and **wait for explicit user
  acknowledgement** before drafting. Interactive only; under the `AIDOC_SAGA`
  guard the base block is skipped entirely, so `block` never stalls a headless
  run. (No model comparison is needed — `block` forces a conscious choice, it
  does not detect a mismatch.)

### D5 — Placement anchors (resolves Pass-4 F1)

- **Base skills (8):** new `## Model precheck` section after `## Prerequisites`
  (verified present in all 8 base skills) and before `## Layer Guidance`.
- **Autopilot skills (8):** they have **no `## Prerequisites` section** (verified
  — structure is `Purpose → Skill Dependencies → Input Contract → Smart
  Document Detection → Workflow → …`). The notice must print **before** the
  `## Workflow` section's "MANDATORY — DO THIS FIRST … invoke the saga driver
  via Bash" directive. Anchor: insert a `## Model precheck` section
  immediately **before `## Workflow`**, and amend the MANDATORY directive's
  wording to read "your first *orchestration* action MUST be the Bash saga-driver
  call" so a one-line preflight notice before it does not violate the
  no-bypass rule. The notice is explicitly NOT drafting and NOT an alternate
  orchestration path.

### D6 — Inline block, no shared include; conformance-guarded (Pass-4 F4 ack)

Skills are self-contained (SHARED_CONTENT.md removed under D-0013), so the block
is duplicated across the 16 skills with only `<LAYER>` differing. The TODO
entry said "gate by the acceptance suite, not a new test"; this plan **adds a
conformance test anyway** as a cheap anti-drift guard for 16 duplicated blocks
(the acceptance suite still exercises the live behaviour). Deviation noted
deliberately.

### Canonical block (base variant — autopilot variant drops the `AIDOC_SAGA` guard line)

```markdown
## Model precheck

Advisory. Surfaces the model you recommended for this layer; it does not and
cannot switch the session model.

1. If the `AIDOC_SAGA` environment variable is set (`printenv AIDOC_SAGA`),
   skip this section — you are running headless under the saga driver.   ← base only
2. If `.claude/aidoc-flow.config.yaml` is absent, or has no `model.*` keys,
   skip this section (no output).
3. Resolve the recommended model: `model.per_layer.<LAYER>` if set, else
   `model.default`.
4. Act on `model.precheck`:
   - `warn` (default) — print one line, then proceed:
     `ℹ <LAYER> recommends model '<rec>'. If you're not on it, run /model <rec> (or set model.precheck: silent to hide this).`
   - `silent` — print nothing; proceed.
   - `block` — print the line above plus
     `precheck=block: confirm you want to draft on the current model, or run /model <rec> first.`
     then wait for the user to confirm before drafting.
```

`<LAYER>` is the literal layer name (BRD…IPLAN); everything else is identical.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/conformance/platforms/test_model_precheck.py` | Asserts the 16 drafting skills carry `## Model precheck` + reference `model.precheck`/`model.per_layer`/`model.default`; asserts the autopilot block appears before the saga-driver Bash directive; asserts base blocks carry the `AIDOC_SAGA` guard line and autopilot blocks do not. |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}/SKILL.md` | + guarded `## Model precheck` block after `## Prerequisites` (8 base). |
| `platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-autopilot/SKILL.md` | + unguarded `## Model precheck` block before `## Workflow`; amend the MANDATORY directive to "first *orchestration* action" (8 autopilot). |
| `platforms/claude-code-plugin/tools/saga_driver.py` | `subprocess.run(cmd, …)` at ~L406 gains `env={**os.environ, "AIDOC_SAGA": "1"}`. |
| `platforms/claude-code-plugin/VERSION` | `0.20.1 → 0.21.0` (triggers the mechanical version-sync hook). |
| `platforms/claude-code-plugin/CHANGELOG.md` | `[0.21.0]` entry. |
| `platforms/claude-code-plugin/docs/CONFIG.md` | Add a "now honored by drafting skills (print-only)" note to the `model.*` section. |
| `plans/FRAMEWORK-TODO.md` | Move `MODEL-PRECHECK-ROLLOUT` Open → Closed with the merge ref; note audit/fixer deferral. |
| `plans/HANDOFF.md` | Top entry. |
| `plans/DECISIONS.md` | D1–D6. |

> The vendored saga-driver copy under the framework bundle is re-synced by
> `tools/sync-plugin-framework.sh` (the bundle includes `tools/`); run it after
> editing `saga_driver.py` and confirm the vendored copy matches (V4).

## Implementation sequence

### Task 1: Driver stamp + headless guard

- Add `env={**os.environ, "AIDOC_SAGA": "1"}` to the dispatch `subprocess.run`
  (`saga_driver.py` ~L406).
- **Test-first — [CODE]:** extend/author a saga-driver unit test asserting the
  dispatched subprocess env carries `AIDOC_SAGA=1` (monkeypatch
  `subprocess.run`, capture kwargs).

### Task 2: Block authoring + apply to 16 skills

- **Test-first — [CODE]:** write `test_model_precheck.py` (red) covering all
  assertions above, then make it green by inserting the blocks.
- Apply the base-variant block (with guard line) to the 8 base skills after
  `## Prerequisites`; apply the autopilot-variant block (no guard line) to the 8
  autopilot skills before `## Workflow`, and amend each autopilot MANDATORY
  directive wording per D5.

### Task 3: Version bump + mechanical sync + bundle re-sync

- Bump `VERSION` `0.20.1 → 0.21.0`; let `sync-version-refs.sh` propagate.
- Run `tools/sync-plugin-framework.sh`; confirm the vendored `saga_driver.py`
  copy updated and no other bundle drift.

### Task 4: Docs of record

- `CHANGELOG.md` `[0.21.0]`; `CONFIG.md` note; `FRAMEWORK-TODO` close;
  `HANDOFF`; `DECISIONS` D1–D6.

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python3 -m pytest tests/conformance/ -q` | all pass incl. new `test_model_precheck` | Scope |
| V2 | `python3 tests/conformance/platforms/plm_lint.py --all` | clean | regression guard |
| V3 | `grep -L "## Model precheck" skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}{,-autopilot}/SKILL.md` | empty (all 16 present) | D5 |
| V4 | `bash tools/sync-plugin-framework.sh && git diff --stat` | only the expected vendored `saga_driver.py` change; no unexpected drift | D3 / Task 3 |
| V5 | saga-driver unit test: dispatched subprocess env | contains `AIDOC_SAGA=1` | Task 1 |
| V6 | Standalone interactive run of `doc-brd` with config `model.per_layer.BRD: claude-opus-4-8`, `precheck: warn`, no `AIDOC_SAGA` | the `ℹ BRD recommends model 'claude-opus-4-8' …` notice prints, drafting proceeds | D1/D4 |
| V7 | Same with `precheck: silent` | no notice line | D4 |
| V8 | Headless path: confirm a saga `draft` subprocess (env `AIDOC_SAGA=1`) prints **no** notice | base block skipped | D3 |
| V9 | `cat platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` | `0.23.0` (no spec change) | Version impact |

## Docs to update

- [ ] `platforms/claude-code-plugin/CHANGELOG.md` — `[0.21.0]` entry
- [ ] `platforms/claude-code-plugin/docs/CONFIG.md` — now-honored note
- [ ] `plans/FRAMEWORK-TODO.md` — close `MODEL-PRECHECK-ROLLOUT` (+ audit/fixer deferral note)
- [ ] `plans/HANDOFF.md` — narrative + next steps
- [ ] `plans/DECISIONS.md` — D1–D6
- [ ] `ROADMAP.md` — not applicable (internal feature)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | The `printenv AIDOC_SAGA` guard adds a Bash call to every standalone base invocation | low | One cheap call; acceptable. Autopilot (the common path) has no guard. Could fold into an existing early Bash step if friction shows. |
| R2 | 16 duplicated blocks drift | med | `test_model_precheck` asserts presence + key refs + guard-line presence/absence per variant; drift fails CI (D6). |
| R3 | Amending the autopilot MANDATORY directive weakens the no-bypass guarantee | med | Reword to "first *orchestration* action MUST be Bash"; the notice is explicitly not drafting and not an alternate orchestration path; conformance asserts the block precedes the Bash directive, not replaces it. |
| R4 | Adding `env=` to `subprocess.run` breaks a saga test asserting exact call args | low | Inspect existing saga-driver tests first; `AIDOC_SAGA` is additive; update any exact-kwargs assertion. |
| R5 | `block` mode interactive pause annoys users | low | Opt-in (default is `warn`); `silent` is one `/aidoc-flow:model` edit away. |
| R6 | Vendored `saga_driver.py` bundle copy left unsynced → drift-guard CI fails | low | Task 3 runs `sync-plugin-framework.sh`; V4 proves it. |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | `model.precheck` enum `warn\|silent\|block`, default `warn` | precheck enum | `platforms/claude-code-plugin/docs/CONFIG.md:113,133,143` |
| 2  | `model.per_layer`/`model.default` exist; defaults `{}`/`claude-sonnet-4-6` | model keys | `platforms/claude-code-plugin/docs/CONFIG.md:99-106,131-132` |
| 3  | No skill reads precheck/per_layer today; only commands do | grep | `skills/` grep empty; only `commands/{model,configure}.md` |
| 4  | Plugin runs on the session model; cannot read/switch it → no reliable compare | caveat | `platforms/claude-code-plugin/commands/model.md` "Honest caveat" |
| 5  | All 8 base skills have `## Prerequisites` → `## Layer Guidance` | sections | `skills/doc-brd/SKILL.md:46,59` (pattern across 8, Pass-4 verified) |
| 6  | No autopilot skill has `## Prerequisites`; first orchestration step is the MANDATORY saga-driver Bash call before `## Workflow` | sections | `skills/doc-brd-autopilot/SKILL.md` (Workflow MANDATORY block; Pass-4 verified 8/8) |
| 7  | Driver dispatches `draft`/`review`/`fixer` as headless `claude -p --dangerously-skip-permissions` subprocesses | dispatch_phase | `platforms/claude-code-plugin/tools/saga_driver.py:387-406` |
| 8  | Driver `subprocess.run` passes no custom `env` (inherits parent) | subprocess.run | `platforms/claude-code-plugin/tools/saga_driver.py:406` |
| 9  | The framework bundle includes `tools/`, so the vendored saga-driver copy needs re-sync | sync scope | `tools/sync-plugin-framework.sh` (syncs `framework/` + `tools/`) |
| 10 | VERSION bump auto-syncs 52 SKILL frontmatter + manifests | sync hook | `scripts/sync-version-refs.sh` (loops `skills/*/SKILL.md` `version:`) |
| 11 | Conformance test harness is `unittest` + `_spec.REPO_ROOT`, no test freezes the skill section set | harness | `tests/conformance/platforms/test_plugin_config_schema.py`; `test_skill_template_alignment.py` (content, not header-set) |

## Review log

### Pass 1–3 — 2026-06-21 — author self-review (compare-based design)

- Converged *from the author's vantage* on a compare-and-warn design across 16
  skills. **Superseded by Pass 4**, which found the compare premise unworkable
  in the default execution path. Retained here for history.

### Pass 4 — 2026-06-21 — independent (fresh-context subagent, against the codebase)

- Claim ledger verified accurate. Three load-bearing gaps survived Passes 1-3:
  **F2** (team-mode autopilot dispatches the drafting skill as a headless
  `claude -p` subprocess → a `warn`/`block` block has no interactive user and
  `block` deadlocks the cascade; D1's "autopilot already prechecks" rationale
  inverted), **F3** (no mechanism to read the session model → compare is a
  near-permanent no-op, V5 unachievable), **F1** (the `## Prerequisites` anchor
  fails for all 8 autopilot skills). Minor: F4 (TODO said "no new test"), F6
  (phantom CONFIG.md edit). Non-issue: F5 (conformance test feasible).
- **Verdict: NOT READY — design revision required.**

### Pass 5 — 2026-06-21 — redesign folding Pass-4 findings + user decisions

> User decisions (2026-06-21): mechanism = **print recommendation, no compare**;
> placement = **interactive entry points only, guard headless**.

- **F3 → D1:** replaced compare-and-warn with print-the-recommendation. No
  session-model read needed; V6/V7 are now achievable (they assert the notice
  prints / is silent, not that a mismatch is detected).
- **F2 → D2+D3+D4:** a print never blocks, so the deadlock is gone; added the
  `AIDOC_SAGA=1` driver stamp (verified `subprocess.run` passes no env today,
  claim 8) + a base-skill guard so headless `draft` subprocesses stay silent;
  redefined `block` as an interactive acknowledgement pause (no comparison),
  skipped entirely headless.
- **F1 → D5:** autopilot anchor corrected to "before `## Workflow`" (verified no
  `## Prerequisites` exists, claim 6) with a precise MANDATORY-directive
  reword (R3) so the preflight notice doesn't bypass the driver.
- **F4 → D6:** kept the conformance test but explicitly acknowledged the TODO's
  "no new test" guidance and justified it (anti-drift for 16 copies).
- **F6:** CONFIG.md edit reframed from "remove no-skill-reads text" (phantom) to
  "add a now-honored note."
- **New surface from the redesign:** the saga-driver edit pulls
  `saga_driver.py` into scope → bundle re-sync (claim 9) + a possible saga-test
  update (R4); both captured in Task 3 / R4 / R6 and V4/V5.
- **Re-validation needed:** Pass 6 must confirm the driver-env change doesn't
  break existing saga unit tests and that the autopilot reword is consistent
  with every autopilot SKILL's actual MANDATORY wording (it may vary per layer).

### Pass 6 — 2026-06-21 — re-validation (found a load-bearing gap the redesign assumed away)

> Opened all 8 autopilot `## Workflow` bodies (not just headers) + checked
> which skills actually invoke the driver. Two of the three Pass-6 items came
> back clean; the third broke the redesign's premise.

- **F7 (LOAD-BEARING) — the autopilot corpus is mid-migration; only 2 of 8
  layer autopilots are saga-driven.** `grep -rl saga_driver.py skills/*/SKILL.md`
  → only `doc-brd-autopilot`, `doc-prd-autopilot`, `doc-chg-autopilot`. The
  6 layer autopilots `ears/bdd/adr/spec/tdd/iplan` still describe a **legacy
  in-session** numbered `## Workflow` (Generation → Validation → Audit↔fix via
  `../doc-<layer>/SKILL.md` references) — **no `saga_driver.py`, no headless
  subprocess.** `HERMES-BACKLOG.md:79` confirms "Phase 4 (PRD..IPLAN saga
  driver propagation)" is **pending plugin work** (SAGA-PARITY-001 is only
  BRD+PRD). Consequences:
  - Claims 6 & 7 and design D2/D3 (headless dispatch / `AIDOC_SAGA` guard) apply
    to **brd/prd only**. For the 6 legacy autopilots the base skill runs
    **in-session/interactive**, so no headless deadlock and no guard need —
    *today*.
  - Autopilot placement is **three** shapes, not one: brd ("MANDATORY — DO THIS
    FIRST"), prd ("Your VERY FIRST tool call MUST be Bash"), and 6 legacy
    (plain numbered Workflow, no first-call constraint → no reword needed).
  - **Coupling with SAGA-PARITY-001 Phase 4:** when Phase 4 rewrites the 6
    legacy autopilots to invoke the driver, their base skills become headless
    and will then need the `AIDOC_SAGA` guard. Whichever feature lands first
    must not silently break the other.
- **F8 (minor, doc-accuracy, OUT OF SCOPE) — `CLAUDE.md:19` overstates.** It
  claims "preemptive saga driver across all 8 layers (SAGA-PARITY-001)"; only
  3 of 9 autopilots invoke it. The driver is layer-capable, but the autopilot
  SKILLs that should call it for `ears..iplan` don't. Flag for a CLAUDE.md
  correction; not part of this plan.
- **F9 (resolved) — saga tests compatible.** `test_saga_driver_invariants.py`
  explicitly "does not spawn live subprocesses"; `test_saga_reconcile_post_audit.py`
  is reconcile-logic only. Neither asserts `subprocess.run` kwargs, so the
  `env=` addition (Task 1) breaks nothing. R4 downgraded to low/none.
- **Base-skill anchor (claim 5) re-confirmed** clean for all 8 base skills.
- **Verdict: NOT READY.** F7 means the design must either (a) keep the guard in
  all base skills defensively (harmless when `AIDOC_SAGA` unset, future-proof
  for Phase 4) and branch the autopilot placement three ways, OR (b) sequence
  this feature relative to SAGA-PARITY-001 Phase 4. This is a scoping/sequencing
  decision for the user, not a mechanical fix — see plan presentation.
