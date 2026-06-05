---
name: doc-iplan
description: Create an Implementation Plan (IPLAN) - Layer 8 of the SDD flow, the mandatory execution bridge from SPEC/TDD to source code via an executable, session-resumable file manifest. Use when ready to implement a SPEC component.
metadata:
  tags:
    - sdd-workflow
    - layer-8-artifact
  custom_fields:
    layer: 8
    artifact_type: IPLAN
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD]
    downstream_artifacts: [CODE]
    version: "0.4.4"
    framework_spec_version: "0.11.3"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-iplan

## Purpose

Create an **Implementation Plan (IPLAN)** — Layer 8 of the SDD flow. An IPLAN
bridges SPEC + TDD to source code: declares test-first file order (inherited
from TDD), executable bash commands, session progress for stateless executors,
and an audit trail from spec to delivered files.

**Layer**: 8 (final doc layer; downstream is Code).
**Upstream**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD.

One IPLAN per SPEC component (matching its TDD). Bugfixes with no new
functionality use a temporary plan in `docs/08_IPLAN/tmp/` instead.

## When to Use

Use `doc-iplan` when:

- Layers 1–7 exist and the source TDD has reached IPLAN-Ready ≥ 90/100.
- You are ready to bridge a SPEC/TDD component into source code.
- You need an executable, session-resumable plan for stateless coding agents.

For end-to-end generation from a SPEC/TDD, a prompt, or an existing IPLAN, use
`../doc-iplan-autopilot/SKILL.md`.

## Prerequisites

Before writing, read:

1. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`
2. **Index template:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml`
3. **Layer README:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/README.md`
4. **ID & tag standards:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
5. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`

Read the upstream **TDD** (primary source for the file manifest and test-first
order) and the **SPEC** it derives from. Reference only documents that exist;
never invent placeholders like `IPLAN-XXX` or `TBD`. Confirm no ID collision:
`ls docs/08_IPLAN/ 2>/dev/null`.

## Layer Guidance

### Permanent vs Temporary plans (decide first)

| | Permanent IPLAN (`IPLAN-NN_{slug}.yaml`) | Temporary IPLAN (`tmp/TMP-IPLAN-*.yaml`) |
|---|---|---|
| **Purpose** | Implement a SPEC component via TDD test cases | Bugfix, correction, investigation — no new functionality |
| **Requires TDD** | Yes — one IPLAN per SPEC/TDD | No — standalone |
| **Registered in index?** | Yes — `IPLAN-00_index.yaml` | No |
| **Triggers audit trail?** | Yes — code inventory, session log | No — disposable |
| **Deleted when?** | Never — historical record (use ABANDONED) | Within 7 days of DONE/ABANDONED |
| **Naming** | `IPLAN-NN_{slug}.yaml` (NN sequential, never reused) | `TMP-IPLAN-YYYY-MM-DD_{slug}.yaml` |

**Rule of thumb:** implements a TDD test contract → permanent; restores intended
behavior or fixes a bug → temporary.

### Required structure (6 sections)

The IPLAN is a YAML document with `metadata` (`document_type: iplan-document`,
`layer: 8`) followed by six sections matching `IPLAN-TEMPLATE.yaml`:

1. **Document Control** — `iplan_id` (`IPLAN-NN`), `source_spec`
   (`@spec: SPEC-NN`), status (`Draft | In Progress | Completed`), version,
   dates, author, `complexity` (1=1 file, 5=architectural), `estimated_files`,
   `session_count`.
2. **File Manifest** — declared creation order, **tests before implementation**
   (TDD principle); each file carries `order`, `status`, `session`, `verified`.
3. **Execution Commands** — runnable bash for `setup`, `implementation`, and
   `validation` (the actual bridge to code).
4. **Implementation Contracts** — Protocol interfaces, exception hierarchies,
   state machines, data models, DI interfaces live *inside* the IPLAN. Required
   only when 3+ files share interfaces; otherwise state "No implementation
   contracts".
5. **Session Handoff** — the stateless-executor bridge; `sessions[]` with
   `partial_work`, `blockers`, `next_session_directive`, `validation_results`.
6. **Traceability** — cumulative upstream tags, downstream `code_paths` /
   `test_paths`, and `code_inventory` (audit trail of every file
   created/modified with session attribution and `verified` status).

### Session handoff protocol

Each stateless session: 1) read `session_handoff.sessions` for the last
state → 2) find the next `NOT_STARTED`/`PARTIAL` file in `file_manifest` →
3) read `partial_work` if resuming → 4) continue, do **not** regenerate
completed work → 5) update file status → 6) append a session with a
`next_session_directive`. Markers: `NOT_STARTED | IN_PROGRESS | DONE | PARTIAL`.

