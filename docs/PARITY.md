# Platform Parity

This document compares the two independent platform deliveries of the
AI Doc Flow framework — **Hermes** (MCP server) and the **Claude
Code plugin** — so users picking between them see the capability
shape on each side.

> Status: as of project `v1.1.0` / `hermes/v0.1.1` /
> `claude-code-plugin/v0.2.0` (2026-05-24; both platforms on the
> 8-layer model; plugin skill set is the canonical **54** — the P3-T6
> base plus the CHG family + `gate-check` + `project-adopt` (P3-T7) and
> `project-profile` + `knowledge-extractor` (ADAPT)). Updates land when
> a platform ships a structurally different capability, not per-PR.

Both platforms pass the shared conformance suite at
[`../tests/conformance/`](../tests/conformance/) and consume the
framework specification at [`../framework/`](../framework/).

## Capability matrix — 8-layer SDD coverage

| # | Layer | Hermes | Plugin |
|---|-------|--------|--------|
| 1 | BRD | `sdd_*` tools (generic) | `doc-brd` + `-autopilot` + `-audit` + `-fixer` |
| 2 | PRD | `sdd_*` tools (generic) | `doc-prd` + 3 variants |
| 3 | EARS | `sdd_*` tools (generic) | `doc-ears` + 3 variants |
| 4 | BDD | `sdd_*` tools (generic) | `doc-bdd` + 3 variants |
| 5 | ADR | `sdd_*` tools (generic) | `doc-adr` + 3 variants |
| 6 | SPEC | `sdd_*` tools (generic) | `doc-spec` + 3 variants |
| 7 | **TDD** | `sdd_*` tools (generic) | `doc-tdd` + 3 variants |
| 8 | **IPLAN** | `sdd_*` tools (generic) | `doc-iplan` + 3 variants |

Each plugin layer ships 4 skills: the base authoring skill plus `-autopilot`,
`-audit`, and `-fixer`.

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

**Plugin — per-layer skills** (each of the 8 layers ships a 4-skill bundle):

| Operation | Plugin skills |
|-----------|--------------:|
| Bare skill (authoring rules) | 8 |
| `-autopilot` | 8 |
| `-audit` | 8 |
| `-fixer` | 8 |

The 8 layer families (`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}`) cover all 8
SDD layers, plus the `doc-chg` change-management family (4 variants — the CHG
governance overlay) and 18 utility skills (`doc-flow`, `doc-naming`, `doc-ref`,
`doc-review`, `doc-validator`, `project-init`, `project-adopt`, `project-profile`,
`gate-check`, `trace-check`, `charts-flow`, `adr-roadmap`, `context-analyzer`,
`quality-advisor`, `skill-recommender`, `workflow-optimizer`, `security-audit`,
`knowledge-extractor`) — **54 skills** total. The `-reviewer` and `-validator`
variants were merged into `-audit`; the former SPEC-subtype and test-type
families were folded into the unified SPEC (L6) and TDD (L7) skills (task P3-T6,
reversing D-0015). `project-profile` + `knowledge-extractor` were added in ADAPT
(D-0019). The CHG family, `gate-check`, and `project-adopt` were added in P3-T7 (see
`plans/P3-T6-PLAN.md`, `plans/P3-T7-PLAN.md`).

## Change management — GATE-SPEC (CHG-D1, both platforms)

Both platforms implement the **GATE-SPEC** framework-spec change gate from the
shared spec (D-0020), with the same three-way enforcer split:

| Half | Plugin | Hermes |
|------|--------|--------|
| Record-level checks (E001–E004) | `gate-check` + `doc-chg` family (skills) | `validation/chg_rules.py` (server-side) |
| Diff-aware checks (E005, E008) | `tests/chg/spec_gate.py` via the staged CI workflow | same shared script in CI |
| Static checks (E006, E007) | shared conformance suite | shared conformance suite |
| Human approval (E004 sign-off) | branch protection on `framework/**` | branch protection on `framework/**` |

## Review / remediation / gate triggers (both platforms)

Both platforms implement the spec's review→remediation→gate loop and its
trigger points (`framework/governance/REVIEW_REMEDIATION_FLOW.md`). Each binds
the engine-agnostic points to its own capabilities; *how* a point is checked is
the platform's choice (the spec only requires that findings, the readiness score,
and the remediation path are surfaced).

| Trigger point | Plugin | Hermes |
|---------------|--------|--------|
| `on_author` (write-time) | `PostToolUse` hook (`hooks/sdd-doc-review.sh`) — advisory nudge to `doc-<layer>-audit` + best-effort `sdd_doc_lint` findings | server-side `validation/` + scoring tool on demand |
| `on_gate_fail` | `doc-<layer>-fixer` skill | `UCRem_*` remediation prompts |
| `pre_promotion` | `gate-check` / the readiness ≥90 gate before the next `doc-<layer>` | scoring gate before the next layer |
| `pre_merge` (PR-time) | `doc-review.yml` running `tools/sdd_doc_lint` (blocking, deterministic) | same `doc-review.yml` shared check |

