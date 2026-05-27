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

This seed is the input to the 8-layer flow under `../docs/`.
