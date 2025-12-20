# doc-iplan-validator

Validate Implementation Plans (IPLAN) documents against Layer 12 schema standards.

## Activation

Invoke when user requests validation of IPLAN documents or after creating/modifying IPLAN artifacts.

## Validation Schema Reference

Schema: `ai_dev_flow/IPLAN/IPLAN_SCHEMA.yaml`
Layer: 12
Artifact Type: IPLAN

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["iplan", "template"]
  - artifact_type: "IPLAN"
  - layer: 12
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - iplan (or iplan-template)
  - layer-12-artifact

Forbidden tag patterns:
  - "^implementation-plan$"
  - "^tasks-plan$"
  - "^iplan-\\d{3}$"
```

### 2. Structure Validation

**Required Sections (13 sections):**
- Title (H1): `# IPLAN-NNN: Title`
- Section 1: Document Control
- Section 2: Position in Workflow
- Section 3: Objective
- Section 4: Context (Prerequisites, Dependencies, Assumptions)
- Section 5: Task List (from source TASKS document)
- Section 6: Implementation Guide (Bash commands, Verification steps)
- Section 7: Technical Details (Architecture, Code Patterns, Configs)
- Section 8: Traceability Tags (all cumulative tags)
- Section 9: Traceability (Upstream Sources, Downstream Artifacts)
- Section 10: Risk Mitigation (Session Risks, Rollback Plan)
- Section 11: Success Criteria (Verification Checklist)
- Section 12: References
- Section 13: Appendix (Checklists, Error Handling, Notes)

**Document Control Required Fields:**
- IPLAN ID
- Document Name
- Version
- Date Created
- Last Updated
- Author
- Status
- Source TASKS

**File Naming:**
Pattern: `IPLAN-NNN_descriptive_name.md`

### 3. Content Validation

**Status Values:**
- Draft
- Ready
- In Progress
- Completed
- Aborted
- Blocked

**Session Format:**
- Pattern: `Session N:`
- Components: session_number, session_name, objective, tasks, verification, duration

**Implementation Guide Structure:**
- Required: Pre-Implementation Checklist, Implementation Steps, Verification Steps
- Optional: Post-Implementation Checklist, Rollback Steps

**Bash Command Blocks:**
- Format: ` ```bash`
- Patterns: `# Step N:`, `# Verification:`, `# Rollback:`
- Safety checks: No `rm -rf` without confirmation, no force push to main/master, no destructive database operations

**Verification Checklist Format:**
- Format: `- [ ] Verification item`
- Categories: Unit Tests, Integration Tests, Build Success, Linting Pass, Security Scan

**Appendix Checklists:**
- Pre-Implementation: Working directory clean, Dependencies installed, Environment configured, Tests passing, Branch created
- Security: No secrets in code, Input validation, Error messages sanitized, Authentication verified
- Error Handling: try/except with specific exceptions, Proper error logging, User-friendly messages, Circuit breaker patterns
- Async/Concurrency: async/await used correctly, No race conditions, Proper resource cleanup, Timeout handling

### 4. Traceability Validation

**Layer 12 Cumulative Tags (9 required):**
- @brd: BRD.NN.EE.SS (required)
- @prd: PRD.NN.EE.SS (required)
- @ears: EARS.NN.EE.SS (required)
- @bdd: BDD.NN.EE.SS (required)
- @adr: ADR-NN (required)
- @sys: SYS.NN.EE.SS (required)
- @req: REQ.NN.EE.SS (required)
- @spec: SPEC-NN (required)
- @tasks: TASKS.NN.EE.SS (required)
- @impl: IMPL.NN.EE.SS (optional)
- @ctr: CTR-NN (optional)

**Downstream Expected:**
- Code (src/...)
- Tests (tests/...)
- Commit (git commit SHA)

**Same-Type References:**
- @related-iplan: IPLAN-NN
- @depends-iplan: IPLAN-NN
- @continues-iplan: IPLAN-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| IPLAN-E001 | error | Missing required tag 'iplan' |
| IPLAN-E002 | error | Missing required tag 'layer-12-artifact' |
| IPLAN-E003 | error | Invalid document_type |
| IPLAN-E004 | error | Invalid architecture_approaches format |
| IPLAN-E005 | error | Forbidden tag pattern detected |
| IPLAN-E006 | error | Missing required section |
| IPLAN-E007 | error | Multiple H1 headings detected |
| IPLAN-E008 | error | Section numbering not sequential (1-13) |
| IPLAN-E009 | error | Document Control missing required fields |
| IPLAN-E010 | error | Missing Task List (Section 5) |
| IPLAN-E011 | error | Missing Implementation Guide (Section 6) |
| IPLAN-E012 | error | Missing Traceability Tags (Section 8) |
| IPLAN-E013 | warning | File name does not match format |
| IPLAN-E014 | error | Source TASKS not in valid format |
| IPLAN-W001 | warning | Task List does not reference source TASKS |
| IPLAN-W002 | warning | Implementation Guide missing bash commands |
| IPLAN-W003 | warning | Traceability Tags incomplete (require 9) |
| IPLAN-W004 | warning | Success Criteria missing verification checklist |
| IPLAN-W005 | warning | Appendix missing Pre-Implementation Checklist |
| IPLAN-W006 | warning | Risk Mitigation section empty |
| IPLAN-I001 | info | Consider adding rollback steps |
| IPLAN-I002 | info | Consider adding Security Checklist |
| IPLAN-I003 | info | Consider adding Error Handling Standard |

## Validation Commands

```bash
# Validate single IPLAN document
python ai_dev_flow/scripts/validate_iplan.py docs/IPLAN/IPLAN-001_example.md

# Validate all IPLAN documents
python ai_dev_flow/scripts/validate_iplan.py docs/IPLAN/

# Check with verbose output
python ai_dev_flow/scripts/validate_iplan.py docs/IPLAN/ --verbose
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify section structure (1-13)
5. Validate Document Control table
6. Check Task List references source TASKS
7. Validate Implementation Guide (bash commands present)
8. Check Traceability Tags section (9 cumulative tags)
9. Verify Success Criteria (verification checklist)
10. Check Appendix checklists
11. Validate upstream references (9 required)
12. Verify file naming convention
13. Generate validation report

## Integration

- Invoked by: doc-flow, doc-iplan (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
IPLAN Validation Report
=======================
Document: IPLAN-001_example.md
Status: PASS/FAIL

Session Structure:
- Source TASKS: TASKS-NNN (Valid/Invalid)
- Tasks referenced: N
- Bash command blocks: N

Implementation Guide:
- Pre-Implementation Checklist: Present/Missing
- Implementation Steps: Present/Missing
- Verification Steps: Present/Missing
- Rollback Steps: Present/Missing

Traceability Tags:
- Required tags (9): N/9
- Optional tags: N

Appendix Checklists:
- Pre-Implementation: Present/Missing
- Security: Present/Missing
- Error Handling: Present/Missing
- Async/Concurrency: Present/Missing

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```
