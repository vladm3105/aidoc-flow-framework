# BDD-01 Review Report — Unified Synthesizer Output

**Artifact:** BDD-01
**Layer:** 04_BDD
**Date:** 2026-06-08
**Synthesizer role:** Chairperson (runs last; aggregates 6 lens slots)

---

## Gate Decision

**PASS**

All gate conditions satisfied:

| Condition | Result |
|-----------|--------|
| Structural floor | PASS |
| Blocking findings (P0/P1) | 0 |
| Content score >= 90 | 95 >= 90 — PASS |
| Coverage quorum | 6/6 lenses ran — PASS |

---

## Executive Summary

BDD-01 is a mature, well-structured suite of 35 scenarios across 5 scenario categories, with complete cumulative upstream traceability (@brd/@prd/@ears at feature level), conformant scenario IDs (BDD.01.03.xxxx 4-hex), and all required metadata. The structural floor passes cleanly on every declared check.

The content review by 6 lenses produces a weighted content score of **95** (gate threshold: 90). No lens surfaced a P0 or P1 finding; the suite is not blocked. The finding set consists of one P2 warning (a missing recovery scenario for the abuse-throttle path, which lacks the paired restoration assertion every other failure-injection class carries) and seven P3 informational items (template-conformance advisory, audit-sink failure edge, redirect malformed-input gap, upstream-owned SSRF encoding bypass, and three operator observability gaps each requiring an upstream EARS amendment before a BDD fix is possible).

Two auditor findings were floor-falsified as false positives (see §Floor-falsified findings below) and are excluded from the verdict. With those findings removed, the auditor lens recomputes to a clean score of 100.

The `beyond_checklist` ratio for this layer is 3/8 = 37.5%, above the 30% drift threshold. This is a playbook calibration signal: the BDD playbook's C1–C5 checks do not fully cover the recovery-pairing, audit-sink failure, and SSRF encoding concerns that emerged from the chaos_engineer and security_engineer lenses. The playbook maintainer should review whether new check rows are warranted.

---

## Readiness Score

**Content score: 95 / 100**

### Per-lens scores

| Lens | Score | Weight | Weighted contribution |
|------|-------|--------|-----------------------|
| qa_lead | 95 | 35 | 33.25 |
| tech_lead | 100 | 25 | 25.00 |
| chaos_engineer | 86 | 14 | 12.04 |
| security_engineer | 92 | 6 | 5.52 |
| operator | 95 | 10 | 9.50 |
| auditor | 100 | 10 | 10.00 |
| **Total** | | **100** | **95.31 → 95** |

Auditor score recomputed to 100 per floor adjudication (both auditor findings discarded as false positives; see §Floor-falsified findings).

---

## Coverage

- Expected lenses: 6
- Lenses that ran: 6
- Quorum met: yes (6/6 >= ceil(6 * 0.5) = 3)
- Confidence: full — no low-confidence flag

---

## Structural Status

**PASS**

The audit skill's deterministic structural checks confirmed:

- All 5 required sections present.
- 35 scenario IDs all conform to BDD.01.03.xxxx 4-hex.
- Cumulative @brd/@prd/@ears present at feature level applying to every scenario.
- Every scenario carries @scenario-type, @priority, @scenario-id, spec_trace.
- Five scenario categories represented: 11 success / 6 error / 12 recovery / 3 parameterized / 3 optional.
- Metadata fields document_type=bdd-document, artifact_type=BDD, layer=4, deliverable_type=code all valid.

---

## Findings by Severity

### P2 — Warning (1 finding)

#### chaos_engineer-P2-001

**Location:** §3.4 BDD.01.03.6934 (abuse/enumeration throttle) — no paired recovery scenario
**Check:** C3
**Lenses:** chaos_engineer

The anti-abuse/anti-enumeration failure path (6934, exercising EARS.01.03.b5fa mass-minting cooldown and EARS.01.03.d8a2 scraping block) injects the throttle/cooldown/block but has NO paired recovery scenario asserting return to normal mode. Both EARS lines describe a TRANSIENT cooldown — 'during it' bounds the window, so the source must resume normal service after the cooldown expires. Every other failure injection in §3.3 (reputation 4df6->c826, link-store-redirect f44a->0759, link-store-write ed21->bcfb, visit-count 5f58->a7ad, pool 6f00->b3fe, conn-pool-saturation 1a55->dd27) is paired with a discrete restoration assertion; the abuse-throttle path is the only failure-injection class with no recovery pair. A cooldown that is never tested as lifting silently degrades a legitimate source with no executable guarantee that throttling clears.

**Recommendation:** Add a recovery scenario: Given a source was throttled/blocked under the EARS.01.03.ab5e/c7e3 cooldown per BDD.01.03.6934 and the cooldown window has elapsed, When the source issues a within-rate submit/lookup, Then the Shortening API / Redirect Handler SHALL serve it normally (no throttle, no cooldown denial) and SHALL emit a cooldown-cleared event carrying the source identity and timestamp. Assert fully-operational restoration, mirroring the c826/0759/dd27 recovery pattern.

