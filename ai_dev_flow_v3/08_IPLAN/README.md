# 08_IPLAN — Implementation Plan

## C4 Model Position

IPLAN is part of the **Implementation Bridge** (L7-L8, no C4 level). It is the execution bridge between TDD and source code. C4-L4 (Code) diagrams belong to the source code layer, not to IPLAN documents.

## Purpose

Mandatory execution layer bridging TDD (L7) to source code. One IPLAN per TDD component. Each IPLAN declares the file creation order (test-first from TDD), provides executable bash commands, tracks session progress across stateless MCP executor calls, and maintains an audit trail from specification to delivered files.

## Permanent vs Temporary Plans

| | Permanent IPLAN (`IPLAN-NN_{slug}.yaml`) | Temporary IPLAN (`tmp/TMP-IPLAN-*.yaml`) |
|---|---|---|
| **Purpose** | Implement a SPEC component via TDD test cases | Bugfix, correction, investigation — no new functionality |
| **Requires TDD** | Yes — one IPLAN per TDD | No — standalone |
| **Registered in index?** | Yes — `IPLAN-00_index.yaml` | No |
| **Triggers audit trail?** | Yes — code inventory, session log | No — disposable |
| **Deleted when?** | Never — historical record (use ABANDONED) | Within 7 days of DONE/ABANDONED |
| **Naming** | `IPLAN-NN_{slug}.yaml` (NN sequential, never reused) | `TMP-IPLAN-YYYY-MM-DD_{slug}.yaml` |

**Rule of thumb**: Does the work implement a TDD test contract? → permanent. Does it restore intended behavior or fix a bug? → temporary.

## Design Decisions

- **Mandatory layer** — one IPLAN per TDD/SPEC component, created when TDD reaches IPLAN-Ready >=90/100.
- **Test-first file order** — file_manifest declares test files before implementation files (TDD principle inherited from L7).
- **Session handoff protocol** — solves the stateless MCP executor problem: each session reads the previous session's state, identifies the next incomplete step, and continues without regenerating completed work.
- **Implementation contracts embedded** — Type interfaces, exception hierarchies, and state machines live in the IPLAN (no separate contract files).
- **Code inventory for audit trail** — every file created/modified is recorded with session attribution and verification status.
- **Temporary plans** for bugfixes only — no TDD upstream, disposable, live in `tmp/`.

## What's Different from TASKS v2

| TASKS v2 (475 lines, 16 sections) | IPLAN v3.2 (~100 lines, 6 sections) |
|---|---|
| Pre-check: 10-layer upstream chain verification | 3-layer upstream: TDD + SPEC + ADR |
| Development Plan Tracking with pre/post gates | File manifest with status markers only |
| Business value, scope, objective narratives | SPEC already covers these |
| 4-phase breakdown pattern | File-by-file creation order (test-first) |
| Unit Test Results section (populated after) | validation_results per session in handoff log |
| Full glossary | Not needed — lean execution |
| No temporary plan concept | `tmp/` for bugfix plans |

## Session Handoff Protocol

Each AI agent session reads the IPLAN in this order:

1. **Read session_handoff.sessions** — identify the last session's state
2. **Check file_manifest.files** — find next NOT_STARTED or PARTIAL file
3. **Read partial_work** description if resuming a PARTIAL step
4. **Continue from that point** — do NOT regenerate completed work
5. **Update file status** after completion or session end
6. **Append to session_handoff.sessions** with next_session_directive

## Template

See [IPLAN-TEMPLATE.yaml](IPLAN-TEMPLATE.yaml).

## Registry

For the authoritative plan registry (statuses, execution path, deferred items, cross-plan obligations, status history), see [IPLAN-00_index.yaml](IPLAN-00_index.yaml).
