# FRWK-REVIEW-4b Plan — EARS statement-model reconciliation

| Field      | Value                          |
|------------|--------------------------------|
| Task       | FRWK-REVIEW-4b                 |
| Depends on | FRWK-REVIEW (PRs #12/#13 merged); framework spec `0.5.0` |
| Status     | IMPLEMENTED — 2026-05-25 (D1 = A canonical-5; branch `claude/frwk-review-4b-ears-model`, spec `0.6.0`); PR pending |
| Feeds      | a single coherent EARS statement model across the spec + platforms; `framework/v0.6.0` |

## Objective

Resolve FRWK-REVIEW finding **#4b** — the EARS layer describes its own statement
model inconsistently. The authoritative template + README list **four** patterns
in `THE … SHALL … WITHIN` form; the EARS **index** lists **five** (adds
Optional / `WHERE`) but in a non-EARS `… THEN …` form; and the two platforms
have drifted further still (one plugin agent lists 5 patterns that *drop*
Unwanted and add Complex; the Hermes personas list 6). This is a spec-semantics
decision, not a copy-edit: it determines how many EARS patterns the framework
recognizes and which grammar is canonical. This task picks one model, makes the
framework spec say it in one voice, aligns the platform docs the spec drives,
and adds a conformance guard so the model can't silently drift again.

## Scope

**In:**

- The three framework EARS files: `framework/layers/03_EARS/EARS-TEMPLATE.yaml`,
  `README.md`, `EARS-00_index.TEMPLATE.md`.
- A new conformance guard (`tests/conformance/`) locking the statement-model set
  and grammar so template/README/index can't diverge again.
- The **first-class plugin** EARS surfaces that re-describe the patterns:
  `platforms/claude-code-plugin/skills/doc-ears/SKILL.md` and
  `platforms/claude-code-plugin/agents/requirements-analyst.md`.
- GATE-SPEC bookkeeping (framework edit ⇒ VERSION + CHANGELOG + both
  `FRAMEWORK_SPEC_VERSION` + 54-skill ripple).

**Out (deferred / flagged, not in this PR):**

- **Hermes vendored content** — `agent-skills/spec-driven-development/…`
  (`sdd-review-personas/SKILL.md`) and `prompts/templates/remediation/UCRem_PROMPT_EARS.md`.
  These are vendored/parsed Hermes assets (excluded from style hooks); their EARS
  tables also drifted (6-pattern, mixed `THEN`). Aligning them is a Hermes-platform
  follow-up tracked here, not a framework-spec change. Recorded as a deferred item.
- A **runtime/parser** that *enforces* EARS grammar on authored documents — the
  guard checks the *spec's self-consistency*, not user artifacts.
- The "Complex" pattern as a distinct structured block (see D1 — it is documented
  as composition, not a sixth type).

## Decision

### D1 — Which EARS model? (RESOLVED 2026-05-25 — **A, canonical-5**, user-confirmed)

Three candidates surfaced from the drift:

- **A. Canonical 5 + `SHALL` + `WITHIN` extension** *(recommended)* —
  `{Ubiquitous, Event-driven (WHEN), State-driven (WHILE), Optional (WHERE),
  Unwanted (IF)}`, all in `THE <component> SHALL <response> [WITHIN <timing>]`
  form. "Complex" is documented as **composition of the base patterns**, not a
  distinct type. `THEN` is rejected everywhere.
- **B. Canonical 6** — A + a distinct `Complex` (WHILE+WHEN) pattern block,
  matching the Hermes personas table.
- **C. Reduced 4** (today's template) — keep `{Ubiquitous, Event, State,
  Unwanted}`, *delete* Optional/`WHERE`; correct the index down to 4 + `SHALL`.

**Recommendation: A.** Rationale:

1. The layer is literally *EARS* — it should match the standard. Canonical EARS
   (Mavin) is exactly these five; the framework template's omission of Optional
   reads as accidental drift, not a principled cut — Optional/`WHERE` already
   appears *independently* in the framework index, the plugin
   `requirements-analyst`, and the Hermes personas, so its intent is clear.
2. `THEN` is **not** EARS grammar; canonical EARS always uses `the <system> shall`.
   The index's `… THEN …` and Hermes' `IF … THEN` are the genuine errors to fix.
3. "Complex" is not a separate grammar — it is base patterns composed
   (e.g. `WHILE <state>, WHEN <event>, THE … SHALL …`). A composition note absorbs
   the Hermes `Complex` row and the `requirements-analyst` `Complex` mention
   without proliferating overlapping types (which is what let `requirements-analyst`
   silently drop `Unwanted`).
4. Keep `WITHIN` — it is a deliberate **framework extension** to canonical EARS
   that supports the layer's quantifiability/testability mandate; it is already
   uniform across template/README/plugin. Document it *as* an extension so it is
   not mistaken for stock EARS.

Net effect of A: framework gains one pattern (Optional/`WHERE`); the index is
corrected (`THEN → SHALL`, add `WITHIN`); README + plugin `doc-ears` gain the
5th pattern; `requirements-analyst` regains `Unwanted` and reframes `Complex`
as composition. Backward-compatible (existing 4-pattern documents stay valid) ⇒
**minor** bump.

## Approach

### Source → target

| File | Change |
|------|--------|
| `EARS-TEMPLATE.yaml` | `_guidance` "Four EARS syntax patterns" → "Five…"; add the `WHERE-THE-SHALL` (Optional / feature) pattern to the guidance block; add a structured `optional_feature:` block mirroring its siblings (`id`, `name`, `statement`, `traceability`); add a one-line **composition** note (patterns may combine — "complex" requirements) and a note that `WITHIN` is a framework testability extension; extend the `_antipatterns` trigger-clause line to include `WHERE`. |
| `README.md` | Add the Optional / `WHERE` row to the "EARS Syntax Patterns" table; add the composition + `WITHIN`-extension notes. |
| `EARS-00_index.TEMPLATE.md` | Rewrite the "EARS Statement Types" table to the 5 canonical types in `THE … SHALL` form (drop the `[trigger] THEN [response]` connective; keep Optional/`WHERE`; align examples; the quality-check line "WHEN/THEN, WHILE/THEN" → "WHEN/SHALL, WHILE/SHALL, …"). |
| plugin `doc-ears/SKILL.md` | "the four patterns" → "the five patterns" (3 occurrences incl. the §2 table, the categorize step, and the info table); add the Optional/`WHERE` row + checklist categorization. |
| plugin `requirements-analyst.md` | Supported patterns line → the canonical 5 (`Ubiquitous, Event-Driven, State-Driven, Optional, Unwanted`), with Complex noted as composition. |
| `tests/conformance/` | New guard (below). |
| `framework/VERSION`, both `FRAMEWORK_SPEC_VERSION`, 54 skills, `CHANGELOG.md` | `0.5.0 → 0.6.0` minor bump + changelog entry. |

### Conformance guard (`tests/conformance/test_ears_model.py`)

Lock the model so the three framework EARS files can't diverge again:

1. **Pattern set agreement** — the template defines structured blocks for all
   five canonical patterns (`event_driven`, `state_driven`, `unwanted_behavior`,
   `optional_feature`, `ubiquitous`); the README pattern table and the index
   statement-type table each name all five (case-insensitive token check:
   `ubiquitous`, `event`, `state`, `optional`/`WHERE`, `unwanted`/`IF`).
2. **Grammar** — no EARS file uses the `THEN [response]` connective form (assert
   the index/README/template contain no `THEN` used as the EARS response
   connective). `SHALL` present in each pattern row.
   *(Placeholder-aware / token-based, not exact-table-format, to avoid brittleness.)*

This adds the EARS-model check the suite currently lacks (today nothing gates the
statement model — which is how the drift accumulated).

## Step sequence

1. **Confirm D1** (canonical-5) — if the user prefers B or C, swap the target set
   before editing.
2. Edit the three framework EARS files to model A.
3. Add `tests/conformance/test_ears_model.py`; run the suite (it should fail
   first if any file still says "four"/uses `THEN`, then pass after the edits).
4. Align the two first-class plugin files.
5. **Verify** (below).
6. **Land:** bump `0.5.0 → 0.6.0` (VERSION + 2 FSV + 54 skills) + `CHANGELOG.md`
   entry; confirm `spec_gate` green; open PR. Record the Hermes-vendored
   alignment as a deferred follow-up in `HANDOFF.md`.

## Verification

- `python3 -m unittest discover -s tests/conformance` — green, including the new
  `test_ears_model` guard.
- `python3 tests/chg/spec_gate.py --base origin/main` — passes (framework changed
  ⇒ VERSION + CHANGELOG bumped).
- `grep -rniE "THEN \[response\]|\[trigger\] THEN" framework/layers/03_EARS/` —
  **no hits** (the non-EARS connective is gone).
- All three framework EARS files + the two plugin files name the **same five**
  patterns; `grep -c "four patterns"` in the EARS surfaces is `0`.
- Version alignment: `framework/VERSION` == both `FRAMEWORK_SPEC_VERSION` (`0.6.0`).
- `test_spec_hygiene` clean (no engine tokens introduced).
- `pre-commit run markdownlint --files <changed .md>` clean.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Adding Optional/`WHERE` expands the template surface | Additive block mirroring the four existing siblings exactly; guidance + example + antipattern updated together; backward-compatible ⇒ minor bump. |
| R2 | Platform EARS docs drift further than the two first-class files (Hermes 6-pattern; `requirements-analyst` had dropped Unwanted) | Fix the two first-class plugin files now; **flag** the Hermes vendored `agent-skills`/`prompts` EARS tables as a tracked follow-up (vendored, not framework-spec). The guard locks the framework, the single source of truth. |
| R3 | "Complex" ambiguity re-drifts a 6th type back in | Document Complex as *composition* in template + README; reconcile the existing `Complex` mentions into that note rather than a structured block. |
| R4 | Conformance guard too brittle (parsing md tables) | Token/keyword-presence + `THEN`-absence checks, not exact table layout; placeholder-tolerant. |
| R5 | GATE-SPEC self-gate (this PR must pass GATE-SPEC) | Minor bump + CHANGELOG by construction (E005/E008); FSV match (E006); suite green (E007). |
| R6 | `WITHIN` mistaken for standard EARS | Explicitly label it a framework testability *extension* in template + README. |

## Review log

> ≥2 passes before implementation (CLAUDE.md § Development workflow). Each pass
> re-reads the whole plan, lists findings, folds fixes back into the sections
> above; stop when a pass finds nothing.

### Pass 1 — 2026-05-25

- **Scope creep risk on Hermes.** First draft put all six drifted docs in scope.
  Hermes `agent-skills`/`prompts` are vendored/parsed platform content, not the
  framework spec; folding them into a framework-spec PR mixes concerns and bloats
  the diff. Reframed: framework + first-class plugin files in scope; Hermes
  vendored EARS tables flagged as a deferred platform follow-up (R2).
- **"Complex" was ambiguous in the target.** Pinned it down: not a 6th structured
  pattern, but a documented *composition* of the base five — this also explains
  the two platform drifts (`requirements-analyst` dropping Unwanted; Hermes' 6th
  row) without proliferating overlapping types (D1 point 3, R3).
- **Guard could false-positive on the word "then".** Narrowed the grammar check
  to the EARS *response connective* (`THEN [response]` / `[trigger] THEN`), not
  any occurrence of "then" in prose (R4 / Verification grep tightened).
- **`WITHIN` provenance.** Added the explicit "framework extension, not stock
  EARS" note so a future reader doesn't try to "fix" it toward canonical EARS
  (R6 / D1 point 4).

### Pass 2 — 2026-05-25

- **Semver.** Confirmed **minor** (`0.5.0 → 0.6.0`): adding a pattern + correcting
  the index grammar is additive/corrective and leaves existing 4-pattern EARS
  documents valid — not breaking. No change.
- **Guard ordering.** Step 3 notes the guard should be added *with* the edits
  (suite fails on the stale "four"/`THEN` state first, then passes) so the guard
  is proven to bite — mirrors the FRWK-REVIEW guard-after-fix discipline. No change.
- **Decision honesty.** D1 is a *recommendation* pending user confirmation; the
  step sequence opens with "confirm D1" and the alternatives (B canonical-6,
  C reduced-4) are spelled out with their concrete consequences, so the user can
  flip it without re-planning. No change.
- No further findings — plan is implementable pending D1 confirmation.

## Implementation log

### 2026-05-25 — implemented (branch `claude/frwk-review-4b-ears-model`)

- D1 = A confirmed (canonical-5 + `SHALL`; `WITHIN` extension; Complex as
  composition). All edits per the source→target table:
  - `EARS-TEMPLATE.yaml` — guidance "four"→"five"; added the WHERE/Optional
    pattern + a structured `optional_feature` block; composition + `WITHIN`-extension
    notes; antipatterns extended (WHERE trigger; banned `THEN` connective).
  - `README.md` — Optional row + composition/extension note.
  - `EARS-00_index.TEMPLATE.md` — table corrected from `[trigger] THEN [response]`
    to the `SHALL` form across all five types; quality-check line updated.
  - plugin `doc-ears/SKILL.md` (four→five, Optional row, categorize/checklist) +
    `requirements-analyst.md` (regained Unwanted; Complex reframed as composition).
  - `tests/conformance/test_ears_model.py` — three guards (five template blocks;
    README/index name all five + carry `WHERE [`; no `THEN [` connective).
    Guard precision spot-checked (matches old `… THEN [response]`, ignores the
    descriptive `'THEN'` mentions).
- **Verification:** conformance **49/49**; `spec_gate` green vs `origin/main`;
  spec `0.5.0 → 0.6.0` (+ both FSV + 54 skills + CHANGELOG); pre-commit clean.
- **Deferred (tracked):** Hermes vendored `agent-skills`/`prompts` EARS tables
  (6-pattern, mixed `THEN`) — a platform follow-up, not a framework-spec change.
- **Pending:** open PR.
