# SPEC-RT-001 Implementation Plan

> Combined plan + impl PR per established per-layer rollout pattern (mirrors EARS-RT-001 + BDD-RT-001 + ADR-RT-001).

**Goal:** Wire team-mode fan-out into `doc-spec-audit` + `doc-spec-fixer` SKILLs, add playbook injection, author 5 SPEC playbooks, validate via live SPEC cascade.

**Architecture:** Mechanical replication of the ADR-RT-001 pattern for the SPEC layer (Layer 6). Framework spec contract from LAYER-PLAYBOOKS-001 unchanged; only SPEC-specific configuration + content lands.

**Design authority:** `plans/LAYER-PLAYBOOKS-001-DESIGN.md` + `platforms/claude-code-plugin/skills/doc-adr-audit/SKILL.md` (ADR-RT-001 template — freshest reference).

---

## SPEC crew (from `framework/governance/REVIEW_CREWS.yaml`)

```yaml
SPEC:
  author: architect
  review: {architect: 30, tech_lead: 30, integration_lead: 20, chaos_engineer: 10, security_engineer: 10}
```

Sum: 100. Rationale (per file comment): "Equal split (10 / 10) — SPEC specifies both performance/resilience and security controls; both axes carry equal weight."

**5 lenses** — the smallest crew across all 8 layers (no operator, no auditor; integration_lead first appears at SPEC).

## Lens → plugin agent mapping

| Lens | Weight | Agent | Note |
|---|---|---|---|
| `architect` | 30 | `solutions-architect` | SPEC author + lens |
| `tech_lead` | 30 | `solutions-architect` | (same agent, distinct brief) |
| `integration_lead` | 20 | `solutions-architect` | **new lens at SPEC**; binds to solutions-architect |
| `chaos_engineer` | 10 | `chaos-engineer` | equal-weight split |
| `security_engineer` | 10 | `security-engineer` | equal-weight split |

Three lenses bind to `solutions-architect` (architect / tech_lead / integration_lead). Pattern is established (ADR has 2 such bindings; SPEC has 3). The brief specifies which lens to apply at Task dispatch time.

---

## File structure

### Modified

| Path | Change |
|---|---|
| `platforms/claude-code-plugin/skills/doc-spec-audit/SKILL.md` (267 → ~500 lines) | Add §Review Mode + §Saga interaction + §Break-circuit policy + playbook injection (step 3a + augmented step 4) |
| `platforms/claude-code-plugin/skills/doc-spec-fixer/SKILL.md` (115 → ~300 lines) | Add §Remediate Mode + §Saga interaction + §Break-circuit policy |
| `CHANGELOG.md` (root) | `[Unreleased]` entry for framework 0.14.3 → 0.14.4 + plugin 0.10.0 → 0.11.0 |
| `ROADMAP.md` | Shipped bullet (if applicable) |
| `plans/HANDOFF.md` | Dated narrative |
| `docs/PARITY.md` | Layer Playbooks row extended to BRD/PRD/EARS/BDD/ADR/SPEC |
| `docs/TAGGING.md` | New row for `claude-code-plugin/v0.11.0` |
| `framework/VERSION` | 0.14.3 → 0.14.4 (PATCH — SPEC playbooks under framework/) |
| `platforms/claude-code-plugin/VERSION` | 0.10.0 → 0.11.0 (MINOR — new layer wiring) |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | Hardcoded "0.14.3" → "0.14.4" |

### Created

| Path | Lens / Weight |
|---|---|
| `framework/playbooks/06_SPEC/architect.md` | 30 |
| `framework/playbooks/06_SPEC/tech_lead.md` | 30 |
| `framework/playbooks/06_SPEC/integration_lead.md` | 20 |
| `framework/playbooks/06_SPEC/chaos_engineer.md` | 10 |
| `framework/playbooks/06_SPEC/security_engineer.md` | 10 |

---

## Implementation sequence

### Task 1: Author 5 SPEC playbooks

