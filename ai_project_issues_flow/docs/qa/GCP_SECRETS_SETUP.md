# GCP Secrets Setup Guide

This document explains how to configure GCP-related secrets for the phase-gated deployment workflows (IPLAN-011).

---

## Current Status ({DATE})

### Completed

| Component | {GCP_PROJECT_DEV} | {GCP_PROJECT_STAGING} |
|:----------|:-----------|:---------------|
| Project ID | `{GCP_PROJECT_DEV}` | `{GCP_PROJECT_STAGING}` |
| Project Number | `598301317494` | `279365414295` |
| WIF Pool | `github-pool` | `github-pool` |
| OIDC Provider | `{WIF_PROVIDER_NAME}` | `{WIF_PROVIDER_NAME}` |
| Service Account | `{GCP_PROJECT_DEV}-sa@{GCP_PROJECT_DEV}.iam.gserviceaccount.com` | `{GCP_PROJECT_STAGING}-sa@{GCP_PROJECT_STAGING}.iam.gserviceaccount.com` |
| IAM Roles | `run.admin`, `artifactregistry.writer`, `iam.serviceAccountUser` | Same |
| WIF Binding | Bound to repository | Bound to repository |

### GitHub Secrets (Configured)

| Secret | Value | Status |
|:-------|:------|:-------|
| `GCP_PROJECT_DEV` | `{GCP_PROJECT_DEV}` | Ready |
| `GCP_PROJECT_STAGING` | `{GCP_PROJECT_STAGING}` | Ready |
| `WIF_CREDENTIALS_DEV` | `projects/598301317494/locations/global/workloadIdentityPools/github-pool/providers/{WIF_PROVIDER_NAME}` | Ready |
| `WIF_CREDENTIALS_STAGING` | `projects/279365414295/locations/global/workloadIdentityPools/github-pool/providers/{WIF_PROVIDER_NAME}` | Ready |
| `TEAMS_WEBHOOK` | Placeholder | **Needs update** |
| `ELEVATED_PAT` | (existing) | Ready |
| `PROJECT_TOKEN` | (existing) | Ready |

### Remaining Steps

The following require **billing enabled** on both GCP projects:

1. **Enable billing** on `{GCP_PROJECT_DEV}` and `{GCP_PROJECT_STAGING}` via GCP Console
2. **Enable Cloud Run API**:
   ```bash
   gcloud services enable run.googleapis.com --project={GCP_PROJECT_DEV}
   gcloud services enable run.googleapis.com --project={GCP_PROJECT_STAGING}
   ```
3. **Enable Artifact Registry API**:
   ```bash
   gcloud services enable artifactregistry.googleapis.com --project={GCP_PROJECT_DEV}
   gcloud services enable artifactregistry.googleapis.com --project={GCP_PROJECT_STAGING}
   ```
4. **Create Artifact Registry repositories**:
   ```bash
   gcloud artifacts repositories create {PROJECT_PREFIX} \
     --repository-format=docker \
     --location={GCP_REGION} \
     --project={GCP_PROJECT_DEV}

   gcloud artifacts repositories create {PROJECT_PREFIX} \
     --repository-format=docker \
     --location={GCP_REGION} \
     --project={GCP_PROJECT_STAGING}
   ```
