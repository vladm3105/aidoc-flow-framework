# AI PR Review — Local Setup

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Prerequisite for**: Manual AI PR review using {AI_TOOL_NAME} Code CLI

---

## Overview

This guide covers setting up your local environment for AI PR review using {AI_TOOL_NAME} Code CLI. For automated CI reviews, see [README.md](./README.md). For the on-demand agent review workflow, see [AI_AGENT_REVIEW_WORKFLOW.md](./AI_AGENT_REVIEW_WORKFLOW.md).

---

## Prerequisites Summary

| # | Task | Time |
|:--|:-----|:-----|
| 1 | Install {AI_TOOL_NAME} Code CLI | ~2 min |
| 2 | Configure GitHub Enterprise host | ~1 min |
| 3 | Authenticate `gh` CLI | ~2 min |
| 4 | Set Anthropic API key | ~1 min |
| 5 | Verify setup | ~2 min |

---

## 1. Install {AI_TOOL_NAME} Code CLI

{AI_TOOL_NAME} Code is Anthropic's official CLI for Claude. Install via npm:

```bash
npm install -g @anthropic-ai/claude-code
```

**Verification**:
```bash
claude --version
# Expected: 2.x.x or higher
```

**Alternative** (if npm is unavailable):
```bash
# Using npx (runs without global install)
npx @anthropic-ai/claude-code --version
```

---

## 2. Configure GitHub Enterprise Host

All `gh` commands require the GHES host prefix. Add to your shell profile:

```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
export GH_HOST={GITHUB_HOST}
```

Reload your shell or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

**Verification**:
```bash
echo $GH_HOST
# Expected: {GITHUB_HOST}
```

---

## 3. Authenticate gh CLI

The `gh` CLI must be authenticated to fetch PR diffs and post reviews.

### 3a. Check Existing Auth

```bash
GH_HOST={GITHUB_HOST} gh auth status
```

If you see "Logged in to {GITHUB_HOST}", skip to Step 4.

### 3b. Authenticate

```bash
GH_HOST={GITHUB_HOST} gh auth login --hostname {GITHUB_HOST}
```

Follow the prompts:
- Protocol: **HTTPS**
- Authentication method: **Login with a web browser** (recommended) or **Paste an authentication token**
- Required scopes: `repo`, `read:org`, `workflow`

### 3c. Verify Authentication

```bash
GH_HOST={GITHUB_HOST} gh auth status
# Expected:  Logged in to {GITHUB_HOST} as <username>

GH_HOST={GITHUB_HOST} gh repo view {GITHUB_ORG}/{REPO_NAME} --json name
# Expected: {"name":"{REPO_NAME}"}
```

---

## 4. Set Anthropic API Key

{AI_TOOL_NAME} Code requires an Anthropic API key. Obtain one from [console.anthropic.com](https://console.anthropic.com/).

### 4a. Set Environment Variable

```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

Reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### 4b. Alternative: Use .env File

Create a `.env` file in your project directory (already gitignored):

```bash
# {LOCAL_PROJECT_PATH}/{REPO_NAME}/.env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

{AI_TOOL_NAME} Code automatically loads `.env` files in the working directory.

### 4c. Verify

```bash
echo $ANTHROPIC_API_KEY | head -c 15
# Expected: sk-ant-api03-...
```

---

## 5. Verify Setup

Run a test review to confirm everything works:

### 5a. Start {AI_TOOL_NAME} Code

```bash
cd {LOCAL_PROJECT_PATH}/{REPO_NAME}
claude
```

### 5b. Test PR Fetch

In the {AI_TOOL_NAME} Code session, test fetching a PR:

```
Can you fetch the diff for PR #1 on {GITHUB_ORG}/{REPO_NAME} using the gh CLI?
```

If Claude successfully fetches the diff, your setup is complete.

### 5c. Test Review (Optional)

To run a full test review:

```
Review PR #<NUMBER> on {GITHUB_ORG}/{REPO_NAME}
following governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md
```

---

## Troubleshooting

| Issue | Cause | Solution |
|:------|:------|:---------|
| `command not found: claude` | CLI not installed | `npm install -g @anthropic-ai/claude-code` |
| `gh: command not found` | gh CLI not installed | Install from [cli.github.com](https://cli.github.com/) |
| `GH_HOST is not set` | Environment variable missing | `export GH_HOST={GITHUB_HOST}` |
| `gh auth status` shows not logged in | Token expired or missing | `GH_HOST={GITHUB_HOST} gh auth login --hostname {GITHUB_HOST}` |
| `401 Unauthorized` from gh | Token lacks required scopes | Re-authenticate with `repo`, `read:org`, `workflow` scopes |
| `ANTHROPIC_API_KEY not found` | API key not set | `export ANTHROPIC_API_KEY="sk-ant-..."` |
| `Invalid API key` | Key is incorrect or expired | Regenerate at [console.anthropic.com](https://console.anthropic.com/) |
| Claude cannot post review | gh auth lacks write access | Ensure token has `repo` scope (full control) |

---

## Environment Summary

After setup, your environment should have:

```bash
# Verify all prerequisites
echo "GH_HOST: $GH_HOST"
echo "ANTHROPIC_API_KEY: $(echo $ANTHROPIC_API_KEY | head -c 15)..."
claude --version
GH_HOST={GITHUB_HOST} gh auth status
```

Expected output:
```
GH_HOST: {GITHUB_HOST}
ANTHROPIC_API_KEY: sk-ant-api03-...
{AI_TOOL_NAME} Code 2.x.x
 Logged in to {GITHUB_HOST} as <username>
```

---

## Related Documents

| Document | Purpose |
|:---------|:--------|
| [README.md](./README.md) | Automated CI review overview |
| [AI_AGENT_REVIEW_WORKFLOW.md](./AI_AGENT_REVIEW_WORKFLOW.md) | On-demand agent review with fix-and-verify loop |
| [MANUAL_REVIEW_GUIDE.md](./MANUAL_REVIEW_GUIDE.md) | Human-facing guide for manual AI review |
| [ONBOARDING.md](./ONBOARDING.md) | Add AI review to a new component repo |
| [GCP_SETUP.md](./GCP_SETUP.md) | Deprecated — GCP Vertex AI setup (no longer required) |
| [GITHUB_TOOLS_SETUP.md](../github/GITHUB_TOOLS_SETUP.md) | gh CLI and MCP server configuration |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.0 | {DATE} | Initial creation — local developer setup for {AI_TOOL_NAME} Code CLI AI review |
