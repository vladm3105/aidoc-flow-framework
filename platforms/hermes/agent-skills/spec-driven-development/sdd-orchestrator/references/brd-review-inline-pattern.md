# BRD Review — Inline 4-Persona Pattern

## When to Use

Use this pattern when:

- UCX `sdd_review` executors are unavailable or would time out
- You need rapid BRD review without subagent dispatch overhead
- User prefers batch processing: review → remediate → next, minimal friction

## Prerequisites

1. BRD document exists and is structurally valid (verified via `sdd_validate`, 0 errors / 0 warnings)
2. UCX project set and template collision resolved
3. Full BRD document read (sections: metadata, document_control, executive_summary, business_objectives, project_scope, stakeholders, functional_requirements, adr_topics, quality_expectations, constraints, acceptance_criteria, risk_management, traceability)

## BRD Review Personas (4)

Unlike ADR reviews (5 personas), BRD reviews use 4 personas focused on business-level concerns:

| Persona | Focus Area | Key Checks |
|---------|-----------|------------|
| **System Architect** | Decision quality, C4-level appropriateness, architecture soundness | Two-layer design, interface contracts, cross-BRD dependencies, C4 Context level compliance |
| **Security Auditor** | Security, compliance, credential management, audit trail | Credential storage, paper/live isolation, session management, regulatory references |
| **Business Analyst** | Requirements completeness, stakeholder coverage, scope boundaries, SMART objectives | Hypothesis testability, metric completeness, scope clarity, cost-benefit reasonableness |
| **Chaos Engineer** | Failure modes, edge cases, missing risks, data validation gaps | Connection loss, duplicate orders, stale data, malformed API responses, crash recovery, clock skew |

## Review Pattern

### Step 1: Read BRD in Sections

For large BRDs (1000+ lines), read strategically:

```
read_file offset=1    limit=200   # metadata, document_control, executive_summary, diagrams, introduction
read_file offset=200  limit=200   # business_objectives, project_scope, stakeholders, first FRs
read_file offset=400  limit=200   # remaining FRs, adr_topics
read_file offset=600  limit=200   # adr_topics cont., quality_expectations, constraints
read_file offset=800  limit=200   # acceptance_criteria, risk_management, approval, traceability
read_file offset=1000 limit=110   # glossary, appendix
```

### Step 2: Produce 4-Persona Review Inline

Structure:

```
## PERSONA REVIEW REPORT: BRD-NN

### 1. THE ARCHITECT — Decision Quality
**Verdict: PASS/PASS with gaps/FAIL**
| Aspect | Assessment |
Architecture soundness, C4-level check, interface clarity, cross-BRD links

### 2. THE AUDITOR — Security & Compliance  
**Verdict: PASS/PASS with gaps/FAIL**
Credential management, isolation guarantees, audit trail, regulatory refs

### 3. THE BUSINESS ANALYST — Requirements Completeness
**Verdict: PASS/PASS with gaps/FAIL**
SMART objectives, scope boundaries, FR coverage, stakeholder completeness

### 4. THE CHAOS ENGINEER — Failure Modes
**Verdict: PASS/PASS with gaps/FAIL**
| Scenario | Covered? | Detail |
Crash recovery, data validation, clock skew, partial fills, edge cases

## SYNTHESIS
| Priority | Count | Issues |
| P0 | N | — |
| P1 | N | blocking gaps |
| P2 | N | enhancements |

**Score: XX/100 (weighted: 100 - P1×3 - P2×0.4)**
**Recommendation: ACCEPT / REVISE / REJECT**
```

### Step 3: Apply P1+P2 Remediations

When user says "fix all issues" or "apply all P1 and P2", use `execute_code` with Python string replacement for multi-section patches:

```python
import subprocess

path = "/path/to/BRD-NN.yaml"
r = subprocess.run(["cat", path], capture_output=True, text=True)
content = r.stdout

# Apply each fix as string.replace(old, new)
# CRITICAL: preserve YAML indentation — new list items must match surrounding indent level
```

After all patches:

- Update `document_control.version` (1.0 → 1.1)
- Update `document_control.last_updated` to current timestamp
- Update `document_control.status` to "Reviewed"
- Prepend new `revision_history.entries` entry
- Verify YAML via `yaml.safe_load()` before writing
- Run `sdd_validate` for structural confirmation

### Step 4: Score and Close

After remediation, re-run `sdd_validate` and `sdd_score_show`. Update `health_score.cross_brd_validated`.

## Common P1 Finding Patterns for BRDs

| Pattern | What to Flag | Example Fix |
|---------|-------------|-------------|
| **Crash before idempotency record** | System submits order, IB returns orderId, system crashes before writing key. On restart, order exists at IB but system has no record. | Add startup reconciliation: query all open orders from IB on reconnect, register any orphans with idempotency key derived from IB orderId. |
| **Malformed API data passthrough** | Broker returns null greeks, negative IV, zero bid+ask — data passed to strategy engine without validation. | Add data validation gate before upstream delivery: reject null greeks, negative IV, zero bid/ask pairs. Flag as DATA_QUALITY event. Escalate after N consecutive events. |
| **Silent position data corruption** | Position stream trusted without sanity checks. Wrong quantity or cost basis leads to incorrect trading decisions. | Cross-validate position market value against account NAV. Flag deviations > threshold as DATA_INTEGRITY. |
| **Session expiry undetected** | Heartbeat checks TCP liveness but not session validity. Expired TWS session silently rejects orders or returns stale data. | Heartbeat must validate both connection liveness AND session validity. Treat expired session same as disconnection. |
| **Paper trading overconfidence** | Success metrics based solely on paper trading — fills are instantaneous with no slippage or liquidity constraints. | Document paper_trading_caveat: paper validation is necessary but not sufficient for live enablement. |
| **Missing security assumptions** | Network security (TLS), clock sync (NTP), API version compatibility not documented as assumptions. | Add to assumptions list with validation_method and impact_if_false. |
| **Partial fill ambiguity** | Limit order partially fills during escalation timer — unclear whether to reset timer, reduce quantity, or continue. | Define partial fill handling: reset timer, reduce remaining qty. If >90% filled, cancel remainder. |

## Proven Cadence (TradeGent CC BRD-10, 2026-05-14)

BRD-10 review and remediation in a single session:

- BRD-10 (1,102 lines): 8 fixes (3 P1 + 5 P2) → v1.0→v1.1, score 100/100
- P1 fixes: startup reconciliation, malformed data validation, position sanity checks
- P2 fixes: session expiry, paper trading caveat, network security, clock skew, partial fill handling
- Total tool calls: ~8 (read ×4, execute_code ×2, patch ×2, validate ×1)
- YAML indentation pitfall: 3 list items inserted at wrong indent level — fixed by heuristic re-indent pass

## Differences from ADR Inline Review

| Aspect | ADR Review | BRD Review |
|--------|-----------|------------|
| Personas | 5 (Architect, Tech Lead, Operator, Auditor, Chaos) | 4 (Architect, Auditor, Business Analyst, Chaos) |
| Focus | Architecture decisions, implementation impact, operations | Business requirements, scope, stakeholders, SMART objectives |
| Score formula | 100 - sum(capped_category_deductions × weights) | Simplified: 100 - P1×3 - P2×0.4 |
| Common P1s | Cooldown scoping, timeout degradation, event bus gaps | Data validation, crash recovery, session management, missing assumptions |
