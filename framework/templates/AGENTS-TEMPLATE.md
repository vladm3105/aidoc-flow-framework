# AGENTS.md — working agreement for AI coding agents on <project-name>

Orients any AI agent (Claude Code, Codex, Gemini CLI, Cursor, Copilot, or custom)
working on this repo. This file is the single working agreement.

## What this repo is

This project is built and maintained under the Specification-Driven Development (SDD)
framework (`aidoc-flow-framework`). Architectural intent, specifications, tests, and
governance artifacts flow through formal layers under `docs/sdd/`.

Project customization and adaptation settings live in `.aidoc/profile.yaml`.

## Where state lives (this repo owns its own continuity)

| Surface | Path | Status |
|---|---|---|
| Decisions (Architecture) | `docs/sdd/05_ADR/` (Layer 05) | Structured YAML records; `docs/DECISIONS.md` is a retired anti-pattern (GD-78) |
| Decisions (Change) | `docs/sdd/09_CHG/` (Layer 09) | Authored in Section 1B of authorizing Change Requests (`CHG-*.yaml`) |
| Changelog | GitHub Releases + `docs/sdd/09_CHG/archive/` | Structured change requests serve as change records; `CHANGELOG.md` is retired / not adopted |
| Roadmap | GitHub Milestones / Issues + `plans/*-PLAN.md` | Feature planning lives in verified plans and milestones; `ROADMAP.md` is retired / not adopted |
| Session Continuity | GitHub Issues + `plans/*-PLAN.md` | Live handoff lives on the active issue; `docs/HANDOFF.md` is retired / not adopted |
| Lessons Learned | `.aidoc/learning/learnings.md` | Consolidated, PR-reviewed system of record; harness memory is scratch, never the record |

## Project Tiers

Files in this repository adhere to the four standard tiers:
1. `seed/` — Stakeholder vision, domain boundaries, and architectural options.
2. `docs/` — Structured SDD specifications (`docs/sdd/01_BRD` through `docs/sdd/10_EVAL`) and modules.
3. `.aidoc/` — Project profile (`.aidoc/profile.yaml`), framework link, and project overrides (`.aidoc/project/`).
4. `logs/` — Ephemeral run logs and tool internals (gitignored).

## Non-negotiables

- **Never create monolithic anti-pattern files:** Do not generate or update loose `CHANGELOG.md`, `ROADMAP.md`, `DECISIONS.md`, or `docs/HANDOFF.md`. Record all state in the sanctioned surfaces declared in the table above.
- **Specification-First:** No code implementation without an authorizing Change Request (`CHG-NN.yaml`) and Implementation Plan (`IPLAN-NN.yaml`). Architectural changes require an ADR under `docs/sdd/05_ADR/`.
- **One task, one worktree:** Feature and defect work runs in a dedicated git worktree and branch (`feature/<issue-or-chg>-<slug>`), never on `main` or `dev`.
- **Submit only verified work:** Run linters (`.aidoc/bin/sdd-lint` or `PYTHONPATH=.aidoc/framework python3 -m sdd_doc_lint`) and local test suites before opening or updating a PR.
