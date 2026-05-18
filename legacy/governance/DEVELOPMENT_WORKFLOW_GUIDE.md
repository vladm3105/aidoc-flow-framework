# Development Workflow Guide

This guide describes the workflow for developing GitHub Issues within the governance framework. It implements a structured approach from issue assignment through completion.

**Scope**: GitHub Issue-based development workflow only. For full governance policies, see [GOVERNANCE_RULES.md](./GOVERNANCE_RULES.md).

**Related Documents**:
- [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) — Completion checklists
- [AI_ISSUE_LIFECYCLE.md](./AI_ISSUE_LIFECYCLE.md) — Issue flow and labels
- [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) — Git workflow
- [plans/README.md](./plans/README.md) — IPLAN templates

---

## Workflow Overview

```
Task Defined -> Issue Created -> Planning Package -> Plan Review/Gap Fix -> Approved IPLAN -> Work -> PR -> Round 1 Gates -> Round 2 (if needed) -> Escalate or Merge -> Deploy Verify
    │               │                │                    │                 │             │      │      │                    │                   │              │
    ▼               ▼                ▼                    ▼                 ▼             ▼      ▼      ▼                    ▼                   ▼              ▼
Hermes/        Hermes adds      Hermes creates       Hermes closes      Hermes records  Execution  CI   sdd_validate ->     Repeat same       Human review     Hermes reviews
Human source   traceability      roadmap/index/      planning gaps      plan approval   agent fix     sdd_review ->        sequence on        if Round 2      post-deploy
                                 changelog plan                          and IPLAN       + PR        sdd_remediate ->     Round 1 fail       fails           evidence
                                                                                                    validate -> Hermes
                                                                                                    final blocker-gap
```

Execution scope for this guide:

- Hermes manages issue triage, planning boundaries, and lifecycle governance gates.
- Execution agents (Claude Code, Codex, OpenCode, or equivalent) perform implementation and deployment steps for issues in `ai:ready`.

---

## Step 1: Issue Assignment

### Receive Issue

When an issue is assigned (label: `ai:ready` or manual assignment):

1. **Read the issue** completely:
   - Title and description
   - Acceptance criteria
   - Labels (phase, component, priority)
   - Linked issues (blocked-by, blocks)

2. **Check prerequisites**:
   - [ ] All `blocked-by` issues are resolved
   - [ ] Required dependencies are available
   - [ ] Acceptance criteria are clear and testable

3. **Planning gate check**:
   - [ ] Planning roadmap exists for issue scope
   - [ ] Planning index exists for required plan artifacts
   - [ ] Changelog plan exists for issue scope
   - [ ] Planning gap review completed (resolved or deferred with rationale)
   - [ ] IPLAN exists and is explicitly approved

4. **Update status**:
   - Add label: `ai:in-progress`
   - Update project board status

### Issue Checklist

Before starting work:
- [ ] Issue has clear acceptance criteria
- [ ] Scope is well-defined
- [ ] No unresolved blockers
- [ ] Branch name determined: `ai/{issue-number}-{short-name}`

`ai:ready` gate policy:

- Only issues in `ai:ready` are eligible for autonomous execution by coding agents.
- Issues created by observability triage remain pending until human/policy approval moves them to `ai:ready`.

---

## Step 2: Review for Practical Implementation

Before writing code, validate the approach:

### Planning-First Requirement

Before implementation starts, complete this sequence:

1. Create planning roadmap for issue scope.
2. Create planning index listing required plan documents.
3. Define changelog plan for issue scope.
4. Run planning gap review and resolve or defer gaps with explicit rationale.
5. Create and approve IPLAN.

### Practical Review Questions

| Question | Purpose |
|:---------|:--------|
| Can this be implemented with available resources? | Feasibility |
| Is the scope achievable in reasonable time? | Scope control |
| Are dependencies identified and available? | Risk mitigation |
| Is the solution appropriately simple? | Avoid over-engineering |
| Can it be tested (unit/integration)? | Quality assurance |

### Review Checklist

- [ ] Solution addresses the stated problem directly
- [ ] Implementation approach is practical
- [ ] No unnecessary complexity
- [ ] Edge cases identified
- [ ] Error handling approach defined

### IPLAN Requirement

Create an IPLAN document (`plans/IPLAN-NNN_{slug}.md`) for every `ai:ready` issue before implementation.

> **Reference**: See [plans/README.md](./plans/README.md) for IPLAN template.

