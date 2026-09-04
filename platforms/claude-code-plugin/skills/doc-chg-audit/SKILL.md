---
name: doc-chg-audit
description: Audit a Change Management (CHG) record - run declarative schema, impact/cascade, gate-routing, and change-level checks plus content review, then produce a pass/fail gate-readiness report (no numeric score) for doc-chg-fixer. Use to validate a CHG before requesting gate approval.
metadata:
  tags:
    - sdd-workflow
    - change-management
    - quality-assurance
  custom_fields:
    artifact_type: CHG
    skill_category: quality-assurance
    version: "0.25.0"
    framework_spec_version: "0.51.0"
    last_updated: "2026-06-12"
    adapts: [section_toggles, active_layers, audit_threshold, review_mode]
---

# doc-chg-audit

## Purpose

Run a **unified CHG audit** — declarative schema checks plus impact, cascade,
gate-routing, change-level, and content-quality review — in one pass, producing
a single combined report that `../doc-chg-fixer/SKILL.md` consumes. The
framework ships no runtime code, so **this skill is the validator**: Claude
performs each check directly against the CHG record using the spec as the
contract. In team mode, this skill fans out the CHG crew
(`integration_lead/architect/chaos_engineer/operator/auditor/security_engineer`)
per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md` §Operations
§Review.

CHG is **NOT a lifecycle layer** in the BRD..IPLAN sense: it has no readiness
score. This audit therefore reports **gate-readiness as a pass/fail** plus a
fix list — it does **not** compute a 0–100 readiness score. The quality bar is
**gate approval**, granted by a human via `../gate-check/SKILL.md`, not by a
number. For team-mode dispatch purposes the CHG layer is addressed as
**`09_CHG`** (the layer-id slot occupied by the change-management overlay).

**Scope**: a CHG can touch any artifact along
`BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code`.
**Upstream**: a CHG record. **Downstream**:
`.aidoc/audit/09_CHG-audit.md` and an optional fix-cycle trigger.

## When to Use

Use after a CHG record exists and before handing it to `../gate-check/SKILL.md`
for C3/Emergency approval, or inside the autopilot's audit↔fix cycle. Do **not**
use to author a CHG (use `../doc-chg/SKILL.md` or `../doc-chg-autopilot/SKILL.md`)
or to run the formal gate itself (that is `../gate-check/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior results;
re-evaluate gate-readiness independently each run.

**Report cleanup:** the audit report is a single file
(`.aidoc/audit/09_CHG-audit.md`) overwritten in place each run — no version
cleanup needed. Keep `CHG-NN.F_fix_report_v*.md`.

## Execution Contract

**Input:** CHG path (`docs/governance/chg/CHG-NN_*...`, or
`CHG-EMG-YYYYMMDD-HHMM` for Emergency).

**Sequence:** 1) run schema/required-field checks → 2) run change-level,
source-routing, and impact/cascade checks → 3) record findings → 4) run
content review (per §Review Mode below — `team` fans out lens subagents
with per-lens playbook briefs, `single_pass` runs every lens sequentially
in this skill's own context) → 4a) load each lens's layer-and-lens playbook
from `framework/playbooks/09_CHG/<lens>.md` and inline it under the lens's
brief (team mode) or apply its checks sequentially (single_pass) → 5)
merge/normalize findings, including a playbook-coverage line surfacing which
lenses ran with their playbook attached → 6) write
`.aidoc/audit/09_CHG-audit.md` → 7) if auto-fixable findings exist, hand off
to `doc-chg-fixer`.

## Review Mode

Resolve `review_mode` from `.aidoc/profile.yaml`; if the key is unset
(the project profile is an override-only delta — most knobs are absent),
fall through to the framework default per the precedence chain in
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md` (`framework
defaults < user-global seed < project profile`). The framework default
is `team` at gates (`pre_promotion` / `pre_merge`) and `single_pass` at
write-time (`on_author`). The same fallback rule applies to every other
adaptation knob (`audit_threshold`, `section_toggles`, `active_layers`,
`glossary`). The schema, routing, impact/cascade, and change-level
structural checks below are run **deterministically by this skill in
every mode** — they are the gate floor per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md` §"Scoring,
conflicts & the gate".

