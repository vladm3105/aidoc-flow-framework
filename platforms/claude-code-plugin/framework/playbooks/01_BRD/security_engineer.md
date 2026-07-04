---
layer: 01_BRD
lens: security_engineer
weight: 8
agent: security-engineer
framework_spec_version: "0.32.7"
---
# security_engineer lens — BRD layer

## Reasoning frame

The security_engineer lens at BRD altitude applies a trust-boundary and
abuse-case lens at the level of business capabilities, not implementation
controls. The BRD is the correct place to declare which actors can submit,
read, or manipulate each capability; which data artifacts require protection;
and what harmful outcomes a motivated adversary could achieve using the system
as described. Implementation-level controls (encryption algorithms, token
lifetimes, firewall rules) belong at PRD (when controls are selected) and SPEC
(when controls are specified). The BRD lens identifies the threats; downstream
layers choose the countermeasures.

At PRD altitude the security_engineer lens asks which specific controls address
the BRD-declared abuse cases, and whether those controls are reflected in the
product's acceptance criteria. At ADR altitude the lens evaluates trust-boundary
architecture: are the boundaries encoded in the selected technical decisions?
At SPEC altitude the lens verifies component-level control correctness. The BRD
lens operates exclusively at capability altitude: who can do what to whom, what
could go wrong, and what external obligations apply.

The BRD security_engineer lens does NOT evaluate: specific control selection
or design (PRD/ADR), component-level security (SPEC), compliance procedure
completeness (auditor), or operational security practices (operator). Its
scope is bounded to the trust topology, data classification, named abuse cases,
and applicable external compliance frameworks — all stated in terms a
non-technical business stakeholder can validate.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Trust boundaries declared at capability altitude.** Each capability
must state who (which actor class or system) is permitted to invoke it:
anonymous public, authenticated user, privileged role, internal system only,
or external partner. A capability without a stated access class has an
undefined trust boundary. Missing → P1 finding citing C1.

**C2 — Data classification of persona-managed artifacts.** Each artifact class
managed by or on behalf of a persona (documents, transactions, logs, credentials,
personal data) must be assigned a data classification label: PII, credential,
confidential business data, public, or the project's equivalent taxonomy. An
artifact without a classification leaves data-handling obligations undefined.
Missing → P2 finding citing C2.

**C3 — Abuse-case capabilities named.** The document must name at least one
adversarial use scenario per critical capability, expressed at capability
altitude (not as implementation attack vectors). Examples: "an authenticated
user may submit documents on behalf of another user without consent," "the
URL-resolution capability may be used to redirect users to harmful external
destinations," "the export capability may exfiltrate bulk PII." These are
business-altitude statements about potential harm, not OWASP vulnerability
labels. Missing → P2 finding citing C3.

**C4 — External compliance obligations cited.** Where a capability operates
on data or in a context subject to external regulation (GDPR, HIPAA, PCI-DSS,
SOC 2, CCPA, relevant RFC), that regulation must be cited explicitly. Uncited
compliance obligations discovered after PRD create rework at the point of
highest cost. Missing → P3 finding citing C4.

**C5 — Authentication and authorisation model declared.** The document must
state the top-level authentication model for each access class declared in C1:
anonymous (no auth), authenticated (named mechanism category — e.g., "OAuth
2.0 bearer token"), or role-restricted (named role taxonomy). The declaration
does not need to specify an implementation, but must be specific enough to
constrain design at PRD. Missing → P2 finding citing C5.

**C6 — Non-repudiation requirements declared where applicable.** For
capabilities involving financial transactions, legally binding commitments,
or audit-regulated actions, the document must state whether non-repudiation
(tamper-evident records of who performed what action and when) is required.
Silence on non-repudiation for high-stakes capabilities is a business-level
gap. Missing → P2 finding citing C6.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame above motivates it. Use sparingly. If
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
