# ADR Review — Inline 5-Persona Pattern

## When to Use

Use this pattern when:

- UCX `sdd_review` executors are unavailable (no API keys, auth failures)
- `delegate_task` subagents would time out with large review prompts (48KB+)
- You need rapid sequential ADR reviews without tool-call overhead
- The user wants batch processing: review → remediate → next, minimal friction

## Prerequisites

1. ADR document exists and is structurally valid (verified via `yaml.safe_load()`)
2. UCX template collision resolved (`_id: ADR-NN` patch or templates moved aside)
3. You have read the full ADR document (at minimum: context, decision, alternatives, consequences, implementation, verification sections)

## Review Pattern

### Step 1: Read ADR in Sections

For large ADRs (1000+ lines), read strategically:

```
read_file offset=1    limit=80   # metadata, document_control, context
read_file offset=200  limit=200  # decision, implementation, alternatives
read_file offset=450  limit=200  # consequences, cost_estimate
read_file offset=850  limit=80   # verification, traceability
```

### Step 2: Produce 5-Persona Review Inline

Structure the review as a markdown report with these 5 personas:

```
## PERSONA REVIEW REPORT: ADR-NN

### 1. THE ARCHITECT — Decision Quality
**Verdict: PASS/PASS with gaps/FAIL**
| Aspect | Assessment |
Rationale explicit, alternatives count, architecture alignment, scalability

### 2. THE TECH LEAD — Implementation Impact
**Verdict: PASS/...**
Complexity assessed, dependencies listed, skill requirements

### 3. THE OPERATOR — Operational Impact
**Verdict: PASS/...**
Deployment, monitoring metrics, rollback, graceful degradation

### 4. THE AUDITOR — Security & Compliance
**Verdict: PASS/...**
Security implications, compliance, audit trail, data retention

### 5. THE CHAOS ENGINEER — Failure Modes
**Verdict: PASS/...**
| Scenario | Covered? | Detail |
Key edge cases to probe: crash mid-operation, data stall, race conditions

## SYNTHESIS
| Priority | Count | Issues |
| P0 | N | — |
| P1 | N | specific gap descriptions |
| P2 | N | enhancements |

**Recommendation: ACCEPT/REVISE/REJECT**
```

### Step 3: Apply P1 Remediations

When the user says "yes, remediate" or "apply", use the `patch` tool directly:

```python
from hermes_tools import patch

# Fix cooldown scoping, timeout degradation, etc.
patch(path, old_string="...", new_string="...")
```

After all patches, update metadata:

- `last_updated` → today's date
- `spec_ready_score` → increment (e.g., 92→93)
- `version` → increment (e.g., 1.0→1.1)
- `revision_history` → prepend new entry

### Step 4: Verify and Continue

```python
import yaml
with open(path) as f:
    data = yaml.safe_load(f)
# Confirm YAML valid, risk count changed, etc.
```

Then offer: "Next: update ADR index, continue to ADR-NN+1"

## Proven Cadence (TradeGent CC, 2026-05-14)

Six engine ADRs reviewed and remediated in one session:

- ADR-04 (404 lines): 4 P1 fixes → 92→93/100 v1.1, risks 3→6
- ADR-05 (1079 lines): 2 P1 fixes → 92→93/100 v1.1, risks 3→4
- ADR-06 (1120 lines): 1 P1 fix → 92→93/100 v1.1, monitoring metrics 4→5
- ADR-07 (794 lines): 1 P1 fix → TBD→93/100 v1.1, Q3 default-bias corrected
- ADR-08 (982 lines): 2 fixes (1 P1 + 1 P2) → 93→94/100 v1.1
- ADR-09 (422 lines): CLEAN REVIEW, no P1 gaps → 91/100 (no remediation needed)

User interaction pattern: "continue" → review → "yes, remediate" (or "fix all issues" for P1+P2) → "continue" → next ADR. No subagent dispatch, no API executor required, total tool calls per ADR: ~5-8 (including metadata updates).

### Cross-Cutting ADR Batch (ADRs 10-19)

Cross-cutting ADRs tend to be shorter (96-273 lines) and more focused than engine ADRs. Review speed increases significantly:

- ADR-10 (Event Bus, 273 lines): 2 fixes (async ack, Redis SPOF buffer) → 90→92/100
- ADR-11 (Auth, 175 lines): CLEAN, 90/100
- ADR-12 (Clock, 160 lines): 4 fixes (NTP self-recovery, monitoring, drift risk, GPS alt) → 89→91/100
- ADR-13 (Idempotency, 157 lines): CLEAN, 91/100
- ADR-14 (WORM, 180 lines): 3 fixes (SIEM alt, mutable-window risk, monitoring) → 88→91/100
- ADR-15 (Observability, 138 lines): CLEAN, 90/100
- ADR-16 (Alerting, 152 lines): CLEAN, 90/100
- ADR-17 (Backpressure, 154 lines): CLEAN, 90/100
- ADR-18 (Validation, 96 lines): 2 fixes (2nd alternative, tradeoffs+implementation) → 90→92/100 — shortest ADR, structurally incomplete (missing sections)
- ADR-19 (Encryption, 179 lines): CLEAN, 90/100

Below-threshold ADRs (88-89/100 before review) typically need 2-4 fixes to reach 91+: structural gaps (missing alternatives, tradeoffs, monitoring), drift/monitoring blind spots, and insufficient risk documentation. The `diagnostic-default-bias` pattern (found in ADR-07 Q3) is rare — most gaps are operational/monitoring, not architectural.

## Common P1 Finding Patterns for ADRs

| Pattern | What to Flag | Example Fix |
|---------|-------------|-------------|
| Crash mid-operation | Idempotency blind spots on restart | Startup reconciliation query |
| Event bus gap | Crash after external confirm but before publish | Periodic reconciliation |
| Data source stall | All-or-nothing timeout rejects valid orders | Tiered degradation |
| Cooldown suppression | Global cooldowns mask independent events | Per-entity scoping |
| Static parameters | No trend monitoring before hard thresholds | Rate-of-change metrics |
| **Diagnostic default-bias** | A diagnostic question defaults to a high-severity state when data is missing, creating systemic upward bias (e.g., Q3 NLP classifier defaults to S3 when confidence < 80%, but in MVP no NLP exists — ALL positions get S3) | Default to a neutral/middle state (S2) when data is insufficient; reserve high-severity states (S3/S4) for explicit negative signals only |
| **Stale-WATCH auto-escalation** | Operator-acknowledgment flags (WATCH level) persist indefinitely without auto-escalation, allowing unsafe conditions to go unaddressed for quarters | Add N-quarter auto-escalation from WATCH→WARNING when no operator acknowledgment recorded |
| **Redis/message bus SPOF** | Inter-engine communication depends on a single Redis instance with no fallback — if Redis crashes, all event-driven coordination halts | Add local event buffering (SQLite) during Redis outage with automatic replay on reconnect; DEGRADED engine state |
| **Synchronous ack blocking** | State propagation publisher blocks sequentially waiting for each consumer's ack — N consumers × timeout = N× delay | Change to async aggregate timeout (asyncio.gather) so all consumers ack in parallel within a single timeout window |
| **NTP/clock drift self-recovery** | Clock validation runs only at startup — prolonged agent runtime (weeks) accumulates silent drift | Add periodic NTP re-check (every 5 min) with auto-recovery from HALTED when drift drops below threshold |
| **Mutable audit window** | Audit/JSONL files are writable on disk between fsync and daily versioned commit — any process could modify entries undetected for hours | Set file permissions to 0400 after write; run hourly sha256 verification cron; daily git commit with signed tags provides checkpoint |
| **In-memory series loss on crash** | Time-series data (daily returns, marks) accumulated in memory and flushed periodically — crash wipes unflushed data | Write-through to SQLite WAL append-only log on every event; accumulator replays from log on startup; <1ms overhead per write |

## Clean Review Outcome

Not every ADR needs remediation. When all 5 personas return PASS with no P1 or P0 gaps, the review is "CLEAN" and the ADR proceeds to the next layer without any changes. ADR-09 (Portfolio OS, 422 lines, 91/100) is an example — the event-sourcing pattern was correctly scoped as P2 read-only, all alternatives properly rejected, and every failure mode was covered. A clean review is a valid and desirable outcome.

Only flag P2 items (enhancements, tightening thresholds) separately — they do not block the ADR and do not require remediation before the next SDD layer.
