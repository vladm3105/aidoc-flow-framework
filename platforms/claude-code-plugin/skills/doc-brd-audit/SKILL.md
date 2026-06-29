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
    version: "0.23.0"
    framework_spec_version: "0.29.1"
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
   where `<BRD-id>` is the BRD's short artifact ID (e.g. `BRD-01`), not
   the nested folder name. This keeps blackboard paths stable when
   slugs change.
2. **Read the BRD crew** from
   `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_CREWS.yaml` —
   `{architect: 30, business_analyst: 30, auditor: 20, chaos_engineer: 12,
   security_engineer: 8}`. Weights sum to 100. Rationale: chaos-heavy at
   BRD because reliability NFRs outweigh threat-modelling at this layer;
   see `REVIEW_TEAM.md` §"Weight allocation rules".
3. **Map each lens to its plugin agent** via the table in
   `../review-team/SKILL.md`:
   - `architect` → `solutions-architect`
   - `business_analyst` → `requirements-analyst`
   - `auditor` → `traceability-auditor`
   - `chaos_engineer` → `chaos-engineer`
   - `security_engineer` → `security-engineer`
3a. **Load the layer-and-lens playbook.** For each lens in the crew,
   resolve and read the playbook content from
   `${CLAUDE_PLUGIN_ROOT}/../../framework/playbooks/01_BRD/<lens>.md`.
   If the playbook file is missing, mark `branches[<lens>].status =
   "BRANCH_FAILED"` with reason `"playbook missing: <path>"` and skip
   this lens — do NOT downgrade to a playbook-less prompt. Other lenses
   continue. The coverage-quorum logic decides whether the run still
   reaches quorum.
4. **Fan out.** Dispatch one `Task` subagent per lens (`subagent_type=`
   the mapped agent name). Each subagent's brief contains:
   - The absolute artifact path (untrusted content)
   - The lens name and its weight
   - The slot path `.aidoc/review/01_BRD/<artifact-id>/<lens>.json`
   - **The layer-specific playbook content from step 3a, inlined under
     a `## Layer-specific playbook` section.** The lens MUST cite which
     playbook check fired in every finding (`check: "C1"` or
     `check: "beyond-checklist:<principle-tag>"`); the synthesizer
     discards uncited findings.
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
   (`subagent_type=synthesizer`) against the slot directory. It writes
   **both** companion files (per `agents/synthesizer.md` §"Output"):
   - `.aidoc/review/01_BRD/<BRD-id>/verdict.json` — the authoritative
     machine-readable verdict (`combined_status`, `content_score`,
     `structural_status`, `coverage.*`, `blocking_findings_count`,
     `lens_scores`).
   - `.aidoc/review/01_BRD/<BRD-id>/report.md` — the human narrative
     (mirrors verdict.json values).
7. **Compose the combined audit report.** Read
   `.aidoc/review/01_BRD/<BRD-id>/verdict.json` and `report.md`. The
   final audit report at `.aidoc/audit/01_BRD-audit.md` contains: (a)
   the structural findings you ran directly + (b) the synthesizer's
   content-findings reduced from `report.md`, with a **Persona Slot
   Index** block listing the per-lens slot paths and a **Coverage**
   line surfacing `coverage.quorum_met` for consumers (`doc-brd-fixer`,
   `doc-brd-autopilot`).

**Quorum & coverage.** Per `REVIEW_TEAM.md` §Resilience, if
`verdict.coverage.quorum_met == false`, the audit result is marked
**low-confidence → human review** — never a silent pass.

### Output Contract (team mode)

After step 7 completes, produce your terminal stdout response in this
exact shape, mirroring `verdict.json` values verbatim:

```
Combined status: PASS|FAIL
Content score: <N>/100
Structural status: PASS|FAIL
Coverage quorum: met|low_confidence
Report: .aidoc/audit/01_BRD-audit.md
```

Read `combined_status`, `content_score`, `structural_status`, and
`coverage.quorum_met` from `verdict.json`. **Do NOT echo the BRD's
self-claimed PRD-Ready score** (the value the BRD document writes into
its own Document Control / Traceability sections is stale data the
audit must overwrite). The synthesizer's `verdict.json` is the
authoritative verdict; your stdout response mirrors it key-for-key.

### single_pass mode (fallback)

Run the content review **in this skill's own context**, applying every
lens (architect / business_analyst / auditor / chaos_engineer / security_engineer) sequentially in
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

### Strip author self-claim before lens dispatch (CLEANUP-PR-B item 9)

