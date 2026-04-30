---
title: "MVP Pipeline End-to-End User Guide"
tags:
  - autopilot
  - workflow-guide
  - ai-agent-primary
custom_fields:
  document_type: "workflow-guide"
  status: "active"
---

# End-to-End Pipeline User Guide: PRD → Deployed Code

**Scenario**: You have a PRD document and want to get to deployed code  
**Tools**: MVP Autopilot + Vertex AI + GitHub Actions  
**Time**: 2 hours (automated) + 30 min (reviews)  

---

## Overview: Your Journey

```
You Write PRD → Autopilot Generates Docs → Vertex AI Generates Code → Deploy to Cloud Run
     1 hour              Automated (1 hour)        Automated (15 min)      Automated (5 min)
```

**Your Effort**: 1 hour (write PRD) + 30 min (reviews)  
**Automation**: Everything else  

---

## Step-by-Step Walkthrough

### Step 1: Create Your PRD Document (Manual - 1 hour)

**What you do**: Write your product requirements

**Location**: `ucx_flow_v3/02_PRD/PRD-01_trading_bot.md`

**Example PRD**:
```markdown
---
title: "PRD-01: Crypto Trading Bot"
tags:
  - prd
  - layer-2-artifact
---

# PRD-01: Crypto Trading Bot

## 1. Executive Summary

A crypto trading bot that executes trades based on moving average crossover strategy.

## 2. Product Vision

Enable automated trading with minimal user intervention.

## 3. Functional Requirements

- FR-001: Monitor BTC/USD price every 5 seconds
- FR-002: Calculate 20-period and 50-period moving averages
- FR-003: Execute buy when fast MA crosses above slow MA
- FR-004: Execute sell when fast MA crosses below slow MA
- FR-005: Enforce risk limits (max 2% position size)

## 4. Non-Functional Requirements

- Performance: 100ms latency for order execution
- Availability: 99.9% uptime
- Security: API keys encrypted at rest
```

**Commit to GitHub**:
```bash
git add ucx_flow_v3/02_PRD/PRD-01_trading_bot.md
git commit -m "docs: Add PRD for trading bot"
git push origin main
```

---

### Step 2: Trigger Autopilot Pipeline (Automated - 1 hour)

**What happens**: GitHub Actions detects PRD, generates all downstream docs

#### Option A: GitHub UI (Easiest)

1. Go to **Actions** tab in GitHub
2. Click **"MVP Autopilot - Full Pipeline"**
3. Click **"Run workflow"**
4. Fill in form:
   ```
   Entry Point: PRD
   Exit Point: SPEC
   Slug: trading_bot
   Profile: mvp
   ```
5. Click **"Run workflow"**

#### Option B: Command Line

```bash
# Trigger via GitHub CLI
gh workflow run mvp-autopilot.yml \
  --field from_layer=PRD \
  --field up_to=SPEC \
  --field slug=trading_bot \
  --field profile=mvp
```

#### Option C: Local Execution (For Testing)

```bash
# Run locally first to test
python3 ucx_flow_v3/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ucx_flow_v3 \
  --from-layer PRD \
  --up-to SPEC \
  --slug trading_bot \
  --mode brownfield \
  --auto-fix \
  --report markdown
```

---

### Step 3: Watch Autopilot Generate Documents (Automated)

**GitHub Actions runs these layers automatically**:

#### Layer 3: EARS Generation (5 min)

**What it does**: Converts PRD requirements to EARS format

**Generated**: `ucx_flow_v3/03_EARS/EARS-01_trading_bot.md`

**Example output**:
```markdown
#### EARS.01.01.01: Market Data Monitoring

WHEN the system is active, THE system SHALL monitor BTC/USD price every 5 seconds.

@prd: PRD.01.03.01
```

**Quality Score**: 92% → [PASS] Auto-approved

---

#### Layer 4: BDD Test Scenarios (5 min)

**What it does**: Creates behavior-driven test scenarios

**Generated**: `ucx_flow_v3/04_BDD/BDD-01_trading_bot.feature`

