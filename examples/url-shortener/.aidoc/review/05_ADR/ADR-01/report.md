# ADR-01 Review Report — Iteration 2 (Re-audit)

**Artifact:** ADR-01 (URL Shortener — Durable KV Storage Decision)
**Layer:** 05_ADR
**Iteration:** 2 (post-fixer pass)
**Date:** 2026-06-08
**Synthesizer:** chairperson reduce pass

---

## Gate decision

**PASS**

Structural floor: PASS (sdd_doc_lint clean, all element IDs conform, all upstream
tags resolve, all 10 required template sections + Glossary + Appendix present and
non-empty, diagram contract satisfied, metadata valid).

Content score: **90** (weighted blend = 90.18, floored to 90; no P0/P1 findings,
no blocking cap applied).

Gate threshold: 90. Score meets threshold exactly. No unresolved P0 or P1 findings.
Combined status: **PASS**.

---

## Readiness score

| Lens              | Weight | Score | Contribution |
|-------------------|--------|-------|--------------|
| architect         | 35     | 95    | 33.25        |
| tech_lead         | 25     | 85    | 21.25        |
| chaos_engineer    | 8      | 82    | 6.56         |
| security_engineer | 12     | 91    | 10.92        |
| operator          | 10     | 82    | 8.20         |
| auditor           | 10     | 100   | 10.00        |
| **Weighted blend**|        |       | **90.18**    |
| **Content score** |        |       | **90**       |

No P0 or P1 findings exist in the merged set; no cap applied beyond integer floor.

---

## Coverage

| Metric         | Value |
|----------------|-------|
| Expected lenses| 6     |
| Ran            | 6     |
| Quorum met     | true  |
| Confidence     | Full  |

All six crew lenses returned valid persona-output records. No low-confidence flag.

---

## Executive summary

The ADR-01 fixer pass resolved the material blocking findings from iteration 1:
the reversibility classification (§3 ADR.01.03.f5f5 one-way with rationale), the
API-to-store trust-boundary decision (ADR.01.03.1050 per-service-principal + TLS +
fail-closed), and the at-rest encryption decision (ADR.01.03.0db1 AES-256 envelope +
provider KMS + rotation cadence). The architect, security_engineer, and auditor
lenses confirm these are substantively resolved. The decision is implementer-bindable
and upstream-consistent (BRD/PRD/EARS/BDD tag chains verified).

The fixer introduced one new defect: it anchored the §5 write-path partitioning
mitigation on element ID ADR.01.03.5536, which is referenced in prose but never
defined as a §3 decision element. This dangling pointer is the most structurally
significant open item (P2, merged from two lenses). It is not blocking under the
gate rules (no P1), but it must be resolved before downstream SPEC authors can
trace the write-partitioning commitment.

Five additional P2 findings surface observability gaps: the monitoring baseline is
missing the primary SLO (redirect read-path p95 latency), the reconciliation-lag
age signal, the data-loss-possible blast classification for the ack-before-durable
failure, and an explicit detection path for silent durability failure. These are
well-scoped additions to §7 that require no architectural change.

Five P3 findings are precision improvements: two from the architect (decision
trailing imperatives, §2 scope statement narrower than §3/§6), two from security
(threat-framing altitude gap, missing §8 audit evidence for the new controls), and
one from chaos (RPO detection-time unquantified).

**Note on auditor lens accuracy.** The auditor scored 100 with no findings and
stated in its notes that ADR.01.03.5536 was among the five new conformant element
IDs added to §3. This is factually incorrect: ADR.01.03.5536 appears only in a
single back-reference in §5 and is not defined anywhere in §3. The auditor missed
a genuine dangling reference on its A3 traceability check. The finding is carried
from tech_lead and chaos_engineer; the auditor score is taken as submitted but the
miss is noted for calibration.

---

## Findings by priority

### P2 — Non-blocking; resolve before SPEC layer

#### MERGED-P2-001 — Dangling element reference ADR.01.03.5536

