# AI PR Review

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Status**: Active
**ADR**: [009-ai-pr-review-custom-workflow.md](../../docs/adr/009-ai-pr-review-custom-workflow.md)

---

## Overview

Automated AI code review runs on every pull request across all project repositories. A custom GitHub Actions workflow invokes {AI_TOOL_NAME} Code CLI in non-interactive mode on the self-hosted runner. Claude analyzes the PR diff and source files, then posts inline line-level comments in the "Files changed" tab — the same UX as human reviewers.

AI review is **advisory**. It supplements but does not replace human review. At least one human reviewer is required per PR (enforced by branch protection).

---

## Architecture

```
Home repo: PR opened / synchronize / ready_for_review
  
  
ai-review.yml (triggers directly)
  
   Verify {AI_TOOL_NAME} Code CLI on runner
   Checkout PR branch (inline git clone, no marketplace actions)
   Fetch PR diff + metadata via gh API
   Run {AI_TOOL_NAME} Code (-p mode, non-interactive)
       Read diff and source files for context
       Analyze for bugs, security, performance, error handling
       Build review payload (inline comments + summary)
       POST formal GitHub review via gh API
       POST conclusion comment with JSON metadata
       Apply PR label (ai:review-passed or ai:review-failed)
   Cleanup temp files

Component repos: PR opened / synchronize / ready_for_review
  
  
Caller workflow (~10 lines)
  
   uses: {REPO_NAME}/.github/workflows/ai-review.yml@main
           secrets: inherit
```

### Key Properties

| Property | Value |
|:---------|:------|
| **Model** | Claude Sonnet (default), configurable per-repo (haiku, opus) |
| **Auth** | `ANTHROPIC_API_KEY` secret (per-repo or org-level) |
| **Runner** | `self-hosted` ({AI_TOOL_NAME} Code CLI pre-installed) |
| **Output** | Inline line-level comments + summary |
| **Events** | `APPROVE`, `COMMENT`, or `REQUEST_CHANGES` (integrates with branch protection) |
| **Context** | Reads source files beyond the diff for deeper understanding |
| **Fallback** | If inline comments fail (422), Claude retries with summary-only review |
| **Skip mechanism** | Add label `skip-ai-review` to bypass on a specific PR |
| **PR Labels** | `ai:review-passed` (no critical/medium findings) or `ai:review-failed` (REQUEST_CHANGES) |
| **Concurrency** | One review per PR number; new pushes cancel in-progress reviews |
| **Cost cap** | `--max-budget-usd 1.00` per review (configurable) |
| **Marketplace actions** | None required (GHES-compatible) |

---

## Review Policy

