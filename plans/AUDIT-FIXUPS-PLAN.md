# AUDIT-FIXUPS Plan — close the 3 residual findings from the C4 + ID_NAMING audit

| Field      | Value                          |
|------------|--------------------------------|
| Task       | AUDIT-FIXUPS                   |
| Depends on | The diagram-conformance + legacy-naming-purge commits on `claude/multi-platform-migration-AamWB`; source of truth `legacy-ucx-v3.2-read-only/ucx_flow_v3` (8 layers; element IDs `{TYPE}.{doc}.{section}.{hash}`) |
| Status     | DONE — 2026-05-26 (WS-A/B/C implemented; see Implementation log) |
| Feeds      | Full agent conformance to the C4 diagram model + the v3.2 ID_NAMING convention across both platforms; unblocks AGENT-TEAM Phase 1 |

## Objective

Three residual findings remain after the diagram-conformance and legacy-naming
audits. Close them so both platforms' agents fully conform to the framework's C4
diagram model and the v3.2 `ID_NAMING_STANDARDS` convention, with no legacy
taxonomy left. Each is an independent workstream; one (WS-A) is a framework-spec
change (GATE-SPEC), the other two are platform-doc-only.

## Scope

**In:**

- **WS-A — ADR decision-sequence requirement (framework, GATE-SPEC).** Make the
  ADR (L5) **decision/interaction sequence** the *required* diagram in
  `framework/layers/05_ADR/ADR-TEMPLATE.yaml`, matching the governance authority
  `DIAGRAM_STANDARDS.md` ("Required decision sequence; no C4/DFD"). Today the
  template offers `sequenceDiagram` **or** `flowchart` as equals, its Section-6
  example is a flowchart, and its checklist never requires `@diagram: sequence-*`.
