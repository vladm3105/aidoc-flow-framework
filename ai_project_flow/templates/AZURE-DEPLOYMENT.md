# Azure Deployment Guide

This guide walks you through deploying the AI Cloud Cost Monitoring platform to Microsoft Azure using Azure Container Apps as the home cloud.

> [!NOTE]
> This is a **template guide**. The platform is currently optimized for GCP deployment. Azure deployment patterns are provided here for reference and future implementation.

## Table of Contents

- [Service Stack Mapping](#service-stack-mapping)
- [Prerequisites](#prerequisites)
- [Infrastructure Overview](#infrastructure-overview)
- [Deployment Pattern](#deployment-pattern)
- [Configuration](#configuration)
- [Cost Estimates](#cost-estimates)

---

## Service Stack Mapping

### GCP → Azure Service Equivalents

| Component | GCP Service | Azure Service | Notes |
|-----------|-------------|---------------|-------|
| **Containers** | Cloud Run | **Azure Container Apps** | Serverless, similar to Cloud Run |
| **Relational DB** | Cloud SQL PostgreSQL | **Azure Database for PostgreSQL** | Managed PostgreSQL |
| **Analytics DB** | BigQuery | **Azure Synapse Analytics** (Serverless SQL) | Or Databricks for complex analytics |
| **Object Storage** | Cloud Storage | **Azure Blob Storage** | Direct equivalent |
| **Secrets** | Secret Manager | **Azure Key Vault** | Direct equivalent |
| **Task Queue** | Cloud Tasks | **Azure Service Bus + Functions** | Service Bus for queues, Functions for workers |
| **Scheduler** | Cloud Scheduler | **Azure Functions** (Timer Trigger) | Native timer-based execution |
| **Cache (optional)** | Memorystore Redis | **Azure Cache for Redis** | Direct equivalent |
| **Container Registry** | GCR / Artifact Registry | **Azure Container Registry (ACR)** | Direct equivalent |
| **VPC/Networking** | VPC Connector | **Virtual Network (VNet)** | Native VNet integration |

---

## Prerequisites

### Required Tools

- **Azure CLI** - [Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Terraform** v1.6+ - [Install](https://www.terraform.io/downloads)
- **Docker** - [Install](https://docs.docker.com/get-docker/)
- **Git** - [Install](https://git-scm.com/downloads)

### Required Permissions

Azure RBAC roles:
- `Contributor` (on resource group) OR specific roles:
  - `Azure Container Apps Contributor`
  - `PostgreSQL Flexible Server Administrator`
  - `Storage Blob Data Contributor`
  - `Key Vault Administrator`
  - `Service Bus Data Owner`

### Azure Account Requirements

- Azure subscription with billing enabled
- Resource Group created
- Azure AD for authentication (optional, can use Auth0)

---

## Infrastructure Overview

### Architecture on Azure

```
Internet
    ↓
Azure Application Gateway or Front Door
    ↓
Azure Container Apps (Frontend + Backend)
    ↓
├── Azure Database for PostgreSQL (VNet, private endpoint)
├── Azure Synapse Analytics (Serverless SQL for analytics)
├── Service Bus + Functions (Background tasks)
├── Key Vault (Credentials)
└── Azure Cache for Redis (Optional cache)
```

---

## Deployment Pattern

### 1. Initial Setup

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "<subscription-id>"

# Create resource group
export RESOURCE_GROUP="ai-cost-monitoring-rg"
export LOCATION="eastus"
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### 2. Infrastructure Deployment (via Terraform)

**Terraform structure** (to be created):

```hcl
# terraform/azure/main.tf

# Resource Group (or reference existing)
resource "azurerm_resource_group" "main" {
  name     = "ai-cost-monitoring-rg"
  location = "East US"
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  # ...
}

# Azure Database for PostgreSQL
resource "azurerm_postgresql_flexible_server" "main" {
  name                = "ai-cost-monitoring-db"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  version             = "16"
  sku_name            = "B_Standard_B1ms"  # MVP
  # ...
}

# Azure Blob Storage
resource "azurerm_storage_account" "main" {
  # ...
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                = "ai-cost-monitoring-kv"
  # ...
}

# Container Apps Environment
resource "azurerm_container_app_environment" "main" {
  name                = "ai-cost-monitoring-env"
  # ...
}

# Container Apps (Frontend, Backend)
resource "azurerm_container_app" "backend" {
  name                         = "backend"
  container_app_environment_id = azurerm_container_app_environment.main.id
  # ...
}

# Service Bus Namespace and Queue
resource "azurerm_servicebus_namespace" "main" {
  # ...
}

# Azure Functions (for scheduled tasks)
resource "azurerm_linux_function_app" "scheduler" {
  # ...
}
```

### 3. Container Deployment

```bash
# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP \
  --name aicostmonitoringacr \
  --sku Basic

# Login to ACR
az acr login --name aicostmonitoringacr

# Build and push
docker build -t aicostmonitoringacr.azurecr.io/frontend:latest ./frontend
docker push aicostmonitoringacr.azurecr.io/frontend:latest

docker build -t aicostmonitoringacr.azurecr.io/backend:latest ./backend
docker push aicostmonitoringacr.azurecr.io/backend:latest

# Deploy Container Apps (via Terraform or Azure CLI)
az containerapp create \
  --name backend \
  --resource-group $RESOURCE_GROUP \
  --environment ai-cost-monitoring-env \
  --image aicostmonitoringacr.azurecr.io/backend:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 10
```

---

## Configuration

### Environment Variables

Key differences from GCP:

```bash
# Azure-specific
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=ai-cost-monitoring-rg

# Database (Azure PostgreSQL)
DATABASE_HOST=ai-cost-monitoring-db.postgres.database.azure.com
DATABASE_PORT=5432

# Analytics (Azure Synapse)
SYNAPSE_WORKSPACE=ai-cost-monitoring-synapse
SYNAPSE_SQL_ENDPOINT=<synapse-endpoint>.sql.azuresynapse.net

# Secrets (Key Vault)
KEY_VAULT_NAME=ai-cost-monitoring-kv

# Task Queue (Service Bus)
SERVICE_BUS_CONNECTION_STRING=<connection-string>
SERVICE_BUS_QUEUE_NAME=tasks

# Cache (Azure Cache for Redis) - optional
REDIS_HOST=<redis-name>.redis.cache.windows.net
REDIS_PORT=6380  # SSL port
REDIS_SSL=true
```

### Managed Identity

Azure Container Apps can use **Managed Identity** to access:
- Azure Database for PostgreSQL
- Key Vault
- Storage Account
- Service Bus

```bash
# Enable managed identity for Container App
az containerapp identity assign \
  --name backend \
  --resource-group $RESOURCE_GROUP \
  --system-assigned

# Grant access to Key Vault
az keyvault set-policy \
  --name ai-cost-monitoring-kv \
  --object-id <managed-identity-principal-id> \
  --secret-permissions get list
```

---

## Cost Estimates

### MVP Deployment (Single Tenant)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **Container Apps** | 0.5 vCPU, 1GB RAM, 2 apps | ~$35 |
| **PostgreSQL Flexible** | B_Standard_B1ms | ~$12 |
| **Synapse Serverless SQL** | ~10GB scanned/month | ~$5 |
| **Blob Storage** | 100GB Standard | ~$2 |
| **Key Vault** | 5 secrets, 1000 operations | ~$1 |
| **Service Bus** | Basic tier | ~$0.05 |
| **Data Transfer** | 10GB/month | ~$1 |
| **Total (MVP)** | | **~$55-65/month** |

### Production Deployment

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **Container Apps** | 2 vCPU, 4GB RAM, 5 apps | ~$175 |
| **PostgreSQL Flexible** | GP_Standard_D4s_v3 (HA) | ~$250 |
| **Synapse Serverless SQL** | 100GB scanned/month | ~$50 |
| **Blob Storage** | 500GB Standard | ~$10 |
| **Azure Cache for Redis** | C1 Standard (optional) | ~$75 |
| **Application Gateway** | WAF v2 | ~$30 |
| **Monitor Logs** | 10GB/month | ~$5 |
| **Total (Production)** | | **~$595-650/month** |

---

## Next Steps

To implement Azure deployment:

1. ✅ Review this service mapping
2. ⬜ Create Terraform modules in `terraform/azure/`
3. ⬜ Adapt application code for Azure services (Azure SDK for Synapse, Service Bus, Key Vault)
4. ⬜ Create Container App definitions
5. ⬜ Set up CI/CD pipeline (Azure DevOps or GitHub Actions)
6. ⬜ Configure Managed Identity for passwordless authentication
7. ⬜ Test full deployment
8. ⬜ Expand this guide with actual deployment commands

---

## Resources

- **Main README**: [README.md](README.md) - Architecture overview
- **GCP Deployment**: [GCP-DEPLOYMENT.md](GCP-DEPLOYMENT.md) - Reference implementation
- **Azure Container Apps**: https://learn.microsoft.com/en-us/azure/container-apps/
- **Azure Terraform Provider**: https://registry.terraform.io/providers/hashicorp/azurerm/

---

*This is a template guide. Contributions and improvements based on actual Azure deployments are welcome!*