**Lenses:** tech_lead (C1), chaos_engineer (C5)
**Location:** §5 Consequences (ADR.01.05.9107) / §3 Decision semantics (referenced ADR.01.03.5536)
**Message:** The §5 coupling-risk mitigation anchors the write-path partitioning
contract on element ADR.01.03.5536, which is cited at §5 but never defined anywhere
in §3. The §3 Decision semantics block defines only ADR.01.03.{5c3c, f5f5, 3315,
1050}; §6 adds 0db1. This is a genuine dangling intra-document element pointer. The
inline prose describes partitioning semantics ('written once, best-effort,
reconciliation logged') but does not resolve whether the visit-count increment is
at-most-once or at-least-once — the increment delivery semantic is ambiguous. A SPEC
author following the citation lands on nothing. This element is the load-bearing
primitive keeping a count-write fault off the redirect path (BDD.01.03.5f58/a7ad).

**Recommendation:** Either (a) promote to a real §3 decision element: add
'ADR.01.03.5536 — Write-path partitioning: the durable mapping (original_url,
status) is written once on issuance and never rewritten by the off-path increment,
which performs an isolated partial-field write' and declare the increment delivery
semantic explicitly (at-most-once with reconciliation OR at-least-once with
idempotent/dedup increment), then keep the §5 citation; or (b) drop the ID from §5
and let the inline prose stand alone, expanding it to declare the delivery semantic
unambiguously. Resolving 5536 also closes the increment-semantics ambiguity.

---

#### CHAOS-P2-1 — Data-loss-possible blast class never applied to RPO>0 scenario

**Lens:** chaos_engineer (C2)
**Location:** §7 Implementation Assessment / Monitoring baseline (ADR.01.05.d549)
**Message:** The §7 phase table assigns blast classes but never applies
data-loss-possible to the highest-blast failure: a KV tier that acks before durable
commit, silently losing a confirmed mapping. Phase 1 risk 'conditional-write
semantics differ' is labelled cross-service, understating the worst case.
**Recommendation:** Add a §7 row classifying durable-commit-without-quorum
(ack-before-durable) as blast radius = data-loss-possible.

---

#### CHAOS-P2-2 — No detection path for silent durability failure

**Lens:** chaos_engineer (beyond-checklist:silent-durability-failure)
**Location:** §3 Decision (ADR.01.03.5c3c) / §7 Monitoring baseline
**Message:** If the managed KV tier acks on write-buffer rather than quorum/fsync,
confirmed mappings are lost silently with no detection signal until a crash. The §7
RPO monitor presumes loss is observable; it is not in this failure mode.
**Recommendation:** State the required durability-acknowledgement contract (quorum/
fsync-before-ack) as a §3 decision constraint and add a §7 detection signal (e.g.,
periodic post-commit read-back / durability audit).

---

#### OPS-P2-1 — Redirect read-path latency absent from monitoring baseline

**Lens:** operator (C2)
**Location:** §7 Implementation Assessment — Monitoring baseline
**Message:** The redirect read path is the highest-traffic path and the primary SLO
(p95 < 50 ms, @threshold:PRD.01.perf.redirectp95), yet no monitoring row exists for
it. A latency regression surfaces only through end-user complaints or an external
synthetic monitor.
**Recommendation:** Add monitoring row: redirect read-path latency (p95), target
< 50 ms, alert >= 50 ms sustained over calibration window (e.g., 2 min).

---

#### OPS-P2-2 — Reconciliation-lag age absent from monitoring baseline

**Lens:** operator (C2)
**Location:** §7 Implementation Assessment — Monitoring baseline
**Message:** Visit-count reconciliation lag has no monitoring row. BDD.01.03.a7ad
establishes a 60 s reconciliation budget. A stuck reconciliation process is silent
under the current baseline; the RPO loss signal fires too late.
**Recommendation:** Add monitoring row: reconciliation lag (age of oldest unresolved
dropped-increment log entry), target < 60 s, alert >= 60 s -> WARN.

---

### P3 — Advisory; address at the layer's discretion

#### ARCH-P3-1 — Decision trailing imperatives blur binding clause (C1)

**Lens:** architect
**Location:** §3 Decision (ADR.01.03.5c3c)
Four elaborating imperatives follow the lead decision sentence in the same paragraph,
blurring which clause is THE binding decision. Optional precision nicety; decision is
implementer-bindable as written. Demote to 'Decision semantics' sub-list.

#### ARCH-P3-2 — §2 scope statement narrower than §3/§6 security decisions (beyond-checklist:scope-bundling)

