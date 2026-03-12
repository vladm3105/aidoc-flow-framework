# UCX Weight Matrix Reference

Complete weight matrices for all supported document types.

---

## Default Weights

Base weights that apply when no document-type override is specified:

| Category | Weight | Max Deduction | Element Codes |
|----------|--------|---------------|---------------|
| functional | 25% | -25 | 01, 22, 24 |
| quality | 15% | -15 | 02, 91-99 |
| compliance | 20% | -20 | (keywords) |
| constraints | 10% | -10 | 03, 04 |
| integration | 10% | -10 | 05, 16, 20 |
| acceptance | 10% | -10 | 06, 14, 40-45 |
| risk | 5% | -5 | 07 |
| architecture | 5% | -5 | 10, 12, 13, 32 |
| **Total** | **100%** | **-100** | |

---

## Weight Matrix by Document Type

### Complete Matrix

| Category | BRD | PRD | EARS | BDD | ADR | SYS | REQ | SPEC | CTR | TASKS | TSPEC |
|----------|----:|----:|-----:|----:|----:|----:|----:|-----:|----:|------:|------:|
| functional | 25 | 30 | 35 | 20 | 10 | 30 | 40 | 25 | 15 | 30 | 25 |
| quality | 15 | 15 | 10 | 15 | 15 | 20 | 15 | 20 | 10 | 10 | 20 |
| compliance | 20 | 15 | 10 | 10 | 10 | 10 | 10 | 10 | 20 | 5 | 10 |
| constraints | 10 | 10 | 10 | 10 | 15 | 10 | 5 | 5 | 15 | 10 | 5 |
| integration | 10 | 10 | 10 | 15 | 15 | 10 | 10 | 15 | 20 | 15 | 15 |
| acceptance | 10 | 10 | 15 | 25 | 5 | 10 | 15 | 15 | 10 | 15 | 20 |
| risk | 5 | 5 | 5 | 2.5 | 15 | 5 | 2.5 | 5 | 5 | 10 | 2.5 |
| architecture | 5 | 5 | 5 | 2.5 | 15 | 5 | 2.5 | 5 | 5 | 5 | 2.5 |
| **Total** | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |

---

## Per-Document-Type Details

### BRD (Layer 1: Business Requirements)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| functional | 25% | -25 | Business feature coverage |
| quality | 15% | -15 | Quality attribute definition |
| **compliance** | **20%** | -20 | **High: Business regulatory requirements** |
| constraints | 10% | -10 | Business constraints |
| integration | 10% | -10 | Partner/external dependencies |
| acceptance | 10% | -10 | Business acceptance criteria |
| risk | 5% | -5 | Business risks |
| architecture | 5% | -5 | High-level architecture |

### PRD (Layer 2: Product Requirements)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| **functional** | **30%** | -25 | **High: Product feature focus** |
| quality | 15% | -15 | Product quality attributes |
| compliance | 15% | -20 | Product compliance (lower than BRD) |
| constraints | 10% | -10 | Product constraints |
| integration | 10% | -10 | Product integrations |
| acceptance | 10% | -10 | Product acceptance |
| risk | 5% | -5 | Product risks |
| architecture | 5% | -5 | Product architecture |

### EARS (Layer 3: Formal Requirements)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| **functional** | **35%** | -25 | **Highest: Formal requirement focus** |
| quality | 10% | -15 | Quality NFRs |
| compliance | 10% | -20 | Compliance requirements |
| constraints | 10% | -10 | Requirement constraints |
| integration | 10% | -10 | Interface requirements |
| **acceptance** | **15%** | -10 | **High: Testability focus** |
| risk | 5% | -5 | Requirement risks |
| architecture | 5% | -5 | System architecture |

### BDD (Layer 4: Behavior Scenarios)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| functional | 20% | -25 | Behavior coverage |
| quality | 15% | -15 | Quality scenarios |
| compliance | 10% | -20 | Compliance scenarios |
| constraints | 10% | -10 | Boundary conditions |
| integration | 15% | -10 | Integration scenarios |
| **acceptance** | **25%** | -10 | **Highest: Test scenario focus** |
| risk | 2.5% | -5 | Lower: Scenario-focused |
| architecture | 2.5% | -5 | Lower: Behavior-focused |

