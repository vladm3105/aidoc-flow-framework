# CLEANUP-PR-D — Decomposition + Threshold-Resolution Gates (Option A)

> Fifth and final child PR of `FRAMEWORK-CLEANUP-001` (master plan PR
> #128). Closes items #15 + #16; opens item #19 (Option B future
> promotion).

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | CLEANUP-PR-D                                |
| Type           | combined plan + impl                        |
| Worktree       | `feat/cleanup-pr-d-decomp-threshold-gates` |
| Depends on     | FRAMEWORK-CLEANUP-001 master plan + PR-A (#129) + PR-C (#130, threshold ID pattern) + PR-B (#131) + PR-E (#132); all merged |
| Closes         | `plans/FRAMEWORK-TODO.md` items #15, #16 |
| Opens          | new item #19 — DECOMP layer promotion (Option B, deferred) |
| Decision gate  | DECISION-GATE-D resolved as **Option A — subsection in PRD** (user 2026-06-11) |
| Version impact | Framework MINOR `0.19.1 → 0.20.0` (new optional section in PRD template + new lint rule + audit-SKILL gate); plugin MINOR `0.16.1 → 0.17.0` |
| Status         | DRAFT — 2026-06-11 |

## Items closed by this PR

| # | Tag | Title |
|---|---|---|
| 15 | `[gate]` | Component-decomposition gate (PRD↔ADR) |
| 16 | `[gate]` | Threshold-binding gate before BDD/TDD PASS |

## Item opened by this PR

| # | Tag | Title | Status |
|---|---|---|---|
| 19 | `[layer-promotion]` | Promote `component_decomposition` to a first-class `02b_DECOMP` layer | DEFERRED — revisit if Option A insufficient |

## Decision-gate resolution

Per user direction (2026-06-11): **Option A — subsection in PRD**, with Option B (new `02b_DECOMP` layer) cataloged as item #19 for future development when complex projects make the PRD subsection insufficient. Rationale: most aidoc-flow consumers will have ≤ 5-component systems where buried decomp in PRD is fine; promote later if real evidence shows the layer is needed.

## Fix shape

### Item 15 — Component-decomposition section in PRD

`PRD-TEMPLATE.yaml` gains a new optional section `component_decomposition` between §7 `scope_and_requirements` and §8 `user_stories`. The section lists each named component with its responsibility + the NFR thresholds it owns:

```yaml
component_decomposition:
  _size_target: 400  # words
  _required: false  # OPTIONAL — only required when downstream cites @threshold
  _guidance: |
    OPTIONAL section. Use when downstream layers (BDD, TDD, SPEC, ADR)
    will cite `@threshold:` to anchor NFRs (latency, error rate,
    capacity, durability, etc.). Each component declares its
    responsibility + the named thresholds it owns; downstream layers
    cite those thresholds by full-id (`PRD.NN.<category>.<key>`).

    The lint rule TH-RES-001 (CLEANUP-PR-D item 16) validates that
    every downstream `@threshold:` resolves to an entry here. If your
    project has no NFRs to bind, omit the section entirely.

    Component IDs are SHORT KEBAB-CASE names (e.g. "redirect-handler",
    "mapping-store"); they are NOT element IDs (per CLEANUP-PR-F item
    18, doc numbers are per-layer independent; components are
    project-local descriptors, not cross-layer trace targets).
  components:
    - id: "<short-kebab-component-name>"
      responsibility: "<one-line description>"
      thresholds:
        - key: "<short_key>"  # e.g. "redirectp95"
          full_id: "PRD.NN.<category>.<key>"  # canonical citation form
          value: <numeric>
          unit: "<unit>"
          source: "@brd: BRD-NN"  # optional — which BRD constraint this binds
```

Section heading in instance docs: `## 7b. Component Decomposition` (matches the `02b_DECOMP` future-layer naming so promotion stays smooth).

### Item 16 — Threshold-resolution gate (TH-RES-001 lint rule)

New `sdd_doc_lint` rule. For every `@threshold: PRD.NN.<category>.<key>` citation found in any artifact:

1. Locate `PRD-NN.md` (the host PRD).
2. Parse its `component_decomposition.components[].thresholds[]` entries.
3. Match by `full_id` field.
4. If match found: PASS.
5. If `component_decomposition` section absent: emit `TH-RES-001 P2` finding (`PRD-NN missing component_decomposition section but downstream cites @threshold`).
6. If section present but no matching `full_id`: emit `TH-RES-001 P1` finding (`@threshold: PRD.NN.x.y unresolved; not declared in PRD-NN`).

**Gate enforcement:** the BDD + TDD + SPEC + ADR audit SKILLs include the structural-lint output as a blocking findings source (existing pattern). TH-RES-001 P1 → blocking; P2 → advisory.

### Backward compat

- Pre-PR-D PRDs lack the `component_decomposition` section. If no downstream layer cites `@threshold:` to them, no finding fires (the rule is citation-driven, not section-presence-driven).
- url-shortener's PRD-01 has inline threshold definitions (line 239) but no formal `component_decomposition` section. Since downstream BDD-01 / TDD-01 / SPEC-01 already cite `@threshold:PRD.01.perf.redirectp95` etc., url-shortener's PRD-01 will surface a `TH-RES-001 P2` finding until the next cascade regenerates it with the new section. This is the expected first-encounter behavior; not a regression.

## File structure

### Modified

| Path | Item | Change |
|---|---|---|
| `framework/layers/02_PRD/PRD-TEMPLATE.yaml` | #15 | New `component_decomposition` section between `scope_and_requirements` and `user_stories` (~25 lines guidance + 15 lines structure) |
| `tools/sdd_doc_lint/__init__.py` | #16 | New TH-RES-001 check function `_check_threshold_resolution()`; loads each PRD's component_decomposition; cross-references downstream @threshold citations |
| `tools/sdd_doc_lint/sync-vendored.sh` | — | sync to platforms/ |
| `platforms/claude-code-plugin/skills/doc-prd/SKILL.md` | #15 | Document the new section in Creation Process + Required structure |
| `platforms/claude-code-plugin/skills/doc-prd-audit/SKILL.md` | #15 | Structural Checklist references new section |
| 4 × `doc-{bdd,tdd,spec,adr}-audit/SKILL.md` | #16 | Combined Report Format ingests TH-RES-001 findings as blocking |
| `framework/governance/REVIEW_TEAM.md` | #15, #16 | New §Operations subsection "Threshold-resolution gate" documenting the rule + section |
| `framework/governance/REVIEW_REMEDIATION_FLOW.md` | #16 | New rule entry in §"Structural floor checks" |
| `framework/playbooks/02_PRD/architect.md` | #15 | New C-check: "component_decomposition section present when downstream cites @threshold" |
| `framework/playbooks/02_PRD/tech_lead.md` | #15 | New beyond-checklist note about NFR-binding pattern |
| `framework/registry/LAYER_REGISTRY.yaml` | — | PRD layer entry gains `optional_sections: [component_decomposition]` (mirrors PR-E's optional_downstream_slots pattern) |
| Versions | — | `0.19.1 → 0.20.0` (framework MINOR — new lint rule + new template section); `0.16.1 → 0.17.0` (plugin MINOR — 5 audit SKILLs gain TH-RES-001 ingest) |
| CHANGELOG, TAGGING (2 rows), HANDOFF, FRAMEWORK-TODO (items #15-16 → Closed, new #19 → Open) | — | Docs of record |
| Tests: `tests/unit/test_threshold_resolution.py` | #16 | NEW unit test for TH-RES-001 (~80 lines, covers PRD missing section / threshold present / threshold absent / multiple PRDs) |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | — | hardcoded `"0.19.1" → "0.20.0"` |

**Total: ~15 substantive files + sync re-propagation + 1 new unit test.**

### Out of scope

- Promoting `component_decomposition` to its own layer (`02b_DECOMP`) — that's item #19 (Option B; deferred per user direction)
- Hand-editing url-shortener PRD-01 to add the `component_decomposition` section (never-hand-edit example artifacts; the TH-RES-001 P2 finding it surfaces is the SYSTEM working correctly — flags a real gap that a future cascade re-run fills)
- Re-cascading the url-shortener corpus to fill the gap — separate work; doesn't block PR-D
- Hermes mirror — plugin-first per HERMES-CATCHUP-001
- Threshold *type-checking* (e.g., value must be numeric, unit must be from a closed set) — initial version is shape-only; richer validation is a follow-up

## Implementation sequence

1. **Plan iterative review** (2 cycles)
2. **PRD template update** — add `component_decomposition` section
3. **Lint rule** — TH-RES-001 in `sdd_doc_lint/__init__.py`
4. **Unit test** — new `tests/unit/test_threshold_resolution.py`
5. **5 audit SKILL updates** — ingest TH-RES-001 as blocking source (PRD audit + 4 downstream)
6. **Playbook updates** — 2 PRD playbooks
7. **Governance docs** — REVIEW_TEAM, REVIEW_REMEDIATION_FLOW
8. **Registry** — PRD `optional_sections` field
9. **Version + sync + docs of record**
10. **Add item #19 to FRAMEWORK-TODO** (Option B future deferral)
11. **Conformance + lint cheap checks**
12. **Open PR**

## Verification

| # | Check | Expected |
|---|---|---|
| 1 | PRD template has `component_decomposition` section | PASS |
| 2 | sdd_doc_lint TH-RES-001 unit test: 4 cases (PASS / missing-section / missing-key / multi-PRD) | PASS |
| 3 | sdd_doc_lint on url-shortener: surfaces TH-RES-001 P2 on PRD-01 (expected — backward-compat behavior) | PASS (1 expected finding) |
| 4 | 5 audit SKILLs document TH-RES-001 in Combined Report Format | PASS — grep |
| 5 | Conformance: 120/120 PASS (1 skipped) | PASS |
| 6 | Unit: 43+4 = 47/47 PASS (1 new test file with 4 cases) | PASS |
| 7 | FRAMEWORK-TODO state: items #15, #16 → Closed; #19 → Open | PASS — count |

## Risks & rollback

| Risk | Mitigation |
|---|---|
| TH-RES-001 fires on url-shortener PRD-01 (no `component_decomposition` section) → 1 expected finding | Document the expected finding in PR body; backward-compat is by-design (citation-driven rule, not section-presence) |
| Future cascade may try to write the section but the author SKILL prompt isn't extensive enough | Doc-prd Creation Process + Required structure updated; if cascade output is thin, the lens-recalibration from PR-B (architect playbook C-check) flags it |
| TH-RES-001 false-positives on non-PRD threshold patterns (e.g., decorative `PRD.99.foo.bar` examples in docs) | The regex `PRD.NN.<cat>.<key>` is conservative — only matches actual citation form per `@threshold:`; non-`@threshold:` mentions of the same string are ignored |
| Item #19 (Option B future) gets forgotten | Cataloged in FRAMEWORK-TODO with clear "when to revisit" criteria + linked to this PR |

**Rollback:** Single PR. `git revert`. Lint rule is additive (citation-driven). Template section is optional.

## Review log

### Pass 0 — initial draft

- **Date:** 2026-06-12T00:30:00Z
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review against codebase

- **Date:** 2026-06-12T00:35:00Z
- **Cross-checks:**
  - PRD-TEMPLATE.yaml section count: 15 (§1-§15) ✓ — new section becomes §7b (no renumber)
  - url-shortener PRD-01 has inline thresholds (line 239) but no formal section ✓ — confirms PR-D's value proposition
  - 4 downstream audit SKILLs (bdd/tdd/spec/adr) ingest structural-lint findings via existing pattern ✓
  - PR-C added `id_patterns.threshold` regex (PRD.NN.<cat>.<key>) ✓ — TH-RES-001 reuses this
  - PR-E established `_required: false` + `_required_when_subtype:` precedent ✓ — new section uses same shape
- **Findings (0 substantive):** plan is realistic; scope matches the 1-2 item shape.

### Pass 2 — re-review

- **Date:** 2026-06-12T00:40:00Z
- **Method:** verify Pass 1 patches; verify no contradictions.
- **Findings:** 0 substantive.
- **Verdict:** self-converged. Per FRAMEWORK-CLEANUP-001 Pass 4 lesson,
  user-driven review on the PR is the real convergence gate.