- **WS-B — Hermes root-docs legacy purge (platform docs).** Remove the
  pre-migration **v2 / 14-layer** narrative (`SYS/REQ/CTR/TSPEC/TASKS`, the legacy
  workflow string, `framework/07_REQ/` + `docs/REQ/` setup, "14-layer … remain
  available") from `sdd-orchestrator/root-docs/{README.md,
  MULTI_PROJECT_QUICK_REFERENCE.md, MULTI_PROJECT_SETUP_GUIDE.md}`. These docs
  present a dual v2/v3 framework where v2=14-layer is "available", conflicting with
  the 8-layer source of truth.
- **WS-C — persona display-name alignment (platform docs).** Align the stale
  persona display names in `UCC_PERSONAS.md` (`DEVILS_ADVOCATE`,
  `INTEGRATION_EXPERT`), `UCRem_PROMPT_SPEC.md`, and `skills/README.md` to the
  Hermes **runtime** persona keys (`chaos_engineer`, `integration_lead`) that the
  `*.md` persona files and `persona_mappings.yaml` actually use.

**Out:**

- The SPEC-only review-prompt diagram line (recommended **leave as-is**: the
  `architect` persona injects the diagram lens into every review uniformly; the
  SPEC line is justified extra reinforcement). No change.
- The framework ↔ Hermes persona-name *mapping* (`adversary` ↔ `chaos_engineer`,
  `synthesizer` ↔ `chairperson`) — that is **AGENT-TEAM Phase 1** scope, not this
  cleanup. WS-C aligns to Hermes' own runtime names, not the framework names.
- The `sdd-orchestrator` "What Was Cut from v2" table and `references/*` legacy
  ban-guards — these **correctly document the removals**; leave them.

## Approach

### WS-A — ADR template (GATE-SPEC)

Edit `framework/layers/05_ADR/ADR-TEMPLATE.yaml` only (DIAGRAM_STANDARDS.md is
already correct — do **not** double-edit it):

- `diagram_standard`: make the **sequenceDiagram** the required decision/interaction
  diagram carrying `@diagram: sequence-*`; keep `flowchart` as an **optional**
  supplement (decision logic / rollback / alternatives) so that capability isn't
  lost.
- Section 6 `architecture_flow`: lead with a required `sequenceDiagram` example +
  the mandatory intent header and `@diagram: sequence-*` tag; demote the existing
  flowchart example to optional.
- Quality criteria ("Architecture clarity: diagrams present"): require the decision
  sequence specifically.

GATE-SPEC obligations (any `framework/` edit): bump `framework/VERSION`
`0.8.0 → 0.8.1` (patch); set both `platforms/*/FRAMEWORK_SPEC_VERSION` to `0.8.1`;
ripple the 54 plugin skills' `framework_spec_version` → `0.8.1`; add a
`CHANGELOG.md` entry; conformance + `tests/chg/spec_gate.py --base origin/main`
green.

### WS-B — root-docs purge (source → target)

Per source of truth, the framework is **8 layers only**; there is no available
14-layer v2. Transformation across the three root-docs:

- Replace the dual "v2 (14-layer, legacy/available) + v3 (8-layer)" framing with
  the 8-layer flow as the single model; keep at most a **one-line historical note**
  ("the pre-migration 14-layer model is superseded by the 8-layer flow") — drop
  "remain available".
- Remove the legacy workflow string `… ADR → SYS → REQ → CTR → SPEC → TSPEC →
  TASKS` → `BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code`.
- Remove legacy artifact/layer references: `SYS/REQ/CTR/TSPEC/TASKS`, "TSPEC
  (Layer 10)", `framework/07_REQ/REQ-MVP-TEMPLATE.md`, `docs/REQ/…` setup, symlink
  notes to "SDD v2 templates (14 layers)".
- Leave changelog-history bullets that *accurately* record the migration (e.g.
  "Updated test structure to TDD (L7) instead of TSPEC (L10)") — but verify each
  reads as past history, not current capability.

### WS-C — persona names (source → target)

- `UCC_PERSONAS.md`: `### 9. DEVILS_ADVOCATE` → `CHAOS_ENGINEER`; `### 11.
  INTEGRATION_EXPERT` → `INTEGRATION_LEAD`; update prose/table cells that name them.
- `UCRem_PROMPT_SPEC.md`, `skills/README.md`: `integration_expert` →
  `integration_lead`, `devils_advocate` → `chaos_engineer`.

## Step sequence

1. **WS-A** on a path that isolates the version bump: edit the ADR template, run
   the GATE-SPEC ripple (VERSION + both FSV + 54 skills + CHANGELOG), verify.
   Commit as one logical GATE-SPEC change.
2. **WS-B** then **WS-C** (platform-doc-only, no spec change) — one commit each.
3. **Verify** (see below) after each workstream.
4. **Land:** commits with conventional prefixes (`feat(framework):` for WS-A;
   `docs(hermes):`/`fix(hermes):` for WS-B/C); update `CHANGELOG.md` and
   `plans/HANDOFF.md`.

## Verification

- **WS-A:** `python3 -m unittest discover -s tests/conformance` (54) green;
  `python3 tests/chg/spec_gate.py --base origin/main` green (E005 VERSION bump,
  E006 FSV match, E008 CHANGELOG); `framework/VERSION` == both FSV == `0.8.1`;
  all 54 skills' `framework_spec_version` == `0.8.1`; the ADR template still parses
  as YAML; `test_spec_hygiene` clean (no engine tokens introduced).
- **WS-B:** `grep -rniE '\b(SYS|REQ|CTR|TSPEC|TASKS)\b|14.layer|Layer 1[01]|→ ?(SYS|REQ|CTR|TSPEC)' root-docs/`
  returns only the retained one-line historical note (calibrate to exclude
  `require/request/system`); no `framework/07_REQ` or `docs/REQ` setup left.
  root-docs are under `agent-skills/` (markdownlint-excluded) — no lint gate, but
  links must still resolve.
- **WS-C:** `grep -rniE 'integration_expert|devils_advocate' platforms/hermes/`
  returns nothing; Hermes prompt/persona tests green
  (`test_persona_manager`, `test_prompt_context_builder`,
  `test_creation_prompt_builder`).
- **All:** conformance unaffected by WS-B/WS-C (platform-doc changes).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | WS-A 54-skill FSV ripple drifts / mismatches | Script the bump; run `spec_gate.py` which enforces FSV==VERSION (E006). Verify whether a conformance test also asserts skill `framework_spec_version`==VERSION; bump all 54 regardless for consistency. |
| R2 | WS-A version bump tangled with platform-doc commits | Keep WS-A as its own commit; WS-B/WS-C carry **no** `framework/` change (no bump). |
| R3 | WS-A loses the flowchart capability ADR legitimately uses (rollback/alternatives) | Keep `flowchart` **allowed/optional**; only make the decision **sequence** required. |
| R4 | WS-B over-deletes useful context, or misreads which `framework/` the docs mean | The docs refer to the legacy ucx 14-layer dir; the migrated repo has no such framework, so removal is safe. Keep a one-line historical note; don't touch the correct "What Was Cut" table or ban-guards. |
| R5 | WS-C renames a display name still referenced elsewhere | Grep-confirm zero residual `integration_expert`/`devils_advocate`; runtime keys (`persona_mappings.yaml`, `*.md`) already use the canonical names, so display-name edits are safe. |
| R6 | Scope creep: WS-B balloons (the v2/v3 narrative is woven through 3 files) | Bounded transformation rules above; verify by grep, not by rewriting whole guides. |

## Review log

> ≥2 passes before implementation (CLAUDE.md). Each pass re-reads the whole plan,
> lists findings, folds fixes back above; stop when a pass finds nothing.

### Pass 1 — 2026-05-26

- **WS-A double-edit risk.** First draft implied editing both the ADR template and
  `DIAGRAM_STANDARDS.md`. The governance doc already mandates the decision sequence
  correctly — only the *template* is loose. Scoped WS-A to `ADR-TEMPLATE.yaml`
  alone (avoids a redundant/contradictory edit). (R-relates to Approach.)
- **Don't drop flowchart.** The template legitimately allows a flowchart for
  decision logic / rollback / alternatives. Reframed WS-A to make the **sequence
  required** while keeping flowchart **optional** (R3).
- **FSV ripple uncertainty.** Unclear whether a conformance test asserts each
  skill's `framework_spec_version` or only `spec_gate` checks the two FSV files.
  Added a verification step to confirm, and to bump all 54 regardless (R1).
- **WS-B dangling references.** Removing the v2 narrative must also remove its
  setup commands (`framework/07_REQ/`, `docs/REQ/…`, v2 symlink notes) or they
  dangle. Added to the transformation rules.
- **WS-C target names.** Pinned WS-C to align with the Hermes **runtime** persona
  files (`chaos_engineer`, `integration_lead`) — explicitly **not** the framework
  `adversary`/`synthesizer` names (that mapping is AGENT-TEAM Phase 1). Recorded in
  Scope/Out.

### Pass 2 — 2026-05-26

- **Sequencing/commit isolation.** Confirmed WS-A must be a standalone GATE-SPEC
  commit (version bump + ripple) and WS-B/WS-C must carry no `framework/` change, so
  the spec gate doesn't fire on the doc commits (R2).
- **Verification false-positives.** The WS-B grep must tolerate the retained
  one-line historical note and must not flag the correct "What Was Cut" table or
  the `references/*` ban-guards; calibrated the grep exclusions.
- **markdownlint scope.** Confirmed `agent-skills/` (root-docs) is markdownlint-
  excluded, so WS-B has no lint gate — but internal links/anchors must still
  resolve; added to verification.
- No further findings — implementable.

## Implementation log

### 2026-05-26 — all three workstreams landed (branch `claude/multi-platform-migration-AamWB`)

- **WS-A** (`feat(framework):`): `ADR-TEMPLATE.yaml` now requires the decision
  `sequenceDiagram` (intent header + `@diagram: sequence-*`), flowchart optional;
  quality criteria updated. GATE-SPEC ripple: `framework/VERSION` + both
  `FRAMEWORK_SPEC_VERSION` + 54 skill `framework_spec_version` → `0.8.1`; CHANGELOG.
  `spec_gate` green ("VERSION + CHANGELOG updated, OK"); conformance 54.
- **WS-B** (`docs(hermes):`): purged the v2/14-layer "available" narrative from the
  3 `sdd-orchestrator/root-docs` (README + 2 MULTI_PROJECT guides) — removed the
  legacy workflow, `SYS/REQ/CTR/TSPEC/TASKS`, duplicate `framework/` rows, and
  `07_REQ`/`docs/REQ` setup; kept a one-line "superseded" note + the accurate
  migration changelog. Verified by grep.
- **WS-C** (`docs(hermes):`): `UCC_PERSONAS.md` #9 `DEVILS_ADVOCATE`→`CHAOS_ENGINEER`,
  #11 `INTEGRATION_EXPERT`→`INTEGRATION_LEAD` + collaboration/UCRem fixer-crew refs,
  matching the runtime persona keys. Conformance 54; Hermes prompt/persona tests
  green (52). The `skills/README` rename-changelog left as history.
- **Verification:** conformance 54 green throughout; spec_gate green (WS-A);
  Hermes prompt/persona tests 52 passed; no residual legacy taxonomy / persona-name
  drift in the agent-facing files.