---

### P3 — Informational (7 findings)

#### qa_lead-P3-001 [template-conformance: INFO]

**Location:** Section 2 — Feature Definition, Background
**Check:** beyond-checklist:background-step-traceability
**Lenses:** qa_lead

INFO / template-conformance: **do NOT remove — required by BDD-TEMPLATE Background convention.** The Background step `And the current time is "09:30:00" in "America/New_York"` is prescribed by BDD-TEMPLATE.yaml's Background convention as a deterministic-clock fixture. It does not trace to an EARS requirement directly, but that is expected for template-mandated infrastructure steps. This finding does not lower the qa_lead score (score retained at 95).

**Recommendation:** No action required. The step is a required BDD-TEMPLATE Background fixture. Retain as-is. If time-of-day EARS requirements are added in future, consider whether a scenario-scoped Given is also needed alongside the Background step.

---

#### chaos_engineer-P3-002

**Location:** §3.1 BDD.01.03.40d7 / §3.2 BDD.01.03.842c (metrics audit-log write) — no audit-sink failure path
**Check:** beyond-checklist:audit-sink-failure
**Lenses:** chaos_engineer

EARS.01.03.a17e mandates the Metrics Reporter write an audit record WITHIN 100 ms on every grant/deny. Scenarios 40d7 (granted) and 842c (denied) assert the audit WRITE on the happy path, but no scenario injects an audit-SINK failure (sink unreachable/slow beyond the 100 ms audit budget). Without a defined behaviour, an unstated assumption governs whether an authZ decision proceeds when its mandatory audit write fails (fail-open: serve without record, vs fail-closed: deny).

**Recommendation:** Either add an audit-sink-degraded scenario (sink slow/unreachable beyond the 100 ms budget) asserting the contracted behaviour (e.g., decision still recorded via durable buffer, or decision-and-audit are atomic), or confirm during ADR/SPEC that audit-sink failure is explicitly out of scope for this layer and note it so the gap is a decision rather than an omission.

---

#### security_engineer-P3-001

**Location:** §3.2 BDD.01.03.4356 / §3.4 redirect path
**Check:** C3
**Lenses:** security_engineer

The redirect endpoint accepts external input via the short-code path segment but has no input-fuzzing scenario for that segment. BDD.01.03.4356 covers a clean unknown code ('/zzz999') and 6934 covers enumeration-pattern abuse, but neither exercises a malformed/oversized/invalid-encoding short-code path (e.g. a 4096-char path segment, percent-encoded control chars, or a NUL in the code position) asserting graceful rejection with no server-side error disclosure. The submit path has this coverage (BDD.01.03.e8b9); the redirect-accepting endpoint does not have a parallel malformed-input case.

**Recommendation:** Add an error/parameterized scenario on the Redirect Handler with malformed short-code path inputs (oversized segment, percent-encoded control char, NUL byte, path-traversal token) asserting it returns the standard 'No such short link exists.' contract WITHIN the redirect budget AND does not disclose any server-side error, stack trace, or dependency diagnostic — mirroring the no-disclosure clause used in BDD.01.03.842c / e8b9.

---

#### security_engineer-P3-002

**Location:** §3.4 BDD.01.03.5599 (SSRF denylist)
**Check:** beyond-checklist:ssrf-encoding-bypass
**Lenses:** security_engineer

The SSRF denylist scenario (5599) covers only the canonical host forms EARS.01.03.fa44 / EARS.01.04.1453 enumerate (loopback 127.0.0.1, RFC1918 10.0.0.5, link-local 169.254.169.254, cloud-metadata hostname). Common SSRF bypass classes are not exercised: decimal/octal/hex-encoded IPs (e.g. 2130706433 for 127.0.0.1), IPv6 forms ([::1], [::ffff:169.254.169.254]), 0.0.0.0, and DNS-rebinding hostnames resolving to private space. This gap is UPSTREAM-OWNED: the EARS denylist names only canonical forms, so an EARS amendment is required before the BDD can bind these rows as named requirements.

**Recommendation:** Raise an EARS amendment extending EARS.01.03.fa44 / EARS.01.04.1453 to require denylist enforcement against encoded-IP, IPv6, 0.0.0.0, and resolved-address (DNS-rebinding) forms; then add the corresponding Examples rows to BDD.01.03.5599. No BDD-only fix is possible until the requirement is named upstream.

---

#### operator-P3-001

**Location:** §3.3 / BDD.01.03.ed21
**Check:** C1
**Lenses:** operator

Scenario ed21 (issuance fail-closed when Link Store write path is degraded) asserts no-ack, no durable mapping, and no orphan code, but carries no observability assert (no log severity, no metric). EARS.01.03.8df7 mandates write-before-ack ordering but does not declare a log or metric signal on write-path failure. By contrast, the parallel redirect-path store failure (EARS.01.03.fab2, covered by BDD.01.03.f44a) does have an EARS-declared ERROR log mandate — creating an asymmetry. Adding an observability Then-step to ed21 without a matching EARS parent would create an orphan untraced scenario element.

