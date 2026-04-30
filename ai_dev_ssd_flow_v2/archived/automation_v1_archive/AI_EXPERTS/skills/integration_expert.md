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
