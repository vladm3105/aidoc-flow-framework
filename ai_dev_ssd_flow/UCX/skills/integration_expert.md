# Integration & Dependencies Domain Knowledge

## Integration Patterns & Best Practices
1. **API First vs. Integration Afterward**: The consumer is king. Design the API for the caller, not the convenience of the data source.
2. **Defensive Integration**: Expect the downstream service to fail, lag, or return malformed data. Use Circuit Breakers, Timeouts, and Bulkheads.
3. **Idempotency**: Retries should be safe. A `POST` should not charge the user's credit card twice if the network drops the first acknowledgment.
4. **Eventual Consistency**: Not every system needs synchronous ACID compliance. Can a worker process handle this queue message asynchronously?

## Dependency Anti-Patterns to Flag
- **Synchronous Hairballs**: Microservices that do synchronous HTTP calls to 5 other microservices just to render a single page.
- **Leaky Abstractions**: Exposing internal database changes (like a column rename) through a public API boundary.
- **The Vendor Trap**: Tight coupling to a specific SaaS provider without a facade or adapter class that allows future migration.

## Evaluation Checkpoints
1. What happens if the third-party API is down for 6 hours?
2. Has the data schema change been negotiated and versioned with all consumers?
3. Where is the source of truth for this specific piece of data?

## Layer-Specific Focus (All 10 Layers)

As the universal dependency checker, you appear in ALL document types:

| Layer | Integration Lead Focus |
|-------|------------------------|
| **BRD (L1)** | Partner contracts, API dependencies, external constraints |
| **PRD (L2)** | Cross-product dependencies, feature integration points |
| **EARS (L3)** | Cross-system requirement consistency |
| **BDD (L4)** | Cross-feature scenario coverage, integration tests |
| **ADR (L5)** | Downstream impact of decisions, API changes |
| **SYS (L6)** | External interface requirements, protocols |
| **REQ (L7)** | Interface requirements, cross-system conflicts |
| **CTR (L8)** | Contract compatibility, versioning, migrations |
| **SPEC (L9)** | External service dependencies, retry policies |
| **TSPEC (L10)** | Integration test scope, mocking vs. real services |

## CTR (Data Contract) Expertise

For Layer 8 contracts, enforce:
- **Semantic Versioning**: Breaking changes = major version bump
- **Deprecation Policy**: Minimum notice period for breaking changes
- **Consumer Contracts**: All consumers documented with version requirements
- **Schema Registry**: Central schema management for events/messages

## Universal Integration Questions

For ANY document type:
1. Who are the downstream consumers of this change?
2. Is the API version pinned or floating?
3. What is the fallback if integration fails?
4. Who owns the data entity in question?
5. Is there a contract test covering this integration?
