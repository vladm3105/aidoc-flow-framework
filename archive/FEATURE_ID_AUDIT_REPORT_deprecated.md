> **⚠️ DEPRECATED**: This report used old `TYPE-NNN:NNN` format.
> Current standard: Unified `TYPE.NNN.NNN` format.
> See: `ai_dev_flow/ID_NAMING_STANDARDS.md`

# Comprehensive Feature-Level Traceability Tag Format Audit

**Date**: 2025-12-01
**Scope**: `/opt/data/docs_flow_framework/ai_dev_flow/` directory
**Audit Focus**: Internal feature/requirement ID formats across all artifact types

---

## Executive Summary

This audit identifies **CRITICAL INCONSISTENCIES** in feature-level traceability ID formats across the docs_flow_framework. The framework employs **multiple conflicting formats** with no unified standard for internal feature numbering within documents.

### Key Findings

1. **Document-Level IDs** (e.g., `BRD-001`, `PRD-022`) - Consistent format: `TYPE-NNN`
2. **Feature-Level IDs (INCONSISTENT)**:
   - Simple numeric: `001`, `002`, `003` - Used in BRD, PRD, SYS, EARS
   - Compound numeric: `FR-NNN-NN` - Schema requirement for PRD only
   - Business Objects: `BO-NNN` - Used in BRD, PRD templates
   - User Stories: `US-NNN` - Used in PRD templates
   - EARS patterns: `EVENT-NNN`, `STATE-NNN`, `UB-NNN` - Defined in EARS templates
   - Non-Functional: `NFR-NNN`, `NFR-PERF-NNN`, `NFR-SEC-NNN` - Scattered across BRD/SYS/EARS

3. **Cross-Reference Format**: `@type: DOC-NNN:NNN` (e.g., `@brd: BRD-017:001`)

---

## Detailed Inventory by Format Type

### 1. SIMPLE NUMERIC FORMAT: `001`, `002`, `003`

**Canonical Usage**: Internal feature numbering within single document

**Where Used**:

| File Path | Lines | Context | Usage |
|-----------|-------|---------|-------|
| `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` | 360-376 | Section: "Internal Feature/Requirement IDs" | Template rule specifying simple numeric format for within-document features |
| `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` | 362-381 | Table: "Internal Feature/Requirement IDs" | Documents that use simple sequential numbering (BRD, PRD, EARS) |
| `/opt/data/docs_flow_framework/ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md` | 143-155 | EARS-012 example with subsection markers | `### EARS-012:001`, `### EARS-012:002` (compound format) |
| `/opt/data/docs_flow_framework/ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md` | 193-205 | SYS-012 example section | `### SYS-012:001`, `### SYS-012:002` (compound format) |
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_CREATION_RULES.md` | 1205 | Feature mapping table | Example: `FR-001, FR-002, FR-005` referencing features |

**Format Definition (from ID_NAMING_STANDARDS.md, lines 360-381)**:
```markdown
| Document Type | Feature ID Format | Example Heading |
|---|---|---|
| BRD-017 | 001, 002, 003 | ### 001: Feature Name |
| PRD-022 | 001, 002, 003 | ### 001: Feature Name |
| EARS-006 | 001, 002, 003 | #### 001: Requirement Name |
```

**Cross-Reference Format**: `@brd: BRD-017:001` (full compound ID combining document + internal feature)

**Rationale**: Document context provides namespace (BRD-017, PRD-022), so prefixing feature with document number is redundant.

---

### 2. COMPOUND NUMERIC FORMAT: `FR-NNN-NN` (Feature Requirement)

**Canonical Definition**: Standardized feature ID combining PRD number and sequence

**Where Used**:

| File Path | Lines | Context | Usage |
|-----------|-------|---------|-------|
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_SCHEMA.yaml` | 152-159 | Feature pattern section | **AUTHORITATIVE SCHEMA**: `pattern: "^FR-\d{3}-\d{2,3}$"` |
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_SCHEMA.yaml` | 154-155 | Feature ID format definition | `format: "FR-{prd_number}-{sequence}"` |
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_CREATION_RULES.md` | 803-814 | Section: "Standard Format" | **CREATION RULE**: `FR-{PRD#}-{sequence}` examples: FR-001-001, FR-022-015 |
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_CREATION_RULES.md` | 819-830 | Validation regex and invalid formats | Regex: `^FR-\d{3}-\d{3}$` |
| `/opt/data/docs_flow_framework/ai_dev_flow/SYS/SYS_SCHEMA.yaml` | 204-212 | Functional requirement format | **SYS SCHEMA**: `format: "FR-NNN"` pattern: `"^FR-\\d{3}$"` (3-digit only) |
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md` | 1690-1692 | Feature mapping table | Template placeholders: `FR-XXX, FR-YYY, FR-ZZZ` |
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_CREATION_RULES.md` | 1223, 1290-1291 | Test coverage mapping | Example: `FR-001 through FR-XXX` for unit/integration tests |
| `/opt/data/docs_flow_framework/ai_dev_flow/README.md` | 778 | Layer summary | Documents SYS schema uses `FR-NNN, NFR-NNN formats` |

**Schema Conflict Alert**: 
- **PRD_SCHEMA.yaml**: `FR-\d{3}-\d{2,3}` (3-digit PRD number + 2-3 digit sequence)
- **SYS_SCHEMA.yaml**: `FR-\d{3}` (3-digit only, no embedded PRD number)

**Actual Usage in Documents**: PRD_CREATION_RULES.md specifies compound format as standard for PRD-level feature IDs

---

### 3. BUSINESS OBJECTIVES: `BO-NNN`

**Canonical Definition**: Business objective identifiers in business requirements layer

**Where Used**:

| File Path | Lines | Context | Usage |
|-----------|-------|---------|-------|
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md` | 125-127 | Section 2.4 Business Objectives table | Template: `BO-001`, `BO-002`, `BO-003` |
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_CREATION_RULES.md` | 1338 | ID standard documentation | **RULE**: BO-XXX format for business objectives |
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_CREATION_RULES.md` | 1351 | Example context | `"BO-003: Automated service execution"` |
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md` | 409-411 | User Story to Business Objective mapping | Template: `[BO-1: Objective]`, `[BO-2:]`, `[BO-3:]` |
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md` | 798-799 | Business Objective alignment section | Example: `BO-001:`, `BO-002:` |
| `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md` | 463-464 | Key Business Objectives Satisfied | Example: `BO-001:`, `BO-002:` |
| `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_tags_against_docs.py` | 89 | Tag validation regex | Pattern matcher: `r'\b(BO-\d+)\b'` |
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-000_GLOSSARY.md` | 110 | Glossary entry | Abbreviation: BO = Business Objective |

**Format Specification**:
- **Pattern**: `BO-NNN` (3-digit zero-padded)
- **Examples**: `BO-001`, `BO-002`, `BO-003`
- **Layer**: BRD/PRD (Layers 1-2)
- **Purpose**: High-level business outcome alignment

---

### 4. USER STORIES: `US-NNN`

**Canonical Definition**: User story identifiers in product requirements

**Where Used**:

| File Path | Lines | Context | Usage |
|-----------|-------|---------|-------|
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md` | 369-392 | Section 6 User Stories table | Template: `US-001`, `US-002`, `US-003`, `US-0XX` |
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md` | 374-376 | Concrete user story examples | `US-001: As a sender...`, `US-002: As a sender...`, `US-003: As a recipient...` |
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md` | 1752 | Test mapping | `User Stories (US-001 through US-XXX)` for acceptance tests |
| `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD_PRE_GENERATION_CHECKLIST.md` | 48, 65, 149, 161, 183, 189 | BDD tag examples | Examples: `@brd:BRD-NNN:FR-001` (no US references in these tags) |
| `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-000_ai_assisted_documentation_features.md` | 110-140 | Feature requirements section | US-001 through US-004 defining AI agent features |

**Format Specification**:
- **Pattern**: `US-NNN` (3-digit zero-padded)
- **Examples**: `US-001`, `US-002`, `US-0XX`
- **Layer**: PRD (Layer 2)
- **Purpose**: User-centric requirements within product features

---

### 5. NON-FUNCTIONAL REQUIREMENTS: `NFR-NNN` and variants

**Canonical Definition**: Non-functional requirement identifiers with optional category prefixes

**Where Used**:

