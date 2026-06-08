# EARS-01 Fix Report — v002

**Artifact:** `docs/03_EARS/EARS-01.md`
**Layer:** 03_EARS · **Mode:** team (per `.aidoc/profile.yaml` → framework default) — applied as deterministic advisory remediation (no blocking findings)
**Date:** 2026-06-08 · **Fix iteration:** 2
**Input audit:** `.aidoc/review/03_EARS/EARS-01/report.md` + `verdict.json` (combined **FAIL**, content **84**/100, **0** blocking findings; 6 P2 + 8 P3)
**Backup:** `tmp/backup/EARS-01_20260608T120330Z/EARS-01.md`

---

## Summary

| Metric | Value |
|--------|-------|
| Findings in (structured) | 14 — 0 P0 · 0 P1 · 6 P2 · 8 P3 |
| Fixed (fully or partially) | 6 (P2-001, P2-004 partial, P2-006, P3-002, P3-003, P3-005) |
| Deferred to manual queue | 8 (P2-002, P2-003, P2-005, P3-001, P3-004, P3-006, P3-007, P3-008) |
| Files modified | `docs/03_EARS/EARS-01.md` |
| Files created | this report |
| Structural lint | **PASS** — STY03 body blocker held clear (body **2242** w ≤ 2250); residual STY02 §3 **warning** only (1369 w, non-blocking) |
| New element IDs | `5391a`, `5391b` (split of `5391`) |

**No P0/P1 blocking findings** — per the skill's team-mode contract, P2/P3 are
advisory and applied **deterministically without lens validation**; no
`fix_N.json` slots and no synthesizer dispatch this iteration. The gate failed
on **score only** (84 < 90).

**Governing constraint this iteration: the STY03 word ceiling.** EARS bodies
target ≤1500 words and **block above 2250** (`AUTHORING_STYLE.md` size targets;
`sdd_doc_lint` STY03). The pre-fix body was already **2221** w — 29 w of
headroom. The audit's content findings overwhelmingly require **adding**
requirement statements (recovery rules, detection rules, an abuse-case line
pair, a firebreak invariant, an audit-log rule) or a **per-line traceability
table** (~70–110 w). These cannot coexist with the 2250-word blocker in a
single file. The fixer therefore applied the high-leverage fixes that fit
(weighted toward the low/heavy lenses — `requirements_specialist` w35,
`qa_lead` w20), **compressed redundant prose** (Phase 7) to keep the structural
gate green, and **queued the additive findings** with the structural remedy
flagged below.

---

## Fixes Applied

| Code | Sev | Check | Issue | Fix | Element(s) | Confidence |
|------|-----|-------|-------|-----|-----------|------------|
| MERGED-P2-001 | P2 | C5 | TLS `c060` traced to the SSRF constraint `PRD.01.12.6f96` (false trace; no PRD element authorises TLS) | Removed the false `@prd`; marked `[author assumption — no PRD transport-encryption element]`; reflected the deferral in the §4 preamble (c060 grouped with the issuance/visit-count author-assumptions) | c060 (§4); §4 preamble | auto-assisted |
| MERGED-P2-006 | P2 | C2 | Takedown `5391` conjoined two positive obligations (cease redirect AND not-found message) under one timing budget | Split into **`5391a`** (cease redirecting WITHIN 1 s p95, retains the 187c override) and **`5391b`** (return "No such short link exists." when a taken-down code is requested); updated the `187c` cross-reference to `5391a` | +5391a, +5391b; 187c | auto-assisted |
| MERGED-P2-004 | P2 | C5 | `19ec` absolute no-loss contradicted `d808`/`PRD.01.12.11be` best-effort drop; no detection path | **Partial** — reconciled `19ec` to "every **durably-accepted** visit increment"; a best-effort drop under `d808` "is not durably accepted and is logged as a count-write failure for reconciliation" (folds the detection signal into the invariant) | 19ec | auto-assisted |
| MERGED-P3-002 | P3 | C5 | `a132` load envelope (100 req/s, 20 concurrent) traces to a PRD feature row carrying no load figures | Added `[author assumption — load-envelope pending a PRD §12 element]` to the tag line (numerics kept out of the tag line to avoid a TH02 threshold clash) | a132 | auto-assisted |
| MERGED-P3-003 | P3 | C4 | Screening "budget" deferred implicitly; no `[ADR deferred]` marker; 500 ms submit p95 not decomposed | Added `[ADR deferred: BRD.01.08.daeb — reputation-screen timeout within the 500 ms submit p95]` to both `db78` and `a2ae`, matching the existing ee86/135e/0b67 convention | db78, a2ae | auto-assisted |
| MERGED-P3-005 | P3 | C5 | Idempotency undeclared for `f909`, `8f70`, `8df7`, `5391` | Appended parenthetical idempotency declarations: f909 (identical-URL resubmission → new distinct code, no dedup), 8f70 (at-most-once per visit event), 8df7 (durable mapping is the commit key; retried ack → no second code), 5391a (re-mark is a no-op) | f909, 8f70, 8df7, 5391a | auto-assisted |

### Compression (Phase 7 — to keep the body under the STY03 2250-word blocker)

Only **non-requirement prose** was compressed; no requirement content removed
(Content-Preservation Rules honoured).

| Action | Rationale | Approx. words |
|--------|-----------|---------------|
| Removed the §4 **Timing profile** table | Redundant restatement — its p95 budgets are already in every §3 `WITHIN` clause and the §4 Performance table; its only unique values (p50/p99) are untraced by any element | −55 |
| Tightened §3 intro, §2 Scope, §4 preamble, §5 Downstream/Coverage, the `deliverable_type` note | Banned-filler / redundant-restatement removal per `AUTHORING_STYLE.md` (PRD feature IDs in §2 Scope already live in §5; threshold convention stated once in §3 intro) | −70 (net) |

