---
title: "IPLAN-006: C4 + DFD + Sequence Integration for AI-Assisted Design"
tags:
  - implementation-plan
  - ai-agent-primary
  - shared-architecture
  - active
custom_fields:
  document_type: iplan
  artifact_type: IPLAN
  layer: 12
  priority: primary
  development_status: active
  lifecycle: mvp-prod-newmvp
  complexity: 4
  architecture_approaches: [ai-agent-based, traditional-8layer]
  date: "2026-02-26"
---

# IPLAN-006: C4 + DFD + Sequence Integration for AI-Assisted Design

## 1. Objective
Implement a unified diagram method where:
- C4 represents structural boundaries and responsibilities.
- DFD represents data movement, stores, and trust boundaries.
- Sequence diagrams represent temporal behavior, retries, and failure choreography.

Lifecycle objective:
- Implement this method as a repeatable **MVP → PROD → NEW MVP** cycle control, not a one-time documentation change.

## 2. Scope
In scope:
- Framework-level documentation updates for diagram model governance.
- Layer 1 BRD template/rules/quality-gate updates.
- Layer 2 PRD template/rules/quality-gate updates.
- Layer 5 ADR template/rules/quality-gate updates.
- Layer 6 SYS template/rules/quality-gate updates.
- Layer 9+ SPEC and implementation/test ownership guidance for C4 L4 (Code level).
- Diagram standard updates and validator enforcement updates.
- AI-assistant prompt contracts and generation constraints.
- Related Claude skills updates for BRD/PRD/ADR/SYS generation and review behavior.
- Cross-cycle traceability updates to support `@depends` links between BRD iterations.
- Lifecycle checkpoints covering MVP artifact generation, PROD feedback capture, and NEW MVP re-entry.

Out of scope:
- Historical backfill of all legacy artifacts.
- Non-Mermaid diagram tooling.
- Changes to unrelated layers unless required by traceability.

Framework-level docs targeted by this plan:
- `ai_dev_ssd_flow/DIAGRAM_STANDARDS.md`
- `ai_dev_ssd_flow/MVP_WORKFLOW_GUIDE.md`

Primary doc-type template targets:
- `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/02_PRD/PRD-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/06_SYS/SYS-MVP-TEMPLATE.md`

Primary skill targets:
- `.claude/skills/doc-brd/SKILL.md`
- `.claude/skills/doc-prd/SKILL.md`
- `.claude/skills/doc-adr/SKILL.md`
- `.claude/skills/doc-sys/SKILL.md`

## 3. Design Additions Recommended (AI-Heavy Usage)
1. Diagram Intent Header (mandatory per diagram section)
- Purpose, audience, abstraction level, and source references.
- Required fields: diagram_type, level, scope_boundary, upstream_refs, downstream_refs.

2. Diagram Contract Tags (machine-parseable)
- Add tags adjacent to diagram blocks:
  - @diagram: c4-l1 | c4-l2 | c4-l3
  - @diagram: dfd-l0 | dfd-l1 | dfd-l2
  - @diagram: sequence-sync | sequence-async | sequence-error
- Enable deterministic AI retrieval and validation.

3. Canonical Naming and IDs
- Node and actor naming registry per document to reduce AI synonym drift.
- Enforce ID reuse across BRD/PRD/ADR for the same concept.

4. AI Guardrail Section in Templates
- Add "Do/Do Not" constraints for generation:
  - Do preserve abstraction level.
  - Do include failure paths for sequence diagrams.
  - Do not mix C4 and DFD semantics in one diagram.
  - Do not introduce unlabeled external systems.

5. Diagram Delta Rule for Iterations
- Add required "What changed since prior cycle" subsection in BRD/PRD/ADR.
- Supports AI-assisted review and reduces full-document regeneration.

6. Trust Boundary Annotation
- Mandatory in DFD and recommended in C4 context/container views.
- Required for security/compliance traceability.

7. Executable Validation Profiles
- Add severity tiers:
  - Error: missing required diagram type for section.
  - Warning: missing failure path or trust boundary.
  - Info: optional enrichment gaps.

