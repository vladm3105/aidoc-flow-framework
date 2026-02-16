# Release Process

This document defines how to version, tag, and release components in the {PROJECT_NAME} (`{PROJECT_PREFIX}`) project.

## Versioning
All repositories follow **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`

| Change Type | Bump | Example |
|:---|:---|:---|
| Bug fix, docs update | PATCH | `v1.0.0` → `v1.0.1` |
| New feature (backward compatible) | MINOR | `v1.0.1` → `v1.1.0` |
| Breaking change | MAJOR | `v1.1.0` → `v2.0.0` |

## Release Workflow

### 1. Monorepo Release

```
1. Ensure `main` is green (all CI checks pass).
2. Update CHANGELOG.md with release notes.
3. Bump version in relevant component config files (e.g., components/{SERVICE_NAME}/pyproject.toml).
4. Create a Git tag:
   git tag -a v1.0.0 -m "Release v1.0.0: Initial release"
   git push origin v1.0.0
5. GitHub Actions will auto-create a Release from the tag.
```

### 2. Component-Specific Tags (Optional)

For component-only releases, use prefixed tags:

```
git tag -a {SERVICE_NAME}/v1.1.0 -m "{SERVICE_NAME} v1.1.0: Add budget alerts"
git push origin {SERVICE_NAME}/v1.1.0
```

## CHANGELOG Format
Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.1.0] - 2026-03-15
### Added
- Budget alert Cloud Function with configurable thresholds
### Fixed
- BigQuery export timezone handling
```

### AI Contributions
When AI assistants contribute to a release, document them in the CHANGELOG:

```markdown
## [1.2.0] - 2026-03-22
### Added
- MCP server health endpoint (#234) [AI-implemented]
### Fixed
- API timeout handling (#235) [AI-assisted]
```

Use these tags:
- `[AI-implemented]` — Fully implemented by AI, human-reviewed
- `[AI-assisted]` — Human-led with AI assistance

## Release Checklist
- [ ] All tests pass on `main`
- [ ] CHANGELOG.md updated
- [ ] Version bumped in config files
- [ ] Git tag created and pushed
- [ ] GitHub Release created with notes

---

## Phase-Gated Deployment (IPLAN-010)

This project uses **phase-gated deployment** instead of continuous deployment. Releases are grouped by project phases (1-8) and deployed together after QA validation.

### Deployment Model

```
Development → Staging (cumulative) → QA Testing → Production
```

| Stage | Trigger | Environment |
|:------|:--------|:------------|
| Dev (PR) | PR created | Per-PR ephemeral (`pr-N.dev.{PROJECT_PREFIX}.{DOMAIN}`) |
| Staging | Phase complete | `staging.{PROJECT_PREFIX}.{DOMAIN}` |
| Production | Manual + QA pass | `{PROJECT_PREFIX}.{DOMAIN}` |

### Phase Release Process

1. **Phase Development Complete**
   - All development issues with `phase:N` closed
   - All deployment issues created

2. **Staging Deployment**
   - AI Agent reviews deployment issues
   - `deploy-staging.yml` deploys phases 1..N cumulatively
   - All deployment issues closed

3. **QA Testing**
   - `execute-qa-testing.yml` activates QA issues
   - Tests run on staging (06:00-08:00 EST window)
   - Pass: QA issues closed with `ai:qa-passed`
   - Fail: Bug issues created, max 3 iterations

4. **Production Deployment**
   - Requires all 8 phases deployed and QA passed
   - Manual `workflow_dispatch` trigger
   - Gradual rollout: 10% → 50% → 100%
   - Auto-rollback on >1% error rate

### Rollback

Production rollback is handled by `rollback-prod.yml`:
1. Shift traffic to previous revision
2. Verify health checks pass
3. Update tracking file

See [IPLAN-010](./plans/IPLAN-010_ai-first-phase-gated-deployment.md) for full workflow details.