**Lens:** architect
**Location:** §3 Decision (ADR.01.03.1050) / §6 (ADR.01.03.0db1)
§2 scope excludes cache/code-generator/replication; per-service-principal auth/TLS
and envelope-encryption are legitimately store-coupled but not named in the charter.
Add one clause to §2 scope admitting the store's trust boundary and at-rest-encryption
posture. No decision change required.

#### CHAOS-P3-1 — RPO detection-time unquantified (C3)

**Lens:** chaos_engineer
**Location:** §7 Monitoring baseline — Confirmed-mapping loss (RPO) row
'Any loss' is a threshold, not a quantified time-to-detect; the RPO row lacks a
detection-time bound or concrete detection signal, unlike the write-conflict and
commit-latency rows. Add a quantified detection-time bound and explicit signal (e.g.,
'durability audit read-back detects within N s').

#### SEC-P3-001 — Threat-framing absent for new security controls (C4)

**Lens:** security_engineer
**Location:** §3 Decision (ADR.01.03.0db1, ADR.01.03.1050) / §6 Integration points
New controls introduced without explicit in-scope vs out-of-scope threat statement.
Residual altitude gap; add a one-line threat framing to §6 notes naming what each
control covers and what it does not.

#### SEC-P3-002 — No §8 verification criterion or §7 signal for new security commitments (beyond-checklist:audit-evidence)

**Lens:** security_engineer
**Location:** §8 Verification / §7 Monitoring baseline
ADR.01.03.1050 (fail-closed) and ADR.01.03.0db1 (encryption-at-rest) are asserted
but not evidenced. Add §8 success criterion for injected store-auth/TLS failure and
a §7 provisioning check that at-rest encryption is enabled before go-live.

---

## Contested findings

None. No genuine either/or judgment exists across lenses at the same location.
The MERGED-P2-001 dedup is a max-severity merge, not a conflict.

---

## Auditor lens miss — calibration note

The auditor lens scored 100/100 with zero findings and stated in notes that
ADR.01.03.5536 was among five new conformant IDs added to §3. This is factually
incorrect. ADR.01.03.5536 appears only as a back-reference in §5 and is never
defined as a §3 decision element — it is a dangling pointer. The auditor's A3
traceability check passed it as conformant. The finding is carried from tech_lead
and chaos_engineer (MERGED-P2-001). The auditor score is taken as submitted (it
reviewed other compliance dimensions correctly); the A3 miss is flagged here as a
calibration signal for the auditor playbook.

---

## Playbook coverage

| Check          | Findings count |
|----------------|----------------|
| C1             | 2              |
| C2             | 3              |
| C3             | 1              |
| C4             | 1              |
| C5             | 1              |
| beyond_checklist | 3            |
| **Total**      | **11**         |

(MERGED-P2-001 spans C1 and C5; counted once under each for histogram purposes,
contributing to both rows above.)

Beyond-checklist ratio: 3/11 = 27%. Below the 30% drift-signal threshold. Playbook
revision not indicated.

No findings were discarded (all 10 unique findings carried valid check citations;
the merged finding's two source records both had valid citations).

---

## Per-lens summary

| Lens              | Score | Findings | Notes |
|-------------------|-------|----------|-------|
| architect         | 95    | 2 × P3   | C4 reversibility (iter-1 P2) resolved; 2 precision nits |
| tech_lead         | 85    | 1 × P2   | Dangling 5536 (fixer-introduced); write-ordering gap resolved |
| chaos_engineer    | 82    | 2 × P2, 2 × P3 | C1/C4 pass; C5 issuance pass; blast-class + silent-durability open |
| security_engineer | 91    | 2 × P3   | Both iter-1 blocking (trust boundary, at-rest crypto) resolved; 2 residuals |
| operator          | 82    | 2 × P2   | Runbook resolved; write-conflict threshold resolved; 2 SLO monitoring gaps remain |
| auditor           | 100   | 0        | All IDs/traceability pass; MISSED dangling 5536 (noted above) |

---

## Summary table

| Category            | Count |
|---------------------|-------|
| Blocking (P0 + P1)  | 0     |
| P2 findings         | 5     |
| P3 findings         | 5     |
| Total findings      | 10    |
| Lenses ran          | 6/6   |
| Content score       | 90    |
| Gate                | PASS  |

---

*Synthesizer: chairperson reduce pass. This report mirrors `verdict.json`; if any
value diverges, the JSON is authoritative.*
