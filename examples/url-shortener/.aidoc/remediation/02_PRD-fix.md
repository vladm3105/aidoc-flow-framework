# PRD-01 — Remediation Report (team mode)

| Field | Value |
|-------|-------|
| Artifact | PRD-01 — URL Shortener |
| Path | `examples/url-shortener/docs/02_PRD/PRD-01.md` |
| Audit input | `.aidoc/audit/02_PRD-audit.md` + `verdict.json` (content_score 85 / FAIL) |
| Saga | `9b956652b2706b30`, iteration 1, phase `fixer` |
| Review mode | `team` (framework default; profile sets no override) |
| Fixer timestamp | 2026-06-10T17:37:38Z |
| Blocking findings (P0/P1) | 0 — no lens-validation/compensation loop required |
| Findings applied | 20 / 20 (12 × P2, 8 × P3) |
| Findings reverted | 0 |
| Manual-review queue | 0 |

## Verdict rationale

The audit failed on **score** (85 < 90), not on a structural or blocking
defect. Every finding is advisory (P2/P3). Per `doc-prd-fixer` §Remediate,
P2/P3 findings are applied deterministically without per-lens patch
validation; with `blocking_findings_count = 0` the saga performs no
`BRANCH_COMPENSATING` transitions and advances run-level to
`BRANCH_COMPLETED`. The theme of the fix set, per the auditor's note, was to
give EARS a **bounded, gated, anchored** form for commitments the PRD already
made as prose — numeric/measurement bounds, §11 launch gates, and explicit ADR
deferrals tied to named §14 topics.

## Fixes Applied

| Code | Pri | Section(s) | Fix | Confidence |
|------|-----|-----------|-----|------------|
| VALID-M001 | P3 | frontmatter | Added `deliverable_type: code` to `custom_fields` (inherited from BRD-01). | auto-safe |
| PO-001 | P2 | §9 PRD.01.09.9e0f | Added an Acceptance clause mirroring the other four FRs and the §10 invalid-destination message. | auto-assisted |
| TL-003 | P3 | §9 PRD.01.09.9e0f; §11 | Enumerated rejected input classes (empty/blank, >2,048 chars, `javascript:`/`data:`/`file:`, malformed/relative); added a §11 Functional input-validation gate. | auto-assisted |
| TL-002 | P2 | §5 PRD.01.05.546d; §9 threshold; §11 Quality | Added a single measurement-scope note (redirect path, server-side, production-equivalent, rolling window excl. cold-start, under the BRD §9 load envelope) and bound all three p95 references to it. | auto-assisted |
| TL-001 | P2 | §11 Security gate | Replaced non-measurable "Pass"/"verified" with concrete methods (screening integration test + takedown runbook drill). | auto-assisted |
| CE-006 | P2 | §11 Security AC | Added a failure-branch gate: dependency-outage drill proving create fails-closed (not fail-open, not stall) when the reputation source is unreachable/slow. | auto-assisted |
| CE-001 | P2 | §10; §11; §14 | Added a distinct §10 code-space-exhaustion error row, a §11 Reliability capacity-guard gate (90% alert + capacity-reject), and a §14 topic-scope anchor. | auto-assisted |
| CE-007 | P3 | §10 | Marked the capacity-exhausted response non-retryable, differentiated from the transient "retry later" outage. | auto-assisted |
| CE-002 | P2 | §13 PRD.01.13.e661; §14 | Anchored the metric-poisoning deferral to the visit-observability ADR topic (BRD.01.08.c478). | auto-assisted |
| CE-003 | P2 | §11 Compliance; §13 PRD.01.13.d50d | Added a §11 Compliance gate recording the data-protection deferral against a named ADR topic. | auto-assisted |
| CE-004 | P2 | §13 PRD.01.13.011a | Added an explicit screening-deadline deferral (ms bound owned by the abuse-protection ADR topic). | auto-assisted |
| CE-005 | P2 | §12 durability stance | Replaced "brief" reconciliation lag with an explicit max-staleness-window ADR deferral (BRD.01.08.c478). | auto-assisted |
| CE-008 | P3 | §9 sequence; §11 | Moved the visit-count increment off the synchronous redirect path (`--)` async dispatch after the redirect) and added a §11 "redirect never blocked on counting" gate. | auto-assisted |
| SE-001 | P2 | §12 | Added per-artifact classification rows: visit-count aggregate = operational/non-sensitive; short-code→URL mapping inherits the URL's PII sensitivity. | auto-assisted |
| SE-002 | P2 | §13 PRD.01.13.011a | Added a takedown-SLA deferral owned by the abuse-protection ADR topic. | auto-assisted |
| SE-003 | P3 | §7 trust-boundary | Specified ≥2 enumeration-defense layers (high-entropy non-sequential codes + per-source rate-limiting) with parameters deferred to ADR. | auto-assisted |
| SE-004 | P3 | §7 trust-boundary | Added an explicit TOCTOU re-screen-vs-screen-once deferral owned by the abuse-protection ADR topic. | auto-assisted |
| ARCH-001 | P2 | §9 sequence-sync | Added a `Visit Counter` participant performing the increment (C→Store), reconciling the increment-flow owner with C4-L2/DFD-L2. | auto-assisted |
| ARCH-002 | P3 | §9 all three diagrams | Added a one-line decomposition note under each (MVP simplifications + post-MVP evolution). | auto-assisted |
| ARCH-003 | P3 | §7 dependencies | Named the reputation-source integration at container altitude (direction, data exchanged, synchronous request/response protocol family). | auto-assisted |

