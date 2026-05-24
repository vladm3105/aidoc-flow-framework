# SDD v3.2 Workflow Quickstart

## Layer Sequence

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → SPEC (L6) → TDD (L7) → IPLAN (L8) → Code
```

## Document Types & File Conventions

| Layer | Artifact | Folder | Template |
|-------|----------|--------|----------|
| 1 | BRD — Business Requirements Document | 01_BRD/ | framework/layers/01_BRD/BRD-TEMPLATE.yaml |
| 2 | PRD — Product Requirements Document | 02_PRD/ | framework/layers/02_PRD/PRD-TEMPLATE.yaml |
| 3 | EARS — Easy Approach to Requirements Syntax | 03_EARS/ | framework/layers/03_EARS/EARS-TEMPLATE.yaml |
| 4 | BDD — Behavior-Driven Development | 04_BDD/ | framework/layers/04_BDD/BDD-TEMPLATE.yaml |
| 5 | ADR — Architecture Decision Record | 05_ADR/ | framework/layers/05_ADR/ADR-TEMPLATE.yaml |
| 6 | SPEC — Technical Specification | 06_SPEC/ | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml |
| 7 | TDD — Test-Driven Development Guide | 07_TDD/ | framework/layers/07_TDD/TDD-TEMPLATE.yaml |
| 8 | IPLAN — Implementation Plan | 08_IPLAN/ | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml |

## Document & Element ID Formats

- **Document ID**: `TYPE-NN` (e.g., `BRD-01`, `ADR-03`)
- **Element ID**: `TYPE.NN.SS.xxxx` (e.g., `BRD.01.07.a7f3`)
  - TYPE = artifact prefix (BRD, PRD, etc.)
  - NN = document number (2+ digits)
  - SS = section number (2+ digits)
  - xxxx = SHA256 first-4-char hex hash

## Cumulative Tag Hierarchy

Each document must include tags for ALL upstream layers:

- BRD: none (root)
- PRD: `@brd`
- EARS: `@brd, @prd`
- BDD: `@brd, @prd, @ears`
- ADR: `@brd, @prd, @ears, @bdd`
- SPEC: `@brd, @prd, @ears, @bdd, @adr`
- TDD: `@brd, @prd, @ears, @bdd, @adr, @spec`
- IPLAN: `@brd, @prd, @ears, @bdd, @adr, @spec, @tdd`

## Three-Phase Lifecycle (per document)

### Phase 1: Create (UCC)

1. Load the appropriate template
2. Dispatch creation personas as parallel subagents
3. Synthesize contributions into a complete document
4. Validate output against layer schema

### Phase 2: Review (UCR)

1. Dispatch ALL listed persona subagents in parallel
2. Collect all findings
3. Fact-checker cross-validates all P0/P1 findings
4. Board-chairperson synthesizes, de-duplicates, scores
5. Score must be >= 90/100 to proceed to next layer

### Phase 3: Remediate (UCRem)

1. Pre-screen findings to determine which domain fixers needed
2. Dispatch fixers as parallel subagents
3. Board-chairperson synthesizes fixes, resolves conflicts

## Review Persona Dispatch by Doc Type

| Doc Type | Parallel Subagents |
|----------|-------------------|
| BRD | system-architect, security-auditor, business-analyst, chaos-engineer |
| PRD | system-architect, security-auditor, technical-lead, product-owner, chaos-engineer |
| EARS | requirements-specialist, technical-lead, qa-lead, chaos-engineer |
| BDD | qa-lead, technical-lead, chaos-engineer, site-reliability-engineer, security-auditor |
| ADR | system-architect, technical-lead, site-reliability-engineer, security-auditor, chaos-engineer |
| SPEC | technical-lead, system-architect, chaos-engineer, site-reliability-engineer, integration-specialist |
| TDD | qa-lead, technical-lead, chaos-engineer, site-reliability-engineer, security-auditor |
| IPLAN | technical-lead, system-architect, site-reliability-engineer, qa-lead, security-auditor |

## Self-Consistent Audit Loop

```
LOOP (max 3 iterations):
  1. Run review (parallel persona subagents)
  2. Fact-checker validates P0/P1 findings
  3. Chairperson synthesizes → produce report
  4. Run remediation (fixer subagents)
  5. Re-run review on fixed document
  6. IF score >= 90 → DONE
  7. IF score < 90 AND iteration < 3 → GOTO 1
  8. IF iteration == 3 → Report manual review needed
```

## TDD-First Code Generation

1. Generate test files FIRST (from TDD Sections 3-4)
2. Run tests — they MUST fail
3. Generate implementation files (from IPLAN file manifest)
4. Run tests — they MUST pass
5. Refactor — keep tests green

## Upstream Artifact Policy

If a required upstream artifact is missing, skip that functionality — do NOT create the missing upstream document. Report the gap to the user.