5. **Configure Teams webhook** (see [Teams Webhook Setup](#teams-webhook-setup))

---

## Required Secrets

| Secret Name | Purpose | Format |
|:------------|:--------|:-------|
| `GCP_PROJECT_DEV` | GCP project ID for dev environment | `{GCP_PROJECT_DEV}` |
| `GCP_PROJECT_STAGING` | GCP project ID for staging environment | `{GCP_PROJECT_STAGING}` |
| `WIF_CREDENTIALS_DEV` | Workload Identity Federation credentials for dev | See [WIF Setup](#workload-identity-federation-wif) |
| `WIF_CREDENTIALS_STAGING` | Workload Identity Federation credentials for staging | See [WIF Setup](#workload-identity-federation-wif) |
| `TEAMS_WEBHOOK` | Microsoft Teams webhook URL for notifications | `https://outlook.office.com/webhook/...` |

---

## Prerequisites

1. **GCP Projects Created**: `{GCP_PROJECT_DEV}`, `{GCP_PROJECT_STAGING}`, `{GCP_PROJECT_PROD}`
2. **Billing Enabled**: Required for Cloud Run and Artifact Registry
3. **GCP CLI Installed**: `gcloud` authenticated with admin permissions
4. **GitHub CLI Installed**: `gh` authenticated with repo admin permissions

---

## Workload Identity Federation (WIF)

WIF allows GitHub Actions to authenticate to GCP without storing long-lived service account keys.

### Step 1: Enable Required APIs

```bash
for PROJECT in {GCP_PROJECT_DEV} {GCP_PROJECT_STAGING}; do
  gcloud services enable \
    iam.googleapis.com \
    iamcredentials.googleapis.com \
    cloudresourcemanager.googleapis.com \
    --project="$PROJECT"
done
```

### Step 2: Create Workload Identity Pool

```bash
PROJECT_ID="{GCP_PROJECT_DEV}"  # Repeat for {GCP_PROJECT_STAGING}

gcloud iam workload-identity-pools create "github-pool" \
  --project="$PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Actions Pool"
```

### Step 3: Create OIDC Provider

```bash
PROJECT_ID="{GCP_PROJECT_DEV}"  # Repeat for {GCP_PROJECT_STAGING}

gcloud iam workload-identity-pools providers create-oidc "{WIF_PROVIDER_NAME}" \
  --project="$PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner == '{GITHUB_ORG}'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

### Step 4: Create Service Account

```bash
# For dev
gcloud iam service-accounts create {GCP_PROJECT_DEV}-sa \
  --project={GCP_PROJECT_DEV} \
  --display-name="AI Cost Monitoring Dev Service Account"

# For staging
gcloud iam service-accounts create {GCP_PROJECT_STAGING}-sa \
  --project={GCP_PROJECT_STAGING} \
  --display-name="AI Cost Monitoring Staging Service Account"
```

### Step 5: Grant Permissions

```bash
# Dev environment
SA_EMAIL="{GCP_PROJECT_DEV}-sa@{GCP_PROJECT_DEV}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding {GCP_PROJECT_DEV} \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding {GCP_PROJECT_DEV} \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding {GCP_PROJECT_DEV} \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountUser"

# Staging environment
SA_EMAIL="{GCP_PROJECT_STAGING}-sa@{GCP_PROJECT_STAGING}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding {GCP_PROJECT_STAGING} \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding {GCP_PROJECT_STAGING} \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding {GCP_PROJECT_STAGING} \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountUser"
```

### Step 6: Bind WIF to Service Account

```bash
# Dev (project number: 598301317494)
gcloud iam service-accounts add-iam-policy-binding \
  {GCP_PROJECT_DEV}-sa@{GCP_PROJECT_DEV}.iam.gserviceaccount.com \
  --project={GCP_PROJECT_DEV} \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/598301317494/locations/global/workloadIdentityPools/github-pool/attribute.repository/{GITHUB_ORG}/{REPO_NAME}"

# Staging (project number: 279365414295)
gcloud iam service-accounts add-iam-policy-binding \
  {GCP_PROJECT_STAGING}-sa@{GCP_PROJECT_STAGING}.iam.gserviceaccount.com \
  --project={GCP_PROJECT_STAGING} \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/279365414295/locations/global/workloadIdentityPools/github-pool/attribute.repository/{GITHUB_ORG}/{REPO_NAME}"
```

### Step 7: Get WIF Credentials String

The `WIF_CREDENTIALS_*` secret value format:

```
projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-pool/providers/{WIF_PROVIDER_NAME}
```

**Current values:**

| Environment | Project Number | WIF Credentials |
|:------------|:---------------|:----------------|
| Dev | 598301317494 | `projects/598301317494/locations/global/workloadIdentityPools/github-pool/providers/{WIF_PROVIDER_NAME}` |
| Staging | 279365414295 | `projects/279365414295/locations/global/workloadIdentityPools/github-pool/providers/{WIF_PROVIDER_NAME}` |

---

## Enable Billing and APIs (Required)

Before deployments can work, billing must be enabled on the GCP projects.

### Step 1: Enable Billing

1. Go to [GCP Console](https://console.cloud.google.com)
2. Select project `{GCP_PROJECT_DEV}`
3. Navigate to **Billing** > **Link a billing account**
4. Select or create a billing account
5. Repeat for `{GCP_PROJECT_STAGING}`

### Step 2: Enable APIs

```bash
# Enable Cloud Run and Artifact Registry (requires billing)
for PROJECT in {GCP_PROJECT_DEV} {GCP_PROJECT_STAGING}; do
  gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    --project="$PROJECT"
done
```

### Step 3: Create Artifact Registry Repositories

```bash
for PROJECT in {GCP_PROJECT_DEV} {GCP_PROJECT_STAGING}; do
  gcloud artifacts repositories create {PROJECT_PREFIX} \
    --repository-format=docker \
    --location={GCP_REGION} \
    --description="AI Cost Monitoring container images" \
    --project="$PROJECT"
done
```

---

## Setting GitHub Repository Secrets

### Verify Current Secrets

```bash
GH_HOST={GITHUB_HOST} gh secret list --repo {GITHUB_ORG}/{REPO_NAME}
```

Expected output:
```
ELEVATED_PAT            Updated {DATE}
GCP_PROJECT_DEV         Updated {DATE}
GCP_PROJECT_STAGING     Updated {DATE}
PROJECT_TOKEN           Updated {DATE}
TEAMS_WEBHOOK           Updated {DATE}
WIF_CREDENTIALS_DEV     Updated {DATE}
WIF_CREDENTIALS_STAGING Updated {DATE}
```

### Update Secrets (if needed)

```bash
export GH_HOST={GITHUB_HOST}
REPO="{GITHUB_ORG}/{REPO_NAME}"

# GCP Project IDs
gh secret set GCP_PROJECT_DEV --repo "$REPO" --body "{GCP_PROJECT_DEV}"
gh secret set GCP_PROJECT_STAGING --repo "$REPO" --body "{GCP_PROJECT_STAGING}"

# WIF Credentials
gh secret set WIF_CREDENTIALS_DEV --repo "$REPO" --body "projects/598301317494/locations/global/workloadIdentityPools/github-pool/providers/{WIF_PROVIDER_NAME}"
gh secret set WIF_CREDENTIALS_STAGING --repo "$REPO" --body "projects/279365414295/locations/global/workloadIdentityPools/github-pool/providers/{WIF_PROVIDER_NAME}"

# Teams Webhook (get from Teams channel connector settings)
gh secret set TEAMS_WEBHOOK --repo "$REPO" --body "https://outlook.office.com/webhook/YOUR_WEBHOOK_URL"
```

---

## Teams Webhook Setup

1. Open Microsoft Teams
2. Navigate to the channel for deployment notifications
3. Click **...** (More options) > **Connectors**
4. Find **Incoming Webhook** and click **Configure**
5. Name it `AI Cost Monitoring Deployments`
6. Copy the webhook URL
7. Update the secret:
   ```bash
   GH_HOST={GITHUB_HOST} gh secret set TEAMS_WEBHOOK \
     --repo {GITHUB_ORG}/{REPO_NAME} \
     --body "https://outlook.office.com/webhook/YOUR_ACTUAL_WEBHOOK_URL"
   ```

---

## Workflow Usage

The secrets are used by these workflows:

| Workflow | Secrets Used |
|:---------|:-------------|
| `deploy-dev.yml` | `WIF_CREDENTIALS_DEV`, `GCP_PROJECT_DEV` |
| `deploy-staging.yml` | `WIF_CREDENTIALS_DEV` (pull), `WIF_CREDENTIALS_STAGING` (push), `GCP_PROJECT_DEV`, `GCP_PROJECT_STAGING` |
| `deploy-prod.yml` | `WIF_CREDENTIALS_STAGING` (pull), `WIF_CREDENTIALS_PROD` (push), `GCP_PROJECT_STAGING`, `GCP_PROJECT_PROD` |
| All deployment workflows | `TEAMS_WEBHOOK` (notifications) |

---

## Troubleshooting

### Error: Billing account not found

```
ERROR: FAILED_PRECONDITION: Billing account for project 'XXXXX' is not found
```

**Solution**: Enable billing on the GCP project via the GCP Console.

### Error: Permission denied to create workload identity pool

```
ERROR: PERMISSION_DENIED: Permission iam.workloadIdentityPools.create denied
```

**Solution**: Ensure you have the `roles/iam.workloadIdentityPoolAdmin` role:

```bash
gcloud projects add-iam-policy-binding {GCP_PROJECT_DEV} \
  --member="user:YOUR_EMAIL" \
  --role="roles/iam.workloadIdentityPoolAdmin"
```

### Error: Attribute condition must reference provider's claims

```
ERROR: INVALID_ARGUMENT: The attribute condition must reference one of the provider's claims
```

**Solution**: Add `--attribute-condition` when creating the OIDC provider:

```bash
--attribute-condition="assertion.repository_owner == '{GITHUB_ORG}'"
```

### Error: Service account does not exist

Create the service account first (Step 4) before binding WIF.

### Error: GitHub Actions authentication failed

1. Verify the WIF credentials format matches exactly
2. Check the GitHub repository matches the WIF binding
3. Ensure the workflow uses `id-token: write` permission

### Error: Teams notification failed

1. Verify the webhook URL is correct and active
2. Check if the Teams channel still exists
3. Regenerate the webhook if expired

---

## Verification Commands

### Check WIF Pool Exists

```bash
gcloud iam workload-identity-pools describe github-pool \
  --project={GCP_PROJECT_DEV} \
  --location=global
```

### Check OIDC Provider Exists

```bash
gcloud iam workload-identity-pools providers describe {WIF_PROVIDER_NAME} \
  --project={GCP_PROJECT_DEV} \
  --location=global \
  --workload-identity-pool=github-pool
```

### Check Service Account Exists

```bash
gcloud iam service-accounts describe {GCP_PROJECT_DEV}-sa@{GCP_PROJECT_DEV}.iam.gserviceaccount.com \
  --project={GCP_PROJECT_DEV}
```

### Check WIF Binding

```bash
gcloud iam service-accounts get-iam-policy {GCP_PROJECT_DEV}-sa@{GCP_PROJECT_DEV}.iam.gserviceaccount.com \
  --project={GCP_PROJECT_DEV}
```

### Check Artifact Registry Repository

```bash
gcloud artifacts repositories describe {PROJECT_PREFIX} \
  --project={GCP_PROJECT_DEV} \
  --location={GCP_REGION}
```

---

## Related Documents

- [IPLAN-011: Unified Phase-Gated Deployment](../../governance/plans/IPLAN-011_unified-phase-gated-deployment.md)
- [GITHUB_WORKFLOWS.md](../../governance/GITHUB_WORKFLOWS.md)
- [setup-wif.sh](../../scripts/project_setup/gcp/setup-wif.sh)
- [setup-environments.sh](../../scripts/project_setup/gcp/setup-environments.sh)
