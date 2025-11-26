# Implementation Plan - BRD/PRD Template Refactoring & Layer Separation

**Created**: 2025-11-26 09:08:09 EST
**Updated**: 2025-11-26 09:30:12 EST
**Status**: Phase 1 & 2 Complete - Continue in Next Session
**Project**: docs_flow_framework
**Location**: `/opt/data/docs_flow_framework/`

## Progress Summary

### ✅ COMPLETED (Session 1 - 2025-11-26)

#### Phase 2: Appendix Reorganization - Teaching Materials (COMPLETE)
- ✅ Extracted Appendix C → `BRD/FR_EXAMPLES_GUIDE.md` (created in previous session)
- ✅ Extracted Appendix B → `EARS-TEMPLATE.md` Section 5.6 (192 lines)
  - Added comprehensive business vs technical requirements boundary guidance
  - 8 categories of exclusions, 7 categories of inclusions
  - 3 edge cases with examples, 5 quick self-check questions
- ✅ Added quick self-check questions to `BDD-TEMPLATE.feature` header (23 lines)
- ✅ Updated BRD Appendix B to summary + reference links (~40 lines)
- ✅ Updated BRD Appendix C to summary + reference link (~25 lines)
- ✅ Removed duplicate content (lines 1914-2429 deleted)
- ✅ Verified BRD token count reduction

#### Phase 1: Content Redistribution - User Stories & Stakeholders (COMPLETE)
- ✅ Created PRD "User Stories & User Roles" section (76 lines total)
  - User Story Format subsection
  - Primary User Stories tables (2 personas)
  - Operational User Stories table
  - User Story Summary statistics table
  - User Story to Business Objective Mapping table
  - User Roles and Permissions table with 5 example roles
- ✅ Simplified BRD Section 5 (User Stories) to high-level summary
  - Replaced 61 lines with 36-line summary
  - Added reference link to PRD section
  - Key User Story Categories (Primary Users, Internal Operations)
  - Summary statistics only (no detailed tables)
  - High-level Business Objective alignment
- ✅ Simplified BRD Section 6.4 (User Roles) to high-level
  - Replaced detailed table with 12-line summary
  - Added reference link to PRD section
  - Lists 3-5 primary role categories only
- ✅ Simplified BRD Section 4 (Stakeholders) with PRD reference
  - Replaced 2 tables with 15-line summary
  - Added reference link to PRD Stakeholders & Communication section
  - Primary stakeholders list only (3-5 key decision-makers)

#### Phase 3: Product Appendices (PARTIAL)
- ✅ Identified Appendix N (Customer Communication Templates) at line 2008
- ⏸️ Appendices E, F not found in current template (do not exist)
- ⏸️ Deferred: Move Appendix N to PRD (for next session)

### 📊 Token Reduction Achieved

| Metric | Value |
|--------|-------|
| **Baseline** | 24,469 tokens |
| **Current** | 21,382 tokens |
| **Reduction** | 3,087 tokens (12.6%) |
| **Target** | 15,000 tokens |
| **Remaining** | 6,382 tokens to reduce |
| **Progress** | 32.6% of total goal |

### 📁 Files Modified

1. **BRD-TEMPLATE.md** - Sections 4, 5, 6.4, Appendices B & C simplified
   - Lines: 2,098
   - Words: 13,780
   - Characters: 99,405
2. **PRD-TEMPLATE.md** - Added "User Stories & User Roles" section
3. **EARS-TEMPLATE.md** - Added Section 5.6 (192 lines)
4. **BDD-TEMPLATE.feature** - Added quick-check header (23 lines)
5. **FR_EXAMPLES_GUIDE.md** - Created in previous session (~5,000 tokens)

### 🔄 Analysis of Results

**Phase 2 Success Factors:**
- Teaching materials successfully extracted to reference guides
- Proper bidirectional cross-references established
- Content available but not bloating main template

**Phase 1 Success Factors:**
- Clear layer separation (business in BRD, product in PRD)
- Maintained traceability through reference links
- PRD now has comprehensive user story guidance

**Token Reduction Below Target Because:**
- Summaries retained significant instructional content
- Reference links with context consume tokens
- Cross-reference explanations needed for clarity
- Example snippets kept for immediate guidance

**Path to 15,000 Token Target:**
- Move Appendix N to PRD: ~500 tokens
- Shorten inline examples in Sections 3.6, 3.7: ~1,000 tokens
- Consolidate repeated pattern explanations: ~500 tokens
- Move additional teaching content to guides: ~4,000 tokens
- **Total potential**: ~6,000 tokens (achieves target)

