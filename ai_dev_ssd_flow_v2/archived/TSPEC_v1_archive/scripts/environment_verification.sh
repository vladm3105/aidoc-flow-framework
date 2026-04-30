#!/bin/bash
# =============================================================================
# TSPEC Environment Verification
# Verifies directory structure and dependencies before implementation
# =============================================================================

set -e

echo "========================================="
echo "TSPEC Environment Verification"
echo "========================================="
echo "Date: $(date)"
echo ""

# Verify scripts directory exists
echo "--- Checking Scripts Directory ---"
if [ -d "/opt/data/docs_flow_framework/ucx_flow_v3/10_TSPEC/scripts" ]; then
    echo "✅ Scripts directory exists"
    ls -la /opt/data/docs_flow_framework/ucx_flow_v3/10_TSPEC/scripts/ | head -5
else
    echo "❌ Scripts directory missing - creating..."
    mkdir -p /opt/data/docs_flow_framework/ucx_flow_v3/10_TSPEC/scripts
fi
echo ""

# Verify error_codes.py exists
echo "--- Checking Error Code Registry ---"
ERROR_CODES_FILE="/opt/data/docs_flow_framework/ucx_flow_v3/scripts/error_codes.py"
if [ -f "$ERROR_CODES_FILE" ]; then
    echo "✅ Error code registry exists"

    # Check for existing TSPEC codes
    if grep -q "TSPEC-E\|UTEST-E\|ITEST-E" "$ERROR_CODES_FILE"; then
        echo "⚠️  TSPEC error codes already present - review for conflicts"
        grep -E "TSPEC-E|UTEST-E|ITEST-E|STEST-E|FTEST-E|PTEST-E|SECTEST-E" "$ERROR_CODES_FILE" | head -10
    else
        echo "✅ No TSPEC error codes found - safe to add"
    fi
else
    echo "❌ Error code registry missing at $ERROR_CODES_FILE"
    exit 1
fi
echo ""

# Check TSPEC corpus structure
echo "--- Analyzing TSPEC Corpus Structure ---"
for TYPE in UTEST ITEST STEST FTEST PTEST SECTEST; do
    echo "Checking $TYPE:"

    # Check for nested structure
    nested_count=$(find /opt/data/docs_flow_framework/ucx_flow_v3/10_TSPEC/$TYPE -type d -name "${TYPE}-[0-9]*" 2>/dev/null | wc -l)

    # Check for flat structure
    flat_count=$(find /opt/data/docs_flow_framework/ucx_flow_v3/10_TSPEC/$TYPE -maxdepth 1 -type f -name "${TYPE}-[0-9]*.md" 2>/dev/null | wc -l)

    if [ $nested_count -gt 0 ]; then
        echo "  ✅ Nested structure: $nested_count folders"
    fi

    if [ $flat_count -gt 0 ]; then
        echo "  ⚠️  Flat structure: $flat_count files (requires migration)"
    fi

    if [ $nested_count -eq 0 ] && [ $flat_count -eq 0 ]; then
        echo "  ℹ️  No files found"
    fi
done
echo ""

# Verify Python import paths
echo "--- Verifying Python Import Paths ---"
python3 << 'EOF'
from pathlib import Path

script_dir = Path('/opt/data/docs_flow_framework/ucx_flow_v3/10_TSPEC/scripts')
shared_scripts = script_dir.parents[1] / 'scripts'

print(f"Script directory: {script_dir}")
print(f"Shared scripts path: {shared_scripts}")
print(f"Shared scripts exists: {shared_scripts.exists()}")
print(f"error_codes.py exists: {(shared_scripts / 'error_codes.py').exists()}")

if not (shared_scripts / 'error_codes.py').exists():
    print("❌ Import path validation FAILED")
    exit(1)
else:
    print("✅ Import path validation PASSED")
EOF

echo ""
echo "========================================="
echo "Environment Verification Complete"
echo "========================================="