## 4. Target Mapping by Artifact
| Artifact | Mandatory Diagram Set | Conditional Diagram Set | Primary Validation Outcome |
|---|---|---|---|
| BRD | C4 L1, DFD L0 | Sequence for critical business journey | Business boundary clarity |
| PRD | C4 L2, DFD L1, Sequence (top journeys) | Sequence error-path variants | Product interaction clarity |
| ADR | C4 L3, Sequence for chosen option | DFD L2 for data-impacting decisions | Decision implementation clarity |
| SYS | System Diagram Contract with C4 L2/L3 references, DFD boundary tags, sequence path constraints | Additional sequence variants for critical integrations | System-to-spec bridge clarity |
| SPEC / Code / Tests (Layer 9+) | C4 L4 ownership and code-structure views | Additional low-level interaction diagrams as needed | Implementation-level design clarity |

Ownership rule:
- C4 L4 (Code level) is owned by SPEC and implementation/test layers (Layer 9+).
- SYS references C4 L4 ownership location but does not require embedded code/class diagrams.

## 5. Execution Plan
### Phase 0: Baseline Alignment (Precondition)
- Fix known validator/template mismatches before introducing stricter diagram rules.
- Confirm MVP profile section-name alignment in validators for BRD/PRD/ADR.
- Resolve ADR MVP architecture section check mismatch (`Architecture Flow` vs validator expectation).
- Produce a short alignment report listing baseline mismatches and remediation status.

### Phase A: Standards and Contracts
- Update DIAGRAM_STANDARDS.md with C4/DFD/Sequence taxonomy and required usage by layer.
- Define forbidden semantic mixing rules.
- Add canonical examples per diagram type in standard format.
- Define parser-tolerant detection patterns for equivalent Mermaid expressions.
- Define accepted trust-boundary annotation formats and required labels.

### Phase B: Template and Rule Integration
- Update BRD-MVP-TEMPLATE.md, PRD-MVP-TEMPLATE.md, ADR-MVP-TEMPLATE.md sections for required diagrams.
- Update SYS-MVP-TEMPLATE.md with required "System Diagram Contract" subsection.
- Update creation and validation rules for each artifact with exact requirements and section references.
- Add AI generation guardrails directly in template AI_CONTEXT blocks.
- Add SYS rule requiring downstream SPEC location reference for C4 L4 ownership.

### Phase C: Validator Enforcement
- Update validate_brd.py, validate_prd.py, validate_adr.py.
- Update validate_sys.py for required SYS diagram-contract checks.
- Add checks for required diagram presence by section and profile.
- Add checks for required tags and trust-boundary annotations where applicable.
- Align ADR validator section matching with current MVP template section names.
- Add compatibility mode for legacy artifacts (warning-first during migration window).
- Add deterministic fixture-based tests for pass/fail scenarios across C4/DFD/sequence checks.
- Enforce SYS visualization severity upgrades from Info to Warning/Error for required conditions.

### Phase D: Quality Gate and Reviewer Alignment
- Update BRD/PRD/ADR/SYS MVP quality-gate docs.
- Add explicit pass/fail matrix for C4/DFD/Sequence coverage.
- Update reviewer skills/prompts to evaluate abstraction correctness and temporal completeness.
- Add SYS-specific matrix: required System Diagram Contract, DFD boundary tags, required sequence paths, SPEC ownership reference.

### Phase E: Explicit Cross-Layer Implementation (All Affected Layers)
Primary goal of this phase:
- Implement the new design approach end-to-end: **C4 + DFD + Sequence diagrams (C4-DFD-Seq)** as enforceable standards, templates, validators, quality gates, and AI-skill behaviors across all affected layers.

- Implement framework-level standard changes in `DIAGRAM_STANDARDS.md` and `MVP_WORKFLOW_GUIDE.md`.
- Implement Layer 1 BRD changes: template, creation rules, validation rules, validator checks, quality-gate checks, and BRD skill generation/review prompts.
- Implement Layer 2 PRD changes: template, creation rules, validation rules, validator checks, quality-gate checks, and PRD skill generation/review prompts.
- Implement Layer 5 ADR changes: template, creation rules, validation rules, validator checks, quality-gate checks, and ADR skill generation/review prompts.
- Implement Layer 6 SYS changes: template, creation rules, validation rules, validator checks, quality-gate checks, and SYS skill generation/review prompts.
- Implement Layer 9+ SPEC/Code/Test changes: SPEC template/rules/validator ownership checks for C4 L4 and required linkage from SYS references.
- Implement shared validator and fixture updates across all affected layers with parity checks for MVP and non-MVP profiles.
- Implement documentation and skill updates so generation, review, and fix workflows enforce the same layer-specific diagram contracts.

