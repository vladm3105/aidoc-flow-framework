# IPLAN-LANG-001 Plan — de-Python the IPLAN template; inherit language from SPEC

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | IPLAN-LANG-001                              |
| Type           | refactor                                    |
| Status         | READY — refreshed 2026-07-06 for spec 0.33.0 (Pass 5 independent, clean); original draft 2026-06-09 |
| Depends on     | none                                        |
| Feeds          | none                                        |
| Version impact | framework spec **PATCH** (0.33.0 → 0.33.1); both `FRAMEWORK_SPEC_VERSION` pointers re-match (auto-synced); plugin + Hermes **product** versions unchanged |

## Objective

The Layer-8 `IPLAN-TEMPLATE.yaml` hardcodes Python toolchain commands and source
paths (`pip install`, `pytest`, `mypy`, `ruff`, `src/[module]`,
`tests/unit/test_[module].py`) in its example content. Language and dependency
stack are already declared once, upstream, at Layer 6
(`SPEC-TEMPLATE.yaml` `language:` + `dependencies:`). A Layer-8 deliverable that
re-pins a language its own `@spec` already owns both (a) violates the framework's
engine-agnostic principle and (b) duplicates a SPEC-owned decision at the wrong
layer. This change makes the template language-neutral: its `file_manifest` paths
and `execution_commands` strings become language-neutral guidance plus a clearly
labelled Python *example*, with explicit instruction to derive concrete
commands/paths from the language + dependencies declared in `@spec: SPEC-NN`. The
template's structural contract (six sections; the three `execution_commands`
categories) is preserved exactly, so no validator and no conformance check
changes.

## Scope

**In:**

- Edit `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`: Section 2
  (`file_manifest`) and Section 3 (`execution_commands`) — replace Python-only
  example content with language-neutral guidance + a labelled Python example;
  add a `_guidance` line tying concrete commands/paths to the `@spec` language +
  dependencies.
- Bump `framework/VERSION` 0.33.0 → 0.33.1 — required by GATE-SPEC-E005 on any
  `framework/**` change; the file must be **staged** so the version-sync hook and
  the gate both fire.
- Add a `CHANGELOG.md` entry in the **same diff** — required by GATE-SPEC-E008
  (hard CI gate, not a soft doc).
- Regenerate the plugin's vendored framework bundle via
  `tools/sync-plugin-framework.sh` (never hand-edit the bundle).

**Out of scope (deferred):**

- Renaming the `execution_commands` categories (`setup` / `implementation` /
  `validation`) to a build/test/lint phase vocabulary — these keys are a
  **validated contract** (`iplan_rules.py:104`) and are already language-neutral;
  renaming them would ripple into both platforms' validators and every golden
  fixture for zero benefit to the named issue.
- A predefined "action vocabulary" resolver / task-runner DSL for
  `execution_commands` — speculative until a second, non-Python platform actually
  consumes IPLANs and demands it.
- Folding design-review governance (Review log / Claim ledger) into IPLAN —
  rejected by design: that rigor lives upstream (BRD…SPEC) and in the markdown
  development plan (`PLAN_STANDARD.md`); IPLAN stays a lean execution manifest.
- De-Pythoning the golden acceptance fixtures
  (`tests/acceptance/fixtures/**/IPLAN-01_golden.yaml`) — a fixture legitimately
  picks one concrete language; Python is a valid choice and these are not derived
  from the template.
- Hand-editing the plugin README spec-version block or the conformance spec-version
  literal — `scripts/sync-version-refs.sh` auto-propagates both on a staged
  `framework/VERSION` bump (these were the "two gaps" closed in the 0.15.2
  release; no longer manual).

## Approach / Design

**Root-cause framing.** Language is a SPEC-owned fact
(`SPEC-TEMPLATE.yaml:97` `language:`, `:98` `dependencies:`). IPLAN
references its SPEC (`@spec: SPEC-NN`, present in `traceability.upstream`). The
fix is *inheritance*, not a new IPLAN field: the template instructs the author to
read the `@spec` language/dependencies and express each phase in that toolchain.

**What is preserved (the contract) — must not change:**

