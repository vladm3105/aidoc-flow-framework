# Governance

This repository is the **source of truth** for aidoc-flow project governance.
The engine-agnostic standards live in
[`framework/governance/`](framework/governance/README.md) and apply across every
aidoc-flow repository. Consuming repositories reference this governance; they do
not copy it.

## Standards

See [`framework/governance/README.md`](framework/governance/README.md) for the
full index. Key documents:

- `DOC_GOVERNANCE_CORE.md` — core principles (single source of truth, YAML-first
  templates, immutability, validation baseline).
- `ID_NAMING_STANDARDS.md` — document IDs, element IDs, traceability tags, file
  naming.
- `TRACEABILITY.md` — the traceability chain and readiness gates.
- `REVIEW_TEAM.md` + `REVIEW_CREWS.yaml` — the multi-persona review model.
- `REVIEW_REMEDIATION_FLOW.md` — the review to remediation to gate quality loop + the independent `pre_merge` review gate.
- `DEFINITION_OF_DONE.md` — completion criteria (artifact + spec change) and the risk-tiered human-in-loop.
- `SECURITY_REVIEW.md` — safety checks for agent-authored artifacts.
- `AUTHORING_STYLE.md` — token-efficient authoring rules.
- `DIAGRAM_STANDARDS.md` + `THRESHOLD_NAMING_RULES.md` — diagram and threshold
  conventions.
- `ADAPTATION.md` + `ADAPTATION_SURFACE.yaml` — how a consuming repo adapts the
  flow without forking.
- `DECISIONS.md` — durable register of governance and spec decisions.
- `chg/` — the change-management overlay and GATE-SPEC (CHG-D1), the meta gate
  governing changes to the `framework/` spec itself.

## Changing governance

Governance changes are proposed and ratified here through the CHG / GATE-SPEC
process (`framework/governance/chg/`). The spec defines the gates; each
consuming platform implements enforcement against this shared contract (record
validator, CI, protected-branch review). This model is recorded as GD-01 in
`framework/governance/DECISIONS.md`.

## Agent Enforcement

The framework provides five enforcement mechanisms for AI agents:

1. **CLAUDE.md gate** — Project CLAUDE.md must include a mandatory governance
   gate (§3.4) and session-start verification. See `CLAUDE.md` → "MANDATORY:
   Governance Gate".

2. **§3.4.1 post-creation validation** — Every CHG must pass the 27-point
   validation checklist after creation, before committing. See
   `DOC_GOVERNANCE_CORE.md` → §3.4.1.

3. **Agent agreements** — `AGENTS.md` includes governance gate instructions
   for ALL AI agents (Claude Code, Codex, Gemini CLI, Copilot, Hermes).

4. **Pre-commit hook** — `hooks/ch-gate-check.sh` blocks commits that modify
   code files without an active CHG. See `hooks/hooks.json` for wiring.

5. **CHG linter** — `scripts/chg_lint.py` (also in `sdd_doc_lint/chg_lint.py`)
   validates CHG documents against governance rules:
   - CHG-L001: Status lifecycle (§3.3) — must follow Proposed → Approved → In-Progress → Implemented → Completed
   - CHG-L002: Gate approval (§3.1) — C3 changes must have approver
   - CHG-L003: CHG scope (§3.4) — no code steps in CHG
   - CHG-L004: IPLAN reference (§3.1.1) — must reference an IPLAN
   - CHG-L005: SDD-first order (§3.1.1) — SDD lifecycle before IPLAN

   Usage: `python scripts/chg_lint.py <chg-file.yaml>`

   Lint rules: GOV-011 (status lifecycle), GOV-012 (gate approval), GOV-013 (IPLAN Gate) in `LINT_RULES.md`.

Consuming projects MUST propagate these enforcement mechanisms. See
`ADAPTATION.md` for the adaptation checklist.
