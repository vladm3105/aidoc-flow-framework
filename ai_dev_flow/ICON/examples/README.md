---
title: "ICON Example Documents"
tags:
  - index-document
  - layer-11-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: ICON
  layer: 11
  priority: shared
---

# ICON Example Documents

## Purpose

This directory contains example Implementation Contracts (ICONs) demonstrating best practices for type-safe parallel development contracts.

## When to Use Standalone ICON Files

Most implementation contracts should be embedded in TASKS files. Use standalone ICON files only when:

- 5+ consumer TASKS files depend on the contract
- Contract definition exceeds 500 lines
- Platform-level shared interfaces
- Contracts used across multiple projects

## Available Examples

| ID | Title | Contract Type | Complexity | Providers | Consumers |
|----|-------|---------------|------------|-----------|-----------|
| [ICON-01](ICON-01_validation_protocol_example.md) | Validation Protocol | Protocol Interface | 2 (moderate) | TASKS-NN | 3 consumers |

## Contract Types Demonstrated

1. **Protocol Interfaces**: `typing.Protocol` with method signatures and type hints
2. Exception Hierarchies (planned)
3. State Machine Contracts (planned)
4. Data Models (planned)
5. DI Interfaces (planned)

## Creating New Examples

When adding examples to this directory:

1. **Use Real Scenarios**: Base examples on actual project implementations
2. **Include All Sections**: Demonstrate complete ICON structure
3. **Show Mock Implementations**: Include mock template for consumer testing
4. **Document Provider/Consumer Flow**: Show the integration workflow
5. **Add Validation Criteria**: Include mypy and test commands

## Using Examples

```bash
# Copy example to your project docs
cp ai_dev_flow/ICON/examples/ICON-NN_*_example.md \
   docs/ICON/ICON-YY_your_contract.md

# Customize for your implementation:
# - Update ICON ID
# - Modify interface specification
# - Update provider/consumer TASKS references
# - Adjust traceability tags
```

---

**Directory Purpose**: ICON example repository
**Last Updated**: 2025-11-13
**Maintainer**: [Project Team]
