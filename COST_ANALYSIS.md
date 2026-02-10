# Trading Nexus - Realistic Cost Analysis

## Executive Summary

**Previous Estimate: $95-162/month** ❌ Too optimistic

**Realistic Estimate: $250-450/month** ✓ Based on actual usage patterns

---

## 1. LLM API Costs (THE BIGGEST COST)

### Current Pricing (Jan 2026)

| Model | Input/MTok | Output/MTok |
|-------|------------|-------------|
| Claude Sonnet 4.5 | $3.00 | $15.00 |
| Claude Opus 4.5 | $5.00 | $25.00 |
| GPT-4o | $5.00 | $15.00 |
| Gemini 2.0 Flash | $0.075 | $0.30 |
| DeepSeek V3 | $0.27 | $1.10 |

### Usage Pattern Analysis

#### Per Earnings Analysis (5 Voting Agents + Consensus)

```
Each Voting Agent:
├── System prompt: ~800 tokens
├── Context/data: ~2,500 tokens  
├── Output: ~1,200 tokens
└── Subtotal: ~4,500 tokens per agent

5 Agents × 4,500 = 22,500 tokens
+ Consensus Agent: ~5,000 tokens
+ Tool calls overhead: ~3,000 tokens
────────────────────────────────────
Total per analysis: ~30,000 tokens
```

#### Monthly Token Usage (Active Trading)

| Activity | Frequency | Tokens/Event | Monthly Tokens |
|----------|-----------|--------------|----------------|
| Earnings Analysis | 3/day × 21 days | 30K | 1.9M |
| Position Monitoring | 4/hour × 6.5h × 21 days | 2K | 1.1M |
| Market Intel Queries | 5/day × 21 days | 5K | 0.5M |
| Order Management | 10/day × 21 days | 3K | 0.6M |
| Research Sessions | 10/month | 50K | 0.5M |
| Re-runs/Debugging | 20% overhead | - | 0.9M |
| **TOTAL** | | | **5.5M tokens** |

#### Cost Calculation (Mixed Model Strategy)

```
Token Distribution:
├── Complex Analysis (Sonnet): 40% = 2.2M tokens
├── Fast Queries (Gemini): 30% = 1.65M tokens  
├── Bulk Processing (DeepSeek): 30% = 1.65M tokens

Monthly LLM Cost:
├── Sonnet (60% input/40% output):
│   ├── Input: 1.32M × $3/MTok = $3.96
│   └── Output: 0.88M × $15/MTok = $13.20
│   └── Subtotal: $17.16
│
├── Gemini 2.0 Flash:
│   ├── Input: 0.99M × $0.075/MTok = $0.07
│   └── Output: 0.66M × $0.30/MTok = $0.20
│   └── Subtotal: $0.27
│
├── DeepSeek V3:
│   ├── Input: 0.99M × $0.27/MTok = $0.27
│   └── Output: 0.66M × $1.10/MTok = $0.73
│   └── Subtotal: $1.00
│
└── TOTAL: ~$18/month (optimistic mixed model)
```

### BUT - Reality Check ⚠️

The above assumes perfect model routing. In practice:

1. **Debugging/iteration**: 2-3x token usage during development
2. **Long context**: Analyses often need 10-20K context
3. **Tool use overhead**: Each MCP tool call adds tokens
4. **Thinking tokens** (Claude 4.1+): Charged separately for tool use

**Realistic LLM Range**: **$50-150/month**

If primarily using Claude Sonnet for quality: **$80-150/month**

---

## 2. Cloud Run Costs

### The "Scale to Zero" Myth

Cloud Run scales to zero... but trading systems need:
- **IB Gateway connection**: Must stay alive during market hours
- **Position monitoring**: Continuous loops
- **Webhook endpoints**: Ready for alerts

### Actual Requirements

#### Always-On IB MCP Server

```
Market hours: 9:30 AM - 4:00 PM ET = 6.5 hours
Pre/post market monitoring: +3 hours
Total: ~10 hours/day × 21 trading days = 210 hours/month

BUT - IB Gateway needs warm connection, so realistically:
24 hours × 30 days = 720 hours (always-on)

Cost for 1 vCPU + 1GB RAM always-on:
├── CPU: 720h × 3600s × $0.000024/vCPU-s = $62.21
├── RAM: 720h × 3600s × 1GB × $0.0000025/GB-s = $6.48
└── Total: ~$69/month for IB server alone
```

#### Other Services (Request-Based)

| Service | Min Instances | Estimated Cost |
|---------|---------------|----------------|
| Agent Orchestrator | 0 (scale to zero) | $5-15 |
| Browser MCP | 0 | $3-8 |
| Webhook Handler | 1 (low latency) | $15-25 |
| **Subtotal** | | **$23-48** |

### Cloud Run Total: **$85-120/month**

---

## 3. Database Costs

### Firestore

| Operation | Volume/Month | Rate | Cost |
|-----------|--------------|------|------|
| Reads | 500K | $0.06/100K | $3.00 |
| Writes | 100K | $0.18/100K | $1.80 |
| Storage | 5 GB | $0.18/GB | $0.90 |
| **Total** | | | **$5-10** |

### BigQuery

