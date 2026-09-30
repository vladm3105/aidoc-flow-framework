# Knowledge Governance — DRAFT (for discussion, not normative)

Status: Draft — 2026-09-29. Nothing below is binding until ratified through the
repo's change process. Open questions are marked **[DISCUSS]** inline.

## 1. Problem

Agents re-learn the same lessons from zero in every project: flaky-network
backoff, read-back discipline, stale-head re-watches. Harness-local memory does
not cross machines, and per-repo logs do not cross repositories. The knowledge
is internal self-improvement capital — what a product owner accumulates — and
currently it evaporates.

## 2. Model: three tiers

| Tier | Home | Content | Survives |
|---|---|---|---|
| 1. Session scratch | harness memory (`~/.local/share`, etc.) | raw observations, candidates | nothing — ephemeral |
| 2. Project knowledge | repo `.aidoc/knowledge/learnings.md` | lessons verified against this tree (repo layouts, consumer quirks, version gotchas) | containers, machines, harnesses (in git) |
| 3. Universal knowledge | canon `.aidoc/knowledge/universal.md` | lessons with zero project-specific references | same, across all repos |

Rule of thumb: if you can delete every `file:line` from an entry and the lesson
survives, it is universal-candidate. `SELF_LEARNING.md` names the *process*
(capture → extract → consolidate → inject); this document names the *asset* and
its movement. The process fills the knowledge; it is not the knowledge.

## 3. Folder convention (pilot)

Every repo carries `.aidoc/knowledge/` (dot-space owned by agents, matching
`.agents/`). One file to start: `learnings.md`. Harness memory is the scratch
inbox, never the record. Declared per-repo in `AGENTS.md` ("Where state lives"
→ Lessons row) so the surface is never a shadow queue.

**[DISCUSS]** `.aidoc/knowledge/` vs `.aidoc/learning/`: `SELF_LEARNING.md`
declares `.aidoc/learning/` (piloted live since PR #783). This draft prefers
`knowledge/` — learning is the activity, knowledge the asset, and
`learning/learnings.md` stutters. Adopting `knowledge/` means amending
`SELF_LEARNING.md`'s File Locations table (explicit supersede, not silent
drift). Rename blast radius if adopted: `AGENTS.md` Lessons row, both
self-learn copies (`.agents/skills/` + `framework/skills/`), the
`learnings.md` contract header, and canon #131's title — plus the pilot
folder itself moves (second-opinion review 2026-09-29).

## 4. Entry format (with identity + provenance)

```markdown
## [K-001][workflow] Title
- **First seen**: YYYY-MM-DD · **Last seen**: YYYY-MM-DD · **Count**: N
- **Provenance**: learned-in `<repo>`, `<context>` (session/issue/PR)
- **Lesson**: What to do / avoid (no project literals at universal tier)
- **Evidence**: verified commands, run URLs, commit SHAs
- **Governance rule**: file §section, or omit if none yet
```

IDs (`K-001`…) are minted once, at promotion — never renumbered, so projects
reference instead of copy and duplicates are detectable. Dates use the system
clock; future-dated entries are defects.

## 5. Lifecycle (owned by the self-learn skill)

Qualify (2+ sessions, or a user correction, or a governance rule) → add / bump
`Count` + `Last seen` on recurrence → archive after 30+ days unobserved (never
delete) → graduate at count ≥ 5 to `framework/governance/DECISIONS.md` (the
spec-governance log, not `plans/DECISIONS.md`) or issues (project tier), or to
universal (cross-tier, §6). Single-occurrence candidates are logged, never
promoted. Mining EVAL/CI failures as consolidation candidates changes nothing
about EVAL itself (no schema, suite, or cycle edits): prose rules stay
reviewer-lens; only mechanically checkable predicates become linter emitters.

## 6. Cross-tier promotion (project → universal)

All three must hold:

1. Count ≥ 5 (existing bar).
2. Evidence reworded to remove project literals — promotion without rewording
   leaks one repo's paths into another's context, which is worse than no sharing.
3. Observed in a second project, or owner-reviewed.

Vehicle: `submit-feedback` to the canon tracker (search before filing; safe
body-file mechanics; read the write back). The canon curates `universal.md` by
PR like any other shared spec.

## 7. Distribution: fetch, don't vendor

`recall` / `start-session` gains one step: pull the universal log from the canon
(one `gh` read), prepend the entries that bear on the task (cap ~3KB, highest
count first). No submodules, no subtree maintenance, always fresh. Offline
fallback: the last fetched snapshot committed beside the skill config — clearly
marked with its fetch date, never edited by hand.

**[DISCUSS]** Is one network call per session acceptable overhead, or should the
fetch be cached per-day in harness scratch? Freshness vs latency tradeoff.

## 8. Responsibilities (no new skills)

- `self-learn`: capture / consolidate / promote within a repo; propose universal
  via `submit-feedback`.
- `recall`: retrieve project log + fetch universal log; return only what bears
  on the task.
- `memory-hygiene`: age-out, dedupe, store repair.
- Canon maintainers: curate `universal.md`; mint `K-` IDs at merge time.

## 9. Open questions for discussion

1. Folder name: `.aidoc/knowledge/` vs `.aidoc/learning/` (§3).
2. Fetch vs vendor for distribution (§7) — and the offline story.
3. Thresholds: is count ≥ 5 + second-project-or-review the right promotion bar,
   or too strict to ever fire?
4. Who may mint `K-` IDs outside the canon merge path (any promoter, or canon only)?
5. Does `universal.md` stay one file, or split per-topic at some size (e.g. 100 entries)?
6. Rollout order: pilot bakes here first (this repo's `.aidoc/learning/` is
   live in PR #783; `knowledge/` pending the §3 rename decision), then canon
   decision, then recall-fetch wiring — or wire recall against the pilot
   immediately?

## 10. Relation to existing material

- Aspirational inventory (not deployed machinery): no `session.post` /
  `learn-inject` hooks, no `trajectories/` files, no `universal.md` anywhere;
  `SELF_LEARNING.md`'s `docs/governance/*` paths do not exist. Read its diagram
  as intent.
- `SELF_LEARNING.md`: process spec; untouched except the File Locations table
  if §3 resolves to `knowledge/`.
- `aidoc-triage` §5, `AGENTS.md` read-back/watch rules, `ship-it` §1: existing
  repo-owned homes for the first three entries — the promotion targets §6
  describes, already proven.
- Canon repo `vladm3105/aidoc-flow-agents-config` (renamed; the old
  `aidoc-flow-claude-agents-config` name redirects): issues #114 (skill
  curation), #117 (triage skill), #131 (shared log proposal). #131 is the
  vehicle for the universal-home half of this draft. (Bare `#N` refs resolve
  in *this* repo to unrelated items — always qualify canon refs with the repo.)
