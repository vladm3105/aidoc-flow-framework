# Initial requirements — URL shortener (seed)

A small URL-shortener service.

- A user submits a long URL and receives a short code; visiting the short link
  redirects to the original URL.
- Short codes are unique and collision-free.
- The service counts how many times each short link is visited.

**Quality targets**

- Redirect latency p95 under 50 ms.
- Availability 99.9% monthly.
- Short codes never collide.

**Out of scope (for this cycle)**

- Custom vanity domains.
- User accounts / authentication.
- Analytics dashboards.

This seed is the input to the 8-layer SDD flow
(BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN); the worked output chain
lives under `../docs/`, and [`../README.md`](../README.md) is the walkthrough.

**Frozen historical input.** Per the seed contract
([`framework/governance/SEED_CONTRACT.md`](../../../framework/governance/SEED_CONTRACT.md),
GD-08), this seed is not edited to resolve a downstream finding once `BRD-01`
was authored: a "the seed says X, the chain does not" gap is disposed in
`BRD-01`'s `seed_disposition:` ledger (absorbed / rejected / deferred), and new
human input arrives through `chg/`, not by amending the claims above.
