---
title: "ICON-000: Implementation Contracts Registry"
tags:
  - implementation-contract
  - layer-11-artifact
  - shared-architecture
  - contract-index
custom_fields:
  document_type: index
  artifact_type: ICON
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---

# ICON-000: Implementation Contracts Registry

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

**Purpose**: Central registry for standalone implementation contract files (ICON).

**⚠️ NOTE**: Most implementation contracts should be embedded in TASKS files. This registry tracks only standalone ICON files used when:
- 5+ consumer TASKS files
- Contract definition >500 lines
- Platform-level shared interfaces
- Contracts used across multiple projects

---

## Quick Reference

| ICON ID | Contract Name | Type | Status | Providers | Consumers | Created |
|---------|---------------|------|--------|-----------|-----------|---------|
| ICON-01 | [Example] | Protocol | Active | 1 | 5 | 2025-11-25 |

---

## Active Contracts

### ICON-01: [Contract Name]

**Status**: Active
**Type**: [Protocol/Exception/State Machine/Data Model/DI Interface]
**Purpose**: [Brief description]
**Providers**: [TASKS-IDs]
**Consumers**: [TASKS-IDs]
<!-- VALIDATOR:IGNORE-LINKS-START -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
**File**: [ICON-01_contract_name.md](./ICON-01_contract_name.md)
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-END -->
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

---

## Contract Statistics

**Total Contracts**: 0
**Active**: 0
**Deprecated**: 0
**Draft**: 0

**By Type**:
- Protocol Interfaces: 0
- Exception Hierarchies: 0
- State Machines: 0
- Data Models: 0
- DI Interfaces: 0

---

## Usage Guidelines

### When to Create ICON Files

**Criteria** (ALL must be met):
1. **5+ Consumer TASKS**: Contract used by 5 or more TASKS files
2. **Large Contract**: Definition exceeds 500 lines
3. **Platform-Level**: Shared across multiple system components
4. **Cross-Project**: Used in multiple projects

**Default**: Embed contracts in TASKS files (section 8: Implementation Contracts)

### File Naming Convention

**Format**: `ICON-NN_descriptive_name.md`

**Examples**:
- `ICON-01_gateway_connector_protocol.md`
- `ICON-02_external_data_event_bus.md`
- `ICON-03_order_execution_exceptions.md`

### Directory Location

**Framework Templates**:
- `ai_dev_flow/ICON/`

**Project-Specific**:
- `[project_root]/docs/ICON/`
- `[project_root]/ai_dev_flow/ICON/`

---

## Traceability Tags

### Tag Format

**Contract Definition**:
```markdown
@icon: ICON-01:GatewayConnector
```

**Provider TASKS**:
```markdown
@icon: ICON-01:GatewayConnector
@icon-role: provider
```

**Consumer TASKS**:
```markdown
@icon: ICON-01:GatewayConnector
@icon-role: consumer
```

### Validation

```bash
# Find all ICON references
grep -r "@icon: ICON-" docs/

# List all ICON files
ls -la docs/ICON/ICON-*.md

# Verify provider/consumer pairs
grep -A1 "@icon: ICON-01" docs/TASKS/
```

---

## Contract Lifecycle

### 1. Creation Phase

1. Verify criteria (5+ consumers, >500 lines, platform-level)
2. Copy ICON-TEMPLATE.md
3. Assign next available ICON-NN ID
4. Complete contract definition
5. Update this registry
6. Notify provider and consumer TASKS owners

### 2. Active Phase

- Track version changes
- Maintain provider/consumer lists
- Monitor usage patterns
- Coordinate breaking changes

### 3. Deprecation Phase

1. Announce deprecation (6-month notice)
2. Provide migration guide
3. Update status to "Deprecated"
4. Monitor consumer migration
5. Archive after all consumers migrate

---

## References

### Internal Documentation
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](../TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md) - Comprehensive guide
- [ICON-TEMPLATE.md](./ICON-TEMPLATE.md) - Contract template
- [ICON_CREATION_RULES.md](./ICON_CREATION_RULES.md) - Decision criteria
- [README.md](./README.md) - ICON directory overview

### Related Artifacts
- [TASKS-TEMPLATE.md](../TASKS/TASKS-TEMPLATE.md) - Embedded contracts (default)
- [TRACEABILITY.md](../TRACEABILITY.md) - Traceability tags
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Naming conventions

---

## Document Metadata

**Version**: 1.0.0
**Created**: 2025-11-25
**Last Updated**: 2025-11-25
**Document Type**: Contract Registry
**Total Contracts**: 0
**Complexity**: 1/5
**Token Count**: ~1,500 tokens
