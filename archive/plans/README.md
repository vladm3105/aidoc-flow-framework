# plans/

Working area for the **multi-platform migration** of this framework — plan
development, TODO audit, and progress tracking.

This is a *living* workspace, distinct from the published planning docs:

| File                         | Purpose                                              |
|-------------------------------|------------------------------------------------------|
| `ROADMAP.md` (repo root)      | Stable, published phase plan. Changes rarely.        |
| `plans/MIGRATION_TODO.md`     | Live task tracker — checked off as work lands.       |
| `plans/PLAN-TEMPLATE.md`      | Starting point for every task plan.                  |
| `plans/*.md` (ad hoc)         | Per-phase working notes, audits, decision scratchpads.|

## Conventions

- One row per task; check `[x]` only when committed **and** pushed.
- Keep task IDs (`P1-T3`, …) stable — they are referenced from commits.
- Every task plan ends with a `## Review log` of ≥2 ISO-stamped passes before
  it may be implemented (see `CLAUDE.md` § Development workflow).
- When a phase completes, snapshot its result in `CHANGELOG.md`, not here.
- `plans/` is retained through the Phase 5 cutover as the migration record.
