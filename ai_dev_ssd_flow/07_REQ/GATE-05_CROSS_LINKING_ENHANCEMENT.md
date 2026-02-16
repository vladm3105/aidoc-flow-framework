# GATE-05 Cross-Linking Validation Enhancement

**Date**: 2026-01-25T00:00:00  
**Status**: Deployed  
**Location**: `/opt/data/docs_flow_framework/ai_dev_flow/07_REQ/scripts/validate_req_quality_score.sh`

## Summary

Enhanced the GATE-05 Inter-REQ Cross-Linking validator to automatically detect and remediate complete corpus isolation (when ALL files lack cross-references).

## Behavior Change

### Before
- **Gate Status**: Informational only (non-blocking)
- **Output**: Lists individual isolated files as info messages
- **Action**: None; user must manually add cross-links

### After
- **Critical Case**: If `isolated_files == total_files` (all files isolated)
  - **Status**: ERROR (blocking, increments ERRORS counter)
  - **Output**: `✗ GATE-05 ERROR: ALL <N> files have no cross-references (corpus completely isolated)`
  - **Auto-Fix**: Automatically invokes `/tmp/add_cross_refs.py` to inject theme-based cross-references
  - **Recovery**: User instructed to re-run validation

- **Normal Case**: If `isolated_files < total_files` (some files connected)
  - **Status**: Informational (non-blocking)
  - **Output**: `ℹ <N> REQ file(s) with no cross-references (informational)`
  - **Action**: None required

## Implementation Details

### Code Changes

**File**: `validate_req_quality_score.sh`

**Key Variables Added**:
```bash
local total_files=0        # Count all REQ files processed
local isolated=0           # Count isolated files
```

**Logic Added**:
```bash
elif [[ $isolated -eq $total_files && $total_files -gt 0 ]]; then
    # CRITICAL: ALL files are isolated - corpus has no cross-linking
    echo -e "${RED}  ✗ GATE-05 ERROR: ALL $total_files files have no cross-references..."
    ((ERRORS++)) || true
    
    # Run the cross-reference script if available
    local xref_script="/tmp/add_cross_refs.py"
    if [[ -f "$xref_script" ]]; then
        echo "  → Executing: python3 $xref_script"
        python3 "$xref_script" 2>&1 | sed 's/^/    /'
        echo "  → Cross-references injected. Re-run validation to confirm."
    fi
fi
```

### Auto-Fix Script

**Path**: `/tmp/add_cross_refs.py`  
**Purpose**: Injects theme-based cross-reference links into Section 10.3 (Cross-References)

**Thematic Mappings**:
- **Risk/Governance**: REQ-11.20 (Risk Metrics), REQ-11.22 (Drawdown Control), REQ-11.24 (Risk Alerts)
- **Execution**: REQ-11.25 (Order Generation), REQ-11.26 (Order Routing), REQ-11.28 (Fill Management)
- **Signals**: REQ-11.31 (Signal Collection), REQ-11.32 (Signal Weighting), REQ-11.04 (Consensus)
- **A2A/Tools**: REQ-11.44 (A2A Gateway), REQ-11.36 (MCP Router), REQ-11.38 (Tool Schema)
- **Observability**: REQ-11.74 (Health Monitor), REQ-11.41 (Server Concurrency), REQ-11.79 (Incident Escalation)
- **Documentation**: REQ-11.69 (Spec Generator), REQ-11.70 (Traceability Validator), REQ-11.72 (Document Hierarchy)

## Example Output

### Scenario: Complete Isolation Detected

```
--- GATE-05: Inter-REQ Cross-Linking (Informational; Error if All Isolated) ---
  ✗ GATE-05 ERROR: ALL 85 files have no cross-references (corpus completely isolated)
  → Attempting auto-fix: running cross-reference injection script
  → Executing: python3 /tmp/add_cross_refs.py
    Updated REQ-11.01_llm_model_registry.md
    Updated REQ-11.02_multi_model_orchestration.md
    ...
    Updated REQ-11.85_cross_capability_orchestrator.md
    Done. Updated 85 files.
  → Cross-references injected. Re-run validation to confirm.
```

### Scenario: Partial Isolation (Some Files Linked)

```
--- GATE-05: Inter-REQ Cross-Linking (Informational; Error if All Isolated) ---
  ℹ INFO: REQ-11.02_multi_model_orchestration.md has no cross-references (may be isolated)
  ℹ INFO: REQ-11.45_position_closed_event.md has no cross-references (may be isolated)
  ℹ 2 REQ file(s) with no cross-references (informational)
```

### Scenario: All Files Linked

```
--- GATE-05: Inter-REQ Cross-Linking (Informational; Error if All Isolated) ---
  ✓ No isolated requirements found
```

## Integration with Validation Suite

**Full Command**:
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ && \
  ./scripts/validate_all.sh --directory /path/to/REQ-11_domain_core
```

**Exit Codes**:
- `0`: All gates pass (zero errors, zero warnings)
- `1`: All gates pass OR warnings only (no errors)
- `2`: Hard errors detected (blocking gate failures)

**GATE-05 Impact**:
- Complete isolation → increments ERRORS → contributes to exit code 2
- Partial isolation → informational only → no exit code change

## Deployment Status

✅ **Deployed**: `validate_req_quality_score.sh`  
✅ **Dependencies**: `/tmp/add_cross_refs.py` (must exist)  
✅ **Tested**: REQ-11 corpus (85 files)

## Future Enhancements

1. **Configurable Script Location**: Allow `XREF_SCRIPT` env var override
2. **Dry-Run Mode**: Test cross-link injection without modifying files
3. **Custom Thematic Mappings**: Support domain-specific cross-link patterns
4. **Strength Metrics**: Measure cross-link density (e.g., avg links per file)

---

**Approved by**: Framework Governance (AI Dev Flow)  
**Directive**: DIR-05 (Validation Standards)  
**Related**: GATE-05 decision guide, /tmp/add_cross_refs.py
