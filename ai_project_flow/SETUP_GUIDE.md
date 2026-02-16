# Framework Setup Guide

Step-by-step guide for customizing the AI-First Project Governance Framework for your project.

## Prerequisites

- [ ] GitHub account with organization access
- [ ] Cloud provider account (GCP, AWS, or Azure)
- [ ] Git installed locally
- [ ] Claude Code CLI installed (for AI review features)
- [ ] Python 3.9+ (for workflow scripts)

---

## Phase 1: Initial Setup

### Step 1.1: Copy Framework

```bash
# Create your project directory
mkdir /path/to/your-project
cd /path/to/your-project

# Copy the framework
cp -r /path/to/ai_project_flow/* .

# Initialize git
git init
```

### Step 1.2: Gather Configuration Values

Before proceeding, collect these values:

| Variable | Your Value |
|----------|------------|
| Project prefix (short, lowercase) | _____________ |
| Project full name | _____________ |
| Repository name | _____________ |
| GitHub organization | _____________ |
| GitHub host | _____________ |
| Primary reviewer username | _____________ |
| Secondary reviewer username | _____________ |
| Cloud provider (GCP/AWS/Azure) | _____________ |

---

## Phase 2: Core Configuration

### Step 2.1: Replace Core Placeholders

Run these commands from your project root, replacing the example values:

```bash
# Project identifiers
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{PROJECT_PREFIX}|YOUR_PREFIX|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{PROJECT_NAME}|Your Project Name|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{REPO_NAME}|your-repo-name|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{GITHUB_ORG}|your-org|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{GITHUB_HOST}|github.com|g' {} \;
```

### Step 2.2: Configure Team

```bash
# Team configuration
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{CODEOWNER_1}|@your-lead-username|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{CODEOWNER_2}|@your-reviewer-username|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{TEAM_SLUG}|your-team|g' {} \;
```

---

## Phase 3: GitHub Setup

### Step 3.1: Create Repository

```bash
# Create repository on GitHub
gh repo create YOUR_ORG/YOUR_REPO --private --description "Your project description"

# Push initial code
git add .
git commit -m "Initial commit: AI-First Project Framework"
git branch -M main
git remote add origin https://github.com/YOUR_ORG/YOUR_REPO.git
git push -u origin main
```

### Step 3.2: Create Project Board

1. Go to your organization: `https://github.com/YOUR_ORG`
2. Click **Projects** → **New project**
3. Select **Board** template
4. Name it: `YOUR_PROJECT - Development Board`
5. Note the project number from the URL

```bash
# Update project board number
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{PROJECT_BOARD_NUMBER}|YOUR_NUMBER|g' {} \;
```

### Step 3.3: Get Board Field IDs

```bash
# Get board configuration
GH_HOST=YOUR_GITHUB_HOST gh api graphql -f query='
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

Update the board IDs:

```bash
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{BOARD_PROJECT_ID}|PVT_...|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{BOARD_STATUS_FIELD_ID}|PVTSSF_...|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{BOARD_OPTION_IN_PROGRESS}|option_id_here|g' {} \;

# Repeat for IN_REVIEW, DONE, etc.
```

### Step 3.4: Create Labels

```bash
# Create AI workflow labels
GH_HOST=YOUR_GITHUB_HOST gh label create "ai:ready" --color "0E8A16" --description "Ready for AI processing"
GH_HOST=YOUR_GITHUB_HOST gh label create "ai:in-progress" --color "1D76DB" --description "AI is working on this"
GH_HOST=YOUR_GITHUB_HOST gh label create "ai:review-requested" --color "FBCA04" --description "AI work done, review needed"
GH_HOST=YOUR_GITHUB_HOST gh label create "ai:review-passed" --color "0E8A16" --description "AI review passed"
GH_HOST=YOUR_GITHUB_HOST gh label create "ai:review-failed" --color "D93F0B" --description "AI review failed"

# Create phase labels
for i in $(seq 1 8); do
  GH_HOST=YOUR_GITHUB_HOST gh label create "phase:$i" --color "C5DEF5" --description "Phase $i"
done

# Create component labels (customize as needed)
GH_HOST=YOUR_GITHUB_HOST gh label create "component:api" --color "BFD4F2"
GH_HOST=YOUR_GITHUB_HOST gh label create "component:frontend" --color "BFD4F2"
GH_HOST=YOUR_GITHUB_HOST gh label create "component:infra" --color "BFD4F2"
```

### Step 3.5: Configure Repository Settings

```bash
# Protect main branch
GH_HOST=YOUR_GITHUB_HOST gh api repos/YOUR_ORG/YOUR_REPO/branches/main/protection \
  -X PUT \
  -f required_status_checks='{"strict":true,"contexts":["ci"]}' \
  -f enforce_admins=false \
  -f required_pull_request_reviews='{"required_approving_review_count":1}'
