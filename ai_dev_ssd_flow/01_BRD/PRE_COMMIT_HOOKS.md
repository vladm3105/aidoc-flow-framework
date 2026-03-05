# BRD Pre-Commit Hooks

## Status: ✅ ACTIVE (as of 2026-03-05)

### Configuration

**Hooks**: 3 BRD validation hooks
1. `brd-core-wrapper` - Structural validation (19 sections)
2. `brd-standardized-element-codes` - Element type codes
3. `brd-legacy-patterns` - Legacy pattern detection

**Config File**: `ai_dev_ssd_flow/scripts/pre_commit_hooks/library/pre-commit-config.project.yaml`

**Status**: `stages: [pre-commit]` (active)

### History

| Date | Event | Reason |
|------|-------|--------|
| 2026-02-25 | Hooks disabled (`stages: [manual]`) | "Temporarily set to manual" |
| 2026-03-05 | Hooks re-enabled (`stages: [pre-commit]`) | IPLAN-001 Phase -1B.1 |

### Emergency Disable

**⚠️ WARNING**: Disabling hooks bypasses BRD validation. Only use for emergencies.

See IPLAN-001 Section 10.1.1 for emergency disable procedure.

### Monitoring

**Check hook status**:
```bash
grep "stages:" ai_dev_ssd_flow/scripts/pre_commit_hooks/library/pre-commit-config.project.yaml | grep "brd-"

# Expected: All 3 BRD hooks show stages: [pre-commit]
```

### Troubleshooting

**Hooks not running**:
1. Check symlink: `ls -la /opt/data/b-local/b-local-docs/.pre-commit-config.yaml`
2. Verify target: `readlink /opt/data/b-local/b-local-docs/.pre-commit-config.yaml`
3. Check stages: `grep "id: brd-core-wrapper" -A 5 <config-file> | grep stages`

**Hooks blocking commits**:
1. Run validator directly: `python3 ai_dev_ssd_flow/01_BRD/scripts/validate_brd.py <brd-file>`
2. Fix validation errors
3. Commit again

### References

- IPLAN-001 v1.2.2: `/opt/data/b-local/b-local-docs/work_plans/IPLAN-001_brd_audit_remediation_v1.2.md`
- Root Cause Addendum: `/opt/data/docs_flow_framework/work_plans/BRD_FRAMEWORK_ROOT_CAUSE_ADDENDUM.md`
- Validation Rules: `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md`