#### Phase E Implementation Matrix (Compact, File-by-File)
| Layer / Scope | Primary Files (minimum) | Required Implementation Outcome for C4-DFD-Seq |
|---|---|---|
| Framework Standards | `ai_dev_ssd_flow/DIAGRAM_STANDARDS.md`, `ai_dev_ssd_flow/MVP_WORKFLOW_GUIDE.md` | Canonical C4/DFD/Sequence taxonomy, ownership, lifecycle gates, and migration policy defined |
| Layer 1 BRD | `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md`, BRD creation/validation/quality-gate docs, BRD validator(s), `.claude/skills/doc-brd/SKILL.md`, `.claude/skills/doc-brd-reviewer/SKILL.md` | Enforce C4 L1 + DFD L0 (+ conditional sequence), tags, and trust-boundary requirements |
| Layer 2 PRD | `ai_dev_ssd_flow/02_PRD/PRD-MVP-TEMPLATE.md`, PRD creation/validation/quality-gate docs, PRD validator(s), `.claude/skills/doc-prd/SKILL.md`, `.claude/skills/doc-prd-reviewer/SKILL.md` | Enforce C4 L2 + DFD L1 + required sequence with explicit error-path checks |
| Layer 5 ADR | `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md`, ADR creation/validation/quality-gate docs, ADR validator(s), `.claude/skills/doc-adr/SKILL.md`, `.claude/skills/doc-adr-reviewer/SKILL.md` | Enforce C4 L3 + required decision choreography sequence (+ DFD L2 when data-impacting) |
| Layer 6 SYS | `ai_dev_ssd_flow/06_SYS/SYS-MVP-TEMPLATE.md`, SYS creation/validation/quality-gate docs, SYS validator(s), `.claude/skills/doc-sys/SKILL.md`, `.claude/skills/doc-sys-reviewer/SKILL.md` | Enforce System Diagram Contract and required downstream SPEC reference for C4 L4 ownership |
| Layer 9+ SPEC / Code / Tests | SPEC template/rules/validator docs and related implementation/test guidance | Enforce C4 L4 ownership declarations and linkage consistency with SYS contract references |
| Shared Validation / QA | `validate_brd.py`, `validate_prd.py`, `validate_adr.py`, `validate_sys.py`, fixture suites | Deterministic pass/fail checks for required C4/DFD/Sequence controls across MVP and non-MVP profiles |
| Shared AI Skill Layer | `.claude/skills/doc-*/SKILL.md` (generation/reviewer/fixer where applicable) | Prompt contracts and review/fix behavior aligned with layer-specific C4-DFD-Seq rules |

#### Phase E Exit Checklist (Done/Not Done)
- [ ] **Framework Standards complete**: `DIAGRAM_STANDARDS.md` and `MVP_WORKFLOW_GUIDE.md` updated and aligned to C4-DFD-Seq taxonomy and lifecycle enforcement.
- [ ] **Layer 1 BRD complete**: BRD template/rules/validator/quality-gate/skills updated to enforce C4 L1 + DFD L0 (+ conditional sequence).
- [ ] **Layer 2 PRD complete**: PRD template/rules/validator/quality-gate/skills updated to enforce C4 L2 + DFD L1 + required sequence error-path checks.
- [ ] **Layer 5 ADR complete**: ADR template/rules/validator/quality-gate/skills updated to enforce C4 L3 + required decision choreography sequence (+ DFD L2 conditions).
- [ ] **Layer 6 SYS complete**: SYS template/rules/validator/quality-gate/skills updated to enforce System Diagram Contract and downstream SPEC ownership reference.
- [ ] **Layer 9+ SPEC/Code/Test complete**: SPEC-side ownership controls for C4 L4 implemented and validated against SYS references.
- [ ] **Shared Validation/QA complete**: validator + fixture updates implemented with deterministic pass/fail coverage for MVP and non-MVP profiles.
- [ ] **Shared AI Skill Layer complete**: generation/review/fix skill prompts and checks aligned with the C4-DFD-Seq contract by layer.

