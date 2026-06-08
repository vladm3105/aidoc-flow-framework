# EARS-01 Fix Report — v001

**Artifact:** `docs/03_EARS/EARS-01.md`
**Layer:** 03_EARS · **Mode:** team (per `.aidoc/profile.yaml` → framework default)
**Date:** 2026-06-08 · **Fix iteration:** 1
**Input audit:** `.aidoc/review/03_EARS/EARS-01/report.md` + `verdict.json` (combined FAIL, content 82/100, 1 blocking P1)

---

## Summary

| Metric | Value |
|--------|-------|
| Findings in (structured) | 17 — 1 P1 · 8 P2 · 8 P3 |
| Fixed / partially fixed | 13 |
| Deferred to manual queue | 4 |
| Files modified | `docs/03_EARS/EARS-01.md` |
| Files created | this report; 3 × `<persona>.fix_1.json` validation slots |
| Backup | `tmp/backup/EARS-01_20260608T073116Z/EARS-01.md` |
| New element IDs | db78, 00b9, 5391, a0ae, 3312 (§3.1); 9671, e606, 135e (§3.4); ee3f (§4) |
| Structural lint | PASS — STY03 blocker cleared (body 2221 w); residual STY02 §3 **warning** only |

The blocking **P1 (MERGED-P1-001)** was remediated and **validated by all three responsible lenses** (security_engineer, chaos_engineer, qa_lead) with **no new P0/P1** — patch accepted. The eight P2 test-blocking findings were resolved except the TLS-orphan (needs an upstream PRD change) and the a2ae/eeaf rejection-idiom split (house-style, queued). P3 advisories were applied except two idempotency declarations deferred under the EARS word ceiling.

---

## Fixes Applied

| Code | Severity | Issue | Fix | Element(s) | Confidence |
|------|----------|-------|-----|-----------|------------|
| MERGED-P1-001 | P1 | Harmful-destination screening absent (no screen-and-reject, no takedown) | Added screen-before-issue line, IF-harmful-reject line, takedown override line, and §4 control row; hardened a2ae (slow-source → fail-closed), 187c (takedown cross-ref), 5391 (actor + WITHIN bound) | +db78, +9671, +5391, +ee3f; a2ae, 187c | manual-required (3-lens PASS) |
| requirements_specialist-002 | P2 | Code-issuance p95<500 ms unsourced | §4 provenance note marks issuance/visit-count timings `[ADR assumed]` pending PRD ratification | §4 preamble | auto-assisted |
| requirements_specialist-003 | P2 | Non-atomic compounds | Split negative obligations: 5821 → +e606 (no-redirect); 0b67 → +135e (retry bound) | 5821, +e606, 0b67, +135e | auto-assisted |
| tech_lead-001 | P2 | URL-length bound had no value | Stated "2,048 characters" inline | eeaf | auto-assisted |
| qa_lead-001 | P2 | "otherwise unresolvable" catch-all | Removed hedge; trigger now "never issued or is mistyped" | 5821 | auto-safe |
| qa_lead-002 | P2 | Trigger "is slow" unbounded | Replaced with "exceeds 1 s at the 95th percentile (the EARS.01.03.8f70 budget)" | d808 | auto-safe |
| security_engineer-002 | P2 | Rate-limit rules unbounded | Added `[ADR deferred: BRD.01.08.daeb — numeric rate bound]` | ee86, b1aa | auto-assisted |
| security_engineer-003 | P2 | Metrics path no access control | Added access-control WHEN line + denied-caller IF line | +a0ae, +3312 | auto-assisted |
| tech_lead-002 | P3 | 0b67 ADR-dependency unmarked | Added `[ADR deferred: BRD.01.08.9665 — code-space sizing]` | 0b67 | auto-assisted |
| tech_lead-003 | P3 | "SHALL NOT retry unboundedly" untestable | Replaced with bounded "at most the configured retry ceiling" `[ADR deferred]` | +135e | auto-assisted |
| chaos_engineer-002 | P3 | Pool exhaustion: no detection | Added utilization-alert line `[ADR deferred]` | +00b9 | auto-assisted |
| qa_lead-005 | P3 | Coverage matrix upstream-only | Added "Downstream BDD (expected)" column | §5 table | auto-safe |
| qa_lead-004 | P3 | No per-line BDD slot | §5 now states per-line scenario IDs are assigned at BDD authoring (layer-level deferral made explicit; per-line `@bdd` IDs withheld per template "don't reference BDD numbers before they exist") | §5 | auto-assisted (partial) |

