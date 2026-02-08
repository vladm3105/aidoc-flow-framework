---
name: doc-prd-autopilot
description: Automated PRD generation pipeline from BRD documents - analyzes dependencies, validates readiness, generates PRDs, performs final review, and supports parallel execution
tags:
  - sdd-workflow
  - automation
  - prd-generation
  - layer-2-artifact
  - shared-architecture
custom_fields:
  layer: 2
  artifact_type: PRD
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: automation-workflow
  upstream_artifacts: [BRD]
  downstream_artifacts: [EARS, BDD, ADR]
  version: "1.2"
---

# doc-prd-autopilot

## Purpose

Automated **Product Requirements Document (PRD)** generation pipeline that processes one or more BRD documents and generates their corresponding PRDs with dependency awareness, readiness validation, and parallel execution support.

**Layer**: 2 (PRD Generation)

**Upstream**: BRD (Layer 1)

**Downstream**: EARS (Layer 3), BDD (Layer 4), ADR (Layer 5)

---

## Skill Dependencies

This autopilot orchestrates the following skills:

| Skill | Purpose | Phase |
|-------|---------|-------|
| `doc-brd-validator` | Validate BRD PRD-Ready score | Phase 2: BRD Readiness |
| `doc-prd` | PRD creation rules, template, section structure | Phase 3: PRD Generation |
| `doc-prd-validator` | Validate PRD structure, content, EARS-Ready score | Phase 4: PRD Validation |
| `doc-prd-reviewer` | Final content review and quality assurance | Phase 5: Final Review |

**Delegation Principle**: The autopilot orchestrates workflow but delegates:
- PRD structure/content rules → `doc-prd` skill
- PRD validation logic → `doc-prd-validator` skill
- BRD validation logic → `doc-brd-validator` skill
- Final content review → `doc-prd-reviewer` skill (or inline review)

---

## When to Use This Skill

Use `doc-prd-autopilot` when:
- You have one or more completed BRD documents ready for PRD generation
- You want automated dependency analysis to determine optimal PRD creation order
- You need PRD-Ready score validation before generation
- You want automatic EARS-Ready score validation after PRD creation
- You need parallel PRD generation for independent BRDs

**Do NOT use when**:
- Creating a single PRD with extensive manual customization (use `doc-prd` instead)
- BRDs are incomplete or in Draft status
- You need fine-grained control over each PRD section

---

## 8-Step Autopilot Workflow

### Overview Diagram

```mermaid
flowchart TD
    subgraph Phase1["Phase 1: Dependency Analysis"]
        A[Input: BRD List] --> B[Analyze Dependencies]
        B --> C[Build Dependency Graph]
        C --> D[Topological Sort]
        D --> E[Define Creation Order]
    end

    subgraph Phase2["Phase 2: BRD Readiness"]
        E --> F{Next BRD}
        F --> G[Check PRD-Ready Score]
        G --> H{Score >= 90?}
        H -->|No| I[Auto-Fix Issues]
        I --> J[Re-validate]
        J --> H
        H -->|Yes| K[Mark BRD Ready]
    end

    subgraph Phase3["Phase 3: PRD Generation"]
        K --> L[Load BRD Content]
        L --> M[Apply PRD Template]
        M --> N[Generate PRD Sections]
        N --> O[Add Traceability Tags]
        O --> P[Write PRD Files]
    end

    subgraph Phase4["Phase 4: PRD Validation"]
        P --> Q[Check EARS-Ready Score]
        Q --> R{Score >= 90?}
        R -->|No| S[Auto-Fix PRD Issues]
        S --> T[Re-validate PRD]
        T --> R
        R -->|Yes| U[Validation Passed]
    end

    subgraph Phase5["Phase 5: Final Review"]
        U --> U1[Check Link Integrity]
        U1 --> U2[Verify Threshold Consistency]
        U2 --> U3[Validate BRD Alignment]
        U3 --> U4[Check Placeholder Text]
        U4 --> U5{Review Passed?}
        U5 -->|No| U6[Flag Issues]
        U6 --> U7[Auto-Fix or Manual]
        U7 --> U5
        U5 -->|Yes| U8[Mark PRD Complete]
    end

    subgraph Phase6["Phase 6: Parallel/Continue"]
        U8 --> V{More BRDs?}
        V -->|Yes| W{Independent?}
        W -->|Yes| X[Parallel Generation]
        W -->|No| F
        X --> F
        V -->|No| Y[Generate Summary Report]
    end

    Y --> Z[Complete]
```