**Example output**:
```gherkin
@brd: BRD.01.01.01 @prd: PRD.01.03.01 @ears: EARS.01.01.01

Feature: BDD-01 — Trading Bot

Scenario: Execute buy on MA crossover
  Given BTC price is tracked
  And 20-MA is below 50-MA
  When 20-MA crosses above 50-MA
  Then system SHALL execute buy order
  And position size SHALL be ≤2% of capital
```

**Quality Score**: 94% → [PASS] Auto-approved

---

#### Layer 5: ADR Architecture Decisions (10 min)

**What it does**: Documents technical architecture choices

**Generated**: `ucx_flow_v3/05_ADR/ADR-01_trading_bot.md`

**Example output**:
```markdown
## Decision: Use FastAPI + ib-async

**Context**: Need low-latency order execution

**Options**:
1. Django (too heavy)
2. Flask (no async)
3. **FastAPI** (async, fast)

**Decision**: FastAPI + ib-async for Interactive Brokers integration

**Consequences**: 
- Pro: <100ms latency
- Pro: Native async
- Con: Requires Python 3.11+
```

**Quality Score**: 88% → [WARN] **Manual Review Required**

**What you do**:
1. GitHub creates comment on PR: "ADR requires review (score: 88%)"
2. You review ADR document
3. Click **"Approve"** button in GitHub PR

---

#### Layer 6: SYS System Requirements (10 min)

**Generated**: `ucx_flow_v3/06_SYS/SYS-01_trading_bot.md`

**Includes**: All 15 required sections (scope, interfaces, data, testing, etc.)

**Quality Score**: 91% → [PASS] Auto-approved

---

#### Layer 7: REQ Atomic Requirements (15 min)

**What it does**: Breaks SYS into atomic requirements

**Generated**: 12 requirement files
```
ucx_flow_v3/07_REQ/
 REQ-01_market_data.md
 REQ-02_ma_calculation.md
 REQ-03_signal_detection.md
 REQ-04_order_execution.md
 REQ-05_risk_management.md
 REQ-06_position_tracking.md
 REQ-07_logging.md
 REQ-08_error_handling.md
 REQ-09_api_authentication.md
 REQ-10_data_persistence.md
 REQ-11_monitoring.md
 REQ-12_configuration.md
```

**Quality Score**: 90% average → [PASS] Auto-approved

---

#### Layer 8: CTR API Contracts (10 min)

**What it does**: Defines API contracts (OpenAPI format)

**Generated**: `ucx_flow_v3/08_CTR/CTR-01_trading_bot.yaml`

**Example**:
```yaml
openapi: 3.0.0
info:
  title: Trading Bot API
  version: 1.0.0

paths:
  /api/v1/trades:
    post:
      summary: Execute trade
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                symbol:
                  type: string
                  example: "BTC-USD"
                side:
                  type: string
                  enum: [buy, sell]
                quantity:
                  type: number
      responses:
        200:
          description: Trade executed
```

**Quality Score**: 93% → [PASS] Auto-approved

---

#### Layer 9: SPEC Technical Specification (15 min)

**What it does**: Complete technical specification in YAML

**Generated**: `ucx_flow_v3/09_SPEC/SPEC-01_trading_bot.yaml`

**Example**:
```yaml
id: SPEC-01
summary: Crypto Trading Bot - Technical Specification

architecture:
  components:
    - market_data_service
    - signal_generator
    - order_executor
    - risk_manager
  
  tech_stack:
    language: Python 3.11
    framework: FastAPI
    broker_api: ib-async
    database: PostgreSQL 16

interfaces:
  rest_api:
    - endpoint: /api/v1/trades
      method: POST
      auth: Bearer token
  
  websocket:
    - endpoint: /ws/market-data
      protocol: WSS

behavior:
  trading_logic:
    ma_fast: 20
    ma_slow: 50
    execution_delay_ms: 50
  
  risk_rules:
    max_position_pct: 2.0
    max_daily_loss_pct: 5.0

performance:
  order_latency_ms: 100
  throughput_tps: 50

traceability:
  brd: BRD.01.01.01
  prd: PRD.01.03.01
  req: REQ.01, REQ.02, REQ.03, REQ.04, REQ.05
```