The **write-time** point is advisory (a nudge, never blocks the edit); the
**PR-time** point is the blocking deterministic gate. The full semantic
readiness *score* stays the LLM `-audit` skill / Hermes scorer — `sdd_doc_lint`
is the fast structural subset beneath it.

## Review team (multi-persona review)

Both platforms run the engine-agnostic **review-team** model
(`framework/governance/REVIEW_TEAM.md` + `REVIEW_CREWS.yaml`): a per-layer crew of
persona-lenses + a synthesizer over a shared blackboard, producing one **unified
review report** (advisory weighted/capped readiness score, coverage, the
deterministic gate, and reduced findings).

| Concern | Plugin | Hermes |
|---------|--------|--------|
| Crew runtime | `Task` subagents (`review-team` skill; lenses incl. `adversary`, `synthesizer`) | `saga_orchestrator` per-persona executor branches |
| Blackboard | git-ignored `.aidoc/review/<artifact-id>/<persona>.json` slots | saga journal + branch summaries |
| Persona names | framework names natively (`adversary`, `synthesizer`) | runtime names (`chaos_engineer`, `chairperson`) + alias map |
| Reduce / score | `synthesizer` subagent (rule-driven) | `saga_reducer` + `review_scoring.py` (code) |
| Resilience | partial-crew → coverage; below quorum → low-confidence (D-0005: blackboard, no saga) | saga retries/compensation; degrade above quorum, escalate below |
| Report | unified report (`UCR_OUTPUT_UNIFIED` / audit report) | `PERSONA_REVIEW_REPORT` / saga summary |

Both bind to the **same** crew map, persona-output contract, scoring/gate policy,
and report shape — so a BRD reviewed by either gets the same lenses and a
structurally identical report.

### Parity proof

- **Deterministic (CI):** `tests/conformance/test_review_report_parity.py` validates
  committed sample report fixtures from **both** runners
  (`tests/conformance/fixtures/review/{hermes,plugin}_BRD-01_report.json`) against the
  shared `review_report.schema.json`, and asserts they share the report structure plus
  the deterministic-gate invariant (`passed == structural_pass AND no_blocking`).
- **Manual (live run):** the end-to-end "same artifact → identical report" check is
  manual, since live LLM output is not CI-deterministic. Procedure:
  1. Pick one artifact (e.g. a real `BRD-01`).
  2. Run it through the plugin review-team (`review-team` at a gate) and through the
     Hermes saga review.
  3. Normalise each output to the unified report shape; validate both against
     `review_report.schema.json` (both must pass).
  4. Confirm structural identity (same keys, coverage shape, gate fields) and that
     the high-severity findings substantively overlap. Record the run.

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
  exact operation (autopilot vs audit vs fixer) as a separate skill
  invocation; Hermes' generic tools dispatch based on inputs.

## SDD layer model — both platforms aligned

Both platforms now implement the framework's **8-layer model**
(BRD·PRD·EARS·BDD·ADR·SPEC·TDD·IPLAN → Code). Hermes was rewritten to
it during P2-T9; the Claude Code plugin's skill corpus — originally
authored against the legacy 12-layer model (…SYS, REQ, CTR, SPEC,
TSPEC, TASKS…) — was migrated under task **PLM** (`plans/PLM-PLAN.md`):
`doc-tspec*`→`doc-tdd*`, `doc-tasks*`→`doc-iplan*`, the SYS/REQ/CTR
families retired, and all layer numbers, element IDs (now 4-segment
`TYPE.NN.SS.xxxx`), paths, and traceability chains realigned. The
plugin's former SPEC-subtype and test-type families were subsequently
folded into the unified SPEC (L6) and TDD (L7) skills, and the corpus
pruned and recreated to a canonical **46 skills** (task P3-T6,
reversing D-0015). Conformance test
`tests/conformance/platforms/test_plm_lint.py` enforces that the plugin
carries no legacy-model fingerprints, so the alignment cannot regress.

## Choosing between Hermes and the plugin

| If you want... | Use |
|----------------|-----|
| An MCP server you can integrate with any MCP-compatible client | **Hermes** |
| Native Claude Code experience with slash-commands | **Plugin** |
| Per-operation skill granularity in your workflow | **Plugin** |
| Server-side validation as an HTTP / stdio service | **Hermes** |
| The widest per-layer audit / autopilot / fixer toolset | **Plugin** (8 layers × base/autopilot/audit/fixer) |
| Internal pytest-style validation of the platform itself | **Hermes** (447 tests) |
| Documentation-first artifacts via skill bodies | **Plugin** (declarative SKILL.md per operation) |

Both platforms can coexist in the same project — they don't conflict
and don't share runtime code.
