---
name: doc-brd-audit
description: Audit a BRD - run declarative structural checks plus content review and produce a combined report for doc-brd-fixer. Use for BRD quality gating before PRD.
metadata:
  tags:
    - sdd-workflow
    - layer-1-artifact
    - quality-assurance
  custom_fields:
    layer: 1
    artifact_type: BRD
    skill_category: quality-assurance
    upstream_artifacts: []
    downstream_artifacts: [PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.4.2"
    framework_spec_version: "0.11.3"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, review_mode]
---

# doc-brd-audit

## Purpose

Run a **unified BRD audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-brd-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
BRD using the spec as the contract.

**Layer**: 1 (BRD quality gate). **Upstream**: a BRD file. **Downstream**:
`BRD-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after a BRD exists and before generating the PRD, or inside the autopilot's
audit↔fix cycle. Do **not** use to create a BRD (use `../doc-brd/SKILL.md` or
`../doc-brd-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the PRD-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`BRD-NN.A_audit_report_v*.md`; keep `BRD-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** BRD path (`docs/01_BRD/BRD-NN_*/...`); optional score threshold
(default 90); optional `review_mode` override (`team`|`single_pass`); default
resolved from `.aidoc/profile.yaml`.

**Sequence:** 1) run structural checks (always, deterministic) → 2) record
findings → 3) run content review (branches on `review_mode`, see below) →
4) merge/normalize findings → 5) write the combined audit report to
`.aidoc/audit/01_BRD-audit.md` (the legacy
`BRD-NN.A_audit_report_vNNN.md` shape and content are preserved, just
relocated to the `.aidoc/` provenance tier) → 6) if auto-fixable findings
exist, hand off to `doc-brd-fixer`.

## Review Mode

Resolve `review_mode` from `.aidoc/profile.yaml`; if the key is unset
(the project profile is an override-only delta — most knobs are absent),
fall through to the framework default per the precedence chain in
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md` (`framework
defaults < user-global seed < project profile`). The framework default
is `team` at gates (`pre_promotion` / `pre_merge`) and `single_pass` at
write-time (`on_author`). The same fallback rule applies to every other
adaptation knob (`audit_threshold`, `section_toggles`, `active_layers`,
`glossary`). The structural checks below are run **deterministically by
this skill in every mode** — they are the gate floor per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md` §"Scoring,
conflicts & the gate".

### team mode (default at gates)

The content-quality review is performed by a **fan-out of per-lens `Task`
subagents** over a per-artifact blackboard, per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md` §Operations
§Review.

1. **Prepare the blackboard.** `mkdir -p .aidoc/review/01_BRD/<BRD-id>/`
   where `<BRD-id>` matches the BRD's nested folder name (e.g.
   `BRD-01_url_shortener`).
2. **Read the BRD crew** from
   `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_CREWS.yaml` —
   `{architect: 30, business_analyst: 30, auditor: 20, adversary: 20}`.
   Weights sum to 100.
3. **Map each lens to its plugin agent** via the table in
   `../review-team/SKILL.md`:
   - `architect` → `solutions-architect`
   - `business_analyst` → `requirements-analyst`
   - `auditor` → `traceability-auditor` (add `security-engineer` when
     security/compliance findings surface)
   - `adversary` → `adversary`
