# CLEANUP-PR-C — Spec / Registry / Template Hygiene

> Child PR of `FRAMEWORK-CLEANUP-001` (master plan PR #128, merged
> `528d6f23`). 4 items: closes `plans/FRAMEWORK-TODO.md` items #11-14.

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | CLEANUP-PR-C                                |
| Type           | combined plan + impl (small, spec-level)    |
| Worktree       | `feat/cleanup-pr-c-spec-registry-hygiene` at `/opt/data/aidoc-flow/framework-cleanup-pr-c/` |
| Depends on     | FRAMEWORK-CLEANUP-001 master plan (PR #128 `528d6f23`) |
| Closes         | `plans/FRAMEWORK-TODO.md` Open items #11, #12, #13, #14 |
| Version impact | Framework MINOR `0.17.1 → 0.18.0` (registry shape change + new governance principle); plugin MINOR `0.14.1 → 0.15.0` (saga driver reads new knob) |
| Status         | DRAFT — 2026-06-11 |

## Items closed by this PR

| # | Tag | Title |
|---|---|---|
| 11 | `[governance]` | Iteration cap implementation-bound, not spec-bound |
| 12 | `[registry]` | `@threshold:` 3-segment keys vs element-ID 4-segment pattern |
| 13 | `[template]` | SPEC + IPLAN declare no layer-local element IDs |
| 14 | `[template]` | EARS emits per-line `@bdd:` downstream slots — direction-of-flow violation |

## Scope per item

### Item 11 — Iteration cap to spec + ADAPTATION_SURFACE knob

`tools/saga_driver.py:130` hard-codes `MAX_ITERATIONS = 3`. The framework
spec (`REVIEW_REMEDIATION_FLOW.md` §The quality loop) says the loop
*"repeats until the gate passes"* — open-ended. The cap is invisible
to anyone reading only the spec.

**Fix shape:**

1. **Spec** — `framework/governance/REVIEW_REMEDIATION_FLOW.md` §The
   quality loop gains a new subsection "Iteration cap" explaining:
   - Default cap = 3 iterations
   - At cap, saga transitions to `PARTIAL_TIMEOUT`; artifact + saga
     journal remain the deliverable
   - The cap is tunable per project via ADAPTATION_SURFACE knob

2. **ADAPTATION_SURFACE.yaml** — add new knob under `knobs:` section:

   ```yaml
   quality_loop:
     max_iterations:
       default: 3
       range: [1, 10]
       description: "Max review→remediate cycles before saga PARTIAL_TIMEOUT"
       consumed_by: ["audit", "fixer"]  # consumer roles
   ```

3. **Plugin saga_driver** — read the knob from `.aidoc/profile.yaml`
   at runtime; fall back to default `3`. Keep the constant as a sentinel
   for backward compatibility. **Pass 1 cross-check:** `saga_driver.py`
   does NOT currently load `.aidoc/profile.yaml` (no `profile.yaml` /
   `yaml.safe_load` call in the module). This means item 11 introduces
   new wiring, not just a constant tweak — needs robust error handling
   for missing file / malformed YAML / missing field. Fallback path
   must preserve current behavior exactly.

**Touches:** `framework/governance/REVIEW_REMEDIATION_FLOW.md` (~15 lines
new subsection), `framework/governance/ADAPTATION_SURFACE.yaml` (~10
lines new knob), `tools/saga_driver.py` (~10 lines to read profile +
fallback), `tests/conformance/test_adaptation_surface.py` (extend with
new knob).

### Item 12 — `@threshold:` ID pattern in LAYER_REGISTRY

`LAYER_REGISTRY.yaml:207-209` has `id_patterns.document` (`TYPE-NN`) and
`id_patterns.element` (`TYPE.NN.SS.xxxx` with 4-hex hash). But threshold
keys use a 3-segment form `PRD.01.perf.redirectp95` that matches NEITHER
pattern. The current `sdd_doc_lint` can't validate threshold-key form
distinctly from element IDs.

**Fix shape:**

1. **Registry** — `framework/registry/LAYER_REGISTRY.yaml` `id_patterns:`
   gains a `threshold` entry:

   ```yaml
   threshold: "^[A-Z]+\\.\\d{2,}\\.[a-z_]+\\.[a-z0-9_]+$"
   ```

   Matches `PRD.01.perf.redirectp95`, `PRD.01.reliability.countstaleness`, etc.

2. **Plugin lint** — `tools/sdd_doc_lint/__init__.py` extends to:
   - Validate `@threshold:KEY` citations against the new regex
   - Flag malformed keys (e.g. `PRD.01.perf.typo!` or `PRD.01.x`) as
     `THRESHOLD-FORM-001` errors
   - Existing TRACE-RES-001 + downstream-skip behavior unchanged

3. **Conformance** — `tests/conformance/test_registry.py` extended to
   verify the new pattern is present + well-formed; new unit test
   `tests/unit/test_threshold_form.py` covers the lint rule.

**Note:** This PR adds the **pattern** + **form check**. The follow-on
**resolution** check (does `@threshold:KEY` actually point to a numeric
value in the host doc) is PR-D's `THRESHOLD-RES-001` rule (items #15+#16).
PR-C ships the pattern; PR-D ships the resolution gate. PR-D depends on
PR-C for this reason (already documented in master plan).

**Touches:** `framework/registry/LAYER_REGISTRY.yaml` (~3 lines),
`tools/sdd_doc_lint/__init__.py` (~30 lines for new rule),
`tests/conformance/test_registry.py` (~10 lines),
`tests/unit/test_threshold_form.py` (new, ~50 lines).

### Item 13 — SPEC + IPLAN element ID exemption (DOCS-ONLY)

The url-shortener review (2026-06-11) noted that `SPEC-01.md` and
`IPLAN-01.md` carry no `SPEC.NN.SS.xxxx` / `IPLAN.NN.SS.xxxx` element
IDs (only upstream refs + Protocol method names). The templates don't
require any.

**Decision (per master plan recommendation):** EXEMPT — formalize the
exemption rather than mandate IDs. The upstream-trace flow already
binds SPEC/IPLAN content to upstream IDs; layer-local element IDs
would be additional complexity for marginal traceability gain.

**Fix shape:** `framework/governance/ID_NAMING_STANDARDS.md` gains a
new subsection "Element-ID exemptions" stating:

- SPEC layer: §5 fail-closed rules and similar policies may, but are
  not required to, carry `SPEC.NN.SS.xxxx` IDs. Upstream `@ears` /
  `@bdd` / `@adr` citations + Protocol method names provide the
  traceability surface.
- IPLAN layer: §4 contracts and step-level operations may, but are
  not required to, carry `IPLAN.NN.SS.xxxx` IDs. Upstream `@spec` /
  `@tdd` citations + file manifest entries provide the traceability
  surface.
- All other layers (BRD, PRD, EARS, BDD, ADR, TDD) MUST carry element
  IDs per template requirements.

**Touches:** `framework/governance/ID_NAMING_STANDARDS.md` (~25 lines
new subsection).

### Item 14 — EARS `@bdd:` downstream slot — formalize as optional

`examples/url-shortener/docs/03_EARS/EARS-01.md` emits per-line
`@bdd: BDD-01` slots (5+ occurrences) — these are downstream pointers,
not upstream lineage. PR #125's TRACE-RES-001 downstream-skip means
they don't fail lint, but they're cosmetic + inconsistent (other
layers don't emit downstream slots).

**Decision:** rather than removing them (which requires SKILL prompt
changes + cascade re-run to verify), **formalize them as optional**
in the necessary-upstream contract. They're harmless given the
downstream-skip lint behavior.

**Fix shape:**

1. **Spec** — `framework/governance/REVIEW_TEAM.md` § (or a new
   `OPTIONAL_SLOTS.md` if cleaner) gains a paragraph clarifying:
   - Per the necessary-upstream contract, only upstream `@<layer>:`
     citations are required + validated
   - Layers may optionally emit downstream `@<layer>:` slots as
     navigation hints; these are skipped by TRACE-RES-001 (per PR #125)
   - Per-layer author SKILLs decide whether to emit; no spec rule
     mandates emission

2. **Audit C-check exemption** — `framework/playbooks/03_EARS/auditor.md`
   (or wherever EARS C-checks live) gains a one-line clarification that
   `@bdd:` per-line slots are optional, not required + not penalized.

3. **Registry** — `LAYER_REGISTRY.yaml` `optional_downstream_slots:`
   new field (per-layer) declaring which downstream layers a layer
   MAY emit slots for. Default empty (most layers); EARS gets `[BDD]`.

**Touches:** `framework/governance/REVIEW_TEAM.md` (~10 lines new
paragraph), `framework/playbooks/03_EARS/auditor.md` (~3 lines),
`framework/registry/LAYER_REGISTRY.yaml` (~5 lines new field).

**Out of scope for this PR:** removing the slots from existing EARS
authoring SKILL prompts. The formalization is sufficient; a future
cleanup PR can remove the slots if desired.

## File structure

### Modified

| Path | Items | Change |
|---|---|---|
| `framework/governance/REVIEW_REMEDIATION_FLOW.md` | #11 | New "Iteration cap" subsection in §The quality loop |
| `framework/governance/ADAPTATION_SURFACE.yaml` | #11 | New `quality_loop.max_iterations` knob |
| `tools/saga_driver.py` | #11 | NEW `.aidoc/profile.yaml` loading (yaml.safe_load + error-path handling for missing-file / malformed / missing-field); read `quality_loop.max_iterations`; fall back to default 3. ~15-20 lines including imports + error handling per Pass 1. |
| `framework/registry/LAYER_REGISTRY.yaml` | #12, #14 | New `threshold` ID pattern; new `optional_downstream_slots` per-layer field |
| `tools/sdd_doc_lint/__init__.py` | #12 | New `THRESHOLD-FORM-001` rule + extend module-import for new registry field |
| `tests/conformance/test_registry.py` | #12 | Verify new pattern + new field |
| `tests/unit/test_threshold_form.py` | #12 | NEW — covers THRESHOLD-FORM-001 rule |
| `framework/governance/ID_NAMING_STANDARDS.md` | #13 | New "Element-ID exemptions" subsection |
| `framework/governance/REVIEW_TEAM.md` | #14 | Paragraph clarifying optional downstream slots |
| `framework/playbooks/03_EARS/auditor.md` | #14 | One-line clarification |
| `framework/VERSION` | — | `0.17.1 → 0.18.0` (MINOR — new governance principle + registry field) |
| `platforms/claude-code-plugin/VERSION` | — | `0.14.1 → 0.15.0` (MINOR — saga driver reads new knob) |
| `platforms/{hermes,claude-code-plugin}/FRAMEWORK_SPEC_VERSION` | — | `0.17.1 → 0.18.0` |
| `CHANGELOG.md` | — | `[Unreleased]` entry above pre-existing CLEANUP-PR-A row |
| `docs/TAGGING.md` | — | New rows for `framework/v0.18.0` + `claude-code-plugin/v0.15.0` |
| `plans/HANDOFF.md` | — | Dated narrative |
| `plans/FRAMEWORK-TODO.md` | — | Move items #11-14 from Open → Closed |

### Created

| Path | Purpose |
|---|---|
| `tests/unit/test_threshold_form.py` | Unit tests for THRESHOLD-FORM-001 rule (item 12) |

## Implementation sequence

### Task 1 — Plan iterative review (this section + Pass 1+)

### Task 2 — Item 11: iteration cap to spec + knob + driver wiring

- Edit REVIEW_REMEDIATION_FLOW.md §The quality loop (new subsection)
- Edit ADAPTATION_SURFACE.yaml (new knob block)
- Edit saga_driver.py: read knob; fall back to 3; constant stays as sentinel
- Add conformance test for new knob

### Task 3 — Item 12: threshold pattern + lint rule

- Edit LAYER_REGISTRY.yaml `id_patterns:` (new `threshold` entry)
- Edit sdd_doc_lint/**init**.py: new THRESHOLD-FORM-001 rule, validates
  `@threshold:` citations against the regex
- Sync vendored copies via `sync-vendored.sh`
- Add unit test for THRESHOLD-FORM-001
- Extend conformance test_registry to verify pattern present + well-formed

### Task 4 — Item 13: ID_NAMING_STANDARDS subsection

- Edit ID_NAMING_STANDARDS.md (new "Element-ID exemptions" subsection)

### Task 5 — Item 14: REVIEW_TEAM paragraph + auditor clarification + registry field

- Edit REVIEW_TEAM.md (new paragraph on optional downstream slots)
- Edit playbooks/03_EARS/auditor.md (one-line clarification)
- Edit LAYER_REGISTRY.yaml `optional_downstream_slots:` field

### Task 6 — Version + sync + docs of record

- `framework/VERSION` `0.17.1 → 0.18.0`
- Plugin VERSION `0.14.1 → 0.15.0`
- Both FRAMEWORK_SPEC_VERSION pointers `0.17.1 → 0.18.0`
- Run `sync-version-refs.sh` (propagates to playbook frontmatter etc.)
- Run `sync-plugin-framework.sh` (mirrors framework bundle)
- Update CHANGELOG / TAGGING / HANDOFF / FRAMEWORK-TODO

### Task 7 — Conformance + lint + unit verification

- `python3 -m unittest discover -s tests/conformance` — expect 121+
  PASS (1 new test from item 12)
- `python3 -m unittest discover -s tests/unit` — expect 44+ PASS
  (1 new test_threshold_form module)
- `python3 -m sdd_doc_lint examples/url-shortener/docs/` — 0
  TRACE-RES-001 + 0 NEW THRESHOLD-FORM-001 (existing thresholds in
  url-shortener corpus should already match the regex; if they don't,
  the regex is wrong)

### Task 8 — Open impl PR (only after Tasks 1-7 all green)

## Out of scope

- THRESHOLD-RES-001 (resolution gate): PR-D's item #16. PR-D depends
  on PR-C for the pattern.
- Removing EARS `@bdd:` slots from existing corpus / SKILL prompts:
  item 14 formalizes them as optional; removal is a future cleanup.
- Backfilling SPEC/IPLAN element IDs to existing artifacts: item 13
  exempts them; no backfill required.
- Hermes-side `saga_orchestrator.py` knob wiring: plugin-first per
  HERMES-BACKLOG.

## Verification

| # | Check | Expected |
|---|---|---|
| 1 | REVIEW_REMEDIATION_FLOW has "Iteration cap" subsection | PASS — manual review |
| 2 | ADAPTATION_SURFACE has `quality_loop.max_iterations` knob | PASS — yaml parse |
| 3 | Saga driver reads knob; fall back to 3 if absent | PASS — unit test |
| 4 | LAYER_REGISTRY has `threshold` ID pattern | PASS — yaml parse + conformance |
| 5 | sdd_doc_lint THRESHOLD-FORM-001 rule fires on malformed keys | PASS — new unit test |
| 6 | url-shortener existing thresholds match new regex (no false positives) | PASS — lint on existing corpus |
| 7 | ID_NAMING_STANDARDS has SPEC+IPLAN exemption subsection | PASS — manual review |
| 8 | REVIEW_TEAM has optional-downstream-slots paragraph | PASS — manual review |
| 9 | LAYER_REGISTRY has `optional_downstream_slots` per-layer field | PASS — yaml parse |
| 10 | Conformance: 121+ PASS (was 120) | PASS |
| 11 | Unit: 44+ PASS (was 43) | PASS |

## Risks & rollback

| Risk | Mitigation |
|---|---|
| `threshold` regex may false-positive on legitimate non-threshold IDs that happen to match the 3-segment pattern | Tune regex to require lowercase categories (`[a-z_]+`) — element IDs use 4-hex hash so won't match; document IDs use `TYPE-NN` so won't match |
| `quality_loop.max_iterations` knob reading may break existing cascades if `.aidoc/profile.yaml` doesn't have the field | Default fallback to 3 (current behaviour) — existing profiles without the knob continue to work |
| ID_NAMING_STANDARDS exemption might be read as "SPEC/IPLAN never have IDs" — should be "MAY have but not required" | Explicit MAY/MUST language in the subsection |
| Framework MINOR bump triggers GATE-SPEC review (CHG required?) | Per existing per-layer rollout pattern, MINOR bumps within the §Playbooks artifact class were PATCH-able; this PR's spec changes (new principle, new registry field) are MINOR-eligible per `docs/PROJECT.md` §2 |

**Rollback:** Single PR. Items are additive — no schema migrations.
`git revert <merge-sha>` restores.

## Review log

> Per CLAUDE.md §"Development workflow" item 2: ≥ 2 review cycles BEFORE
> PR.

### Pass 0 — initial draft

- **Date:** 2026-06-11T21:30:00Z
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review against codebase

- **Date:** 2026-06-11T21:40:00Z
- **Method:** verify every claim against current main (`79b91d0e`,
  post-CLEANUP-PR-A merge). Test the threshold regex against actual
  url-shortener thresholds; verify regex correctly rejects 4-segment
  element IDs; check saga_driver's current profile-loading state;
  confirm ADAPTATION_SURFACE knob-section structure.
- **Findings (1 MEDIUM, 0 MAJOR/HIGH):**
  - **P1-1 (MEDIUM):** Item 11 said "saga_driver reads the knob" as if
    it's a small tweak. Pass 1 grep showed `saga_driver.py` doesn't
    currently load `.aidoc/profile.yaml` at all. This is **new wiring**
    (yaml.safe_load + error-path handling), not a one-line change.
    *Patch:* Item 11 scope note expanded; fallback path must preserve
    current behavior exactly. Adds ~15-20 lines vs the "~10" estimate.
- **Cross-checks clean:**
  - Threshold regex `^[A-Z]+\\.\\d{2,}\\.[a-z_]+\\.[a-z0-9_]+$` matches
    all 5 sampled url-shortener thresholds (`PRD.01.perf.redirectp95`,
    etc.) ✓
  - Same regex correctly REJECTS 4-segment element IDs
    (`BRD.01.07.aaaa`, `EARS.01.03.5066`, `SPEC.01.05.98ff`) — no
    false-match ✓
  - `tests/conformance/test_registry.py` has the right shape to extend
    (existing tests for `id_patterns`, top-level keys, etc.) ✓
  - ADAPTATION_SURFACE `knobs:` section starts at line 35; structure
    is ready to receive the new knob ✓
- **Net structural change:** 1 in-place scope clarification.
- **Status:** Patches folded in. Awaiting Pass 2.

### Pass 2 — re-review of Pass 1 patches

- **Date:** 2026-06-11T21:50:00Z
- **Method:** re-read patched plan; verify Pass 1 patches consistent
  with downstream sections (File structure, Tasks, Verification).
- **Findings (1 MED):**
  - **P2-1 (MEDIUM):** Pass 1 expanded item 11 scope ("new wiring,
    not a one-line change; ~15-20 lines") but the Modified table row
    for `tools/saga_driver.py` still says only "Read profile knob;
    fall back to default 3" without scope estimate. Reader could
    underestimate the LOC. Cosmetic but worth tightening.
    *Patch:* Modified-table row for saga_driver.py expanded with the
    "new yaml.safe_load wiring" note from Pass 1.
- **Cross-checks clean:**
  - Item 11/12/13/14 scope all internally consistent with File
    structure rows ✓
  - Verification rows 1-11 map to expected checks ✓
  - Out of scope correctly defers THRESHOLD-RES-001 (item 16) to PR-D
    - the EARS slot removal to a future cleanup ✓
  - Version impact arithmetic (0.17.1 → 0.18.0 framework; 0.14.1 →
    0.15.0 plugin) consistent with master plan's PR-C "framework
    MINOR floor" ✓
- **Net structural change:** 1 in-place file-structure-row expansion.
- **Status:** Patches folded in.

### Pass 3 — convergence check

- **Date:** 2026-06-11T22:00:00Z
- **Method:** final read-through for any remaining inconsistencies.
- **Findings:** 0 substantive.
- **Verdict (caveat):** self-Pass-3 converged; user-driven review
  on the PR is the real convergence gate (per FRAMEWORK-CLEANUP-001
  Pass 4 lesson).

**Convergence trend:**

| Pass | Found | MAJOR | HIGH | MED | MIN |
|---|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 1 | 0 |
| 2 | 1 | 0 | 0 | 1 | 0 |
| 3 | 0 | 0 | 0 | 0 | 0 |