Hybrid content shape per `framework/governance/REVIEW_TEAM.md` §Playbooks. ~95-110 lines each. Per-lens content topics (derived from SPEC-layer concerns: interface contracts, sequence diagrams, integration semantics, performance/resilience NFRs, security controls):

**architect (30, solutions-architect)** — Specification integrity + boundary lens (SPEC author).

- C1: Every section the SPEC template requires is present (header, interfaces, sequences, NFRs, controls, contracts). Missing → P1 citing C1.
- C2: Each interface defined as (name, inputs, outputs, errors, semantics). Hand-wavy interface → P2 citing C2.
- C3: Each ADR decision the SPEC inherits is reflected (the SPEC does not contradict an inherited ADR commitment). Contradiction → P1 citing C3.
- C4: SPEC altitude maintained (not a re-statement of EARS, not a class-level design). Wrong altitude → P2 citing C4.
- C5: Section-level traceability (every section trades to upstream ADR/EARS or declares "no upstream"). Orphan section → P3 citing C5.

**tech_lead (30, solutions-architect)** — Implementability + drift lens.

- C1: Every interface is implementable in the target stack (no impossible contracts). Impossible → P1 citing C1.
- C2: Sequence diagrams are well-formed (every send has a receive; numbered steps consistent). Malformed → P2 citing C2.
- C3: Error-handling is explicit per interface (per-error: cause, response, retry semantics). Missing → P2 citing C3.
- C4: Concurrency model named (single-threaded / actor-per-X / shared-state-with-locks). Missing on concurrent paths → P2 citing C4.
- C5: Resource ownership declared (which component owns each persistent resource). Missing → P3 citing C5.

**integration_lead (20, solutions-architect)** — Cross-component-contract lens (NEW at SPEC).

- C1: Every component boundary (this-service ↔ adjacent-service) has a named contract (interface + version + delivery semantics). Missing → P1 citing C1.
- C2: Compatibility matrix declared when the boundary supports multiple consumer versions. Hand-wave → P2 citing C2.
- C3: Failure semantics across the boundary stated (timeout / retry / circuit-break / DLQ). Missing → P2 citing C3.
- C4: Schema-evolution policy named for shared data (backward / forward / both / breaking). Missing → P2 citing C4.
- C5: Observability across the boundary (who exposes which trace / metric / log when the boundary is crossed). Missing → P3 citing C5.

**chaos_engineer (10, chaos-engineer)** — Resilience-under-load lens.

- C1: Performance NFR has a concrete target (p95 / p99 latency, throughput, error budget). Missing/vague → P1 citing C1.
- C2: Saturation curve characterized (system behavior beyond design load). Unknown → P2 citing C2.
- C3: Degradation order specified when overloaded (which feature degrades first, which is preserved). Missing → P2 citing C3.
- C4: Recovery time after a transient fault bounded (MTTR target). Missing → P3 citing C4.
- C5: At-most-once / at-least-once semantics stated for every side-effect-producing interface. Missing → P3 citing C5.

**security_engineer (10, security-engineer)** — Control-implementation lens.

- C1: Each ADR-named security control implemented in the SPEC (authn at boundary X, authz at boundary Y, audit at boundary Z). Missing → P1 citing C1.
- C2: Crypto choices instantiated (algorithm + mode + key-management call-out per ADR). Hand-wave → P2 citing C2.
- C3: Input-validation rule stated per public interface (allowlist / denylist / typed-parse). Missing → P2 citing C3.
- C4: Failure-closed default in this SPEC matches the ADR commitment. Mismatch → P1 citing C4.
- C5: Audit-event emission specified for security-relevant operations. Missing → P3 citing C5.

### Task 2: Wire team-mode into `doc-spec-audit/SKILL.md`