### Step 1: Input BRD List

**Command Format**:
```
/doc-prd-autopilot <BRD_LIST>
```

**Input Options**:
- **Single BRD**: `BRD-01` or `docs/01_BRD/BRD-01_f1_iam/`
- **Multiple BRDs**: `BRD-01,BRD-02,BRD-03` (comma-separated)
- **All BRDs**: `all` or `*` (scan entire docs/01_BRD/ directory)
- **Pattern Match**: `BRD-0*` (glob patterns)

**Example Invocations**:
```bash
# Single BRD
/doc-prd-autopilot BRD-01

# Multiple specific BRDs
/doc-prd-autopilot BRD-01,BRD-02,BRD-05

# All available BRDs
/doc-prd-autopilot all

# Pattern match (foundation modules)
/doc-prd-autopilot BRD-0[1-7]
```

### Step 2: Dependency Analysis & Creation Order

The autopilot analyzes cross-BRD dependencies to determine optimal PRD creation order.

**Dependency Sources**:
1. **Explicit References**: `@depends-brd: BRD-NN` tags in BRD documents
2. **Cross-BRD References**: References to other BRDs in Traceability sections
3. **Module Dependencies**: Foundation module (F1-F7) vs Domain module (D1-D7) hierarchy
4. **Platform vs Feature**: Platform BRDs before Feature BRDs

**Algorithm**:
```python
def analyze_dependencies(brd_list):
    """
    1. Build directed graph of BRD dependencies
    2. Detect circular dependencies (error if found)
    3. Perform topological sort
    4. Group independent BRDs for parallel processing
    5. Return ordered execution plan
    """
    graph = build_dependency_graph(brd_list)

    if has_cycle(graph):
        raise CircularDependencyError()

    sorted_order = topological_sort(graph)
    parallel_groups = identify_independent_groups(sorted_order)

    return ExecutionPlan(sorted_order, parallel_groups)
```

**Output Example**:
```
Dependency Analysis Complete:
├── Execution Order: BRD-06 → BRD-07 → [BRD-01, BRD-02] → BRD-03 → BRD-04 → BRD-05
├── Parallel Groups:
│   ├── Group 1: [BRD-06] (Infrastructure)
│   ├── Group 2: [BRD-07] (Config)
│   ├── Group 3: [BRD-01, BRD-02] (Parallel - no dependencies)
│   ├── Group 4: [BRD-03] (depends on BRD-01)
│   └── Group 5: [BRD-04, BRD-05] (Parallel - depend on BRD-03)
└── Estimated Time: Sequential 7 units, Parallel 4 units
```

### Step 3: PRD-Ready Score Validation

Before generating a PRD, validate that the source BRD meets PRD-Ready requirements.

> **Skill Delegation**: This phase uses validation rules from `doc-brd-validator` skill.
> See: `.claude/skills/doc-brd-validator/SKILL.md` for complete BRD validation rules.

**PRD-Ready Scoring Criteria (100%)**:

| Category | Weight | Criteria |
|----------|--------|----------|
| Business Requirements Completeness | 40% | All 18 BRD sections present, objectives defined, stakeholders identified |
| Technical Readiness | 30% | Architecture Decision Requirements section complete, technology prerequisites documented |
| Business Alignment | 20% | Success criteria quantified, risks assessed, constraints documented |
| Traceability | 10% | Strategy references included, downstream placeholders defined |

