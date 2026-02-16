#!/bin/bash
# AWS ECR Setup for Container Registry
# Template - customize for your project
#
# Prerequisites:
# - AWS CLI installed and configured
# - IAM permissions for ECR operations
#
# Usage: ./setup-ecr.sh

set -euo pipefail

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================
AWS_REGION="{AWS_REGION}"
PROJECT_PREFIX="{PROJECT_PREFIX}"
SERVICE_NAME="{SERVICE_NAME}"
REPO_NAME="${PROJECT_PREFIX}/${SERVICE_NAME}"

# ============================================
# VALIDATION
# ============================================
echo "=== AWS ECR Setup ==="
echo ""
echo "Configuration:"
echo "  Region: ${AWS_REGION}"
echo "  Repository: ${REPO_NAME}"
echo ""

# Check for placeholder values
if [[ "${AWS_REGION}" == *"{"* ]]; then
    echo "ERROR: Please update the configuration variables at the top of this script"
    exit 1
fi

# ============================================
# STEP 1: Create ECR Repository
# ============================================
echo "Step 1: Creating ECR repository..."

if aws ecr describe-repositories --repository-names "${REPO_NAME}" --region "${AWS_REGION}" &>/dev/null; then
    echo "  ⓘ Repository ${REPO_NAME} already exists"
else
    aws ecr create-repository \
        --repository-name "${REPO_NAME}" \
        --region "${AWS_REGION}" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    echo "  ✓ Repository created: ${REPO_NAME}"
fi

# ============================================
# STEP 2: Set Lifecycle Policy
# ============================================
echo "Step 2: Setting lifecycle policy..."

cat > /tmp/ecr-lifecycle-policy.json << 'EOF'
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 images",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF

aws ecr put-lifecycle-policy \
    --repository-name "${REPO_NAME}" \
    --region "${AWS_REGION}" \
    --lifecycle-policy-text file:///tmp/ecr-lifecycle-policy.json

echo "  ✓ Lifecycle policy applied (keeps last 10 images)"

# ============================================
# OUTPUT
# ============================================
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "ECR Repository URI: ${ECR_URI}"
echo ""
echo "Add this to your GitHub repository secrets:"
echo "  ECR_REGISTRY=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
echo ""
echo "Docker login command:"
echo "  aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}"
echo ""
echo "Cleanup:"
rm -f /tmp/ecr-lifecycle-policy.json