4. **Fan out.** Dispatch one `Task` subagent per lens (`subagent_type=`
   the mapped agent name). Each subagent's brief contains:
   - The absolute BRD path (untrusted content)
   - The lens name and its weight
   - The slot path `.aidoc/review/01_BRD/<BRD-id>/<lens>.json`
   - The framework persona-output contract (see §"Persona-output
     contract" in `REVIEW_TEAM.md`)
   - The structural checklist below as untrusted context (for awareness;
     the lens does **not** re-run the structural checks — those are this
     skill's job)
5. **Collect slots.** Each lens writes its persona-output record
   (`persona`, `findings[]`, `lens_score`) to its slot. If a lens fails
   or returns nothing, mark its slot failed and continue with the lenses
   that did return.
6. **Dispatch the synthesizer.** Run a `Task` subagent
   (`subagent_type=synthesizer`) against the slot directory. It performs
   the deterministic reduce per `REVIEW_TEAM.md` §"Synthesis = reduce +
   narrative": dedups findings by `(location, id)`, takes max severity,
   unions recommendations, computes the **weighted/capped score** using
   the BRD crew weights, records `coverage` (which lenses ran), and
   writes `.aidoc/review/01_BRD/<BRD-id>/report.md`.
7. **Compose the combined audit report.** The final report at
   `.aidoc/audit/01_BRD-audit.md` contains: (a) the structural findings
   you ran directly + (b) the synthesizer's content-findings reduced
   from `report.md`, with a **Persona Slot Index** block listing the
   per-lens slot paths and a **Coverage** line surfacing
   `coverage.quorum_met` for consumers (`doc-brd-fixer`,
   `doc-brd-autopilot`).

**Quorum & coverage.** Per `REVIEW_TEAM.md` §Resilience, if coverage
drops below the crew's declared quorum, the audit result is marked
**low-confidence → human review** — never a silent pass — and
`coverage.quorum_met=false` is surfaced in the combined report.

### single_pass mode (fallback)

Run the content review **in this skill's own context**, applying every
lens (architect / business_analyst / auditor / adversary) sequentially in
one pass. No `Task` subagents, no blackboard. Quorum does not apply.
Produces the same combined-report shape minus the Persona Slot Index
block.

Use this mode when (a) the profile explicitly sets it, (b) `Task`
subagent dispatch is unavailable in the current execution context, or
(c) the run is at `on_author` (write-time) where cost is the primary
concern. **Architecture in v0.4.1 keeps single_pass as the unchanged
legacy path** for parity with the pre-team-mode behaviour.

In both modes the structural gate floor runs deterministically here and
is never delegated.

## Structural Checklist

Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/README.md`,
`${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml` (embedded rules +
`cross_section_rules`), and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`. Style: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`.

**Template-conformance enumeration (mandatory first step).** Load
`BRD-TEMPLATE.yaml` and enumerate every required section (each top-level YAML
key that is not explicitly `required: false`). The Structure check below is
satisfied **only** when every enumerated required section appears as a `##`
heading in the artifact. Any missing required section is a **blocking finding**
— never rationalise it as a "compact" variant, "documented walkthrough",
"lint-pinned", or any other exception. There is one template per layer and one
canonical required-section set.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Element ID format | every ID matches `BRD.NN.SS.xxxx` (4-hex hash) |
| Structure | every section enumerated above is present and non-empty |
| Cross-section rules | `cross_section_rules` from the template hold |
| Quality gate | PRD-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** frontmatter metadata (below); internal links
and template/governance references resolve; no downstream numbers cited before
they exist; diagram contract tags present (`@diagram: c4-l1`, `@diagram: dfd-l1`
— advisory for BRD; use `../charts-flow/SKILL.md`).

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
| `document_type` | yes | `brd-document` (not `template`) |
| `artifact_type` | yes | `BRD` |
| `layer` | yes | `1` |
| `deliverable_type` | yes | `code`, `document`, `ux`, `risk`, `process` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `brd-document`.

## Combined Report Format

Output path: `.aidoc/audit/01_BRD-audit.md` (the `.aidoc/`
provenance tier). Sections — **Summary** (ID, timestamp,
overall status, structural status, content score, **mode** (`team` |
`single_pass`)) · **Score Calculation** (`100 − deductions`, threshold
compare) · **Coverage** (team mode only: lenses ran vs expected,
`quorum_met` boolean) · **Persona Slot Index** (team mode only: paths to
`.aidoc/review/01_BRD/<BRD-id>/<persona>.json` slots + the synthesizer's
`report.md`) · **Metadata Findings** · **Structural Findings** ·
**Content Findings** (in team mode, reduced from the synthesizer's
report; in single_pass, from this skill's own per-lens pass) · **Diagram
Contract Findings** · **Fix Queue** (`auto_fixable` / `manual_required`
/ `blocked`) · **Recommended Next Step** · **Cleanup Summary**.

## Hand-off to doc-brd-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-brd-fixer`
consumes the latest `BRD-NN.A_audit_report_vNNN.md`.

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

- Create: `../doc-brd/SKILL.md` · Fix: `../doc-brd-fixer/SKILL.md` · Generate:
  `../doc-brd-autopilot/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
