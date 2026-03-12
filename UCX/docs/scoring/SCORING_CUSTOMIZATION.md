# UCX Scoring Customization

Guide to customizing category-weighted scoring for your project.

---

## Overview

UCX scoring is configurable at multiple levels:

| Level | Location | Scope |
|-------|----------|-------|
| Framework defaults | `ucx/config/scoring_weights.yaml` | All UCX users |
| Industry template | `docs/scoring/templates/*.yaml` | Industry-specific |
| Project config | `docs/UCX/scoring_weights.yaml` | Single project |

---

## Project Configuration

### Creating Project Config

Create `docs/UCX/scoring_weights.yaml` in your project:

```yaml
# docs/UCX/scoring_weights.yaml

# Extend an industry template (optional)
extends: fintech_compliance

# Override document-type weights
document_types:
  brd:
    categories:
      functional:
        weight: 0.30  # Higher for feature-heavy BRD
      compliance:
        weight: 0.15  # Lower to balance

# Add project-specific keywords
defaults:
  categories:
    compliance:
      keywords_append:
        - "BridgeCustody"
        - "NoahWallet"
        - "B-LocalTransfer"
```

### Validation

Validate your config before use:

```bash
ucx scoring validate docs/UCX/scoring_weights.yaml
```

---

## Weight Customization

### Adjusting Category Weights

When increasing one weight, decrease another to maintain 100% total:

```yaml
# Focus on functional requirements (product-heavy project)
document_types:
  brd:
    categories:
      functional:
        weight: 0.35  # +0.10 from default 0.25
      compliance:
        weight: 0.10  # -0.10 from default 0.20
```

### Validation Rules

1. All weights must be between 0.0 and 1.0
2. Sum of weights must equal 1.0 (100%)
3. At least 8 categories must be defined

### Common Weight Patterns

| Pattern | Functional | Compliance | Quality | Use Case |
|---------|------------|------------|---------|----------|
| Feature-Heavy | 35% | 10% | 15% | MVP, product launch |
| Compliance-Heavy | 20% | 30% | 15% | Regulated industry |
| Quality-Heavy | 20% | 15% | 25% | Enterprise, SaaS |
| Balanced | 25% | 20% | 15% | General purpose |

---

## Keyword Customization

### Adding Project Keywords

Append keywords without replacing defaults:

```yaml
defaults:
  categories:
    compliance:
      keywords_append:
        - "CustomRegulation"
        - "InternalAudit"
        - "ProjectGate"
```

### Replacing Keywords

Replace all default keywords:

```yaml
defaults:
  categories:
    compliance:
      keywords:
        - "HIPAA"
        - "PHI"
        - "BAA"
        # Default fintech keywords NOT included
```

### Category-Specific Keywords

```yaml
defaults:
  categories:
    integration:
      keywords_append:
        - "BridgeAPI"
        - "NoahGateway"
    risk:
      keywords_append:
        - "FraudRisk"
        - "ChargebackRisk"
```

---

## Industry Templates

### Using Templates

Reference a template with `extends`:

```yaml
extends: healthcare_compliance
```

Available templates:

| Template | Industry | Key Keywords |
|----------|----------|--------------|
| `fintech_compliance` | Finance | FinCEN, KYC, AML, PCI-DSS |
| `healthcare_compliance` | Healthcare | HIPAA, PHI, FDA, CLIA |
| `general_compliance` | Technology | GDPR, SOC2, ISO27001 |
| `government_compliance` | Government | FedRAMP, FISMA, ITAR |

### Template + Custom Keywords

Templates can be combined with custom keywords:

```yaml
extends: fintech_compliance

defaults:
  categories:
    compliance:
      keywords_append:
        - "StateMoneyTransmitter"
        - "BitLicense"
```

### Creating Custom Templates

1. Create `docs/UCX/scoring/templates/custom_template.yaml`
2. Define keywords and optional weight adjustments
3. Reference with `extends: custom_template`

```yaml
# docs/UCX/scoring/templates/custom_template.yaml
industry: custom
description: "Custom industry template"

compliance:
  keywords:
    - "CustomTerm1"
    - "CustomTerm2"
  weight_adjustment: 0.05  # Increase compliance weight by 5%
```

---

## Threshold Customization

### Adjusting Pass/Warn/Fail

```yaml
defaults:
  thresholds:
    pass: 90   # Stricter pass threshold
    warn: 75   # Stricter warn threshold
    fail: 0    # Keep fail at 0
```

### Per-Document-Type Thresholds

```yaml
document_types:
  brd:
    thresholds:
      pass: 80  # More lenient for early-stage BRDs
      warn: 60
```

---

## Max Deduction Customization

### Adjusting Category Caps

```yaml
defaults:
  categories:
    compliance:
      max_deduction: 30  # Increase cap for regulated industries
    functional:
      max_deduction: 20  # Decrease cap
```

### Rationale

- Higher caps = more impact from that category
- Lower caps = limit impact even with many findings
- Should remain proportional to weight

---

## Advanced Customization

### Persona Category Overrides

Currently not configurable via YAML. Persona → category mapping is defined in code.

### Element Code Remapping

Currently not configurable via YAML. Element code → category mapping follows ID_NAMING_STANDARDS.

### Custom Categories

Adding new categories is not supported. The 8 standard categories cover all SDD document needs.

---

## Example Configurations

### Fintech Startup (Compliance-Light)

```yaml
extends: fintech_compliance

document_types:
  brd:
    categories:
      functional:
        weight: 0.35
      compliance:
        weight: 0.10  # Startup phase, less regulatory focus
      acceptance:
        weight: 0.15

defaults:
  thresholds:
    pass: 80  # More lenient for MVP
```

### Healthcare Enterprise

```yaml
extends: healthcare_compliance

document_types:
  brd:
    categories:
      compliance:
        weight: 0.30  # High compliance focus
        max_deduction: 35
      risk:
        weight: 0.10  # Higher risk focus for healthcare

defaults:
  thresholds:
    pass: 90  # Stricter for healthcare
```

### Government Contractor

```yaml
extends: government_compliance

document_types:
  brd:
    categories:
      compliance:
        weight: 0.35  # Highest compliance
      architecture:
        weight: 0.10  # Higher for security architecture
      functional:
        weight: 0.15  # Lower for compliance-first

defaults:
  thresholds:
    pass: 95  # Very strict for government
    warn: 85
```

---

## Troubleshooting

### Config Not Applied

1. Verify file location: `docs/UCX/scoring_weights.yaml`
2. Run validation: `ucx scoring validate`
3. Check for YAML syntax errors

### Weights Don't Sum to 100%

```
ScoringConfigError: BRD weights sum to 105.0%
```

Ensure all weight changes balance out.

### Template Not Found

```
Warning: Template 'custom_template' not found
```

Check template path: `docs/UCX/scoring/templates/custom_template.yaml`

---

*Version: 1.12.0 | Created: 2026-03-12*
