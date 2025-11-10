# Generic Domain Configuration

**Version**: 1.0
**Purpose**: Universal fallback domain configuration for projects without specific domain
**Domain**: Internal Tools, Utilities, Custom Domains, General-Purpose Applications
**Status**: Production
**Regulatory Scope**: Company Policies Only (Minimal)

---

## Overview

This configuration provides generic, domain-agnostic terminology for projects that don't fit into specialized domains (Financial Services, Healthcare, E-commerce, etc.). Use this for internal business tools, utilities, proof-of-concepts, or custom domains.

---

## Placeholder Replacement Dictionary

| Placeholder | Generic Term | Context |
|-------------|--------------|---------|
| `[RESOURCE_COLLECTION]` | **Collection** | Container for entities |
| `[RESOURCE_ITEM]` | **Entity** | Individual object |
| `[RESOURCE_ACTION]` | **Operation** | Action performed |
| `[EXTERNAL_DATA_PROVIDER]` | **External API** | Third-party service |
| `[CALCULATION_ENGINE]` | **Processing Engine** | Core processing system |
| `[USER_ROLE]` | **User / Admin** | System user |
| `[TRANSACTION]` | **Action** | System transaction |
| `[CONSTRAINT]` | **Business Rule** | System constraint |
| `[REGULATORY_REQUIREMENT]` | **Company Policy** | Internal policy |
| `[DATA_STORE]` | **Database** | Storage system |
| `[EVENT]` | **Event** | State change |
| `[WORKFLOW]` | **Workflow** | Business process |
| `[METRIC]` | **Metric** | Measurement |
| `[ALERT]` | **Alert** | Notification |
| `[REPORT]` | **Report** | Output document |

---

## AI Assistant Placeholder Replacement

```bash
# Generic replacements
find docs/ -type f -name "*.md" -exec sed -i \
  -e 's/\[RESOURCE_COLLECTION\]/Collection/g' \
  -e 's/\[RESOURCE_ITEM\]/Entity/g' \
  -e 's/\[RESOURCE_ACTION\]/Operation/g' \
  -e 's/\[EXTERNAL_DATA_PROVIDER\]/External API/g' \
  -e 's/\[CALCULATION_ENGINE\]/Processing Engine/g' \
  -e 's/\[USER_ROLE\]/User/g' \
  -e 's/\[TRANSACTION\]/Action/g' \
  -e 's/\[CONSTRAINT\]/Business Rule/g' \
  -e 's/\[REGULATORY_REQUIREMENT\]/Company Policy/g' \
  -e 's/\[DATA_STORE\]/Database/g' \
  -e 's/\[EVENT\]/Event/g' \
  -e 's/\[WORKFLOW\]/Workflow/g' \
  -e 's/\[METRIC\]/Metric/g' \
  -e 's/\[ALERT\]/Alert/g' \
  -e 's/\[REPORT\]/Report/g' \
  {} +
```

---

## Requirements Subdirectory Structure

### Standard Subdirectories Only

No domain-specific subdirectories added. Use standard structure:

```bash
# Standard subdirectories (no domain extensions)
docs/reqs/api/          # API requirements
docs/reqs/auth/         # Authentication
docs/reqs/data/         # Data management
docs/reqs/core/         # Core business logic
docs/reqs/integration/  # External integrations
docs/reqs/monitoring/   # Monitoring & observability
docs/reqs/reporting/    # Reporting features
docs/reqs/security/     # Security requirements
docs/reqs/ui/           # User interface
```

---

## Regulatory Framework

### Minimal Compliance

**Company Policies Only**:
- Internal security policies
- Data retention policies
- Access control policies
- Code review standards
- Deployment procedures

**No External Regulations** (unless specified by company):
- Use generic "Company Policy" terminology
- Reference internal policy documents
- Implement company-specific controls

---

## Terminology Dictionary

### Generic Terms

| Concept | Generic Term | Alternatives |
|---------|--------------|--------------|
| Container | Collection | List, Set, Group |
| Item | Entity | Object, Record, Instance |
| Action | Operation | Method, Function, Command |
| User | User | Person, Actor, Principal |
| Data Store | Database | Repository, Store, Persistence |
| External Service | External API | Integration, Provider, Endpoint |

---

## Example Use Cases

### Use Case 1: Internal Admin Tool

**Placeholder Replacements**:
```
[RESOURCE_COLLECTION] → User Collection
[RESOURCE_ITEM] → User Entity
[RESOURCE_ACTION] → User Operation
[REGULATORY_REQUIREMENT] → Company IT Policy
```

### Use Case 2: Data Migration Utility

**Placeholder Replacements**:
```
[RESOURCE_COLLECTION] → Data Set
[RESOURCE_ITEM] → Data Record
[RESOURCE_ACTION] → Transform Operation
[CALCULATION_ENGINE] → ETL Pipeline
```

---

## AI Assistant Application Guidance

### When to Use

Apply GENERIC_DOMAIN_CONFIG.md when:
- User selects "Other/Generic" in domain questionnaire
- Project is internal tool or utility
- No specific domain applies
- Custom domain without existing configuration

### Application Sequence

1. Load GENERIC_DOMAIN_CONFIG.md
2. Create standard subdirectories only (no domain extensions)
3. Apply generic placeholder replacements
4. Use generic examples in templates
5. Reference company policies instead of external regulations

### Validation Checklist

- [ ] Standard subdirectories created (api, auth, data, core)
- [ ] No domain-specific subdirectories (no risk/, trading/, tenant/)
- [ ] Placeholder `[RESOURCE_COLLECTION]` replaced with "Collection"
- [ ] Placeholder `[USER_ROLE]` replaced with "User"
- [ ] Compliance references use "Company Policy"
- [ ] Generic terminology used throughout

---

## References

- [AI_ASSISTANT_RULES.md](./AI_ASSISTANT_RULES.md#rule-3-domain-configuration-application)
- [DOMAIN_SELECTION_QUESTIONNAIRE.md](./DOMAIN_SELECTION_QUESTIONNAIRE.md#6-othergeneric)
- [FINANCIAL_DOMAIN_CONFIG.md](./FINANCIAL_DOMAIN_CONFIG.md) - Financial domain
- [SOFTWARE_DOMAIN_CONFIG.md](./SOFTWARE_DOMAIN_CONFIG.md) - Software/SaaS domain

---

**End of Generic Domain Configuration**
