# Implementation Plan - Fix Documentation Inconsistencies

**Created**: 2025-11-14 12:57:03 EST
**Status**: Ready for Implementation
**Project**: AI Dev Flow Framework (docs_flow_framework)

## Objective

Fix 47 identified documentation inconsistencies across the AI Dev Flow framework, focusing on broken file references, layer numbering confusion, terminology ambiguity, and template standardization.

## Context

### Review Findings
Comprehensive review identified **47 issues** across 8 categories:
- **Critical (12)**: Broken file references, layer numbering confusion
- **High (18)**: Terminology inconsistencies, template variations
- **Medium (12)**: Outdated instructions, cross-reference issues
- **Low (5)**: Historical comments, minor version inconsistencies

### Key Problem Areas
1. **Layer Numbering Confusion**: Mermaid diagrams use L1-L11 (visual groupings) but documentation uses formal Layers 0-15
2. **Terminology Ambiguity**: "Implementation Plans" refers to both IMPL (Layer 8) and IPLAN (Layer 12)
3. **Missing Template Files**: index.md references BRD-template-2.md and BRD-trading-template.md which don't exist
4. **Broken Example References**: SPEC_DRIVEN_DEVELOPMENT_GUIDE.md references 9 non-existent example files

### Decisions Made
- **SKIP**: @tags format standardization (user requested to skip this item)
- **Approach**: Replace specific example file references with generic placeholders
- **Priority**: Focus on Phases 1-3 (Critical, High, and Medium priority issues)

## Task List

### Phase 1: Critical Fixes
- [ ] Fix broken template references in index.md (remove BRD-template-2.md, BRD-trading-template.md)
- [ ] Update BRD/README.md to reflect only existing BRD-TEMPLATE.md
- [ ] Add layer numbering clarification notes to all Mermaid diagrams (TRACEABILITY.md, README.md, index.md)
- [ ] Standardize "Implementation Plans" terminology across all files
- [ ] Replace missing example file references in SPEC_DRIVEN_DEVELOPMENT_GUIDE.md with generic placeholders

### Phase 2: High Priority Fixes
- [ ] Create layer mapping table (Formal Layers 0-15 vs Mermaid L1-L11)
- [ ] Add mapping table to README.md and TRACEABILITY.md
- [ ] Standardize Traceability section numbering across all templates
- [ ] Standardize Document Control fields across all templates
- [ ] Fix ADR-000 technology stack reference in ADR-TEMPLATE.md

### Phase 3: Medium Priority Fixes
- [ ] Scan and update all 10K token limit references to current limits
- [ ] Ensure consistency with TOOL_OPTIMIZATION_GUIDE.md
- [ ] Create validation script to check all markdown links
- [ ] Fix any broken internal links found by validation script

### Phase 4: Low Priority (Future Maintenance)
- [ ] Clean up migration comments (TASKS_PLANS, CONTRACTS)
- [ ] Standardize version numbering across all README files
- [ ] Create GLOSSARY.md for canonical term definitions

## Implementation Guide

### Prerequisites
- Working directory: `/opt/data/docs_flow_framework/`
- Git repository: Ensure clean working tree before starting
- Review report available in conversation history

### Affected Files by Phase

**Phase 1 Files:**
```
ai_dev_flow/index.md
ai_dev_flow/BRD/README.md
ai_dev_flow/README.md
ai_dev_flow/TRACEABILITY.md
ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
ai_dev_flow/QUICK_REFERENCE.md
ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md
All *-TEMPLATE.md files
```

**Phase 2 Files:**
```
ai_dev_flow/README.md
ai_dev_flow/TRACEABILITY.md
ai_dev_flow/ADR/ADR-TEMPLATE.md
ai_dev_flow/BRD/BRD-TEMPLATE.md
ai_dev_flow/REQ/REQ-TEMPLATE.md
ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md
ai_dev_flow/TASKS/TASKS-TEMPLATE.md
ai_dev_flow/SPEC/SPEC-TEMPLATE.md
ai_dev_flow/EARS/EARS-TEMPLATE.md
ai_dev_flow/PRD/PRD-TEMPLATE.md
```

**Phase 3 Files:**
```
ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md
Create: validate_documentation_consistency.py
```

### Execution Steps

#### Phase 1: Critical Fixes (4-6 hours)

1. **Fix Template References**
   ```bash
   # Edit ai_dev_flow/index.md
   # Remove lines referencing BRD-template-2.md and BRD-trading-template.md
   # Keep only: [BRD-TEMPLATE.md](./BRD/BRD-TEMPLATE.md)

   # Edit ai_dev_flow/BRD/README.md
   # Update template list to show only BRD-TEMPLATE.md
   ```

2. **Add Layer Numbering Clarification**
   Add this note to all Mermaid diagrams:
   ```markdown
   > **Note on Diagram Labels**: Mermaid subgraph labels (L1-L11) are visual groupings for diagram clarity, not formal layer numbers. Always use formal layer numbers (0-15) when implementing cumulative tagging or referencing layers in code/documentation.
   ```

   Files to update:
   - `ai_dev_flow/TRACEABILITY.md` (lines 34-76)
   - `ai_dev_flow/README.md` (after Mermaid diagrams)
   - `ai_dev_flow/index.md` (if contains Mermaid diagrams)

