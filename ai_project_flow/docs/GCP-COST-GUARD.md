# GCP-Only Cost Guard — Implementation Description

**Purpose:** Automated cost protection for GCP-only deployments  
**Scope:** GCP budget alerts, LLM cost control, idle resource detection, auto-remediation  
**Effort:** 3-4 days  
**Monthly Cost:** $0-15 (free tier)

---

## Problem Statement

| Issue | Impact | Solution |
|-------|--------|----------|
| LLM billing spike ($3K+) | Unexpected costs | Auto-disable at threshold |
| Idle GCP services ($50-100/mo) | Ongoing waste | Detect and alert/disable |
| Manual monitoring required | Time waste | Automated remediation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GCP-ONLY COST GUARD                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ GCP Budget  │───▶│   Pub/Sub   │───▶│  Cloud Function     │ │
│  │   Alerts    │    │   Topic     │    │  (Remediation)      │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│                                                    │            │
│  ┌─────────────┐    ┌─────────────┐               ▼            │
│  │ Cloud       │───▶│  BigQuery   │    ┌─────────────────────┐ │
│  │ Scheduler   │    │  (Billing   │    │  Actions:           │ │
│  │ (daily)     │    │   Export)   │    │  • Disable API      │ │
│  └─────────────┘    └──────┬──────┘    │  • Stop instance    │ │
│                            │           │  • Set quota to 0   │ │
│                            ▼           │  • Send alert       │ │
│                     ┌─────────────┐    └─────────────────────┘ │
│                     │ Cloud Func  │                            │
│                     │ (Idle Scan) │──▶ Firestore (config)      │
│                     └─────────────┘                            │
│                            │                                   │
│  ┌─────────────────────────▼───────────────────────────────────┐│
│  │ GCP Recommender API + Cloud Billing API                     ││
│  │ • Rightsizing recommendations (VM, Cloud SQL)               ││
│  │ • Idle resource insights                                    ││
│  │ • Unattached disk detection                                 ││
│  │ • Cost breakdown by service/SKU                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ LLM Wrapper (in your app code)                              ││
│  │ • Tracks spend per request                                  ││
│  │ • Enforces daily/monthly limits                             ││
│  │ • Logs to Cloud Logging for analysis                        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Budget Alert → Auto-Remediation

**Trigger:** GCP Budget Alert at configurable thresholds  
**Action:** Cloud Function disables specific services

| Threshold | Action |
|-----------|--------|
| 50% of budget | Slack/email warning |
| 80% of budget | Disable non-critical services |
| 100% of budget | Disable all optional services |

**Services to auto-disable (configurable in Firestore):**
- Cloud Run services (non-production)
- Vertex AI endpoints
- BigQuery slots (if using reservations)
- Any service tagged `{SERVICE_NAME}: auto-disable`

### 2. LLM Cost Control

**Implementation:** Python wrapper around LiteLLM

```python
class CostGuardedLLM:
    def __init__(self, daily_limit=100, monthly_limit=500):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
    
    def call(self, prompt, model="gemini-2.0-flash"):
        current_spend = self._get_spend_from_firestore()
        
        if current_spend['daily'] >= self.daily_limit:
            raise DailyLimitExceeded(f"Daily LLM limit ${self.daily_limit} reached")
        
        if current_spend['monthly'] >= self.monthly_limit:
            raise MonthlyLimitExceeded(f"Monthly LLM limit ${self.monthly_limit} reached")
        
        response = litellm.completion(model=model, messages=[{"role": "user", "content": prompt}])
        self._record_cost(response.usage, model)
        return response
```

### 3. Idle Resource Detection

**Trigger:** Cloud Scheduler (daily at 6 AM)  
**Scanner:** Cloud Function queries Cloud Monitoring API

| Resource Type | Idle Criteria |
|---------------|---------------|
| Cloud Run | 0 requests in 7 days |
| Compute Engine | CPU < 5% for 7 days |
| Cloud SQL | 0 connections in 7 days |
| BigQuery datasets | 0 queries in 30 days |
| Pub/Sub topics | 0 messages in 30 days |

### 4. GCP Recommender Integration

**Purpose:** Leverage GCP's native cost intelligence (free API)

| Recommender Type | What It Finds |
|------------------|---------------|
| `MachineTypeRecommender` | Oversized VMs |
| `IdleResourceRecommender` | Idle VMs, Cloud SQL |
| `DiskIdleRecommender` | Unattached disks |

