#!/bin/bash
# AWS IAM OIDC Setup for GitHub Actions
# Template - customize for your project
#
# Prerequisites:
# - AWS CLI installed and configured
# - Appropriate IAM permissions
#
# Usage: ./setup-iam-oidc.sh

set -euo pipefail

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================
AWS_ACCOUNT_ID="{AWS_ACCOUNT_ID}"
AWS_REGION="{AWS_REGION}"
GITHUB_ORG="{GITHUB_ORG}"
REPO_NAME="{REPO_NAME}"
PROJECT_PREFIX="{PROJECT_PREFIX}"
ROLE_NAME="github-actions-${PROJECT_PREFIX}"

# ============================================
# VALIDATION
# ============================================
echo "=== AWS OIDC Setup for GitHub Actions ==="
echo ""
echo "Configuration:"
echo "  AWS Account: ${AWS_ACCOUNT_ID}"
echo "  Region: ${AWS_REGION}"
echo "  GitHub Org: ${GITHUB_ORG}"
echo "  Repository: ${REPO_NAME}"
echo "  Role Name: ${ROLE_NAME}"
echo ""

# Check for placeholder values
if [[ "${AWS_ACCOUNT_ID}" == *"{"* ]]; then
    echo "ERROR: Please update the configuration variables at the top of this script"
    echo "       Replace {PLACEHOLDER} values with your actual values"
    exit 1
fi

# ============================================
# STEP 1: Create OIDC Provider
# ============================================
echo "Step 1: Creating OIDC Provider for GitHub Actions..."

# Check if OIDC provider already exists
EXISTING_PROVIDER=$(aws iam list-open-id-connect-providers --query "OpenIDConnectProviderList[?contains(Arn, 'token.actions.githubusercontent.com')]" --output text || true)

if [ -z "${EXISTING_PROVIDER}" ]; then
    aws iam create-open-id-connect-provider \
        --url https://token.actions.githubusercontent.com \
        --client-id-list sts.amazonaws.com \
        --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1"
    echo "  ✓ OIDC provider created"
else
    echo "  ⓘ OIDC provider already exists"
fi

# ============================================
# STEP 2: Create Trust Policy
# ============================================
echo "Step 2: Creating trust policy..."

cat > /tmp/trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${REPO_NAME}:*"
        }
      }
    }
  ]
}
EOF

echo "  ✓ Trust policy created at /tmp/trust-policy.json"

# ============================================
# STEP 3: Create IAM Role
# ============================================
echo "Step 3: Creating IAM role..."

# Check if role already exists
if aws iam get-role --role-name "${ROLE_NAME}" &>/dev/null; then
    echo "  ⓘ Role ${ROLE_NAME} already exists, updating trust policy..."
    aws iam update-assume-role-policy \
        --role-name "${ROLE_NAME}" \
        --policy-document file:///tmp/trust-policy.json
else
    aws iam create-role \
        --role-name "${ROLE_NAME}" \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "GitHub Actions role for ${PROJECT_PREFIX}"
    echo "  ✓ Role created: ${ROLE_NAME}"
fi

# ============================================
# STEP 4: Attach Policies
# ============================================
echo "Step 4: Attaching policies..."

# ECR access for container deployments
aws iam attach-role-policy \
    --role-name "${ROLE_NAME}" \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess || true
echo "  ✓ ECR policy attached"

# ECS access for container orchestration (optional - uncomment if using ECS)
# aws iam attach-role-policy \
#     --role-name "${ROLE_NAME}" \
#     --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess || true
# echo "  ✓ ECS policy attached"

# ============================================
# OUTPUT
# ============================================
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Role ARN: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
echo ""
echo "Add this to your GitHub repository secrets:"
echo "  AWS_ROLE_ARN=arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
echo "  AWS_REGION=${AWS_REGION}"
echo ""
echo "Cleanup:"
rm -f /tmp/trust-policy.json
