# AI PR Review — Onboarding New Repos

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Prerequisite**: {AI_TOOL_NAME} Code CLI installed on the selected runner (GitHub-hosted or approved self-hosted)

---

## Overview

The AI PR review system uses a **reusable workflow** pattern. All review logic lives in the home repo (`{REPO_NAME}`). Component repos need only a ~10-line caller workflow and one GitHub secret (`ANTHROPIC_API_KEY`).

The workflow runs {AI_TOOL_NAME} Code CLI on the selected runner — no Python dependencies or GCP auth required for AI review.

---

## Steps to Onboard a New Repo

### 1. Add `ANTHROPIC_API_KEY` Secret

Set the Anthropic API key on the new repo (or use an org-level secret):

```bash
export GH_HOST={GITHUB_HOST}
export REPO="{GITHUB_ORG}/{PROJECT_PREFIX}-new-component"

gh secret set ANTHROPIC_API_KEY --repo $REPO --body "<your-anthropic-api-key>"
```

If the org has an org-level `ANTHROPIC_API_KEY` secret, this step is not needed per-repo.

### 2. Add Caller Workflow

Create `.github/workflows/ai-review.yml` in the component repo:

```yaml
name: AI PR Review

on:
  pull_request:
    types: [opened, synchronize, ready_for_review]

jobs:
  ai-review:
    uses: {GITHUB_ORG}/{REPO_NAME}/.github/workflows/ai-review.yml@main
    secrets: inherit
```

This is the only file needed. The home repo workflow handles:
- Verifying {AI_TOOL_NAME} Code CLI on the runner
- Checking out the PR branch
- Fetching the PR diff and metadata
- Running {AI_TOOL_NAME} Code in non-interactive mode
- Posting the formal GitHub review
- Posting conclusion comment with JSON metadata
- Applying `ai:review-passed` or `ai:review-failed` label

### 3. Create Required Labels

Create the following labels on the new repo:

```bash
export GH_HOST={GITHUB_HOST}
export REPO="{GITHUB_ORG}/{PROJECT_PREFIX}-new-component"

# Skip label (opt-out mechanism)
gh label create "skip-ai-review" --repo $REPO \
  --color "CCCCCC" \
  --description "Skip AI code review on this PR"

# Review outcome labels (applied by AI review workflow)
gh label create "ai:review-passed" --repo $REPO \
  --color "0e8a16" \
  --description "AI review passed — no critical or medium findings"

gh label create "ai:review-failed" --repo $REPO \
  --color "b60205" \
  --description "AI review found critical or medium issues"
```

| Label | Color | Purpose |
|:------|:------|:--------|
| `skip-ai-review` | Gray | Opt-out: skip AI review on specific PRs |
| `ai:review-passed` | Green | AI review passed (APPROVE or COMMENT with low-only findings) |
| `ai:review-failed` | Red | AI review failed (REQUEST_CHANGES) |

### 4. Verify

1. Create a feature branch with a test change
2. Open a PR
3. Check the Actions tab — `AI Review` workflow should trigger
4. Verify inline comments appear in the "Files changed" tab
5. Test the skip label by adding `skip-ai-review` to a PR

---

## What Component Repos Do NOT Need

- No copy of `ai-review-reusable.yml` — called via `uses:` reference
- No Python scripts or dependencies
- No GCP auth setup (WIF, service accounts) for AI review
- No {AI_TOOL_NAME} Code installation — pre-installed on the self-hosted runner

---

## Workflow Inputs (Optional)

The caller workflow can override defaults by passing inputs:

```yaml
jobs:
  ai-review:
    uses: {GITHUB_ORG}/{REPO_NAME}/.github/workflows/ai-review-reusable.yml@main
    secrets: inherit
    with:
      model: "haiku"          # default: "sonnet" (options: haiku, sonnet, opus)
      max-budget-usd: "0.25"  # default: "1.00" (USD per review)
```

---

## Runner Requirement

The self-hosted runner must have {AI_TOOL_NAME} Code CLI installed and in PATH. The workflow verifies this in the first step and fails with install instructions if missing.

```bash
# Verify on the runner
claude --version
# Expected: 2.x.x ({AI_TOOL_NAME} Code)
```

Install if needed:
```bash
npm install -g @anthropic-ai/claude-code
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|:--------|:-------------|:----|
| Workflow does not trigger | Missing caller `ai-review.yml` in component repo | Add file per Step 2 |
| `{AI_TOOL_NAME} Code CLI not found` error | CLI not installed on runner | Install: `npm install -g @anthropic-ai/claude-code` |
| Auth failure from Claude | `ANTHROPIC_API_KEY` secret not set | Set per-repo or org-level secret per Step 1 |
| Inline comments 422 | Line mapping mismatch (force-push between events) | Automatic fallback to summary-only review |
| Review not posted | `GITHUB_TOKEN` permissions insufficient | Ensure caller repo allows `pull-requests: write` |
| Review timeout (5 min) | Large diff or complex codebase | Increase `max-budget-usd` or switch to `haiku` model |
| No review on draft PR | Expected behavior | AI review skips draft PRs |
| No review on dependabot PR | Expected behavior | AI review skips `dependabot[bot]` |
| Job queued indefinitely | No self-hosted runner for component repo | Register runner for the component repo or use org-level runner |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 2.2 | {DATE} | Updated workflow reference: ai-review-reusable.yml → ai-review.yml (consolidated workflow) |
| 2.1 | {DATE} | Added `ai:review-passed` and `ai:review-failed` labels to Step 3 |
| 2.0 | {DATE} | Rewritten for {AI_TOOL_NAME} Code CLI — simplified onboarding (1 secret, no GCP setup) |
| 1.0 | {DATE} | Initial creation — deployment/onboarding documentation |
