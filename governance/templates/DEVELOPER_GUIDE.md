# Developer Guide

Setup and workflow reference for the AI Cost Monitoring platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Local Development](#local-development)
- [Common Tasks](#common-tasks)
- [Debugging](#debugging)
- [Deployment](#deployment)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|:---------|:--------|:--------|
| Python | 3.11+ | Backend services, agents, MCP servers |
| Node.js | 18+ | Frontend (CopilotKit), AG-UI components |
| Git | Latest | Version control |
| gcloud CLI | Latest | GCP interaction |
| Docker | Latest | Local container testing (optional) |

### Cloud Accounts

**Home Cloud: GCP** — The platform runs on GCP (Cloud Run, BigQuery, Firestore, Secret Manager). See [ADR-002](docs/adr/002-gcp-only-first.md).

The platform **monitors** costs across AWS, Azure, GCP, and Kubernetes via MCP servers, but **deploys** exclusively to GCP.

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}.git
cd {REPO_NAME}
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env  # or your preferred editor
```

**Minimum required variables:**
```bash
GCP_PROJECT_ID=your-project-id
GH_TOKEN=ghp_your-github-token
```

### 3. GCP Authentication

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project your-project-id
```

### 4. Verify Setup

```bash
# Verify GCP access
gcloud projects describe $GCP_PROJECT_ID

# Verify GitHub access
GH_HOST={GITHUB_HOST} gh auth status
```

---

## Repository Structure

This is a **monorepo**. All documentation, governance, and component source code live in this single repository.

```
{REPO_NAME}/              (Monorepo)
 .github/
    ISSUE_TEMPLATE/               8 issue templates
    workflows/                    9 GitHub Actions workflows
    labeler.yml                   PR labeling rules
    PULL_REQUEST_TEMPLATE.md

 governance/                       Project governance
    PROJECT_PLAN.md               Full project plan (~75 tasks)
    ROADMAP.md                    Phase timeline and dependencies
    GOVERNANCE_RULES.md           Operational policies and conventions
    DEFINITION_OF_DONE.md         Completion criteria
    REPOSITORY_STRATEGY.md        Monorepo architecture
    HOME_REPO.md                  Repository guide
    BRANCHING_STRATEGY.md         Git branching model
    RELEASE_PROCESS.md            Versioning and releases
    ROLES_AND_TOOLS.md            Human vs AI responsibilities
    GITHUB_WORKFLOWS.md           Workflow documentation
    GITHUB_PROJECT_SETUP.md      AI workflow setup
    GITHUB_TOOLS_SETUP.md         CLI and MCP configuration
    plans/                        Permanent development plans (execution history)

 tmp/                             Temporary artifacts and temporary plans (disposable)

 docs/
    adr/                          9 Architecture Decision Records
    core/                         8 Technical specifications
    architecture/                 System diagrams
    UX/                           Implementation guides

 components/                       Component source code
    {SERVICE_NAME}/               GCP budget alerts + auto-remediation
    mcp-servers/                  MCP server specifications
    agents/                       AI agents (Phase 4)
    frontend/                     CopilotKit frontend (Phase 5)
    infrastructure/               Terraform modules (Phase 2)

 scripts/                          Utility scripts

 CLAUDE.md                         {AI_TOOL_NAME} Code-specific instructions
 README_AIAGENT.md                 Universal AI agent rules
 DEVELOPER_GUIDE.md                This document
 CONTRIBUTING.md                   Contribution guidelines
 HANDOFF.md                        Developer handoff notes
 GCP-DEPLOYMENT.md                 GCP deployment guide
 .env.example                      Environment template
 README.md                         Project overview
```

### Component Directories

| Component | Phase | Purpose | Tech Stack |
|:----------|:-----:|:--------|:-----------|
| `components/{SERVICE_NAME}` | 1 | GCP budget alerts + auto-remediation | Python, Cloud Functions, Pub/Sub, Firestore |
| `components/infrastructure` | 2 | Terraform modules (Cloud Run, BigQuery) | Terraform, HCL |
| `components/mcp-servers` | 3 | 4 MCP servers (3 native + OpenCost custom) | Python, FastMCP, Cloud Run |
| `components/agents` | 4 | 5 AI agents (Coordinator + 4 Domain) | Python, Google ADK, LiteLLM |
| `components/frontend` | 5 | Next.js + CopilotKit | Next.js, CopilotKit, AG-UI |

---

## Local Development

### Phase 1: GCP Cost Guard Development

Phase 1 work happens in `components/{SERVICE_NAME}/`. See [PROJECT_PLAN.md](governance/PROJECT_PLAN.md) for task list.

```bash
cd components/{SERVICE_NAME}

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### Phase 2+: Backend Development

Backend development (FastAPI, agents, MCP) happens in the respective component directories:

```bash
# Agents
cd components/agents
pip install -e ".[dev]"

# MCP Servers
cd components/mcp-servers
pip install -e ".[dev]"

# Frontend
cd components/frontend
npm install
```

### Working with BigQuery

```bash
# Authenticate with GCP
gcloud auth application-default login

# Set project
gcloud config set project your-project-id
```

---

## Common Tasks

### Adding a New MCP Tool

MCP tool development happens in `components/mcp-servers/`. See [02-mcp-tool-contracts.md](docs/core/02-mcp-tool-contracts.md) for specifications.

1. Create tool function in the appropriate MCP server directory
2. Register the tool in the MCP server
3. Add tests
4. Update `docs/core/02-mcp-tool-contracts.md`

### Adding a New API Endpoint

API development happens in the backend component. See [05-api-endpoint-spec.md](docs/core/05-api-endpoint-spec.md) for specifications.

1. Create route in the FastAPI routes directory
2. Register in the app
3. Add tests
4. Update `docs/core/05-api-endpoint-spec.md`

### Running Tests

Each component has its own test suite:

```bash
# In any component directory
cd components/<component>

# Python tests
pytest
pytest --cov=src --cov-report=html

# TypeScript tests (frontend)
npm test
```

### Creating Issues

All issues are tracked in this repo:

```bash
GH_HOST={GITHUB_HOST} gh issue create \
  --repo {GITHUB_ORG}/{REPO_NAME} \
  --title "Issue title" \
  --body "Description"
```

Issues auto-add to [Project Board #{PROJECT_BOARD_NUMBER}](https://{GITHUB_HOST}/orgs/{GITHUB_ORG}/projects/{PROJECT_BOARD_NUMBER}) with Status=Todo.

---

## Debugging

### Python Debugging

**VS Code configuration (`.vscode/launch.json`):**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.api.main:app", "--reload"],
      "env": {"ENVIRONMENT": "development"}
    }
  ]
}
```

**Inline breakpoint:**
```python
import pdb; pdb.set_trace()
```

### Logging

**Python:**
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed info")
logger.info("General info")
logger.warning("Warning message")
logger.error("Error occurred")
```

**TypeScript:**
```typescript
console.log('Debug:', data);
console.warn('Warning:', warning);
console.error('Error:', error);
```

---

## Deployment

GCP is the deployment target for all components. See [GCP-DEPLOYMENT.md](./GCP-DEPLOYMENT.md) for the full guide.

**Quick deploy to Cloud Run:**
```bash
# Deploy API
gcloud run deploy ai-cost-api \
  --source . \
  --platform managed \
  --region us-central1

# Deploy frontend
cd components/frontend
gcloud run deploy ai-cost-ui \
  --source . \
  --platform managed \
  --region us-central1
```

Infrastructure is managed via Terraform in `components/infrastructure/`. See [07-deployment-infrastructure.md](docs/core/07-deployment-infrastructure.md).

---

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'src'`
```bash
# Ensure you're in the component directory root and venv is activated
source venv/bin/activate
python -m src.api.main  # Use -m flag
```

**Issue:** BigQuery authentication fails
```bash
gcloud auth application-default login
```
> **Note**: Do not use `GOOGLE_APPLICATION_CREDENTIALS` with service account key files. This project uses Workload Identity Federation for all GCP auth. See [GOVERNANCE_RULES.md §2](governance/GOVERNANCE_RULES.md#2-security-posture).

**Issue:** Port already in use
```bash
lsof -ti:8000 | xargs kill -9
```

---

## Additional Resources

- [CONTRIBUTING.md](./CONTRIBUTING.md) — Contribution guidelines
- [README.md](./README.md) — Project overview and architecture
- [HANDOFF.md](./HANDOFF.md) — Current status and next steps
- [docs/core/](./docs/core/) — Technical specifications (8 specs)
- [docs/adr/](./docs/adr/) — Architecture Decision Records (9 ADRs)
- [governance/](./governance/) — Project governance documents
