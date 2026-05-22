# Platform Parity

This document compares the two independent platform deliveries of the
AI Doc Flow framework — **Hermes** (MCP server) and the **Claude
Code plugin** — so users picking between them see the capability
shape on each side.

> Status: as of `v0.4.0` / `hermes/v0.1.0` /
> `claude-code-plugin/v0.1.0` (2026-05-20). Updates land when a
> platform ships a structurally different capability, not per-PR.

Both platforms pass the shared conformance suite at
[`../tests/conformance/`](../tests/conformance/) and consume the
framework specification at [`../framework/`](../framework/).

## Capability matrix — 8-layer SDD coverage

| # | Layer | Hermes | Plugin |
|---|-------|--------|--------|
| 1 | BRD | `sdd_*` tools (generic) | `doc-brd` + `-audit` + `-autopilot` + `-fixer` + `-reviewer` |
| 2 | PRD | `sdd_*` tools (generic) | `doc-prd` + 5 variants |
| 3 | EARS | `sdd_*` tools (generic) | `doc-ears` + 5 variants |
| 4 | BDD | `sdd_*` tools (generic) | `doc-bdd` + 5 variants |
| 5 | ADR | `sdd_*` tools (generic) | `doc-adr` + 5 variants |
| 6 | SPEC | `sdd_*` tools (generic) | `doc-spec` + 5 variants |
| 7 | **TDD** | `sdd_*` tools (generic) | **— gap.** Plugin reflects the legacy `tspec` model; no `doc-tdd` skill yet. See [Known parity gap](#known-parity-gap--sdd-layer-model). |
| 8 | **IPLAN** | `sdd_*` tools (generic) | **— gap.** Plugin has `doc-tasks` from the legacy 11-layer model; no `doc-iplan` skill yet. |

## Workflow operations

The two platforms expose their capability surface differently:

**Hermes — platform-wide MCP tools** (operate on any layer the client
specifies):

| Tool | Purpose |
|------|---------|
| `sdd_init` | Scaffold a project's `UCX/` directory |
| `sdd_validate` | Structural validation against the layer template |
| `sdd_validate_chg` | CHG artifact validation |
| `sdd_validate_links` | Cross-document link validation |
| `sdd_score_validate` / `sdd_score_show` / `sdd_score_compare` | Readiness scoring |
| `sdd_preflight` | Environment / input readiness |
| `sdd_consistency` | Cross-document traceability |
| `sdd_create` / `sdd_create_build` | Artifact authoring + template build |
| `sdd_review` | Review workflow |
| `sdd_scan` | Project scan |

**Plugin — per-layer skills** (each layer has its own skill bundle):

| Operation | Plugin skills (across 22 layer + helper families) |
|-----------|-----------------------------------------------:|
| Bare skill (authoring rules) | 22 |
| `-audit` | 21 |
| `-autopilot` | 22 |
| `-fixer` | 22 |
| `-reviewer` | 21 |
| `-validator` | 21 |

The 22 plugin skill families cover the 6-of-8 SDD layers above plus
SPEC-subtype skills (`doc-cspec`, `doc-dspec`, `doc-uxspec`,
`doc-riskspec`, `doc-procspec`), TSPEC-subtype skills (`doc-utest`,
`doc-itest`, `doc-stest`, `doc-ftest`, `doc-ptest`, `doc-sectest`),
plus orchestrators (`doc-flow`, `doc-naming`, `doc-validator`,
`doc-review`, `doc-ref`).

## Platform-specific extras

### Hermes-only

- **MCP-server runtime** — Hermes is a standalone server; integrates
  with any MCP-compatible client (Claude Code, custom).
- **Scaffold runtime** — `sdd_init` materializes `<project>/UCX/`
  with personas + prompts + layer templates copied from
  `framework/layers/`.
- **447-test pytest suite** — internal tests covering Hermes' own
  runtime behavior.
- **`agent-skills/` package** — `sdd-orchestrator` (180 files) +
  `sdd-review-personas` (1 file) ported from the user's branch via
  P2-T7; provides additional governance + reference content.
- **HTTP / stdio transport** — MCP-protocol-native transport per the
  upstream spec; works in both modes.

### Plugin-only

- **Auto-discovery** — Claude Code finds `skills/<name>/SKILL.md`,
  `agents/<name>.md`, `commands/<name>.md` without an explicit
  registration block in the manifest.
- **Slash-prefix invocation** — `/aidoc-flow:doc-brd-autopilot`,
  `/aidoc-flow:doc-flow`, etc.
- **AI Team subagent roster** (9 agents in `agents/`) — a specialist
  team mirroring the SDD lifecycle: `pm-orchestrator` (delegates via
  the `Task` tool) plus the spec lane (`requirements-analyst`,
  `solutions-architect`, `test-architect`), execution lane
  (`software-engineer`, `devops-release-engineer`), and read-only
  quality gates (`code-reviewer`, `security-engineer`,
  `traceability-auditor`). Subagents are a Claude Code construct;
  Hermes has no equivalent (it is the MCP tool-server such agents
  call). See `platforms/claude-code-plugin/agents/README.md`.
- **`save-plan`** slash command (in `commands/`) — captures the
  current conversation plan to a timestamped file.
- **Per-skill operation granularity** — the plugin user picks the
  exact operation (audit vs autopilot vs fixer vs reviewer vs
  validator) as a separate skill invocation; Hermes' generic tools
  dispatch based on inputs.

## Known parity gap — SDD layer model

The plugin's skill set was originally authored against an **older
11-layer model** (BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC,
TSPEC, TASKS) — not the framework's current **8-layer model** (BRD,
PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN). Specifically:

- **Plugin lacks** `doc-tdd` and `doc-iplan` skills (the new model's
  layers 7 and 8).
- **Plugin has** `doc-sys`, `doc-req`, `doc-ctr`, `doc-tspec`,
  `doc-tasks` — legacy-model artifacts that map ambiguously to the
  new model (`tspec` ≈ `tdd`? `tasks` ≈ `iplan`?).
- **~150 documentary references** in plugin skill bodies point at
  paths under `framework/<X>` for legacy-model concepts (e.g.
  `framework/scripts/`, `framework/11_TASKS/`, `framework/ADR/`)
  that don't exist in the current 8-layer framework layout.

Hermes was rewritten to the 8-layer model during P2-T9 (closed the
D-0013 architectural gap for its scaffold and validation runtime).
The plugin still reflects the legacy model in skill names,
frontmatter metadata, and the documentary references above.

**Resolution** is a per-skill content-migration task tracked as a
**post-v1.0 cleanup** (P3-T1 §Deferred R2). The skills work as
Claude Code artifacts — the references are documentation hygiene
rather than runtime correctness — but the layer-model mismatch is
real and surfaced here so users can plan around it.

## Choosing between Hermes and the plugin

| If you want... | Use |
|----------------|-----|
| An MCP server you can integrate with any MCP-compatible client | **Hermes** |
| Native Claude Code experience with slash-commands | **Plugin** |
| Per-operation skill granularity in your workflow | **Plugin** |
| Server-side validation as an HTTP / stdio service | **Hermes** |
| Today's 8-layer SDD model coverage end-to-end (incl. TDD + IPLAN) | **Hermes** |
| The widest per-layer audit / autopilot / fixer toolset | **Plugin** (8 layers + SPEC subtypes + TSPEC subtypes) |
| Internal pytest-style validation of the platform itself | **Hermes** (447 tests) |
| Documentation-first artifacts via skill bodies | **Plugin** (declarative SKILL.md per operation) |

Both platforms can coexist in the same project — they don't conflict
and don't share runtime code.