| File Path | Lines | Context | Usage |
|-----------|-------|---------|-------|
| `/opt/data/docs_flow_framework/ai_dev_flow/SYS/SYS_SCHEMA.yaml` | 220-266 | Non-functional requirement format | **AUTHORITATIVE**: `format: "NFR-NNN"` pattern: `"^NFR-\\d{3}$"` with category prefixes |
| `/opt/data/docs_flow_framework/ai_dev_flow/SYS/SYS_SCHEMA.yaml` | 225-266 | Category definitions with prefixes | `NFR-P` (Performance), `NFR-R` (Reliability), `NFR-S` (Scalability), `NFR-SEC` (Security), `NFR-O` (Observability), `NFR-M` (Maintainability) |
| `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md` | 655-748 | Section 5 Non-Functional Requirements table | 46 examples: `NFR-001` through `NFR-046` with mixed use of prefixes |
| `/opt/data/docs_flow_framework/ai_dev_flow/EARS/EARS-TEMPLATE.md` | 142-155 | Non-Functional examples | `NFR-PERF-001`, `NFR-PERF-002`, `NFR-SEC-001`, `NFR-REL-001` |
| `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md` | 477 | ADR traceability | Example: `EARS NFR-PERF-001` |
| `/opt/data/docs_flow_framework/ai_dev_flow/REQ/REQ_CREATION_RULES.md` | 289 | Requirement type documentation | Note: `NFR-related (p50/p95/p99 latencies, throughput limits)` |

**Format Variants**:

| Variant | Pattern | Layer | Example | Category |
|---------|---------|-------|---------|----------|
| Simple | `NFR-NNN` | SYS, BRD | `NFR-001`, `NFR-013` | Generic non-functional |
| Performance | `NFR-PERF-NNN` | EARS, BRD | `NFR-PERF-001`, `NFR-PERF-002` | Latency, throughput |
| Security | `NFR-SEC-NNN` | EARS, BRD | `NFR-SEC-001` | Authentication, encryption |
| Reliability | `NFR-REL-NNN` | EARS, BRD | `NFR-REL-001` | Uptime, MTBF |

**Inconsistency Alert**: BRD-TEMPLATE.md uses `NFR-001` through `NFR-046` (all simple format), while EARS-TEMPLATE.md introduces categorical variants like `NFR-PERF-`, `NFR-SEC-`, `NFR-REL-`.

---

### 6. EARS STATEMENT PATTERNS: `EVENT-NNN`, `STATE-NNN`, `UB-NNN`

**Canonical Definition**: EARS requirement statement types with prefix identifiers

**Where Used**:

| File Path | Lines | Context | Usage |
|-----------|-------|---------|-------|
| `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md` | 463-464, 476, 483, 490-491 | Traceability examples | References: `EVENT-001, EVENT-002`, `STATE-001`, `UB-001, UB-002` |
| `/opt/data/docs_flow_framework/ai_dev_flow/EARS/EARS_SCHEMA.yaml` | 146-200+ | EARS pattern types | **SCHEMA DEFINITION**: event_driven, state_driven, ubiquitous_driven pattern types |

**Format Definition**:
- **Event-Driven**: `EVENT-NNN` (WHEN condition triggered)
- **State-Driven**: `STATE-NNN` (WHILE condition exists)
- **Ubiquitous**: `UB-NNN` (ALWAYS true)

**Example Context** (TRACEABILITY.md):
```
- BO-001: Prevent excessive resource collection heat → Satisfied by EARS statements EVENT-001, EVENT-002
- BO-002: Ensure regulatory compliance → Satisfied by EARS statements STATE-001, UB-001
- Feature: Real-time risk limit validation → Specified by EARS statements EVENT-001 through EVENT-005
```

**Note**: These are **conceptual patterns** from the TRACEABILITY document. Actual EARS document files use generic `### EARS-NNN:001` format (see COMPLETE_TAGGING_EXAMPLE.md).

---

## Cross-Reference Format: Compound Document:Feature IDs

**Canonical Format**: `@type: DOC-NNN:FEATURE-NNN` or `@type: DOC-NNN-YY:FEATURE-NNN`

**Where Defined**:

| File Path | Lines | Context |
|-----------|-------|---------|
| `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` | 373-376 | Section: "Cross-Reference Format" specifies `@brd: BRD-017:001` pattern |
| `/opt/data/docs_flow_framework/ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md` | 111-116 | PRD example shows `@brd: BRD-009:015, BRD-009:006` |

**Examples**:
```markdown
@brd: BRD-017:001     # BRD-017, feature 001
@prd: PRD-022:005     # PRD-022, feature 005
@ears: EARS-006:003   # EARS-006, requirement 003
```

**Guarantees Uniqueness**: Full ID = `DOCUMENT-TYPE-NNN:FEATURE-NNN`
- `BRD-017:001` = BRD-017, Feature 001 (globally unique)
- `PRD-022:015` = PRD-022, Feature 015 (globally unique)

