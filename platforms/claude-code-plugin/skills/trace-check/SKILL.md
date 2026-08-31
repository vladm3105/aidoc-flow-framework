---
name: trace-check
description: "DEPRECATED in v0.4.0. Use `/aidoc-flow:doc-validator` traceability pass. This skill is a redirect stub and will be removed in v1.0.0."
metadata:
  custom_fields:
    version: "0.25.0"
    framework_spec_version: "0.47.0"
    last_updated: "2026-05-31"
    skill_category: quality-assurance
    deprecated: true
    replacement: "doc-validator (traceability pass)"
---

# trace-check (deprecated)

This skill was consolidated into `doc-validator` in plugin v0.4.0. The
bidirectional traceability mechanics - >=95% symmetry scoring, orphan
detection, safe auto-fix with timestamped backup + rollback - are preserved
verbatim under `doc-validator`'s traceability pass.

**Migration**: replace any `trace-check <target>` invocation with
`/aidoc-flow:doc-validator <target>` (traceability pass runs by default).

This stub will be removed in plugin v1.0.0.
