# GitHub Tools Setup Guide

This document describes the tools available for AI assistants to interact with GitHub repositories and projects.

---

## Tool Strategy

**Primary Tool**: GitHub MCP Server (AI-native, direct tool calls)
**Fallback**: gh CLI (for operations not supported by MCP)

| Tool | Type | Status | Use Case |
|:-----|:-----|:-------|:---------|
| **GitHub MCP Server** | AI-native protocol | **Primary** | All issue/PR/branch/file operations |
| **gh CLI** | Command-line | Fallback | Projects V2, labels, milestones, GraphQL |

### Loading MCP Tools (Required Before Use)

MCP tools are **deferred** and must be loaded before calling. Use `ToolSearch`:

```python
# Option 1: Search by keyword (loads matching tools)
ToolSearch(query="+github issue")

# Option 2: Direct selection (if you know the exact tool name)
ToolSearch(query="select:mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__issue_write")
```

**IMPORTANT**: After `ToolSearch` returns tools, they are loaded and ready to call. Do NOT call `select:` again for tools already returned by a keyword search.

---

## 1. GitHub CLI (gh)

### 1.1 Installation

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Verify
gh --version
```

### 1.2 Authentication (GitHub Enterprise)

```bash
# Interactive login
gh auth login --hostname {GITHUB_HOST}

# Add required scopes
gh auth refresh --hostname {GITHUB_HOST} \
  --scopes project,repo,workflow,read:org,gist

# Verify
gh auth status --hostname {GITHUB_HOST}
```

### 1.3 Environment Setup

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export GH_HOST={GITHUB_HOST}
export GH_ORG="{GITHUB_ORG}"
export GH_REPO="{REPO_NAME}"
```

### 1.4 Extensions

```bash
# Install gh-projects extension
gh extension install github/gh-projects

# Verify
gh projects --help
```

### 1.5 Common Commands

#### Issues

```bash
# List issues
gh issue list

# List with filters
gh issue list --label "ai:ready" --state open

# View issue
gh issue view 123

# Create issue
gh issue create --title "Bug: API timeout" --body "Description" --label "type:bug"

# Update issue labels
gh issue edit 123 --add-label "ai:in-progress" --remove-label "ai:ready"

# Add comment
gh issue comment 123 --body "Working on this"

# Close issue
gh issue close 123
```

#### Pull Requests

```bash
# List PRs
gh pr list

# View PR
gh pr view 123

# Create PR
gh pr create --title "Fix API timeout" --body "Closes #123" --base main --head ai/123-fix-timeout

# Review PR
gh pr review 123 --approve --body "LGTM"

# Merge PR
gh pr merge 123 --squash --delete-branch
```

#### Projects V2 (GraphQL)

```bash
# List project items
gh api graphql -f query='
  query($org: String!, $number: Int!) {
    organization(login: $org) {
      projectV2(number: $number) {
        items(first: 20) {
          nodes {
            content {
              ... on Issue { title number }
            }
          }
        }
      }
    }
  }' -f org="$GH_ORG" -F number=31

# Get project field IDs
gh projects field-list 31 --org $GH_ORG --format json
```

#### Labels

```bash
# List labels
gh label list

# Create label
gh label create "ai:ready" --color "0e8a16" --description "Ready for AI"

# Delete label
gh label delete "old-label" --yes
```

#### Workflows

```bash
# List workflows
gh workflow list

# Run workflow
gh workflow run ci.yml

# View run status
gh run view 12345

# View logs
gh run view 12345 --log
```

---

## 2. GitHub MCP Server (Primary)

### 2.1 Overview

The Model Context Protocol (MCP) server provides AI-native access to GitHub APIs. AI assistants call MCP tools directly without shell execution, providing:

- **Structured responses**: Native JSON, no parsing required
- **Direct tool calls**: No shell command construction
- **Error handling**: Typed errors with context
- **Batch operations**: `push_files` for multi-file commits
- **Extended features**: Sub-issues, notifications, discussions

### 2.2 Installation

The MCP server runs via Docker (official GitHub image):

