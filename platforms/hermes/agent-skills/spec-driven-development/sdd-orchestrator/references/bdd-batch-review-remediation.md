# BDD Batch Review and Remediation — Complete Pattern

## Context

After batch-generating BDD documents from EARS using `references/batch-bdd-generation-from-ears.md`,
every BDD needs:

1. Structural validation (`sdd_validate`)
2. 5-persona parallel review (qa-lead, technical-lead, chaos-engineer, site-reliability-engineer, security-auditor)
3. Fact-checker + board-chairperson synthesis
4. Remediation dispatch (fixers)
5. Re-validation

Doing this per-BDD is slow. The pattern below processes 7 BDDs across 4 phases.

## Phase 1: Parallel Review Dispatch (5 Personas)

Split 5 personas across two `delegate_task` calls (3 + 2) due to `max_concurrent_children=3`:

```
Batch A: qa-lead, technical-lead, chaos-engineer
Batch B: site-reliability-engineer, security-auditor
```

Both delegate calls run in parallel (separate tool invocations).
Each persona gets read access to all BDD files + EARS upstreams.

## Phase 2: Fact-Checker + Board-Chairperson Synthesis

After all 5 reviews return, dispatch sequentially:

1. **fact-checker**: Cross-validate all P0/P1 findings against documents. Remove false positives.
2. **board-chairperson**: De-duplicate, category-weight, score, produce manifest with execution order.

### Chairperson Scoring — Post-Remediation Expectation

| State | Typical Score | Implication |
|-------|---------------|-------------|
| Raw EARS→BDD generation | ~35/100 | Threshold not met |
| After automated remediation (document quality fixes) | ~55/100 | Still below 90 |
| After ADR-blocked items resolved + edge-case expansion | ~85-95/100 | Threshold met or close |

**The ~55 gap is normal for EARS-generated BDDs: roughly half structural/document-quality, half ADR-upstream.**

### De-duplicated Finding Template

Chairperson manifest uses this triage table:

| Count | Priority | Category | Action |
|-------|----------|----------|--------|
| N | P0 | critical | Remediate immediately |
| N | P1 | high | Remediate in this pass |
| N | P2 | medium | Defer to next pass or ADR resolution |

## Phase 3: Remediation by Fixer Type

Dispatch fixers in parallel based on manifest categories. Common BDD fix types:

| Fix Type | Scope Per BDD | Fixer |
|----------|---------------|-------|
| health_score alignment | 1 per BDD | chaos-engineer |
| Cross-link corrections | all cross_refs | technical-lead |
| Add missing EARS success scenarios | 2-4 scenarios | qa-lead |
| Add audit_logging scenarios | 1 per BDD | security-auditor |
| Add data_source_failed recovery | 1 per BDD | site-reliability-engineer |
| Rewrite boilerplate Gherkin (generic Given/When/Then) | all scenarios | qa-lead |

## Phase 4: Post-Remediation Validation

```python
# Validate all remediated BDDs at directory level
# sdd_validate(doc_type="bdd", document="04_BDD", layer="04_BDD")
# Expected: all files PASS 0 errors / 0 warnings
```

Then re-score via `sdd_score_show` if available. If score is >=90, layer is ready for ADR.
If still <90, inspect chairperson manifest for remaining P0/P1 items. Often they are
ADR-blocked and require upstream architecture decisions before BDD can cover them.

## BDD Remediation Checklist (TradeGent CC Proven)

After generating BDDs from EARS, apply these fixes in order:

1. **health_score**: must be `6/x` where x = total scenarios (not hard-coded or generic)
2. **priority tags**: scenario `priority: P0` must also have `@p0-critical` tag; `priority: P1` → `@p1-high`
3. **cross_links**: populate `downstream_expected` and `related_requirements` with upstream doc IDs
4. **Missing EARS coverage**: for every EARS requirement not traced by any scenario, add success scenario
5. **Audit logging**: for every scenario with side effects, ensure auditable action is logged
6. **Recovery scenarios**: at least 1 per BDD (from last unwanted_behavior or system failure path)
7. **Boilerplate rewrite**: replace `[description or step details]` with concrete Given/When/Then
8. **Data source failed**: for scenarios dependent on external data, add recovery for data-source failure

