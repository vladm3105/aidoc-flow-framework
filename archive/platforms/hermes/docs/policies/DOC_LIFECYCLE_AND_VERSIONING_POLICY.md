# Documentation Lifecycle and Versioning Policy

| Field | Value |
| --- | --- |
| Policy ID | DOC-LIFECYCLE-POLICY-001 |
| Status | Active |
| Version | 2.1 |
| Date | 2026-05-06 |
| Scope | MCP documentation lifecycle, version changes, and update triggers |

---

## 1. Objective

Define mandatory lifecycle states, versioning rules, and update triggers for MCP documentation artifacts.

Implementation complexity: 3/5.

---

## 2. Planning-First Governance Gate

Mandatory pre-creation gate for every layer and every workstream type (documentation, testing, and coding):

1. Analyze provided source information and constraints.
2. Create a layer roadmap artifact.
3. Create a layer planning index listing required planning documents.
4. Define per-layer changelog scope and expected entries.
5. Review roadmap and planning index for gaps and resolve gaps or record explicit deferrals.
6. Create document-level implementation plans (IPLAN) for each target artifact before implementation work.
7. Run plan review and gap-fix pass on each IPLAN.
8. Record explicit plan approval.

Mandatory constraints:

- No lifecycle artifact creation starts before the planning gate is approved.
- No testing or coding work starts before the corresponding approved IPLAN exists.
- Plan approval authority is either a human reviewer or an independent LLM-as-judge session started from a fresh context.
- Plan review must verify missing artifacts, dependency coverage, and traceability completeness.

---

## 3. Lifecycle States

Allowed lifecycle states:

- draft
- active
- deprecated
- archived

State transition rules:

- draft to active requires quality gate PASS.
- active to deprecated requires replacement reference or explicit no-replacement rationale.
- deprecated to archived requires deprecation window completion and final reconciliation entry.

---

## 4. Versioning Rules

Version increments:

- patch: typo, formatting, non-normative clarifications with no contract impact
- minor: added sections, added examples, expanded validation guidance without breaking contract
- major: normative rule change, precedence change, compatibility behavior change, or gate behavior change

Required update behavior:

- Every version increment must update revision history in the artifact.
- Major version changes must include a compatibility note and migration note.

---

## 5. Mandatory Review Triggers

A documentation review is required when changes affect:

- ucx_hermes/src/mcp_server/cli/main.py (CLI surface contract)
- ucx_hermes/src/mcp_server/prompts/context_builder.py (source mapping and prompt assembly contracts)
- ucx_hermes/src/mcp_server/review/runner.py (artifact emission and run result contracts)
- ucx_hermes/src/mcp_server/remediation/runner.py (remediation artifact emission and fix-instruction contracts)
- ucx_hermes/src/mcp_server/skills/project_ucx_loader.py (project asset loading and missing-asset behavior)
- prompt artifact schema or sidecar output structure

---

## 6. Pull Request Governance Lifecycle

Mandatory PR governance sequence for issue-fix workflows:

1. Complete and approve the planning-first governance gate.
2. Define task (human or AI-originated).
3. Create GitHub issue with acceptance criteria and traceability tags.
4. Perform implementation work according to approved plans and submit pull request.
5. Execute Round 1 gate sequence:
   - `sdd_validate`
   - `sdd_review`
   - `sdd_remediate`
   - post-remediation `sdd_validate`
   - Hermes final blocker-gap/inconsistency review
6. If Round 1 fails, execute Round 2 with the same sequence.
7. If Round 2 fails, escalate to human review and block merge.
8. On merge, close linked GitHub issue(s).

Alert channels for escalation and merge-time notifications are implementation-defined.

---

## 7. Compatibility and Deprecation Constraints

Mandatory constraints:

- Deprecated artifacts must remain readable during deprecation period when policy requires compatibility.
- New canonical artifacts must not silently change semantics of existing active docs.
- Deprecation entry must specify start date, planned sunset date, and replacement artifact.

Failure modes:

- Contract-impacting change published as patch.
- Deprecated artifact removed without replacement or rationale.
- Runtime behavior changes with no triggered doc update.

---

## 8. Evidence Requirements

Required evidence for lifecycle compliance:

- Planning package artifacts (roadmap, planning index, per-layer changelog plan).
- Plan review artifact with resolved gaps and explicit deferrals.
- Plan approval record (human reviewer or independent LLM-as-judge session).
- Updated revision history entries
- Reconciliation log update in DOC-RECONCILIATION-LOG-001
- Coverage matrix update in DOC-COVERAGE-MATRIX-001
- Compliance report update in COMPLIANCE-REPORT-002 when gates are re-evaluated
- PR round artifacts: validation report(s), review/remediation report(s), Hermes final review result
- Escalation artifact when human review is required

---

## 9. Resource Requirements and Constraints

- Contributors: docs-maintainer plus runtime-maintainer reviewer
- Storage: negligible
- Constraint: lifecycle status and version must remain machine-parseable and deterministic
