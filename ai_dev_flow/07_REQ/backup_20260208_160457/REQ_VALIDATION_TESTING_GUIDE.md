# REQ Validation Testing Guide

**Location**: `/opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts/`  
**Date**: 2026-01-25

## Overview

The REQ validation suite includes automated test coverage for critical gates, including GATE-05 (Inter-REQ Cross-Linking isolation detection).

## Test Scripts

### test_gate05_isolation.sh

**Purpose**: Verify GATE-05 correctly detects when ALL requirements in a corpus lack cross-references and triggers auto-remediation.

**Location**: `scripts/test_gate05_isolation.sh`

**What It Does**:
1. Creates an isolated test corpus (10 REQ files with zero cross-links)
2. Runs the quality gate validator against it
3. Verifies GATE-05 raises an ERROR (not just informational)
4. Confirms auto-fix script is invoked
5. Cleans up temporary test files

**Exit Codes**:
- `0`: Test passed (error detection works, auto-fix triggered)
- `1`: Test failed (isolation not detected or auto-fix failed)

**Usage**:

Via `validate_all.sh`:
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ
./scripts/validate_all.sh --test-gate05
```

Directly:
```bash
bash /opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts/test_gate05_isolation.sh
```

**Expected Output**:
```
============================================
GATE-05 TEST: Complete Isolation Detection
============================================

1. Creating test corpus (10 isolated REQ files, no cross-links)...
  Created REQ-X.01.md
  ...
  Created REQ-X.10.md

2. Running validation on isolated corpus (should trigger GATE-05 ERROR)...

--- GATE-05: Inter-REQ Cross-Linking (Informational; Error if All Isolated) ---
  ✗ GATE-05 ERROR: ALL 10 files have no cross-references (corpus completely isolated)
  → Attempting auto-fix: running cross-reference injection script
  → Executing: python3 /tmp/add_cross_refs.py
    Updated REQ-X.01.md
    ...
    Done. Updated 10 files.
  → Cross-references injected. Re-run validation to confirm.

3. Testing EXIT CODE logic...
  Exit code: 2
  (Expected: 2 = ERROR, 1 = WARNING-only, 0 = PASS)
  ✅ GATE-05 ERROR detected correctly

4. Cleanup...

✅ TEST COMPLETE
```

## Integration with validate_all.sh

The main validation driver has been updated to support the test mode:

**Options**:
```bash
./scripts/validate_all.sh --test-gate05
```

**Behavior**:
- Runs only the GATE-05 isolation detection test
- Creates temporary isolated corpus
- Exits with 0 (pass) or 1 (fail)
- Does not perform normal REQ validation

## Running Tests

### Quick Test
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ
./scripts/validate_all.sh --test-gate05
```

### Full Validation Suite (Including Test)
```bash
# Normal corpus validation
./scripts/validate_all.sh --directory /path/to/REQ-11_domain_core

# Then run test separately
./scripts/validate_all.sh --test-gate05
```

### CI/CD Integration
```bash
# Include in automated test pipeline
#!/bin/bash
set -e
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ
./scripts/validate_all.sh --test-gate05
echo "✅ GATE-05 test passed"
```

## Test Coverage

| Test | Validates | Gate | Status |
|------|-----------|------|--------|
| test_gate05_isolation.sh | Complete corpus isolation detection | GATE-05 | ✅ Deployed |
| Error counter increment | ERRORS variable incremented | GATE-05 | ✅ Tested |
| Auto-fix invocation | Cross-ref script called | GATE-05 | ✅ Tested |
| Exit code semantics | Error = exit 2 | Validation Suite | ✅ Tested |

## Troubleshooting

### Test fails with "GATE-05 ERROR not detected"

**Cause**: GATE-05 logic not incrementing isolated files count  
**Solution**: Verify `/opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts/validate_req_quality_score.sh` has the updated check:
```bash
elif [[ $isolated -eq $total_files && $total_files -gt 0 ]]; then
    # CRITICAL: ALL files are isolated
    ((ERRORS++)) || true
fi
```

### Auto-fix script not found

**Cause**: `/tmp/add_cross_refs.py` doesn't exist  
**Solution**: Ensure the cross-reference script is available:
```bash
ls -l /tmp/add_cross_refs.py
```

If missing, recreate it (see GATE-05 Enhancement docs)

### Exit codes wrong

**Cause**: validate_req_quality_score.sh not returning correct exit code  
**Solution**: Check the main validator returns exit code based on ERRORS counter:
```bash
if [[ $ERRORS -gt 0 ]]; then
    exit 2
elif [[ $WARNINGS -gt 0 ]]; then
    exit 1
else
    exit 0
fi
```

## Maintenance

- Keep test corpus small (10 files) for fast execution
- Verify auto-fix script path matches deployment location
- Review test output regularly for regression
- Update test cases when GATE-05 logic changes

---

**Related Documentation**:
- [GATE-05 Enhancement](GATE-05_CROSS_LINKING_ENHANCEMENT.md)
- [Validation Quality Score](validate_req_quality_score.sh)
- [REQ Validation Suite](README.md)