### Phase F: MVP Cycle Pilot (Build and Validate)
- Run pilot on one MVP BRD→PRD→ADR chain.
- Extend pilot path to include SYS and SPEC checkpoints for C4 L4 ownership handoff.
- Validate diagram controls during MVP artifact creation and quality gates.
- Measure defect types and AI regeneration frequency for MVP artifacts.

### Phase G: PROD Feedback Capture (Operate and Learn)
- Capture production feedback specific to diagram quality outcomes:
  - ambiguity in implementation handoff
  - review defects tied to structure/data-flow/temporal gaps
  - rework categories linked to C4/DFD/sequence coverage
- Record findings in lifecycle review notes for the cycle.

### Phase H: NEW MVP Re-Entry (Next Iteration)
- Convert PROD findings into updated diagram requirements for next BRD.
- Require cross-cycle link from new BRD using `@depends` to prior BRD.
- Re-run parity checks before enabling strict mode for the next cycle.

## 6. AI-Specific Failure Modes and Controls
| Failure Mode | Cause | Control |
|---|---|---|
| Semantic blending (C4 + DFD in one view) | Ambiguous prompts | Diagram contract tags + lint rule |
| Missing error path in sequence | Happy-path-only generation | Mandatory alternate/exception branch check |
| Inconsistent actor naming | Synonym expansion by model | Node naming registry + uniqueness check |
| Diagram drift from text requirements | Regeneration without trace refs | Mandatory upstream_refs/downstream_refs fields |
| Over-detailed BRD diagrams | AI over-specification | Abstraction-level guardrail per artifact |

## 7. Resource Requirements and Constraints
Resources:
- Maintainer time for template/rule/validator edits.
- Validator test fixtures for compliant and non-compliant diagrams.
- Reviewer skill updates for AI prompt contracts.
- CI execution capacity for fixture suite and profile-parity checks.

Constraints:
- Mermaid-only requirement remains mandatory.
- Backward compatibility must preserve existing valid artifact IDs and traceability tags.
- No expansion to additional modeling standards until C4/DFD/Sequence stabilizes.

Migration constraints:
- Legacy corpus requires a staged enforcement window to avoid mass false-failures.
- New and modified artifacts use strict mode first; unchanged legacy artifacts use compatibility mode temporarily.

## 8. Validation and Acceptance Criteria
Acceptance criteria:
1. BRD validator fails when C4 L1 or DFD L0 is missing in required sections.
2. PRD validator fails when C4 L2, DFD L1, or required sequence diagrams are missing.
3. ADR validator fails when C4 L3 is missing and warns/fails per policy for required sequence/DFD L2 conditions.
4. SYS validator enforces required System Diagram Contract content and validates reference to downstream SPEC location for C4 L4 ownership.
5. SYS quality-gate visualization checks are upgraded from Info to Warning/Error for required conditions.
6. Quality-gate docs contain deterministic checks matching validator behavior.
7. AI generation prompts produce compliant diagrams in pilot artifacts without manual structural fixes.
8. Baseline alignment report confirms zero unresolved validator/template section mismatches for targeted profiles.
9. Fixture suite passes for all targeted validators with explicit pass/fail coverage.
10. MVP and non-MVP profile checks produce equivalent core enforcement outcomes.
11. Explicit implementation commits exist for each affected layer (BRD, PRD, ADR, SYS, SPEC) covering template/rules/validator/quality-gate/skill touchpoints where applicable.
12. Framework-level docs (`DIAGRAM_STANDARDS.md`, `MVP_WORKFLOW_GUIDE.md`) are updated and aligned with per-layer enforcement behavior.
13. PROD feedback report produced for the pilot cycle with diagram-related defect taxonomy.
14. NEW MVP entry artifact includes cross-cycle dependency link (`@depends`) and updated diagram constraints derived from PROD feedback.

## 9. Measurable Impact Metrics
- Diagram compliance rate: compliant artifacts / total artifacts.
- Regeneration rate: diagram-related AI rewrite count per artifact.
- Review findings density: diagram-related findings per review cycle.
- Traceability completeness: required diagram tags linked to upstream/downstream references.