```bash
# Pull the official GitHub MCP server image
docker pull ghcr.io/github/github-mcp-server:latest

# Verify version
docker run -i --rm ghcr.io/github/github-mcp-server --version
```

**Current Version**: v0.30.3 (Build Date: {DATE})

### 2.3 Configuration for GitHub Enterprise

#### Step 1: Generate Personal Access Token

1. Navigate to: `https://{GITHUB_HOST}/settings/tokens`
2. Click **Generate new token (classic)**
3. Set expiration (recommend 90 days)
4. Select required scopes (see 2.4)
5. Copy token immediately (shown only once)

#### Step 2: Configure MCP Server

**Option A: User-Level Config** (`~/.claude/settings.json`)

```json
{
  "mcpServers": {
    "github-{PROJECT_PREFIX}-{PROJECT_PREFIX}": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server",
        "--gh-host", "https://{GITHUB_HOST}",
        "stdio"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    }
  }
}
```

**Option B: Project-Level Config** (`.mcp.json` in repo root) - **Recommended** [PASS] Current

```json
{
  "mcpServers": {
    "github-{PROJECT_PREFIX}-{PROJECT_PREFIX}": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx...",
        "ghcr.io/github/github-mcp-server",
        "--gh-host", "https://{GITHUB_HOST}",
        "stdio"
      ]
    }
  }
}
```

**Option C: Claude Desktop Config** (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "github-{PROJECT_PREFIX}-{PROJECT_PREFIX}": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server",
        "--gh-host", "https://{GITHUB_HOST}",
        "stdio"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    }
  }
}
```

**Note**: The `-tt-{PROJECT_PREFIX}` suffix indicates TechTrend GitHub Enterprise instance (`tt`) and AI Cost Monitoring project (`{PROJECT_PREFIX}`).

#### Step 3: Set Environment Variable (for Option B)

```bash
# Add to ~/.bashrc or ~/.zshrc
export GH_TOKEN="ghp_xxxxxxxxxxxx"
```

#### Step 4: Restart {AI_TOOL_NAME} Code/Desktop

After configuration changes, restart the AI assistant to load the new MCP server.

### 2.4 Token Scopes (Required)

| Scope | Required | Purpose |
|:------|:--------:|:--------|
| `repo` | [PASS] | Full repository access (issues, PRs, code) |
| `workflow` | [PASS] | GitHub Actions (run, view, cancel) |
| `read:org` | [PASS] | Organization membership, teams |
| `gist` | Optional | Gist creation/management |
| `notifications` | Optional | Notification management |
| `project` | Optional | Projects V2 (if using GraphQL via gh CLI) |

**Minimum scopes for AI workflow**: `repo`, `workflow`, `read:org`

### 2.5 Security Considerations

| Practice | Description |
|:---------|:------------|
| **Token rotation** | Rotate tokens every 90 days |
| **Minimal scopes** | Only grant required scopes |
| **Environment variables** | Never hardcode tokens in config files committed to git |
| **Audit logs** | Review token usage in GHE audit logs |
| **.gitignore** | Add `.mcp.json` if it contains tokens |

```bash
# Add to .gitignore if using hardcoded tokens
echo ".mcp.json" >> .gitignore
```

### 2.6 Verification

After setup, verify MCP server connectivity:

```bash
# Check Docker image version
docker run -i --rm ghcr.io/github/github-mcp-server --version

