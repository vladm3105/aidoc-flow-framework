# ADR-01.F — Fix Report v001

**Artifact:** ADR-01 — Link Record Storage (Managed KV Store as Durable Mapping Substrate)
**Layer:** 05_ADR
**Fix date:** 2026-06-08
**Mode:** team (review_mode unset → framework default `team`)
**Saga iteration:** 1 · fixer fix-iteration: 1
**Input audit:** `.aidoc/review/05_ADR/ADR-01/report.md` (combined_status FAIL, content_score 86)

---

## Summary

| Metric | Value |
|--------|-------|
| Findings in (blocking) | 1 P1 |
| Findings in (advisory) | 4 P2 + 4 P3 |
| Findings fixed | 9 / 9 |
| Findings remaining | 0 |
| Files created | 1 (`security_engineer.fix_1.json`) |
| Files modified | 1 (`docs/05_ADR/ADR-01.md`) |
| Structural lint | clean (sdd-doc-lint exit 0; STY02/STY03 resolved) |

The single blocking P1 (security_engineer C1, API↔store trust boundary) was
patched in §3 + §6 and **lens-validated** by the `security-engineer` subagent:
`resolved=true, regression=false`, lens_score **74 → 92**. The four P2 and four
P3 advisory findings were applied deterministically (no lens validation per
team-mode policy). Adding the remediation content pushed the document over the
STY03 blocking length (2467 words); it was condensed back to a clean lint
(verbose prose trimmed in §1/§2/§3/§9 + Appendix; remediation content kept).

---

## Fixes Applied

| Code | Issue | Fix | File / Location | Confidence |
|------|-------|-----|-----------------|------------|
| MERGED-P1-001 | API↔store trust boundary undeclared (security_engineer C1) | Added §3 bullet `ADR.01.03.1050` naming a per-service principal (provider IAM role / scoped least-privilege key) + TLS 1.2+ in-transit + fail-closed on auth/TLS failure; mirrored posture into the §6 Integration-points row. | ADR-01.md §3, §6 | auto-assisted |
| MERGED-P2-001 | Reversibility classification absent (architect C4) | Added §3 bullet `ADR.01.03.f5f5` — explicit `Reversibility: one-way`, machine-greppable, cross-linked to §7 Rollback. | ADR-01.md §3 | auto-safe |
| MERGED-P2-002 | Write-ordering for count vs. mapping unspecified (tech_lead C1) | Added §3 bullet `ADR.01.03.5536` (mapping written once, never rewritten; count via isolated partial-field write) and extended the §5 `ADR.01.05.9107` mitigation cell to cite it. | ADR-01.md §3, §5 | auto-assisted |
| MERGED-P2-003 | Blast radius unclassified (chaos_engineer C2) | Added a **Blast radius** column to the §7 MVP-phases table — Phase 1 cross-service, Phase 2/3 single-service; §7 RPO monitoring row labelled data-loss-possible. | ADR-01.md §7 | auto-assisted |
| MERGED-P2-004 | Data-at-rest encryption stance absent (security_engineer C3) | Added §6 data-at-rest note `ADR.01.03.0db1` — provider-managed envelope encryption (AES-256), provider-managed KMS key, provider default rotation; CMK deferred. | ADR-01.md §6 | auto-assisted |
| MERGED-P3-001 | Issuance at-most-once semantics undeclared (chaos_engineer C5) | §3 bullet `ADR.01.03.3315` — at-most-once per logical submission, idempotency keyed on submitter key (fallback content-derived), cross-ref BDD.01.03.bcfb. | ADR-01.md §3 | auto-assisted |
| MERGED-P3-002 | Increment side-effect semantics undeclared (chaos_engineer C5) | Folded into `ADR.01.03.5536` — increment at-most-once on hot path + at-least-once reconciliation backstop with per-event dedup marker (no double-count). | ADR-01.md §3, §5 | auto-assisted |
| MERGED-P3-003 | Write-conflict alert threshold unquantified (chaos_engineer C3 / operator) | §7 monitoring row quantified: `> 5 conflicts/min sustained over a 5-min window → WARN` (BRD.01.08.9665; provisional pending load-test calibration). | ADR-01.md §7 | auto-assisted |
| MERGED-P3-004 | Rollback lacks numbered steps (operator C1) | §7 Rollback replaced prose with a 7-step runbook (halt → drain → snapshot → provision → import+verify → re-point → RPO smoke test); `one cycle` → `~2–4 hours at MVP volume`. | ADR-01.md §7 | auto-assisted |

### New element IDs introduced (§3, hash-derived per ID_NAMING_STANDARDS)

`ADR.01.03.f5f5` (reversibility) · `ADR.01.03.3315` (issuance) ·
`ADR.01.03.1050` (trust boundary) · `ADR.01.03.5536` (write-ordering) ·
`ADR.01.03.0db1` (encryption-at-rest, anchored in §6). No collision with the
existing §3 id `ADR.01.03.5c3c`.

---

## Validation Slots index

| Slot file | Lens | Finding | Resolved | Regression | lens_score |
|-----------|------|---------|----------|------------|------------|
| `security_engineer.fix_1.json` | security_engineer | MERGED-P1-001 | yes | no | 74 → 92 |

Advisory findings (P2/P3) applied deterministically — no lens-validation slot
per team-mode policy (only blocking P0/P1 go through the patch-validation loop).

---

## Manual-Review Queue

None. All nine findings resolved at ADR altitude. Concrete key ARNs, exact
cipher suites, rotation periods, idempotency-key wire format, and the
load-test-calibrated conflict-rate ceiling are intentionally deferred to SPEC
(the security lens confirmed their absence is not a blocking P0/P1 at the ADR level).

---

## Validation After Fix

| Metric | Before | After (expected) |
|--------|--------|------------------|
| Structural lint (sdd-doc-lint) | STY03 + STY02 errors after edits | clean (exit 0) |
| security_engineer lens_score | 74 | 92 (patch-validated) |
| Blocking findings (P0/P1) | 1 | 0 |
| Combined gate status | FAIL | re-audit required to confirm PASS |

Re-audit is the binding gate — this report records the remediation, not a new
score. The synthesizer's combined score is recomputed by `doc-adr-audit` on the
next pass.

---

## Cleanup Summary

No prior fix reports to supersede (this is v001). Backup retained at
`tmp/backup/ADR-01_20260609T021223Z/ADR-01.md`.

---

## Next Steps

1. Re-run `doc-adr-audit` (saga iteration 1 re-review) to recompute the
   combined gate. Expect PASS: 0 blocking findings remain, structural floor is
   green, and the security lens (heaviest contributor to the prior 86 cap)
   rose 74 → 92.
2. On PASS, the autopilot loop promotes ADR-01 toward SPEC authoring.
