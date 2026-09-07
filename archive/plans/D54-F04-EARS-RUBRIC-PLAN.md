# D54-F04 Plan — broaden the EARS-Ready rubric so a quantified non-latency bound counts as "quantified" (stop mandating latency percentiles for every timing requirement)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | D54-F04-EARS-NONLATENCY-RUBRIC              |
| Type           | fix (rubric clarification)                  |
| Status         | READY — 2026-07-06 (Pass 2 independent; Pass 3 self) |
| Depends on     | none                                        |
| Feeds          | an EARS requirement bounded by cycles / iterations / an event-window scores as quantified without spurious p50/p95/p99 docks |
| Version impact | framework spec **PATCH** (`0.34.0 → 0.34.1`) — reconciles the over-strict `EARS-TEMPLATE.yaml` rubric to the **already-correct** playbook lenses + the already-supported non-latency threshold syntax. No new syntax/structure/capability. Both `FRAMEWORK_SPEC_VERSION` pointers auto-re-match; plugin + Hermes **product** versions unchanged. |

## Objective

The EARS quality-attribute rubric in `framework/layers/03_EARS/EARS-TEMPLATE.yaml` conflates
**"quantified"** with **"has latency percentiles."** It mandates `p50/p95/p99` for *every*
timing requirement and marks a requirement "non-measurable" without them — so a genuinely
quantified **non-latency** bound (a `WITHIN [3 processing cycles]`, `[5 retry iterations]`,
`[24-hour event window]`, or a `*.count` threshold) is docked for "lacking percentiles," even
though the EARS `WITHIN` extension exists precisely to carry such bounds and the threshold
syntax already supports non-latency categories (`circuit.failure.count`, arbitrary domains).

