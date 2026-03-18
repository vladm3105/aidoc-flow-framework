# UCX Development Workflow

## Overview

This document describes the development workflow used in UCX for planning features, tracking changes, and maintaining documentation. This approach ensures traceability, clear versioning, and comprehensive documentation.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Document Hierarchy](#document-hierarchy)
3. [Commit Strategy](#commit-strategy)
4. [Code Review & Testing](#code-review--testing)
5. [CI/CD Integration](#cicd-integration)
6. [Feature Development Workflow](#feature-development-workflow)
7. [Bug Fix Workflow](#bug-fix-workflow)
8. [Hotfix Process](#hotfix-process)
9. [Versioning Strategy](#versioning-strategy)
10. [Rollback Procedures](#rollback-procedures)
11. [Documentation Standards](#documentation-standards)
12. [Plan Document Lifecycle](#plan-document-lifecycle)
13. [Roadmap Management](#roadmap-management)
14. [Changelog Standards](#changelog-standards)
15. [Deprecation Process](#deprecation-process)
16. [Example: Full Feature Lifecycle](#example-full-feature-lifecycle)
17. [Quick Reference](#quick-reference)

---

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Plan Before Code** | New features require a PLAN document before implementation |
| **Version Everything** | Each release has a version number and changelog |
| **Document as You Go** | Documentation updated with each significant change |
| **Roadmap-Driven** | Development guided by ROADMAP with clear priorities |
| **Traceable History** | Every change linked to plan, changelog, and roadmap |

---

## Document Hierarchy

```
UCX/
├── docs/
│   ├── ROADMAP.md                    # Master planning document
│   ├── CHANGELOG_v{X.Y.Z}.md         # Per-version change history
│   ├── plans/                        # Feature plans (permanent)
│   │   ├── PLAN-001_feature_name.md
│   │   ├── PLAN-002_feature_name.md
│   │   └── ...
│   ├── CONTEXT_ENGINEERING.md        # Feature documentation
│   ├── WORKFLOW_ARCHITECTURE.md      # Architecture documentation
│   └── ...
└── tmp/                              # Temporary documents (bug fixes, experiments)
    └── fix_issue_123.md              # Deleted after resolution
```

---

## Commit Strategy

### Commit Frequency

| Scenario | When to Commit |
|----------|----------------|
| **Feature development** | After each logical unit of work (function, module, phase) |
| **Bug fix** | After fix is verified working |
| **Documentation** | After significant updates |
| **Refactoring** | After each safe transformation |

### Commit Message Format

Use conventional commits with scope:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes nor adds |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

**Scopes** (UCX-specific):
| Scope | Usage |
|-------|-------|
| `ucx` | Core UCX functionality |
| `validator` | Validation system |
| `review` | Review phase (UCR) |
| `remediate` | Remediation phase (UCRem) |
| `cli` | CLI commands |
| `skills` | Persona skills |
| `docs` | Documentation |

### Commit Examples

**Feature development** (multiple commits):
```bash
# Phase 1: Core implementation
git commit -m "feat(ucx): add context engine base class

Implements HierarchicalContext dataclass and ContextEngine.
Part of PLAN-003."

# Phase 2: Integration
git commit -m "feat(review): integrate context engine with UCR phase

- Add build_hierarchical_context() to persona prompts
- Update prompt builder to use filtered sections"

# Phase 3: Tests
git commit -m "test(ucx): add context engine unit tests

Coverage: 94% for context_engine.py"
```

**Bug fix** (single commit after verification):
```bash
git commit -m "fix(validator): prevent circular rename in duplicate fixer

GATE-E008 fixer was creating infinite loops when elements
referenced each other. Added visited set to track processed IDs.

Fixes #123"
```

**Documentation update**:
```bash
git commit -m "docs(ucx): add DEVELOPMENT_WORKFLOW.md

Documents the development process including plans, changelogs,
versioning, and commit practices."
```

### When to Commit

```
Feature Development Timeline:
────────────────────────────────────────────────────────────────►
    │           │           │           │           │
    ▼           ▼           ▼           ▼           ▼
  PLAN      Phase 1     Phase 2     Tests      Release
 created   complete    complete   passing
    │           │           │           │           │
    └─ commit   └─ commit   └─ commit   └─ commit   └─ final commit
       (docs)     (feat)      (feat)      (test)      (chore: bump version)
```

### Commit Checkpoints

**During feature development**, commit when:
- [ ] A logical unit of work is complete
- [ ] Tests pass for the new code
- [ ] Code compiles/runs without errors
- [ ] You're about to start a different task
- [ ] End of work session

**After bug fix**, commit when:
- [ ] Fix is implemented
- [ ] Fix is tested locally
- [ ] No regressions introduced
- [ ] Ready for review

**After documentation**, commit when:
- [ ] Document is complete and reviewed
- [ ] Links and references are valid
- [ ] Formatting is correct

### Branch Strategy

| Branch | Purpose | Commits |
|--------|---------|---------|
| `main` | Stable releases | Merge commits only |
| `feature/PLAN-NNN-name` | Feature development | Regular commits |
| `fix/issue-NNN` | Bug fixes | Fix commits |
| `docs/topic` | Documentation | Doc commits |

### Commit Best Practices

1. **Atomic commits**: Each commit should represent one logical change
2. **Passing state**: Never commit broken code to shared branches
3. **Reference plans**: Include `PLAN-NNN` in commit body for features
4. **Reference issues**: Include `Fixes #NNN` for bug fixes
5. **Regular commits**: Don't accumulate too many changes before committing
6. **Meaningful messages**: Future you will thank present you

---

## Code Review & Testing

### Pull Request Requirements

| Change Type | PR Required | Reviewers | CI Must Pass |
|-------------|-------------|-----------|--------------|
| New feature | Yes | 1+ (or self-review for solo) | Yes |
| Bug fix | Yes | 1+ (or self-review for solo) | Yes |
| Documentation | Optional | Self-review acceptable | Yes |
| Hotfix | Yes (expedited) | 1+ | Yes |

### PR Workflow

```
Feature Branch                    Main Branch
     │                                │
     ├── Development commits          │
     │                                │
     ├── Push branch                  │
     │                                │
     ├── Create PR ──────────────────►│
     │                                │
     │◄─── Code Review ───────────────│
     │                                │
     ├── Address feedback             │
     │                                │
     ├── CI passes ✓                  │
     │                                │
     └── Merge ──────────────────────►│
                                      │
```

### PR Template

```markdown
## Summary
Brief description of changes.

## Related
- PLAN-NNN (if applicable)
- Fixes #NNN (if applicable)

## Changes
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests (if applicable)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project conventions
- [ ] Documentation updated
- [ ] CHANGELOG updated (for releases)
```

### Testing Requirements

| Change Type | Unit Tests | Integration Tests | Coverage Target |
|-------------|------------|-------------------|-----------------|
| **New feature** | Required | Recommended | 80%+ for new code |
| **Bug fix** | Required (covers bug) | If applicable | Covers fix |
| **Refactor** | Existing must pass | Existing must pass | No regression |
| **Performance** | Benchmarks | Load tests | Baseline comparison |

### Test Categories

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_context_engine.py
│   └── test_validators.py
├── integration/             # Component interaction tests
│   ├── test_review_flow.py
│   └── test_remediation.py
└── e2e/                     # End-to-end scenarios
    └── test_full_audit.py
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ucx --cov-report=term-missing

# Run specific category
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run before commit (quick check)
pytest tests/unit/ -v --tb=short
```

### Coverage Requirements

| Module | Minimum Coverage | Target Coverage |
|--------|------------------|-----------------|
| Core (`ucx/core/`) | 80% | 90% |
| Validators (`ucx/validators/`) | 85% | 95% |
| CLI (`ucx/cli/`) | 70% | 80% |
| Skills (`ucx/skills/`) | 60% | 75% |

---

## CI/CD Integration

### Pre-commit Hooks

UCX uses pre-commit hooks for automated quality checks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ucx-validate
        name: UCX Document Validation
        entry: bash -c 'ucx validate brd docs/01_BRD --tier1-only --no-fix'
        language: system
        files: ^docs/.*\.md$
        stages: [pre-commit]

      - id: pytest-check
        name: Run Unit Tests
        entry: pytest tests/unit/ -v --tb=short
        language: system
        pass_filenames: false
        stages: [pre-commit]

      - id: ruff-check
        name: Ruff Linting
        entry: ruff check ucx/
        language: system
        types: [python]
```

### CI Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, feature/*, fix/*]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run linting
        run: ruff check ucx/

      - name: Run tests
        run: pytest tests/ --cov=ucx --cov-report=xml

      - name: Check coverage
        run: coverage report --fail-under=80

  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate BRD documents
        run: ucx validate brd docs/01_BRD --tier1-only --no-fix
```

### Pipeline Stages

```
Push/PR
   │
   ▼
┌─────────────────┐
│  Lint & Format  │  ← ruff, black, isort
└────────┬────────┘
         │ Pass
         ▼
┌─────────────────┐
│   Unit Tests    │  ← pytest tests/unit/
└────────┬────────┘
         │ Pass
         ▼
┌─────────────────┐
│ Integration     │  ← pytest tests/integration/
│ Tests           │
└────────┬────────┘
         │ Pass
         ▼
┌─────────────────┐
│ Coverage Check  │  ← Minimum 80%
└────────┬────────┘
         │ Pass
         ▼
┌─────────────────┐
│ Doc Validation  │  ← ucx validate
└────────┬────────┘
         │ Pass
         ▼
    ✓ Ready to Merge
```

### Automated Checks

| Check | Tool | Blocking | When |
|-------|------|----------|------|
| Code formatting | black, isort | Yes | Pre-commit, CI |
| Linting | ruff | Yes | Pre-commit, CI |
| Type checking | mypy | No (warnings) | CI |
| Unit tests | pytest | Yes | Pre-commit, CI |
| Integration tests | pytest | Yes | CI |
| Coverage | coverage.py | Yes (80%) | CI |
| Doc validation | ucx validate | Yes | CI |

---

## Feature Development Workflow

### Workflow Overview

```
PLAN → Review → Implement → Test/Code Review → Commit → CI → CHANGELOG → Docs → Approve → Release
  │       │         │              │             │       │        │         │        │        │
  ▼       ▼         ▼              ▼             ▼       ▼        ▼         ▼        ▼        ▼
Create  Validate  Write      AI Agent:       Push    Run      Create   Update   Get     Tag &
 doc    practical  code     - Unit tests   changes  integr.  version  README   sign-   deploy
        approach           - Bug fixes              tests    notes    & docs   off
                           - Comments
                           - Docstrings
```

### Step 1: Create Plan Document

Before implementing a new feature, create a plan in `docs/plans/`:

**Filename Format**: `PLAN-NNN_descriptive_name.md`

**Template**:
```markdown
# PLAN-NNN: Feature Name

## Status
- [ ] Planning
- [ ] Review
- [ ] In Progress
- [ ] Testing
- [ ] Complete

## Summary
Brief description of the feature.

## Problem Statement
What problem does this solve?

## Proposed Solution
How will it be implemented?

## Implementation Details
### Phase 1: ...
### Phase 2: ...

## Testing Strategy
How will it be tested?

## Documentation Updates
What docs need updating?

## Rollout Plan
How will it be released?
```

**Example Plans**:
- `PLAN-001_unified_brd_validation.md`
- `PLAN-002_category_weighted_scoring.md`
- `PLAN-003_persona_prompt_restructuring.md`

### Step 2: Review Plan

Review the plan with focus on **reasonable and practical implementation**:

| Review Criteria | Questions to Ask |
|-----------------|------------------|
| **Feasibility** | Can this be implemented with available resources? |
| **Scope** | Is the scope well-defined and achievable? |
| **Dependencies** | Are all dependencies identified and available? |
| **Complexity** | Is the solution appropriately simple? |
| **Testability** | Can the implementation be thoroughly tested? |
| **Maintainability** | Will the code be maintainable long-term? |

**Review Checklist**:
- [ ] Solution addresses the stated problem
- [ ] Implementation approach is practical
- [ ] No over-engineering or unnecessary complexity
- [ ] Edge cases and error handling considered
- [ ] Resource requirements are reasonable
- [ ] Timeline is realistic

### Step 3: Update Roadmap

Add the feature to `docs/ROADMAP.md`:

1. Add to **Planned Releases** section with target version
2. Add to **Feature Requests** table with status "Planned"
3. Link to the PLAN document

### Step 4: Implement Feature

During implementation:
- Reference the PLAN document in commit messages
- Update PLAN status checkboxes as phases complete
- Keep implementation aligned with plan
- Follow coding standards and conventions

### Step 5: Test/Code Review by AI Agent

AI Agent performs comprehensive quality assurance:

| Task | Description |
|------|-------------|
| **Bug Detection** | Identify and fix all bugs before commit |
| **Unit Tests** | Create/update unit tests for new code (target: 80%+ coverage) |
| **Regression Tests** | Ensure existing functionality not broken |
| **Code Comments** | Update embedded comments in scripts |
| **Docstrings** | Update function/procedure help and documentation |

**AI Agent Review Checklist**:
- [ ] All identified bugs fixed
- [ ] Unit tests written for new functions/classes
- [ ] Regression tests pass
- [ ] Code comments explain non-obvious logic
- [ ] Function docstrings include: purpose, parameters, returns, raises
- [ ] Module-level docstrings updated
- [ ] Type hints added where applicable

**Example Docstring Standard**:
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

### Step 6: Commit

Commit changes following [Commit Strategy](#commit-strategy):
- Atomic commits for logical units
- Conventional commit messages
- Reference PLAN document in commit body

### Step 7: CI (Continuous Integration)

CI pipeline runs automatically on push:

| Stage | Tests | Purpose |
|-------|-------|---------|
| **Lint** | ruff, black | Code quality |
| **Unit** | pytest unit/ | Component correctness |
| **Integration** | pytest integration/ | Component interactions |
| **Coverage** | coverage.py | Minimum 80% threshold |
| **Docs** | ucx validate | Document validation |

**Integration Test Focus**:
- API endpoint interactions
- Database operations
- External service integrations
- Multi-component workflows
- Error propagation across boundaries

### Step 8: Create Changelog

After CI passes, create `docs/CHANGELOG_v{X.Y.Z}.md`:

**Template**:
```markdown
# Changelog v{X.Y.Z}

**Release Date**: YYYY-MM-DD

## Summary
One-line summary of this release.

## New Features
- Feature 1 description
- Feature 2 description

## Bug Fixes
- Fix 1 description

## Breaking Changes
| Change | Migration Path |
|--------|----------------|
| Old behavior | New behavior |

## Implementation Details
Technical details for developers.

## Related Documents
- [PLAN-NNN](plans/PLAN-NNN_feature_name.md)
- [ROADMAP](ROADMAP.md)
```

### Step 9: Update Documentation

Update relevant documentation:
- `README.md` - Add to version history, update feature docs
- Feature-specific docs (e.g., `CONTEXT_ENGINEERING.md`)
- API documentation if applicable
- Update ROADMAP (Planned → Completed)

### Step 10: Approve

Obtain approval before release:

| Approval Type | When Required | Approver |
|---------------|---------------|----------|
| **Self-review** | Solo projects | Developer |
| **Peer review** | Team projects | Team member |
| **Lead approval** | Major features | Tech lead |
| **Stakeholder** | Breaking changes | Product owner |

**Approval Checklist**:
- [ ] All CI checks pass
- [ ] Code review completed
- [ ] Documentation updated
- [ ] CHANGELOG accurate
- [ ] No unresolved issues
- [ ] Ready for production

### Step 11: Release

Execute release:

```bash
# 1. Merge to main
git checkout main
git merge feature/PLAN-NNN-feature-name

# 2. Bump version
echo '__version__ = "X.Y.Z"' > ucx/version.py
git commit -m "chore(ucx): bump version to X.Y.Z"

# 3. Tag release
git tag vX.Y.Z
git push origin main --tags

# 4. Update roadmap
# Mark feature as completed in ROADMAP.md
```

### Workflow Summary Table

| Step | Actor | Output | Gate |
|------|-------|--------|------|
| 1. Plan | Developer | PLAN-NNN.md | - |
| 2. Review | Developer/AI | Approved plan | Practical & feasible |
| 3. Roadmap | Developer | Updated ROADMAP | - |
| 4. Implement | Developer | Source code | Aligned with plan |
| 5. Test/Review | AI Agent | Tests + fixes | Coverage + quality |
| 6. Commit | Developer | Git commits | Atomic + conventional |
| 7. CI | Automation | Pipeline pass | All checks green |
| 8. Changelog | Developer | CHANGELOG.md | Accurate + complete |
| 9. Docs | Developer | Updated docs | Reflects changes |
| 10. Approve | Reviewer | Sign-off | Ready for release |
| 11. Release | Developer | Tagged version | Deployed |

---

## Bug Fix Workflow

### Temporary Documents

Bug fixes use temporary documents in `tmp/` (not version controlled):

```
tmp/
├── fix_duplicate_id_bug.md      # Investigation notes
├── debug_session_2026-03-15.md  # Debug session log
└── hotfix_plan.md               # Quick fix plan
```

### Workflow

1. **Investigate**: Create `tmp/fix_{issue}.md` with investigation notes
2. **Fix**: Implement fix, reference issue in commit
3. **Test**: Verify fix resolves issue
4. **Changelog**: Add to appropriate version changelog
5. **Cleanup**: Delete temporary documents

### When to Use PLAN vs tmp/

| Scenario | Use PLAN | Use tmp/ |
|----------|----------|----------|
| New feature | Yes | No |
| Major refactor | Yes | No |
| Bug fix | No | Yes |
| Investigation | No | Yes |
| Experiment | No | Yes |
| Breaking change | Yes | No |

---

## Hotfix Process

### When to Use Hotfix

Hotfixes are for **critical production issues** that cannot wait for normal release cycle:

| Situation | Use Hotfix? | Notes |
|-----------|-------------|-------|
| Security vulnerability | Yes | Immediate action required |
| Data corruption bug | Yes | User data at risk |
| Complete feature broken | Yes | Core functionality unavailable |
| Minor bug | No | Normal bug fix workflow |
| Performance issue | Depends | Only if severe degradation |
| Missing feature | No | Normal feature workflow |

### Hotfix Workflow

```
Production Issue Detected
         │
         ▼
┌─────────────────────┐
│ 1. Assess Severity  │  ← Is this truly critical?
└──────────┬──────────┘
           │ Critical
           ▼
┌─────────────────────┐
│ 2. Create Branch    │  ← hotfix/issue-description
│    from main        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Fix & Test       │  ← Minimal change, focused fix
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Expedited Review │  ← Shorter review, 1 approval
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Merge & Tag      │  ← Patch version bump
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. Document         │  ← Changelog, post-mortem
└─────────────────────┘
```

### Hotfix Commands

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/security-fix-description

# 2. Make minimal fix
# ... fix the issue ...

# 3. Test thoroughly
pytest tests/ -v

# 4. Commit with clear message
git commit -m "fix(security): patch XSS vulnerability in input handler

CRITICAL: This fixes a security vulnerability that allowed...

Hotfix for v1.18.0"

# 5. Push and create expedited PR
git push -u origin hotfix/security-fix-description
gh pr create --title "HOTFIX: Security patch" --label "hotfix,critical"

# 6. After merge, tag patch release
git checkout main
git pull origin main
git tag v1.18.1
git push origin v1.18.1

# 7. Update changelog
echo "Created hotfix CHANGELOG_v1.18.1.md"
```

### Hotfix Checklist

- [ ] Issue is truly critical (security, data loss, complete breakage)
- [ ] Fix is minimal and focused (no feature additions)
- [ ] Tests cover the specific fix
- [ ] At least one reviewer approved
- [ ] CI passes
- [ ] Patch version bumped
- [ ] Changelog created
- [ ] Post-mortem scheduled (for significant issues)

### Post-Mortem Template

For significant hotfixes, create `tmp/postmortem_YYYY-MM-DD.md`:

```markdown
# Post-Mortem: [Issue Description]

**Date**: YYYY-MM-DD
**Severity**: Critical / High
**Duration**: X hours

## Summary
What happened and what was the impact?

## Timeline
- HH:MM - Issue detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix deployed
- HH:MM - Verified resolved

## Root Cause
Why did this happen?

## Resolution
How was it fixed?

## Prevention
What changes will prevent recurrence?
- [ ] Add test for this scenario
- [ ] Add monitoring/alerting
- [ ] Update documentation
- [ ] Process improvement
```

---

## Versioning Strategy

### Semantic Versioning

UCX follows semantic versioning: `MAJOR.MINOR.PATCH`

| Component | When to Increment | Example |
|-----------|-------------------|---------|
| **MAJOR** | Breaking changes | 1.0.0 → 2.0.0 |
| **MINOR** | New features (backward compatible) | 1.18.0 → 1.19.0 |
| **PATCH** | Bug fixes | 1.18.0 → 1.18.1 |

### Version Lifecycle

```
Planning     →    Development    →    Release    →    Maintenance
   │                   │                 │                │
   ▼                   ▼                 ▼                ▼
ROADMAP.md         PLAN-NNN.md     CHANGELOG.md     Bug fixes
(planned)          (in progress)    (released)       (patches)
```

### Version Timeline in Roadmap

```
v1.12.0 ──► v1.13.x ──► v1.14.x ──► v1.15.x ──► v1.16.x ──► v1.17.0 ──► v1.18.0
   │           │            │            │           │            │           │
   │           │            │            │           │            │           └─► Layer Action Handoff
   │           │            │            │           │            └─► Fixer-to-LLM
   │           │            │            │           └─► Single-file validation
   │           │            │            └─► Extended auto-fix
   │           │            └─► Prompt Inspection
   │           └─► Context Engineering
   └─► Category-Weighted Scoring
```

---

## Rollback Procedures

### When to Rollback

| Situation | Action |
|-----------|--------|
| Critical bug in new release | Rollback to previous version |
| Performance regression | Rollback or hotfix |
| Data integrity issues | Immediate rollback |
| Minor issues | Hotfix preferred over rollback |

### Rollback Decision Tree

```
Issue Detected in v1.18.0
         │
         ▼
    Is it critical?
    /           \
   No            Yes
   │              │
   ▼              ▼
Hotfix       Can we fix quickly?
(normal)     /              \
            Yes              No
            │                │
            ▼                ▼
         Hotfix          ROLLBACK
        v1.18.1         to v1.17.0
```

### Rollback Commands

```bash
# 1. Identify last known good version
git tag --list 'v*' --sort=-version:refname | head -5
# v1.18.0  ← Current (broken)
# v1.17.0  ← Last good
# v1.16.2
# ...

# 2. Create rollback branch
git checkout -b rollback/v1.18.0-to-v1.17.0

# 3. Revert to previous version
git revert --no-commit v1.17.0..v1.18.0

# 4. Or reset to previous tag (more aggressive)
git reset --hard v1.17.0

# 5. Update version file
echo '__version__ = "1.17.1"' > ucx/version.py

# 6. Commit rollback
git commit -m "revert: rollback v1.18.0 to v1.17.0

ROLLBACK: Critical issue in v1.18.0 causing [description].
Reverting to stable v1.17.0 while fix is developed.

Issue: #NNN"

# 7. Push and tag
git push origin rollback/v1.18.0-to-v1.17.0
git tag v1.17.1
git push origin v1.17.1
```

### Rollback Checklist

- [ ] Identified last known good version
- [ ] Confirmed rollback is necessary (not hotfixable)
- [ ] Notified stakeholders
- [ ] Created rollback branch
- [ ] Tested rollback locally
- [ ] Documented what's being reverted
- [ ] Created rollback tag (e.g., v1.17.1)
- [ ] Updated changelog with rollback entry
- [ ] Scheduled fix for rolled-back features

### Rollback Changelog Entry

```markdown
# Changelog v1.17.1

**Release Date**: YYYY-MM-DD

## Summary
ROLLBACK: Reverting v1.18.0 due to critical issue.

## Reason
[Description of the critical issue]

## Reverted Features
- Feature 1 from v1.18.0 (temporarily removed)
- Feature 2 from v1.18.0 (temporarily removed)

## Next Steps
- Fix in progress: PLAN-NNN or Issue #NNN
- Expected re-release: v1.19.0

## Affected Users
[Who is affected and any workarounds]
```

### Post-Rollback Actions

1. **Communicate**: Notify users about the rollback
2. **Investigate**: Determine root cause
3. **Plan Fix**: Create PLAN document for proper fix
4. **Re-test**: Comprehensive testing before re-release
5. **Document**: Add to post-mortem and lessons learned

---

## Documentation Standards

### When to Update Documentation

| Trigger | Action |
|---------|--------|
| New feature released | Update README, create/update feature doc |
| API change | Update API reference |
| Breaking change | Update migration guide |
| Bug fix | Update changelog only |
| Config change | Update configuration docs |

### Documentation Checklist

Before release:
- [ ] CHANGELOG created for version
- [ ] README version history updated
- [ ] Feature documentation created/updated
- [ ] ROADMAP updated (planned → completed)
- [ ] PLAN document marked complete
- [ ] API documentation updated (if applicable)

### Documentation Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `README.md` | Primary reference | Every release |
| `ROADMAP.md` | Planning & tracking | Every release |
| `CHANGELOG_v*.md` | Version history | Per version |
| `docs/plans/PLAN-*.md` | Feature planning | During development |
| Feature docs | Feature details | When feature changes |

---

## Plan Document Lifecycle

### Status Progression

```
[ ] Planning      → Initial design phase
[ ] In Progress   → Active development
[ ] Review        → Code review / testing
[x] Complete      → Released and documented
```

### Plan Document Retention

| Status | Retention |
|--------|-----------|
| Planning | Keep until abandoned or started |
| In Progress | Keep until complete |
| Complete | **Keep permanently** (historical reference) |
| Abandoned | Archive with note explaining why |

### Referencing Plans

In changelogs and commits:
```markdown
See [PLAN-003](plans/PLAN-003_persona_prompt_restructuring.md)
```

In README:
```markdown
| [PLAN-003](docs/plans/PLAN-003_persona_prompt_restructuring.md) | Context engineering |
```

---

## Roadmap Management

### Roadmap Sections

1. **Overview** - Current version and next major
2. **Version Timeline** - Visual ASCII diagram
3. **Planned Releases** - Future versions with features
4. **Completed Releases** - Past versions with summaries
5. **Feature Requests** - Backlog with priorities
6. **References** - Links to plans and changelogs

### Feature Request Table

```markdown
| Request | Priority | Status | Notes |
|---------|----------|--------|-------|
| Multi-Document Validation | High | Planned (v1.19.0) | After action handoff |
| PRD validation parity | Medium | Planned (v1.20.0) | After multi-doc |
| VS Code extension | Low | Future | Post-v2.0.0 |
```

### Priority Definitions

| Priority | Meaning | Timeline |
|----------|---------|----------|
| **High** | Critical for next release | 1-2 versions |
| **Medium** | Important but not blocking | 3-4 versions |
| **Low** | Nice to have | Future/backlog |

---

## Changelog Standards

### Changelog Naming

**Format**: `CHANGELOG_v{MAJOR}.{MINOR}.{PATCH}.md`

**Examples**:
- `CHANGELOG_v1.18.0.md`
- `CHANGELOG_v1.17.0.md`
- `CHANGELOG_v1.16.2.md`

### Changelog Structure

```markdown
# Changelog v1.18.0

**Release Date**: 2026-03-17

## Summary
Layer Action Handoff System for capturing out-of-scope items.

## New Features
- **Layer Action Handoff**: Capture items as ACTIONS instead of findings
- New scripts: `extract_actions.py`, `validate_actions.py`

## Bug Fixes
- BRD scores no longer penalized for downstream layer items

## Breaking Changes
| Change | Migration Path |
|--------|----------------|
| (none) | - |

## Related Documents
- [PLAN-007](plans/PLAN-007_layer_notice_handoff.md)
- [ROADMAP](ROADMAP.md)
```

### Linking Changelogs

In README version history:
```markdown
| 1.18.0 | 2026-03-17 | Layer Action Handoff. See [CHANGELOG_v1.18.0](docs/CHANGELOG_v1.18.0.md) |
```

---

## Deprecation Process

### Deprecation Timeline

```
Version N        Version N+1       Version N+2       Version N+3
    │                │                 │                 │
    ▼                ▼                 ▼                 ▼
Feature          Deprecation        Deprecation        Removal
Active           Warning Added      Warning Persists   (Breaking Change)
                 (still works)      (still works)
```

### Deprecation Policy

| Phase | Version | Action | User Impact |
|-------|---------|--------|-------------|
| **Announce** | N | Add deprecation notice to docs | Awareness |
| **Warn** | N+1 | Add runtime deprecation warning | Warning messages |
| **Persist** | N+2 | Continue warnings, offer migration | Migration time |
| **Remove** | N+3 (MAJOR) | Remove feature | Breaking change |

### Deprecation Notice Template

Add to documentation:

```markdown
> **DEPRECATED** (v1.18.0): `old_function()` is deprecated and will be
> removed in v2.0.0. Use `new_function()` instead.
> See [Migration Guide](docs/MIGRATION.md#old-function).
```

### Runtime Warning

Add to code:

```python
import warnings

def old_function():
    """Deprecated: Use new_function() instead."""
    warnings.warn(
        "old_function() is deprecated and will be removed in v2.0.0. "
        "Use new_function() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... existing implementation ...
```

### Deprecation Changelog Entry

```markdown
## Deprecations

| Deprecated | Replacement | Removal Version |
|------------|-------------|-----------------|
| `old_function()` | `new_function()` | v2.0.0 |
| `--old-flag` | `--new-flag` | v2.0.0 |
```

### Migration Guide Template

Create `docs/MIGRATION_vX.md` for major version upgrades:

```markdown
# Migration Guide: v1.x to v2.0

## Breaking Changes

### 1. `old_function()` Removed

**Before (v1.x)**:
```python
result = old_function(arg1, arg2)
```

**After (v2.0)**:
```python
result = new_function(arg1, arg2, new_required_arg)
```

**Migration Steps**:
1. Replace all calls to `old_function` with `new_function`
2. Add the new required argument
3. Update tests

### 2. CLI Flag Changes

| Old Flag | New Flag | Notes |
|----------|----------|-------|
| `--old-flag` | `--new-flag` | Same behavior |
| `--removed` | (none) | Feature removed |
```

### Deprecation Tracking

Add to ROADMAP.md:

```markdown
## Planned Deprecations

| Feature | Deprecated In | Remove In | Replacement |
|---------|---------------|-----------|-------------|
| `doc-brd-validator` skill | v1.15.0 | v2.0.0 | `doc-brd-audit` |
| `--skip-validation` flag | v1.16.0 | v2.0.0 | `--no-validation` |
| Legacy scoring formula | v1.12.0 | v2.0.0 | Category-weighted |
```

### Deprecation Checklist

- [ ] Deprecation announced in documentation
- [ ] Runtime warning added (if applicable)
- [ ] CHANGELOG entry added
- [ ] ROADMAP updated with deprecation tracking
- [ ] Migration guide created (for major changes)
- [ ] Minimum 2 minor versions before removal
- [ ] Removal only in MAJOR version

---

## Example: Full Feature Lifecycle

### Feature: Context Engineering (v1.13.0)

**Phase 1: Plan**
1. Created `docs/plans/PLAN-003_persona_prompt_restructuring.md`
2. Defined scope, phases, testing strategy

**Phase 2: Review**
1. Reviewed plan for practical implementation
2. Confirmed feasibility and scope
3. Added to ROADMAP.md as "Planned (v1.13.0)"

**Phase 3: Implement**
1. Implemented hierarchical context
2. Implemented prior findings summarization
3. Implemented attention steering
4. Updated PLAN status checkboxes

**Phase 4: Test/Code Review (AI Agent)**
1. AI Agent identified edge case bugs - fixed
2. Unit tests added for new classes (85% coverage)
3. Regression tests verified existing functionality
4. Docstrings added to all new functions
5. Code comments updated for complex logic

**Phase 5: Commit & CI**
1. Atomic commits for each implementation phase
2. CI pipeline: lint ✓, unit tests ✓, integration tests ✓
3. Coverage threshold met (80%+)

**Phase 6: Changelog & Docs**
1. Created `docs/CHANGELOG_v1.13.0.md`
2. Created `docs/CONTEXT_ENGINEERING.md` (feature documentation)
3. Updated README.md version history

**Phase 7: Approve & Release**
1. Code review completed
2. Sign-off obtained
3. Updated ROADMAP.md (planned → completed)
4. Tagged v1.13.0

**Phase 8: Follow-up**
1. v1.13.1 completed deferred features
2. Created `docs/CHANGELOG_v1.13.1.md`
3. Updated `CONTEXT_ENGINEERING.md`
4. Marked PLAN-003 as complete

**Artifacts Created**:
```
docs/
├── plans/PLAN-003_persona_prompt_restructuring.md  # Planning
├── CHANGELOG_v1.13.0.md                            # Release notes
├── CHANGELOG_v1.13.1.md                            # Follow-up release
├── CONTEXT_ENGINEERING.md                          # Feature docs
└── ROADMAP.md                                      # Updated tracking
```

---

## Quick Reference

### Creating a New Feature

```bash
# 1. Create branch and plan
git checkout -b feature/PLAN-008-new-feature
touch docs/plans/PLAN-008_new_feature.md
git add docs/plans/PLAN-008_new_feature.md
git commit -m "docs(ucx): add PLAN-008 for new feature"

# 2. Review plan (validate practical implementation)
# - Check feasibility, scope, dependencies
# - Ensure solution is not over-engineered

# 3. Edit roadmap
# Add to Planned Releases and Feature Requests
git commit -m "docs(ucx): add new feature to ROADMAP"

# 4. Implement feature (commit after each phase)
git commit -m "feat(ucx): implement phase 1 of PLAN-008"
git commit -m "feat(ucx): implement phase 2 of PLAN-008"

# 5. Test/Code Review by AI Agent
# - Fix all bugs identified
# - Add unit tests (80%+ coverage)
# - Run regression tests
# - Update code comments and docstrings
git commit -m "test(ucx): add unit tests for PLAN-008"
git commit -m "docs(ucx): update docstrings and comments"

# 6. Push and run CI (integration tests)
git push -u origin feature/PLAN-008-new-feature
# Wait for CI pipeline to pass

# 7. Create changelog
touch docs/CHANGELOG_v1.19.0.md
git commit -m "docs(ucx): add CHANGELOG_v1.19.0"

# 8. Update docs
git commit -m "docs(ucx): update README and feature docs for v1.19.0"

# 9. Get approval (PR review)
gh pr create --title "feat: PLAN-008 new feature"

# 10. After approval, merge and release
git checkout main
git merge feature/PLAN-008-new-feature
git commit -m "chore(ucx): bump version to 1.19.0"
git tag v1.19.0
git push origin main --tags
```

### Creating a Bug Fix

```bash
# 1. Create branch
git checkout -b fix/issue-123-description

# 2. Investigate (optional temp doc - don't commit)
mkdir -p tmp
touch tmp/fix_bug_description.md  # Local only, in .gitignore

# 3. Fix and test

# 4. Commit fix
git add .
git commit -m "fix(validator): resolve issue with duplicate detection

Detailed explanation of the fix.

Fixes #123"

# 5. Add to changelog
git commit -m "docs(ucx): add fix to CHANGELOG_v1.18.1"

# 6. Cleanup and merge
rm tmp/fix_bug_description.md
git checkout main
git merge fix/issue-123-description
```

### Commit Commands Cheat Sheet

```bash
# Feature commits
git commit -m "feat(scope): add new capability"
git commit -m "feat(scope): implement PLAN-NNN phase N"

# Bug fix commits
git commit -m "fix(scope): resolve issue description"
git commit -m "fix(scope): correct behavior - Fixes #NNN"

# Documentation commits
git commit -m "docs(scope): add/update documentation"
git commit -m "docs(ucx): add CHANGELOG_vX.Y.Z"

# Test commits
git commit -m "test(scope): add unit tests for feature"
git commit -m "test(scope): improve coverage for module"

# Refactor commits
git commit -m "refactor(scope): restructure for clarity"
git commit -m "refactor(scope): extract helper function"

# Chore commits
git commit -m "chore(ucx): bump version to X.Y.Z"
git commit -m "chore(deps): update dependencies"
```

### Release Checklist

**Planning & Review**:
- [ ] PLAN document created
- [ ] Plan reviewed for practical implementation
- [ ] ROADMAP updated with planned feature

**Implementation**:
- [ ] All PLAN phases complete
- [ ] Code follows project conventions

**Test/Code Review (AI Agent)**:
- [ ] All bugs identified and fixed
- [ ] Unit tests written (80%+ coverage for new code)
- [ ] Regression tests pass
- [ ] Code comments updated for non-obvious logic
- [ ] Function docstrings complete (purpose, params, returns, raises)

**CI & Quality**:
- [ ] All commits pushed
- [ ] CI pipeline passes (lint, unit, integration)
- [ ] Integration tests cover component interactions

**Documentation**:
- [ ] CHANGELOG created and committed
- [ ] README version history updated
- [ ] Feature documentation updated
- [ ] ROADMAP updated (planned → completed)
- [ ] PLAN marked complete

**Approval & Release**:
- [ ] Code review completed
- [ ] Approval obtained
- [ ] Version number bumped in `ucx/version.py`
- [ ] Final commit: `chore(ucx): release vX.Y.Z`
- [ ] Branch merged to main
- [ ] Tag created: `git tag vX.Y.Z`

---

## Benefits of This Approach

| Benefit | How It's Achieved |
|---------|-------------------|
| **Traceability** | Every feature linked: PLAN → CHANGELOG → README |
| **Planning** | ROADMAP provides clear priorities and timeline |
| **Practical Focus** | Plan review ensures reasonable implementation |
| **Quality** | AI Agent catches bugs, ensures test coverage |
| **Documentation** | Comments and docstrings updated with code |
| **Integration** | CI runs integration tests automatically |
| **History** | CHANGELOGs preserve detailed version history |
| **Approval Gate** | Explicit approval before release |
| **Maintenance** | Easy to find why/when changes were made |

---

## Related Documents

- [ROADMAP.md](ROADMAP.md) - Master planning document
- [README.md](../README.md) - Primary reference
- [plans/](plans/) - Feature planning documents
- [CHANGELOG_v*.md](.) - Version changelogs

---

*Last Updated: 2026-03-18*