---

## 🎯 REMAINING WORK (Next Session)

### Phase 3: Product Appendices Relocation (PENDING)

**Appendix N Analysis:**
- Location: Lines 2008-2037 in BRD-TEMPLATE.md
- Content: Customer Communication Templates (transaction status, errors, promotional)
- Size: ~30 lines, ~500 tokens estimated
- Rationale: Product-level messaging, belongs in PRD

**Tasks:**
- [ ] Create PRD Section "Customer-Facing Content & Messaging"
  - [ ] Subsection: Transaction Status Messages
  - [ ] Subsection: Error Messages
  - [ ] Subsection: Promotional Messages
- [ ] Move BRD Appendix N content to PRD
- [ ] Replace BRD Appendix N with reference link to PRD
- [ ] Update appendix lettering (shift O → N)
- [ ] **Estimated Token Impact**: BRD -500, PRD +500

**Other Product Appendices** (Note: E & F do not exist in current template):
- Appendix K (Fee Schedule): KEEP in BRD (business-level)
- Appendix L (Partner SLA): KEEP in BRD (business-level)
- Appendix M (Regulatory Matrix): KEEP in BRD (business-level)
- Appendix O (Business Metrics): KEEP in BRD (business-level)

### Phase 4: Document ID Generalization (PENDING)

- [ ] Replace specific IDs in BRD template
  - [ ] `BRD-001` through `BRD-009` → `BRD-NNN` or `[Platform_BRD-001]`
  - [ ] `FR-001, FR-002, FR-003` → `FR-NNN`
  - [ ] `US-001, US-002` → `US-NNN`
  - [ ] `NFR-001` → `NFR-NNN`
  - [ ] Keep specific IDs only in FR_EXAMPLES_GUIDE.md (teaching examples)
- [ ] Verify PRD template (already uses generic patterns)
- [ ] Update EARS/BDD traceability patterns
  - [ ] Ensure `@brd: BRD-NNN:FR-NNN` format
  - [ ] Ensure `@prd: PRD-NNN:FR-NNN` format
- [ ] Update `ID_NAMING_STANDARDS.md`
  - [ ] Document generic placeholder patterns
  - [ ] Document semantic labels ([Platform_BRD], [Feature_BRD])
- [ ] **Token Impact**: Neutral (same content, better portability)

### Phase 5: Creation & Validation Rules Updates (PENDING)

**BRD_CREATION_RULES.md:**
- [ ] Update Section 4 guidance (simplified stakeholders, business-level only)
- [ ] Remove Section 5 guidance (User Stories moved to PRD)
- [ ] Update section count: "19 Sections" → "18 Sections"
- [ ] Add Appendix K-M creation guidance (Fee Schedule, Partner SLA, Regulatory Matrix)
- [ ] Fix Executive Summary alignment (3-paragraph pattern vs 6 elements)
- [ ] Update all document ID references to generic patterns

**BRD_VALIDATION_RULES.md:**
- [ ] Update CHECK 1: Validate 18 sections (not 19)
- [ ] Remove CHECK 20: User Stories validation (moved to PRD)
- [ ] Remove CHECK 21: User Roles validation (moved to PRD)
- [ ] Add CHECK 25-27: Specialized appendix validation by BRD type
- [ ] Update all CHECK references to use generalized IDs

**PRD_CREATION_RULES.md** (may need to create):
- [ ] Add Section "User Stories & User Roles" creation guidance
  - [ ] User story derivation from business objectives
  - [ ] Story ID numbering (US-001+)
  - [ ] FR linkage methodology
  - [ ] Business objective mapping process
  - [ ] Role identification methodology
  - [ ] Permission matrix construction
- [ ] Add Stakeholder Analysis guidance
  - [ ] Stakeholder identification methodology
  - [ ] Interest/Influence level criteria
  - [ ] Engagement strategy patterns

**PRD_VALIDATION_RULES.md** (may need to create):
- [ ] Add CHECK: User Stories format (US-NNN pattern)
- [ ] Add CHECK: User Story to FR traceability
- [ ] Add CHECK: User Roles table completeness
- [ ] Add CHECK: User Story to Business Objective mapping

### Phase 6: SDD Guide & Cross-References Update (PENDING)

**SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:**
- [ ] Update Layer 1 (BRD) description
  - [ ] Clarify: business-level FRs, stakeholder groups (NOT user stories/roles)
  - [ ] Add note: "User stories defined in downstream PRD"
