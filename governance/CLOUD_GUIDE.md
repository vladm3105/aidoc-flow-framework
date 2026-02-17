# Cloud Provider Guide

This guide covers cloud provider setup for the AI-First Project Governance Framework. Choose one or more providers based on your requirements.

## Provider Comparison

| Feature | GCP | AWS | Azure |
|---------|-----|-----|-------|
| **Container Service** | Cloud Run | ECS/Fargate | Container Apps |
| **Container Registry** | Artifact Registry | ECR | ACR |
| **OIDC Auth** | Workload Identity Federation | IAM OIDC | Managed Identity |
| **Setup Scripts** | [PASS] Included | [WARN] Template only | [WARN] Template only |
| **Workflow Support** | [PASS] Full | [PASS] Full | [PASS] Full |

---

## GCP Setup

GCP is the primary supported cloud provider with full automation scripts.

### Prerequisites

- GCP Organization with billing enabled
- `gcloud` CLI installed and authenticated
- Organization-level permissions for project creation

### Step 1: Create GCP Projects

```bash
cd governance/scripts/project_setup/cloud/gcp

# Edit variables at the top of the script
nano setup-projects.sh

# Required variables:
# PROJECT_PREFIX="your-prefix"
# BILLING_ACCOUNT="XXXXXX-XXXXXX-XXXXXX"
# ORG_ID="123456789"

# Run the script
./setup-projects.sh
```

This creates three projects:
- `{PROJECT_PREFIX}-dev`
- `{PROJECT_PREFIX}-staging`
- `{PROJECT_PREFIX}-prod`

### Step 2: Set Up Workload Identity Federation

```bash
# Edit variables
nano setup-wif.sh

# Required variables:
# GITHUB_ORG="your-org"
# GITHUB_REPO="your-repo"
# GITHUB_HOST="github.com"  # or your GHES host

# Run the script
./setup-wif.sh
```

This configures:
- Workload Identity Pool: `{WIF_POOL_NAME}`
- OIDC Provider: `{WIF_PROVIDER_NAME}`
- Service accounts for CI/CD

### Step 3: Set Up Artifact Registry

```bash
./setup_artifact_registry.sh
```

Creates Docker repositories in each environment.

### Step 4: Configure Environments

```bash
./setup-environments.sh
```

Sets up:
- Cloud Run services
- IAM permissions
- Environment-specific configurations

### Step 5: Add GitHub Secrets

```bash
GH_HOST={GITHUB_HOST} gh secret set GCP_PROJECT_DEV --body "{PROJECT_PREFIX}-dev"
GH_HOST={GITHUB_HOST} gh secret set GCP_PROJECT_STAGING --body "{PROJECT_PREFIX}-staging"
GH_HOST={GITHUB_HOST} gh secret set GCP_PROJECT_PROD --body "{PROJECT_PREFIX}-prod"
GH_HOST={GITHUB_HOST} gh secret set GCP_REGION --body "{GCP_REGION}"
GH_HOST={GITHUB_HOST} gh secret set WIF_PROVIDER --body "projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/{WIF_POOL_NAME}/providers/{WIF_PROVIDER_NAME}"
GH_HOST={GITHUB_HOST} gh secret set WIF_SA_EMAIL_DEV --body "github-actions@{PROJECT_PREFIX}-dev.iam.gserviceaccount.com"
GH_HOST={GITHUB_HOST} gh secret set WIF_SA_EMAIL_STAGING --body "github-actions@{PROJECT_PREFIX}-staging.iam.gserviceaccount.com"
GH_HOST={GITHUB_HOST} gh secret set WIF_SA_EMAIL_PROD --body "github-actions@{PROJECT_PREFIX}-prod.iam.gserviceaccount.com"
```

### GCP Workflow Configuration

The deployment workflows are pre-configured for GCP. Update these placeholders:

```yaml
# .github/workflows/deploy-dev.yml
env:
  GCP_PROJECT: ${{ secrets.GCP_PROJECT_DEV }}
  GCP_REGION: ${{ secrets.GCP_REGION }}
  SERVICE_NAME: {SERVICE_NAME}
```

---

## AWS Setup

AWS support is provided through workflow templates. Setup scripts are not yet included.

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- GitHub OIDC provider configured in AWS IAM

### Step 1: Create OIDC Provider

```bash
# Create OIDC provider for GitHub Actions
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1"
```

### Step 2: Create IAM Role

```bash
# Create trust policy
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::{AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:{GITHUB_ORG}/{REPO_NAME}:*"
        }
      }
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name github-actions-{PROJECT_PREFIX} \
  --assume-role-policy-document file://trust-policy.json

# Attach policies (customize as needed)
aws iam attach-role-policy \
  --role-name github-actions-{PROJECT_PREFIX} \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

aws iam attach-role-policy \
  --role-name github-actions-{PROJECT_PREFIX} \
  --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess
```

### Step 3: Create ECR Repository