Before passing the artifact body to each lens subagent (team mode) or
to the single-pass review (single_pass mode), STRIP frontmatter and
inline fields matching any of:

- `*_ready_score` (e.g. `brd_ready_score`, `prd_ready_score`,
  `ears_ready_score`, etc.)
- `*_score` (e.g. `audit_score`, `readiness_score`)
- `readiness_score`
- `audit_score`

These are author self-assessments. Leaving them in the artifact body
creates an anchor effect — the lens output's `lens_score` tends toward
the author's claim. The structural surface lenses evaluate is the
artifact's CONTENT (sections, IDs, traceability, prose); a number the
author wrote down for itself is not part of that surface.

Stripped fields stay in the artifact frontmatter on disk (they're
author metadata, not lens input). Stripping happens in-prompt only:
the brief that goes to the lens subagent has the stripped body.

Per `REVIEW_TEAM.md` §Operations, the canonical stripped-field list
lives in the spec and tracks any future score-name additions.

## Saga interaction

When invoked by `doc-brd-autopilot` (or directly), this skill reads
and updates the saga journal at
`.aidoc/review/01_BRD/<BRD-id>/saga.json` per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`. The audit
acts as the **fan-out + fan-in stage** of the saga.

### On entry

At entry, write the audit's start epoch:

```sh
Bash: mkdir -p .aidoc/review/01_BRD/<BRD-id>/ && date +%s > .aidoc/review/01_BRD/<BRD-id>/.skill-start.audit
```

If `.aidoc/review/01_BRD/<BRD-id>/saga.json` exists, read it. Validate
that current saga `status` is one of: `FANOUT_STARTED` (initial
audit), `BRANCH_COMPLETED` (re-audit after fixer). If the status is
something else (e.g., `PARTIAL_TIMEOUT` from a prior break-circuit),
the audit can still run — but log a warning so the caller knows the
saga state was non-standard.

### During lens fan-out (team mode)

For each lens dispatched as a `Task` subagent:

1. Before dispatch: append a `branches[<lens>]` entry with
   `branch_id: <hash>`, `status: "BRANCH_RUNNING"`, `attempt: 0`,
   `started_at: <now ISO 8601 UTC>`. Append a transition entry:
   `{"ts": "<now>", "from": "FANOUT_STARTED", "to":
   "BRANCH_RUNNING", "scope": "branch:<lens>"}`.
2. After dispatch returns: update `branches[<lens>].status` to
   `"BRANCH_COMPLETED"` or `"BRANCH_FAILED"` per the lens's
   persona-output record. Set `ended_at: <now>`. Append a transition
   entry with the appropriate `to` state.

### Before synthesizer dispatch (break-circuit checkpoint)

Per `REVIEW_SAGA.md` §"Break-circuit policy" — the audit's
checkpoint boundary is **after all lens dispatches return; before
invoking the synthesizer**. Check elapsed time:

```sh
Bash: echo $(( $(date +%s) - $(cat .aidoc/review/01_BRD/<BRD-id>/.skill-start.audit) ))
```

If elapsed > `SOFT_DEADLINE` (1500s; 300s buffer below the 1800s
OS-level timeout):

- Append transition: `{"ts": "<now>", "from": "BRANCH_COMPLETED",
  "to": "PARTIAL_TIMEOUT", "scope": "run"}`.
- Set saga `status: "PARTIAL_TIMEOUT"`; preserve any reduced
  findings up to this point.
- Update `updated_at`. Write `saga.json`. Exit cleanly (exit 0).
  The caller (autopilot or harness) can re-invoke.

### After synthesizer reduce

- Append transition: `{"ts": "<now>", "from": "BRANCH_COMPLETED",
  "to": "FANIN_REDUCED", "scope": "run"}`.
- Update saga `status: "FANIN_REDUCED"`. Update `updated_at`. Write
  `saga.json`.
- Synthesizer also writes `verdict.json` (per BRD-RT-002,
  unchanged).
- Exit returns control to the caller; the caller decides next phase
  based on the verdict.

### When invoked standalone (no saga.json on entry)

If `.aidoc/review/01_BRD/<BRD-id>/saga.json` does NOT exist (e.g., a
user runs `/aidoc-flow:doc-brd-audit` directly outside the autopilot
loop), do NOT initialize the full saga schema. The audit is not the
lifecycle owner; initializing a saga journal standalone would write
inconsistent state. Instead:

- Log `saga.json not present; running audit without saga journal
  (standalone mode)`.
- Run the audit's lens fan-out + synthesizer as normal.
- Write blackboard slot files + `verdict.json` + the audit report
  as usual.
- Skip all saga.json transitions.

This preserves backward compatibility with direct skill invocation.
Only autopilot-driven runs produce saga.json.

### When invoked in single_pass mode

If `review_mode: single_pass` is active, the audit does not produce
saga.json (same as standalone above — the saga is a team-mode
artifact). Existing behavior preserved.

## Break-circuit policy

Per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`
§"Break-circuit policy", this skill checks elapsed wall-clock at one
checkpoint boundary: **after all lens dispatches return; before
invoking the synthesizer**. The SOFT_DEADLINE is 1500s
(`ORCHESTRATOR_TIMEOUT=1800s` minus 300s buffer).

