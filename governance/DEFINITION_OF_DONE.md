# Definition of Done (DoD)

This document defines when a task, sprint, or phase is considered **complete**.

**Related Documents**:
- [GOVERNANCE_RULES.md](./GOVERNANCE_RULES.md) — Operational policies and conventions (how we work)
- [templates/PROJECT_PLAN-TEMPLATE.md](./templates/PROJECT_PLAN-TEMPLATE.md) — Project plan template
- [templates/ROADMAP-TEMPLATE.md](./templates/ROADMAP-TEMPLATE.md) — Roadmap template

> **Note**: Create `PROJECT_PLAN.md` and `ROADMAP.md` in your project from the templates above.

## Task Level
A task (Issue) is **Done** when:
- [ ] Code is written and follows project conventions
- [ ] Unit tests written with ≥80% coverage on new/modified code
- [ ] Integration tests written for service boundary changes (if applicable)
- [ ] All tests pass locally (`pytest` or `npm test`)
- [ ] Security scan passes (no HIGH/CRITICAL vulnerabilities)
- [ ] PR is reviewed and approved by at least 1 reviewer
- [ ] PR review verifies changes against linked issue acceptance criteria (see [GOVERNANCE_RULES.md §3](./GOVERNANCE_RULES.md#linked-issue-verification-in-pr-review-mandatory))
- [ ] AI PR review workflow passes (or `skip-ai-review` label applied with justification)
- [ ] CI pipeline passes (lint, test, build)
- [ ] PR is merged to `main`
- [ ] Related documentation is updated (if applicable)
- [ ] Issue is closed via PR link (`Closes #123`)

## UI/Frontend Task Level
A UI task is **Done** when (in addition to Task Level criteria):
- [ ] E2E tests written using Playwright MCP or Playwright test runner
- [ ] Visual regression verified (screenshot comparison if applicable)
- [ ] Accessibility snapshot captured and reviewed
- [ ] Console errors checked (no JavaScript errors)

## AI-Implemented Task Level
An AI-implemented task is **Done** when (in addition to Task Level criteria):
- [ ] AI label workflow completed: `ai:ready` → `ai:in-progress` → `ai:review-requested` → (PR merge)
- [ ] Project Board #{PROJECT_BOARD_NUMBER} status updated at each label transition (see [GOVERNANCE_RULES.md §3](./GOVERNANCE_RULES.md#3-ai-workflow))
- [ ] Issue acceptance criteria **verified** (not blind-checked) and marked (`- [x]`) before requesting review (see [GOVERNANCE_RULES.md §3](./GOVERNANCE_RULES.md#3-ai-workflow))
- [ ] PR number and URL posted as comment on linked issue (see [GOVERNANCE_RULES.md §3](./GOVERNANCE_RULES.md#issue-pr-link-mandatory))
- [ ] PR has at least one reviewer assigned (CODEOWNERS auto-assign or manual from [CONTRIBUTING.md roster](../CONTRIBUTING.md#reviewer-roster))
- [ ] If AI agent performed on-demand review with fix loop: all critical/medium findings resolved and re-review APPROVE posted ([AI_AGENT_REVIEW_WORKFLOW.md](./AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md))
- [ ] If on-demand AI review performed: conclusion comment posted and `ai:review-passed` or `ai:review-failed` label applied to PR
- [ ] Review history posted to linked issue after each review/re-review (see [GOVERNANCE_RULES.md §3](./GOVERNANCE_RULES.md#issue-review-history-mandatory))
- [ ] Human reviewer has validated AI-generated code
- [ ] No security vulnerabilities introduced (verified by human)
- [ ] Commit includes AI co-author attribution:
  ```
  Co-Authored-By: {AI_TOOL_NAME} <{AI_TOOL_EMAIL}>
  ```
- [ ] AI branch `ai/<issue>-<name>` is auto-deleted after merge

> **Note**: `ai:approved`/`ai:rejected` labels are not used — PR approval status is sufficient. See [GOVERNANCE_RULES.md §3](./GOVERNANCE_RULES.md#3-ai-workflow).

## Sprint Level
A sprint is **Done** when:
- [ ] All committed sprint tasks meet the Task-level DoD
- [ ] No critical (`P0`) bugs remain open
- [ ] Sprint retrospective is completed (lessons learned noted)
- [ ] Sprint deliverables are demo-ready
- [ ] Governance document sync completed (see [GOVERNANCE_RULES.md §6](./GOVERNANCE_RULES.md#6-document-maintenance))

## Phase Level
A phase is **Done** when:
- [ ] All sprints within the phase are complete
- [ ] Phase **Exit Criteria** (defined in your project's `ROADMAP.md`) are met
- [ ] Component is tagged with a release version (SemVer)
- [ ] CHANGELOG.md is updated per [RELEASE_PROCESS.md](./RELEASE_PROCESS.md)
- [ ] Governance document sync completed (see [GOVERNANCE_RULES.md §6](./GOVERNANCE_RULES.md#6-document-maintenance))
- [ ] Integration with Platform repo is verified (if applicable)

## Phase-Gated Deployment

### Development Issue Complete
A development issue (`ai:development`) is **Complete** when:
- [ ] PR merged to `main`
- [ ] Issue closed via PR link
- [ ] Deployment issue auto-created (`ai:deployment`)
- [ ] QA testing issue auto-created (`ai:qa-testing`) if functional changes

### Phase Development Complete
A phase's development is **Complete** when:
- [ ] All development issues with `phase:N` are closed
- [ ] `check-phase-completion.yml` detects phase completion
- [ ] All deployment issues exist for the phase

### Staging Deployment Complete
A phase's staging deployment is **Complete** when:
- [ ] AI Agent reviews all deployment issues
- [ ] Consolidated deployment plan created
- [ ] `deploy-staging.yml` successfully deploys all phases 1..N
- [ ] All deployment issues closed with `ai:deployment`

### QA Testing Complete
A phase's QA testing is **Complete** when:
- [ ] All QA issues activated (blocked-by deployment resolved)
- [ ] `execute-qa-testing.yml` runs all test types:
  - Smoke tests pass
  - Unit tests pass (coverage ≥90%)
  - Integration tests pass (coverage ≥70%)
  - E2E tests pass
  - Feature-specific tests pass
- [ ] All QA issues closed with `ai:qa-passed`
- [ ] OR: Bug issues created and iterated (max 3 times)

### Bug Fix Iteration Complete
A bug fix iteration is **Complete** when:
- [ ] Bug issue (`ai:development` + `bug` + `iteration:N`) resolved
- [ ] PR merged, creating new deployment + QA issues
- [ ] QA tests pass on fixed code
- [ ] OR: Max iterations (3) reached → `needs-human` escalation created

### Production Ready
A phase is **Production Ready** when:
- [ ] All phases 1..N deployed to staging
- [ ] All QA testing complete (all `ai:qa-passed`)
- [ ] No open `blocker` issues
- [ ] No open `needs-human` issues
- [ ] `governance/cicd/phase-deployments.json` shows all phases `qa_status: passed`

## Component Repository Release
A component repo is **Release-Ready** when:
- [ ] All Phase-level DoD items are satisfied
- [ ] README is complete and accurate
- [ ] CI/CD pipeline builds and tests successfully
- [ ] Git tag is created (e.g., `v1.0.0`)
- [ ] GitHub Release is published with notes

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 2.0 | {DATE} | Added Phase-Gated Deployment section: Development Issue Complete, Phase Development Complete, Staging Deployment Complete, QA Testing Complete, Bug Fix Iteration Complete, Production Ready checklists |
| 1.9 | {DATE} | Added PR label criterion (`ai:review-passed`/`ai:review-failed`) to AI-Implemented Task checklist |
| 1.8 | {DATE} | Added PR link posted to linked issue as AI-Implemented Task checklist item |
| 1.7 | {DATE} | Added review history cross-post to linked issue as AI-Implemented Task checklist item |
| 1.6 | {DATE} | Added linked issue verification as Task Level checklist item |
| 1.5 | {DATE} | Added AI agent on-demand review fix-verify loop checklist item |
| 1.4 | {DATE} | Added AI PR review workflow pass as Task Level checklist item |
| 1.3 | {DATE} | Added acceptance criteria sync checklist item — must check off issue criteria before review |
| 1.2 | {DATE} | Added AI task checklist items: board status sync at label transitions, PR reviewer assignment (CODEOWNERS or manual) |
| 1.1 | {DATE} | Extracted process rules to GOVERNANCE_RULES.md; fixed AI label lifecycle (removed `ai:approved`); replaced inline doc sync section with cross-reference |
| 1.0 | {DATE} | Initial DoD with task/sprint/phase completion criteria |
