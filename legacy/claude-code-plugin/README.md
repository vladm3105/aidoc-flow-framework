# Parked Claude Code plugin skills (legacy — review later)

Skills moved out of the shipped plugin surface
(`platforms/claude-code-plugin/skills/`) and parked here pending review.
Anything under this directory is **not discovered or shipped** by the plugin
(Claude Code auto-loads only `skills/<name>/SKILL.md`).

**No skills are currently parked.** History:

| Skill | Parked | Reason | Status |
|-------|--------|--------|--------|
| `project-mngt` | 2026-05-22 | MVP/MMP/MMR planning methodology skill; not SDD-layer-specific (uses domain-generic `REQ-NN` IDs). Pulled from the plugin to be re-evaluated for fit/placement. | **Retired 2026-05-27** — out of v1 scope; overlaps `adr-roadmap`/`doc-iplan`; candidate for a post-v1.0 domain profile. See `plans/DECISIONS.md` (D-0017 resolution). Recoverable from git history + `legacy-ucx-v3.2-read-only`. |

## Reviewing a parked skill

To bring one back, move its directory to
`platforms/claude-code-plugin/skills/<name>/`, set
`development_status: active` in its `SKILL.md` frontmatter, restore the inbound
references that were neutralized when it was parked, and re-run the conformance
suite. See `plans/DECISIONS.md` (D-0017) and `plans/MIGRATION_TODO.md` for the
park record.
