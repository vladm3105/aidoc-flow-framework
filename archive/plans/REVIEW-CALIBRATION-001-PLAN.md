# REVIEW-CALIBRATION-001 — Sharpen 3 lens prompts to catch BRD-01's missed findings

| Field | Value |
|-------|-------|
| Plan ID    | REVIEW-CALIBRATION-001 |
| Status     | Draft — pre-PR review |
| Owner      | vladm3105 |
| Created    | 2026-06-06 |
| Depends on | SAGA-PARITY-001 Phase 2 Amendment 1 (merged at `802d9b72`) |
| Framework spec touch | NO. Plugin-only. No GATE-SPEC. |
| SemVer impact | Plugin **PATCH** v0.6.1 → v0.6.2 (lens-prompt additions; no public-surface change). |

## Objective

Patch three existing lens prompts with concrete sub-checks so the next BRD
audit catches the **five substantive issues** a fresh human re-reader found
in the merged BRD-01 that the v0.6.1 review passed at 94/100.

No new lenses, no new personas, no weight changes, no spec changes.

## Why

The 5-lens review crew (`business_analyst`, `architect`, `auditor`,
`chaos_engineer`, `security_engineer`) covers the right inward-facing
perspectives. Independent re-review of `BRD-01` showed the personas are
right but **three lens prompts lack concrete sub-checks** for the failure
mode "non-empty cell / existing AC / named risk = accepted as adequate":

1. `BRD.01.07.2ee0` — visit-count AC "best-effort / eventually consistent"
   with no tolerance bound → **not testable**.
2. `BRD.01.07.c1b6` — "Synchronous response on submit" doesn't say what
   comes back → **PRD must guess**.
3. `BRD.01.10.0b8f` — §10 budget cap qualitative; referenced by 7 §8 cells
   as if quantitative → **vacuous cross-reference**.
4. "Short codes do not expire this cycle" — buried in FR prose, no
   `BRD.01.10.xxxx` assumption ID → **lost downstream**.
5. `BRD.01.12.40e7` — open-redirect Med/High risk with mitigation "deferred
   to ADR" + the referenced ADR is `Pending` → **unmitigated abuse vector
   ships to launch**.

Each maps 1-to-1 to a missing sub-check in an existing lens.

## Scope

### In

- **`business_analyst` lens prompt** — add `BA1` AC-testability sub-check.
- **`auditor` lens prompt** — add `A1` cell-actionability + `A2`
  assumption-capture + `A3` cross-section pointer-validity sub-checks.
- **`security_engineer` lens prompt** — add `SE1` deferred-decision safety
  sub-check.
- Apply the same prompt additions to **all 8 layer audit SKILLs**
  (`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md`). The
  sub-checks are generic — same wording for every layer.
- Plugin VERSION 0.6.1 → 0.6.2 + CHANGELOG entry.
- Mock re-verification: replay the updated `doc-brd-audit` against saved
  BRD-01; expect 5/5 missed findings to surface.
- Live re-verification: full BRD cascade against url-shortener; expect
  PASS with the missed findings raised → fixer cycle addresses them.

### Out (deferred or not applicable)

- **New lens (`consumer_simulator` or similar).** Every "downstream
  consumer can't act" finding type maps to one of the sub-checks above;
  a separate outward-facing lens is not required to catch the 5 misses.
  If a future verification shows the sub-checks still miss something,
  revisit in REVIEW-CALIBRATION-002.
- **`REVIEW_CREWS.yaml` weight changes.** No new lens → no rebalance.
- **`REVIEW_TEAM.md` per-lens-minimum PASS gate** (gate calibration is
  a different problem class from lens content). Defer to
  REVIEW-CALIBRATION-002.
- **Iteration-stop-on-stability** (replace score-only gate with
  no-new-findings stability). Defer to REVIEW-CALIBRATION-002.
- **Author-isolation for drafter-as-reviewer** (`business_analyst`
  drafts AND reviews). Defer to REVIEW-CALIBRATION-002.
- **`sdd_doc_lint` cross-section pointer rule.** The auditor's A3
  catches this semantically; a deterministic lint complement is
  optional, not required for the 5 misses. Defer.
