---
title: "CTR Validation Strategy (Quick Reference)"
tags:
  - validation
  - ctr
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: CTR
  priority: high
  version: "1.0"
  scope: ctr-validation
---

# CTR Validation Strategy (Quick Reference)

**Purpose:** Quick reference for CTR validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [CTR_VALIDATION_COMMANDS.md](./CTR_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [CTR_AI_VALIDATION_DECISION_GUIDE.md](./CTR_AI_VALIDATION_DECISION_GUIDE.md) for CTR-specific decision patterns.

---

## CTR Validation Architecture

- Validation scripts live in [scripts](./scripts).
- Implemented validators:
  - [scripts/validate_ctr_quality_score.sh](scripts/validate_ctr_quality_score.sh) — quality gates (see [CTR_MVP_QUALITY_GATE_VALIDATION.md](./CTR_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_ctr.sh](scripts/validate_ctr.sh) — standard validator; run with `--help` to view supported modes.
  - [scripts/validate_ctr_spec_readiness.py](scripts/validate_ctr_spec_readiness.py) — **SPEC-readiness scorer** (new; evaluates ≥90% compliance for SPEC generation readiness).
  - [scripts/validate_ctr_ids.py](scripts/validate_ctr_ids.py) — CTR ID and naming validator.
- Quality gates enforce Pydantic model examples, type-annotated usage examples, and concrete domain data (see below).

---

## CTR Quality Gates and Rules

- Gate definitions: [CTR_MVP_QUALITY_GATE_VALIDATION.md](./CTR_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [CTR_MVP_VALIDATION_RULES.md](./CTR_MVP_VALIDATION_RULES.md)
- Creation rules: [CTR_MVP_CREATION_RULES.md](./CTR_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## SPEC-Readiness Scoring Criteria

The `validate_ctr_spec_readiness.py` validator awards 10 points per passing check (100 total):

| Check | Criterion | Notes |
|-------|-----------|-------|
| **API Spec** | Section 2-5: API Specification OR Interface Definition present | Required for all contract types |
| **Data Models** | Pydantic models OR JSON Schema examples | Type annotations required (see below) |
| **Error Handling** | Error Handling section with exception catalog table | Must list HTTP codes, retry policy, recovery steps |
| **Versioning** | Versioning section with policy and breaking changes | Semantic version, compatibility rules |
| **Testing** | Testing/Verification section documented | Contract test strategy required |
| **Endpoints/Methods** | Documented endpoints or functions | GET/POST/PUT/DELETE patterns or equivalent |
| **OpenAPI/Schema** | OpenAPI reference or inline JSON Schema | Automated tooling validation |
| **Type Annotations** | 3+ type-annotated function examples | Use Pydantic + `def fn(param: Type) -> ReturnType` patterns |
| **Error Recovery** | 2+ recovery keywords: retry, backoff, fallback, circuit breaker, timeout | Strategic resilience documented |
| **Concrete Examples** | 10+ concrete domain-specific instances | Real IDs, dates, symbols (e.g., `TSLA`, `2026-01-25T00:00:00`, `user_id: "usr_789"`) |

**Target**: ≥90 points (9/10 checks) for SPEC generation readiness.

**Pydantic Example Pattern**:
```python
from pydantic import BaseModel, Field
from typing import Literal

class OrderRequest(BaseModel):
    order_id: str = Field(..., example="ord_123")
    symbol: str = Field(..., example="TSLA")
    action: Literal["BUY", "SELL"] = "BUY"
    quantity: int = Field(..., example=10)
    limit_price: float = Field(optional=True, example=150.50)
```

**Typed Usage Example**:
```python
def validate_order(order: OrderRequest) -> bool:
    return order.quantity > 0

def route_order(order: OrderRequest, broker: str) -> str:
    return f"{broker}:{order.symbol}:{order.action}:{order.order_id}"
```

---

## Quick Usage

### Quality Gates & Structure
```bash
bash scripts/validate_ctr_quality_score.sh <directory>
bash scripts/validate_ctr.sh --help
```

### SPEC-Readiness (≥90% compliance for SPEC generation)
```bash
python scripts/validate_ctr_spec_readiness.py --directory docs/08_CTR --min-score 90
python scripts/validate_ctr_spec_readiness.py --ctr-file docs/08_CTR/CTR-01_iam.md
```

### ID Validation
```bash
python scripts/validate_ctr_ids.py --directory docs/08_CTR
```

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**CTR-Specific Docs:**
- [CTR_VALIDATION_COMMANDS.md](./CTR_VALIDATION_COMMANDS.md)
- [CTR_AI_VALIDATION_DECISION_GUIDE.md](./CTR_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)