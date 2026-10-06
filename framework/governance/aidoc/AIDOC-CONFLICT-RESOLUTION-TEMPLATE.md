# Architecture & Operational Standard: Autonomous PR Conflict Resolution Protocol

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.88.2 |

**Scope:** Conflict Triage & Resolution Procedures for `[Project Name]`
**Governing Rules:** `WORKTREE_FLOW.md`, `CI_AUTONOMOUS_PR_STANDARD.md`
**Canonical Template:** `framework/governance/aidoc/AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md`

---

## 1. Purpose & Motivation

When multiple autonomous agents or human contributors merge feature branches into `dev`, an open pull request may experience merge conflicts. While simple conflicts in append-only files (such as changelogs, indexes, or task registries) can be safely reconciled autonomously, semantic conflicts in application logic or interface contracts can introduce subtle architectural regressions if resolved blindly.

This standard establishes the **Conflict Classification Matrix**, **Forward Merge Procedure**, and **Auto-Merge Re-Arming Mandate**.

---

## 2. Conflict Classification Matrix

| Conflict Class | Permitted File Scope | Agent Action | Human Escalation Required? |
|---|---|---|---|
| **Class 1: Deterministic / Additive** | Append-only markdown tables, task tracking lists, changelogs, non-overlapping schema additions, documentation registries | Autonomously resolve in local worktree via forward branch merge | **No** (unless re-verification fails) |
| **Class 2: Semantic / Architectural** | Code files (`src/**`), interface definitions, database migrations, concurrent edits to the same function body, file deletions vs modifications | `git merge --abort` immediately; post diagnostic report to PR | **YES (Mandatory Halt)** |

---

## 3. Autonomous Resolution Protocol

For Class 1 conflicts, the assigned agent executes the following exact sequence inside the task's dedicated git worktree:

### Step 1: Synchronize Remote State

```bash
cd ../<project>-<task>
git fetch origin dev
```

### Step 2: Forward Merge Target Branch

```bash
git merge origin/dev
```

*Note: NEVER use `git rebase` on branches that have already been pushed to remote pull requests. Rebasing rewires commit history and disrupts GitHub/GitLab PR review tracking.*

### Step 3: Inspect & Reconcile Conflicts

1. Identify conflicted files using `git status --short`.
2. Verify that **ALL** conflicted files fall strictly within the Class 1 category.
3. If any Class 2 file appears, immediately execute:
   ```bash
   git merge --abort
   ```
   and halt execution with an escalation comment on the PR.
4. For Class 1 files, reconcile conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) by preserving both upstream and local entries in sorted, chronological, or designated structural order.

### Step 4: Validate Changes Locally

Run project static analysis, linting, and local unit test suites to verify that the resolution introduced zero syntax or structural errors:

```bash
pre-commit run --all-files
pytest tests/
```

### Step 5: Commit & Push Forward Merge

```bash
git add <reconciled-files>
git commit -m "chore: merge origin/dev to resolve additive conflicts"
git push origin feature/<branch-name>
```

*Note: Zero force-pushes allowed. Passing `--force` or `--force-with-lease` is strictly prohibited.*

### Step 6: Auto-Merge Re-Arming Mandate (CRITICAL)

Pushing a new commit automatically clears armed auto-merge status on GitHub/GitLab. The agent MUST explicitly re-verify and re-arm auto-merge:

```bash
# Query PR check status
gh pr checks <PR_NUMBER>

# Re-arm auto-merge
gh pr merge <PR_NUMBER> --auto --squash

# Verify auto-merge is active
gh pr view <PR_NUMBER> --json autoMergeRequest --jq '.autoMergeRequest'
```

---

## 4. Circuit Breakers

- **CB-5.1 (Single Resolution Attempt):** An agent is permitted at most ONE autonomous conflict resolution attempt per PR. If conflict markers persist or new conflicts arise post-push, the agent must halt and alert the human maintainer.
- **CB-5.2 (Zero Semantic Guessing):** Any conflict in algorithmic logic, control flow, or interface typing triggers an immediate abort and escalation.