**Minimum Score**: 90% (configurable)

**Auto-Fix Actions**:
| Issue | Auto-Fix Action |
|-------|-----------------|
| Missing timing profiles (p50/p95/p99) | Add template timing table |
| Pending ADR topics without elaboration | Add business driver and constraints placeholders |
| Missing threshold registry | Add Appendix with threshold template |
| Incomplete Document Control | Add missing required fields |
| Missing section numbers | Renumber sections sequentially |

**Validation Command** (internal):
```bash
python ai_dev_flow/scripts/validate_prd_ready.py \
  --brd docs/01_BRD/BRD-01_f1_iam/ \
  --min-score 90 \
  --auto-fix
```

### Step 4: PRD Generation

Generate the PRD document from the validated BRD.

> **Skill Delegation**: This phase follows rules defined in `doc-prd` skill.
> See: `.claude/skills/doc-prd/SKILL.md` for complete PRD creation guidance.

**Generation Process**:

1. **Load BRD Content**:
   - Read all BRD section files (for sectioned BRDs)
   - Extract business requirements, objectives, stakeholders
   - Parse Architecture Decision Requirements topics

2. **Template Selection** (per `doc-prd` skill):
   - **MVP Template** (default): `ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.md` (17 sections, ≥85% thresholds)
   - **Full Template**: For enterprise/regulatory projects (21 sections, ≥90% thresholds)
   - **Section Templates**: For sectioned PRDs (>25KB)

3. **Section Mapping** (BRD → PRD):

| BRD Section | PRD Section(s) |
|-------------|----------------|
| 0. Document Control | 1. Document Control |
| 1. Executive Summary | 2. Executive Summary |
| 2. Business Context | 3. Problem Statement |
| 3. Stakeholder Analysis | 4. Target Audience & User Personas |
| 4. Business Requirements | 6. Goals & Objectives, 9. Functional Requirements |
| 5. Success Criteria | 5. Success Metrics (KPIs) |
| 6. Constraints | 12. Constraints & Assumptions |
| 7. Architecture Decision Requirements | 18. Traceability (Architecture Decision Requirements) |
| 8. Risk Assessment | 13. Risk Assessment |
| 9. Traceability | 18. Traceability |

4. **PRD-Specific Content Generation**:
   - Section 7: Scope & Requirements (derive from BRD scope)
   - Section 8: User Stories & User Roles (extract from stakeholders)
   - Section 10: Customer-Facing Content & Messaging (MANDATORY)
   - Section 11: Acceptance Criteria (from BRD success criteria)
   - Section 14: Success Definition (go-live criteria)
   - Section 15: Stakeholders & Communication
   - Section 16: Implementation Approach
   - Section 17: Budget & Resources
   - Section 19: References
   - Section 20: EARS Enhancement Appendix (timing, boundary, state, fallback)
   - Section 21: Quality Assurance & Testing Strategy

5. **Traceability Tags**:
   ```markdown
   @brd: BRD.01.01.01, BRD.01.01.02, BRD.01.23.01
   ```

6. **File Output**:
   - **Monolithic** (<25KB): `docs/02_PRD/PRD-NN_{slug}.md`
   - **Sectioned** (>=25KB): `docs/02_PRD/PRD-NN_{slug}/PRD-NN.S_{section}.md`

### Step 5: EARS-Ready Score Validation

After PRD generation, validate EARS-Ready score.

> **Skill Delegation**: This phase uses validation rules from `doc-prd-validator` skill.
> See: `.claude/skills/doc-prd-validator/SKILL.md` for complete validation rules and error codes.

**EARS-Ready Scoring Criteria (100%)**:

| Category | Weight | Criteria |
|----------|--------|----------|
| Business Requirements Clarity | 40% | SMART objectives, functional requirements, acceptance criteria |
| Requirements Maturity | 35% | System boundaries, stakeholder requirements, problem statement |
| EARS Translation Readiness | 20% | User journeys, quality attributes quantified, timing profiles |
| Strategic Alignment | 5% | Domain-specific business logic references |

