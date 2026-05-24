# TEST-CHECKLIST-001: MCP New Contract Compliance Rows

## Scope

This checklist maps newly added compliance-matrix contract rows in SPEC-001, SPEC-002, SPEC-003, and SPEC-004 to concrete unit and integration tests.

## Execution Notes

- Unit tests validate deterministic parsing, normalization, and schema checks.
- Integration tests validate end-to-end workflow behavior across create/validate/review/fix/report stages.
- Mark each item complete only after executable evidence exists in CI or local test logs.
- Required completion gate per row: Unit = PASS, Integration = PASS, and evidence link recorded.
- A row remains incomplete if either test type is missing or evidence is not linked.

## Checklist

| ID | SPEC Row | Unit Test Case | Integration Test Case | Unit Status | Integration Status | Evidence Link |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | SPEC-001: Source eligibility | `test_source_eligibility_excludes_archived_paths_without_override` | `test_pipeline_discovery_excludes_archived_artifacts_by_default` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC001_TC003.md` |
| TC-002 | SPEC-001: Upstream-missing policy | `test_upstream_missing_emits_skip_metadata_fields` | `test_downstream_operation_skips_when_required_upstream_missing` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC001_TC003.md` |
| TC-003 | SPEC-002: Optional-layer skip routing | `test_optional_layer_skip_populates_routing_metadata` | `test_missing_optional_ctr_reroutes_to_next_layer_with_skip_metadata` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC001_TC003.md` |
| TC-004 | SPEC-003: Input precedence and conflict blocking | `test_input_source_precedence_iplan_over_ref_over_prompt` | `test_conflicting_scope_or_objective_between_sources_returns_explicit_failure` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC004_TC009.md` |
| TC-005 | SPEC-003: Registry binding | `test_profile_binding_matches_authoritative_registry_entry` | `test_validate_uses_active_registry_metadata_for_target_artifact` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC004_TC009.md` |
| TC-006 | SPEC-003: Subtype resolution | `test_subtype_profile_resolution_is_deterministic` | `test_subtype_code_routes_to_expected_subtype_profile_end_to_end` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC004_TC009.md` |
| TC-007 | SPEC-003: Structural gate order | `test_folder_structure_gate_runs_before_non_structural_checks` | `test_validate_stops_on_blocking_structure_violation_before_content_checks` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC004_TC009.md` |
| TC-008 | SPEC-003: Layer boundary enforcement | `test_boundary_patterns_reject_downstream_syntax_in_layer` | `test_cross_layer_reference_violation_fails_validation_with_boundary_error` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC004_TC009.md` |
| TC-009 | SPEC-003: Threshold precedence | `test_threshold_precedence_order_profile_then_registry_then_defaults` | `test_scoring_conflict_uses_active_precedence_source_consistently` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC004_TC009.md` |
| TC-010 | SPEC-004: Audit/review/fix report families | `test_report_family_name_generation_uses_A_R_F_prefixes` | `test_audit_wrapper_outputs_deterministic_family_selection_and_versioned_names` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC010_TC014.md` |
| TC-011 | SPEC-004: Naming-family mapping | `test_lifecycle_to_audit_wrapper_name_mapping_preserves_lineage_fields` | `test_multi_stage_run_preserves_deterministic_name_mapping_across_reports` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC010_TC014.md` |
| TC-012 | SPEC-004: Timestamp normalization | `test_generated_at_requires_explicit_timezone_offset` | `test_report_generation_applies_repository_timezone_policy_when_enabled` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC010_TC014.md` |
| TC-013 | SPEC-004: Combined audit fix queue | `test_combined_fix_queue_schema_requires_all_buckets_and_per_finding_fields` | `test_fixer_consumes_combined_queue_and_classifies_findings_by_bucket` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC010_TC014.md` |
| TC-014 | SPEC-004: Drift hash validation | `test_drift_hash_format_requires_sha256_prefix_and_64_hex` | `test_drift_enabled_run_enforces_required_upstream_hash_entries` | PASS | PASS | `mcp/tmp/TEST_EVIDENCE_2026-03-24_TC010_TC014.md` |

## Coverage Summary

- Total new contract rows covered: 14
- Unit test cases: 14
- Integration test cases: 14

## Completion Rule

- Checklist is complete only when all TC rows have Unit Status = PASS, Integration Status = PASS, and Evidence Link is populated.
- Workstream G and Workstream H approval gates must reject incomplete rows.

## Referenced Compliance Matrices

- SPEC-001 Section 7
- SPEC-002 Section 11
- SPEC-003 Section 9
- SPEC-004 Section 10
