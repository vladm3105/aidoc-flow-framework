# IPLAN-SESSION-HANDOFF-001 Plan — IPLAN §5 `session_handoff` is empty at Draft

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | IPLAN-SESSION-HANDOFF-001                                     |
| Type           | bugfix                                                        |
| Status         | PLANNED — 2026-09-04T00:00:00Z                                |
| Depends on     | GD-25 (spec `0.50.0`, #601) — this is its deferred §5 half     |
| Feeds          | closes #621                                                   |
| Version impact | framework MINOR `0.50.0 → 0.51.0`; change level **C2**         |

## Objective

`framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` §5 `session_handoff.sessions[]`
ships a worked example that asserts a session already ran — a date, an agent, and
`action: created` on a file that is not on disk. Platform B instructs an author to
*seed* that block at Draft, so an agent copying the example produces a Draft IPLAN
whose §5 records history that never happened. This is GD-25 / #601 one section up,
and the two engines contradict each other on it.

This change ratifies **`sessions: []` at Draft**, moves the worked entry into
`_guidance` as an explicitly-labelled *append* shape, brings both engines and the
four plugin IPLAN skills onto that rule, records it as **GD-26**, and locks it with
a conformance guard that reads the **parsed YAML value** rather than a comment.

## Scope

**In:**

- `IPLAN-TEMPLATE.yaml` §5 — the shipped value becomes `sessions: []`; the worked
  entry moves into `_guidance` labelled as what a session appends.
- `framework/layers/08_IPLAN/README.md` — the layer doc states the Draft state.
- `framework/governance/DECISIONS.md` — **GD-26**.
- `framework/VERSION` `0.50.0 → 0.51.0` + the mechanical fanout.
- Four plugin `doc-iplan*` skills: the Draft-seed instruction, **two** validation
  checklist lines, the Tier-1 audit row and the Structure paragraph, the autopilot's
  generation step, and the fixer's phase-1 action.
- **Every surface that says a required section must be non-empty**, because
  `sessions: []` is about to be the correct Draft value of one. There are three and
  the first pass caught one: `doc-iplan-audit/SKILL.md` (Claim 9),
  `doc-iplan/SKILL.md:200` (Claim 27 — inside the very file whose step 9 will now
  instruct the empty list, twelve lines above it), and `UCC_PROMPT_IPLAN.md:53`
  (Claim 28, which says "populated", stronger still, and already contradicts `:56`
  today). **NEW@pass1**
- `platforms/hermes/prompts/templates/creation/UCC_PROMPT_IPLAN.md` — its Draft
  instruction is already right; it gains the explicit prohibition plus the `:53`
  carve-out.
- `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:503` — a one-line
  fix. Under "For IPLAN **creation**, enforce:" it requires "Session handoff:
  previous session state" — #621's defect shape on Platform A (Claim 31).
  **NEW@pass1**
- `tests/conformance/test_iplan_session_handoff_draft.py` — new guard.

**Out of scope (deferred):**

- **`IPLAN-MVP-TEMPLATE.yaml` carries an entirely different `session_handoff`
  shape** — `last_session` / `status_markers` / `resume_from`, no `sessions[]` at
  all (Claim 22). It does not fabricate a session, so #621 does not reach it, but
  the two templates disagree about the section's *keys*. **This goes as a comment on
  the open #438, not as a new issue** — #438 already owns "all 8
  `*-MVP-TEMPLATE.yaml` are non-conformant" and cites this exact file at `:52-53`.
  Opening a second issue would violate this repo's one-issue-per-defect rule.
  **NEW@pass1**
- **`UCC_OUTPUT_SCHEMA.md:302` is a THIRD shape** — `session_handoff` declared as a
  scalar string with no `sessions` key at all (Claim 32). Named here so a future
  reader does not read this plan's silence as coverage. **NEW@pass1**
- Reconciling §2 `file_manifest` ↔ §6 `code_inventory`, and the detection gap
  GD-25 recorded for them. Untouched.
- `session_handoff.sessions[].files_touched[].action` stays `created | modified`.
  GD-25 decided it and #621 does not dispute it (Claim 12).
- Hermes' `agent-skills/**` copies of the *session protocol* — `SKILL.md:1022` and
  `references/ai-assistant-rules.md:66`. Those two state the **append** step, which
  is correct under either shape, and they are an independent drifted copy of
  `framework/AI_ASSISTANT_RULES.md` — still saying "v3.2" (Claim 21). ⚠️ **This
  rationale does NOT extend to the whole tree, and Pass 1 caught it doing so.**
  `sdd-orchestrator/SKILL.md:503` is a *creation-time* rule, not an append rule, so
  it moved INTO scope above. **NEW@pass1**
- `framework/AI_ASSISTANT_RULES.md` §"Session Handoff Protocol". It states the
  per-session protocol, which this change does not alter.
- The example corpus (`examples/url-shortener/`), regenerated wholesale after
  framework changes.
- `framework/governance/chg/gates/GATE-08_IPLAN.md` E004 (`:71`) — it requires the
  session-handoff **section present**, not populated sessions, so an empty list
  satisfies it unchanged (Claim 35). Named rather than silent, so a future reader
  does not re-derive it. **NEW@pass1**

## Approach / Design

### The decision

**A Draft IPLAN carries `session_handoff.sessions: []`.** An entry is APPENDED by a
session as it ends. No entry is seeded, at Draft or ever, by an author.

### Why not the §6-style seed (the closer-looking analogue)

GD-25 seeded §6 `code_inventory` at Draft and argued an empty block is the weaker
artifact. That argument does **not** transfer, for two reasons, and both belong in
GD-26 because a future reader will otherwise re-derive §6's rule here:

1. **§6's seed is DERIVED; a §5 seed would be FABRICATED.** §6 seeds one entry per
   §2 `file_manifest` path — the expected set is known at Draft, which is exactly
   what makes an empty §6 indistinguishable from an executor that never wrote back.
   Nobody knows the future *sessions*, so a seeded session entry has no source.
2. **It would contradict `document_control.session_count: 0`** (Claim 3). A seeded
   session-zero makes `len(sessions) == 1` against a count of `0` — a fresh
   internal contradiction of precisely the class GD-25 was repairing.

And the empty list keeps the reading that matters: `sessions: []` beside an
all-`NOT_STARTED` §2 is coherent, while `sessions: []` beside a `DONE` §2 is a
*detectable* executor failure.

### Where the Draft's "start here" actually lives

The plugin's step 9 seeds the handoff "so the first executor has a clear
`next_session_directive`" (Claim 5). No new key is introduced to preserve that:

- The first file to build is startup-protocol **step 2** — the lowest-`order`
  `NOT_STARTED` entry in §2 (Claim 2).
- Environment preconditions belong in §3 `execution_commands.setup`, a required
  section for `code_build` / `combined` (Claim 23).
- `next_session_directive` is what ONE session hands the NEXT. A Draft has had no
  session, so it has none to write. The field stays exactly where it is, per
  session — **nothing is removed and nothing is added**, which is what keeps this
  non-breaking (an IPLAN already carrying sessions stays valid) and therefore MINOR
  / C2 rather than the C3 formal gate a key relocation would owe.

### The template edit, concretely

`sessions:` (Claim 1) becomes `sessions: []`. Everything currently under it moves
into `_guidance` under a heading naming it as the append shape, **retaining its
`# created | modified` enum comment** — see Risk R1.

`_guidance` gains three passages, in this order after the existing "Handoff
markers" block:

- **EMPTY AT DRAFT** — the rule, plus the `session_count` contradiction as the
  reason a seeded entry is wrong rather than merely unnecessary.
- **THIS IS NOT §6's RULE** — the derived-vs-fabricated asymmetry above, so the
  next reader does not "fix" §5 into §6's shape.
- **SHAPE A SESSION APPENDS** — the moved worked entry, labelled *never a Draft
  value*.

### Platform fanout

| Surface | Today | After |
| --- | --- | --- |
| `doc-iplan/SKILL.md` step 9 (Claim 5) | "Seed session handoff … so the first executor has a clear `next_session_directive`" | leave `sessions: []`; never seed a session entry. The `code_inventory` half of the step is unchanged |
| `doc-iplan/SKILL.md` checklist (Claim 6) | "Session Handoff seeded with a `next_session_directive`" | `sessions:` present; `[]` in a Draft; each appended session carries a directive |
| `doc-iplan/SKILL.md:200` (Claim 27) **NEW@pass1** | "All 6 sections present and non-empty" | same Draft carve-out as the audit's Structure rule. Without this, step 9 and a checklist twelve lines below it contradict each other inside one file |
| `doc-iplan-audit/SKILL.md` Tier-1 row (Claim 8) | "`session_handoff.sessions` present with a `next_session_directive`" | Draft-aware, still blocking: `sessions` present; `[]` in a Draft; every appended entry carries a directive |
| `doc-iplan-audit/SKILL.md` Structure rule (Claim 9) | "every section … present and **non-empty**" | one added sentence: a Draft's `session_handoff` carrying `sessions: []` satisfies this and is not a missing section |
| `doc-iplan-autopilot/SKILL.md` (Claim 10) | "seeded session handoff" | an empty `sessions: []` handoff |
| `doc-iplan-fixer/SKILL.md` phase 1 (Claim 11) | "seed `file_manifest`, `session_handoff`, … from the template" | unchanged in shape; gains "`session_handoff` seeds `sessions: []` — never a session entry" |
| Hermes `UCC_PROMPT_IPLAN.md` (Claims 13, 14) | "Initialize with empty sessions array" | unchanged in substance; gains the explicit prohibition |
| Hermes `UCC_PROMPT_IPLAN.md:53` (Claim 28) **NEW@pass1** | "All 6 sections present and **populated**" — already contradicts `:56` today | same Draft carve-out. `UCR_PROMPT_IPLAN.md:36` and `UCRem_PROMPT_IPLAN.md:71` say only "present" and need nothing |
| Hermes `sdd-orchestrator/SKILL.md:503` (Claim 31) **NEW@pass1** | under "For IPLAN **creation**, enforce:" — "Session handoff: previous session state, next_step directive" | drop the previous-session-state clause at creation; a Draft has none |

⚠️ **The first draft of this plan said "Platform A needed no substantive change: it
was already right." Pass 1 falsified that and it is retracted.** Platform A's IPLAN
*creation prompt* is right, and #621's live disagreement does resolve by Platform B
moving to it — but its orchestrator skill carries a separate creation-time rule with
the same defect (Claim 31), and its own success criteria contradict its own Draft
instruction (Claim 28). Three one-line edits, not zero.

### What is NOT broken — checked, so it is not re-derived

- **No lint rule can fail a Draft over an empty §5.** STRUCT01's derived
  required-section set for IPLAN is `{document_control, traceability}`, because §5
  carries `_required_when_subtype:` (Claim 33).
- **Hermes' runtime validator already tolerates it** — it defaults `sessions` to
  `[]`, no-ops the loop and appends a *pass* (Claim 34).
- **`GATE-08_IPLAN.md` E004 requires the section present, not populated** (Claim 35).
- **`action` stays a two-value enum and GD-25's one-match assertion survives**
  (Claim 12, Risk R1, V5).

All four are **NEW@pass1**.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/conformance/test_iplan_session_handoff_draft.py` | the guard |

### Modified

| Path | Change |
| ---- | ------ |
| `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | §5 value → `sessions: []`; three `_guidance` passages; worked entry moved |
| `framework/layers/08_IPLAN/README.md` | §"Session Handoff Protocol" states the Draft state |
| `framework/governance/DECISIONS.md` | GD-26 |
| `framework/VERSION` | `0.50.0` → `0.51.0` |
| `platforms/claude-code-plugin/skills/doc-iplan/SKILL.md` | step 9, checklist line |
| `platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md` | Tier-1 row, Structure paragraph |
| `platforms/claude-code-plugin/skills/doc-iplan-autopilot/SKILL.md` | generation step |
| `platforms/claude-code-plugin/skills/doc-iplan-fixer/SKILL.md` | phase-1 action |
| `platforms/hermes/prompts/templates/creation/UCC_PROMPT_IPLAN.md` | explicit prohibition; `:53` Draft carve-out |
| `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md` | `:503` creation-time rule (one line) |
| `CHANGELOG.md` · `ROADMAP.md` · `platforms/claude-code-plugin/CHANGELOG.md` · `plans/HANDOFF.md` | records |
| *(mechanical)* `platforms/*/FRAMEWORK_SPEC_VERSION`, 52 × SKILL frontmatter, bundled `framework/**`, READMEs, `docs/PARITY.md` | written by the two sync scripts — never by hand |

## Implementation sequence

### Task 1: the guard, first and RED

- Write `tests/conformance/test_iplan_session_handoff_draft.py`.
- **Test-first — [CODE]:** it must FAIL against current `main` before any template
  edit. GD-25's own guard is the model, and its central lesson applies unchanged:
  the Draft rule reads `yaml.safe_load(...)["session_handoff"]["sessions"]` and
  asserts `== []` — **a guard reading only the enum comment would have passed
  `2943bf3b`**, the commit that shipped #601 (Claim 16).
- Rules: (a) the parsed value is `[]`; (b) `_guidance` carries the Draft rule, the
  §6 asymmetry and the append-shape example; (c) each of the four `doc-iplan*`
  skills states the empty-at-Draft rule positively and none instructs seeding a
  session entry; (d) GD-26 exists and its body carries the rule.
- **No bundle-identity assertion.** A first draft had one; Claim 17 shows
  `test_the_vendored_bundle_matches_the_spec` already byte-compares this exact file
  and its own docstring says it adds no coverage. Re-implementing it fails the
  minimal-and-realistic convention. **NEW@pass1**
- **The negative rules need a prohibition exemption**, exactly as GD-25's do
  (Claim 18): a *correct* sentence such as "never seed a session entry" contains
  the banned words and must not red the check.
- Scan `doc-iplan*/**/*.md`, not top-level `SKILL.md`, and normalize whitespace
  before matching — both are GD-25's recorded findings (Claim 19).

### Task 2: the template

- Apply the §5 edit above.
- **Do not hand-edit the vendored copy** at
  `platforms/claude-code-plugin/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`;
  Task 6 generates it.

### Task 3: layer README + GD-26

- README: state the Draft state in §"Session Handoff Protocol", phrased so the
  guard can assert it (GD-25 asserts two literal phrases against this same file —
  Claim 20).
- GD-26: the decision, the two rejected shapes and why, the derived-vs-fabricated
  asymmetry, the `session_count` contradiction, GATE-SPEC-W002/W003 dispositions,
  the guard, and the mutations run.

### Task 4: the four plugin skills + Hermes

- Apply the fanout table — **ten** surfaces across **six** files. (Pass 1 added
  three; Pass 2 caught that this line still said "seven … five", which would have
  had an implementer stop three rows short, two of them R7's.)
- **Re-run GD-25's guard after every skill edit** — see Risk R2, whose site list and
  mitigation rule were both rewritten by Pass 1.

### Task 5: version bump

- `framework/VERSION` → `0.51.0`, then `CHANGELOG.md` `### Changed — Framework
  Spec` heading (GATE-SPEC-E005 + E008 — Claim 24).

### Task 6: mechanical fanout, in this exact order

- `bash scripts/sync-version-refs.sh`, **then** `bash tools/sync-plugin-framework.sh`.
  Reversing it lands drifted bundled playbooks and a red bundle guard.
- Do not hand-edit `docs/PARITY.md`'s framework token before the sync: it is both
  the detector's source and one of its targets, and editing it first strands the
  whole fanout silently at exit 0.

### Task 7: records

- `CHANGELOG.md`, `ROADMAP.md`, `platforms/claude-code-plugin/CHANGELOG.md`,
  `plans/HANDOFF.md`. Set this plan's Status to `In Progress` when Task 1 starts
  and let the merging PR's `Closes #621` close the issue.

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python3 -m unittest discover -s tests/conformance -t tests/conformance -k session_handoff_draft` — run **before** Task 2 | RED (the new guard fails on unmodified `main`) | Task 1 test-first |
| V2 | same command after Task 2-4 | OK | the rule shipped |
| V3 | `python3 -m unittest discover -s tests/conformance -t tests/conformance -k iplan` | OK — **21 existing tests still pass** alongside the new module | R1, R2 |
| V4 | `python3 -c "import yaml,sys;d=yaml.safe_load(open('framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml'));print(d['session_handoff']['sessions'])"` | `[]` | the decision |
| V5 | `grep -c '^\s*action:\s*\S*\s*#' framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | `1` — the moved line keeps its enum comment, so GD-25's one-match assertion holds (Claim 12) | R1 |
| V6 | `python3 -m unittest discover -s tests/conformance -t tests/conformance` | OK, ≥ 547 + new | no regression |
| V7 | `python3 -m pytest tests/conformance -q` | passed (baseline 498 / 1040 subtests, plus the new module) | no regression |
| V8 | `python3 -m unittest discover -s tests/acceptance/deterministic -t .` | 64 OK — the golden fixture is `In Progress`, not Draft, so the Draft rule cannot reach it (Claims 15, 15a) | R3 |
| V9 | `python3 -m unittest discover -s tests/unit -t .` | 209 OK | no regression |
| V10 | `PYTHONPATH=tools python3 -m unittest discover -s tools/sdd_doc_lint/tests` | 6 OK | no regression |
| V11 | `pre-commit run --all-files` | green, rc=0 — re-run **after** the commit, see R4 | hooks |
| V12 | `python3 tests/chg/spec_gate.py --base origin/main` | VERSION + CHANGELOG updated, OK | GATE-SPEC |
| V13 | `git diff --stat` shows the bundled template identical to `framework/` | bundle guard green | Task 6 |
| V14 | **The exemption invariant.** `PYTHONPATH=tests/conformance python3 -c` importing `_sentences`/`_PROHIBITION`/`_EMPTY_INVENTORY` from the GD-25 module (it does `from _spec import …` at `:54`, so a bare `python3 -c` raises `ModuleNotFoundError`); for each of the four `doc-iplan*` skills count `code_inventory`-bearing sentences and how many are `_PROHIBITION`-exempt | **Baseline measured on `main` before any edit: 7 sentences, 0 exempt** (`doc-iplan` 4, the other three 1 each). After the edits the exempt count MUST still be **0**. A rise means a prohibition clause was merged into a `code_inventory` sentence and a guard went green by being disarmed | **R2b** |
| V14a | Same script also prints, for every `\b(empty\|blank)\b` in a `code_inventory` sentence, the character distance to the nearest `code_inventory` and whether a `.` intervenes | the `doc-iplan-autopilot/SKILL.md:139-144` gap **reported as a number** (~90 today), not assumed. A non-match prints nothing, which is why V14a measures distance rather than matches | R2, R2a |
| V15 | `grep -rniE "present and (non-empty\|populated)\|all sections\|every section\|complete all sections" platforms/ \| grep -v "^platforms/claude-code-plugin/framework/"` | every hit either carries the Draft carve-out or is judged and named. **`doc-iplan/SKILL.md:173` ("complete all sections required for the chosen subtype") is deliberately left**: it is materially weaker than `:200` and is governed by the rewritten step 9 nine lines below | R7 |

## Docs to update

- [ ] `CHANGELOG.md` — `0.50.0 → 0.51.0` framework-spec entry (required by GATE-SPEC-E008)
- [ ] `ROADMAP.md` — recently-shipped bullet
- [ ] `platforms/claude-code-plugin/CHANGELOG.md` — the four skills moved, **and an
      explicit "no plugin `VERSION` bump" line**: this is an authoring-instruction
      change carried by the spec release, exactly as GD-25 recorded for the same
      class (Claim 36). A bump would drag in the 60-file plugin fanout and a
      per-bump founder OK, for no behavioural change. **NEW@pass1**
- [ ] `plans/HANDOFF.md` — replace the "#621 — the same defect one section up, filed not fixed" section
- [ ] `framework/governance/DECISIONS.md` — GD-26
- [ ] `plans/DECISIONS.md` — only if a non-obvious repo-level choice emerges; the spec decision belongs in GD-26, not both

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Moving the worked entry into `_guidance` breaks GD-25's `test_the_sibling_action_carrier_is_not_extended`, which matches `^\s*action:\s*\S+\s*#\s*(...)$` over the **whole template source** and asserts **exactly one** match (Claim 12) | med | The moved line keeps its `# created \| modified` comment and its leading whitespace, so the count stays 1. **V5 measures it rather than assuming.** If it ever does not, the fix is to scope GD-25's regex to the guidance — never to drop the enum comment. **GD-26 must state that the pinned enum now lives only inside a block scalar** — the live-value/quoted-shape distinction `_entry_status_lines`'s docstring says GD-25 deliberately scoped for (Claim 16) — so the guard's subject changed character even though it stayed green **(NEW@pass1)** |
| R2 | A plugin-skill edit reds GD-25's `_EMPTY_INVENTORY` scan, which matches `empty\|blank` within **40 non-period characters** of `code_inventory`, in either order (Claim 30) | **high** | ⚠️ **Pass 1 falsified this row's original mitigation and it is retracted.** It said to rely on "separate sentences … `_sentences()` splits on `.!?` and newlines". It does **not**: `_normalize` collapses every whitespace run to a single space *before* the split, so the `\|\n` branch is dead code and a line break separates nothing (Claim 29, proven by running it). Whole markdown tables collapse into one "sentence". **The real rule is: `empty`/`blank` and `code_inventory` must be MORE than 40 characters apart (`[^.]{0,40}?` matches a 40-character gap, so ≥ 40 reds), OR have a literal `.` between them, OR sit in a sentence containing a `_PROHIBITION` word (Claim 18).** Note `[^.]` excludes only the literal `.`, so a period *inside a token* (`SKILL.md`, `IPLAN.NN.SS.xxxx`) breaks a match without ending a sentence — which is why several existing sites cannot match. The third alternation, `code_inventory[^.]{0,20}?files:\s*\[\s*\]`, is not reachable by this plan's text (it writes `sessions: []`, never `files: []`) Also preserve `test_every_iplan_skill_states_the_planned_seed` — all four skills must still name `planned` near `code_inventory`. **V3 after every skill edit, not once at the end**, and **V14 measures the margin** |
| R2a | The *site* R2 named was wrong. The plan's proposed step-9 text (Claim 5 row) contains no "empty" at all; the collision is in the **autopilot** — `doc-iplan-autopilot/SKILL.md:139-144` is one sentence, and the After text "an empty `sessions: []` handoff" lands ~88 non-period characters from `code_inventory` at `:143`. It survives on margin, unmeasured | **high** | V14 measures all four skill sites, not one. **NEW@pass1** |
| R2b | **A new prohibition clause DISARMS GD-25's two negative guards over a whole table.** `_PROHIBITION` is applied **per-sentence** (Claim 37), and `_normalize` collapses a markdown table with no `.`+whitespace into ONE sentence. Measured: `doc-iplan-fixer/SKILL.md:247-256` is a **single 1,900-character "sentence"** carrying `code_inventory` twice and currently **not** exempt — so both guards actively scan it. Inserting "never a session entry" into that table flips it to exempt. `doc-iplan/SKILL.md` step 9 is the same shape | **high** — measured, not predicted | **Every new prohibition clause MUST be its own sentence, terminated by `.` + whitespace, and MUST NOT share a sentence with any `code_inventory` clause.** V14 enforces it as an invariant rather than trusting the wording. Without this the suite stays green **because nothing happens** — the `CLAUDE.md` trap "a fix can silently disarm an existing regression test". **NEW@pass2** |
| R3 | The new Draft rule invalidates a golden fixture or the deterministic acceptance test that reads `sessions[0].next_session_directive` | low | The golden is `status: In Progress` (Claim 15) and the test asserts on that golden only (Claim 15a). Confirmed by V8 |
| R4 | The pre-commit blocks the commit: the phantom-release guard resolves `VERSION` from committed history only, so the commit introducing a release cannot pass the hook that release satisfies — open as #620 | **certain** | `git commit --no-verify`, then `pre-commit run --all-files` immediately and confirm green (V11). Record it in the PR body, as #622 did |
| R5 | Scope creep into §6, the MVP template, or `action:` | med | All three are named in "Out of scope" with a reason. The MVP-template divergence goes as a **comment on #438**, which already owns it — not a new issue |
| R6 | A future reader "repairs" §5 into §6's seeded shape | med | GD-26 and the template's `_guidance` both carry the derived-vs-fabricated asymmetry explicitly, and the guard asserts the passage is present |
| R7 | The "non-empty required section" rule is repaired on one surface and left live on the other two, so an auditor or a Hermes run still fails a Draft the author was told to write — GD-25's named failure mode | **high** (it was live in the first draft) | All three are in Scope and in the fanout table: Claims 9, 27, 28. **NEW@pass1** |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | §5 ships a populated worked session whose `action` is `created` | `action: created` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:271 |
| 1a | that entry hangs off the shipped `sessions:` key | `sessions:` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:266 |
| 2  | startup-protocol step 2 selects the next `NOT_STARTED`/`PARTIAL` file from §2 | `Session startup protocol` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:255 |
| 3  | `document_control` counts sessions and starts at 0, so a seeded entry contradicts it | `session_count` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:92 |
| 4  | §5 carries `next_session_directive` per session, not per document | `next_session_directive` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:275 |
| 5  | Platform B instructs seeding the handoff at Draft for the directive's sake | `9. **Seed session handoff**` | platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:182 |
| 6  | the same skill's validation checklist restates it | `Session Handoff seeded` | platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:205 |
| 7  | the skill's §5 blurb names the per-session fields | `**Session Handoff**` | platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:107 |
| 8  | the audit's **Tier-1 blocking** row requires `sessions` present *with* a directive | `Session handoff` | platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md:397 |
| 9  | the Structure row requires every required section present **and non-empty** | `Structure` | platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md:395 |
| 10 | the autopilot's generation step names a *seeded* session handoff | `seeded session` | platforms/claude-code-plugin/skills/doc-iplan-autopilot/SKILL.md:141 |
| 11 | the fixer's phase 1 seeds `session_handoff` from the template | `1 — Missing sections` | platforms/claude-code-plugin/skills/doc-iplan-fixer/SKILL.md:250 |
| 12 | GD-25's guard asserts **exactly one** `action:` enum line in the template source, `created \| modified` | `test_the_sibling_action_carrier_is_not_extended` | tests/conformance/test_iplan_code_inventory_lifecycle.py:282 |
| 13 | Platform A initializes an **empty** sessions array — the opposite instruction | `**Session Handoff**` | platforms/hermes/prompts/templates/creation/UCC_PROMPT_IPLAN.md:37 |
| 14 | and restates it as a success criterion | `Session handoff section initialized` | platforms/hermes/prompts/templates/creation/UCC_PROMPT_IPLAN.md:56 |
| 15 | the acceptance golden IPLAN is `In Progress`, not `Draft`, so a Draft rule cannot reach it | `status: In Progress` | tests/acceptance/fixtures/layer_08_iplan/valid/IPLAN-01_golden.yaml:16 |
| 15a | the deterministic test asserting a first-session directive reads that golden only | `test_first_session_has_next_session_directive` | tests/acceptance/deterministic/test_layer_iplan.py:67 |
| 16 | GD-25's Draft rule reads **parsed YAML**, because a comment-only guard would have passed the commit that shipped #601 | `test_every_example_entry_is_in_the_draft_state` | tests/conformance/test_iplan_code_inventory_lifecycle.py:178 |
| 16a | the sibling helper that reads **source lines** is deliberately scoped away from `_guidance`, because a literal scalar may quote an entry's shape — the distinction R1 turns on | `_entry_status_lines` | tests/conformance/test_iplan_code_inventory_lifecycle.py:122 |
| 17 | that module also byte-compares the vendored bundle copy of this template | `test_the_vendored_bundle_matches_the_spec` | tests/conformance/test_iplan_code_inventory_lifecycle.py:302 |
| 18 | its negative scans carry a prohibition exemption, without which a correct sentence reds the check | `_PROHIBITION` | tests/conformance/test_iplan_code_inventory_lifecycle.py:99 |
| 19 | and glob `doc-iplan*/**/*.md` with whitespace normalized, both recorded findings | `IPLAN_SKILL_GLOB` | tests/conformance/test_iplan_code_inventory_lifecycle.py:79 |
| 20 | GD-25 asserts two literal phrases against the layer README, so that file is an established guard surface | `test_the_layer_readme_describes_the_seed` | tests/conformance/test_iplan_code_inventory_lifecycle.py:373 |
| 21 | Hermes' `agent-skills` rules copy is an independent drifted fork, not a synced vendor copy | `Legacy subtype taxonomies when generating active v3.2 artifacts` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/references/ai-assistant-rules.md:71 |
| 22 | the MVP template's `session_handoff` has different keys entirely — no `sessions[]` | `session_handoff:` | framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml:47 |
| 23 | §3 `execution_commands` is required for `code_build`/`combined`, so preconditions have a home | `_required_when_subtype` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:201 |
| 24 | GATE-SPEC-E005/E008 require a `framework/VERSION` bump and a CHANGELOG entry for any `framework/**` change | `GATE-SPEC-E005` | tests/chg/spec_gate.py:86 |
| 25 | GD-25 defers the §5 analogue to #621 by name, so this plan discharges a named owner rather than reopening a closed decision | `The §5 analogue is real and is filed` | framework/governance/DECISIONS.md:115 |
| 26 | `major ⇒ C3` is one-directional, so an additive/non-breaking MINOR may be C2 | `major ⇒ C3` | framework/governance/DECISIONS.md:21 |
| 27 | the **authoring** skill carries its own "present and non-empty" rule, twelve lines above the step that will instruct `sessions: []` **(NEW@pass1)** | `All 6 sections present and non-empty` | platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:200 |
| 28 | Hermes' success criteria demand every section "populated", contradicting its own empty-array instruction at `:56` **today** **(NEW@pass1)** | `All 6 sections present and populated` | platforms/hermes/prompts/templates/creation/UCC_PROMPT_IPLAN.md:53 |
| 29 | `_sentences` normalizes whitespace **before** splitting, so its `\|\n` branch is dead — a line break separates nothing, and markdown tables collapse to one sentence **(NEW@pass1)** | `_sentences` | tests/conformance/test_iplan_code_inventory_lifecycle.py:118 |
| 30 | `_EMPTY_INVENTORY` matches `empty\|blank` within 40 non-period characters of `code_inventory`, in either order **(NEW@pass1)** | `_EMPTY_INVENTORY` | tests/conformance/test_iplan_code_inventory_lifecycle.py:88 |
| 31 | Platform A's orchestrator enforces "previous session state" at IPLAN **creation** — #621's shape, so Platform A is not wholly correct **(NEW@pass1)** | `Session handoff: previous session state, next_step directive` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:503 |
| 32 | a third `session_handoff` shape exists — a scalar string with no `sessions` key **(NEW@pass1)** | `session_handoff` | platforms/hermes/prompts/templates/creation/UCC_OUTPUT_SCHEMA.md:302 |
| 33 | STRUCT01's derived required-section set for IPLAN is `{document_control, traceability}`, so no lint rule can fail a Draft over an empty §5 **(NEW@pass1)** | `"IPLAN": frozenset(["document_control", "traceability"])` | tests/conformance/test_required_section_sets.py:160 |
| 34 | Hermes' runtime IPLAN validator defaults `sessions` to `[]`, no-ops its loop and appends a pass **(NEW@pass1)** | `check_session_handoff` | platforms/hermes/src/mcp_server/validation/iplan_rules.py:116 |
| 35 | the IPLAN gate's E004 requires the session-handoff **section present**, not populated sessions **(NEW@pass1)** | `E004` | framework/governance/chg/gates/GATE-08_IPLAN.md:71 |
| 36 | GD-25 shipped four skill edits with **no plugin `VERSION` bump**, on the GD-24 precedent — the same class as this change **(NEW@pass1)** | `No plugin` | platforms/claude-code-plugin/CHANGELOG.md:37 |
| 37 | `_PROHIBITION` exempts the whole **sentence**, not the match — so one prohibition word anywhere in a collapsed markdown table exempts the entire table from both negative guards **(NEW@pass2)** | `if not match or _PROHIBITION.search(sentence):` | tests/conformance/test_iplan_code_inventory_lifecycle.py:329 |

## Review log

### Pass 1 — 2026-09-04 — independent (`verified-planning-reviewer`, fresh context)

**Five load-bearing findings, all folded. Four were verified against source before
folding rather than taken on the agent's word; the fourth was proven by executing
the function.**

- **The "non-empty required section" repair reached 1 of 3 surfaces.** The plan
  fixed only `doc-iplan-audit/SKILL.md:395` and missed `doc-iplan/SKILL.md:200` —
  inside the very file whose step 9 the plan rewrites, twelve lines below it — and
  `UCC_PROMPT_IPLAN.md:53`, which demands sections be "populated" and so already
  contradicts its own `:56` today. Shipping as drafted would have manufactured a
  fresh internal contradiction of exactly #621's class, and would have reproduced
  GD-25's explicitly-designed-against failure ("the auditor cannot fail an IPLAN the
  author was told to write"). → both added to Scope, the fanout table, and the ledger
  (Claims 27, 28); new risk **R7**; new check **V15**.
- **R2's mitigation was factually false.** It claimed `_sentences()` splits on
  newlines. `_normalize` collapses all whitespace *first*, so the `|\n` branch is
  dead code — confirmed by running it: `_sentences("a b\nc d")` returns
  `['a b c d']`. Whole markdown tables are one "sentence". → R2 rewritten around the
  real rule (≥ 40 non-period characters apart, or a literal `.`, or a `_PROHIBITION`
  word); Claims 29, 30 added.
- **R2 also named the wrong collision site.** The proposed step-9 text contains no
  "empty" at all; the exposure is `doc-iplan-autopilot/SKILL.md:139-144`, one
  sentence in which the new text sits ~88 non-period characters from
  `code_inventory` — surviving on margin, unmeasured. → new risk **R2a**, new check
  **V14** measuring all four sites.
- **"Platform A needed no substantive change" was false and is retracted in place.**
  `sdd-orchestrator/SKILL.md:503`, under "For IPLAN **creation**, enforce:",
  requires "Session handoff: previous session state" — #621's defect on the other
  engine. The old blanket Out-of-scope rationale ("they state the append step")
  covers `:1022` and `ai-assistant-rules.md:66` but not this. → `:503` moved into
  Scope (Claim 31); the deferral rewritten to name what it does and does not cover.
- **A third shape exists and was silent:** `UCC_OUTPUT_SCHEMA.md:302` declares
  `session_handoff` as a scalar string with no `sessions` key. → parked explicitly
  (Claim 32).

Minor findings folded: Claim 16's citation pointed at the source-line helper rather
than the parsed-YAML test (split into 16 / 16a); `_EMPTY_INVENTORY` added to the
ledger; the "no plugin `VERSION` bump" decision stated with its GD-25 precedent
(Claim 36); the **bundle-identity** guard rule was **deleted** as a duplicate of an existing
test that says it adds no coverage (Task 1's rules were re-lettered afterwards, so
(c) there is now the four-skills rule, which is retained); R1 gained the GD-26 sentence about the enum now living only
inside a block scalar; Scope/Claim 9 reconciled on the audit **paragraph**. Three
"what is NOT broken" facts the plan relied on but never verified were added as
Claims 33-35.

**Verified correct and unchanged:** every verification baseline (V3=21, V6=547,
V7=498/1040, V8=64, V9=209, V10=6, V5=1 — the reviewer re-derived each and explained
why V6 and V7 differ: `test_repo_scripts.py`'s `load_tests` shim adds 49 methods
unittest sees and pytest does not); R1 and R3; the rationale for the ratified
decision; and both remaining deferrals.

### Pass 2 — 2026-09-04 — independent (`verified-planning-reviewer`, fresh context)

**Three load-bearing findings — down from Pass 1's five, so the loop is converging
and no scope cut is triggered.** The first was verified by execution before folding.

- **The plan's own edits would have silently disarmed GD-25's two negative guards.**
  `_PROHIBITION` exempts the whole *sentence* (Claim 37), and `_normalize` collapses
  a markdown table into one. Measured on `main`: `doc-iplan-fixer/SKILL.md:247-256`
  is a **single 1,900-character "sentence"** carrying `code_inventory` twice and
  **not** currently exempt — and inserting the planned "never a session entry"
  clause flips it to exempt. The suite would have gone green *because nothing
  happened*. → new risk **R2b**; **V14 rewritten as an invariant** against a
  baseline measured before any edit (7 `code_inventory` sentences across the four
  skills, **0** exempt; it must still be 0 after).
- **V14 as drafted could not produce its own Expected result.** It printed regex
  *matches*, but the thing R2a exists to measure is a **non-match** — the ~90-character
  gap in the autopilot — so it would have printed nothing while claiming to report a
  margin. It also needed `PYTHONPATH=tests/conformance` (the module does
  `from _spec import …`). → split into **V14** (the invariant) and **V14a** (the
  distance measurement).
- **Task 4's surface count was stale after the Pass-1 fold** — "seven surfaces across
  five files, three of them added by Pass 1" is self-contradictory, and the table now
  has **ten across six**. An implementer using it as the completion criterion stops
  three rows short, two of them R7's. → corrected. *(This is the scope-cut hazard the
  fold discipline warns about: a fold breaks internal references more readily than
  facts.)*

Non-load-bearing, folded: R2's threshold was off by one (`[^.]{0,40}?` permits a
40-character gap, so the safe boundary is **> 40**, not ≥) and omitted the third
alternation and the dotted-token asymmetry; V15's grep was bounded by the two
literals Pass 1 happened to find, so it was widened and `doc-iplan/SKILL.md:173` is
now **named as deliberately left** rather than silently outside the sweep; R7 is
printed out of order; the review log's "rule (c)" referred to a pre-re-lettering
letter; two paths were elided as `...`.

**Re-validated and unchanged:** the three newly-scoped surfaces are the **complete**
set — an independent wider sweep found no fourth, and three near-misses were checked
and cleared (`PLAN_STANDARD.md:37` governs markdown plans not the YAML artifact;
`doc-iplan-audit/SKILL.md:443`; the `UCR`/`UCRem` prompts, already correct).
`sdd-orchestrator/SKILL.md:503` is the only other creation-time instruction on either
engine. Claims 33/34/35 all mean what they assert — 33 twice over, since
`sdd_doc_lint` skips `_required_when_subtype` sections *and* STRUCT01 only checks for
a `##` heading. R1 and R3 re-verified sound; R3 extends to a second golden
(`fullpath/golden_chain`, also `In Progress`). No fixture is a `Draft` with a seeded
session.

**Growth check.** Of Pass 1's 12 new rows, 8 change what gets built or define the
rule the implementer follows; Claims 32-35 are negative evidence backing the
Out-of-scope and "what is NOT broken" statements. All four were independently
verified true, and this repo's "named rather than silent" convention is why they are
kept rather than cut — the alternative is a future reader re-deriving each as a fresh
bug. Pass 2 added exactly one row (37), which is load-bearing.

**Result:** ready — no further load-bearing findings.
