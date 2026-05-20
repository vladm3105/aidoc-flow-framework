# ADR Benchmark Generation Pattern — Proven Workflow

## When to Use

After completing Layer 4 (BDD) with all documents at health >= 8, and the ADR
layer generation plan is approved. This reference covers generating, reviewing,
and remediating the first 2 benchmark ADRs before batching the remaining 17.

## Pattern: 2-Benchmark → 5-Persona Review → Convergent Remediation

### Step 1: Pre-Generation Checklist (Before Any ADR Creation)

Upstream fixes MUST be complete before ADR generation begins. ADRs reference
BRD, PRD, EARS, and BDD documents at hash-level precision — broken hashes
propagate to all downstream layers.

- [ ] Fix any BDD hash collisions (same hash used for different scenarios across documents — e.g., `58db` used for "Recovery from Data Source Failed" in BDD-04,07,08,09). Recompute with `hashlib.sha256(f"{doc_id}:{section_id}:{name}").hexdigest()[:4]`.
- [ ] Fix PRD `xxxx` placeholder hashes in `@brd: BRD.NN.XX.xxxx` references. Read the actual BRD section, extract its hash, and replace. NOTE: `id_standard.placeholder: xxxx` in PRD metadata is INTENTIONAL template boilerplate — do NOT fix these.
- [ ] Verify all BDD validation reports exist in `out/04_BDD/`.
- [ ] Verify ADR template is current: run `sdd_init(project, update=true)`.

### Step 2: Select Benchmarks

Pick the umbrella ADR (ADR-01 = Orchestration Model) plus the highest-complexity
engine ADR (ADR-07 = State Machine Architecture). These two have:
- Most upstream dependencies (BRD-01 covers all engines; BDD-07 has 8 P0/P1 deferred findings)
- Tightest integration points (orchestration touches all 9 engines; state machine touches 5 engines)
- Highest review scrutiny (if these pass, the remaining 17 will be easier)

### Step 3: Parallel Generation

Dispatch two `delegate_task` subagents in a single call (3-subagent batch limit
allows 2 in one call). Each subagent must:

1. Read the ADR-TEMPLATE.yaml from the target layer directory
2. Read ALL 4 upstream documents (BDD, EARS, PRD, BRD) for the target engine
3. Write a complete YAML document following the template structure:
   - Context (Section 2): business problem, constraints, stakeholders from BRD/PRD
   - Decision (Section 3): chosen approach with rationale, key components
   - Alternatives (Section 4): 2-3 rejected options with rejection reasons and cost estimates
   - Consequences (Section 5): positive outcomes, tradeoffs, costs
   - Architecture Flow (Section 6): Mermaid sequence/state diagram
   - Implementation Assessment (Section 7): phases, complexity 1-5, rollback path
   - Verification (Section 8): concrete success criteria with measurements
   - Traceability (Section 9): hash-level references to all 4 upstream layers
4. Overwrite the file to `05_ADR/ADR-NN.yaml`
5. Verify with `yaml.safe_load()`

Expected output size: 700-900 lines, 40-70KB per ADR.

### Step 4: Validation

`sdd_validate` on the target file. **Template collision bug alert**: the
validator scans the entire project tree including `UCX/templates/`. If the
ADR-TEMPLATE.yaml has `id: ADR-NN`, the validator will parse it and fail even
though the target document is clean. Workaround: move ALL ADR template files
to /tmp before validation, then restore them afterward.

`yaml.safe_load()` on the target document will succeed while `sdd_validate`
fails — this is the diagnostic signature of the template collision bug, not a
content error.

### Step 5: 5-Persona Parallel Review

Dispatch 5 review subagents:

| Batch | Personas | Focus |
|-------|----------|-------|
| Batch A (3) | system-architect, technical-lead, chaos-engineer | Decision evaluation, feasibility, failure modes |
| Batch B (2) | site-reliability-engineer, security-auditor | Operations, compliance |

All 5 personas review BOTH benchmark ADRs. Each writes a review file. Expected:
each review is 200-300 lines, 15-35KB, with 8-15 findings categorized as
CRITICAL/HIGH/MEDIUM/LOW.

### Step 6: Convergent Fix Extraction

After all 5 reviews return, extract the CONVERGENT findings — issues that
appeared in 3+ of 5 reviews. These are the real problems. Individual persona
findings that don't converge are noise (different personas have different
tolerances).

Typical convergent finding count: 10-14 per ADR. Categories:
- CRITICAL: missing state machine transitions, wrong trigger rules, missing crash recovery
- HIGH: ambiguous scoring formulations, missing ordering guarantees, underspecified persistence
- MEDIUM: missing integration points, cost estimate gaps, edge-case handling

