# SDD v3 Migration Plan

## Summary

SDD v3 collapses the 14-layer framework into **7 document layers + Code**:

```
v2 (14 layers):                  v3 (7 layers):
BRD (L1)                         BRD (L1)
PRD (L2)                         PRD (L2)
EARS (L3)                        EARS (L3)
BDD (L4)                         BDD (L4)
ADR (L5)                         ADR (L5)
SYS (L6)    ──cut──              TDD (L6)    ← NEW: lightweight TDD guide
REQ (L7)    ──cut──              SPEC (L7)
CTR (L8)    ──cut──              Code
SPEC (L9)   ──► L7
TSPEC (L10) ──cut──
TASKS (L11) ──cut──
CODE (L12)  ──► Code
TESTS (L13) ──cut──
VALID (L14) ──cut──
```

## What Gets Cut (and Why)

| Layer | Reason for Removal |
|-------|-------------------|
| SYS (L6) | ADR captures architectural decisions; PRD captures scope. SYS repackages both. |
| REQ (L7) | EARS + BDD provide sufficient requirement granularity for most projects. |
| CTR (L8) | Only needed for multi-team API contracts. Single-team projects skip it. |
| TSPEC (L10) | Replaced by lightweight TDD layer (L6). 42-file TSPEC v1 is excessive. |
| TASKS (L11) | AI generates implementation tasks from SPEC on-the-fly. |
| TESTS (L13) | Test files are code, not documentation. TDD layer defines test contracts. |
| VALIDATION (L14) | Validation gates embedded in each document's readiness score. |

## Document Reduction

| Metric | v2 | v3 | Delta |
|--------|----|----|-------|
| Document layers | 14 | 7 | -50% |
| Template files | 20+ (incl. subtypes) | 9 | -55% |
| Cumulative tag bloat | 14 tags at deepest | 6 tags at deepest | -57% |
| Traceability chain length | BRD→PRD→EARS→BDD→ADR→SYS→REQ→CTR→SPEC→TSPEC→TASKS→CODE | BRD→PRD→EARS→BDD→ADR→TDD→SPEC→Code | -33% |

## What Gets Copied (Modified)

| Source (ai_dev_ssd_flow/) | Target (ai_dev_flow_v3/) | Changes |
|---------------------------|--------------------------|---------|
| 01_BRD/BRD-TEMPLATE.yaml | 01_BRD/BRD-TEMPLATE.yaml | Update downstream: PRD→EARS→BDD→ADR→TDD→SPEC. Drop SYS/REQ/CTR/TSPEC/TASKS refs. |
| 01_BRD/BRD-00_index.md | 01_BRD/BRD-00_index.md | Rewrite for 7-layer flow |
| 02_PRD/PRD-TEMPLATE.yaml | 02_PRD/PRD-TEMPLATE.yaml | Update upstream/downstream chain |
| 03_EARS/EARS-TEMPLATE.yaml | 03_EARS/EARS-TEMPLATE.yaml | Update chain |
| 04_BDD/BDD-TEMPLATE.yaml | 04_BDD/BDD-TEMPLATE.yaml | Update chain; add TDD downstream ref |
| 05_ADR/ADR-TEMPLATE.yaml | 05_ADR/ADR-TEMPLATE.yaml | Update chain; TDD replaces SYS as downstream |
| LAYER_REGISTRY.yaml | LAYER_REGISTRY.yaml | Rewrite for 7 layers |
| ID_NAMING_STANDARDS.md | ID_NAMING_STANDARDS.md | Strip SYS/REQ/CTR/TSPEC/TASKS/CHG refs |
| TRACEABILITY.md | TRACEABILITY.md | Rewrite traceability chain |
| THRESHOLD_NAMING_RULES.md | THRESHOLD_NAMING_RULES.md | Copy as-is |
| DIAGRAM_STANDARDS.md | DIAGRAM_STANDARDS.md | Copy as-is |
| SPEC_DRIVEN_DEVELOPMENT_GUIDE.md | SPEC_DRIVEN_DEVELOPMENT_GUIDE.md | Rewrite for 7-layer workflow |
| TESTING_STRATEGY_TDD.md | TESTING_STRATEGY_TDD.md | Adapt for new TDD layer |
| METADATA_TAGGING_GUIDE.md | METADATA_TAGGING_GUIDE.md | Simplify for 7 artifact types |
| QUICK_REFERENCE.md | QUICK_REFERENCE.md | Rewrite |

## What Gets Created New

| File | Description |
|------|-------------|
| 06_TDD/TDD-TEMPLATE.yaml | Lightweight TDD guide: test pyramid, BDD→test mapping, thresholds, test file ordering |
| 06_TDD/TDD-00_index.md | TDD index |
| 06_TDD/README.md | TDD layer README |
| 07_SPEC/SPEC-TEMPLATE.yaml | Simplified SPEC: unified v1.0 metadata model, upstream from TDD+ADR, no REQ/CTR/SYS refs |
| 07_SPEC/SPEC-00_index.md | SPEC index for v3 |
| 07_SPEC/README.md | SPEC layer README |
| README.md | v3 framework entry point |
| DOC_GOVERNANCE_CORE.md | Simplified doc governance |
| AI_ASSISTANT_RULES.md | Simplified AI rules |

## What Gets Dropped

| Dropped | Reason |
|---------|--------|
| 00_REF/ | Optional reference docs; don't participate in 7-layer chain |
| 06_SYS/, 07_REQ/, 08_CTR/ | Cut layers |
| 09_SPEC/ subtypes (CSPEC, DSPEC, UXSPEC, RISKSPEC, PROCSPEC) | Excessive subtype fragmentation; SPEC is unified |
| 10_TSPEC/ with 6 subtypes | Replaced by single 06_TDD/ |
| 11_TASKS/ | AI generates tasks from SPEC |
| CHG/ | Change management is project-level concern, not framework |
| PROJECT/ | Project-specific templates |
| archived/ | Not needed for clean v3 |
| tmp/ | Development artifacts |
| All 30+ root reference docs not in the "copied" list above | Unnecessary bloat for simplified framework |

## Traceability Chain (v3)

```
BRD ──► PRD ──► EARS ──► BDD ──► ADR ──► TDD ──► SPEC ──► Code
 @brd   @brd   @brd    @brd   @brd   @brd   @brd
        @prd   @prd    @prd   @prd   @prd   @prd
               @ears   @ears  @ears  @ears  @ears
                       @bdd   @bdd   @bdd   @bdd
                              @adr   @adr   @adr
                                     @tdd   @tdd
                                            @spec
```

Maximum 6 cumulative tags at SPEC layer (vs 14 in v2).

## TDD Layer Design (Critical Decision)

The TDD layer is a **single document per SPEC component**, NOT a suite of 6 subtypes.

Template sections:
1. **Test Pyramid** — pyramid diagram with type distribution (unit 70%, integration 20%, e2e 10%)
2. **BDD Scenario Mapping** — each BDD scenario maps to test type + test file path
3. **Test File Order** — declaration order for TDD execution (test file → implementation file)
4. **Thresholds** — pass/fail criteria per test type
5. **Traceability** — upstream BDD + ADR, downstream SPEC

This replaces the 42-file TSPEC v1 archive with a single 80-line template.
