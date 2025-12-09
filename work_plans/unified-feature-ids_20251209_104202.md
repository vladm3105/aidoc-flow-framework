# Unified Feature ID System - Implementation Plan

**Date**: 2025-12-09
**Scope**: `/opt/data/docs_flow_framework/` (primary), then copy to `/opt/data/ibmcp/`
**Goal**: Create globally unique, unified feature IDs for AI and human tracking
**Status**: APPROVED - Ready for Implementation

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

### Copy to `/opt/data/ibmcp/ai_dev_flow/`
Mirror all core documentation changes (5 files)

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

### Phase 4: Mirror to ibmcp
Copy updated files to `/opt/data/ibmcp/ai_dev_flow/`

### Phase 5: Validation
1. Grep for old format `TYPE-NNN:NNN` - should find zero matches in updated files
2. Verify all `doc-*` skills have unified format rule

---

## Execution Order

```
/opt/data/docs_flow_framework/
├── ai_dev_flow/
│   ├── 1. ID_NAMING_STANDARDS.md (authoritative)
│   ├── 2. TRACEABILITY.md
│   ├── 3. README.md
│   ├── 4. QUICK_REFERENCE.md
│   └── 5. SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
└── .claude/skills/
    └── 6-19. doc-*/SKILL.md (14 files)

/opt/data/ibmcp/ai_dev_flow/
└── 20-24. Mirror core docs (5 files)
```

**Total files**: 24 files (19 in docs_flow_framework, 5 in ibmcp)