- [ ] Update Layer 2 (PRD) description
  - [ ] Expand: user stories, user roles, product features
  - [ ] Add note: "Derived from Business Objectives in upstream BRD-NNN"
- [ ] Update Principles - Complete Traceability
  - [ ] Add: user story derivation chain (BO→US→FR)
- [ ] Update token limit guidance
  - [ ] "BRD optimized to ~15K tokens through modular appendices"

**Template Cross-References:**
- [ ] BRD Section 1.4: Add note "User stories defined in downstream PRD"
- [ ] PRD Section header: Add note "Derived from Business Objectives in upstream BRD-NNN"
- [ ] EARS Section 7: Update traceability pattern to include user stories
- [ ] BDD header: Update cumulative tags to include `@user-story: US-NNN`

**Optional - Migration Guide:**
- [ ] Create `TEMPLATE_MIGRATION_GUIDE.md`
- [ ] Document how to convert old BRDs (with user stories) to new structure
- [ ] Provide mapping table: Old Section → New Template Location

### Additional Token Reduction Opportunities (For 15K Target)

**High-Impact Reductions (~4,000 tokens):**
- [ ] Shorten Section 3.6 (Technology Stack Prerequisites) examples
  - Current: 3 full example blocks (Platform, Feature Full, Feature Abbreviated)
  - Proposed: 1 compact example + reference to example BRD
  - Savings: ~800 tokens
- [ ] Shorten Section 3.7 (Mandatory Technology Conditions) examples
  - Current: 3 full example blocks with detailed impact analysis
  - Proposed: 1 compact example + reference to example BRD
  - Savings: ~800 tokens
- [ ] Extract Section 6.2 (FR Structure) detailed guidance → FR_EXAMPLES_GUIDE.md
  - Current: ~50 lines of inline FR formatting guidance
  - Proposed: Reference link to FR_EXAMPLES_GUIDE.md Section
  - Savings: ~1,000 tokens
- [ ] Consolidate Appendix pattern explanations
  - Multiple appendices repeat "Purpose", "Structure", "Format" patterns
  - Proposed: Single Appendix Guidelines section, appendices use compact format
  - Savings: ~1,500 tokens

**Medium-Impact Reductions (~1,500 tokens):**
- [ ] Shorten Section 2 (Business Objectives) inline examples
  - Keep 1-2 examples, move rest to example BRDs
  - Savings: ~300 tokens
- [ ] Shorten Section 7 (NFR) inline examples across subsections
  - 8 NFR subsections each with examples
  - Proposed: 1-2 key examples total, reference example BRDs
  - Savings: ~800 tokens
- [ ] Consolidate traceability tag explanations
  - Repeated across multiple sections
  - Proposed: Single section reference
  - Savings: ~400 tokens

---

## Execution Guide for Next Session

### Recommended Order

**1. Complete Phase 3 (30 minutes)**
- Move Appendix N to PRD
- Update cross-references
- Verify token reduction

**2. Apply Additional Token Reductions (1-2 hours)**
- Shorten Sections 3.6, 3.7 examples
- Extract Section 6.2 guidance to FR_EXAMPLES_GUIDE.md
- Consolidate appendix patterns
- Target: Reduce BRD by additional 3,000-4,000 tokens

**3. Verify Token Target Achieved (15 minutes)**
- Measure BRD token count
- Confirm ≤ 15,000 tokens
- Document final metrics

**4. Complete Phase 4 (45 minutes)**
- Generalize all document IDs
- Update ID_NAMING_STANDARDS.md

**5. Complete Phase 5 (2 hours)**
- Update BRD_CREATION_RULES.md
- Update BRD_VALIDATION_RULES.md
- Create PRD_CREATION_RULES.md
- Create PRD_VALIDATION_RULES.md

**6. Complete Phase 6 (1 hour)**
- Update SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
- Update all template cross-references
- Optional: Create TEMPLATE_MIGRATION_GUIDE.md

**7. Final Validation (30 minutes)**
- Run markdown linter on all modified templates
- Verify all cross-references resolve
- Test token counts
- Create git commit with summary

### Session Resume Command

```bash
cd /opt/data/docs_flow_framework
# Review progress
cat work_plans/refactor-brd-prd-templates_20251126_090809_updated.md

# Check current state
wc -w -c -l ai_dev_flow/BRD/BRD-TEMPLATE.md
wc -w -c -l ai_dev_flow/PRD/PRD-TEMPLATE.md

# Continue with Phase 3: Move Appendix N
```

