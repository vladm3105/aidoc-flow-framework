#!/bin/bash
# Smoke test script for dev deployments
# Usage: smoke_test.sh <base_url>
#
# Validates basic service functionality after each dev deployment:
# - Health check endpoint
# - Readiness endpoint
# - Version endpoint
# - Config load check

set -e

BASE_URL="${1:?Usage: smoke_test.sh <base_url>}"
MAX_RETRIES=${MAX_RETRIES:-5}
RETRY_DELAY=${RETRY_DELAY:-10}
TIMEOUT=${TIMEOUT:-10}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_pass() {
    echo -e "${GREEN}${NC} $1"
}

log_fail() {
    echo -e "${RED}${NC} $1"
}

log_info() {
    echo -e "${YELLOW}→${NC} $1"
}

smoke_test() {
    local endpoint=$1
    local expected_code=${2:-200}
    local description=${3:-$endpoint}

    for i in $(seq 1 $MAX_RETRIES); do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            "${BASE_URL}${endpoint}" \
            --max-time "$TIMEOUT" 2>/dev/null || echo "000")

        if [ "$HTTP_CODE" == "$expected_code" ]; then
            log_pass "${description}: HTTP ${HTTP_CODE}"
            return 0
        fi

        log_info "Attempt $i/${MAX_RETRIES}: ${description} returned HTTP ${HTTP_CODE}, expected ${expected_code}"
        sleep $RETRY_DELAY
    done

    log_fail "${description}: Failed after ${MAX_RETRIES} attempts (last: HTTP ${HTTP_CODE})"
    return 1
}

smoke_test_json() {
    local endpoint=$1
    local json_field=$2
    local description=${3:-$endpoint}

    for i in $(seq 1 $MAX_RETRIES); do
        RESPONSE=$(curl -s "${BASE_URL}${endpoint}" --max-time "$TIMEOUT" 2>/dev/null || echo "")
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            "${BASE_URL}${endpoint}" \
            --max-time "$TIMEOUT" 2>/dev/null || echo "000")

        if [ "$HTTP_CODE" == "200" ]; then
            # Check if JSON field exists
            FIELD_VALUE=$(echo "$RESPONSE" | jq -r ".$json_field" 2>/dev/null || echo "null")
            if [ "$FIELD_VALUE" != "null" ] && [ -n "$FIELD_VALUE" ]; then
                log_pass "${description}: HTTP ${HTTP_CODE}, ${json_field}=${FIELD_VALUE}"
                return 0
            else
                log_info "Attempt $i/${MAX_RETRIES}: ${description} missing field '${json_field}'"
            fi
        else
            log_info "Attempt $i/${MAX_RETRIES}: ${description} returned HTTP ${HTTP_CODE}"
        fi

        sleep $RETRY_DELAY
    done

    log_fail "${description}: Failed after ${MAX_RETRIES} attempts"
    return 1
}

echo "========================================"
echo "Running smoke tests against ${BASE_URL}"
echo "========================================"
echo ""

FAILED=0

# Test 1: Health check
if ! smoke_test "/health" 200 "Health check"; then
    FAILED=$((FAILED + 1))
fi

# Test 2: Readiness check
if ! smoke_test "/ready" 200 "Readiness check"; then
    FAILED=$((FAILED + 1))
fi

# Test 3: Version endpoint (with JSON field check)
if ! smoke_test_json "/version" "version" "Version endpoint"; then
    FAILED=$((FAILED + 1))
fi

# Test 4: Config load check (optional - may not exist in all services)
if ! smoke_test "/health/config" 200 "Config load check"; then
    # Config endpoint is optional, don't fail the whole suite
    log_info "Config endpoint not available (optional)"
fi

echo ""
echo "========================================"
if [ $FAILED -eq 0 ]; then
    log_pass "All smoke tests passed"
    exit 0
else
    log_fail "$FAILED smoke test(s) failed"
    exit 1
fi