# Test API connectivity (via gh CLI)
GH_HOST={GITHUB_HOST} gh api user --jq '.login'
```

In {AI_TOOL_NAME} Code, the AI can call:

```
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__list_issues(owner="{GITHUB_ORG}", repo="{REPO_NAME}")
```

Expected: List of repository issues (not 401 error)

### 2.5 Available MCP Tools

#### Issues

| Tool | Description |
|:-----|:------------|
| `list_issues` | List issues with filters |
| `get_issue` | Get issue details |
| `create_issue` | Create new issue |
| `update_issue` | Update issue (title, body, labels, state) |
| `add_issue_comment` | Add comment to issue |
| `search_issues` | Search issues with query syntax |
| `add_sub_issue` | Add sub-issue to parent |
| `list_sub_issues` | List sub-issues |

#### Pull Requests

| Tool | Description |
|:-----|:------------|
| `list_pull_requests` | List PRs with filters |
| `get_pull_request` | Get PR details |
| `create_pull_request` | Create new PR |
| `update_pull_request` | Update PR |
| `merge_pull_request` | Merge PR |
| `get_pull_request_diff` | Get PR diff |
| `get_pull_request_files` | Get changed files |
| `get_pull_request_reviews` | Get PR reviews |
| `create_and_submit_pull_request_review` | Submit review |
| `update_pull_request_branch` | Update branch from base |

#### Branches & Files

| Tool | Description |
|:-----|:------------|
| `list_branches` | List repository branches |
| `create_branch` | Create new branch |
| `get_file_contents` | Get file or directory contents |
| `create_or_update_file` | Create or update single file |
| `push_files` | Push multiple files in one commit |
| `delete_file` | Delete file |

#### Workflows

| Tool | Description |
|:-----|:------------|
| `list_workflows` | List repository workflows |
| `run_workflow` | Trigger workflow |
| `list_workflow_runs` | List workflow runs |
| `get_workflow_run` | Get run details |
| `get_job_logs` | Get job logs |
| `cancel_workflow_run` | Cancel running workflow |
| `rerun_workflow_run` | Rerun workflow |

#### Search

| Tool | Description |
|:-----|:------------|
| `search_code` | Search code across repos |
| `search_issues` | Search issues |
| `search_pull_requests` | Search PRs |
| `search_repositories` | Search repos |
| `search_users` | Search users |

#### Other

| Tool | Description |
|:-----|:------------|
| `list_notifications` | List notifications |
| `get_discussion` | Get discussion details |
| `list_discussions` | List discussions |
| `create_gist` | Create gist |
| `list_gists` | List gists |
| `fork_repository` | Fork a repository |
| `create_repository` | Create new repository |
| `assign_copilot_to_issue` | Assign GitHub Copilot to issue |

---

## 3. Comparison Matrix

### 3.1 Feature Comparison

| Feature | MCP Server | gh CLI | Winner |
|:--------|:----------:|:------:|:-------|
| **Issues** |
| List/View/Create/Update | [PASS] | [PASS] | Equal |
| Sub-issues | [PASS] | [FAIL] | **MCP** |
| **Pull Requests** |
| Full CRUD | [PASS] | [PASS] | Equal |
| Update branch from base | [PASS] | [FAIL] | **MCP** |
| **Branches** |
| List | [PASS] | [PASS] | Equal |
| Create (remote, no local git) | [PASS] | [FAIL] | **MCP** |
| **Files** |
| Read/Write single | [PASS] | [PASS] | Equal |
| Push multiple files (atomic) | [PASS] | [FAIL] | **MCP** |
| **Projects V2** |
| Full access | [FAIL] | [PASS] (GraphQL) | **gh CLI** |
| **Labels** |
| CRUD | [FAIL] | [PASS] | **gh CLI** |
| **Milestones** |
| CRUD | [FAIL] | [PASS] | **gh CLI** |
| **Workflows** |
| Full access | [PASS] | [PASS] | Equal |
| **Search** |
| Code/Issues/Repos | [PASS] | [PASS] | Equal |
| **Notifications** |
| List/Manage | [PASS] | [FAIL] | **MCP** |
| **Discussions** |
| Read | [PASS] | [FAIL] | **MCP** |
| **API Flexibility** |
| Any endpoint | [FAIL] | [PASS] (`gh api`) | **gh CLI** |
| GraphQL | [FAIL] | [PASS] | **gh CLI** |

### 3.2 Why MCP is Primary

| Advantage | Description |
|:----------|:------------|
| **AI-native** | Direct tool calls, no shell command construction |
| **Structured data** | Native JSON responses, no parsing |
| **Atomic operations** | `push_files` commits multiple files in one call |
| **Remote-first** | Create branches, push files without local git |
| **Extended features** | Sub-issues, notifications, discussions |
| **Error handling** | Typed errors with context |
| **No shell injection** | Tool parameters, not command strings |

### 3.3 gh CLI Fallback Cases

MCP lacks support for these operations (use gh CLI):

| Operation | gh CLI Command |
|:----------|:---------------|
| Projects V2 | `gh api graphql -f query='mutation {...}'` |
| Create label | `gh label create "name" --color "hex"` |
| Delete label | `gh label delete "name"` |
| Create milestone | `gh api repos/OWNER/REPO/milestones -f title="..."` |
| Custom API | `gh api /repos/OWNER/REPO/...` |

### 3.2 When to Use Each

| Scenario | Tool | Reason |
|:---------|:-----|:-------|
| **MCP Server (Primary)** |
| Issue CRUD | MCP | Direct tool calls, structured responses |
| PR CRUD | MCP | Direct tool calls, structured responses |
| Create branch | MCP | No local git required |
| Push files | MCP | Multi-file commits in one call |
| Search code/issues | MCP | Native search syntax |
| Notifications | MCP | Only available in MCP |
| Discussions | MCP | Only available in MCP |
| Sub-issues | MCP | Only available in MCP |
| Workflow management | MCP | Direct tool calls |
| **gh CLI (Fallback)** |
| Projects V2 | gh CLI | Requires GraphQL (not in MCP) |
| Labels CRUD | gh CLI | Not exposed in MCP |
| Milestones CRUD | gh CLI | Not exposed in MCP |
| Custom API endpoints | gh CLI | `gh api` for any endpoint |
| GraphQL queries | gh CLI | Full GraphQL support |

---

## 4. Project Configuration

### 4.1 Repository Details

| Field | Value |
|:------|:------|
| Host | `{GITHUB_HOST}` |
| Organization | `{GITHUB_ORG}` |
| Repository | `{REPO_NAME}` |
| Project Board | `#{PROJECT_BOARD_NUMBER}` |

