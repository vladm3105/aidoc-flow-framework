---
layer: 01_BRD
lens: auditor
weight: 20
agent: traceability-auditor
framework_spec_version: "0.41.3"
---
# auditor lens — BRD layer

## Reasoning frame

The auditor lens applies conformance and traceability checks that are objective
and layer-invariant: are the required sections present, do the element IDs
follow the naming standard, do external references resolve, is the glossary
complete? At BRD altitude the auditor does not evaluate the quality of the
business logic — that is the business_analyst's domain — but verifies that the
document is structurally complete enough for downstream layers to inherit it
without ambiguity.

At PRD altitude the auditor applies the same structural checks but against
PRD-specific element-ID patterns (`PRD.{doc}.{section}.{hash[:4]}`) and
PRD-required template sections. At EARS the auditor verifies EARS-specific
section structure and requirement-ID conformance. The checks change per layer;
the auditor's role — structural completeness + ID conformance + reference
resolution — is constant.

The BRD auditor lens does NOT evaluate: whether the business content is
internally consistent (architect), whether objectives are measurable
(business_analyst), whether reliability NFRs are present (chaos_engineer), or
whether security trust boundaries are declared (security_engineer). Content
quality belongs to the content lenses. The auditor only asks: "Is this document
complete, navigable, and anchored to its references?"

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Element ID conformance.** Every identifiable element (objective,
requirement, acceptance criterion, persona, capability) must carry an ID
conforming to the project's ID_NAMING_STANDARDS. For BRD the expected pattern
is `BRD.{doc-slug}.{section-code}.{hash[:4]}` (or the project-specific
variant declared in ID_NAMING_STANDARDS). IDs that are missing, duplicated,
or do not match the declared pattern prevent downstream traceability linking.
Missing → P1 finding citing C1 (gate-blocking; synthesizer must not issue
approval verdict while this fires).

**C2 — Required template sections present.** The BRD template mandates a
defined set of sections (e.g., §Executive Summary, §Business Objectives,
§Personas, §Scope, §Requirements, §Acceptance Criteria, §Glossary,
§Document Control). Every mandatory section must be present, even if
populated with "N/A — not applicable" and a rationale. Absent sections are
not inferrable from adjacent content. Missing → P1 finding citing C2.

**C3 — External reference resolution.** Every external reference cited in the
document — an RFC number, a previously approved BRD (e.g., BRD-12), a
regulation identifier (e.g., GDPR Art. 17), a market report, or a cited
ADR — must resolve to an identifiable source. A reference that cannot be
located or verified leaves a gap in the document's authority chain. Missing
→ P2 finding citing C3.

**C4 — Glossary coverage.** Every domain-specific term introduced in the
document body must appear in §Glossary with a definition scoped to this
document's usage. Terms that are standard English or standard industry terms
(e.g., "API", "user") may be omitted. Terms that carry project-specific
meaning (e.g., "fulfillment event", "settlement window") must be defined.
Missing → P3 finding citing C4.

**C5 — Document Control complete.** §Document Control must include all
required fields: Owner (named individual or role), Status (one of:
Draft / Review / Approved), Version (SemVer or sequential revision number),
and Effective Date (ISO 8601). A partially filled Document Control block
creates governance routing uncertainty. Missing → P2 finding citing C5.

**C6 — No dangling cross-references.** Every internal cross-reference (e.g.,
"see §Requirements C3", "per Objective OBJ-04") must point to an element
that exists in the document with that identifier. Dangling cross-references
indicate edits that broke a reference and were not updated. Missing → P2
finding citing C6.

**C7 — Version history present if status is Review or Approved.** If the
Document Control Status is "Review" or "Approved", a version history table
must be present showing at least one prior revision entry. A document at
Review/Approved status with no revision history cannot be audited for
change provenance. Missing → P3 finding citing C7.

**C8 — Seed-disposition ledger complete against the seed.** When the cycle has
a `<project>/seed/` input, read the seed prose against this BRD's
`seed_disposition:` ledger and confirm **every** claim the seed makes has a row
(governance `SEED_CONTRACT.md`, GD-08). This is a reading judgement the
deterministic `SEED01` lint cannot make — `SEED01` proves each row is
well-formed and each `absorbed` target resolves, but only this lens can catch a
seed claim the ledger *omitted*. Flag any seed claim with no disposition, and
any finding "resolved" by editing the seed rather than by a ledger row (the seed
is frozen). Missing claim / seed edited to pass → P2 finding citing C8.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame above motivates it. Use sparingly. If
more than 30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).


*Cross-layer cardinality note (CLEANUP-PR-F item 18):* apparent-orphan
downstream docs (e.g., `PRD-02` declaring `@brd: BRD-01` when `PRD-01`
also exists with the same upstream) MAY be valid siblings of the same
upstream, not actual orphans. Validate the trace by tag resolution, not
by doc-number alignment. See `framework/governance/ID_NAMING_STANDARDS.md`
§Cross-layer cardinality.
## No-findings rationale

A lens returning `lens_score: 100` with `findings: []` (zero findings)
MUST accompany its persona-output record with a `no_findings_rationale`
field naming at least one specific section where the lens *did* examine
the artifact and explicitly cleared. Example for this lens:

> `no_findings_rationale: "§<section-number> <topic> — examined and
> verified clean against checks C1-C5; no deviation from upstream
> required attributes."`

The synthesizer treats a missing or empty `no_findings_rationale` on
a `lens_score: 100 / findings: []` output as a structural error and
caps the lens at 95 (with a `STRUCTURE-RAT-001` advisory in the
verdict). The cap is a calibration nudge against "convergence theater"
— a lens that genuinely cleared the artifact must say *what* it
cleared, otherwise the score is unsubstantiated.

Filing findings (any priority, including P3 nits) bypasses the
rationale requirement — findings ARE the rationale.

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
