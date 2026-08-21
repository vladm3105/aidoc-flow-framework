# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** last deployable commit is the `main` tip carrying PR **#520** — verify with
`git log --oneline -1 origin/main` (it was `9f163fda` at the wrap; assert the PR, not the
hash). Framework spec **`0.41.1`**, plugin `0.25.0`, Hermes `0.12.1`. **Merged, not
released** — no tag cut, no consumer has run against `0.41.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.41.1`. Working tree clean except this handoff.

**Verified this session** (run, not asserted): conformance 371 passed / 795 subtests ·
acceptance-deterministic 64 / 56 · `sdd_doc_lint` 5 · `tests/unit` shim 1 / 2 ·
`pre-commit run --all-files` clean. **0 failing.**
*(`pytest tools/sdd_doc_lint/tests` needs `PYTHONPATH=tools` or it fails to collect.)*

## ⚠️ This repo does NOT auto-merge — ask every time

`.github/ai-review/config.json:22` records it as deliberately omitted from the
operations-side `auto_merge.repos` allowlist: spec/governance repo, `tier:spec`,
human-always. **`CLAUDE.md`'s OPS-0062 section reads the opposite way** and is where you
will look first — it describes the generic default, not this repo's exclusion. The
`"enabled": true` flag beside that comment is inert, and the allowlist itself lives in
`vladm3105/aidoc-flow-operations`. PR #520 was merged on the founder's explicit in-session
"merge it if green" — authorization for that PR only. Never infer standing approval.

## The backlog is GitHub issues

`plans/FRAMEWORK-TODO.md` is a tombstone carrying an entry → issue mapping. Do not add to
it; **#509** tracks the remaining pointers that still name it.

**Open issues: 68.** Re-derive with `gh issue list --state open --limit 300` — never
`--search` (tokenised, eventually consistent), never the default `--limit 30`.
In-progress work carries **`status: in progress`**.

## What this session did

**Merged PR #520 — framework spec `0.41.0 → 0.41.1`, ratified as GD-12.** Closes
**#433**, **#434**, **#445**: the CHG gate approval form — the surface a reviewer actually
fills in — disagreed with the gate definitions in both directions. `GATE-03-E008` and
`GATE-SPEC-W003` were defined and catalogued but absent from the form; §2.2's upstream-tag
counts said 2/3/4 against the registry's 1/1/2; three documents stated the ADR requirement
as the full `@brd @prd @ears @bdd` chain. Six statements corrected across three files.
Markers cleared from all three issues.

**Two of the three issues understated their own defect, and the fixing censuses found the
rest.** #433 compared five gates; there are six. #445 named two carriers of the ADR chain;
there are three. Both extras are recorded as comments on those issues.

**New guard: `tests/conformance/test_governance.py::GateCheckIdParity`** — check-id set
equality across all six gates × `{E, W}` × the three surfaces. It compares the form's
**fillable items** (lines carrying `[ ]`), not its mentions, because the mention-based
first draft was measurably satisfiable by prose. Four mutants killed, one survives by
design; both scope limits are in the docstring.

**A near-miss worth knowing about, recorded in GD-12 rather than dropped.** The first
draft wrote *"do NOT add `@brd` or `@prd`"* into two E007 resolution templates — a new
prohibition on a **blocking ERROR**, contradicting four surfaces that permit those tags as
optional provenance (`ADR-TEMPLATE.yaml`, `TRACEABILITY.md`, `REVIEW_TEAM.md`,
`playbooks/05_ADR/auditor.md`). Caught in pre-push review; no test would have caught it.

**Three OPS-0065 review cycles, all FAIL, all folded** — the cap is 3 and was not exceeded.

## What to do next — prioritized

Filter: [`is:open is:issue`](https://github.com/vladm3105/aidoc-flow-framework/issues) ·
in-flight: `--label "status: in progress"`. Below is only the ordering.

1. **[#519](https://github.com/vladm3105/aidoc-flow-framework/issues/519) — filed this
   session and now load-bearing.** `CHG-TEMPLATE.yaml:59` routes `External` to GATE-01
   alone, while `GATE-01:19` claims "External (business impact)" and `GATE-03:19` claims
   "External (technical)". #520's new §2 form note sends a practitioner to that table as
   the authority, so a CVE-driven change now follows it to GATE-01 and never reaches
   `GATE-03-E002`/`E008` — both blocking, both Security. Fix shape and a proposed
   conformance guard are in the issue. GATE-SPEC change; needs a `VERSION` bump.
2. **[#435](https://github.com/vladm3105/aidoc-flow-framework/issues/435)** — the fourth
   gate-docs issue, deliberately left out of #520 because it is a process question
   (gate docs say "Position: Before Layers X-Y" while `CHG-TEMPLATE.yaml`'s workflow
   updates artifacts *before* verifying gate criteria), not a doc correction. Wants its
   own GD entry. Natural pair with #519 in one release.
3. **[#442](https://github.com/vladm3105/aidoc-flow-framework/issues/442) /
   [#443](https://github.com/vladm3105/aidoc-flow-framework/issues/443)** —
   `LINT_RULES.md` is wrong twice over: FM01's stated meaning is false, and five rules
   documented `warning` are always emitted `error` while the `advisory` tier is never
   emitted. Both are spec-vs-implementation, so verify against
   `tools/sdd_doc_lint/__init__.py` before writing.
4. **[#508](https://github.com/vladm3105/aidoc-flow-framework/issues/508)** — the spec
   still names the retired `FRAMEWORK-TODO.md` by path across five `framework/**` files,
   four of them vendored. GATE-SPEC change; can ride with item 1 or 2.
5. **[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423)** — the only
   issue currently marked in progress, and **not** this session's. ⚠️ The previous handoff
   said its work was in `stash@{0}` and not on the remote. **That is now false and needs
   no rescue**: it is committed as `f05dfc0d` on `origin/fix/423-site-badge-selfheal`
   (`scripts/sync-version-refs.sh`, +41/−14). The stash is gone; the work is safe.

## Blockers and standing constraints

**⚠️ PR #517 is open, stale, and should be closed rather than merged.** It carries the
*previous* session's `plans/HANDOFF.md`, which this file supersedes wholesale. It is green
and `CLEAN`, but merging it would restore a superseded handoff. Close it; do not rebase it.

**⚠️ Every doc PR serialises on `CHANGELOG.md`.** All entries insert at the top of
`## [Unreleased]`, so each merge makes the next open PR `DIRTY`. Structural, not a mistake;
the only lever is fewer PRs — which is why items 1 and 2 above are proposed as one release.

**⚠️ `Hermes pytest` is RED on `main` and it is not yours.**
`platforms/hermes/pyproject.toml:7` pins `mcp[cli]>=1.0.0` with no ceiling; pip resolves
**mcp 2.0.0**, which renamed the `Tool` fields, so all four unit modules fail to *collect*.
Red on every run since **2026-07-27**, including #520's. Not a required context, which is
why it survives. **[#465](https://github.com/vladm3105/aidoc-flow-framework/issues/465)**;
founder-deferred. Do not re-diagnose it.

**Phase 0 `lint-smoke` in `tests/scripts/test-acceptance.sh` is RED** — example-corpus debt
deferred to the wholesale regen; use `--skip-lint-smoke`.

**Filed but not fixed this session:** **#518** (Hermes reference corpus states ADR
traceability as "all 4 upstream layers" — a platform corpus, not the spec) and **#519**
(item 1 above).

**What did NOT change:** no release, no tag, neither platform version moved, the example
corpus was not touched, and no `plans/` document other than this one was written.