**The playbook lenses are already correct** — `tech_lead.md` counts "latency targets, payload
limits, timeout values, rate limits, **retry counts, and any other quantified** [bound]," and
`requirements_specialist` / `security_engineer` / `chaos_engineer` all accept generic numeric
bounds. The over-strict rubric lives **only** in the template. This plan reconciles the
template's four percentile-mandating surfaces to that already-correct model: **latency**
requirements use percentiles; **non-latency** requirements are quantified by a concrete
numeric value + unit. No new syntax (the TODO's constraint).

## Scope

**In — reword the four percentile-mandating rubric surfaces in `EARS-TEMPLATE.yaml`:**

- **Scoring weight (`:44`)** — "Quality attribute completeness (15%): **percentiles**,
  security, reliability targets" → "quantified targets (**latency percentiles OR a concrete
  non-latency numeric bound + unit**), security, reliability targets."
- **EARS-Ready Checklist (`:223`)** — "All **timing** requirements have p50/p95/p99 values" →
  "All **latency/response-time** requirements have p50/p95/p99 values; **non-latency** bounds
  (cycle/iteration counts, event-windows, batch sizes, retry limits, `*.count` thresholds) are
  quantified by a concrete numeric value + unit — percentiles do not apply."
- **Antipattern (`:230`)** — keep "FAIL: vague **latency** ('real-time'/'fast') — use
  percentiles"; add the complement so it does not read as "all timing needs percentiles"
  (a concrete non-latency bound is acceptable, not a FAIL).
- **Quality-attributes guidance (`:288`)** — "All **timing** constraints MUST use percentile
  notation" → "All **latency** constraints MUST use percentile notation; a non-latency bound
  uses a concrete value + unit (e.g. `WITHIN 3 cycles`, `@threshold: ADR.NN.circuit.failure.count`)."
  **Also reconcile the illustration block below it (`:289-303`)** so it does not still model
  percentiles-for-all-timing (Pass-2 MINOR): retitle "Timing Profile Matrix" → "**Latency**
  Profile Matrix" and add one non-latency example row (e.g. a count/window bound) so the
  surface is internally consistent with its reworded top line.

**Propagation + docs:** bump `framework/VERSION` `0.34.0 → 0.34.1` (staged); re-vendor the
plugin framework bundle (`sync-plugin-framework.sh`); `CHANGELOG.md` (GATE-SPEC E005+E008);
`plans/DECISIONS.md` (D-0057); close `D54-F04` in `plans/FRAMEWORK-TODO.md`; `plans/HANDOFF.md`.

**Out of scope (deferred — with rationale):**

- **The playbook lenses** (`framework/playbooks/03_EARS/*.md`) — **already correct** (they
  count any quantified bound); touching them would be churn. This plan only fixes the template
  rubric that contradicts them. *(The TODO said "+ auditor playbook"; grounding showed the
  playbooks are the authority the template should match, not a co-defect.)*
- **New non-latency threshold syntax** — unnecessary; `THRESHOLD_NAMING_RULES.md` already
  supports arbitrary categories (`circuit.failure.count`). "No new syntax" per the TODO.
- **Hand re-scoring / hand-editing the example corpus** — the percentile rubric is
  **LLM-auditor scoring, not a `sdd_doc_lint` rule** (there is no offline scorer; the audit
  skill IS the rubric). The corpus DOES carry non-latency bounds the current strict rubric
  would dock — `examples/url-shortener/docs/03_EARS/EARS-01.md` has `RTO ≤ 30 min`, `≥ 99.9%
  monthly`, and a visit-count reconciliation-window (an event-window) — and the reword
  intentionally stops docking them (a correct score improvement). Per the wholesale-regen
  convention ([[project-examples-regenerated-wholesale]]), that improvement lands at the next
  corpus regen; it is **not** hand-applied here, and no deterministic gate changes (see V5).
  *(Pass-2 corrected the earlier draft, which wrongly claimed the corpus was latency-only and
  cited the linter — which cannot see the rubric — as evidence of "no delta.")*

## Approach / Design (D-0057)

Single reconciliation principle: **quantification is dimension-appropriate.** A latency /
response-time dimension is quantified by percentiles (a distribution); a **count / window /
size** dimension is quantified by a concrete numeric bound + unit. The template's four
surfaces currently assert the former universally; each is reworded to scope percentiles to
**latency** and to explicitly admit a concrete non-latency bound as quantified — matching what
`tech_lead.md` (the authoritative lens) already enforces and what the `WITHIN` extension +
threshold categories already express. Prose-only; the rubric's *structure* (weights, checklist
shape, section keys) is unchanged, so no validator/conformance/schema reads or breaks.

**Version reasoning.** Reconciling an over-strict template rubric to the already-shipped
playbook behavior + existing syntax is a **clarification/correction**, not a new capability —
a spec **PATCH** (`docs/PROJECT.md`: MAJOR = breaking contract change; MINOR = additive
feature; neither applies). It does soften a scoring dock (a doc previously marked
"non-measurable" for a non-latency bound may now pass), but that is *correcting* a
false-negative, not adding a feature. *(If the founder prefers to treat any auditor-behavior
change as MINOR, bump to `0.35.0` at ratification — the diff is identical.)*

**Backward-compatibility.** Purely additive-permissive: no requirement that passed before
fails now; the only delta is that a quantified non-latency bound stops being docked. Every
current corpus stays green.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `framework/layers/03_EARS/EARS-TEMPLATE.yaml` | reword the 4 percentile-mandating surfaces (`:44`, `:223`, `:230`, `:288`) → latency-vs-non-latency quantification |
| `framework/VERSION` (→ `0.34.1`) + `CHANGELOG.md` | version + entry (GATE-SPEC E005+E008) |
| `platforms/claude-code-plugin/framework/layers/03_EARS/EARS-TEMPLATE.yaml` | re-vendored by `sync-plugin-framework.sh` (not hand-edited) |
| `plans/DECISIONS.md` (D-0057) / `plans/FRAMEWORK-TODO.md` (close D54-F04) / `plans/HANDOFF.md` | docs |

## Implementation sequence

### Task 1: Reword the rubric

- Edit the four surfaces in `framework/layers/03_EARS/EARS-TEMPLATE.yaml`; confirm the file
  still parses as YAML and the `_guidance` block structure is intact.

