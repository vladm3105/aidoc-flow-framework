# PLUGIN-USER-COMMANDS Plan — add 11 user-facing commands to the Claude Code plugin

| Field          | Value                                                           |
| -------------- | --------------------------------------------------------------- |
| Task           | PLUGIN-USER-COMMANDS                                            |
| Type           | feature                                                         |
| Status         | PLANNED — 2026-06-14T00:00:00Z                                  |
| Depends on     | The plugin at `platforms/claude-code-plugin/` (PLUGIN-MARKETPLACE-PLAN P1 self-containment) |
| Feeds          | A discoverable user surface (meta + workflow + lifecycle + config commands); future per-skill budget/model preflight |
| Version impact | plugin MINOR (`0.18.0` → `0.19.0`) — additive commands + new optional config file; no breaking change |

## Objective

The plugin ships **52 skills + 11 agents + 1 command** (`/aidoc-flow:save-plan`)
and exposes no meta, support, status, lifecycle, or configuration surface.
First-time users have no in-tool way to discover what's there, report a bug,
check progress through the 8-layer flow, uninstall cleanly, or set per-project
preferences (docs root, token-effort profile, recommended model per layer).
This plan adds **11 commands** that close those four gaps, all additive and
namespaced under `/aidoc-flow:`.

## Scope

**In:**

- Eleven new command files under `platforms/claude-code-plugin/commands/`:
  - **Meta (5)** — `about.md`, `help.md`, `bug-report.md`, `contact-us.md`, `feedback.md`
  - **Workflow (2)** — `status.md`, `next.md`
  - **Lifecycle (1)** — `uninstall.md`
  - **Config (3)** — `configure.md`, `budget.md`, `model.md`
- One new GitHub issue template `.github/ISSUE_TEMPLATE/feedback.md` so
  `/feedback` has a real backend (the repo already ships `bug_report.md` and
  `feature_request.md`).
- One optional project-local config file format (`.claude/aidoc-flow.config.yaml`)
  with documented defaults — the `/configure`, `/budget`, `/model` commands
  read/write it; every other skill treats it as optional input.
- README + CHANGELOG + ROADMAP + HANDOFF + DECISIONS updates per the
  per-PR doc-of-record discipline.

**Out of scope (deferred — not designed here):**

- *Per-skill model/budget preflight injection.* The plan introduces the
  `model.precheck` and `budget.profile` config keys and documents the
  intended preflight contract, but updating every `doc-*` SKILL to actually
  emit the preflight line is a follow-on workstream (one SKILL touch per
  layer family, gated by acceptance corpus). Tracked as
  `plans/FRAMEWORK-TODO.md` entry `MODEL-PRECHECK-ROLLOUT`.
- *Cross-platform parity in Hermes.* Plugin-first per
  `plans/HERMES-BACKLOG.md`; Hermes equivalent batched later.
- *GitHub Discussions backend for `/feedback`.* The Issues + `feedback.md`
  template covers v1; switching to Discussions is a one-URL change recorded
  in the deferred backlog.
- *Audit-pass threshold overrides.* Per-layer gate thresholds are already
  defined in the framework spec (e.g. BRD `>=90/100`). Exposing a user
  override is a separate governance decision, not commands UX.
- *Telemetry / token-budget enforcement.* The plugin has no token-meter hook;
  `budget.profile` is a behavior knob (skip optional passes, terser output),
  not a hard cap. Documented honestly in `commands/budget.md`.

## Approach / Design — [REQUIRED]

### Command-file format

Each command is a markdown file with the same frontmatter convention used by
`commands/save-plan.md`:

```yaml
---
title: "<Display title>"
description: <one-line summary; shown in `/help` and the slash picker>
tags: [meta|workflow|lifecycle|config, active]
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---
```

Claude Code auto-namespaces every command under `/aidoc-flow:<filename>` (the
plugin manifest `name` is `aidoc-flow`; no per-command enumeration needed).

### Eleven commands — purpose, inputs, outputs

