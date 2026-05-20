# P4-T4 Plan — Retrofits + parity report

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P4-T4                                |
| Depends on | P4-T1 design (Q4, Q5, Q6); P4-T0 audit §4 |
| Status     | DONE — 2026-05-21T03:10:00Z          |
| Feeds      | P4-T5 (verify + close)               |

## Objective

Ship five small artifacts per the P4-T1 design and P4-T0 deferred-
items roll-up:

1. `platforms/hermes/CHANGELOG.md` — Hermes `[0.1.0]` mirroring
   project `[0.3.0]` scoped to Hermes-specific content.
2. `platforms/claude-code-plugin/CHANGELOG.md` — plugin `[0.1.0]`
   mirroring project `[0.4.0]` scoped to plugin-specific content.
3. `platforms/hermes/README.md` expanded — full mirror of the P3-T3
   plugin README structure (~80 lines from the current 27-line
   placeholder).
4. `LICENSE` at repo root — MIT, copyright `vladm3105`.
5. `docs/PARITY.md` — feature-gap report between Hermes and the
   plugin.

Plus a small housekeeping item recommended by P4-T3 G15:
6. **Add a workflow-push-restriction note** to `docs/TAGGING.md`
   for symmetry with the existing tag-push restriction note.

## Audit refresh — parity finding (Pass 1 G1)

Recon during planning surfaced a real parity gap: the plugin's
`doc-*` skill set reflects the **legacy 11-layer model**
(BRD/PRD/EARS/BDD/ADR/SYS/REQ/CTR/SPEC/TSPEC/TASKS) while Hermes
was rewritten to the new 8-layer model (BRD/PRD/EARS/BDD/ADR/SPEC/
TDD/IPLAN) during P2-T9. Specifically:

- **Plugin lacks** `doc-tdd` and `doc-iplan` skills (layers 7-8 of
  the new framework model).
- **Plugin has** `doc-sys`, `doc-req`, `doc-ctr`, `doc-tspec`,
  `doc-tasks` (legacy-model artifacts that map ambiguously to the
  new 8-layer model — `tspec` ≈ `tdd`? `tasks` ≈ `iplan`?).

This is the P3-T1 §Deferred R2 issue resurfacing. Resolution is
post-Phase-3 content work (per-skill content migration), not P4
mechanical work. The parity report documents the gap honestly
without trying to fix it.

## Scope

**In:** the 6 artifacts listed above.

**Out:**

- Fixing the parity gap itself (content migration of plugin skills
  to the 8-layer model). That's a post-v1.0 task.
- Updates to `framework/` (no spec changes in P4).
- The CHANGELOG retrofit for Phase 4 changes themselves — Phase 4
  closes in P4-T5 with `[0.5.0]` at the project level; if any
  changes land in `platforms/<X>/` during P4-T5, that platform's
  next CHANGELOG entry is `[0.1.1]` and happens then. P4-T4's
  per-platform CHANGELOGs only cover the platform's first release
  (`[0.1.0]`).
- Phase 5 cutover documentation.

## Approach

### 1. `platforms/hermes/CHANGELOG.md`

Single `[0.1.0]` entry mirroring project `[0.3.0]` scoped to
Hermes-relevant content. Structure:

```markdown
# Hermes Platform Changelog

All notable changes to the Hermes MCP server platform are
documented here. Format based on [Keep a Changelog](https://...);
SemVer per [Semantic Versioning](https://...).

> Scope: this changelog tracks the **Hermes platform** at
> `platforms/hermes/`. For framework spec changes see
> [`../../framework/`](...); for project-level migration history
> see [`../../CHANGELOG.md`](...).

## [Unreleased]

## [0.1.0] — 2026-05-20

First independent release of the Hermes MCP server platform on the
multi-platform aidoc-flow-framework repository. Conforms to
`framework/v0.1.0`.

### Added
- Hermes MCP server platform structure ...
- `pyproject.toml` — `name = "hermes-server"`, `[project.scripts]
  hermes-mcp = "mcp_server.server:main_sync"` ...
- `VERSION` (`0.1.0`) and `FRAMEWORK_SPEC_VERSION` (`0.1.0`,
  matching `framework/VERSION`) ...
- The 447-test pytest suite at `tests/` ...

### Changed
- Rewired runtime to consume `framework/layers/<NN>_<X>/` per
  D-0013 — `CANONICAL_SCAFFOLD_MAPPINGS`, `_default_ssd_root`,
  `_default_repo_root`, `_resolve_canonical_template_root`.
- All `ucx_flow_v3` runtime coupling rewritten to `framework/`.

### Removed
- The 8 drifted layer template YAMLs from
  `agent-skills/.../sdd-orchestrator/templates/` per D-0013 ...
- 6 D-0013-obsolete sync files from the agent-skills package.

> Full migration audit trail at
> [`../../plans/P2-T0-PLAN.md`](...) through P2-T9.
```