### team mode (default at gates)

The content-quality review is performed by a **fan-out of per-lens `Task`
subagents** over a per-artifact blackboard, per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md` §Operations
§Review.

1. **Prepare the blackboard.** `mkdir -p .aidoc/review/09_CHG/<CHG-id>/`
   where `<CHG-id>` is the CHG's short artifact ID (e.g. `CHG-01` or
   `CHG-EMG-20260612-1430`), not the nested folder name or file slug.
   This keeps blackboard paths stable when slugs change.
2. **Read the CHG crew** from
   `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_CREWS.yaml` —
   `{integration_lead: 30, architect: 20, chaos_engineer: 15, operator: 15, auditor: 10, security_engineer: 10}`.
   Weights sum to 100. Rationale: integration_lead carries the dominant
   weight (30) because CHG is fundamentally a propagation problem —
   blast-radius enumeration and cross-layer consistency across the
   affected layers is the lens's core value; operator + chaos_engineer
   get larger weights than typical (15 each) because CHG sits at the
   deploy boundary and covers emergency-change + rollback paths; see
   `REVIEW_TEAM.md` §"Weight allocation rules".
3. **Map each lens to its plugin agent** via the table in
   `../review-team/SKILL.md`:
   - `integration_lead` → `aidoc-flow:solutions-architect` (CHG primary lens —
     propagation completeness across affected layers, gate routing,
     blast-radius enumeration; also CHG author per `REVIEW_CREWS.yaml`)
   - `architect` → `aidoc-flow:solutions-architect`
   - `chaos_engineer` → `aidoc-flow:chaos-engineer`
   - `operator` → `aidoc-flow:devops-release-engineer`
   - `auditor` → `aidoc-flow:traceability-auditor`
   - `security_engineer` → `aidoc-flow:security-engineer`

   Because `aidoc-flow:solutions-architect` carries TWO lens-roles at CHG
   (`integration_lead` + `architect`), each lens is dispatched as a
   **separate `Task` subagent invocation** with its own lens-specific
   playbook brief; do NOT collapse them into one call — the lenses score
   independently and the synthesizer deduplicates findings at fan-in.
3a. **Load the layer-and-lens playbook.** For each lens in the crew,
   resolve and read the playbook content from
   `${CLAUDE_PLUGIN_ROOT}/framework/playbooks/09_CHG/<lens>.md`.
   If the playbook file is missing, mark `branches[<lens>].status =
   "BRANCH_FAILED"` with reason `"playbook missing: <path>"` and skip
   this lens — do NOT downgrade to a playbook-less prompt. Other lenses
   continue. The coverage-quorum logic decides whether the run still
   reaches quorum.
4. **Fan out.** Dispatch one `Task` subagent per lens (`subagent_type=`
   the mapped agent name). Each subagent's brief contains:
   - The absolute artifact path (untrusted content)
   - **Disregard the author self-assessment score.** The lens MUST NOT
     read, cite, or weight any `*_ready_score`/`*_score`/`readiness_score`/
     `audit_score`/`gate_ready` in the artifact when forming its `lens_score`
     (`REVIEW_TEAM.md` GD-05 — read directly, so de-anchored by instruction).
   - The lens name and its weight
   - The slot path `.aidoc/review/09_CHG/<CHG-id>/<lens>.json`
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
   (`subagent_type=aidoc-flow:synthesizer`) against the slot directory. It writes
   **both** companion files (per `agents/synthesizer.md` §"Output"):
   - `.aidoc/review/09_CHG/<CHG-id>/verdict.json` — the authoritative
     machine-readable verdict (`combined_status`, `gate_ready`,
     `structural_status`, `coverage.*`, `blocking_findings_count`,
     `lens_scores`). For CHG, `combined_status` and `gate_ready` are
     the primary fields; `content_score` is recorded but is **not** the
     gate criterion (CHG has no numeric readiness score).
   - `.aidoc/review/09_CHG/<CHG-id>/report.md` — the human narrative
     (mirrors verdict.json values).
7. **Compose the combined audit report.** Read
   `.aidoc/review/09_CHG/<CHG-id>/verdict.json` and `report.md`.
   The final audit report at `.aidoc/audit/09_CHG-audit.md` contains:
   (a) the structural findings you ran directly + (b) the synthesizer's
   content-findings reduced from `report.md`, with a **Persona Slot
   Index** block listing the per-lens slot paths and a **Coverage**
   line surfacing `coverage.quorum_met` for consumers
   (`doc-chg-fixer`, `doc-chg-autopilot`).

**Quorum & coverage.** Per `REVIEW_TEAM.md` §Resilience, if
`verdict.coverage.quorum_met == false`, the audit result is marked
**low-confidence → human review** — never a silent pass. For CHG this
means `gate_ready: false` regardless of finding counts when quorum
fails.

### Output Contract (team mode)

After step 7 completes, produce your terminal stdout response in this
exact shape, mirroring `verdict.json` values verbatim:

```
Combined status: PASS|FAIL
Gate ready: true|false
Structural status: PASS|FAIL
Coverage quorum: met|low_confidence
Report: .aidoc/audit/09_CHG-audit.md
```

Read `combined_status`, `gate_ready`, `structural_status`, and
`coverage.quorum_met` from `verdict.json`. **Do NOT echo any author
self-claimed readiness number** (the CHG body has no readiness score by
design; if such a number was inserted by mistake, the strip step below
removes it before lens dispatch). The synthesizer's `verdict.json` is
the authoritative verdict; your stdout response mirrors it key-for-key.

### single_pass mode (fallback)

Run the content review **in this skill's own context**, applying every
lens (integration_lead / architect / chaos_engineer / operator /
auditor / security_engineer) sequentially in one pass, each lens
consulting its own `framework/playbooks/09_CHG/<lens>.md` playbook
inline. No `Task` subagents, no blackboard. Quorum does not apply.
Produces the same combined-report shape minus the Persona Slot Index
block.

Use this mode when (a) the profile explicitly sets
`review_mode: single_pass`, (b) `Task` subagent dispatch is unavailable
in the current execution context (e.g., crew quorum can't be met because
multiple lens agents are unreachable), or (c) the run is at `on_author`
(write-time) where cost is the primary concern. **Architecture in
v0.4.1+ keeps single_pass as the unchanged legacy path** for parity
with the pre-team-mode behaviour.

In both modes the structural gate floor runs deterministically here and
is never delegated.

### Disregard author self-claim (de-anchor the lens; REVIEW_TEAM.md GD-05)

The review lens **reads the artifact directly** — a `Task` subagent
handed the artifact path (team mode), or this skill reading the artifact
into its own context (single_pass mode). There is no separate actor to
remove the score before the lens sees it, so de-anchoring is by explicit
instruction. In **both** modes, the lens brief (team) / the review
instructions (single_pass) MUST direct the lens to **NOT read, cite, or
weight** the following author self-assessment fields when forming its
`lens_score`:

- `*_ready_score` (e.g. `brd_ready_score`, `prd_ready_score`,
  `ears_ready_score`, etc.)
- `*_score` (e.g. `audit_score`, `readiness_score`)
- `readiness_score`
- `audit_score`
- `gate_ready` (when present as an author-asserted boolean in the
  artifact body — the audit re-computes this from scratch; the
  author's assertion must not anchor the lenses)

These are author self-assessments. Left un-disregarded they create an
anchor effect — the lens output's `lens_score` (or `gate_ready` boolean)
tends toward the author's claim. The surface a lens evaluates is the
artifact's CONTENT (sections, IDs, traceability, prose, propagation
completeness); a number or boolean the author wrote down for itself is
not part of that surface. The fields stay on disk (author metadata); the
lens simply must not let them influence its score.

Per `REVIEW_TEAM.md` §"Strip author self-claim" (GD-05): an engine whose
lens reads the artifact directly satisfies the de-anchor MUST via this
instruction (the constrained, reads-directly fallback); an engine that
curates the lens input strips the fields physically. The canonical
field list lives in the spec.

### No-findings rationale block

When a lens returns an empty `findings[]` array, the lens's
persona-output record MUST include a `no_findings_rationale` string
that names the playbook checks the lens ran and the specific evidence
that supported the empty result. This is part of the persona-output
contract — an empty `findings[]` without a rationale is treated by the
synthesizer as a **failed lens** (the lens did not actually do its
job), not a clean pass. The rationale travels into `report.md` as a
one-line summary per silent lens, so the audit report shows *why*
each silent lens was silent rather than just listing them. For CHG
specifically, a silent integration_lead with no rationale is a
red flag (CHG's primary lens going silent without explanation
suggests the lens skipped propagation enumeration entirely).

## Saga interaction

When invoked by `doc-chg-autopilot` (or directly), this skill reads
and updates the saga journal at
`.aidoc/review/09_CHG/<CHG-id>/saga.json` per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`. The audit
acts as the **fan-out + fan-in stage** of the saga.

