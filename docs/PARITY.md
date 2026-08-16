# Platform Parity

This document compares the two independent platform deliveries of the
AI Doc Flow framework — **Hermes** (MCP server) and the **Claude
Code plugin** — so users picking between them see the capability
shape on each side.

> Status: as of project `v1.1.0` / `hermes/v0.12.1` /
> `claude-code-plugin/v0.25.0` (framework spec `0.41.0`; both platforms on the
> 8-layer model; plugin skill set is the canonical 52 = 32 layer-family + 4 CHG + 14 utilities + 2 deprecated redirect stubs (`doc-review`, `trace-check`, scheduled for removal in `v1.0.0`)). Updates land when a platform ships a structurally different
> capability, not per-PR.

Both platforms pass the shared conformance suite at
[`../tests/conformance/`](../tests/conformance/) and consume the
framework specification at [`../framework/`](../framework/).

## Parity contract — lifecycle-behavior parity (not just output-shape)

The framework spec defines **lifecycle-behavior parity** between the two
platforms: both expose the same observable saga lifecycle (state machine,
transition table, journal schema, break-circuit policy) over the
create→review→revise loop, while keeping their own runtime mechanisms
(Hermes: Python saga runtime; plugin: SKILL prompts + JSON journal + Bash
subprocesses). The contract lives in
[`../framework/governance/REVIEW_SAGA.md`](../framework/governance/REVIEW_SAGA.md)
(arriving in the `0.13.0` spec cycle via SAGA-PARITY-001, D-0031, which
extends D-0005's blackboard contract with an outer-loop journal).

Earlier states of this document described **output-shape parity** —
"both produce schema-conformant unified reports." That terminal-state
parity remains (enforced by
[`../tests/conformance/test_review_report_parity.py`](../tests/conformance/test_review_report_parity.py)),
but it is now one component of the broader lifecycle-behavior parity
contract.

**Enforcement parity — all 8 layers (plugin v0.21.0+).** On the
**autopilot-dispatched path**, both platforms enforce the state machine
**preemptively for every layer**: Hermes via its Python saga runtime
(`saga_orchestrator.py`); the plugin via the `tools/saga_driver.py` script
vendored into the bundle, now invoked by **all 8 layer autopilots**
(`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-autopilot`) plus the CHG family
as thin entry points — completed by SAGA-PARITY-001 **Phase 4**
(the `0.21.0` plugin cycle, 2026-06-22). The driver's `can_transition`
raises on invalid transitions and owns the saga.json journal directly.
(Background: plugin v0.6.0's cooperative-enforcement attempt empirically
failed in the 2026-06-05 live BRD verification — invalid transitions,
non-terminal final status, no subprocess dispatch — motivating the v0.6.1
pivot to preemptive enforcement, which Phase 4 then propagated from BRD to
the remaining 7 layers.)

**Residual (base-skill draft path).** The correction above is scoped to the
autopilot path. Seven of the eight *base* skills (`doc-{prd,ears,bdd,adr,
spec,tdd,iplan}/SKILL.md`) were slimmed to zero saga prose by Phase 4, but
**`doc-brd/SKILL.md` remains the lone residual** — its `## Draft mode
(saga-driven)` still instructs the LLM to cooperatively append a branch
transition to `saga.json` when one exists (`:183-190`), guarded by the
standalone-invocation skip. Audit/fixer skills likewise do not invoke the
driver. So "preemptive for every layer" holds for the dispatched run-scope
machine, not for every skill path.

Note a scope difference the two runtimes keep: the plugin's driver is an
**outer, wall-clock-bounded, multi-iteration** create→review→revise loop
(soft deadline → `PARTIAL_TIMEOUT` break-circuit, cross-invocation resume,
`quality_loop_max_iterations`). Hermes's review saga is **single-pass by
default**, but since HERMES-REVIEW-LOOP-001 Phase 1 (the `0.11.0` Hermes
cycle, D-0063) `sdd_review` also offers an **opt-in `quality_loop`** — a bounded
review→remediate→re-review loop that reads the same
`quality_loop_max_iterations` cap, enforces a `SOFT_DEADLINE_SECONDS`
wall-clock bound, and *writes* `PARTIAL_TIMEOUT` on the final failing gate.
It sequences fresh forward saga runs (no cross-invocation resume yet — G-R1
is Phase 2), and functions only on the LLM crew-review path (a numeric
score is required; off it the loop degrades to a single pass). The
default (`quality_loop` off) remains a single-pass fan-out/fan-in of one
existing document. Both defaults are conformant: `REVIEW_SAGA.md:150-154`
accepts an orchestrator that ignores the break-circuit and records its last
checkpoint state (not `PARTIAL_TIMEOUT`) as a valid graceful degradation.
Hermes's default reaches a legal terminal by a different but
equally-conformant path — an orderly quorum-based escalation (branch
timeout → `BRANCH_FAILED` → `ESCALATED`). The plugin's *cross-invocation
resume* machinery (G-R1) is still deferred until Hermes's loop gains Phase 2
(D-0050 → D-0063).

Conformance tests check the observable artifact (saga.json shape + state
machine + break-circuit policy greppable invariants), not the enforcement
mechanism — both preemptive and cooperative implementations are
compliant if they produce schema-conformant journals with valid
transitions.

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
governance overlay) and 14 utility skills (`doc-flow`, `doc-naming`, `doc-ref`,
`doc-validator`, `review-team`, `project-init`, `project-adopt`,
`project-profile`, `knowledge-extractor`, `gate-check`, `charts-flow`,
`adr-roadmap`, `quality-advisor`, `security-audit`) — 52 (50 active + 2 deprecated)
skills total. The `-reviewer` and `-validator` variants were
merged into `-audit`; the former SPEC-subtype and test-type families were
folded into the unified SPEC (L6) and TDD (L7) skills (task P3-T6, reversing
D-0015). `project-profile` + `knowledge-extractor` were added in ADAPT
(D-0019). The CHG family, `gate-check`, and `project-adopt` were added in
P3-T7. In plugin `v0.4.0`, `skill-recommender`, `workflow-optimizer`, and
`context-analyzer` were folded into `doc-flow` (hard-deleted); `doc-review`
and `trace-check` were folded into `doc-validator` and retained as deprecated
redirect stubs (scheduled for removal in `v0.6.0`). See
`plans/P3-T6-PLAN.md`, `plans/P3-T7-PLAN.md`, and
`platforms/claude-code-plugin/CHANGELOG.md`.

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

