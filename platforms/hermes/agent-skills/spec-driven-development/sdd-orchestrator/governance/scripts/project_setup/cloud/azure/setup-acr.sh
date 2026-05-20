#!/bin/bash
# Azure Container Registry (ACR) Setup
# Template - customize for your project
#
# Prerequisites:
# - Azure CLI installed and logged in
# - Resource group created
#
# Usage: ./setup-acr.sh

set -euo pipefail

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================
AZURE_SUBSCRIPTION_ID="{AZURE_SUBSCRIPTION_ID}"
AZURE_RESOURCE_GROUP="{AZURE_RESOURCE_GROUP}"
PROJECT_PREFIX="{PROJECT_PREFIX}"
# ACR names must be alphanumeric only, 5-50 chars
ACR_NAME="${PROJECT_PREFIX}acr"
LOCATION="eastus"
SKU="Basic"  # Basic, Standard, or Premium

# ============================================
# VALIDATION
# ============================================
echo "=== Azure Container Registry Setup ==="
echo ""
echo "Configuration:"
echo "  Subscription: ${AZURE_SUBSCRIPTION_ID}"
echo "  Resource Group: ${AZURE_RESOURCE_GROUP}"
echo "  ACR Name: ${ACR_NAME}"
echo "  SKU: ${SKU}"
echo ""

# Check for placeholder values
if [[ "${AZURE_SUBSCRIPTION_ID}" == *"{"* ]]; then
    echo "ERROR: Please update the configuration variables at the top of this script"
    exit 1
fi

# Validate ACR name (alphanumeric only)
if [[ ! "${ACR_NAME}" =~ ^[a-zA-Z0-9]+$ ]]; then
    echo "ERROR: ACR name must be alphanumeric only (no hyphens or special characters)"
    echo "Current: ${ACR_NAME}"
    exit 1
fi

# Set subscription
az account set --subscription "${AZURE_SUBSCRIPTION_ID}"

# ============================================
# STEP 1: Create ACR
# ============================================
echo "Step 1: Creating Azure Container Registry..."

if az acr show --name "${ACR_NAME}" --resource-group "${AZURE_RESOURCE_GROUP}" &>/dev/null; then
    echo "   ACR ${ACR_NAME} already exists"
else
    az acr create \
        --resource-group "${AZURE_RESOURCE_GROUP}" \
        --name "${ACR_NAME}" \
        --sku "${SKU}" \
        --location "${LOCATION}"
    echo "   ACR created: ${ACR_NAME}"
fi

# ============================================
# STEP 2: Enable Admin User (Optional)
# ============================================
echo "Step 2: Enabling admin user for local development..."

az acr update \
    --name "${ACR_NAME}" \
    --resource-group "${AZURE_RESOURCE_GROUP}" \
    --admin-enabled true

echo "   Admin user enabled"

# ============================================
# STEP 3: Get ACR Details
# ============================================
echo "Step 3: Retrieving ACR details..."

ACR_LOGIN_SERVER=$(az acr show --name "${ACR_NAME}" --resource-group "${AZURE_RESOURCE_GROUP}" --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name "${ACR_NAME}" --resource-group "${AZURE_RESOURCE_GROUP}" --query username -o tsv)

echo "   Login server: ${ACR_LOGIN_SERVER}"

# ============================================
# OUTPUT
# ============================================
echo ""
echo "=== Setup Complete ==="
echo ""
echo "ACR Login Server: ${ACR_LOGIN_SERVER}"
echo ""
echo "Add this to your GitHub repository secrets:"
echo "  ACR_REGISTRY=${ACR_LOGIN_SERVER}"
echo ""
echo "For local development, login with:"
echo "  az acr login --name ${ACR_NAME}"
echo ""
echo "Or with admin credentials:"
echo "  docker login ${ACR_LOGIN_SERVER} -u ${ACR_USERNAME}"
echo "  (get password with: az acr credential show --name ${ACR_NAME} --query passwords[0].value -o tsv)"
