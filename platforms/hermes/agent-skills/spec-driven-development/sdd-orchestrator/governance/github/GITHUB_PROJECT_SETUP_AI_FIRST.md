# GitHub Project Setup Guide — AI-First Companion

Project-agnostic companion for AI-first GitHub Project configuration.

This document supplements (does not replace) [GITHUB_PROJECT_SETUP.md](./GITHUB_PROJECT_SETUP.md) with AI-first controls and migration checks.

---

## Purpose

Use this companion when enabling AI-driven issue execution and phase-gated automation in a new repository.

Core goals:
- Align labels, board fields, and workflows to AI lifecycle.
- Ensure workflow automation and governance docs are consistent.
- Keep all configuration reusable across organizations/projects.

---

## AI-First Setup Additions

### 1) Label Lifecycle

Ensure these labels exist and are documented consistently:
- `ai:ready`
- `ai:in-progress`
- `ai:review-requested`
- `ai:review-passed`
- `ai:review-failed`

### 2) Board Status Mapping

Ensure status transitions map to label lifecycle and automation workflows.

### 3) Workflow Migration Coverage

Verify the workflow inventory in [GITHUB_WORKFLOWS.md](./GITHUB_WORKFLOWS.md) includes:
- issue/PR board sync
- AI review
- phase completion checks
- deployment triggers (including optional AI-driven dev deploy path)
- QA and bug-loop workflows

### 4) Secrets and Permissions

Validate required secrets and least-privilege permissions per workflow family.

---

## Migration Checklist

- [ ] Labels are created and documented in governance docs.
- [ ] Board fields and option mappings are validated.
- [ ] Workflow summary table matches actual `.github/workflows/*` inventory.
- [ ] AI-specific workflow docs include trigger, inputs, outputs, failure behavior.
- [ ] Project-specific names/IDs are replaced with placeholders.

---

## Validation Commands

```bash
# List workflows
gh workflow list

# List labels
gh label list

# Optional: list recent workflow runs
gh run list --limit 20
```

---

## Related Docs

- [GITHUB_PROJECT_SETUP.md](./GITHUB_PROJECT_SETUP.md)
- [GITHUB_WORKFLOWS.md](./GITHUB_WORKFLOWS.md)
- [../GOVERNANCE_RULES.md](../GOVERNANCE_RULES.md)
- [../AI_ISSUE_LIFECYCLE.md](../AI_ISSUE_LIFECYCLE.md)