3. **Standardize Implementation Plans Terminology**
   Search and replace across all files:
   - "Implementation Plans (Layer 8)" → "Implementation Specifications (IMPL) - Layer 8"
   - "Implementation Plans (Layer 12)" → "Implementation Work Plans (IPLAN) - Layer 12"

   ```bash
   grep -r "Implementation Plans" ai_dev_flow/ --include="*.md"
   # Review each occurrence and update appropriately
   ```

4. **Fix Missing Example References**
   In `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` lines 132-134, 976-984:
   - Replace specific file paths with generic placeholders
   - Example: `./REQ/risk/lim/REQ-003_position_limit_enforcement.md` → `./REQ/{category}/{subcategory}/REQ-NNN_{slug}.md`
   - Add note: "**Note**: File paths shown are illustrative examples. Replace with actual paths for your project."

#### Phase 2: High Priority Fixes (8-12 hours)

5. **Create Layer Mapping Table**
   Add to `README.md` and `TRACEABILITY.md`:

   ```markdown
   ## Layer Numbering Reference

   ### Formal Layer Numbers (Use in Code/Tags/Documentation)
   | Layer | Artifact Type | Purpose |
   |-------|---------------|---------|
   | 0 | Strategy (STRAT) | Strategic business direction |
   | 1 | Business Requirements (BRD) | Business needs and goals |
   | 2 | Product Requirements (PRD) | Product features and specifications |
   | 3 | EARS | Structured requirement statements |
   | 4 | System Requirements (SYS) | System-level specifications |
   | 5 | Architecture Decisions (ADR) | Technical architecture choices |
   | 6 | Contracts (CTR) | Interface contracts (dual-file format) |
   | 7 | Requirements (REQ) | Atomic requirements |
   | 8 | Implementation Specifications (IMPL) | Project management plans |
   | 9 | Specifications (SPEC) | Detailed technical specs |
   | 10 | BDD | Behavior-driven test scenarios |
   | 11 | Tasks (TASKS) | Development task breakdown |
   | 12 | Implementation Work Plans (IPLAN) | Session execution plans |
   | 13 | Code | Actual implementation |
   | 14 | Tests | Unit/integration tests |
   | 15 | Validation | End-to-end validation |

   ### Mermaid Diagram Visual Groupings (L1-L11)
   Diagrams use simplified labels for visual clarity:
   - **L1**: Business Layer (contains Layers 1-3: BRD, PRD, EARS)
   - **L2**: System Layer (contains Layer 4: SYS)
   - **L3**: Architecture Layer (contains Layer 5: ADR)
   - **L4**: Contract Layer (contains Layer 6: CTR)
   - **L5**: Requirements Layer (contains Layer 7: REQ)
   - **L6**: Implementation Specs (contains Layer 8: IMPL)
   - **L7**: Technical Specs (contains Layer 9: SPEC)
   - **L8**: Testing Layer (contains Layer 10: BDD)
   - **L9**: Task Management (contains Layer 11: TASKS)
   - **L10**: Session Planning (contains Layer 12: IPLAN)
   - **L11**: Code & Validation (contains Layers 13-15: Code, Tests, Validation)

   **Important**: Always use formal layer numbers (0-15) in:
   - Cumulative tagging implementations
   - Documentation references
   - Code comments
   - Traceability matrices
   ```

6. **Standardize Template Sections**
   - Review all *-TEMPLATE.md files
   - Decide on numbered vs non-numbered section format
   - Apply consistently (recommend: "## 7. Traceability" across all)

7. **Standardize Document Control Sections**
   - Define standard fields for all templates
   - Recommended fields: Status, Version, Date Created, Last Updated, Author, Document ID, Layer Number
   - Apply to all templates

8. **Fix ADR-000 Reference**
   - Check if `ADR-000_technology_stack.md` should exist
   - Either create file or update ADR-TEMPLATE.md line 93 to remove reference

#### Phase 3: Medium Priority (12-16 hours)

9. **Update Token Limit References**
   ```bash
   grep -r "10,000 token\|10K token" ai_dev_flow/ --include="*.md"
   # Update to current limits from TOOL_OPTIMIZATION_GUIDE.md
   ```

10. **Create Validation Script**
    Create `validate_documentation_consistency.py`:
    ```python
    #!/usr/bin/env python3
    """
    Documentation Consistency Validation Script
    Checks for:
    - Broken markdown links
    - Layer number reference consistency
    - Template reference validity
    - Deprecated terminology usage
    """

    import os
    import re
    from pathlib import Path

    def validate_markdown_links(directory):
        """Check all markdown links resolve to existing files"""
        pass

    def check_layer_references(directory):
        """Verify layer number references match formal 0-15 scheme"""
        pass

    def validate_template_refs(directory):
        """Check template references in README files match actual files"""
        pass

    def check_deprecated_terms(directory):
        """Find usage of deprecated terminology"""
        deprecated = ["TASKS_PLANS", "CONTRACTS/", "10,000 token"]
        pass

    if __name__ == "__main__":
        validate_markdown_links("./ai_dev_flow")
        check_layer_references("./ai_dev_flow")
        validate_template_refs("./ai_dev_flow")
        check_deprecated_terms("./ai_dev_flow")
    ```

