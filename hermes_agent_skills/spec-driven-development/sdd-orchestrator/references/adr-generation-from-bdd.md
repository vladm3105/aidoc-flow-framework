# Batch ADR Generation from BDD — Complete Pattern (TradeGent CC Proven)

## Context

After completing BDD Layer 4 (9 docs, 115 scenarios, all health >= 8, validated 0E/0W),
ADR Layer 5 translates deferred BDD findings + PRD adr_topic_elaboration + EARS requirements
+ BRD constraints into Architecture Decision Records. This reference documents the full
pipeline proven at TradeGent CC on 2026-05-12.

## ADR Document Count

| Category | Count | IDs |
|----------|-------|-----|
| Engine-specific (1:1 with BDD) | 9 | ADR-01 through ADR-09 |
| Cross-cutting (affects all engines) | 10 | ADR-10 through ADR-19 |
| **Total** | **19** | |

Engine ADRs are 22-69KB each. Cross-cutting ADRs are 3-12KB each.

## Phase 0: Pre-Generation Checklist (2 hours)

Before ANY ADR is written, these upstream fixes must be complete:

- [ ] **Fix BDD hash collisions**: Common hashes (e.g., `58db` across 4 docs) violate SHA-256 content hashing. Recompute per scenario. Scripted in Python via execute_code.
- [ ] **Fix PRD placeholder hashes**: All `xxxx` placeholders in `@brd: BRD.NN.XX.xxxx` references replaced with actual upstream hashes. Only 2 `xxxx` tokens were real reference gaps in TradeGent CC (the rest were template metadata markers).
- [ ] **Verify all BDD validation reports**: 9 reports in `out/04_BDD/*.ucx.validate.json`, all `summary.is_valid: true`.
- [ ] **Confirm ADR template is current**: Run `sdd_init(project, update=true)` and verify no new sections added.
- [ ] **Verify all upstream layers validate 0E/0W**.

## Phase 1: Benchmark Generation (2 ADRs, ~3 hours)

Generate ADR-01 (umbrella orchestration) and ADR-07 (state machine & scoring rubric) first.
These are the most complex documents — ADR-07 alone unblocks 8 BDD P0/P1 deferred findings.

### Subagent dispatch

Both dispatched in one `delegate_task` call with 2 tasks. Each subagent:
- Reads ADR-TEMPLATE.yaml for structure (446 lines)
- Reads ADR-01.yaml reference if cross-ADR consistency is needed
- Reads upstream BDD, EARS, PRD, BRD files for domain content
- Writes complete YAML and verifies with yaml.safe_load()

### 5-persona review

After generation, dispatch all 5 review personas:
- system-architect (35% weight — decision evaluation, alternatives analysis)
- technical-lead (25% — implementation feasibility)
- security-auditor (15% — compliance, regulatory gaps)
- chaos-engineer (15% — failure modes, what-if-reversed)
- site-reliability-engineer (10% — operational readiness)

Split across two `delegate_task` calls (3 + 2). Expected score range: 42-84/100 before remediation.

### Benchmark remediation

Dispatch 2 remediation subagents — one per ADR. Provide convergent fix list (items flagged by 2+ reviewers). Typical fixes:
- **CRITICAL**: S4 trigger rule defect, missing crash recovery, missing dead-letter queue, state propagation ack, terminology consistency
- **HIGH**: Missing state transitions, override lifecycle, scoring deduplication, Q-score mapping, heartbeat timeout detection
- **MEDIUM**: Schema versioning, exit sequence sub-FSM, integration point listings, cost estimate updates

Each remediation subagent patches the ADR file directly via targeted `patch` commands (not full rewrite).

### ADR-07 special consideration

ADR-07 (State Machine) is the most complex document and caused remediation subagents to time out. If this happens:
- Apply the single most critical fix (S4 trigger rule) directly via `patch`
- Re-dispatch targeted remediation for remaining fixes with pre-extracted data only
- On second timeout, apply remaining fixes via `execute_code` with direct YAML manipulation

## Phase 2: Remaining Engine ADRs (7 ADRs, ~4 hours)

Generate ADR-02-06, 08-09. These are 1:1 with BDD documents.

## Phase 3: Cross-Cutting ADRs (10 ADRs, ~2 hours)

Generate ADR-10 through ADR-19. Key decisions:
- ADR-10: Event Bus & State Propagation (Redis Pub/Sub)
- ADR-11: Authentication & Authorization (API-key MVP, OAuth2 PROD)
- ADR-12: Clock Authority & Calendar (NTP + static holiday YAML)
- ADR-13: Idempotency & Deduplication (SQLite store, 90-day TTL)
- ADR-14: Regulatory Reporting & WORM (JSONL MVP, S3 Object Lock PROD)
- ADR-15: Health Check & Observability (Redis heartbeats, JSON logging)
- ADR-16: Operator Notification & Incident Response (console MVP, email PROD, cooldown dedup)
- ADR-17: Backpressure & Rate-Limiting (token bucket, queue caps)
- ADR-18: Input Validation & Data Integrity (Pydantic boundaries, SHA-256 checksums)
- ADR-19: Data Encryption & Secrets (Fernet file encryption, TLS enforcement)

