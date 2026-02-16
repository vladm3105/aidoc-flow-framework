# System Architecture

## Architecture Diagram

<img src="system-architecture.svg" alt="System Architecture" width="100%" />

## Overview

The AI Cost Monitoring platform is designed as a **cloud-native, serverless, and multi-cloud** solution. It leverages modern AI agent patterns (MCP) and separates the data plane from the control plane.

## Key Components

### 1. User Interface Layer
- **Grafana Dashboards**: Primary interface for visualizing cost metrics, trends, and alerts. Best for quick operational monitoring.
- **AG-UI Chat Interface**: Conversational AI interface built with Next.js and CopilotKit. Best for ad-hoc queries, root cause analysis, and complex reasoning ("Why did my bill go up?").

### 2. Application Layer (Control Plane)
Hosted on **Cloud Run** (or AWS Fargate / Azure Container Apps) for serverless scalability.

- **Unified API Gateway**: FastAPI-based backend that handles authentication (Auth0), rate limiting, and request routing.
- **AI Agent Coordinator**: The "brain" of the system. Uses Google ADK and LiteLLM to interpret user intents and route tasks to specialized agents.
- **MCP Server Layer**: Standardized [Model Context Protocol](https://modelcontextprotocol.io/) servers that act as tools for the AI agents.
  - **GCP Cost MCP**: Queries BigQuery billing export.
  - **AWS Cost MCP**: Queries AWS Cost Explorer API.
  - **Azure Cost MCP**: Queries Azure Cost Management API.

### 3. Data & Infrastructure Layer (Data Plane)
- **BigQuery (or Athena/Synapse)**: The core analytics engine. Ingests raw billing data from all clouds and normalizes it into a unified schema. This is the source of truth for all cost metrics.
- **Cloud SQL (PostgreSQL)**: Stores application metadata, user profiles, tenant configurations, and RBAC policies.
- **Cloud Tasks**: Managed asynchronous job queue for long-running reports, data ingestion jobs, and alert processing. Replaces traditional Celery/Redis infrastructure.

### 4. Integration Layer (Monitored Clouds)
The platform connects to external cloud providers (AWS, Azure, GCP) via read-only APIs to fetch:
- Billing data
- Resource inventory
- Utilization metrics (for idle resource detection)

## Design Principles

1. **Cloud Agnostic Core**: While the "home cloud" hosts the infrastructure (e.g., GCP), the logic is designed to monitor *any* cloud.
2. **Serverless First**: No managing Kubernetes clusters or VMs. Uses managed services (Cloud Run, Cloud SQL, BigQuery) to minimize operational overhead.
3. **Data Gravity**: We bring analysis to the data. Billing data is massive; we use cloud-native data warehouses (BigQuery) rather than pulling everything into application memory.
4. **AI as a First-Class Citizen**: The architecture is built around AI agents using the MCP standard, making the system extensible and intelligent by default.

## Deployment

See the deployment guides for hosting this architecture:
- [GCP Deployment](../../GCP-DEPLOYMENT.md)
- [AWS Deployment](../../AWS-DEPLOYMENT.md)
- [Azure Deployment](../../AZURE-DEPLOYMENT.md)
