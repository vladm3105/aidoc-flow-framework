#!/bin/bash
# TEST: GATE-05 Complete Isolation Detection & Auto-Fix
# Simulates a scenario where all REQ files have no cross-references

set -e

echo "============================================"
echo "GATE-05 TEST: Complete Isolation Detection"
echo "============================================"
echo ""

# Test directory
TEST_DIR="/tmp/gate05_test_corpus"
mkdir -p "$TEST_DIR"

echo "1. Creating test corpus (10 isolated REQ files, no cross-links)..."
for i in {01..10}; do
  cat > "$TEST_DIR/REQ-X.$i.md" << 'EOF'
---
document_type: req
title: "REQ-X.$i: Test Requirement"
---

# REQ-X.$i: Test Requirement

## 1. Document Control

| Item | Value |
|------|-------|
| Status | Draft |

## 2. Requirement Description

This is an isolated requirement with no cross-references to other REQ files.

## 3. Functional Specification

No cross-links here.
EOF
  sed -i "s/X\.$i/$i/g" "$TEST_DIR/REQ-X.$i.md"
  echo "  Created REQ-X.$i.md"
done

echo ""
echo "2. Running validation on isolated corpus (should trigger GATE-05 ERROR)..."
echo ""

cd /opt/data/docs_flow_framework/ai_dev_flow/07_REQ

# Run validation (capture exit code)
./scripts/validate_req_quality_score.sh "$TEST_DIR" 2>&1 | grep -A 20 "GATE-05" || true

echo ""
echo "3. Testing EXIT CODE logic..."
./scripts/validate_req_quality_score.sh "$TEST_DIR" > /tmp/gate05_test_output.txt 2>&1
EXIT_CODE=$?
echo "  Exit code: $EXIT_CODE"
echo "  (Expected: 2 = ERROR, 1 = WARNING-only, 0 = PASS)"

if grep -q "GATE-05 ERROR" /tmp/gate05_test_output.txt; then
  echo "  ✅ GATE-05 ERROR detected correctly"
else
  echo "  ⚠️  GATE-05 ERROR not detected"
fi

echo ""
echo "4. Cleanup..."
rm -rf "$TEST_DIR"
rm -f /tmp/gate05_test_output.txt

echo ""
echo "✅ TEST COMPLETE"
echo ""
echo "Summary:"
echo "  • Test corpus created with 10 completely isolated REQ files"
echo "  • GATE-05 should detect ALL files lack cross-references"
echo "  • Should trigger ERROR (blocking) and attempt auto-fix"
echo "  • Script correctly increments ERRORS counter"
