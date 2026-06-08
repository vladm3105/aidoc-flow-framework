# EARS-01 Unified Review Report — Iteration 5

## Executive Summary

**combined_status: FAIL** | content_score: 84 / threshold: 90 | structural_status: PASS | blocking_findings: 0 | quorum: 5/5 lenses

EARS-01 passes all Tier-1 structural checks (element IDs valid, all six required sections present and non-empty, EARS syntax valid, no vague timing terms, metadata valid; the prior STRUCT-001 malformed 5391a/5391b IDs are resolved). The structural floor is cleared.

The artifact fails the quality gate solely because the weighted content score (84) does not reach the framework threshold (90). There are no P0 or P1 blocking findings; the failure is driven by six P2 quality gaps distributed across four lenses. The security lens (weight 8) returns a perfect score with zero findings, signalling that the §4 security obligations are structurally sound; the quality deficit originates from requirements atomicity, measurability, BDD-traceability granularity, and timing-contract consistency.

The artifact is substantively complete and well-structured. The six P2 gaps are targeted and fixable. The ten P3 findings are improvement items that do not block the gate individually but depress the content score collectively. Addressing all six P2 gaps and the most impactful P3 clusters (traceability matrix expansion, idempotency declarations, ADR-marker naming) would close the score gap and enable a PASS verdict on iteration 6.

---

## Coverage

| Metric | Value |
|---|---|
| Lenses expected | 5 |
| Lenses returned | 5 |
| Quorum met | true (5/5 >= ceil(5*0.5)=3) |
| Confidence | Full — no low-confidence flag |

---

## Per-Lens Scores

| Lens | Weight | Score | Weighted Contribution |
|---|---|---|---|
| requirements_specialist | 35 | 82 | 28.70 |
| tech_lead | 25 | 86 | 21.50 |
| qa_lead | 20 | 79 | 15.80 |
| chaos_engineer | 12 | 84 | 10.08 |
| security_engineer | 8 | 100 | 8.00 |
| **Totals** | **100** | | **84.08 → 84** |

---

## Gate Decision

The gate is deterministic. PASS requires: structural_status == PASS AND content_score >= 90 AND blocking_findings_count == 0.

- structural_status: PASS (met)
- content_score: 84 < 90 (not met)
- blocking_findings_count: 0 (met)

**VERDICT: FAIL** (content score 84 below threshold 90; no P0/P1 blockers present)

---

## Playbook Coverage

| Check | Findings | Notes |
|---|---|---|
| C1 | 2 | Missing percentile qualifiers; missing per-line BDD slots |
| C2 | 4 | Atomicity (primary line conjunctions; budget partitioning) |
| C3 | 1 | Unmeasurable throttling response shape |
| C4 | 2 | ADR marker naming; firebreak ordering |
| C5 | 6 | PRD anchor gaps; glossary omission; idempotency declarations |
| beyond-checklist | 1 | QA-006: unsubstantiated '100%' coverage claim |

beyond_checklist / total = 1/16 = 6.3% — within the 30% drift threshold; playbook is current.

---

## Findings by Severity

### P2 — Quality Gaps (6 findings; collectively responsible for gate fail)

**RS-001** | Check C5 | EARS.01.03.a0ae (§3.1) and EARS.01.03.3312 (§3.4)
Service-Owner role-restriction obligation has no authorising PRD element. Both lines impose role-based access-control obligations but the cited @prd element (PRD.01.09.21ad) establishes no authorization or denial obligation, and PRD §7 explicitly lists authentication out-of-scope. Neither line carries an [author assumption] deferral marker.
Recommendation: (a) Add '[author assumption — no PRD access-control element]' to both lines mirroring the c060 TLS treatment; or (b) drop the role-restriction clause from a0ae and convert 3312 to a generic deferral; or (c) add a PRD §12 authorization constraint and re-point both @prd tags.

---

**RS-002** | Check C2 | EARS.01.03.a2ae (lines 262-268) and EARS.01.03.9671 (lines 272-278)
Three conjoined obligations in one unwanted-behaviour line. a2ae and 9671 each fuse three separately-testable obligations: the fail-closed/reject decision, the no-code-issued invariant, and the user-facing message. The doc already split 539a/539b on this atomicity principle; this same principle should apply here.
Recommendation: Split each into an outcome line (decision + no code issued, WITHIN 500 ms p95) and a separate message line, each carrying its own @prd tag, mirroring the 539a/539b split.

