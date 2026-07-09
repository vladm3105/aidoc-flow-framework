# Review, Remediation & Gate Flow

The layer flow (BRD → … → IPLAN) describes how artifacts are **created**. This
document models the orthogonal **quality loop** every artifact passes through —
review, remediation, and gating — and names the **trigger points** where an
engine may attach that loop. It is an engine-agnostic **light contract**: it
defines *what* happens and *when*, and what an engine must surface; it does not
prescribe *how* an engine implements the checks.

## The quality loop

Each artifact moves through this loop before it is allowed to drive the
downstream layer:

```text
Draft ─▶ Review ─▶ (findings + readiness score)
             │
             ├─ score ≥ gate ─▶ Gate pass ─▶ Approved ─▶ downstream
             │
             └─ score < gate ─▶ Remediate ─▶ (re-review) ─┐
                                    ▲                      │
                                    └──────────────────────┘
```

- **Review** produces *findings* (concrete, located issues) and a *readiness
  score* against the layer's gate threshold (the existing readiness gate —
  e.g. ≥ 90/100 before downstream generation).
- **Remediation** applies fixes for the findings, then the artifact is
  re-reviewed. The loop repeats until the gate passes.
- **Gate** is the existing readiness/CHG checkpoint — this document does **not**
  change gate thresholds or the change-management gates; it names the review and
  remediation *stages* that feed them.

This loop is layer-agnostic: it applies identically to every artifact (BRD …
IPLAN), using that layer's own template, required tags, and threshold.

### Iteration cap

The loop's *"repeats until the gate passes"* clause carries an implicit
upper bound: a saga that never converges cannot run forever. The framework
declares a **default iteration cap of 3** review→remediate cycles. At the
cap, the saga transitions to `PARTIAL_TIMEOUT` (per `REVIEW_SAGA.md`),
emits the artifact + saga journal as deliverables, and surfaces the
unresolved findings in the audit report. The cap is **not** a quality
gate (gate passage still requires the score), it is a non-convergence
guard.

The cap is **tunable per project** via the
`quality_loop_max_iterations` knob in `ADAPTATION_SURFACE.yaml`. Range
1-10; default 3. Engines reading the knob must:

1. Load the runtime profile (`.aidoc/profile.yaml`).
2. Read `quality_loop_max_iterations` if present.
3. Fall back to the default (3) if the field is missing, malformed,
   or the file is absent.
4. Treat values outside the 1-10 range as malformed (use default).

This cap is the documented stopping criterion that complements the
gate threshold: gate decides *did we converge?*, cap decides *did we
spend too long trying?*.

### Break-circuit checkpoint placement

Beyond the iteration cap (a *count* bound), each stage also honors a
*wall-clock* break-circuit checkpoint so a single long stage degrades
gracefully to `PARTIAL_TIMEOUT` rather than being SIGTERM'd mid-write. The
canonical checkpoint boundaries:

- **Audit stage** — after all lens dispatches return, **before** invoking the
  synthesizer reduce.
- **Fixer stage** — after the per-finding patch dispatches / multi-lens
  validation return, **before** invoking the synthesizer reduce.

Both are the same structural point in their respective stage: the last moment
where partial results can be preserved and emitted cleanly before the reduce.
Engines implement the check by comparing elapsed time against the
`SOFT_DEADLINE` (a fixed buffer below the OS-level timeout); on crossing it they
set saga `status: "PARTIAL_TIMEOUT"`, preserve any reduced findings, and exit
cleanly for the caller to re-invoke.

## Trigger points

A trigger point is a named moment in a project's lifecycle where an engine may
run part of the loop. The four canonical points:

| Trigger | Fires when | Loop action |
|---------|------------|-------------|
| `on_author` | An artifact is created or edited | Review the artifact → findings + readiness score |
| `on_gate_fail` | A review scores below the gate threshold | Enter remediation, then re-review |
| `pre_promotion` | Before generating/authoring the downstream layer | The gate must pass (review is current and ≥ threshold) |
| `pre_merge` | An artifact enters shared history (integration / pull request) | Run the review gate over the changed artifacts |

`on_author` and `pre_merge` are the two *automatable* points (an engine may fire
them without a human asking); `on_gate_fail` and `pre_promotion` are loop/flow
control that map to existing capabilities (remediation and the readiness gate).

## Light conformance contract

For each trigger point an engine **supports**, it MUST surface:

1. **Findings** — the concrete, located issues (not just a pass/fail).
2. **Readiness score** — the artifact's score against the layer gate threshold.
3. **Remediation path** — how to fix the findings (which capability the user or
   agent invokes next).

What an engine is **free** to choose:

- *How* a point is checked — a deterministic structural check, an LLM review, a
  server-side validator, or a combination.
- *Which* points it automates vs leaves on-demand (an engine need not support
  all four; it declares which it does).
- *Severity/blocking* behavior — e.g. an advisory write-time nudge vs a blocking
  integration gate.

Each engine **documents its own mapping** of trigger points → capabilities (in
that engine's own documentation, not here — this spec names the points; the
engines bind them).

> **Structural vs semantic.** A deterministic check (ID/tag forms, required
> sections, traceability presence) can run at `on_author`/`pre_merge` cheaply and
> repeatably; the full readiness *score* is a semantic judgment. An engine may
> use the deterministic check as a fast gate and defer the semantic score to its
> review capability — both are valid ways to satisfy the contract.