## 10. Recommended Next Step
Execute phases in lifecycle order: **Phase 0 → A → B → C → D → E (all-layer implementation) → F (MVP pilot) → G (PROD feedback capture) → H (NEW MVP re-entry)**.

## 10.1 Implementation Delegation (Execution Authority)
This IPLAN remains the umbrella strategy and governance plan for C4-DFD-Seq adoption.

Detailed implementation execution is delegated to:
- `plans/IPLAN-007_c4_dfd_seq_foundation_layers_execution.md`
  - scope: framework + BRD/PRD/ADR/SYS + validators/fixtures + related skills.
- `plans/IPLAN-008_c4_dfd_seq_spec_rollout_execution.md`
  - scope: SPEC/Code/Test ownership enforcement + end-to-end pilot + MVP→PROD→NEW MVP rollout controls.

Execution order and dependency:
1. Execute IPLAN-007 first (foundation implementation baseline).
2. Execute IPLAN-008 second (downstream ownership and lifecycle rollout), dependent on IPLAN-007 outputs.

No-duplication rule:
- Do not duplicate implementation tasks between IPLAN-006 and IPLAN-007/IPLAN-008.
- IPLAN-006 tracks policy, governance, checkpoints, and lifecycle decisions; implementation evidence is recorded in IPLAN-007 and IPLAN-008 deliverables.

## 11. Recommendation Updates (Applied to This Plan)
### 11.1 Priority Order (Must Implement First)
1. Diagram Contract Tags + Intent Header
- Make these mandatory before adding strict validator checks.
- Rationale: AI generation quality depends on deterministic parsing and retrieval metadata.

2. Trust Boundary Annotation in DFD
- Enforce for DFD L0/L1/L2 in BRD/PRD/ADR where applicable.
- Rationale: security and compliance analysis depend on explicit boundary mapping.

3. Sequence Error-Path Requirement
- Require at least one alternate/exception path in required sequence diagrams.
- Rationale: AI-generated happy-path-only outputs underrepresent operational risk.

4. Canonical Naming Registry
- Add per-document actor/component naming table and enforce reuse.
- Rationale: reduces AI synonym drift and improves cross-layer traceability.

5. Diagram Delta Rule per Iteration
- Add subsection documenting changes from prior cycle artifacts.
- Rationale: minimizes full regeneration and improves review precision.

### 11.2 Default Enforcement Policy
- BRD:
  - Error: missing C4 L1 or DFD L0.
  - Warning: missing trust boundary annotation.
  - Info: missing optional business sequence.
- PRD:
  - Error: missing C4 L2, DFD L1, or primary sequence for top journeys.
  - Warning: missing exception path in sequence.
  - Info: missing additional sequence variants.
- ADR:
  - Error: missing C4 L3.
  - Error: missing sequence diagram when decision changes interaction choreography.
  - Warning: missing DFD L2 for data-impacting decisions.
- SYS:
  - Error: missing required "System Diagram Contract" subsection.
  - Error: missing required C4 L2/L3 references and required sequence path constraints in System Diagram Contract.
  - Warning: missing DFD boundary tags where data movement boundaries are described.
  - Error: missing downstream SPEC location reference for C4 L4 ownership.
- SPEC / Code / Tests (Layer 9+):
  - Error: missing declared C4 L4 ownership location where required by SYS references.

### 11.3 AI Prompt Contract Defaults
Add to template AI context blocks as default constraints:
- Include exactly one diagram purpose statement before each required diagram block.
- Use only registered actor/component names.
- Keep C4, DFD, and sequence semantics separate (no mixed diagram intent).
- Include one explicit failure/timeout/retry branch in required sequence diagrams.

### 11.4 Rollout Checkpoints (Execution Control)
Checkpoint 0: Baseline Alignment Ready
- Known validator/template naming mismatches resolved and verified.

Checkpoint 1: Standards Ready
- DIAGRAM_STANDARDS includes taxonomy, tags, intent header, trust boundary policy.

Checkpoint 2: Template Ready
- BRD/PRD/ADR/SYS templates include required diagram sections and AI guardrails.

Checkpoint 3: Validator Ready
- Validators enforce mandatory diagram presence and profile-specific rules.
- Compatibility mode available for legacy corpus during migration window.
- Fixture suite implemented and passing for target scenarios.
- SYS validator enforces System Diagram Contract and C4 L4 ownership reference checks.

