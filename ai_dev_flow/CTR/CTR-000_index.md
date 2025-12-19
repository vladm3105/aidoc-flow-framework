---
title: "CTR-000: CTR Index"
tags:
  - index-document
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: CTR
  layer: 9
  priority: shared
---

# CTR-000: API Contracts Master Index

## Purpose
This index catalogs all API contract documents (CTR) that define interfaces between components in the SDD workflow. Contracts specify request/response schemas, error handling, quality attributes, and versioning policies for component communication.

## Organization
Contracts can be organized in subdirectories by service type for better document management and SPEC alignment:
- `agents/`: Agent-to-agent communication contracts
- `mcp/`: MCP server contracts
- `infra/`: Infrastructure service contracts
- `shared/`: Cross-cutting contracts

See [README.md](./README.md) for detailed guidance on organizational structure.

## Template References
- **Markdown Template**: [CTR-TEMPLATE.md](./CTR-TEMPLATE.md) - Human-readable contract documentation
- **YAML Template**: [CTR-TEMPLATE.yaml](./CTR-TEMPLATE.yaml) - Machine-readable schema definitions

## Contract Catalog

### Active Contracts

| Contract ID | Title | Service Type | Status | Version | Upstream REQ | Downstream SPEC | Last Updated |
|-------------|-------|--------------|--------|---------|--------------|-----------------|--------------|
| CTR-TEMPLATE | Contract Template | template | Draft | 1.0.0 | N/A | N/A | YYYY-MM-DD |

*Add new contracts below as they are created*

### Deprecated Contracts

| Contract ID | Title | Deprecated Date | Superseded By | Migration Deadline |
|-------------|-------|-----------------|---------------|-------------------|
| *No deprecated contracts yet* | | | | |

## Contract Status Definitions

- **Draft**: Contract under development, not yet approved for implementation
- **Active**: Contract approved and in use by providers/consumers
- **Deprecated**: Contract marked for removal, migration path provided
- **Superseded**: Contract replaced by newer version

## Adding New Contracts

### Naming Convention
- **Format**: `CTR-NN_descriptive_slug.md` + `CTR-NN_descriptive_slug.yaml`
- **NNN**: 2+ digit sequence number (01, 02, 015)
- **Slug**: snake_case descriptive title matching both files

### Process
1. **Reserve ID**: Check this index for next available CTR-NN number
2. **Copy Templates**: Copy both CTR-TEMPLATE.md and CTR-TEMPLATE.yaml
3. **Create Dual Files**: Create both .md and .yaml with same CTR-NN_slug
4. **Complete Documentation**: Fill all sections in markdown template
5. **Define Schema**: Complete YAML schema with request/response structures
6. **Update Index**: Add entry to this index with metadata
7. **Link Traceability**: Reference upstream REQ/ADR and downstream SPEC
8. **Validate**: Ensure schema validation passes, links resolve

### Optional: Organize by Service Type
For projects with 10+ contracts or multiple service types, consider organizing contracts in subdirectories:
```
CTR/
├── agents/
│   ├── CTR-001_data_processor_api.md
│   └── CTR-001_data_processor_api.yaml
├── mcp/
│   ├── CTR-010_validation_service_mcp.md
│   └── CTR-010_validation_service_mcp.yaml
└── infra/
    ├── CTR-020_pubsub_message_schema.md
    └── CTR-020_pubsub_message_schema.yaml
```

## Maintenance

### Quarterly Review
- Review all **Active** contracts for accuracy
- Check if any contracts should be marked **Deprecated**
- Validate that all contract links resolve correctly
- Update SPEC references if implementations change

### Contract Changes
- **Breaking Changes**: Require new major version (CTR-NN v2.0.0)
- **Non-Breaking Additions**: Increment minor version (CTR-NN v1.1.0)
- **Bug Fixes**: Increment patch version (CTR-NN v1.0.1)

### Deprecation Process
1. Mark contract status as **Deprecated** in this index
2. Update contract .md file with deprecation notice
3. Provide 30-day migration period minimum
4. Reference superseding contract (if applicable)
5. After migration deadline, move to **Deprecated Contracts** table

## Cross-References

### Workflow Position
```
REQ (Atomic Requirements)
    ↓
**CTR (API Contracts)** ← Current artifact type
    ↓
SPEC (Technical Implementation)
```

### Related Documentation
- [README.md](./README.md): Comprehensive guide to API contracts
- [TRACEABILITY.md](../TRACEABILITY.md): Traceability requirements for all artifacts
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md): Naming conventions for CTR files
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md): Development workflow including CTR phase

## Statistics

- **Total Contracts**: 0 (excluding template)
- **Active Contracts**: 0
- **Deprecated Contracts**: 0
- **Service Types**: 0 (agents: 0, mcp: 0, infra: 0, shared: 0)

*Update statistics when adding/modifying contracts*

---

**Index Version**: 1.0
**Last Updated**: YYYY-MM-DD
**Next Review**: YYYY-MM-DD (recommend quarterly review)
