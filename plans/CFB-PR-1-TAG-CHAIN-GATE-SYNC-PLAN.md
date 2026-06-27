# CFB-PR-1 — `BL-TAG-CHAIN-GATE-SYNC` → cumulative→necessary-upstream doc migration

> First child of `CONSUMER-FEEDBACK-001`. Started as a 2-file fix
> (`TRACEABILITY.md` + `GATE-08`); the mandatory Pass-2 independent review
> found the obsolete **cumulative-tag model** survives in ~10 framework-core
> teaching surfaces that `NECESSARY-UPSTREAM-001` (spec 0.16.0) never scrubbed
> from prose — fixing only 2 would leave the framework self-contradictory and
> self-create a dangling pointer. Per founder decision (2026-06-27), expanded
> to the **full doc migration**, split into ≤3-surface sub-PRs. Documentation
> only; the contract itself is unchanged.

| Field          | Value                                                |
| -------------- | ---------------------------------------------------- |
| Task           | CFB-PR-1 (`BL-TAG-CHAIN-GATE-SYNC`, expanded)        |
| Type           | documentation                                        |
| Status         | IMPLEMENTED (bundled) — 2026-06-27 · ~20 surfaces, framework-spec-only PATCH 0.23.1 |
| Parent         | `plans/CONSUMER-FEEDBACK-001-PLAN.md` (PR-1)         |
| Depends on     | none (Wave-1 foundation)                             |
| Feeds          | PR-2 (coverage engine reads the corrected chain); PR-3 |
| Version impact | framework **PATCH** — human-readable governance/teaching-doc correction; the machine-read contract (`LAYER_REGISTRY.yaml` + templates' tag fields) is already correct and unchanged |

## Objective

Migrate every framework-core doc that still teaches the pre-0.16.0
**cumulative-tag model** ("each layer inherits all upstream tags") to the live
**necessary-upstream** model (each layer cites only its `required_tags`; deeper
lineage is transitive). The contract does not change — only the prose/tables
that misdescribe it. `framework/governance/REVIEW_TEAM.md:262-318` already
carries the correct language and is the wording reference.

## Scope

**In — the 10 stale surfaces, grouped into 4 sub-PRs (≤3 each, Rule-1 cap):**

- **PR-1a — trace contract source-of-truth:** `framework/governance/TRACEABILITY.md`,
  `framework/governance/chg/gates/GATE-08_IPLAN.md`,
  `framework/governance/README.md` (its 1-line description of TRACEABILITY).
- **PR-1b — principles + author rules + template guidance:**
  `framework/governance/DOC_GOVERNANCE_CORE.md` (Principle 3),
  `framework/AI_ASSISTANT_RULES.md` (the live author-facing bug),
  `framework/layers/05_ADR/ADR-TEMPLATE.yaml` (`_guidance` only — NOT tag fields).
- **PR-1c — guides:** `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`,
  `framework/QUICK_REFERENCE.md`, `framework/README.md`.
- **PR-1d — review-flow pointer:** `framework/governance/REVIEW_REMEDIATION_FLOW.md`
  (1-line cross-ref). Small; rides last or folds into the lightest sibling.

**Out of scope (deferred — owner named):**

- Do NOT re-add cumulative tags anywhere (BL-Q1); do NOT touch template tag
  fields — only `_guidance` prose. Templates' actual tags already match the
  contract.
- Hermes `sdd-orchestrator/references/*` + plugin mirrors carry the same stale
  copies → owned by **PR-10 `ENG-STALE-DEPTH-DOCS`** (already flagged
  >3-surface; the cumulative copies join that Hermes sweep).
- `TRACEABILITY.md` `>=90/100` readiness wording → **PR-9 `BL-READY-SCORE-ADVISORY`**.
- Auditor playbooks (`07_TDD`, `08_IPLAN`) already frame cumulative tags as
  optional/decorative — correct, not touched.

## Approach / Design

### Authoritative contract (`LAYER_REGISTRY.yaml` `required_tags`)

Verified against registry + templates + lint-passing corpus (all agree):

| Layer | Necessary upstream (`required_tags`) |
| ----- | ------------------------------------ |
| BRD   | — |
| PRD   | `@brd` |
| EARS  | `@prd` (NOT `@brd @prd`) |
| BDD   | `@ears` |
| ADR   | `@ears, @bdd` |
| SPEC  | `@ears, @bdd, @adr` |
| TDD   | `@ears, @bdd, @adr, @spec` |
| IPLAN | `@spec, @tdd` |

The chain is **not cumulative**: from ADR on, `@brd`/`@prd` are dropped; IPLAN
keeps only `@spec`/`@tdd`. `required_tags` is the *minimum* trace-resolution
set — a doc MAY carry extra provenance tags (e.g. a platform ADR's `@brd`/`@prd`
in `context`), so the corrected tables describe the **required** column only.

### Consistent corrected language (all surfaces)

- Replace "cumulative tagging / each layer inherits all upstream tags / Maximum
  8 cumulative tags" with "**necessary-upstream tagging** — each layer cites
  only its `required_tags`; deeper lineage is transitive (one hop per layer, or
  `tools/trace_walk.py`)."
- Any per-layer tag table → the contract table above (required column).
- "cumulative traceability" used loosely as an end-to-end descriptor (e.g.
  `framework/README.md:12`, guide overview) → "**end-to-end traceability**" (the
  chain still spans BRD→IPLAN transitively; just not via redundant local tags).

## Implementation sequence (per sub-PR; each its own branch + CI + merge)

1. **PR-1a** — rewrite `TRACEABILITY.md` "Cumulative Tagging"→"Necessary-upstream
   tagging" + fix validation table; trim `GATE-08-E003` resolution to
   `@spec`/`@tdd`; fix `governance/README.md` description.
2. **PR-1b** — `DOC_GOVERNANCE_CORE.md` Principle 3 reworded; `AI_ASSISTANT_RULES.md:12`
   corrected (the live bug); `ADR-TEMPLATE.yaml:389` `_guidance` corrected.
3. **PR-1c** — `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` (§Cumulative Traceability +
   overview), `QUICK_REFERENCE.md` table, `framework/README.md:12`.
4. **PR-1d** — `REVIEW_REMEDIATION_FLOW.md:175` cross-ref.

Sub-PRs land in close succession; none claims "framework now consistent" until
PR-1d merges (transient cross-PR inconsistency is acceptable per the
sequenced-PR discipline).

## Verification (each sub-PR + a final repo-wide gate)

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | Each corrected per-layer table == `LAYER_REGISTRY.yaml` `required_tags` | exact | contract |
| V2 | `GATE-08-E003` resolution lists only `@spec`+`@tdd` | true | PR-1a |
| V3 | Each sub-PR ≤3 doc surfaces (`git diff --name-only`) | true | Rule-1 |
| V4 | `python3 -m sdd_doc_lint examples/url-shortener/docs/` | green/unchanged | C-1 guard |
| V5 | Conformance suite green | green | land-gate |
| V6 (final, after PR-1d) | `grep -rin "cumulative" framework/ --include=*.md \| grep -vi "non-cumulative"` returns ONLY: the deferred Hermes/plugin mirrors (PR-10), THRESHOLD_NAMING_RULES (unrelated "cumulative total" usage), REVIEW_TEAM origin-note, and auditor-playbook "optional/decorative" framing | no stale per-layer-chain assertion remains in framework-core | Objective |

## Docs to update

- [ ] `plans/FRAMEWORK-TODO.md` — `BL-TAG-CHAIN-GATE-SYNC` → Closed (after PR-1d) with merge SHAs; note the scope expansion.
- [ ] `plans/CONSUMER-FEEDBACK-001-PLAN.md` — record PR-1 expanded to 1a–1d (cumulative-residue migration).
- [ ] `CHANGELOG.md` — framework PATCH entry.

## Claim ledger

| #  | Claim | Citation |
| -- | ----- | -------- |
| 1 | required_tags per layer (the contract table) | `LAYER_REGISTRY.yaml:25,38,51,71,84,97,110,123` |
| 2 | Correct wording already exists (reference) | `framework/governance/REVIEW_TEAM.md:266-271,318` |
| 3 | GATE-08-E003 example is the stale 7-tag chain; rule needs only spec/tdd | `GATE-08_IPLAN.md:225-231` vs `:70,197` |
| 4 | Stale cumulative surfaces (the 10) | `TRACEABILITY.md:13-24,34-43`; `GATE-08:225-231`; `governance/README.md:13`; `DOC_GOVERNANCE_CORE.md:7`; `AI_ASSISTANT_RULES.md:12`; `ADR-TEMPLATE.yaml:389`; `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:24-39`; `QUICK_REFERENCE.md:18-20`; `framework/README.md:12`; `REVIEW_REMEDIATION_FLOW.md:175` |
| 5 | Corpus confirms non-cumulative | `examples/url-shortener/docs/03_EARS/EARS-01.md` (@prd, no @brd); `08_IPLAN/IPLAN-01.md` (@spec/@tdd) |

## Review log

### Pass 1 — 2026-06-26 — self-review

- Scope-vs-triage: validation table (34-43) equally stale; widened within
  2 surfaces; recorded authoritative table.

### Pass 2 — 2026-06-26 — independent (fresh-context, `Plan` agent)

- **[BLOCKING] Incomplete scope:** the cumulative model survives in ~6+
  framework-core surfaces (DOC_GOVERNANCE_CORE Principle 3, AI_ASSISTANT_RULES
  live bug, the guide, quick-ref, framework/README, REVIEW_REMEDIATION) +
  ADR `_guidance`; fixing only 2 files self-creates a dangling pointer at
  `governance/README.md:13`. → **Verified all by grep**; founder chose full
  cleanup. Scope expanded to the 10-surface migration, split into 4 ≤3-surface
  sub-PRs (1a–1d). Objective re-scoped to "migrate the model," not "2-file fix."
- Other findings folded: "all three sources agree" softened (ADR provenance
  nuance); V6 promoted to a repo-wide final gate; ADR `_guidance` brought in.

### Pass 3 — 2026-06-27 — self re-validation (of the expanded scope)

- 10 surfaces enumerated + assigned to 4 sub-PRs, each ≤3 (V3). Deferred
  surfaces (Hermes/plugin mirrors→PR-10; readiness wording→PR-9) named with
  owners. Corrected language sourced from REVIEW_TEAM.md (consistent). Contract
  table re-checked against registry. No new load-bearing gaps.

### Pass 4 — 2026-06-27 — implementation findings (folded; founder decisions)

- **Bundled, not split (founder).** GATE-SPEC forces a `framework/VERSION` bump
  on every framework PR, and the only bump tool is combined-by-design — so 4
  sub-PRs = 4 version rituals. Bundled into ONE PR + one bump instead.
- **Scope expanded 10 → ~20 surfaces (founder: full reconciliation).** The V6
  repo-wide grep during implementation found the cumulative model also in the
  EARS/BDD **templates**, **GATE-03** (+ error catalog), 3 layer READMEs, the
  BDD-00 index, `DEFINITION_OF_DONE`, and the ADR auditor playbook — several
  asserting **false `required_tags`** (EARS "@brd+@prd", BDD "@brd+@prd+@ears",
  ADR "4 tags") that contradict the registry. GATE-03 counts confirmed
  **doc-only** (not coded; `sdd_doc_lint` enforces via the registry), so safe to
  correct. All folded into the bundle.
- **Framework-spec-only bump (founder).** `framework/VERSION` 0.23.0 → 0.23.1;
  `FRAMEWORK_SPEC_VERSION` pins + 52 skill + 51 playbook `framework_spec_version`
  → 0.23.1; **plugin VERSION stays 0.22.0** (its code didn't change). Required
  hand-completion beyond `bump_version.py` (it misses playbooks + `SKILL_AUTHORING`
  - plugin README + a hardcoded conformance assertion).
- **Verified:** V6 grep clean; conformance **135 tests OK**; corpus lint
  unchanged. Structural tag *fields* untouched (BL-Q1).

**Result:** IMPLEMENTED, conformance-green, bundled into one PR. CI ai-review
(now functional) serves as the independent pre-merge review.
