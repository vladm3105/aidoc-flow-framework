---
layer: 03_EARS
lens: requirements_specialist
weight: 35
agent: requirements-analyst
framework_spec_version: "0.34.2"
---
# requirements_specialist lens — EARS layer

## Reasoning frame

The requirements_specialist lens at EARS altitude validates that every
PRD §9 functional requirement has been refined into atomic, testable
statements written in canonical EARS syntax. At BRD altitude the
business_analyst drafted capability-altitude requirements — broad
commitments about what the system must do without specifying
trigger-response structure. At PRD altitude the product_owner translated
those commitments into feature-altitude requirements with priorities and
acceptance criteria. At EARS altitude this lens asks the terminal
refinement question: does each requirement appear as a syntactically
correct EARS line that can be tested and traced without interpretation?

EARS syntax enforces precision through pattern selection. Each of the
six canonical patterns (ubiquitous, event-driven, state-driven,
optional, unwanted, complex) constrains what information must be
present. Ubiquitous: "The system shall…" — no trigger, no state, always
true. Event-driven: "When <trigger>, the system shall…" State-driven:
"While <state>, the system shall…" Optional: "Where <feature> is
included, the system shall…" Unwanted: "If <condition>, the system
shall <response>." Complex: combines two or more of the above. Any
line that cannot be classified into one of these six patterns is not an
EARS line — it is prose masquerading as a requirement.

This lens does NOT evaluate: whether the stated behaviours are
technically implementable (tech_lead), whether each line maps to a BDD
scenario (qa_lead), whether failure modes are complete (chaos_engineer),
or whether abuse cases are covered (security_engineer). The lens is
confined to EARS-pattern compliance, atomicity, measurability, and
bidirectional traceability with the PRD.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Canonical EARS pattern used.** Every requirement line must begin
with or be classifiable under one of the six EARS canonical patterns:
ubiquitous, event-driven, state-driven, optional, unwanted, or complex.
Lines that read as prose obligations ("The system should handle…",
"Users can expect…", "The platform manages…") without pattern structure
are not EARS-conformant and cannot be tested or traced. Missing →
P1 finding citing C1.

**C2 — Atomicity: one rule per line.** Each EARS line must express
exactly one obligation. Conjoined obligations ("…and the system shall
also…", comma-separated response clauses, or two distinct triggers in
one line) create ambiguous test conditions and prevent clean BDD
mapping. Compounds must be split into separate lines, each with its own
`@prd:` tag. Missing → P2 finding citing C2.

**C3 — Measurable response.** The response clause of every EARS line
must be expressed in terms a test can verify without product judgement.
Phrases such as "appropriately", "as needed", "in a reasonable time",
"handles gracefully", or "ensures quality" are not measurable. Acceptable
forms include numeric thresholds, enumerated state transitions, named
error codes, or an explicit ADR-deferred measurement plan. Missing →
P2 finding citing C3.

**C4 — @prd: tag resolves to an actual PRD element.** Every EARS line
must carry a `@prd:` traceability tag whose value names an existing PRD
section reference (e.g., `@prd:REQ-042`, `@prd:§9.3`). A tag that
references a non-existent PRD element severs the traceability chain and
makes impact analysis unreliable. Missing or dangling tag → P1 finding
citing C4.

**C5 — No orphan rule; every line traces to a PRD §9 row.** Every EARS
line must correspond to at least one PRD §9 functional requirement row.
Lines that introduce obligations not present in any PRD §9 row are
scope-creep at the requirements layer; lines in the EARS document that
no PRD §9 row requires are orphans that inflate test scope. Missing →
P2 finding citing C5.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame motivates it. Use sparingly. If
more than 30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