### 2. `platforms/claude-code-plugin/CHANGELOG.md`

Same structure, scoped to plugin content from project `[0.4.0]`.

### 3. `platforms/hermes/README.md` (expansion)

Mirror the P3-T3 plugin README's 7-section structure:

1. One-paragraph "what this is"
2. **What's inside** table (Hermes' modules + test counts + agent-
   skills package counts)
3. **Install** — `pip install hermes-server` placeholder + `.mcp.json`
   config snippet
4. **Use** — invoking `hermes-mcp`; the MCP tools (sdd_init,
   sdd_validate, sdd_create, sdd_score_*, sdd_consistency, etc.)
5. **Framework spec conformance** — `cat VERSION` + `cat
   FRAMEWORK_SPEC_VERSION` snippet
6. **Platform info table**
7. **Relationship to the Claude Code plugin** — symmetric with
   plugin README's Hermes section

Target ~80 lines (vs current 27-line placeholder).

### 4. `LICENSE` at repo root

Standard MIT text:

```
MIT License

Copyright (c) 2026 vladm3105

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 5. `docs/PARITY.md`

Structure:

```markdown
# Platform Parity

This document compares the two independent platform deliveries of
the AI Doc Flow framework — Hermes (MCP server) and the Claude
Code plugin — so users picking between them see the capability
shape on each side.

> Status: as of `v0.4.0` / `hermes/v0.1.0` /
> `claude-code-plugin/v0.1.0`.

## Capability matrix — 8-layer SDD coverage

| Layer | Hermes (MCP tools) | Plugin (skills) |
|-------|---------------------|-----------------|
| 1 BRD | `sdd_*` (generic) | `doc-brd` + audit + autopilot + fixer + reviewer + validator |
| 2 PRD | `sdd_*` (generic) | `doc-prd` + audit + autopilot + fixer + reviewer + validator |
| 3 EARS | `sdd_*` (generic) | `doc-ears` + audit + autopilot + fixer + reviewer + validator |
| 4 BDD | `sdd_*` (generic) | `doc-bdd` + audit + autopilot + fixer + reviewer + validator |
| 5 ADR | `sdd_*` (generic) | `doc-adr` + audit + autopilot + fixer + reviewer + validator |
| 6 SPEC | `sdd_*` (generic) | `doc-spec` + audit + autopilot + fixer + reviewer + validator |
| 7 **TDD** | `sdd_*` (generic) | **— gap.** Plugin reflects the legacy `tspec` / `tasks` model; no `doc-tdd` skill yet. See "Known parity gap" below. |
| 8 **IPLAN** | `sdd_*` (generic) | **— gap.** No `doc-iplan` skill yet (plugin has `doc-tasks` from the legacy model). |

## Workflow operations

Hermes exposes **platform-wide MCP tools** that operate on any
layer:

- `sdd_init` — scaffold a project
- `sdd_validate` / `sdd_validate_chg` / `sdd_validate_links` —
  structural validation
- `sdd_score_validate` / `sdd_score_show` / `sdd_score_compare` —
  readiness scoring
- `sdd_preflight` — environment / input readiness
- `sdd_consistency` — cross-document traceability
- `sdd_create` / `sdd_create_build` — artifact authoring
- `sdd_review` — review workflow
- `sdd_scan` — project scan

The plugin's coverage is **per-layer skills**, each with a
consistent ~6-operation surface:

| Operation | Plugin coverage (across 22 skill families) |
|-----------|--------------------------------------------|
| Bare skill (authoring rules) | 22 |
| `-audit` | 21 |
| `-autopilot` | 22 |
| `-fixer` | 22 |
| `-reviewer` | 21 |
| `-validator` | 21 |

## Platform-specific extras

### Hermes-only
- MCP-server runtime — Hermes is a standalone server; integrates
  with any MCP client.