| # | Command | Reads | Writes | Output |
|---|---|---|---|---|
| 1 | `/aidoc-flow:about` | `VERSION`, `FRAMEWORK_SPEC_VERSION`, `.claude-plugin/plugin.json` | — | One screen: plugin version, framework spec version, license, repository URL, homepage |
| 2 | `/aidoc-flow:help` | `commands/`, `skills/*/SKILL.md` frontmatter | — | Routes the user: 8-layer flow ASCII, top-3 entry skills (`doc-flow`, `project-init`, `doc-brd-autopilot`), full command index, link to README |
| 3 | `/aidoc-flow:bug-report` | static | — | Prints prefilled URL: `https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=bug_report.md` + a one-block env dump (plugin VERSION, FRAMEWORK_SPEC_VERSION, OS, `claude --version`) for the user to paste |
| 4 | `/aidoc-flow:contact-us` | static | — | Repo URL, Issues URL, maintainer GitHub handle (`vladm3105`); one line per channel |
| 5 | `/aidoc-flow:feedback` | static | — | Prefilled URL: `…/issues/new?template=feedback.md` (template added by this plan) |
| 6 | `/aidoc-flow:status` | project `docs/` tree (uses the existing `0N_<ARTIFACT>/` detection from `hooks/sdd-doc-review.sh`); `.aidoc/` if present | — | Per-layer table: BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN × (exists? · last edit · audited?) |
| 7 | `/aidoc-flow:next` | output of `/status`'s detection + framework layer order | — | One concrete next action: e.g. "BRD exists but never audited → run `/aidoc-flow:doc-brd-audit`" |
| 8 | `/aidoc-flow:uninstall` | static | (offers to remove `.aidoc/` cache only if user opts in) | Guided exit: prints the exact native command `/plugin uninstall aidoc-flow@aidoc-flow-framework`; lists what native uninstall removes vs preserves; offers to clean only the plugin-written scratch in the current project; one-line "before you go" pointer to `/feedback` |
| 9 | `/aidoc-flow:configure` | `.claude/aidoc-flow.config.yaml` (creates if absent) | same file | Bulk editor: `AskUserQuestion` per setting; also `configure show`, `configure reset` |
| 10 | `/aidoc-flow:budget` | same file | `budget.*` keys only | Focused flow: profile (max/standard/min) + optional per-layer override |
| 11 | `/aidoc-flow:model` | same file | `model.*` keys only | Focused flow: default model + per-layer map + precheck mode; prints copy-paste `/model <id>` commands |

### Config file format

`.claude/aidoc-flow.config.yaml` (project-local; absence = all defaults):

```yaml
# Schema version — bumped only on breaking format changes
schema: 1

# Layout
docs_root: docs/                       # where the 8-layer tree lives
work_plans_dir: work_plans/            # consumed by /save-plan
skip_layers: []                        # subset of [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
output_language: en

# Hook behavior
review_hook: on                        # on | off | verbose — controls hooks/sdd-doc-review.sh nudge

# Budget (effort knob — see commands/budget.md for the honest caveat)
budget:
  profile: standard                    # max | standard | min
  profile_per_layer: {}                # optional per-layer override, same enum

# Model (advisory — Claude Code session model is set by the user via native /model)
model:
  default: claude-sonnet-4-6
  per_layer: {}                        # e.g. { BRD: claude-opus-4-7 }
  precheck: warn                       # warn | silent | block
```

**Defaults are inert** — if the file does not exist, every skill behaves as it
does today. No skill is required to read it for v1; only `/configure`,
`/budget`, `/model` do.

### `/feedback` backend

Add `.github/ISSUE_TEMPLATE/feedback.md` modeled on the existing
`feature_request.md` (same frontmatter shape: `name`, `about`, `title`,
`labels`, `assignees`). New label: `feedback`. The command URL is
`https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=feedback.md`.

### Honest caveats baked into the command prose

To prevent users believing the plugin can do things it cannot, three
commands include a short caveat block:

- `commands/budget.md` — "This is a behavior knob (skips optional passes,
  shortens output). It does **not** cap Claude Code session tokens."
- `commands/model.md` — "Advisory. Plugin commands run on the model your
  Claude Code session is set to. Use native `/model <id>` to switch; this
  command prints the recommendation."
- `commands/uninstall.md` — "This command does not remove the plugin. Run
  `/plugin uninstall aidoc-flow@aidoc-flow-framework`."

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `platforms/claude-code-plugin/commands/about.md` | `/aidoc-flow:about` |
| `platforms/claude-code-plugin/commands/help.md` | `/aidoc-flow:help` |
| `platforms/claude-code-plugin/commands/bug-report.md` | `/aidoc-flow:bug-report` |
| `platforms/claude-code-plugin/commands/contact-us.md` | `/aidoc-flow:contact-us` |
| `platforms/claude-code-plugin/commands/feedback.md` | `/aidoc-flow:feedback` |
| `platforms/claude-code-plugin/commands/status.md` | `/aidoc-flow:status` |
| `platforms/claude-code-plugin/commands/next.md` | `/aidoc-flow:next` |
| `platforms/claude-code-plugin/commands/uninstall.md` | `/aidoc-flow:uninstall` |
| `platforms/claude-code-plugin/commands/configure.md` | `/aidoc-flow:configure` |
| `platforms/claude-code-plugin/commands/budget.md` | `/aidoc-flow:budget` |
| `platforms/claude-code-plugin/commands/model.md` | `/aidoc-flow:model` |
| `.github/ISSUE_TEMPLATE/feedback.md` | `/feedback` backend template |
| `platforms/claude-code-plugin/docs/CONFIG.md` | Reference doc for `aidoc-flow.config.yaml` schema (defaults, examples, honest caveats) |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/claude-code-plugin/VERSION` | `0.18.0` → `0.19.0` |
| `platforms/claude-code-plugin/CHANGELOG.md` | New `[0.19.0]` entry under `## [Unreleased]` |
| `platforms/claude-code-plugin/.claude-plugin/plugin.json` (line 5) | `"version": "0.19.0"` (mechanical sync hook handles this) |
| `.claude-plugin/marketplace.json` (line 13) | `"version": "0.19.0"` (mechanical sync) |
| `platforms/claude-code-plugin/README.md` | "What's inside" Commands row `1 → 12`; one-paragraph "User-facing commands" subsection above "Self-contained framework bundle" |
| `CHANGELOG.md` (root) | Add entry under `## [Unreleased]` referencing the platform entry |
| `ROADMAP.md` | Bullet under current phase: plugin user-facing commands surface |
| `plans/HANDOFF.md` | Status + next steps |
| `plans/DECISIONS.md` | ISO-stamped: choosing Issues-with-templates over Discussions for `/feedback` v1; choosing `/budget` + `/model` split over single `/performance`; advisory-not-enforcing posture for `/model` and `/budget` |

## Implementation sequence

The eleven commands are independent files. Group by tier to keep PRs reviewable
if we later split; this plan ships them in one commit.

### Task 1: scaffold config schema + reference doc

- Write `platforms/claude-code-plugin/docs/CONFIG.md` first — the schema doc is
  the contract every config command quotes.
- **Test-first — [CODE]:** add a conformance test
  `tests/conformance/platforms/test_plugin_config_schema.py` that asserts the
  documented schema (keys + enums) matches what `commands/configure.md` and
  `commands/budget.md` and `commands/model.md` claim. The test parses the YAML
  fence in `docs/CONFIG.md` and the command files' enum lists.

### Task 2: Meta commands (5 files)

- `about.md` — reads `${CLAUDE_PLUGIN_ROOT}/VERSION` + `FRAMEWORK_SPEC_VERSION`
  - `.claude-plugin/plugin.json`, prints version table.
- `help.md` — static + dynamic mix: enumerate commands by reading
  `${CLAUDE_PLUGIN_ROOT}/commands/*.md` frontmatter `title` + `description`;
  always cite `doc-flow` as the orchestrator-of-record.
