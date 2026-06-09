# ADR-RT-001 Implementation Plan

> Combined plan + impl PR per established per-layer rollout pattern (mirrors EARS-RT-001 + BDD-RT-001).

**Goal:** Wire team-mode fan-out into `doc-adr-audit` + `doc-adr-fixer` SKILLs, add playbook injection, author 6 ADR playbooks, validate via live ADR cascade.

**Architecture:** Mechanical replication of the BDD-RT-001 pattern for the ADR layer (Layer 5). Framework spec contract from LAYER-PLAYBOOKS-001 unchanged; only ADR-specific configuration + content lands.

**Design authority:** `plans/LAYER-PLAYBOOKS-001-DESIGN.md` + `platforms/claude-code-plugin/skills/doc-bdd-audit/SKILL.md` (BDD-RT-001 template — freshest reference).

---

## ADR crew (from `framework/governance/REVIEW_CREWS.yaml`)

```yaml
ADR:
  author: architect
  review: {architect: 35, tech_lead: 25, chaos_engineer: 8, security_engineer: 12, operator: 10, auditor: 10}
```

Sum: 100. Rationale (per file comment): "Security-heavy at ADR (12 > 8) — ADRs encode trust boundaries, authn/authz choices, and crypto decisions; security is the dominant axis."

## Lens → plugin agent mapping

| Lens | Weight | Agent | Note |
|---|---|---|---|
| `architect` | 35 | `solutions-architect` | ADR author + lens |
| `tech_lead` | 25 | `solutions-architect` (alt role-binding) | |
| `security_engineer` | 12 | `security-engineer` | security-heavy at ADR |
| `operator` | 10 | `devops-release-engineer` | rollout/reversibility view |
| `auditor` | 10 | `traceability-auditor` | upstream-trace audit |
| `chaos_engineer` | 8 | `chaos-engineer` | failure-mode of the decision |

---

## File structure

### Modified

| Path | Change |
|---|---|
| `platforms/claude-code-plugin/skills/doc-adr-audit/SKILL.md` (268 → ~500 lines) | Add §Review Mode (team + single_pass), §Saga interaction, §Break-circuit policy, playbook injection step 3a + augmented step 4 |
| `platforms/claude-code-plugin/skills/doc-adr-fixer/SKILL.md` (113 → ~300 lines) | Add §Remediate Mode (team + single_pass), §Saga interaction, §Break-circuit policy |
| `CHANGELOG.md` (root) | `[Unreleased]` entry for framework 0.14.2 → 0.14.3 + plugin 0.9.0 → 0.10.0 |
| `platforms/claude-code-plugin/CHANGELOG.md` | `[0.10.0]` entry |
| `ROADMAP.md` | Shipped bullet |
| `plans/HANDOFF.md` | Dated narrative |
| `docs/PARITY.md` | Layer Playbooks row extended to BRD/PRD/EARS/BDD/ADR |
| `docs/TAGGING.md` | New row for `claude-code-plugin/v0.10.0` |
| `framework/VERSION` | 0.14.2 → 0.14.3 (PATCH — adds ADR playbooks under framework/) |
| `platforms/claude-code-plugin/VERSION` | 0.9.0 → 0.10.0 (MINOR — new layer wiring) |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | Hardcoded "0.14.2" → "0.14.3" |

### Created

| Path | Lens / Weight |
|---|---|
| `framework/playbooks/05_ADR/architect.md` | 35 |
| `framework/playbooks/05_ADR/tech_lead.md` | 25 |
| `framework/playbooks/05_ADR/security_engineer.md` | 12 |
| `framework/playbooks/05_ADR/operator.md` | 10 |
| `framework/playbooks/05_ADR/auditor.md` | 10 |
| `framework/playbooks/05_ADR/chaos_engineer.md` | 8 |

---

## Implementation sequence

### Task 1: Author 6 ADR playbooks