### On entry

At entry, write the audit's start epoch:

```sh
Bash: mkdir -p .aidoc/review/09_CHG/<CHG-id>/ && date +%s > .aidoc/review/09_CHG/<CHG-id>/.skill-start.audit
```

If `.aidoc/review/09_CHG/<CHG-id>/saga.json` exists, read it.
Validate that current saga `status` is one of: `FANOUT_STARTED` (initial
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

Note: because `aidoc-flow:solutions-architect` carries two lens-roles at CHG
(`integration_lead`, `architect`), the saga records **two independent
branches** (one per lens-role), not one shared branch. Each branch
transitions independently.

### Before synthesizer dispatch (break-circuit checkpoint)

Per `REVIEW_SAGA.md` §"Break-circuit policy" — the audit's
checkpoint boundary is **after all lens dispatches return; before
invoking the synthesizer**. Check elapsed time:

```sh
Bash: echo $(( $(date +%s) - $(cat .aidoc/review/09_CHG/<CHG-id>/.skill-start.audit) ))
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
  based on the verdict (`gate_ready: true` ⇒ proceed to gate-check;
  `false` ⇒ dispatch fixer).

### When invoked standalone (no saga.json on entry)

If `.aidoc/review/09_CHG/<CHG-id>/saga.json` does NOT exist (e.g.,
a user runs `/aidoc-flow:doc-chg-audit` directly outside the
autopilot loop), do NOT initialize the full saga schema. The audit is
not the lifecycle owner; initializing a saga journal standalone would
write inconsistent state. Instead:

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

Additionally, per `REVIEW_REMEDIATION_FLOW.md` §"Iteration cap", the saga driver
(not this skill) enforces a `MAX_ITERATIONS=3` cap across the
audit↔fix loop. When the saga reaches `MAX_ITERATIONS` without
converging to `gate_ready: true`, the saga driver writes
`status: "PARTIAL_TIMEOUT"` (or `"ESCALATED"` if a P0 finding
remains unresolved) and emits the artifact with the latest verdict.
**This audit treats `PARTIAL_TIMEOUT` as a FAIL (gate-not-ready) but
does NOT retry** — the driver is the only component that re-invokes;
retrying from within the audit would multiply the iteration count.

Change-level enforcement (per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`) does NOT
relax the break-circuit policy: even an Emergency CHG that converges
slowly stops at `MAX_ITERATIONS` and waits for a human review rather
than looping indefinitely. The gate-routing classification (GATE-01 /
GATE-03 / GATE-06 / GATE-08 / GATE-CODE / GATE-SPEC) likewise stays
within the cap.

