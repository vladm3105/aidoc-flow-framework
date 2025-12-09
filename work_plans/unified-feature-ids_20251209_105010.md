# Implementation Plan - Unified Feature ID System

**Created**: 2025-12-09 10:50:10 EST
**Status**: Ready for Implementation

## Objective

Create globally unique, unified feature IDs for AI and human tracking across docs_flow_framework and ibmcp repositories.

## Confirmed Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Separator** | Dot (`.`) | `BRD.017.001` - clean, unambiguous |
| **NFR Format** | Flatten to NNN | Maximum uniformity, no domain prefix |
| **Scope** | Both repos | Consistent framework across all projects |

## Key Changes from Current Standard

### Current (ID_NAMING_STANDARDS.md lines 360-421):
- Internal Feature ID: `NNN` (e.g., `### 001: Feature Name`)
- Cross-Reference: `@type: TYPE-NNN:NNN` (e.g., `@brd: BRD-017:001`)
- NFR Format: `NFR-{CAT}-NNN` (e.g., `NFR-PERF-001`)

### New Unified Format:
- Internal Feature ID: `NNN` (unchanged)
- Cross-Reference: `@type: TYPE.NNN.NNN` (e.g., `@brd: BRD.017.001`)
- NFR Format: `NNN` (flattened, no category prefix - use 900-series for NFRs)

---

## Current vs Proposed Format Comparison

| Aspect | Current System | Proposed Unified System |
|--------|----------------|------------------------|
| **Format** | `@type: TYPE-NNN:NNN` | `TYPE.NNN.NNN` |
| **Example** | `@brd: BRD-017:001` | `BRD.017.001` |
| **Feature ID standalone** | `001` (not unique) | `BRD.017.001` (globally unique) |
| **Regex pattern** | `@[a-z]+: [A-Z]+-\d+:\d+` | `[A-Z]+\.\d{3}\.\d{3}` |
| **Hierarchy** | Implicit (tag + doc + feature) | Explicit (TYPE.DOC.FEATURE) |
| **NFR handling** | `NFR-PERF-001` | `SYS.008.901` (flattened to NNN) |

---

## Proposed Unified Feature ID Format

### Format Specification

```
{TYPE}.{DOC_NUM}.{FEATURE_NUM}
```

| Component | Format | Example | Description |
|-----------|--------|---------|-------------|
| TYPE | 2-5 uppercase letters | `BRD`, `PRD`, `SYS` | Document type |
| DOC_NUM | 3-4 digits, zero-padded | `017`, `001`, `1000` | Document number |
| FEATURE_NUM | 3 digits, zero-padded | `001`, `030`, `105` | Feature within document |

### Examples by Document Type

| Document Type | Unified Feature ID | Meaning |
|---------------|-------------------|---------|
| BRD Objective | `BRD.017.001` | BRD-017, Objective 001 |
| PRD Feature | `PRD.022.015` | PRD-022, Feature 015 |
| EARS Statement | `EARS.006.003` | EARS-006, Statement 003 |
| SYS Requirement | `SYS.008.001` | SYS-008, Requirement 001 |
| REQ Atomic | `REQ.003.001` | REQ-003, Requirement 001 |
| ADR Decision | `ADR.033.001` | ADR-033, Decision Point 001 |

### NFR Handling (CONFIRMED: Flatten to NNN)

NFRs use the same `NNN` format as functional requirements. To distinguish NFRs:
- **Reserved ranges** (recommended): 900-999 for NFRs within each document
- **Or sequential**: Continue numbering from functional requirements

**Examples**:
| Old Format | New Unified Format | Meaning |
|------------|-------------------|---------|
| `NFR-PERF-001` | `SYS.008.901` | SYS-008, NFR #1 (900-series) |
| `NFR-SEC-002` | `SYS.008.902` | SYS-008, NFR #2 |
| `NFR-SCALE-003` | `SYS.008.903` | SYS-008, NFR #3 |

**Category tracking**: Use document metadata or comments to preserve category info (PERF, SEC, SCALE, etc.) if needed for reporting.

---

## Cross-Reference Format Update

### Current → Proposed