### 4.2 Setup Status

| Tool | Status | Notes |
|:-----|:-------|:------|
| MCP Servers (6 total) | [PASS] All Active | See Section 4.5 for details |
| gh CLI | [PASS] Active | Fallback for Projects V2, labels |

### 4.3 MCP Configuration for This Project

The project includes `.mcp.json` with 6 MCP servers using the `-tt-{PROJECT_PREFIX}` suffix (TechTrend AI Cost Monitoring).

**Naming Convention**: `{function}-tt-{PROJECT_PREFIX}`

- `tt` = TechTrend (GitHub Enterprise instance)
- `{PROJECT_PREFIX}` = AI Cost Monitoring project prefix

GitHub server configuration:

```json
{
  "mcpServers": {
    "github-{PROJECT_PREFIX}-{PROJECT_PREFIX}": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx...",
        "ghcr.io/github/github-mcp-server",
        "--gh-host", "https://{GITHUB_HOST}",
        "stdio"
      ]
    }
  }
}
```

See `.mcp.json` in repository root for complete configuration (6 servers).

### 4.4 Required Environment Variables

The current configuration embeds the GitHub token directly in `.mcp.json`. For gh CLI fallback:

```bash
# Add to ~/.bashrc or ~/.zshrc

# ============================================
# REQUIRED - gh CLI Fallback
# ============================================
export GH_HOST={GITHUB_HOST}
export GH_ORG="{GITHUB_ORG}"
export GH_REPO="{REPO_NAME}"
```

#### Environment Variables for Future Phases

When additional MCP servers are added:

| Server | Required Variables | Phase |
|:-------|:-------------------|:------|
| aws | `AWS_PROFILE`, `AWS_REGION` | Phase 3 |
| postgres | `POSTGRES_CONNECTION_STRING` | Phase 7 |
| teams | `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` | All Phases |
| sqlite | `SQLITE_DB_PATH` | Optional |

### 4.5 MCP Servers Overview

All 6 servers configured in `.mcp.json` are open source and active.

#### Active Servers (6 total)