### Document ID and tags

- **IPLAN is a DOCUMENT-level artifact** — referenced in dash form `IPLAN-NN`
  (e.g. `@iplan: IPLAN-01`). There is **no** hierarchical dotted element ID for
  an IPLAN; never write `IPLAN.NN.SS.xxxx`.
- IPLAN is Layer 8, so it carries the full cumulative chain of upstream tags
  that genuinely exist: `@brd @prd @ears @bdd @adr @spec @tdd`. Hierarchical
  upstreams use the dotted form (`@tdd: TDD.01.04.a3c1`); document-level
  upstreams use dash form (`@spec: SPEC-01`, `@adr: ADR-03`).
- **Removed patterns** (do not use): `TASK-XXX`, `TODO-XXX`, `TI-XXX`,
  `ITEM-XXX`, and any `IPLAN.NN.SS.xxxx` hierarchical ID.

## Creation Process

1. **Determine type** — permanent vs temporary (table above).
2. **Reserve ID** — next free `IPLAN-NN` (two digits, sequential, never reused);
   the ID typically matches its SPEC/TDD component.
3. **Create the file** — permanent: `docs/08_IPLAN/IPLAN-NN_{slug}.yaml`;
   temporary: `docs/08_IPLAN/tmp/TMP-IPLAN-YYYY-MM-DD_{slug}.yaml`.
4. **Document Control first**, then complete all 6 sections from the template.
5. **Declare the file manifest** test-first, every file `status: NOT_STARTED`.
6. **Write execution commands** (`setup` / `implementation` / `validation`).
7. **Define implementation contracts** if 3+ files share interfaces; else state
   "No implementation contracts".
8. **Seed session handoff** so the first executor has a clear
   `next_session_directive`; add an empty `code_inventory`.
9. **Register in the index** (permanent only) — add to
   `docs/08_IPLAN/IPLAN-00_index.yaml` and update `metadata.total_plans`.
10. **Validate** (below) and commit the IPLAN and index together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] `metadata.layer: 8`, `document_type: iplan-document`.
- [ ] Document Control complete (`iplan_id`, `source_spec`, status, dates).
- [ ] All 6 sections present and non-empty.
- [ ] File Manifest lists tests before implementation; each file has a status
      marker and `verified` flag.
- [ ] Execution commands cover setup / implementation / validation.
- [ ] Implementation Contracts declared (or "No implementation contracts").
- [ ] Session Handoff seeded with a `next_session_directive`.
- [ ] Upstream tags (`@brd @prd @ears @bdd @adr @spec @tdd`) reference existing
      docs; document ID is `IPLAN-NN` (no dotted IPLAN element ID).
- [ ] `code_inventory` ready to record created/modified files.
- [ ] Permanent plan registered in `IPLAN-00_index.yaml`; temporary under `tmp/`.

**Error codes** (all severity `error`): `XDOC-006` tag format invalid · `XDOC-008` broken internal link · `XDOC-009` missing traceability section.

**Quality gate (blocking):** CODE-Ready score ≥ 90/100 with 0 Tier-1 errors
before implementation begins. If issues are found, fix and re-check; if
unfixable, log for manual review.

## Next Skill

IPLAN is the last documentation layer. Proceed to **Code**: execute the file
manifest test-first, updating `status`/`verified`, `session_handoff`, and
`code_inventory` so any later stateless session can resume.

## Adaptation

Read `.aidoc/profile.yaml`; honor only this skill's knobs
(`section_toggles`, `glossary`). Ignore unknown keys; absent a profile, use
framework defaults. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml`
- Layer README: `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/README.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Quality gate: `../doc-iplan-audit/SKILL.md` · Fixes: `../doc-iplan-fixer/SKILL.md`
- Generation pipeline: `../doc-iplan-autopilot/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Bridge a SPEC/TDD component into source code |
| **Layer** | 8 (final doc layer; downstream = Code) |
| **Upstream tags** | `@brd @prd @ears @bdd @adr @spec @tdd` |
| **Key decision** | Permanent vs Temporary |
| **Document ID** | `IPLAN-NN` (dash form; no dotted element ID) |
| **Six sections** | doc_control · file_manifest · execution_commands · implementation_contracts · session_handoff · traceability |
| **Handoff markers** | NOT_STARTED · IN_PROGRESS · DONE · PARTIAL |
| **Next** | Code (implementation) |