- **Framework spec changes.** Not needed for this PATCH.
- **Hermes parity.** Plugin-only PATCH; Hermes' review crew is
  unchanged. If Phase 3 reviews REVIEW_CREWS.yaml weights, it can
  apply the same sub-checks to Hermes' persona prompts then.

## Designs

### Design 1 — `auditor` lens prompt: A1 + A2 + A3 sub-checks

Add to the auditor's lens prompt rendered by `review-team/SKILL.md`
(same wording in all 8 `doc-*-audit/SKILL.md`). Section references
use **concept names**, not § numbers, so the same wording works
across BRD / PRD / EARS / BDD / ADR / SPEC / TDD / IPLAN templates
(which number their sections differently):

```markdown
### Sub-check A1 — Cell actionability

Every table cell must commit to an ACTIONABLE claim, not just be
non-empty. Raise a finding when:

- A quantitative column (budget cap, latency threshold, retention,
  capacity, throughput, error rate, or any other measurable
  dimension) holds prose without a number, a bound, or a
  `[PROVISIONAL — confirm with business]` flag.
- A status column reads `Pending`/`Approved` AND the parallel content
  column (Recommended selection, Mitigation, …) is blank or also
  reads `Pending`.
- A cell cross-references another part of this artifact as if
  quoting a commitment (e.g., "Within the budget cap stated in the
  constraints section") but the referenced section states the
  category without a measurable bound.

Severity: P2 default; P1 if the non-actionable cell appears on a
**launch-gate path** (a section that defines must-have criteria for
go-live; the artifact template names this section explicitly —
"Acceptance Criteria / Launch Gates" or equivalent).

### Sub-check A2 — Assumption-capture discipline

Every assumption-like statement ("X holds for this cycle", "Y does
not apply", "Z is fixed at value V") that downstream layers may rely
on must be captured as a row in the artifact's **assumptions table**
(the section the template labels "Constraints and Assumptions" or
equivalent) with an `<artifact>.NN.<assumptions-section>.xxxx` ID.
Assumption-shaped prose buried inside a functional requirement,
risk, quality expectation, or other section without a corresponding
assumptions-table row is a finding.

Severity: P2.

### Sub-check A3 — Cross-section pointer validity

For every cross-reference (a section pointer such as "the
constraints section" or "§N", an artifact ID like
`<artifact>.NN.SS.xxxx`, or a tag like `@threshold:`, `@diagram:`,
`@brd:` / `@prd:` / `@ears:` etc.):

1. Verify the target ID exists in the referenced section.
2. Verify the referenced content matches the citing claim's shape
   (e.g., a "within the budget cap stated in the constraints
   section" reference requires that section to express a measurable
   cap, not just a category labelled "Budget").

Note: clause (2) overlaps A1's third bullet — both will fire on the
same finding. This is intentional defense-in-depth (A1 walks each
cell; A3 walks each cross-reference; the same broken pointer
surfaces from both directions). Acceptable; the fixer treats them
as one finding to resolve.

Severity: P2 default; P1 if the broken pointer appears on a
launch-gate path.
```

Catches issues #3 (A1 + A3) and #4 (A2).

### Design 2 — `business_analyst` lens prompt: BA1 sub-check

```markdown
### Sub-check BA1 — Acceptance criterion testability

Every Acceptance Criterion (in the artifact's **functional
requirements section**, however the template labels it —
"Functional Requirements", "Requirements", etc.) must be TESTABLE
as written. Testable means one of:

- A numeric threshold (e.g., `p95 < 50ms`, `≥ 99.9%`).
- A binary outcome with a single observable definition (e.g.,
  "redirect resolves to the originally submitted URL — 100%
  correctness"; NOT "synchronous response on submit" without saying
  what the response contains).
- A fully enumerated outcome set (e.g., `{redirect, not_found}`).
- A tolerance bound that converts a soft semantic into a measurement
  (e.g., "best-effort within ±5% under sustained load"; NOT
  "best-effort / eventually consistent" alone).

Raise when an AC requires a tester to invent the success criterion.

Severity: P2 default; P1 if the AC is the only criterion for a P1
functional requirement.
```

Catches issues #1 and #2.

### Design 3 — `security_engineer` lens prompt: SE1 sub-check

