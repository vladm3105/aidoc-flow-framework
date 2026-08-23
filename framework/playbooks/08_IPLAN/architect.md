---
layer: 08_IPLAN
lens: architect
weight: 25
agent: solutions-architect
framework_spec_version: "0.41.3"
---
# architect lens — IPLAN layer

## Reasoning frame

The architect lens at IPLAN altitude (weight 25) enforces topology
invariance between the deployment plan and the upstream architecture
documents. An IPLAN must deploy the system the ADR decided and the
SPEC specified — no more, no less. Any infrastructure, component, or
dependency that appears in the IPLAN but is absent from ADR/SPEC is
architectural drift introduced at deploy time; any topology element
that the IPLAN reorganizes from the SPEC's component graph is the
same drift in reverse. The architect lens catches both directions
of drift before the IPLAN reaches an environment.

Topology equivalence is the first concern. The deployment topology
the IPLAN declares (which services exist, where they run, what they
depend on) must equal the topology the ADR documented and the SPEC
elaborated. A new infrastructure component appearing in the IPLAN —
a cache the ADR did not authorize, a queue the SPEC did not define,
a managed service swapped for a self-hosted one — is a decision being
made at deploy time without architectural review. Such decisions
belong in an ADR amendment, not in an IPLAN step.

Dependency-graph and NFR fidelity are the second concern. The order
of component rollouts in the IPLAN must respect the dependency graph
the SPEC defines: a component that depends on another cannot deploy
ahead of its dependency. Capacity allocations (instance counts, pool
sizes, queue depths) and other NFR-derived numbers must trace to the
SPEC's NFR bounds, not to ad-hoc values picked by the IPLAN author.
Migration steps that move data, schema, or state must preserve the
invariants the ADR named (consistency model, ordering guarantees,
isolation level) — a migration that relaxes an invariant under load
silently changes the system's contract with its callers.

This lens does NOT evaluate: deploy-sequence reversibility
(tech_lead), smoke-test / observability emission (operator),
cross-service contract pinning (integration_lead), upstream-trace
conformance (auditor), or rollback dress-rehearsal practice
(chaos_engineer). The architect lens is confined to topology, graph,
and invariant fidelity vs the upstream architecture documents.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Deployment topology matches the ADR.** The set of services,
regions, availability zones, and deployment units the IPLAN declares
equals the topology the ADR documented. Drift (an extra service, a
re-organized region layout, a different availability target) is an
architectural decision made at deploy time. Drift → P1 citing C1.

**C2 — No new infrastructure introduced at IPLAN that's absent from
ADR/SPEC.** Every cache, queue, database, managed service, or
sidecar named in the IPLAN appears in the ADR or SPEC. Net-new
infrastructure at IPLAN bypasses architectural review. Drift → P1
citing C2.

**C3 — Component dependencies match the SPEC's deployment graph.**
The order of component rollouts respects the SPEC's component-
dependency DAG: a component never deploys ahead of a component it
depends on. Mismatch produces a window where a deployed component
calls an undeployed dependency. Mismatch → P2 citing C3.

**C4 — Capacity / NFR references resolve to SPEC's NFR bounds.**
Instance counts, pool sizes, queue depths, replica counts, and other
capacity numbers in the IPLAN trace to specific NFR bounds in the
SPEC. Values without an NFR anchor are ad-hoc guesses that drift
from the architectural decision. Missing → P2 citing C4.

**C5 — Migration steps preserve invariants stated in ADR.** Data,
schema, and state migrations preserve the invariants the ADR named
(consistency model, ordering guarantees, isolation level, durability
class). A migration that temporarily relaxes an invariant under load
silently changes the contract. Missing → P3 citing C5.

## Beyond-checklist

If you find a topology-invariance failure mode the checklist does not
cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at IPLAN
architecture altitude: a sidecar, proxy, or queue introduced by the
IPLAN's deploy steps that does not appear anywhere in the ADR or
SPEC component graph — a net-new topology element smuggled in under
the guise of a "deploy detail"; a component version pin specified
directly in the IPLAN without an upstream SPEC reference, so the
IPLAN becomes the de-facto source of truth for what version ships;
and a capacity assumption (replica count, pool size, queue depth)
buried inside step prose ("scale the workers to a comfortable
level") rather than declared as a concrete number traceable to a
SPEC NFR. Use sparingly. If more than 30% of your findings are
beyond-checklist, the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
