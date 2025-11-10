# Workflow Diagram Fixes - Phase 1 Complete

**Date**: 2025-11-02
**Status**: Phase 1 Critical Updates COMPLETE | Phase 2 Partially Complete (2/7) | Phase 3 Pending

---

## Completed Work

### Phase 1: Critical Updates (3/3 COMPLETE ✅)

1. **✅ index.md** - Authoritative warning already present at line 80
   - Contains the complete Mermaid diagram with 10 layers
   - Designated as single source of truth for workflow

2. **✅ README.md** - Updated workflow section (lines 9-28)
   - Replaced text-based flowchart with reference to index.md
   - Added simplified 10-layer quick reference
   - Added key decision point about CTR creation

3. **✅ SPEC_DRIVEN_DEVELOPMENT_GUIDE.md** - Updated workflow section (lines 4-16)
   - Removed duplicate Mermaid diagram (~90 lines)
   - Added reference to authoritative index.md diagram
   - Simplified to workflow overview with layer structure

### Phase 2: Subdirectory READMEs (2/7 COMPLETE)

4. **✅ adrs/README.md** - Updated workflow section (lines 15-28)
   - Fixed corrupted text ("Requirements Expressions). All work traces back...")
   - Removed orphaned parentheses syntax error ("← )")
   - Added "YOU ARE HERE" marker for Architecture Layer
   - Added upstream/downstream references

5. **✅ bbds/README.md** - Updated workflow section (lines 14-27)
   - Fixed corrupted text
   - Added "YOU ARE HERE" marker for Testing Layer
   - Added upstream/downstream references

---

## Remaining Work

### Phase 2: Subdirectory READMEs (5 files remaining)

Each file needs the same pattern applied as adrs/ and bbds/:

**6. ears/README.md** (lines 14-42)
- Position: Business Layer (EARS)
- Upstream: PRD (Product Requirements Document)
- Downstream: BDD (Behavior-Driven Development)

**7. prd/README.md** (lines 18-46)
- Position: Business Layer (PRD)
- Upstream: BRD (Business Requirements Document)
- Downstream: EARS (Easy Approach to Requirements Syntax)

**8. reqs/README.md** (lines 18-46)
- Position: Requirements Layer (REQ)
- Upstream: SYS (System Requirements Specification)
- Downstream: IMPL (Implementation Plans)

**9. specs/README.md** (lines 9-37)
- Position: Implementation Layer (SPEC)
- Upstream: CTR (API Contracts) or IMPL (Implementation Plans)
- Downstream: TASKS (Code Generation Plans)

**10. sys/README.md** (lines 18-46)
- Position: Architecture Layer (SYS)
- Upstream: ADR (Architecture Decision Records)
- Downstream: REQ (Atomic Requirements)

**Standard Template for All 5**:
```markdown
## Position in Development Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**

[DOCUMENT_TYPE] is in the **[LAYER_NAME]** within the complete SDD workflow:

**Business Layer** (BRD → PRD → EARS) → **Testing Layer** (BDD) → **Architecture Layer** (ADR → SYS) → **Requirements Layer** (REQ) → **Project Management Layer** (IMPL) → **Interface Layer** (CTR - optional) → **Implementation Layer** (SPEC) → **Code Generation Layer** (TASKS) → **Execution Layer** (Code → Tests) → **Validation Layer** (Validation → Review → Production)

← **YOU ARE HERE** (insert at appropriate position)

**Key Points**:
- **Upstream**: [Immediate upstream document]
- **Downstream**: [Immediate downstream document]
- **Decision Point**: After IMPL, CTR is created if the requirement specifies an interface; otherwise, proceed directly to SPEC

For the complete workflow diagram with all relationships and styling, see [index.md](../index.md#traceability-flow).
```

---

### Phase 3: Mermaid-Only Updates (3 files remaining)

These files have simplified Mermaid diagrams showing local context. Keep the diagrams but add reference notes:

**11. contracts/README.md** (before line 15)
- Add reference note before existing Mermaid
- Keep existing Mermaid diagram (lines 15-30)
- Add "Simplified View" note after Mermaid

**12. impl_plans/README.md** (before line 11)
- Add reference note before existing Mermaid
- Keep existing Mermaid diagram (lines 11-27)
- Add "Simplified View" note after Mermaid

**13. ai_tasks/README.md** (before line 29)
- Add reference note before existing Mermaid
- Keep existing Mermaid diagram (lines 29-54)
- Add "Simplified View" note after Mermaid

**Standard Pattern**:
```markdown
## Position in Development Workflow

**⚠️ For the complete workflow diagram, see [../index.md](../index.md#traceability-flow).**

[DOCUMENT_TYPE] is positioned in the **[LAYER_NAME]** layer. The diagram below shows the immediate context:

[EXISTING MERMAID DIAGRAM]

**Simplified View Above**: This diagram shows only the immediate workflow context for [DOCUMENT_TYPE]. See [index.md](../index.md#traceability-flow) for the complete 10-layer AI Dev Flow with all upstream and downstream relationships.
```

---

## Impact Summary

### Completed (5/12 files)
- ✅ All critical main documents updated (README, SPEC_DRIVEN_DEVELOPMENT_GUIDE, index)
- ✅ Corrupted text fixed in adrs/ and bbds/
- ✅ Syntax errors removed ("← )" orphaned parentheses)
- ✅ "YOU ARE HERE" markers added for navigation
- ✅ Reference links to authoritative index.md

### Remaining (7/12 files)
- ⏳ 5 subdirectory READMEs with text-based workflows
- ⏳ 3 subdirectory READMEs with Mermaid diagrams

---

## Estimated Time Remaining

- **Phase 2 (5 files)**: 15-20 minutes (3-4 min per file)
- **Phase 3 (3 files)**: 10-15 minutes (3-5 min per file)
- **Total**: 25-35 minutes to complete

---

## Validation Checklist

After all files are updated:

- [ ] All links to `[../index.md](../index.md#traceability-flow)` resolve correctly
- [ ] Mermaid diagram in index.md renders properly
- [ ] All "YOU ARE HERE" markers are in correct positions
- [ ] No corrupted text patterns remain ("Requirements Expressions). All work traces back...")
- [ ] No orphaned parentheses ("← )")
- [ ] All 7 text-based workflow sections reference index.md
- [ ] All 3 Mermaid-only sections have reference notes

---

## Commands to Complete Remaining Work

**For Phase 2 files** (ears, prd, reqs, specs, sys):

1. Read the file to find the "## Position in Development Workflow" section
2. Identify the line range with the old text-based workflow
3. Use Edit tool to replace with standard template (customize [DOCUMENT_TYPE], [LAYER_NAME], Upstream, Downstream)

**For Phase 3 files** (contracts, impl_plans, ai_tasks):

1. Read the file to find the Mermaid diagram
2. Add reference note **before** the Mermaid section
3. Add "Simplified View" note **after** the Mermaid closing backticks

---

**Next Steps**: Continue with remaining 7 files in Phase 2 and Phase 3
