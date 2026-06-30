---
layer: 06_SPEC
lens: security_engineer
weight: 10
agent: security-engineer
framework_spec_version: "0.32.1"
---
# security_engineer lens — SPEC layer

## Reasoning frame

The security_engineer lens at SPEC altitude carries equal weight with
chaos_engineer (10 / 10). At ADR altitude security was dominant
(weight 12) because the ADR is where trust boundaries, authn, and
authz get chosen. At SPEC altitude security is co-equal with
resilience because the SPEC is where those choices get implemented —
each control the ADR named must appear in the SPEC as a concrete
implementation, each crypto choice must be instantiated with
algorithm + mode + key-management, every public interface must have
input validation, the failure-closed default must match the ADR
commitment, and security-relevant operations must emit audit events.

Control implementation is the lens's central concern. The ADR
committed to authentication at boundary X — does the SPEC actually
encode it? The ADR committed to authorization at boundary Y — is
there a rule in the SPEC saying who may do what? The ADR committed
to audit logging at boundary Z — does the SPEC name the audit-event
schema? A SPEC that quietly skips a control the ADR mandated leaves
the security posture defective by design.

Crypto instantiation is the second concern. The ADR may have named
"AES-GCM with KMS-managed keys." The SPEC must instantiate that
choice: which block size, which IV strategy, which KMS, which key
rotation cadence, which envelope encryption pattern. Hand-wave
phrases at SPEC altitude push the choice into implementation, where
the developer may pick a weak default.

Input validation, failure-closed match, and audit-event emission
round out the lens. Every public interface (anything that crosses
a trust boundary, including the system's external API surface and
each component boundary in the SPEC's integration topology) must
state its input validation rule: allowlist / denylist / typed-
parse / schema-validate. Failure-closed behavior in the SPEC must
match the failure-closed commitment the ADR made; a SPEC that
quietly fails open under control unavailability undoes the ADR's
defensive posture. Audit events must be emitted for security-
relevant operations so a post-incident reviewer can reconstruct
what happened.

This lens does NOT evaluate: specification integrity (architect),
implementability mechanics (tech_lead), cross-component contracts
(integration_lead), or resilience-under-load (chaos_engineer). The
security_engineer lens is confined to control implementation,
crypto instantiation, and audit-trail integrity.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every ADR-named security control implemented in the SPEC.**
For each control the ADR committed to (authentication at boundary X,
authorization at boundary Y, audit at boundary Z, encryption of data
class W), the SPEC contains a concrete rule or interface implementing
it. Quietly skipping a committed control is a defect. Missing → P1
citing C1.

**C2 — Crypto choices instantiated.** Where the ADR named an
algorithm or scheme (AES-GCM, RSA-OAEP, HMAC-SHA256, etc.), the SPEC
instantiates it with the operational parameters: block / mode / IV
strategy, key length, key-management binding, rotation cadence,
envelope pattern. Hand-wave → P2 citing C2.

**C3 — Input-validation rule per public interface.** Every interface
that crosses a trust boundary (external API surface + each
inter-component boundary in the SPEC topology) names its input
validation rule: allowlist / denylist / typed-parse / schema-
validate. Missing → P2 citing C3.

**C4 — Failure-closed default matches ADR commitment.** Where the
ADR committed to failure-closed behavior on a security control
(e.g., deny when authz lookup is unavailable), the SPEC implements
that behavior. A SPEC that quietly fails open undoes the ADR's
defensive posture. Mismatch → P1 citing C4.

**C5 — Audit-event emission for security-relevant operations.** The
SPEC names which operations emit audit events (authn success / fail,
authz decision, privilege change, sensitive read/write, control
configuration change) and the audit-event schema (subject / action /
resource / decision / timestamp / context). Missing → P3 citing C5.

## Beyond-checklist

If you find a security-control failure mode the checklist does not
cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at SPEC:
secret-in-config (the SPEC names a secret value inline rather than a
secret-management reference), insecure-default-protocol (the SPEC
names an interface using a protocol whose default mode is plaintext
or weak), or unscoped-token-lifetime (the SPEC introduces a token
type without naming its expiry / revocation semantics). Use
sparingly. If more than 30% of your findings are beyond-checklist,
the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