### ADR (Layer 5: Architecture Decisions)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| functional | 10% | -25 | Lower: Decision-focused |
| quality | 15% | -15 | Quality trade-offs |
| compliance | 10% | -20 | Compliance decisions |
| **constraints** | **15%** | -10 | **High: Decision context** |
| **integration** | **15%** | -10 | **High: Integration decisions** |
| acceptance | 5% | -10 | Lower: Decision-focused |
| **risk** | **15%** | -5 | **High: Decision impact** |
| **architecture** | **15%** | -5 | **Highest: Architecture focus** |

### SYS (Layer 6: System Requirements)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| **functional** | **30%** | -25 | **High: System feature focus** |
| **quality** | **20%** | -15 | **High: System NFRs** |
| compliance | 10% | -20 | System compliance |
| constraints | 10% | -10 | System constraints |
| integration | 10% | -10 | System integrations |
| acceptance | 10% | -10 | System acceptance |
| risk | 5% | -5 | System risks |
| architecture | 5% | -5 | System architecture |

### REQ (Layer 7: Atomic Requirements)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| **functional** | **40%** | -25 | **Highest: Atomic requirement focus** |
| quality | 15% | -15 | Quality requirements |
| compliance | 10% | -20 | Compliance requirements |
| constraints | 5% | -10 | Requirement constraints |
| integration | 10% | -10 | Interface requirements |
| acceptance | 15% | -10 | Testable criteria |
| risk | 2.5% | -5 | Lower: Atomic-focused |
| architecture | 2.5% | -5 | Lower: Requirement-focused |

### SPEC (Layer 9: Technical Specifications)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| functional | 25% | -25 | Spec coverage |
| **quality** | **20%** | -15 | **High: Spec quality** |
| compliance | 10% | -20 | Spec compliance |
| constraints | 5% | -10 | Spec constraints |
| **integration** | **15%** | -10 | **High: Interface specs** |
| **acceptance** | **15%** | -10 | **High: Verification** |
| risk | 5% | -5 | Implementation risks |
| architecture | 5% | -5 | Spec architecture |

### CTR (Layer 8: Data Contracts)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| functional | 15% | -25 | Contract coverage |
| quality | 10% | -15 | Contract quality |
| **compliance** | **20%** | -20 | **High: Contract compliance** |
| constraints | 15% | -10 | Contract constraints |
| **integration** | **20%** | -10 | **Highest: Contract boundaries** |
| acceptance | 10% | -10 | Contract validation |
| risk | 5% | -5 | Contract risks |
| architecture | 5% | -5 | Contract structure |

### TASKS (Layer 11: Task Breakdown)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| **functional** | **30%** | -25 | **High: Task coverage** |
| quality | 10% | -15 | Task quality |
| compliance | 5% | -20 | Lower: Implementation-focused |
| constraints | 10% | -10 | Task constraints |
| integration | 15% | -10 | Task dependencies |
| acceptance | 15% | -10 | Task completion criteria |
| **risk** | **10%** | -5 | **High: Task risks** |
| architecture | 5% | -5 | Task architecture |

### TSPEC (Layer 10: Test Specifications)

| Category | Weight | Max Deduction | Rationale |
|----------|--------|---------------|-----------|
| functional | 25% | -25 | Test coverage |
| **quality** | **20%** | -15 | **High: Test quality** |
| compliance | 10% | -20 | Test compliance |
| constraints | 5% | -10 | Test constraints |
| integration | 15% | -10 | Integration tests |
| **acceptance** | **20%** | -10 | **High: Test coverage** |
| risk | 2.5% | -5 | Lower: Test-focused |
| architecture | 2.5% | -5 | Lower: Test-focused |

---

## Weight Validation

Weights must sum to exactly 100% for each document type. The UCX weight loader validates this on config load:

```python
from ucx.scoring import load_weights, ScoringConfigError

try:
    weights = load_weights("brd")
except ScoringConfigError as e:
    print(f"Invalid weights: {e}")
```

### Validation Rules

1. Sum of all category weights must equal 1.0 (100%)
2. Each weight must be between 0.0 and 1.0
3. Document type must be known or falls back to BRD defaults

---

## Max Deduction Caps

Default max deductions per category:

| Category | Max Deduction | Rationale |
|----------|---------------|-----------|
| functional | 25 | Largest impact category |
| quality | 15 | Moderate impact |
| compliance | 20 | High impact (regulatory) |
| constraints | 10 | Limited impact |
| integration | 10 | Limited impact |
| acceptance | 10 | Limited impact |
| risk | 5 | Smallest scope |
| architecture | 5 | Smallest scope |

Caps can be customized per project but should remain proportional to weights.

---

*Version: 1.12.0 | Created: 2026-03-12*
