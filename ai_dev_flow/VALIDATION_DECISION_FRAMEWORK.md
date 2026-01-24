---
title: "Validation Decision Framework"
tags:
  - framework-guide
  - validation
  - decision-framework
custom_fields:
  document_type: guide
  artifact_type: REF
  priority: shared
  development_status: active
  version: "1.0"
---

# Validation Decision Framework

Purpose: Give AI assistants a consistent, framework-wide process to decide whether to fix documents, adjust validators, or accept warnings.

## When You See a Validation Finding

1) Read the actual document content (do not assume the validator is right).
2) Identify template profile (mvp vs full) and intended section names.
3) Classify the issue:
   - Content missing/incomplete → usually fix the document.
   - Format/markup mismatch → usually fix the validator.
   - Template variation (mvp vs full) → make validator template-aware.
   - Style/threshold preference (e.g., “3+ functions”) → weigh value; adjust validator or accept.
4) Ask: does fixing this improve SPEC/code generation or traceability?
5) Choose and execute: Fix document | Fix validator | Accept/log.
6) Re-run validation and record the outcome.

## Decision Matrix

| Situation | Action | Rationale |
|-----------|--------|-----------|
| Required section truly missing | Fix document | Content gap blocks readiness |
| Section exists but named per template (mvp vs full) | Fix validator | Template-aware validation |
| Table/headers with normal markdown (bold, spacing) | Fix validator | Formatting should not fail quality |
| Arbitrary thresholds (e.g., ≥3 functions) and interface is already complete | Adjust validator or accept | Enforce value, not vanity |
| Placeholders in prose/tables | Fix document | Incomplete content |
| Protocol/ABC stubs | Prefer `NotImplementedError` stubs; if ellipsis flagged, fix validator | Raising clarifies contract and avoids ambiguous placeholders |
| REQ missing inter-folder cross-links (GATE-05) | Fix document if logically related; accept if standalone | Traceability improves downstream work; standalone requirements are valid |
| REQ in wrong domain subdirectory | Fix document (move file) | Organization matters for discovery and governance |

## Priority Rules

1) Errors that block generation (missing sections/content) → fix document first.
2) False positives that erode trust → fix validator next.
3) Style-only warnings → consider cost/benefit; accept if no quality gain.
4) Always re-run validation after changes.

## Minimal Workflow

- Run validator for the artifact.
- Triage findings with the matrix above.
- Implement fixes (doc or validator); keep changes small and justified.
- Re-validate; if passing, note any accepted warnings.

## Auto-Fix Guidance (AI Assistants)

When a clear, low-risk fix will move a document to "pass", the assistant should apply it automatically (and re-validate):
- Remove/replace placeholders in prose/tables with concrete values.
- Add minimal missing structure/content that is unambiguous (e.g., required section headers present in template).
- Resolve harmless format gaps that cause false positives (e.g., bold headers) by updating the validator rather than stripping formatting.
- For style thresholds (e.g., required count of typed methods), prefer adding a small, meaningful addition that genuinely improves clarity; if not value-adding, consider relaxing the rule per template profile.
- For Protocol/ABC examples, use `raise NotImplementedError("method not implemented")` instead of `pass` or bare ellipsis to keep the contract explicit while remaining abstract.
- If a fix is ambiguous or materially changes intent, stop and ask before editing.

## Pointers

- REQ-specific addendum: [07_REQ/AI_VALIDATION_DECISION_GUIDE.md](./07_REQ/AI_VALIDATION_DECISION_GUIDE.md)
- Naming standards: [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md)
- Validation scripts: [scripts/](./scripts/)
