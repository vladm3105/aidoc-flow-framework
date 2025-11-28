---
title: "SPEC-TEMPLATE: technical-specification"
tags:
  - spec-template
  - layer-10-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: SPEC
  layer: 10
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  template_for: technical-specification
---

> **📋 Document Authority**: This is the **PRIMARY STANDARD** for SPEC Markdown structure.
> - All SPEC Markdown documents must conform to this template
> - `SPEC_CREATION_RULES.md` - Helper guidance for template usage
> - `SPEC_VALIDATION_RULES.md` - Post-creation validation checks

> **⚠️ UPSTREAM ARTIFACT REQUIREMENT**: Before completing traceability tags:
> 1. **Check existing artifacts**: List what upstream documents actually exist in `docs/`
> 2. **Reference only existing documents**: Use actual document IDs, not placeholders
> 3. **Use `null` appropriately**: Only when upstream artifact type genuinely doesn't exist for this feature
> 4. **Do NOT create phantom references**: Never reference documents that don't exist
> 5. **Do NOT create missing upstream artifacts**: If upstream artifacts are missing, skip that functionality. Only create functionality for existing upstream artifacts.

