# LAYER-PLAYBOOKS-001 — Per-Layer Lens Playbooks (Design)

**Status:** design approved by user during brainstorming session (2026-06-07)
**Next:** implementation plan via `writing-plans` skill → `plans/LAYER-PLAYBOOKS-001-PLAN.md`
**Authority:** framework/governance/REVIEW_TEAM.md (to be extended)

## Problem statement

The framework spec layer-specializes review lenses by **name** (`business_analyst` at BRD, `product_owner` at PRD, `requirements_specialist` at EARS — three lenses with distinct reasoning modes and distinct weights). The plugin's lens→agent map collapses these into a small set of generic agents (e.g., one `requirements-analyst` agent serves all three). Result: layer-specific failure modes are reasoned about by a generic agent without a layer-specific failure-mode catalog. Live BRD review missed altitude-leak issues the human spotted post-hoc; PRD review missed CE-3 redirect-lookup-deadline coupling (subtle but real). The audit team is doing its job *generically* but not *layer-specifically*.

Adding per-layer agent files (~40 agent definitions) is the wrong fix — it duplicates procedural skill (output protocol, JSON schema discipline, evidence-citation discipline) across files, and every framework change requires N edits. The right fix is to keep generic agents (procedural skill) and inject per-layer **playbooks** (the lens's layer-specific failure-mode catalog and reasoning frame) into the lens subagent's brief at fan-out time.

## Decisions (the design surface)

| # | Decision | Choice | Rationale |
|---|---|---|---|
| 1 | Where playbooks live | **Engine-agnostic.** Contract in `framework/governance/REVIEW_TEAM.md` (new §Playbooks); files at `framework/playbooks/<NN>_<LAYER>/<lens>.md` | Lens names live in framework; their reasoning catalogs belong at the same layer. Plugin loads from framework path. Hermes can adopt immediately when it implements team-mode. |
| 2 | Granularity | **Per-lens** (not per-agent) | Preserves the framework's lens distinction. PRD's `architect` (weight 25) and `tech_lead` (weight 20) lenses both map to `solutions-architect` agent but reason at distinct altitudes — they get distinct playbooks. |
| 3 | Initial PR scope | **All layers in one PR** (mechanism + 45 playbooks) | Adheres to "submit only finalized work" rule (no post-merge backfill PR). Larger PR but no fragmentation. Live cascade on BRD or PRD validates mechanism. |
| 4 | Injection mechanism | **Audit SKILL inlines playbook content** into the per-lens Task brief | Deterministic; auditable; subagent never touches filesystem. Adds one Read per lens at fan-out time. Other options (path-by-reference, subagent auto-load) push complexity into every generic agent. |
| 5 | Content shape | **Hybrid** (principle frame + deterministic checklist + beyond-checklist escape hatch) | Determinism floor (checklist findings are reproducible) + judgment ceiling (principle frame catches what checklist misses). Findings cite which check fired — auditable. |

## Architecture

```
┌─ framework/governance/REVIEW_TEAM.md ─────────────────────────┐
│ §Playbooks (new section)                                       │
│   - file location convention                                   │
│   - required frontmatter schema (yaml)                         │
│   - content sections (frame / checks / beyond / scoring)       │
│   - finding citation rule: every finding cites check id OR     │
│     "beyond-checklist:<principle>"                             │
└────────────────────────────────────────────────────────────────┘
              │
              │ defines contract for ↓
              ▼
┌─ framework/playbooks/<NN>_<LAYER>/<lens>.md (×45 files) ──────┐
│ ---                                                            │
│ layer: 02_PRD                                                  │
│ lens: chaos_engineer                                           │
│ weight: 8                                                      │
│ agent: chaos-engineer                                          │
│ framework_spec_version: "0.14.0"                               │
│ ---                                                            │
│ # Reasoning frame (the WHY — 2-3 paragraphs)                   │
│ # Required evidence checks (C1..Cn) — deterministic floor      │
│ # Beyond-checklist (principle-driven escape hatch)             │
│ # Scoring rubric (0-100 mapping)                               │
└────────────────────────────────────────────────────────────────┘
              │
              │ loaded by ↓
              ▼
┌─ platforms/claude-code-plugin/skills/doc-<layer>-audit/SKILL.md
│ team-mode fan-out (existing PRD-RT-001 / BRD-RT-001 pattern):  │
│   for each lens in REVIEW_CREWS[layer]:                        │
│     1. resolve playbook_path =                                 │
│        ${CLAUDE_PLUGIN_ROOT}/../../framework/playbooks/        │
│        <NN_LAYER>/<lens>.md                                    │
│     2. Read playbook content                                   │
│     3. compose Task brief with playbook inlined under          │
│        "## Layer-specific playbook" section                    │
│     4. dispatch Task subagent (existing agent file)            │
└────────────────────────────────────────────────────────────────┘
              │
              │ subagent writes ↓
              ▼
┌─ .aidoc/review/<NN>_<LAYER>/<art>/<lens>.json ────────────────┐
│ persona-output record. findings[].check is a NEW required     │
│ field. Schema:                                                 │
│   findings: [{                                                 │
│     id: "CE-1",                                                │
│     priority: "P2",                                            │
│     check: "C1"     ← cites which checklist check fired       │
│       OR                                                       │
│     check: "beyond-checklist:degraded-mode-asymmetry"          │
│     ...                                                        │
│   }]                                                           │
└────────────────────────────────────────────────────────────────┘
              │
              │ consumed by ↓
              ▼
┌─ synthesizer agent / verdict.json ────────────────────────────┐
│ - findings without a check field: DISCARDED (with narrative   │
│   note in report.md)                                           │
│ - fabricated check id (not in playbook): DISCARDED            │
│ - beyond-checklist findings: accepted, grouped separately     │
│ verdict.json gains:                                            │
│   playbook_coverage: {                                         │
│     C1: <count>, C2: <count>, ..., beyond_checklist: <n>      │
│   }                                                            │
│ report.md surfaces "checks that didn't fire" as confidence    │
│ signal.                                                        │
└────────────────────────────────────────────────────────────────┘
```

## Playbook content shape

Each `framework/playbooks/<NN>_<LAYER>/<lens>.md` file follows this shape (target ~150 lines):

```markdown
---
layer: 02_PRD
lens: chaos_engineer
weight: 8
agent: chaos-engineer
framework_spec_version: "0.14.0"
---
# chaos_engineer lens — PRD layer

## Reasoning frame (the WHY)

[2-3 paragraphs: what this lens uniquely sees at this layer altitude,
how it differs from the same lens at adjacent layers (e.g., chaos_engineer
at SPEC vs at PRD), what the lens does NOT do that other lenses cover.]

## Required evidence checks (the deterministic floor)

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — §13 risk row symmetry.** Every §13 risk row must have:
  (a) a §10 user-facing surface (error message / response),
  (b) a §11 launch-gate or technical AC,
  (c) a §12 assumption or constraint anchor.
Missing any → P2 finding citing C1.

**C2 — Bounded degraded mode.** Every degraded-mode prose statement
includes a bound (numeric or explicitly ADR-deferred). Unbounded
prose ("slow", "unreachable") without a deferral marker → P2 citing C2.

**C3 — Failure-branch gating.** Every §11 control AC also verifies the
control's failure mode (not just happy-path presence). Missing → P2 citing C3.

[... C4..Cn, layer-specific, finite, deterministically applicable]

## Beyond-checklist (the WHEN)

If you find a layer-specific failure mode the checklist doesn't cover,
raise it as a P2/P3 finding citing "beyond-checklist:<principle-tag>"
and state the principle from the reasoning frame above that motivates
it. These findings count toward the lens score but are flagged
separately in the persona-output record. Use sparingly: if you find
yourself raising more beyond-checklist than checklist findings,
the playbook needs revision (file a follow-up).

## Scoring (0-100)

[Rubric explaining how to derive lens_score from the count + priority
of findings. Tied to checklist coverage + beyond-checklist density.
Example:
  100: no findings, every check ran clean
   90-99: some P3 findings, no checklist holes
   80-89: 1-2 P2 findings against checks, no P1
   70-79: 3+ P2 findings against checks or 1 P1
   <70: P0 finding present or systemic checklist failure
]
```

## Error handling

| Edge case | Behavior |
|---|---|
| Playbook file missing for a (layer, lens) pair | Audit SKILL detects on Read, writes `BRANCH_FAILED` for that lens with reason `"playbook missing: framework/playbooks/<layer>/<lens>.md"`. Other lenses continue. Coverage quorum logic (existing) decides if quorum still met. Never silently downgrade to playbook-less prompt. |
| Playbook frontmatter malformed | Audit SKILL validates frontmatter before brief composition. Malformed → `BRANCH_FAILED` with reason `"playbook frontmatter invalid: <yaml error>"`. Same quorum semantics. |
| Lens subagent returns finding with no `check` field | Synthesizer treats finding as **out-of-scope** and discards. Logged in synthesizer narrative ("3 findings discarded — no playbook check citation"). |
| Lens subagent returns finding with fabricated `check` id (not in playbook) | Discarded; narrative tag `"finding cited unknown check <id>"`. |
| Lens subagent returns finding with `check: "beyond-checklist:<principle>"` | Accepted; principle is free-form text. Synthesizer groups separately. Coverage stats track ratio of checklist vs beyond-checklist findings — drift signal. |
| Crew member added to REVIEW_CREWS.yaml without authoring playbook | Conformance test fails CI. Caught pre-merge. |
| Playbook bumped during in-flight saga | Saga is forward-only; next iteration reads current playbook. Acceptable because PARTIAL_TIMEOUT resume is the only multi-version path. |
| Brief size blow-up (45 × 150 lines inlined could add ~6KB per lens brief) | Acceptable. Existing briefs pass ~10KB artifact text. Well under context limits. |
| Cross-layer reasoning in a finding | Out of scope for this PR. Each lens stays within its layer. |

## Testing strategy

| Layer | Test | What it verifies |
|---|---|---|
| Conformance | `tests/conformance/test_playbook_coverage.py` (new) | Every `(layer, lens)` in `framework/governance/REVIEW_CREWS.yaml` has a corresponding `framework/playbooks/<layer>/<lens>.md` file |
| Conformance | extend `tests/conformance/test_framework_spec_version.py` | Every playbook's `framework_spec_version` matches `framework/VERSION` |
| Conformance | `tests/conformance/test_playbook_frontmatter.py` (new) | Each playbook has required frontmatter fields, YAML parses, lens weight matches REVIEW_CREWS.yaml |
| Lint | extend `scripts/sync-version-refs.sh` | Mechanical propagation of `framework_spec_version` into all 45 playbook frontmatters when `framework/VERSION` bumps |
| Unit | `tests/unit/test_playbook_loader.py` (new) | Audit SKILL's playbook-loading helper resolves the correct path, handles missing-file case with documented `BRANCH_FAILED` reason |
| Unit | `tests/unit/test_finding_check_field.py` (new) | Schema requires `check`; missing/fabricated → discarded; `beyond-checklist:` → accepted in separate bucket |
| Acceptance (smoke) | `test-acceptance.sh --dry-run --phase=cascade --from-layer=brd --to-layer=brd` | Audit SKILL composes brief with playbook section present. No live LLM call |
| Acceptance (live) | One live cascade run on BRD or PRD layer | Full path: SKILL → inline → dispatch → findings with `check` → synthesizer coverage stats. Pass: ≥60% findings cite a checklist check; coverage quorum met; score within ±3 of pre-playbook baseline (BRD 96 / PRD 93) |
| Manual review | Diff PRD finding quality before/after playbook | Compare 15-finding verdict.json from prior PRD saga vs fresh PRD audit post-playbook. Did playbook surface findings the prior pass missed without losing beyond-checklist insights? |

**Out-of-scope tests** (documented for clarity):

- Playbook content quality itself — manual + live acceptance run only
- Cross-playbook altitude consistency — manual review during authoring
- Hermes parity — deferred to HERMES-BACKLOG.md

## Scope (in / out)

### In scope (this PR)

- New `framework/governance/REVIEW_TEAM.md` §Playbooks section
- 45 playbook files at `framework/playbooks/<NN>_<LAYER>/<lens>.md` across all 8 layers
- Audit SKILL extension in all 8 `doc-<layer>-audit/SKILL.md` (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN) for playbook loading + brief composition
- Synthesizer agent extension to honor `findings[].check` field + emit `verdict.playbook_coverage`
- Conformance + unit tests as enumerated above
- `framework/VERSION` minor bump (0.13.1 → 0.14.0) — adds playbooks as new artifact class
- `platforms/claude-code-plugin/VERSION` minor bump — consumes new spec
- CHANGELOG entries (framework + plugin); ROADMAP update; HANDOFF.md narrative; CLAUDE.md current-state line

### Out of scope (deferred)

- Playbook inheritance / `extends:` mechanism (per-lens chosen over shared base)
- Per-project playbook overrides via `.aidoc/profile.yaml`
- Cross-layer finding propagation ("this PRD finding is really a BRD issue")
- Playbook generation tooling (manual authoring; automate if patterns emerge)
- Hermes parity (tracked in `plans/HERMES-BACKLOG.md` per plugin-first policy)
- Backfilling BRD/PRD with the calibrated playbooks (this PR authors them as part of the 45)

## Crew breakdown (45 playbooks)

Counts per layer derived from `framework/governance/REVIEW_CREWS.yaml`:

| Layer | Lenses | Count |
|---|---|---|
| BRD | architect, business_analyst, auditor, chaos_engineer, security_engineer | 5 |
| PRD | product_owner, architect, tech_lead, chaos_engineer, security_engineer, auditor | 6 |
| EARS | requirements_specialist, tech_lead, qa_lead, chaos_engineer, security_engineer | 5 |
| BDD | qa_lead, tech_lead, chaos_engineer, security_engineer, operator, auditor | 6 |
| ADR | architect, tech_lead, chaos_engineer, security_engineer, operator, auditor | 6 |
| SPEC | architect, tech_lead, integration_lead, chaos_engineer, security_engineer | 5 |
| TDD | qa_lead, tech_lead, chaos_engineer, security_engineer, operator, auditor | 6 |
| IPLAN | tech_lead, architect, operator, integration_lead, auditor, chaos_engineer | 6 |
| **Total** | | **45** |

## Risk acknowledgment

The live acceptance run is the **only** check that playbooks actually improve lens output. Conformance + unit tests prove the wiring works; they cannot prove the playbooks make reviews better. This is the unavoidable risk of any "calibration" feature — verified by re-running the cascade and observing whether finding distribution shifts in the expected direction (more checklist-cited findings, fewer post-hoc human-spotted gaps).

If the live acceptance run shows score regression > 3 points or > 30% beyond-checklist ratio, treat playbooks for that layer as miscalibrated and iterate the playbook content (not the mechanism) before merging.

## Open follow-ups (none currently)

Design surface fully resolved during brainstorming. All 4 design questions + content shape answered.

---

**Approved by user:** 2026-06-07 during brainstorming session
**Next:** implementation plan via `writing-plans` skill → `plans/LAYER-PLAYBOOKS-001-PLAN.md`