1. AI review triggers on `pull_request` events: `opened`, `synchronize`, `ready_for_review`
2. Skipped automatically for: draft PRs, `dependabot[bot]`, PRs labeled `skip-ai-review`
3. AI reviews focus on: bugs, security, performance, error handling, type safety
4. AI reviews exclude: style/formatting (ruff handles this), docstrings, import ordering
5. Maximum 15 inline comments per review
6. `APPROVE` event posted only when no bugs or security issues found AND no inline comments
7. Reviews appear as `github-actions` bot (not a named reviewer)
8. AI review cannot satisfy "required reviewer" branch protection rules
9. On-demand AI reviews **must** verify PR against linked issue acceptance criteria ([GOVERNANCE_RULES.md §3](../GOVERNANCE_RULES.md#linked-issue-verification-in-pr-review-mandatory))
10. AI review applies `ai:review-passed` or `ai:review-failed` label and posts conclusion comment after each review

---

## File Inventory

### Home Repo (single source of truth)

| File | Purpose | Lines |
|:-----|:--------|------:|
| [`.github/workflows/ai-review.yml`](../../.github/workflows/ai-review.yml) | Unified workflow — {AI_TOOL_NAME} Code CLI (triggers locally + callable by component repos) | ~230 |
| [`governance/AI_PR_Review/REVIEW_INSTRUCTIONS.md`](./REVIEW_INSTRUCTIONS.md) | 5-phase analysis methodology for AI code review | ~180 |
| [`governance/AI_PR_Review/FIX_INSTRUCTIONS.md`](./FIX_INSTRUCTIONS.md) | Auto-fix instructions for AI-suggested fixes | ~45 |
| [`governance/scripts/project_setup/cloud/gcp/setup-ai-review-gcp.sh`](../scripts/project_setup/cloud/gcp/setup-ai-review-gcp.sh) | GCP prerequisite automation (WIF setup) | ~479 |

### Component Repos (per-repo)

| File | Purpose |
|:-----|:--------|
| `.github/workflows/ai-review.yml` | Caller workflow (~10 lines, references home repo's `ai-review.yml`) |
| `skip-ai-review` label | Created per-repo for opt-out |
| `ai:review-passed` label | AI review passed (green) |
| `ai:review-failed` label | AI review failed (red) |

### Secrets (per-repo)

| Secret | Source |
|:-------|:-------|
| `ANTHROPIC_API_KEY` | Anthropic API key (or org-level secret on GHES) |

GCP secrets (`WIF_PROVIDER`, `WIF_SA_EMAIL`, `GCP_PROJECT_ID`) are no longer required for AI review. They remain in use by deploy and terraform workflows.

---

## Review Behavior

### Scope

Claude skips non-code files and focuses only on substantive code changes:

**Skipped**: `*.md`, `*.txt`, `*.json`, `*.toml`, `*.yaml`, `*.yml`, `*.lock`, images, `docs/`, `.github/`, `governance/`

**Reviewed**: Python, TypeScript, Terraform, shell scripts, and other code files in the diff.

### How Claude Reviews

1. Reads the PR diff at `/tmp/pr-diff.txt`
2. Reads PR metadata (title, body, changed file count)
3. Optionally reads source files in the repo for additional context
4. Builds a JSON review payload with inline comments and summary
5. Posts the review via `gh api` (GHES REST API)

### 5-Phase Analysis Methodology

Claude follows a mandatory 5-phase analysis (see [REVIEW_INSTRUCTIONS.md](./REVIEW_INSTRUCTIONS.md)):

| Phase | Description |
|:------|:------------|
| **1. Full-File Context** | Read complete source files, not just diffs |
| **2. Systematic Path Tracing** | Trace happy/error/retry/concurrent paths |
| **3. Symmetry Check** | Verify patterns applied consistently across analogous cases |
| **4. Chain Analysis** | Follow caller/callee chains to identify missing handling |
| **5. Design Tradeoff Recognition** | Don't flag documented limitations as bugs |

This methodology prevents common false positives and ensures thorough review coverage.

### Review Events

| Event | Condition | Branch Protection | Label Applied |
|:------|:----------|:-----------------|:--------------|
| `APPROVE` | No Critical or Medium findings | Counts toward approvals | `ai:review-passed` |
| `COMMENT` | Low-severity findings only | No merge impact | `ai:review-passed` |
| `REQUEST_CHANGES` | Critical or Medium findings | Blocks merge | `ai:review-failed` |

### Error Handling

| Scenario | Behavior |
|:---------|:---------|
| Empty or trivial diff (<10 bytes) | Skip review, exit 0 |
| {AI_TOOL_NAME} Code CLI not found on runner | Exit 1 with install instructions |
| `ANTHROPIC_API_KEY` missing | Claude exits with auth error |
| Inline comments get 422 (stale line mapping) | Claude retries with summary-only review |
| Review exceeds budget cap | Claude stops, partial review may be posted |
| Review exceeds 5-minute timeout | Step fails, visible in Actions |

### Limits

| Limit | Value |
|:------|:------|
| Max inline comments per review | 15 |
| Default cost cap per review | $1.00 USD |
| Review timeout | 5 minutes |
| Concurrency | 1 review per PR (latest push wins) |

---

## Cost

| Model | Monthly (25 PRs) | Annual | Notes |
|:------|:----------------:|:------:|:------|
| Claude Haiku 4.5 | ~$0.50-1.50 | ~$6-18 | Fastest, lowest cost |
| Claude Sonnet 4.5 (default) | ~$2-5 | ~$24-60 | Best quality/cost balance |
| Claude Opus 4.6 | ~$10-25 | ~$120-300 | Security-critical PRs only |

Cost per review is capped by `--max-budget-usd` (default: $1.00). Actual cost depends on diff size, number of source files read, and model used.

---

## Related Documents

| Document | Purpose |
|:---------|:--------|
| [REVIEW_INSTRUCTIONS.md](./REVIEW_INSTRUCTIONS.md) | 5-phase analysis methodology with self-check requirements |
| [FIX_INSTRUCTIONS.md](./FIX_INSTRUCTIONS.md) | Auto-fix capability instructions and scope constraints |
| [ADR-009](../../docs/adr/009-ai-pr-review-custom-workflow.md) | Decision rationale (Custom Workflow vs PR-Agent vs Bot vs Claude Action) |
| [LOCAL_SETUP.md](./LOCAL_SETUP.md) | Local developer setup ({AI_TOOL_NAME} Code CLI, gh auth, API key) |
| [ONBOARDING.md](./ONBOARDING.md) | Add AI review to a new component repo |
| [Implementation Plans](../plans/) | Implementation plans |
| [GOVERNANCE_RULES.md](../GOVERNANCE_RULES.md) | AI PR Review policy (section 3) |
| [AI_AGENT_REVIEW_WORKFLOW.md](./AI_AGENT_REVIEW_WORKFLOW.md) | On-demand AI agent review with fix-and-verify loop |
| [MANUAL_REVIEW_GUIDE.md](./MANUAL_REVIEW_GUIDE.md) | Human-facing guide for manual AI review using local assistants ({AI_TOOL_NAME} Code, Gemini CLI, Copilot) |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 2.2 | {DATE} | Updated for consolidated workflow — single ai-review.yml replaces separate caller + reusable; added conclusion + label steps to architecture |
| 2.1 | {DATE} | Added PR labels (`ai:review-passed`/`ai:review-failed`) to Key Properties, Review Policy rule 10, Review Events table |
| 2.0 | {DATE} | Replaced Gemini 2.5 Flash + Python script with {AI_TOOL_NAME} Code CLI on self-hosted runner (ADR-009 v1.1) |
| 1.3 | {DATE} | Added linked issue verification to Review Policy (rule 9) |
| 1.2 | {DATE} | Added MANUAL_REVIEW_GUIDE.md to Related Documents |
| 1.1 | {DATE} | Added AI_AGENT_REVIEW_WORKFLOW.md to Related Documents |
| 1.0 | {DATE} | Initial creation — restructured as operational guidance |
