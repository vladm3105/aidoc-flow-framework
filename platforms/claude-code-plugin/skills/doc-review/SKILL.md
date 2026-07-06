---
name: doc-review
description: "DEPRECATED in v0.4.0. Use `/aidoc-flow:doc-validator` with scope=prose. This skill is a redirect stub and will be removed in v0.7.0."
metadata:
  custom_fields:
    version: "0.23.1"
    framework_spec_version: "0.33.0"
    last_updated: "2026-05-31"
    skill_category: quality-assurance
    deprecated: true
    replacement: "doc-validator (scope=prose)"
---

# doc-review (deprecated)

This skill was consolidated into `doc-validator` in plugin v0.4.0. The four
prose-quality classes (DATA / REF / TYPO / TERM) and the severity model are
preserved verbatim under `doc-validator` Mode: prose.

**Migration**: replace any `doc-review <target>` invocation with
`/aidoc-flow:doc-validator scope=prose <target>`.

This stub will be removed in plugin v0.7.0.
