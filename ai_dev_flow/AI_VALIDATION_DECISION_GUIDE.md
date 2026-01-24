---
title: "AI Validation Decision Guide (Framework-Wide)"
tags:
  - ai-assistant-guide
  - validation-framework
  - decision-tree
  - best-practices
custom_fields:
  document_type: ai-guide
  artifact_type: framework-support
  priority: critical
  version: "1.0"
  scope: all-document-types
---

# AI Validation Decision Guide

**Purpose:** Decision-making framework for validators across all SDD document types (BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TASKS).

**Audience:** AI assistants and engineers working with validation failures.

**Related Documents:**
- [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md) - Core validation rules
- [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md) - Architecture and gates
- [VALIDATION_COMMANDS.md](./VALIDATION_COMMANDS.md) - CLI reference

**Document-Specific Guides:**
- [07_REQ/AI_VALIDATION_DECISION_GUIDE.md](./07_REQ/AI_VALIDATION_DECISION_GUIDE.md) - REQ-specific patterns

**Last Updated:** 2026-01-24

---

## The Core Question

When a validation fails, you must decide:

1. **Fix the document** - Content is wrong, incomplete, or malformed
2. **Fix the validator** - Validation rule is too strict, incorrect, or misaligned with template
3. **Accept the warning** - Document is correct; warning is informational or non-critical

---

## Universal Decision Framework

### Primary Decision Matrix

| Situation | Action | Rationale | Document Type |
|-----------|--------|-----------|---|
| Required section truly missing | Fix document | Content gap blocks downstream processing | All |
| Section exists but named per template variant (MVP vs full) | Fix validator | Template-aware validation needed | All |
| Normal markdown formatting (bold, spacing, table formatting) | Fix validator | Format should not fail quality gates | All |
| Arbitrary thresholds and interface is complete | Adjust validator or accept | Enforce value, not vanity metrics | All |
| Placeholders in prose/tables (TBD, TODO, FIXME) | Fix document | Incomplete content blocks readiness | All |
| Protocol/ABC stubs with NotImplementedError | Accept or note | Stubs clarify contract better than placeholders | SPEC, CTR |
| Missing inter-document cross-links | Fix document if related; accept if standalone | Traceability improves downstream work | All |
| Wrong folder/domain classification | Fix document (move file) | Organization matters for discovery | BRD, PRD, REQ |

### Priority Rules (Ranked)

1. **Errors blocking generation** (missing sections, required content)
   - Action: Fix document first
   - Example: REQ missing all 11 sections

2. **False positives eroding trust** (validator too strict)
   - Action: Fix validator next
   - Example: Validator rejects valid markdown formatting

3. **Style-only warnings** (cosmetic issues)
   - Action: Consider cost/benefit; accept if no quality gain
   - Example: File slightly exceeds token limit but content is necessary

4. **Always re-run validation** after changes to verify fix

---

## Document-Type Specific Patterns

### REQ Validation Decisions

**See:** [07_REQ/AI_VALIDATION_DECISION_GUIDE.md](./07_REQ/AI_VALIDATION_DECISION_GUIDE.md) for comprehensive REQ-specific patterns, gate details, and resolution workflows.

**Key REQ Gates:**
- **GATE-01**: Placeholder detection → Fix document (remove TBD, TODO, FIXME)
- **GATE-02**: Downstream references → Fix document (remove forward refs)
- **GATE-04**: Index sync → Fix document (update REQ index)
- **GATE-05**: Cross-linking → Generator tool or fix document (add @depends/@discoverability)
- **GATE-11**: Traceability tags → Fix document (add @brd, @prd, @ears)
- **GATE-13**: Domain classification → Fix document (correct folder/metadata)

---

### BRD/PRD/EARS Validation Decisions

**Scope:** Business requirements validation

