# CHANGELOG v1.21.5

**Release Date**: 2026-03-21
**Type**: Patch

## Summary

This patch release improves the robustness of the AI preflight probe by adding an ISO date fallback mechanism. The preflight validation now gracefully handles LLM formatting drift where providers (especially Claude) occasionally return inconsistent epoch tokens while still including the correct ISO date in the response text.

## Changes

### AI Preflight Probe: ISO Date Fallback

**Problem**:
The AI preflight probe's Phase 3 (epoch date validation) occasionally failed with false negatives when LLMs returned responses containing:
- Correct ISO date (YYYY-MM-DD) in the prose text
- Malformed or inconsistent epoch token (unix timestamp that maps to a different UTC date)

Example: Claude response included "2026-03-21" in text but `1774252800` (which equals 2026-03-23 UTC), causing preflight to raise despite the date being logically correct.

**Root Cause**:
LLMs sometimes structure date responses inconsistently, particularly when using natural language formatting (e.g., "**{date} in UTC epoch**: `{timestamp}`"). The prose and numeric token can drift if generation is interrupted or response temperature causes rephrasing.

**Solution**:
- Phase 3 (epoch date probe) now implements a two-stage validation:
  1. **Primary**: Extract and validate epoch unix timestamp (existing behavior)
  2. **Fallback**: If epoch mismatches expected date, search response text for ISO date pattern (`\b\d{4}-\d{2}-\d{2}\b`)
  3. **Preference**: If expected date found in ISO matches, prefer it; otherwise use first valid ISO date parsed
  4. **Exit condition**: Only raise AIClientError if BOTH epoch validation AND ISO fallback fail

**Impact**:
- Reduces false-negative preflight failures from formatting drift in Claude, Codex, and other LLM responses
- Maintains safety: ISO date must parse as valid `YYYY-MM-DD` and be extracted from the response itself
- Zero breaking changes: Existing preflight behavior remains unchanged when responses are well-formed

### Code Changes

**File**: `ucx/ai/cli_client.py`

**Modified method**: `_run_availability_preflight()` (Phase 3 logic, lines 475-483)
```python
if detected_date != expected_utc_date:
    iso_detected_date = self._extract_iso_utc_date(response, expected_utc_date)
    if iso_detected_date == expected_utc_date:
        detected_date = iso_detected_date
```

**New method**: `_extract_iso_utc_date(text, expected_date=None)` (lines 723-750)
- Extracts ISO dates from response text using regex pattern `\b(\d{4}-\d{2}-\d{2})\b`
- Parses all matches with `datetime.date.fromisoformat()`
- Returns expected_date if found in matches (preference), else first parsed date
- Returns None if no valid ISO dates found

### Test Coverage

**File**: `tests/unit/test_ai.py`

**New test**: `test_preflight_accepts_iso_date_when_epoch_is_inconsistent()` (lines 506-520)
- Simulates Claude-style formatting drift: correct ISO date + inconsistent epoch token
- Validates that preflight passes via ISO fallback instead of raising error
- Confirms regression protection for the exact scenario described above

**Existing tests**: All 24 preflight tests passing
- 4 core Phase 1-3 preflight pytest cases
- 20 edge case and error handling tests
- Verified no breaking changes to existing behavior

### Documentation

- Updated `ucx/ai/cli_client.py` docstrings and inline comments to explain fallback mechanism
- Preflight documentation in `docs/` updated to reflect two-stage validation approach

## Commits

This release is included in commit:
```
feat(ai): add ISO date fallback to preflight probe for Claude formatting drift tolerance

- Implement two-stage date validation in preflight Phase 3:
  Primary: epoch extraction (existing), Fallback: ISO date search
- Add _extract_iso_utc_date() helper for YYYY-MM-DD pattern matching
- Prefer expected_date in matches; fallback to first valid ISO date
- Add regression test for Claude-style epoch/ISO mismatch scenario
- All 24 preflight tests passing, zero breaking changes
- Reduces false-negative preflight failures from formatting drift

Fixes: LLM availability preflight failures when epoch token is malformed
Tests: test_preflight_accepts_iso_date_when_epoch_is_inconsistent()
```

## Validation

- **Unit Tests**: 24 preflight tests passing (4 core + 20 edge cases)
- **Regression Test**: New test validates exact error scenario from user report
- **Integration Test**: Live Claude remediation executed successfully with preflight passing via ISO fallback
- **Source Protection**: Confirmed source files unchanged after remediation run

## Backward Compatibility

✅ **Fully backward compatible**
- Epoch extraction logic unchanged
- Preflight only applies ISO fallback when epoch validation fails
- All existing tests passing without modification
- No API changes or version bumps required

## Known Limitations

- ISO fallback works best when response contains the expected date in prose
- If response contains multiple dates, preference is given to expected_date; first valid date used as secondary fallback
- Fallback doesn't apply to responses that lack any date format (extremely rare; Phase 2 capability check typically catches this earlier)

## Next Steps (v1.22.0)

- Consider extending ISO date fallback to LiteLLMClient (currently CLI-only)
- Add telemetry/logging to track fallback activation rate across providers
- Potential: Expand pattern matching for other date formats (ISO timestamp, RFC 3339, etc.)