Net effect: the six content fixes added ≈ +123 w; compression returned the body
to **2242** w (from a transient peak of 2375 w), clearing STY03 with an 8-word
margin.

---

## Manual-Review Queue

All eight deferred findings are **advisory P2/P3** that require either (a)
adding new requirement statements, or (b) a per-line traceability table — both
of which breach the **STY03 2250-word body blocker** in a single-file EARS, or
(c) an upstream PRD change. None is a blocking finding.

| Code | Sev | Check | Why deferred | Unblock path |
|------|-----|-------|--------------|--------------|
| MERGED-P2-002 | P2 | C1 | Per-line BDD slots for ~27 §3 lines need a `[BDD-pending]` roster / per-line matrix (~70–110 w). Will not fit under the 2250-word blocker. | **Structural decision** (below) — then add the roster |
| MERGED-P3-004 | P3 | C2 | Constraint-/risk-derived matrix rows are the same per-line coverage data as P2-002 | Same as P2-002 |
| MERGED-P2-003 | P2 | C5 | Reputation fail-closed **recovery** rule is a new event-driven EARS line — no word budget | Structural decision, then add a `WHEN source reachable again → resume` line |
| MERGED-P2-005 | P2 | C1 | Mass-minting/enumeration **abuse pair** needs an event-driven throttle line + an IF-enumeration line — two new lines, no budget | Structural decision, then add the pair `[ADR deferred: BRD.01.08.daeb]` |
| MERGED-P3-006 | P3 | C5 | Pool-exhaustion **clearance/recovery** line is additive — no budget | Structural decision, then add the clearance line |
| MERGED-P3-007 | P3 | C4 | Reputation-outage **firebreak** invariant is a new ubiquitous line. ID pre-derived: **`EARS.01.03.b3fb`** ("Reputation-outage redirect firebreak") — ready to drop in once budget exists | Structural decision, then add `b3fb` |
| MERGED-P3-008 | P3 | C4 | Metrics authZ **audit-log** rule/marker is additive; lowest crew weight (security w8) | Structural decision, then add the audit-log line or `[ADR deferred]` marker |
| MERGED-P3-001 | P3 | C2 | Error-path atomicity convention across eeaf/fa44/9671/a2ae — house-style; the iteration-1 lens validator confirmed the message-implies-no-code idiom as house-style, not a defect | Author decision: ratify the idiom or split all four uniformly |

### Recommended structural decision (author / governance — outside the in-file fixer surface)

EARS-01 formalises **28 requirement lines** for five features plus their
error/security/reliability surface; at ≈1369 w in §3 alone it sits permanently
against the EARS whole-body ceiling. To absorb the queued additive content,
choose one:

1. **Split §3 into per-EARS-type section files** (Phase 0 nested folder
   `docs/03_EARS/EARS-01_url-shortener/`). Resets the per-file body count so the
   recovery/detection/abuse/firebreak/audit-log lines and the per-line BDD
   roster all fit. *Trade-off:* makes EARS-01 inconsistent with the example's
   flat single-file-per-layer convention (`BRD-01.md`, `PRD-01.md`).
2. **Grant this multi-feature EARS an explicit `_size_target` relaxation**
   (`AUTHORING_STYLE.md` allows templates to relax via `_guidance`/
   `_size_target`). Keeps the single file; raises the STY03 ceiling for this
   artifact with a recorded justification.

Either decision then lets a follow-up fixer pass close P2-002/P2-003/P2-005 and
the four C4/C5 advisories deterministically.

---

## Validation After Fix

| Dimension | Before (iter-2 audit) | After (this fix) |
|-----------|-----------------------|------------------|
| Combined status | FAIL | re-audit pending (iteration 3) |
| Content score | 84 | recomputed by re-audit |
| Structural floor | PASS | **PASS** (STY03 held clear at 2242 w; STY02 §3 warning only; transient STY03/TH02 introduced mid-edit were both cleared) |
| Unresolved P0 / P1 | 0 / 0 | 0 / 0 |
| P2 closed | — | 3 of 6 (P2-001, P2-004 partial, P2-006) |
| P3 closed | — | 2 of 8 (P3-002, P3-003, P3-005) |

> The frontmatter `bdd_ready_score: 94` and the Document Control "94/100" row
> are pre-fix values; the re-audit refreshes them.

**Lens-impact (informational estimate — actual scores set by re-audit):**
`requirements_specialist` (P2-001, P2-006, P3-002 closed) and `qa_lead`
(P3-005 closed; P2-002/P3-004 queued) are the weighted swing lenses; `qa_lead`
recovery is capped by the queued per-line BDD finding (P2-002), which the word
ceiling prevents closing in-file.

## Validation Slots index

None this iteration — no P0/P1 blocking findings, so no lens-validation
dispatch occurred (team-mode validates blocking patches only; P2/P3 are applied
deterministically).

## Cleanup Summary

- Backup retained at `tmp/backup/EARS-01_20260608T120330Z/`.
- `EARS-01.F_fix_report_v001.md` **retained** — it records the iteration-1 P1
  remediation history and is not superseded by this iteration-2 report.

## Next Steps

1. Re-run `/aidoc-flow:doc-ears-audit` (iteration 3) to recompute the content
   score against the closed findings.
2. If the score remains < 90, the gap is driven by the eight queued findings —
   resolve the **recommended structural decision** above (split §3 or grant a
   `_size_target` relaxation), then run a follow-up fixer pass to close
   P2-002 / P2-003 / P2-005 / P3-001 / P3-004 / P3-006 / P3-007 (`b3fb` ready) /
   P3-008.
