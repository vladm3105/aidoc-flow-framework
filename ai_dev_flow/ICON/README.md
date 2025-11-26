---
title: ICON Directory Overview
tags:
  - implementation-contract
  - layer-11-artifact
  - directory-overview
custom_fields:
  document_type: readme
  artifact_type: ICON
  layer: 11
---

# ICON Directory

**Purpose**: Standalone Implementation Contract files for Layer 11 (TASKS) parallel development coordination.

**⚠️ IMPORTANT**: Most implementation contracts should be embedded in TASKS files. Use standalone ICON files only when criteria are met (see ICON_CREATION_RULES.md).

## Integration Workflow (CRITICAL)

### Step-by-Step Process

1. **Identify Need**: TASKS file analysis shows 3+ downstream dependencies
2. **Create ICON File**: Use ICON-TEMPLATE.md
3. **Update Provider TASKS**: Add Section 8.1 with contract details
4. **Update Consumer TASKS**: Add Section 8.2 to each consumer
5. **Validate Integration**: Run validation commands
6. **Mark ICON as Active**: Only after validation passes

### Validation Commands

**Before marking ICON as Active, run these commands**:

```bash
# Navigate to project root
cd /opt/data/ibmcp/

# Check total references (must equal 1 provider + N consumers)
grep -r "@icon: ICON-XXX" docs/TASKS/ | wc -l

# Verify provider role exists
grep -r "@icon-role: provider" docs/TASKS/ | grep "ICON-XXX"

# Verify consumer roles exist (count must equal N consumers)
grep -r "@icon-role: consumer" docs/TASKS/ | grep "ICON-XXX" | wc -l

# Check no orphaned ICON files
for icon in ICON-001 ICON-002 ICON-003; do
  count=$(grep -r "@icon: $icon" docs/TASKS/ | wc -l)
  if [ $count -eq 0 ]; then
    echo "ERROR: $icon is orphaned (0 TASKS references)"
  else
    echo "OK: $icon has $count TASKS references"
  fi
done
```

### Anti-Pattern Prevention

❌ **NEVER**: Create ICON file and stop
❌ **NEVER**: Skip TASKS file updates
❌ **NEVER**: Mark ICON as "Active" before validation

✅ **ALWAYS**: Complete full integration workflow
✅ **ALWAYS**: Validate bidirectional traceability
✅ **ALWAYS**: Run validation commands before marking Active

---

## Directory Contents

| File | Purpose |
|------|---------|
| **ICON-000_index.md** | Contract registry and quick reference |
| **ICON-TEMPLATE.md** | Template for creating new contracts |
| **ICON_CREATION_RULES.md** | Decision framework for ICON vs embedded |
| **README.md** | This file - directory overview |

**Contract Files**: `ICON-NNN_descriptive_name.md` (created as needed)

---

## Quick Start

### 1. Should You Create an ICON File?

**Decision Criteria** (ALL must be met):
- [ ] 5+ consumer TASKS files
- [ ] Contract definition >500 lines
- [ ] Platform-level shared interface
- [ ] Cross-project usage

**If NO to any**: Embed in TASKS file instead (Section 8: Implementation Contracts)

See [ICON_CREATION_RULES.md](./ICON_CREATION_RULES.md) for detailed decision framework.

### 2. Creating a New ICON File

```bash
# 1. Copy template
cp ICON-TEMPLATE.md ICON-001_your_contract_name.md

# 2. Update frontmatter and metadata
# - Assign ICON-001 (next available ID)
# - Set contract_type (protocol/exception/state-machine/data-model/di-interface)
# - List providers and consumers

# 3. Complete contract definition
# - Define type-safe interfaces
# - Document provider requirements
# - Document consumer requirements
# - Add validation examples

# 4. Update registry
# Edit ICON-000_index.md to add new contract entry

# 5. Notify stakeholders
# Inform provider and consumer TASKS owners
```

### 3. Using Existing ICON Files

**Provider TASKS** (implements contract):
```markdown
## 8. Implementation Contracts

@icon: ICON-001:GatewayConnector
@icon-role: provider

See [ICON-001_gateway_connector.md](../../ai_dev_flow/ICON/ICON-001_gateway_connector.md)
```

**Consumer TASKS** (depends on contract):
```markdown
## 3. Dependencies

@icon: ICON-001:GatewayConnector
@icon-role: consumer

Requires GatewayConnector protocol for gateway connections.
```

---

## File Naming Convention

**Format**: `ICON-NNN_descriptive_name.md`

**Rules**:
- **ICON-NNN**: Sequential numbering starting from 001
- **descriptive_name**: Lowercase with underscores
- **Extension**: Always `.md`

**Examples**:
- `ICON-001_gateway_connector_protocol.md`
- `ICON-002_market_data_event_bus.md`
- `ICON-003_order_execution_exceptions.md`
- `ICON-004_position_state_machine.md`

---

## Traceability Tags

### Tag Format

**Contract Definition**:
```yaml
@icon: ICON-NNN:ContractName
```

**With Role** (in TASKS files):
```yaml
@icon: ICON-001:GatewayConnector
@icon-role: provider
```

```yaml
@icon: ICON-001:GatewayConnector
@icon-role: consumer
```

### Role Types