### Step 7: Parallel Remediation

Dispatch 2 fixer subagents (one per ADR) with the full list of convergent
fixes. Each fixer must:
1. Read the ADR YAML + all 5 review files
2. Apply ALL fixes (not a subset)
3. Overwrite the original file
4. Verify `yaml.safe_load()`

**Timeout risk**: Large ADRs (700+ lines) may timeout on slow models. If a
subagent times out, apply the CRITICAL fixes directly via `patch` and accept
that HIGH/MEDIUM fixes will be caught during Phase 3 (cross-cutting ADR
generation where cross-ADR consistency checks force resolution).

### Step 8: Decision Point

After remediation, decide whether to:
- A) Re-review (if score still < 90 after fixes) — adds 30 min
- B) Move to Phase 2 (remaining engine ADRs) — faster, gaps surface in Phase 3
- C) Move to Phase 3 (cross-cutting ADRs) — regulatory ADRs are the real gap;
  engine ADR operational gaps are minor by comparison

Typical post-remediation scores:
- ADR-01 (orchestration): ~82-88/100 (operational gaps, auth deferred to ADR-11)
- ADR-07 (state machine): ~78-85/100 (scoring rubric detail gaps, exit sequence sub-FSM)

Neither reaches the 90 threshold after benchmark remediation alone — this is
NORMAL. The 90 threshold is achieved in Phase 3 when cross-cutting ADRs resolve
the deferred items (auth, regulatory, event bus contracts).

## ADR Remediation Fix Categories

### CRITICAL (do first, apply directly if subagent times out)

| Fix | Example from TradeGent CC |
|-----|---------------------------|
| Fix wrong trigger/decision rule | "any Q=4 → exit" → "3+ questions at S3+ OR any Q=4 → exit" |
| Add state machine with transition table | AUTONOMOUS→WARNING→HALTED→MANUAL→RECONCILING |
| Add crash recovery protocol | Checkpoint + missed-window detection + replay |
| Fix cross-ADR terminology conflicts | INITIALIZING/ACTIVE/DEGRADED/HALTED vs STARTING/ACTIVATED/STOPPING |
| Add circuit breaker pattern | Event-bus degradation → local mode with delayed sync |

### HIGH (do in remediation subagent)

| Fix | Example |
|-----|---------|
| Add event ordering strategy | Per-engine monotonic sequence numbers |
| Specify idempotency key persistence | SQLite-backed, 90-day TTL |
| Add backpressure mechanism | Per-engine queue depth limits with shed policy |
| Fix cost estimates | Break down broker API costs, Redis hosting, LLM inference |
| Spec override lifecycle | Duration, persistence, interaction priority |

### MEDIUM (deferrable)

| Fix | Example |
|-----|---------|
| Add missing integration points | Data Freshness Validator not in integration list |
| Add event loss measurement | Window-completion count vs expected windows |
| Add dead-letter queue | Unprocessable events → DLQ consumer → audit log |
| Add schema versioning | Version field on transitions |
| Add heartbeat timeout detection | Prevent false DEGRADED from single missed heartbeat |

## Estimated Effort

| Phase | Time |
|-------|------|
| Pre-generation checklist | 2 hrs |
| Generate 2 benchmarks | 1-2 hrs |
| Validate (with template workaround) | 15 min |
| 5-persona review (parallel) | 5-10 min wall clock |
| Convergent fix extraction | 5 min |
| Remediation (parallel, 2 subagents) | 5-10 min wall clock |
| Re-validate | 15 min |
| **Total wall clock** | **~4-5 hrs** |

## Key Pitfalls

1. **Template collision bug**: Don't waste time debugging YAML that `yaml.safe_load()` says is fine. Move template files to /tmp.
2. **Subagent timeout**: ADRs are large (40-70KB). Remediation subagents working on both ADR + 5 review files may timeout. Apply CRITICAL fixes directly.
3. **PRD `id_standard.placeholder: xxxx`**: This is NOT a broken hash — it's template boilerplate showing the ID format. Only fix `@brd: BRD.NN.XX.xxxx` and `@ears: EARS.NN.XX.xxxx` references.
4. **BDD hash collisions**: Scenario IDs must be content-derived. Same scenario name across different documents MUST produce different hashes because the doc_id differs.
5. **Convergent finding threshold**: 3+ of 5 personas agreeing = real issue. 1-2 personas = noise. Don't over-fix individual persona findings.