11. **Run Validation and Fix Issues**
    ```bash
    python3 validate_documentation_consistency.py
    # Review output and fix any remaining issues
    ```

### Verification

#### Phase 1 Verification
- [ ] All links in index.md point to existing files
- [ ] BRD/README.md lists only existing templates
- [ ] All Mermaid diagrams have layer numbering clarification note
- [ ] No ambiguous "Implementation Plans" references remain
- [ ] SPEC_DRIVEN_DEVELOPMENT_GUIDE.md uses generic example placeholders

#### Phase 2 Verification
- [ ] Layer mapping table present in README.md and TRACEABILITY.md
- [ ] All templates use consistent section numbering
- [ ] All templates have standardized Document Control sections
- [ ] ADR-000 reference issue resolved

#### Phase 3 Verification
- [ ] No references to "10,000 token" or "10K token" limits remain
- [ ] Validation script runs without errors
- [ ] All broken internal links fixed

### Git Workflow
```bash
# Before starting
cd /opt/data/docs_flow_framework
git status  # Ensure clean working tree
git checkout -b fix-documentation-inconsistencies

# After Phase 1
git add ai_dev_flow/index.md ai_dev_flow/BRD/README.md ai_dev_flow/TRACEABILITY.md ai_dev_flow/README.md ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
git commit -m "fix(docs): Phase 1 - Fix critical documentation inconsistencies

- Remove references to non-existent BRD templates
- Add layer numbering clarification to Mermaid diagrams
- Standardize Implementation Plans terminology
- Replace missing example references with generic placeholders

Fixes 12 critical issues identified in documentation review.
"

# After Phase 2
git add ai_dev_flow/README.md ai_dev_flow/TRACEABILITY.md ai_dev_flow/*/\*-TEMPLATE.md
git commit -m "fix(docs): Phase 2 - Standardize templates and add layer mapping

- Add comprehensive layer mapping table (formal vs Mermaid)
- Standardize Traceability section numbering across templates
- Standardize Document Control fields
- Fix ADR-000 technology stack reference

Fixes 18 high-priority issues.
"

# After Phase 3
git add ai_dev_flow/ validate_documentation_consistency.py
git commit -m "fix(docs): Phase 3 - Update token limits and add validation

- Update all token limit references to current standards
- Create documentation consistency validation script
- Fix remaining broken internal links

Fixes 12 medium-priority issues.
"

# Create PR
git push origin fix-documentation-inconsistencies
```

## References

### Related Files
- **Review Report**: Conversation history contains full 47-issue analysis
- **Framework Documentation**: `/opt/data/docs_flow_framework/ai_dev_flow/`
- **ID Naming Standards**: `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`
- **Tool Optimization Guide**: `/opt/data/docs_flow_framework/ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md`

### Key Documents to Update
```
ai_dev_flow/index.md
ai_dev_flow/README.md
ai_dev_flow/TRACEABILITY.md
ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
ai_dev_flow/QUICK_REFERENCE.md
ai_dev_flow/BRD/README.md
ai_dev_flow/ADR/ADR-TEMPLATE.md
ai_dev_flow/BRD/BRD-TEMPLATE.md
ai_dev_flow/REQ/REQ-TEMPLATE.md
ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md
ai_dev_flow/TASKS/TASKS-TEMPLATE.md
ai_dev_flow/SPEC/SPEC-TEMPLATE.md
ai_dev_flow/EARS/EARS-TEMPLATE.md
ai_dev_flow/PRD/PRD-TEMPLATE.md
```

### Issue Categories Summary
| Category | Count | Severity | Phase |
|----------|-------|----------|-------|
| Incorrect file references | 4 | Critical/High | 1 |
| Inconsistent terminology | 3 | High | 1 |
| Broken cross-references | 3 | Medium | 3 |
| Template inconsistencies | 3 | Medium | 2 |
| Naming convention violations | 1 | Low | 4 |
| Layer numbering issues | 3 | Critical/High | 1, 2 |
| Outdated instructions | 3 | Medium | 3 |
| Missing/incorrect metadata | 2 | Medium | 2 |

## Estimated Effort

- **Phase 1**: 4-6 hours
- **Phase 2**: 8-12 hours
- **Phase 3**: 12-16 hours
- **Phase 4**: 4-6 hours (future)

**Total for Phases 1-3**: 24-34 hours

## Success Criteria

1. All broken file references resolved
2. Layer numbering confusion eliminated with clear mapping table
3. Consistent terminology across all documentation
4. All templates follow standardized format
5. Validation script runs clean
6. No references to deprecated naming conventions
7. Token limits updated to current standards

## Notes

- **User Decision**: Skip @tags format standardization (not needed for current scope)
- **Approach**: Use generic placeholders for examples rather than creating specific example files
- **Priority**: Focus on Phases 1-3; Phase 4 can be future maintenance
- **Testing**: Run validation script after each phase to catch issues early
