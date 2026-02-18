# SDD Framework Configuration Variables

**Framework**: Specification-Driven Development (SDD)

> **Depth Selection**: This configuration applies to all SDD depths (Lite, Standard, Full). Layer-specific templates are in [`ai_dev_ssd_flow/`](../../ai_dev_ssd_flow/).

This document lists all placeholder variables used throughout the SDD governance framework. Replace these values when customizing the framework for your project.

## Quick Reference

| Category | Variables | Priority |
|----------|-----------|----------|
| Core | 6 | Required |
| Team | 3 | Required |
| AI Agent | 9 | Required |
| Cloud - GCP | 7 | Choose one+ |
| Cloud - AWS | 4 | Choose one+ |
| Cloud - Azure | 5 | Choose one+ |
| Infrastructure | 8 | Required |
| Configuration | 8 | Optional |
| **Total** | **50** | |

---

## Required - Core

These must be configured for every project.

| Variable | Description | Example | Files Affected |
|----------|-------------|---------|----------------|
| `{PROJECT_PREFIX}` | Short identifier (lowercase, no spaces) | `myproj` | ~270 files |
| `{PROJECT_NAME}` | Full project name | `My AI Project` | ~25 files |
| `{REPO_NAME}` | Repository name (GitHub) | `my-ai-project` | ~110 files |
| `{GITHUB_ORG}` | GitHub organization name | `my-organization` | ~140 files |
| `{GITHUB_HOST}` | GitHub hostname | `github.com` | ~260 files |
| `{PROJECT_BOARD_NUMBER}` | GitHub Project board number | `1` | ~55 files |

### Replacement Commands

```bash
# Core replacements
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{PROJECT_PREFIX}|myproj|g' {} \;
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{PROJECT_NAME}|My AI Project|g' {} \;
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{REPO_NAME}|my-ai-project|g' {} \;
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{GITHUB_ORG}|my-organization|g' {} \;
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{GITHUB_HOST}|github.com|g' {} \;
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{PROJECT_BOARD_NUMBER}|1|g' {} \;
```

---

## Required - Team

Configure your team reviewers and identifiers.

| Variable | Description | Example | Files Affected |
|----------|-------------|---------|----------------|
| `{CODEOWNER_1}` | Primary code reviewer (GitHub username) | `@lead-dev` | CODEOWNERS, docs |
| `{CODEOWNER_2}` | Secondary code reviewer | `@senior-dev` | CODEOWNERS, docs |
| `{TEAM_SLUG}` | GitHub team identifier | `dev-team` | workflows, docs |

---

## Required - AI Agent Configuration

Configure AI assistant integration.

| Variable | Description | Example | Files Affected |
|----------|-------------|---------|----------------|
| `{TIMEZONE}` | Project timezone | `America/New_York` | ~23 files |
| `{AI_TOOL_NAME}` | AI assistant name | `Claude` | ~108 files |
| `{AI_TOOL_EMAIL}` | AI assistant email for commits | `noreply@anthropic.com` | templates |
| `{COMMUNICATION_TOOL}` | Primary communication tool | `Teams` or `Slack` | docs |
| `{BOARD_OPTION_IN_PROGRESS}` | Board "In Progress" option ID | `47fc9ee4` | workflows |
| `{BOARD_OPTION_IN_REVIEW}` | Board "In Review" option ID | `de81af01` | workflows |
| `{BOARD_OPTION_DONE}` | Board "Done" option ID | `98236657` | workflows |
| `{BOARD_STATUS_FIELD_ID}` | Board Status field ID | `PVTSSF_...` | workflows |
| `{BOARD_PROJECT_ID}` | Board Project node ID | `PVT_...` | workflows |

### Finding Board IDs

Use the GitHub GraphQL API to find your project board IDs:

```bash
gh api graphql -f query='
query {
  organization(login: "YOUR_ORG") {
    projectV2(number: YOUR_BOARD_NUMBER) {
      id
      field(name: "Status") {
        ... on ProjectV2SingleSelectField {
          id
          options {
            id
            name
          }
        }
      }
    }
  }
}'
```

---

## Required - Cloud Provider

Choose one or more cloud providers and configure accordingly.

### GCP (Google Cloud Platform)

| Variable | Description | Example |
|----------|-------------|---------|
| `{GCP_PROJECT_DEV}` | GCP dev project ID | `myproj-dev` |
| `{GCP_PROJECT_STAGING}` | GCP staging project ID | `myproj-staging` |
| `{GCP_PROJECT_PROD}` | GCP prod project ID | `myproj-prod` |
| `{GCP_REGION}` | GCP region | `us-east4` |
| `{WIF_POOL_NAME}` | Workload Identity pool name | `github-actions-pool` |
| `{WIF_PROVIDER_NAME}` | Workload Identity provider | `github-provider` |
| `{GCP_ARTIFACT_REGISTRY}` | Artifact Registry path | `us-east4-docker.pkg.dev` |

### AWS (Amazon Web Services)

