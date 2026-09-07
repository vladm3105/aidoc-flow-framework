# Azure Setup Scripts

Setup scripts for configuring Azure infrastructure for GitHub Actions CI/CD.

## Prerequisites

- Azure CLI installed and logged in (`az login`)
- Appropriate Azure permissions (Subscription Contributor, Azure AD admin)
- GitHub repository created

## Scripts

| Script | Purpose |
|--------|---------|
| `setup-managed-identity.sh` | Configure OIDC authentication via federated credentials |
| `setup-acr.sh` | Create Azure Container Registry |

## Usage

### 1. Configure Managed Identity with OIDC

This script sets up workload identity federation so GitHub Actions can authenticate to Azure without storing credentials.

```bash
# Edit the script to set your values
nano setup-managed-identity.sh

# Run the script
./setup-managed-identity.sh
```

**Configuration variables:**

- `AZURE_SUBSCRIPTION_ID` - Your subscription ID
- `AZURE_TENANT_ID` - Your Azure AD tenant ID
- `AZURE_RESOURCE_GROUP` - Target resource group
- `GITHUB_ORG` - Your GitHub organization
- `REPO_NAME` - Your repository name
- `PROJECT_PREFIX` - Project identifier

**Output:**

- Azure AD application registration
- Service principal with Contributor role
- Federated credentials for main branch and PRs

### 2. Create Container Registry

```bash
# Edit the script to set your values
nano setup-acr.sh

# Run the script
./setup-acr.sh
```

**Configuration variables:**

- `AZURE_SUBSCRIPTION_ID` - Your subscription ID
- `AZURE_RESOURCE_GROUP` - Target resource group
- `PROJECT_PREFIX` - Project identifier (alphanumeric only)
- `SKU` - Registry tier (Basic, Standard, Premium)

**Output:**

- Azure Container Registry
- Admin user enabled for local development
- Login server URL

## GitHub Secrets

After running the scripts, add these secrets to your GitHub repository:

| Secret | Value | Source |
|--------|-------|--------|
| `AZURE_CLIENT_ID` | Application (client) ID | setup-managed-identity.sh output |
| `AZURE_TENANT_ID` | Directory (tenant) ID | Azure AD |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID | Azure Portal |
| `ACR_REGISTRY` | `prefixacr.azurecr.io` | setup-acr.sh output |

## Troubleshooting

### Federated Credential Error

1. Verify application exists: `az ad app list --display-name github-actions-PREFIX`
2. Check subject claim matches: `repo:ORG/REPO:ref:refs/heads/main`
3. Ensure issuer is exactly: `https://token.actions.githubusercontent.com`

### ACR Push Permission Denied

1. Verify service principal has AcrPush role on ACR
2. Check ACR name is correct (alphanumeric only, no hyphens)
3. Ensure workflow authenticates before docker push

### Role Assignment Failed

1. Check you have Owner or User Access Administrator role
2. Verify subscription ID is correct
3. Ensure resource group exists

## Cleanup

To remove resources created by these scripts:

```bash
# Delete ACR (WARNING: deletes all images)
az acr delete --name prefixacr --resource-group RG_NAME --yes

# Delete service principal and app registration
APP_ID=$(az ad app list --display-name github-actions-PREFIX --query "[0].appId" -o tsv)
az ad app delete --id $APP_ID

# Delete resource group (WARNING: deletes all resources in group)
az group delete --name RG_NAME --yes
```

## Additional Resources

- [Azure OIDC for GitHub Actions](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)
- [Azure Container Registry docs](https://docs.microsoft.com/en-us/azure/container-registry/)