- Scaffold runtime — `sdd_init` materializes `<project>/UCX/`
  with skills + prompts + layer templates copied from
  `framework/layers/`.
- Pytest test suite — 447 internal tests covering Hermes' own
  runtime behaviour.
- `agent-skills/` package — `sdd-orchestrator` + `sdd-review-personas`
  (181 files; ported from the user's branch via P2-T7).
- Engine-name configuration — `mcp_server.server:main_sync` script
  entry; runs over stdio or HTTP per MCP spec.

### Plugin-only
- Auto-discovery — Claude Code finds `skills/<name>/SKILL.md`
  without an explicit registration block.
- Slash-prefix invocation — `/aidoc-flow:doc-brd-autopilot` etc.
- `requirements-analyst` subagent (in `agents/`).
- `save-plan` slash command (in `commands/`).
- Per-skill `-audit` / `-autopilot` / `-fixer` / `-reviewer` /
  `-validator` granularity — the plugin user picks the exact
  operation as a separate skill invocation rather than relying on
  the server's generic dispatcher.

## Known parity gap — SDD layer model

The plugin's skill set was originally authored against an older
**11-layer model** (BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC,
TSPEC, TASKS) — not the framework's current **8-layer model**
(BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN). Specifically:

- **Plugin lacks** `doc-tdd` and `doc-iplan` skills.
- **Plugin has** `doc-sys`, `doc-req`, `doc-ctr`, `doc-tspec`,
  `doc-tasks` — legacy-model artifacts that map ambiguously to
  the new model (`tspec` ≈ `tdd`? `tasks` ≈ `iplan`?).

Hermes was rewritten to the 8-layer model during P2-T9 (closed the
D-0013 gap for its scaffold and validation runtime). The plugin
still reflects the legacy model in skill names, frontmatter
metadata, and ~150 documentary references to layer paths that
don't exist under the current `framework/layers/`.

Resolution is a per-skill content-migration task tracked as a
**post-v1.0 cleanup** (P3-T1 §Deferred R2). The skills work as
Claude Code artifacts — the references are documentation hygiene
rather than runtime correctness — but the layer-model mismatch is
real and surfaced here so users can plan around it.

## Choosing between Hermes and the plugin

| If you want... | Use |
|----------------|-----|
| An MCP server you can integrate with any MCP client | Hermes |
| Native Claude Code experience with slash-commands | Plugin |
| Per-operation skill granularity in your workflow | Plugin |
| Server-side validation as a HTTP/stdio service | Hermes |
| Today's 8-layer SDD model coverage end-to-end | Hermes (covers all 8) |
| The widest per-layer audit / autopilot / fixer toolset | Plugin (8 layers + subtypes) |

Both platforms pass the shared conformance suite at
[`../tests/conformance/`](...) and consume the framework spec at
[`../framework/`](...).
```

### 6. `docs/TAGGING.md` workflow-push-restriction note

Append a short paragraph to the existing footnote (or open a new
section) noting that `.github/workflows/**` pushes have the same
in-container restriction as `refs/tags/*`. Plus a forward-pointer
to `plans/P4-T3-PLAN.md` Implementation note for the workaround
commands.

## Step sequence

1. **Hermes CHANGELOG.md** — write the new file (Step §1).
2. **Plugin CHANGELOG.md** — write the new file (Step §2).
3. **Hermes README.md** — expand from placeholder to populated
   (Step §3). Use Edit (file already exists).
4. **LICENSE** at repo root (Step §4).
5. **docs/PARITY.md** (Step §5).
6. **docs/TAGGING.md** workflow-push note (Step §6).
7. **Verify** (see below).
8. **Land** — single commit covering all 6 artifacts; update
   `plans/HANDOFF.md`; tick P4-T4 in `plans/MIGRATION_TODO.md`.
   Push.

## Verification

- **V1. All 6 artifacts present at expected paths:**
  - `platforms/hermes/CHANGELOG.md`
  - `platforms/claude-code-plugin/CHANGELOG.md`
  - `platforms/hermes/README.md` (still exists; expanded)
  - `LICENSE`
  - `docs/PARITY.md`
  - `docs/TAGGING.md` (still exists; appended note)
- **V2. Per-platform CHANGELOG content:**
  - Each has `## [Unreleased]` and `## [0.1.0] — 2026-05-20`
    sections.
  - Each scopes to its platform's content only (no cross-platform
    bleed).
  - Each cross-references the project-level CHANGELOG + relevant
    plan files.
- **V3. Hermes README expansion:**
  - `wc -l platforms/hermes/README.md` > 60 (up from 27).
  - No `PLACEHOLDER` strings.
  - Section 7 (relationship-to-plugin) present, mirroring P3-T3
    pattern.
- **V4. LICENSE:**
  - `head -1 LICENSE` reads `MIT License`.
  - Copyright line includes `vladm3105` and year `2026`.
  - Plugin manifest's `license` field still reads `"MIT"`
    (consistency).
- **V5. PARITY.md:**
  - Capability matrix (8 layers × 2 platforms) present.
  - Operations table present.
  - Platform-specific extras section present per platform.
  - Known parity gap section explicitly names the missing
    `doc-tdd` / `doc-iplan` and the legacy-vs-new layer model
    issue.
- **V6. TAGGING.md workflow note:**
  - `grep -c workflows` in `docs/TAGGING.md` returns ≥ 1.
- **V7. Conformance suite still 25 + 6 = 31 tests passing:**
  Sanity check; new docs shouldn't break tests.
- **V8. Hermes own pytest suite unaffected:** docs-only changes;
  expect 447 / 447 (no re-run required — the diff is non-test).
- **V9. No `framework/` or `platforms/<X>/src/` changes:**
  `git diff --stat HEAD -- framework/ platforms/hermes/src/
  platforms/claude-code-plugin/skills/` empty.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | The per-platform CHANGELOG mirrors project content verbatim, creating maintenance drift later. | Each per-platform CHANGELOG cross-references the project-level CHANGELOG for "full migration audit trail". Per-platform content is scoped to that platform's release; the project-level remains authoritative for cross-cutting changes. |
| R2 | The parity report becomes outdated as platforms diverge. | Header notes "Status: as of `v0.4.0` / `hermes/v0.1.0` / `claude-code-plugin/v0.1.0`". Future platform releases should update; if drift is non-trivial, a follow-up task refreshes. Not P4-T4's concern. |
| R3 | The legacy-vs-new layer model parity gap looks like a P4-T4 bug rather than a documented known issue. | "Known parity gap" section explicitly names it as deferred (P3-T1 §Deferred R2 → post-v1.0). The report is honest, not aspirational. |
| R4 | LICENSE choice (MIT) doesn't match a future commercial / dual-license intent the user may have. | P4-T1 Q6 selected MIT in line with the plugin manifest placeholder. Future relicense is a single LICENSE-file edit + manifest update — not Phase 4 work. |
| R5 | Hermes README expansion claims features not actually shipped. | Recon inventoried Hermes' actual tool surface (sdd_init, sdd_validate, sdd_create, etc. — from `tool_registry.py`). README only mentions verified-present tools. |
| R6 | The TAGGING.md workflow-push-restriction note duplicates the P4-T3 plan's documentation. | Per-document scope: TAGGING.md captures the cross-tag policy; P4-T3 plan captures the task-specific finding. Brief cross-reference, not duplication. |
| R7 | The parity matrix oversimplifies — Hermes' `sdd_validate` and the plugin's `-validator` skills behave differently. | The matrix shows coverage shape, not behavioural parity. The "Choosing between..." table is the user-facing summary; the matrix is the inventory. Behavioural parity is a Phase-5 user-acceptance concern. |

## Review log

### Pass 1 — 2026-05-21T02:45:00Z

- **G1. Parity finding — surface honestly.** Recon found the
  plugin's skill set reflects the legacy 11-layer model, not the
  new 8-layer. P4-T4's job is to *document* this, not fix it
  (per-skill content migration is post-v1.0). The "Known parity
  gap" section names it explicitly with a forward-pointer to
  P3-T1 §Deferred R2.
- **G2. Per-platform CHANGELOG retrofit posture (P4-T1 Q4).**
  Minimal-honest: each platform's `[0.1.0]` mirrors the project-
  level scoped content, with cross-references for the full audit
  trail. Avoids both the "stub-only" anti-pattern (broken-link
  drift) and the "re-derive from scratch" expense.
- **G3. Hermes README mirror.** Section structure matches P3-T3
  plugin README exactly; content sourced from `tool_registry.py`
  (real tool list) + Hermes pyproject (project name + script
  entry) + actual test counts.
- **G4. LICENSE consistency check.** Plugin manifest declares
  `"license": "MIT"`; the LICENSE file at repo root must say MIT.
  V4 enforces. If a future relicense happens, both files update
  together — not P4-T4's concern.
- **G5. PARITY.md asymmetry handling.** Hermes is platform-wide
  MCP tools; plugin is per-layer skills. Matrix presents both
  honestly without forcing them into the same shape.
- **G6. TAGGING.md workflow note (P4-T3 G15).** Documents the
  in-container restriction set symmetrically — tags + workflow
  files. Forward-pointer to the per-task plan's exact-commands
  section.
- **G7. Verify gates symmetric.** V1 enumerates the 6 artifacts;
  V2-V6 spot-check content per artifact; V7-V9 are sanity (suite
  green, no out-of-scope changes).
- **G8. Risk surface manageable.** Six artifacts, mostly content
  authoring against established patterns (P3-T3 README, project
  CHANGELOG). No code changes; no risk to the test suites.

### Pass 2 — 2026-05-21T03:00:00Z

- **G9. Parity-report layer count cross-check.** Plugin has 22
  `doc-<X>` bare skills total; 8 of them are the new-model
  primary layers (`brd`, `prd`, `ears`, `bdd`, `adr`, `spec` —
  that's 6, not 8; tdd + iplan missing). Confirmed by recon:
  `ls platforms/claude-code-plugin/skills/ | grep -E '^doc-[a-z]+$'`
  returned 22 entries, of which 6 match the new framework
  layers. The PARITY matrix table reflects this honestly.
- **G10. CHANGELOG `[Unreleased]` placeholder.** Each per-platform
  CHANGELOG opens with `## [Unreleased]` (empty) above `[0.1.0]` —
  symmetric with the project-level CHANGELOG. Forward-looking
  entries land in Unreleased; releases get cut as a new section.
- **G11. CHANGELOG date.** Both per-platform `[0.1.0]` entries
  use date `2026-05-20` (the day Hermes + plugin first releases
  happened, per their tags `hermes/v0.1.0` at commit `20c061d`
  / `claude-code-plugin/v0.1.0` at commit `087f7d5`). Not the
  P4-T4 commit date (which is `2026-05-21`).
- **G12. PARITY.md is curated, not exhaustive.** Target ~150
  lines (vs the comprehensive 22-skill × 5-op = 110-cell matrix
  that would result from full enumeration). Header sets
  "as of <version>" expectation; updates are user-acceptance-
  driven, not per-PR.
- **G13. No new findings on Approach / Step sequence /
  Verification.** Plan is internally consistent. Ready to present
  on approval.

## Implementation note (2026-05-21T03:10:00Z)

Executed. All 9 verify gates green; no implementation-time findings.

- **V1 artifacts:** all 6 present at expected paths.
- **V2 CHANGELOGs:** each has `[Unreleased]` + `[0.1.0] — 2026-05-20`;
  scoped content; cross-references to project-level and per-task
  plans.
- **V3 Hermes README:** 113 lines (up from 27); 0 PLACEHOLDER
  strings; 2 references to "Claude Code plugin" (Relationship +
  Choosing section pointer).
- **V4 LICENSE:** MIT, `Copyright (c) 2026 vladm3105`; plugin
  manifest's `"license": "MIT"` matches.
- **V5 PARITY.md sections:** 5 H2 sections (capability matrix,
  workflow operations, platform-specific extras, known parity
  gap, choosing between).
- **V6 TAGGING.md workflow note:** new "In-container push
  restrictions" section with the two-row table (tags + workflows)
  and the per-phase plan cross-references.
- **V7 conformance:** 31/31 tests still pass (docs-only changes
  don't affect tests).
- **V9 scope discipline:** zero changes under `framework/`,
  `platforms/hermes/src/`, `platforms/hermes/tests/`,
  `platforms/claude-code-plugin/skills/`.

Parity report surfaced the legacy-vs-new layer model gap honestly:
plugin lacks `doc-tdd` + `doc-iplan`; has `doc-sys` / `doc-req` /
`doc-ctr` / `doc-tspec` / `doc-tasks` from the legacy 11-layer
model. Hermes covers all 8 new-model layers via its generic
`sdd_*` tools. Resolution deferred to post-v1.0 per
P3-T1 §Deferred R2.