## Structural Checklist

Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml`,
`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`, and the gate definitions under
`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/`. Style:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`.

**Template-conformance enumeration (mandatory first step).** Load
`CHG-TEMPLATE.yaml` and enumerate the required sections
(`document_control` / `change_control` / `change_description` /
`impact_assessment` / `implementation` / `verification` /
`gate_approval` / `rollback_plan` / `emergency_change` / `glossary`).
Which of those sections are **conditionally required** depends on
`change_level` and `change_source` — see the per-level matrix in
`framework/governance/chg/README.md` §"Section requirements per
change level". The Structure check is satisfied **only** when every
required section (for the artifact's change level + source
combination) appears in the artifact. Any missing required section
is a **blocking finding** — never rationalise it as a "compact" or
"emergency-abbreviated" variant; the conditional-block mechanism is
the *only* way to legitimately omit a section.

**Tier 1 — blocking (error):**

| Check | Verifies | Code |
|-------|----------|------|
| Schema / required fields | `metadata`, `change_control`, `change_description`, `impact_assessment`, `implementation`, `verification` present and non-empty per template | CHG-E001 |
| Change level | `change_level` is one of C1/C2/C3/Emergency **and** matches the actual scope (typo→C1, section→C2, cross-layer→C3, P0/P1 prod→Emergency) | CHG-E001 |
| Gate routing | `entry_gate` matches `change_source` (Upstream/External→GATE-01, Midstream→GATE-03, Design→GATE-06, Execution→GATE-08, Feedback→GATE-CODE, Spec→GATE-SPEC) | CHG-E002 |
| Impact / cascade | `impact_assessment.affected_layers` lists **every** affected artifact; `cascade_direction` correct for the source (downstream / bubble-up / lateral); no template anti-pattern | CHG-E003 |
| Conditional blocks | `rollback_plan` present for C2/C3; `gate_approval.gate` set for C3; `emergency_change` complete for Emergency (incl. `post_mortem_due`, `incident_severity`) | CHG-E004 |
| Spec change | if `change_source: spec`: `semver_impact` set; `change_level` ≥ C2 (never C1); `major`⇒C3; provenance (`why`/`trigger`) present — see `gates/GATE-SPEC_FRAMEWORK.md` | CHG-E002 |

