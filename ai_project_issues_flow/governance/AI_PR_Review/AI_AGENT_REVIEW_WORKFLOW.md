# AI Agent PR Review Workflow

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**Scope**: On-demand, interactive AI agent PR review with fix-and-verify loop
**Related**: [README.md](./README.md) (automated review) | [GOVERNANCE_RULES.md](../GOVERNANCE_RULES.md) §3 (AI workflow)

---

## 1. Overview

This document defines the workflow for **on-demand AI agent PR reviews** — distinct from the automated {AI_TOOL_NAME} Code CLI review that fires on every PR via GitHub Actions.

| Mode | Trigger | Agent | Review Type | Fix Loop | Merge Impact |
|:-----|:--------|:------|:------------|:---------|:-------------|
| Automated | `pull_request` event | {AI_TOOL_NAME} Code CLI (GH Actions) | `APPROVE` or `COMMENT` | None | Advisory only |
| On-demand agent | Human command or `ai:ready` label | Claude / Gemini CLI / Copilot | `REQUEST_CHANGES` / `APPROVE` / `COMMENT` | Yes (up to 3 iterations) | Advisory (human review still required) |

**When to use on-demand agent review**:
- Deep review of complex PRs (architecture, security, multi-file changes)
- PRs requiring fix-and-verify loop (agent reviews, fixes, re-reviews)
- Supplementing automated review with domain-specific analysis
- Pre-merge validation when human reviewer is unavailable

**When automated review is sufficient**:
- Standard feature PRs with passing CI
- Documentation-only PRs
- PRs where human reviewer is immediately available

---

## 2. Prerequisites