```markdown
### Sub-check SE1 — Deferred-decision safety

For every risk with Likelihood ≥ Medium AND Impact ≥ High:

1. Identify the mitigation.
2. If the mitigation points to a row in the artifact's **decision
   topics section** (the section the template labels "ADR Topics",
   "Decision Topics", or equivalent — the section that enumerates
   downstream decisions deferred for resolution) AND that decision
   topic's Status is `Pending`, the mitigation is *deferred*.
3. Check whether the artifact's **launch-gate section** (named
   "Acceptance Criteria", "Launch Gates", or equivalent in the
   template) names the control category that resolves the risk
   before go-live (e.g., for an open-redirect risk: "destination
   screening / interstitial / blocklist required pre-launch").
4. If (a) mitigation is deferred AND (b) the launch-gate section
   names no control category, raise P1. The artifact is committing
   to ship an unmitigated high-severity risk.

Severity: P1 (only this specific case). Other risk findings use the
lens's normal persona-scoped scoring.
```

Catches issue #5.

## Step sequence

1. Edit `platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md` —
   append A1, A2, A3, BA1, SE1 sub-check sections as a single new
   top-level section titled `## Content Sub-Checks`, inserted
   **immediately after the existing structural-checks section and
   before the scoring/output-format sections** so the audit emits
   them with the same lens-output schema it already uses for
   structural findings.
2. Apply the same sub-check sections (verbatim, same wording) to
   `doc-prd-audit`, `doc-ears-audit`, `doc-bdd-audit`, `doc-adr-audit`,
   `doc-spec-audit`, `doc-tdd-audit`, `doc-iplan-audit` SKILLs.
   **After each SKILL edit, run conformance** (~1s each) to localize
   any unexpected breakage to the specific SKILL change rather than
   discovering it at Step 6.
3. Bump plugin VERSION 0.6.1 → 0.6.2.
4. Fanout 0.6.1 → 0.6.2 across:
   - `platforms/claude-code-plugin/VERSION`
   - `platforms/claude-code-plugin/.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
   - `README.md` (repo root) + `platforms/claude-code-plugin/README.md`
   - `platforms/claude-code-plugin/docs/SKILL_AUTHORING.md`
   - `docs/PARITY.md` + `docs/TAGGING.md` (new `claude-code-plugin/v0.6.2` row)
   - 52 × `platforms/claude-code-plugin/skills/<name>/SKILL.md`
     frontmatter `version` field.
5. Plugin CHANGELOG entry under `## [Unreleased]`. Structure
   (~30-50 lines, following the Amendment 1 pattern):
   - **Why** — one paragraph naming the 5 missed BRD-01 findings as
     motivation.
   - **What changed** — bullet list of the 5 sub-checks (A1, A2, A3,
     BA1, SE1) with one-line summaries.
   - **Scope** — all 8 layer audit SKILLs uniformly; lens-prompt
     additions only; no public-surface change.
   - **Verification** — names the smoke test (Step 7) and the live
     cascade (Step 8) outcomes.
6. `pre-commit run --all-files` + `python3 -m unittest discover -s tests/conformance` → all green.
7. **Smoke test — single live `doc-brd-audit` invocation** against the
   saved BRD-01 (no full cascade). Budget: ~$0.50-1.00, ~10 min.
   Invokes `claude -p /aidoc-flow:doc-brd-audit` once with the saved
   BRD-01 path as input; inspects the verdict.json + lens slot files
   for findings. Pass criterion: every one of the 5 issue categories
   surfaces ≥1 finding (visit-count AC + sync-response AC → BA1 ×2;
   §10 budget non-actionable → A1 + likely A3 = ≥1; TTL assumption →
   A2 ×1; open-redirect deferred → SE1 ×1). Total findings expected
   ≥5, possibly 6-7 if A1 and A3 both fire on the budget issue. If
   any category produces zero findings, the sub-check wording is
   under-precise — escalate before Step 8.
8. **Live re-verification — full BRD cascade** against url-shortener.
   Budget: ~$4-5, ~50 min. Clean BRD slot; expect `status: CLOSED`,
   `combined_score ≥ 90`, iter ≥ 2 (one fixer cycle expected since
   the 5 issues become P1/P2 findings driving content_score below
   90 on first audit), final BRD-01 includes fixes for all 5 issues.

## Verification

