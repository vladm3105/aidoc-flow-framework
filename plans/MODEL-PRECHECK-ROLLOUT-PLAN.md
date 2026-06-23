# MODEL-PRECHECK-ROLLOUT Plan — surface the per-layer model recommendation at the autopilot entry point

| Field          | Value |
| -------------- | ----- |
| Task           | MODEL-PRECHECK-ROLLOUT |
| Type           | feature |
| Status         | READY FOR IMPL — 2026-06-22 (scope locked: autopilots-only; design converged Pass 1-7) |
| Depends on     | PLUGIN-USER-COMMANDS (`model.*` keys) + SAGA-PARITY-001 Phase 4 (uniform saga-driven autopilots) — both merged |
| Feeds          | — |
| Version impact | Claude Code plugin MINOR (`0.21.0 → 0.22.0`); no framework spec change |

## Objective

PLUGIN-USER-COMMANDS introduced `model.default` / `model.per_layer` /
`model.precheck` in the optional `.claude/aidoc-flow.config.yaml` and the
`/aidoc-flow:model` command that edits them. `commands/model.md` documents that
`precheck` is the mode "`doc-*` skills consult … when about to draft," but **no
skill consults it** — a documented-but-unimplemented behavior. This rollout
closes that honesty gap by surfacing the per-layer model recommendation at the
**autopilot entry point** (the single interactive moment that starts each
layer's cascade), so a human can switch model before authoring.

It does **not** compare against the session model (a skill can't reliably read
its own model id) — it **prints the recommendation** + the `/model <rec>`
switch command and lets the human decide.

## Scope

**In:**

- A standardized `## Model precheck` section added to the **8 autopilot**
  skills `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-autopilot`. It reads
  `.claude/aidoc-flow.config.yaml` if present, resolves the recommended model
  (`model.per_layer.<LAYER>` → else `model.default`), and acts on
  `model.precheck`: `warn` (print one notice line + proceed, default) ·
  `silent` (print nothing) · `block` (print + ask the user to confirm or switch
  before continuing). Absent config / keys → skip silently (no output).
- A one-line reword of each autopilot's saga-driver directive from "first
  **tool call** MUST be Bash" → "first **orchestration action** MUST be Bash",
  so the precheck (which reads the config — a tool call — and prints) is allowed
  to run *before* the driver invocation without being read as "bypassing the
  driver."
- One conformance test asserting all 8 autopilots carry `## Model precheck`
  and reference the canonical config keys.
- Docs of record + plugin MINOR bump.

**Out of scope (deferred):**

- **Base / audit / fixer skills.** Post-Phase-4 these run **headless** under the
  saga driver in the normal (team) flow, where a notice is pointless and `block`
  can't ask anyone. They'd only print for the *less-common* standalone
  invocation (`/aidoc-flow:doc-brd` directly), and covering that needs an
  `AIDOC_SAGA` headless-guard for no real gain. Park; pull only if standalone
  single-layer use shows a gap.
- **A saga-driver-based implementation.** The driver is the single orchestration
  point, but it's a Bash subprocess that can't cleanly pause for `block`'s
  acknowledgement — implementing in the autopilot SKILL (live session) keeps all
  three `precheck` modes honest. (D3.)
- Comparing recommended vs current model (impossible to do reliably); auto-
  switching the model (the plugin can't); any new config key or
  `/aidoc-flow:model` change; `budget.*` precheck.

## Approach / Design

### D1 — Print the recommendation; never compare

A skill has no reliable way to read its own session-model id, so a
compare-and-warn design is a near-permanent no-op. The block **always prints
the per-layer recommendation** + the copy-paste `/model <rec>` command; the
human compares. Honest and fully implementable; matches CONFIG.md's "advisory"
framing.

### D2 — Autopilot-only placement (the one interactive moment)

Phase 4 made every autopilot the single interactive entry that hands straight
to the saga driver. The precheck prints **once, interactively, at the top of
the autopilot** — covering the whole layer cascade — *before* the driver's
headless subprocesses spin up. The base/audit/fixer skills run headless under
the driver and are out of scope (see Scope). No `AIDOC_SAGA` guard, no driver
change.

### D3 — Implement in the SKILL, not the driver

Considered putting the config-read + notice in `saga_driver.py` (one place vs
eight). Rejected: the driver is a Bash subprocess that can't pause for the
user's `block` acknowledgement, so it would silently break `block`. The
autopilot SKILL runs in the live session and *can* ask — so SKILL-prose keeps
`warn`/`silent`/`block` all honest.

### D4 — `precheck` semantics under the print model

- `warn` (default): print the notice line, then proceed to the driver.
- `silent`: print nothing, proceed.
- `block`: print the notice + "Confirm you want to draft on the current model,
  or run `/model <rec>` first," and **wait for the user's reply** before the
  driver call. (No model comparison needed — `block` forces a conscious choice.)

### D5 — Placement anchor + the directive reword

Insert `## Model precheck` **after `## Smart Document Detection` and before
`## Workflow`** (verified section order across all 8 autopilots). Then reword
the Step-1 saga directive so the precheck may run first:

- 7 autopilots (`prd,ears,bdd,adr,spec,tdd,iplan`, Phase-4 wording): "Your VERY
  FIRST tool call MUST be the `Bash` tool" → "Your first **orchestration**
  action MUST be the `Bash` tool (after the Model-precheck notice above)".
- `doc-brd-autopilot` (pre-Phase-4 wording): "MANDATORY — DO THIS FIRST. Your
  first and only action … is to invoke the saga driver" → "… your first
  **orchestration** action … (after the Model-precheck notice above)".

The notice is explicitly NOT drafting and NOT an alternate orchestration path;
conformance asserts the precheck section precedes the Bash directive.

### Canonical block

```markdown
## Model precheck

Advisory, best-effort. Surfaces the model you recommended for this layer; it
cannot switch the session model. Before invoking the driver:

1. If `.claude/aidoc-flow.config.yaml` is absent, or has no `model.*` keys, skip
   this section entirely (no output).
2. Resolve the recommended model: `model.per_layer.<LAYER>` if set, else
   `model.default`.
3. Act on `model.precheck`:
   - `warn` (default) — print one line, then continue to the driver:
     `ℹ <LAYER> recommends model '<rec>'. If you're not on it, run /model <rec> (or set model.precheck: silent to hide this).`
   - `silent` — print nothing; continue.
   - `block` — print the line above plus
     `precheck=block: confirm you want to draft on the current model, or run /model <rec> first.`
     and wait for the user to confirm before continuing.
```

`<LAYER>` is the literal layer name (BRD…IPLAN); everything else is identical.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/conformance/platforms/test_model_precheck.py` | Assert all 8 autopilots carry `## Model precheck` referencing `model.precheck`/`model.per_layer`/`model.default`, and that the section precedes the `saga_driver.py` directive. |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/claude-code-plugin/skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-autopilot/SKILL.md` | + `## Model precheck` section before `## Workflow`; reword the Step-1 saga directive (8 files). |
| `platforms/claude-code-plugin/VERSION` | `0.21.0 → 0.22.0` (mechanical version-sync fanout). |
| `platforms/claude-code-plugin/CHANGELOG.md` | `[0.22.0]` entry. |
| `platforms/claude-code-plugin/docs/CONFIG.md` | Note that autopilot skills now honor `model.precheck` (print-only). |
| `docs/TAGGING.md` | current-tags row for `claude-code-plugin/v0.22.0` (sync script doesn't cover it — same gap as Phase 4). |
| `plans/FRAMEWORK-TODO.md` / `HANDOFF.md` / `DECISIONS.md` | close the entry / narrative / D-0035. |

## Implementation sequence

### Task 1: Conformance test first

- **Test-first — [CODE]:** author `test_model_precheck.py` (red — the 8
  autopilots fail). Assert `## Model precheck` present + the three key refs, and
  that its offset in the body is before the first `saga_driver.py` mention.

### Task 2: Apply the block + reword to 8 autopilots

- Insert the canonical block (with `<LAYER>` substituted) after
  `## Smart Document Detection`; reword the Step-1 directive per D5 (mind the
  brd-vs-rest wording difference). Make the test green.

### Task 3: Version bump + docs

- Bump `VERSION` `0.21.0 → 0.22.0`; run `sync-version-refs.sh`; hand-fix
  `docs/TAGGING.md`. CHANGELOG `[0.22.0]`; CONFIG note; FRAMEWORK-TODO close;
  HANDOFF; DECISIONS D-0035.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | `python -m unittest discover -s tests/conformance` | all pass incl. new test | Scope |
| V2 | `python tests/conformance/platforms/plm_lint.py --all` | clean | regression guard |
| V3 | `grep -L "## Model precheck" skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-autopilot/SKILL.md` | empty (all 8) | D2 |
| V4 | each autopilot: `## Model precheck` offset < first `saga_driver.py` offset | true for all 8 | D5 |
| V5 | `cat platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` | `0.23.0` (no spec change) | Version impact |
| V6 | markdownlint on the 8 changed SKILLs | Passed | hygiene |
| V7 | **Live (user CLI, deferred):** run an autopilot with `model.per_layer.<L>` set + `precheck: warn` | the `ℹ … recommends …` notice prints, cascade proceeds | Objective |

## Docs to update

- [ ] `platforms/claude-code-plugin/CHANGELOG.md` — `[0.22.0]`
- [ ] `platforms/claude-code-plugin/docs/CONFIG.md` — now-honored note
- [ ] `docs/TAGGING.md` — `claude-code-plugin/v0.22.0` row
- [ ] `plans/FRAMEWORK-TODO.md` — close `MODEL-PRECHECK-ROLLOUT`
- [ ] `plans/HANDOFF.md` — narrative + next steps
- [ ] `plans/DECISIONS.md` — D-0035 (print-only, autopilot-only, SKILL-not-driver)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | The directive reword weakens the no-bypass guarantee (model drafts in-session instead of invoking the driver) | med | Reword to "first *orchestration* action"; the notice is explicitly not drafting/not orchestration; V4 + conformance assert the precheck *precedes* (not replaces) the Bash directive; the "STOP, you are bypassing the driver" guardrail stays. |
| R2 | 8 duplicated blocks drift | med | `test_model_precheck` asserts presence + key refs; drift fails CI. |
| R3 | brd's different directive wording missed in the reword | low | Task 2 handles brd explicitly; V4 is wording-agnostic (offset check). |
| R4 | A user reads the printed notice as the plugin claiming it switched the model | low | Wording says "cannot switch … run /model" explicitly. |
| R5 | Standalone base-skill users get no notice | low (by design) | Documented deferral; autopilot is the recommended entry; pull later if needed. |

## Claim ledger

| #  | Claim | Citation |
| -- | ----- | -------- |
| 1  | `model.precheck` enum `warn\|silent\|block`, default `warn`; `model.per_layer`/`default` exist | `platforms/claude-code-plugin/docs/CONFIG.md` (model block + enums + defaults) |
| 2  | `commands/model.md` documents skills "consult" precheck but no skill does | `commands/model.md` "Honest caveat" step 3; `skills/` grep empty |
| 3  | All 8 autopilots are saga-driven with `### Saga-driven generation loop` + a Bash `saga_driver.py` Step-1 directive | Phase 4 (`test_autopilot_saga_parity.py`, merged `f277ea1a`) |
| 4  | Autopilot section order has `## Smart Document Detection` then `## Workflow` (insertion anchor) | `skills/doc-prd-autopilot/SKILL.md` section headers |
| 5  | brd directive wording differs from the other 7 ("MANDATORY — DO THIS FIRST / first and only action" vs "VERY FIRST tool call") | `skills/doc-brd-autopilot/SKILL.md` vs `doc-prd-autopilot/SKILL.md` |
| 6  | `model.*` is plugin-only config → no framework-spec/FSV change | `docs/CONFIG.md` lives under `platforms/claude-code-plugin/` |

## Review log

### Pass 1-3 — 2026-06-21 — author self-review (compare-based design)

Converged on a compare-and-warn design across many skills. **Superseded by
Pass 4** (compare premise unworkable).

### Pass 4-6 — 2026-06-21 — independent (subagent) + redesign

Found the compare design unworkable: a skill can't read its own session model
(F3); team-mode drafting runs headless so warn/block has no user and block
deadlocks (F2); and the autopilot corpus was mid-migration (F7, since fixed by
Phase 4). Redesigned to **print recommendation, interactive entry points only**.
User decisions (2026-06-21): mechanism = print, no compare; placement =
interactive only.

### Pass 7 — 2026-06-22 — scope lock (post-Phase-4)

- Phase 4 landed (`f277ea1a`): all 8 autopilots now saga-driven and uniform, so
  the placement is one shape, and base/audit/fixer are now reliably headless in
  the normal flow.
- **Scope locked to autopilots-only** (D2) — drops the base skills + the
  `AIDOC_SAGA` headless-guard + the driver `env` stamp entirely (all were only
  needed to cover the standalone-base path). Net: 8 SKILL edits + 1 test + docs;
  plugin MINOR. No `saga_driver.py` change, no framework-bundle re-sync.
- **D3 recorded:** implement in the SKILL, not the driver (preserves `block`).
- **R1 retained** as the one load-bearing risk: the directive reword must not
  let the model draft in-session; mitigated by "orchestration action" wording +
  the offset/precedence conformance check.
- Result: design converged; ready to implement. The high-value check is the
  **independent review of the implementation diff** before merge (the lesson
  from Phase 4, where that caught the Step-3 defect).