---

## Step 3: Implement

Gate condition: start this step only after planning artifacts and IPLAN are approved.

### Create Branch

```bash
git checkout main
git pull origin main
git checkout -b ai/{issue-number}-{short-name}
# Example: ai/123-add-budget-alerts
```

### Implementation Guidelines

| Guideline | Description |
|:----------|:------------|
| **Follow conventions** | Project coding standards, naming conventions |
| **Incremental commits** | Commit after each logical unit of work |
| **Reference issue** | Include `#{issue-number}` in commit messages |
| **Stay in scope** | Only implement what the issue requests |

### During Implementation

- [ ] Follow project coding conventions
- [ ] Keep changes focused on issue scope
- [ ] Update IPLAN status if applicable
- [ ] Note any blockers or questions in issue comments

---

## Step 4: Test/Code Review (AI Agent)

Before creating PR, perform comprehensive quality checks:

### Bug Detection & Fixes

- [ ] Run existing tests - all must pass
- [ ] Identify edge cases - test them
- [ ] Fix any bugs found during testing
- [ ] Verify no regressions introduced

### Unit Tests

- [ ] Write unit tests for new functions/classes
- [ ] Target: ≥80% coverage on new code
- [ ] Test happy path and error cases
- [ ] Test edge cases identified during review

### Regression Tests

- [ ] Run full test suite
- [ ] Verify existing functionality unchanged
- [ ] Check integration points still work

### Code Comments

Update comments for non-obvious logic:

```python
# BAD: No comment for complex logic
result = sum(x * weights[i] for i, x in enumerate(values) if x > threshold)

# GOOD: Explains the purpose
# Calculate weighted sum of values exceeding threshold
# Used for scoring documents above minimum quality bar
result = sum(x * weights[i] for i, x in enumerate(values) if x > threshold)
```

### Docstrings

Complete docstrings for all new functions:

```python
def validate_document(path: str, strict: bool = False) -> ValidationResult:
    """Validate a document against schema rules.

    Args:
        path: Absolute path to the document file.
        strict: If True, treat warnings as errors.

    Returns:
        ValidationResult with findings and score.

    Raises:
        FileNotFoundError: If document path doesn't exist.
        ValidationError: If document structure is invalid.
    """
```

### Test/Code Review Checklist

- [ ] All identified bugs fixed
- [ ] Unit tests written (≥80% coverage on new code)
- [ ] Regression tests pass
- [ ] Code comments explain non-obvious logic
- [ ] Function docstrings complete (purpose, params, returns, raises)
- [ ] Type hints added where applicable
- [ ] Module docstrings updated (if new module)

---

## Step 5: Commit

### Commit Strategy

| Scenario | When to Commit |
|:---------|:---------------|
| Logical unit complete | Function, class, or module finished |
| Tests added | After writing tests for a component |
| Bug fixed | After fix is verified working |
| Documentation | After updating docs/comments |

### Commit Message Format

```
<type>(<scope>): <short summary>

<body - explains why, not what>

<footer - references>
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

**Examples**:

```bash
# Feature implementation
git commit -m "feat(alerts): add budget threshold notification

Implements email notification when budget exceeds 80%.
Uses existing notification service.

Ref #123"

# Bug fix
git commit -m "fix(api): resolve timeout on large queries

Reduced query complexity by pre-aggregating data.

Fixes #456"

# Tests
git commit -m "test(alerts): add unit tests for threshold logic

Coverage: 92% for budget_alerts.py

Ref #123"
```

### AI Co-Author Attribution

Include in final commit:

```
Co-Authored-By: {AI_TOOL_NAME} <{AI_TOOL_EMAIL}>
```

---

## Step 6: CI Pipeline

### Push and Verify

```bash
git push -u origin ai/{issue-number}-{short-name}
```

### CI Stages

| Stage | Tests | Must Pass |
|:------|:------|:----------|
| **Lint** | ruff, black, isort | Yes |
| **Unit Tests** | pytest unit/ | Yes |
| **Integration Tests** | pytest integration/ | Yes |
| **Coverage** | coverage.py (≥80%) | Yes |
| **Security** | Security scan | Yes |
| **Doc Validation** | If docs changed | Yes |

### If CI Fails

1. Read the failure logs
2. Fix the issue locally
3. Run tests locally to verify
4. Push fix commit
5. Wait for CI to re-run

---

## Step 7: Documentation Updates

### Update Issue

Post progress comment on the issue:

```markdown
## Implementation Complete