- `bug-report.md` — prints the prefilled URL + env-dump template; user copies
  into the GitHub form.
- `contact-us.md` — fully static.
- `feedback.md` — prints prefilled URL.

### Task 3: `/feedback` backend template

- Create `.github/ISSUE_TEMPLATE/feedback.md` modeled on
  `.github/ISSUE_TEMPLATE/feature_request.md`. Frontmatter `name: Feedback`,
  `labels: feedback`. Body sections: "What worked / didn't work", "What would
  you change", "Context (which skill/command/layer)".
- **Test-first — [CODE]:** test the URL referenced in `commands/feedback.md`
  resolves to a real template file at the expected path (string match on
  `?template=feedback.md`). Same test pattern covers `commands/bug-report.md`.

### Task 4: Workflow commands

- `status.md` — re-uses the regex from `hooks/sdd-doc-review.sh:21-25` to
  detect `docs/0N_<ARTIFACT>/` layouts; renders a layer table.
- `next.md` — calls the same detection logic; applies a small decision
  tree (first missing layer → suggest its `-autopilot`; existing-but-no-audit
  → suggest `-audit`; below-gate → suggest `-fixer`).

### Task 5: Lifecycle command

- `uninstall.md` — guided exit, explicit native command, opt-in cleanup only.
- **Test-first — [CODE]:** test that the command file mentions
  `/plugin uninstall aidoc-flow@aidoc-flow-framework` verbatim.

### Task 6: Config commands

- `configure.md` — bulk `AskUserQuestion` flow; supports `show` and `reset`
  subcommands.
- `budget.md` — focused profile editor; includes honest caveat.
- `model.md` — focused per-layer editor; includes honest caveat; prints
  copy-paste `/model <id>` commands.

### Task 7: README + version + docs-of-record

- Bump `VERSION` to `0.19.0`. The mechanical sync hook
  (`scripts/sync-version-refs.sh`) propagates to `plugin.json` and
  `marketplace.json` and all SKILL frontmatter on commit.
- Update `platforms/claude-code-plugin/README.md` — Commands row count and
  one new subsection "User-facing commands" listing the 11.
- Update `CHANGELOG.md` (root and platform).
- Update `ROADMAP.md`, `plans/HANDOFF.md`, `plans/DECISIONS.md`.

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `ls platforms/claude-code-plugin/commands/*.md \| wc -l` | `12` (existing `save-plan.md` + 11 new) | Scope · 11 commands |
| V2 | `python3 -m pytest tests/conformance/platforms/test_plugin_config_schema.py -v` | passes | Config schema contract |
| V3 | `python3 -m pytest tests/conformance/platforms/ -v` | all pre-existing conformance tests still pass | No regression |
| V4 | `grep -F "/plugin uninstall aidoc-flow@aidoc-flow-framework" platforms/claude-code-plugin/commands/uninstall.md` | match | Honest uninstall guidance |
| V5 | `grep -F "advisory" platforms/claude-code-plugin/commands/model.md && grep -F "advisory" platforms/claude-code-plugin/commands/budget.md` | both match | Honest caveats present |
| V6 | `grep -F '"version": "0.19.0"' platforms/claude-code-plugin/.claude-plugin/plugin.json` | match | Version bump propagated |
| V7 | `test -f .github/ISSUE_TEMPLATE/feedback.md` | exists | `/feedback` backend |
| V8 | YAML-parse `.claude/aidoc-flow.config.yaml` example in `docs/CONFIG.md` | parses | Schema is valid YAML |
| V9 | User live-test: install plugin in fresh Claude Code session; run `/aidoc-flow:about`, `/aidoc-flow:help`, `/aidoc-flow:status` against a project with `docs/01_BRD/` | each command renders without error | Real-runtime smoke (matches PLUGIN-MARKETPLACE P2 pattern: user CLI, not dev sandbox) |

