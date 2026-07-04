# HERMES-SINGLE-PASS-STRIP Plan — strip author self-claim for the `single_pass` review paths (REVIEW_TEAM.md:82 conformance fix)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-SINGLE-PASS-STRIP                     |
| Type           | fix (conformance)                           |
| Status         | READY — 2026-07-04 (3 review passes; Pass 2 = 3 independent agents, Pass 3 independent; 0 load-bearing) |
| Depends on     | none (H-6.2 strip helper already shipped)   |
| Feeds          | completes H-6.2 (the `single_pass` half the saga-only fix left open) |
| Version impact | **Hermes PATCH** (`0.6.0 → 0.6.1`). **No framework change** — the contract exists in `REVIEW_TEAM.md`; consumer-side only. No GATE-SPEC, no re-vendor. |

## Objective

`REVIEW_TEAM.md:81-82` requires engines to strip author self-claim fields
(`*_ready_score`/`*_score`/`readiness_score`/`audit_score`) from the artifact body
before a lens sees it — **"both in `team` mode and `single_pass` mode."** It is an
**engine-level, surface-agnostic MUST**.

H-6.2 (D-0049) added `_strip_author_self_claim` but only in the saga `team` path
(`saga_orchestrator.py:615`, before fan-out). The **`single_pass` paths were left
unstripped**, so H-6.2's CLOSED status was premature — the MUST is still violated on
two surfaces:

- **MCP `prompt_only`** (`tool_registry.py:1624`) — builds the review prompt via the
  shared builder with unstripped `sections`.
- **CLI `single_pass`** (`cli/main.py:1005`) — the `hermes review` default
  (`--review-mode` **defaults to `prompt_only`**, `cli/main.py:104,200`), also
  building via the shared builder with unstripped `review_sections`.

Both write the artifact body — author `*_ready_score` anchors intact — into the lens
prompt (`review_prompt.txt`), the exact anchor effect the spec forbids.

This fixes the violation at the **single chokepoint both paths share**: the review
prompt builder `run_project_review_build` (`runner.py:27`). Stripping there covers
MCP + CLI `single_pass` *and* the saga branches/aggregate in one place.

**Playbook injection for `single_pass` is explicitly NOT in this plan** — the
independent review surfaced three unresolved design questions (crew-vs-`personas`
override, the binding-citation instruction being literally false without a
synthesizer, crew-vs-project-mapping coherence). It is deferred to its own plan with
those questions captured as a new backlog entry (see Out of scope). This plan is the
minimum sufficient fix for the conformance violation.

## Scope

**In:**

- **Extract the strip helper to a shared module.** Move `_strip_author_self_claim` +
  `_SELF_CLAIM_RE` (`saga_orchestrator.py:85,91`) into a new
  `review/section_hygiene.py` as the public `strip_author_self_claim(sections)`
  (pure move, no behavior change).
- **Strip at the builder (the chokepoint).** `run_project_review_build`
  (`runner.py:27`) calls `strip_author_self_claim(sections)` at the top, before
  `assemble_project_review_prompt`. This covers **all five** call sites: MCP
  `prompt_only` (`tool_registry.py:1624`), CLI `single_pass` (`cli/main.py:1005`),
  saga branch (`saga_orchestrator.py:284`,`:422`), saga aggregate
  (`saga_orchestrator.py:939`).
- **Remove the now-redundant saga pre-strip.** Delete the `saga_orchestrator.py:615`
  call + the local `_strip_author_self_claim` def + `_SELF_CLAIM_RE`, and **prune the
  now-orphaned `replace` import** (`saga_orchestrator.py:10` — `replace` is used only
  by the strip helper, `:99`; `dataclass` stays, used by `SagaReviewResult`). The
  saga still strips — via the runner each branch/aggregate calls.
- Update the two existing tests importing `_strip_author_self_claim`
  (`test_saga_review_orchestrator.py:530,554`) to `strip_author_self_claim` from
  `section_hygiene`; add a runner-level strip test + MCP + CLI `single_pass` prompt
  assertions (no existing `prompt_only` test — these are the first guard).
- **Correct H-6.2 in `HERMES-BACKLOG.md`** (its CLOSED claim covered only the saga
  half) + **add a deferred backlog entry** for `single_pass` playbook injection.
- Hermes `0.6.0 → 0.6.1`; Hermes CHANGELOG (naming the 0.6.0 non-conformance) + root
  CHANGELOG; D-0051; HANDOFF.