| Server | Package | License | Purpose | Status |
|:-------|:--------|:--------|:--------|:------:|
| **github-{PROJECT_PREFIX}-{PROJECT_PREFIX}** | `ghcr.io/github/github-mcp-server` (Docker) | MIT | Issues, PRs, branches, files, workflows | [PASS] Active |
| **filesystem-tt-{PROJECT_PREFIX}** | `@modelcontextprotocol/server-filesystem` | MIT | Secure file operations | [PASS] Active |
| **memory-tt-{PROJECT_PREFIX}** | `@modelcontextprotocol/server-memory` | MIT | Persistent knowledge graph | [PASS] Active |
| **sequential-thinking-tt-{PROJECT_PREFIX}** | `@modelcontextprotocol/server-sequential-thinking` | MIT | Problem decomposition | [PASS] Active |
| **context7-tt-{PROJECT_PREFIX}** | `@upstash/context7-mcp` | Free Tier | Library documentation lookup | [PASS] Active |
| **playwright-tt-{PROJECT_PREFIX}** | `@playwright/mcp` | Apache 2.0 | Browser automation, E2E tests | [PASS] Active |

**Total: 6 MCP Servers (All Open Source)**

#### License Summary

| License | Servers | Source |
|:--------|:--------|:-------|
| MIT | github-{PROJECT_PREFIX}-{PROJECT_PREFIX}, filesystem-tt-{PROJECT_PREFIX}, memory-tt-{PROJECT_PREFIX}, sequential-thinking-tt-{PROJECT_PREFIX} | [GitHub MCP Server](https://github.com/github/github-mcp-server), [MCP Official](https://github.com/modelcontextprotocol/servers) |
| Apache 2.0 | playwright-tt-{PROJECT_PREFIX} | Microsoft |
| Free Tier | context7-tt-{PROJECT_PREFIX} | Upstash |

#### Servers Not Configured (Available for Future Phases)

| Server | Package | Purpose | Phase |
|:-------|:--------|:--------|:------|
| git | `@modelcontextprotocol/server-git` | Git repository operations | Optional |
| fetch | `@modelcontextprotocol/server-fetch` | Web content fetching | Optional |
| time | `@modelcontextprotocol/server-time` | Time/timezone operations | Optional |
| postgres | `@modelcontextprotocol/server-postgres` | PostgreSQL database | Phase 7 |
| sqlite | `@modelcontextprotocol/server-sqlite` | SQLite local testing | Optional |
| aws | `@awslabs/mcp-server-aws-core` | AWS Cost Explorer, IAM | Phase 3 |
| teams | `msteams-mcp-server` | Microsoft Teams messaging | All Phases |

### 4.6 AI Assistant Workflow

```

              AI ASSISTANT - 6 ACTIVE MCP SERVERS
              (All using -tt-{PROJECT_PREFIX} suffix)


  CORE DEVELOPMENT (4)
   github-{PROJECT_PREFIX}-{PROJECT_PREFIX} (Docker)
      Issues, PRs, branches, files, workflows
   filesystem-tt-{PROJECT_PREFIX}
      File operations
   memory-tt-{PROJECT_PREFIX}
      Knowledge graph
   sequential-thinking-tt-{PROJECT_PREFIX}
       Problem decomposition

  DOCUMENTATION (1)
   context7-tt-{PROJECT_PREFIX}
       Library docs lookup

  BROWSER AUTOMATION (1)
   playwright-tt-{PROJECT_PREFIX}
       E2E tests, web scraping


  gh CLI (Fallback - only when MCP lacks support)
   Projects V2, Labels, Milestones, GraphQL

  Local git (Workspace operations)
   git add, commit, push

```

### 4.7 Operation Mapping

| Operation | Tool | Command/Tool |
|:----------|:-----|:-------------|
| List AI-ready issues | MCP | `mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__list_issues(labels=["ai:ready"])` |
| Claim issue | MCP | `mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__update_issue(labels=["ai:in-progress"])` |
| Create feature branch | MCP | `mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__create_branch(branch="ai/123-feature")` |
| Push implementation | MCP | `mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__push_files(files=[...], message="...")` |
| Create PR | MCP | `mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__create_pull_request(head, base, title)` |
| Request review | MCP | `mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__update_pull_request(reviewers=[...])` |
| Read file | MCP | `mcp__filesystem-tt-{PROJECT_PREFIX}__read_file(path="...")` |
| Store knowledge | MCP | `mcp__memory-tt-{PROJECT_PREFIX}__create_entities(entities=[...])` |
| Lookup docs | MCP | `mcp__context7-tt-{PROJECT_PREFIX}__query_docs(query="...")` |
| Browser automation | MCP | `mcp__playwright-tt-{PROJECT_PREFIX}__browser_navigate(url="...")` |
| Update project status | gh CLI | `gh api graphql` (Projects V2) |
| Manage labels | gh CLI | `gh label create/edit/delete` |

---

## 5. Troubleshooting

### gh CLI Issues

```bash
# Check authentication
gh auth status --hostname {GITHUB_HOST}

# Re-authenticate
gh auth login --hostname {GITHUB_HOST}

# Check scopes
gh auth refresh --hostname {GITHUB_HOST} --scopes project,repo,workflow
```

### MCP Server Issues

| Error | Cause | Solution |
|:------|:------|:---------|
| `401 Bad credentials` | Wrong token or missing `--gh-host` | Check token and `--gh-host` flag |
| `404 Not Found` | Wrong owner/repo | Verify repository path |
| Tool not found | Tool not loaded | Use `ToolSearch` first |
| Docker container exits | Missing `-i` flag or token | Ensure `-i --rm` and `-e GITHUB_PERSONAL_ACCESS_TOKEN` |
| Old version | Stale Docker image | Run `docker pull ghcr.io/github/github-mcp-server:latest` |

### Common Fixes

```bash
# Verify GHE connectivity
curl -I https://{GITHUB_HOST}

# Test API access
gh api repos/{GITHUB_ORG}/{REPO_NAME} --hostname {GITHUB_HOST}

# Check token scopes
gh auth status --hostname {GITHUB_HOST} --show-token

# Update Docker image
docker pull ghcr.io/github/github-mcp-server:latest

# Check MCP server version
docker run -i --rm ghcr.io/github/github-mcp-server --version

# Test MCP server manually
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="$GH_TOKEN" \
  ghcr.io/github/github-mcp-server \
  --gh-host https://{GITHUB_HOST} \
  --version
```

---

## 6. Quick Reference

### Environment Variables

```bash
export GH_HOST={GITHUB_HOST}           # For gh CLI fallback
export GH_ORG={GITHUB_ORG}
export GH_REPO={REPO_NAME}
export PROJECT_NUMBER=31
```

### Loading MCP Tools (Required First Step)

```python
# IMPORTANT: Load MCP tools before use
# Option 1: Keyword search (loads all matching tools)
ToolSearch(query="+github issue")

# Option 2: Direct selection
ToolSearch(query="select:mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__issue_write")

# After loading, tools are available to call
```

### MCP Tool Patterns (Primary)

```python
# Repository constants
OWNER = "{GITHUB_ORG}"
REPO = "{REPO_NAME}"

# List AI-ready issues (use list_issues or search_issues)
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__list_issues(owner=OWNER, repo=REPO, labels=["ai:ready"])

# Get issue details
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__get_issue(owner=OWNER, repo=REPO, issue_number=123)

# Claim issue (update labels)
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__update_issue(
    owner=OWNER, repo=REPO, issue_number=123,
    labels=["ai:in-progress", "type:feature"]
)

# Add progress comment
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__add_issue_comment(
    owner=OWNER, repo=REPO, issue_number=123,
    body="Started implementation."
)

# Create feature branch
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__create_branch(
    owner=OWNER, repo=REPO,
    branch="ai/123-add-budget-alerts"
)

# Push implementation
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__push_files(
    owner=OWNER, repo=REPO,
    branch="ai/123-add-budget-alerts",
    message="feat: add budget alerts\n\nCloses #123",
    files=[
        {"path": "src/alerts.py", "content": "..."},
        {"path": "tests/test_alerts.py", "content": "..."}
    ]
)

# Create pull request
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__create_pull_request(
    owner=OWNER, repo=REPO,
    title="feat: add budget alerts",
    head="ai/123-add-budget-alerts",
    base="main",
    body="## Summary\nImplements budget alert system.\n\nCloses #123"
)

# Search issues
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__search_issues(
    query="repo:{GITHUB_ORG}/{REPO_NAME} label:ai:ready"
)
```

### gh CLI Commands (Fallback)

```bash
# Projects V2 (not in MCP)
gh projects field-list $PROJECT_NUMBER --org $GH_ORG

# Labels (not in MCP)
gh label create "ai:ready" --color "0e8a16"
gh label list

# Milestones (not in MCP)
gh api repos/$GH_ORG/$GH_REPO/milestones

# GraphQL (not in MCP)
gh api graphql -f query='...'
```

### AI Workflow Commands

```python
# Complete AI workflow using MCP (github-{PROJECT_PREFIX}-{PROJECT_PREFIX})

# 1. Find work
issues = mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__list_issues(owner, repo, labels=["ai:ready"])

# 2. Claim issue
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__update_issue(owner, repo, issue_number,
    labels=["ai:in-progress"])

# 3. Create branch
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__create_branch(owner, repo,
    branch=f"ai/{issue_number}-{slug}")

# 4. Implement & push
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__push_files(owner, repo, branch, files, message)

# 5. Create PR
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__create_pull_request(owner, repo, title, head, base, body)

# 6. Mark for review
mcp__github-{PROJECT_PREFIX}-{PROJECT_PREFIX}__update_issue(owner, repo, issue_number,
    labels=["ai:review-requested"])
```

---

## 7. Browser Automation (Playwright MCP)

### 7.1 Overview

The Playwright MCP server provides browser automation capabilities for:

- **E2E Testing**: Automated testing of web interfaces
- **Web Scraping**: Extracting data from web pages
- **Visual Verification**: Screenshot capture and comparison
- **Form Automation**: Filling forms, clicking buttons, navigating pages
- **Console Monitoring**: Capturing browser console logs and errors

### 7.2 Configuration

The Playwright MCP server is configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Package**: `@playwright/mcp` (Apache 2.0 License)

### 7.3 Available Tools

#### Navigation

| Tool | Description |
|:-----|:------------|
| `browser_navigate` | Navigate to a URL |
| `browser_navigate_back` | Go back in browser history |
| `browser_tabs` | List open browser tabs |

#### Interaction

| Tool | Description |
|:-----|:------------|
| `browser_click` | Click an element by reference |
| `browser_fill_form` | Fill form fields |
| `browser_type` | Type text into focused element |
| `browser_press_key` | Press keyboard key |
| `browser_hover` | Hover over an element |
| `browser_drag` | Drag element to target |
| `browser_select_option` | Select dropdown option |
| `browser_file_upload` | Upload file to input |
| `browser_handle_dialog` | Accept/dismiss dialogs |

#### Inspection

| Tool | Description |
|:-----|:------------|
| `browser_snapshot` | Capture accessibility tree (preferred over screenshot) |
| `browser_take_screenshot` | Capture visual screenshot |
| `browser_console_messages` | Get console logs/errors |
| `browser_network_requests` | List network requests |

#### Execution

| Tool | Description |
|:-----|:------------|
| `browser_run_code` | Execute custom Playwright JavaScript |
| `browser_evaluate` | Evaluate JavaScript in page context |
| `browser_wait_for` | Wait for element/condition |

#### Management

| Tool | Description |
|:-----|:------------|
| `browser_resize` | Resize browser window |
| `browser_close` | Close current page |
| `browser_install` | Install browser binaries |

### 7.4 Usage Examples

#### Navigate and Capture Snapshot

```python
# Navigate to page
mcp__playwright-tt-{PROJECT_PREFIX}__browser_navigate(url="https://console.cloud.google.com/billing")

# Capture accessibility tree (structured data)
mcp__playwright-tt-{PROJECT_PREFIX}__browser_snapshot()
```

#### Fill Login Form

```python
# Navigate to login
mcp__playwright-tt-{PROJECT_PREFIX}__browser_navigate(url="https://example.com/login")

# Fill form fields
mcp__playwright-tt-{PROJECT_PREFIX}__browser_fill_form(
    fields=[
        {"selector": "#username", "value": "user@example.com"},
        {"selector": "#password", "value": "********"}
    ]
)

# Click submit
mcp__playwright-tt-{PROJECT_PREFIX}__browser_click(ref="e5")  # ref from snapshot
```

#### Run Custom Playwright Code

```python
# Execute custom JavaScript with Playwright API
mcp__playwright-tt-{PROJECT_PREFIX}__browser_run_code(
    code="""async (page) => {
        await page.getByRole('button', { name: 'Submit' }).click();
        await page.waitForURL('**/dashboard');
        return await page.title();
    }"""
)
```

#### Monitor Console Errors

```python
# Get console messages (errors and warnings)
mcp__playwright-tt-{PROJECT_PREFIX}__browser_console_messages(level="warning")
```

#### Take Screenshot

```python
# Capture screenshot to file
mcp__playwright-tt-{PROJECT_PREFIX}__browser_take_screenshot(
    filename="tmp/billing-dashboard.png"
)
```

### 7.5 Element References

Playwright MCP uses `ref` attributes from snapshots to identify elements:

1. **Capture snapshot**: `browser_snapshot()` returns accessibility tree with `[ref=eN]` markers
2. **Use reference**: Pass `ref="eN"` to interaction tools

Example snapshot output:

```yaml
- generic [ref=e2]:
  - heading "Dashboard" [level=1] [ref=e3]
  - button "Export" [ref=e4] [cursor=pointer]
  - link "Settings" [ref=e5]:
    - /url: /settings
```

To click "Export" button: `browser_click(ref="e4")`

### 7.6 Use Cases for This Project

| Use Case | Application |
|:---------|:------------|
| **GCP Billing Verification** | Navigate GCP console, verify cost data |
| **Dashboard Testing** | E2E tests for cost monitoring dashboards |
| **Alert Validation** | Verify alert notifications render correctly |
| **Report Generation** | Screenshot cost reports for documentation |
| **Integration Testing** | Test MCP server web interfaces |

### 7.7 Troubleshooting

| Error | Cause | Solution |
|:------|:------|:---------|
| `browser_install` required | Browser binaries not installed | Run `mcp__playwright__browser_install()` |
| Element not found | Invalid ref or page changed | Capture new snapshot, use updated ref |
| Timeout | Page load slow or element not visible | Use `browser_wait_for` before interaction |
| Console errors (404) | Normal for favicon, external resources | Check `browser_console_messages` for actual errors |

#### Install Browser Binaries

If browsers are not installed:

```bash
# Via npx
npx playwright install chromium

# Or via MCP tool
mcp__playwright__browser_install()
```

#### Debug Page State

```python
# 1. Capture snapshot to see current page structure
mcp__playwright-tt-{PROJECT_PREFIX}__browser_snapshot()

# 2. Check console for JavaScript errors
mcp__playwright-tt-{PROJECT_PREFIX}__browser_console_messages(level="error")

# 3. List network requests for failed API calls
mcp__playwright-tt-{PROJECT_PREFIX}__browser_network_requests()
```

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.5 | {DATE} | Fixed MCP server naming consistency: `github-{PROJECT_PREFIX}` → `github-{PROJECT_PREFIX}-{PROJECT_PREFIX}` in all examples to match .mcp.json |
| 1.4 | {DATE} | Added ToolSearch requirement for loading MCP tools before use; added MCP tool loading examples to Tool Strategy and Quick Reference sections |
| 1.3 | {DATE} | Updated to reflect actual 6 MCP servers with `-tt-{PROJECT_PREFIX}` naming convention; removed unconfigured servers |
| 1.2 | {DATE} | Added Section 7: Browser Automation (Playwright MCP) with tools, examples, and troubleshooting |
| 1.1 | {DATE} | Updated to Docker-based GitHub MCP server (v0.30.3) |
| 1.0 | {DATE} | Initial document |