- The six top-level sections (`document_control`, `file_manifest`,
  `execution_commands`, `implementation_contracts`, `session_handoff`,
  `traceability`) — enumerated by the plugin `doc-iplan` skill and by the
  acceptance harness's top-level-key check.
- The three `execution_commands` categories `setup` / `implementation` /
  `validation`, each a non-empty list — required by Hermes
  `iplan_rules.py:104`.
- `metadata.layer: 8` and `metadata.document_type: "iplan-document"` — the only
  template-body fields the conformance suite asserts (`test_layers.py:35`).

**Edit A — `file_manifest.files` (Section 2).** Replace the three Python paths
with language-neutral placeholders (`<unit test for the component>`,
`<implementation file>`, `<integration test>`), keep test-first ordering, and
extend `_guidance` with: "Paths follow the conventions of the language declared
in `@spec: SPEC-NN`. Example (Python): `tests/unit/test_auth.py`,
`src/auth/service.py`."

**Edit B — `execution_commands` (Section 3).** Keep the three category keys.
Replace the Python command strings with a language-neutral lead comment per
category plus a labelled `# example (Python):` line, and extend the section
`_guidance`: "Concrete commands depend on the language + dependencies declared in
`@spec: SPEC-NN`; express each phase in that toolchain. The example lines below
are illustrative (Python)." Each category remains a non-empty list of strings
(comments are valid list items), so IPLAN-003 stays green.

**Propagation.** Edit the canonical template only → run
`tools/sync-plugin-framework.sh` to regenerate the byte-identical plugin bundle
(the drift guard `tests/conformance/platforms/test_plugin_framework_bundle.py`
enforces equality). Versions propagate automatically: staging `framework/VERSION`
runs the `sync-version-refs.sh` pre-commit hook, which rewrites both
`FRAMEWORK_SPEC_VERSION` pointers, the plugin README spec block, the conformance
spec-version literal, and the SKILL/playbook frontmatter that quote the version.
The only hand-authored version-adjacent file is the `CHANGELOG.md` entry.

