# IPLAN-002: AI PR Review Workflow Setup

**Phase**: Cross-phase
**Status**: Template
**Created**: {DATE}
**Issues**: #{AI_REVIEW_SETUP_ISSUE}
**Epic**: #{INFRASTRUCTURE_EPIC}
**Applies Before**: First PR requiring AI review

---

## Purpose

Configure the AI-powered PR review workflow using {AI_TOOL_NAME} Code CLI. This plan covers initial setup, workflow configuration, and integration with the phase-gated deployment process.

---

## Findings

| # | Finding | Severity | Impact |
|---|---------|----------|--------|
| 1 | AI review requires API key configuration | HIGH | Workflow will fail without key |
| 2 | Review labels must be created before workflow runs | MEDIUM | Workflow can't apply labels |
| 3 | Reusable workflow needs repository permissions | MEDIUM | Cross-repo calls blocked |

---

## Analysis

### Current State

- GitHub Actions workflows exist but AI review is not configured
- No `ANTHROPIC_API_KEY` secret set
- AI review labels (`ai:review-passed`, `ai:review-failed`) may not exist

### Target State

- AI review triggers automatically on PR creation/update
- Reviews complete within budget limit (`{AI_REVIEW_BUDGET}` per review)
- Pass/fail labels applied automatically
- Review comments posted to PR
- Conclusion summary posted to linked issue

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| GitHub Actions enabled | Blocks | Verify |
| ANTHROPIC_API_KEY secret | Blocks | Configure |
| ai:review-* labels created | Blocks | Configure |
| {AI_TOOL_NAME} Code CLI available | Blocks | Verify runner |

---

## Change Execution Checklist

### Pre-Implementation
- [ ] Verify GitHub Actions is enabled for repository
- [ ] Obtain Anthropic API key from console.anthropic.com
- [ ] Review ai-review.yml workflow file

### Implementation

#### Step 1: Configure Secrets
```bash
GH_HOST={GITHUB_HOST} gh secret set ANTHROPIC_API_KEY --body "sk-ant-..."
```

#### Step 2: Create Labels
```bash
GH_HOST={GITHUB_HOST} gh label create "ai:review-passed" --color "0E8A16" --description "AI review passed"
GH_HOST={GITHUB_HOST} gh label create "ai:review-failed" --color "D93F0B" --description "AI review failed"
GH_HOST={GITHUB_HOST} gh label create "skip-ai-review" --color "CCCCCC" --description "Skip AI review for this PR"
```

#### Step 3: Verify Workflow
- [ ] Create test branch with small change
- [ ] Open PR to trigger ai-review workflow
- [ ] Verify review comment posted
- [ ] Verify label applied (`ai:review-passed` or `ai:review-failed`)

#### Step 4: Configure Budget (Optional)
Update `.github/workflows/ai-review.yml`:
```yaml
env:
  AI_REVIEW_MODEL: "{AI_REVIEW_MODEL}"
  AI_REVIEW_BUDGET: "{AI_REVIEW_BUDGET}"
```

### Post-Implementation
- [ ] Document API key rotation procedure
- [ ] Add AI review to PR template checklist
- [ ] Update CONTRIBUTING.md with AI review expectations
- [ ] Mark this plan as Complete

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API key exposure | LOW | HIGH | Use GitHub secrets, never commit |
| Review cost overrun | LOW | MEDIUM | Set budget limit in workflow |
| False positive failures | MEDIUM | LOW | Allow `skip-ai-review` label override |

---

## Rollback Procedure

If AI review causes issues:
1. Add `skip-ai-review` label to affected PRs
2. Disable workflow: rename `ai-review.yml` to `ai-review.yml.disabled`
3. Investigate logs and fix configuration
4. Re-enable workflow after fix verified

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {DATE} | {AUTHOR} | Initial template |
