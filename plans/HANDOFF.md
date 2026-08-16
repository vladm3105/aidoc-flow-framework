# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** last deployable commit is the `main` tip carrying PR **#516** (the framework
`0.41.0` fold) — verify with `git log --oneline -1 origin/main`. **Framework spec moved
this session: `0.40.0 → 0.41.0`.** Plugin `0.25.0` and Hermes `0.12.1` are **unchanged**.
**Nothing was released and no tag was cut** — merged is not deployed. Working tree clean
apart from this handoff.

## ⚠️ The backlog is GitHub issues. `plans/FRAMEWORK-TODO.md` is a tombstone

It carries an entry → issue mapping and nothing else. Do not add to it. Any instruction
telling you to append to it is stale (**#508**/**#509** track the remaining pointers).
**69 open issues.** Re-derive with `gh issue list --state open --limit 300` — never
`--search` (tokenised, eventually consistent) and never the default `--limit 30` (this
repo is past #500). In-progress work carries the label `status: in progress`.

## What this session did

**Merged three PRs.** #512 (the previous wrap's handoff) · **#457** (closes **#417**,
scoped agent dispatch) · **#516** (closes **#444/#446/#448/#450**, the `0.41.0` fold).
In-progress markers cleared on all five closed issues — the merge does not do it.

**#417 — the previous handoff's top item was partly wrong, and the wrong part was the
expensive one.** It prescribed rewriting the 51 playbooks' bare `agent:` key "in the plugin
mirror only, via `tools/sync-plugin-framework.sh`". Impossible: that script `cp -R`s
`framework/` **over** the mirror, and `test_plugin_framework_bundle.py` asserts the mirror
byte-identical, so a hand-edit fails a required check and is then overwritten. The premise
was also wrong — **GD-06 ratifies that key as an engine-defined executor each platform maps
for itself**, and the plugin resolves lens → agent from its own crew table
(`skills/review-team/SKILL.md`), never from the key. The "51" was right; the conclusion was
not. Now recorded in the guard's docstring, both changelogs and `docs/AGENTS.md`, so it is
not re-derived.

A scripted census found **five** real missed surfaces where the handoff listed three.

**#516 — a false blocker was caught in review, in my own GD entry.** GD-11's first draft
said the four PRs "cannot merge independently". `tests/chg/spec_gate.py:78-88` shows E005 is
a membership test on `framework/VERSION` that does **not** constrain the value, so
sequential merges at `0.41.0`/`0.42.0`/… each pass. The entry's "precedent set" bullet
rested on that premise, so merged it would have licensed batching governance work behind a
false appeal to a gate. Rewritten to the cost argument and narrowed.

**Filed 3 issues** — #513, #514, #515 — all from review of this session's own work.

**#423's work is no longer at risk.** It was in `stash@{0}`, which does not survive a
container. Now commit `f05dfc0d` on pushed branch `fix/423-site-badge-selfheal`, confirmed
with `git branch -r --contains`. **An unreviewed WIP commit, not a PR.**

## Verification — run this session, on the merged tip

| Check | Result |
|---|---|
| `tests/conformance` | 369 passed, 783 subtests |
| `tests/acceptance/deterministic` | 64 passed, 56 subtests |
| `tools/sdd_doc_lint/tests` | 5 passed |
| `tests/conformance/test_repo_scripts.py` (the `tests/unit` shim) | 1 passed, 2 subtests |
| `pre-commit run --all-files` | clean |

**0 failing.** Run them with `PYTHONPATH=tools` — without it `sdd_doc_lint` fails on import
and reads as a regression.

## What to do next — prioritized

Filter: [`is:open is:issue`](https://github.com/vladm3105/aidoc-flow-framework/issues) ·
in-flight: `--label "status: in progress"`. Below is only the ordering.

1. **[#513](https://github.com/vladm3105/aidoc-flow-framework/issues/513) — Hermes ships a
   stale copy of a spec file that now teaches a forbidden practice.**
   `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/references/ai-assistant-rules.md:12`
   still says *"Use the cumulative tag hierarchy `@brd` → … → `@iplan`"*, which canonical
   `framework/AI_ASSISTANT_RULES.md:12` now calls **trace fabrication (forbidden)**; `:23-26`
   carry all four pre-fix generation-order clauses. #516 re-pinned Hermes to `0.41.0` while
   this copy stayed behind. `platforms/**` only — **no version bump, no GATE-SPEC.**
   Actionable with no discovery.
2. **[#514](https://github.com/vladm3105/aidoc-flow-framework/issues/514) — the document-ID
   lockstep is one-sided and misses a fourth surface.** `ucx-validation-gate.sh:54` gates
   `^BRD-[0-9]{2}$`; `saga_orchestrator.py:66` accepts 1-digit IDs neither the registry nor
   the new schema allows. Both `platforms/hermes/**`; can ship with item 1.
3. **[#515](https://github.com/vladm3105/aidoc-flow-framework/issues/515) — `@chg:` is
   defined on a page scoped to trace tags**, while the other two non-trace tags live in
   `ID_NAMING_STANDARDS.md`/`TRACEABILITY.md` *with* a `cross_links` template slot `@chg:`
   lacks — so a P1 requirement has no key to write into. `framework/**`: needs a `VERSION`
   bump + GD entry, so **batch with the next spec release**, not alone.
4. **`plans/DECISIONS.md` — D-entry for the precedence carve-out.** Deferred by #510, still
   open. Records that this repo's own-gaps rule governs over the spec's Tier-2 model until
   #508 lands. A decision taken with no decision-log entry is the gap.
5. **[#508](https://github.com/vladm3105/aidoc-flow-framework/issues/508)** — the spec still
   names the retired `FRAMEWORK-TODO.md` by path across five `framework/**` files with four
   vendored mirrors. GATE-SPEC change; rides with item 3 on the next bump.
6. **[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423)** — still labelled
   in progress, correctly. Review `f05dfc0d` on `fix/423-site-badge-selfheal` before opening
   a PR; it has had none.

## Blockers and standing constraints

**⚠️ This repo does not auto-merge — ask every time.**
`.github/ai-review/config.json:22` records it as deliberately omitted from the
**operations-side** `auto_merge.repos` allowlist (spec/governance repo, `tier:spec`,
human-always), and that allowlist is read from `trust_config_repo`
(`vladm3105/aidoc-flow-operations@main`), **not** from this repo. All three merges this
session ran on **explicit founder authorization given in-session**. Never infer standing
approval from the fact they merged.

**⚠️ A governance PR that bumps a version cannot meet the ≤3-surface cap.**
`sync-version-refs.sh` re-stages its own writes, so `VERSION`, `CLAUDE.md`'s token,
`README.md`, `docs/PARITY.md`, both platform READMEs and the SKILL frontmatters move
together or conformance goes red. #516 was 178 files. **The founder granted the Rule 1
exception per-bump, in-session, with an audit-trail line in the commit** — ask again; it is
not standing.

**⚠️ `Hermes pytest` is RED on `main` and it is not yours.**
`platforms/hermes/pyproject.toml:7` pins `mcp[cli]>=1.0.0` with no ceiling; pip resolves
**mcp 2.0.0**, which renamed the `Tool` fields, so all four unit modules fail to *collect*.
Red on every run since **2026-07-27**. **Not a required context**, which is why it survives.
Tracked as [#465](https://github.com/vladm3105/aidoc-flow-framework/issues/465); the founder
deferred the fix. Do not re-diagnose it — it will be the only red on every PR you open.

**⚠️ Every doc PR serialises on `CHANGELOG.md`.** All insert at the top of `## [Unreleased]`,
so each merge makes the next PR `DIRTY`. Expect a rebase per PR; it is structural.

**⚠️ A plugin `VERSION` bump needs a hand-authored `docs/TAGGING.md` row**, or conformance
goes red — `test_plugin_release_metadata.py:137`. A **framework-spec** bump does **not**:
that assertion covers only the plugin tag, and no test asserts a `framework/v` row. Measured
this session, so do not re-derive it from the plugin rule.

**Phase 0 `lint-smoke` in `tests/scripts/test-acceptance.sh` is RED** — example-corpus debt
deferred to the wholesale regen; use `--skip-lint-smoke`. That harness runs on no PR path
here (only the umbrella's `release.yml`, on `v*` tags, against a **pinned old SHA**).

**Not verified this session:** nothing released, no tag cut, neither platform version moved,
no example-corpus regen attempted. The `0.41.0` spec bump is **merged, not deployed** — no
consumer has run against it.