**Artifact-body delivery to the lens (D-0051, hermes 0.7.0).** The two platforms
deliver the artifact under review to the lens differently: the plugin lens is agentic
and **reads the on-disk file** (via the artifact path in its brief); the Hermes lens
is an API completion, so the review prompt now **inlines** the document body
(`## Document to Review`, from the per-persona `included_sections`) directly into the
prompt. Before `v0.7.0`, Hermes inlined *no* body — the API-path review was
content-blind (it scored metadata only); D-0051 closed that gap.

**Author-self-claim de-anchor — both mechanisms (GD-05).** The `REVIEW_TEAM.md`
strip MUST is now satisfied on **both** platforms, by the mechanism each engine's
architecture allows (GD-05, framework `0.33.0`): **Hermes curates the lens input**, so
it **physically removes** the score before the lens sees it (D-0051); the **plugin lens
reads the artifact directly**, so it **disregards** the score by an explicit brief
instruction (the constrained fallback — it cannot physically strip). The plugin
instruction was added across the 9 `doc-*-audit` + 9 `doc-*-fixer` SKILLs + `review-team`

+ `traceability-auditor` (H-14 / D-0052, plugin `v0.23.1`).

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
| Crew runtime | `Task` subagents (`review-team` skill; lenses incl. `chaos_engineer`, `security_engineer`, `synthesizer`) | `saga_orchestrator` per-persona executor branches |
| Blackboard | git-ignored `.aidoc/review/<artifact-id>/<persona>.json` slots | saga journal + branch summaries |
| Persona names | framework names natively (`chaos_engineer`, `security_engineer`, `synthesizer`, …) | framework names natively (`chaos_engineer`, `security_engineer`, …); single remaining alias `chairperson` → `synthesizer` |
| Reduce / score | `synthesizer` subagent (rule-driven) | `saga_reducer` + `review_scoring.py` (code) |
| Saga lifecycle (D-0031 / `0.13.0` spec cycle) | `saga.json` written at `.aidoc/review/<NN>_<LAYER>/<id>/saga.json`; same state machine + journal schema as Hermes. **All 8 layers (plugin v0.21.0+)**: preemptive enforcement via `tools/saga_driver.py` invoked by every `doc-<layer>-autopilot` (SAGA-PARITY-001 Phase 4). Outer wall-clock-bounded, multi-iteration loop. | Python saga runtime (`saga_orchestrator.py`, `saga_models.py`, `saga_journal.py`); preemptive enforcement; single-pass by default, **opt-in bounded multi-iteration loop** via `sdd_review quality_loop` (HERMES-REVIEW-LOOP-001 Phase 1, `v0.11.0`) |
| Resilience — partial crew | blackboard slots + coverage/quorum (D-0005 blackboard, authoritative for crew state) + saga.json journal for outer-loop phase state (D-0031) | saga retries/compensation; degrade above quorum, escalate below |
| Resilience — partial outer loop | `saga.json` PARTIAL_TIMEOUT state via break-circuit; next invocation resumes from checkpoint | **default single-pass**: state machine **accepts** `PARTIAL_TIMEOUT` but the default path doesn't write it. **`quality_loop` opt-in (`v0.11.0`, D-0063)**: *writes* `PARTIAL_TIMEOUT` on the final failing gate + enforces `SOFT_DEADLINE_SECONDS`; each iteration is a fresh forward run — cross-invocation resume (G-R1) is Phase 2 |
| Report | unified report (`UCR_OUTPUT_UNIFIED` / audit report) | `PERSONA_REVIEW_REPORT` / saga summary |
| Layer Playbooks (all 8 layers) | ✅ active — 45 playbooks (BRD 5 / PRD 6 / EARS 5 / BDD 6 / ADR 6 / SPEC 5 / TDD 6 / IPLAN 6) | ✅ **all 8 lifecycle layers active** (HERMES-PARITY-PHASE-2/3, hermes 0.4.0/0.5.0): saga branches inject `framework/playbooks/<NN>_<LAYER>/<lens>.md`, enforce the `check:` citation floor (discard uncited), emit `verdict.playbook_coverage`. **CHG: crew-map parity** (`persona_mappings.yaml`); a live/sanctioned CHG *saga* review (schema `09_CHG` + dispatch) is a follow-on |