**Tier 2 — advisory (warning):** ID form (`CHG-NN` dash, or
`CHG-EMG-YYYYMMDD-HHMM`; no hierarchical 4-segment IDs); internal links and
template/gate references resolve; registry entry exists; `supersedes` lists
valid artifact IDs; verification checks cover each affected layer.

**Authoring-style check (Tier 2 → Tier 1 at threshold).** Verify the CHG
record complies with `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`:
no banned phrases, form preferences observed (tables/bullets over prose where
homogeneous), size targets met within +50% (CHG body ≤ 1500 words). **Promote
to blocking** when ≥3 banned phrases occur in one section OR the record
exceeds its size target by >50%.

**Combined status:** `PASS` (gate-ready) only if all Tier 1 checks pass and no
blocking issues remain; otherwise `FAIL`. There is **no numeric score** — the
report states `gate_ready: true|false` and the next required approval (C1 self,
C2 peer review, C3/Emergency `../gate-check/SKILL.md`).

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `chg-document` (not `template`) |
| `purpose` | yes | `governance` |
| `change_level` | yes | `C1`, `C2`, `C3`, `Emergency` |
| `change_source` | yes (≥C2) | `upstream`, `midstream`, `design`, `execution`, `external`, `feedback`, `spec` |

Findings: `VALID-M001` missing `change_source`; `VALID-M002` invalid level/source
value; `VALID-M003` `document_type` not `chg-document`.

## Content Sub-Checks

These sub-checks supplement the structural / metadata gates with
content-quality checks targeting failure modes the single-pass review
historically missed. Section references use the CHG template's section
names (`change_description` / `impact_assessment` / `rollback_plan`
/ `gate_approval` / `emergency_change`).

### Sub-check A1 — Cell actionability (auditor lens)

Every claim in `change_description`, `impact_assessment`, and
`rollback_plan` must commit to an ACTIONABLE statement — a verb +
object + observable criterion — not just be non-empty. Raise a
finding when:

- A `change_description` bullet states what changed but not how the
  change is observable post-deploy (e.g., "improved logging" with no
  log-line example or metric).
- An `impact_assessment.affected_layers` row names a layer but
  carries no concrete artifact ID (must point to `BRD-NN` /
  `PRD-NN` / `EARS-NN` / etc., not just "BRD layer").
- A `rollback_plan` step reads "revert change" without naming the
  commit, the artifact version, or the deploy unit being reverted.
- A `verification` row reads "tested" or "validated" without the
  test ID, command, or measurable outcome.

Severity: P2 default; P1 if the non-actionable cell appears on
`rollback_plan` (rollback non-actionability is gate-blocking for C2
and above) or on a C3/Emergency `gate_approval` path.

### Sub-check A2 — Assumption-capture discipline (auditor lens)

Every assumption-shaped statement in `change_description` or
`impact_assessment` — "X holds for this change", "Y is unchanged by
this cascade", "Z is deferred to follow-up CHG" — must be either:

- Captured as a P2 advisory finding for the audit report (so the
  reviewer sees what the author assumed without verifying), OR
- Linked to an explicit follow-up CHG ID for deferred items (see
  Sub-check SE1 below for deferred-decision safety).

Buried assumptions ("Privy supports custodial USDC" sitting inside
a `change_description` paragraph without acknowledgment) are an
audit finding.

Severity: P2.

### Sub-check A3 — Cross-section pointer validity (auditor lens)

For every cross-reference inside the CHG (a section pointer such as
"see rollback_plan §3", an artifact ID like `BRD-01` / `SPEC-04`,
or a tag like `@spec:` / `@brd:` / `@ears:` referenced in
`impact_assessment.affected_layers`):

1. Verify the target ID exists in the referenced section (or in the
   referenced upstream artifact).
2. Verify the referenced content matches the citing claim's shape
   (e.g., a reference "as constrained by BRD-01 §Budget" requires
   BRD-01 §Budget to express a measurable cap).

Note: clause (2) overlaps A1's "missing artifact ID" bullet — both
will fire on the same finding. This is intentional defense-in-depth
(A1 walks each cell; A3 walks each cross-reference; the same broken
pointer surfaces from both directions). The fixer treats them as one
finding to resolve.

Severity: P2 default; P1 if the broken pointer appears on the
`gate_approval` path or in a `rollback_plan` reference.

### Sub-check BA1 — Gate-routing testability (business_analyst lens)

The declared `entry_gate` must match the declared `change_source`
per the routing table in `framework/governance/chg/README.md`:

- `upstream` / `external` → `GATE-01`
- `midstream` → `GATE-03`
- `design` → `GATE-06`
- `execution` → `GATE-08`
- `feedback` → `GATE-CODE`
- `spec` → `GATE-SPEC`

The routing must be **testable** — that is, the gate definition
under `framework/governance/chg/gates/<GATE>.md` must exist AND
declare an approver role that the `gate_approval` block (when
present) can name. A `change_source` set without a matching
`entry_gate` (or with a fabricated gate not in the table) is a
finding.

Severity: P1 (gate-routing mismatch is the exact failure mode the
CHG-E002 structural check exists to catch; BA1 catches the
testability sub-failure within a routing that passes the structural
schema check but has no resolvable gate definition).

### Sub-check SE1 — Deferred-decision safety (security_engineer lens)

For every `change_description` item or `impact_assessment` row
marked "deferred to follow-up CHG":

1. The follow-up CHG ID must be named (`CHG-NN` or
   `CHG-EMG-YYYYMMDD-HHMM`).