Hybrid content shape per `framework/governance/REVIEW_TEAM.md` §Playbooks. ~95-110 lines each. Per-lens content topics (derived from ADR-layer concerns: decision integrity, trust-boundary encoding, alternatives-considered rigor, reversibility classification, security-heavy axis weighting):

**architect (35, solutions-architect)** — Decision integrity + alternatives lens (ADR author).

- C1: Decision statement is single-sentence imperative ("THE service SHALL adopt X for Y reason"). Diffuse / multi-clause → P1 citing C1.
- C2: Alternatives Considered section enumerates ≥2 alternatives with reject rationale per alternative. Missing alternative or stub rationale → P1 citing C2.
- C3: Trade-offs explicit (what we gain / what we give up). Implicit-only → P2 citing C3.
- C4: Reversibility classification present (one-way / two-way / reversible). Missing → P2 citing C4.
- C5: Boundary crossed by this decision called out (service / module / component / data). Missing → P3 citing C5.

**tech_lead (25, solutions-architect)** — Implementability + drift lens.

- C1: Decision implementable as written — no semantic ambiguity in adoption mechanics. Ambiguous → P1 citing C1.
- C2: Constraints from upstream BRD/PRD/EARS satisfied by this decision (not contradicted). Contradicts upstream → P1 citing C2.
- C3: Downstream impact on SPEC + TDD enumerated (what the SPEC must encode, what the TDD must verify). Missing → P2 citing C3.
- C4: Migration path from current state described when reversibility ≠ one-way. Missing path on reversible decisions → P2 citing C4.
- C5: Cross-ADR consistency check — does any prior ADR conflict / supersede / get superseded by this one? Missing cross-ref → P3 citing C5.

**security_engineer (12, security-engineer)** — Trust-boundary lens (DOMINANT at ADR per crew rationale).

- C1: Trust boundaries explicitly named when the decision crosses one (process / network / tenant / role). Crossed silently → P1 citing C1.
- C2: AuthN choice (who) + AuthZ choice (what) called out when the decision affects either. Missing → P1 citing C2.
- C3: Crypto algorithm + key-management choice specified when the decision touches encryption. Hand-wave ("encrypt at rest") → P2 citing C3.
- C4: Threat model named (which threat does this defend against; which it does NOT). Missing → P2 citing C4.
- C5: Failure-closed vs failure-open behavior stated when the decision touches a security control. Missing → P2 citing C5.

**operator (10, devops-release-engineer)** — Rollout / reversibility lens.

- C1: Rollback procedure described when reversibility is two-way or reversible. Missing → P2 citing C1.
- C2: Observability hooks identified (what metric / log / event detects success/failure of this decision in prod). Missing → P2 citing C2.
- C3: Deployment ordering called out when this decision sequences with others (e.g., "must precede ADR-NN"). Missing → P3 citing C3.
- C4: Capacity / cost impact enumerated (rough order-of-magnitude). Hand-wave → P3 citing C4.
- C5: Runtime config knob declared when the decision can be toggled at runtime (feature flag, profile, env). Missing on toggleable decisions → P3 citing C5.

**auditor (10, traceability-auditor)** — Upstream-trace + ID-conformance lens.

- C1: Every `@brd: / @prd: / @ears:` tag in the ADR resolves to an existing upstream element. Broken tag → P1 citing C1.
- C2: Element IDs conform to `ADR.NN.SS.xxxx` 4-hex content-hash pattern. Non-conformant → P1 citing C2.
- C3: Each Decision row in the summary table has a paired element-level ID in the body. Orphan summary row → P2 citing C3.
- C4: Cumulative `@brd / @prd / @ears` header on the ADR doc resolves cleanly to upstream layers. Missing/broken → P2 citing C4.
- C5: Cross-ADR `@adr:` references use dash form for doc-level refs (`@adr: ADR-NN`); element-level refs use dotted form. Wrong form → P3 citing C5.