---

## Verification Checklist

### After Phase 3
- [ ] Appendix N moved to PRD
- [ ] BRD Appendix N replaced with reference link
- [ ] Appendix O renumbered to Appendix N
- [ ] All Appendix N cross-references updated
- [ ] Token count reduced by ~500 tokens

### After Additional Reductions
- [ ] BRD token count ≤ 15,000 tokens
- [ ] No content loss (all moved to reference guides)
- [ ] Cross-references intact

### After Phase 4
- [ ] No hardcoded document IDs (BRD-001, FR-001, etc.)
- [ ] Generic patterns used (BRD-NNN, FR-NNN)
- [ ] ID_NAMING_STANDARDS.md updated
- [ ] All traceability tags use generic format

### After Phase 5
- [ ] BRD_CREATION_RULES.md references 18 sections
- [ ] User story guidance removed from BRD rules
- [ ] User story guidance added to PRD rules
- [ ] All appendix types have creation guidance
- [ ] All specialized appendices have validation checks

### After Phase 6
- [ ] SPEC_DRIVEN_DEVELOPMENT_GUIDE.md layer descriptions accurate
- [ ] All template cross-references resolve
- [ ] User story derivation chain documented
- [ ] Token limits documented

### Final Validation
- [ ] Markdown linting passes (all templates)
- [ ] YAML frontmatter valid (all templates)
- [ ] Token counts within limits
- [ ] Layer separation enforced
- [ ] All cross-references resolve
- [ ] Rules aligned with templates

---

## Success Metrics

### Current Status
- ✅ Phase 1 Complete
- ✅ Phase 2 Complete
- ⏸️ Phase 3 Partial (Appendix N identified, not moved)
- ❌ Phase 4 Pending
- ❌ Phase 5 Pending
- ❌ Phase 6 Pending

### Target Metrics
- [ ] BRD token count ≤ 15,000 tokens (Current: 21,382)
- [ ] PRD token count ≤ 10,000 tokens (Current: unknown, needs measurement)
- [ ] All templates ≤ 50,000 token limit
- [ ] Zero hardcoded document IDs in templates
- [ ] All creation/validation rules aligned with templates
- [ ] Layer 1/Layer 2 separation enforced
- [ ] All cross-references resolve correctly
- [ ] Markdown linting passes with no errors

---

## Files Reference

### Modified Files (Session 1)
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/EARS/EARS-TEMPLATE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-TEMPLATE.feature`

### Created Files (Session 1)
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md.backup`

### Created Files (Previous Session)
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/FR_EXAMPLES_GUIDE.md`

### To Modify (Next Session)
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_CREATION_RULES.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_VALIDATION_RULES.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_CREATION_RULES.md` (create)
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_VALIDATION_RULES.md` (create)
- `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`

### Optional To Create (Next Session)
- `/opt/data/docs_flow_framework/ai_dev_flow/TEMPLATE_MIGRATION_GUIDE.md`

---

## Notes for Next Session

### Key Insights
1. **Token reduction requires aggressive extraction**: Summaries with context still consume significant tokens. Need to move more teaching content to reference guides.

2. **Cross-references are valuable but costly**: Each reference link with explanation adds ~30-50 tokens. Keep references but minimize explanatory text.

3. **Examples should live in example BRDs, not templates**: Templates should show format/structure only, full examples belong in actual BRD documents (e.g., BRD-009).

4. **Appendices E & F don't exist**: Work plan assumed these based on pattern, but current template doesn't have them. Only Appendix N needs moving.

5. **Phase order was correct**: Doing Phase 2 first (teaching extraction) before Phase 1 (content moves) worked well. Continue with Phase 3 next.

### Risks & Mitigation
- **Risk**: Aggressive token reduction might remove helpful guidance
  - **Mitigation**: All content moved to reference guides, not deleted

- **Risk**: Too many cross-references confuse users
  - **Mitigation**: Limit to 1 reference per section, use clear "📚 Complete X" format

- **Risk**: Rules updates might miss edge cases
  - **Mitigation**: Test with sample BRD/PRD creation before finalizing

### Estimated Remaining Effort
- Phase 3 completion: 30 minutes
- Additional token reductions: 1-2 hours
- Phase 4: 45 minutes
- Phase 5: 2 hours
- Phase 6: 1 hour
- Validation & testing: 30 minutes
- **Total**: 5-6 hours

---

**End of Progress Report**