**Quality Score**: 95% → [PASS] Auto-approved

**Autopilot Complete!** All documents generated in ~1 hour.

---

### Step 4: Review Generated Documents (Manual - 15 min)

**GitHub creates a Pull Request** with all generated files.

**What you do**:

1. **Open PR**: Click link in GitHub Actions notification
2. **Review Files Changed**: Check tabs for each layer
3. **Verify Traceability**: Links between layers correct?
4. **Approve**: Click "Approve" button

**PR will show**:
```
[PASS] Quality Gate: 92% (threshold: 90%)
[PASS] All validations passed
[PASS] Traceability verified
[WARN] 1 manual review pending (ADR)
```

---

### Step 5: Generate Code with Vertex AI (Automated - 15 min)

**Triggered automatically** after PR approval or manually via GitHub Actions.

#### What Happens Behind the Scenes:

**GitHub Action runs**:
```yaml
- name: Generate Code with Vertex AI
  run: |
    python3 ucx_flow_v3/scripts/vertex_code_generator.py \
      --spec ucx_flow_v3/09_SPEC/SPEC-01_trading_bot.yaml \
      --contracts ucx_flow_v3/08_CTR/ \
      --model claude-3.7-sonnet \
      --output src/ \
      --project ${{ secrets.GCP_PROJECT_ID }} \
      --location us-central1
```

**Vertex AI processes**:
1. Loads SPEC-01_trading_bot.yaml
2. Loads all CTR contract files
3. Creates comprehensive prompt
4. Calls Claude 3.7 Sonnet (best for code)
5. Generates production code

**Generated Files**:
```
src/
 trading_bot/
    __init__.py
    main.py                    # FastAPI app
    services/
       market_data.py         # Market data service
       signal_generator.py    # MA crossover logic
       order_executor.py      # Order execution
       risk_manager.py        # Risk limits
    models/
       trade.py               # Pydantic models
       order.py
    api/
       routes.py              # API endpoints
       websocket.py           # WebSocket handler
    config.py                  # Configuration
 tests/
     unit/
        test_signal_generator.py
        test_risk_manager.py
        test_order_executor.py
     integration/
         test_trading_flow.py
```

**Example Generated Code** (src/services/signal_generator.py):
```python
"""
Signal Generator Service
Implements MA crossover strategy per SPEC-01

@spec: SPEC-01
@req: REQ.03.01.01
"""

from typing import List, Optional
import pandas as pd
from pydantic import BaseModel, Field

class SignalGenerator:
    """Generate trading signals based on MA crossover strategy."""
    
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        """
        Initialize signal generator.
        
        Args:
            fast_period: Fast MA period (default: 20 per SPEC)
            slow_period: Slow MA period (default: 50 per SPEC)
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def calculate_ma(self, prices: List[float], period: int) -> float:
        """Calculate simple moving average."""
        if len(prices) < period:
            return 0.0
        return sum(prices[-period:]) / period
    
    def generate_signal(self, prices: List[float]) -> Optional[str]:
        """
        Generate buy/sell signal based on MA crossover.
        
        Returns:
            'buy' if fast MA crosses above slow MA
            'sell' if fast MA crosses below slow MA
            None if no signal
        
        Per SPEC-01: behavior.trading_logic
        """
        if len(prices) < self.slow_period:
            return None
        
        fast_ma = self.calculate_ma(prices, self.fast_period)
        slow_ma = self.calculate_ma(prices, self.slow_period)
        
        # Check previous values for crossover
        prev_fast = self.calculate_ma(prices[:-1], self.fast_period)
        prev_slow = self.calculate_ma(prices[:-1], self.slow_period)
        
        # Buy signal: fast crosses above slow
        if prev_fast <= prev_slow and fast_ma > slow_ma:
            return 'buy'
        
        # Sell signal: fast crosses below slow
        if prev_fast >= prev_slow and fast_ma < slow_ma:
            return 'sell'
        
        return None
```