---

**RS-003** | Check C3 | EARS.01.03.ee86 (§3.3, lines 189-191)
Throttling response not measurable / not enumerated. 'explicit throttling response' names no status code, no user-facing message, and no WITHIN latency clause. Every sibling rejection line names a concrete response. A BDD author cannot assert the Then without inventing the response contract.
Recommendation: Name the throttling contract — an HTTP 429 (or a named throttling message) plus a WITHIN p95 clause; keep only the numeric rate threshold as the [ADR deferred] value.

---

**TL-001** | Check C1 | EARS.01.03.ab5e (155), .c7e3 (163), .a17e (171), .b5fa (292), .d8a2 (300)
Detection/audit/cooldown emit bounds carry no percentile while every other timed rule uses p95. Bare millisecond bounds ('WITHIN 100 ms', 'WITHIN 50 ms') with no statistical qualifier prevent engineers from determining the measurement harness (max-over-window vs percentile sampling) and the resulting SLO.
Recommendation: Append 'at the 95th percentile' to each bare bound, or state '(hard ceiling, 100% of events)' if an absolute bound is intended. Apply to all five affected elements.

---

**QA-001** | Check C1 | §3.1–§3.5 (all 30 EARS lines); §5 coverage matrix
No per-line BDD slot; §5 matrix maps only 5 feature groups for 30+ individual lines. None of the ~30 §3 lines or 9 §4 lines carry an inline @bdd: tag or [BDD-pending] placeholder. The matrix's five-row structure cannot enumerate which EARS lines require distinct BDD scenarios.
Recommendation: Add a [BDD-pending:EARS.01.03.xxxx] inline placeholder beneath each EARS line in §3 and §4, OR expand the §5 matrix to one row per EARS line with columns: EARS line ID | upstream PRD anchor | downstream BDD slot.

---

**CE-001** | Check C2 | EARS.01.03.a2ae, .135e, .8df7 (submit path, lines 254-268, 321-325)
Submit-path budget unpartitioned across sequential timeout/retry stages. Three dependencies each independently claim a WITHIN 500 ms p95 budget; no line states how the single submit p95 envelope is partitioned. Under worst-case sequential failure the aggregate wait compounds well past 500 ms.
Recommendation: Add an EARS line (or extend 8df7/135e) stating the submit-path aggregate p95 budget and its partition across screen + pool-claim/retry + durable-commit, OR add an ADR-deferred marker covering the aggregate partition.

---

### P3 — Improvement Items (10 findings)

**RS-004** | Check C2 | EARS.01.03.f909, .ab5e, .c7e3
Coupled secondary obligations folded into primary lines (idempotency rule; enforce+emit-event). f909 embeds a no-dedup normative rule inline with no element ID; ab5e and c7e3 couple enforcement and observability obligations under one latency budget.
Recommendation: Promote f909's no-dedup rule to its own ubiquitous element. For ab5e/c7e3, split enforcement and detection-event obligations into separate lines or reclassify as explicitly compound with a shared budget statement.

---

**RS-005** | Check C5 | EARS.01.04.c060 (§4 Security) and EARS.01.04.ca05 (§4 Reliability)
Two §4 quality rows lack a PRD anchor (BRD-direct trace, self-disclosed). Both carry explicit in-doc deferral markers — c060 '[author assumption — no PRD transport-encryption element]'; ca05 has no @prd tag with PRD §5 treating availability as a post-launch objective. Both are sanctioned deferrals.
Recommendation: Accept as-is given the explicit deferral markers; optionally add PRD §12 anchors so both §4 rows gain PRD anchors and the C5 gap closes cleanly.

---

**TL-002** | Check C4 | EARS.01.03.ab5e, .c7e3, .b5fa, .d8a2
Bare '[ADR deferred: BRD.01.08.daeb]' markers do not name the deferred quantity. Unlike well-formed sibling markers (db78, 0b67, 135e, 00b9, ee86), these four markers name only the ADR topic without spelling out the specific deferred item.
Recommendation: Extend each bare marker to name the deferred quantity, e.g. '[ADR deferred: BRD.01.08.daeb — anti-abuse submission-volume threshold and cooldown]', matching the explicit form already used for other deferrals.