### Task 2: Version + propagation

- `framework/VERSION → 0.34.1` (staged); `sync-plugin-framework.sh` re-vendor; `CHANGELOG.md`
  in the same diff (GATE-SPEC-E008).

### Task 3: Docs of record

- D-0057; close D54-F04; HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | grep `EARS-TEMPLATE.yaml` for the reworded surfaces | each now scopes percentiles to **latency** + admits a concrete non-latency bound | Scope |
| V2 | `python -c "import yaml; yaml.safe_load(open('framework/layers/03_EARS/EARS-TEMPLATE.yaml'))"` | parses; rubric structure (weights/checklist keys) intact | Approach |
| V3 | `diff` canonical vs plugin-bundle `EARS-TEMPLATE.yaml` | identical (re-vendored) | Task 2 |
| V4 | `python -m pytest tests/conformance -q` | green (incl. `test_layers` + bundle drift guard) | propagation |
| V5 | `sdd_doc_lint` output over `examples/*/docs/` is **byte-identical** before vs after the edit | unchanged — proves the fix is rubric-only (LLM-auditor scope) and touches no deterministic gate; the rubric-driven score improvement lands at the next wholesale regen, not via the linter | edit-is-rubric-scoped |
| V6 | grep `EARS-TEMPLATE.yaml` for a surviving universal "all timing … percentiles" mandate | none (every percentile mandate is scoped to latency) | Objective |
| V7 | `python tests/chg/spec_gate.py` | OK — VERSION + CHANGELOG present (E005+E008) | Task 2 |
| V8 | consistency: the reworded rubric agrees with `playbooks/03_EARS/tech_lead.md` "any other quantified" | aligned (no new contradiction) | Design |

## Docs to update

