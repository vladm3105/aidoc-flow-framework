# CLAUDE.md — Project Memory

Persistent context for the **multi-platform migration** of the AI Doc Flow
Framework. Auto-loaded every session. Keep it short and current.

## What this project is

Delivering the document-flow framework as **one engine-agnostic specification
(`framework/`) with two independent platforms**:

- **Platform A — Hermes AI** — MCP-server engine (`platforms/hermes/`).
- **Platform B — Claude Code plugin** — native Claude Code engine, no MCP
  (`platforms/claude-code-plugin/`).

The platforms share the `framework/` spec and nothing else.

## Current state

- **Working branch:** `claude/multi-platform-migration-AamWB` — all work goes
  here. `main` is locked; never push to it without explicit permission.
- **Phase:** Phase 1 — Framework Spec Extraction (Phase 0 complete; Phase 1
  Step 0 legacy isolation complete).
- The repo is mid-restructure — root holds the new project; the frozen
  pre-migration project lives under `legacy/`.

## Rules

- **Legacy is frozen.** `legacy/` is read-only history. **Copy** content out of
  it and adapt — never move or edit files in place. `legacy/` is removed at the
  Phase 5 cutover.
- **Never push to `main`.** Only the working branch above.
- Legacy CI is disabled (parked in `legacy/github-workflows-disabled/`).

## Development workflow

Every change follows this flow:

1. **Plan.** Write the plan into `plans/` before touching code — start from
   `plans/PLAN-TEMPLATE.md`.
2. **Review — pass 1.** Re-read the plan for gaps, missing cases, and likely
   bugs. Record findings as a timestamped entry in the plan's `## Review log`.
3. **Harden, then review again.** Fix every issue found, then do a *second*
   review pass and record it as another `## Review log` entry (findings, or an
   explicit "no new findings"). Repeat until a pass finds nothing. A plan is
   **not ready** to present, hand off, or implement until its `## Review log`
   shows **at least two** ISO-stamped passes — never present a plan or call
   `ExitPlanMode` before then.
4. **Implement.** Execute the plan. Update the plan file with progress and
   state/status as you go — stamp every update with an ISO 8601 timestamp
   (`YYYY-MM-DDThh:mm:ssZ`).
5. **Verify.** Run the applicable validators / conformance checks. Nothing is
   "done" until they pass.
6. **Land.** One logical change per commit, with a conventional prefix
   (`docs:`, `refactor:`, `chore:`, `fix:`, `feat:`). On every commit/push,
   update `CHANGELOG.md` and `ROADMAP.md` as needed, and tick
   `plans/MIGRATION_TODO.md`.

Record every non-obvious choice in `plans/DECISIONS.md` (ISO-stamped) so the
rationale survives across sessions.

Hooks may be added to automate the mechanical parts (timestamping, syncing the
tracker / changelog / roadmap). Keep judgment-based steps (planning, review)
manual.

## Session handoff

Sessions run in ephemeral containers — preserve continuity in the repo:

- Maintain `plans/HANDOFF.md` — current progress, achievements, next steps,
  open questions. Refresh it at meaningful milestones.
- **Before any context compaction**, write/refresh the handoff record and
  update `CHANGELOG.md` so no progress is lost.
- Start each session by reading `plans/HANDOFF.md`.

## Definition of done

A task is done only when: code/docs changed, **committed and pushed**, plan
status updated with an ISO timestamp, `CHANGELOG.md` / `ROADMAP.md` synced, and
applicable validators/conformance checks pass. Only then tick `[x]` in
`plans/MIGRATION_TODO.md`.

## Where things are

- `ROADMAP.md` — stable phased plan (Phase 0 → cutover v1.0.0).
- `plans/MIGRATION_TODO.md` — **live task tracker**; update it as work lands
  (check `[x]` only when committed + pushed).
- `plans/README.md` — migration workspace conventions.
- `plans/HANDOFF.md` — session continuity: progress, achievements, next steps.
- `plans/DECISIONS.md` — log of non-obvious decisions and their rationale.
- `.claude/hooks/` — automation: pre-compact snapshot, session-start handoff.
- `docs/PROJECT.md` — versioning, branching, conformance, change management.
- `docs/REPO_STRUCTURE.md` — target layout + `legacy/` → target mapping.

## Environment

Ephemeral cloud container, re-cloned each session. **Only committed + pushed
work survives.** Commit messages must not contain model identifiers.
