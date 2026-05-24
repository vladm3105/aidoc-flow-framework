# AWS Setup Scripts

Setup scripts for configuring AWS infrastructure for GitHub Actions CI/CD.

## Prerequisites

- AWS CLI installed and configured (`aws configure`)
- Appropriate IAM permissions (IAM admin, ECR admin)
- GitHub repository created

## Scripts

| Script | Purpose |
|--------|---------|
| `setup-iam-oidc.sh` | Configure OIDC authentication for GitHub Actions |
| `setup-ecr.sh` | Create ECR container registry |

## Usage

### 1. Configure IAM OIDC

This script sets up OIDC-based authentication so GitHub Actions can assume an IAM role without storing AWS credentials.

```bash
# Edit the script to set your values
nano setup-iam-oidc.sh

# Run the script
./setup-iam-oidc.sh
```

**Configuration variables:**

- `AWS_ACCOUNT_ID` - Your AWS account ID
- `AWS_REGION` - Target region (e.g., `us-east-1`)
- `GITHUB_ORG` - Your GitHub organization
- `REPO_NAME` - Your repository name
- `PROJECT_PREFIX` - Project identifier

**Output:**

- IAM OIDC provider (if not exists)
- IAM role with trust policy for GitHub Actions
- Attached ECR policies

### 2. Create ECR Repository

```bash
# Edit the script to set your values
nano setup-ecr.sh

# Run the script
./setup-ecr.sh
```

**Configuration variables:**

- `AWS_REGION` - Target region
- `PROJECT_PREFIX` - Project identifier
- `SERVICE_NAME` - Service/application name

**Output:**

- ECR repository with lifecycle policy
- Repository URI for Docker pushes

## GitHub Secrets

After running the scripts, add these secrets to your GitHub repository:

| Secret | Value | Source |
|--------|-------|--------|
| `AWS_ROLE_ARN` | `arn:aws:iam::ACCOUNT:role/github-actions-PREFIX` | setup-iam-oidc.sh output |
| `AWS_REGION` | `us-east-1` | Your chosen region |
| `ECR_REGISTRY` | `ACCOUNT.dkr.ecr.REGION.amazonaws.com` | setup-ecr.sh output |

## Troubleshooting

### AssumeRoleWithWebIdentity Error

1. Verify OIDC provider exists: `aws iam list-open-id-connect-providers`
2. Check trust policy subject matches your repo: `repo:ORG/REPO:*`
3. Ensure thumbprint is correct (GitHub's current thumbprint)

### ECR Push Permission Denied

1. Verify role has `AmazonEC2ContainerRegistryFullAccess` policy
2. Check ECR repository exists in correct region
3. Ensure workflow uses correct role ARN

## Cleanup

To remove resources created by these scripts:

```bash
# Delete ECR repository (WARNING: deletes all images)
aws ecr delete-repository --repository-name PREFIX/SERVICE --force

# Delete IAM role
aws iam detach-role-policy --role-name github-actions-PREFIX --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess
aws iam delete-role --role-name github-actions-PREFIX

# Delete OIDC provider (only if no other repos use it)
aws iam delete-open-id-connect-provider --open-id-connect-provider-arn arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com
```