| Item | Volume | Rate | Cost |
|------|--------|------|------|
| Query Processing | 50 GB/month | $5/TB | $0.25 |
| Storage | 10 GB | $0.02/GB | $0.20 |
| **Total** | | | **$1-5** |

### Neo4j (Graph RAG)

| Option | Cost |
|--------|------|
| Aura Free | $0 (200K nodes limit) |
| Aura Professional | $65+/month |
| Self-hosted on Compute Engine | $25-40/month |

**Recommended**: Start with Aura Free, budget **$0-65/month**

### Database Total: **$10-80/month**

---

## 4. Third-Party Data Services

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Polygon.io | Free / Starter | $0-29 |
| Financial Datasets MCP | Usage-based | $10-30 |
| Octagon (Transcripts) | Usage-based | $10-25 |
| Alpha Vantage | Free / Premium | $0-50 |
| **Total** | | **$20-135** |

---

## 5. Other GCP Services

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Cloud Scheduler | 10 jobs | $1-3 |
| Secret Manager | 20 secrets | $1-2 |
| Cloud Logging | 10 GB | $5-15 |
| Cloud Monitoring | Basic | $0-10 |
| Network Egress | 20 GB | $2-5 |
| Artifact Registry | 5 GB | $0-2 |
| **Total** | | **$10-35** |

---

## 6. Interactive Brokers

| Item | Cost |
|------|------|
| Account Minimum | $0 (no minimum) |
| Market Data (US Stocks) | $0 (included with trading) |
| Real-time Options | $0-15/month |
| Level 2 Data | $0-25/month |
| **Total** | **$0-40** |

---

## Cost Summary

### Minimum Viable (Constrained)

| Category | Monthly Cost |
|----------|-------------|
| LLM APIs (mostly cheap models) | $50 |
| Cloud Run (minimal always-on) | $85 |
| Databases (free tiers) | $10 |
| Data Services (free tiers) | $20 |
| GCP Services | $10 |
| IB Data | $0 |
| **TOTAL** | **$175** |

### Realistic Active Trading

| Category | Monthly Cost |
|----------|-------------|
| LLM APIs (quality models) | $100 |
| Cloud Run | $100 |
| Databases (Neo4j Pro) | $75 |
| Data Services | $60 |
| GCP Services | $25 |
| IB Data | $15 |
| **TOTAL** | **$375** |

### Full Production

| Category | Monthly Cost |
|----------|-------------|
| LLM APIs (high volume) | $150 |
| Cloud Run (redundancy) | $120 |
| Databases (scaled) | $80 |
| Data Services (premium) | $100 |
| GCP Services | $35 |
| IB Data | $40 |
| **TOTAL** | **$525** |

---

## Comparison: Previous vs Realistic

| Category | Previous Estimate | Realistic Estimate |
|----------|-------------------|-------------------|
| LLM APIs | $12-15 | $50-150 |
| Cloud Run | $20-40 | $85-120 |
| Databases | $35-70 | $10-80 |
| Data Services | $8-12 | $20-135 |
| Other GCP | $7-13 | $10-35 |
| IB | $0 | $0-40 |
| **TOTAL** | **$95-162** | **$175-525** |

**Why the difference?**

1. **LLM costs underestimated**: Didn't account for tool overhead, debugging, retries
2. **Cloud Run "scale to zero"**: Trading systems need always-on components
3. **Data services**: Quality financial data isn't free
4. **Neo4j**: Free tier is very limited for Graph RAG

---

## Cost Optimization Strategies

### 1. Model Tiering (Save 40-60%)
```
Use cheap models for:
├── Position monitoring (Gemini Flash)
├── Simple queries (DeepSeek)
├── Data formatting (Haiku)

Reserve expensive models for:
├── Final consensus (Sonnet)
├── Complex analysis (Sonnet/Opus)
```

### 2. Caching (Save 20-30%)
```
Cache repeated prompts:
├── System instructions
├── Tool definitions
├── Historical context
```

### 3. Batch Processing (Save 50%)
```
Use Anthropic Batch API for:
├── End-of-day analysis
├── Historical backtesting
├── Bulk data processing
```

### 4. Smart Scheduling (Save 15-25%)
```
Scale down Cloud Run:
├── After market hours
├── Weekends/holidays
├── Non-trading periods
```

### 5. Free Tier Maximization
```
GCP Free Tier:
├── Firestore: 50K reads/day free
├── BigQuery: 10GB/month free
├── Cloud Run: 2M requests/month free

Stay within limits for development
```

---

## Recommendation

### Phase 1: Development ($175-250/month)
- Use free tiers aggressively
- Gemini Flash for most operations
- Neo4j Aura Free
- Polygon.io free tier

### Phase 2: Paper Trading ($250-375/month)
- Add Claude Sonnet for key decisions
- Neo4j Aura Professional if needed
- Polygon Starter plan

### Phase 3: Live Trading ($375-525/month)
- Full model ensemble
- Redundant infrastructure
- Premium data feeds
- 24/7 monitoring capability

---

## Updated Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Created | 2026-01-02T00:00:00 |
| Author | Cost Analysis Review |
| Previous Estimate | $95-162/month |
| **Revised Estimate** | **$175-525/month** |
