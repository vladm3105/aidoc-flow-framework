# {PROJECT_PREFIX}-{SERVICE_NAME}

GCP Cost Guard — standalone budget protection for the {PROJECT_NAME} platform.

## Components

| Component | Path | Description |
|:----------|:-----|:------------|
| CostGuardedLLM | `src/cost_guard/llm_wrapper.py` | LLM wrapper with daily/monthly spend limits |
| Budget Remediation | `src/cost_guard/functions/budget_remediation.py` | Cloud Function: auto-disable services at budget thresholds |
| Idle Scanner | `src/cost_guard/functions/idle_scanner.py` | Cloud Function: detect idle GCP resources daily |
| Firestore Utils | `src/cost_guard/utils/firestore.py` | Firestore client for config and spend tracking |
| Logging | `src/cost_guard/utils/logging.py` | Structured logging for all components |

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

```bash
# Clone
git clone https://{GITHUB_HOST}/{GITHUB_ORG}/{PROJECT_PREFIX}-{SERVICE_NAME}.git
cd {PROJECT_PREFIX}-{SERVICE_NAME}

# Install (with dev dependencies)
uv pip install -e ".[dev]"
```

### Commands

```bash
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/

# Test
pytest tests/ -v

# Test with coverage
pytest tests/ -v --cov=cost_guard --cov-report=term-missing
```

## Docker Build

```bash
# Build container
cd components/{SERVICE_NAME}
docker build -t {PROJECT_PREFIX}-{SERVICE_NAME} .

# Run locally
docker run -p 8080:8080 {PROJECT_PREFIX}-{SERVICE_NAME}

# Health check
curl http://localhost:8080/health
```

### Container Details

| Property | Value |
|:---------|:------|
| Base Image | `python:3.12-slim` |
| User | `appuser` (non-root) |
| Port | `8080` |
| Health Endpoint | `/health` |
| Entry Point | `python -m cost_guard.main` |

## Deployment

Deployed to Cloud Run via GitHub Actions workflows:

| Environment | Workflow | Trigger |
|:------------|:---------|:--------|
| Development | `deploy-dev-pr.yml` | PR opened/synced |
| Staging | `deploy-staging.yml` | Phase completion |
| Production | `deploy-prod.yml` | Manual dispatch |

### Required Infrastructure

Before first deployment, run Terraform modules in `terraform/`:

```bash
cd terraform
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply
```

Creates: Pub/Sub topics, Firestore database, BigQuery dataset, Cloud Functions.

## Architecture

This repository is a component of the [AI Cloud Cost Monitoring](https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}) platform. It provides Phase 1 (standalone GCP cost protection) functionality.

## License

Apache 2.0 — see [LICENSE](LICENSE).
