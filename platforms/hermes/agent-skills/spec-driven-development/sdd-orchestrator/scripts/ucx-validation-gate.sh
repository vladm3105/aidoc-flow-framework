#!/usr/bin/env bash
# UCX Validation Gate — quick structural check before calling sdd_validate
# Usage: ucx-validation-gate.sh <path_to_brd.yaml>
#
# This script runs FAST local checks that would otherwise slow down the
# iterative sdd_validate cycle. It catches the most common UCX structural
# errors (tag count, server header, YAML syntax) before invoking the MCP.

set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
    echo "Usage: ucx-validation-gate.sh <path_to_brd.yaml>"
    exit 1
fi

ERRORS=0

# 1. YAML parseable
python3 -c "import yaml; yaml.safe_load(open('$FILE'))" 2>/dev/null || {
    echo "[FATAL] YAML parse failed"
    exit 1
}

# 2. tag count (BRD max 1)
TAGS=$(python3 -c "
import yaml
d = yaml.safe_load(open('$FILE'))
tags = d.get('metadata',{}).get('tags',[])
print(len(tags))
" 2>/dev/null || echo 999)
if [[ "$TAGS" -gt 1 ]]; then
    echo "[ERROR] metadata.tags has $TAGS items; max 1 for brd (SDD-XS-004)"
    ((ERRORS++)) || true
fi

# 3. server header
SERVER=$(python3 -c "
import yaml
d = yaml.safe_load(open('$FILE'))
print(d.get('metadata',{}).get('validation',{}).get('server','MISSING'))
" 2>/dev/null || echo "MISSING")
if [[ "$SERVER" != "ucx_hermes" ]]; then
    echo "[ERROR] metadata.validation.server='$SERVER' (expected 'ucx_hermes')"
    ((ERRORS++)) || true
fi

# 4. doc_id format
DOCID=$(python3 -c "
import yaml
d = yaml.safe_load(open('$FILE'))
print(d.get('id','MISSING'))
" 2>/dev/null || echo "MISSING")
if [[ "$DOCID" == "MISSING" || ! "$DOCID" =~ ^BRD-[0-9]{2,}$ ]]; then
    echo "[ERROR] Invalid or missing id: '$DOCID' (expected BRD-NN)"
    ((ERRORS++)) || true
fi

if [[ "$ERRORS" -eq 0 ]]; then
    echo "[PASS] Fast gate: $FILE (calling sdd_validate next...)"
else
    echo "[FAIL] $ERRORS fast-gate error(s) in $FILE — fix before sdd_validate"
    exit 1
fi
