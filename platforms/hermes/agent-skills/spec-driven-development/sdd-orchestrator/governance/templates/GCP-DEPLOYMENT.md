# GCP Deployment Guide

This guide walks you through deploying the AI Cloud Cost Monitoring platform to Google Cloud Platform using Cloud Run.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Infrastructure Deployment](#infrastructure-deployment)
- [Application Deployment](#application-deployment)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **gcloud CLI** - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform** v1.6+ - [Install](https://www.terraform.io/downloads)
- **Docker** - [Install](https://docs.docker.com/get-docker/)
- **Git** - [Install](https://git-scm.com/downloads)

### Required Permissions

You need the following IAM roles in your GCP project:

- `roles/owner` OR all of:
  - `roles/run.admin` - Deploy Cloud Run services
  - `roles/cloudsql.admin` - Manage Cloud SQL
  - `roles/redis.admin` - Manage Memorystore
  - `roles/iam.serviceAccountAdmin` - Create service accounts
  - `roles/secretmanager.admin` - Manage secrets
  - `roles/storage.admin` - Manage Cloud Storage

### GCP Project Requirements

- **GCP Project** with billing enabled
- **Organization** (optional but recommended for multi-tenant)
- **Billing Account** linked to the project

---

## Initial Setup

### 1. Clone Repository

```bash
git clone https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}.git
cd {REPO_NAME}
```

### 2. Configure gcloud

```bash
# Login to GCP
gcloud auth login

# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
chmod +x scripts/enable-gcp-apis.sh
./scripts/enable-gcp-apis.sh
```

### 3. Create Service Account

```bash
# Create service account for Cloud Run
gcloud iam service-accounts create ai-cost-monitoring-sa \
    --display-name="AI Cost Monitoring Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:ai-cost-monitoring-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:ai-cost-monitoring-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:ai-cost-monitoring-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

**Critical Values to Update:**

- `GCP_PROJECT_ID` - Your GCP project ID
- `AUTH0_DOMAIN` - Your Auth0 tenant domain
- `DATABASE_PASSWORD` - Generate a strong password
- `REDIS_PASSWORD` - Generate a strong password
- `SECRET_KEY` - Generate with `openssl rand -hex 32`

---

## Infrastructure Deployment

### Option A: Terraform (Recommended)

```bash
cd terraform

# Initialize Terraform
terraform init

# Review the planned changes
terraform plan

# Apply infrastructure
terraform apply

# Note the output values (database IP, Redis IP, etc.)
terraform output
```

### Option B: Manual Setup

#### 1. Create Cloud SQL Instance

```bash
gcloud sql instances create ai-cost-monitoring-db \
    --database-version=POSTGRES_16 \
    --tier=db-custom-1-3840 \
    --region=us-central1 \
    --network=default \
    --no-assign-ip

# Create database
gcloud sql databases create ai_cost_monitoring \
    --instance=ai-cost-monitoring-db

# Set password
gcloud sql users set-password postgres \
    --instance=ai-cost-monitoring-db \
    --password="YOUR_SECURE_PASSWORD"
```

#### 2. Create Redis Instance

```bash
gcloud redis instances create ai-cost-monitoring-cache \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0
```

#### 3. Create Secrets

```bash
# Auth0 Client Secret
echo -n "your-auth0-client-secret" | \
    gcloud secrets create auth0-client-secret --data-file=-

# Database Password
echo -n "your-database-password" | \
    gcloud secrets create database-password --data-file=-

# Redis Password (if using AUTH)
echo -n "your-redis-password" | \
    gcloud secrets create redis-auth --data-file=-

# Google API Key (for Gemini)
echo -n "your-google-api-key" | \
    gcloud secrets create google-api-key --data-file=-
```

---

## Application Deployment

### 1. Build Container Images

```bash
# Build frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/frontend ./frontend

# Build backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/backend ./backend

# Build MCP server
gcloud builds submit --tag gcr.io/$PROJECT_ID/gcp-mcp-server ./components/mcp-servers/gcp
```

### 2. Deploy Backend to Cloud Run

```bash
gcloud run deploy ai-cost-monitoring-backend \
    --image gcr.io/$PROJECT_ID/backend \
    --platform managed \
    --region us-central1 \
    --service-account ai-cost-monitoring-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars GCP_PROJECT_ID=$PROJECT_ID \
    --set-secrets DATABASE_PASSWORD=database-password:latest,AUTH0_CLIENT_SECRET=auth0-client-secret:latest \
    --add-cloudsql-instances $PROJECT_ID:us-central1:ai-cost-monitoring-db \
    --vpc-connector projects/$PROJECT_ID/locations/us-central1/connectors/default \
    --memory 1Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 20 \
    --timeout 60s \
    --allow-unauthenticated
```

### 3. Deploy Frontend to Cloud Run

```bash
gcloud run deploy ai-cost-monitoring-frontend \
    --image gcr.io/$PROJECT_ID/frontend \
    --platform managed \
    --region us-central1 \
    --set-env-vars NEXT_PUBLIC_BACKEND_URL=https://ai-cost-monitoring-backend-<hash>-uc.a.run.app \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --allow-unauthenticated
```

### 4. Deploy MCP Server to Cloud Run

```bash
gcloud run deploy gcp-cost-mcp-server \
    --image gcr.io/$PROJECT_ID/gcp-mcp-server \
    --platform managed \
    --region us-central1 \
    --service-account ai-cost-monitoring-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --no-allow-unauthenticated  # Only accessible by backend
```

---

## Configuration

### 1. Database Migration

```bash
# Get Cloud SQL connection name
gcloud sql instances describe ai-cost-monitoring-db --format="value(connectionName)"

# Run migrations via Cloud SQL Proxy
cloud_sql_proxy -instances=<CONNECTION_NAME>=tcp:5432 &

# Run Alembic migrations
cd backend
alembic upgrade head
```

### 2. Auth0 Configuration

1. Go to [Auth0 Dashboard](https://manage.auth0.com)
2. Create a new Application (Regular Web Application)
3. Configure:
   - **Allowed Callback URLs**: `https://your-frontend-url/api/auth/callback`
   - **Allowed Logout URLs**: `https://your-frontend-url`
   - **Allowed Web Origins**: `https://your-frontend-url`
4. Update `.env` with Auth0 credentials

### 3. Budget Alerts

```bash
# Create budget
gcloud billing budgets create \
    --billing-account=<BILLING_ACCOUNT_ID> \
    --display-name="AI Cost Monitoring Budget" \
    --budget-amount=500 \
    --threshold-rule=percent=0.5 \
    --threshold-rule=percent=0.8 \
    --threshold-rule=percent=1.0
```

---

## Verification

### 1. Check Service Health

```bash
# Get service URLs
gcloud run services list --platform managed

# Test backend health endpoint
curl https://<BACKEND_URL>/health

# Test frontend
curl https://<FRONTEND_URL>
```

### 2. Verify Database Connection

```bash
# SSH into Cloud Run instance (requires additional setup)
# Or check logs
gcloud run services logs read ai-cost-monitoring-backend --limit=50
```

### 3. Monitor Costs

```bash
# View current month costs
gcloud billing accounts describe <BILLING_ACCOUNT_ID>

# Check Cloud Run usage
gcloud run services describe ai-cost-monitoring-backend \
    --region us-central1 \
    --format="value(status.observedGeneration)"
```

---

## Troubleshooting

### Common Issues

#### 1. Cloud Run Service Won't Start

**Symptom**: Service shows "Revision failed"

**Solutions**:

```bash
# Check logs
gcloud run services logs read ai-cost-monitoring-backend --limit=100

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Memory/CPU limits too low
```

#### 2. Database Connection Errors

**Symptom**: "Connection refused" or "Could not connect to Cloud SQL"

**Solutions**:

```bash
# Verify Cloud SQL instance is running
gcloud sql instances describe ai-cost-monitoring-db

# Check VPC connector
gcloud compute networks vpc-access connectors list --region us-central1

# Ensure service account has cloudsql.client role
```

#### 3. Authentication Failures

**Symptom**: "Unauthorized" or Auth0 errors

**Solutions**:

- Verify Auth0 callback URLs match exactly
- Check that secrets are properly set
- Ensure `AUTH0_AUDIENCE` matches your API identifier

#### 4. High Cold Start Latency

**Symptom**: First request takes 5-10 seconds

**Solutions**:

```bash
# Set minimum instances to 1
gcloud run services update ai-cost-monitoring-backend \
    --min-instances 1 \
    --region us-central1
```

---

## CI/CD Integration

### GitHub Actions Example

> Note: This snippet follows the GitHub.com baseline from `governance/GOVERNANCE_RULES.md` §2a. Marketplace actions and `ubuntu-latest` are allowed when pinned and reviewed.

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}
          service_account: ${{ secrets.GCP_WIF_SERVICE_ACCOUNT }}
      
      - name: Deploy Backend
        run: |
          gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/backend ./backend
          gcloud run deploy ai-cost-monitoring-backend \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/backend \
            --region us-central1
```

---

## Cost Optimization Tips

1. **Use Minimum Instances Wisely**
   - Set `min-instances=0` for dev/staging
   - Set `min-instances=1` only for production critical services

2. **Enable Request Logging Sampling**

   ```bash
   gcloud run services update ai-cost-monitoring-backend \
       --no-cpu-throttling \
       --region us-central1
   ```

3. **Set Appropriate Timeouts**
   - Default 60s is often too high
   - Reduce to 30s for API endpoints

4. **Monitor BigQuery Costs**
   - Use partitioning for cost_metrics table
   - Set up query cost alerts

---

## Support & Resources

- **Documentation**: [docs/](docs/)
- **ADRs**: [docs/adr/](docs/adr/)
- **Cloud Run Docs**: <https://cloud.google.com/run/docs>
- **Terraform Docs**: [terraform/README.md](terraform/README.md)

---

## Next Steps

1. [PASS] Deploy infrastructure
2. [PASS] Deploy application services
3. Configure monitoring dashboards
4. Set up automated backups
5. Configure custom domain
6. Enable HTTPS with SSL certificate
7. Set up CI/CD pipeline
8. Load test and optimize