**Minimum Score**: 85% for MVP (90% for full template) - configurable

**Auto-Fix Actions** (per `doc-prd-validator` error codes):

| Issue | Error Code | Auto-Fix Action |
|-------|------------|-----------------|
| Missing timing profile matrix | PRD-W002 | Add Section 20.1 template |
| Missing boundary value matrix | PRD-W002 | Add Section 20.2 template |
| Missing state transition diagram | PRD-W002 | Add Section 20.3 Mermaid template |
| Missing fallback documentation | PRD-W002 | Add Section 20.4 template |
| Incomplete customer-facing content | PRD-E006 | Flag for manual review (Section 10) |

### Step 6: Final Content Review

After EARS-Ready validation passes, perform comprehensive content review.

**Review Checklist**:

| Check | Description | Auto-Fix | Manual |
|-------|-------------|----------|--------|
| Link Integrity | All internal links between sections resolve | Yes | - |
| Threshold Consistency | Performance metrics match across sections | Yes | - |
| BRD Alignment | PRD content accurately reflects BRD requirements | - | Review |
| Placeholder Detection | No `[TODO]`, `[TBD]`, `YYYY-MM-DD` remaining | Yes | - |
| Traceability Tags | All `@brd:` tags reference valid BRD IDs | Yes | - |
| Cross-Reference Validity | `@depends:` and `@discoverability:` tags valid | Yes | - |
| Section Completeness | No empty or stub sections | - | Flag |
| Customer Content | Section 10 has substantive content | - | Flag |

**Review Process**:

1. **Link Integrity Check**:
   ```
   Scanning PRD-01 for internal links...
   ├── PRD-01.0_index.md: 17 links found
   │   ├── PRD-01.1_document_control.md ✓
   │   ├── PRD-01.2_executive_summary.md ✓
   │   └── ... (all valid)
   └── Result: 0 broken links
   ```

2. **Threshold Consistency Check**:
   ```
   Comparing thresholds across sections...
   ├── Section 5 (Success Metrics): auth.p99 = 100ms
   ├── Section 9 (Quality Attributes): auth.p99 = 100ms
   ├── Section 17 (Appendix B.1): auth.p99 = 100ms
   └── Result: Consistent ✓
   ```

3. **BRD Alignment Check**:
   ```
   Verifying PRD requirements map to BRD source...
   ├── PRD.01.01.01 → BRD.01.01.01 (Multi-Provider Auth) ✓
   ├── PRD.01.01.02 → BRD.01.01.02 (4D Authorization) ✓
   └── Result: 12/12 requirements aligned ✓
   ```

4. **Placeholder Detection**:
   ```
   Scanning for placeholder text...
   ├── [TODO]: 0 found
   ├── [TBD]: 0 found
   ├── YYYY-MM-DD: 0 found
   ├── [Name]: 0 found
   └── Result: No placeholders ✓
   ```

**Review Output**:
```
Final Review Complete:
├── Link Integrity: PASS (0 broken links)
├── Threshold Consistency: PASS (all metrics aligned)
├── BRD Alignment: PASS (12/12 requirements)
├── Placeholder Detection: PASS (0 placeholders)
├── Traceability Tags: PASS (15 valid @brd references)
├── Section Completeness: PASS (17/17 sections)
└── Customer Content: FLAG (Section 10 needs business review)

Review Score: 95/100
Status: PASS (threshold: 90)
Flagged for Manual Review: Section 10 (Customer-Facing Content)
```

**Auto-Fix Actions**:

| Issue | Auto-Fix Action |
|-------|-----------------|
| Broken internal link | Update link path or remove |
| Inconsistent threshold | Align to BRD source value |
| Placeholder text | Replace with actual content or flag |
| Invalid @brd tag | Remove or correct reference |
| Missing date | Insert current date |

---

### Step 7: Process Next BRD

