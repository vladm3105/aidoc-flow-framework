# Platform Parity

This document compares the two independent platform deliveries of the
AI Doc Flow framework — **Hermes** (MCP server) and the **Claude
Code plugin** — so users picking between them see the capability
shape on each side.

> Status: as of `v1.0.0` / `hermes/v0.1.1` /
> `claude-code-plugin/v0.1.0` (2026-05-22; plugin layer-model
> migration PLM-B1 landed). Updates land when a platform ships a
> structurally different capability, not per-PR.

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
| 7 | **TDD** | `sdd_*` tools (generic) | `doc-tdd` + `-audit` + `-autopilot` + `-fixer` + `-reviewer` + `-validator` |
| 8 | **IPLAN** | `sdd_*` tools (generic) | `doc-iplan` + 5 variants |

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

| Operation | Plugin skills (across 19 layer + subtype families) |
|-----------|-----------------------------------------------:|
| Bare skill (authoring rules) | 14 |
| `-audit` | 19 |
| `-autopilot` | 19 |
| `-fixer` | 19 |
| `-reviewer` | 18 |
| `-validator` | 18 |

The 19 plugin layer/subtype families cover **all 8** SDD layers above
plus SPEC-subtype skills (`doc-cspec`, `doc-dspec`, `doc-uxspec`,
`doc-riskspec`, `doc-procspec`) and test-subtype skills (`doc-utest`,
`doc-itest`, `doc-stest`, `doc-ftest`, `doc-ptest`, `doc-sectest`),
plus orchestrators (`doc-flow`, `doc-naming`, `doc-validator`,
`doc-review`, `doc-ref`). (Plugin skill count 142 → 125 after PLM-B1
retired the legacy SYS/REQ/CTR families.)

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

## Known parity gap — SDD layer model (migration in progress)

The plugin's skill set was originally authored against the **legacy
12-layer model** (BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC,
TSPEC, TASKS, Code) — not the framework's current **8-layer model**
(BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN). The mismatch is
pervasive — legacy layer numbers, element-code scheme, upstream
chains, `ai_dev_ssd_flow/` paths, and dead validation-script
references run through most skill bodies. Hermes was rewritten to the
8-layer model during P2-T9; the plugin is being migrated under task
**PLM** (`plans/PLM-PLAN.md`), staged and conformance-gated by
`tests/conformance/platforms/plm_lint.py`.

**Done (PLM-B1):**

- **Layers 7 & 8 now exist** — `doc-tspec*` → `doc-tdd*` and
  `doc-tasks*` → `doc-iplan*`, fully rewritten to the framework's
  `07_TDD` / `08_IPLAN` contracts (TDD is a single unified template,
  no subtypes; IPLAN carries the file-manifest / session-handoff
  model).
- **Legacy layers retired** — `doc-sys`, `doc-req`, `doc-ctr` removed
  (no home in the 8-layer model; their concerns fold into EARS / ADR
  / SPEC). Plugin skill count 142 → 125.
- **Orchestrators + agents realigned** — `doc-flow`,
  `skill-recommender`, `project-init`, and the agent roster now route
  the 8-layer flow only.

**Remaining (PLM-B2…B7):** the other layer families (`doc-brd`,
`doc-prd`, `doc-ears`, `doc-bdd`, `doc-adr`, `doc-spec`), the SPEC-
and test-subtype families, and the residual helpers still carry
legacy-model bodies (~108 skill files). Tracked per-batch in
`plans/MIGRATION_TODO.md`; the gap section is removed once
`plm_lint --all` is clean (PLM-B7). **Open decision** before B4/B5:
the fate of the SPEC-subtype (`doc-cspec/dspec/uxspec/riskspec/procspec`)
and test-subtype (`doc-utest/itest/stest/ftest/ptest/sectest`)
families, which have no single-template backing in the 8-layer model.

## Choosing between Hermes and the plugin

| If you want... | Use |
|----------------|-----|
| An MCP server you can integrate with any MCP-compatible client | **Hermes** |
| Native Claude Code experience with slash-commands | **Plugin** |
| Per-operation skill granularity in your workflow | **Plugin** |
| Server-side validation as an HTTP / stdio service | **Hermes** |
| Fully 8-layer-clean SDD coverage end-to-end today | **Hermes** (plugin mid-migration — PLM; layers 7–8 + orchestrators done) |
| The widest per-layer audit / autopilot / fixer toolset | **Plugin** (8 layers + SPEC subtypes + test subtypes) |
| Internal pytest-style validation of the platform itself | **Hermes** (447 tests) |
| Documentation-first artifacts via skill bodies | **Plugin** (declarative SKILL.md per operation) |

Both platforms can coexist in the same project — they don't conflict
and don't share runtime code.
