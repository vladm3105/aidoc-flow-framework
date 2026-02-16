# AWS-Only Cost Guard — Implementation Description

**Purpose:** Automated cost protection for AWS-only deployments  
**Scope:** AWS budget alerts, LLM cost control, idle resource detection, auto-remediation  
**Effort:** 3-4 days  
**Monthly Cost:** $0-15 (mostly free tier)

---

## Problem Statement

| Issue | Impact | Solution |
|-------|--------|----------|
| Bedrock/SageMaker billing spike | Unexpected costs | Auto-disable at threshold |
| Idle AWS services ($50-100/mo) | Ongoing waste | Detect and alert/disable |
| Manual monitoring required | Time waste | Automated remediation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS-ONLY COST GUARD                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ AWS Budget  │───▶│     SNS     │───▶│     Lambda          │ │
│  │   Alerts    │    │   Topic     │    │  (Remediation)      │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│                                                    │            │
│  ┌─────────────┐    ┌─────────────┐               ▼            │
│  │ EventBridge │───▶│ Cost        │    ┌─────────────────────┐ │
│  │ Scheduler   │    │ Explorer    │    │  Actions:           │ │
│  │ (daily)     │    │             │    │  • Stop EC2         │ │
│  └─────────────┘    └──────┬──────┘    │  • Disable endpoint │ │
│                            │           │  • Scale to 0       │ │
│                            ▼           │  • Send alert       │ │
│                     ┌─────────────┐    └─────────────────────┘ │
│                     │   Lambda    │                            │
│                     │ (Idle Scan) │──▶ DynamoDB (config)       │
│                     └─────────────┘                            │
│                            │                                   │
│  ┌─────────────────────────▼───────────────────────────────────┐│
│  │ AWS Trusted Advisor + Cost Explorer API                     ││
│  │ • Rightsizing recommendations (EC2, RDS)                    ││
│  │ • Idle resource insights                                    ││
│  │ • Reserved Instance utilization                             ││
│  │ • Cost breakdown by service/tag                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ LLM Wrapper (in your app code)                              ││
│  │ • Tracks Bedrock spend per request                          ││
│  │ • Enforces daily/monthly limits                             ││
│  │ • Logs to CloudWatch                                        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Budget Alert → Auto-Remediation

**Trigger:** AWS Budgets with SNS notification  
**Action:** Lambda function disables specific services

| Threshold | Action |
|-----------|--------|
| 50% of budget | Slack/email warning |
| 80% of budget | Disable non-critical services |
| 100% of budget | Disable all optional services |

**Services to auto-disable (configurable in DynamoDB):**
- Lambda functions (non-production)
- Bedrock endpoints
- SageMaker endpoints
- ECS tasks (dev/staging)
- Any resource tagged `{SERVICE_NAME}: auto-disable`

### 2. LLM Cost Control (AWS Bedrock)

**Implementation:** Python wrapper for Bedrock

```python
import boto3
from decimal import Decimal

class CostGuardedBedrock:
    def __init__(self, daily_limit=100, monthly_limit=500):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.bedrock = boto3.client('bedrock-runtime')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('{SERVICE_NAME}-spend')
    
    def invoke(self, prompt, model_id="anthropic.claude-3-sonnet"):
        current_spend = self._get_spend_from_dynamodb()
        
        if current_spend['daily'] >= self.daily_limit:
            raise DailyLimitExceeded(f"Daily limit ${self.daily_limit} reached")
        
        if current_spend['monthly'] >= self.monthly_limit:
            raise MonthlyLimitExceeded(f"Monthly limit ${self.monthly_limit} reached")
        
        response = self.bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({"prompt": prompt})
        )
        self._record_cost(response, model_id)
        return response
```

### 3. Idle Resource Detection

**Trigger:** EventBridge Scheduler (daily)  
**Scanner:** Lambda function queries CloudWatch metrics

| Resource Type | Idle Criteria |
|---------------|---------------|
| Lambda | 0 invocations in 7 days |
| EC2 | CPU < 5% for 7 days |
| RDS | 0 connections in 7 days |
| S3 | 0 requests in 30 days |
| SQS | 0 messages in 30 days |

### 4. AWS Trusted Advisor Integration

**Purpose:** Leverage AWS's native cost recommendations

| Check Category | What It Finds |
|----------------|---------------|
| Cost Optimization | Idle EC2, RDS, EBS volumes |
| Performance | Over/under-provisioned resources |
| Security | Unused IAM credentials |

> **Note:** Full Trusted Advisor requires Business/Enterprise Support plan. Basic checks are free.

---

## Infrastructure (Mostly Free Tier)

| Component | Purpose | Monthly Cost |
|-----------|---------|--------------|
| Lambda (3) | Remediation, idle scan, advisor | $0 (1M free) |
| SNS (1 topic) | Budget alert routing | $0 |
| DynamoDB | Config, spend tracking | $0 (on-demand, minimal) |
| EventBridge | Scheduler | $0 |
| CloudWatch | Metrics, logs | $0-5 |
| Cost Explorer API | Budget + cost data | $0.01/request |
| **Total** | | **$0-15/month** |

---

## Implementation Timeline (3-4 Days)

### Day 1: Budget Alerts + Remediation (4-6 hours)

- [ ] Create SNS topic `cost-alerts`
- [ ] Create Lambda function `budget-remediation`
- [ ] Set up AWS Budget with SNS notification
- [ ] Create DynamoDB table `{SERVICE_NAME}`
- [ ] Test: trigger alert, verify resource stopped

### Day 2: LLM Cost Control (3-4 hours)

- [ ] Create `CostGuardedBedrock` wrapper class
- [ ] Create DynamoDB schema for spend tracking
- [ ] Integrate into existing Bedrock calls
- [ ] Add CloudWatch logging
- [ ] Test: verify limits enforced

### Day 3: Idle Resource Detection + Trusted Advisor (4-5 hours)

- [ ] Create Lambda function `idle-scanner`
- [ ] Query CloudWatch for usage metrics
- [ ] Integrate Trusted Advisor API (if available)
- [ ] Store results in DynamoDB
- [ ] Set up weekly email via SES
- [ ] Test: verify idle resources detected

### Day 4 (Optional): Simple Dashboard (4-6 hours)

- [ ] Use QuickSight (pay-per-session) or simple React app
- [ ] View current spend vs limits
- [ ] View recommendations
- [ ] Toggle auto-remediation on/off

---

## Success Criteria

- [ ] Bedrock spend never exceeds daily/monthly limits
- [ ] Budget alerts trigger within 1 hour of threshold
- [ ] Idle AWS resources detected weekly
- [ ] Auto-remediation prevents unexpected spikes
- [ ] Total infrastructure cost < $15/month

---

## Next Steps

1. **Use this for AWS-only** → 3-4 days, $0-15/month
2. **Or use Full MVP** → 15-20 days, $13-40/month, more features

See [GCP-COST-GUARD.md](GCP-COST-GUARD.md) for GCP version.  
See [AZURE-COST-GUARD.md](AZURE-COST-GUARD.md) for Azure version.  
See [MINIMAL-COST-GUARD.md](MINIMAL-COST-GUARD.md) for multi-cloud version.