| Requirement | Detail |
|:------------|:-------|
| `gh` CLI authenticated | `GH_HOST={GITHUB_HOST} gh auth status` must show "Logged in" |
| Environment variable | `export GH_HOST={GITHUB_HOST}` (all `gh` commands require this) |
| Repo access | Read access to repo, write access to PR reviews and branches |
| Session start protocol | Agent must have read: README_AIAGENT.md, GOVERNANCE_RULES.md, PROJECT_PLAN.md §2, plans/README.md |
| Reviewer roster | Agent must know the [CONTRIBUTING.md reviewer roster](../../CONTRIBUTING.md#reviewer-roster) for assignment |
| Self-review rule | PR author cannot self-review; agent must assign a **different** human reviewer |

---

## 3. Review Lifecycle State Machine

```
                  ┌────────────────────────────────────────────────────────────────────────┐
                  │                                                                        │
                  ▼                                                                        │
  [1. READ PR] ──→ [2. VERIFY LINKED ISSUE] ──→ [3. ANALYZE] ──→ [4. POST REVIEW]────────┤
                                                                       │                  │
                                                         ┌─────────────┼────────┐         │
                                                         ▼             ▼        ▼         │
                                                     APPROVE      COMMENT  REQ_CHG        │
                                                         │             │        │         │
                                                         ▼             ▼   [5. FIX]       │
                                                   [CONCLUSION]  [CONCLUSION]  │          │
                                                         │             │  [6. PUSH]       │
                                                      (done)        (done)     │          │
                                                                         [7. RE-REVIEW]───┘
                                                                               │
                                                                         [CONCLUSION]
                                                                               │
                                                                     (max 3 iterations,
                                                                      then escalate)
```

| State | Action | Output |
|:------|:-------|:-------|
| 1. READ PR | Fetch PR metadata, diff, CI status | Local understanding of all changes |
| 2. VERIFY LINKED ISSUE | Parse PR body for issue links, fetch acceptance criteria, verify each | Issue verification table (pass/fail per criterion) |
| 3. ANALYZE | Categorize findings by severity | Findings list (Critical / Medium / Low) |
| 4. POST FORMAL REVIEW | Submit GitHub Review with inline comments + summary comment (includes issue verification) + issue review history comment | Review event on PR; review record on linked issue |
| 5. FIX ISSUES | Edit files to resolve findings | Local file changes |
| 6. PUSH FIXES | Commit with co-author, push to PR branch | Updated PR, CI triggered |
| 7. RE-REVIEW | Read updated diff, verify each fix, check CI; post re-review result to linked issue | APPROVE or repeat from step 5 |
| CONCLUSION | Post separate conclusion comment on PR with merge decision | "Approved to merge" or "Work needed" comment on PR |

---

## 4. Step 1 — Read PR Diff and Metadata

### Fetch PR metadata

```bash
GH_HOST={GITHUB_HOST} gh pr view <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --json number,title,body,author,labels,reviewers,baseRefName,headRefName,additions,deletions,files,commits,state,mergeable
```

### Fetch PR diff

```bash
GH_HOST={GITHUB_HOST} gh pr diff <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO>
```

### Check CI status

```bash
GH_HOST={GITHUB_HOST} gh pr checks <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO>
```

### Fetch full file content (when diff is insufficient)

```bash
GH_HOST={GITHUB_HOST} gh api \
  /repos/{GITHUB_ORG}/<REPO>/contents/<FILE_PATH>?ref=<HEAD_BRANCH> \
  --jq '.content' | base64 -d
```

### Diff filtering

Apply the same skip patterns as the automated review (`scripts/ai_review.py`). Exclude from code analysis:
- `*.md`, `*.txt`, `*.json`, `*.toml`, `*.yaml`, `*.yml`, `*.lock`, `*.csv`
- `*.svg`, `*.png`, `*.jpg`, `*.jpeg`, `*.gif`, `*.ico`, `*.woff*`, `*.eot`, `*.ttf`
- `docs/*`, `.github/*`, `governance/*`, `LICENSE`, `.gitmodules`, `.gitignore`

Exception: include filtered files when performing a documentation-specific review.

---

## 5. Step 2 — Verify Linked Issue

Every PR review **must** verify the PR against its linked issue's acceptance criteria. Code quality review alone is insufficient.

### 5a. Parse Issue Links

Scan the PR body for issue references:
- `Closes #N`, `Fixes #N`, `Resolves #N` (auto-close keywords)
- `#N` references in the body text
- Parent epic references (`Parent Epic: #N`)

### 5b. Fetch Issue Acceptance Criteria

```bash
GH_HOST={GITHUB_HOST} gh issue view <ISSUE_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --json title,body,state,labels
```

Extract the `## Acceptance Criteria` section from the issue body. Each `- [ ]` or `- [x]` item is a criterion.

### 5c. Verify Each Criterion

| Criterion Type | Verification Method |
|:---------------|:-------------------|
| File/directory exists | `gh api /repos/.../contents/<path>?ref=<branch>` or Glob tool |
| Configuration has specific values | Fetch file content, confirm values |
| Feature is implemented | Read source code from PR branch, check function signatures and logic |
| Tests pass | Check CI status via `gh pr checks` |
| Protection rules applied | `gh api /repos/.../branches/main/protection` |
| Dependency structure | Check `pyproject.toml`, `package.json`, or equivalent |

### 5d. Include in Review Output

Add a **Linked Issue Verification** section to the review summary:

```
## Linked Issue Verification

**Issue**: #19 — [P1-1.0] Create {PROJECT_PREFIX}-{SERVICE_NAME} repository

| # | Criterion | Status | Evidence |
|:-:|:----------|:------:|:---------|
| 1 | Repo created in org | Pass | gh api confirms repo exists |
| 2 | Python project structure | Pass | File tree matches spec |
| 3 | Branch protection enabled | Pass | API confirms 1 reviewer, no force-push |
```

### 5e. No Linked Issue

If no issue is linked in the PR body:
- Note the absence in the review: _"No linked issue found. PR body does not contain Closes/Fixes/Resolves keywords."_
- Do not block the review for missing issue link, but flag it

---

## 6. Step 3 — Analyze and Categorize Findings

### Severity Levels

| Severity | Definition | Examples | Review Event |
|:---------|:-----------|:---------|:-------------|
| Critical | Security vulnerability, data loss, crash in production path | SQL injection, credential exposure, unhandled null in API response, authentication bypass | REQUEST_CHANGES |
| Medium | Bug with workaround, performance degradation, missing error handling in non-critical path | N+1 query, bare `except`, missing input validation on internal API, resource leak | REQUEST_CHANGES or COMMENT |
| Low | Code quality, naming, minor improvement opportunity | Unused import, suboptimal algorithm (correct but slow), missing type hint | COMMENT |

### Review Focus Areas

Same as automated review system prompt (`scripts/ai_review.py`):
1. Bugs, logic errors, off-by-one, null/None handling
2. Security issues (injection, credential leaks, OWASP Top 10)
3. Performance problems (N+1 queries, unbounded loops, memory leaks)
4. Error handling gaps (bare except, swallowed exceptions)
5. Type safety and API contract violations

**Exclude from review** (ruff/mypy handle these):
- Style or formatting
- Missing docstrings or comments
- Import ordering
- Line length

### Decision Tree — Review Event Selection

```
Has Critical findings?
├── YES → REQUEST_CHANGES
└── NO
    Has Medium findings?
    ├── YES
    │   Affects correctness or security?
    │   ├── YES → REQUEST_CHANGES
    │   └── NO (performance/style only) → COMMENT
    └── NO
        Has Low findings?
        ├── YES → COMMENT (with inline suggestions)
        └── NO → APPROVE
```

---

## 7. Step 4 — Post Formal Review

Two outputs are posted: a **formal GitHub Review** (appears in "Files changed" tab, integrates with branch protection) and a **summary comment** (appears in PR conversation, for visibility). The review **must** include the Linked Issue Verification table from Step 2.

### 7a. Formal Review via GitHub Reviews API

```bash
GH_HOST={GITHUB_HOST} gh api \
  --method POST \
  "/repos/{GITHUB_ORG}/<REPO>/pulls/<PR_NUMBER>/reviews" \
  --input <(cat <<'REVIEW_EOF'
{
  "commit_id": "<HEAD_SHA>",
  "event": "REQUEST_CHANGES",
  "body": "**AI Agent Review (Claude)**\n\n## Summary\n<1-3 sentence assessment>\n\n## Findings\n- **Critical**: <count> | **Medium**: <count> | **Low**: <count>\n\n## Verdict\nREQUEST_CHANGES — <reason>\n\n---\n_Review by AI agent. Human review still required per GOVERNANCE_RULES.md._",
  "comments": [
    {
      "path": "src/cost_guard/main.py",
      "line": 42,
      "body": "**[Critical]** Division by zero when `budget_amount` is 0.\n\nSuggested fix:\n```python\nif budget_amount == 0:\n    raise ValueError('budget_amount must be > 0')\n```"
    },
    {
      "path": "src/cost_guard/alerts.py",
      "line": 15,
      "body": "**[Medium]** Bare `except` swallows all exceptions including `KeyboardInterrupt`. Use `except Exception:` instead."
    }
  ]
}
REVIEW_EOF
)
```

### 7b. Summary Comment for Visibility

```bash
GH_HOST={GITHUB_HOST} gh pr comment <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --body "$(cat <<'COMMENT_EOF'
## AI Agent Review Summary

| Severity | Count | Files |
|:---------|:-----:|:------|
| Critical | 1 | src/cost_guard/main.py |
| Medium | 1 | src/cost_guard/alerts.py |
| Low | 0 | -- |

**Verdict**: REQUEST_CHANGES -- 1 critical finding must be resolved before merge.

_See formal review in the "Files changed" tab for inline comments._
COMMENT_EOF
)"
```

### 7c. Issue Review History Comment (Mandatory)

After posting the PR review, the agent **must** also post a summary comment on the **linked issue** (`Closes #N`). This creates a review audit trail directly on the issue, so stakeholders tracking the issue can see review progress without navigating to the PR.

```bash
GH_HOST={GITHUB_HOST} gh issue comment <ISSUE_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --body "$(cat <<'COMMENT_EOF'
## PR Review Record — PR #<PR_NUMBER>

**Reviewer**: AI Agent (Claude Opus 4.6)
**Date**: <YYYY-MM-DD HH:MM EST>
**Commit**: `<SHORT_SHA>`
**Verdict**: <APPROVE | COMMENT | REQUEST_CHANGES>

### Findings
- **Critical**: <count> | **Medium**: <count> | **Low**: <count>

### Acceptance Criteria Verification
| # | Criterion | Status |
|:-:|:----------|:------:|
| 1 | <criterion text> | Pass/Fail |

### Notes
<1-2 sentence summary of review outcome and any follow-up items>

---
_Auto-posted by AI agent review workflow. See [PR #<PR_NUMBER>](<PR_URL>) for full review._
COMMENT_EOF
)"
```

**Rules**:
- Post on **every** review event (APPROVE, COMMENT, REQUEST_CHANGES)
- Post on **every** re-review iteration (prefix with "Re-Review #N")
- If no linked issue exists, skip this step (already flagged in the PR review)
- Keep the comment concise — link to the PR for full inline comments

### 7d. Review Conclusion Comment (Mandatory)

After completing the full review cycle (initial review, and fix-and-verify loop if applicable), the agent **must** post a **separate conclusion comment** on the PR. This is the final output of the review — a clear, standalone merge decision that human reviewers and stakeholders can reference.

**When to post**: After every terminal state — APPROVE, COMMENT (no fix loop), or final RE-REVIEW iteration.

**Decision values**: Exactly one of:
- **"Approved to merge"** — All findings resolved (or none found), acceptance criteria passing
- **"Work needed"** — Unresolved findings remain, or acceptance criteria are failing

```bash
GH_HOST={GITHUB_HOST} gh pr comment <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --body "$(cat <<'COMMENT_EOF'
## Review Conclusion

**Decision**: <Approved to merge | Work needed>

### Review Summary

| Phase | Findings | Resolved |
|:------|:--------:|:--------:|
| Initial review | <N> Critical, <N> Medium, <N> Low | -- |
| Re-review #<N> | <N> remaining | <N>/<N> |

### Acceptance Criteria
<N>/<N> criteria for issue #<ISSUE_NUMBER> verified and passing.

### Checklist
- [ ] No critical or medium findings remain
- [ ] All fix commits scoped to identified findings only
- [ ] No regressions introduced
- [ ] Acceptance criteria verified

### Recommendation
<1-2 sentence recommendation for human reviewer>

---
_AI Agent Review Conclusion (<Agent Name>) | <YYYY-MM-DD>_
COMMENT_EOF
)"
```

**Rules**:
- The conclusion is **separate** from the formal review event and issue cross-post — it is an additional comment
- Post exactly **one** conclusion per review cycle (not per iteration)
- If the fix loop ran multiple iterations, the conclusion summarizes the full cycle
- The conclusion replaces any earlier "summary comment" (§7b) as the authoritative merge decision — §7b remains for mid-review visibility but the conclusion is the final word

### Machine-Readable JSON Metadata

Include a hidden JSON block in the conclusion comment for downstream automation (dashboards, audit reports, compliance checks):

```html
<!-- AI_REVIEW_METADATA {"decision":"approved","model":"claude-sonnet-4-5-20250929","pr":42,"repo":"{GITHUB_ORG}/{PROJECT_PREFIX}-{SERVICE_NAME}","findings":{"critical":0,"medium":0,"low":1},"review_event":"APPROVE","timestamp":"{DATE}T15:30:00-05:00"} AI_REVIEW_METADATA -->
```

| Field | Values | Notes |
|:------|:-------|:------|
| `decision` | `"approved"` or `"rejected"` | No other values |
| `findings` | Integer counts only | No finding text (avoids JSON escaping issues) |
| `timestamp` | ISO 8601 with EST offset | `-05:00` (EST) or `-04:00` (EDT) |

Generate JSON with `jq -c` or equivalent to ensure proper escaping.

### Review Event Reference

| Event | When to Use | Branch Protection Effect |
|:------|:------------|:------------------------|
| `APPROVE` | Zero Critical/Medium findings, all checks passing | Counts toward required approvals |
| `REQUEST_CHANGES` | Any Critical finding, or Medium findings affecting correctness/security | Blocks merge until resolved or dismissed |
| `COMMENT` | Low findings only, or informational feedback | No merge impact |

### Inline Comment Format

Each inline comment must include:
- **Severity tag**: `[Critical]`, `[Medium]`, or `[Low]`
- **Description**: Concise explanation of the issue
- **Suggested fix**: Code block with the recommended change (when applicable)
- **Line reference**: Must reference a line from the NEW side of the diff (lines with `+`)

Maximum 15 inline comments per review (same limit as automated system).

---

## 8. Step 5 — Label and Assign

### Assign reviewer (if not already assigned)

```bash
GH_HOST={GITHUB_HOST} gh pr edit <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --add-reviewer <username>
```

Select reviewer from [CONTRIBUTING.md roster](../../CONTRIBUTING.md#reviewer-roster) based on component scope:

| Component | Reviewer |
|:----------|:---------|
| All / governance | `{CODEOWNER_1}` or `{CODEOWNER_2}` |
| Terraform, CI/CD, Cloud Run | `{CODEOWNER_1}` |
| Workflows, auth, secrets | `{CODEOWNER_1}` |
| ADRs, specs, design | `{CODEOWNER_1}` |

### Verify Issue PR Link

If the linked issue does not already have a "PR Created" comment (check issue comments), post one now per [GOVERNANCE_RULES.md §3](../GOVERNANCE_RULES.md#issue-pr-link-mandatory). This ensures the issue always has a direct link to the PR, so stakeholders viewing the project board can navigate from issue to PR without searching.

```bash
GH_HOST={GITHUB_HOST} gh issue comment <ISSUE_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --body "$(cat <<'COMMENT_EOF'
## PR Created — #<PR_NUMBER>

| Field | Value |
|:------|:------|
| **PR** | [#<PR_NUMBER>: <PR_TITLE>](<PR_URL>) |
| **Branch** | `<HEAD_BRANCH>` → `<BASE_BRANCH>` |
| **Created** | <YYYY-MM-DD HH:MM EST> |

---
_Auto-posted on PR creation._
COMMENT_EOF
)"
```

### Add labels (if applicable)

```bash
GH_HOST={GITHUB_HOST} gh pr edit <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --add-label "<label>"
```

### Apply PR Review Label (Mandatory)

After posting the conclusion comment, apply the appropriate PR label. This enables machine-queryable filtering of reviewed PRs.

**Labels**:
| Label | When to Apply |
|:------|:--------------|
| `ai:review-passed` | APPROVE or COMMENT event with zero critical/medium findings |
| `ai:review-failed` | REQUEST_CHANGES event |

**Apply label** (idempotent — remove existing first):

```bash
# Remove any existing AI review labels
GH_HOST={GITHUB_HOST} gh api -X DELETE \
  "/repos/{GITHUB_ORG}/<REPO>/issues/<PR_NUMBER>/labels/ai%3Areview-passed" 2>/dev/null || true
GH_HOST={GITHUB_HOST} gh api -X DELETE \
  "/repos/{GITHUB_ORG}/<REPO>/issues/<PR_NUMBER>/labels/ai%3Areview-failed" 2>/dev/null || true

# Apply new label
echo '{"labels":["ai:review-passed"]}' > /tmp/label-payload.json
GH_HOST={GITHUB_HOST} gh api -X POST \
  "/repos/{GITHUB_ORG}/<REPO>/issues/<PR_NUMBER>/labels" \
  --input /tmp/label-payload.json
```

**Scope distinction**:
- **Issue labels** (`ai:ready`, `ai:in-progress`, `ai:review-requested`): Track work lifecycle on issues in the home repo
- **PR labels** (`ai:review-passed`, `ai:review-failed`): Track AI review outcome on PRs in home and component repos

---

## 9. Step 6 — Fix-and-Verify Loop

The fix-and-verify loop is entered when:
1. The review posted `REQUEST_CHANGES`
2. The AI agent has write access to the PR branch
3. The agent is authorized to fix (via human instruction or `ai:ready` label on linked issue)

### 9a. Checkout PR Branch

```bash
# Fetch and checkout the PR branch
git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>
git checkout pr-<PR_NUMBER>

# Or if the branch name is known:
git fetch origin <HEAD_BRANCH>
git checkout <HEAD_BRANCH>
```

### 9b. Apply Fixes

Fix each finding identified in the review. Rules:
- Fix **only** the identified findings; do not refactor surrounding code
- Each fix must directly address a specific finding from the review
- If a finding requires an architecture decision, escalate to human reviewer instead of fixing

### 9c. Commit and Push

```bash
# Stage only the files with fixes
git add <file1> <file2> ...

# Commit with co-author attribution
git commit -m "$(cat <<'EOF'
fix: resolve AI review findings on PR #<PR_NUMBER>

- [Critical] Guard against division by zero in budget_amount (main.py:42)
- [Medium] Replace bare except with except Exception (alerts.py:15)

Co-Authored-By: {AI_TOOL_NAME} <{AI_TOOL_EMAIL}>
EOF
)"

# Push to the PR branch
git push origin HEAD:<HEAD_BRANCH>
```

### 9d. Wait for CI

```bash
GH_HOST={GITHUB_HOST} gh pr checks <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> --watch
```

Do not proceed to re-review until all required CI checks pass.

### 9e. Re-Review

Fetch the updated diff and verify each fix:

```bash
# Fetch updated diff
GH_HOST={GITHUB_HOST} gh pr diff <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO>
```

### Re-Review Verification Checklist

For each finding from the original review:

| Check | Method | Pass Criteria |
|:------|:-------|:--------------|
| Finding resolved | Read diff at the finding location | Code change addresses root cause, not just symptoms |
| No regression | Review the full fix commit diff | Fix does not introduce new bugs or break existing behavior |
| CI passes | `gh pr checks --watch` | All required checks green |
| Scope contained | Compare fix diff to original findings | Fix does not include unrelated changes |
| Tests updated | Check test files in diff | New test covers the fixed scenario (when applicable) |

### 9f. Post Re-Review

If all findings are resolved:

```bash
GH_HOST={GITHUB_HOST} gh api \
  --method POST \
  "/repos/{GITHUB_ORG}/<REPO>/pulls/<PR_NUMBER>/reviews" \
  --input <(cat <<'REVIEW_EOF'
{
  "commit_id": "<NEW_HEAD_SHA>",
  "event": "APPROVE",
  "body": "**AI Agent Re-Review (Claude)**\n\nAll previously identified findings resolved:\n- [x] Critical: Division by zero guard added (main.py:42)\n- [x] Medium: Bare except replaced (alerts.py:15)\n\nCI status: All checks passing.\nNo new issues introduced by fix commits.\n\n**Verdict**: APPROVE\n\n---\n_Re-review by AI agent. Human review still required._",
  "comments": []
}
REVIEW_EOF
)
```

After posting the re-review on the PR, also post a re-review record on the linked issue (same format as §7c, prefixed with "Re-Review #N"):

```bash
GH_HOST={GITHUB_HOST} gh issue comment <ISSUE_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --body "$(cat <<'COMMENT_EOF'
## PR Re-Review #<N> Record — PR #<PR_NUMBER>

**Reviewer**: AI Agent (Claude Opus 4.6)
**Date**: <YYYY-MM-DD HH:MM EST>
**Commit**: `<NEW_SHORT_SHA>`
**Verdict**: <APPROVE | REQUEST_CHANGES>

### Resolved Findings
- [x] <finding 1>
- [x] <finding 2>

### Unresolved Findings
- [ ] <finding if any>

---
_Auto-posted by AI agent review workflow. See [PR #<PR_NUMBER>](<PR_URL>) for full review._
COMMENT_EOF
)"
```

If findings remain unresolved, repeat from Step 9b.

### 9g. Iteration Cap

Maximum **3 iterations** of the fix-verify loop. If findings persist after 3 rounds:

1. Post a `COMMENT` review listing unresolved findings
2. Assign a human reviewer with escalation note:

```bash
GH_HOST={GITHUB_HOST} gh pr comment <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --body "**Escalation**: AI agent fix-verify loop reached 3-iteration cap. Unresolved findings require human review:
- [ ] <finding 1>
- [ ] <finding 2>

Assigning human reviewer for resolution."

GH_HOST={GITHUB_HOST} gh pr edit <PR_NUMBER> \
  --repo {GITHUB_ORG}/<REPO> \
  --add-reviewer {CODEOWNER_1}
```

---

## 10. Edge Cases

| Scenario | Handling |
|:---------|:---------|
| **False positive** | Dismiss own review with rationale: `gh api --method PUT /repos/.../pulls/.../reviews/<REVIEW_ID>/dismissals -f message="False positive: <reason>"` |
| **Disagreement with automated review** | Post `COMMENT` review with rationale; do not override automated Claude review |
| **Partial fix** | Post `COMMENT` listing resolved items (`[x]`) and unresolved items (`[ ]`); assign human reviewer for remaining items |
| **Scope creep during fixes** | Revert unrelated changes; keep fixes scoped to identified findings only |
| **Stale diff (force-push between review and fix)** | Re-fetch diff, re-review from scratch; reference the new HEAD SHA |
| **Merge conflict** | Run `git merge origin/<base> --no-edit`; if conflict is non-trivial, escalate to human |
| **CI failure after fix** | Do not post APPROVE; investigate CI failure; post `COMMENT` with failure details and next steps |
| **Agent lacks repo write access** | Post `REQUEST_CHANGES` review with fixes described in inline comments as code suggestions; human applies fixes manually |
| **PR already approved by human** | AI agent review is supplementary; post findings as `COMMENT` to avoid overriding human approval |
| **Linked issue has no acceptance criteria** | Note the gap in the review comment; do not block merge for missing criteria if code is correct |
| **No linked issue in PR body** | Flag in review summary: _"No linked issue found."_ Continue code review; do not block merge |
| **PR bundles work from multiple issues** | Verify acceptance criteria for each linked issue separately; note in review if PR scope exceeds a single issue |

---

## 11. Governance Integration

### Label Lifecycle Mapping

**Issue Labels** (work lifecycle on linked issue):

| Review Outcome | Label Action | Board Status | Option ID |
|:---------------|:-------------|:-------------|:----------|
| REQUEST_CHANGES (entering fix loop) | Keep `ai:in-progress` | In Progress | `{BOARD_OPTION_IN_PROGRESS}` |
| Fix loop complete, APPROVE posted | Apply `ai:review-requested` | In Review | `{BOARD_OPTION_IN_REVIEW}` |
| Human merges PR | (auto) | Done | `{BOARD_OPTION_DONE}` |

**PR Labels** (review outcome on PR):

| Review Event | PR Label | Trigger |
|:-------------|:---------|:--------|
| APPROVE | `ai:review-passed` | No critical/medium findings |
| COMMENT (low-only) | `ai:review-passed` | Informational findings only |
| REQUEST_CHANGES | `ai:review-failed` | Critical or medium findings |

PR labels are **replaced** on each review (not accumulated). A re-review that passes replaces `ai:review-failed` with `ai:review-passed`.

### Board Status Update

```bash
GH_HOST={GITHUB_HOST} gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "MDk6UHJvamVjdFYyOTg="
    itemId: "<ITEM_ID>"
    fieldId: "MDI2OlByb2plY3RWMlNpbmdsZVNlbGVjdEZpZWxkMTIyMA=="
    value: { singleSelectOptionId: "<OPTION_ID>" }
  }) { projectV2Item { id } }
}'
```

### Acceptance Criteria Verification

Before posting APPROVE, the agent must verify all acceptance criteria in the linked issue body per [GOVERNANCE_RULES.md §3](../GOVERNANCE_RULES.md#acceptance-criteria-sync-mandatory):

| Criterion Type | Verification Method |
|:---------------|:-------------------|
| File/directory exists | `ls`, `gh api`, or Glob tool |
| Configuration has specific values | Read file, confirm contents |
| Feature is implemented | Read source code, run tests |
| CI/CD passes | `gh pr checks --watch` |
| Protection rules applied | Query API to confirm settings |

Check off each verified criterion (`- [ ]` to `- [x]`) in the issue body before requesting human review.

---

## 12. Security Constraints

| Constraint | Detail | Reference |
|:-----------|:-------|:----------|
| Authentication | WIF only (no service account JSON keys) | ADR-002 |
| GHES host | All `gh` commands use `GH_HOST={GITHUB_HOST}` | CLAUDE.md |
| Communication | Teams/Email only (no Slack) | GOVERNANCE_RULES.md §1 |
| Trust boundary | Agent has no access to SA keys, API tokens, production databases, billing credentials | ROLES_AND_TOOLS.md |
| Review authority | AI agent reviews are **advisory**; human review is mandatory per branch protection | GOVERNANCE_RULES.md §3 |
| Self-review | PR author cannot self-review; assign a different human reviewer | CONTRIBUTING.md |
| Commit attribution | All fix commits include `Co-Authored-By: <Agent> <noreply@provider.com>` | README_AIAGENT.md §4 |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.5 | {DATE} | Added machine-readable JSON metadata to §7d, PR label application to §8, PR labels to §11; replaced Gemini references with {AI_TOOL_NAME} Code CLI |
| 1.4 | {DATE} | Added §7d (Review Conclusion Comment) — mandatory separate conclusion comment with "Approved to merge" or "Work needed" decision after every review cycle |
| 1.3 | {DATE} | Added Issue PR Link verification in §8 (Label and Assign) — ensure linked issue has PR number and URL comment for board navigation |
| 1.2 | {DATE} | Added §7c (Issue Review History Comment) — mandatory cross-post of review summary to linked issue after every review and re-review; creates audit trail on the issue |
| 1.1 | {DATE} | Added Step 2 (Verify Linked Issue) — mandatory verification of PR against linked issue acceptance criteria; renumbered steps 3-7; added edge cases for missing/multiple linked issues |
| 1.0 | {DATE} | Initial creation -- on-demand AI agent PR review workflow with fix-and-verify loop |
