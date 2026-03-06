#!/usr/bin/env bash
# =============================================================================
# 01_parse.sh — Step 1: Parse Council Audit Report into JSON
# =============================================================================
# Usage: 01_parse.sh <COUNCIL_AUDIT_REPORT.md> <output.json>
# Reads the audit report, sends it to the configured AI agent with the
# parse_report.txt prompt, and writes the resulting JSON array to output.json.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/core"

source "$CORE_DIR/config.sh"
source "$CORE_DIR/utils.sh"

require_jq

REPORT_FILE="${1:-}"
OUTPUT_JSON="${2:-}"

[[ -z "$REPORT_FILE" ]] && die "Usage: 01_parse.sh <REPORT.md> <output.json>"
[[ -z "$OUTPUT_JSON" ]] && die "Usage: 01_parse.sh <REPORT.md> <output.json>"
require_file "$REPORT_FILE"

log_step "Step 1: Parsing council audit report → JSON"
log_info "Report:  $REPORT_FILE"
log_info "Output:  $OUTPUT_JSON"
log_info "Agent:   $AI_AGENT"

# Build the prompt: prepend parse_report.txt, append the report content
PROMPT_TEMPLATE="$SCRIPT_DIR/prompts/parse_report.txt"
require_file "$PROMPT_TEMPLATE"

PROMPT_TMP=$(tmp_file "council_parse_prompt")
cleanup_on_exit "$PROMPT_TMP"

cat "$PROMPT_TEMPLATE" > "$PROMPT_TMP"
echo "" >> "$PROMPT_TMP"
cat "$REPORT_FILE" >> "$PROMPT_TMP"

log_info "Sending to AI agent (AI_AGENT=$AI_AGENT)..."

# Call the AI agent
RESPONSE_TMP=$(tmp_file "council_parse_response")
cleanup_on_exit "$RESPONSE_TMP"

if [[ "${DRY_RUN:-false}" == "true" ]]; then
  log_dry "Would call: ai_exec.sh $PROMPT_TMP"
  # Write a sample dry-run output for pipeline testing
  cat > "$RESPONSE_TMP" << 'EOF'
[
  {"id":"R1","priority":"P0","type":"section_add","action":"Add ledger sharding strategy and replication topology specification","target_section":"6.5","source_expert":"architect","target_document":"BRD-01","acceptance_criteria":"Section 6.5 defines sharding strategy, consistency model, and replication topology"},
  {"id":"R4","priority":"P0","type":"compliance_spec","action":"Add AML controls: velocity limits, structuring detection, watchlist screening, SAR triggers","target_section":"7.1","source_expert":"auditor","target_document":"BRD-01","acceptance_criteria":"Section 7.1 defines AML control architecture with all four required mechanisms"},
  {"id":"R10","priority":"P2","type":"frontmatter_tag","action":"Add @depends: BRD-40, BRD-42, BRD-45, BRD-46 to frontmatter (circular dependency: BRD-01 claims no upstream)","target_section":"frontmatter","source_expert":"integration_expert","target_document":"BRD-01","acceptance_criteria":"Frontmatter includes @depends field listing BRD-40, BRD-42, BRD-45, BRD-46"},
  {"id":"R11","priority":"P2","type":"matrix_row","action":"Add BRD-01 entity ownership rows to Integration Matrix with event bus topics and API contracts","target_section":"integration_matrix","source_expert":"integration_expert","target_document":"BRD-00_INTEGRATION_MATRIX","acceptance_criteria":"Integration Matrix contains BRD-01 row with entity ownership, event topics, and API contracts"}
]
EOF
  log_dry "Sample JSON written to $RESPONSE_TMP (4 items)"
else
  "$AI_EXEC_SH" "$PROMPT_TMP" > "$RESPONSE_TMP"
fi

# Extract JSON array from response using the external helper (avoids bash heredoc parse issues)
python3 "$SCRIPT_DIR/extract_json.py" "$RESPONSE_TMP" "$OUTPUT_JSON"

log_ok "Step 1 complete: $(jq 'length' "$OUTPUT_JSON") actions written to $OUTPUT_JSON"