**Code Generation Report**:
```
[PASS] Generated 8 source files
[PASS] Generated 6 test files
[PASS] Contract compliance: 98%
[PASS] Test coverage: 85%
[PASS] All type hints present
[PASS] All docstrings present
```

---

### Step 6: Validate Generated Code (Automated - 5 min)

**GitHub Actions automatically runs**:

```yaml
- name: Validate Generated Code
  run: |
    # Syntax check
    python -m py_compile src/**/*.py
    
    # Type checking
    mypy src/ --strict
    
    # Contract compliance
    python3 ucx_flow_v3/scripts/check_contract_compliance.py \
      --code src/ \
      --contracts ucx_flow_v3/08_CTR/ \
      --min-score 95
    
    # Security scan
    bandit -r src/ -f json
```

**Validation Results**:
```
[PASS] Syntax: All files valid
[PASS] Type hints: 100% coverage
[PASS] Contract compliance: 98% (threshold: 95%)
[PASS] Security: No high/critical issues
```

---

### Step 7: Run Tests (Automated - 5 min)

**Vertex AI also generated tests!**

```yaml
- name: Run Tests
  run: |
    pytest src/tests/ \
      -v \
      --cov=src \
      --cov-report=json \
      --cov-report=html
```

**Test Results**:
```
=================== test session starts ===================
src/tests/unit/test_signal_generator.py ......    [ 40%]
src/tests/unit/test_risk_manager.py .......      [ 75%]
src/tests/integration/test_trading_flow.py ...   [100%]

---------- coverage: 85% ----------
```

**If tests fail**:
- Vertex AI auto-fixes (max 3 retries)
- Each retry improves based on error messages

---

### Step 8: Create Pull Request for Code (Automated)

**GitHub Actions creates PR**:

**Title**: `feat: Generate trading bot code from SPEC-01`

**Body**:
```markdown
## Code Generation Report

**Model**: claude-3.7-sonnet (Vertex AI)
**SPEC**: SPEC-01_trading_bot.yaml
**Generation Time**: 47 seconds

### Generated Files
- [PASS] 8 source files (src/trading_bot/)
- [PASS] 6 test files (tests/)
- [PASS] 1 Dockerfile
- [PASS] 1 Cloud Run config

### Quality Metrics
- **Contract Compliance**: 98%
- **Test Coverage**: 85%
- **Type Coverage**: 100%
- **Security Score**: A

### Validation
- [PASS] All tests passing (16/16)
- [PASS] Security scan clean
- [PASS] Type checking passed
- [PASS] Contract compliance verified

Ready for review and merge.
```

---

### Step 9: Review and Merge Code (Manual - 10 min)

**What you do**:

1. **Review Code**: Check generated files in PR
2. **Verify Logic**: Does it match your PRD intent?
3. **Check Tests**: Are test scenarios comprehensive?
4. **Approve**: Click "Approve and Merge"

**Tips for Review**:
- [PASS] Focus on business logic correctness
- [PASS] Verify MA periods (20, 50) match PRD
- [PASS] Check risk limits (2%) implemented
- ⏭  Skip coding style (already validated)

---

### Step 10: Deploy to Cloud Run (Automated - 5 min)

**Triggered automatically** on merge to main.

```yaml
- name: Deploy to Cloud Run
  run: |
    gcloud run deploy trading-bot \
      --source . \
      --region us-central1 \
      --platform managed \
      --allow-unauthenticated \
      --set-env-vars="ENV=production" \
      --service-account=trading-bot@$PROJECT.iam.gserviceaccount.com
```

**Deployment Output**:
```
[PASS] Building source using Buildpacks
[PASS] Creating revision trading-bot-00001
[PASS] Routing traffic to revision
[PASS] Service deployed

URL: https://trading-bot-xyz123.a.run.app
```