**Branch**: `ai/123-add-budget-alerts`
**PR**: #{pr-number}

### Changes
- Added budget threshold notification
- Created unit tests (92% coverage)

### Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed

### Ready for Review
```

### Update Acceptance Criteria

Mark completed acceptance criteria in the issue:

```markdown
## Acceptance Criteria
- [x] Budget threshold is configurable
- [x] Email notification sent when exceeded
- [x] Notification includes budget details
```

---

## Step 8: Create PR & Get Approval

### Create Pull Request

```bash
gh pr create \
  --title "feat(alerts): add budget threshold notification" \
  --body "## Summary
Implements budget threshold notification.

## Related
- Closes #123

## Changes
- Added notification service integration
- Created unit tests

## Testing
- [x] Unit tests (92% coverage)
- [x] Integration tests
- [x] Manual testing"
```

### PR Checklist

- [ ] PR title follows conventional commit format
- [ ] PR body references issue (`Closes #123`)
- [ ] All CI checks pass
- [ ] Reviewer assigned (CODEOWNERS or manual)
- [ ] Self-review completed

### Request Review

1. Update issue label: `ai:review-requested`
2. Post PR link on issue
3. Wait for reviewer feedback

### Address Feedback

If changes requested:
1. Make requested changes
2. Push new commits
3. Re-request review
4. Update issue comment with changes made

### Round-Based PR Governance (Mandatory)

After PR submission, apply this sequence:

1. Round 1: `sdd_validate` -> `sdd_review` -> `sdd_remediate` -> post-remediation `sdd_validate` -> Hermes final blocker-gap/inconsistency review.
2. If any blocking gate fails, run Round 2 with the same sequence.
3. If Round 2 fails, escalate to human review and keep merge blocked until resolved.
4. If gates pass, merge is allowed.

---

## Step 9: Close Issue

### After PR Merge

1. **Verify issue closed** - PR should auto-close via `Closes #123`
2. **Update project board** - Status should update automatically
3. **Verify branch deleted** - Auto-deleted after merge
4. **Validate post-deployment signals** - Hermes confirms monitoring/alert state is healthy for the fixed scope
5. **Post completion comment** (if not auto-closed):

```markdown
## Completed

PR #{pr-number} merged to main.

### Summary
- Budget threshold notification implemented
- Unit test coverage: 92%
- Documentation updated

### Follow-up
- None required
```

---

## Quick Reference

### Label Transitions

```
ai:ready → ai:in-progress → ai:review-requested → (PR merged) → (issue closed)
```

### Branch Naming

```
ai/{issue-number}-{short-name}
# Examples:
ai/123-add-budget-alerts
ai/456-fix-api-timeout
```

### Commit Types

| Type | Usage |
|:-----|:------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Code restructuring |
| `chore` | Maintenance |

### Checklist Summary

**Before Implementation**:
- [ ] Issue understood and acceptance criteria clear
- [ ] Approach reviewed for practicality
- [ ] Branch created

**During Implementation**:
- [ ] Code follows conventions
- [ ] Incremental commits made
- [ ] Tests written

**Before PR**:
- [ ] All tests pass
- [ ] Docstrings complete
- [ ] Comments updated
- [ ] CI passes

**Before Close**:
- [ ] PR approved and merged
- [ ] Issue acceptance criteria marked complete
- [ ] Branch deleted

---

## Troubleshooting

| Issue | Solution |
|:------|:---------|
| CI fails on lint | Run `ruff check --fix` and `black .` locally |
| Tests fail | Check test output, fix code or test |
| Coverage below threshold | Add more tests for uncovered code |
| PR blocked by review | Address feedback, re-request review |
| Issue not auto-closing | Manually close with comment linking PR |

> **Reference**: See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more solutions.

---

## Related Documents

| Document | Purpose |
|:---------|:--------|
| [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) | Completion checklists |
| [AI_ISSUE_LIFECYCLE.md](./AI_ISSUE_LIFECYCLE.md) | Full issue lifecycle |
| [GOVERNANCE_RULES.md](./GOVERNANCE_RULES.md) | Operational policies |
| [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) | Git workflow |
| [plans/README.md](./plans/README.md) | IPLAN templates |
| [AI_PR_Review/](./AI_PR_Review/) | PR review workflow |

---

*Last Updated: 2026-03-18*
