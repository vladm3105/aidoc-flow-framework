# Manual AI PR Review Guide

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Audience**: Developers using locally installed AI assistants to review PRs
**Related**: [README.md](./README.md) (automated review) | [AI_AGENT_REVIEW_WORKFLOW.md](./AI_AGENT_REVIEW_WORKFLOW.md) (agent protocol)

---

## 1. When to Use Manual AI Review

The project has two AI review modes. Use the right one:

| Criteria | Automated ({AI_TOOL_NAME} Code CLI) | Manual (Local AI Assistant) |
|:---------|:---------------------------|:----------------------------|
| **Trigger** | Fires on every PR automatically | Developer invokes from CLI |
| **Model** | Claude Sonnet (default) | Claude Opus/Sonnet, Gemini Pro, Copilot (deeper) |
| **Depth** | Diff-only, 15-comment cap | Full file reads, fix-and-verify loop, architecture review |
| **Cost** | ~$2-5/month (Anthropic API) | Variable (uses local API quota) |
| **Fix loop** | None | Up to 3 iterations |
| **Setup** | Zero (runs in CI) | Requires local CLI + `gh` auth |

**Use manual review when**:
- PR touches security-sensitive code (auth, secrets, IAM)
- Multi-file architectural changes spanning 3+ components
- Fix-and-verify loop needed (agent reviews, fixes, pushes, re-reviews)
- Human reviewer is unavailable and pre-merge validation is needed
- Automated review flagged issues that need deeper investigation

**Automated review is sufficient when**:
- Standard feature PR with passing CI
- Documentation-only or config-only changes
- Human reviewer is immediately available

---

## 2. Prerequisites

| Requirement | Verification |
|:------------|:-------------|
| `gh` CLI authenticated | `GH_HOST={GITHUB_HOST} gh auth status` shows "Logged in" |
| `GH_HOST` env var | `export GH_HOST={GITHUB_HOST}` in your shell profile |
| AI assistant installed | `claude --version` or `gemini --version` or `gh copilot --version` |
| Repo cloned locally | `cd {LOCAL_PROJECT_PATH}/{REPO_NAME}` (or your local path) |
| Write access (for fix loop) | Repo collaborator with push permission to PR branches |

For detailed `gh` and MCP setup, see [GITHUB_TOOLS_SETUP.md](../GITHUB_TOOLS_SETUP.md).

---

## 3. Quick Start

### 3a. {AI_TOOL_NAME} Code CLI

```bash
export GH_HOST={GITHUB_HOST}
cd /path/to/{REPO_NAME}

# Start {AI_TOOL_NAME} Code and request a review
claude
```

Then in the {AI_TOOL_NAME} Code session:

```
use governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md and review
https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}/pull/<NUMBER>
```

Or for a component repo:

```
review PR #<NUMBER> on {GITHUB_ORG}/{PROJECT_PREFIX}-{SERVICE_NAME}
following governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md
```

{AI_TOOL_NAME} Code uses the `gh` CLI (with `GH_HOST` prefix) to fetch the PR diff, analyze it, and post a formal GitHub review with inline comments.

### 3b. Gemini CLI

```bash
export GH_HOST={GITHUB_HOST}
cd /path/to/{REPO_NAME}

gemini
```

Then in the Gemini session, provide the same review instruction referencing the workflow document.

### 3c. GitHub Copilot (VS Code)

In VS Code with the repo open, use Copilot Chat:

```
@workspace Review PR #<NUMBER> on {GITHUB_ORG}/{REPO_NAME}.
Follow the review workflow in governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md.
Post a formal GitHub review with inline comments.
```

Copilot CLI alternative:

```bash
GH_HOST={GITHUB_HOST} gh copilot suggest "Review PR #42 and post findings"
```

---

## 4. What the Agent Does

When you invoke a review, the agent follows the [AI_AGENT_REVIEW_WORKFLOW.md](./AI_AGENT_REVIEW_WORKFLOW.md) state machine:

1. **READ** — Fetches PR metadata, diff, and CI status via `gh` CLI
2. **VERIFY LINKED ISSUE** — Parses PR body for `Closes #N` / `Fixes #N`, fetches the linked issue's acceptance criteria, and verifies each criterion against the PR changes
3. **ANALYZE** — Categorizes findings by severity (Critical / Medium / Low)
4. **POST REVIEW** — Submits a formal GitHub Review with inline comments + summary comment (includes linked issue verification table) + **cross-posts review summary to the linked issue** for audit trail
5. **FIX** _(if REQUEST_CHANGES and authorized)_ — Edits files, commits with co-author, pushes to PR branch
6. **RE-REVIEW** _(max 3 iterations)_ — Verifies fixes, checks CI, posts APPROVE or repeats; cross-posts re-review result to linked issue
7. **CONCLUSION** — Posts a separate conclusion comment with decision: **"Approved to merge"** or **"Work needed"**, including findings summary and acceptance criteria status
8. **LABEL** — Applies `ai:review-passed` or `ai:review-failed` PR label based on review outcome

The agent filters out non-code files (`*.md`, `*.yaml`, `docs/*`, `governance/*`) and focuses on bugs, security, performance, error handling, and type safety. Style and formatting are excluded (ruff handles those).

