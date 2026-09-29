# Consolidated learnings

System of record for durable lessons from session work. Human- and
agent-readable; every entry carries verified evidence, never paraphrase alone.
Harness memory is the scratch inbox — promotion lands here, by PR, so every
agent with a checkout sees the same lessons.

Contract: entry format and lifecycle follow `.agents/skills/self-learn/`
(qualify → add/bump/archive; 30-day age-out; count ≥ 5 graduates to
`framework/governance/DECISIONS.md` or the issue tracker). Hygiene per
`memory-hygiene`. Declared in `AGENTS.md` ("Where state lives").

## [workflow] Flaky GitHub ops need backoff + re-verification, never a diagnosis
- **First seen**: 2026-09-28
- **Last seen**: 2026-09-29
- **Count**: 8
- **Lesson**: On `Could not resolve host` / `error connecting to api.github.com`, sleep and retry; re-read `gh pr checks` fresh before acting — a FAILURE badge seen during the outage window may be stale/transient.
- **Evidence**: 2026-09-28 `git push` failed 2x then succeeded, API errors interleaved with successes; 2026-09-29 `gh pr view 777/778` failed 3x with `error connecting to api.github.com`, recovered after 30s backoff, both PRs read back MERGED
- **Governance rule**: aidoc-triage §5 flaky pool (rerun, don't chase)

## [workflow] Read-back discipline: a URL or exit code alone never proves a write
- **First seen**: 2026-09-28
- **Last seen**: 2026-09-29
- **Count**: 4
- **Lesson**: After every mutating call (issue create/comment/edit, transfer, merge), read the object back and check the field that matters (body length non-zero, labels list, state MERGED). `--body -` publishes a literal `-` with exit 0; a merge command printing a diffstat does not prove MERGED.
- **Evidence**: AGENTS.md read-back rule; 2026-09-29 comment IDs 5880738964/5880739537/5880962628 read back by length, merges 9212effc/e44aaaff read back as MERGED
- **Governance rule**: AGENTS.md (verify-what-you-published); submit-feedback §6; ship-it §3

## [workflow] Re-watch from the new head after every push (stale-SHA trap)
- **First seen**: 2026-09-28
- **Last seen**: 2026-09-29
- **Count**: 2
- **Lesson**: A push voids every prior check reading — confirm `headRefOid` before trusting any colour, kill superseded watches, and re-watch from the new head. A previous run's green is not this commit's.
- **Evidence**: 2026-09-28 zero-job heads vs fresh green heads; 2026-09-29 PR #778 AGENTS.md push 406addf0: terminated the stale watch, re-watched to green on the new head, merged
- **Governance rule**: AGENTS.md (watching-your-PR, headRefOid); ship-it §1 stale-SHA trap

## Candidates logged, not promoted (single occurrence)
- Repo-wide zero-match grep before engaging a filed "contradiction" (2026-09-29, #775) — closed as covered by aidoc-triage §2's core discipline; no separate entry.
- Duplicate-skill check before creating (2026-09-29, two same-session applications) — stays candidate, Count 2; needs one cross-session observation.
