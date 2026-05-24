## Deployment Issue

**Source**

| Field | Value |
|:------|:------|
| Development Issue | #**DEV_ISSUE** |
| Pull Request | #**PR_NUMBER** |
| Merged | **MERGED_AT** |
| Commits | **COMMITS** |

**Depends on**: #**DEV_ISSUE** (development complete)

---

## Changes Summary

**PR_TITLE**

---

## Deployment Considerations

| Category | Status | Notes |
|:---------|:-------|:------|
| Database Migrations | **MIGRATIONS_NOTE** | Review migrations/ or alembic/ |
| Config Changes | **CONFIG_NOTE** | Review .env, config/, Terraform |
| Infrastructure | **INFRA_NOTE** | Review Dockerfile, Cloud Run config |

---

## Deployment Checklist

- [ ] Review changes summary above
- [ ] Verify all dependent deployments are ready
- [ ] Check for breaking changes
- [ ] Verify rollback procedure exists
- [ ] Add specific deployment notes below if needed

---

*Created automatically from PR #**PR_NUMBER** merge*