- [ ] `CHANGELOG.md` — PATCH `0.34.0 → 0.34.1`, D54-F04
- [ ] `plans/DECISIONS.md` — D-0057 (dimension-appropriate quantification; template reconciled to the playbooks)
- [ ] `plans/FRAMEWORK-TODO.md` — close `D54-F04`
- [ ] `plans/HANDOFF.md` — progress

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Rewording weakens the latency-percentile mandate (authors drop percentiles for real latency reqs) | low | the latency surfaces KEEP "MUST use percentiles"; only non-latency bounds are admitted (V6 confirms the latency mandate survives) |
| R2 | Editing the canonical but not re-vendoring the bundle → drift-guard CI fail | low | Task 2 runs `sync-plugin-framework.sh`; V3 + V4 verify |
| R3 | PATCH vs MINOR mis-call | low | reconciliation/clarification of an over-strict rubric to already-shipped behavior = PATCH; precedent for `_guidance` rewordings is PATCH (ENG-PLATFORM-ADR-TIMING `0.32.5→0.32.6`; BL-READY-SCORE-ADVISORY `0.32.3→0.32.4`, which reworded contradicting `_guidance` prose); founder may elect MINOR at ratification (identical diff) |
| R4 | `framework/VERSION` unstaged → hook skipped → GATE-SPEC fail | low | Task 2 stages VERSION; V7 (gate) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The scoring weight names "percentiles" as the quality-attr criterion | `Quality attribute completeness (15%): percentiles` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:44 |
| 2  | The EARS-Ready checklist mandates p50/p95/p99 for all timing | `All timing requirements have p50/p95/p99 values` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:223 |
| 3  | The antipattern equates non-percentile timing with a FAIL | `FAIL: vague timing` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:230 |
| 4  | Quality-attributes guidance mandates percentiles for all timing | `All timing constraints MUST use percentile notation` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:288 |
| 5  | The tech_lead lens already counts ANY quantified bound (the authority to match) | `retry counts, and any other quantified` | framework/playbooks/03_EARS/tech_lead.md:67 |
| 6  | requirements_specialist accepts numeric thresholds / enumerated forms (not only percentiles) | `numeric thresholds, enumerated state transitions` | framework/playbooks/03_EARS/requirements_specialist.md:65 |
| 7  | Non-latency threshold categories already exist (no new syntax) | `circuit.failure.count` | framework/governance/THRESHOLD_NAMING_RULES.md:124 |
| 8  | The `WITHIN` extension exists to carry quantifiable bounds | `is a framework extension (not` | framework/layers/03_EARS/README.md:45 |
| 9  | Current framework spec version is 0.34.0 (PATCH target 0.34.1) | `0.34.0` | framework/VERSION:1 |
| 10 | GATE-SPEC-E005 requires VERSION bump on any framework/** change | `failures.append("GATE-SPEC-E005")` | tests/chg/spec_gate.py:86 |
| 11 | GATE-SPEC-E008 requires CHANGELOG in the same diff | `CHANGELOG.md` | tests/chg/spec_gate.py:87 |
| 12 | The plugin ships a re-vendored bundle of the EARS template | `dest="$repo_root/platforms/claude-code-plugin/framework"` | tools/sync-plugin-framework.sh:21 |

## Review log

### Pass 1 — 2026-07-06 — self-review

Draft after grounding all four percentile-mandating surfaces in `EARS-TEMPLATE.yaml` and
confirming the **playbooks are already correct** (`tech_lead.md` counts any quantified bound)
and the **threshold syntax already supports non-latency categories** — so the fix is a
template-only reconciliation, "no new syntax" holds, and the TODO's "+ auditor playbook" leg
is unnecessary (the playbooks are the authority, not a co-defect). Framework PATCH (clarify an
over-strict rubric to shipped behavior). Pending: independent Pass 2.

### Pass 2 — 2026-07-06 — independent (fresh-context adversarial)

All 12 citations verified. Core premise confirmed against source: a grep of
`framework/playbooks/03_EARS/` for percentile/timing/quantif language returns **only**
`tech_lead.md`'s inclusive "any other quantified" clause — **no playbook mandates
percentiles**, so "playbooks already correct / out of scope" holds and there is no
under-scoped co-defect; the two hard mandates (`:223`, `:288`) + two soft surfaces (`:44`,
`:230`) are the complete set (no missed fifth). No-new-syntax + latency-mandate-preserved both
confirmed. Findings folded:

- **[LOAD-BEARING] The "no corpus delta" verification was wrong twice.** (a) The percentile
  rubric is LLM-auditor scoring, not a `sdd_doc_lint` rule — so the old V5 (run the linter)
  structurally cannot observe a rubric delta. (b) The corpus is NOT latency-only:
  `EARS-01.md` carries `RTO ≤ 30 min`, `≥ 99.9% monthly`, and a visit-count reconciliation
  window that the strict rubric would dock. → Rewrote the Out-of-scope bullet (the reword
  intentionally un-docks these; the improvement lands at the next **wholesale regen**, not
  hand-applied) and rewrote **V5** to assert the deterministic `sdd_doc_lint` output is
  *byte-identical* before/after — proving the edit is rubric-only and touches no gate.
- **[MINOR] `:288` illustration-block residue.** The "Timing Profile Matrix" (p50/p95/p99) +
  "Timing vocabulary replacements" block below `:288` stays percentiles-for-all-timing. →
  Added to Scope: retitle → "Latency Profile Matrix" + one non-latency example row.
- **[NIT] PATCH precedent.** → Cited ENG-PLATFORM-ADR-TIMING + BL-READY-SCORE-ADVISORY in R3.

### Pass 3 — 2026-07-06 — self-review (re-validate the Pass-2 fold)

Re-checked: the rewritten V5 is a real, runnable, meaningful check (deterministic-lint
invariance = the edit is rubric-scoped); the corpus Out-of-scope bullet is now factually
correct + cites the wholesale-regen convention; the `:288` block reconciliation is in Scope so
the surface won't self-contradict; the latency mandate survives on `:223`/`:288`; D-0057 is the
next free decision number (D-0056 = LINT-DOCID). Internal consistency across version-impact /
Scope / File-structure / V1-V8 / ledger holds. No new gaps.

**Result:** ready