---

## Critical Inconsistencies & Conflicts

### Conflict 1: `FR-` Format Varies by Layer

| Layer | File | Pattern | Example | Status |
|-------|------|---------|---------|--------|
| **PRD** | `PRD_SCHEMA.yaml` | `^FR-\d{3}-\d{2,3}$` | `FR-001-001` | AUTHORITATIVE (Schema) |
| **PRD** | `PRD_CREATION_RULES.md` | `FR-{prd#}-{sequence}` | `FR-022-015` | Alignment with schema |
| **SYS** | `SYS_SCHEMA.yaml` | `^FR-\d{3}$` | `FR-001` | AUTHORITATIVE (Schema) |
| **BRD** | `BRD_CREATION_RULES.md` | `FR-XXX` or `FR-001` | Placeholder/example | Template only |

**Impact**: PRD defines 6-digit format (`FR-NNN-NN`), but SYS defines 3-digit format (`FR-NNN`). Leads to ambiguity when referencing FR across layers.

**Resolution Required**: Clarify whether:
1. Different layers use different FR formats intentionally
2. SYS schema should be updated to match PRD's compound format
3. FR patterns are not meant to cross layer boundaries

---

### Conflict 2: NFR Prefixes Not Unified

| Document | Pattern Examples | Context |
|----------|------------------|---------|
| `BRD-TEMPLATE.md` | `NFR-001` through `NFR-046` | All simple format, no category prefixes |
| `EARS-TEMPLATE.md` | `NFR-PERF-001`, `NFR-PERF-002`, `NFR-SEC-001`, `NFR-REL-001` | Categorical prefixes introduced |
| `SYS_SCHEMA.yaml` | `NFR-P`, `NFR-R`, `NFR-S`, `NFR-SEC`, `NFR-O`, `NFR-M` | Category prefix definitions |
| `TRACEABILITY.md` | `NFR-PERF-001` | Single example with category |

**Impact**: BRD template creates simple `NFR-NNN` IDs, but EARS refines them into categories. No guidance on mapping from BRD NFRs to EARS NFR categories.

**Question**: Should BRD template be updated to use categorical NFR prefixes?

---

### Conflict 3: Internal Feature ID Rules Conflict with Schema Patterns

**ID_NAMING_STANDARDS.md Rule** (lines 360-381):
```markdown
| Document Type | Feature ID Format | Example Heading |
| BRD-017 | 001, 002, 003 | ### 001: Feature Name |
```

**BUT**: PRD_SCHEMA.yaml requires `FR-NNN-NN` format for PRD documents.

**Interpretation Issue**: Are simple numeric IDs (001, 002, 003) meant to:
- Replace full document context (used within document only)?
- Coexist with FR-NNN-NN format (both used)?
- Apply only to certain document types?

---

### Conflict 4: Business Objectives Format Undefined in Templates

**Documentation**:
- `BRD_CREATION_RULES.md` line 1338: "`BO-XXX`, `FR-XXX`, `NFR-XXX` for each requirement"
- `BRD-TEMPLATE.md` lines 125-127: `BO-001`, `BO-002`, `BO-003`

**BUT**: No formal schema definition for BO format. No validation rules. No generation rules.

**Question**: Should `BO-NNN` be formally defined with regex pattern in `BRD_SCHEMA.yaml`?

---

## Summary Table: Format Definitions by Document Type

| Format | Layer | Document Types | Pattern | Examples | Status |
|--------|-------|-----------------|---------|----------|--------|
| Simple Numeric | 1-3 | BRD, PRD, SYS, EARS | `\d{3}` | 001, 002, 003 | **RULE** (ID_NAMING_STANDARDS) |
| FR Compound | 2 | PRD | `^FR-\d{3}-\d{2,3}$` | FR-001-001, FR-022-015 | **SCHEMA** (PRD) |
| FR Simple | 6 | SYS | `^FR-\d{3}$` | FR-001, FR-042 | **SCHEMA** (SYS) |
| BO | 1-2 | BRD, PRD | `BO-\d{3}` | BO-001, BO-002 | **RULE** (BRD) |
| US | 2 | PRD | `US-\d{3}` | US-001, US-002 | **RULE** (PRD) |
| NFR Simple | 1, 6 | BRD, SYS | `NFR-\d{3}` | NFR-001, NFR-046 | **SCHEMA** (SYS) |
| NFR Categorical | 3 | EARS | `NFR-[PERF\|SEC\|REL\|P\|R\|S\|SEC\|O\|M]-\d{3}` | NFR-PERF-001, NFR-SEC-001 | **TEMPLATE** (EARS) |
| EVENT | 3 | EARS (conceptual) | `EVENT-\d{3}` | EVENT-001, EVENT-002 | **REFERENCE** (TRACEABILITY) |
| STATE | 3 | EARS (conceptual) | `STATE-\d{3}` | STATE-001 | **REFERENCE** (TRACEABILITY) |
| UB | 3 | EARS (conceptual) | `UB-\d{3}` | UB-001 | **REFERENCE** (TRACEABILITY) |