**Out of scope (deferred — new backlog entry, with the review's design questions):**

- **Playbook injection for `single_pass`.** Feasible in principle (the builder takes
  `playbook_text`) but has three unresolved design decisions the review surfaced:
  1. **Crew vs requested `personas`.** `prompt_only` forwards
     `personas=arguments.get("personas")` (`tool_registry.py:1626`); a crew-union
     injection would mismatch a caller that passes a persona subset. Must key off the
     requested personas (fallback to crew) or justify whole-crew injection.
  2. **The binding-citation instruction is false for `single_pass`.**
     `_PLAYBOOK_CITATION_RULE` (`context_builder.py:383-392`) is appended
     unconditionally when `playbook_text` is set and asserts "Findings without a valid
     `check` citation are **discarded by the synthesizer**" — but `single_pass` has no
     synthesizer/discard. Fixing this needs a parametrized (softened) citation rule —
     a `context_builder` change, not a call-site tweak.
  3. **Crew (`REVIEW_CREWS.yaml`) vs project `persona_mappings.yaml`** can diverge;
     injection following the spec crew regardless must be stated + justified.
- **Citation floor + `playbook_coverage` for `single_pass`.** `prompt_only` returns
  raw stdout and never parses findings; enforcing the floor needs a parse→filter
  pipeline `single_pass` structurally lacks. Deferred with the injection.
- **No-findings 95-cap (H-6.1)** — N/A (no per-lens scoring in `single_pass`).

## Approach / Design (D-0051)

### Why the runner, not the call site

The review-prompt build is funneled through one function, `run_project_review_build`
(`runner.py:27`), by all five callers. `REVIEW_TEAM.md:82` is engine-level, so the
strip belongs at that chokepoint — one edit closes every `single_pass` surface (MCP +
CLI) and keeps the saga covered. A per-call-site strip (the first draft's approach)
structurally guarantees a missed surface — it already missed the CLI default path.

The saga's existing `:615` pre-fan-out strip becomes redundant once the runner
strips (every saga branch + the aggregate call the runner). Removing it avoids a
double-strip; the regex is idempotent anyway (`sub` on already-clean content is a
no-op), so correctness does not depend on the removal — but removing it keeps one
chokepoint and prunes the orphaned `replace` import.

`run_project_review_build` has no non-review caller (verified — 5 callers, all review
prompt builds), so stripping there is universally correct: every review lens prompt
must have the author's self-score removed.

### The extraction

`strip_author_self_claim` moves verbatim to `review/section_hygiene.py` (a pure
function over `list[SourceSection]`, importing only `re`, `dataclasses.replace`, and
`SourceSection`). `runner.py` imports it; `saga_orchestrator.py` drops its copy. This
avoids a cross-module import of a private `_name` and gives the helper an honest
shared home both the runner and (former) saga logic point to.

### Versioning

The strip is fixing a **conformance violation shipped in Hermes 0.6.0** (`single_pass`
never stripped) → a **bugfix** → **Hermes PATCH** `0.6.0 → 0.6.1`. No `framework/`
change (the contract pre-exists in `REVIEW_TEAM.md`); no GATE-SPEC, no re-vendor. The
CHANGELOG states that 0.6.0's `single_pass` path was non-conformant to
`REVIEW_TEAM.md:82`, not merely "added a strip."

### Backward-compatibility

Moving the strip to the runner strips every review build — which is the intended
contract. The only observable change is that `single_pass` prompts (MCP + CLI) no
longer contain the author's `*_ready_score` lines; return shapes are unchanged (raw
stdout for `prompt_only`; the saga path is behavior-identical, just stripping one
layer down). No parsing/scoring path changes.

## File structure

### Added

| Path | Purpose |
| ---- | ------- |
| `platforms/hermes/src/mcp_server/review/section_hygiene.py` | shared `strip_author_self_claim` + `_SELF_CLAIM_RE` |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/hermes/src/mcp_server/review/runner.py` | import + call `strip_author_self_claim(sections)` at the top of `run_project_review_build` (`:27`) |
| `platforms/hermes/src/mcp_server/review/saga_orchestrator.py` | delete local strip def + `_SELF_CLAIM_RE` + the `:615` call; prune the orphaned `replace` import (`:10`) |
| `platforms/hermes/tests/unit/test_saga_review_orchestrator.py` | retarget the 2 strip-test imports to `section_hygiene` |
| `platforms/hermes/tests/unit/` (new or existing runner/section-hygiene test) | runner-level strip test + MCP + CLI `single_pass` prompt-has-no-score assertions |
| `platforms/hermes/VERSION` (→ `0.6.1`) + Hermes CHANGELOG + root CHANGELOG | version + entries (name the 0.6.0 non-conformance) |
| `plans/HERMES-BACKLOG.md` | correct H-6.2 (saga-only → now fully closed); add deferred `single_pass` playbook-injection entry |
| `plans/DECISIONS.md` (D-0051) / `plans/HANDOFF.md` | docs |

## Implementation sequence

### Task 1: extract strip helper (pure move) — [CODE]

- New `section_hygiene.py`; `saga_orchestrator.py` drops the def + `_SELF_CLAIM_RE` +
  `:615` call + prunes `replace`. Retarget the 2 tests. Saga suite green (behavior via
  the runner, next task).

### Task 2: strip at the runner (the fix) — [CODE]

- `run_project_review_build` calls `strip_author_self_claim(sections)` before
  assembling. Tests: (V2) MCP `prompt_only` build → `prompt_text`/`review_prompt.txt`
  has no `brd_ready_score`; (V3) CLI `single_pass` build → same; (V1) saga suite still
  green (now strips one layer down).

### Task 3: version + docs

- Hermes `0.6.1`; both CHANGELOGs; D-0051; correct H-6.2 + add the deferred injection
  entry in HERMES-BACKLOG; HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | `python -m pytest platforms/hermes/tests -q` (saga incl.) | green — saga behavior unchanged (strips via the runner now) | pure-move + chokepoint |
| V2 | MCP `prompt_only` review build over a section with `brd_ready_score: 92` | assembled `prompt_text` has no `brd_ready_score` line | MCP single_pass fix |
| V3 | CLI `single_pass` review build (default `--review-mode`) over the same | `review_prompt.txt` has no `brd_ready_score` line | CLI single_pass fix |
| V4 | runner-level: `run_project_review_build` strips regardless of caller; unrelated prose survives | stripped + prose intact | chokepoint correctness |
| V5 | `section_hygiene.strip_author_self_claim` unit (the moved V8 tests) | pass unchanged | pure move |
| V6 | `ruff check platforms/hermes/src` | clean — no orphaned `replace` import | G3 |
| V7 | `python -m pytest tests/conformance -q` | green (no framework change) | no regression |

## Docs to update

- [ ] `platforms/hermes/CHANGELOG.md` — `[0.6.1]` (names the 0.6.0 single_pass non-conformance)
- [ ] root `CHANGELOG.md` — Hermes `0.6.0 → 0.6.1` entry
- [ ] `plans/DECISIONS.md` — D-0051
- [ ] `plans/HERMES-BACKLOG.md` — correct H-6.2 CLOSED→completed-here; add deferred single_pass injection entry
- [ ] `plans/HANDOFF.md` — arc progress

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Removing the saga `:615` strip changes saga behavior | low | the runner now strips every branch/aggregate build; V1 runs the full saga suite; the moved helper is unit-tested (V5); regex is idempotent so no double-strip concern |
| R2 | Orphaned `replace` import trips ruff after the def is removed | med | Task 1 prunes it; V6 runs ruff explicitly |
| R3 | A review build exists that SHOULD keep the score (some non-lens use of the builder) | low | verified all 5 callers are review lens prompts (`__init__` export aside); `REVIEW_TEAM.md:82` mandates strip for every lens prompt |
| R4 | Stripping in the runner double-strips for the saga (perf) | low | saga `:615` removed → single strip per build; even if kept, idempotent |
| R5 | H-6.2's "CLOSED" correction reads as reopening shipped work | low | frame as "H-6.2 shipped the saga half; this completes the `single_pass` half the spec's `both modes` clause requires" — same task lineage, not a regression |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The review-prompt builder is the shared chokepoint (strip site) | `def run_project_review_build` | platforms/hermes/src/mcp_server/review/runner.py:27 |
| 2  | The builder does NOT strip today | `assemble_project_review_prompt` | platforms/hermes/src/mcp_server/review/runner.py:38 |
| 3  | MCP `prompt_only` builds via the shared builder with unstripped sections | `run_project_review_build(` | platforms/hermes/src/mcp_server/tool_registry.py:1624 |
| 4  | CLI `single_pass` builds via the shared builder with unstripped sections | `run_project_review_build(` | platforms/hermes/src/mcp_server/cli/main.py:1005 |
| 5  | CLI `--review-mode` defaults to `prompt_only` (so the CLI default IS single_pass) | `default="prompt_only"` | platforms/hermes/src/mcp_server/cli/main.py:104 |
| 6  | Saga branch also calls the shared builder (covered by the runner strip) | `run_project_review_build(` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:422 |
| 7  | Saga aggregate also calls the shared builder | `aggregate = run_project_review_build` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:939 |
| 8  | The strip helper + regex live locally in `saga_orchestrator` (to be extracted) | `_strip_author_self_claim` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:91 |
| 9  | The saga calls the strip once before fan-out (to be removed) | `_strip_author_self_claim` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:615 |
| 10 | `replace` is imported and used ONLY by the strip helper (orphaned on removal) | `dataclass, replace` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:10 |
| 11 | Two existing tests import `_strip_author_self_claim` (must retarget) | `_strip_author_self_claim` | platforms/hermes/tests/unit/test_saga_review_orchestrator.py:530 |
| 12 | Spec: strip MUST in **both** `team` and `single_pass` mode (engine-level) | `single_pass` | framework/governance/REVIEW_TEAM.md:82 |
| 13 | H-6.2 is currently marked CLOSED (only the saga half shipped) | `CLOSED` | plans/HERMES-BACKLOG.md:256 |
| 14 | Current Hermes version is `0.6.0` (→ `0.6.1` PATCH) | `0.6.0` | platforms/hermes/VERSION:1 |
| 15 | Most recent decision is D-0050 → next free is D-0051 | `D-0050` | plans/DECISIONS.md:13 |

## Review log

### Pass 1 — 2026-07-04 — self-review

- (superseded by the slim rewrite below; see Pass 2/3)

### Pass 2 — 2026-07-04 — independent (3-agent parallel per OPS-0067)

Three fresh-context reviewers (citations, design, completeness) reviewed the
**original** draft (which bundled the strip MUST-fix with `single_pass` playbook
injection, Hermes MINOR). Findings:

- **Citations:** 18/18 ledger rows confirmed; 1 trivial line-drift (`--fix`ed).
- **[LOAD-BEARING] Strip missed the CLI `single_pass` caller** (`cli/main.py:1005`;
  `--review-mode` defaults to `prompt_only`) — the headline "closes the violation"
  was overstated. → **Fixed by striping at the runner chokepoint** (covers MCP + CLI +
  saga).
- **[LOAD-BEARING] Orphaned `replace` import** on removing the local strip def
  (ruff F401). → Task 1 now prunes it; V6 runs ruff.
- **[LOAD-BEARING] H-6.2 marked CLOSED but only the saga half shipped.** → this plan
  corrects the backlog + completes the `single_pass` half.
- **[LOAD-BEARING] Injection: crew-vs-requested-`personas` mismatch** (G6) +
  **[MINOR] false binding-citation instruction for `single_pass`** (F3, needs a
  `context_builder` change) + **[MINOR] crew-vs-project-mapping divergence** (F2).
  Three unsolved design questions on the *enhancement*.

**Decision — slimmed to the strip conformance fix; injection deferred.** The MUST-fix
had a single real issue (the second caller → runner-level). The injection generated
three design problems, all tracing to it being a speculative enhancement bundled with
the fix — exactly the over-engineering signal the CLAUDE.md "minimal-and-realistic"
rule + this plan's own R6 warn about. Injection moves to its own plan with F2/F3/G6
captured as a new HERMES-BACKLOG entry. Version drops MINER→PATCH (pure conformance
fix). No circular-import risk was found for the (now-deferred) helper (G5, clean).

### Pass 3 — 2026-07-04 — independent (fresh-context code-reviewer) re-review of the slimmed plan

**0 load-bearing findings.** The reviewer verified the pivot end-to-end:

- **Runner-level strip safe + complete.** All 5 callers of `run_project_review_build`
  route through the one function; `assemble_project_review_prompt` is invoked at
  exactly one site (`runner.py:38`) → stripping there reaches every review-lens
  prompt. **No third unstripped surface:** the other `run_executor` calls send
  either runner-built (already-stripped) prompts or a *remediation* prompt
  (`tool_registry.py:1759`) — a different stage the MUST doesn't scope.
- **Removing saga `:615` is behavior-identical.** Between `:615` and the runner
  calls, `sections` feeds only `document_fingerprint = f"…:{len(sections)}:…"`
  (`:630`); the strip returns one section per input, so `len(sections)` — and thus
  `deterministic_review_run_id` — is byte-identical. `replace` confirmed orphaned
  (`:99` only); `dataclass` retained.
- **No circular import** (`review → prompts`, one-directional); **no existing test
  asserts a score survives into a built prompt** (all `*_ready_score` test hits are
  validation/scoring/parser tests). PATCH + H-6.2 correction + injection deferral all
  confirmed sound.
- 14/15 ledger rows confirmed; 1 cosmetic citation nit (row 13 → `:256` CLOSED
  marker) — folded.

**Result:** ready
