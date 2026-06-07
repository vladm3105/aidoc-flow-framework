---
name: doc-bdd-audit
description: Audit a BDD suite - run declarative structural checks plus content review and produce a combined report for doc-bdd-fixer. Use for BDD quality gating before ADR.
metadata:
  tags:
    - sdd-workflow
    - layer-4-artifact
    - quality-assurance
  custom_fields:
    layer: 4
    artifact_type: BDD
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS]
    downstream_artifacts: [ADR, SPEC, TDD, IPLAN]
    version: "0.6.2"
    framework_spec_version: "0.13.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold]
---

# doc-bdd-audit

## Purpose

Run a **unified BDD audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-bdd-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
BDD suite using the spec as the contract.

**Layer**: 4 (BDD quality gate). **Upstream**: a BDD file. **Downstream**:
`BDD-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after a BDD suite exists and before generating the ADR, or inside the
autopilot's audit↔fix cycle. Do **not** use to create a BDD (use
`../doc-bdd/SKILL.md` or `../doc-bdd-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the ADR-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`BDD-NN.A_audit_report_v*.md`; keep `BDD-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** BDD path (`docs/04_BDD/BDD-NN_*/...`); optional score threshold
(default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write `BDD-NN.A_audit_report_vNNN.md`
→ 6) if auto-fixable findings exist, hand off to `doc-bdd-fixer`.

## Structural Checklist

Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/README.md`,
`${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml` (embedded rules + scenario
conventions), and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`. Style: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`.

**Template-conformance enumeration (mandatory first step).** Load
`BDD-TEMPLATE.yaml` and enumerate every required section (each top-level YAML
key that is not explicitly `required: false`). The Structure check below is
satisfied **only** when every enumerated required section appears as a `##`
heading in the artifact. Any missing required section is a **blocking finding**
— never rationalise it as a "compact" variant, "documented walkthrough",
"lint-pinned", or any other exception. There is one template per layer and one
canonical required-section set.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Element ID format | every ID matches `BDD.NN.SS.xxxx` (4-hex hash) |
| Structure | every section enumerated above is present and non-empty |
| Gherkin quality | scenarios are atomic, executable, valid Given-When-Then |
| Cumulative tags | `@brd @prd @ears` present, Gherkin-native, no space after colon |
| Scenario tags | each scenario has `@scenario-type`, priority, `@scenario-id`, `spec_trace` |
| Thresholds | quantitative values use `@threshold:` keys (no magic numbers) |
| Quality gate | ADR-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** frontmatter metadata (below); internal links
and template/governance references resolve; no downstream numbers cited before
they exist; five scenario categories represented; times `HH:MM:SS` with IANA
timezones; sequence-diagram tag present if a flow is illustrated (use
`../charts-flow/SKILL.md`).

**Authoring-style check (Tier 2 → Tier 1 at threshold).** Verify the document
complies with `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`:
no banned phrases, form preferences observed (tables/bullets over prose where
homogeneous), size targets met within +50%. **Promote to blocking** when ≥3
banned phrases occur in one section OR the document exceeds its size target by
>50%.

**Combined status:** `PASS` only if all Tier 1 pass **and** content score ≥
threshold **and** no blocking issues; otherwise `FAIL`.

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `bdd-document` (not `template`) |
| `artifact_type` | yes | `BDD` |
| `layer` | yes | `4` |
| `deliverable_type` | yes | `code`, `document`, `ux`, `risk`, `process` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `bdd-document`.

## Content Sub-Checks