| Role | Description | Usage |
|------|-------------|-------|
| `provider` | Implements the contract | TASKS file defining implementation |
| `consumer` | Depends on the contract | TASKS files using contract |
| (no role) | Reference only | Documentation references |

### Validation Commands

```bash
# Find all ICON references
grep -r "@icon: ICON-" docs/

# List ICON files
ls -la docs/ICON/ICON-*.md

# Verify provider/consumer pairs
grep -A1 "@icon: ICON-001" docs/TASKS/

# Check for orphaned contracts (no consumers)
for file in docs/ICON/ICON-*.md; do
  id=$(basename "$file" | cut -d_ -f1)
  count=$(grep -r "@icon: $id" docs/TASKS/ | wc -l)
  echo "$id: $count references"
done
```

---

## Contract Types

### 1. Protocol Interfaces

**Purpose**: Type-safe service interfaces
**Use Case**: Async/sync services, plugin architectures, adapter patterns
**Example**: GatewayConnector, MarketDataProvider

### 2. Exception Hierarchies

**Purpose**: Typed exception handling
**Use Case**: Error classification, retry logic, circuit breakers
**Example**: GatewayException, OrderException

### 3. State Machine Contracts

**Purpose**: Valid state transitions
**Use Case**: Connection states, order lifecycle, session management
**Example**: ConnectionState, OrderState

### 4. Data Models

**Purpose**: Validated data structures
**Use Case**: API requests/responses, events, configuration
**Example**: MarketDataEvent, OrderRequest

### 5. Dependency Injection Interfaces

**Purpose**: DI container interfaces
**Use Case**: Service factories, repository patterns
**Example**: ServiceProvider, RepositoryFactory

---

## Lifecycle Management

### Active Phase

**Responsibilities**:
- Track version changes
- Maintain provider/consumer lists
- Monitor usage patterns
- Coordinate breaking changes

**Versioning** (Semantic):
- **Major**: Breaking changes (signature changes, removed methods)
- **Minor**: Backward-compatible additions (new optional parameters)
- **Patch**: Documentation updates, clarifications

### Deprecation Phase

**Process**:
1. Announce deprecation (6-month notice)
2. Provide migration guide
3. Update status to "Deprecated" in ICON-000_index.md
4. Monitor consumer migration progress
5. Archive after all consumers migrate

**Communication**:
- Update contract file with deprecation notice
- Notify all provider/consumer TASKS owners
- Document migration path
- Provide timeline for sunset

---

## Best Practices

### ✅ Do

- **Validate criteria** before creating ICON files
- **Use semantic versioning** for contract changes
- **Document all changes** in version history
- **Notify stakeholders** of breaking changes
- **Maintain registry** (ICON-000_index.md) current
- **Review quarterly** for relevance and usage

### ❌ Don't

- **Create ICON files prematurely** (start with embedded)
- **Skip migration** when criteria change
- **Make breaking changes** without notice
- **Forget to update registry** when creating contracts
- **Leave orphaned contracts** (no consumers)
- **Mix contract types** in single ICON file

---

## Integration with SDD Workflow

### Layer Position

**Layer 11**: TASKS (Task Breakdown)
- Bridges SPEC (Layer 10) and IPLAN (Layer 12)
- Coordinates parallel implementation
- Enables type-safe integration

### Relationship to Other Layers

**Layer 9 (CTR)**: External API contracts
- `@ctr:` tags reference external APIs
- ICON contracts are internal only

**Layer 11 (ICON)**: Internal implementation contracts
- `@icon:` tags reference implementation contracts
- Embedded in TASKS or standalone ICON

**Layer 12 (IPLAN)**: Implementation plans
- `@iplan:` tags reference execution plans
- Consume contracts defined in TASKS/ICON

---

## References

### Internal Documentation

**Primary Guides**:
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](../TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md) - Comprehensive guide
- [ICON_CREATION_RULES.md](./ICON_CREATION_RULES.md) - Decision criteria
- [ICON-000_index.md](./ICON-000_index.md) - Contract registry
- [ICON-TEMPLATE.md](./ICON-TEMPLATE.md) - Contract template

**Related Artifacts**:
- [TASKS-TEMPLATE.md](../TASKS/TASKS-TEMPLATE.md) - Embedded contracts (default)
- [TRACEABILITY.md](../TRACEABILITY.md) - Traceability tags
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Naming conventions
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow

### External Resources

- [PEP 544: Protocols](https://peps.python.org/pep-0544/) - Structural subtyping
- [PEP 589: TypedDict](https://peps.python.org/pep-0589/) - Typed dictionaries
- [mypy Documentation](https://mypy.readthedocs.io/) - Type checking
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation

---

## Support

### Questions or Issues

**Documentation**:
- Check IMPLEMENTATION_CONTRACTS_GUIDE.md first
- Review ICON_CREATION_RULES.md for decisions
- Consult ICON-000_index.md for examples

**Unclear Criteria**:
- Apply decision matrix from ICON_CREATION_RULES.md
- Document exceptions with rationale
- Review in quarterly audit

**Migration Needs**:
- Follow migration strategy in ICON_CREATION_RULES.md
- Update all stakeholders
- Coordinate transition timing

---

## Document Metadata

**Version**: 1.0.0
**Created**: 2025-11-25
**Last Updated**: 2025-11-25
**Document Type**: Directory Overview
**Complexity**: 1/5
**Token Count**: ~2,000 tokens