**Version reasoning.** Example-content + guidance edits that preserve every
structural contract are a spec **PATCH** (`docs/PROJECT.md` defines MAJOR as a
breaking contract change; there is none). This mirrors recent framework PATCH
moves (e.g. 0.32.6 → 0.32.7, HERMES-SAGA-JOURNAL-CONFORMANCE's schema-enum
addition) that touched `framework/**` + `framework/VERSION` + both
`FRAMEWORK_SPEC_VERSION` pointers and left the plugin + Hermes **product**
versions unchanged.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | Edits A + B — de-Python `file_manifest` + `execution_commands` example content; add `@spec`-derivation guidance |
| `framework/VERSION` | 0.33.0 → 0.33.1 (staged so hook + GATE-SPEC fire) |
| `CHANGELOG.md` | New entry (required by GATE-SPEC-E008) |
| `platforms/claude-code-plugin/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | Regenerated by `tools/sync-plugin-framework.sh` (not hand-edited) |
| `platforms/*/FRAMEWORK_SPEC_VERSION`, plugin README spec block, conformance literal, SKILL/playbook frontmatter | Auto-rewritten by `sync-version-refs.sh` hook (no manual edit) |
| `plans/HANDOFF.md`, `plans/DECISIONS.md` | Docs-of-record |

## Implementation sequence

### Task 1: Edit the canonical template

- Apply Edit A to `file_manifest` and Edit B to `execution_commands` in
  `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`.
- Confirm the file still parses as YAML and that the six sections + three
  `execution_commands` categories + `metadata.layer`/`document_type` are intact.

### Task 2: Bump the framework spec version

- `framework/VERSION` → 0.33.1, and **stage it** so the `sync-version-refs.sh`
  pre-commit hook propagates the string to every dependent file.

### Task 3: Regenerate the plugin bundle

- Run `tools/sync-plugin-framework.sh`; do not hand-edit the bundle.

### Task 4: CHANGELOG + docs of record

- Add the `CHANGELOG.md` entry (framework spec 0.33.0 → 0.33.1, IPLAN-LANG-001) —
  in the **same commit/diff** as the `framework/**` change (GATE-SPEC-E008).
- `plans/HANDOFF.md` narrative; `plans/DECISIONS.md` the "IPLAN inherits language
  from SPEC; no new field" decision.

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python -c "import yaml; d=yaml.safe_load(open('framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml')); assert d['metadata']['layer']==8 and d['metadata']['document_type']=='iplan-document'; assert set(d['execution_commands'])>={'setup','implementation','validation'} and all(d['execution_commands'][k] for k in ('setup','implementation','validation')); print('ok')"` | `ok` — contract preserved | Approach (preserved contract) |
| V2 | `grep -nE 'pip install\|pytest\|mypy\|ruff\|src/\[module\]' framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml \| grep -v 'example (Python)'` | no matches (every remaining Python token is on a labelled example line) | Objective |
| V3 | `python -m pytest tests/conformance/ -q` | green (incl. `test_layers.py`, `test_version.py`, plugin bundle drift guard) | Scope / propagation |
| V4 | `diff -q framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml platforms/claude-code-plugin/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | identical (bundle re-synced) | Task 3 |
| V5 | `python -m pytest platforms/hermes/tests/unit/test_iplan_rules.py -q` | green — IPLAN-003 categories unchanged | Out-of-scope guarantee |
| V6 | `python tests/chg/spec_gate.py` (or equivalent gate run) over the staged diff | OK — VERSION + CHANGELOG both present (E005 + E008 pass) | Tasks 2 + 4 |
| V7 | `grep -rn '0.33.0' framework/VERSION platforms/*/FRAMEWORK_SPEC_VERSION` | no matches (all auto-moved to 0.33.1) | Task 2 propagation |

## Docs to update

- [ ] `CHANGELOG.md` — entry (hard gate GATE-SPEC-E008; tracked as Task 4)
- [ ] `plans/HANDOFF.md` — narrative + next steps
- [ ] `plans/DECISIONS.md` — "IPLAN inherits language from SPEC; no new field"
- [ ] `ROADMAP.md` — bullet only if a roadmap line tracks IPLAN; else skip

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Renaming/removing an `execution_commands` category breaks Hermes IPLAN-003 | low | Explicitly out of scope; V5 guards the validator stays green |
| R2 | A category becomes an empty list (comments only) and trips IPLAN-003's non-empty check | low | Keep ≥1 string item per category; V1 asserts non-empty |
| R3 | Bundle drift guard fails because canonical edited but bundle not re-synced | med | Task 3 runs the sync script; V4 + V3 (drift guard) verify equality |
| R4 | `framework/VERSION` not staged → hook does not run → stale version strings + GATE-SPEC failure | med | Task 2 stages VERSION; V6 (gate) + V7 (no stale 0.15.2) catch it |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | SPEC declares the implementation language (the upstream owner of this fact) | `language:` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:97 |
| 2  | SPEC also declares dependencies (name/version/purpose) | `dependencies:` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:98 |
| 3  | The IPLAN template hardcodes Python in execution_commands setup | `pip install -r requirements.txt` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:114 |
| 4  | The IPLAN template hardcodes Python validation commands | `--cov=src/[module]` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:120 |
| 5  | The IPLAN template hardcodes Python file paths | `tests/unit/test_[module].py` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:87 |
| 6  | IPLAN references its SPEC, so language is inheritable via `@spec` | `@spec: SPEC-NN` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:190 |
| 7  | Hermes validates the three execution_commands categories (contract — must not rename) | `required_categories = ["setup", "implementation", "validation"]` | platforms/hermes/src/mcp_server/validation/iplan_rules.py:104 |
| 8  | Each category must be a non-empty list | `if not isinstance(commands, list) or len(commands) == 0` | platforms/hermes/src/mcp_server/validation/iplan_rules.py:107 |
| 9  | Conformance asserts only `metadata.layer` + `document_type` from the template body | `test_template_parses_and_metadata_matches_registry` | tests/conformance/test_layers.py:35 |
| 10 | Plugin ships a byte-identical GENERATED bundle; edit canonical + re-run the sync script | `dest="$repo_root/platforms/claude-code-plugin/framework"` | tools/sync-plugin-framework.sh:21 |
| 11 | A drift guard fails CI if the bundle diverges from canonical | `test_plugin_framework_bundle.py` | tools/sync-plugin-framework.sh:12 |
| 12 | The plugin doc-iplan skill enumerates the six sections (preserve them) | `Six sections` | platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:246 |
| 13 | Current framework spec version is 0.33.0 (PATCH target 0.33.1) | `0.33.0` | framework/VERSION:1 |
| 14 | `sync-version-refs.sh` auto-rewrites the README "framework spec" block in the framework-bump branch (NOT a manual gap; the README rewrite two lines below fires only when `fw_prev != fw_ver`) | `log "framework sync $fw_prev -> $fw_ver"` | scripts/sync-version-refs.sh:185 |
| 15 | `sync-version-refs.sh` auto-rewrites the conformance spec-version literal (NOT a manual gap) | `replace_in_file tests/conformance/platforms/test_plugin_release_metadata.py` | scripts/sync-version-refs.sh:218 |
| 16 | GATE-SPEC-E005 requires `framework/VERSION` to change on any `framework/**` change | `failures.append("GATE-SPEC-E005")` | tests/chg/spec_gate.py:86 |
| 17 | GATE-SPEC-E008 requires `CHANGELOG.md` in the same diff (hard gate) | `if "CHANGELOG.md" not in files` | tests/chg/spec_gate.py:87 |

## Review log

### Pass 1 — 2026-06-09T00:00:00Z — self-review

- **Initial mis-scope corrected (pre-draft):** first framing called this a
  framework MINOR and proposed phase-labelling `execution_commands`. Reading
  `iplan_rules.py:104` showed the category keys are a validated contract and
  already language-neutral, so the rename was dropped to Out-of-scope and the
  change reduced to example-content de-Pythoning → **PATCH**. The named issue is
  exactly one thing (Python hardcoding); scope now matches it.
- **Propagation completeness:** confirmed the plugin `framework/` is a vendored
  *generated* bundle, not a symlink, so added Task 3 (`sync-plugin-framework.sh`)
  plus V4/V3 drift checks.
- **Governance question resolved:** the user's "should IPLAN include governance?"
  is answered No in Out-of-scope with the layer-boundary rationale.

### Pass 2 — 2026-06-09T00:00:00Z — independent (fresh-context)

A fresh-context reviewer verified all 13 original ledger citations against source
(all correct) and surfaced one load-bearing error plus two refinements:

- **LOAD-BEARING — "two known sync-version-refs gaps" were already closed.** The
  prior draft added a Task 4 to hand-edit the plugin README spec block + the
  conformance literal, citing the 0.15.1→0.15.2 precedent. That precedent's
  *problem statement* was read, not its *fix*: `sync-version-refs.sh:183,197`
  now auto-rewrite both, and `CHANGELOG.md` (0.15.2 entry) documents closing
  exactly those gaps. **Resolution:** deleted the manual Task 4, the two
  File-structure rows, risk R4-old, the scope bullet, and V6-old; added an
  Out-of-scope bullet stating both are auto-synced; added ledger rows 14–15.
  *Verified independently:* read `scripts/sync-version-refs.sh:179-199` and the
  `CHANGELOG.md` 0.15.2 entry before folding in.
- **CHANGELOG is a hard gate, not a soft doc.** `spec_gate.py:86-88` fails
  GATE-SPEC-E005 (VERSION) and GATE-SPEC-E008 (CHANGELOG) for any `framework/**`
  change absent from the diff. **Resolution:** promoted CHANGELOG to Task 4,
  added verification V6 (gate run), added ledger rows 16–17, and noted in Task 2
  that `framework/VERSION` must be *staged* for both the hook and the gate.
- **De-Python safety re-confirmed by the reviewer beyond Hermes:** the acceptance
  harness reads only top-level section keys (not `execution_commands` content),
  no JSON schema validates IPLAN content, and no plugin/Hermes skill embeds its
  own Python command examples — so the edit has no hidden downstream consumer.
  No change needed; recorded for the audit trail.
- **Housekeeping:** stripped the `[REQUIRED]`/`[IF APPLICABLE]` section-tag
  markers per the PLAN-TEMPLATE authoring rule (finalized plans delete them),
  which also lets the `check_plan.py` gate recognize the Claim ledger / Review
  log sections.

### Pass 3 — 2026-06-09T00:00:00Z — independent (fresh-context) re-validation

A second fresh-context reviewer re-validated the Pass 2 patches against source:

- Both auto-syncs the Pass 2 correction depends on are real and fire on a
  `framework/VERSION` bump — plugin README block (`sync-version-refs.sh:179-190`)
  and conformance literal (`:197-199`, with the sibling `assertEqual(...,
  framework_version())` guard intact so the literal-sync does not weaken the
  gate). Pass 2's central correction holds.
- GATE-SPEC-E005 + E008 confirmed as hard failures (`spec_gate.py:85-88`,
  exit 1 on any failure); Tasks 2 + 4 satisfy both.
- All eight rewritten ledger symbols + the nine spot-checked rows resolve to
  their cited `file:line`.
- No dangling reference left by deleting the old manual Task 4: the only
  surviving "manual"/"MINOR"/"rename" mentions are inside this Review log as
  audit history; the live body (Out-of-scope, File-structure, version-impact,
  Tasks, V6/V7, R4) is internally consistent.
- De-Python edit stays green: each `execution_commands` category remains a
  non-empty list, and no conformance test / acceptance fixture / schema reads
  `execution_commands` content (only top-level section keys, `_harness.py:63`).
- Two non-blocking nits noted (V2 grep escaping is shell-fragile but renders
  correctly; ledger row 11 cites the guard's documentation line rather than the
  enforcing assertion in the test file). Neither affects correctness.

### Pass 4 — 2026-07-06 — refresh re-validation (spec 0.15.x → 0.33.0)

The draft sat un-implemented for ~1 month; re-grounded every claim against the current
`0.33.0` tree before reviving:

- **Design still valid.** `IPLAN-TEMPLATE.yaml` **still** hardcodes Python — `file_manifest`
  paths (`:87` `tests/unit/test_[module].py`, `:92` `src/[module]/[component].py`) and
  `execution_commands` (`:114` `pip install`, `:120` `pytest --cov`, `:121` `mypy`, `:122`
  `ruff`). The `setup`/`implementation`/`validation` category keys are unchanged (`:112/116/119`)
  — PR-E's code_build/deploy/combined sub-typing did **not** touch them, so the preserved-contract
  premise holds.
- **Citations re-pointed.** All 17 ledger symbols re-verified present; line numbers moved
  (SPEC `language:` :96→:97; IPLAN paths/commands; `@spec` :159→:190; doc-iplan "Six sections"
  :192→:246; the two `sync-version-refs.sh` auto-syncs :183/:197→:142/:218). Row 13's version
  symbol updated `0.15.2 → 0.33.0`; the two shifted script symbols re-anchored. `check_plan.py
  --fix` re-points advisory lines from the (authoritative) symbols.
- **Version target moved** PATCH `0.15.2→0.15.3` ⇒ `0.33.0 → 0.33.1`; precedent updated to a
  recent framework PATCH (0.32.6→0.32.7). Infra contracts unchanged: GATE-SPEC-E005/E008
  (`spec_gate.py:86-88`), the plugin-bundle drift guard, and `sync-version-refs.sh`
  auto-propagation all still hold at 0.33.0.

### Pass 5 — 2026-07-06 — independent (fresh-context, on the refreshed plan)

A fresh-context reviewer re-verified the refreshed plan against the current tree:
design still valid (template still hardcodes Python; the three category keys survive PR-E);
preserved-contract claim holds (nothing parses `execution_commands` *content* —
`iplan_rules.py:104-107` checks category presence + non-empty only; `test_layers.py`
asserts metadata; the acceptance harness asserts only the section KEY is present; no schema
references it); version/gates correct (VERSION 0.33.0, E005/E008 hard failures, generated
bundle + drift guard). 8+ citations spot-checked — all resolve. **One MINOR:** row-14
citation had been re-pointed to `:142` (the *plugin*-version sync branch, which doesn't fire
on this plugin-unchanged PATCH); the framework-spec README auto-sync is in the `fw_prev !=
fw_ver` branch (`:185-189`). Re-anchored row 14 to `:185` (`log "framework sync …"`) with a
clarified claim. 0 load-bearing.

**Result:** ready — four prior passes (three independent) + a 0.33.0 refresh; the final independent pass surfaced only one MINOR citation re-point (folded), zero load-bearing.
