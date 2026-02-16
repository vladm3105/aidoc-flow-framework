# Core Technical Documentation

Technical specifications and design documents for the {PROJECT_NAME} project.

## Document Index

| Document | Description |
|----------|-------------|
| [Executive Summary](executive-summary.md) | High-level project overview |
| [Database Schema](01-database-schema.md) | Database design and entity relationships |
| [MCP Tool Contracts](02-mcp-tool-contracts.md) | Model Context Protocol tool definitions |
| [Agent Routing Spec](03-agent-routing-spec.md) | AI agent routing and dispatch logic |
| [Tenant Onboarding](04-tenant-onboarding.md) | Multi-tenant onboarding process |
| [API Endpoint Spec](05-api-endpoint-spec.md) | REST API endpoint specifications |
| [Deployment Infrastructure](07-deployment-infrastructure.md) | Cloud deployment architecture |
| [Cost Model](08-cost-model.md) | Cost estimation and tracking |
| [Observability Spec](09-observability-spec.md) | Monitoring, logging, and alerting |

## Document Conventions

### Numbering

Documents are numbered by topic area:
- **01-09**: Core system specifications
- **10-19**: Integration specifications (reserved)
- **20-29**: Operational procedures (reserved)

### Placeholders

Documents use `{VARIABLE_NAME}` placeholders that must be replaced during project setup. See [CONFIG.md](../../CONFIG.md) for variable definitions.

### Diagrams

Visual diagrams are provided in SVG format where applicable:
- `executive-summary.svg` - System architecture overview

## Relationship to Other Docs

```
docs/
├── core/          # This directory - technical specs
├── adr/           # Architecture Decision Records
├── qa/            # QA testing documentation
└── architecture/  # System architecture diagrams
```

## Updating Documentation

When updating core documentation:

1. Maintain consistent formatting across documents
2. Update the index table above when adding new documents
3. Cross-reference related documents using relative links
4. Version significant changes in the document's changelog section