| Variable | Description | Example |
|----------|-------------|---------|
| `{AWS_ACCOUNT_ID}` | AWS account ID | `123456789012` |
| `{AWS_REGION}` | AWS region | `us-east-1` |
| `{AWS_ROLE_ARN}` | IAM role ARN for GitHub Actions | `arn:aws:iam::123456789012:role/github-actions` |
| `{ECR_REGISTRY}` | ECR registry URL | `123456789012.dkr.ecr.us-east-1.amazonaws.com` |

### Azure

| Variable | Description | Example |
|----------|-------------|---------|
| `{AZURE_SUBSCRIPTION_ID}` | Azure subscription ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `{AZURE_TENANT_ID}` | Azure tenant ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `{AZURE_CLIENT_ID}` | Azure app client ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `{ACR_REGISTRY}` | Azure Container Registry | `myregistry.azurecr.io` |
| `{AZURE_RESOURCE_GROUP}` | Azure resource group | `myproj-rg` |

---

## Required - Infrastructure

| Variable | Description | Example |
|----------|-------------|---------|
| `{SERVICE_NAME}` | Main service/application name | `api-service` |
| `{DOCKER_IMAGE_PREFIX}` | Docker image prefix | `myproj` |
| `{SMOKE_TEST_ENDPOINTS}` | Health check endpoints | `/health,/ready` |
| `{REVISION_RETENTION}` | Cloud Run revision count | `10` |
| `{MIN_INSTANCES}` | Minimum container instances | `0` |
| `{MAX_INSTANCES}` | Maximum container instances | `10` |
| `{MEMORY_LIMIT}` | Container memory limit | `1Gi` |
| `{CPU_LIMIT}` | Container CPU limit | `1` |

---

## Optional - Configuration

These have sensible defaults but can be customized.

| Variable | Description | Default |
|----------|-------------|---------|
| `{PHASE_COUNT}` | Number of project phases | `8` |
| `{COVERAGE_THRESHOLD}` | Test coverage percentage | `80` |
| `{AI_REVIEW_MODEL}` | Claude model for review | `sonnet` |
| `{AI_REVIEW_BUDGET}` | Max cost per review ($) | `1` |
| `{DEPLOY_WINDOW_START}` | Deployment window start (hour) | `10` |
| `{DEPLOY_WINDOW_END}` | Deployment window end (hour) | `16` |
| `{ERROR_RATE_THRESHOLD}` | Rollback error rate (%) | `1` |
| `{NOTIFICATION_WEBHOOK}` | Teams/Slack webhook URL | (none) |

---

## Additional Variables

These appear in specific contexts:

| Variable | Description | Context |
|----------|-------------|---------|
| `{GITHUB_PAT}` | GitHub Personal Access Token | MCP servers, scripts |
| `{DOMAIN}` | Project domain | URLs, configs |
| `{LOCAL_PROJECT_PATH}` | Local development path | Documentation, MCP |
| `{ADMIN_USERNAME}` | Admin GitHub username | Scripts |
| `{SECURITY_EMAIL}` | Security contact email | Issue templates |

---

## Workflow Runtime Placeholders

These placeholders are used internally by GitHub Actions workflows and are **NOT replaced during setup**. They are substituted at runtime by the workflows themselves.

| Placeholder | Description | Used In |
|-------------|-------------|---------|
| `DEV_ISSUE_PLACEHOLDER` | Development issue number | QA workflows |
| `PR_NUMBER_PLACEHOLDER` | Pull request number | QA, deployment workflows |
| `PR_TITLE_PLACEHOLDER` | Pull request title | Notification workflows |
| `MERGED_AT_PLACEHOLDER` | PR merge timestamp | Cleanup workflows |
| `COMMITS_PLACEHOLDER` | Commit list | Release, notification workflows |
| `MIGRATIONS_PLACEHOLDER` | Migration status | Deployment workflows |
| `CONFIG_PLACEHOLDER` | Config change status | Deployment workflows |
| `INFRA_PLACEHOLDER` | Infrastructure change status | Deployment workflows |
| `BLOCKED_BY_PLACEHOLDER` | Blocking issue reference | Issue automation |

**Note**: Do not replace these in your configuration. They are handled automatically by the workflow execution engine.

---

## Validation

After replacing all variables, validate no placeholders remain:

```bash
# Use the validation script (recommended)
./governance/scripts/project_setup/validate_configuration.sh

# Or run with --fix to see replacement commands
./governance/scripts/project_setup/validate_configuration.sh --fix
```

The validation script:
- Scans all files for unreplaced placeholders
- Categorizes placeholders by type (Core, Team, Cloud, AI, etc.)
- Shows files with the most remaining placeholders
- Optionally generates sed commands for common replacements

### Manual Validation

```bash
# Check for unreplaced placeholders manually
grep -roh '\{[A-Z_]*\}' . --include="*.md" --include="*.yml" --include="*.sh" --include="*.json" | sort -u

# Should return empty or only valid template syntax like {} in YAML
```

## Automation Script

A helper script is provided for bulk replacement:

```bash
./scripts/configure_framework.sh \
  --project-prefix "myproj" \
  --project-name "My AI Project" \
  --repo-name "my-ai-project" \
  --github-org "my-organization" \
  --github-host "github.com"
```

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for the complete customization process.