After completing one PRD:
1. Mark current BRD→PRD as complete
2. Update traceability matrix
3. Move to next BRD in execution order
4. Repeat Steps 3-5

**Progress Tracking**:
```
PRD Generation Progress:
[████████░░░░░░░░] 3/7 Complete

Completed:
  ✓ PRD-06 (from BRD-06) - EARS-Ready: 94%
  ✓ PRD-07 (from BRD-07) - EARS-Ready: 92%
  ✓ PRD-01 (from BRD-01) - EARS-Ready: 96%

In Progress:
  ⟳ PRD-02 (from BRD-02) - Generating Section 10...

Pending:
  ○ PRD-03 (from BRD-03) - Awaiting BRD-01 completion
  ○ PRD-04 (from BRD-04)
  ○ PRD-05 (from BRD-05)
```

### Step 8: Parallel Generation

For independent BRDs (no cross-dependencies), generate PRDs in parallel.

**Parallel Execution Rules**:
1. **Independence Check**: No shared `@depends-brd` references
2. **Resource Limits**: Maximum 3 parallel generations (configurable)
3. **Failure Isolation**: One failure doesn't block others
4. **Progress Reporting**: Aggregate status updates

**Parallel Execution Example**:
```
Parallel Group Execution:
├── Thread 1: BRD-01 → PRD-01 [████████████████] 100%
├── Thread 2: BRD-02 → PRD-02 [████████████░░░░] 75%
└── Thread 3: BRD-05 → PRD-05 [████████░░░░░░░░] 50%
```

---

## Configuration

### Default Configuration

```yaml
# config/prd_autopilot.yaml
prd_autopilot:
  version: "1.2"

  scoring:
    prd_ready_min: 90
    ears_ready_min: 90
    review_score_min: 90
    strict_mode: false

  execution:
    max_parallel: 3
    auto_fix: true
    continue_on_error: false
    timeout_per_brd: 300  # seconds

  output:
    structure: auto  # auto, monolithic, sectioned
    size_threshold_kb: 25
    report_format: markdown

  validation:
    skip_validation: false
    fix_iterations_max: 3

  review:
    enabled: true
    check_links: true
    check_thresholds: true
    check_brd_alignment: true
    check_placeholders: true
    check_traceability: true
    auto_fix_links: true
    auto_fix_placeholders: true
    flag_customer_content: true
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--min-prd-ready` | 90 | Minimum PRD-Ready score |
| `--min-ears-ready` | 90 | Minimum EARS-Ready score |
| `--min-review-score` | 90 | Minimum Final Review score |
| `--max-parallel` | 3 | Maximum parallel PRD generations |
| `--no-auto-fix` | false | Disable auto-fix (manual only) |
| `--continue-on-error` | false | Continue if one BRD fails |
| `--dry-run` | false | Preview execution plan only |
| `--output-format` | auto | Force monolithic or sectioned output |
| `--skip-review` | false | Skip final content review phase |
| `--review-only` | false | Run only final review on existing PRD |

---

## Execution Modes

### Mode 1: Interactive (Default)

User confirms each step before proceeding.

```bash
/doc-prd-autopilot BRD-01,BRD-02 --interactive

# Output:
# Dependency Analysis: BRD-01 → BRD-02 (BRD-02 depends on BRD-01)
#
# [1/2] BRD-01: PRD-Ready Score = 92% (PASS)
# Generate PRD-01? [Y/n] y
# PRD-01 generated. EARS-Ready Score = 94% (PASS)
#
# [2/2] BRD-02: PRD-Ready Score = 88% (FAIL)
# Auto-fix available. Apply fixes? [Y/n] y
# Fixes applied. New score = 91% (PASS)
# Generate PRD-02? [Y/n] y
# PRD-02 generated. EARS-Ready Score = 90% (PASS)
#
# Summary: 2/2 PRDs generated successfully.
```

### Mode 2: Automatic

No user confirmation, auto-fix enabled.

