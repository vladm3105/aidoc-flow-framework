# NECESSARY-UPSTREAM-001 Implementation Plan

> Framework-level redesign of the per-layer dependency contract. Single PR covering the framework spec + the plugin SKILL behaviors that consume the contract (author + audit + fixer SKILLs, plus the acceptance harness's cumulative-trace assertion).

**Goal:** Replace the framework's cumulative-trace dependency contract with a "necessary upstream + transitive reachability" model — each layer declares only what its own evaluation reads, and lineage to layers further upstream remains discoverable via the @-tag chain rather than redundant redeclaration.

**Origin:** TDD-RT-001 live cascade (2026-06-09) produced TDD-01 with `@prd: PRD.01.13.7760` / `@prd: PRD.01.13.ebf9` referring to a non-existent `docs/02_PRD/PRD-01.md`. The TDD auditor C1 correctly diagnosed this as trace fabrication (2 × P1), the fixer correctly refused to silently delete the tags (would contaminate the test fixture), the saga ended at `PARTIAL_TIMEOUT` in iter-3 (5407s of 5400s budget) — the fixer had explicitly reached a fixed point at iter-2 (`0 files modified`) because the only blocking findings required either generating PRD-01.md or removing trace claims the doc itself asserted as required, neither of which is in the fixer's surface. Root cause: `framework/registry/LAYER_REGISTRY.yaml` mandates `TDD.required_tags: [brd, prd, ears, bdd, adr, spec]`, forcing the TDD author SKILL to emit `@prd:` and `@brd:` tags even though no TDD playbook lens consumes PRD or BRD content. The framework's @-tag *mechanism* is fine; the framework's @-tag *contract* over-demands. See [`TDD-RT-001-PLAN.md`](TDD-RT-001-PLAN.md) for the failed cascade evidence.

---

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | NECESSARY-UPSTREAM-001                      |
| Type           | refactor (framework spec contract + plugin SKILL behavior) |
| Status         | DRAFT — 2026-06-09T20:00:00Z (Pass 1 patched 22:00; Pass 2 patched 22:30; Pass 3 patched 23:00) |
| Depends on     | TDD-RT-001 (paused, branch `feat/tdd-rt-001`) |
| Feeds          | Re-run of TDD-RT-001 cascade; future per-layer regenerations; IPLAN-RT-001 (task #268) authors IPLAN playbooks to the new contract from the start |
| Worktree       | `feat/necessary-upstream-001` at `/opt/data/aidoc-flow/framework-necessary-upstream-001/` (per [[feedback_plans_live_in_owning_submodule]] + the worktree-isolation pattern from SPEC-RT-001) |
| Version impact | framework MINOR (0.15.2 → 0.16.0) — adaptation-surface contract change. Plugin MINOR (0.12.0 → 0.13.0) — 7 layer-author SKILLs drop cumulative-tag instructions. |
| GATE-SPEC      | Triggers (per `docs/PROJECT.md` §6 — framework/** change requires SPEC review). Plan documents the contract change end-to-end so the gate can pass on first submission. |

## Objective

Make every layer's declared `required_tags` and `upstream_artifacts:` match what that layer's audit playbook lenses actually read. Stop forcing downstream layers to redeclare every preceding layer as a direct dependency. Preserve full transitive lineage through the @-tag chain plus a one-shot walk tool.

## Scope

**In:**

1. Re-specify `framework/registry/LAYER_REGISTRY.yaml` `required_tags` + `can_reference` per the necessary-upstream table (below).
2. Re-specify each `<X>-TEMPLATE.yaml`'s §7 Traceability block to list only the necessary `<x>_references:` slots. Index templates (`<LAYER>-00_index.TEMPLATE.md`) carry transitive-chain prose ("BRD → PRD → … → Code") which stays accurate and is **not** modified.
3. Re-specify auditor.md C1 in the **4 layers that have an auditor lens with a trace-resolution C1** — PRD, BDD, ADR, TDD. C1 must validate only tags within the new minimal `required_tags` set, AND any emitted `@-tag` whose target is unresolvable is P1 regardless of whether it was declared. (BRD's auditor C1 is about ID conformance, not trace — unchanged. EARS/SPEC have no auditor lens — handled by Task 4b.)
4. Add a `sdd_doc_lint` trace-resolution check that runs at every layer (including EARS/SPEC where no auditor lens exists, and at all 5 auditor-lens layers as a deterministic structural floor). This gives uniform enforcement regardless of crew shape.
5. Update **15 plugin SKILLs** that carry hardcoded cumulative-trace references: 7 layer-author SKILLs (`doc-prd`/`doc-ears`/`doc-bdd`/`doc-adr`/`doc-spec`/`doc-tdd`/`doc-iplan`) drop "cumulative upstream tags" instructions, and 8 layer audit/fixer SKILLs (`doc-ears-audit`, `doc-ears-fixer`, `doc-bdd-audit`, `doc-bdd-fixer`, `doc-adr-fixer`, `doc-spec-audit`, `doc-spec-fixer`, `doc-iplan-fixer`) drop cumulative-tag wording — the author emits only the tags required by the registry's `required_tags` for that layer; fixers add missing required tags but never synthesize tags upstream of the necessary set.
5b. Update `tests/scripts/test-acceptance.sh` validator probe — drop "cumulative" prompt wording, lower the expected count threshold from 20 to a registry-derived value.
6. Replace cumulative-trace prose in `framework/governance/REVIEW_TEAM.md` + update `framework/governance/ADAPTATION_SURFACE.yaml` `cascade_rule` to reflect the new default (necessary-upstream baseline; disabling a skippable layer further shrinks it).
7. Add `tools/trace_walk.py` (≤ 100 LOC, stdlib only) — one-shot transitive walker so the "find every artifact tracing back to BRD-NN" workflow stays a single command.
8. Add `tests/conformance/test_layer_registry_necessary_upstream.py` — asserts registry matches the necessary-upstream table; asserts each layer's `§7 Traceability` block lists only the necessary slots.
9. Add `tests/unit/test_sdd_doc_lint_trace_resolution.py` + `tests/unit/test_trace_walk.py`.
10. Bump `framework/VERSION` 0.15.2 → 0.16.0 (MINOR — adaptation-surface contract change per `framework/governance/ADAPTATION_SURFACE.yaml` `traceability` row) **and** `platforms/claude-code-plugin/VERSION` 0.12.0 → 0.13.0 (MINOR — 7 SKILL behavior changes).
11. Re-run live TDD cascade from `feat/tdd-rt-001` worktree to verify the failed cascade converges under the new contract.

**Out of scope (deferred):**

- Hermes mirror updates — plugin-first per [[feedback_plugin_first_then_hermes]]; Hermes pickup tracked in `plans/HERMES-BACKLOG.md`.
- IPLAN-layer auditor.md authoring + IPLAN playbooks (5–6 files) — `framework/playbooks/08_IPLAN/` does not yet exist; that work belongs to **IPLAN-RT-001 (task #268)**, which will author the IPLAN playbooks **to the new contract from the start**. Bundling them here is speculative scope and would couple two independent rollouts.
- Regenerating the already-merged url-shortener artifacts to the new minimal form — they remain valid under the new contract (their declared tags still resolve), and next-time regeneration adopts the new form naturally. Forced regeneration is speculative scope.
- Adding a graphical dependency-visualization tool — speculative; `trace_walk.py` covers the concrete need.
- Adding `DOC_GOVERNANCE_CORE.md` Principle 9 — the principle is sufficiently encoded in the REVIEW_TEAM.md update; a separate principle doc is speculative.
- Changing the 8-layer sequence itself (BRD → … → IPLAN) — unchanged.
- Changing crew weights, lens-to-agent mappings, or lens playbook *content* — all 39 currently-authored lens playbooks already author Cn checks correctly under this model (no Cn check at ADR depth or below reads BRD or PRD content; the registry was the misalignment, not the playbooks).

## The principle

> **Necessary upstream + transitive reachability.** A layer's `required_tags` and `upstream_artifacts:` declare what its own evaluation reads. Lineage to layers further upstream is discoverable transitively through the @-tag chain (one hop per layer) and through `tools/trace_walk.py` for one-shot queries. Enforcement is split: **`sdd_doc_lint`** (deterministic structural floor, runs at every layer) flags any emitted `@-tag` whose target is unresolvable on disk as a lint error; **auditor C1** (content layer; lives at PRD, BDD, ADR, TDD where the lens exists) additionally checks that the resolved element semantically supports the citation — not just that it exists. Unresolvable tags are always errors; non-required tags emitted as decorative lineage are permitted as long as they resolve.

## The necessary-upstream table

| Layer | `required_tags` (new) | `can_reference` (new) | Rationale (which playbook lens reads this) |
|---|---|---|---|
| BRD | `[]` | `[]` | root |
| PRD | `[brd]` | `[BRD]` | every PRD lens reads BRD context |
| EARS | `[prd]` | `[PRD]` | EARS SHALLs derive from PRD features; BRD reachable via PRD |
| BDD | `[ears]` | `[EARS]` | scenarios encode EARS SHALLs |
| ADR | `[ears, bdd]` | `[EARS, BDD]` | architect / security lenses cite EARS (requirements) + BDD (scenarios needing architectural support) |
| SPEC | `[ears, bdd, adr]` | `[EARS, BDD, ADR]` | architect / tech_lead / integration_lead cite EARS + BDD + ADR; no SPEC lens cites BRD or PRD |
| TDD | `[ears, bdd, adr, spec]` | `[EARS, BDD, ADR, SPEC]` | qa_lead C1 (BDD pairing), tech_lead C1 (SPEC interfaces), security_engineer C1 (BDD authn) + C2-C4 (SPEC interfaces / crypto), operator C2 (ADR reversibility); no TDD lens cites BRD or PRD |
| IPLAN | `[spec, tdd]` | `[SPEC, TDD]` | implementation order derives from SPEC component decomposition + TDD test-first sequence |

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tools/trace_walk.py` | One-shot transitive @-tag walker (`trace_walk.py <ARTIFACT> --to <LAYER>`). Stdlib only, ≤ 100 LOC, one positional arg + one optional flag. |
| `tests/conformance/test_layer_registry_necessary_upstream.py` | Asserts registry matches the necessary-upstream table; asserts each `<X>-TEMPLATE.yaml`'s §7 Traceability block lists only the necessary `<x>_references:` slots. |
| `tests/unit/test_sdd_doc_lint_trace_resolution.py` | Fixture-driven: lint surfaces error on @-tag referencing missing file; surfaces error on @-tag with element ID not present in target file; passes when all tags resolve. |
| `tests/unit/test_trace_walk.py` | 3-layer fixture corpus; walk emits expected chain; non-zero exit on broken chain. |

### Modified

| Path | Change |
| ---- | ------ |
| `framework/registry/LAYER_REGISTRY.yaml` | Shrink `required_tags` + `can_reference` per the necessary-upstream table above. |
| `framework/layers/02_PRD/PRD-TEMPLATE.yaml` | §7 Traceability: keep `brd_references` only. `_guidance` prose unchanged (cross-layer guidance stays valid). |
| `framework/layers/03_EARS/EARS-TEMPLATE.yaml` | §7: keep `prd_references` only. |
| `framework/layers/04_BDD/BDD-TEMPLATE.yaml` | §7: keep `ears_references` only. |
| `framework/layers/05_ADR/ADR-TEMPLATE.yaml` | §7: keep `ears_references` + `bdd_references` only. |
| `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` | §7: keep `ears_references` + `bdd_references` + `adr_references` only. |
| `framework/layers/07_TDD/TDD-TEMPLATE.yaml` | §7: keep `ears_references` + `bdd_references` + `adr_references` + `spec_references` only. (Already drops brd/prd at TDD-TEMPLATE.yaml:266 — completing the alignment.) |
| `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | §7: keep `spec_references` + `tdd_references` only. |
| `framework/playbooks/02_PRD/auditor.md` | C1 wording — validate only `@brd:` tags within the new minimal `required_tags`; unresolvable tag at any depth → P1. |
| `framework/playbooks/04_BDD/auditor.md` | C1 wording — validate only `@ears:` tags. |
| `framework/playbooks/05_ADR/auditor.md` | C1 wording — validate `@ears:` + `@bdd:` tags (drop brd/prd from the required check). |
| `framework/playbooks/07_TDD/auditor.md` | C1 wording — validate `@ears:` + `@bdd:` + `@adr:` + `@spec:` tags (drop brd/prd from the required check; harmonize with the new contract). |
| `framework/playbooks/01_BRD/auditor.md` | **Unchanged** — BRD's C1 is ID conformance, not trace resolution (BRD is the root). |
| `platforms/claude-code-plugin/sdd_doc_lint/__init__.py` (or new rule module) | New lint rule `TRACE-RES-001`: each `@<layer>: <ID>` tag in the document resolves against the corresponding file + element ID; non-resolution = lint error. Runs uniformly at every layer including EARS/SPEC/IPLAN. |
| `platforms/claude-code-plugin/skills/doc-prd/SKILL.md` | Drop "cumulative upstream tags" instructions; the author emits only the tags required by registry. |
| `platforms/claude-code-plugin/skills/doc-ears/SKILL.md` | Same. |
| `platforms/claude-code-plugin/skills/doc-bdd/SKILL.md` | Same. |
| `platforms/claude-code-plugin/skills/doc-adr/SKILL.md` | Same. |
| `platforms/claude-code-plugin/skills/doc-spec/SKILL.md` | Same. |
| `platforms/claude-code-plugin/skills/doc-tdd/SKILL.md` | Same. 6 hardcoded "cumulative" references confirmed at lines 12, 80, 122, 138, 153, 189 — all must change. |
| `platforms/claude-code-plugin/skills/doc-iplan/SKILL.md` | Same. |
| `platforms/claude-code-plugin/skills/doc-ears-audit/SKILL.md` | Reword "cumulative-tag coverage" reporting language → "trace-resolution coverage" (informational; no behavior change). |
| `platforms/claude-code-plugin/skills/doc-ears-fixer/SKILL.md` | Rewrite Phase-N table row instructing addition of cumulative tags as remediation → "add tags missing from registry's `required_tags` for this layer." |
| `platforms/claude-code-plugin/skills/doc-bdd-audit/SKILL.md` | Same wording change as doc-ears-audit. |
| `platforms/claude-code-plugin/skills/doc-bdd-fixer/SKILL.md` | Same wording change as doc-ears-fixer (line 243). |
| `platforms/claude-code-plugin/skills/doc-adr-fixer/SKILL.md` | Same wording change as doc-ears-fixer. |
| `platforms/claude-code-plugin/skills/doc-spec-audit/SKILL.md` | Same wording change as doc-ears-audit (line 473). |
| `platforms/claude-code-plugin/skills/doc-spec-fixer/SKILL.md` | Same wording change as doc-ears-fixer (line 248). |
| `platforms/claude-code-plugin/skills/doc-iplan-fixer/SKILL.md` | Same wording change as doc-ears-fixer. |
| `tests/scripts/test-acceptance.sh` | Line 1523 — rewrite `doc-validator` probe prompt (drop "cumulative"; switch to resolution-only check); lower expected-count threshold from 20 to a registry-derived value (≥ 10). |
| `framework/governance/REVIEW_TEAM.md` | New subsection "Necessary upstream + transitive trace" (~30 lines); deprecates cumulative-trace prose. |
| `framework/governance/ADAPTATION_SURFACE.yaml` | `cascade_rule` — restate that the new default is the necessary-upstream baseline; disabling a skippable layer further shrinks it (semantics already correct, baseline statement updates). |
| `framework/VERSION` | 0.15.2 → 0.16.0 |
| `platforms/claude-code-plugin/VERSION` | 0.12.0 → 0.13.0 (7 layer-author SKILLs modified — MINOR per SemVer). |
| `CHANGELOG.md` (root) | `[Unreleased]` entry — framework spec MINOR + plugin MINOR; explain the contract change + rollback safety + the failed TDD-RT-001 cascade that motivated it. |
| `ROADMAP.md` | "Shipped" bullet under framework v0.16.0 + plugin v0.13.0. |
| `plans/HANDOFF.md` | Dated narrative — paused TDD-RT-001 awaiting this PR; re-run after merge. |
| `docs/TAGGING.md` | Two new rows: `framework/v0.16.0` and `claude-code-plugin/v0.13.0` documenting NECESSARY-UPSTREAM-001. |

**Not modified** (verified during Pass 1):

- `framework/layers/<L>/<L>-00_index.TEMPLATE.md` — these carry only one-line transitive-chain prose ("BRD → PRD → … → Code") which stays accurate under the new model.
- `framework/layers/01_BRD/BRD-TEMPLATE.yaml` — BRD §7 has no upstream block (BRD is root); only `cross_links` for sibling BRDs, untouched.
- 39 currently-authored lens playbook files OTHER than the 4 auditor.md edited above — no Cn check at ADR depth or below cites BRD or PRD content; playbooks are already correct under the new model. (Verified during plan drafting against the 6 freshly-authored TDD playbooks.)

## Implementation sequence

### Task 1: Plan two-cycle review (NO code yet)

- Pass 1: self-review against this draft — surface every gap (over-specification, missing layers, principle ambiguity, verification gaps). Patch in place.
- Pass 2: re-review the patched draft — confirm no new inconsistencies introduced. If Pass 2 surfaces material gaps, run Pass 3.
- Plan PR opens only when a pass surfaces zero substantive gaps. Implementation begins ONLY after that PR is merged.

### Task 1b — Setup (one-time, before any code work): create the worktree

- `git worktree add -b feat/necessary-upstream-001 /opt/data/aidoc-flow/framework-necessary-upstream-001 origin/main`
- All Task 2-9 work happens inside this worktree. The TDD-RT-001 worktree at `/opt/data/aidoc-flow/framework-tdd-rt-001/` stays paused at its current state (5 commits ahead of main) — it will be reworked AFTER NECESSARY-UPSTREAM-001 merges to main (see Task 9 rebase note).

### Task 2: Update `framework/registry/LAYER_REGISTRY.yaml`

- Apply the necessary-upstream table to every layer's `required_tags` and `can_reference`.
- **Existing test that asserts the old shape (Pass 3 finding P3-9):** `tests/conformance/test_registry.py:63` `test_required_tags_are_cumulative` literally encodes the cumulative invariant. Rename → `test_required_tags_match_necessary_upstream_table`; rewrite to assert the new table; the sibling test `test_can_reference_matches_required_tags` (line 69) is structural ("can_reference = required_tags in uppercase") and stays valid unchanged.
- **Test-first — [CODE]:** write `tests/conformance/test_layer_registry_necessary_upstream.py` (a NEW file, additional to the rewritten test in `test_registry.py`); assert each layer template's §7 Traceability block lists only the necessary `<x>_references:` slots (assertion not currently covered anywhere); confirm it fails against the current cumulative templates; then update the templates per Task 3 and assert it passes.

### Task 3: Update 7 layer templates' §7 Traceability blocks

- One PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN template at a time; verify the §7 block lists only the necessary `<x>_references:` slots after each edit. `_guidance` prose stays intact (cross-layer guidance prose remains valid under the new contract).
- The conformance test from Task 2 covers this — green when all 7 templates are correct.

### Task 4: Update auditor.md C1 across 4 layers

- **Scope:** PRD, BDD, ADR, TDD only (the 4 layers with both an auditor lens AND a trace-resolution C1). BRD's C1 is ID conformance, not trace — unchanged. EARS / SPEC have no auditor lens — handled by Task 4b. IPLAN's auditor.md doesn't yet exist — to be authored under IPLAN-RT-001 to the new contract from the start.
- **Wording change:** each C1 currently enforces "Every `@brd:` / `@prd:` / `@ears:` / `@bdd:` / `@adr:` / `@spec:` tag resolves to an element ID." The change is to validate **only the tags within `required_tags`** as required citations; any tag OUTSIDE that set is permitted (decorative lineage) but still must resolve if emitted (unresolved = P1).
- C1 line numbers (verified Pass 1): PRD line 43, BDD line 48, ADR line 51, TDD line 55.
- **Test-first — [CODE]:** extend `tests/unit/test_finding_check_field.py` (existing) with assertions about C1 wording per layer; confirm new wording is present after the edits.

### Task 4b: Add `sdd_doc_lint` trace-resolution rule (new)

- Add lint rule `TRACE-RES-001` to `platforms/claude-code-plugin/sdd_doc_lint/`: every `@<layer>: <ID>` tag in the document is resolved against the corresponding file + element ID; non-resolution = `error` level finding. Runs uniformly at every layer including EARS / SPEC / IPLAN where no auditor lens exists. Backs the structural floor.
- **Excluded artifacts:** index documents (`artifact_type: BRD-INDEX`, `PRD-INDEX`, etc.) — they don't carry trace tags by design. Per task #239 history, the lint already special-cases index docs; the new rule inherits the exclusion. (Pass 3 finding P3-1.)
- The rule is deterministic and registry-aware (`sdd_doc_lint` already loads `LAYER_REGISTRY.yaml`).
- **Test-first — [CODE]:** add `tests/unit/test_sdd_doc_lint_trace_resolution.py` — fixture documents with (a) all tags resolving (pass), (b) tag referencing missing file (error), (c) tag with element ID not present in target file (error), (d) index doc with no trace tags (pass — exclusion check). Modeled after the existing `test_sdd_doc_lint_struct01.py` shape.

### Task 4c: Update 7 layer-author SKILLs (plugin)

- `doc-prd/SKILL.md`, `doc-ears/SKILL.md`, `doc-bdd/SKILL.md`, `doc-adr/SKILL.md`, `doc-spec/SKILL.md`, `doc-tdd/SKILL.md`, `doc-iplan/SKILL.md`.
- Each SKILL currently instructs the author to emit "cumulative upstream tags" (e.g., `doc-tdd/SKILL.md` lines 12, 80, 122, 138, 153, 189 carry six redundant cumulative-tag references). The change: the author emits ONLY the tags required by the registry's `required_tags` for that layer; transitive lineage is reachable via `trace_walk.py`, not redeclared.
- The SKILL frontmatter `upstream_artifacts` field is rewritten to the new minimal set.

### Task 4d: Update 8 layer audit/fixer SKILLs (plugin)

- Pass 2 sweep found 8 audit/fixer SKILLs with cumulative-trace references that need updating:
  - `doc-ears-audit/SKILL.md`, `doc-ears-fixer/SKILL.md`
  - `doc-bdd-audit/SKILL.md`, `doc-bdd-fixer/SKILL.md`
  - `doc-adr-fixer/SKILL.md`
  - `doc-spec-audit/SKILL.md`, `doc-spec-fixer/SKILL.md`
  - `doc-iplan-fixer/SKILL.md`
- Two distinct patterns:
  - **Informational** (audit SKILLs at SPEC, BDD, EARS): report-shape descriptions referencing "cumulative-tag coverage" — reword to "trace-resolution coverage."
  - **Load-bearing** (fixer SKILLs at SPEC line 248, BDD line 243, EARS, ADR, IPLAN): table rows instructing the fixer to "add missing cumulative tags (`@brd @prd @ears @bdd @adr`)" as remediation — rewrite to "add missing tags from the registry's `required_tags` for this layer; do not synthesize tags upstream of the necessary set."
- 4 SKILLs scanned clean (no hits): `doc-brd-audit`, `doc-brd-fixer`, `doc-prd-audit`, `doc-prd-fixer`, `doc-adr-audit`, `doc-tdd-audit`, `doc-tdd-fixer`, `doc-iplan-audit` (doesn't exist).

### Task 4e: Update acceptance harness validator probe

- `tests/scripts/test-acceptance.sh:1523` instructs the `doc-validator` SKILL: "Validate **cumulative** @brd…@tdd traceability across the chain... Enumerate every resolved tag." Expected count threshold: 20 resolved trace tags.
- Both the prompt and the count threshold are now wrong under the new contract:
  - Prompt: rewrite to "Validate every emitted @-tag resolves to an existing element on disk across the chain." Drop "cumulative."
  - Threshold: derive from the necessary-upstream table at probe time, not hardcoded. Sum the `required_tags` counts of every layer present in `$chain_dir` — that's the minimum number of distinct `@<layer>: <ID>` *citations* the validator must enumerate. Each cited element typically appears 2–3× in the document (cumulative header + §7 + body); the runtime threshold is `2 × Σ required_tags[L]` (a conservative floor that allows for additional decorative-but-resolvable lineage). For url-shortener (no IPLAN, no PRD): `2 × (0+1+1+2+3+4) = 22`. Codified as: derive in shell at probe time by reading the registry — do not hardcode (avoids future bit-rot when active_layers shifts).

### Task 5: Update REVIEW_TEAM.md + ADAPTATION_SURFACE.yaml narrative

- `REVIEW_TEAM.md`: add subsection "Necessary upstream + transitive trace" between §Operations and §Resilience (~30 lines). Mark cumulative-trace prose as deprecated; cross-reference the new subsection.
- `ADAPTATION_SURFACE.yaml`: restate `cascade_rule` so the new default baseline (necessary-upstream per the table) is the starting point; disabling a skippable layer still further shrinks it. Semantics already correct — only the baseline statement needs alignment.

### Task 6: Add `tools/trace_walk.py`

- ≤ 100 LOC stdlib-only Python; one positional arg (artifact ID like `TDD-01`), optional `--to <LAYER>`. Walks @-tags transitively (BFS over the layer DAG); emits ALL reachable ancestors (the DAG closure, not a single path) with their hop-distance. Returns non-zero on any unresolvable tag encountered during the walk.
- **Algorithm (specified to avoid ambiguity — Pass 3 finding P3-5):** Under the new contract a layer can have multiple direct upstream layers (e.g., TDD → {EARS, BDD, ADR, SPEC}), so the walk is a DAG closure, not a single chain. Output format: `<artifact-id> --[hop-N]--> <ancestor-id>` lines, sorted by hop, then by ancestor-id alphabetically. With `--to <LAYER>`, filter output to ancestors at or above that layer.
- **Test-first — [CODE]:** `tests/unit/test_trace_walk.py` — fixture corpus with 3 layers; assert walk emits every expected ancestor (set comparison, not ordered chain); assert hop counts; assert non-zero exit on broken chain.

### Task 7: Version + docs of record

- Bump `framework/VERSION` 0.15.2 → 0.16.0 AND `platforms/claude-code-plugin/VERSION` 0.12.0 → 0.13.0; the mechanical doc-sync hook propagates into `plugin.json`, `marketplace.json`, 52 × SKILL.md frontmatter, both `README.md` files, `docs/SKILL_AUTHORING.md`, `docs/PARITY.md` current-state row, all playbook frontmatters, `FRAMEWORK_SPEC_VERSION` in both platforms.
- Manual updates: root `CHANGELOG.md` `[Unreleased]` entry (framework MINOR + plugin MINOR); `ROADMAP.md` shipped bullet; `plans/HANDOFF.md` dated narrative; `docs/TAGGING.md` two new rows (`framework/v0.16.0`, `claude-code-plugin/v0.13.0`).

### Task 8: Conformance + lint

- `env -u LD_LIBRARY_PATH pre-commit run --all-files`
- `python3 -m unittest discover -s tests/conformance -v` — expected 119/119 PASS (118 existing + 1 new conformance test).
- `python3 -m unittest discover -s tests/unit -v` — expected current count + 2 (test_trace_walk, test_sdd_doc_lint_trace_resolution).

### Task 9: Re-run failed TDD cascade

- From the `feat/tdd-rt-001` worktree (`/opt/data/aidoc-flow/framework-tdd-rt-001/`), after this PR merges to main, fetch + rebase, then re-run:
  `bash tests/scripts/test-acceptance.sh url-shortener --live --phase=cascade --from-layer=tdd --to-layer=tdd`
- Expected outcome: TDD-01 drafted with `upstream_artifacts: [EARS-01, BDD-01, ADR-01, SPEC-01]`, no `@prd:` / `@brd:` cumulative tags, iter-1 PASS, content_score ≥ 90, saga CLOSED. The earlier 2 × P1 auditor findings vanish — exactly the diagnostic check that the failed cascade was a structural defect, not a calibration miss.
- **Why TDD-only (Pass 3 finding P3-3):** BRD/PRD/EARS/BDD/ADR/SPEC per-layer cascades all passed under cumulative trace with no unresolvable-tag findings; the SKILL changes in Tasks 4c+4d are deterministic *removals* (drop the synthesis of `@brd:` / `@prd:` at layers that don't need them). Under the new contract, the artifacts will emit fewer trace tags, all of which resolve. The TRACE-RES-001 lint rule (Task 4b) catches any residual cumulative emission at any layer; the live TDD cascade is the integration check that catches both the SKILL behavior change AND the registry+template+playbook chain end-to-end. Per-layer cascades for EARS/BDD/ADR/SPEC are deferred to the natural next regeneration cycle (not gated by this PR).
- **TDD-RT-001 rebase note:** TDD-RT-001's commits modify `doc-tdd-audit/SKILL.md` + `doc-tdd-fixer/SKILL.md` + 6 new TDD playbooks + framework 0.15.1→0.15.2 version bump. NECESSARY-UPSTREAM-001 does **not** touch `doc-tdd-audit` / `doc-tdd-fixer` (0 cumulative hits, verified Pass 2). Conflicts will appear in: `framework/VERSION` (0.15.1→0.15.2 vs 0.15.2→0.16.0 — drop the TDD-RT-001 bump commit; re-bump from 0.16.0 → 0.16.1 PATCH for the 6 added TDD playbooks instead) and propagated sync-hook outputs (resolved by re-running `scripts/sync-version-refs.sh`). Rebase strategy decided in TDD-RT-001's follow-up commit, not here.

### Task 10: Open PR (only after Tasks 1-9 all green)

- Submit-only-final per [[feedback_submit_only_final]] — local two-cycle review (Task 1) + green conformance (Task 8) + green TDD cascade (Task 9) MUST be in place before the PR opens.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| 1 | `python3 -m unittest tests.conformance.test_layer_registry_necessary_upstream` | PASS | Task 2 |
| 2 | `python3 -m unittest tests.unit.test_finding_check_field` (extended) | PASS | Task 4 |
| 3 | `python3 -m unittest tests.unit.test_sdd_doc_lint_trace_resolution` | PASS | Task 4b |
| 4 | `python3 -m unittest tests.unit.test_trace_walk` | PASS | Task 6 |
| 5 | `python3 -m unittest discover -s tests/conformance` | 119/119 (118 existing + 1 new) | Task 8 |
| 6 | `python3 -m unittest discover -s tests/unit` | current count + 2 new | Task 8 |
| 7 | `env -u LD_LIBRARY_PATH pre-commit run --all-files` | PASS | Task 8 |
| 8 | Cascade re-run from `feat/tdd-rt-001` (Task 9) | TDD-01 saga CLOSED, content_score ≥ 90, no unresolvable @-tags, `upstream_artifacts: [EARS-01, BDD-01, ADR-01, SPEC-01]` (no BRD/PRD) | Task 9 |
| 9 | `tools/trace_walk.py TDD-01 --to EARS` on the regenerated TDD-01 | Output set contains `{EARS-01, BDD-01, ADR-01, SPEC-01}` (4 direct ancestors of TDD under the new model); order-independent set membership check; exit code 0 | Task 6 + Task 9 |

## Risks & rollback

| Risk | Mitigation |
|---|---|
| New `sdd_doc_lint` TRACE-RES-001 rule fails an existing already-merged artifact whose declared tags happen to be unresolvable on disk | All currently-merged artifacts were generated against a known-complete upstream (full url-shortener cascade run pre-TDD-RT-001). Manual pre-merge spot-check: run `tools/trace_walk.py` against every artifact ID on main (BRD-01, PRD-01, EARS-01, BDD-01, ADR-01, SPEC-01) — non-zero exit on any artifact indicates an unresolvable tag and blocks this PR. (Per Task 6 spec, the walker exits non-zero on any unresolvable tag; the `--to` flag is irrelevant for exit-code checking.) If any pre-existing artifact fails, regenerate it via cascade (per [[feedback_never_hand_edit_example_artifacts]]) BEFORE this PR opens. |
| `trace_walk.py` over-scope creep | Hard cap: stdlib only, ≤ 100 LOC, one positional arg + one optional flag. Listed in Out-of-scope items if scope grows. |
| Missed a hardcoded cumulative-tag site in the SKILL sweep (Task 4c+4d) → plugin still emits unresolvable tags | The TRACE-RES-001 lint rule from Task 4b catches residue at the structural floor (every cascade-generated artifact passes through lint). The Task 9 live cascade re-run is the integration check — any missed SKILL surfaces as a lint error there, before the PR opens. |
| The acceptance harness's `doc-validator` probe (`tests/scripts/test-acceptance.sh:1523`) still expects ≥ 20 cumulative resolved tags | Updated in Task 4e — the probe now uses a registry-aware expected count (≤ count of `required_tags[layer]` per `LAYER_REGISTRY.yaml`); the validator prompt drops the word "cumulative" and instructs resolution-only checking. |
| Forgot a layer / template / playbook in the sweep | Conformance test in Task 2 enumerates every layer from the registry and asserts each layer's template + auditor playbook (where it exists) match the new contract; CI fails immediately if any layer drifts. The SKILL sweep is enumerated explicitly in Task 4c/4d/4e (15 SKILL files + 1 harness file by name) — no implicit "all layers" claim. |

**Rollback:** Single-PR, single-VERSION-bump unit. Revert is one `git revert <merge-sha>`. Re-merged artifacts that adopted the new minimal form remain valid under the restored cumulative contract too (cumulative is a superset; adding back the redundant tags would happen on next regeneration, but already-merged artifacts don't fail validation under cumulative because their declared tags still resolve).

## Out of scope (deferred, one-line each)

- Hermes mirror — tracked in `plans/HERMES-BACKLOG.md`
- Forced regeneration of already-merged url-shortener artifacts
- Graphical dependency visualizer
- `DOC_GOVERNANCE_CORE.md` Principle 9 codification
- 8-layer sequence reshape
- Crew-weight or lens-to-agent reassignment
- IPLAN auditor.md + IPLAN lens playbooks — authored under IPLAN-RT-001 (task #268) to the new contract from the start
- Lens playbook content rewrites — 39 currently-authored lens playbooks (excluding the 4 auditor.md C1 edits in Task 4) already align with the new model (verified Pass 2: zero `@brd:` / `@prd:` citations in ADR/SPEC/TDD non-auditor playbooks)

## Review log

> Per CLAUDE.md §"Development workflow" item 2: this plan MUST complete ≥ 2 full review cycles BEFORE the plan PR opens. Each cycle = *review → patch → re-review*. Continue until a cycle surfaces zero substantive gaps.

### Pass 0 — initial draft

- **Date:** 2026-06-09T20:00:00Z
- **Drafted from:** TDD-RT-001 cascade failure analysis (this conversation).
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review

- **Date:** 2026-06-09T22:00:00Z
- **Method:** cross-check every claim in the draft against the actual codebase (registry, templates, playbooks, lint, tests/, plugin SKILLs).
- **Findings (12 substantive gaps, 5 MAJOR / 5 MEDIUM / 2 MINOR):**
  - **G1 (MAJOR):** Auditor lens exists only at 5 layers (BRD, PRD, BDD, ADR, TDD), not 7. EARS, SPEC, IPLAN have no auditor lens.
    *Patch:* Task 4 scope reduced to PRD/BDD/ADR/TDD; introduced Task 4b (sdd_doc_lint trace-resolution rule, runs at every layer including EARS/SPEC).
  - **G2 (MAJOR):** Wrong test file name (`test_playbook_check_schema.py` doesn't exist).
    *Patch:* Replaced with `tests/unit/test_finding_check_field.py` (extension target) + new `tests/unit/test_sdd_doc_lint_trace_resolution.py`.
  - **G3 (MAJOR):** Lens-playbook count "47" → actual 39.
    *Patch:* Count corrected in Out-of-scope.
  - **G4 (MAJOR):** IPLAN has no playbooks (task #268 pending).
    *Patch:* IPLAN authoring explicitly deferred to IPLAN-RT-001; that plan will author IPLAN playbooks to the new contract from the start.
  - **G5 (MAJOR):** Misframed — auditor C1 ALREADY enforces trace resolution; the defect is inconsistency in *which* upstream layers each C1 checks, not absence of the check.
    *Patch:* Task 4 wording rewritten as "harmonize C1 to the new minimal required set," not "introduce a new check."
  - **G6 (MEDIUM):** `ADAPTATION_SURFACE.yaml` `cascade_rule` references `required_tags`; needs alignment with the new baseline.
    *Patch:* Added to Modified table; Task 5 updates it alongside REVIEW_TEAM.md.
  - **G7 (MINOR):** Index templates carry only one-line transitive-chain prose, not a §7 block.
    *Patch:* "Not modified" subsection added; index templates explicitly unchanged.
  - **G8 (MAJOR):** TDD author SKILL hardcodes "cumulative upstream tags" in 6 places. Registry+template change alone is insufficient. Same applies to 6 sibling layer-author SKILLs.
    *Patch:* New Task 4c (update 7 layer-author SKILLs); plugin VERSION bump 0.12.0 → 0.13.0 added to metadata + Modified table + Task 7.
  - **G9 (MEDIUM):** No worktree specified.
    *Patch:* `feat/necessary-upstream-001` at `/opt/data/aidoc-flow/framework-necessary-upstream-001/` added to metadata.
  - **G10 (MINOR):** GATE-SPEC trigger not stated.
    *Patch:* Added to metadata table.
  - **G11 (MEDIUM):** PRD-TEMPLATE `_guidance` prose status unclear.
    *Patch:* Task 3 explicitly notes `_guidance` prose stays intact.
  - **G12 (MINOR):** Risk-table doc-`<layer>`-fixer claim ambiguous for layers without a fixer.
    *Patch:* Risk text now says "regenerate via cascade, not hand-edit" — aligned with `feedback_never_hand_edit_example_artifacts`.
- **Net structural change:** scope expanded by 2 new tasks (4b, 4c) and 2 file deltas (sdd_doc_lint rule, 7 SKILL edits); plugin VERSION now also moves; conformance count revised from 120 to 119+2; verification table grew from 7 to 9 rows.
- **Status:** SUPERSEDED by Pass 2 (which surfaced 6 more gaps not caught here).

### Pass 2 — re-review

- **Date:** 2026-06-09T22:30:00Z
- **Method:** re-read the patched plan top-to-bottom; cross-check claims introduced by Pass 1 against the actual codebase (audit/fixer SKILLs, acceptance harness).
- **Findings (6 substantive gaps surfaced — 4 inconsistencies introduced by Pass 1, 2 new scope items):**
  - **P1 (MAJOR):** Line 3 blockquote still said "no plugin SKILL surgery" — directly contradicted Task 4c added in Pass 1.
    *Patch:* Blockquote rewritten to acknowledge the SKILL surgery scope.
  - **P2 (MAJOR):** Out-of-scope list still contained "Plugin SKILL surgery (none needed — the SKILLs read the registry at dispatch time)" — contradicted Task 4c.
    *Patch:* Bullet removed; replaced with the (genuinely deferred) IPLAN-RT-001 + 39-playbooks-already-correct items, and Pass 2 verification of the latter recorded.
  - **P3 (MAJOR):** Risk-table row "Plugin SKILLs read the registry at dispatch time" was empirically wrong (6 hardcoded sites in doc-tdd alone). The wrong premise propagated as a wrong mitigation.
    *Patch:* Risk row rewritten — actual risk is "missed a hardcoded site in the sweep"; mitigation is the TRACE-RES-001 lint catching residue at the structural floor + live cascade re-run.
  - **P4 (MEDIUM):** Pass 1 review log claimed G12 patched ("regenerate via cascade, not hand-edit"), but the actual risk-table body was never updated.
    *Patch:* Body text updated to match the Pass 1 log claim.
  - **P5 (MAJOR, NEW SCOPE):** `tests/scripts/test-acceptance.sh:1523` explicitly instructs the `doc-validator` probe to "Validate cumulative @brd…@tdd traceability" with an expected-count threshold of 20 resolved trace tags. Under the new contract, TDD-01 will emit ~10 trace tags total — the threshold would fail every cascade. Pass 1 missed this entirely.
    *Patch:* Added new **Task 4e** updating the probe prompt + threshold; added `tests/scripts/test-acceptance.sh` to the Modified table; added scope item 5b; added risk row.
  - **P6 (MAJOR, NEW SCOPE):** A full sweep across all 16 audit + fixer SKILLs (run during Pass 2) surfaced 8 SKILLs with cumulative-trace references — 4 audit SKILLs with informational mentions + 4 fixer SKILLs with **load-bearing** instructions to "add missing cumulative tags" as remediation. Pass 1 only addressed the 7 author SKILLs.
    *Patch:* Added new **Task 4d** covering the 8 audit/fixer SKILLs; expanded scope item 5 from "7 layer-author SKILLs" → "15 plugin SKILLs"; added the 8 SKILL paths to the Modified table.
- **Net structural change:** scope expanded by 2 new tasks (4d, 4e); 9 new file deltas (8 audit/fixer SKILLs + the acceptance harness); 4 risk-table rows revised; verification map unchanged (same conformance + cascade verifies the new scope). Plugin VERSION bump 0.12.0 → 0.13.0 stands — the change in surface area was already MINOR-scoped.
- **Status:** SUPERSEDED by Pass 3 (which surfaced 1 MAJOR + 4 MEDIUM + 2 COSMETIC gaps not caught here).

### Pass 3 — re-review

- **Date:** 2026-06-09T23:00:00Z
- **Method:** re-read patched plan; cross-check Pass 2 patches against the codebase (existing conformance tests for the registry, sdd_doc_lint index-doc handling, trace-walk DAG algorithm).
- **Findings (7 substantive gaps — 1 MAJOR, 4 MEDIUM, 2 COSMETIC):**
  - **P3-9 (MAJOR):** `tests/conformance/test_registry.py:63` has an existing test `test_required_tags_are_cumulative` literally encoding the cumulative invariant. Pass 1/Pass 2 only added a NEW conformance test; the existing test would fail under the new shape. The plan claimed "118 + 1 new = 119" without acknowledging the existing test.
    *Patch:* Task 2 expanded — rename + rewrite `test_required_tags_are_cumulative` → `test_required_tags_match_necessary_upstream_table` within `test_registry.py`. New conformance file `test_layer_registry_necessary_upstream.py` adds the §7 block assertions (distinct purpose: template-shape coverage that `test_registry.py` doesn't currently provide). Net: 118 → 119 (existing test renamed+rewritten + 1 new file).
  - **P3-1 (MEDIUM):** Task 4b's TRACE-RES-001 spec didn't explicitly say it excludes index documents (`BRD-INDEX`, `PRD-INDEX`, …) — index docs carry no trace tags by design, and task #239 history shows the lint already special-cases them.
    *Patch:* Added explicit exclusion clause to Task 4b + fixture (d) to the test-first spec.
  - **P3-2 (MEDIUM):** Task 4e threshold `≥ 10` was a guess ("tolerance for skipped IPLAN") rather than a derived value.
    *Patch:* Reworded to derive at probe time from `LAYER_REGISTRY.yaml` (`2 × Σ required_tags[L]` per active layer in `$chain_dir`); shows worked url-shortener calculation; codifies as runtime-derived to avoid bit-rot when `active_layers` shifts.
  - **P3-3 (MEDIUM):** Task 9 re-ran only the TDD cascade, with no justification for why BRD/PRD/EARS/BDD/ADR/SPEC cascades weren't required.
    *Patch:* Added explicit rationale — SKILL changes are deterministic removals; TRACE-RES-001 lint catches residue at the structural floor; TDD cascade is the integration check; per-layer cascades for EARS/BDD/ADR/SPEC deferred to natural regeneration.
  - **P3-5 (MEDIUM):** `trace_walk.py` algorithm was underspecified — under the new contract a layer can have multiple direct upstream layers (TDD → 4 deps), so "the chain" is ambiguous (multiple paths exist). Verification row 9 asserted a specific 4-hop chain that may not match the algorithm's chosen path.
    *Patch:* Task 6 spec extended — BFS DAG closure, deterministic sort by hop + ancestor-id, set-membership verification. Verification row 9 reworded to a set check, order-independent.
  - **P3-4 (MINOR):** No explicit step to create the worktree before Task 2.
    *Patch:* Added Task 0 — `git worktree add` invocation + TDD-RT-001 paused-state note.
  - **P3-10 (BONUS, MEDIUM):** TDD-RT-001 rebase strategy not described — its `framework/VERSION 0.15.1 → 0.15.2` commit conflicts with NECESSARY-UPSTREAM-001's `0.15.2 → 0.16.0`.
    *Patch:* Added "TDD-RT-001 rebase note" to Task 9 — drop the TDD-RT-001 version-bump commit; re-bump 0.16.0 → 0.16.1 PATCH for the 6 added TDD playbooks; resolve sync-hook outputs by re-running `scripts/sync-version-refs.sh`.
  - **P3-6 (COSMETIC):** Status field not updated for Pass 2/Pass 3.
    *Patch:* Now reads "DRAFT — 2026-06-09T20:00:00Z (Pass 1 patched 22:00; Pass 2 patched 22:30; Pass 3 patched 23:00)."
  - **P3-7 (COSMETIC):** Pass 1 + Pass 2 status entries said "Awaiting next pass" rather than declaring supersession.
    *Patch:* Both updated to "SUPERSEDED by Pass N."
- **Net structural change:** 1 added task (Task 0 — Setup); 1 existing conformance test renamed + rewritten; 1 verification row reworded; 5 task bodies tightened with rationale/algorithm specifics. No new file deltas. No version-impact change. Conformance count claim corrected: 118 → 119 (rename in-place + 1 net-new test file).
- **Status:** SUPERSEDED by Pass 4 (which surfaced only 3 minor clarity/accuracy gaps — no MAJOR or MEDIUM substantive findings; convergence signal).

### Pass 4 — re-review (convergence pass)

- **Date:** 2026-06-09T23:30:00Z
- **Method:** re-read patched plan; cross-check Pass 3 patches against the codebase (Task 1b ordering, all conformance tests for hidden cumulative-shape assertions, trace_walk command syntax, version-test interactions).
- **Findings (3 MINOR/clarity gaps — 0 MAJOR, 0 MEDIUM):**
  - **P4-D (MINOR/CLARITY):** Risk-row spot-check command listed `--to BRD` for every artifact (`BRD-01 --to BRD; …; SPEC-01 --to BRD`). The `--to <LAYER>` flag filters output to ancestors at or above the named layer — irrelevant for exit-code-based checking (the walker exits non-zero on broken tag regardless of filter).
    *Patch:* Rewritten as a shell loop over the artifact IDs; the `--to` flag dropped; exit-code-only check.
  - **P4-C (MINOR/CLARITY):** Verification row 9 wording `(≥ EARS-01, BDD-01, ADR-01, SPEC-01)` — the `≥` symbol before a set is unclear (meant "at least these elements").
    *Patch:* Reworded to `Output set contains {EARS-01, BDD-01, ADR-01, SPEC-01}` — plain set-containment language.
  - **P4-3 (MINOR/ACCURACY):** Origin paragraph said "saga hit MAX_ITERATIONS without converging." Strictly, the saga hit `PARTIAL_TIMEOUT` in iter-3 (5407s of 5400s budget) — the cycle would have hit `MAX_ITERATIONS` next, but the budget expired first. The fixer also reached an explicit fixed point at iter-2.
    *Patch:* Origin reworded for accuracy — now describes PARTIAL_TIMEOUT in iter-3 + the iter-2 fixed-point evidence (cited from the actual fix report).
- **Cross-checks that came back clean (no further patches needed):**
  - `tests/conformance/_spec.py` — no cumulative-trace assertions.
  - `tests/conformance/test_framework_review_guards.py` — uses `LAYER_TAGS` tuple as the @-tag regex universe, NOT as a "must reference these" assertion. Clean under the new model.
  - `tests/conformance/platforms/test_plugin_release_metadata.py` — pins framework_version + plugin_version dynamically against `_spec.py`/VERSION files; the mechanical sync hook propagates both bumps automatically, so the test stays green.
  - Other plan files (`BRD-RT-002-VERDICT-CHAIN-PLAN.md`, `DOC-CHECK-PLAN.md`, `P1-T5-PLAN.md`) reference "cumulative" — historical context only, not files this PR modifies.
  - `origin/main` exists — Task 1b worktree command will succeed as written.
- **Net structural change:** zero new tasks, zero new file deltas, zero scope change. Three string-level edits.
- **Status:** Convergence. No MAJOR or MEDIUM gaps surfaced. The plan is ready for PR submission per CLAUDE.md §"Development workflow" item 2 ("Continue cycling until a review surfaces nothing"). Pass 5 confirmation can run as a brief sanity check on the 3 Pass-4 minor edits, but is optional under the convergence rule.

### Pass 5 — sanity check on Pass 4's minor edits (optional; pending decision)