### Hardening edits (from lens-validator advisories on the P1 patch)

- **chaos_engineer:** a2ae trigger widened to "unreachable **or does not respond within the screening budget**" — binds the slow-but-reachable screen to the fail-closed sink.
- **qa_lead:** 5391 takedown given a defined actor ("**WHEN a Service Owner** marks…") and a `WITHIN 1 s at the 95th percentile` propagation bound.
- **security_engineer:** 187c carries a reciprocal cross-reference ("**except links taken down per EARS.01.03.5391**").

---

## Manual-Review Queue

| Code | Sev | Why deferred |
|------|-----|--------------|
| requirements_specialist-001 | P2 | **TLS orphan** `EARS.01.04.c060` has no upstream source; `@prd` mis-points to SSRF `PRD.01.12.6f96`. Resolution requires an upstream PRD §12 TLS constraint (then re-point) or removal if out of MVP — both outside the EARS fixer surface; content-preservation forbids silent deletion. |
| requirements_specialist-003 (residual) | P2 | a2ae / eeaf conjoin reject + no-code + message. Retained as the document's established rejection idiom (qa_lead validator confirmed this is house-style, not a new defect). Split into atomic lines if strict atomicity is later required. |
| requirements_specialist-004 | P3 | a132 load envelope traces through BRD only; needs a PRD §12 non-functional load element (or re-point `@brd` to a BRD §9 quality row) — upstream change. |
| qa_lead-006 / qa_lead-007 | P3 | Idempotency declarations for issuance (f909) and visit-count (8f70) deferred under the EARS STY03 word ceiling (body 2221/2250). Add when §3 is split into per-section files. |
| STY02 (structural) | warn | §3 Requirements is 1251 words (target ≤800; warning >1200). Inherent to +10 requirement lines in a single-file EARS. Recommend splitting §3 into per-EARS-type section files (Phase 0 nested-folder). Warning-only — does not fail the structural gate. |

---

## Validation After Fix

| Dimension | Before | After |
|-----------|--------|-------|
| Combined status | FAIL | re-audit pending (iteration 2) |
| Content score | 82 | recomputed by re-audit |
| Structural floor | PASS | **PASS** (STY03 ERROR cleared; STY02 §3 warning only) |
| Unresolved P1 | 1 (MERGED-P1-001) | **0** — resolved, 3-lens PASS |
| Blocking lint errors | 0 | 0 (transient ID02/TH01/STY03 introduced during editing were all cleared) |

> The frontmatter `bdd_ready_score: 94` and the Document Control "94/100" row are pre-fix values; the re-audit refreshes them.

## Validation Slots index

| Lens | Agent | Slot | lens_score | verdict |
|------|-------|------|-----------|---------|
| security_engineer | security-engineer | `.aidoc/review/03_EARS/EARS-01/security_engineer.fix_1.json` | 93 | PASS |
| chaos_engineer | chaos-engineer | `.aidoc/review/03_EARS/EARS-01/chaos_engineer.fix_1.json` | 86 | PASS |
| qa_lead | test-architect | `.aidoc/review/03_EARS/EARS-01/qa_lead.fix_1.json` | 85 | PASS |

All three returned `resolves_finding: true`, `new_blocking_findings: []`. No regression → patch retained.

## Cleanup Summary

No superseded fix reports (this is v001). Backup retained at `tmp/backup/EARS-01_20260608T073116Z/`.

## Next Steps

Re-run `/aidoc-flow:doc-ears-audit` (iteration 2) to recompute the content score and confirm the gate. If score ≥ 90 and structural PASS, promote to BDD (Layer 4). The four queued items above are author/upstream decisions, not blockers to re-audit.
