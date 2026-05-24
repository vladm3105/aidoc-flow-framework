# Repository Structure Decision Matrix

**Decision**: Migrate from Polyrepo (Git Submodules) to Monorepo (`components/` directory)

**Date**: {DATE}

---

## Decision Criteria

| Criterion | Polyrepo (Submodules) | Monorepo (components/) | Winner |
|:----------|:----------------------|:-----------------------|:-------|
| AI agent context | Dual git state, agents confused by nested repos | Single git context, all files accessible | **Monorepo** |
| PR workflow | 2 PRs per cross-component feature | 1 PR for atomic changes | **Monorepo** |
| Commit ceremony | Commit child → push → commit parent → push | Single commit, single push | **Monorepo** |
| Code review | Split reviews across repos | Unified review of related changes | **Monorepo** |
| Refactoring | Manual coordination across repos | IDE-assisted, atomic refactors | **Monorepo** |
| Dependency management | Version pinning via submodule refs | Direct imports, no version drift | **Monorepo** |
| Independent deployment | Native support | Requires path-based CI triggers | Polyrepo |
| Team isolation | Strong boundaries | Requires CODEOWNERS discipline | Polyrepo |
| Repo size | Small repos, fast clones | Larger repo over time | Polyrepo |

**Result**: 6-3 in favor of Monorepo

---

## Context: Why This Matters Now

### Team Size

- **Current**: 1-2 developers (AI-assisted)
- **Impact**: No cross-team coordination benefits from polyrepo; submodule overhead is pure cost

### Development Pattern

- **Current**: AI agents drive majority of code changes via {AI_TOOL_NAME} Code, Gemini CLI
- **Impact**: AI agents work best with single git context; submodules cause "which repo am I in?" confusion

### Component Coupling

- **Current**: {SERVICE_NAME} closely coupled to home repo governance and infra docs
- **Impact**: Most changes span home + component repo anyway

---

## Specific Pain Points (Observed)

| Pain Point | Frequency | Severity |
|:-----------|:----------|:---------|
| AI agent commits to wrong repo | Weekly | High |
| Two-PR ceremony for single feature | Every feature | Medium |
| Submodule pointer drift (forgot to update parent) | Bi-weekly | Medium |
| "Detached HEAD" confusion in submodule | Monthly | Low |
| CI runs twice (parent + child) for same change | Every feature | Low |

---

## Migration Path

1. **Import** existing submodule with full history into `components/{SERVICE_NAME}/`
2. **Remove** `.gitmodules` and `modules/` directory
3. **Relocate** `prod_mcp-servers/` to `components/mcp-servers/`
4. **Update** all documentation references (25+ files)
5. **Archive** original component repo (read-only, do not delete)

See: [Implementation Plans](plans/) for migration details.

---

## Reversibility

**Low risk**: If monorepo causes issues, components can be extracted back to separate repos using `git filter-repo`. History is preserved in both directions.

---

## References

- [REPOSITORY_STRATEGY.md](REPOSITORY_STRATEGY.md) — Updated strategy document
- [Implementation Plans](plans/) — Detailed migration and other plans
