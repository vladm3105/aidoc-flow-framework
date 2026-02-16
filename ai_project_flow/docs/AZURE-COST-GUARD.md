# Azure-Only Cost Guard — Implementation Description

**Purpose:** Automated cost protection for Azure-only deployments  
**Scope:** Azure budget alerts, LLM cost control, idle resource detection, auto-remediation  
**Effort:** 3-4 days  
**Monthly Cost:** $0-20 (mostly free tier)

---

## Problem Statement

| Issue | Impact | Solution |
|-------|--------|----------|
| Azure OpenAI billing spike | Unexpected costs | Auto-disable at threshold |
| Idle Azure services ($50-100/mo) | Ongoing waste | Detect and alert/disable |
| Manual monitoring required | Time waste | Automated remediation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   AZURE-ONLY COST GUARD                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ Azure Cost  │───▶│ Event Grid  │───▶│  Azure Function     │ │
│  │   Alerts    │    │   Topic     │    │  (Remediation)      │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│                                                    │            │
│  ┌─────────────┐    ┌─────────────┐               ▼            │
│  │ Azure       │───▶│ Cost Mgmt   │    ┌─────────────────────┐ │
│  │ Scheduler   │    │    API      │    │  Actions:           │ │
│  │ (daily)     │    │             │    │  • Stop VM          │ │
│  └─────────────┘    └──────┬──────┘    │  • Disable endpoint │ │
│                            │           │  • Scale to 0       │ │
│                            ▼           │  • Send alert       │ │
│                     ┌─────────────┐    └─────────────────────┘ │
│                     │ Azure Func  │                            │
│                     │ (Idle Scan) │──▶ Cosmos DB (config)      │
│                     └─────────────┘                            │
│                            │                                   │
│  ┌─────────────────────────▼───────────────────────────────────┐│
│  │ Azure Advisor + Cost Management API                         ││
│  │ • Rightsizing recommendations (VMs, SQL)                    ││
│  │ • Idle resource insights                                    ││
│  │ • Reserved Instance recommendations                         ││
│  │ • Cost breakdown by resource/meter                          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ LLM Wrapper (in your app code)                              ││
│  │ • Tracks Azure OpenAI spend per request                     ││
│  │ • Enforces daily/monthly limits                             ││
│  │ • Logs to Azure Monitor                                     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Budget Alert → Auto-Remediation

**Trigger:** Azure Cost Management Budget Alert  
**Action:** Azure Function disables specific services

| Threshold | Action |
|-----------|--------|
| 50% of budget | Teams/email warning |
| 80% of budget | Disable non-critical services |
| 100% of budget | Disable all optional services |

**Services to auto-disable (configurable in Cosmos DB):**
- Azure Functions (non-production)
- Azure OpenAI endpoints
- Container Apps (dev/staging)
- Any resource tagged `{SERVICE_NAME}: auto-disable`

### 2. LLM Cost Control (Azure OpenAI)

**Implementation:** Python wrapper for Azure OpenAI

```python
from azure.cosmos import CosmosClient
from openai import AzureOpenAI

class CostGuardedAzureOpenAI:
    def __init__(self, daily_limit=100, monthly_limit=500):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.client = AzureOpenAI()
        self.cosmos = CosmosClient.from_connection_string(conn_str)
    
    def call(self, prompt, model="gpt-4"):
        current_spend = self._get_spend_from_cosmos()
        
        if current_spend['daily'] >= self.daily_limit:
            raise DailyLimitExceeded(f"Daily limit ${self.daily_limit} reached")
        
        if current_spend['monthly'] >= self.monthly_limit:
            raise MonthlyLimitExceeded(f"Monthly limit ${self.monthly_limit} reached")
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        self._record_cost(response.usage, model)
        return response
```

### 3. Idle Resource Detection

**Trigger:** Azure Logic Apps or Timer-triggered Function (daily)  
**Scanner:** Azure Function queries Azure Monitor metrics

| Resource Type | Idle Criteria |
|---------------|---------------|
| Container Apps | 0 requests in 7 days |
| Virtual Machines | CPU < 5% for 7 days |
| Azure SQL | 0 connections in 7 days |
| Storage Accounts | 0 transactions in 30 days |
| Service Bus | 0 messages in 30 days |

### 4. Azure Advisor Integration

**Purpose:** Leverage Azure's native cost recommendations (free)

| Advisor Category | What It Finds |
|------------------|---------------|
| Cost | Oversized VMs, idle resources |
| Performance | Optimization opportunities |
| Reliability | HA recommendations |

---

## Infrastructure (Mostly Free Tier)

| Component | Purpose | Monthly Cost |
|-----------|---------|--------------|
| Azure Functions (3) | Remediation, idle scan, advisor | $0 (1M free) |
| Event Grid (1 topic) | Budget alert routing | $0 |
| Cosmos DB | Config, spend tracking | $0-5 (serverless) |
| Azure Monitor | Metrics, logs | $0 (basic) |
| Cost Management API | Budget + cost data | $0 |
| Azure Advisor | Recommendations | $0 |
| **Total** | | **$0-20/month** |

---

## Implementation Timeline (3-4 Days)

### Day 1: Budget Alerts + Remediation (4-6 hours)

- [ ] Create Event Grid topic `cost-alerts`
- [ ] Create Azure Function `budget-remediation`
- [ ] Set up Cost Management Budget with action group
- [ ] Create Cosmos DB container `{SERVICE_NAME}`
- [ ] Test: trigger alert, verify resource stopped

### Day 2: LLM Cost Control (3-4 hours)

- [ ] Create `CostGuardedAzureOpenAI` wrapper class
- [ ] Create Cosmos DB schema for spend tracking
- [ ] Integrate into existing Azure OpenAI calls
- [ ] Add Azure Monitor logging
- [ ] Test: verify limits enforced

### Day 3: Idle Resource Detection + Advisor (4-5 hours)

- [ ] Create Azure Function `idle-scanner`
- [ ] Query Azure Monitor for usage metrics
- [ ] Integrate Azure Advisor API
- [ ] Store results in Cosmos DB
- [ ] Set up weekly email via Logic Apps
- [ ] Test: verify idle resources detected

### Day 4 (Optional): Simple Dashboard (4-6 hours)

- [ ] Use Power BI (free) or simple React app
- [ ] View current spend vs limits
- [ ] View Advisor recommendations
- [ ] Toggle auto-remediation on/off

---

## Success Criteria

- [ ] Azure OpenAI spend never exceeds daily/monthly limits
- [ ] Budget alerts trigger within 1 hour of threshold
- [ ] Idle Azure resources detected weekly
- [ ] Auto-remediation prevents unexpected spikes
- [ ] Total infrastructure cost < $20/month

---

## Next Steps

1. **Use this for Azure-only** → 3-4 days, $0-20/month
2. **Or use Full MVP** → 15-20 days, $13-40/month, more features

See [GCP-COST-GUARD.md](GCP-COST-GUARD.md) for GCP version.  
See [MINIMAL-COST-GUARD.md](MINIMAL-COST-GUARD.md) for multi-cloud version.
