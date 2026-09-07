# GCP Setup Scripts

Setup scripts for configuring Google Cloud Platform infrastructure for GitHub Actions CI/CD.

## Prerequisites

- Google Cloud CLI installed and authenticated (`gcloud auth login`)
- Appropriate IAM permissions (Project Creator, IAM Admin)
- GitHub repository created

## Scripts

| Script | Purpose |
|--------|---------|
| `setup-projects.sh` | Create GCP projects (dev, staging, prod) |
| `setup-wif.sh` | Configure Workload Identity Federation for GitHub Actions |
| `setup_artifact_registry.sh` | Create Artifact Registry for container images |
| `setup-environments.sh` | Configure GitHub environments with GCP secrets |
| `setup-ai-review-gcp.sh` | Set up GCP resources for AI PR review |
| `configure_revision_retention.sh` | Set Cloud Run revision retention policy |

## Usage

### 1. Create GCP Projects

```bash
# Edit the script to set your values
nano setup-projects.sh

# Run the script
./setup-projects.sh
```

**Configuration variables:**

- `PROJECT_PREFIX` - Project identifier (e.g., `myproj`)
- `BILLING_ACCOUNT` - Your GCP billing account ID
- `ORG_ID` - Your GCP organization ID

**Output:**

- `{PROJECT_PREFIX}-dev` project
- `{PROJECT_PREFIX}-staging` project
- `{PROJECT_PREFIX}-prod` project

### 2. Configure Workload Identity Federation

This script sets up OIDC-based authentication so GitHub Actions can authenticate to GCP without storing service account keys.

```bash
# Edit the script to set your values
nano setup-wif.sh

# Run the script
./setup-wif.sh
```

**Configuration variables:**

- `GCP_PROJECT_DEV` - Dev project ID
- `GCP_PROJECT_STAGING` - Staging project ID
- `GCP_PROJECT_PROD` - Prod project ID
- `GITHUB_ORG` - Your GitHub organization
- `REPO_NAME` - Your repository name
- `WIF_POOL_NAME` - Workload Identity pool name
- `WIF_PROVIDER_NAME` - Workload Identity provider name

**Output:**

- Workload Identity pool and provider
- Service account with appropriate roles
- WIF credentials JSON for each environment

### 3. Create Artifact Registry

```bash
./setup_artifact_registry.sh
```

**Output:**

- Docker repository in Artifact Registry
- Push permissions for service accounts

### 4. Configure GitHub Environments

```bash
./setup-environments.sh
```

**Output:**

- GitHub environments (dev, staging, production)
- Environment secrets (WIF_CREDENTIALS_*, GCP_PROJECT_*)

## GitHub Secrets

After running the scripts, these secrets will be configured:

| Secret | Value | Environment |
|--------|-------|-------------|
| `WIF_CREDENTIALS_DEV` | WIF JSON | dev |
| `WIF_CREDENTIALS_STAGING` | WIF JSON | staging |
| `WIF_CREDENTIALS_PROD` | WIF JSON | production |
| `GCP_PROJECT_DEV` | Project ID | Repository |
| `GCP_PROJECT_STAGING` | Project ID | Repository |
| `GCP_PROJECT_PROD` | Project ID | Repository |

## Troubleshooting

### Workload Identity Federation Error

1. Verify pool exists: `gcloud iam workload-identity-pools list --location global`
2. Check provider configuration: `gcloud iam workload-identity-pools providers describe`
3. Ensure attribute mapping is correct for GitHub OIDC

### Artifact Registry Push Denied

1. Verify service account has `roles/artifactregistry.writer`
2. Check repository exists in correct region
3. Ensure docker is configured: `gcloud auth configure-docker`

### IAM Permission Denied

1. Check you have Owner or IAM Admin role on the project
2. Verify project ID is correct
3. Run `gcloud auth list` to verify active account

## Cleanup

To remove resources created by these scripts:

```bash
# Delete Artifact Registry repository (WARNING: deletes all images)
gcloud artifacts repositories delete {PROJECT_PREFIX} \
  --location={GCP_REGION} --project={GCP_PROJECT_DEV}

# Delete WIF pool
gcloud iam workload-identity-pools delete {WIF_POOL_NAME} \
  --location=global --project={GCP_PROJECT_DEV}

# Delete projects (WARNING: irreversible)
gcloud projects delete {PROJECT_PREFIX}-dev
gcloud projects delete {PROJECT_PREFIX}-staging
gcloud projects delete {PROJECT_PREFIX}-prod
```

## Additional Resources

- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub OIDC with GCP](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-google-cloud-platform)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)