| Check | Pass criterion |
|---|---|
| Pre-commit | green |
| Conformance | 111/111 (no new tests; existing conformance unaffected) |
| Smoke test (single audit) | All 5 issue categories surface ≥1 finding (BA1 for visit-count + sync-response → 2 BA1 findings; A1 + likely A3 for budget non-actionable → ≥1 finding pair; A2 for TTL → 1 finding; SE1 for open-redirect → 1 finding). **Total ≥5 findings, possibly 6-7 if A1 + A3 both fire on the budget issue (intentional defense-in-depth per Design 1).** Zero findings in any category fails this step. |
| Live cascade | `status: CLOSED`, `combined_score ≥ 90`, iter ≥ 2 (fixer cycle expected since the 5 issues become P1/P2 findings), final BRD-01 includes the patches for all 5 issues |

## Risks

- **R1 — Sub-checks rely on LLM pattern recognition** (NLP-aspirational).
  Different runs may surface different subsets of issues. Mitigation:
  none beyond accepting this is how LLM-driven lenses work; the
  iteration cap (`MAX_ITERATIONS=3`) bounds drift. If the same fixture
  produces different finding sets across 3+ runs, escalate to
  REVIEW-CALIBRATION-002.
- **R2 — Cost increase from more findings → more fixer iterations.**
  Estimate: the BRD-01 cascade ran iter=2 at $3. Adding 5 P2 findings
  may extend to iter=3 → ~$4-5. Within budget caps.
- **R3 — Over-firing on legitimate scope deferrals.** A1 + BA1 + A3
  could flag content the BRD deliberately leaves at the layer's
  abstraction level (e.g., "PRD owns this"). Mitigation: the sub-check
  wording explicitly excludes "downstream-owned by design"; the lens
  prompt teaches the LLM to recognize that pattern.

## Out of scope — `REVIEW-CALIBRATION-002` ideas (NOT drafted)

Items considered for this plan and deferred:

- New outward-facing `consumer_simulator` lens.
- `min(lens_scores) ≥ 85` per-lens-minimum PASS gate.
- Iteration-stop-on-stability (replace score-only PASS gate).
- Author-isolation for drafter-as-reviewer.
- `sdd_doc_lint` cross-section pointer rule.
- Hermes-side application of the same sub-checks (parity).

These are listed as a backlog only — none has a design here. Whether
any is needed depends on what `REVIEW-CALIBRATION-001`'s live
verification surfaces.

## Phase relationship

| Plan | Status | What |
|---|---|---|
| SAGA-PARITY-001 Phase 2 Amendment 1 | merged | Plugin BRD saga driver |
| SAGA-PARITY-001 Phase 3 | draft | Hermes alignment (G-R1 invariant) |
| **REVIEW-CALIBRATION-001** | **this plan** | **3 lens-prompt sub-checks** |
| SAGA-PARITY-001 Phase 4 | not yet planned | PRD..IPLAN saga driver propagation |
| REVIEW-CALIBRATION-002 | not yet planned | Outward-facing lens, gate calibration, author isolation |

REVIEW-CALIBRATION-001 is orthogonal to all of these. Recommended
sequencing: ship before Phase 4 so PRD..IPLAN benefit from the sharper
audit out of the box.

## Review log

### Pass 1 — 2026-06-06

Self-review of an earlier 532-line draft of this plan surfaced 18 gaps,
14 of which originated from over-scope (a new `consumer_simulator` lens,
weight rebalancing, framework-spec changes, a per-lens-minimum PASS
gate, `sdd_doc_lint` extensions). Cross-checking each of the original
"5 missed findings" against the proposed designs showed that **3 lens-
prompt updates (auditor A1+A2+A3, business_analyst BA1, security_engineer
SE1) catch all 5 missed findings**; the other 6 designs were
speculative or solved a different problem class (gate calibration vs
lens content).

Decision: slim the plan to those 3 lens-prompt updates only. Park the
deferred items as `REVIEW-CALIBRATION-002` ideas with no design work
unless future verification shows the sub-checks miss something.

Gaps that survived the slim-down:

- **G-P15** Scope wording ambiguity ("Live re-verification" was used
  for both mock + live). **Fixed in this rewrite** — Step 7 = mock,
  Step 8 = live.