For the full state machine, API payloads, severity definitions, and edge cases, see [AI_AGENT_REVIEW_WORKFLOW.md](./AI_AGENT_REVIEW_WORKFLOW.md).

---

## 5. Controlling the Review

### Review-Only (No Fix Loop)

```
Review PR #42 but do NOT fix any issues. Post all findings as COMMENT only.
```

### Security-Focused Review

```
Review only security aspects of PR #42 — focus on injection, credential leaks, auth bypass, OWASP Top 10.
```

### Re-Review After Fixes

```
Re-review PR #42. Verify that all findings from the previous review are resolved.
Check the latest commit diff and CI status.
```

### Scope-Limited Review

```
Review only the Python files in PR #42. Skip Terraform, YAML, and documentation changes.
```

### Skip AI Review on a PR

```bash
GH_HOST={GITHUB_HOST} gh pr edit <NUMBER> \
  --repo {GITHUB_ORG}/{REPO_NAME} \
  --add-label skip-ai-review
```

---

## 6. Reading the Output

### Where to Find Results

| Output | Location |
|:-------|:---------|
| Inline comments (with `[Critical]`/`[Medium]`/`[Low]` tags) | PR → "Files changed" tab |
| Summary comment (findings table + verdict) | PR → Conversation tab |
| Review event (APPROVE/COMMENT/REQUEST_CHANGES) | PR → Reviews sidebar |
| **Conclusion comment** ("Approved to merge" / "Work needed") | PR → Conversation tab (final comment) |
| **PR label** (`ai:review-passed` / `ai:review-failed`) | PR → Labels sidebar |

### Interpreting the Verdict

| Review Event | Meaning | Your Action |
|:-------------|:--------|:------------|
| `APPROVE` | No bugs or security issues found | Proceed to human review and merge |
| `COMMENT` | Low-severity findings only | Address at discretion; not blocking |
| `REQUEST_CHANGES` | Critical or Medium findings affecting correctness/security | Fix findings before merge (agent may enter fix loop) |

AI reviews are **advisory**. Human review is still required per branch protection rules.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|:--------|:------|:----|
| Agent cannot fetch PR diff | `GH_HOST` not set | `export GH_HOST={GITHUB_HOST}` |
| `gh` returns 401 Unauthorized | Token expired or missing scopes | `GH_HOST={GITHUB_HOST} gh auth refresh` |
| `github-{PROJECT_PREFIX}-{PROJECT_PREFIX}` MCP returns 401 | Known MCP token issue | Agent automatically falls back to `gh` CLI |
| No review posted (doc-only PR) | Diff filtering excluded all files | Expected — non-code files are filtered out |
| Agent cannot push to PR branch | No write access | Grant collaborator access, or use review-only mode |
| Review comments on wrong lines (422) | Force-push between review and fix | Agent retries with summary-only review automatically |
| Agent does not follow the workflow | Workflow doc not referenced in prompt | Include the path to `AI_AGENT_REVIEW_WORKFLOW.md` in your prompt |
| Fix loop exceeds 3 iterations | Complex issues beyond agent capability | Agent escalates to human reviewer with unresolved findings |

---

## 8. Related Documents

| Document | Purpose |
|:---------|:--------|
| [README.md](./README.md) | Automated review overview ({AI_TOOL_NAME} Code CLI via Actions) |
| [AI_AGENT_REVIEW_WORKFLOW.md](./AI_AGENT_REVIEW_WORKFLOW.md) | Full agent protocol: state machine, API calls, severity levels, fix loop, edge cases |
| [LOCAL_SETUP.md](./LOCAL_SETUP.md) | Local developer setup ({AI_TOOL_NAME} Code CLI, gh auth, API key) |
| [GCP_SETUP.md](./GCP_SETUP.md) | Deprecated — GCP prerequisites (no longer required) |
| [ONBOARDING.md](./ONBOARDING.md) | Add AI review to a new component repo |
| [ADR-009](../../docs/adr/009-ai-pr-review-custom-workflow.md) | Decision rationale for AI PR review approach |
| [GOVERNANCE_RULES.md](../GOVERNANCE_RULES.md) | AI PR review policy (§3), board sync rules |
| [GITHUB_TOOLS_SETUP.md](../GITHUB_TOOLS_SETUP.md) | `gh` CLI and MCP server configuration |
| [CONTRIBUTING.md](../../CONTRIBUTING.md#reviewer-roster) | Reviewer roster for PR assignment |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.5 | {DATE} | Replaced Gemini references with {AI_TOOL_NAME} Code CLI; added PR label step and output row |
| 1.4 | {DATE} | Added conclusion step to agent workflow summary and output table — mandatory "Approved to merge" or "Work needed" comment |
| 1.3 | {DATE} | Updated agent workflow summary — review cross-posts summary to linked issue for audit trail |
| 1.2 | {DATE} | Added ADR-009 and GOVERNANCE_RULES.md to Related Documents |
| 1.1 | {DATE} | Added linked issue verification step (Step 2) to agent workflow summary |
| 1.0 | {DATE} | Initial creation -- human-facing guide for manual AI PR review using local assistants |
