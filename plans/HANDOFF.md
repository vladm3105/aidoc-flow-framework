# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** last deployable commit is the `main` tip carrying PR **#510** (the backlog
retirement) — verify with `git log --oneline -1 origin/main`. Framework spec `0.40.0`,
plugin `0.25.0`, Hermes `0.12.1` — **unchanged this session; nothing was released.**
Five PRs merged, five open. Working tree: clean except this handoff and a `CHANGELOG.md`
entry for #511, both landing in the wrap commit.

## ⚠️ The backlog moved. `plans/FRAMEWORK-TODO.md` is a tombstone

**GitHub issues are the task surface.** `plans/FRAMEWORK-TODO.md` no longer holds work —
it carries an entry → issue mapping table and nothing else. Do not add to it. Any
instruction you find elsewhere telling you to append to it is stale (**#509** tracks the
remaining pointers).

**Open issues: 71.** Re-derive with `gh issue list --state open --limit 300` — never
`--search` (tokenised and eventually consistent), and never the default `--limit 30`
(this repo is past #500).

In-progress work is labelled **`status: in progress`** (created this session; there is no
project board, and the token was checked — `gh issue list --label "status: in progress"`).

## What this session did

**Merged five PRs.** #459 (#437, dead `.mcp.json` paths) · #464 (#405, version-fanout
count guard) · #456 (#412, single-file `TRACE-RES-001`) · #510 (backlog retirement) ·
PR #511 (`AGENTS.md` routed to the tracker). Issues #405/#412/#437 closed by their
merges; markers cleared. *(That `PR` prefix is load-bearing — markdownlint's autofix
turns a line-initial `#511` into an H1.)*

**Filed 45 issues (#465–#509).** 42 are the backlog migrated **verbatim** — moved, not
summarised, because the entries carry `file:line` evidence worth more than their titles.
All 42 verified to carry a Provenance section warning that some predate spec `0.40.0`.

**Reviewed the eight queued fix PRs** with a three-lens OPS-0065 pass. That review is the
reason four of them are not merged: they fixed their instance and left a sibling alive
while claiming the class closed. Findings are in each PR thread.

**V15 is CONFIRMED and its paragraph is deleted** — a `schedule`-triggered
`standards-drift` was followed by a `workflow_run` `pin-currency-reader` on both
2026-08-03 and 2026-08-10, all four runs green. That is the chain V14 could only prove
off a dispatched upstream. Do not re-open it.

## What to do next — prioritized

Filter: [`is:open is:issue`](https://github.com/vladm3105/aidoc-flow-framework/issues) ·
in-flight: `--label "status: in progress"`. Below is only the ordering.

1. **[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417) — PR #457 is
   open and does NOT close it.** Security: the plugin's read-only review gate stays
   subvertible. The PR scoped the tables and literals, but review found three live
   surfaces it misses — **51 playbook files carry bare `agent: <name>` frontmatter**
   (`framework/playbooks/**`, and `REVIEW_TEAM.md:259` defines that key as the lens's
   *executor*), the nine `doc-*-fixer` skills say "Dispatch the synthesizer" in prose with
   no identifier, and the new guard's `TABLE_ROW_LAST_CELL` regex anchors to the **last**
   cell so it cannot see `platforms/claude-code-plugin/README.md:213-224`, where the agent
   is the middle cell. ⚠️ **Do not scope the playbooks in `framework/`** — the spec carries
   no platform names. Rewrite `agent:` → `aidoc-flow:agent` in the *plugin mirror only*,
   via `tools/sync-plugin-framework.sh`. Rebase onto `main` first.
2. **PRs #460–#463 → fold into ONE spec PR.** All four are correct and all four are red on
   **GATE-SPEC E005** (`framework/**` changed, `framework/VERSION` not bumped). They would
   bump to the same version, so they cannot merge independently. Shape: `framework/VERSION`
   `0.40.0 → 0.41.0` (MINOR — #461 adds a normative `@chg:` tag), a **GD-11** entry in
   `framework/governance/DECISIONS.md` + its plugin mirror, both
   `platforms/*/FRAMEWORK_SPEC_VERSION`, then the sync fanout. Precedent: the 0.40.0 bump
   (`eb48d051`) touched **174 files** in one commit. Propagation order is load-bearing:
   `framework/VERSION` → `scripts/sync-version-refs.sh` → `tools/sync-plugin-framework.sh`.
3. **`plans/DECISIONS.md` — D-entry for the precedence carve-out.** #510 deferred it. It
   records that this repo's own-gaps rule governs over the spec's Tier-2 model until #508
   lands. A decision taken with no decision-log entry is the gap.
4. **[#508](https://github.com/vladm3105/aidoc-flow-framework/issues/508)** — the spec
   still names the retired file by path across **five** `framework/**` files with four
   vendored mirrors. GATE-SPEC change; needs the 0.41.0 bump, so it can ride with item 2.
5. **[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423)** — work in
   progress is in **`stash@{0}`** on branch `fix/423-site-badge-selfheal`
   (`scripts/sync-version-refs.sh`, +41/−14). ⚠️ Stashes do not survive a container, and
   this one is **not on the remote** — recover or discard it early.

## Blockers and standing constraints

**⚠️ This repo does not auto-merge.** `.github/ai-review/config.json:22` records it as
deliberately omitted from the **operations-side** `auto_merge.repos` allowlist — spec/
governance repo, `tier:spec`, human-always. ⚠️ That allowlist is read from
`trust_config_repo` (`vladm3105/aidoc-flow-operations@main`), **not** from this repo.
This session's five merges ran on **explicit founder authorization given in-session**
("merge it with `--admin`"). Ask; never infer standing approval from the fact they merged.

**⚠️ Every doc PR serialises on `CHANGELOG.md`.** All of them insert at the top of
`## [Unreleased]`, so each merge makes the next PR `DIRTY`. Four rebases this session —
structural, not a mistake. Folding #460–#463 into one PR removes three of them.

**⚠️ `Hermes pytest` is RED on `main` and it is not yours.**
`platforms/hermes/pyproject.toml:7` pins `mcp[cli]>=1.0.0` with no ceiling; pip now
resolves **mcp 2.0.0**, which renamed the `Tool` fields, so all four unit modules fail to
*collect*. Red on every run since **2026-07-27**. Not a required context, which is why it
survived. Tracked as **[#465](https://github.com/vladm3105/aidoc-flow-framework/issues/465)**;
the founder deferred the fix this session. Do not re-diagnose it.

**⚠️ A plugin `VERSION` bump needs a hand-authored `docs/TAGGING.md` row**, or conformance
goes red — `tests/conformance/platforms/test_plugin_release_metadata.py:137` asserts the
current tag string appears in the file, and `sync-version-refs.sh:56-60` deliberately does
not write it. That assertion is a bare substring check, satisfied by the § "Release
inventory" preamble as well as the row.

**Phase 0 `lint-smoke` in `tests/scripts/test-acceptance.sh` is RED** — example-corpus debt
deferred to the wholesale regen; use `--skip-lint-smoke`. That harness runs on no PR path
here (only the umbrella's `release.yml`, on `v*` tags, against a **pinned old SHA**).

**Not verified this session:** nothing was released, no tag was cut, and neither platform
version moved. The 0.41.0 bump in item 2 has not been started.