```bash
aws ecr create-repository \
  --repository-name {PROJECT_PREFIX}/{SERVICE_NAME} \
  --region {AWS_REGION}
```

### Step 4: Add GitHub Secrets

```bash
GH_HOST={GITHUB_HOST} gh secret set AWS_ACCOUNT_ID --body "{AWS_ACCOUNT_ID}"
GH_HOST={GITHUB_HOST} gh secret set AWS_REGION --body "{AWS_REGION}"
GH_HOST={GITHUB_HOST} gh secret set AWS_ROLE_ARN --body "arn:aws:iam::{AWS_ACCOUNT_ID}:role/github-actions-{PROJECT_PREFIX}"
```

### AWS Workflow Template

Create or modify `.github/workflows/deploy-aws.yml`:

```yaml
name: Deploy to AWS

on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/{SERVICE_NAME}:$IMAGE_TAG .
          docker push $ECR_REGISTRY/{SERVICE_NAME}:$IMAGE_TAG

      # Add ECS/Fargate deployment steps as needed
```

---

## Azure Setup

Azure support is provided through workflow templates. Setup scripts are not yet included.

### Prerequisites

- Azure subscription
- Azure CLI installed and authenticated
- Service principal or managed identity configured

### Step 1: Create Service Principal

```bash
# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "github-actions-{PROJECT_PREFIX}" \
  --role Contributor \
  --scopes /subscriptions/{AZURE_SUBSCRIPTION_ID} \
  --sdk-auth
```

Save the output JSON for GitHub secrets.

### Step 2: Configure Federated Credentials

```bash
# Get app object ID
APP_ID=$(az ad app list --display-name "github-actions-{PROJECT_PREFIX}" --query "[0].id" -o tsv)

# Create federated credential
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:{GITHUB_ORG}/{REPO_NAME}:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### Step 3: Create Container Registry

```bash
az acr create \
  --resource-group {AZURE_RESOURCE_GROUP} \
  --name {PROJECT_PREFIX}acr \
  --sku Basic
```

### Step 4: Add GitHub Secrets

```bash
GH_HOST={GITHUB_HOST} gh secret set AZURE_SUBSCRIPTION_ID --body "{AZURE_SUBSCRIPTION_ID}"
GH_HOST={GITHUB_HOST} gh secret set AZURE_TENANT_ID --body "{AZURE_TENANT_ID}"
GH_HOST={GITHUB_HOST} gh secret set AZURE_CLIENT_ID --body "{AZURE_CLIENT_ID}"
```

### Azure Workflow Template

Create or modify `.github/workflows/deploy-azure.yml`:

```yaml
name: Deploy to Azure

on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Login to ACR
        run: |
          az acr login --name {PROJECT_PREFIX}acr

      - name: Build and push
        run: |
          docker build -t {ACR_REGISTRY}/{SERVICE_NAME}:${{ github.sha }} .
          docker push {ACR_REGISTRY}/{SERVICE_NAME}:${{ github.sha }}

      # Add Container Apps deployment steps as needed
```

---

## Multi-Cloud Configuration

If using multiple cloud providers, you can:

1. **Separate workflows per provider**
   - `deploy-gcp.yml`, `deploy-aws.yml`, `deploy-azure.yml`

2. **Environment-based routing**
   - Dev on GCP, Staging on AWS, Prod on Azure

3. **Conditional deployment**
   ```yaml
   jobs:
     deploy-gcp:
       if: vars.CLOUD_PROVIDER == 'gcp'
     deploy-aws:
       if: vars.CLOUD_PROVIDER == 'aws'
   ```

---

## Secrets Summary

### GCP Secrets
| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_DEV` | Dev project ID |
| `GCP_PROJECT_STAGING` | Staging project ID |
| `GCP_PROJECT_PROD` | Prod project ID |
| `GCP_REGION` | GCP region |
| `WIF_PROVIDER` | Full WIF provider path |
| `WIF_SA_EMAIL_DEV` | Dev service account |
| `WIF_SA_EMAIL_STAGING` | Staging service account |
| `WIF_SA_EMAIL_PROD` | Prod service account |

### AWS Secrets
| Secret | Description |
|--------|-------------|
| `AWS_ACCOUNT_ID` | AWS account ID |
| `AWS_REGION` | AWS region |
| `AWS_ROLE_ARN` | GitHub Actions IAM role ARN |

### Azure Secrets
| Secret | Description |
|--------|-------------|
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_CLIENT_ID` | Service principal client ID |

---

## Troubleshooting

### GCP: WIF Authentication Fails

1. Verify pool/provider names match
2. Check GitHub repository is allowed in provider conditions
3. Ensure service account has required permissions

### AWS: AssumeRoleWithWebIdentity Fails

1. Verify OIDC provider thumbprint
2. Check trust policy subject condition
3. Ensure role has required policies attached

### Azure: Federated Credential Issues

1. Verify issuer URL is correct
2. Check subject matches your repository/branch
3. Ensure app registration has required permissions