```bash
/doc-prd-autopilot all --auto

# Output:
# PRD Autopilot - Automatic Mode
# ==============================
# Scanning: docs/01_BRD/
# Found: 7 BRDs
#
# Phase 1: Dependency Analysis... Done
# Phase 2-4: Processing...
#   [████████████████] 7/7 Complete
#
# Summary:
#   ✓ 7 PRDs generated
#   ✓ 3 BRDs auto-fixed
#   ✓ Average EARS-Ready: 93%
```

### Mode 3: Dry Run

Preview execution plan without generating files.

```bash
/doc-prd-autopilot all --dry-run

# Output:
# PRD Autopilot - Dry Run Mode
# ============================
#
# Execution Plan:
# 1. BRD-06 (Infrastructure) → PRD-06
# 2. BRD-07 (Config) → PRD-07
# 3. [Parallel] BRD-01, BRD-02 → PRD-01, PRD-02
# 4. BRD-03 → PRD-03
# 5. [Parallel] BRD-04, BRD-05 → PRD-04, PRD-05
#
# Estimated Duration: ~4 units (parallel) vs ~7 units (sequential)
#
# No files will be created in dry-run mode.
```

---

## Output Files

### Generated PRD Structure

**Monolithic Output** (single file <25KB):
```
docs/02_PRD/
├── PRD-00_TRACEABILITY_MATRIX.md  # Updated
└── PRD-01_f1_iam.md               # New PRD
```

**Sectioned Output** (folder structure >=25KB):
```
docs/02_PRD/
├── PRD-00_TRACEABILITY_MATRIX.md  # Updated
└── PRD-01_f1_iam/
    ├── PRD-01.0_index.md
    ├── PRD-01.1_document_control.md
    ├── PRD-01.2_executive_summary.md
    ├── PRD-01.3_problem_statement.md
    ...
    └── PRD-01.21_qa_strategy.md
```

### Summary Report

Generated after completion:

```markdown
# PRD Autopilot Summary Report

**Execution Date**: 2026-02-08
**Input**: 7 BRDs
**Output**: 7 PRDs

## Execution Order

| Step | BRD | PRD | PRD-Ready | EARS-Ready | Duration | Status |
|------|-----|-----|-----------|------------|----------|--------|
| 1 | BRD-06 | PRD-06 | 94% | 92% | 45s | Success |
| 2 | BRD-07 | PRD-07 | 91% | 90% | 52s | Success |
| 3 | BRD-01 | PRD-01 | 96% | 96% | 48s | Success |
| 3 | BRD-02 | PRD-02 | 92% | 91% | 47s | Success (Parallel) |
| 4 | BRD-03 | PRD-03 | 90% | 93% | 50s | Success |
| 5 | BRD-04 | PRD-04 | 88%→91% | 90% | 62s | Success (Auto-fixed) |
| 5 | BRD-05 | PRD-05 | 93% | 94% | 44s | Success (Parallel) |

## Auto-Fixes Applied

| BRD | Issue | Fix Applied |
|-----|-------|-------------|
| BRD-04 | Missing timing profiles | Added p50/p95/p99 table |
| BRD-04 | Pending ADR topic | Added business driver |

## Next Steps

1. Review generated PRDs for domain-specific content
2. Complete Section 10 (Customer-Facing Content) manually if flagged
3. Run `/doc-ears-autopilot` to generate EARS from PRDs
```

---

## Error Handling

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `CircularDependencyError` | BRD-A depends on BRD-B and vice versa | Review and remove circular reference |
| `BRDNotFoundError` | Specified BRD does not exist | Check path and BRD ID |
| `PRDReadyScoreLow` | BRD score < 90% after auto-fix attempts | Manual BRD improvement required |
| `EARSReadyScoreLow` | PRD score < 90% after auto-fix | Manual PRD improvement required |
| `TemplateNotFoundError` | PRD template missing | Verify `ai_dev_flow/02_PRD/` exists |

### Recovery Actions