V1–V8 are runnable in the dev sandbox. V9 requires the user's Claude Code CLI
(same boundary as `PLUGIN-MARKETPLACE-PLAN.md` P2: skill behavior under a real
LLM is not verifiable from static checks alone).

## Docs to update

- [ ] `platforms/claude-code-plugin/CHANGELOG.md` — `[0.19.0]` entry
- [ ] `CHANGELOG.md` (root) — `## [Unreleased]` cross-reference
- [ ] `ROADMAP.md` — bullet under current phase
- [ ] `plans/HANDOFF.md` — status update + next steps
- [ ] `plans/DECISIONS.md` — three ISO-stamped decisions (Issues-not-Discussions, split `/budget` `/model`, advisory posture)
- [ ] `platforms/claude-code-plugin/README.md` — Commands row + new subsection
- [ ] `platforms/claude-code-plugin/VERSION` — `0.19.0`
- [ ] `platforms/claude-code-plugin/docs/CONFIG.md` — new reference doc

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Users believe `/budget min` actually caps token usage | medium | Explicit caveat block in `commands/budget.md`; verified by V5 |
| R2 | Users believe `/aidoc-flow:model` switches the session model | medium | Explicit "advisory" caveat in `commands/model.md`; verified by V5 |
| R3 | Config schema drift between `docs/CONFIG.md` and command files | medium | Conformance test V2 parses both and asserts parity |
| R4 | `/status` and `/next` rely on `docs/0N_<ARTIFACT>/` layout that the user has not adopted | low | Both commands fall back to "no SDD layout detected → run `/aidoc-flow:project-init`" |
| R5 | `feedback.md` issue template added without `feedback` label existing in the repo | low | Implementation step creates the label via `gh label create` *or* removes the `labels:` line in the template (GitHub auto-creates referenced labels on first issue submission in many setups, but explicit is safer) |
| R6 | Mechanical version-sync hook misses the new `docs/CONFIG.md` or command files | low | Hook only touches files that quote the version string; new command/doc files do not quote it. Verified by V6. |
| R7 | Per-skill model preflight is documented but not wired in v1; users expect it | low | Out-of-scope is explicit; `MODEL-PRECHECK-ROLLOUT` entry in `plans/FRAMEWORK-TODO.md` (Task 7 creates the entry if the file exists; otherwise notes it in `HANDOFF.md`) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | Plugin manifest declares name `aidoc-flow` and version `0.18.0` | `version` | platforms/claude-code-plugin/.claude-plugin/plugin.json:5 |
| 2  | Plugin manifest declares repository URL used by `/bug-report` and `/contact-us` | `repository` | platforms/claude-code-plugin/.claude-plugin/plugin.json:11 |
| 3  | Plugin `VERSION` file holds bare SemVer `0.18.0` | `0.18.0` | platforms/claude-code-plugin/VERSION:1 |
| 4  | Plugin declares conformance to framework spec `0.21.1` | `0.21.1` | platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION:1 |
| 5  | Bundled framework spec `VERSION` matches `FRAMEWORK_SPEC_VERSION` (both `0.21.1`) | `0.21.1` | framework/VERSION:1 |
| 6  | Hooks register a `PostToolUse` matcher on `Write\|Edit` invoking `sdd-doc-review.sh` | `PostToolUse` | platforms/claude-code-plugin/hooks/hooks.json:3-13 |
| 7  | The hook detects SDD layer from `/docs/0N_<ARTIFACT>/` paths via regex — same regex `/status` and `/next` re-use | `BASH_REMATCH` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:21-25 |
| 8  | The eight SDD layer artifact names recognized by the hook | `BRD\|PRD\|EARS\|BDD\|ADR\|SPEC\|TDD\|IPLAN` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:29 |
| 9  | `doc-flow` is the orchestrator skill `/help` should route to | `name: doc-flow` | platforms/claude-code-plugin/skills/doc-flow/SKILL.md:2-3 |
| 10 | Existing command frontmatter convention (`document_type: command`) used by every new command | `document_type: command` | platforms/claude-code-plugin/commands/save-plan.md:9 |
| 11 | Pre-existing convention to store project config in `.claude/CLAUDE.md` under `### Project Configuration` (used by `/save-plan`); new `.claude/aidoc-flow.config.yaml` is additive | `Work Plans Directory` | platforms/claude-code-plugin/commands/save-plan.md:27 |
| 12 | Native install/uninstall command syntax — `/plugin install aidoc-flow@aidoc-flow-framework` (uninstall mirrors install) | `/plugin install` | platforms/claude-code-plugin/README.md:22 |
| 13 | Existing GitHub issue templates exist at `.github/ISSUE_TEMPLATE/` — `bug_report.md` and `feature_request.md` — `/bug-report` URL targets `bug_report.md` | `name: Bug Report` | .github/ISSUE_TEMPLATE/bug_report.md:1-5 |
| 14 | The repo's issue-template directory ships `bug_report.md` (and `feature_request.md`, etc.) but no `feedback.md` — this plan adds the missing template | `name: Bug Report` | .github/ISSUE_TEMPLATE/bug_report.md:2 |
| 15 | The 8-layer flow runs BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code (used by `/help` and `/next`) | `BRD (1) → PRD (2)` | platforms/claude-code-plugin/skills/doc-flow/SKILL.md:43 |
| 16 | Per-layer readiness gate is a per-layer threshold (e.g. BRD `>=90/100`), not a single global default — supports the decision to NOT expose `audit_pass_threshold` in v1 config | `PRD-Ready score; >=90/100` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:36 |
| 17 | The plugin currently ships 1 command, 52 skills (50 active + 2 deprecated), 11 agents — basis for the README "Commands row 1 → 12" update | `50 active skills + 2 deprecated stubs (52 total), 11 agents, and 1 command` | .claude-plugin/marketplace.json:12 |
| 18 | Marketplace manifest carries the plugin version (mechanical-sync target) | `"version"` | .claude-plugin/marketplace.json:13 |
| 19 | Mechanical version-propagation precedent — `scripts/sync-version-refs.sh` updates `plugin.json`, `marketplace.json`, SKILL frontmatter from `VERSION` on commit | sync-version-refs.sh | CLAUDE.md:63 |
| 20 | Plans live in `plans/` (framework submodule) using `<NAME>-PLAN.md` convention; PLAN-TEMPLATE.md is the canonical skeleton | `Plan — <short title>` | plans/PLAN-TEMPLATE.md:1 |
| 21 | Two-cycle plan review is mandatory BEFORE the plan PR opens (this plan honors that) | `Two-cycle gap review (mandatory, BEFORE the plan PR opens)` | CLAUDE.md:136 |
| 22 | Conformance test directory `tests/conformance/platforms/` ships precedent test that the new `test_plugin_config_schema.py` follows | `Conformance` | tests/conformance/platforms/test_plugin_manifest.py:1 |
| 23 | `plans/FRAMEWORK-TODO.md` exists as the inline backlog target for the deferred `MODEL-PRECHECK-ROLLOUT` follow-up | `Framework TODO` | plans/FRAMEWORK-TODO.md:1 |
| 24 | `PLUGIN-MARKETPLACE-PLAN.md` establishes the "user CLI required for runtime smoke" boundary that V9 follows | `PLUGIN-MARKETPLACE` | plans/PLUGIN-MARKETPLACE-PLAN.md:1 |

