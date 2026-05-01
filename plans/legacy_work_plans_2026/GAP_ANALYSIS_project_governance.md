# Gap Analysis: project_governance Genericization Plan

**Date**: 2026-02-16
**Plan Under Review**: `PLAN_project_governance_genericization.md`

---

## Executive Summary

The current plan has **12 significant gaps** that need to be addressed before implementation. The plan correctly identifies the core strategy but underestimates scope and misses several critical elements.

| Category | Gap Count | Severity |
|----------|-----------|----------|
| Missing Files | 1 | HIGH |
| Missing Placeholders | 8 | HIGH |
| Scope Underestimation | 1 | MEDIUM |
| Cross-Reference Issues | 1 | MEDIUM |
| Structural Gaps | 1 | LOW |

---

## GAP 1: Missing File - GITHUB_PROJECT_SETUP.md

**Severity**: HIGH

**Issue**: The plan lists 16 files to modify but misses `GITHUB_PROJECT_SETUP.md` (the non-AI-FIRST version).

**Current State**:
- File exists at `/opt/data/ucx_framework/project_governance/GITHUB_PROJECT_SETUP.md`
- File is marked **DEPRECATED** with redirect to AI_FIRST version
- Contains 7.5KB of project-specific content

**Resolution Options**:
1. **DELETE** - Remove deprecated file entirely (recommended)
2. **KEEP** - Add to "Files to Delete" section in plan

**Recommendation**: Add to "Files to Delete" list since it's deprecated and duplicates AI_FIRST content.

---

## GAP 2: Missing Placeholder - GitHub Secret Names

**Severity**: HIGH

**Issue**: Plan lists only 15 placeholder variables but 25+ secret names are hardcoded throughout.

**Missing Secrets Found**:
```
ANTHROPIC_API_KEY
ELEVATED_PAT
PROJECT_TOKEN
GCP_ACCESS_TOKEN
GCP_PROJECT_ID
GCP_SA_KEY
GCP_SERVICE_ACCOUNT
GCP_WORKLOAD_IDENTITY_PROVIDER
WIF_PROVIDER
WIF_SA_EMAIL
WIF_SA_EMAIL_DEV
WIF_SA_EMAIL_STAGING
WIF_SA_EMAIL_PROD
WIF_CREDENTIALS_DEV
WIF_CREDENTIALS_STAGING
WIF_CREDENTIALS_PROD
```

**Resolution**: Add new placeholder category `{SECRET_*}` or document these as "standard secret names" that don't need replacement.

---

## GAP 3: Missing Placeholder - Label Names

**Severity**: HIGH

**Issue**: Plan mentions labels but doesn't provide placeholders for label taxonomy.

**Labels Found (30+ unique)**:
```
AI Labels:       ai:ready, ai:in-progress, ai:review-passed, ai:review-failed,
                 ai:deployment, ai:development, ai:qa-testing, ai:blocked,
                 ai:human-required, ai:approved, ai:rejected

Phase Labels:    phase:1 through phase:8

Component:       component:agents, component:mcp, component:monitoring,
                 component:ui, component:auth, component:data, component:sdk

Cloud:           cloud:gcp, cloud:aws, cloud:azure

Iteration:       iteration:1, iteration:2, iteration:3

Special:         skip-ai-review
```