```

---

## Phase 4: Cloud Provider Setup

### Option A: GCP Setup

See [CLOUD_GUIDE.md](CLOUD_GUIDE.md#gcp-setup) for detailed instructions.

```bash
# Run GCP setup scripts
cd scripts/project_setup/cloud/gcp

# 1. Create GCP projects
./setup-projects.sh

# 2. Set up Workload Identity Federation
./setup-wif.sh

# 3. Set up Artifact Registry
./setup_artifact_registry.sh

# 4. Configure environments
./setup-environments.sh
```

### Option B: AWS Setup

See [CLOUD_GUIDE.md](CLOUD_GUIDE.md#aws-setup) for detailed instructions.

### Option C: Azure Setup

See [CLOUD_GUIDE.md](CLOUD_GUIDE.md#azure-setup) for detailed instructions.

---

## Phase 5: AI Review Setup

### Step 5.1: Configure Claude Code

```bash
# Copy Claude configuration
cp .claude/settings.local.json.template .claude/settings.local.json

# Edit with your settings
nano .claude/settings.local.json
```

### Step 5.2: Set Up Anthropic API Key

```bash
# Add to GitHub secrets
GH_HOST=YOUR_GITHUB_HOST gh secret set ANTHROPIC_API_KEY --body "your-api-key"
```

### Step 5.3: Configure AI Review Model

```bash
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{AI_REVIEW_MODEL}|sonnet|g' {} \;

find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{AI_REVIEW_BUDGET}|1|g' {} \;
```

---

## Phase 6: Final Configuration

### Step 6.1: Configure Remaining Variables

```bash
# Timezone
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{TIMEZONE}|America/New_York|g' {} \;

# Service name
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{SERVICE_NAME}|your-service|g' {} \;

# Domain
find . -type f \( -name "*.md" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) \
  -exec sed -i 's|{DOMAIN}|yourdomain.com|g' {} \;
```

### Step 6.2: Validate Configuration

```bash
# Check for remaining placeholders
echo "=== Remaining placeholders ==="
grep -roh '\{[A-Z_]*\}' . --include="*.md" --include="*.yml" --include="*.sh" --include="*.json" | sort -u | grep -v "^{}$"

# If any remain, replace them before proceeding
```

### Step 6.3: Move Root Templates

```bash
# Move templates to project root
mv templates/README.md ./
mv templates/CLAUDE.md ./
mv templates/CONTRIBUTING.md ./
mv templates/DEVELOPER_GUIDE.md ./
mv templates/.mcp.json ./
mv templates/.env.example ./

# Keep deployment docs in templates or move as needed
```

---

## Phase 7: Verification

### Step 7.1: Test Workflows

```bash
# Create a test branch
git checkout -b test/setup-verification

# Make a small change
echo "# Test" >> TEST.md
git add TEST.md
git commit -m "Test: Verify CI/CD setup"
git push -u origin test/setup-verification

# Create PR and verify:
# - CI workflow runs
# - AI review triggers
# - Labels are applied correctly
```

### Step 7.2: Test Issue Templates

1. Go to **Issues** → **New issue**
2. Verify all templates appear correctly
3. Create a test issue with `ai:ready` label
4. Verify project board automation

### Step 7.3: Test Deployment (Optional)

```bash
# Trigger dev deployment
# (after merging test PR to main)
```

---

## Checklist

- [ ] Core placeholders replaced (PROJECT_PREFIX, PROJECT_NAME, etc.)
- [ ] Team configuration complete (CODEOWNERS, reviewers)
- [ ] GitHub repository created
- [ ] Project board configured with correct IDs
- [ ] Labels created
- [ ] Branch protection enabled
- [ ] Cloud provider configured
- [ ] Secrets added to GitHub
- [ ] AI review configured
- [ ] CI/CD tested
- [ ] Issue templates verified

---

## Troubleshooting

### Workflows not triggering

1. Check workflow files have correct syntax: `yamllint .github/workflows/*.yml`
2. Verify secrets are set: `gh secret list`
3. Check repository permissions for GitHub Actions

### Board automation not working

1. Verify board IDs are correct
2. Check `ELEVATED_PAT` secret has project permissions
3. Review workflow logs for GraphQL errors

### AI review not running

1. Verify `ANTHROPIC_API_KEY` is set
2. Check Claude Code CLI is available in runner
3. Review ai-review workflow logs

For more help, see [governance/GOVERNANCE_RULES.md](governance/GOVERNANCE_RULES.md).
