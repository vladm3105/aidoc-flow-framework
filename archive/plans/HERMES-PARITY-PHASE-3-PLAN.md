# HERMES-PARITY-PHASE-3 Plan — 8-layer playbook coverage (verify) + CHG crew parity

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-PARITY-PHASE-3                        |
| Type           | feature                                     |
| Status         | PLANNED — 2026-07-03T20:08:53-04:00         |
| Depends on     | HERMES-PARITY-PHASE-2 (D-0046, merged #232) |
| Feeds          | later phases (live CHG saga dispatch; H-6/H-2 calibration deltas) |
| Version impact | **Hermes MINOR** (`hermes` `0.4.0 → 0.5.0`) — CHG review-crew parity + 8-layer playbook coverage milestone; **no framework spec bump** (no `framework/**` change — GATE-SPEC no-op) |

## Objective

Close the remaining playbook-parity gap. Two parts: **H-5** — the other 6 lifecycle
layers (EARS/BDD/ADR/SPEC/TDD/IPLAN) are **already** covered because Phase 2's
injection is layer-agnostic (`playbook_loader` maps all 9 layers; `is_crew_lens`
reads `REVIEW_CREWS.yaml`) — so this phase **verifies + tests + documents** the
8-layer coverage rather than implementing it; and **H-10** — bring CHG to crew
parity by adding the `chg` review crew to `persona_mappings.yaml` and removing the
`HERMES_DEFERRED_LAYERS` whitelist so the crew-coverage conformance test asserts
CHG. No new engine code and no framework change.

## Scope

**In:**

- **H-5 (verify + test):** a parametrized loader test proving all **8 lifecycle
  layers** resolve their crew-lens playbooks (the payoff of Phase 2's layer-agnostic
  design). `docs/PARITY.md` Layer-Playbooks row → "all 8 lifecycle layers active".
- **H-10 (CHG crew parity):** add a `chg` entry to `persona_mappings.yaml`'s
  `review:` map with the framework CHG crew
  (`integration_lead, architect, chaos_engineer, operator, auditor, security_engineer`
  — `REVIEW_CREWS.yaml` CHG weights 30/20/15/15/10/10); remove `CHG` from
  `HERMES_DEFERRED_LAYERS` (`test_review_scoring.py:157`) so
  `test_hermes_review_crews_cover_framework_crews` now asserts the CHG crew is
  covered; a test confirming the 6 `framework/playbooks/09_CHG/<lens>.md` resolve.
- Hermes MINOR bump `0.4.0 → 0.5.0`; Hermes CHANGELOG; `docs/PARITY.md`; close H-5 +
  the crew-parity half of H-10 in `HERMES-BACKLOG.md`; D-0047; HANDOFF.

**Out of scope (deferred — enumerated, not designed):**

- **Live/sanctioned CHG saga review dispatch.** The real guardrail is **not** a
  schema wall — Hermes never loads `saga.schema.json` at runtime (it is a
  framework-side conformance contract; `grep` of `platforms/hermes/src` → 0 hits).
  The guardrail is that **no default code path dispatches a CHG review**:
  `doc_type=chg` is not a documented/sanctioned review target, and the crew resolver
  reads the review map by `doc_type` with **no allowlist** (`_resolve_review_branch_runtime`
  → `review_map.get(doc_type)`, `saga_orchestrator.py:194`). **Known side effect, accepted:** adding the `chg`
  crew entry (required for the crew-coverage parity below) makes an *explicit*
  `doc_type=chg` review dispatchable where it was previously inert (empty crew) — and
  such a run's saga journal would carry `layer` outside the `saga.schema.json` enum
  (schema-non-conformant, though unchecked at Hermes runtime). Making CHG a
  first-class review target (adding `09_CHG` to the schema — a `framework/` change —
  - a sanctioned dispatch path + the live doc-chg-audit cascade) is the dedicated
  **live-CHG follow-on**. Phase 3 delivers **crew-map parity only** and documents
  this boundary; V7 confirms no default flow dispatches CHG.
- **H-6 / H-2 calibration deltas** (no-findings rationale, author-self-claim
  stripping, fixer-regression detection) — distinct synthesizer-quality features;
  a later phase.
- **`prompt_only` injection** (Phase 2 follow-on) and **Phase 1b** (saga
  break-circuit exercise) — unchanged, still queued.

## Approach / Design (D-0047)

### H-5 is already delivered — this phase proves it

Phase 2 (D-0046) shipped `playbook_loader` with `_LAYER_DIRS` covering all 9 layers
and `is_crew_lens` reading `REVIEW_CREWS.yaml`, and wired injection into the
layer-agnostic `_branch_llm_findings`. Verified empirically: `load_playbook(<layer>,
<crew-lens>)` returns a playbook with parsed `Cn` ids for **every** crew lens of
EARS/BDD/ADR/SPEC/TDD/IPLAN. So H-5 needs **no code** — it needs a regression test
locking in the 8-layer coverage and a doc update. (This is the intended payoff of
designing the Phase-2 injection layer-agnostically.)

### H-10 — CHG crew parity, minimally

`REVIEW_CREWS.yaml` already carries the CHG crew and the 6 `09_CHG` playbooks exist

- resolve (verified). The only missing piece for **crew parity** is Hermes's
`persona_mappings.yaml`, which has no `chg` review entry — so
`test_hermes_review_crews_cover_framework_crews` skips CHG via the
`HERMES_DEFERRED_LAYERS` whitelist. Add the `chg` review crew (matching the
framework lenses) and drop CHG from the whitelist; the test then enforces CHG crew
coverage like the 8 lifecycle layers. This does **not** run a CHG saga (see Out of
scope) — it establishes the static crew-map parity the whitelist was deferring.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/hermes/skills/persona_mappings.yaml` | add a `chg:` review entry (the 6 CHG crew lenses) |
| `platforms/hermes/tests/unit/test_review_scoring.py` | remove `CHG` from `HERMES_DEFERRED_LAYERS` (`:157`) — the crew-coverage test now asserts CHG |
| `platforms/hermes/tests/unit/test_playbook_injection.py` | parametrize the loader test over all 8 lifecycle layers + a CHG-lenses case |
| `platforms/hermes/VERSION` + `CHANGELOG.md` | `0.4.0 → 0.5.0`; entry |
| `docs/PARITY.md` | Layer-Playbooks row → all 8 lifecycle layers active; CHG crew parity |
| `plans/HERMES-BACKLOG.md` / `HANDOFF.md` / `DECISIONS.md` | H-5 + H-10(crew) closed; D-0047 |

## Implementation sequence

### Task 1: H-5 regression test — [CODE]

- Extend `test_playbook_injection.py`: parametrize over all 8 lifecycle layers ×
  their `REVIEW_CREWS.yaml` crew lenses; assert each resolves a playbook with `Cn`
  ids. (Locks in the Phase-2 payoff.)

### Task 2: H-10 CHG crew parity — [CODE]

- Add the `chg` review entry to `persona_mappings.yaml`; remove `CHG` from
  `HERMES_DEFERRED_LAYERS`; add a CHG playbook-resolution assertion. Confirm
  `test_hermes_review_crews_cover_framework_crews` passes with CHG enforced.

### Task 3: version + docs

- Hermes `0.5.0`; CHANGELOG; PARITY row; backlog (H-5 + H-10-crew closed, live-CHG
  deferred); D-0047; HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | parametrized loader test: all 8 lifecycle layers' crew lenses resolve playbooks with `Cn` ids | green | H-5 |
| V2 | `test_hermes_review_crews_cover_framework_crews` with CHG NOT whitelisted | green — CHG crew covered by `persona_mappings.yaml` | H-10 |
| V3 | `load_playbook("CHG", <lens>)` for the 6 CHG lenses | all resolve with `Cn` ids | H-10 |
| V4 | `python -m pytest platforms/hermes/tests -q` | green | no regression |
| V5 | `python -m pytest tests/conformance -q` | green | no cross-platform regression |
| V6 | no `framework/**` diff; Hermes `FRAMEWORK_SPEC_VERSION` `0.32.6` unchanged | GATE-SPEC no-op | version scope |
| V7 | grep the Hermes tools/CLI for any default flow that dispatches a review with `doc_type=chg` | none — CHG review is not a default/sanctioned target (only an explicit caller could) | R2 (deferral honesty) |

## Docs to update

- [ ] `platforms/hermes/CHANGELOG.md` — `[0.5.0]`
- [ ] `docs/PARITY.md` — Layer-Playbooks (8 lifecycle active + CHG crew)
- [ ] `plans/HERMES-BACKLOG.md` — H-5 + H-10(crew) closed; live-CHG-saga follow-on logged
- [ ] `plans/DECISIONS.md` — D-0047
- [ ] `plans/HANDOFF.md` — arc progress
- [ ] `CHANGELOG.md` (root) — Hermes 0.5.0

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Removing CHG from the whitelist fails the crew-coverage test (a CHG lens name mismatch vs `persona_mappings`) | med | the `chg` entry uses the exact `REVIEW_CREWS.yaml` CHG lens names; V2 is the gate; `canonical_persona` aliasing already handled |
| R2 | Adding `chg` to `persona_mappings.yaml` makes an *explicit* `doc_type=chg` review dispatchable (previously inert) → a schema-non-conformant saga journal if run | med | accepted + documented (Out of scope): no DEFAULT flow dispatches CHG (V7); `doc_type=chg` is unsanctioned until the live-CHG follow-on adds `09_CHG` to the schema + a real dispatch path. The crew-map entry is *required* for the H-10 crew-coverage parity and is otherwise inert |
| R3 | "All 8 layers active" over-claims if some layer's injection path differs | low | V1 tests every lifecycle layer's crew lenses through the real `load_playbook`; the orchestrator path is layer-agnostic (one code path, proven in Phase 2) |
| R4 | Version bump debatable (H-5 already shipped in 0.4.0) | low | the NEW capability is CHG crew parity + the documented 8-layer milestone → MINOR; independent review to confirm |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | `playbook_loader` maps all 9 layer dirs (so it is not BRD+PRD-limited) | `_LAYER_DIRS` | platforms/hermes/src/mcp_server/review/playbook_loader.py:26 |
| 2  | Injection is wired into the layer-agnostic LLM branch (one path, any layer) | `load_playbook` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:395 |
| 2b | The crew/runtime resolver reads the review map by `doc_type` with NO allowlist (so `doc_type=chg` resolves once the map has it) | `review_map.get(doc_type` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:194 |
| 3  | `REVIEW_CREWS.yaml` carries the CHG crew (so `is_crew_lens` works for CHG) | `CHG:` | framework/governance/REVIEW_CREWS.yaml:87 |
| 4  | The CHG review crew is integration_lead/architect/chaos_engineer/operator/auditor/security_engineer | `integration_lead: 30` | framework/governance/REVIEW_CREWS.yaml:95 |
| 5  | The 6 `09_CHG` playbooks exist | `lens: integration_lead` | framework/playbooks/09_CHG/integration_lead.md:3 |
| 6  | `persona_mappings.yaml` has no `chg` review entry (the gap) | `iplan:` | platforms/hermes/skills/persona_mappings.yaml:64 |
| 7  | The crew-coverage test whitelists CHG (`HERMES_DEFERRED_LAYERS`) — remove it | `HERMES_DEFERRED_LAYERS` | platforms/hermes/tests/unit/test_review_scoring.py:157 |
| 8  | `saga.schema.json` `layer` enum is `01_BRD..08_IPLAN` (no `09_CHG`) — live CHG saga is deferred | `08_IPLAN` | framework/governance/saga.schema.json:36 |
| 9  | Hermes product version is `0.4.0` (→ `0.5.0` MINOR) | `0.4.0` | platforms/hermes/VERSION:1 |
| 10 | Most recent decision is D-0046 → next free is D-0047 | `D-0046` | plans/DECISIONS.md:13 |

## Review log

### Pass 1 — 2026-07-03T20:08:53-04:00 — self-review

- **Central finding validated empirically:** `load_playbook(<layer>, <crew-lens>)`
  returns a playbook with `Cn` ids for all 8 lifecycle layers (EARS/BDD/ADR/SPEC/
  TDD/IPLAN) AND the 6 CHG lenses — so H-5 needs no code and CHG playbook resolution
  already works; only `persona_mappings.yaml` + the whitelist are missing for CHG
  crew parity. This is why the plan is verify-and-wire, not implement.
- **Honest scope boundary:** the live CHG saga run (schema `09_CHG` + orchestrator
  dispatch) is genuinely out of reach here (no CHG saga wiring exists; the schema is
  `framework/`) — deferred explicitly (Out of scope + R2) so the plan doesn't
  over-promise.
- **Version-bump call flagged** (R4) for the reviewer: H-5 shipped in 0.4.0, so the
  new capability is CHG crew parity + the 8-layer milestone → MINOR.
- Citation gate: 10 rows resolve (`--fix` re-pointed 3 drifted lines).

### Pass 2 — 2026-07-03T20:35:00-04:00 — independent (fresh-context)

Fresh `code-reviewer` verified all 10 ledger rows, **re-ran the H-5 claim
empirically** (0 failures — every crew lens of all 8 lifecycle layers + the 6 CHG
lenses resolves a playbook with `Cn` ids), and confirmed the CHG crew-parity
mechanism is sound (`expected − mapped = ∅`; the plan edits the exact `review:`
block the test reads; all 6 CHG `personas/*.md` exist so `_validate_persona_mapping`
won't reject the key; suites green). **1 load-bearing finding, folded:**

- **F-LB1 — the deferral's guardrail was fictional.** I justified deferring live CHG
  by a `saga.schema.json` "09_CHG wall" — but Hermes never loads that schema at
  runtime (framework-side only; 0 `src` hits), and the crew resolver has no
  `doc_type` allowlist (`_get_review_config`, `:193`). So adding `chg` makes an
  *explicit* `doc_type=chg` review dispatchable (previously inert), producing a
  schema-non-conformant journal if run. Re-grounded the deferral on the real
  guardrail ("no default flow dispatches CHG; `doc_type=chg` unsanctioned"),
  documented the accepted side effect, rewrote R2, added V7 + Claim 2b.
- Minor: row-2 line → `:395`; version MINOR is a framing call (R4, kept).

**Result:** ready