Checkpoint 4: Quality Gate Ready
- Quality-gate docs mirror validator logic with same severities and outcomes.
- SYS quality-gate severities aligned with validator outcomes for required visualization controls.

Checkpoint 5: Implementation Complete (All Affected Layers)
- Framework docs, targeted layer templates/rules/validators/quality-gates, and related skills are updated and internally consistent.
- SPEC ownership checks for C4 L4 are implemented and linked from SYS requirements.

Checkpoint 6: Pilot Pass
- One BRD→PRD→ADR chain validates without manual diagram structure fixes.
- SYS and SPEC checkpoints validate C4 L4 ownership handoff behavior.
- MVP and non-MVP parity checks pass for core rules.

Checkpoint 7: PROD Feedback Captured
- Pilot cycle includes production feedback report with diagram-related findings.

Checkpoint 8: NEW MVP Re-Entry Ready
- Next-cycle BRD planning includes `@depends` linkage and updated diagram controls from PROD findings.

### 11.5 Definition of Done
- All rollout checkpoints (0-8) passed.
- Compliance rate for pilot artifacts >= 95%.
- Manual diagram rework reduced by >= 50% against baseline sample.

## 12. Governance and Migration Policy
### 12.1 Compatibility Window
- Duration: defined by maintainer at rollout start.
- Scope: unchanged legacy artifacts remain warning-first for new C4/DFD/sequence checks.
- Exit condition: fixture suite stable and pilot compliance threshold achieved.

### 12.2 Strict Mode Activation
- Apply strict mode immediately to newly created artifacts.
- Apply strict mode to any artifact materially modified after rollout date.

### 12.3 Non-MVP Profile Parity
- Maintain a parity checklist for BRD/PRD/ADR standard profiles.
- Core rule parity required: mandatory diagram types, tags, trust boundaries, and sequence error-path checks.

### 12.4 Operational Reporting
- Publish weekly migration report during compatibility window:
  - validator failure counts by rule and layer
  - false-positive triage status
  - strict-mode adoption percentage

### 12.5 Lifecycle Reporting (MVP → PROD → NEW MVP)
- At cycle close, publish:
  - MVP artifact compliance summary
  - PROD feedback summary for diagram-driven defects
  - NEW MVP carry-forward control updates

## 13. Execution Status Snapshot (2026-02-26, EST)

Status: **In Progress (not end-to-end complete)**

Completed in current execution window:
- Framework standards updated for C4/DFD/Sequence governance and layer enforcement (`DIAGRAM_STANDARDS.md`, `MVP_WORKFLOW_GUIDE.md`).
- Foundation validator and quality-gate implementation advanced from documentation-only to executable checks for BRD/PRD/ADR/SYS.
- BRD/PRD/ADR/SYS quality-gate scripts updated to enforce layer-specific diagram contract checks.
- ADR/SYS quality-gate script execution defects corrected (`check_visualization` call path and numeric parsing issues).
- Targeted smoke execution performed with fixture corpus under `tmp/diagram_contract_fixtures/`.
- BRD/PRD/ADR/SYS reviewer skills updated to include explicit diagram-contract compliance checks aligned with runtime validator/gate semantics.
- IPLAN-008 SPEC bridge fixture threshold completed (2 pass / 4 fail deterministic linkage tests for SYS→SPEC ownership mapping).
- IPLAN-008 pilot pass matrix evidence produced across BRD/PRD/ADR/SYS/SPEC/TSPEC/TASKS (`tmp/IPLAN-008_PILOT_PASS_MATRIX_RAW.txt`, `tmp/IPLAN-008_PILOT_PASS_MATRIX_REPORT_2026-02-26.md`).
- IPLAN-008 PROD feedback taxonomy report and NEW MVP re-entry controls with `@depends` lineage evidence produced.

Still pending for IPLAN-006 closure:
- Delegated execution closeout of IPLAN-007 compatibility-window quantitative criteria.
- IPLAN-008 strict-mode release criteria verification in downstream chain.
- Final umbrella-plan sign-off with explicit evidence links from IPLAN-007/IPLAN-008 deliverables.
