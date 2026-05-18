---
title: "IPLAN-007: C4-DFD-Seq Foundation Layers Execution"
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
  timezone: "America/New_York"
  parent_plan: "IPLAN-006"
---

# IPLAN-007: C4-DFD-Seq Foundation Layers Execution

## 1. Purpose
Execute implementation of the **C4-DFD-Seq** design approach across framework standards and foundation documentation layers:
- Framework standards
- BRD (Layer 1)
- PRD (Layer 2)
- ADR (Layer 5)
- SYS (Layer 6)

This plan is implementation-focused and closes execution gaps identified in IPLAN-006:
- explicit file-level targets
- owner/dependency/evidence tracking
- quantified acceptance gates
- strict compatibility-window exit criteria

## 2. Scope
In scope:
- `ai_dev_ssd_flow/DIAGRAM_STANDARDS.md`
- `ai_dev_ssd_flow/MVP_WORKFLOW_GUIDE.md`
- `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/02_PRD/PRD-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/05_ADR/ADR-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/06_SYS/SYS-MVP-TEMPLATE.md`
- BRD/PRD/ADR/SYS creation rules + validation rules + quality-gate docs
- BRD/PRD/ADR/SYS validators and fixture tests
- `.claude/skills/doc-brd/SKILL.md`
- `.claude/skills/doc-prd/SKILL.md`
- `.claude/skills/doc-adr/SKILL.md`
- `.claude/skills/doc-sys/SKILL.md`
- Reviewer skills for BRD/PRD/ADR/SYS

Out of scope:
- SPEC template internals and downstream implementation artifacts (covered by IPLAN-008)
- historical backfill of unchanged legacy documents

## 3. Target Design Rules (Must Enforce)
- BRD: required C4 L1 + DFD L0; sequence conditional for critical journeys.
- PRD: required C4 L2 + DFD L1 + required top-journey sequence with exception path.
- ADR: required C4 L3 + required decision choreography sequence; DFD L2 conditional for data-impact decisions.
- SYS: required System Diagram Contract with C4 L2/L3 references, DFD boundary tags, and sequence path constraints.
- Mermaid-only diagram format.
- Diagram contract tags + intent header for machine-parseable validation.

## 4. Implementation Matrix (File-by-File, Actionable)
| Workstream | Files | Owner | Depends On | Evidence Required |
|---|---|---|---|---|
| Framework Standards | `DIAGRAM_STANDARDS.md`, `MVP_WORKFLOW_GUIDE.md` | Framework Maintainer | None | diff + updated section anchors for taxonomy/ownership |
| BRD Layer | BRD template, BRD rules, BRD quality gate, BRD validator, BRD skills | BRD Maintainer | Framework Standards | validator pass + fixture pass + skill prompt updates |
| PRD Layer | PRD template, PRD rules, PRD quality gate, PRD validator, PRD skills | PRD Maintainer | Framework Standards | validator pass + fixture pass + skill prompt updates |
| ADR Layer | ADR template, ADR rules, ADR quality gate, ADR validator, ADR skills | ADR Maintainer | Framework Standards | validator pass + fixture pass + section-name parity proof |
| SYS Layer | SYS template, SYS rules, SYS quality gate, SYS validator, SYS skills | SYS Maintainer | Framework Standards, ADR | validator pass + fixture pass + System Diagram Contract checks |
| Shared Validation | `validate_brd.py`, `validate_prd.py`, `validate_adr.py`, `validate_sys.py`, fixtures | Validation Maintainer | BRD/PRD/ADR/SYS updates | deterministic pass/fail fixtures for all required controls |

## 5. Execution Steps
### Step A: Baseline Alignment
- Resolve current validator/template section-name mismatches before new checks.
- Generate baseline mismatch report with remaining issue count.

### Step B: Framework Rule Implementation
- Implement C4/DFD/Sequence taxonomy, intent headers, diagram tags, trust-boundary standard, and migration policy.

### Step C: Layer Template + Rule Implementation
- Implement BRD/PRD/ADR/SYS template and rule changes with identical semantics.
- Add AI guardrails in generation context blocks.

### Step D: Validator + Fixture Implementation
- Implement required checks by layer and profile.
- Implement compatibility mode (warning-first) for unchanged legacy docs.
- Add deterministic fixtures for required/optional/forbidden combinations.

### Step E: Quality Gate + Skills Implementation
- Align quality gate severities with validator severities.
- Update generation/reviewer skill prompts and checklists to same contract.

### Step F: Foundation Verification
- Run targeted validator + fixture suites.
- Produce implementation evidence pack for each matrix row.

## 6. Quantified Acceptance Criteria
1. Baseline mismatch report shows **0 unresolved section-name mismatches** for BRD/PRD/ADR/SYS.
2. Each foundation validator fails on missing required diagrams for its layer.
3. Each foundation validator enforces required sequence exception-path checks where specified.
4. Each foundation validator enforces trust-boundary requirements where specified.
5. Quality-gate outcomes match validator outcomes with **0 severity drift** on fixture corpus.
6. Reviewer skills include explicit checks for abstraction-level correctness and temporal completeness.
7. Fixture suite includes at least:
   - 4 pass fixtures (one per layer)
   - 8 fail fixtures (two per layer)
8. MVP and non-MVP profiles produce equivalent outcomes for core mandatory checks.

## 7. Compatibility Window (Quantified)
- Duration: **2 release cycles** from merge date.
- Mode:
  - new or materially modified artifacts: strict mode
  - unchanged legacy artifacts: warning-first mode
- Exit criteria (all required):
  1. strict-mode adoption ≥ 90% of active artifacts
  2. false-positive rate < 5% over rolling 2-week sample
  3. zero unresolved P1 validator defects

## 8. Metrics, Baseline, and Ownership
| Metric | Baseline Window | Target | Owner | Collection Method |
|---|---|---|---|---|
| Diagram compliance rate | 2 weeks pre-merge | ≥ 95% | Validation Maintainer | validator reports |
| Diagram-related regeneration rate | 2 weeks pre-merge | -40% from baseline | Layer Maintainers | generation logs |
| Review finding density (diagram category) | 2 weeks pre-merge | -35% from baseline | Reviewer Maintainers | review reports |
| Severity drift (validator vs quality gate) | first post-merge week | 0 | QA Maintainer | fixture diff checks |

## 9. Exit Checklist (Done/Not Done)
- [x] Framework standards implemented with evidence.
- [x] BRD layer implemented with validator+fixture evidence.
- [x] PRD layer implemented with validator+fixture evidence.
- [x] ADR layer implemented with validator+fixture evidence.
- [x] SYS layer implemented with validator+fixture evidence.
- [x] Shared validation and fixtures implemented with deterministic outcomes.
- [x] Quality-gate and reviewer skills aligned with validator severities.
- [ ] Quantified compatibility-window entry criteria met.

### 9.1 Checklist Evidence Snapshot (2026-02-26, EST)
- Implemented files include framework standards, BRD/PRD/ADR/SYS validators, and BRD/PRD/ADR/SYS quality-gate scripts.
- Executable quality-gate behavior validated with targeted shell runs and fixture corpus under `tmp/diagram_contract_fixtures/`.
- Reviewer-skill parity is completed for BRD/PRD/ADR/SYS diagram-contract checks.
- Remaining open item is limited to quantified compatibility-window entry criteria collection.

## 10. Deliverables
- Updated framework standards docs
- Updated BRD/PRD/ADR/SYS templates/rules/quality-gates
- Updated BRD/PRD/ADR/SYS validators + fixtures
- Updated generation/reviewer skills for these layers
- Foundation evidence pack (owner, date, file refs, validation outputs)
