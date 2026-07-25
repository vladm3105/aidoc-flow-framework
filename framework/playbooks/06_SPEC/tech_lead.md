---
layer: 06_SPEC
lens: tech_lead
weight: 30
agent: solutions-architect
framework_spec_version: "0.38.0"
---
# tech_lead lens — SPEC layer

## Reasoning frame

The tech_lead lens at SPEC altitude carries equal weight with architect
(30 each) because the SPEC is the layer where architectural intent
meets implementation reality. Architect ensures the SPEC captures the
right specification; tech_lead ensures the SPEC is implementable in
the target stack. An interface that names a protocol the runtime
cannot support, a sequence diagram with a send and no matching
receive, an error contract that does not enumerate causes, a
concurrency model implicit when the path is concurrent, or a
persistent resource without a declared owner all defeat the SPEC's
purpose: the implementer reading only the SPEC must be able to produce
correct code without re-deriving design choices.

Implementability at SPEC altitude differs from implementability at
ADR altitude. At ADR the question was "can an engineer map this
decision to concrete architectural primitives?" At SPEC the question
is "can an engineer translate this interface and sequence into
runtime code that will work?" Impossibility at SPEC includes:
non-existent runtime primitives (no such message type in the chosen
broker), bound contradictions (a method declared synchronous calling
an async-only API), or impossible-to-satisfy NFRs (single-threaded
execution claiming sub-millisecond p99 across a network hop).

Sequence diagrams encode the cross-component runtime story. A
well-formed sequence has every send matched by a receive (or
explicitly declared a fire-and-forget). The numbered steps must be
internally consistent (step N+1 must causally follow step N).
Malformed sequences leave the implementer guessing at the runtime
order of operations.

Error handling, concurrency, and resource ownership are the remaining
pillars. Errors must be explicit per interface (per-error: cause,
response shape, retry semantics) so the consumer knows how to handle
each. Concurrency models must be named on concurrent paths so the
implementer chooses the right primitive (lock-based / actor / lock-
free / single-threaded). Resource ownership must be declared so two
components do not silently both claim authority over the same
persistent resource.

This lens does NOT evaluate: specification integrity (architect),
cross-component contracts (integration_lead), resilience-under-load
(chaos_engineer), or security-control implementation
(security_engineer). The tech_lead lens is confined to
implementability and runtime correctness.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every interface implementable in the target stack.** Each
interface defined in the SPEC corresponds to runtime primitives that
exist in the target stack and that compose correctly (no
sync-calling-async impossibilities, no missing message types in the
chosen broker, no NFRs that single-threaded execution cannot satisfy).
Impossibility → P1 citing C1.

**C2 — Sequence diagrams well-formed.** Every send has a matched
receive (or explicitly declared fire-and-forget). Numbered steps are
internally consistent (step N+1 causally follows step N). The
diagram contains no dangling arrows, no impossible orderings, no
ambiguous join points. Malformed → P2 citing C2.

**C3 — Error handling explicit per interface.** Every interface
enumerates its error conditions and for each: cause (what triggers
the error), response shape (what the caller sees), and retry
semantics (idempotent / not-idempotent / not-retryable). Missing →
P2 citing C3.

**C4 — Concurrency model named on concurrent paths.** Any code path
that touches shared state or runs concurrently with another path
names the concurrency primitive (lock-based / actor / lock-free /
single-threaded / event-loop). Implicit concurrency on a shared-state
path is a defect. Missing on concurrent paths → P2 citing C4.

**C5 — Resource ownership declared.** Every persistent resource (DB
table, cache key, message queue, file path, external API quota) is
declared as owned by exactly one named component. Joint ownership
without a named coordination protocol leads to writes that race or
to silent staleness. Missing → P3 citing C5.

## Beyond-checklist

If you find an implementability or runtime-correctness failure mode the
checklist does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at SPEC:
implicit-blocking-IO (a path declared synchronous performs blocking
I/O), hidden-allocator-pressure (the SPEC implies large allocations
on hot paths without naming the allocator strategy), or undeclared-
batching (a path batches behavior without a stated batch boundary).
Use sparingly. If more than 30% of your findings are beyond-checklist,
the playbook needs revision (file a follow-up).

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