---

**TL-003** | Check C5 | EARS Glossary (lines 411-422) vs PRD §15 (lines 427-436); §4 preamble
'p95' is the artifact's load-bearing measurable but is absent from the EARS glossary. PRD §15 defines 'p95'; EARS uses 'at the 95th percentile' throughout §3 and the 'p95' shorthand in §4, but the EARS glossary omits the term.
Recommendation: Add a 'p95' (or '95th percentile') row to the EARS glossary matching the PRD §15 definition verbatim, noting that the §3 prose form and §4 'p95' shorthand denote the same measure.

---

**QA-002** | Check C2 | §5 Traceability — coverage matrix
Coverage matrix lacks EARS line ID column; constraint- and risk-derived lines absent; §4 lines absent. At least 13 EARS lines derive from PRD §12/§13 anchors not covered by the five §9 feature rows; all nine §4 quality-attribute lines are absent from the matrix entirely.
Recommendation: Add an EARS line ID column to the §5 matrix. Add rows for constraint/risk-derived lines and §4 quality-attribute lines, each with their upstream PRD anchor and a BDD-pending slot.

---

**QA-003** | Check C5 | EARS.01.03.a17e
Audit-log write has no idempotency declaration. Four other stateful lines carry explicit idempotency parentheticals; a17e does not. Retry semantics for this durable append are undeclared.
Recommendation: Append an idempotency note, minimum: '(Idempotency: each grant/deny event produces exactly one audit record; writes retried within the same request scope are deduplicated by request ID.)'

---

**QA-004** | Check C5 | EARS.01.03.00b9
Capacity-utilization alert emission has no idempotency declaration. No edge-trigger, cooldown, or deduplication guard is declared; a BDD scenario cannot assert the expected emission count.
Recommendation: Add an edge-trigger or idempotency note stating the alert fires at most once per threshold-crossing transition.

---

**QA-005** | Check C5 | EARS.01.03.ab5e; EARS.01.03.c7e3
Throttle and cooldown state transitions have no idempotency declarations. Concurrent threshold crossings before a write completes could apply state transitions multiple times or emit duplicate detection events. Dependent IF-lines (b5fa, d8a2) cannot be unambiguously tested.
Recommendation: Add idempotency parentheticals to both lines declaring at-most-once throttle-set semantics per detection window (ab5e) and cooldown reset/extend policy per configured policy (c7e3).

---

**QA-006** | Check beyond-checklist:coverage-scope-claim | §5 Traceability — final paragraph
'PRD 100%' coverage claim is unsubstantiated for §4 quality-attribute lines and constraint/risk-derived lines. The §5 closing note claims complete PRD coverage but the matrix structure does not enumerate §4 lines, §12 constraint anchors, or §13 risk anchors.
Recommendation: Revise the coverage claim to accurately scope what is mapped: 'all five P1 §9 functional features mapped; §4 quality-attribute and §12/§13-derived lines tracked inline via @prd tags (BDD slot assignment deferred to L4)'.

---

**CE-002** | Check C4 | EARS.01.03.db78, .a2ae, .0b67, .135e, .8df7 (submit path)
Submit-path multi-dependency failure ordering / firebreak not stated. No line states the check order between pool-claim and reputation-screen; a guaranteed-fail request (pool exhausted) may still invoke the external reputation screen, wasting budget.
Recommendation: State the submit-path check order explicitly (cheap-local checks -> pool availability -> reputation screen -> durable claim), naming the firebreak between internal and external dependencies.

---

## Contested Findings

None. All lenses agreed on direction; no either/or judgment conflicts requiring human resolution.

---

## Discarded Findings

None. All 16 findings carried valid playbook check citations (C1–C5 or beyond-checklist). Zero findings discarded.

---

*Report generated by the Synthesizer (review chairperson). verdict.json is authoritative for machine consumers; this narrative is advisory enrichment. Both files agree on all numeric values.*