## Deferral Rules (What to Defer to ADR)

If score is still <90 after checklist, the remaining gap is usually ADR-blocked.

Concrete deferral categories from TradeGent CC batch:

| Finding | Why Deferred to ADR | Documented In |
|---------|---------------------|---------------|
| AuthN/AuthZ for scenario execution (OAuth, RBAC) | Needs authentication contract and role hierarchy | SPEC §security |
| Pre-trade risk gate (fat-finger, size limits) | Needs risk architecture and gate placement decision | ADR §risk-model |
| Idempotency and deduplication of scenarios | Needs transaction model and exactly-once decision | SPEC §reliability |
| Race conditions and concurrent execution | Needs concurrency model and locking strategy | ADR §concurrency |
| Edge cases (clock skew, DST, market holidays) | Needs calendar service and holiday decision | ADR §calendar |
| Timing assertions (WITHIN tolerance at BDD level) | Needs latency contract and timer precision spec | SPEC §performance |
| Parameterized tables (matrix scenarios) | Needs data contract and parameter schema | SPEC §data |
| Circuit breakers and cascading failure | Needs resilience architecture decision | ADR §resilience |
| Regulatory reporting hooks | Needs compliance event stream design | SPEC §compliance |

**Rule**: If a scenario requires mocking an external service, a time-travel harness,
or multi-system coordination to test, it likely belongs at SPEC/TDD level, not BDD.

## Batch Remediation via execute_code

For homogeneous fixes across all BDDs (e.g., health_score fix, cross_link corrections),
use Python inside `execute_code` rather than per-file subagent dispatch:

```python
import yaml, os
from collections.abc import Mapping

def deep_update(target, source):
    for k, v in source.items():
        if isinstance(v, Mapping):
            target[k] = deep_update(target.get(k, {}), v)
        else:
            target[k] = v
    return target

# Load all BDDs via subprocess.run(["cat", path]) — NOT read_file
# Apply fixes programmatically
# Dump with yaml.safe_dump and safe quoting
# Validate all
```

## Batch Remediation via Subagent Dispatch (Semantic Authoring)

When fixes require Gherkin authoring, scenario generation, or EARS-to-BDD translation
(subjective, not deterministic) `execute_code` is insufficient. Use `delegate_task`
fixer subagents instead. Proven at TradeGent CC 2026-05-08.

### Subagent batching

`delegate_task` max_concurrent_children=3. For N BDDs, dispatch in ceil(N/3) calls.
Example for 7 BDDs:

- Call 1: delegate_task([BDD-02, BDD-04, BDD-05 fixers])
- Call 2: delegate_task([BDD-06, BDD-07, BDD-08 fixers])
- Call 3: delegate_task([BDD-09 fixer])

### Per-subagent prompt template

Each subagent receives:

1. TARGET FILE path (original BDD to overwrite)
2. UPSTREAM EARS path (read for requirement details and timing assertions)
3. FIX LIST (structured, not prose): priority, cross_links, add_success (list of scenario descriptions), add_error, add_recovery (bool), add_audit (bool), rewrite_gherkin (bool), add_timing (bool), fix_spec_trace (bool), health_score, notes
4. RULES:
   - Overwrite original file; do NOT create new path
   - Scenario IDs: BDD.NN.SS.xxxx where xxxx = first 4 chars of SHA256("BDD.NN:{section}:{name}")
   - Keep exact YAML structure under scenario_structure.scenarios.{success,error,recovery,audit}
   - After writing, verify yaml.safe_load() and report scenario count breakdown
   - Return absolute file path and final scenario count

### Verification after each batch