| Current | Proposed |
|---------|----------|
| `@brd: BRD-017:001` | `@brd: BRD.017.001` |
| `@prd: PRD-022:015` | `@prd: PRD.022.015` |
| `@sys: SYS-008:FR-001` | `@sys: SYS.008.001` |
| `@sys: SYS-008:NFR-PERF-001` | `@sys: SYS.008.901` |

### Traceability Tag Examples

```markdown
## 7. Traceability

### Upstream References
@brd: BRD.017.001, BRD.017.006
@prd: PRD.022.015
@ears: EARS.006.003
@sys: SYS.008.001, SYS.008.901
```

---

## Validation Rules

### Regex Pattern (Simplified)

```python
# Unified Feature ID pattern (all requirements including NFRs)
UNIFIED_FEATURE_ID_PATTERN = r'^[A-Z]{2,5}\.\d{3,4}\.\d{3}$'

# Examples that match:
# BRD.017.001, PRD.022.015, SYS.008.001, SYS.008.901
```

### AI Assistant Rules

1. **Always use unified format**: `TYPE.NNN.NNN` not `TYPE-NNN:NNN`
2. **Zero-pad all numbers**: `001` not `1`
3. **NFRs use 900-series**: `SYS.008.901` (not `NFR-PERF-001`)
4. **Validate on creation**: Check pattern match before saving
5. **Cross-reference format**: `@type: TYPE.NNN.NNN` (e.g., `@sys: SYS.008.001`)

---

## Files to Update

### Repository: `/opt/data/docs_flow_framework/`

**Core Documentation (5 files in ai_dev_flow/)**:
1. `ID_NAMING_STANDARDS.md` - Update sections:
   - Lines 360-382: "Internal Feature/Requirement IDs" - change `TYPE-NNN:NNN` to `TYPE.NNN.NNN`
   - Lines 385-421: "NFR Categorical Prefixes" - REMOVE section (flatten NFRs to simple NNN)
2. `TRACEABILITY.md` - Update cross-reference examples
3. `README.md` - Update feature-level tags table
4. `QUICK_REFERENCE.md` - Add Internal Feature IDs section
5. `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` - Add unified ID section

**Claude Skills (14 files in .claude/skills/doc-*/)**:
Add rule to each SKILL.md: "Always use unified format: TYPE.NNN.NNN not TYPE-NNN:NNN"
- `doc-brd/SKILL.md`
- `doc-prd/SKILL.md`
- `doc-ears/SKILL.md`
- `doc-bdd/SKILL.md`
- `doc-adr/SKILL.md`
- `doc-sys/SKILL.md`
- `doc-req/SKILL.md`
- `doc-impl/SKILL.md`
- `doc-ctr/SKILL.md`
- `doc-spec/SKILL.md`
- `doc-tasks/SKILL.md`
- `doc-iplan/SKILL.md`
- `doc-flow/SKILL.md`
- `doc-validator/SKILL.md`

**Document Templates (14 primary templates)**:
Update Section 7 (Traceability) examples to use unified format `TYPE.NNN.NNN`:
- `BRD/BRD-TEMPLATE.md`
- `PRD/PRD-TEMPLATE.md`
- `EARS/EARS-TEMPLATE.md`
- `ADR/ADR-TEMPLATE.md`
- `SYS/SYS-TEMPLATE.md`
- `REQ/REQ-TEMPLATE.md`
- `IMPL/IMPL-TEMPLATE.md`
- `CTR/CTR-TEMPLATE.md`
- `CTR/CTR-TEMPLATE.yaml`
- `SPEC/SPEC-TEMPLATE.md`
- `SPEC/SPEC-TEMPLATE.yaml`
- `TASKS/TASKS-TEMPLATE.md`
- `IPLAN/IPLAN-TEMPLATE.md`
- `ICON/ICON-TEMPLATE.md`

**Traceability Matrix Templates (13 files)**:
Update cross-reference examples to use unified format:
- `BRD/BRD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `PRD/PRD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `EARS/EARS-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `BDD/BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `ADR/ADR-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `SYS/SYS-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `IMPL/IMPL-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `CTR/CTR-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `SPEC/SPEC-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `TASKS/TASKS-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `IPLAN/IPLAN-000_TRACEABILITY_MATRIX-TEMPLATE.md`
- `ICON/ICON-000_TRACEABILITY_MATRIX-TEMPLATE.md`