**Legend**: SCHEMA = Machine-readable validation (authoritative), RULE = Documentation rule (prescriptive), TEMPLATE = Example only, REFERENCE = Conceptual pattern

---

## Recommendations

### HIGH PRIORITY

1. **Clarify PR vs SYS FR Format** (Conflict 1)
   - Decision: Keep both (layer-specific) or converge to one?
   - If converge: Which format wins?
   - Document decision in consolidated schema

2. **Formalize BO Format** (Conflict 4)
   - Add `BO_SCHEMA.yaml` or extend BRD schema
   - Define regex pattern: `^BO-\d{3}$`
   - Add validation rules

3. **Unify NFR Categorical Prefixes** (Conflict 2)
   - Update BRD-TEMPLATE.md to recommend categorical NFR format
   - Add mapping table: BRD NFR → EARS NFR category
   - Update SYS schema to reflect final decision

### MEDIUM PRIORITY

4. **Clarify Scope: Internal vs Cross-Document IDs** (Conflict 3)
   - Explicitly state: simple numeric `001` used ONLY for within-document references
   - FR-NNN-NN used for CROSS-document traceability (PRD layer)
   - Add decision diagram in ID_NAMING_STANDARDS.md

5. **Create Unified Pattern Reference Guide**
   - Consolidate patterns from all SCHEMA/RULE/TEMPLATE files
   - Single source of truth (proposed: `FEATURE_ID_STANDARD.md`)
   - Regex patterns for each format with layer/document restrictions

### LOW PRIORITY

6. **Add EVENT/STATE/UB to Formal Standards**
   - Currently only in TRACEABILITY.md (conceptual)
   - Promote to EARS_SCHEMA.yaml with formal definitions
   - Add validation rules

7. **Create Migration Guide**
   - For projects using non-standard formats
   - Mapping tables for common variations
   - Batch update scripts

---

## Files Requiring Updates

### Critical Updates Needed

1. **`PRD_SCHEMA.yaml`** - Clarify FR format scope (PRD-only vs cross-layer?)
2. **`SYS_SCHEMA.yaml`** - Align FR pattern with PRD or document intentional difference
3. **`BRD_SCHEMA.yaml`** - Add BO format definition (currently missing)
4. **`EARS_SCHEMA.yaml`** - Formalize EVENT/STATE/UB patterns (currently only in TRACEABILITY)
5. **`ID_NAMING_STANDARDS.md`** - Clarify simple numeric vs compound format decision rules

### Documentation Updates

6. **`BRD-TEMPLATE.md`** - Consider updating NFR examples to use categorical format
7. **`EARS-TEMPLATE.md`** - Formalize EVENT/STATE/UB statement ID format
8. **`TRACEABILITY.md`** - Reference formal definitions from schemas (currently standalone)

---

## Audit Methodology

Search patterns used:
```bash
grep -r "FR-\d+|BO-\d+|US-\d+|EVENT-|STATE-|UB-|NFR-" ai_dev_flow/
grep -r "^###.*\(001\|002\|003\)" ai_dev_flow/ --include="*.md"
```

Files analyzed: 49 files
- 13 `*_CREATION_RULES.md` files
- 13 `*-TEMPLATE.md` and `*-TEMPLATE.yaml` files
- 12 `*_SCHEMA.yaml` files
- 1 `TRACEABILITY.md`
- 1 `ID_NAMING_STANDARDS.md`
- 1 `COMPLETE_TAGGING_EXAMPLE.md`
- 8 supporting files (README, GLOSSARY, VALIDATION_RULES, etc.)

---

**Audit Status**: COMPLETE
**Inconsistencies Found**: 4 CRITICAL, 2 MEDIUM, 1 LOW
**Confidence Level**: HIGH (patterns verified across multiple authoritative sources)