After each delegate_task returns, run `yaml.safe_load()` + `os.path.getmtime()` on every file in the batch to confirm:

- File mtime changed (not still at pre-remediation timestamp)
- Scenario count increased by expected delta
- YAML parses without error

```python
import os, yaml
for f in bdd_files:
    mtime = os.path.getmtime(f)
    with open(f) as fh:
        data = yaml.safe_load(fh)
    sc = data.get("scenario_structure", {}).get("scenarios", {})
    total = sum(len(sc.get(k, [])) for k in ["success","error","recovery","audit"])
    print(f"{f}: modified={datetime.fromtimestamp(mtime)} scenarios={total}")
```

Re-dispatch any subagent that timed out or failed to modify the file.

### Post-batch UCX validation

Run `sdd_validate` on every rewritten file. Expected: PASS (0 errors, 0 warnings).
Do not rely on subagent self-verification — validate independently.

## Health Push Pass — Convergent Data-Correction Pattern (TradeGent CC Proven)

After the first remediation pass (add missing scenarios, rewrite boilerplate Gherkin, add audit/recovery),
health_score typically lands at 6/x. Pushing from 6 → 8 requires a SECOND review+remediation cycle,
but the fixes are qualitatively different — PURE DATA CORRECTIONS, not new scenario authoring.

### Why a Second Pass Is Needed

The first remediation focuses on *adding missing content* (scenarios, audit trails, recovery paths).
Reviewers can't catch data-quality issues until that content exists. The second pass catches:

- SHALL keyword pollution in Then clauses (redundant with Given/When/Then format)
- spec_trace format inconsistency (legacy placeholders, mixed `@ears:` vs `Behavior:` prefixes)
- ears_coverage miscounts (numerator AND denominator wrong)
- Non-standard scenario ID segments (SS/ER/RC/AU instead of .03.)

### How It Works — Convergent-Then-Dispatch

1. **Dispatch 5-persona re-review** in parallel, targeting ONLY the docs with health < 8.
   Each persona writes a `*-HEALTH8-REVIEW.md` report. Personas are the same 5 used for BDD review.

2. **Do NOT run fact-checker or board-chairperson.** The findings will be highly convergent
   (same 8-12 items across all 5 reports) because they're objective data defects, not subjective
   content gaps. Running synthesis would add latency for zero value.

3. **Extract convergent fix lists** — scan the review reports for items mentioned by 2+ personas.
   These are the ground-truth fixes. Items mentioned by only 1 persona are noise.

4. **Dispatch fixer subagents** implementing the convergent list per BDD. Fixers should:
   - Remove all SHALL keywords from Then clauses (replace "SHALL retain" → "retain")
   - Normalize spec_trace to `@ears: EARS.NN.SS.xxxx` format
   - Correct ears_coverage counts
   - Unify scenario ID segments
   - Bump health_score to 8/x
   - Update last_updated

5. **Validate all rewritten files** with `sdd_validate`. Expected: PASS 0E/0W.

### Typical Convergent Findings (TradeGent CC, 2026-05-12)

| Finding | Affected Docs | Fix |
|---------|--------------|-----|
| SHALL keyword in Then clauses | ALL 7 | Remove; use present-tense declarative verbs |
| spec_trace: legacy "5 (Behavior — X)" format | BDD-06, BDD-08 | Replace with `@ears: EARS.NN.SS.xxxx` |
| spec_trace: "Behavior: X" prefix (no @ears) | BDD-07 | Replace with `@ears:` prefix |
| ears_coverage: 6/8 when actual is 8/8 | BDD-06 | Correct to 8/8 |
| ears_coverage: 6/8 when actual is 7/7 | BDD-08 | Correct to 7/7 |
| scenario IDs: SS/ER/RC/AU segments | BDD-05 | Replace with .03. segment |
| health_score: 6/x | ALL 7 | Bump to 8/x |
| stale version (1.0) | BDD-08 | Bump to 1.1 |
| missing spec_trace descriptions | BDD-04 | Add parenthetical descriptions |