**Common Decision Patterns:**
- **Missing epics/user stories**: Fix document (add content)
- **Vague acceptance criteria**: Fix document (clarify requirements)
- **Inconsistent status fields**: Fix document (align states)
- **Missing traceability to strategy**: Fix document (add cross-links)

**See:** Specific guidance in `01_BRD/AI_VALIDATION_DECISION_GUIDE.md` (when available).

---

### SPEC Validation Decisions

**Scope:** Technical specification and code generation readiness

**Common Decision Patterns:**
- **Missing API contracts**: Fix document (add OpenAPI/gRPC specs)
- **Schema mismatch with REQ**: Fix document (align with REQ)
- **Code gen readiness fails**: Fix document (ensure all models/stubs present)
- **Invalid Python syntax in examples**: Fix document (correct code)

**See:** Specific guidance in `09_SPEC/AI_VALIDATION_DECISION_GUIDE.md` (when available).

---

## General Resolution Process

### Step 1: Understand the Validation Error

```
✗ GATE-XX: Error message
  File: path/to/document.md
  Details: Specific failing condition
```

1. Read the actual document content (don't assume validator is right)
2. Identify the document type (BRD, REQ, SPEC, etc.)
3. Identify the document's template profile (MVP vs full)
4. Check the error message context

### Step 2: Classify the Issue

Ask these questions in order:

1. **Is the content actually missing or wrong?**
   - Yes → Fix the document
   - No → Move to Step 3

2. **Is the section named differently per template variant?**
   - Yes → Fix the validator
   - No → Move to Step 3

3. **Is the formatting/markup causing the failure?**
   - Yes → Fix the validator
   - No → Move to Step 4

4. **Is this an arbitrary threshold with complete content?**
   - Yes → Adjust validator or accept
   - No → Review the specific gate documentation

### Step 3: Execute the Fix

Choose and implement one of:

1. **Fix Document**: Modify content, structure, or metadata
2. **Fix Validator**: Adjust validation rule, thresholds, or template awareness
3. **Accept/Log**: Document is correct; warning is acceptable

### Step 4: Re-Validate & Verify

```bash
# Single file
bash validate_all.sh --file <document.md>

# Directory
bash validate_all.sh --directory <folder>
```

Confirm the fix resolves the issue without introducing new failures.

### Step 5: Update Framework Knowledge

If you discover:
- A new pattern or edge case
- A validator issue affecting multiple documents
- A template ambiguity

Update the relevant decision guide or validator rules for future reference.

---

## When to FIX vs ACCEPT

### Fix the Document If:

✅ Required section truly missing  
✅ Content is incomplete or placeholder  
✅ File in wrong domain/folder  
✅ Metadata fields incorrect or inconsistent  
✅ Cross-links logically related  
✅ Grammar/spelling errors in critical sections  

### Fix the Validator If:

✅ Template variant not recognized (MVP vs full)  
✅ Valid markdown syntax rejected  
✅ Too-strict threshold on metrics  
✅ Incorrect regex pattern matching  
✅ False positive for format violations  

### Accept the Warning If:

✅ Informational only (GATE-05 without critical links)  
✅ Style preference (icon choice, heading levels)  
✅ Non-blocking threshold slightly exceeded  
✅ Legacy compatibility note (document is valid, rule is legacy)  

---

## Handling Validation Conflicts

### Scenario: Multiple Validators Disagree

**Example:** REQ has 11 sections (template happy) but SPEC-readiness score is 45% (below 90% threshold).

**Resolution Process:**

1. **Identify the gap**: SPEC-readiness checks for implementation details (models, protocols) while template checks for structure.
2. **Understand validator purpose**:
   - Template validator: Ensures 11 sections exist
   - SPEC-readiness: Ensures content is sufficient for code generation
3. **Root cause**: Document has structure but lacks implementation details
4. **Fix**: Add Pydantic models, protocol definitions, exception classes
5. **Verify**: Re-run both validators

### Scenario: WARNING vs ERROR

**Example:** GATE-11 (ERROR) says @prd tag missing, but document intentionally has no PRD parent.

**Resolution Process:**

1. **Classify**: Is this document truly orphaned, or is it a valid root requirement?
2. **Decision**:
   - If truly orphaned → Fix validator (make GATE-11 aware of standalone REQs)
   - If should have parent → Fix document (add @prd tag)
3. **Update docs**: Document the pattern for future reference

---

## Common Patterns by Document Type

### Pattern: "Everything is in GATES; nothing is in sections"

**Issue**: Document has all gates passing but low SPEC-readiness score.

**Cause**: Gates validate structure; SPEC-readiness validates content richness.

**Fix**: Add implementation details (models, schemas, code examples).

---

### Pattern: "My structure is right but gates are failing"

**Issue**: Document has all 11 sections but gates report errors.

**Cause**: Sections may exist but gates check for specific content within them.

**Fix**: Review gate-specific requirements (e.g., GATE-04 requires specific field values).

---

### Pattern: "Validation passes locally but fails in CI"

**Issue**: Document validates on development machine but fails in CI/CD.

**Causes**:
- Different Python version (use explicit Python 3.12+)
- Different file path encoding
- Environment variables not set
- Validator version mismatch

**Fix**:
- Use absolute paths
- Specify Python 3.12+ explicitly
- Check validator versions match
- Test in CI environment locally before pushing

---

## Framework Extensions

### Adding Document-Type Specific Guides

To extend this framework for a new document type:

1. Create `<LAYER>/<ARTIFACT>/AI_VALIDATION_DECISION_GUIDE.md`
2. Document type-specific gates and patterns
3. Link from this framework-wide guide
4. Cross-reference `VALIDATION_DECISION_FRAMEWORK.md` for universal rules

### Adding Custom Validators

To add a new validator:

1. Create `<LAYER>/<ARTIFACT>/scripts/validate_<name>.sh` or `.py`
2. Follow orchestrator pattern (integrate with `validate_all.sh`)
3. Output standard format: Gate, severity, message
4. Document in `VALIDATION_COMMANDS.md` and `VALIDATION_STRATEGY_GUIDE.md`

---

## Quick Reference: Decision Checklists

### When Document Validation Fails

```
[ ] 1. Read actual document content
[ ] 2. Identify document type and template profile
[ ] 3. Review gate-specific documentation
[ ] 4. Classify issue (missing content? template variance? format?)
[ ] 5. Choose action (fix document, fix validator, accept)
[ ] 6. Implement fix
[ ] 7. Re-run validation
[ ] 8. Verify no new failures
[ ] 9. Update framework docs if pattern is new
```

### When Creating New Validation Rules

```
[ ] 1. Define gate purpose and severity (ERROR/WARNING/INFO)
[ ] 2. Document success/failure criteria
[ ] 3. Provide 2-3 examples (pass and fail cases)
[ ] 4. Consider template variants (MVP vs full)
[ ] 5. Add to validator script
[ ] 6. Test against sample documents
[ ] 7. Document in VALIDATION_COMMANDS.md
[ ] 8. Add decision patterns to AI_VALIDATION_DECISION_GUIDE.md
[ ] 9. Link from VALIDATION_STRATEGY_GUIDE.md
```

---

## Related Resources

- [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md) - Core universal rules
- [VALIDATION_STRATEGY_GUIDE.md](./VALIDATION_STRATEGY_GUIDE.md) - Architecture and gate details
- [VALIDATION_COMMANDS.md](./VALIDATION_COMMANDS.md) - CLI command reference
- [07_REQ/AI_VALIDATION_DECISION_GUIDE.md](./07_REQ/AI_VALIDATION_DECISION_GUIDE.md) - REQ-specific patterns

---

**Last Updated:** 2026-01-24  
**Status:** Framework-wide decision guide for all document types  
**Audience:** AI assistants, engineers, validator maintainers  
**Scope:** Validation decision-making across entire SDD framework