## Validation Slots index

No per-lens validation slots were written: `blocking_findings_count = 0`, so no
finding entered the team-mode patch-validation loop. All fixes are advisory
(P2/P3) and applied deterministically per `doc-prd-fixer` §Remediate.

## Validation After Fix

| Metric | Before | After |
|--------|-------:|------:|
| Content score | 85 | (re-audit pending) |
| Blocking findings | 0 | 0 |
| P2 findings | 12 | 0 applied (re-audit pending) |
| P3 findings | 8 | 0 applied (re-audit pending) |
| Structural floor | PASS | PASS (subject to re-audit) |

## Framework-gap note (NOT an artifact defect — do NOT hand-edit)

The post-edit `sdd_doc_lint` hook reports **32 × `TRACE-RES-001`**
("trace tag '@brd: …' unresolvable (host document missing; expected host
'BRD-01')") against every `@brd:` tag in the PRD. These are **false
positives**: the host document `docs/01_BRD/BRD-01.md` exists and contains
every referenced element (e.g. `BRD.01.07.6c3f` at BRD-01 §7,
`BRD.01.08.daeb` at BRD-01 §8). The original audit's structural floor
explicitly recorded "Cumulative `@brd:` tags resolve | PASS". The
`TRACE-RES-001` rule is under active development on this branch
(`feat/trace-res-fixup-001`; cf. commit `1188e06b` "TRACE-RES-001
downstream-tag skip"). Per project policy ("Never hand-edit example
artifacts"; "a framework skill can't handle a class of remediation … is a
framework workflow gap — fix the skill or the workflow, never the artifact"),
the correct, PII-traceable `@brd:` tags were **left unchanged**. The fix is
owed to the lint rule's host-resolution logic, not to PRD-01.

## Cleanup Summary

- No superseded `PRD-01.F_fix_report_v*.md` existed — first fix pass; nothing
  deleted.
- Backup written to `tmp/backup/PRD-01_20260610-133145/PRD-01.md`.

## Next Steps

Re-run `doc-prd-audit` (saga re-enters at `BRANCH_COMPLETED`) to confirm the
content score clears 90. The TRACE-RES-001 lint false positives are tracked
separately as a framework lint-rule gap and must not gate this artifact.
