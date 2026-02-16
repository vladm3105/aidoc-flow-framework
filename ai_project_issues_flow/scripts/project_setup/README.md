# Project Setup Scripts

Scripts for initializing and configuring the AI-First Project Governance Framework.

## Directory Structure

```
project_setup/
├── README.md                          # This file
├── setup_github_environments.sh       # GitHub environment configuration
├── validate_configuration.sh          # Placeholder validation script
└── cloud/
    ├── gcp/                           # Google Cloud Platform setup
    │   ├── README.md
    │   ├── setup-projects.sh
    │   ├── setup-wif.sh
    │   ├── setup_artifact_registry.sh
    │   ├── setup-environments.sh
    │   ├── setup-ai-review-gcp.sh
    │   └── configure_revision_retention.sh
    ├── aws/                           # Amazon Web Services setup
    │   ├── README.md
    │   ├── setup-iam-oidc.sh
    │   └── setup-ecr.sh
    └── azure/                         # Microsoft Azure setup
        ├── README.md
        ├── setup-managed-identity.sh
        └── setup-acr.sh
```

## Quick Start

### 1. Validate Configuration

Before setting up cloud resources, validate that all placeholder variables have been replaced:

```bash
./validate_configuration.sh
```

This script scans for unreplaced `{VARIABLE}` placeholders and categorizes them by type.

### 2. Choose Cloud Provider

Select your cloud provider and follow the setup guide:

| Provider | Guide | Authentication Method |
|----------|-------|----------------------|
| GCP | [cloud/gcp/README.md](cloud/gcp/README.md) | Workload Identity Federation |
| AWS | [cloud/aws/README.md](cloud/aws/README.md) | IAM OIDC |
| Azure | [cloud/azure/README.md](cloud/azure/README.md) | Federated Credentials |

### 3. Configure GitHub Environments

After cloud setup, configure GitHub environments:

```bash
./setup_github_environments.sh
```

## Scripts

### validate_configuration.sh

Validates that all placeholder variables have been replaced with actual values.

**Usage:**
```bash
# Check for unreplaced placeholders
./validate_configuration.sh

# Show replacement commands
./validate_configuration.sh --fix
```

**Output:**
- List of unreplaced placeholders by category
- Files with most remaining placeholders
- Optional sed commands for bulk replacement

### setup_github_environments.sh

Configures GitHub environments (dev, staging, production) with appropriate protection rules.

**Prerequisites:**
- GitHub CLI installed and authenticated
- Repository admin permissions
- Cloud credentials already configured

**Usage:**
```bash
./setup_github_environments.sh
```

**Configures:**
- Environment protection rules
- Required reviewers (production)
- Deployment branch policies
- Wait timers

## Cloud Provider Setup

### GCP (Recommended)

Full setup with Workload Identity Federation:

```bash
cd cloud/gcp
./setup-projects.sh          # Create dev/staging/prod projects
./setup-wif.sh               # Configure WIF authentication
./setup_artifact_registry.sh # Create container registry
./setup-environments.sh      # Set GitHub secrets
```

### AWS

OIDC-based authentication setup:

```bash
cd cloud/aws
./setup-iam-oidc.sh  # Configure IAM OIDC provider
./setup-ecr.sh       # Create ECR repository
```

### Azure

Federated credentials setup:

```bash
cd cloud/azure
./setup-managed-identity.sh  # Configure managed identity
./setup-acr.sh               # Create Azure Container Registry
```

## Configuration Variables

All scripts use placeholder variables from `CONFIG.md`. Key variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{PROJECT_PREFIX}` | Short identifier | `myproj` |
| `{GITHUB_ORG}` | GitHub organization | `my-org` |
| `{GITHUB_HOST}` | GitHub hostname | `github.com` |
| `{REPO_NAME}` | Repository name | `my-project` |

See [CONFIG.md](../../CONFIG.md) for the complete list.

## Troubleshooting

### Script Permission Denied

```bash
chmod +x *.sh
chmod +x cloud/*/*.sh
```

### Placeholder Not Replaced

Run the validation script to identify unreplaced placeholders:

```bash
./validate_configuration.sh --fix
```

### Cloud CLI Not Found

Ensure the appropriate CLI is installed:

- GCP: `gcloud --version`
- AWS: `aws --version`
- Azure: `az --version`

### Authentication Failed

Re-authenticate with your cloud provider:

- GCP: `gcloud auth login`
- AWS: `aws configure`
- Azure: `az login`
