# ai-pr-review Quick Reference

## Invocation

```
/ai-pr-review PR#<NUMBER>
```

Or within conversation:
```
Review PR #42 following the AI PR Review workflow.
```

## Review Types

| Type | Command | Description |
|:-----|:--------|:------------|
| Basic | `Review PR #42` | Code analysis + formal review |
| With Issue | `Review PR #42 against issue #30` | + acceptance criteria verification |
| With Fixes | `Review PR #42 with fixes enabled` | + fix-and-verify loop |

## Severity Tags

- `[Critical]` - Security, data loss, crashes → REQUEST_CHANGES
- `[Medium]` - Bugs, missing error handling → REQUEST_CHANGES
- `[Low]` - Best practices, minor issues → COMMENT

## Review Events

| Event | Condition | Label |
|:------|:----------|:------|
| APPROVE | No critical/medium | `ai:review-passed` |
| COMMENT | Low only | `ai:review-passed` |
| REQUEST_CHANGES | Critical/medium | `ai:review-failed` |

## Skip Label

Add `skip-ai-review` label to bypass automated review.

## Limits

- 15 inline comments max
- $1.00 USD budget cap
- 5 minute timeout
- 3 fix-verify iterations max

## Prerequisites

1. `gh` CLI authenticated
2. `ANTHROPIC_API_KEY` secret set
3. Labels created: `ai:review-passed`, `ai:review-failed`, `skip-ai-review`

## Setup Labels

```bash
./scripts/setup-ai-pr-review-labels.sh
```

## Manual Workflow Trigger

```bash
gh workflow run ai-pr-review.yml --field pr_number=42 --field model=sonnet
```

## Output Locations

| Output | Where |
|:-------|:------|
| Inline comments | PR → Files changed tab |
| Summary | PR → Conversation |
| Conclusion | PR → Conversation (final) |
| Label | PR → Labels sidebar |

## Related

- [AI_AGENT_REVIEW_WORKFLOW.md](../../governance/AI_PR_Review/AI_AGENT_REVIEW_WORKFLOW.md)
- [code-review skill](./code-review/SKILL.md)