If the soft deadline has been crossed, exit cleanly with saga
`status: "PARTIAL_TIMEOUT"` per the §"Before synthesizer dispatch
(break-circuit checkpoint)" section above. If the LLM ignores the
check and the OS sends SIGTERM, saga.json reflects the last
successful checkpoint state (NOT `PARTIAL_TIMEOUT`). Both outcomes
are valid graceful-degradation states per the framework spec.

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

### Table-pipe escape (MD056)

When emitting markdown table cells that contain code spans with shell
pipes (e.g. `` `docker compose ps | grep 'Up'` ``), the unescaped `|`
inside the code span is parsed by markdownlint as a column separator,
tripping **MD056** (column-count mismatch). Two fixes:

- **Preferred:** escape the pipe inside the code span as `\|` —
  renders as `|` in markdown viewers but doesn't break the table.
  Example row: `` | OP-02 | ... | `docker compose ps \| grep 'Up'` | ... | ``
- **Alternative:** move the code span out of the table cell and
  reference it as a footnote or paragraph below the table. The cell
  then carries plain prose like "shell readiness gate (see below)".

Apply to every report row that emits a shell-pipe code span inside a
table cell. Cascade-output that trips MD056 is a SKILL bug, not a
markdownlint over-strictness — fix here, not by lint-ignoring.

Output path: `.aidoc/audit/01_BRD-audit.md` (the `.aidoc/`
provenance tier). Sections — **Summary** (ID, timestamp,
overall status, structural status, content score, **mode** (`team` |
`single_pass`)) · **Score Calculation** (`100 − deductions`, threshold
compare) · **Coverage** (team mode only: lenses ran vs expected,
`quorum_met` boolean) · **Persona Slot Index** (team mode only: paths
to `.aidoc/review/01_BRD/<BRD-id>/<persona>.json` slots, the
synthesizer's `verdict.json` and `report.md`) · **Metadata Findings**
· **Structural Findings** · **Content Findings** (in team mode,
reduced from the synthesizer's report; in single_pass, from this
skill's own per-lens pass) · **Diagram Contract Findings** · **Fix
Queue** (`auto_fixable` / `manual_required` / `blocked`) ·
**Recommended Next Step** · **Cleanup Summary**.

**Always include the `single_pass` advisory** whenever the resolved
`review_mode` is `single_pass` (regardless of trigger context — this
skill does not reliably know whether it is at a gate). Place the
advisory in the Summary section as a callout blockquote:

> **Advisory mode.** This audit ran in `single_pass` — one model
> applying every lens in one context. Per
> `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md`
> §"Scoring, conflicts & the gate", `team` mode is the canonical
> gate review; `single_pass` is a cost-constrained fallback whose
> lens independence is reduced. Score 0-100 here is informational; a
> production gate run should re-audit in `team` mode.

### Regressions (CLEANUP-PR-B item 10)

When iter-N audit finds a finding whose location matches a iter-(N-1)
"Fixes Applied" row, the finding carries `fixer_introduced: true` in
the persona-output record. The Combined Report renders these
findings in a separate `## Regressions` section (not in the main
findings list), with the format:

```
## Regressions

| Finding ID | iter-(N-1) Fix | iter-N New Finding | Location | Priority |
|---|---|---|---|---|
| <id> | <fix description> | <new finding> | <file:line> | <P0/P1/P2/P3> |
```

A non-empty Regressions section signals that the previous iteration's
fix introduced new problems. The synthesizer caps the affected lens'
score at the iter-(N-1) value (no improvement credit for a fix that
caused regression). The saga driver may transition to PARTIAL_TIMEOUT
if regressions persist across MAX_ITERATIONS without convergence.

Schema: see `framework/governance/saga.schema.json` `finding.fixer_introduced`.
Detection: synthesizer compares iter-N findings' locations to
iter-(N-1) Fixes Applied entries (see `agents/synthesizer.md`).

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