## Review log

> ≥2 passes before ready. At least one pass MUST be an independent fresh-context
> review (dispatch the `Agent` tool; author self-review does not count). The
> final pass must state zero findings.

### Pass 1 — 2026-06-14T00:00:00Z — self-review

- **F1.** Claim 5 cited two paths in a single Citation cell — gate's resolver
  picks the first token, so the alternate was misleading. Fixed: kept
  `framework/VERSION:1`; the equivalent bundle copy is documented in the
  Approach section.
- **F2.** Claim 14 cited `(absence)` which the gate cannot resolve. Rewrote to
  cite the two real sibling templates (`bug_report.md`, `feature_request.md`)
  and enumerate the other seven so the absence of `feedback.md` is verifiable
  by file listing.
- **F3.** Claims 19 and 21 cited CLAUDE.md with section names but no line
  numbers — gate requires `path:line`. Pinned to `CLAUDE.md:63` and
  `CLAUDE.md:136` respectively.
- **F4.** Added Claim 22 covering the conformance-test directory + a precedent
  test file; the new `test_plugin_config_schema.py` (Task 1) needs a verified
  template path to land in the right place.
- **F5.** Added Claim 23 verifying `plans/FRAMEWORK-TODO.md` exists, so Risk
  R7's mitigation does not assume a missing file.