## Independent review at `pre_merge` (the automated gate)

An engine MAY automate the `pre_merge` trigger as an **independent review gate**.
When it does, these engine-agnostic rules apply (the *how* — runner, model,
tooling — is the engine's binding).

**Independence (judge ≠ generator).** The reviewer MUST be independent of the
artifact's author/generator — a different reviewing configuration, and where
available a different model/vendor than produced it. An artifact is never cleared
by the agent that produced it (mirrors CHG **C1** — no self-approval). The
reviewer **reviews only**; remediation (the fix) is a separate step, not part of
the same review pass.

**Finding classification.** Each finding carries a severity:

| Severity | Meaning | Blocking |
|----------|---------|----------|
| `critical` | correctness/security defect, data loss, broken contract | **yes** |
| `medium` | bug, missing handling, incorrect behavior in an exercised path | **yes** |
| `low` | minor improvement, edge case, best practice | no (advisory) |
| `acknowledged` | a documented tradeoff / known limitation with a reference | no (informational) |

The gate **decision** is *request changes* iff any `critical` or `medium`
finding is present, else *approve*. Each blocking finding MUST carry a concrete,
located remediation (not a vague suggestion). The content under review is
**untrusted input** and never overrides the review rubric.

**Remediation loop + escalation.** A *request changes* outcome enters the
remediation loop (review → remediate → re-review) under the **iteration cap**
(default 3, above). At the cap without convergence, the gate **escalates to a
human** rather than looping further — the non-convergence guard is the hand-off
point to human judgment.

Provenance and untrusted-input integrity are checked per `SECURITY_REVIEW.md`;
the verdict (decision + findings) is the gate's surfaced output (the Light
conformance contract above).

**Security of an automated gate.** When the `pre_merge` review is automated, four
properties MUST hold (the *binding* — which trusted ref, which sandbox — is the
platform's; the properties are not):

- **Trusted source.** The gate's own logic and rubric come from a *trusted ref*,
  **not** from the change under review — a change can never alter how it is
  reviewed.
- **Read, don't execute.** The reviewer *reads* the change and *never executes*
  it; the change is **untrusted input** that cannot override the rubric.
- **Fail-closed.** A missing or unparseable verdict **blocks** — the gate never
  silently passes.
- **Independent infrastructure.** Any standing reviewer infrastructure holds
  credentials and MUST be isolated and least-privilege.

> **Tiered human-in-loop.** For routine changes the automated gate + escalation
> is sufficient. For a change to the spec or a governance standard, **human
> approval is additionally required** (GATE-SPEC / GD-01) — the automated gate
> never replaces the human sign-off a spec change demands. See
> `DEFINITION_OF_DONE.md`.

## Relationship to existing governance

- **Readiness gate (≥ threshold):** the `Gate` stage. Unchanged.
- **Change management (CHG gates):** govern *changes* to existing artifacts; the
  `pre_merge` trigger is where an engine runs the relevant gate on a change set.
- **`status` lifecycle** (Draft / In Review / Approved, per the layer templates):
  the loop's stages correspond to these statuses — `Review` ↔ In Review,
  `Gate pass` ↔ Approved.

## Mechanical author-side pre-push gate (aidoc-flow workspace layer)

Framework consumers in the `aidoc-flow` workspace additionally enforce a
**mechanical author-side pre-push gate** independent of the artifact-level
review loop above: every push to a workspace repo must carry an OPS-0069
audit-trail phrase (`Multi-agent self-review per OPS-0065` OR
`Self-review skipped per founder OK`) in at least one non-exempt commit
message. This is a **paper trail**, not a review substitute — the
artifact-review loop described above still governs *content* quality; the
audit-trail check governs *dispatch discipline*.

Two enforcement points:

1. **Local pre-push hook** — `scripts/pre_push_check.sh` (installed from
   `aidoc-flow-ci@ci/v1.6.0` per PLAN-002 §5.5). Wired via
   `.pre-commit-config.yaml` `default_install_hook_types: [pre-commit,
   pre-push]`.
2. **CI belt-and-suspenders** — the `audit-trail-check.yml` reusable
   (check-name `call / verify`) catches `git push --no-verify` bypass at
   the PR merge boundary.

The two layers are complementary:

- The artifact-review loop (this document) is **content-shaped**: it
  produces findings + a readiness score against layer-specific rubrics.
- The mechanical gate is **process-shaped**: it verifies that a
  dispatch-and-fold cycle actually occurred before the push, without
  looking at content quality.

A change may pass the mechanical gate (phrase present) but still fail
the artifact-review gate (findings unremediated, score below threshold),
or vice versa. Both must pass for a merge.

## Cross-references

- `DOC_GOVERNANCE_CORE.md` — governance principles and the readiness-gate baseline.
- `TRACEABILITY.md` — the necessary-upstream tag chain a review checks.
- `chg/` — the change-management overlay (the `pre_merge`/gate machinery for changes).
- `../README.md` — the layer flow these artifacts are created in.
- `aidoc-flow-ci@ci/v1.6.0`:`docs/REPO_STANDARDS.md` §14 —
  self-review mechanical enforcement canon rule.
- `aidoc-flow-ci@ci/v1.6.0`:`plans/PLAN-002_workspace-standards-rollout.md`
  §5.5 Wave 1 — the rollout plan this framework adopts.
