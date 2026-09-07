# FRAMEWORK-TODO — retired (tombstone)

> **This file is no longer the backlog. Do not add entries to it.**
> The task surface for this repository is
> **[GitHub issues](https://github.com/vladm3105/aidoc-flow-framework/issues)**.

## Why it was retired

A file-based queue has no reader that can count. Every count in it was
maintained by hand, so every count went stale; nothing surfaced an entry at the
start of a session; and no consumer of this framework could see it at all — a
gap filed here was visible only to someone already inside this repo. A tracker
counts, filters, assigns, and closes on merge for free.

## Where the content went

All **42** open entries that did not already have an issue were migrated
**verbatim** — moved, not re-derived, so no analysis was lost in summarising.
Each migrated issue carries a Provenance section naming its original entry.

**Re-verify `file:line` citations before acting on any migrated issue.** Some
entries predate spec `0.40.0` and were captured against a tree that has since
moved.

The table lists **all 49** open entries. Seven of them already had an
issue and were therefore not migrated — #386, #405, #412, #417, #423, #437
and #465 — which is why 49 rows carry 42 migrations.

Three rows (#492, #498, #501) were **triage section headers** rather than
findings, and #490 was a superseded cross-reference stub; they were migrated
for provenance and can be closed as `not planned` once their successor issues
are confirmed.

| Backlog entry | Issue |
|---|---|
| [layer-promotion] Promote `component_decomposition` to a 02b_DECOMP layer | [#491](https://github.com/vladm3105/aidoc-flow-framework/issues/491) |
| D54 consumer feedback — triage header | [#492](https://github.com/vladm3105/aidoc-flow-framework/issues/492) |
| Engramory consumer feedback — triage header | [#498](https://github.com/vladm3105/aidoc-flow-framework/issues/498) |
| BeeLocal consumer feedback — triage header | [#501](https://github.com/vladm3105/aidoc-flow-framework/issues/501) |
| `ACCEPTANCE-FIXTURE-WARNING-DEBT` | [#478](https://github.com/vladm3105/aidoc-flow-framework/issues/478) |
| `BL-REF-GRANULARITY` | [#502](https://github.com/vladm3105/aidoc-flow-framework/issues/502) |
| `BL-STATUS-SCOPE` | [#503](https://github.com/vladm3105/aidoc-flow-framework/issues/503) |
| `CONTRIBUTING-SECRET-TABLE-NO-CI-ROW` | [#506](https://github.com/vladm3105/aidoc-flow-framework/issues/506) |
| `CORPUS-PRD-TH-RES` | [#487](https://github.com/vladm3105/aidoc-flow-framework/issues/487) |
| `CORPUS-REFGRAN-RECASCADE` | [#486](https://github.com/vladm3105/aidoc-flow-framework/issues/486) |
| `D-0071-JQ-NULL-CLAIM-CONTRADICTED` | [#477](https://github.com/vladm3105/aidoc-flow-framework/issues/477) |
| `D54-F01-PROVISIONAL-IDS` | [#494](https://github.com/vladm3105/aidoc-flow-framework/issues/494) |
| `D54-F02-REUSE-MANIFEST` | [#493](https://github.com/vladm3105/aidoc-flow-framework/issues/493) |
| `D54-F05-BDD-COVERAGE-ROLLUP` | [#495](https://github.com/vladm3105/aidoc-flow-framework/issues/495) |
| `D54-F07-TAG-SYNTAX-REFERENCE` | [#496](https://github.com/vladm3105/aidoc-flow-framework/issues/496) |
| `D54-F08-SKELETON-EMIT` | [#497](https://github.com/vladm3105/aidoc-flow-framework/issues/497) |
| `DEPRECATED-STUB-REMOVAL-V1` | [#484](https://github.com/vladm3105/aidoc-flow-framework/issues/484) |
| `ENG-STALE-DEPTH-DOCS` | [#500](https://github.com/vladm3105/aidoc-flow-framework/issues/500) |
| `FRWK-REVIEW-003-UNSURFACED` | [#466](https://github.com/vladm3105/aidoc-flow-framework/issues/466) |
| `HERMES-MCP-FLOATING-DEP` | [#465](https://github.com/vladm3105/aidoc-flow-framework/issues/465) |
| `IDCOORD-NUMERIC-SECTION-ID` | [#479](https://github.com/vladm3105/aidoc-flow-framework/issues/479) |
| `LINKS-PLATFORM-DEBT` | [#481](https://github.com/vladm3105/aidoc-flow-framework/issues/481) |
| `LINT-FINDING-MESSAGES-UNBOUNDED` | [#474](https://github.com/vladm3105/aidoc-flow-framework/issues/474) |
| `LINT-LOCAL-REGISTRY-NO-TEMPLATES` | [#475](https://github.com/vladm3105/aidoc-flow-framework/issues/475) |
| `LINT-TRACE-RES-SINGLE-FILE` | [#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412) |
| `MCP-CONFIG-DEAD-PATHS` | [#437](https://github.com/vladm3105/aidoc-flow-framework/issues/437) |
| `MODEL-PRECHECK-ROLLOUT` | [#490](https://github.com/vladm3105/aidoc-flow-framework/issues/490) |
| `PIN-CURRENCY-READER-HAS-NO-READER` | [#476](https://github.com/vladm3105/aidoc-flow-framework/issues/476) |
| `PLAN-003-LINK-SUMMARY-RETROFIT` | [#504](https://github.com/vladm3105/aidoc-flow-framework/issues/504) |
| `PRECOMMIT-CONFIG-COMMENTS-STALE` | [#505](https://github.com/vladm3105/aidoc-flow-framework/issues/505) |
| `PREPROD-AGENT-WEBFETCH` | [#468](https://github.com/vladm3105/aidoc-flow-framework/issues/468) |
| `PREPROD-B2-GATE-SCOPE` | [#471](https://github.com/vladm3105/aidoc-flow-framework/issues/471) |
| `PREPROD-HYGIENE` | [#482](https://github.com/vladm3105/aidoc-flow-framework/issues/482) |
| `PREPROD-L7-BARE-DISPATCH` | [#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417) |
| `RELEASE-TIER-STALE-SUBMODULE-PIN` | [#473](https://github.com/vladm3105/aidoc-flow-framework/issues/473) |
| `SAGA-ALL-BRANCHES-FAILED-CLOSES` | [#469](https://github.com/vladm3105/aidoc-flow-framework/issues/469) |
| `SAGA-DRAFT-HARDCODED-FROM-STATE` | [#470](https://github.com/vladm3105/aidoc-flow-framework/issues/470) |
| `SDD-CORPUS-UNVERIFIED` | [#507](https://github.com/vladm3105/aidoc-flow-framework/issues/507) |
| `SEED-ABSORPTION-001-T7` | [#480](https://github.com/vladm3105/aidoc-flow-framework/issues/480) |
| `SKETCH-FILE-STANDALONE` | [#499](https://github.com/vladm3105/aidoc-flow-framework/issues/499) |
| `SKILL-DEDUP-001` | [#483](https://github.com/vladm3105/aidoc-flow-framework/issues/483) |
| `SYNC-FW-TOKEN-SELF-GATED` | [#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) |
| `SYNC-HISTORICAL-REF-CORRUPTION` | [#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) |
| `SYNC-SECRET-SCANNING-KNOBS` | [#467](https://github.com/vladm3105/aidoc-flow-framework/issues/467) |
| `SYNC-VERSION-PROVENANCE-OVERBUMP` | [#485](https://github.com/vladm3105/aidoc-flow-framework/issues/485) |
| `SYNC-WEBSITE-SILENT-NOOP` | [#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423) |
| `TAGGING-GATE-SUBSTRING-ONLY` | [#472](https://github.com/vladm3105/aidoc-flow-framework/issues/472) |
| `TRACE-RES-001-PER-LAYER-TEST-MODE` | [#488](https://github.com/vladm3105/aidoc-flow-framework/issues/488) |
| `WEBSITE-VERSION-BADGE-DRIFT` | [#489](https://github.com/vladm3105/aidoc-flow-framework/issues/489) |

## The 87 closed entries

Closed entries were **not** migrated — they are history, and git holds them.
Read them with:

```sh
git log --follow -p -- plans/FRAMEWORK-TODO.md
```

## What replaces the capture rule

Capture at discovery is unchanged; only the surface moved. Open the issue
instead of appending a row. See `CLAUDE.md` § "Own-repo gaps".
