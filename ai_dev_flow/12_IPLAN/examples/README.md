---
title: "IPLAN Example Documents"
tags:
  - index-document
  - layer-12-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: IPLAN
  layer: 12
  priority: shared
---

# IPLAN Example Documents

## Purpose

This directory contains example Implementation Plans (IPLANs) demonstrating best practices for session-based execution plans with bash commands and resume points.

## Example Categories

### 1. Simple Implementation Examples
- Single-phase implementations
- Basic bash command sequences
- Simple verification steps

### 2. Multi-Phase Implementation Examples
- Complex features requiring multiple phases
- Dependencies between phases
- Checkpoint and resume patterns

### 3. Infrastructure Setup Examples
- Environment configuration
- Cloud resource provisioning
- Service deployment

### 4. Data Migration Examples
- Database migrations
- Data transformation pipelines
- ETL processes

### 5. Integration Implementation Examples
- Third-party API integrations
- Message queue setup
- Webhook implementations

## Example Naming Convention

Examples follow IPLAN naming with `_example` suffix:

```
IPLAN-NN_{feature_name}_example.md
```

Example filenames:
- `IPLAN-01_api_integration_example.md`
- `IPLAN-02_database_migration_example.md`
- `IPLAN-03_service_deployment_example.md`

## Creating New Examples

When adding examples to this directory:

1. **Use Real Scenarios**: Base examples on actual project implementations
2. **Include All sections**: Demonstrate complete IPLAN structure
3. **Show Resume Points**: Include checkpoint and resume capability
4. **Add Verification**: Show how to verify each phase completion
5. **Document Learnings**: Add notes about challenges and solutions

## What Makes a Good Example

Good IPLAN examples demonstrate:

- ✅ Clear session context and prerequisites
- ✅ Well-structured phases with bash commands
- ✅ Comprehensive verification steps
- ✅ Resume points for long-running implementations
- ✅ Error handling and rollback procedures
- ✅ Complete traceability to upstream artifacts (REQ, SPEC, TASKS)

## Using Examples

To use an example as a template:

```bash
# Copy example to your project docs
cp ai_dev_flow/12_IPLAN/examples/IPLAN-NN_feature_example_*.md \
   docs/12_IPLAN/IPLAN-YY_your_feature.md

# Customize for your implementation
# - Update IPLAN ID (zero-padded, e.g., 01, 02, 003)
# - Modify phases for your specific feature
# - Adjust bash commands for your environment
# - Update traceability references
```

## Contributing Examples

When contributing new examples:

1. Ensure example is based on real, working implementation
2. Remove any sensitive information (credentials, internal URLs)
3. Generalize using placeholder format: `[PLACEHOLDER - e.g., examples]`
4. Add detailed comments explaining decisions
5. Include lessons learned section

## Available Examples

| ID | Title | Category | Complexity | Related Artifacts |
|----|-------|----------|------------|-------------------|
| [IPLAN-01](IPLAN-01_example.md) | User Authentication API Implementation | API Integration | 3 (moderate) | TASKS-01, SPEC-01, REQ-01, ADR-01, BDD-01 |

**Key Learning Points**:
- JWT-based authentication implementation
- Session-based execution with verification steps
- Complete traceability chain from BRD through IPLAN

---

**Directory Purpose**: IPLAN example repository
**Last Updated**: 2025-11-13
**Maintainer**: [Project Team]