### Copy to `/opt/data/ibmcp/ai_dev_flow/`
Mirror all core documentation changes (32 files: 5 core docs + 14 templates + 13 matrix templates)

---

## Implementation Plan

### Phase 1: Update ID_NAMING_STANDARDS.md (Authoritative Source)
Location: `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`

1. **Update "Internal Feature/Requirement IDs" section (lines 360-382)**:
   - Change cross-reference format from `@type: TYPE-NNN:NNN` to `@type: TYPE.NNN.NNN`
   - Update examples: `@brd: BRD-017:001` → `@brd: BRD.017.001`
   - Update uniqueness guarantee examples

2. **Replace "NFR Categorical Prefixes" section (lines 385-421)**:
   - Remove categorical prefix system (`NFR-PERF-NNN`, `NFR-SEC-NNN`, etc.)
   - Replace with: NFRs use 900-series numbering (e.g., `901`, `902`, `903`)
   - Update cross-reference format: `@sys: SYS.008.901` (not `@sys: SYS-008:NFR-PERF-001`)

3. **Add regex pattern for validation**:
   ```python
   UNIFIED_FEATURE_ID_PATTERN = r'^[A-Z]{2,5}\.\d{3,4}\.\d{3}$'
   ```

### Phase 2: Update Core Documentation
1. `TRACEABILITY.md` - Update all `TYPE-NNN:NNN` to `TYPE.NNN.NNN`
2. `README.md` - Update feature-level tags table
3. `QUICK_REFERENCE.md` - Add unified feature ID section
4. `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` - Add unified ID reference

### Phase 3: Update Claude Skills (14 doc-* skills)
Add to each `.claude/skills/doc-*/SKILL.md`:
```markdown
## Unified Feature ID Format (MANDATORY)

**Always use**: `TYPE.NNN.NNN` (dot separator)
**Never use**: `TYPE-NNN:NNN` (colon separator - DEPRECATED)

Examples:
- `@brd: BRD.017.001` ✅
- `@brd: BRD-017:001` ❌

NFRs use 900-series: `SYS.008.901` (not `NFR-PERF-001`)
```

### Phase 4: Update Document Templates (14 files)
Update Section 7 (Traceability) examples in each template:
- Change `@type: TYPE-NNN:NNN` → `@type: TYPE.NNN.NNN`
- Change NFR format examples from `NFR-{CAT}-NNN` → `NNN` (900-series)

### Phase 5: Update Traceability Matrix Templates (13 files)
Update cross-reference examples in each matrix template:
- Change feature-level references to unified format

### Phase 6: Mirror to ibmcp
Copy updated files to `/opt/data/ibmcp/ai_dev_flow/`

### Phase 7: Validation
1. Grep for old format `TYPE-NNN:NNN` - should find zero matches in updated files
2. Verify all `doc-*` skills have unified format rule
3. Verify all templates use unified format in examples

---

## Execution Order

```
/opt/data/docs_flow_framework/
├── ai_dev_flow/
│   ├── 1. ID_NAMING_STANDARDS.md (authoritative)
│   ├── 2. TRACEABILITY.md
│   ├── 3. README.md
│   ├── 4. QUICK_REFERENCE.md
│   ├── 5. SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
│   ├── 6-19. */*-TEMPLATE.md (14 document templates)
│   └── 20-32. */*_TRACEABILITY_MATRIX-TEMPLATE.md (13 matrix templates)
└── .claude/skills/
    └── 33-46. doc-*/SKILL.md (14 skills)

/opt/data/ibmcp/ai_dev_flow/
└── 47-78. Mirror all updated files (32 files)
```

**Total files**: 78 files
- docs_flow_framework: 46 files (5 core docs + 14 templates + 13 matrix templates + 14 skills)
- ibmcp: 32 files (mirror of core docs + templates + matrix templates)

---

## Verification

- [ ] No occurrences of old format `TYPE-NNN:NNN` in updated files
- [ ] All 14 doc-* skills have unified format rule
- [ ] All 14 document templates use unified format in Section 7
- [ ] All 13 matrix templates use unified format in examples
- [ ] ibmcp files match docs_flow_framework

---

## References

- Authoritative source: `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`
- Related: `TRACEABILITY.md`, `QUICK_REFERENCE.md`
- Previous work: `traceability-rules-update_20251208_210250_COMPLETED.md`