2. The trigger condition for the follow-up must be stated (e.g.,
   "deferred until Q3 throughput audit completes" or "deferred
   pending vendor SLA confirmation").
3. If the deferred item is a security-sensitive control (auth,
   crypto, data retention, access boundary) AND the current CHG is
   C3 or Emergency, the deferral must additionally name the
   compensating control active in the interim.

A deferred item missing (1) or (2) is P1 (the deferral becomes a
silent drop; downstream layers cannot enforce a follow-up that has
no ID). A deferred security-sensitive item missing (3) is P0 (a
C3/Emergency change is shipping with an unmitigated control gap).

Severity: P0 / P1 per the cases above; never lower than P1.

### Excluded patterns — downstream-owned by design

The above sub-checks must NOT fire on content the CHG deliberately
defers to downstream artifacts. Examples:

- An `impact_assessment` row that says "detailed test coverage
  enumerated in TDD-04" is not an A1 actionability violation — the
  CHG correctly delegates test enumeration to the TDD.
- A `change_description` that says "rollback procedure detailed in
  IPLAN-03 §rollback" is not an A1 actionability violation — the
  CHG correctly delegates implementation steps to the IPLAN.

Recognize these via explicit delegation phrases ("detailed in X",
"enumerated in X", "delegated to X", where X is a named downstream
artifact ID) and skip the finding.

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

Output: `.aidoc/audit/09_CHG-audit.md`, with sections — **Summary** (CHG ID,
timestamp, overall status, `gate_ready: true|false`, change level, entry gate) ·
**Gate-Readiness** (PASS/FAIL + the required approver per the change level, not
a score) · **Metadata Findings** · **Schema Findings** · **Change-Level &
Routing Findings** · **Impact / Cascade Findings** · **Content Findings** ·
**Persona Slot Index** (team mode only — list each
`.aidoc/review/09_CHG/<CHG-id>/<persona>.json` path for the six lenses:
`integration_lead.json`, `architect.json`, `chaos_engineer.json`,
`operator.json`, `auditor.json`, `security_engineer.json`) ·
**Coverage** (a single line surfacing `coverage.quorum_met` (`met` |
`low_confidence`) and `coverage.playbook_coverage` — which lenses ran
with their `framework/playbooks/09_CHG/<lens>.md` playbook attached
versus which failed playbook-load and were marked `BRANCH_FAILED`) ·
**Fix Queue** (`auto_fixable` / `manual_required` / `blocked`) ·
**Recommended Next Step** (fixer, or `../gate-check/SKILL.md` if
gate-ready) · **Cleanup Summary**.

The Persona Slot Index and Coverage block are emitted only in `team`
mode; in `single_pass` mode those two sections are omitted (the
combined report shape collapses to its legacy form). The
authoritative machine-readable companion is the synthesizer's
`verdict.json` at `.aidoc/review/09_CHG/<CHG-id>/verdict.json` —
`doc-chg-fixer` and `doc-chg-autopilot` consume `verdict.json` as
the source of truth; this markdown report is the human narrative
mirror.

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

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor only this skill's declared knobs:
`section_toggles` (a toggled-off **optional** section is not a finding; a
missing **required** section still is — and CHG's conditional blocks
follow the change-level matrix, not `section_toggles`), `active_layers`
(never flag the absence of — or a missing reference to — a layer the
project disabled in `impact_assessment`, per the cascade rule),
`audit_threshold` (CHG has no numeric readiness score, so this knob is
only honored when the project profile uses it to **raise** the
authoring-style banned-phrase / size-target thresholds; ignored
otherwise), and `review_mode` (select `team` or `single_pass` per
§Review Mode above; if `review_mode` is unset, fall through to the
framework default `team` at gates / `single_pass` at write-time).
Ignore unknown keys.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Hand-off to doc-chg-fixer

Normalize every finding to: `source` (`schema`|`routing`|`impact`|`metadata`|`content`),
`code`, `severity` (`error`|`warning`|`info`), `file`, `field/section`,
`action_hint`, `confidence` (`auto-safe`|`auto-assisted`|`manual-required`).
`doc-chg-fixer` consumes the `.aidoc/audit/09_CHG-audit.md` report.

## Related Resources

- Create: `../doc-chg/SKILL.md` · Fix: `../doc-chg-fixer/SKILL.md` · Generate:
  `../doc-chg-autopilot/SKILL.md` · Gate: `../gate-check/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/`
