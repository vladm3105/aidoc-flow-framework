# CHANGELOG v1.11.0

**Release Date**: 2026-04-02
**Type**: Minor (Unified Report Naming Standard)
**Plan**: [PLAN-021](../plans/PLAN-021_sdd_reporting_naming_standard.md)

## Summary

Unified report naming across all mcp_sdd tools. Convention: `{DOC-ID}.{STAGE}.{FORMAT}`. Sub-framework registry (sdd, gov, kb). Derived copies renamed from `_validation`/`_remediated` to `_validate_copy`/`_remediate_copy`.

## Changes

### Report Naming

| Runner | Old | New |
|--------|-----|-----|
| validation | `validation_report.json` | `BRD-03.validate.json` |
| remediation | `remediation_report.json` | `BRD-03.remediate.json` |
| validate_fix | `validate_fix_report.json` | `BRD-03.validate_fix.json` |
| remediate_fix | `remediate_fix_report.json` | `BRD-03.remediate_fix.json` |
| consistency | `consistency_report.json` | `BRD-03.consistency.json` |
| link_validation | `link_validation_report.json` | `BRD-03.links.json` |
| prescreen | `prescreen_report.json` | `BRD-03.prescreen.json` |

### Derived Copies

| Old | New |
|-----|-----|
| `BRD-03_security_compliance_validation.yaml` | `BRD-03_security_compliance_validate_copy.yaml` |
| `BRD-03_security_compliance_remediated.yaml` | `BRD-03_security_compliance_remediate_copy.yaml` |

### New Standards

- `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` — canonical reference
- `extract_doc_id()` in `utils/source_files.py`
- `REPORT_PATTERN` / `DERIVED_COPY_PATTERN` regex constants

### Legacy Cleanup

1,089 legacy report files deleted from b-local-docs project (clean break, no backward compatibility).

## Backward Compatibility

Breaking change — no backward compatibility with legacy report naming. All consumers must use new naming.