**Resolution Options**:
1. Keep labels as-is (they're generic enough)
2. Add `{LABEL_PREFIX}` placeholder for `ai:` → `{LABEL_PREFIX}:`

**Recommendation**: Keep AI/phase/component labels as standard framework labels. Only replace project-specific prefixes if any exist.

---

## GAP 4: Missing Placeholder - Issue Numbers

**Severity**: MEDIUM

**Issue**: Dozens of hardcoded issue numbers throughout documentation.

**Examples Found**:
- Project board: `#31`
- Epics: `#11` through `#18`
- Sprint 0 tasks: `#6` through `#10`
- Phase 1 tasks: `#19` through `#32`
- Example issues: `#100`, `#123`, `#200`

**Resolution**:
1. Replace specific numbers with `#{EXAMPLE_ISSUE}` or `#{N}`
2. Remove all issue number references (they're project-specific)

**Recommendation**: Remove all specific issue numbers or convert to generic examples like `#N`, `#EPIC_N`.

---

## GAP 5: Missing Placeholder - WIF Pool/Provider Names

**Severity**: HIGH

**Issue**: GCP Workload Identity Federation configuration has hardcoded names.

**Found Values**:
- Pool name: `github-actions-pool`
- Provider name: `ghes-provider`
- Service account: `aiocto-ai-reviewer`
- Service account: `aiocto-deployer`

**Resolution**: Add placeholders:
- `{WIF_POOL_NAME}` → default `github-actions-pool`
- `{WIF_PROVIDER_NAME}` → default `github-provider`
- `{SA_AI_REVIEWER}` → `{PROJECT_PREFIX}-ai-reviewer`
- `{SA_DEPLOYER}` → `{PROJECT_PREFIX}-deployer`

---

## GAP 6: Missing Placeholder - Sprint/Iteration Names

**Severity**: MEDIUM

**Issue**: Sprint naming patterns are hardcoded.

**Found Patterns**:
- `Sprint 0` (research/planning)
- `Sprint 1.1`, `Sprint 1.2` (phase.iteration format)
- `Sprint 2.1`, `Sprint 2.2`, etc.
- Milestone names: `AIOCTO - Phase 1`, `AIOCTO - Sprint 0`

**Resolution**: Add placeholder:
- `{SPRINT_PREFIX}` → default empty or project prefix
- Document sprint naming convention as configurable

---

## GAP 7: Missing Placeholder - Dates and Timeline

**Severity**: MEDIUM

**Issue**: 50+ hardcoded dates throughout documentation.

**Found Date Patterns**:
- Sprint dates: `Feb 17, 2026` through `Jul 18, 2026`
- Document versions: `2026-02-13`, `2026-02-14`, `2026-02-15`
- Release examples: `2026-03-15`, `2026-03-22`

**Resolution**:
1. Convert absolute dates to relative: `Week 1`, `Week 2`, etc.
2. Remove version history dates (they're metadata)
3. Use `{START_DATE}` + offset for milestones

---

## GAP 8: Scope Underestimation - Reference Count

**Severity**: MEDIUM

**Issue**: Plan estimates "800+ string substitutions" but actual count is higher.

**Actual Counts**:
```
grep -c results:
- "techtrend"        : 180+ occurrences
- "aiocto"           : 200+ occurrences
- "USDA"             : 150+ occurrences
- "AI-Cloud-Cost"    : 80+ occurrences
- "gcp-cost-guard"   : 30+ occurrences
- Total unique refs  : 644 lines with matches
- Estimated total    : 1000-1200 substitutions
```

**Resolution**: Update estimate to ~1200 substitutions. Consider scripted approach for bulk replacement.

---

## GAP 9: Missing - Deprecated File Handling Strategy

**Severity**: MEDIUM

**Issue**: Plan doesn't address deprecated files beyond deletion.

**Deprecated Files Found**:
1. `GITHUB_PROJECT_SETUP.md` - marked deprecated
2. `AI_PR_Review/GCP_SETUP.md` - marked deprecated (per IPLAN-006)

**Missing from Plan**:
- What to do with cross-references to deprecated files
- Whether to keep deprecation notices in remaining files
- Migration guidance for users of old patterns

**Resolution**: Add "Deprecated File Strategy" section:
1. Delete deprecated files
2. Update all references to point to replacement files
3. Remove deprecation notices from replacement files

---

## GAP 10: Missing - Cross-Reference Validation

**Severity**: MEDIUM

**Issue**: Plan mentions "ensure no broken internal links" but doesn't detail the approach.

**Cross-Reference Types Found**:
- Internal markdown links: `[text](./FILE.md)`
- Anchor links: `[text](#section-name)`
- Relative paths: `../governance/FILE.md`
- References from deleted IPLAN files

**Risk**: After placeholder substitution and file deletion, many links will break.

**Resolution**: Add verification step:
```bash
# Check for broken internal links
grep -roh '\[.*\](\.\/[^)]*\.md)' project_governance/ | \
  while read link; do
    # validate each link exists
  done
```

---

## GAP 11: Missing - URL Placeholders Beyond GHES

**Severity**: LOW

**Issue**: Plan only addresses `github.techtrend.us` but other URLs exist.

**Additional URLs Found**:
- `https://console.anthropic.com/` - Anthropic console
- `https://console.cloud.google.com/billing` - GCP console
- `https://github.com/...` - Public GitHub repos (keep as-is)
- `https://aiocto-cost-guard-staging.run.app` - Cloud Run URL

**Resolution**:
- Keep public URLs (github.com, anthropic.com, etc.)
- Add `{CLOUD_RUN_URL}` placeholder for deployment URLs
- Document which URLs should be replaced vs kept

---

## GAP 12: Missing - Relationship to ai_dev_flow

**Severity**: LOW (Documentation Gap)

**Issue**: No documentation on how `project_governance` relates to `ai_dev_flow` (SDD methodology).

**Current State**:
- `ai_dev_flow/` - Comprehensive 12-layer SDD methodology
- `project_governance/` - Lightweight AI-first approach for small projects
- No cross-references between them

**Resolution**: Add to README.md:
```markdown
## Relationship to SDD Methodology

This framework is a **lightweight alternative** to the full SDD methodology
(`ai_dev_flow/`). Use this for:
- Small projects (1-6 months)
- Teams familiar with agile/sprint workflow
- Projects not requiring comprehensive documentation

For larger projects requiring formal requirements traceability,
use the full SDD methodology instead.
```

---

## Updated File Counts

### Files to Delete (Updated)
| File | Reason |
|------|--------|
| `GITHUB_PROJECT_SETUP.md` | **NEW** - Deprecated, redirect exists |
| `AI_PR_Review/GCP_SETUP.md` | **NEW** - Deprecated per IPLAN-006 |
| `plans/IPLAN-001` through `IPLAN-011` | Project-specific examples |
| `cicd/phase-deployments.json` | Project-specific configuration |

**Total**: 14 files (was 12)

### Files to Modify (Updated)
| File | Changes |
|------|---------|
| All 16 originally listed | Per original plan |
| `AI_PR_Review/ONBOARDING.md` | **NEW** - Heavy project refs |
| `AI_PR_Review/LOCAL_SETUP.md` | **NEW** - Links to deprecated GCP_SETUP |

**Total**: 18 files (was 16)

---

## Updated Placeholder Variables

### Required (Core)
| Variable | Description | Current Value |
|----------|-------------|---------------|
| `{PROJECT_PREFIX}` | Short identifier | `aiocto` |
| `{PROJECT_NAME}` | Full name | `AI Ops Monitoring - Cost Module` |
| `{REPO_NAME}` | Repository name | `AI-Cloud-Cost-Monitoring` |
| `{GITHUB_ORG}` | Organization | `USDA-AI-Innovation-Hub` |
| `{GITHUB_HOST}` | GitHub hostname | `github.techtrend.us` |
| `{PROJECT_BOARD_NUMBER}` | Board number | `31` |

### Required (Cloud - GCP)
| Variable | Description | Current Value |
|----------|-------------|---------------|
| `{GCP_PROJECT_DEV}` | Dev project | `aiocto-dev` |
| `{GCP_PROJECT_STAGING}` | Staging project | `aiocto-staging` |
| `{GCP_PROJECT_PROD}` | Prod project | `aiocto-prod` |
| `{WIF_POOL_NAME}` | **NEW** WIF pool | `github-actions-pool` |
| `{WIF_PROVIDER_NAME}` | **NEW** WIF provider | `ghes-provider` |

### Required (Infrastructure)
| Variable | Description | Current Value |
|----------|-------------|---------------|
| `{CLOUD_RUN_URL}` | **NEW** Deployment URL | `aiocto-cost-guard-staging.run.app` |
| `{ARTIFACT_REGISTRY}` | **NEW** Docker registry | `us-east4-docker.pkg.dev/{PROJECT}` |

### Optional (Timeline)
| Variable | Description | Default |
|----------|-------------|---------|
| `{PHASE_COUNT}` | Number of phases | `8` |
| `{START_DATE}` | **NEW** Project start | `YYYY-MM-DD` |
| `{SPRINT_DURATION}` | **NEW** Sprint length | `2 weeks` |

**Total Variables**: 20 (was 15)

---

## Recommended Plan Updates

### 1. Add to "Files to Delete"
```markdown
| `GITHUB_PROJECT_SETUP.md` | Deprecated, uses AI_FIRST version |
| `AI_PR_Review/GCP_SETUP.md` | Deprecated per IPLAN-006 |
```

### 2. Add to "Files to Modify"
```markdown
| `AI_PR_Review/ONBOARDING.md` | 40+ replacements | Medium |
| `AI_PR_Review/LOCAL_SETUP.md` | 20+ replacements, fix deprecated links | Medium |
```

### 3. Add New Section - "Standard Labels (Keep As-Is)"
```markdown
## Standard Labels (No Replacement Needed)

These labels are part of the framework standard and should be kept:
- `ai:*` labels (ready, in-progress, review-passed, etc.)
- `phase:*` labels (1-N based on PHASE_COUNT)
- `component:*` labels (project-specific, but pattern is standard)
- `cloud:*` labels (gcp, aws, azure)
- `iteration:*` labels (1, 2, 3)
```

### 4. Add New Section - "Verification Script"
```markdown
## Verification Script

After all replacements, run:
\`\`\`bash
# Check for remaining project-specific strings
grep -r "aiocto\|USDA\|techtrend\|AI-Cloud-Cost\|gcp-cost-guard" \
  project_governance/ --include="*.md"

# Check for broken internal links
find project_governance/ -name "*.md" -exec grep -l '\[.*\](\./' {} \; | \
  xargs -I {} sh -c 'echo "Checking {}"; grep -oh "\[.*\](\./[^)]*)" {}'
\`\`\`
```

### 5. Update Estimated Scope
```markdown
## Estimated Scope (Revised)

- **Files to modify**: 18 markdown files (was 16)
- **Files to delete**: 14 files (was 12)
- **Files to create**: 5 new framework files
- **Total replacements**: ~1200 string substitutions (was 800+)
- **Placeholder variables**: 20 (was 15)
```

---

## Conclusion

The original plan provides a solid foundation but needs these updates:
1. Add 2 deprecated files to delete list
2. Add 2 files to modify list
3. Add 5 new placeholder variables
4. Update replacement count estimate
5. Add verification script section
6. Add standard labels documentation
7. Document relationship to ai_dev_flow

After these updates, the plan will be comprehensive and ready for implementation.