**chaos_engineer (8, chaos-engineer)** — Decision-failure-mode lens.

- C1: "What breaks if this decision is wrong?" answered (one or more failure scenarios named). Missing → P2 citing C1.
- C2: Blast radius classified (single-service / cross-service / data-loss-possible). Missing → P2 citing C2.
- C3: Detection-time bound stated for the failure mode (how fast we'll know it's broken). Missing → P3 citing C3.
- C4: Mitigation pre-built when the decision is one-way + high blast radius. Missing → P3 citing C4.
- C5: At-most-once vs at-least-once semantics declared when the decision touches a side-effect-producing operation. Missing → P3 citing C5.

Beyond-checklist escape per playbook (template): one paragraph naming the kinds of issues that fall outside the Cn checks. Synthesizer keeps these if `check: "beyond-checklist:<tag>"` is provided.

### Task 2: Wire team-mode into `doc-adr-audit/SKILL.md`

Adopt the BDD-RT-001 audit-wiring pattern (PR #112 commit `8951396f`). Add four new sections + extend Frontmatter `adapts`:

- `## Review Mode` — team-mode default at gates; single_pass fallback; structural-floor invariant
- `## Saga interaction` — entry, fan-out, break-circuit, reduce, standalone-fallback
- `## Break-circuit policy` — 1500s SOFT_DEADLINE per skill invocation
- Step 3a — playbook resolution: `${CLAUDE_PLUGIN_ROOT}/../../framework/playbooks/05_ADR/<lens>.md` → `BRANCH_FAILED` if missing (no silent downgrade)
- Step 4 — inline playbook content into per-lens Task brief under `## Layer-specific playbook`; lens MUST cite `check: "C1"` or `"beyond-checklist:<tag>"`; uncited findings discarded by synthesizer
- Frontmatter `adapts: [section_toggles, active_layers, audit_threshold]` → append `review_mode`

### Task 3: Wire team-mode into `doc-adr-fixer/SKILL.md`

Adopt the BDD-RT-001 fixer-wiring pattern (PR #112 commit `e9f786f6`). Add three new sections + extend Frontmatter `adapts`:

- `## Remediate Mode` — team-mode patch-validation cycle for P0/P1 (dispatch responsible lens as Task subagent in patch-validation mode → `<persona>.fix_<N>.json` slot); deterministic for P2/P3 (no lens validation); single_pass fallback unchanged
- `## Saga interaction` — enter from `FANIN_REDUCED`; transitions; `BRANCH_COMPENSATING` for P0/P1 patch-validation cycles; close at `CLOSED` or escalate to `ESCALATED`
- `## Break-circuit policy` — 1500s SOFT_DEADLINE
- Frontmatter `adapts: [section_toggles]` → `[section_toggles, review_mode]`

### Task 4: Bump versions UPFRONT

Lesson from EARS-RT-001 (PR #108 initial CI failure on GATE-SPEC-E005 because VERSION wasn't bumped when framework/** changed). Bump in this PR series:

- `framework/VERSION` 0.14.2 → 0.14.3 (PATCH — new playbook content within existing artifact class, no contract changes)
- `platforms/claude-code-plugin/VERSION` 0.9.0 → 0.10.0 (MINOR — new layer SKILL behavior wiring)
- `tests/conformance/platforms/test_plugin_release_metadata.py` hardcoded "0.14.2" → "0.14.3"
- Run `bash scripts/sync-version-refs.sh` to propagate across plugin.json, marketplace.json, 52 SKILL frontmatters, READMEs, docs/PARITY.md current-state row, CLAUDE.md current-state line, `framework_spec_version` in `claude-code-plugin/FRAMEWORK_SPEC_VERSION`, etc.
- Run `bash tools/sync-plugin-framework.sh` to mirror canonical → vendored under `platforms/claude-code-plugin/framework/playbooks/05_ADR/`

### Task 5: Live ADR cascade

`bash tests/scripts/test-acceptance.sh url-shortener --live --phase=cascade --from-layer=adr --to-layer=adr`

Expected: ADR-01.md drafted from upstream BRD/PRD/EARS/BDD; 6-lens fan-out per audit; convergence to PASS within 2-3 iter cycles. Wall-clock budget: 5400s (SAGA-BUDGET-001). Score gate: ≥ 90.

Acceptance criteria per the EARS-RT-001 / BDD-RT-001 pass-criteria pattern:

1. All 6 ADR slot files at `.aidoc/review/05_ADR/<ADR-id>/{architect,tech_lead,security_engineer,operator,auditor,chaos_engineer}.json` present
2. `verdict.json` `combined_status: PASS` with `content_score >= 90` and `coverage.quorum_met: true`
3. `report.md` + `04_BDD-audit.md` (actually `05_ADR-audit.md`) present
4. Saga journal shows parallel `BRANCH_RUNNING` + `BRANCH_COMPLETED` transitions (same-second timestamps, proving fan-out is parallel)
5. Every committed finding cites a Cn check or `beyond-checklist:` tag
6. `sdd_doc_lint` on `docs/05_ADR/ADR-01.md` exits 0 (only WARNING-level findings tolerable)

### Task 6: Doc-of-record + open PR

Update + commit:

- `CHANGELOG.md` (root) entry "Added — Framework Spec 0.14.3 + Plugin 0.9.0 → 0.10.0 (ADR-RT-001)"
- `platforms/claude-code-plugin/CHANGELOG.md` `[0.10.0]` entry
- `ROADMAP.md` Shipped row for ADR-RT-001
- `plans/HANDOFF.md` dated narrative
- `docs/PARITY.md` Layer Playbooks coverage row
- `docs/TAGGING.md` plugin tag row
- Commit cascade evidence: `examples/url-shortener/docs/05_ADR/ADR-01.md`, `.aidoc/review/05_ADR/`, `.aidoc/audit/05_ADR-audit.md`
- Regenerate `.secrets.baseline` if saga.json document_fingerprint triggers detect-secrets
- Push branch + open PR with verdict.json + cascade evidence cited in PR description

---

## Out of scope (deferred)

- SPEC-RT-001, TDD-RT-001, IPLAN-RT-001 (separate per-layer follow-up PRs per task list #266-268)
- Final `@unittest.skip` removal from `test_playbook_coverage.py` (task #258 — happens with the last per-layer PR once all 45 playbooks present)
- Hermes-platform mirror of ADR-RT-001 (deferred per `plans/HERMES-BACKLOG.md`)
- CLAUDE.md "Current state" line plugin version sync (noted as a separate doc-of-record gap; the sync-version-refs hook only matches the framework string in that line)

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| ADR draft fails because no upstream BDD-01.md on the example | Verify `examples/url-shortener/docs/04_BDD/BDD-01.md` is present on main (it is, post-PR #112). Cascade upstream-check (phase 0) catches this anyway. |
| Cascade timeout (was the issue in BDD-RT-001 run #1) | SAGA-BUDGET-001 bumped budget to 5400s (PR #111). Should comfortably accommodate ADR's 6-lens fan-out + 2-3 iter cycles. |
| security_engineer lens dominant axis introduces P1 cluster (vs BDD where chaos_engineer was dominant) | Acceptable; the fixer's team-mode patch-validation cycle handles P1s correctly. ADR is the first layer where security is dominant — useful calibration signal. |
| `architect` lens binding to `solutions-architect` agent (same as `tech_lead`) — agent prompt overload? | The lens-mapping table in `review-team/SKILL.md` already binds these two lenses to this agent; the brief specifies which lens to apply at dispatch time. Pattern proven at SPEC + TDD layers (also share `solutions-architect`). |
| sync-plugin-framework.sh skips `playbooks/05_ADR/` if its TOOLS_FILES enumeration is stale | The script syncs whole subtrees (`SUBTREES=(layers governance registry playbooks)`); playbooks is auto-included. No new directory enumeration needed. |

## Review log

### Pass 1 — 2026-06-08 — self-review

Walk the plan top-down looking for gaps:

1. **REVIEW_CREWS.yaml ADR row not actually changed by this PR** — confirmed; ADR crew was declared at 0.12.0 (CHAOS-SEC-SPLIT-001). Plan does NOT modify that file. ✓
2. **saga_driver.py already declares `05_ADR` crew** (architect/tech_lead/chaos_engineer/security_engineer/operator/auditor) — confirmed by grep on tools/saga_driver.py. No saga_driver edit needed. ✓
3. **Playbook frontmatter sync** — `scripts/sync-version-refs.sh` already extended for playbook frontmatter (LAYER-PLAYBOOKS-001 task #271). Will auto-propagate the framework_spec_version into the 6 new ADR playbooks. ✓
4. **Conformance test for playbook coverage** — `test_playbook_coverage.py` still has `@unittest.skip` per task #258. Adding 6 ADR playbooks moves coverage to 28/45 (was 22/45). Will NOT remove the skip in this PR (final-cleanup PR does that). ✓
5. **Lens → plugin agent mapping** — `architect` AND `tech_lead` both bind to `solutions-architect`. The lens brief distinguishes them at Task dispatch time. Same pattern at SPEC + TDD layers per `review-team/SKILL.md`. ✓
6. **Auditor cross-ADR ref check (C5)** — uses `@adr:` tag form. ID_NAMING_STANDARDS.md confirms `ADR-NN` (dash) for doc-level, `ADR.NN.SS.xxxx` (dotted) for element-level. ✓
7. **Operator lens C5 ("toggleable decisions")** — vs ADAPTATION_SURFACE knobs. Acceptable scope — ADRs that introduce a runtime knob should reference the surface; not all ADRs do. ✓
8. **Pass-criteria step 3 wrote `04_BDD-audit.md`** — typo from copy-paste. Fixed inline above: `05_ADR-audit.md`. ✓
9. **CLAUDE.md "Current state" stale plugin version** — pre-existing issue (4 versions stale). Out of scope here; noted in Out-of-scope list. ✓

Pass 1: 9 findings, all addressed inline (typos fixed, scope-clarifications added, pre-existing items deferred).

### Pass 2 — 2026-06-08 — re-review after Pass 1 patches

Re-walk the plan with fresh eyes:

1. **Pass 1 finding 8 typo fixed** — confirmed `05_ADR-audit.md` in step 3. ✓
2. **Task 4 says "sync-version-refs.sh" but the hook is at scripts/sync-version-refs.sh AND also wired to fire on VERSION change** — confirmed; just running `git commit` triggers it. Plan still calls it explicitly for safety; redundant but harmless. ✓
3. **No Hermes work in this PR** — confirmed; per plugin-first policy, Hermes mirror deferred. Captured in Out of scope. ✓
4. **All references to PR #110 / #111 / #112 are correct** — STY03 fence-fix (#110), SAGA-BUDGET-001 (#111), BDD-RT-001 (#112). All merged. ✓
5. **6 playbook lenses match `tools/saga_driver.py:_LAYER_CREWS["05_ADR"]` exactly** — architect, tech_lead, chaos_engineer, security_engineer, operator, auditor. Match. ✓
6. **CHANGELOG entry placement** — should go BEFORE the EARS-RT-001 entry (most recent first). Note for impl. ✓
7. **Plan VERSION bump direction** — framework PATCH 0.14.2→0.14.3 + plugin MINOR 0.9.0→0.10.0. Mirrors EARS-RT-001 + BDD-RT-001 exactly. ✓

Pass 2 verdict: zero new substantive gaps. Plan ready.