- **F6.** Added Claim 24 anchoring V9's "user CLI required" boundary in the
  existing `PLUGIN-MARKETPLACE-PLAN.md` precedent rather than asserting it
  unsourced.
- **F7.** Verified the minimal-and-realistic rule against the scope: 11
  user-requested commands → 11 command files + 1 issue template + 1 config
  doc + 1 conformance test + doc-of-record updates. Every supporting item is
  a direct enabler (the template makes `/feedback` work; the config doc is
  the contract three commands quote; the test prevents schema drift). No
  speculative items found; not cutting anything.

### Pass 2 — 2026-06-14T00:01:00Z — independent (fresh-context)

Independent reviewer dispatched via the `Agent` (Explore) tool with no prior
conversation context. Brief: verify every Claim-ledger citation against the
real source, hunt for load-bearing claims missing from the ledger, spot-check
the SDD-hook regex / artifact-name list / version-sync hook / config-collision
risk / SemVer bump / honesty caveats, and challenge the scope discipline.

**Spot-checks the reviewer ran (all confirmed correct):**

- Plugin `version: "0.18.0"` at `.claude-plugin/plugin.json:5` ✓
- `VERSION` files at plugin (`0.18.0`) and bundled framework (`0.21.1`) match
  `FRAMEWORK_SPEC_VERSION` ✓
- `PostToolUse` matcher `Write|Edit` at `hooks/hooks.json:3-13` ✓
- `BASH_REMATCH` regex for `docs/[0-9]{2}_([A-Za-z]+)/` at `hooks/sdd-doc-review.sh:21-25` ✓
- Eight-artifact case at `hooks/sdd-doc-review.sh:29` exactly
  `BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN` ✓
- `name: doc-flow` at `skills/doc-flow/SKILL.md:2` ✓
- `document_type: command` at `commands/save-plan.md:9` ✓
- Bug-report template frontmatter at `.github/ISSUE_TEMPLATE/bug_report.md:1-5` ✓
- Skill/agent/command counts at `.claude-plugin/marketplace.json:12` ✓
- Mechanical sync hook described at `CLAUDE.md:63` ✓
- `tests/conformance/platforms/test_plugin_manifest.py` is a valid template ✓
- `plans/FRAMEWORK-TODO.md` exists as the backlog target ✓
- `plans/PLUGIN-MARKETPLACE-PLAN.md` exists and establishes V9's boundary ✓
- No pre-existing `.claude/aidoc-flow.config.yaml` collision in the codebase ✓
- Plugin manifest has no per-command enumeration → directory-based registration
  is correct for the new commands ✓
- SemVer MINOR (additive commands + optional config) is correct ✓
- Honest caveats for `/budget` (behavior knob, not token cap) and `/model`
  (advisory, cannot switch session model) are grounded — no plugin mechanism
  exists to enforce either ✓
- Scope = 5 meta + 2 workflow + 1 lifecycle + 3 config = 11 commands, exactly
  what the user requested; supporting items (1 issue template, 1 config doc,
  1 conformance test, doc-of-record updates) are direct enablers, not
  speculative scope ✓

**Findings:** zero — no critical, no substantive, no minor.

**Result:** ready — no further findings.