---

## Complete Timeline

| Step | Layer | Task | Time | Automated? |
|------|-------|------|------|------------|
| 1 | L2 | Write PRD | 1h | [FAIL] Manual |
| 2 | - | Trigger pipeline | 1m | [PASS] GitHub UI |
| 3a | L3 | Generate EARS | 5m | [PASS] Autopilot |
| 3b | L4 | Generate BDD | 5m | [PASS] Autopilot |
| 3c | L5 | Generate ADR | 10m | [PASS] Autopilot |
| 3d | L6 | Generate SYS | 10m | [PASS] Autopilot |
| 3e | L7 | Generate REQ | 15m | [PASS] Autopilot |
| 3f | L8 | Generate CTR | 10m | [PASS] Autopilot |
| 3g | L9 | Generate SPEC | 15m | [PASS] Autopilot |
| 4 | - | Review PR | 15m | [FAIL] Manual |
| 5 | L11 | Generate code | 15m | [PASS] Vertex AI |
| 6 | L12 | Validate code | 5m | [PASS] GitHub Actions |
| 7 | L12 | Run tests | 5m | [PASS] GitHub Actions |
| 8 | - | Create code PR | 1m | [PASS] GitHub Actions |
| 9 | - | Review code | 10m | [FAIL] Manual |
| 10 | L13 | Deploy Cloud Run | 5m | [PASS] GitHub Actions |

**Total Time**: 2h 12m  
**Your Effort**: 1h 26m (PRD + 2 reviews)  
**Automated**: 46m (all generation + deployment)  

---

## What You Get

### Documentation
- [PASS] Complete traceability (PRD → SPEC)
- [PASS] 12 atomic requirements
- [PASS] API contracts (OpenAPI)
- [PASS] Test scenarios (BDD)
- [PASS] Architecture decisions

### Code
- [PASS] Production-ready Python code
- [PASS] 100% type hints
- [PASS] Comprehensive docstrings
- [PASS] 85%+ test coverage
- [PASS] Contract-compliant APIs

### Deployment
- [PASS] Deployed to Cloud Run
- [PASS] Public URL
- [PASS] Auto-scaling
- [PASS] Monitoring enabled

---

## Cost Breakdown

### Vertex AI Usage
- **SPEC → Code**: ~4000 tokens input, ~15000 tokens output
- **Model**: Claude 3.7 Sonnet
- **Cost**: $3/1M input + $15/1M output = **$0.24 per generation**

### GitHub Actions
- **Minutes used**: ~15 minutes per pipeline
- **Cost**: Free (2000 min/month included)

### Cloud Run
- **Free tier**: 2M requests/month
- **Cost**: $0 for MVP testing

**Total per MVP**: **~$0.25** 

---

## Troubleshooting

### "Quality score below threshold"
**Problem**: Layer scored <90%  
**Solution**: Review and approve manually, or re-run with `--auto-fix`

### "Contract compliance failed"
**Problem**: Generated code doesn't match CTR  
**Solution**: Vertex AI auto-retries with error context (max 3x)

### "Tests failed"
**Problem**: Generated tests failing  
**Solution**: Auto-retry OR manual fix + re-trigger

### "Deployment failed"
**Problem**: Cloud Run deployment error  
**Solution**: Check logs with `gcloud run logs read trading-bot`

---

## Next Steps

1. **Try it**: Create a simple PRD
2. **Trigger**: Run workflow from GitHub UI
3. **Watch**: Monitor Actions tab
4. **Review**: Approve generated docs
5. **Deploy**: Merge and deploy!

**Questions? Issues?** Check GitHub Actions logs or framework docs.

---

## Summary

**You write PRD (1 hour)**  
↓  
**Autopilot generates docs (automated, 1 hour)**  
↓  
**Vertex AI generates code (automated, 15 min)**  
↓  
**Tests run (automated, 5 min)**  
↓  
**Deploy to Cloud Run (automated, 5 min)**  
↓  
** Live application in <2 hours!**
