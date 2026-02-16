#!/bin/bash
# Azure Managed Identity Setup for GitHub Actions
# Template - customize for your project
#
# Prerequisites:
# - Azure CLI installed and logged in
# - Appropriate Azure permissions
#
# Usage: ./setup-managed-identity.sh

set -euo pipefail

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================
AZURE_SUBSCRIPTION_ID="{AZURE_SUBSCRIPTION_ID}"
AZURE_TENANT_ID="{AZURE_TENANT_ID}"
AZURE_RESOURCE_GROUP="{AZURE_RESOURCE_GROUP}"
GITHUB_ORG="{GITHUB_ORG}"
REPO_NAME="{REPO_NAME}"
PROJECT_PREFIX="{PROJECT_PREFIX}"
APP_NAME="github-actions-${PROJECT_PREFIX}"
LOCATION="eastus"

# ============================================
# VALIDATION
# ============================================
echo "=== Azure Managed Identity Setup for GitHub Actions ==="
echo ""
echo "Configuration:"
echo "  Subscription: ${AZURE_SUBSCRIPTION_ID}"
echo "  Tenant: ${AZURE_TENANT_ID}"
echo "  Resource Group: ${AZURE_RESOURCE_GROUP}"
echo "  App Name: ${APP_NAME}"
echo "  GitHub: ${GITHUB_ORG}/${REPO_NAME}"
echo ""

# Check for placeholder values
if [[ "${AZURE_SUBSCRIPTION_ID}" == *"{"* ]]; then
    echo "ERROR: Please update the configuration variables at the top of this script"
    exit 1
fi

# Set subscription
az account set --subscription "${AZURE_SUBSCRIPTION_ID}"

# ============================================
# STEP 1: Create Resource Group (if needed)
# ============================================
echo "Step 1: Ensuring resource group exists..."

if az group show --name "${AZURE_RESOURCE_GROUP}" &>/dev/null; then
    echo "  ⓘ Resource group ${AZURE_RESOURCE_GROUP} already exists"
else
    az group create --name "${AZURE_RESOURCE_GROUP}" --location "${LOCATION}"
    echo "  ✓ Resource group created: ${AZURE_RESOURCE_GROUP}"
fi

# ============================================
# STEP 2: Create Azure AD Application
# ============================================
echo "Step 2: Creating Azure AD application..."

# Check if app already exists
EXISTING_APP=$(az ad app list --display-name "${APP_NAME}" --query "[0].appId" -o tsv || true)

if [ -n "${EXISTING_APP}" ]; then
    APP_ID="${EXISTING_APP}"
    echo "  ⓘ Application ${APP_NAME} already exists: ${APP_ID}"
else
    APP_ID=$(az ad app create --display-name "${APP_NAME}" --query appId -o tsv)
    echo "  ✓ Application created: ${APP_ID}"
fi

# ============================================
# STEP 3: Create Service Principal
# ============================================
echo "Step 3: Creating service principal..."

if az ad sp show --id "${APP_ID}" &>/dev/null; then
    echo "  ⓘ Service principal already exists"
else
    az ad sp create --id "${APP_ID}"
    echo "  ✓ Service principal created"
fi

# ============================================
# STEP 4: Configure Federated Credentials
# ============================================
echo "Step 4: Configuring federated credentials for GitHub OIDC..."

# Get the object ID of the application
APP_OBJECT_ID=$(az ad app show --id "${APP_ID}" --query id -o tsv)

# Create federated credential for main branch
cat > /tmp/federated-credential-main.json << EOF
{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:${GITHUB_ORG}/${REPO_NAME}:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}
EOF

# Create federated credential for pull requests
cat > /tmp/federated-credential-pr.json << EOF
{
  "name": "github-pr",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:${GITHUB_ORG}/${REPO_NAME}:pull_request",
  "audiences": ["api://AzureADTokenExchange"]
}
EOF

# Apply federated credentials (ignore errors if already exists)
az ad app federated-credential create \
    --id "${APP_OBJECT_ID}" \
    --parameters @/tmp/federated-credential-main.json 2>/dev/null || echo "  ⓘ Main branch credential already exists"

az ad app federated-credential create \
    --id "${APP_OBJECT_ID}" \
    --parameters @/tmp/federated-credential-pr.json 2>/dev/null || echo "  ⓘ PR credential already exists"

echo "  ✓ Federated credentials configured"

# ============================================
# STEP 5: Assign Role
# ============================================
echo "Step 5: Assigning Contributor role to resource group..."

SP_OBJECT_ID=$(az ad sp show --id "${APP_ID}" --query id -o tsv)

az role assignment create \
    --assignee-object-id "${SP_OBJECT_ID}" \
    --assignee-principal-type ServicePrincipal \
    --role "Contributor" \
    --scope "/subscriptions/${AZURE_SUBSCRIPTION_ID}/resourceGroups/${AZURE_RESOURCE_GROUP}" \
    2>/dev/null || echo "  ⓘ Role assignment already exists"

echo "  ✓ Contributor role assigned"

# ============================================
# OUTPUT
# ============================================
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Add these to your GitHub repository secrets:"
echo "  AZURE_CLIENT_ID=${APP_ID}"
echo "  AZURE_TENANT_ID=${AZURE_TENANT_ID}"
echo "  AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID}"
echo ""
echo "Cleanup:"
rm -f /tmp/federated-credential-main.json /tmp/federated-credential-pr.json