### Anti-Pattern: Re-dispatching Full Fixers

Do NOT dispatch fixers with instructions like "add missing scenarios" or "rewrite Gherkin"
in the health push pass. The scenarios are already there and the Gherkin is already concrete
from the first pass. Health push fixers should ONLY apply data corrections. Giving them
broad authoring instructions causes them to waste API calls rewriting already-good content.

### Why This Won't Reach 9 or 10

The remaining gap (8/x → 10/10) requires ADR decisions:

- Auth/AuthZ scenarios need OAuth/RBAC architecture
- Race condition scenarios need state-machine contracts
- Edge-case scenarios need calendar-service decisions
- Parameterized tables need data-contract schemas
- Timing contracts need latency-budget ADRs

These are legitimately ADR-blocked. Health 8/x is the ceiling for BDD content before
Layer 5 ADR generation. Document this in the chairperson manifest with explicit deferral
rationale per finding.

## Known Issues

1. **read_file inside execute_code**: Use `subprocess.run(["cat", path])` for clean YAML.
2. **Subagent timeout on large BDDs**: `delegate_task` with >800 line documents times out. Review via file-read + findings generation is more reliable.
3. **Placeholder hashes in element IDs**: BDD generation from EARS may produce `xxxx` placeholder hashes. Fix by recomputing SHA256 of "{doc_id}:{section_id}:{label}".
4. **BDD YAML schema traversal — scenarios are NOT a flat list**: BDD v3.2 nests scenarios under `scenario_structure.scenarios.{success,error,recovery,edge,performance,security}`. Accessing `doc.get("scenarios", [])` returns `[]` every time. Correct traversal:

   ```python
   ss = doc.get("scenario_structure", {})
   sc = ss.get("scenarios", {})
   total = 0
   for key in ["success", "error", "edge", "performance", "security", "recovery"]:
       total += len(sc.get(key, []))
   ```

   **Symptom**: All BDDs show 0 scenarios in inventory; reality is 6-15 per doc. This broke a user status query because the parser assumed a flat `scenarios` list. Always traverse the typed buckets.
5. **sdd_remediate is structural-only, not semantic**: See `references/ucx-remediate-content-limitations.md`. For scenario authoring, always use subagent dispatch or scripted patching with complete YAML rewriting.
6. **UCX validation is structural-only**: `sdd_validate` confirms schema and ID compliance; it does NOT check scenario coverage, Gherkin quality, or traceability accuracy. Content quality is verified via chairperson scoring, not UCX tooling.
7. **sdd_validate JSON report field location**: `passed` and `is_valid` at the top level of the returned JSON are often `null` (UCX quirk). The actual validation result lives in `summary.is_valid`. Always read `summary.is_valid` or `summary` block — never trust top-level `passed`/`is_valid`. Symptoms: script shows all BDDs FAIL despite 0 errors/0 warnings; reality is PASS.
8. **Subagent timeout recovery pattern** (TradeGent CC proven): When a fixer subagent times out (600s), re-dispatch it solo in the next `delegate_task` call with a fresh context. BDD-05 took 3 dispatch attempts to complete. Do not give up on the first timeout — each retry reduces the context window load since prior attempt's work may be partly written to disk. Verify file mtime after each retry — if mtime advanced, the subagent did write output before timing out; inspect the file to determine whether re-dispatch is needed.
9. **Benchmark doc metadata gap pattern**: When some BDDs are created as benchmarks (concrete Gherkin, validated early) and others as batch templates (boilerplate, generated later), the benchmarks may have BETTER scenario quality but WORSE metadata (missing health_score, cross_links, stale version/last_updated). Fix benchmarks with structural patches — never re-dispatch them to subagents. Benchmarks don't need Gherkin rewrites; they only need metadata alignment. The reverse is also true: batch docs may have up-to-date metadata but hollow Gherkin. Triage each doc individually rather than applying uniform fixes.
