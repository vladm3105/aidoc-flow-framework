# Hermes Agent as SDD Strategy Execution Runtime

## Pattern

When an SDD pipeline defines a strategy that must execute autonomously (trading agent, monitoring system, etc.), **Hermes Agent** can serve as the runtime orchestrator instead of building a custom execution engine. This pattern was proven with the TradeGent CC autonomous covered call trading agent (BRD-01 through BRD-10, ADR-21).

## When to Use

- SDD pipeline defines an autonomous strategy with scheduled check windows
- Strategy requires external system integration (broker APIs, databases, webhooks)
- MVP timeline is tight — building a custom orchestrator is too expensive
- Strategy rules evolve over time — soft updates (skill patches) preferred over code deploys
- Multi-platform operator alerting is needed (Telegram, Discord, etc.)

## Architecture

```
Hermes Agent (orchestration runtime)
  ├── cronjob: scheduled check windows (market hours, daily scans)
  ├── skills: SDD documents loaded as decision rules
  ├── memory: persistent state across sessions (positions, account, keys)
  ├── execute_code: apply strategy rules programmatically
  ├── MCP tools: broker/external system integration
  └── gateway: operator alerts via messaging platforms
```

## Implementation Steps

### 1. Hermes Profile Setup

```bash
hermes profile create tradegent
hermes -p tradegent config set agent.max_turns 120
hermes -p tradegent tools enable cronjob memory delegation
```

### 2. Register External MCP Servers

```bash
hermes -p tradegent mcp add broker-ib \
  --command "/opt/data/tradegent/.venv/bin/python" \
  --args "-m ib_mcp_server" \
  --cwd "/opt/data/tradegent/"
```

### 3. Create Strategy Skills from SDD Documents

Convert each SDD document into a Hermes skill:
- BRD → "what to do" (objectives, constraints)
- PRD → "how it works" (features, capabilities)
- EARS → "formal rules" (WHEN-THE-SHALL-WITHIN)
- BDD → "acceptance tests" (Given-When-Then scenarios)

Skills go in `~/.hermes/skills/tradegent/`.

### 4. Schedule Cron Jobs

```bash
# Monday check window (9:30am EST)
hermes -p tradegent cron create "30 9 * * 1" \
  --prompt "Run Monday morning check window per BRD-04. Fetch positions and quotes. Open new calls at delta-0.35. Load skills: brd-04, brd-03, prd-03, ears-04."

# Wednesday afternoon check (3:00pm EST)
hermes -p tradegent cron create "0 15 * * 3" \
  --prompt "Run Wednesday afternoon roll-out evaluation per BRD-04. Check DTE<=2 positions. Evaluate net credit >= 0.80."
```

### 5. Configure Gateway for Alerts

```bash
hermes -p tradegent gateway setup  # Configure Telegram/Discord
hermes -p tradegent gateway install  # Run as systemd service
```

## Advantages Over Custom Orchestrator

| Aspect | Custom Orchestrator | Hermes Agent |
|--------|-------------------|--------------|
| Build time | 4-6 developer-weeks | ~1 developer-week |
| Scheduling | Build cron + state machine | Built-in `cronjob` tool |
| External APIs | Build integration layer | MCP servers (reusable) |
| State persistence | Build database layer | Built-in `memory` tool |
| Rule updates | Code redeploy | Skill patches (no deploy) |
| Operator alerts | Build notification system | Built-in `gateway` (Telegram/Discord/etc.) |
| Audit trail | Build logging pipeline | Session transcripts |
| Multi-platform | N/A | 15+ messaging platforms |

## Pitfalls

- **LLM inference cost**: Each check window triggers a session (~5-10K tokens). At 5-10 checks/day, cost is ~$5-10/month. Acceptable for MVP; monitor for budget.
- **Cron precision**: Minute-level, not sub-second. Acceptable for market-hour check windows (2-minute tolerance per EARS requirements).
- **Single process**: Hermes crash during market hours requires watchdog. Configure systemd `Restart=always` with `RestartSec=2`.
- **Strategy drift**: LLM may deviate from strict rulebook if skills are not sufficiently explicit. Write skills in imperative EARS syntax, not narrative.

## Cost Comparison (TradeGent CC)

| Item | Custom (ADR-01) | Hermes (ADR-21) |
|------|----------------|-----------------|
| Development | 6 developer-weeks | 1 developer-week |
| Infrastructure | $200/month (Redis, etc.) | $0 (Hermes is open-source) |
| LLM Inference | $0 | $5-10/month |
| **Total MVP** | **6 weeks + $200/mo** | **1 week + $5-10/mo** |

## Reference

ADR-21 documents this decision for the TradeGent CC project:
`/opt/data/tradegent_covered_calls/05_ADR/ADR-21_hermes_orchestration_runtime.yaml`
