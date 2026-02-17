# AI-First Project Governance Framework

A complete, reusable project management framework for small AI-first projects. This framework provides:

- **Project Governance** - Structured documentation for planning, tracking, and quality assurance
- **CI/CD Pipelines** - GitHub Actions workflows for automated testing and deployment
- **AI-Powered Code Review** - Integrated AI review workflows using Claude Code CLI
- **Issue/PR Templates** - Standardized templates for consistent project tracking
- **Setup Automation** - Scripts for cloud infrastructure and GitHub configuration

## Quick Start

### 1. Copy Framework to Your Project

```bash
cp -r ai_project_flow/* /path/to/your/project/
```

### 2. Configure Variables

Edit `CONFIG.md` reference and replace all placeholders throughout the framework:

```bash
# Required - find and replace these across all files
{PROJECT_PREFIX}     → your-prefix        # e.g., "myproj"
{PROJECT_NAME}       → Your Project Name  # e.g., "My AI Project"
{REPO_NAME}          → your-repo-name     # e.g., "my-ai-project"
{GITHUB_ORG}         → your-org           # e.g., "my-organization"
{GITHUB_HOST}        → github.com         # or your GHES host
```

See [CONFIG.md](CONFIG.md) for the complete list of 50+ placeholder variables.

### 3. Set Up GitHub

```bash
# Run the GitHub setup script
./scripts/project_setup/setup_github_environments.sh
```

### 4. Configure Cloud Provider

Choose your cloud provider and run the appropriate setup scripts:

**GCP:**
```bash
./scripts/project_setup/cloud/gcp/setup-projects.sh
./scripts/project_setup/cloud/gcp/setup-wif.sh
./scripts/project_setup/cloud/gcp/setup_artifact_registry.sh
```

**AWS/Azure:** See [CLOUD_GUIDE.md](CLOUD_GUIDE.md) for setup instructions.

## Framework Structure

```
 README.md                    # This file
 CONFIG.md                    # All placeholder variables
 SETUP_GUIDE.md              # Step-by-step customization
 CLOUD_GUIDE.md              # Cloud provider guidance

 governance/                  # Project governance docs
    GOVERNANCE_RULES.md     # Core operational rules
    PROJECT_PLAN.md         # Project planning template
    AI_PR_Review/           # AI code review documentation
    plans/                  # IPLAN structure (README template)
    ...                     # Additional governance docs

 .github/                     # GitHub automation
    workflows/              # 20 GitHub Actions workflows
    ISSUE_TEMPLATE/         # 10 issue templates
    CODEOWNERS              # Reviewer assignment
    ...

 templates/                   # Root documentation templates
    README.md               # Project README template
    CLAUDE.md               # AI agent configuration
    CONTRIBUTING.md         # Contribution guide
    ...

 scripts/                     # Automation scripts
    project_setup/          # Initial setup scripts
       cloud/             # Cloud-specific scripts (GCP/AWS/Azure)
    workflows/              # CI/CD helper scripts
    ghes-runner/            # Optional GHES runner setup

 components/                  # Component structure templates
    {component}/            # Component README templates

 .claude/                     # Claude Code configuration
    settings.local.json.template

 docs/                        # Technical documentation
     adr/                    # Architecture Decision Records
     qa/                     # QA documentation
     core/                   # Technical specifications
     ...
```

## Key Features

### AI-First Development Workflow

1. **Issue Processing** - Structured 4-phase workflow before implementation
2. **AI Label Lifecycle** - `ai:ready` → `ai:in-progress` → `ai:review-requested`
3. **Board Sync** - Automatic GitHub Project board status updates
4. **AI Code Review** - Automated PR review using Claude Code CLI

### Phase-Gated Deployment

- **Dev** - Automatic deployment on merge to main
- **Staging** - Deployment on phase completion
- **Production** - Manual trigger with QA approval

### Multi-Cloud Support

- **GCP** - Full support with Cloud Run, Artifact Registry, Workload Identity Federation
- **AWS** - Template support (setup scripts in development)
- **Azure** - Template support (setup scripts in development)

## Documentation

| Document | Purpose |
|----------|---------|
| [CONFIG.md](CONFIG.md) | Complete placeholder variable reference |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Step-by-step customization guide |
| [CLOUD_GUIDE.md](CLOUD_GUIDE.md) | Cloud provider comparison and setup |
| [governance/GOVERNANCE_RULES.md](governance/GOVERNANCE_RULES.md) | Operational rules and conventions |
| [templates/CLAUDE.md](templates/CLAUDE.md) | AI agent configuration template |

## Requirements

- GitHub (github.com or GitHub Enterprise Server)
- Cloud provider account (GCP, AWS, or Azure)
- Claude Code CLI (for AI code review)
- Python 3.9+ (for workflow scripts)

## Relationship to SDD Methodology

This framework is a **lightweight alternative** to the full Specification-Driven Development (SDD) methodology:

| Aspect | SDD (ai_dev_flow) | This Framework |
|--------|-------------------|----------------|
| Scope | Large projects | Small-medium projects |
| Layers | 12 formal layers | Agile phases/sprints |
| Docs | BRD→PRD→REQ→SPEC→TASKS | PROJECT_PLAN + IPLANs |
| Traceability | Full requirement tracing | Issue-based tracking |
| Timeline | Months-years | 1-6 months |
| Team | Multiple roles | Solo/small team + AI |

For larger projects requiring formal requirements traceability, use the full SDD methodology in `ai_dev_flow/`.

## License

This framework is provided as-is for use in AI-first software development projects.