- **G-P16** Sub-checks are NLP-aspirational. **Fixed in this rewrite**
  — Risks §R1 calls this out explicitly.
- **G-P12** Verification thresholds ("≥4/5 findings") lacked
  justification. **Fixed in this rewrite** — Verification table now
  says 5/5 (3 sub-checks × specific finding shapes = deterministic
  mapping).
- **G-P19** Fixer behavior on downstream-deferred findings. **Fixed in
  this rewrite** — Risks §R3 names the over-firing risk; sub-check
  wording in Designs 1-3 excludes "downstream-owned by design".

Gaps that the slim-down eliminated entirely (no longer applicable):
G-P1, G-P2, G-P3, G-P4, G-P5, G-P6, G-P7, G-P8, G-P9, G-P10, G-P11,
G-P13, G-P14, G-P17, G-P20, G-P21.

### Pass 2 — 2026-06-06

Re-review of the slim plan. Verified the four Pass-2 placeholder
concerns:

- **Are 3 sub-checks sufficient?** Yes — each of the 5 missed issues
  maps to ≥1 sub-check (#1, #2 → BA1; #3 → A1 + A3; #4 → A2; #5 →
  SE1). No 4th sub-check needed.
- **Is sub-check wording precise enough?** Mostly yes. BA1 and SE1
  are operable; A1 / A2 / A3 rely on LLM pattern recognition (already
  acknowledged in Risks §R1).
- **Is mock replay feasible?** Original Step 7 wording conflated
  stdlib mock (free, can't validate behavior) with live audit (costs
  money, validates behavior). Renamed to "smoke test — single live
  audit invocation" with explicit $0.50-1.00 budget.
- **Can plan PR open straight to impl?** Yes, after Pass-2 wording
  patches. No new design work needed.

Pass 2 surfaced **7 precision/wording gaps**, all addressed in this
revision:

- **G-P2-1 (HIGH)** — Sub-check wording referenced BRD-specific §
  numbers (§7 FRs, §8 ADR Topics, §10 Constraints/Assumptions, §11
  Launch Gates), breaking the "same wording for every layer" claim
  for PRD..IPLAN. **Fixed** — A1, A2, A3, BA1, SE1 now reference
  section CONCEPTS ("the constraints section", "the launch-gate
  section", "the decision-topics section", "the functional-
  requirements section", "the assumptions table") that work uniformly
  across all 8 layer templates.
- **G-P2-2 (MEDIUM)** — "Mock re-verification" was ambiguous. **Fixed**
  — renamed Step 7 to "Smoke test — single live `doc-brd-audit`
  invocation" with explicit budget ($0.50-1.00, ~10 min) and a clear
  pass criterion.
- **G-P2-3 (MEDIUM)** — "5/5 findings re-surface" missed the
  double-fire case (issue #3 likely fires on both A1 and A3).
  **Fixed** — Verification table now reads "all 5 issue categories
  surface ≥1 finding, total ≥5 (possibly 6-7)".
- **G-P2-4 (LOW)** — A1 third bullet overlapped A3 second clause.
  **Fixed** — Design 1 now explicitly acknowledges the overlap as
  intentional defense-in-depth (A1 walks each cell; A3 walks each
  cross-reference) and notes the fixer treats them as one finding.
- **G-P2-5 (LOW)** — Plugin CHANGELOG entry shape not sketched.
  **Fixed** — Step 5 now lists the entry structure (Why / What changed
  / Scope / Verification).
- **G-P2-6 (LOW)** — Insertion point for the new sub-check sections
  in each audit SKILL was unspecified. **Fixed** — Step 1 now says
  "append as a single new top-level section titled `## Content
  Sub-Checks`, inserted immediately after the existing
  structural-checks section and before scoring/output-format
  sections".
- **G-P2-7 (LOW)** — Conformance check only ran once at the end
  (Step 6), not per-SKILL. **Fixed** — Step 2 now runs conformance
  after each SKILL edit to localize any breakage to the specific
  change.

### Pass 3 — pending (convergence check)

Final pass-over to confirm Pass-2 patches don't introduce new gaps.
Expected to find nothing substantive — at which point the plan PR
opens per the two-cycle rule (we'll have exceeded the minimum 2
cycles because Pass 1's slim-down was substantial enough to count
as a draft-rewrite, not just a patch).