Both bind to the **same** crew map, persona-output contract, scoring/gate
policy, saga state machine, and report shape — so a BRD reviewed by either
exposes the same observable lifecycle (states + transitions + journal
shape) and produces a structurally identical report.

### Parity proof — two layers

Lifecycle-behavior parity is enforced at two layers; both must pass on CI.

+ **Output-shape (terminal-state) parity:**
  `tests/conformance/test_review_report_parity.py` validates committed
  sample report fixtures from **both** runners
  (`tests/conformance/fixtures/review/{hermes,plugin}_BRD-01_report.json`)
  against the shared `review_report.schema.json`, and asserts they share
  the report structure plus the deterministic-gate invariant
  (`passed == structural_pass AND no_blocking`).
+ **Saga-lifecycle parity (added by SAGA-PARITY-001, D-0031):**
  `tests/conformance/test_saga_lifecycle_parity.py` validates committed
  sample saga journals from both runners
  (`tests/conformance/fixtures/saga/{hermes,plugin}_BRD-01_saga.json`)
  against the shared `framework/governance/saga.schema.json`, and asserts
  **both** platforms' `_ALLOWED_TRANSITIONS` equal the `REVIEW_SAGA.md`
  transition table exactly — including the `PARTIAL_TIMEOUT` break-circuit
  state. **`SagaRealJournalConformance` (H-12, D-0048)** additionally
  validates a **real** Hermes journal — driven through the actual journal
  functions for a lifecycle layer, the `--layer`-omitted default path, and
  a CHG run (`layer: 09_CHG`) — not just a hand-authored fixture, so the
  Hermes journal-conformance claim is now enforced against real output. (The `## Break-circuit policy` SKILL-prose is a separate
  plugin-side concern — it lives in the ~18 `doc-*-audit` / `doc-*-fixer`
  skills, not the autopilots — and is not asserted by this parity test.)
+ **Manual end-to-end (live run):** the "same artifact → identical
  lifecycle and report" check is manual, since live LLM output is not
  CI-deterministic. Procedure:
  1. Pick one artifact (e.g. a real `BRD-01`).
  2. Run it through the plugin review-team (`review-team` at a gate)
     and through the Hermes saga review.
  3. Validate both saga journals against `saga.schema.json` AND both
     unified reports against `review_report.schema.json`.
  4. Confirm same observable terminal state (`CLOSED` or `ESCALATED`)
     and that the high-severity findings substantively overlap. Record
     the run.

## Platform-specific extras

### Hermes-only

+ **MCP-server runtime** — Hermes is a standalone server; integrates
  with any MCP-compatible client (Claude Code, custom).
+ **Scaffold runtime** — `sdd_init` materializes `<project>/UCX/`
  with personas + prompts + layer templates copied from
  `framework/layers/`.
+ **447-test pytest suite** — internal tests covering Hermes' own
  runtime behavior.
+ **`agent-skills/` package** — `sdd-orchestrator` (180 files) +
  `sdd-review-personas` (1 file) ported from the user's branch via
  P2-T7; provides additional governance + reference content.
+ **HTTP / stdio transport** — MCP-protocol-native transport per the
  upstream spec; works in both modes.

### Plugin-only

+ **Auto-discovery** — Claude Code finds `skills/<name>/SKILL.md`,
  `agents/<name>.md`, `commands/<name>.md` without an explicit
  registration block in the manifest.
+ **Slash-prefix invocation** — `/aidoc-flow:doc-brd-autopilot`,
  `/aidoc-flow:doc-flow`, etc.
+ **AI Team subagent roster** (11 agents in `agents/` — 9 lifecycle + 2 review lenses) — a specialist
  team mirroring the SDD lifecycle: `pm-orchestrator` (delegates via
  the `Task` tool) plus the spec lane (`requirements-analyst`,
  `solutions-architect`, `test-architect`), execution lane
  (`software-engineer`, `devops-release-engineer`), and read-only
  quality gates (`code-reviewer`, `security-engineer`,
  `traceability-auditor`). Subagents are a Claude Code construct;
  Hermes has no equivalent (it is the MCP tool-server such agents
  call). See `platforms/claude-code-plugin/docs/AGENTS.md`.
+ **`save-plan`** slash command (in `commands/`) — captures the
  current conversation plan to a timestamped file.
+ **Per-skill operation granularity** — the plugin user picks the
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
pruned and recreated to the P3-T6 46-skill baseline (reversing D-0015),
then extended and consolidated to the current canonical 52-skill release
(50 active + 2 deprecated stubs) described above. Conformance test
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
