# Test change request — add visit-rate analytics dashboard

## Motivation

Stakeholders need visibility into per-short-link traffic patterns to
identify high-value links, detect abuse spikes, and inform capacity
planning. The seed currently lists "Analytics dashboards" as out of
scope; this change request moves that capability into scope.

## Scope

- Add a per-short-link visit-rate metric (rolling 1h, 24h, 7d windows).
- Add a dashboard endpoint that exposes the metric per link owner.
- Persist visit timestamps for at least 30 days to support the 7d window.
- Out of scope for this CHG: cross-link aggregations, alerting,
  third-party analytics integrations.

## Expected downstream impacts

The CHG propagation report from `doc-chg-autopilot` should enumerate
each of these (or explicitly flag why one was rejected):

- BRD: Functional Requirements adds "visit-rate analytics" capability.
  Out-of-scope list updated to remove "analytics dashboards".
- PRD: Functional Capabilities adds dashboard endpoint container.
  Non-Functional Requirements adds 30-day retention + dashboard p95
  latency target.
- EARS: New requirements for visit-rate computation (Event-driven on
  redirect) and dashboard query (Ubiquitous, role-restricted).
- BDD: New scenario for "owner views per-link visit rate".
- ADR: New ADR required for metrics storage choice (time-series DB vs
  rolling-window aggregation in main DB).
- SPEC: New component for the metrics service + persistence schema +
  dashboard API contract.
- TDD: New test cases for metric correctness, retention boundary,
  dashboard authorization.
- IPLAN: New tasks for metrics service implementation, storage
  migration, dashboard endpoint, retention job, integration tests.

## Notes for the audit

The acceptance phase asserts that `doc-chg-autopilot`'s propagation
report references each layer above. An empty or missing-layer report
fails the gate. The ADR topic ("metrics storage choice") is required
because the change introduces a new persistence concern; a propagation
report that omits the ADR layer is a regression.