## ADR Subagent Timeout Pattern

**Symptom**: `delegate_task` for ADR generation times out at 600s. The subagent reads 4 upstream files (BDD, EARS, PRD, BRD), the template (446 lines), and the reference ADR (1,400 lines) — then writes 50KB+ YAML and verifies it. Total API call volume exceeds the timeout budget.

**Workaround (Proven)**:

A) **Pre-extract upstream data** — run `execute_code` before dispatching to extract scenario IDs, EARS requirement IDs, feature descriptions. Provide these as inline text in the subagent prompt. The subagent then only reads ADR-TEMPLATE.yaml and ADR-01.yaml (2 files instead of 6).

B) **Direct write_file from execute_code** — for engine ADRs, the template structure is deterministic. Build the YAML via Python dict, dump with `yaml.dump()`, verify with `yaml.safe_load()`, and write via `write_file`. This eliminates subagent overhead entirely. Used successfully for ADR-04 and ADR-09.

C) **Retry solo on timeout** — when a subagent times out, re-dispatch it solo in the next call. Check file mtime after each retry — if it advanced, the subagent wrote output before timing out. ADR-02, 06 generated on first timeout; ADR-04 took 5 attempts.

## UCX sdd_validate Template Interference

**Symptom**: `sdd_validate(doc_type="adr", document="ADR-01.yaml")` returns parse error referencing `id: ADR-NN` at line 20 column 1 — a line that does NOT exist in ADR-01.yaml. The validator discovers template files in the project tree and tries to validate them alongside the target document.

**Affected paths** (all must be moved before validation):
- `05_ADR/ADR-TEMPLATE.yaml`
- `UCX/templates/ADR-TEMPLATE.yaml`
- `UCX/templates/layers/05_ADR/ADR-TEMPLATE.yaml`

**Workaround**:
```bash
mv project/05_ADR/ADR-TEMPLATE.yaml /tmp/
mv project/UCX/templates/ADR-TEMPLATE.yaml /tmp/
mv project/UCX/templates/layers/05_ADR/ADR-TEMPLATE.yaml /tmp/
# Run validation
# Restore after:
mv /tmp/ADR-TEMPLATE.yaml project/05_ADR/
mv /tmp/UCX-ADR-TEMPLATE.yaml project/UCX/templates/
mv /tmp/UCX-layers-ADR-TEMPLATE.yaml project/UCX/templates/layers/05_ADR/
```

This is a known UCX framework bug (template discovery scans all directories, not just the target layer). Document in CHANGELOG and report to UCX maintainers. The files parse correctly with `yaml.safe_load()` — the validator is the bottleneck, not the content.

## ADR Numbering Convention

| Range | Purpose |
|-------|---------|
| ADR-01 through ADR-09 | Engine-specific (1:1 with BDD-01 through BDD-09) |
| ADR-10 through ADR-19 | Cross-cutting (affects all engines) |

ADR-01 is the umbrella agent orchestration — it IS an engine ADR (Engine 1 in the 9-engine architecture), not a cross-cutting one.

## BDD Deferred Findings → ADR Coverage

All 28 BDD deferred + SEC findings must map to at least one ADR. Verify with a coverage matrix table in PLAN-008. Typical mapping:

| BDD Finding | ADR |
|-------------|-----|
| P0-04 Auth/AuthZ | ADR-11 |
| P0-05 Pre-trade risk | ADR-05 |
| P0-06 Full exit sequence | ADR-07 |
| P0-07 Duplicate order | ADR-04 + ADR-13 |
| P0-08 Hard stop + roll race | ADR-07 |
| P0-09 State split | ADR-10 |
| P0-10 Cascading thundering herd | ADR-17 |
| P0-11 Clock skew | ADR-12 |
| SEC-001 (Auth) | ADR-11 |
| SEC-002 (Input validation) | ADR-18 |
| REG-001 (SEC 15c3-5) | ADR-05 |
| REG-002 (SEC 17a-4 WORM) | ADR-14 |
| REG-003 (CAT NMS) | ADR-14 |
| REG-004 (FINRA) | ADR-14 |

## Post-Generation Tasks

After all 19 ADRs are generated:
- [ ] Run `sdd_validate` on each (after moving template files)
- [ ] 5-persona review on ADR-02-09, ADR-10-19 (benchmarks 01/07 already reviewed)
- [ ] Remediate findings
- [ ] Re-score ADR-01/03/07 (currently TBD/100 in spec_ready_score)
- [ ] Update ADR-00_index.md with all 19 entries, status, categories
- [ ] Update CHANGELOG.md
- [ ] Verify SPEC-Ready score >= 90/100 for all ADRs before advancing to Layer 6
