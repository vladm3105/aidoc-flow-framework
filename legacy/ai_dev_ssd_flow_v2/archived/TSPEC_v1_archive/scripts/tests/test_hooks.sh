#!/bin/bash
# =============================================================================
# Test script for TSPEC hooks
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"
HOOKS_DIR="$SCRIPT_DIR/.."

echo "========================================="
echo "TSPEC Hooks Test Suite"
echo "========================================="
echo ""

# Test 1: Valid TSPEC files (should pass)
echo "Test 1: Valid TSPEC files"
if bash "$HOOKS_DIR/tspec_core_validator_hook.sh" "$FIXTURES_DIR/valid"; then
    echo "✅ Test 1 PASSED"
else
    echo "❌ Test 1 FAILED"
    exit 1
fi
echo ""

# Test 2: Invalid TSPEC files (should fail)
echo "Test 2: Invalid TSPEC files (below threshold)"
if bash "$HOOKS_DIR/tspec_tasks_ready_hook.sh" "$FIXTURES_DIR/invalid"; then
    echo "❌ Test 2 FAILED (should have failed but passed)"
    exit 1
else
    echo "✅ Test 2 PASSED (correctly failed)"
fi
echo ""

# Test 3: Edge cases (reserved IDs and reports should be skipped)
echo "Test 3: Edge cases (reserved IDs, reports)"
if bash "$HOOKS_DIR/tspec_core_validator_hook.sh" "$FIXTURES_DIR/edge_cases"; then
    echo "✅ Test 3 PASSED (files correctly skipped)"
else
    echo "❌ Test 3 FAILED"
    exit 1
fi
echo ""

# Test 4: Score format detection (3 formats)
echo "Test 4: Score format detection"
# Create temp fixtures with different formats
TMP_DIR=$(mktemp -d)
mkdir -p "$TMP_DIR/UTEST/UTEST-90_fmt1" "$TMP_DIR/UTEST/UTEST-91_fmt2" "$TMP_DIR/UTEST/UTEST-92_fmt3"

# Format 1: 95%
cat > "$TMP_DIR/UTEST/UTEST-90_fmt1/UTEST-90_fmt1.md" << 'EOF'
# UTEST-90
TASKS-Ready Score: 95%
EOF

# Format 2: 95/100
cat > "$TMP_DIR/UTEST/UTEST-91_fmt2/UTEST-91_fmt2.md" << 'EOF'
# UTEST-91
TASKS-Ready Score: 95/100
EOF

# Format 3: [95]
cat > "$TMP_DIR/UTEST/UTEST-92_fmt3/UTEST-92_fmt3.md" << 'EOF'
# UTEST-92
TASKS-Ready Score [95]
EOF

if bash "$HOOKS_DIR/tspec_tasks_ready_hook.sh" "$TMP_DIR"; then
    echo "✅ Test 4 PASSED (all 3 formats detected)"
else
    echo "❌ Test 4 FAILED (score format detection issue)"
    rm -rf "$TMP_DIR"
    exit 1
fi
rm -rf "$TMP_DIR"
echo ""

echo "========================================="
echo "All Tests PASSED"
echo "========================================="
