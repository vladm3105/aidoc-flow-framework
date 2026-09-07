# Two-Layer Broker MCP Architecture Pattern

## When to Use

When building a trading system that needs to integrate with one or more broker APIs (Interactive Brokers, Schwab, Tastytrade, etc.) and wants broker portability without rewriting strategy code.

## Pattern

```
┌─ Strategy Engines (in-process) ──────────────────────────┐
│  import internal_api  # broker-agnostic abstractions      │
│  internal_api.place_order(symbol, qty, price, action)    │
└──────────────────────┬────────────────────────────────────┘
                       │ Python function calls (0ms IPC)
┌──────────────────────▼────────────────────────────────────┐
│  Internal API (Python library, broker-independent)        │
│  • Validation gates: market hours, idempotency, freshness │
│  • Data sanity checks: position vs NAV, null greeks      │
│  • Typed return structures (Pydantic models)             │
│  • No broker-specific imports                            │
└──────────────────────┬────────────────────────────────────┘
                       │ MCP stdio (JSON-RPC, ~1-2ms)
┌──────────────────────▼────────────────────────────────────┐
│  Broker MCP Server (per-broker, stdio process)            │
│  • 11 MCP tools: 1:1 mapping to broker API calls         │
│  • Connection lifecycle: heartbeat, backoff, READY flag  │
│  • Rate limiting: token-bucket with CRITICAL tier        │
│  • Idempotency: SQLite WAL key → status store            │
│  • Paper/live isolation: port-based (7496 vs 7497)       │
│  • Watchdog: systemd auto-restart, 3-crash halt          │
└──────────────────────┬────────────────────────────────────┘
                       │ IB API (TCP, TLS, ~5-10ms)
┌──────────────────────▼────────────────────────────────────┐
│  TWS/Gateway (External — Interactive Brokers)             │
└──────────────────────────────────────────────────────────┘
```

## Key Decisions

| Decision | Choice | Alternatives Rejected |
|----------|--------|----------------------|
| Protocol | MCP stdio (JSON-RPC) | HTTP REST (higher latency), Direct monolith (broker lock-in) |
| Broker library | ib_insync (sync, mature) | ib_async (async, no benefit for single-threaded IB API) |
| Idempotency store | SQLite WAL (local, survives restart) | Redis (next cycle for multi-process) |
| Rate limiter | Token-bucket 50/sec, 5 reserved for CRITICAL | Per-engine queues (ADR-17 cross-cutting standard) |
| Credential encryption | AES-256-GCM (FIPS 140-2 path) | Fernet (ADR-19 standard, acceptable for non-FIPS) |
| Process supervision | systemd watchdog, 2s restart, 3-crash halt | Supervisor (acceptable alternative) |

## SDD Pipeline (BRD→IPLAN) for Broker Integration

```
L1 BRD-10: Business requirements — two-layer arch, 12 FRs, 11 ADR topics
L2 PRD-10: Product specs — 7 capabilities, 5 stories, 3 containers, 6 data flows
L3 EARS-10: Formal reqs — 30 requirements, 5-state FSM, 11 quality attributes
L4 BDD-10: Acceptance — 19 scenarios (10 success + 6 error + 2 recovery + 1 audit)
L5 ADR-20: Architecture — 5 decisions, 8 cross-cutting deps, 4 MVP phases
```

## ADR Cross-References for Broker ADR

When creating a broker integration ADR, it must reference these existing cross-cutting ADRs:

| ADR | Topic | Relationship |
|-----|-------|-------------|
| ADR-13 | Idempotency | Extends — reuse SQLite pattern, add broker reconciliation |
| ADR-17 | Rate Limiting | Extends — reuse token-bucket, add IB pacing + CRITICAL tier |
| ADR-18 | Input Validation | Implements — Pydantic at MCP boundary |
| ADR-19 | Secrets | Extends — AES-256-GCM for broker creds (FIPS path) |
| ADR-10 | Event Bus | Depends on — strategy engines communicate via event bus |

## Pitfalls

- **ADR ID collision**: ADR-10 is typically already taken (Event Bus). Use ADR-20 or next available number. Update all cross-references with batch replace.
- **ib_insync vs ib_async**: ib_insync for MVP (sync, single-broker). ib_async reconsider for next cycle (async, multi-broker).
- **TWS daily restart**: 11:45pm EST auto-restart. Suppress alerts during this window. Auto-reconnect handles it.
- **IB API single-threaded**: Serialize all TWS calls. Rate limiter with priority queue is essential — time-critical orders must jump the queue.