```bash
# Resume from last successful point
/doc-prd-autopilot resume

# Skip failed BRD and continue
/doc-prd-autopilot all --continue-on-error

# Retry single failed BRD
/doc-prd-autopilot BRD-04 --force
```

---

## Integration with Other Skills

### Upstream Skills
- **`doc-brd`**: Create/update BRDs before running autopilot
- **`doc-validator`**: Pre-validate BRDs for readiness

### Downstream Skills
- **`doc-ears-autopilot`**: Chain autopilot for EARS generation (future)
- **`doc-ears`**: Manual EARS creation from PRDs
- **`doc-prd`**: Manual PRD editing after autopilot

### Typical Workflow

```
1. doc-brd (create BRDs)
2. doc-prd-autopilot (generate PRDs) ← This skill
3. doc-ears (create EARS from PRDs)
4. doc-bdd (create BDD from EARS)
5. ... continue SDD workflow
```

---

## Prerequisites

Before using this skill, ensure:

1. **BRD Documents Exist**: At least one BRD in `docs/01_BRD/`
2. **Templates Available**: `ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.md`
3. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

### Pre-Flight Check

```bash
# Verify BRD directory
ls docs/01_BRD/

# Verify PRD template
ls ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.md

# Check for existing PRDs
ls docs/02_PRD/ 2>/dev/null || echo "PRD directory will be created"
```

---

## Validation Checklist

After autopilot completion:

- [ ] All target PRDs generated
- [ ] Each PRD has EARS-Ready score >= 90%
- [ ] Each PRD has Final Review score >= 90%
- [ ] Traceability matrix updated (`PRD-00_TRACEABILITY_MATRIX.md`)
- [ ] Each PRD references upstream BRD with `@brd` tags
- [ ] Section 10 (Customer-Facing Content) has substantive content
- [ ] Section 20 (EARS Enhancement Appendix) completed
- [ ] No broken links in generated documents (verified by Final Review)
- [ ] No placeholder text remaining (verified by Final Review)
- [ ] Thresholds consistent across sections (verified by Final Review)
- [ ] BRD alignment verified (all PRD requirements trace to BRD source)

---

## Quick Reference

| Input | Output | Key Metric |
|-------|--------|------------|
| BRD(s) | PRD(s) | EARS-Ready >= 90% |

**Usage**:
```
/doc-prd-autopilot <BRD-LIST> [OPTIONS]
```

**Common Commands**:
```bash
# Single BRD
/doc-prd-autopilot BRD-01

# All BRDs (automatic)
/doc-prd-autopilot all --auto

# Preview only
/doc-prd-autopilot all --dry-run

# Resume after failure
/doc-prd-autopilot resume
```

---

## Related Resources

### Skills (Delegated)

- **PRD Skill**: `.claude/skills/doc-prd/SKILL.md` - PRD creation rules and structure
- **PRD Validator Skill**: `.claude/skills/doc-prd-validator/SKILL.md` - Validation rules and error codes
- **BRD Validator Skill**: `.claude/skills/doc-brd-validator/SKILL.md` - BRD readiness validation

### Templates and Rules

- **PRD Template**: `ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.md`
- **PRD Schema**: `ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml`
- **PRD Creation Rules**: `ai_dev_flow/02_PRD/PRD_MVP_CREATION_RULES.md`
- **PRD Validation Rules**: `ai_dev_flow/02_PRD/PRD_MVP_VALIDATION_RULES.md`

### Framework References

- **SDD Workflow**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- **MVP Autopilot**: `ai_dev_flow/AUTOPILOT/MVP_AUTOPILOT.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2 | 2026-02-08 | Added Phase 5: Final Content Review with link integrity, threshold consistency, BRD alignment, and placeholder detection checks |
| 1.1 | 2026-02-08 | Added skill dependencies, integrated doc-prd and doc-prd-validator skills |
| 1.0 | 2026-02-08 | Initial skill creation with 7-step workflow |