Adopt the ADR-RT-001 audit-wiring pattern (PR #113 commit `0181ed75`). Add four new sections + extend Frontmatter `adapts`:

- `## Review Mode` (team default at gates; single_pass fallback)
- `## Saga interaction` (entry / fan-out / break-circuit / reduce / standalone)
- `## Break-circuit policy` (1500s SOFT_DEADLINE)
- Step 3a — playbook resolution: `framework/playbooks/06_SPEC/<lens>.md` → `BRANCH_FAILED` if missing
- Step 4 — playbook inlined into per-lens Task brief; uncited findings discarded by synthesizer
- Frontmatter `adapts: [section_toggles, active_layers, audit_threshold]` → append `review_mode`

### Task 3: Wire team-mode into `doc-spec-fixer/SKILL.md`

Adopt the ADR-RT-001 fixer-wiring pattern (PR #113 commit `9c9780e3`):

- `## Remediate Mode` (team-mode patch-validation for P0/P1; deterministic for P2/P3; single_pass fallback unchanged)
- `## Saga interaction` (FANIN_REDUCED → BRANCH_COMPENSATING for P0/P1 → CLOSED or ESCALATED)
- `## Break-circuit policy` (1500s SOFT_DEADLINE)
- Frontmatter `adapts: [section_toggles]` → `[section_toggles, review_mode]`

### Task 4: Bump versions UPFRONT

EARS-RT-001 lesson applied — bump in this PR series:

- `framework/VERSION` 0.14.3 → 0.14.4 (PATCH)
- `platforms/claude-code-plugin/VERSION` 0.10.0 → 0.11.0 (MINOR)
- `tests/conformance/platforms/test_plugin_release_metadata.py` "0.14.3" → "0.14.4"
- Run `bash scripts/sync-version-refs.sh` (propagates across plugin.json, marketplace.json, SKILL frontmatters, READMEs, docs/PARITY.md, CLAUDE.md current-state line)
- Run `bash tools/sync-plugin-framework.sh` (mirrors canonical → vendored)
- Add `docs/TAGGING.md` row for `claude-code-plugin/v0.11.0`

### Task 5: Live SPEC cascade

`bash tests/scripts/test-acceptance.sh url-shortener --live --phase=cascade --from-layer=spec --to-layer=spec`

Expected: SPEC-01.md drafted from upstream BRD/PRD/EARS/BDD/ADR; 5-lens fan-out per audit; convergence to PASS within 2-3 iter cycles. Wall-clock budget: 5400s (SAGA-BUDGET-001). Score gate: ≥ 90.

Acceptance criteria:

1. All 5 SPEC slot files at `.aidoc/review/06_SPEC/<SPEC-id>/{architect,tech_lead,integration_lead,chaos_engineer,security_engineer}.json` present
2. `verdict.json` `combined_status: PASS` with `content_score >= 90` and `coverage.quorum_met: true`
3. `report.md` + `06_SPEC-audit.md` present
4. Saga journal shows parallel `BRANCH_RUNNING` + `BRANCH_COMPLETED` transitions (same-second timestamps)
5. Every committed finding cites a Cn check or `beyond-checklist:` tag
6. `sdd_doc_lint` on `docs/06_SPEC/SPEC-01.md` exits 0

### Task 6: Doc-of-record + open PR

Update + commit CHANGELOG, HANDOFF, docs/PARITY.md, docs/TAGGING.md, cascade evidence (`docs/06_SPEC/`, `.aidoc/review/06_SPEC/`, `.aidoc/audit/06_SPEC-audit.md`), `.secrets.baseline` if saga.json fingerprint triggers detect-secrets. Push branch + open PR citing verdict.json + cascade evidence.

---

## Out of scope (deferred)

- TDD-RT-001 / IPLAN-RT-001 (task #267, #268)
- Final `@unittest.skip` removal from `test_playbook_coverage.py` (task #258 — happens with the last per-layer PR)
- Hermes mirror (deferred per `plans/HERMES-BACKLOG.md`)
- CLAUDE.md "Current state" plugin-version sync (pre-existing doc-of-record gap)
- New dedicated `integration-lead.md` plugin agent (the `solutions-architect` agent serves the lens via distinct brief; same pattern as `architect` + `tech_lead`)

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| SPEC draft fails because no upstream ADR-01.md on the example | Verify `examples/url-shortener/docs/05_ADR/ADR-01.md` is present on main (it is, post-PR #113). Cascade upstream-check (phase 0) catches anyway. |
| `integration_lead` lens dispatch confuses solutions-architect agent (3 lenses on same agent) | The brief explicitly names the lens; established pattern at ADR (2 lenses on solutions-architect). Risk: agent might bleed lens concerns across runs. Mitigation: if observed, fold into beyond-checklist findings. |
| Equal-weight chaos/security split surfaces P1 cluster on both axes | Acceptable; the fixer's team-mode patch-validation handles P1s correctly. Expected at SPEC layer where both NFRs and security controls land. |
| 5-lens crew (smallest yet) produces less coverage per audit | The architect+tech_lead+integration_lead trio (3 × 30+30+20 = 80% of weight) already covers the bulk of SPEC concerns; chaos/security at 10/10 add the cross-cutting axes. Total coverage matches the doc altitude. |
| sync-plugin-framework.sh / sync-version-refs.sh missed step | Both proven on EARS/BDD/ADR rollouts; no new failure mode expected. |

## Review log

### Pass 1 — 2026-06-09 — self-review

1. **REVIEW_CREWS.yaml SPEC row unchanged** — SPEC crew was declared at 0.12.0 (CHAOS-SEC-SPLIT-001). Plan does NOT modify that file. ✓
2. **saga_driver.py already declares `06_SPEC` crew** (architect/tech_lead/integration_lead/chaos_engineer/security_engineer) — confirmed by grep. ✓
3. **integration_lead is a new lens at SPEC** — no `integration-lead.md` agent file exists. Per `review-team/SKILL.md` table, `integration_lead` binds to `solutions-architect`. Plan addresses this in Out-of-scope. ✓
4. **3 lenses bind to solutions-architect** (architect / tech_lead / integration_lead) — established pattern (ADR has 2 such bindings; same agent, distinct briefs). ✓
5. **5-lens crew is smallest** — confirmed by REVIEW_CREWS.yaml inspection. No operator + no auditor at SPEC (those are layer-specific; SPEC altitude doesn't require deployment-ordering or tag-trace auditing). ✓
6. **Playbook frontmatter sync** — `scripts/sync-version-refs.sh` already extended for playbook frontmatter (LAYER-PLAYBOOKS-001 task #271). Will auto-propagate `framework_spec_version: "0.14.4"` into the 5 new SPEC playbooks. ✓
7. **Conformance test for playbook coverage** — `test_playbook_coverage.py` still has `@unittest.skip` per task #258. Adding 5 SPEC playbooks moves coverage to 33/45 (was 28/45). Will NOT remove the skip in this PR. ✓
8. **Pass-criteria step 3 mentions `06_SPEC-audit.md`** — matches the layer-directory convention. ✓
9. **No Hermes work** — per plugin-first policy. ✓
10. **`integration_lead.md` playbook lens C1 mentions "named contract"** — clarified to (interface + version + delivery semantics) so it's concrete. ✓
11. **Plan VERSION bump direction** — framework PATCH 0.14.3→0.14.4 + plugin MINOR 0.10.0→0.11.0. Mirrors precedent. ✓

Pass 1: 11 findings, all clarifications / confirmations addressed inline.

### Pass 2 — 2026-06-09 — re-review

1. **Pass 1 finding 4** (3-lens binding on solutions-architect) — verified by re-reading review-team/SKILL.md mapping table. Each lens's brief is distinct (the agent prompt is identical but the per-lens playbook content + role declaration drive the lens behavior). ✓
2. **chaos_engineer lens C2 "Saturation curve"** — well-defined at SPEC altitude (vs ADR's "what breaks if wrong"); the SPEC is where saturation behavior is characterized. ✓
3. **security_engineer C4 "failure-closed match"** — checks SPEC against ADR; the lens uses cross-layer comparison (legitimate at SPEC altitude). ✓
4. **All references to PR numbers** — STY03 fence-fix #110, SAGA-BUDGET-001 #111, BDD-RT-001 #112, ADR-RT-001 #113. All merged. ✓
5. **5-lens crew → 5 playbook files** — match. ✓

Pass 2 verdict: zero new substantive gaps. Plan ready.
