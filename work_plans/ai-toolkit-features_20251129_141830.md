# Implementation Plan - AI Product Development Toolkit Features

**Created**: 2025-11-29 14:18:30 EST
**Status**: Ready for Implementation
**Source**: Gap analysis of [AI Product Development Toolkit](https://github.com/TechNomadCode/AI-Product-Development-Toolkit)

## Objective

Implement 5 missing features from the AI Product Development Toolkit to enhance the docs_flow_framework with user-centric and rapid prototyping capabilities.

## Context

### Background
- Compared AI Product Development Toolkit (8-step workflow) with docs_flow_framework (16-layer SDD)
- Our framework is more comprehensive but lacks some user-centric features
- User approved all 5 identified features for implementation

### Key Decisions
- UX-User-Flow: New Layer 2.5 (between PRD and EARS)
- MVP-Concept: New Layer 2.6 (optional)
- Lean-MVP: Alternative fast-track path (bypasses Layers 3-12)
- doc-ui skill: Visual code generation prompts (v0.dev, Figma, etc.)
- AI Parameters: Add guidance section to AI_ASSISTANT_RULES.md

## Task List

### Pending
- [ ] Phase 1: Create UX-User-Flow artifact structure + doc-ux skill
- [ ] Phase 2: Create MVP-Concept template + doc-mvp skill
- [ ] Phase 3: Create Lean-MVP fast-track template + doc-lean-mvp skill
- [ ] Phase 4: Create doc-ui skill (UI/Visual Design Prompts)
- [ ] Phase 4.5: Add AI Parameter Guidance to AI_ASSISTANT_RULES.md
- [ ] Phase 5: Update framework documentation (6 files)
- [ ] Phase 6: Create validation scripts (3 scripts)
- [ ] Final: Commit all changes

### Notes
- Total: 16 new files + 7 modified files
- Follow existing template patterns from PRD-TEMPLATE.md
- Use existing skill structure from doc-prd/SKILL.md as reference

## Implementation Guide

### Prerequisites
- Read existing templates for pattern reference:
  - `ai_dev_flow/PRD/PRD-TEMPLATE.md`
  - `.claude/skills/doc-prd/SKILL.md`
- Read framework documentation:
  - `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
  - `ai_dev_flow/TRACEABILITY.md`
  - `ai_dev_flow/ID_NAMING_STANDARDS.md`

### Execution Steps

#### Phase 1: UX-User-Flow Artifact (Layer 2.5)
Create files:
```
ai_dev_flow/UX/
├── UX-TEMPLATE.md          # Main template (10 sections)
├── UX-000_index.md         # Index file
├── README.md               # UX layer documentation
└── examples/
    └── UX-001_example.md   # Example UX document

.claude/skills/doc-ux/
└── SKILL.md                # doc-ux skill
```

UX-TEMPLATE.md sections:
1. Document Control (ID, version, status, traceability)
2. Overview & Context
3. User Personas (linked from PRD)
4. User Journey Maps (primary flow, alternative paths, error states)
5. Screen/View Inventory
6. Interaction Patterns
7. Navigation Structure
8. Accessibility Requirements
9. Responsive Behavior
10. Traceability Links (@prd, @brd references)

Traceability tag: `@ux: UX-XXX:FLOW-YY`

#### Phase 2: MVP-Concept Template
Create files:
```
ai_dev_flow/MVP/
├── MVP-CONCEPT-TEMPLATE.md  # Focused MVP hypothesis doc (11 sections)
├── MVP-000_index.md         # Index file
├── README.md                # MVP layer documentation
└── examples/
    └── MVP-001_example.md   # Example MVP concept

.claude/skills/doc-mvp/
└── SKILL.md                 # doc-mvp skill
```

MVP-CONCEPT-TEMPLATE.md sections:
1. Document Control
2. Problem Hypothesis
3. Solution Hypothesis
4. Core Value Proposition
5. MVP Scope Definition (In-Scope, Out-of-Scope, Deferred)
6. Success Metrics & KPIs
7. Risk Assumptions to Validate
8. Target User Segment
9. Timeline & Constraints
10. Validation Plan
11. Traceability Links

Traceability tag: `@mvp: MVP-XXX`

#### Phase 3: Lean-MVP Fast-Track Template
Create files:
```
ai_dev_flow/LEAN-MVP/
├── LEAN-MVP-TEMPLATE.md     # Ultra-lean single-page spec (9 sections)
├── README.md                # Fast-track workflow documentation
└── examples/
    └── LEAN-MVP-001_example.md

.claude/skills/doc-lean-mvp/
└── SKILL.md                 # doc-lean-mvp skill
```

LEAN-MVP-TEMPLATE.md sections (single page):
1. Header (ID, Date, Owner)
2. One-Line Problem Statement
3. One-Line Solution
4. 3-5 Core Features (numbered list)
5. Out of Scope (brief list)
6. Success Criteria (3 max)
7. Build Timeline (24-48 hours target)
8. Tech Stack (brief)
9. Risks & Assumptions

Traceability tag: `@lean-mvp: LEAN-MVP-XXX`

#### Phase 4: UI Generation Skill (doc-ui)
Create file:
```
.claude/skills/doc-ui/
└── SKILL.md                 # UI generation prompts skill
```

Content:
- v0.dev prompt templates
- Component generation patterns
- Design system integration prompts
- Figma-to-code workflow guidance
- Visual mockup specifications
- Responsive design prompts
- Accessibility checklist for UI

Supported tools: v0.dev (Vercel), Figma Code Generation, Tailwind UI, shadcn/ui

#### Phase 4.5: AI Parameter Guidance
Modify: `ai_dev_flow/AI_ASSISTANT_RULES.md`

Add new section "AI Model Parameter Guidance":
- Temperature settings by task type table
- Model selection by task table
- Context window management guidelines
- Token optimization strategies

#### Phase 5: Framework Updates
Modify 6 files:

1. `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
   - Add UX as Layer 2.5
   - Add MVP as Layer 2.6 (optional)
   - Document Lean-MVP as fast-track alternative
   - Update layer diagram

2. `ai_dev_flow/AI_ASSISTANT_RULES.md`
   - Add AI parameter guidance section

3. `ai_dev_flow/TRACEABILITY.md`
   - Add @ux tag documentation
   - Add @mvp tag documentation
   - Update cumulative tagging examples

4. `ai_dev_flow/ID_NAMING_STANDARDS.md`
   - Add UX-XXX format
   - Add MVP-XXX format
   - Add LEAN-MVP-XXX format

5. `.claude/skills/doc-flow/SKILL.md`
   - Update workflow to include UX layer
   - Add MVP concept guidance
   - Reference Lean-MVP as alternative

6. `.claude/skills/README.md`
   - Add doc-ux, doc-mvp, doc-lean-mvp, doc-ui to skills index

#### Phase 6: Validation Scripts
Create 3 scripts:
```
ai_dev_flow/scripts/
├── validate_ux_template.sh      # UX template validation
├── validate_mvp_template.sh     # MVP template validation
└── validate_lean_mvp.sh         # Lean-MVP validation
```

### Verification
- [ ] All 16 new files created in correct locations
- [ ] All 7 modified files updated correctly
- [ ] New traceability tags documented (@ux, @mvp, @lean-mvp)
- [ ] Skills index updated with 4 new skills
- [ ] Layer structure updated to include 2.5 and 2.6
- [ ] Validation scripts executable and functional

## New Layer Structure (Post-Implementation)

```
Layer 0:  Strategy (external)
Layer 1:  BRD (Business Requirements)
Layer 2:  PRD (Product Requirements)
Layer 2.5: UX (User Experience Flows) ← NEW
Layer 2.6: MVP (MVP Concept) ← NEW (optional)
Layer 3:  EARS (Formal Requirements)
Layer 4:  BDD (Behavior Tests)
Layer 5:  ADR (Architecture Decisions)
Layer 6:  SYS (System Requirements)
Layer 7:  REQ (Atomic Requirements)
Layer 8:  IMPL (Implementation Plans - optional)
Layer 9:  CTR (API Contracts - optional)
Layer 10: SPEC (Technical Specifications)
Layer 11: TASKS (Code Generation Plans)
Layer 12: IPLAN (Session Plans)
Layer 13: Code
Layer 14: Tests
Layer 15: Validation

Alternative: LEAN-MVP (fast-track, bypasses Layers 3-12)
```

## New Traceability Tags

| Tag | Format | Layer | Example |
|-----|--------|-------|---------|
| `@ux` | `@ux: UX-XXX:FLOW-YY` | 2.5 | `@ux: UX-001:FLOW-03` |
| `@mvp` | `@mvp: MVP-XXX` | 2.6 | `@mvp: MVP-001` |
| `@lean-mvp` | `@lean-mvp: LEAN-MVP-XXX` | Alt | `@lean-mvp: LEAN-MVP-001` |

## References

- Source repository: https://github.com/TechNomadCode/AI-Product-Development-Toolkit
- Plan file: `/home/ya/.claude/plans/humming-crunching-cherny.md`
- Existing templates: `ai_dev_flow/PRD/PRD-TEMPLATE.md`, `.claude/skills/doc-prd/SKILL.md`
- Framework docs: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`, `ai_dev_flow/TRACEABILITY.md`
