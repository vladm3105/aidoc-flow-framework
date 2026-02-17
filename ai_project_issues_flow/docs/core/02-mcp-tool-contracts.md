# MCP Tool Contracts Specification

**Layer**: Data Access
**Phase**: 3
**Status**: Template

## Overview

This specification defines the MCP (Model Context Protocol) server contracts for cloud provider data access. MCP servers provide DATA ACCESS only; AI Agents handle reasoning and decisions.

## MCP Server Inventory

| Server | Type | Provider | Phase |
|--------|------|----------|-------|
| GCP MCP | Native | `gcloud-mcp` + BigQuery MCP | 3 |
| AWS MCP | Native | `@awslabs/mcp-server-aws-core` | 3 |
| Azure MCP | Native | `Azure.Mcp.Server` | 3 |
| OpenCost MCP | Custom | Internal | 3 |

## Tool Contract Schema

```yaml
tool:
  name: string          # Tool identifier
  description: string   # Human-readable description
  inputSchema:
    type: object
    properties: {}      # JSON Schema for inputs
    required: []
  outputSchema:
    type: object
    properties: {}      # JSON Schema for outputs
```

## GCP MCP Tools

### get_billing_data

```yaml
tool:
  name: get_billing_data
  description: Retrieve GCP billing data for specified date range
  inputSchema:
    type: object
    properties:
      project_id:
        type: string
        description: GCP project ID
      start_date:
        type: string
        format: date
      end_date:
        type: string
        format: date
    required: [project_id, start_date, end_date]
  outputSchema:
    type: object
    properties:
      total_cost:
        type: number
      currency:
        type: string
      line_items:
        type: array
```

### get_resource_recommendations

```yaml
tool:
  name: get_resource_recommendations
  description: Get cost optimization recommendations from GCP Recommender
  inputSchema:
    type: object
    properties:
      project_id:
        type: string
      recommender_type:
        type: string
        enum: [cost, performance, security]
    required: [project_id]
```

## AWS MCP Tools

### get_cost_explorer_data

```yaml
tool:
  name: get_cost_explorer_data
  description: Retrieve AWS Cost Explorer data
  inputSchema:
    type: object
    properties:
      account_id:
        type: string
      start_date:
        type: string
        format: date
      end_date:
        type: string
        format: date
      granularity:
        type: string
        enum: [DAILY, MONTHLY]
    required: [start_date, end_date]
```

## Response Time Requirements

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| Simple query | 500ms | 1s | 2s |
| Aggregation | 1s | 2s | 3s |
| Cross-cloud | 2s | 4s | 5s |

## References

- [ADR-001: Use MCP Servers](../adr/001-use-mcp-servers.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