**Recommendation:** Requires upstream EARS amendment: add an unwanted-behavior EARS line — IF the Link Store write path fails or times out on the issuance path, THE Shortening API SHALL emit a log entry at ERROR severity carrying the fault type and a timestamp. Once that line exists, add a corresponding observability Then-step to BDD.01.03.ed21 and its recovery pair BDD.01.03.bcfb.

---

#### operator-P3-002

**Location:** §3.2 / BDD.01.03.bcf8
**Check:** C1
**Lenses:** operator

Scenario bcf8 (harmful destination rejected) asserts the user-facing rejection message and that no short code is issued, but carries no observability assert. A harmful-destination rejection is an operationally significant abuse-screening event; operators need audit-trail or metric coverage to monitor screening effectiveness and detect false-positive spikes. EARS.01.03.9671 does not declare a log or metric emission for harmful rejections.

**Recommendation:** Requires upstream EARS amendment: extend EARS.01.03.9671 (or add a companion line) declaring that the Shortening API SHALL emit a harmful-destination-rejected log entry at WARN severity carrying the destination hash, reputation verdict, and timestamp. Once that line exists, add the corresponding Then-step to BDD.01.03.bcf8.

---

#### operator-P3-003

**Location:** §4 quality attributes / EARS.01.04.e27b, EARS.01.04.ca05
**Check:** C5
**Lenses:** operator

No scenario exercises a redirect p95 latency-SLO breach or a monthly availability-SLO breach and asserts an alert fires to an operator channel. EARS.01.04.e27b declares a p95<50ms latency target and EARS.01.04.ca05 declares 99.9% monthly availability, but neither EARS line includes an alert-emission clause. Adding BDD breach-alert scenarios without an upstream EARS parent would produce orphaned scenarios.

**Recommendation:** Requires upstream EARS amendment: add EARS lines declaring that when redirect latency p95 exceeds the threshold window the service SHALL emit a latency-SLO-breach alert, and that when availability drops below 99.9% projected monthly the service SHALL emit an availability-SLO alert with payload and channel. Once those lines exist, add corresponding BDD breach scenarios asserting alert payload and delivery channel.

---

## Contested Findings

None. All lenses converged; no genuine either/or conflicts requiring a human/lead call.

---

## Playbook Coverage

| Check | Surviving finding count |
|-------|------------------------|
| C1 | 2 |
| C3 | 2 |
| C5 | 1 |
| beyond_checklist | 3 |
| **Total** | **8** |

Beyond-checklist ratio: 3/8 = **37.5%** — exceeds the 30% drift threshold. The BDD playbook's C1–C5 checks do not yet cover recovery-pairing gaps (chaos_engineer), audit-sink failure edges (chaos_engineer), or SSRF encoding bypass classes (security_engineer). Playbook maintainer should evaluate adding check rows for these concern classes.

---

## Floor-falsified Findings

The audit skill's deterministic traceability/coverage floor adjudicated two auditor findings as false positives. Both are excluded from the verdict and from the finding set above.

### Discarded: auditor-P2-001

**Cited check:** C1
**Location:** §3.1 / BDD.01.03.2986 ("missing @prd")
**Reason discarded:** FALSE POSITIVE — floor adjudication.

The feature-level cumulative tag `@prd:PRD.01.09.7f20` applies to every scenario (established in §2). Scenario 2986 exercises EARS.01.04.c060, which EARS-01 records as an author assumption with NO PRD transport-encryption element. The scenario correctly carries no scenario-specific @prd; adding one would fabricate a false traceability link. The auditor misread the cumulative tagging model as requiring a scenario-specific @prd on every scenario.

### Discarded: auditor-P2-002

**Cited check:** beyond-checklist:coverage-matrix-incomplete
**Location:** §4.2 Traceability matrix ("incomplete, 9 scenarios missing")
**Reason discarded:** FALSE POSITIVE — floor adjudication.

All 9 named scenarios (0759, 1a55, 40d7, 4df6, 5f58, 6f00, 8b97, ed21, f44a) ARE present in the §4.2 matrix as BDD-scenario column values (verified 1–3 occurrences each). The auditor misread the matrix orientation: the matrix is an EARS→BDD forward map where scenarios appear as values, not row keys. The matrix is not incomplete.

**Effect on auditor score:** With both findings discarded, no valid findings remain for the auditor lens. Auditor lens_score recomputed to 100 (from raw self-score of 87).

---

## Summary Table

| Priority | Count | Blocking? |
|----------|-------|-----------|
| P0 | 0 | — |
| P1 | 0 | — |
| P2 | 1 | No |
| P3 | 7 | No |
| **Total** | **8** | **0 blocking** |

**Combined status: PASS**
**Content score: 95**
**Structural status: PASS**
**Blocking findings: 0**