---

## Infrastructure (All Free Tier)

| Component | Purpose | Monthly Cost |
|-----------|---------|--------------|
| Cloud Functions (3) | Remediation, idle scan, recommender | $0 |
| Pub/Sub (1 topic) | Budget alert routing | $0 |
| Firestore | Config, spend tracking | $0 |
| Cloud Scheduler (2 jobs) | Daily idle scan, weekly report | $0 |
| BigQuery | Billing export queries | $0 |
| Cloud Logging | All logs | $0 |
| Recommender API | Cost optimization | $0 |
| **Total** | | **$0-15/month** |

---

## Implementation Timeline (3-4 Days)

### Day 1: Budget Alerts + Remediation (4-6 hours)

- [ ] Create Pub/Sub topic `cost-alerts`
- [ ] Create Cloud Function `budget-remediation`
- [ ] Set up GCP Budget with Pub/Sub notification
- [ ] Create Firestore collection `{SERVICE_NAME}/config`
- [ ] Test: trigger alert, verify service disabled

### Day 2: LLM Cost Control (3-4 hours)

- [ ] Create `CostGuardedLLM` wrapper class
- [ ] Create Firestore schema for spend tracking
- [ ] Integrate into existing LLM calls
- [ ] Add Cloud Logging for all LLM calls
- [ ] Test: verify limits enforced

### Day 3: Idle Resource Detection + Recommender (4-5 hours)

- [ ] Create Cloud Function `idle-scanner`
- [ ] Query Cloud Monitoring API for usage metrics
- [ ] Integrate Recommender API
- [ ] Store results in Firestore
- [ ] Set up weekly email digest
- [ ] Test: verify idle resources detected

### Day 4 (Optional): Simple Dashboard (4-6 hours)

- [ ] Use Retool/Appsmith (free tier) or simple Next.js
- [ ] View current spend vs limits
- [ ] View idle resources
- [ ] Toggle auto-remediation on/off

---

## Configuration (Firestore Schema)

```
{SERVICE_NAME}/
├── config/
│   ├── budgets: { monthly_limit: 1000, alert_thresholds: [0.5, 0.8, 1.0] }
│   ├── llm: { daily_limit: 100, monthly_limit: 500, enabled: true }
│   └── remediation: { 
│         auto_disable: true,
│         protected_services: ["prod-api", "prod-db"],
│         auto_disable_services: ["dev-*", "staging-*"]
│       }
├── spend/
│   ├── {DATE}: { llm: 45.30, total: 123.50 }
│   └── {DATE}: { llm: 32.10, total: 98.20 }
└── idle-resources/
    └── scan-{DATE}: [
          { type: "cloud-run", name: "old-service", idle_days: 45 },
          { type: "compute", name: "test-vm", idle_days: 30 }
        ]
```

---

## What's Included vs Excluded

| Feature | ✅ Included | ❌ Excluded |
|---------|-------------|-------------|
| GCP auto-remediation | ✅ | |
| LLM cost limits | ✅ | |
| GCP idle detection | ✅ | |
| GCP Recommender | ✅ | |
| **Multi-cloud** | | ❌ (see MINIMAL-COST-GUARD.md) |
| **AI predictions** | | ❌ |
| **Full dashboard** | | ❌ |

---

## Success Criteria

- [ ] LLM spend never exceeds daily/monthly limits
- [ ] Budget alerts trigger within 1 hour of threshold
- [ ] Idle GCP resources detected weekly
- [ ] Auto-remediation prevents unexpected spikes
- [ ] Total infrastructure cost < $15/month

---

## When to Use This vs Full MVP

| Scenario | Use This | Use Full MVP |
|----------|----------|--------------|
| GCP-only infrastructure | ✅ | |
| Need it in 3-4 days | ✅ | |
| $0/month budget | ✅ | |
| Multi-cloud monitoring | | ✅ |
| AI predictions needed | | ✅ |
| MCP agent architecture | | ✅ |

---

## Next Steps

1. **Use this for GCP-only** → 3-4 days, $0-15/month
2. **Or use Full MVP** → 15-20 days, $13-40/month, more features

See [MINIMAL-COST-GUARD.md](MINIMAL-COST-GUARD.md) for multi-cloud version.