These sub-checks supplement the structural / metadata gates with
content-quality checks targeting failure modes the v0.6.1 review
missed (REVIEW-CALIBRATION-001, plan PR #95). Section references
use concept names (not § numbers) so the same wording applies across
all 8 layer templates.

### Sub-check A1 — Cell actionability (auditor lens)

Every table cell must commit to an ACTIONABLE claim, not just be
non-empty. Raise a finding when:

- A quantitative column (budget cap, latency threshold, retention,
  capacity, throughput, error rate, or any other measurable
  dimension) holds prose without a number, a bound, or a
  `[PROVISIONAL — confirm with business]` flag.
- A status column reads `Pending`/`Approved` AND the parallel
  content column (Recommended selection, Mitigation, …) is blank or
  also reads `Pending`.
- A cell cross-references another part of this artifact as if
  quoting a commitment (e.g., "Within the budget cap stated in the
  constraints section") but the referenced section states the
  category without a measurable bound.

Severity: P2 default; P1 if the non-actionable cell appears on a
**launch-gate path** (the section the template labels "Acceptance
Criteria", "Launch Gates", or equivalent).

### Sub-check A2 — Assumption-capture discipline (auditor lens)

Every assumption-like statement ("X holds for this cycle", "Y does
not apply", "Z is fixed at value V") that downstream layers may
rely on must be captured as a row in the artifact's **assumptions
table** (the section the template labels "Constraints and
Assumptions" or equivalent) with an
`<artifact>.NN.<assumptions-section>.xxxx` ID. Assumption-shaped
prose buried inside a functional requirement, risk, quality
expectation, or other section without a corresponding
assumptions-table row is a finding.

Severity: P2.

### Sub-check A3 — Cross-section pointer validity (auditor lens)

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
surfaces from both directions). The fixer treats them as one
finding to resolve.

Severity: P2 default; P1 if the broken pointer appears on a
launch-gate path.

### Sub-check BA1 — Acceptance criterion testability (business_analyst lens)

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
- A tolerance bound that converts a soft semantic into a
  measurement (e.g., "best-effort within ±5% under sustained
  load"; NOT "best-effort / eventually consistent" alone).

Raise when an AC requires a tester to invent the success criterion.

Severity: P2 default; P1 if the AC is the only criterion for a P1
functional requirement.

### Sub-check SE1 — Deferred-decision safety (security_engineer lens)

For every risk with Likelihood ≥ Medium AND Impact ≥ High:

1. Identify the mitigation.
2. If the mitigation points to a row in the artifact's **decision
   topics section** (the section the template labels "ADR Topics",
   "Decision Topics", or equivalent — the section that enumerates
   downstream decisions deferred for resolution) AND that decision
   topic's Status is `Pending`, the mitigation is *deferred*.
3. Check whether the artifact's **launch-gate section** names the
   control category that resolves the risk before go-live (e.g.,
   for an open-redirect risk: "destination screening / interstitial
   / blocklist required pre-launch").
4. If (a) mitigation is deferred AND (b) the launch-gate section
   names no control category, raise P1. The artifact is committing
   to ship an unmitigated high-severity risk.

Severity: P1 (only this specific case). Other risk findings use the
lens's normal persona-scoped scoring.

### Excluded patterns — downstream-owned by design

The above sub-checks must NOT fire on content the artifact's layer
deliberately leaves at this abstraction level. Examples:

- A BRD that says "PRD owns persona definitions" is not an
  assumption-capture violation (A2) — it is a correct deferral.
- An AC that says "specific outcome enumerated in PRD" is not a
  testability violation (BA1) — the BRD-level AC is correct.

Recognize these via explicit deferral phrases ("owned by X",
"deferred to X", "specified in X", where X is the next-downstream
layer) and skip the finding.

## Combined Report Format

Output: `BDD-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** · **Coverage Findings** (Gherkin
syntax, five-category coverage, cumulative-tag coverage, `spec_trace` presence) ·
**Fix Queue** (`auto_fixable` / `manual_required` / `blocked`) · **Recommended
Next Step** · **Cleanup Summary**.

## Hand-off to doc-bdd-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-bdd-fixer`
consumes the latest `BDD-NN.A_audit_report_vNNN.md`.

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor only this skill's declared knobs:
`section_toggles` (a toggled-off **optional** section is not a finding; a
missing **required** section still is), `active_layers` (never flag the
absence of — or a missing reference to — a layer the project disabled, per the
cascade rule), and `audit_threshold` (use the project's quality-gate score
only when it is **>=** the framework default; ignore any lower value). Ignore
unknown keys.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-bdd/SKILL.md` · Fix: `../doc-bdd-fixer/SKILL.md` · Generate:
  `../doc-bdd-autopilot/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
