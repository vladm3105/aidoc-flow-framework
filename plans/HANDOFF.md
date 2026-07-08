# Session Handoff

> **▶ IN FLIGHT (2026-07-08) — PROVISIONAL-IDS-002 Phase 1 impl PR open (spec-tier,
> awaiting founder ratification).** The plan PR (#269) merged; the Phase-1 impl builds
> `rehash --check` (the Model-2 drift verifier) + formalizes the hash-input contract.
> **Versions:** framework spec `0.35.0` (this PR) · plugin `0.23.2` · hermes `0.7.3`.
>
> **PROVISIONAL-IDS-002 Phase 1 (D-0062, framework 0.34.2 → 0.35.0):** executes the
> ratified Model-2 direction (D-0061). **(1)** Formalized the byte-exact hash-input
> contract in `ID_NAMING_STANDARDS.md` — the normalization transform (NFC → casefold →
> strip `[a-z0-9 ]` → collapse ws → trim → first 100) + the BRD §7 FR field-extraction
> boundary (multi-line description, wrapped band); migrated the normalization out of the
> BRD template (now a cross-ref). **(2)** `python -m sdd_doc_lint.rehash --check` recomputes
> each canonical BRD §7 FR hash and emits **`IDDRIFT01`** (advisory) on a mismatch — opt-in
> (NOT default lint → corpus lint byte-identical), `canonical`-gated, BRD §7 only. **(3)** 16
> conformance tests (`test_rehash_verifier.py`); primitives vendored byte-identical (rehash.py
> added to the sync + drift guard). **Scoped "verifiable on demand," not "verified"** (Phase 1
> doesn't run on the corpus; corpus reconciliation is Phase 2). **Deferred to founder-decided
> Phase 2+:** `rehash --fix`, all-8-layer extraction, corpus reconciliation, advisory→gate
> promotion, Unicode-category strip. Also unblocks **H-11c** (Hermes SHA-256 residue).
>
> ---
>
> **✅ PRIOR SESSION COMPLETE (2026-07-06) — Hermes doc arc + the ENTIRE framework-core
> backlog cleared + H-11b + a Claude-plugin production-readiness audit & fix.**
> **Versions then:** framework spec `0.34.1` · plugin `0.23.2` · hermes `0.7.3`.
>
> **Plugin production-readiness (2026-07-06, D-0060, plugin 0.23.2):** a 4-agent audit
> (spec-consistency / skills / packaging / conformance-tooling-docs) found the plugin
> clean/green on every dimension **except one release BLOCKER** — the 9 `doc-*-audit`
> skills + `synthesizer.md` resolved their vendored playbooks/`REVIEW_TEAM.md` via
> `${CLAUDE_PLUGIN_ROOT}/../../framework/…`, which escapes the plugin root, so the
> weighted-crew review collapsed to zero coverage **in any distributed install** (worked
> only in the source checkout by coincidence). Fixed (dropped `/../../`, 11 refs) + 3
> SHOULD-FIX (doc-ears D54-F04 propagation; deprecated-stub `v0.7.0 → v1.0.0`; example
> lint-baseline note).
> **Framework production-readiness (FRAMEWORK-PROD-READINESS-001, D-0061, framework 0.34.2):**
> the audit's 2 framework-side items — (1) **SHA-256 over-claim scoped to reality** across all
> **13** spec surfaces (`ID_NAMING_STANDARDS.md` + 5 templates + 5 layer READMEs + PRD-00/SPEC-00
> index templates): each now says the SHA-256 form is the *canonicalization target, unverified
> until `rehash --check`* (engines LLM-generate, not real hashes; algorithm unchanged); (2)
> **GD-02…05 flipped Proposed → Accepted**. Prose/status only, lint byte-identical.
> **▶ DECIDED — PROVISIONAL-IDS-002 = Model 2** (founder, 2026-07-07): enforce the content-hash
> as a **content-drift identifier**, using the **stable-ID + drift-fingerprint** model (ID minted
> once, never breaks citations; `rehash --check` compares `SHA256(current content)` to the ID's
> embedded hash and flags drift). NOT Model 1 (strict content-addressing) — it would shatter
> `@`-tag citations across 7 downstream layers on any upstream edit. This honesty-scoping is the
> interim; **the next build is the PROVISIONAL-IDS-002 plan** — `rehash --check` (drift-detect) +
> `rehash --fix` (re-canonicalize) + corpus reconciliation (the LLM-generated corpus IDs mostly
> won't match today), which flips "unverified until `rehash --check`" → "drift-checked by it."
> This also unblocks **H-11c** (the Hermes-side SHA-256 mention).
>
> **What shipped this session (14 PRs, D-0053 → D-0060):**
>
> - **Hermes doc arc:** H-11 orchestrator crew-model modernization (D-0053), ENG-STALE-DEPTH-DOCS
>   (single-path reconciliation), **H-11b** (D-0059 — deleted 5 orphaned/stale vendored
>   `references/` copies).
> - **Framework-core backlog — CLEARED** (every P2/P3 item shipped or deferred-with-rationale):
>   `ENG-FWD-COVERAGE`/`D54-F07`/`D54-F05` reconciled as already-shipped (COV01/COV02 +
>   TAG_SYNTAX.md); **IPLAN-LANG-001** (D-0054, de-Python the IPLAN template); **D54-F13/COV03**
>   (D-0055, phase-leak advisory — no new tag, band + roadmap already encode both axes);
>   **LINT-DOCID-HEADER-FALSE-POSITIVE** (D-0056, digit-leading ID02); **D54-F04** (D-0057,
>   dimension-appropriate EARS quantification); **D54-F08** deferred build-on-demand (D-0058).
> - *Recurring theme:* grounding repeatedly SHRANK the work — 3 "P2" items were already shipped,
>   D54-F13's "first-class phase tag" was avoided as redundant, D54-F04 was template-only, D54-F08
>   deferred rather than over-built. Minimal-and-realistic paid off.
>
> **CI facts for the next session:**
>
> - **Composition gate FIXED** — the v1.5.1 `aidoc-flow-ci` bump (#254) resolved the
>   `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` gap; **plan/docs/non-spec PRs now merge via the normal
>   green path (no `--admin`)**. Spec-tier PRs still need founder ratification.
> - **Known ai-review false-positive** — the v1.5.1 `ai-review` is diff-scoped: it flags a plan
>   cross-reference as a "broken xref" on every impl PR that cites its separately-merged plan
>   (hit #261). Verify the file is on `main`, `--admin` past it; real fix is upstream in
>   `aidoc-flow-ci` (resolve referenced paths against the repo, not just the PR diff).
>
> **▶ Open threads for next session (nothing blocking):**
>
> - **Hermes-parity backlog** (`HERMES-BACKLOG.md`): H-1/H-6.3 (saga architectural gate,
>   deferred), H-2 (shared-playbook port), H-13 (large-artifact chunking, follow-on to D-0051).
> - **H-11 residue (deferred):** H-11a (21 non-loaded cosmetic `v3.2` strings — low value);
>   **H-11c** (element-ID SHA-256 residue) — framework-BLOCKED by **PROVISIONAL-IDS-002**
>   (the framework templates ALSO still say SHA256; driving that framework-wide hash-vs-LLM-string
>   decision would unblock H-11c + reconcile the templates).
> - **Pre-existing TODO items (out of this session's scope):** `SKETCH-FILE-STANDALONE` (author-
>   deferred), `BL-REF-GRANULARITY` / `BL-STATUS-SCOPE` (BeeLocal consumer items), the legacy
>   `[legacy]` v3.2 scan.
>
> **CHANGELOG note:** the root `[Unreleased]` section has accumulated a large set
> (framework `0.32.x → 0.34.1`, hermes `0.4.0 → 0.7.3`, plugin `0.23.0 → 0.23.1`) — a release-cut
> (tag + `changelog/` split per `docs/TAGGING.md`) is a reasonable next deliberate action, but was
> not done here (out of scope of "update the changelog"; the entries are complete + accurate).
>
> ---
>
> **🟢 HERMES-PARITY ARC STARTED — Phase 1 SHIPPED (2026-07-02).** The big
> outstanding arc is underway. An evidence-backed assessment **corrected the stale
> `HERMES-BACKLOG.md` premise**: Hermes already HAS team-mode (working saga
> orchestrator + crew reconciliation), and the whole 0.32.x arc (D-0038…D-0044) is
> **auto-satisfied** via vendored `sdd_doc_lint` + shared templates. The real gap is
> older engine debt: **playbook injection + saga completeness**. **Phase 1 shipped**
> (#229 plan + impl): added the spec-required `PARTIAL_TIMEOUT` state to Hermes's
> saga table (was missing) + `test_saga_lifecycle_parity.py` enforcing both
> platforms against `REVIEW_SAGA.md` (a test `PARITY.md` over-claimed existed). No
> framework/Hermes version bump. D-0045; 4-phase roadmap in
> `plans/HERMES-PARITY-PHASE-1-PLAN.md` + the refreshed `HERMES-BACKLOG.md`.
> **Phase 2 — playbook injection (BRD+PRD) ✅ SHIPPED** (#231 plan + impl,
> `hermes/v0.4.0`, D-0046): the review saga injects per-`(layer,lens)` playbooks,
> enforces the `check:` citation floor (discard uncited), emits
> `verdict.playbook_coverage`. Keyed on crew membership (so `fact_checker`/
> `chairperson` are exempt, not failed — the bug the plan review caught); byte-identical
> `finding_filter` vendor; `check` threaded parser→reducer→verdict. 496 Hermes + 157
> conformance green. H-4 CLOSED for BRD+PRD.
> **Phase 3 — 8-layer coverage + CHG crew parity ✅ SHIPPED** (#233 plan + impl,
> `hermes/v0.5.0`, D-0047): H-5 was already delivered by Phase 2's layer-agnostic
> injection (verified + regression-tested across all 8 lifecycle layers); H-10 added
> the `chg` review crew to `persona_mappings.yaml` + removed the deferred-whitelist
> so the crew-coverage test enforces CHG. Crew-map parity only. 497 Hermes + 157
> conformance green.
> **H-12 — real saga-journal schema conformance ✅ SHIPPED** (#236 plan + impl,
> framework `0.32.7` + `hermes/v0.5.1`, D-0048): the real journal missed 4
> `saga.schema.json`-required fields (`artifact_id`/`layer`/`iteration`/`transitions`)
> and never recorded `transitions`; the Phase-1 guard validated only hand-authored
> fixtures, masking it. Added the 4 defaulted fields to `SagaRunState`, schema-shaped
> transition recording (run seed + each successful status/branch change,
> `{ts,from,to,scope}`), roundtrip in `_to_run_state`; the orchestrator derives
> `layer` from the **required** `doc_type` via `normalize_layer(layer or doc_type)`
> (F1 — not the optional `--layer`, caught by the independent plan review); added
> `09_CHG` to the schema enum (framework PATCH, re-vendored) so CHG journals validate;
> new `SagaRealJournalConformance` validates a real journal (lifecycle +
> `--layer`-omitted + CHG). "Live CHG saga" also closed (a real CHG journal now
> conforms). 160 conformance + Hermes saga tests green.
> **H-6.1 + H-6.2 — review calibration ✅ SHIPPED** (#238 plan + impl,
> `hermes/v0.6.0`, D-0049): no-findings rationale cap (`STRUCTURE-RAT-001`; parser
> captures the field + a latent clean-empty→`fallback`/`lens_score=None` bug fixed)
>
> - strip author self-claim (`*_ready_score`/`*_score`/… redacted before fan-out).
> Consumer-side; no framework change. Independent review reproduced the parser
> premise empirically + returned 0 load-bearing. 508 Hermes + 160 conformance green.
> **H-6.3 stays deferred** (single-pass saga → no iter-(N-1)); **H-2** not bundled
> (sub-checks live only in plugin SKILLs — needs a shared-playbook port decision).
> **HERMES-REVIEW-CONTENT-DELIVERY ✅ SHIPPED** (#243 plan + impl, `hermes/v0.7.0`,
> D-0051): the big one. While implementing the `single_pass` strip (#242), impl-stage
> end-to-end verification revealed **Hermes's LLM review was content-blind** — the
> prompt is persona+template+rules+metadata only, the executor a pure completion
> (`working_dir` not forwarded), `system_prompt=None`; the lens scored a document it
> never read. Fixed at the shared builder: inline a `## Document to Review` block from
> `included_sections` (dedupe the template placeholder), fold the runner-level strip so
> the inlined body is stripped — **making the H-6.2 strip effective for the first time
> (inert in 0.6.0)** + superseding #242. No new token accounting. 3-agent Pass 2 +
> independent Pass 3; the *impl-stage verify* (not the plan reviews) caught the gap.
> 511 Hermes + 160 conformance green. Deferred: H-13 large-artifact chunking.
> **H-14 plugin-side strip ✅ SHIPPED** (framework `0.33.0` + plugin `0.23.1`; GD-05 +
> D-0052): verified the plugin's agentic lens reads the author score from disk (the
> plugin analog of D-0051). Ratified **GD-05** (PR #246, founder-signed — the strip MUST
> gains a disregard-instruction fallback for direct-read lenses) + implemented plugin-side
> (9 audit + 9 fixer SKILLs + review-team + traceability-auditor). Both platforms now
> satisfy the strip MUST (Hermes physical strip, plugin disregard). 4-pass review folded
> 11 findings incl. the false "single_pass physically strips" claim + the missed 9-fixer
> surface. 160 conformance green.
> **H-11 sdd-orchestrator modernization ✅ SHIPPED** (PR #248 plan; impl `hermes/v0.7.1`
> - skill `2.1.0`, D-0053): the `sdd-orchestrator` skill described the obsolete v3.2
> "15 parallel personas + Lite/Standard/Full depth-tier" model. `SKILL.md` corrected to
> the weighted-crew + playbook + single-path model (persona model → point at
> `REVIEW_CREWS.yaml` + one illustrative BRD crew; scoring → weighted-average of crew
> `lens_score`s; BRD sections → point at `BRD-TEMPLATE.yaml`; 5-lens crews; MCP paths +
> "v3.2" pins fixed) + the two **loaded** governance files carrying the depth-tier residue
> (`GOVERNANCE_RULES.md` §7 + the primary-load `governance-load-protocol.md`) → single-path
> model. Doc-accuracy only; no engine/framework change. 4-pass review (Pass 2 = 3 agents,
> Pass 3 = fresh-context independent) expanded scope 1→3 files + 5 findings, MINOR→PATCH,
> D-0052→D-0053. 3 follow-ups carved (H-11a cosmetic v3.2 sweep, H-11b vendored-copy
> D-0013 decision, H-11c element-ID SHA-256 residue). H-11 CLOSED.
> **🟢 FRAMEWORK-CORE BACKLOG SWEEP (2026-07-06) — begun after the Hermes doc arc.**
> Grounded the whole framework-core backlog and found several "top P2" items were
> **already shipped** by the COV01/COV02 coverage engine + `TAG_SYNTAX.md`. Reconciled
> the tracking (PR #252, verified against code): **`ENG-FWD-COVERAGE` CLOSED** (= COV01/
> COV02 + `TRACEABILITY_MATRIX.md`); **`D54-F07`** doc-shipped, enforcement cosmetic-deferred;
> **`D54-F05`** core-subsumed by corpus-wide COV02; **`D54-F13`** narrowed to just its
> genuinely-open **phase-leak leg**. Then shipped **`IPLAN-LANG-001`** (PR #253 refreshed
> plan; impl PR = spec-tier, framework `0.33.0 → 0.33.1`, **D-0054**): de-Pythoned
> `IPLAN-TEMPLATE.yaml` example content (§2 `file_manifest` + §3 `execution_commands` +
> §5/§6 residual paths → `<…, per the @spec language>` + labelled Python examples);
> inheritance from `@spec`, no new field; structural contract preserved (no validator/
> conformance change); bundle re-vendored; 5-pass review (3 independent). Closes
> FRAMEWORK-TODO `D54-F06`. Then shipped **`D54-F13` phase-leak** (PR #256 plan; impl PR =
> spec-tier, framework `0.33.1 → 0.34.0`, **D-0055**): new lint rule **`COV03`** — the
> inverse of COV01's escape, an **advisory** (never blocks) when a `Future`-banded (deferred)
> FR IS realized downstream. **No new phase tag** — grounding found the `Future` band +
> BRD-00 `Cycle` roadmap already encode both phase axes (cross-cycle leaks are structurally
> prevented by trace-inert future BRDs). Canonical `tools/sdd_doc_lint` + both mirrors;
> TRACEABILITY.md §Coverage gates; 6 tests; zero example-corpus findings; verified
> end-to-end. Closes `D54-F13`. Then shipped **`LINT-DOCID-HEADER-FALSE-POSITIVE`** (PR #258
> plan; impl D-0056): the ID02 malformed-doc-id scan now fires **only on digit-leading
> `TYPE-<n>` tokens** (a valid id is `TYPE-<digits>`; a letter-leading `TYPE-<word>` like
> `PRD-Ready`/`BRD-TEMPLATE` is prose) — generalizes D-0043's `-INDEX` exemption. **Pure
> `tools/sdd_doc_lint` bugfix — no `framework/` change, no version bump, auto-mergeable**
> (D-0043 precedent). Then shipped **`D54-F04`** (PR #260 plan; impl D-0057, spec `0.34.0 →
> 0.34.1`): reworded the EARS-Ready rubric so a **non-latency** quantified bound (cycles /
> iterations / event-window / `*.count`) counts as quantified — percentiles stay required for
> **latency** only. Template-only (the playbook lenses were already correct); no new syntax;
> deterministic lint byte-identical (rubric is LLM-auditor scoring). Then **`D54-F08`
> DEFERRED** (build-on-demand, D-0058): the `--skeleton` template emit is a speculative DX
> convenience with real hazards (anti-aligned with the guidance-dense design; comment-fidelity
> loss on a YAML strip; normative underscore keys `_authored_form`/`_required_when_subtype`
> can't be naively stripped; no demand signal) — deferred with rationale, not built (founder
> chose defer). **✅ FRAMEWORK-CORE BACKLOG CLEARED** — every P2/P3 item is shipped or
> deferred-with-rationale; nothing genuinely-open remains.
> **H-11 follow-ups (Hermes backlog):** **H-11b CLOSED** (D-0059, hermes 0.7.3) — deleted the
> 5 orphaned + stale hand-vendored `sdd-orchestrator/references/` framework-doc copies
> (grep-verified no loader; `id-naming-standards.md` was "SDD v3.2", 53 vs 191 canonical lines,
> describing the retired sequential-ID scheme; per D-0013 Hermes reads `framework/` directly →
> delete, not re-sync). **H-11a** (21 non-loaded cosmetic `v3.2` strings) + **H-11c** (element-ID
> SHA-256 residue — framework-gated by PROVISIONAL-IDS-002; framework templates also still say
> SHA256) remain DEFERRED (low value / framework-blocked respectively).
> **Note:** IPLAN-LANG-001 (#255) + D54-F13/COV03 (#257) + D54-F04 (#261) all merged
> (founder-ratified). **CI FIX:** the v1.5.1 `aidoc-flow-ci` bump (#254) FIXED the
> composition-check-on-PR-head gap (`AIDOC-CI-COMPOSITION-CHECK-PRHEAD`) — plan/docs PRs now
> merge via the **normal green path** (no `--admin` needed); #258/#260 merged cleanly without
> admin. **KNOWN CI FALSE-POSITIVE:** the v1.5.1 `ai-review` is diff-scoped — it flags a plan
> cross-reference as a "broken xref" on every impl PR that cites its separately-merged plan
> (e.g. #261). Verify the file is on `main` and `--admin` past it; the real fix is upstream in
> `aidoc-flow-ci` (resolve referenced paths against the repo, not just the PR diff).
>
> ---
>
> **ENG-STALE-DEPTH-DOCS ✅ SHIPPED** (PR #250 plan; impl `hermes/v0.7.2` + skill `2.1.1`,
> no new D-number): completes the **behavioral** legs of H-11a — the sdd-orchestrator's
> *user-facing* published docs still advertised the dead SDD-Lite/Standard/Full
> depth-variant model (D-0053 fixed the SKILL + 2 loaded governance files; these 7
> published `root-docs/`+`governance/` surfaces were the remainder, incl. a
> **self-contradictory** README and two **dead links** to a nonexistent
> `SDD_DEPTH_GUIDE.md`). All reconciled to the single-path model; closes FRAMEWORK-TODO
> `ENG-STALE-DEPTH-DOCS` (residual: the public-render leg, verify at next release cut).
> 3-pass review (Pass 2 independent caught a missed changelog-line surface). No
> framework/engine change. What's left under H-11a is now purely the cosmetic v3.2
> version-string sweep.
> **▶ Next (Hermes follow-ons, each its own plan):**
> **(1)** ~~`H-6`/`H-2` calibration deltas~~ — H-6.1/6.2 done (above);
> remaining calibration items (no-findings rationale /
> author-self-claim strip / fixer-regression). **(3)** Phase 1b (saga break-circuit
> exercise + `quality_loop_max_iterations`). **(4)** `prompt_only` playbook injection;
> H-13 large-artifact chunking. ~~`H-11` agent-skill modernization~~ ✅ done. See
> `HERMES-BACKLOG.md`.
>
> ---
>
> **🟢 P3 CLEANUP ARC — items 2 & 3 SHIPPED + prerequisite bugfix + regen runbook +
> P3 docs sweep (2026-06-30).** `main` clean at framework spec **0.32.6**, plugin
> `0.23.0`. Eight PRs merged this session (all admin-merged — composition-CI gap
> forces `--admin`; founder standing OK).
>
> - **Item 2 — `BL-READY-SCORE-ADVISORY` ✅ SHIPPED** (#221 plan + #222 impl, spec
>   `0.32.3 → 0.32.4`, D-0042). Marked the 14 `*_ready_score`/`target_score` fields
>   advisory across the 7 layer templates + reworded 15 contradicting `_guidance`
>   prose lines (ai-review caught the "required"/"quality gate" contradiction the
>   2-cycle plan review missed → plan Pass 3).
> - **`STRUCT01-INDEX-EXEMPTION` ✅ SHIPPED** (#223 plan + #224 impl, pure linter
>   fix, no spec bump, D-0043). Prerequisite bug surfaced by item-3's review: the
>   `*-INDEX` STRUCT01/trace exemption read top-level `artifact_type` but the 8
>   index templates nest it under `custom_fields` → consumers' indexes threw
>   STRUCT01. Fix: filename-based `_is_index_doc` + ID02 `-INDEX` skip. 3 passes
>   (Pass 2 caught the original docs-only fix would self-trip ID02 → pivoted).
> - **Item 3 — `ENG-BRD-SKETCH-ROADMAP` ✅ SHIPPED** (#225 plan + #226 impl, spec
>   `0.32.4 → 0.32.5`, D-0044). BRD-00 index "Planned BRDs" table = roadmap home
>   (cycle/PROD/`@depends:`/status); `01_BRD/README.md` project-init + trace-inert
>   Sketch; `BRD-TEMPLATE.yaml` cross-ref. 4 passes, 3 independent.
> - **Item 4 — regen runbook delivered + P3 docs sweep SHIPPED.**
>   `plans/CORPUS-REGEN-RUNBOOK.md` is the founder-runnable procedure for the
>   **wholesale corpus regen** (needs a live plugin CLI; not runnable in this
>   container) — it closes the deferred **corpus-side** remediation backlog (16
>   COV02 orphans, CORPUS-REFGRAN-RECASCADE, CORPUS-PRD-TH-RES). The **P3 docs
>   sweep** (spec 0.32.6) shipped three template stragglers: `INDEX-UPSTREAM-RESIDUE`
>   (5 stale `Upstream:` lines in the index templates → necessary-upstream —
>   template-side, NOT a regen item), `ENG-PLATFORM-ADR-TIMING` (platform ADR-timing
>   wording + PRD platform-flow exception), `D54-F12-AGENTIC-ANTIPATTERNS` (agentic
>   FAIL/PASS pairs in BRD/PRD antipatterns).
>
> **▶ RESUME HERE — next session:**
>
> 1. **Run the corpus regen** (`plans/CORPUS-REGEN-RUNBOOK.md`) on a live plugin
>    CLI — the corpus lags spec `0.29.x → 0.32.6`. Closes the 3 corpus-side
>    remediation items (16 COV02 orphans, CORPUS-REFGRAN-RECASCADE, CORPUS-PRD-TH-RES).
> 2. **Remaining P3/P2 items** (all `OPEN` in FRAMEWORK-TODO): `D54-F04` (EARS-Ready
>    non-latency rubric — playbook work, not a trivial clarification), plus the P2s
>    (`IPLAN-LANG-001`, `D54-F06/F13/F05/F07`, `ENG-STALE-DEPTH-DOCS`,
>    `BL-REF-GRANULARITY`, `BL-STATUS-SCOPE`).
> 3. **New follow-ons logged this session:** `SKETCH-FILE-STANDALONE` (standalone
>    Sketch-file lint support), `LINT-DOCID-HEADER-FALSE-POSITIVE` (`_DOC_ID`
>    flags `<TYPE>-<word>` header/link tokens).
> 4. **Hermes parity** — still the one large outstanding arc (`HERMES-BACKLOG.md`).
>
> **Merge-flow:** every PR here needs `--admin` (composition-CI gap,
> `AIDOC-CI-COMPOSITION-CHECK-PRHEAD`) — founder standing OK for this arc.
>
> ---
>
> **🟢 FOLLOW-UP SESSION COMPLETE (2026-06-29, post-P1-wave) — loose end closed;
> `main` clean at framework `0.32.3` / plugin `0.23.0`; no open PRs; nothing in
> flight.** Reviewed and **deleted** the dangling `feat/cfb-pr-1a-trace-contract`
> branch (fully superseded by #180 — detail in the "Loose end RESOLVED" note
> below) and recorded the closure via **#219** (admin-merged; see CI finding
> next). **The ▶ RESUME HERE list below is UNCHANGED and remains the
> next-session start point — begin with Hermes parity.**
>
> **⚠️ CI finding — merge-flow gotcha** (now tracked as
> `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` in `FRAMEWORK-TODO.md`): the
> branch-protection-required **`call / composition`** check is **structurally
> unsatisfiable on a PR head** in this repo. `ai-review.yml` runs on
> `pull_request_target` (run `head_sha` = base = main HEAD), so the
> `workflow_run`-triggered `composition.yml` posts `call / composition` to main's
> HEAD, never to the PR's head commit. Every PR's combined status stays `pending`
> on that context → the OPS-0062 green-path `gh pr merge` is `BLOCKED` and the PR
> must be closed via `--admin` (as both #218 and #219 were). **`skip-ai-review`
> label-cycling does NOT fix it.** Fix locus is the **aidoc-flow-ci** composition
> reusable (post to the `workflow_run` PR-head SHA) — cross-repo, track upstream.
> Next session: expect to admin-merge AI-opened PRs here until that lands.
>
> ---
>
> **🟢 SESSION COMPLETE (2026-06-29) — CONSUMER-FEEDBACK P1 wave shipped + P3
> docs cleared. `main` clean; framework spec `0.32.3`, plugin `0.23.0`. No open
> PRs; nothing in flight.**
>
> **Shipped this session (10 PRs; framework spec `0.29.0 → 0.32.3`):** PR-3b
> (#206, 0.29.1) · ELEMENT-COVERAGE-001 (#209, 0.30.0) · tooling backlog (#210) ·
> PROVISIONAL-IDS-001 (#212, 0.31.0) · REUSE-MANIFEST-001 (#214, 0.32.0) ·
> SPEC/IPLAN ID-exemption note (#215, 0.32.1) · IPLAN registry-schema note (#216,
> 0.32.2) · BeeLocal docs sweep (#217, 0.32.3) · framework ci/v1.4.2 pin (#207) ·
> aidoc-flow-ci #46 (ci/v1.4.2). Plus 3 plan PRs (#208/#211/#213) and
> **D-0039/40/41**. The whole CONSUMER-FEEDBACK P1 wave (coverage engine /
> provisional IDs / reuse) is delivered; the P3 docs backlog is essentially clear.
>
> **Per-arc detail (this session's work) below; the ▶ RESUME HERE list is the
> next-session start point.**
>
> **REUSE-MANIFEST-001** (plan #213 merged → impl): satisfied-by-reference —
> `reuse: {state: referenced, target: <doc_id|path>@<commit>}` frontmatter
> exempts a referenced doc's elements from COV01/COV02 (reused as-is) + a
> `REUSE01` advisory per referenced doc (dedicated `_check_reuse`, all layers);
> `REUSE02` in-repo-pinned-target contract (URLs → @discoverability only);
> full-prefix rule (upstream lineage also in-repo+referenced → `@`-tags resolve,
> no trace change). D-0041. 3-pass converged; 314 green; corpus baseline
> unchanged. **NEXT:** CONSUMER-FEEDBACK later waves (D54-F06 IPLAN
> project-types, the Engramory/BeeLocal items); reuse follow-ons
> (REUSE-MANIFEST-002 element-granular; audit-skill no-free-≥90 enforcement).
>
> **PROVISIONAL-IDS-001** (plan #211 → #212 merged): manual-mode provisional IDs
> — `id_state` flag + `PROV01`; `0000` template literal; `PH01`
> `(?<!\.)\bx{3,}\b`; normative SHA-256 in `ID_NAMING_STANDARDS.md` (D-0040).
> **`rehash` (PROVISIONAL-IDS-002) DISCARDED** — premise broken (IDs are
> LLM-generated, not deterministic; see [[project-element-ids-not-deterministic]]).
>
> **ELEMENT-COVERAGE-001** (plan #208 merged → #209 merged): COV01/COV02 now bind
> at **element level** via a curated one-hop `REALIZING_LAYERS` map
> (BDD→{SPEC,TDD}, EARS→{BDD,SPEC,TDD}, BRD-FR→{PRD}; ADR excluded — D-0039).
> COV02 surfaces the **16 orphaned BDD scenarios**; COV01 0 new corpus findings.
> (Orphan remediation deferred to corpus regeneration — see
> [[project-examples-regenerated-wholesale]].)
>
> Design-of-record **`plans/YAML-BDD-SCHEMA-PLAN.md`** (PR #197, D-0038, 3-pass
> converged) → migrate BDD off Gherkin-in-markdown to a structured **YAML
> `scenarios:` block inside `BDD-NN.md`**. The whole loop is now closed: spec
> describes it (PR-3 template+GD-03+TAG_SYNTAX), linter reads it (PR-2 dual-mode),
> transcoder + `doc-bdd*` skills produce it (PR-1/PR-5), corpus is it (PR-4
> BDD-01). The Gherkin/GD-03 tag collision (the CFB-PR-3 26-element fan-out) is
> dissolved at the root; IDs stable (16 downstream `@bdd:` resolve); coverage now
> element-precise. **Merged:** #198 (PR-1) · #200 (PR-2) · #201 (PR-3, spec-tier
> 0.29.0) · #202 (PR-4) · #203 (PR-5, plugin 0.23.0). (Note: GD-04 #199 landed
> 0.28.0 mid-arc → PR-3 re-bumped to 0.29.0.)
>
> **▶ RESUME HERE — next session, priority order:**
>
> 1. **Hermes parity** — the one large outstanding arc. Hermes lags the plugin
>    on the recent spec: element-level COV01/COV02 (D-0039), YAML-BDD scenarios,
>    provisional IDs (D-0040), reuse/satisfied-by-reference (D-0041). Plugin-first
>    sequencing held it until the framework settled; the framework has now had a
>    big run (`0.29.0 → 0.32.3`), so it's ripe. Tracked in
>    `plans/HERMES-BACKLOG.md`. **Multi-step — start fresh with full context;**
>    plan → 2-cycle review → impl per the workflow.
> 2. **`BL-READY-SCORE-ADVISORY`** (`FRAMEWORK-TODO.md`, P3) — mark the
>    `*_ready_score` / `target_score` fields explicitly advisory across **all
>    ADR/SPEC/TDD templates (~52 occurrences)** so a blank value doesn't read as
>    incomplete. A template sweep (one PR), NOT small. Author Q4: mark-advisory,
>    do NOT build a rubric.
> 3. **`ENG-BRD-SKETCH-ROADMAP`** (`FRAMEWORK-TODO.md`, design item) — a BRD
>    "sketch" sub-form + project-init roadmap. Plan-worthy (new sub-form).
> 4. **Remaining small docs/template items** in `FRAMEWORK-TODO.md` (the D54/ENG/BL
>    P3 stragglers); and **corpus regeneration** when ready — the example corpus is
>    recreated wholesale (see [[project-examples-regenerated-wholesale]]), which
>    retires the deferred corpus-remediation items (16 COV02 orphans,
>    CORPUS-REFGRAN-RECASCADE, CORPUS-PRD-TH-RES, INDEX-UPSTREAM-RESIDUE).
>
> **Loose end RESOLVED (2026-06-29):** branch `feat/cfb-pr-1a-trace-contract`
> (commit `a770c4fb`) reviewed and **deleted (local + origin)** — fully
> superseded. Every correction it carried (TRACEABILITY.md necessary-upstream
> heading/per-layer list/validation table, GATE-08-E003 resolution,
> governance/README.md wording) already lives on `main` via #180's
> cumulative→necessary-upstream reconciliation, and `main` goes further
> (CFB-PR-2 coverage-matrix paragraph; richer GATE-08-E003 transitive-reach
> note). Reviving it would have regressed the docs.
>
> **Coverage engine map** (the session's core surface — for the Hermes port +
> any coverage follow-on): `tools/sdd_doc_lint/__init__.py` —
> `_check_forward_coverage`/`_check_backward_coverage` (COV01/COV02, element-level
> via `REALIZING_LAYERS` + `_element_realizing_citers`), `_check_reuse`
> (REUSE01/02), `_reuse_map`, `_check_bdd_schema`, `build_edge_graph`,
> `_PLACEHOLDERS` (PROV/PH01), `_extract_frontmatter` (`id_state`/`reuse`).
> Decisions: **D-0039** (element coverage), **D-0040** (provisional IDs),
> **D-0041** (reuse). Don't re-attempt `rehash` — premise broken
> ([[project-element-ids-not-deterministic]]).
>
> ---
>
> **Per-PR detail of the shipped arc (PR-1…PR-5) — historical:**
>
> 1. ✅ **PR-1 (SHIPPED this session) — `_THRESHOLD` fix + transcoder.** The two
>    self-contained, fully-verified pieces:
>    (a) `_THRESHOLD` regex tightened to `([^\s|'"]+)` so an inline `@threshold:`
>    ending a quoted YAML scalar doesn't false-fire TH01 (Pass-2 LB-1; all-layer,
>    regression-free — verified zero quote-adjacent thresholds in the corpus).
>    Vendored byte-identical to both platform copies. `tests/unit/test_threshold_quoted_scalar.py`.
>    (b) `tools/gherkin_to_bdd_yaml.py` transcoder — parses the corpus's Gherkin
>    constructs (feature/background/outline/examples/multi-step/inline-threshold/
>    comments) and copies each `@scenario-id:` **verbatim** into `id:` (keeps the
>    16 downstream `@bdd:` citations stable). `tests/unit/test_gherkin_to_bdd_yaml.py`.
>    Suite green: 130 unit + 148 conformance; corpus == baseline.
> 2. ✅ **PR-2 (SHIPPED this session) — `sdd_doc_lint` dual-mode BDD parse path.**
>    `build_edge_graph` synthesises verbatim `ears` edges (doc-form included →
>    REFGRAN fires; `cited_doc = doc_id_from_token`); TRACE-RES-001 + TAG01 read
>    scenario `ears`; new `BDD-SCHEMA-001` structural-only check (no double-report
>    with REFGRAN); legacy Gherkin docs fall back to the `@`-tag path. Re-vendored
>    byte-identical. `tests/unit/test_bdd_yaml_mode.py` (11); legacy fixtures
>    supplemented not replaced (Pass-3 finding 1). 141 unit + 148 conformance;
>    corpus == baseline; end-to-end smoke (transcoder → fork) on the real BDD-01.
> 3. ✅ **PR-3 (SHIPPED this session) — BDD template + schema; spec 0.27.0 →
>    0.29.0 (re-bumped from 0.28.0 after a version collision with GD-04 #199).** `BDD-TEMPLATE.yaml` category-dict → flat `scenarios:` list +
>    `type:` discriminator + `feature:` YAML block (no `ears`, D-3) +
>    `document_control` drops reference rows; `BDD-00_index.TEMPLATE.md` →
>    structured `ears:`/YAML schema; governance reconciled (`TAG_SYNTAX.md` BDD
>    rows + GD-03 "BDD carrier" clause). **GATE-SPEC forced the MINOR bump into
>    this PR** (E005) — `bump_version.py` did FSV pins + 104 frontmatter + bundle
>    re-vendor + version fanout. 148 conformance + 141 unit; corpus == baseline;
>    spec_gate green. **Spec-tier → human sign-off (no auto-merge).** This
>    absorbs the plan's old PR-7 (standalone bump).
> 3b. **PR-3b (NEXT, PATCH bump) — deferred governance polish:** `QUICK_REFERENCE.md`
>    - the `04_BDD/*.md` playbook **bodies** (Gherkin → YAML scenario references;
>    PR-3 only bumped their version frontmatter, not content). framework/ change →
>    needs its own PATCH bump (0.29.0 → 0.29.1).
> 4. ✅ **PR-4 (SHIPPED this session) — corpus BDD-01 migrated to YAML.** The
>    transcoder (hardened: fence-classified placement + doc-control row strip +
>    empty-subheading collapse) converted `examples/.../04_BDD/BDD-01.md` (31
>    scenarios, ids verbatim → all 16 downstream `@bdd:` resolve, V4). **Corpus
>    REFGRAN 7 → 5** (2 BDD edges gone; the 5 SPEC/TDD/IPLAN `@adr`/`@tdd` remain
>    = `CORPUS-REFGRAN-RECASCADE`). The 7 `BDD-01_golden` fixtures were already
>    non-Gherkin → no change. New corpus baseline: **1 TH-RES, 5 REFGRAN, 6 STY02**.
>    290 unit/conformance green; acceptance unchanged (3 pre-existing SPEC `@adr`
>    failures). Not framework/ → no bump.
> 5. ✅ **PR-5 (SHIPPED this session) — `doc-bdd*` skills author the YAML form.**
>    All four (`doc-bdd`/`-audit`/`-fixer`/`-autopilot`) rewritten off Gherkin
>    `@`-tags to the structured `scenarios:` YAML model (`ears:` list as
>    required-upstream; `BDD-SCHEMA-001`; `feature:` block no `ears`). 5-section
>    template-alignment contract preserved (content-only). Plugin MINOR
>    **0.22.0 → 0.23.0**; 148 conformance + plm_lint clean + 142 unit green.
> 6. **PR-6** governance docs (GD-03 note, `TAG_SYNTAX.md` BDD row,
>    `QUICK_REFERENCE`, 04_BDD playbooks).
> 7. ~~**PR-7** standalone version bump~~ — **ABSORBED into PR-3** (GATE-SPEC
>    forces the bump to ride with each framework/ change; PR-3 did 0.29.0, PR-3b
>    will do 0.28.1, PR-5/skills + any later framework/ change bump as needed).
>    Only `ROADMAP.md` may still want a closing note at the end of the arc.
>
> **How to resume:** read this banner + `plans/YAML-BDD-SCHEMA-PLAN.md` (D-1…D-6,
> the schema, the 5-function linter-fork contract, V1–V11). Linter lives in
> `tools/sdd_doc_lint/__init__.py`; transcoder/emitter go in `tools/`; tests in
> `tests/unit/`. Corpus baseline for the V11 cross-check (post-PR-4): 1× TH-RES-001, 5×
> REFGRAN01, 6× STY02 on `main`.
>
> **Note:** YAML-BDD resolves the **2 BDD** REFGRAN edges; the **5
> SPEC/TDD/IPLAN `@adr`/`@tdd`** edges remain `CORPUS-REFGRAN-RECASCADE`'s job
> (still open in `FRAMEWORK-TODO.md`).

---

> **🟢 CFB-PR-2 coverage engine — FULL ARC SHIPPED + MERGED (2026-06-27). `main`
> is clean at framework spec `0.27.0`.**
>
> Five PRs landed, each plan-reviewed (2-3 independent passes) + spec-tier
> human-signed:
> `COV01` forward gate (#187, 0.24.0) → `COV02` backward gate (#190, 0.25.0) →
> GD-03 ref-granularity policy (#192, 0.26.0) → PR-3 plan (#193) → **`REFGRAN01`
> enforcement (#194, 0.27.0)**. The engine computes the `@`-tag graph once and
> asserts forward (`COV01`: BRD FR → SPEC/IPLAN) + backward (`COV02`: EARS/BDD →
> SPEC/TDD) coverage, doc-level, and enforces element-granular refs (`REFGRAN01`,
> GD-03). All backed by normative spec (BRD `_authored_form` rule, SPEC-00
> `coverage` section, GD-03 + `governance/TAG_SYNTAX.md`).
>
> **▶ RESUME HERE — next session, priority order:**
>
> 1. **`CORPUS-REFGRAN-RECASCADE`** (`FRAMEWORK-TODO.md`) — re-cascade the **7**
>    doc-level corpus tags to element-level (5 drop + 2 convert, incl. the
>    BDD-01 Feature `@ears` fan-out to its 26 scenarios). Blocked on the
>    `doc-<layer>-fixer` skills (not invocable in a framework-dev session) →
>    **either** run them in a live plugin session **or** add a `REFGRAN --fix`
>    mechanical auto-fixer (drop-redundant + fan-out are deterministic). Until
>    then `REFGRAN01` is warnings-only in `build` (does not raise the exit code).
>    Closing this gets the corpus gate-code-clean (plan V7).
> 2. **Element-level `COV01`/`COV02` upgrade** — the *payoff*: now that refs are
>    element-precise (REFGRAN01), upgrade the gates from doc-level to
>    element-level reach. This finally catches the **15 orphaned BDD scenarios**
>    `COV02` can't see at doc level. Needs the EARS/BDD deferral signal designed
>    (the doc-of-record: `CFB-PR-2-COVERAGE-ENGINE-PLAN.md` DD-5/DD-6 + the 2b
>    plan's deferral notes). A new plan → review → impl.
> 3. **`BL-STATUS-SCOPE` (PR-3b)** — per-context `status` enum + scope-aware
>    validation (resolve the PR-7 `Sketch` interaction). Split out of PR-3.
> 4. **Sub-PRs 2c** (phase reconciliation — registry phase-schema + phase-leak
>    gate, DD-6 row 4) and **2d** (BDD doc-set EARS roll-up). Plus the later
>    CONSUMER-FEEDBACK waves (PR-4 provisional IDs, PR-5 reuse manifest, …).
>
> **Tooling backlog** (`FRAMEWORK-TODO.md`): `BUMP-SKILL-AUTHORING-CHECKLIST-STRAGGLER`
> (recurs every bump), `SYNC-VERSION-PROVENANCE-OVERBUMP`,
> `RELEASE-CHANGELOG-TEST-CONVENTION-GAP`, `CORPUS-PRD-TH-RES` (pre-existing
> PRD-01 `@threshold:` gap — the corpus's only non-REFGRAN error).
>
> **How to resume:** read this banner + `plans/CFB-PR-2-COVERAGE-ENGINE-PLAN.md`
> (the design-of-record) + the relevant sub-PR plan; the engine lives in
> `tools/sdd_doc_lint/__init__.py` (`_check_forward_coverage` / `_check_backward_coverage`
> / `_check_ref_granularity` / `build_edge_graph`), tests in
> `tests/unit/test_{forward,backward}_coverage.py` + `test_ref_granularity.py`.

---

> **🟢 CONSUMER-FEEDBACK-001 — 3 consumer-feedback logs triaged → workstream underway (2026-06-27).**
>
> Triaged three downstream-project feedback logs (D54 / Engramory / BeeLocal)
> into **22 framework items** (`FRAMEWORK-TODO.md`, 3 dated banners), sequenced
> by the orchestration plan **`plans/CONSUMER-FEEDBACK-001-PLAN.md`** (12 child
> PRs in 4 waves). **Shipped this session:**
>
> - **PR-1 `BL-TAG-CHAIN-GATE-SYNC`** → grew into the full **cumulative→
>   necessary-upstream doc reconciliation** (~20 surfaces, incl. false
>   `required_tags` claims in EARS/BDD templates + GATE-03, and a live
>   author-facing bug in `AI_ASSISTANT_RULES.md`). Framework spec **0.23.1**.
>   Merged **#180** (`8e001192`); closed **#181** (`6aad56bf`).
>   Plan: `plans/CFB-PR-1-TAG-CHAIN-GATE-SYNC-PLAN.md`.
> - **`bump_version.py` fix** (#182, `e77a743a`): it silently skipped all 51
>   playbooks (regex required indentation; playbook frontmatter is column-0) →
>   every framework bump left conformance red. Now bumps playbooks +
>   SKILL_AUTHORING + plugin README; decouples plugin VERSION. A framework bump
>   now leaves **1** manual touch (the deliberate hard-pin tripwire) not 54.
> - **PR-2 coverage engine — design of record** merged **#184** (`58e27917`).
>   `plans/CFB-PR-2-COVERAGE-ENGINE-PLAN.md`, converged over **3 independent +
>   4 self** review passes (Pass-4/6 caught that the design assumed code/artifact
>   facts that don't hold — fixed; see its R-a…R-f "Implementation reality").
>
> **sub-PR 2a-core** (branch `feat/cfb-pr-2a-coverage-core`, pushed, no PR
> yet; rebased onto main `81c6f05e`, incl. #186 CI bump). Split: **2a-core** (engine) + **2a-ref**
> (PR-3 ref-granularity, separate). 2a-core build order:
>
> 1. ✅ **`sdd_trace_graph`** — shared @-tag primitives extracted from
>    `trace_walk.py` (DD-1 foundation); `test_sdd_trace_graph.py` (8 tests) +
>    `test_trace_walk` green. Commit `e3377ac6`. **Relocated in step 2** →
>    `tools/sdd_doc_lint/trace_graph.py` (package submodule).
> 2. ✅ **Bidirectional element edge-graph + heading-context FR scanner**
>    (DD-3, DD-1/R-c). *Decision (resolved):* the shared module **moved into
>    the `sdd_doc_lint` package** as `trace_graph.py`, so the **vendored**
>    copies import it via package-relative `from .trace_graph import …`
>    (carried by `sync-vendored.sh`; byte-identity drift-guard extended).
>    Shipped: `scan_fr_elements()`/`FRElement` (the `## … Functional
>    Requirements` heading + the `Acceptance criteria:` boundary classify gated
>    FRs; band token captured, parenthetical-wrap-tolerant) and
>    `build_edge_graph()`/`EdgeGraph`/`TraceEdge` (net-new upstream-citation
>    adjacency — `citers_of` / `citers_of_doc` / `citers_in_layer`; reuses the
>    shared primitives so forward/backward agree, multi-`@brd` per DD-8).
>    Grounded on the real corpus: all 4 BRD-01 §7 FRs classified (band P1), the
>    AC sub-block excluded, all 4 cited element-level by PRD-01; one-hop
>    necessary-upstream chain holds. `test_fr_scanner.py` (9) +
>    `test_edge_graph.py` (9); 208 unit+conformance green. Commits
>    `49614c3d` (relocate) → `5d742a72` (scanner) → `c518d347` (edge-graph).
> 3. ✅ **`covered_state` enum + band parser + escapes** (DD-2/DD-4/DD-5).
>    `CoveredState` (StrEnum: AUTHORED / DEFERRED / REALIZED_BY /
>    SATISFIED_BY_REFERENCE-stubbed), `parse_band()` (validates against the
>    `priority_definitions` mirror {P1,P2,Future}; `Future`=deferral),
>    `covered_state_of()` (realized_by → REALIZED_BY precedence; Future →
>    DEFERRED; else AUTHORED). New escape surface (none existed): a
>    `realized_by: <LAYER>` token on the FR bullet's first line, captured into
>    `FRElement.realized_by` (D-0037). Corpus: 4 BRD-01 FRs → AUTHORED.
>    `test_covered_state.py` (11); 221 green. Commit `546458a7`.
> 4. ✅ **Forward coverage gate + run-mode severity + CLI args** (DD-6/DD-9).
>    `_check_forward_coverage` (COV01): AUTHORED BRD FRs must reach ≥1 SPEC +
>    ≥1 IPLAN (doc-level reach from host BRD; PR-3 refines to element);
>    escapes never block. Severity: no-SPEC → error both modes; SPEC-but-no-
>    IPLAN → warning(build)/error(gate-code). Gated to corpora with SPEC+IPLAN
>    present (DD-1; no-ops on single-file + partial fixtures). New
>    `--mode {build|gate-code}` + `--skip-coverage-gate` args, threaded through
>    `lint_path(mode=, skip_coverage=)`. **Deferred** (element-granularity/2c):
>    DD-6 row 1 (escaped informational) + row 4 (phase leak). DD-9: corpus
>    findings byte-identical to main (0 COV01). `test_forward_coverage.py` (9);
>    231 green. Commit `54992250`.
> 5. ✅ **`tools/sdd_coverage.py` matrix emitter** (DD-7). Thin reporter over
>    the shared `build_edge_graph` core; emits a GENERATED, deterministic
>    `TRACEABILITY_MATRIX.md` (per gated FR: band, covered_state, reached
>    downstream layers). Generated the example matrix (4 BRD-01 FRs, all reach
>    SPEC+IPLAN); idempotent, 0 added linter findings, markdownlint clean.
>    `test_sdd_coverage.py` (6); 240 green. Commit `7ccd90ef`. **The
>    `framework/governance/TRACEABILITY.md` cross-ref moved to step 6** (lands
>    with the framework MINOR bump so the framework change is GATE-SPEC-grouped).
> 6. ✅ **Framework spec changes + MINOR bump 0.23.1 → 0.24.0** (DD-3/DD-4/DD-7).
>    One GATE-SPEC-compliant change: (a) `governance/TRACEABILITY.md` cross-ref
>    to the generated matrix + `trace_walk.py`; (b) `BRD-TEMPLATE.yaml`
>    normative `_authored_form` rule (band + `Acceptance criteria:` boundary +
>    `realized_by` escape); (c) `test_coverage_engine.py` (V5 matrix
>    regenerate-and-diff + COV01 contract + template-rule guard); (d) bump via
>    `bump_version.py` (104 FSV + both pins + re-vendor + version-ref fanout),
>    hard-pin → 0.24.0, CHANGELOG [Unreleased] entry. 248 green; versions
>    consistent; example corpus 0 COV01. Commit `0d27c819`.
>
> **🟢 2a-core COMPLETE — opening PR `feat/cfb-pr-2a-coverage-core` → main.**
> Forward-coverage engine shipped: shared trace primitives + bidirectional
> element edge-graph + heading-context FR scanner + `covered_state` classifier +
> the `COV01` forward gate (run-mode severity) + the `sdd_coverage.py` matrix
> emitter + the `TRACEABILITY.md` cross-ref + the BRD-template FR-annotation
> rule. Framework spec **0.24.0**. Document-level binding; **2a-ref / PR-3
> (element granularity)** is the co-dependent follow-on (refines reach +
> enables DD-6 row 1/4 = escaped-informational + phase-leak). Sub-PRs 2b
> (backward GATE-06), 2c (phase reconciliation), 2d (BDD roll-up) remain per
> `plans/CFB-PR-2-COVERAGE-ENGINE-PLAN.md`. **2a-core merged `48d501d6` (PR #187).**
>
> **🟢 sub-PR 2b (backward leg) IMPLEMENTED → PR open.** Plan PR #189 merged
> (`a446d512`). Shipped on `feat/cfb-pr-2b-backward-leg`: backward coverage lint
> `COV02` (dual of `COV01`) — every EARS/BDD requirement doc must transitively
> reach a SPEC/TDD, else flagged (warning/`build`, error/`gate-code`); gated to a
> real (non-`-00`) SPEC/TDD present (the `-00` index signal, since SPEC/IPLAN
> declare no canonical elements); behind `--skip-coverage-gate`. + SPEC-00
> `## Coverage` section (the doc-of-record — `COV02` is a structural lint code,
> not a formal gate-catalog entry) + the SPEC-00 necessary-upstream `Upstream:`
> fix. **Framework spec `0.24.0 → 0.25.0`.** 260 green; corpus 0 COV01/0 COV02;
> vendored byte-identity intact. Doc-level binding; **element-level + the EARS/BDD
> deferral signal + the 15 orphaned BDD scenarios → PR-3.** Sub-PRs 2c (phase
> reconciliation), 2d (BDD roll-up) remain.
>
> **Pre-existing corpus issue surfaced in step 4 (NOT a CFB-PR-2 regression):**
> `TH-RES-001` errors on `examples/url-shortener/docs/02_PRD/PRD-01.md`
> (missing `component_decomposition`; 11 downstream `@threshold:` citations
> unresolvable) — confirmed identical under main's linter. Out of CFB-PR-2
> scope (threshold-resolution, CLEANUP-PR-D). Flag for corpus remediation via
> the framework fixer (never hand-edit the example artifact). Logged in
> `FRAMEWORK-TODO.md`.
>
> **Open follow-ups** (logged in `FRAMEWORK-TODO.md`): the cumulative-residue
> sweep missed the stale `Upstream:` enumerations in layer index templates /
> READMEs (e.g. `SPEC-00_index` "Upstream: BRD, PRD, EARS, BDD, ADR"). The
> `ai-review` CI keeps infra-failing on large diffs (your IPLAN-0024 stream) —
> manual review substitutes were posted on #174/#180.
>
> ---
>
> **🟢 IPLAN-0024 P4 — `ai-review.yml` pin `@ci/v1.1.3` → `@ci/v1.1.5` (2026-06-27).**
>
> Consumes the curl-replaces-`actions/checkout` fix shipped on
> aidoc-flow-ci main (PR #36) and validated on operations P3 (PR #148
> merged earlier this session — all 9 checks green including ai-review
> on operations' self-hosted runners). **This PR is the CRITICAL test**:
> framework runs on `ubuntu-latest` (GitHub-hosted), the runner class
> where every v1.1.0→v1.1.3 sparse-checkout iteration failed. If ai-
> review fires cleanly post-merge using v1.1.5 here, IPLAN-0024 closes
> successfully. Chicken-and-egg: BASE main pins v1.1.3 → ai-review on
> this PR fires using the still-buggy v1.1.3 workflow; ship via
> `skip-ai-review` label + admin-merge. Operations carries IPLAN-0024
> primary tracking (`ops/iplans/IPLAN-0024_template-pattern.md`).
>
> **🟢 SAGA-PARITY-001 PHASE 4 SHIPPED + CI RESTORED (2026-06-22).**
>
> **Phase 4 merged** — PR #161, merge `f277ea1a`, plugin `0.20.1 → 0.21.0`.
> All 6 layer autopilots (`ears/bdd/adr/spec/tdd/iplan`) migrated from the
> legacy in-session loop to the saga-driver shape; `review_mode` added to 7
> `adapts:`; new `test_autopilot_saga_parity.py`; an independent diff review
> caught + fixed a Step-3 dangling cross-ref before merge. All 8 layer
> autopilots are now uniform. (Closed entry in `FRAMEWORK-TODO.md`.)
>
> **CI outage root-caused + fixed (the real story).** Every workflow had been
> `startup_failure`-ing at `0s` on all branches. It was **NOT billing** (the
> long detour through budget pages was a misdiagnosis on my part). The actual
> cause: the repo's **Actions permissions policy was `local_only`**, which
> blocks *all* non-owner actions — including `actions/checkout`,
> `actions/setup-python`, `github/codeql-action`. Fixed via API to
> `allowed_actions: selected` + `github_owned_allowed: true` (GitHub-owned
> actions allowed; third-party still blocked). CI immediately went green; #161
> was merged via the `enforce_admins` toggle *during* the outage, #162
> (Dependabot checkout 6→7) merged via the **normal path** after the fix —
> proving the workaround is no longer needed. **Lesson:** a `startup_failure`
> at `0s` across *all* workflows ⇒ check `gh api repos/<r>/actions/permissions`
> (`local_only`?) BEFORE billing.
>
> **NEXT (priority order):**
>
> 1. ✅ **MODEL-PRECHECK-ROLLOUT** — **SHIPPED** (PR #164, merge `6700301f`,
>    plugin `0.22.0`). All 8 autopilots print the per-layer model recommendation
>    (D-0035, autopilots-only). Closed in `FRAMEWORK-TODO.md`.
> 2. **P2 plugin deploy-verification** — `plans/PLUGIN-P2-DEPLOY-RUNBOOK.md`;
>    needs the user's local Claude Code CLI (live skill run proving
>    `${CLAUDE_PLUGIN_ROOT}` resolves in SKILL prose). Flips the plugin from
>    "release-ready" to "deploy-verified".
> 3. **Hermes parity** — ROADMAP "Now" item; Hermes lags the plugin.
>
> **Plugin state:** `0.22.0`, release-ready (conformance green, `plm_lint`
> clean, BYO-marketplace installable). **Release tag lags:**
> `claude-code-plugin/v0.20.1` is the latest pushed tag — push `v0.21.0` and
> `v0.22.0` from a local clone (tag pushes are a local-clone action). Not yet
> deploy-verified (item 2).
>
> **Phase 4 plan (historical detail): `plans/SAGA-PARITY-001-PHASE-4-PLAN.md` — CONVERGED (Pass 1-3), IMPLEMENTED.**
> Scope: rewrite the 6 legacy `## Workflow` sections to the proven
> `doc-prd-autopilot` two-subsection shape (team saga loop + single_pass
> fallback verbatim); add `review_mode` to the `adapts:` frontmatter of the 6
>
> - reconcile `doc-prd-autopilot` (Pass-2 R6.1 — they branch on `review_mode`
> but only brd declared it); + a conformance test asserting all 8 carry the
> saga block AND `review_mode` in `adapts:`. Plugin MINOR `0.20.1 → 0.21.0`;
> no spec change. Pass 2 (independent subagent) verified R1 no-detail-loss,
> R2 thresholds/index files, driver 8-layer support — all clean; folded the
> R6.1 adapts gap + R3 (PRD is byte-source, not brd) + R6.4 (version-sync also
> touches frontmatter). Source→target table, 12-row claim ledger, V1-V7+V4b in
> the plan.
>
> **NEXT SESSION — exact next steps:**
>
> 1. Open the **plan PR** (plan-only; plan is review-converged) → merge.
>    (Do NOT implement before the plan PR merges — repo workflow gate.)
> 2. **Implement** (Tasks 1-3): test-first conformance test → restructure 6
>    SKILLs + add `review_mode` to 7 `adapts:` lines → VERSION bump + docs.
>    Verify V1-V7 + V4b.
> 3. After merge, resume **MODEL-PRECHECK-ROLLOUT** against the uniform corpus.
> 4. (Independent of the above) the user can run the **P2 deploy runbook** on
>    their CLI anytime to deploy-verify the plugin.
>
> *Optional cleanup noticed:* `CLAUDE.md:19` could be tightened to
> "driver supports all 8 layers; 2 of 8 layer autopilots wired (Phase 4
> propagates the rest)" — minor, not blocking.

---

> **🟢 PLUGIN MARKETPLACE PRE-PUBLISH DOC-POLISH — 2026-06-15.** Three
> doc-only fixes prior to publishing `claude-code-plugin/v0.20.1` to the
> marketplace, discovered during a marketplace-readiness review.
> (1) `.claude-plugin/marketplace.json` description: "1 command" →
> "12 commands"; (2) plugin README "What's inside" enumerates the
> 2 deprecated-stub skills (`doc-review`, `trace-check`) in a dedicated
> row; (3) README "Framework spec conformance" section reworded to
> remove the incorrect claim that the bundle ships its own
> `framework/VERSION` (the bundle deliberately omits it per D-0022).
> No plugin VERSION bump; 129/129 conformance unchanged. Branch
> `docs/plugin-marketplace-polish`.

---

> **🟢 ACCEPTANCE-FIXTURES-DRIFT IMPL READY FOR PR — 2026-06-14.** Closes
> 12 long-standing deterministic-suite failures that were red on the
> umbrella `PR Checks` workflow since 2026-06-02. Three coordinated
> fixes: harness `template_sections()` honors `_required: false` +
> `_required_when_subtype: [list]`; fullpath upstream goldens gain
> the cited element IDs + `doc_id` for YAML goldens; per-layer fixture
> dirs gain 28 upstream sibling copies. Verification: 58 deterministic
> tests pass (was 43 passing + 12 failing); 129/129 conformance
> unchanged. Branch `feat/acceptance-fixtures-drift`. Plan PR #147 merged.

<!-- archive section below -->

> **🟢 PLATFORM README VERSION-CELL DRIFT FIX (PATCH) — 2026-06-14.** Plugin
> `0.20.0 → 0.20.1`. Root-cause fix for a long-standing drift bug in
> `platforms/claude-code-plugin/README.md` Platform info table — the
> `Version` cell had been stuck at `0.6.3` since plugin v0.7.0 (~14 bumps
> ago) because `scripts/sync-version-refs.sh` only awk'd bare `^X.Y.Z$`
> lines, missing inline table cells. Canonicalized cell to the tag form
> `claude-code-plugin/v<X.Y.Z>` and extended the sync script to propagate
> the tag form in platform READMEs. Same drift exists in
> `platforms/hermes/README.md` — flagged in `FRAMEWORK-TODO.md`
> (`HERMES-README-VERSION-DRIFT`) for Hermes's next bump. Branch
> `fix/plugin-readme-version-sync`.
>
> **Previously resolved (one-line summary):** Plugin `0.19.0 → 0.20.0`
> shipped (PR #144) — `/aidoc-flow:bug-report` and `/aidoc-flow:feedback`
> now accept a user prompt argument and have the LLM draft a complete
> GitHub issue from it. Plugin `0.18.0 → 0.19.0` shipped (PR #142 plan +
> PR #143 impl) — 11 user-facing commands.
>
> **Previously resolved (one-line summary):** PLUGIN-USER-COMMANDS shipped
> `0.18.0 → 0.19.0` (PR #142 plan + PR #143 impl): 11 user-facing commands
> across meta/workflow/lifecycle/config, optional
> `.claude/aidoc-flow.config.yaml` with `docs/CONFIG.md` schema,
> `feedback.md` issue template, 9-assertion conformance test, D-0033 a/b/c.
> NECESSARY-UPSTREAM-001 (spec `0.15.2 → 0.16.0`, plugin
> `0.11.0 → 0.12.0`) shipped on the necessary-upstream +
> transitive-reachability trace contract; details below for archive.

<!-- archive section below -->

> **🟢 NECESSARY-UPSTREAM-001 READY FOR PR — 2026-06-09.** Framework spec
> `0.15.2 → 0.16.0` (MINOR) + Claude Code plugin `0.11.0 → 0.12.0` (MINOR).
> Branch `feat/necessary-upstream-001` at `/opt/data/aidoc-flow/framework-necessary-upstream-001/`,
> 6 commits ahead of `origin/main` (rebased), all conformance + unit tests
> green (120/120 + 40/40, 1 skip each).
>
> **Shipped:** replaces the cumulative-trace dependency contract — every
> downstream layer redeclaring every preceding layer in `required_tags` —
> with **necessary upstream + transitive reachability**: each layer
> declares only what its own evaluation reads; lineage to layers further
> upstream is discoverable transitively via the @-tag chain (one hop per
> layer) and via the new `tools/trace_walk.py`. New `sdd_doc_lint TRACE-RES-001`
> rule provides deterministic structural-floor enforcement at every layer
> regardless of crew shape. 15 plugin SKILLs aligned with the new contract;
> acceptance-harness validator probe updated.
>
> **Plan review discipline:** 4 full Pass cycles before opening (Pass 1
> 12 gaps / Pass 2 6 gaps / Pass 3 7 gaps / Pass 4 3 minor → CONVERGENCE)
> per CLAUDE.md §"Development workflow" item 2.
>
> **Paused work blocked by this PR:**
>
> - **TDD-RT-001** (worktree at `/opt/data/aidoc-flow/framework-tdd-rt-001/`,
>   branch `feat/tdd-rt-001`, 5 commits ahead of main) — rebase after merge.
>   Per plan Task 9: the TDD-RT-001 framework version-bump commit
>   (`0.15.1 → 0.15.2`) conflicts with this PR's `0.15.2 → 0.16.0`; drop the
>   old bump and re-bump `0.16.0 → 0.16.1` PATCH for the 6 added TDD
>   playbooks. `doc-tdd-audit/SKILL.md` + `doc-tdd-fixer/SKILL.md` (added in
>   TDD-RT-001) will need their own cumulative-tag scrub during rebase
>   following the pattern in commit 43229908.
> - **IPLAN-RT-001** (task #268, no branch yet) — authors IPLAN playbooks
>   to the new contract from the start.
>
> **Next steps:**
>
> 1. Open PR for NECESSARY-UPSTREAM-001.
> 2. After merge, in feat/tdd-rt-001 worktree: fetch + rebase; resolve
>    version-bump conflict; cumulative-tag scrub `doc-tdd-audit` + `doc-tdd-fixer`;
>    re-run live TDD cascade per plan Task 9 (expected: TDD-01 drafted with
>    `upstream_artifacts: [EARS-01, BDD-01, ADR-01, SPEC-01]`, no `@prd`/`@brd`
>    cumulative tags, iter-1 PASS, content_score ≥ 90).
> 3. After TDD-RT-001 lands, kick off IPLAN-RT-001.
>
> ---
>
> **PLANSTD-001 IMPLEMENTED — 2026-06-09.** Framework spec
> `0.14.3 → 0.15.0` (MINOR). Plan PR #114 (plan-only) merged; this is the
> follow-on impl. Shipped: `framework/layers/08_IPLAN/PLAN_STANDARD.md`
> (new normative, engine-agnostic spec doc — unified development/work plan
> standard with an applicability matrix over `feature`/`bugfix`/
> `documentation`/`refactor`/`chore` + `[REQUIRED]`/`[CODE]`/`[IF APPLICABLE]`
> section tags); `plans/PLAN-TEMPLATE.md` rewritten to conform; IPLAN
> `README.md` cross-linked (third, orthogonal concept vs the Permanent +
> Temporary YAML IPLANs — neither changes). Plugin framework bundle
> re-vendored byte-identical; both `FRAMEWORK_SPEC_VERSION` pointers re-matched
> to `0.15.0`; **plugin (`0.10.1`) + Hermes (`0.3.0`) product versions
> unchanged** (independent streams). **Two pre-PR review gaps caught and
> fixed in-impl** (not in the merged plan): (1) hand-edited the hardcoded
> spec-version literal at `tests/conformance/platforms/test_plugin_release_metadata.py:140`
> (`0.14.3 → 0.15.0`) — not auto-synced by any hook; (2) ran
> `sync-version-refs.sh` **before** `sync-plugin-framework.sh` so canonical
> playbook frontmatter propagated before vendoring (byte-identity). A third,
> surfaced by V1: `sync-version-refs.sh` does not rewrite the plugin README's
> `$ cat FRAMEWORK_SPEC_VERSION` block / "Conforms to" lines — updated by hand
> (`platforms/claude-code-plugin/README.md`). Conformance: 118 pass / 1 skip.
> **Decision:** D-0032 (`plans/DECISIONS.md`). Built off `origin/main`
> (`feat/planstd-001-impl`), the 4-commits-ahead base — not the stale PR #114
> head branch.
>
> **Pre-existing drift noted, left untouched (out of scope):**
> `platforms/claude-code-plugin/README.md` "Version | `0.6.3`" table cell and
> CLAUDE.md "Current state" plugin-version line are stale vs the actual plugin
> product version (`0.10.1`); the `sync-version-refs.sh` awk only updates the
> bare `$ cat VERSION` line and `claude-code-plugin/v<X>` refs, not these prose
> cells. Not caused by this change; not conformance-tested.
>
> **🟢 PLUGIN BRD LAYER COMPLETE — 2026-06-06.** Framework spec `0.13.0` /
> plugin `0.6.2` / project `v1.1.0`. The plugin's BRD-layer machinery is
> shipped and end-to-end verified. **Five PRs landed this session:**
> #92 (plugin v0.6.1 — SAGA-PARITY-001 Phase 2 Amendment 1: preemptive
> `tools/saga_driver.py` replaces cooperative-enforcement SKILL prompts;
> 7 in-flight bugs B1-B7 fixed on the same branch); #93 (CLAUDE.md
> "Minimal-and-realistic plans" durable convention); #95 (plan PR for
> REVIEW-CALIBRATION-001); #96 (plugin v0.6.2 — 5 content sub-checks
> across 8 audit SKILLs; verified end-to-end against a saved
> before-fix BRD-01); #97 (plugin-first development-sequencing policy
>
> - `plans/HERMES-BACKLOG.md`).
>
> **Three new auto-memory entries** (in
> `~/.claude/projects/-opt-data-aidoc-flow/memory/`):
> `feedback-skill-drift-under-preemptive-driver`,
> `feedback-plans-minimal-and-realistic`,
> `feedback-plugin-first-then-hermes`.
>
> **Plugin BRD layer is the testbed** — saga driver + sub-checks both
> verified by the url-shortener acceptance cascade. The 5 sub-checks
> already shipped to PRD..IPLAN audit SKILLs (same wording, generic
> section concepts); only the autopilot SKILLs for those 7 layers
> still need the saga-driver dispatch pattern.
>
> **Hermes work explicitly deferred** —
> [`HERMES-BACKLOG.md`](HERMES-BACKLOG.md) is the single source of
> truth for what Hermes needs to catch up on (currently H-1
> SAGA-PARITY-001 Phase 3 G-R1 invariant; H-2 REVIEW-CALIBRATION-001
> lens sub-checks). Hermes-side iteration batches later.
>
> **Natural next item:** SAGA-PARITY-001 Phase 4 — propagate the saga
> driver from BRD to PRD..IPLAN (7 layer `doc-*-autopilot` SKILLs need
> the same slim-and-dispatch pattern Amendment 1 brought to
> `doc-brd-autopilot`).
>
> **Local branches remaining** (no remote): `plan/prd-rt-001-team-mode`
> (older draft); `plan/saga-parity-001-phase-3` (predates Amendment 1,
> needs refresh per HERMES-BACKLOG H-1 — do not open as-is).
>
> ---
>
> **🟢 CONSOLIDATION REVIEW FIXES — 2026-05-27.** A code review of the 55→50
> consolidation (3 finder passes) caught a real **correctness regression** and
> some capability flattening; all fixed on `claude/multi-platform-migration-AamWB`.
> **#1 (correctness):** `doc-validator` lost `trace-check`'s `adapts: [active_layers]`
> → on adapted projects it would false-fail disabled-layer traceability; restored
> `adapts` + an `## Adaptation` consult-clause. **Capability restore:** put the
> folded procedural detail back — `doc-flow` regained the intent-keyword→skill map,
> status-taxonomy position scan + progress %, P0/P1/P2 prioritization over the
> critical path, and upstream-ranking/vocabulary context scan; `doc-validator`
> regained `auto_fix` safety (backup/rollback/no-placeholder) and the four-class
> prose review (DATA/REF/TYPO/TERM + dictionary). **Refs:** `code-reviewer.md` no
> longer routes the code/PR dimension to `doc-validator` (reviews code natively;
> `doc-validator` only for spec/traceability). **Polish:** trimmed `doc-validator`
> description, distinguished `doc-flow`'s two routing sections (by-layer vs
> by-action), stamped `last_updated`. Cross-file consistency pass found **0**
> dangling refs / count mismatches. Conformance 66 green; pre-commit clean. The
> mechanical consolidation (counts/repoints/deletions) was already sound.
>
> **🟢 PLUGIN SKILL CONSOLIDATION — 55 → 50, redundancy audit (2026-05-27).**
> Branch **`claude/multi-platform-migration-AamWB`**. Audited the 55 plugin skills
> for redundancy; folded five overlapping utilities into two homes with **no
> capability lost**: `skill-recommender` + `workflow-optimizer` + `context-analyzer`
> → **`doc-flow`** (now does intent→skill mapping, position/next-step detection, and
> the pre-authoring context scan; `skill-recommender` also duplicated Claude Code's
> native skill dispatch); `trace-check` + `doc-review` → **`doc-validator`** (now
> covers bidirectional traceability + optional repair and prose review via
> `scope`/`auto_fix`). `doc-naming` kept as the ID authority; the 32 per-layer
> 4-variant skills untouched (deliberate granularity, per `docs/PARITY.md`).
> Repointed every cross-ref across skills/agents/README/`SKILL_AUTHORING.md`
> (~28 files), updated `plm_lint`'s set, counts (utilities 19→14, total 55→50), and
> the root `marketplace.json`. Plugin **`0.3.0 → 0.4.0`**; CHANGELOG `[0.4.0]`.
> **Verify:** 0 dangling refs; `plm_lint --all` clean; conformance 66 green;
> `pre-commit` all Passed. **User-only:** push tag `claude-code-plugin/v0.4.0`.
>
> **🔵 PLUGIN-MARKETPLACE P2 PREP — identity + mirror tooling (2026-05-27).**
> Branch **`claude/multi-platform-migration-AamWB`**. Did the in-container half of
> P2: **identity decided + applied** (D-0023 — one brand `aidoc-flow.com`,
> path-based per-integration pages `/claude-code` `/codex` `/vscode` `/hermes`;
> `.ai` reserved for agents/cloud; plugin `author`/`homepage` set, root
> `marketplace.json` counts/version fixed). Added a **`marketplace.json` validation
> gate** (`test_plugin_manifest.py`: owner + safe/resolvable sources; conformance
> **65 → 66**) and the **one-way mirror generator** `tools/build-plugin-mirror.sh`
> (refreshes the bundle, lays the plugin at mirror root with `source "."`, writes
> the `aidoc-flow.com`-owned marketplace.json; output to git-ignored `dist/`). Plan
> has a full **P2 execution runbook**. **All remaining P2 is user-only** (no CLI in
> sandbox; GitHub scope = monorepo; tag push 403s): stand up site+mailbox →
> `claude plugin validate` → live skill run (the R2 `${CLAUDE_PLUGIN_ROOT}`-in-prose
> check, against `examples/url-shortener/seed/`) → `/plugin install` smoke →
> ("tested/ready" true only after these) → create the mirror repo + push `dist/`
> tree → submit → push tag `claude-code-plugin/v0.3.0`. **One open input for the
> agent:** the GitHub **org/namespace** for the mirror.
>
> **🟢 PLUGIN-MARKETPLACE P1 DONE — plugin is self-contained + validated — 2026-05-27.**
> Branch **`claude/multi-platform-migration-AamWB`**. Plan:
> `plans/PLUGIN-MARKETPLACE-PLAN.md` (3 review passes + impl log). Made the Claude
> Code plugin **installable self-contained**: vendored a byte-identical copy of
> `framework/{layers,governance,registry}` + the SDD guide into
> `platforms/claude-code-plugin/framework/` (53 files) via the new
> `tools/sync-plugin-framework.sh`, and repointed **380 refs across 66 files** from
> `framework/…` (broke on install — Claude Code caches only the plugin dir) to
> `${CLAUDE_PLUGIN_ROOT}/framework/…`. Single source of truth stays the monorepo
> spec (**D-0022**, the vendoring exception to D-0013), enforced by a **drift-guard**
>
> - a **manifest/bundled-reference-resolution gate** (new
> `test_plugin_framework_bundle.py` + `test_plugin_manifest.py`; conformance **57 →
> 65**). `plugin.json` gained `$schema` + placeholder `author`; README rewritten
> (install-first + bundle section; 55 skills / 11 agents). Re-sync wired into
> `docs/PROJECT.md` §6 + a `spec_gate.py` reminder; bundle excluded from
> markdownlint/pre-commit (it inherits canonical `framework/`'s GATE-SPEC exemption,
> and no auto-fixer may break byte-identity). Plugin **`0.2.0 → 0.3.0`**; CHANGELOG
> `[0.3.0]`. **Verify:** sdd_doc_lint example chain clean; `plm_lint --all` clean;
> full conformance 65 green; ruff/format clean; `pre-commit run --files` all Passed.
> **KEY FINDING (carry to P2):** claude-code-guide confirmed `${CLAUDE_PLUGIN_ROOT}`
> auto-expands only in hooks/MCP/LSP/monitor `command` fields, **not** skill/agent
> body prose — so P1 delivers *self-containment* (files now ship at the anchor), but
> whether the running model resolves the variable in prose is the **P2 live-test**
> gate (fallbacks documented in plan R2). **P2 (user CLI, deferred):** `claude plugin
> validate` + live skill run + install smoke; then mirror repo + `marketplace.json` +
> identity + submission. **User-only:** push tag `claude-code-plugin/v0.3.0`.
>
> **🟢 AGENT-TEAM PHASE 3 COMPLETE — parity proof; ALL PHASES DONE — 2026-05-26.**
> Branch **`claude/multi-platform-migration-AamWB`**. Added the deterministic parity
> check: a shared unified-report schema
> (`tests/conformance/fixtures/review/review_report.schema.json`), sample report
> fixtures from **both** runners (`hermes_BRD-01_report.json`,
> `plugin_BRD-01_report.json`), and `tests/conformance/test_review_report_parity.py`
> (dependency-free validator: each fixture validates against the schema; the two share
> the report shape; `passed == structural_pass AND no_blocking`). Conformance **54 →
> 57**. `docs/PARITY.md` gains a review-team comparison + the parity proof (CI +
> documented **manual live-run** procedure, since live LLM output isn't
> CI-deterministic). **AGENT-TEAM Phases 0–3 are all complete** (spec → Hermes conform
> → plugin build → parity). Platform/test-only; no framework spec change.
> **Standing user-only carry-overs:** branch protection on `framework/**`; push
> `framework/v0.x` + `hermes/v0.x` + `claude-code-plugin/v0.x` release tags from a
> local clone. **Open:** land this branch (PR) when ready.
>
> **🟢 AGENT-TEAM PHASE 2 COMPLETE (plugin build) — 2026-05-26.** Branch
> **`claude/multi-platform-migration-AamWB`**. Built the plugin's **review-team**
> mechanism (the plugin's binding of `framework/governance/REVIEW_TEAM.md`):
> `skills/review-team/SKILL.md` + two review-lens agents `agents/adversary.md` &
> `agents/synthesizer.md`. The crew fans out as Claude Code `Task` subagents writing
> to the **git-ignored `.aidoc/review/` blackboard**; the `synthesizer` reduces the
> slots (dedup `location`+`id`, max severity, weighted/capped score from
> `REVIEW_CREWS.yaml`, coverage/quorum) into one report. `independent` default +
> `single_pass` fallback; team-at-gates / `single_pass`-advisory-at-`on_author`
> (`review_mode` knob). **D-0005: blackboard + coverage, no saga port.** Wiring:
> `pm-orchestrator` dispatches the team, `doc-flow` lists it, the skill documents the
> `-audit`/`-fixer`/`-autopilot` team mode (one shared mechanism, not 24 rewrites);
> `.gitignore` ignores `.aidoc/review/`; plugin CHANGELOG noted; lens→agent mapping
> table covers the framework crews. `plm_lint` clean corpus-wide; markdownlint clean;
> conformance 54; no framework change. **Next:** Phase 3 — parity proof (report-fixture
> schema check from both runners + a documented manual live-run; update `docs/PARITY.md`).
>
> **🟢 AGENT-TEAM PHASE 1 COMPLETE (Hermes conform) — 2026-05-26.** Branch
> **`claude/multi-platform-migration-AamWB`**. All 5 Phase-1 steps landed (commits
> `4578e63` scoring, `6e5c957` parser+saga+resilience, + report/crew/retitle):
> **parser** captures `lens_score`/`location`/`id` (+`recommendation` alias);
> **saga_orchestrator** computes `review_score`+`coverage` (via `review_scoring`)
> and surfaces them on the result/summaries; **resilience** — degrades on a failed
> branch (proceed + coverage), escalates **only below quorum** (new
> `BRANCH_FAILED→BRANCH_COMPLETED`); **report** `UCR_OUTPUT_UNIFIED` carries
> score+coverage; **crew/name** — Hermes review crews cover every framework crew via
> the alias (new guard test), `THE DEVIL'S ADVOCATE → THE CHAOS ENGINEER` retitled
> (11 prompts). Documented in `docs/architecture/REVIEW_TEAM_CONFORMANCE.md`. 49
> review unit tests green; conformance 54; ruff clean; platform-only (no spec change).
> The 2 `test_saga_review_pipeline` failures are the pre-existing missing-`mcp`-package
> import (reproduced on base). **Next:** Phase 2 (plugin build the review-team via
> subagents + `.aidoc/review/` blackboard; D9 — no saga port) then Phase 3 parity.
>
> **🟢 AGENT-TEAM PHASE 1 STARTED (Hermes conform) — 2026-05-26.** Branch
> **`claude/multi-platform-migration-AamWB`**. First Phase-1 increment: the
> deterministic **scoring + coverage** conformance + the **framework↔Hermes
> persona-name mapping**. New `platforms/hermes/src/mcp_server/review/review_scoring.py`
> (weighted/capped readiness score from `REVIEW_CREWS.yaml` weights, renormalised
> over lenses that ran; unresolved P0 ⇒ 0, P1 ⇒ capped below gate; `CoverageReport`
> with quorum → low-confidence; `FRAMEWORK_PERSONA_ALIASES` `chaos_engineer`→`adversary`,
> `chairperson`→`synthesizer`) + `tests/unit/test_review_scoring.py` (10) +
> `docs/architecture/REVIEW_TEAM_CONFORMANCE.md` (persona-output field map + status).
> Additive — the working saga/reducer/parser untouched. Conformance **54**; ruff clean;
> reducer/parser/scoring tests green (14); no framework change. **Remaining Phase 1:**
> capture `lens_score` in `persona_output_parser`; surface `score`+`coverage` in the
> saga result + `PERSONA_REVIEW_REPORT`/`UCR_*` shape; reconcile `persona_mappings.yaml`
> review crews with the framework crews (this also resolves the gap-review finding that
> UCR prompts still title the lens "THE DEVIL'S ADVOCATE"). **Next:** continue Phase 1.
>
> **🟢 AUDIT-FIXUPS (WS-A/B/C) DONE — 2026-05-26.** Branch
> **`claude/multi-platform-migration-AamWB`**. Plan: `plans/AUDIT-FIXUPS-PLAN.md`
> (2 review passes). Closed the 3 residual findings from the C4 + ID_NAMING audits.
> **WS-A** (framework GATE-SPEC, spec **0.8.0→0.8.1**): `ADR-TEMPLATE.yaml` now
> *requires* the decision `sequenceDiagram` (`@diagram: sequence-*`; flowchart
> optional), matching `DIAGRAM_STANDARDS.md`; bumped both FSV + 54 skills + CHANGELOG;
> `spec_gate` green. **WS-B** (platform docs): purged the v2/14-layer "available"
> narrative (`SYS/REQ/CTR/TSPEC/TASKS`, legacy workflow, `07_REQ` setup) from the 3
> `sdd-orchestrator/root-docs`, leaving a one-line "superseded" note + accurate
> migration changelog. **WS-C** (platform docs): `UCC_PERSONAS.md`
> `DEVILS_ADVOCATE→CHAOS_ENGINEER`, `INTEGRATION_EXPERT→INTEGRATION_LEAD` (+ UCRem
> fixer crew) to match runtime persona keys. Conformance **54**; Hermes prompt/persona
> tests green; no residual legacy. **Deferred by design:** the framework
> `adversary`/`synthesizer` ↔ Hermes `chaos_engineer`/`chairperson` name mapping is
> **AGENT-TEAM Phase 1**. **Next:** AGENT-TEAM Phase 1 (Hermes persona-output /
> saga_reducer schema conform).
>
> **🟢 HERMES PROMPT LEGACY-NAMING PURGE (ID_NAMING / traceability) — 2026-05-26.**
> Branch **`claude/multi-platform-migration-AamWB`**. On the directive "agents must
> use the `ID_NAMING_STANDARDS` convention; no mix with legacy naming" — with v3.2
> `legacy-ucx-v3.2-read-only/ucx_flow_v3` confirmed as the **source of truth** (it
> is the migration source; the migration changed *tooling* UCX→plugin+Hermes, not
> the spec; verified `ucx_flow_v3` = the 8 layers `01_BRD…08_IPLAN`, no
> `SYS/REQ/CTR/TSPEC`, element IDs `{TYPE}.{doc}.{section}.{hash}`). **Audit:** plugin
> agents/skills clean (legacy mentions are intentional *banned/removed* refs); Hermes
> personas clean; **Hermes prompt templates were heavily contaminated** with the
> pre-migration 10/12-layer `SYS→REQ→CTR→SPEC→TSPEC→TASKS` taxonomy + legacy
> element-ID forms. **Fixed (11 prompt files, platform-only, no spec change):**
> `UCC_OUTPUT_SCHEMA.md` (rewrote L6–L10 → L6 SPEC / L7 TDD / L8 IPLAN), `UCC_PERSONAS.md`
> (layer→persona map + assignments), `UCC_PROMPT_{BRD,PRD,ADR,SPEC}`, `UCR_PROMPT_ADR`,
> `UCRem_PROMPT_{BRD,PRD,ADR,SPEC}`: SPEC L9→L6, upstream/downstream chains,
> `@sys/@ctr`→`@spec`, `SYS-Ready`→`SPEC-Ready`, and the **type-code+sequence**
> element-ID scheme (`PRD.NN.TT.SS`, `BRD.{doc}.{type_code}.{seq}`, 3-segment
> `ADR.{doc}.{seq}`) → canonical `{TYPE}.{doc}.{section}.{hash}` (hash, not seq —
> per CM "no sequential numbering"). Conformance **54**; Hermes prompt/persona tests
> green (52+19). **Flagged (not fixed — lower-priority docs):** `sdd-orchestrator/root-docs/README.md`
> ("v2 14-layer … remain available" + a legacy workflow line) and `MULTI_PROJECT_*`
> guides still carry legacy layer references; persona display-name drift
> (`integration_expert`→`integration_lead`, `devils_advocate`→`chaos_engineer/adversary`).
> The `sdd-orchestrator` "What Was Cut from v2" table + `references/*` ban-guards are
> **correct** (document removals) — leave. **Next:** AGENT-TEAM Phase 1.
>
> **🟢 AGENT DIAGRAM-CONFORMANCE (C4 + DFD + sequence) — 2026-05-26.** Branch
> **`claude/multi-platform-migration-AamWB`**. On the directive "make sure agents
> use the framework's C4/sequence/dataflow model — nothing missed, plugin + Hermes":
> audited both platforms against `framework/governance/DIAGRAM_STANDARDS.md`. The
> **Hermes review side missed diagrams entirely** (no persona referenced
> C4/DFD/sequence; PRD/SPEC/ADR review prompts had no diagram checks) while the
> **plugin creation/audit side already enforced** them. Fixes (platform-only, no
> spec change): Hermes personas `architect` (new C4/DFD/sequence per-layer lens),
> `integration_lead` (sequence/dataflow + DFD trust boundaries), `auditor`
> (`@diagram:` tag checks) — these inject into every creation+review crew;
> `references/diagram-standards.md` de-contaminated (dropped `mermaid-gen` /
> `.claude/skills` tokens, points to the framework authority); `UCR_PROMPT_SPEC`
> now verifies the C4-L3/DFD-L3 contract. Plugin `solutions-architect` /
> `traceability-auditor` / `code-reviewer` made the diagram + `@diagram:`-tag +
> C4-L4-ownership checks explicit. Also fixed a residual legacy **SPEC `L9 → L6`**
> numbering in `tech_lead`/`integration_lead` + the SPEC review/remediation prompts.
> Conformance **54**; markdownlint clean; Hermes persona/reducer tests green.
> **Flagged (not fixed):** deeper legacy *TSPEC-as-Layer-10* divergence in
> `UCC_OUTPUT_SCHEMA.md` + `MULTI_PROJECT_*` / `docs/plans` (separate cleanup).
> **Next:** AGENT-TEAM Phase 1 (Hermes persona-output / saga_reducer schema conform).
>
> **🔵 AGENT-TEAM PHASE 0 READY — review-team spec (2026-05-25).** Branch
> **`claude/agent-team-plan`** (plan + Phase 0). Plan: `plans/AGENT-TEAM-PLAN.md`
> (D1–D8 confirmed, Pass-3 gap-hardened). **Phase 0** adds the engine-agnostic
> multi-persona **review-team** model: `framework/governance/REVIEW_TEAM.md`
> (crews + hub blackboard + persona-output contract + deterministic weighted/capped
> scoring & conflict policy with the structural gate as the reproducible floor +
> create/review/remediate shapes + resilience/security) and `REVIEW_CREWS.yaml`
> (per-layer crews + weights + default mode); a `review_mode` knob on
> `ADAPTATION_SURFACE.yaml`; `test_review_team.py` (suite **54**). Spec
> **`0.7.1 → 0.8.0`**; `spec_gate` green. **Next:** open the Phase 0 PR; after it
> merges, **Phase 1** (Hermes *conform* its persona_output/saga_reducer to the
> schema) then **Phase 2** (plugin *build* the review-team via subagents + the
> `.aidoc/review/` blackboard), then **Phase 3** parity proof.
>
> **🔵 FRAMEWORK DOC-CONSISTENCY (post-EARS review) READY (2026-05-25).** Branch
> **`claude/framework-doc-consistency`**. Reviewed the framework docs/README for
> inconsistencies after the EARS + ID changes. Findings + fixes: `EARS-TEMPLATE.yaml`
> had **3 three-segment element-ID examples** (the `id_standard` example
> `EARS.01.c4d8` contradicted its own 4-segment format; two `_antipatterns`) →
> corrected to 4-segment `TYPE.NN.SS.xxxx`; `QUICK_REFERENCE.md` Key Files table was
> missing `SECURITY_REVIEW.md` + `REVIEW_REMEDIATION_FLOW.md` → added. Everything
> else consistent (the `WHEN-THE-SHALL-WITHIN` tagline is uniform shorthand; the
> 5-pattern detail + 4-seg `ID_NAMING_STANDARDS` are correct). Spec **0.7.0 → 0.7.1**
> (patch; + both FSV + 54 skills + CHANGELOG); conformance **50**; `spec_gate` green.
> **Next:** open the PR.
>
> **🔵 PLATFORM-ALIGN B3 TAIL — persona-profile legacy scrub (2026-05-25).** Branch
> **`claude/hermes-persona-legacy-cleanup`** (B3 PR #21 merged). On "fix remaining
> tasks", scrubbed the **descriptive** SYS/REQ/CTR/TSPEC residue from the 10 vendored
> persona profiles (`skills/personas/*.md`): dead scoring-weight lines, `doc_types`
> tokens, and the dedicated legacy rows/sections (CTR Expertise, TSPEC Quality
> Metrics, eval-table rows). Doc-only — no runtime/VERSION change (part of unreleased
> Hermes `0.3.0`); local suite **382**, conformance **50**. **Retained by design:**
> `agent-skills/` "cut from v3"/"deprecated" history (accurate) + threshold `req`/`ctr`
> (unrelated). **Next:** open the PR. That fully closes PLATFORM-ALIGN + the flagged
> residue. **Remaining are user-only:** branch protection on `framework/**`; push
> `framework/v0.x` + `hermes/v0.x` tags from a local clone.
>
> **🔵 PLATFORM-ALIGN B3 READY — legacy-layer removal (2026-05-25).** Branch
> **`claude/hermes-legacy-layer-removal`** (B1+B2 merged as PR #20, Hermes `0.2.0`).
> Per the user's "full removal" decision, removed the **operative** SYS/REQ/CTR/TSPEC
> compat surface: 12 prompt templates; `registry.py` `LAYER_PREFIXES` entries (kept
> `tasks`); `persona_mappings.yaml` creation+review entries; the `ctr` branch in
> `validation/runner.py`; the README mention; legacy-layer tests in
> `test_validation_runner.py`. Hermes `0.2.0 → 0.3.0`; local suite **382**;
> conformance **50**; lint clean. **Deliberately retained** (descriptive, accurate
> history): vendored persona-profile `doc_types`/percentage mentions +
> `agent-skills/` "cut from v3"/"deprecated" notes. **Next:** open PR-3; the
> mcp-gated tests (test_server/test_yaml_parity) are the CI gate. **This closes
> PLATFORM-ALIGN** (A vendored linter; B1+B2 hash IDs; B3 legacy removal).
>
> **🔵 PLATFORM-ALIGN PART B (B1+B2) READY; B3 ESCALATED (2026-05-25).** Branch
> **`claude/platform-align-b`** (Part A merged as PR #19). **B1+B2 done:** Hermes
> element-IDs migrated to the framework **4-segment hash** form — runtime
> validators (`cross_section.py`, `remediation/runner.py`) 3-seg→4-seg + tests
> (local suite 383 green), and the 8-layer EARS/BDD prompt IDs + `UCC_PROMPT_EARS`
> legend off the legacy type-code scheme. Hermes `VERSION 0.1.0 → 0.2.0` +
> CHANGELOG; conformance **50**. **B3 ESCALATED (not done):** the legacy layers
> (SYS/REQ/CTR/TSPEC) are an *intentional documented "legacy compatibility"
> surface* (`registry.py` `LAYER_PREFIXES` + comment; `persona_mappings.yaml`;
> persona docs) covered only by mcp-gated tests — per plan B3.4 I paused removal for
> a user decision (full-remove / deprecate / leave). **Next:** open PR-2 for B1+B2;
> resolve B3 with the user.
>
> **🔵 PLATFORM-ALIGN PART A READY — vendor the doc-linter (2026-05-25).** Branch
> **`claude/platform-align`**. Plan: `plans/PLATFORM-ALIGN-PLAN.md` (all parts
> approved). **Part A done:** `tools/sdd_doc_lint` made location-independent
> (upward-search for `framework/registry/` + `--registry`/`$SDD_REGISTRY`; CLI exit
> 2 when no registry); **byte-identical copies vendored** into both platforms
> (`platforms/*/sdd_doc_lint/`), kept in sync by `sync-vendored.sh` + a conformance
> drift-guard (suite **50**); the plugin `on_author` hook now runs the vendored
> linter reliably (advisory, exit-0, skips with no `framework/`). Platform/tooling
> only — no spec bump. `pre-commit` clean. **Next:** open PR-1; after it merges,
> **Part B** (cut from `main`): B1 prompt IDs type-code→4-seg hash, B2 Hermes
> runtime regex 3→4-seg + tests, B3 **remove** the 12 SYS/REQ/CTR/TSPEC legacy-layer
> prompts + their runtime coupling, Hermes `VERSION` bump.
>
> **🔵 DOC-CHECK PHASES 1–4 READY — automated review triggers (2026-05-25).**
> Branch **`claude/doc-check-triggers`** (cut from `main` after Phase 0 / PR #17
> merged). Plan: `plans/DOC-CHECK-PLAN.md`. Implements the platform automation
> over the spec's trigger points: **Phase 1** `tools/sdd_doc_lint/` (stdlib
> structural linter — IDs/tags/threshold/EARS-grammar/placeholders, registry-driven;
> valid+broken fixtures + 3 unit tests); **Phase 2** plugin `on_author` advisory
> hook (`hooks/hooks.json` + `sdd-doc-review.sh`, nudges `doc-<layer>-audit` +
> best-effort linter, never blocks); **Phase 3** `.github/workflows/doc-review.yml`
> blocking `pre_merge` gate (self-tested via fixtures); **Phase 4** PARITY +
> plugin/Hermes README trigger mappings. **Platform/tooling only — no `framework/`
> change, no spec bump** (stays `0.7.0`); conformance **49**; pre-commit clean.
> **Design note:** the deterministic gate is reliable in **CI**; the **write-time
> hook is advisory** (linter best-effort) since running a linter in an arbitrary
> consumer's live session would need bundling — a possible follow-up. **Next:**
> open the Phases 1–4 PR.
>
> **🔵 DOC-CHECK PHASE 0 READY — review/remediation/gate loop in the spec (2026-05-25).**
> Branch **`claude/doc-check-automation`**. Plan: `plans/DOC-CHECK-PLAN.md`
> (framework-first; decisions: light contract + spec/hook/CI). **Phase 0** models
> the quality loop in the spec — new `framework/governance/REVIEW_REMEDIATION_FLOW.md`
> naming `Draft→Review→Remediate→Gate→Approved` + four trigger points
> (`on_author`, `on_gate_fail`, `pre_promotion`, `pre_merge`) with a light
> conformance contract (engine surfaces findings/score/remediation path at each
> supported point; *how* is the engine's choice). Doesn't change gate thresholds.
> Spec **`0.6.0 → 0.7.0`** (+ both FSV + 54 skills + CHANGELOG); registered in the
> governance README + `test_governance` EXPECTED_FILES; conformance **49**;
> `spec_gate` green. **Next:** open Phase 0 PR; after it merges, **Phases 1–4**
> (cut from `main`) — the shared stdlib check `tools/sdd_doc_lint/`, the plugin
> `on_author` advisory hook (#1), the `pre_merge` blocking CI (#2), and Hermes
> trigger-point mapping/parity. The deterministic check is the *platform-tier*
> implementation of the spec's trigger points, not the centerpiece.
>
> **🔵 HERMES EARS ALIGNMENT READY — deferred #4b follow-up (2026-05-25).** Branch
> **`claude/hermes-ears-align`** (cut from `main`). Closed the one item deferred
> from FRWK-REVIEW #4b: aligned the Hermes **vendored** EARS pattern surfaces to
> the framework's canonical 5-pattern / `the [system] shall` model (no `THEN`;
> "complex" = composition). Edited 6 files — the two persona docs
> (`requirements_specialist`, `sdd-review-personas`) and the EARS prompt templates
> (`UCC_PROMPT_EARS`, `UCC_OUTPUT_SCHEMA`, `UCR_PROMPT_EARS`, `UCRem_PROMPT_EARS`):
> tables → 5 rows + composition note; `IF…THEN`/`IF-THEN` → `IF … the system
> shall`; dropped the standalone `Complex` row + `CX` type code. **Platform-only**
> — no `framework/` change, no spec bump (spec stays `0.6.0`); recorded in
> `platforms/hermes/CHANGELOG.md`. Conformance **49/49**; lint clean (vendored
> content skips markdownlint). **Still separate (not done):** the prompts' legacy
> type-code element-ID scheme (`EARS.NN.<code>.<seq>`) vs the framework hash IDs —
> a larger, distinct cleanup. **Next:** open the PR.
>
> **🔵 FRWK-REVIEW #4b READY — EARS statement-model reconciliation (2026-05-25).**
> The deferred EARS finding, implemented on branch **`claude/frwk-review-4b-ears-model`**
> (pushed, cut from `main` after the FRWK-REVIEW PRs). Plan:
> `plans/FRWK-REVIEW-4b-EARS-MODEL-PLAN.md` (D1 = A, canonical-5, user-confirmed).
> The EARS layer was described four ways; standardized on **canonical EARS** —
> five patterns (Ubiquitous, Event/WHEN, State/WHILE, Optional/WHERE, Unwanted/IF),
> all `THE … SHALL …` (the non-EARS `THEN` connective removed); `WITHIN` kept as a
> framework extension; "complex" documented as composition, not a 6th type. Added
> the Optional/`WHERE` pattern to the template (guidance + `optional_feature`
> block), README, and index; aligned plugin `doc-ears` + `requirements-analyst`;
> new `tests/conformance/test_ears_model.py` (suite **49**). Spec **`0.5.0 → 0.6.0`**
> (+ both FSV + 54 skills + CHANGELOG); `spec_gate` green. **Deferred:** Hermes
> vendored `agent-skills`/`prompts` EARS tables (platform follow-up). **Next:** open
> the PR; that fully closes the FRWK-REVIEW review (incl. its one deferred item).
>
> **✅ FRWK-REVIEW COMPLETE — framework pre-production audit fixes (2026-05-24).**
> Both PRs **merged** to `main`; framework spec **`0.3.2 → 0.5.0`**. Plan:
> `plans/FRAMEWORK-REVIEW-FIXES-PLAN.md` (13 findings, decisions D1–D6, 2 review
> passes). **PR #12 — Batches 1 (correctness) + 2 (security), spec `0.4.0`:**
> SPEC/TDD trace-tag element forms + `id_standard` notes on L6–L8; BDD downstream
> framing; BRD-XS numbering gap; PRD-index enum; registry index-split doc; "5-Gate"
> branding retired (GATE-SPEC is the 6th); emergency SLA unified to 48h; GATE-SPEC
> surfaced on the approval form + post-mortem template; new engine-agnostic
> `governance/SECURITY_REVIEW.md`; blocking `GATE-03-E008` (external-change
> CVE/advisory-or-N/A); `DIAGRAM_STANDARDS.md` click-handler/inline-HTML
> sanitization; `GATE-SPEC-W003` agent-facing security review. **PR #13 — Batch 3
> (THRESHOLD de-bloat), spec `0.5.0`:** `THRESHOLD_NAMING_RULES.md` trimmed 909 →
> 734 (financial examples genericized in place; off-charter §8 Environment
> Override + §12 propagation-SLA/approver matrix removed; stale "UCX Flow Team"
> provenance replaced); safety gate passed (no programmatic consumer). New
> `tests/conformance/test_framework_review_guards.py` (3 guards); suite **46**,
> green throughout; each PR passed GATE-SPEC by construction. #13 (total_sections/
> P0-P1) found N/A; **deferred:** finding #4b (EARS index statement-type/syntax
> model decision). **User-only carry-overs (standing):** branch protection on
> `framework/**`; push the `framework/v0.x` release tags from a local clone.
>
> **✅ PRE-COMMIT HOOKS — (2026-05-24, D-0021).** Added `.pre-commit-config.yaml`
>
> - a `pre-commit` CI workflow: hygiene, ruff + ruff-format, bandit (medium+),
> markdownlint, yamllint, detect-secrets, pip-audit (manual), and a local
> conformance hook. Pragmatic rule sets; `legacy/` + Hermes vendored content
> (`agent-skills/`, `prompts/`, `skills/`) excluded from markdownlint. Full
> repo-wide cleanup applied (markdownlint/ruff over ~450 files + hand-fixed
> residual incl. genuine Hermes findings F821/F823/UP042). `pre-commit run
> --all-files` is green; conformance + 383 testable Hermes tests pass. Branch
> `claude/precommit-hooks` → PR. Enable locally: `pip install pre-commit &&
> pre-commit install`.
>
> **✅ MERGED TO MAIN — PR #2 (2026-05-24).** The whole post-v1.0.0 line landed
> on `main` (merge commit `3974daa`): canonical 54-skill plugin set, ADAPT
> overlay, **CHG-D1 / GATE-SPEC**, **CHG-D2 / GD-01**. All four PR checks were
> green pre-merge — including the **Framework-spec change gate**, GATE-SPEC's
> first real enforcement (E005 VERSION + E008 CHANGELOG + E006/E007 conformance)
> on a live PR. `main` is the integration line; `claude/skill-revision` is merged
> (safe to delete). Framework spec **0.3.1**; conformance 43; the `workflows`
> permission is now granted (so `.github/workflows/**` is pushable in-container).
>
> **Remaining (user-only):**
>
> - **Branch protection on `framework/**`** (repo → Settings → Branches) — the
>   human-approval half of GATE-SPEC. The automated half now enforces via the
>   `chg-gate.yml` workflow; the human sign-off exists only once this rule is set.
> - **Release tags** — annotated; tag pushes still 403 in-container (separate
>   from the workflows scope, see `docs/TAGGING.md`), so push from a local clone:
>
>   ```sh
>   git tag -a framework/v0.2.0 f22fe6a -m "Framework spec v0.2.0 — adaptation overlay (ADAPT, D-0019)"
>   git tag -a framework/v0.3.0 f8e8bf5 -m "Framework spec v0.3.0 — GATE-SPEC framework-spec change gate (CHG-D1, D-0020)"
>   git tag -a framework/v0.3.1 3753de2 -m "Framework spec v0.3.1 — governance decision register (CHG-D2, GD-01)"
>   git push origin framework/v0.2.0 framework/v0.3.0 framework/v0.3.1
>   ```
>
>   Optional project milestone tag: `git tag -a v1.1.0 3974daa -m "Post-cutover feature release — adaptation overlay + CHG GATE-SPEC" && git push origin v1.1.0`.
> - Delete the merged `claude/skill-revision` branch.
>
> **✅ CHG-D2 COMPLETE — framework governance decision register (2026-05-23).**
> Established `framework/governance/DECISIONS.md` — the spec's own durable home
> for decisions about the spec + its governance — and recorded the CHG
> implementation model (CHG-D1) there as **GD-01** (engine-agnostic). The
> migration log's spec-affecting decisions now graduate here; D-0013 + D-0019 are
> listed pending. Recording it was itself a GATE-SPEC change — the **first real
> exercise of the gate** (framework spec **0.3.0 → 0.3.1**; + both FSV + 54
> skills). Conformance **43** (DECISIONS.md folded into the existing governance
> file-set checks; its content passes the engine-token hygiene scan);
> `plm_lint` clean; `spec_gate` passes vs origin/main. ROADMAP CHG-D1 **and**
> CHG-D2 are now done. **Branch: `claude/skill-revision`** (PR #2 → `main`,
> clean fast-forward). **Workflows now active** — the user granted the GitHub App
> the `workflows` permission, so `.github/workflows/**` is pushable from the
> container. Fixed the stale **Plugin smoke-checks** guard in place (skill count
> `-lt 100`/~142 → `-lt 40`/~54) and **activated `chg-gate.yml`** (the GATE-SPEC
> CI workflow, `pull_request`-scoped); `plans/workflows-pending/` is drained.
> **Remaining user-only:** branch protection / required reviewers on
> `framework/**` (the human-approval half of GATE-SPEC); push the 0.3.x tags from
> a local clone.
>
> **✅ CHG-D1 COMPLETE — GATE-SPEC, the framework-spec change gate (2026-05-23).**
> ROADMAP CHG-D1 done (D-0020, plan `plans/CHG-D1-PLAN.md`): change management as
> **skills + CI/CD, both platforms**. Added **GATE-SPEC** — the *meta* gate
> governing changes to the `framework/` spec itself (templates/governance/
> registry/VERSION), orthogonal to the artifact-cascade gates. Five increments:
> (1) shared spec — `GATE-SPEC_FRAMEWORK.md` + `spec` change_source +
> `semver_impact` + error-catalog/diagram/CHG-template/README wiring + a
> conformance guard; (2) plugin skills — `gate-check` runs it, `doc-chg` family
> routes to it, `knowledge-extractor` **unblocked** (spec promotion now routes to
> a real CHG record + GATE-SPEC); (3) CI — `tests/chg/spec_gate.py` (diff-aware
> E005/E008) + staged `plans/workflows-pending/chg-gate.yml`; (4) Hermes
> server-side — `validation/chg_rules.py` + 5 unit tests; (5) close. Three-way
> enforcer split: record validator (E001–E004) · CI (E005–E008) · protected-branch
> review (human E004); **a skill never self-approves**. Framework spec **0.2.0 →
> 0.3.0** (+ both FSV + 54 skills). Conformance **38 → 43**; Hermes CHG 8/8 (full
> validation suite green bar pre-existing `mcp`-SDK-missing collection errors);
> `plm_lint` clean. **Branch: `claude/skill-revision`.** **Follow-up: CHG-D2**
> (record CHG-D1 as a formal `framework/governance/` decision — now actionable).
> **User-only:** relocate `chg-gate.yml` → `.github/workflows/`; set branch
> protection on `framework/**` (the human-approval half); push the 0.3.0 tags.
>
> **✅ ADAPT COMPLETE — adaptation surface + knowledge extractor (2026-05-23).** New feature:
> project adaptation overlay + knowledge extractor (plan `plans/ADAPT-PLAN.md`,
> hardened Pass 1–4; design recorded D-0019). **Increment 1 (this commit):** the
> engine-agnostic surface spec `framework/governance/ADAPTATION.md` + the
> machine-readable `ADAPTATION_SURFACE.yaml` (closed 4-knob registry —
> `active_layers`, `section_toggles`, `audit_threshold` raise-only, `glossary`;
> `id_format` deferred; skippable layers `[BDD, ADR]` + cascade rule). Registered
> in `governance/README.md` + the governance conformance contract (+1 test).
> Conformance **33/33**. **Increment 2 done:** `adapts:` frontmatter +
> `## Adaptation` consult-clause wired into the **35-skill adapting set** (layer
> base/autopilot/audit/fixer ×8 + `trace-check` + `project-init`/`-adopt`) via
> `/tmp/wire_adapts.py`; new `tests/conformance/platforms/test_adaptation.py`
> asserts `adapts ⊆ surface` + authority-ref + ≥35 wired. Conformance **36/36**,
> `plm_lint --all` clean. **Increments 3+4 done:** new **`project-profile`**
> utility skill (creates/maintains `.aidoc/profile.yaml`, materializes the
> user-global seed, validates against the surface); registered everywhere —
> plugin README (52→**53**, utilities 16→17), `SKILL_AUTHORING` §1 (corrected
> stale 46→53, added the change-mgmt family + project-adopt/gate-check it had
> omitted), `skill-recommender` intent map + catalog, `doc-flow` utility list.
> Conformance **36/36**, `plm_lint` clean, skill count **53**. **ADAPT-B done
> (functional):** added the **learnings-log** convention to `ADAPTATION.md` (§7,
> entry shape + best-effort capture + owner-routing) and the **`knowledge-extractor`**
> skill (manual: read profile+learnings → judge generalizability → classify owner
> → draft; spec target → CHG draft stamped *blocked on the unbuilt spec-gate*,
> guidance target → PR-ready description; never applies/approves). Registered
> everywhere (README 53→**54**, utilities 17→18; `SKILL_AUTHORING`;
> `skill-recommender` intent+catalog); `project-profile` link restored.
> **✅ ADAPT COMPLETE — version bumped (feature close):** `framework/VERSION` +
> both platform `FRAMEWORK_SPEC_VERSION` `0.1.0 → **0.2.0**`, and all 54 plugin
> skills' `framework_spec_version` (user decision = bump everything). Conformance
> **37/37** (+leakage guard), `plm_lint` clean, skill count **54**. **Branch:
> `claude/skill-revision`** (user-confirmed). **Deferred follow-up:** the CHG
> spec-change gate (CHG-D1) — spec→CHG promotions are drafted but ungated until
> built. **Pending user-only (carry-overs):** push the 0.2.0 spec/release tags
> from a local clone (in-container `refs/tags/*` 403); decide whether to roll
> these commits into a plugin release (CHANGELOG `[Unreleased]` not yet cut).
>
> **✅ NEW SKILLS ADDED — 46 → 52 (2026-05-23, P3-T7).** A post-revision review
> found framework-backed capabilities with no skill; added 6 (skipping
> `doc-code`/implement by user choice): the **`doc-chg` family** (base +
> `-autopilot`/`-audit`/`-fixer`) for the CHG change-management overlay
> (`framework/governance/chg/`) — change-level classification (C1–C3/Emergency),
> source→gate routing, cascade impact, `gate_ready` instead of a ≥90 score;
> **`gate-check`** — runs the CHG approval gates (GATE-01/03/06/08/CODE) and
> prepares `GATE_APPROVAL_FORM` (human approves, never the skill); and
> **`project-adopt`** — brownfield counterpart to `project-init`. Wired into
> `doc-flow`, `skill-recommender`, plugin `README` (52), `CHANGELOG`,
> `docs/PARITY.md`, and `plm_lint` `MIGRATED`. Conformance **32/32**. Record:
> `plans/P3-T7-PLAN.md`.
>
> **✅ SKILL SET REVISED — canonical 46 (2026-05-23, P3-T6).** Pruned the plugin
> skill corpus **124 → 46** and recreated every survivor to one standard
> (`platforms/claude-code-plugin/docs/SKILL_AUTHORING.md`): the 8 layer families
> `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}` × {base, `-autopilot`, `-audit`,
> `-fixer`} = 32, plus 14 utilities. Removed (reversing D-0015): 25 SPEC-subtype
>
> - 36 test-type families (folded into SPEC L6 / TDD L7), 14 deprecated
> `-reviewer`/`-validator` (merged into `-audit`), 3 legacy utils
> (contract-tester/test-automation/mermaid-gen), 16 loose `.md`, and the orphaned
> `doc-flow/SHARED_CONTENT.md` (D-0013). Each skill `version` now defaults to the
> plugin version (0.2.0) + `framework_spec_version`; Version-History footers
> dropped; `mermaid-gen`→`charts-flow`; `agents/README` + `doc-validator` +
> `doc-review` repointed to `-audit`. Conformance **32/32**. Record:
> `plans/P3-T6-PLAN.md`. **Open:** (1) confirm push branch — working tree is on
> `claude/skill-revision`, task setup named `claude/multi-platform-migration-AamWB`;
> (2) consider bumping plugin 0.2.0→0.3.0 given the scope (skills track the
> plugin version, so they'd follow); (3) the "new skills" idea is still pending.
>
> **🚀 PLUGIN v0.2.0 RELEASE PREPPED (2026-05-23) — launch-wise, in-container half.**
> Cut the Claude Code plugin's first post-migration release: `VERSION` +
> `plugin.json` bumped `0.1.0 → 0.2.0`; CHANGELOG `[Unreleased]` → `[0.2.0] —
> 2026-05-23`; added the repo-root **plugin marketplace** manifest
> (`.claude-plugin/marketplace.json`, marketplace `aidoc-flow-framework` →
> plugin `aidoc-flow`, subdir source) so it installs via `/plugin marketplace
> add vladm3105/aidoc-flow-framework` + `/plugin install
> aidoc-flow@aidoc-flow-framework`; install command added to root + plugin
> READMEs; `docs/TAGGING.md` Current-tags table extended (`v1.0.0`,
> `claude-code-plugin/v0.2.0`). Conformance 32/32. The annotated tag
> `claude-code-plugin/v0.2.0` is created locally on the release commit (push
> 403s in-container — same pattern as every prior tag). **Remaining = user-only:
> (1) merge this branch into `main`; (2) push the tag from a local clone;
> (3) relocate CI workflows from `plans/workflows-pending/` → `.github/workflows/`.**
> See "Independent pending user actions" below for exact commands.
>
> **✅ MIGRATION COMPLETE (2026-05-21).** All five phases done; the
> Phase 5 cutover is closed at project `v1.0.0` (in-container half).
> The working branch holds the finished multi-platform project. The
> only remaining steps are **user-side local-clone actions** — tag
> pushes + the `main` force-replace + CI-workflow relocation
> (commands in `plans/MIGRATION_TODO.md` P5-T6). Pre-migration
> history is on the protected `legacy-ucx-v3.2-read-only` branch.
>
> **✅ PLM COMPLETE (2026-05-22) — Plugin layer-model migration.** The Claude
> Code plugin's entire **125-skill** corpus is migrated from the legacy
> 12-layer SDD model to the framework's **8-layer** model — all batches B0–B7
> landed. Sequence: B1 renamed tspec→tdd & tasks→iplan + retired sys/req/ctr
> (142→125); B2 brd/prd/ears; B3 bdd/adr + adr-roadmap; B4 spec (L9→L6) + 5
> SPEC-subtypes (L6 helpers); B5 6 test-subtypes (L7 helpers); B6 12
> helper/orchestrator skills (incl. doc-naming, element-code system deleted);
> B7 promoted the gate to conformance + deleted the PARITY gap + CHANGELOG
> close-out. Both platforms now implement the 8-layer model. `plm_lint --all`
> is clean and enforced by conformance (`tests/conformance/platforms/test_plm_lint.py`;
> suite **32/32**). Records: `plans/PLM-PLAN.md`, `DECISIONS.md` D-0015.
>
> **Post-migration gap audit (2026-05-22, D-0016):** verified the framework
> correctly absorbs SYS/REQ/CTR (SYS→SPEC, CTR→SPEC, REQ→EARS) against the v3.2
> source; fixed deprecated-layer residue the gate had missed in the plugin
> surface — `agents/requirements-analyst.md` (REQ→EARS), the trace-check example,
> and a broken `doc-validator` ref — and hardened `plm_lint` (now scans
> `agents/`+`commands/`; adds dash-ref / layer-dir / context-aware 3-segment
> patterns). project-mngt keeps generic REQ-NN (excepted).

Continuity record across ephemeral sessions. Read this first each session;
refresh it at milestones and **before any context compaction**.
Timestamps are ISO 8601 UTC (`YYYY-MM-DDThh:mm:ssZ`).

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Last updated  | 2026-05-24T22:00:00Z                       |
| Working branch| `main` (FRWK-REVIEW PRs #12 + #13 merged) |
| Current phase | **FRWK-REVIEW complete** — framework pre-production audit landed in two PRs; framework spec **0.5.0**; conformance **46**; GATE-SPEC enforcing on PRs. |
| Next task     | **None pending in-container.** **User-only:** branch protection / required reviewers on `framework/**` (GATE-SPEC human half); push framework `v0.2.0/v0.3.0/v0.3.1` (+ optional `v0.4.0/v0.5.0`, `v1.1.0`) tags from a local clone. **Deferred:** finding #4b (EARS index statement-type/syntax model decision). |

## Progress

- Phase 0 (Planning & Scaffolding) — complete.
- Phase 1 Step 0 (P1-T0, legacy isolation) — complete.
- P1-T1 (audit of `legacy/ucx_flow_v3/`) — complete; see
  `plans/P1-AUDIT-ucx_flow_v3.md`.
- P1-T2 (layer extraction) — complete; `framework/layers/` holds 24 files;
  see `plans/P1-T2-PLAN.md`.
- P1-T3 (registry extraction) — complete; `framework/registry/` holds
  `LAYER_REGISTRY.yaml` + `README.md`; see `plans/P1-T3-PLAN.md`.
- P1-T4 (governance + CHG extraction) — complete; `framework/governance/`
  holds 18 files; see `plans/P1-T4-PLAN.md`.
- P1-T5 (shared conformance suite) — complete; `tests/conformance/` holds the
  helper + 4 test modules (22 tests, all green); see `plans/P1-T5-PLAN.md`.
  The engine-agnostic `framework/README.md` was written here (pulled forward
  from P1-T7).
- P1-T6 (`framework/VERSION` + tag convention) — complete; `framework/VERSION`
  at `0.1.0`, tag namespaces in `docs/PROJECT.md` §3, suite at 24 tests; see
  `plans/P1-T6-PLAN.md`. The `framework/v0.1.0` git tag is deferred to Phase 1
  close (D-0009, tracked as P1-T8).
- P1-T7 (framework root assembly) — complete; the 4 methodology docs extracted
  into `framework/`; suite at 25 tests; see `plans/P1-T7-PLAN.md`.
  **`framework/` is now fully assembled.**
- P1-T8 (Phase 1 close) — **complete.** Changelog cut into `[0.1.0]` /
  `[0.2.0]`, ROADMAP marked, and the three annotated tags (`v0.1.0`,
  `framework/v0.1.0`, `v0.2.0`) published to the remote (pushed from a local
  clone after the in-container tag push was blocked by the git proxy). See
  `plans/P1-T8-PLAN.md`. **Phase 1 complete.**
- P2-T0 (Phase 2 audit & task breakdown) — **complete.** Paper-only audit
  resolved that `mcp_ucx` is the deprecated predecessor of `ucx_hermes` and
  is out of Phase 2 scope; Phase 2 input is 280 files. Mapped 4 code-level +
  prose-level framework-coupling sites; defined the audit-confirmed P2-T1…T6
  breakdown. See `plans/P2-T0-PLAN.md` / `plans/P2-AUDIT-hermes.md`.
- P2-T1 (Hermes design) — **complete.** Five design choices resolved
  (`plans/P2-T1-DESIGN.md`): keep `mcp_server` import path with
  `hermes-server` distribution (Q1 — Platform B is JS/MD, no Python
  collision); two plain-text VERSION files for spec declaration (Q2);
  **drop platform `templates/` — consume `framework/layers/`** (Q3, D-0013);
  `hermes-mcp` script entry (Q4); mirror legacy layout minus dropped
  paths (Q5). D-0013 logs the templates-source-of-truth decision.
- P2-T2 (port-verbatim) — **complete.** 64 files copied byte-identical
  from `legacy/ucx_hermes/` to `platforms/hermes/`: `examples/` (1),
  `prompts/` (46), `skills/layer_aliases/` (1), `skills/personas/` (15),
  `skills/persona_mappings.yaml` (1). All seven verify gates green —
  `diff -r` identical on every path, no `ucx_flow` references in the
  copied targets, expected-absent paths still absent, conformance suite
  25/25. → `plans/P2-T2-PLAN.md`.

## Achievements

- 2026-05-18 — Isolated the pre-migration project into `legacy/` (frozen);
  disabled legacy CI; rewrote root `README.md`; repointed `.mcp.json`.
- 2026-05-18 — Added `plans/` workspace, root `CLAUDE.md`, `DECISIONS.md`,
  and `PreCompact` / `SessionStart` continuity hooks.
- 2026-05-18 — Audited `legacy/ucx_flow_v3/` (49 files); resolved P1 open
  questions (D-0005 index templates, D-0006 `framework/` v0.1.0).
- 2026-05-18 — Added the two-pass plan-review gate (D-0007): `CLAUDE.md`
  rule, `plans/PLAN-TEMPLATE.md`, `PreToolUse(git commit)` warning hook.
- 2026-05-18 — Extracted the 8 SDD layers into `framework/layers/`
  (templates, READMEs, index templates — engine-neutral).
- 2026-05-18 — Extracted `LAYER_REGISTRY.yaml` into `framework/registry/`
  as the authoritative machine-readable layer model.
- 2026-05-18 — Extracted governance docs + CHG overlay into
  `framework/governance/` (18 files, engine-neutral; CHG spec-only).
- 2026-05-18 — Built the shared conformance suite (`tests/conformance/`,
  22 tests) and wrote the engine-agnostic `framework/README.md`.
- 2026-05-19 — Created `framework/VERSION` (`0.1.0`) and the tag-namespace
  convention (D-0009); conformance suite at 24 tests.
- 2026-05-19 — Extracted the 4 methodology docs into `framework/`;
  `framework/` fully assembled; conformance suite at 25 tests.
- 2026-05-19 — Closed Phase 1: changelog cut + ROADMAP marked; release tags
  `v0.1.0`, `framework/v0.1.0`, `v0.2.0` published to the remote.
- 2026-05-19 — Added `docs/TAGGING.md` tagging policy (release + bookmark
  tags, D-0011).
- 2026-05-19 — Defined the framework's purpose: the IPLAN is the terminal
  product; code/deploy out of scope; v1 = software/devops; domain profiles
  post-v1.0 (D-0012, `ROADMAP.md`).
- 2026-05-19 — Completed P2-T0 (Phase 2 audit & task breakdown):
  `legacy/mcp_ucx/` confirmed out of scope; Phase 2 input is 280 files;
  coupling sites mapped; P2-T1…T6 defined.
- 2026-05-19 — Completed P2-T1 (Hermes design): five design choices
  resolved; D-0013 records the templates-single-source-of-truth rule
  (platforms consume `framework/layers/`, never duplicate).
- 2026-05-20 — Completed P2-T2 (port-verbatim): 64 files copied
  byte-identical into `platforms/hermes/`; verify gates all green.
- 2026-05-20 — Completed P2-T7 (port `hermes_agent_skills/` from main):
  181 files (was 187; 6 D-0013-obsolete sync files deleted) at
  `platforms/hermes/agent-skills/spec-driven-development/`; zero
  `ucx_flow|UCX_FLOW` hits; audit §5b updated; two plan deviations
  documented as Pass 3 retro (G11 deletion vs deprecation, G13 `/opt/data`
  verify softening).
- 2026-05-20 — Completed P2-T3 (port-with-repoint): 200 files +
  VERSION/FRAMEWORK_SPEC_VERSION ported; pyproject migrated to
  `hermes-server` / `0.1.0` / `hermes-mcp` (P2-T1 Q1+Q4); path-map
  rewrote all current-behavior `ucx_flow_v3` references in 18 files;
  11 historical docs preserved verbatim per G13; audit §3a/§3c
  refreshed; .mcp.json repointed. Conformance 25/25; Hermes' own
  suite 397/447 (50 failures from D-0013 scaffold-runtime gap →
  deferred to new P2-T9 task).
- 2026-05-20 — Completed P2-T8 (drop skill's templates duplication):
  deleted 8 drifted layer YAMLs at `agent-skills/.../sdd-orchestrator/
  templates/`; rewired 25 references in `SKILL.md` +
  `sdd-workflow-quickstart.md` to `framework/layers/0N_TYPE/
  TYPE-TEMPLATE.yaml`; rewrote line-692 `skill_view` example to a
  direct-read instruction. Content-equivalence check confirmed deltas
  were engine-hardcode + phrasing — no substantive content lost.
  D-0013 conformance for the skill package complete. Pass 3 retro
  records G17 (verify gate V6 was too coarse — corrected to scope
  the grep to `skill_view.*templates/`).
- 2026-05-20 — Completed P2-T9 (rewire MCP scaffold + validation
  runtime to `framework/layers/`): removed the `templates/` row from
  `CANONICAL_SCAFFOLD_MAPPINGS`; rewrote `_default_ssd_root` to
  `framework/layers`; fixed `_default_repo_root` parents count
  (`[4]→[5]` — layout shifted in P2-T3); rewrote
  `validation/runner.py:_resolve_canonical_template_root` as a
  3-stage precedence chain (override → scaffold output → canonical);
  cleaned up test fixtures. **Hermes test suite 397/447 → 447/447;
  conformance 25/25.** Pass 3 retro records G16 (parents-count audit
  lesson) + G17 (cross-module path-computer audit lesson). The 50
  P2-T3-deferred failures are all closed; D-0013 conformance for
  the MCP server complete.
- 2026-05-20 — Completed P2-T5 (Phase 2 verify): ran 14 consolidated
  gates — conformance 25/25, Hermes 447/447, zero coupling in
  current-behavior content, docs whitelist exact-match (11 files),
  VERSION files match `framework/VERSION`, smoke test scaffolds 71
  files end-to-end. Audit math reconciled (440 = 439 + 1 P0-scaffolded
  README). Verify record landed at `plans/P2-T5-VERIFY.md`. Phase 2
  is structurally complete; P2-T6 may cut the changelog and tags.
- 2026-05-20 — Completed P2-T6 (Phase 2 close): `CHANGELOG.md` cut to
  `[0.3.0] — 2026-05-20` (full Phase 2 cycle: Added / Changed /
  Removed, folding the 4 pre-existing `[Unreleased]` items);
  `ROADMAP.md` status `Phase 2 complete (v0.3.0) — Phase 3 next`;
  Phase 2 section ends with `Status: complete (v0.3.0,
  hermes/v0.1.0)`; `docs/TAGGING.md` table appended with the 2 new
  tag rows. Close commit `20c061d` pushed to the working branch.
  Annotated tags `v0.3.0` + `hermes/v0.1.0` created locally on
  `20c061d`; tag push 403'd as expected (P1-T8 pattern). Tag
  publication requires the user to run the local-clone workaround
  documented in `plans/P2-T6-PLAN.md` Implementation note. **Phase 2
  is structurally closed.**
- 2026-05-20T17:25:00Z — User published the two Phase 2 tags via the
  local-clone workaround. `git ls-remote --tags origin` now returns
  all 5 tags; `v0.3.0` and `hermes/v0.1.0` both dereference to the
  close commit `20c061d`. **Phase 2 is formally closed.** Next: Phase 3
  (Platform B — Claude Code plugin).
- 2026-05-20T18:35:00Z — Completed P3-T0 (Phase 3 audit + task
  breakdown). `plans/P3-AUDIT-claude-code-plugin.md` inventories
  `.claude/` (191 files), resolves the **copy-with-divergence**
  relationship (root stays in dev-time service until Phase 5), maps
  framework coupling to a single uniform rewire (`ai_dev_flow` →
  `framework` across 30 files), and classifies every top-level path.
  Phase 3 shape is 5 sub-tasks (T1–T5) — simpler than P2's 9 because
  coupling is small, no predecessor noise (no `mcp_ucx`-style tree),
  and the artifact is declarative (no Python package or test suite).
  6 open questions for P3-T1 design; see `plans/P3-T0-PLAN.md` for
  the full breakdown.
- 2026-05-20T19:10:00Z — Completed P3-T1 (design, paper-only).
  7 questions resolved in `plans/P3-T1-DESIGN.md`. Manifest is
  minimal (auto-discovery handles registration; confirmed via
  claude-code-guide agent — no published `$schema` URL,
  `name`/`description`/`version`/`author` are the recommended core
  fields). Plugin skill set finalised: **142 skills** (129 doc-* +
  13 non-doc); plugin name `aidoc-flow`; copy strategy a 3-stage
  `cp -r` + `rm -rf` recipe; no lifecycle hooks in v0.1.0.
  Pass 2 caught a Pass 1 skill-count miscount (144 → 142) and
  softened the manifest author block (populated from
  `git config user.name` at P3-T3, not hardcoded).
- 2026-05-20T20:20:00Z — Completed P3-T2 (port content). 3-stage
  `cp -r` + `rm -rf` recipe landed 142 skills + 19 root files + 1
  agent + 1 command at `platforms/claude-code-plugin/` (168 total
  files). Basic sed cleared 211 line hits of `ai_dev_flow` across
  30 source files; Class B (5 layer dirs) + Class C
  (ID_NAMING_STANDARDS) + project-mngt `/opt/data` rewrite applied.
  G13 illustration paths preserved. All 11 verify gates green;
  conformance unchanged at 25/25. Pass 3 retro records G17 (sed
  delimiter collision — `|` clash with regex alternation, corrected
  to `#` mid-flight) and G18 (Class D stale-reference set sized:
  ~150 line hits across 30 stale segments; top item
  `framework/scripts/` with 60 refs; resolution deferred to a
  content-migration task per P3-T1 §Deferred R2).
- 2026-05-20T21:10:00Z — Completed P3-T3 (plugin scaffold).
  `.claude-plugin/plugin.json` (7 fields, minimal manifest);
  `VERSION` + `FRAMEWORK_SPEC_VERSION` both `0.1.0`; `README.md`
  expanded from 27-line placeholder to 82-line user-facing doc.
  Two implementation findings recorded: **Finding 1** (omit author
  block — in-container `git config user.name` returns `Claude`, not
  the repo owner; manifest's `repository` URL handles ownership
  signaling); **Finding 2** (no platform `CHANGELOG.md` — following
  Hermes precedent for symmetry; retrofit deferred). All 11 verify
  gates green; conformance 25/25 unaffected.
- 2026-05-20T21:55:00Z — Completed P3-T4 (Phase 3 verify). 22 gates
  ran across conformance, structure, content + coupling sweep,
  manifest validity, and integration-level checks. Mid-flight cleanup
  surfaced and removed **47 broken symlinks** the source `.claude/`
  carried (self-referencing pointers at `/opt/data/docs_flow_framework/
  .claude/skills/<name>` — leftovers from the old multi-project
  symlink consumption pattern). Post-cleanup file count is 171 =
  git = disk; audit math reconciles cleanly. All 22 gates green.
  Verify record at `plans/P3-T4-VERIFY.md`. Lesson for future port
  plans: add `find -type l` to the audit recon to surface symlinks
  upfront (P3-T0 + P2-T0/T2 audits missed this).
- 2026-05-20T22:40:00Z — Completed P3-T5 (Phase 3 close).
  `CHANGELOG.md` cut to `[0.4.0] — 2026-05-20` (full Phase 3 cycle
  — Added / Changed / Removed, plus a carried-known-issue note for
  the ~150 Class D stale refs); `ROADMAP.md` status `Phase 3 complete
  (v0.4.0) — Phase 4 next`; Phase 3 section ends with `Status:
  complete (v0.4.0, claude-code-plugin/v0.1.0)`; `docs/TAGGING.md`
  table appended (7 rows total). Close commit `087f7d5` pushed to the
  working branch. Annotated tags `v0.4.0` + `claude-code-plugin/v0.1.0`
  created locally on `087f7d5`; tag push 403'd as expected (third
  occurrence of the in-container 403 — P1-T8, P2-T6, P3-T5). Tag
  publication requires the user to run the local-clone workaround
  documented in `plans/P3-T5-PLAN.md` Implementation note. **Phase 3
  is structurally closed.**
- 2026-05-20T22:55:00Z — User published the two Phase 3 tags via the
  local-clone workaround. `git ls-remote --tags origin` now returns
  all 7 tags; `v0.4.0` and `claude-code-plugin/v0.1.0` both
  dereference to the close commit `087f7d5`. **Phase 3 is formally
  closed.** Next: Phase 4 (Conformance & Independence).
- 2026-05-20T23:45:00Z — Completed P4-T0 (Phase 4 audit + task
  breakdown). `plans/P4-AUDIT-conformance.md` assesses the platform-
  conformance contract (4 bullets: PC1+PC4 statically testable
  today, PC2+PC3 deferred to runtime exercise), the CI gap (no
  `.github/workflows/`; 3 greenfield workflows planned —
  conformance, Hermes, plugin), and the CHANGELOG/README/LICENSE
  gaps (both platforms lack `CHANGELOG.md`, Hermes README still
  Phase-0 placeholder, no repo-root `LICENSE`). 9 deferred items
  from P1/P2/P3 rolled up: 5 in-scope for Phase 4, 4 deferred
  further (content-design / already-done). Phase 4 shape is 5
  sub-tasks (T1 design → T2 conformance tests → T3 CI → T4
  retrofits+parity → T5 verify+close). 6 open questions for P4-T1.
  See `plans/P4-T0-PLAN.md` for the full breakdown.
- 2026-05-20 — Added `docs/STARTUP_HANDOFF.md` — distills business /
  startup ideas from the architectural decisions of the multi-platform
  migration: IPLAN-as-product, IPLAN corpus (D-0012 R2), engine-
  agnostic spec, domain profiles (post-v1.0), CHG governance-as-code
  (CHG-D1), ephemeral-session workflow tooling, migration as case
  study. Does not affect the migration's technical scope; ideas
  surfaced organically and are filed for a future strategy session.
- 2026-05-21T00:35:00Z — Completed P4-T1 (design, paper-only).
  6 questions resolved in `plans/P4-T1-DESIGN.md`. New conformance
  sub-package `tests/conformance/platforms/` with two modules
  (`test_version_declaration.py` + `test_engine_isolation.py`);
  suite grows 25 → 28-30. PC4 scope: runtime-significant
  directories only (`src/`, `pyproject.toml`, `.claude-plugin/`,
  `commands/`, `agents/`); documentary references in
  READMEs/docs/skills allowed. CI runner: `ubuntu-latest`;
  Python 3.12 via `actions/setup-python@v5`. CHANGELOG retrofit:
  minimal-honest (each platform's `[0.1.0]` mirrors the
  corresponding project release scoped to that platform). Hermes
  README: full mirror of P3-T3 plugin README. LICENSE: MIT (matches
  plugin manifest placeholder); copyright `vladm3105`. Q7
  confirmed no framework tag bump.
- 2026-05-21T01:20:00Z — Completed P4-T2 (platform conformance
  tests). New sub-package `tests/conformance/platforms/` with 6
  test methods across 2 modules: `test_version_declaration.py`
  (4 tests — PC1) + `test_engine_isolation.py` (2 tests — PC4
  with case-insensitive forbidden-token scan, scoped to runtime-
  significant directories per P4-T1 Q2). `_spec.py` extended
  additively. **Conformance suite: 25 → 31 tests, all green.**
  One implementation-time correction: initial `_spec.py` Edit
  failed silently (file not Read first) — caught by the ImportError
  in suite output; re-Read + re-Edit landed cleanly. Lesson: silent
  Edit failures are real; treat unexpected ImportErrors after
  "successful" Edits as suspect.
- 2026-05-21T02:15:00Z — Completed P4-T3 (CI workflows authored).
  Three greenfield workflows (`conformance.yml`, `hermes.yml`,
  `plugin.yml`) — all `ubuntu-latest`, Python 3.12 via
  setup-python@v5, concurrency cancel-in-progress, minimal
  `contents: read`. No carry-over from legacy. All 8 verify gates
  green; local smoke confirms commands work.
  **Implementation-time discovery — fifth in-container
  restriction:** the GitHub App credentials lack the `workflows`
  permission, so the in-container push of `.github/workflows/*.yml`
  is rejected. Workflow files staged at `plans/workflows-pending/`
  for the user to `git mv` into `.github/workflows/` from a local
  clone — exact commands in `plans/P4-T3-PLAN.md` Implementation
  note. (`docs/TAGGING.md` was extended in P4-T4 to document this
  restriction symmetrically with the tag-push restriction.)
- 2026-05-21T04:15:00Z — Completed P4-T5 (Phase 4 verify + close,
  combined per P4-T0 design). 13 gates ran green; one carried-
  known-issue surfaced (`api_runner.py:115` stale install
  instruction `pip install 'ucx_hermes[api]'`; correct is
  `hermes-server[api]` — 1-line fix deferred to Phase 5
  housekeeping per R5 scope). Close commit `954d8da` shipped;
  `CHANGELOG.md [0.5.0]` cut; ROADMAP marked; `docs/TAGGING.md`
  table grew to 8 rows. Annotated tag `v0.5.0` created locally;
  in-container tag push 403'd as expected (4th occurrence —
  P1-T8, P2-T6, P3-T5, P4-T5). Verify record at
  `plans/P4-T5-VERIFY.md`. **Phase 4 structurally closed.**
- 2026-05-21T04:30:00Z — User published `v0.5.0` from a local
  clone (initial push didn't land; the local tag existed and
  `git push origin v0.5.0` transmitted it). `git ls-remote --tags
  origin` now returns 8 tags; `v0.5.0^{}` dereferences to the
  close commit `954d8da`. **Phase 4 formally closed.** Project
  moves into Phase 5 (Cutover). Workflow relocation from P4-T3
  remains an independent pending user action.
- 2026-05-21T05:35:00Z — Completed P5-T0 (cutover audit + task
  breakdown). `plans/P5-AUDIT-cutover.md` inventories the two
  destructive removal targets (`legacy/` 28M/2275 files; root
  `.claude/` loader) and confirms **no runtime dependency** from
  the surviving tree on either. Classifies every cutover operation
  by reversibility × authority — the `main` replacement and all
  tag pushes are **user-only** (main is locked per docs/PROJECT.md
  §3; tags hit the 5th refs/tags/* 403). Recommends shipping
  `v1.0.0` with the documented plugin layer-model gap (content
  migration → post-v1.0). 6-task breakdown with confirmation gates
  on the destructive removals; root `.claude/` removal sequenced
  late (it disables the session's own hooks). 6 open questions for
  P5-T1. **The destructive steps and the main replacement will each
  be surfaced for explicit confirmation when reached.**
- 2026-05-21T04:45:00Z — Closed one of the two pending items:
  fixed `api_runner.py:115` stale install string
  (`ucx_hermes[api]` → `hermes-server[api]`; commit `23ae664`);
  Hermes suite 447/447, conformance 31/31; recorded in CHANGELOG
  `[Unreleased] Fixed`. The **workflow relocation remains
  user-only** — the in-container GitHub App lacks the `workflows`
  permission, so `.github/workflows/**` pushes are rejected; the
  files stay staged at `plans/workflows-pending/` until the user
  `git mv`'s them from a local clone (commands in
  `plans/P4-T3-PLAN.md`). The larger carried issues (plugin
  legacy-vs-new layer model; ~150 stale `framework/<X>` refs)
  are post-v1.0 content migrations, not quick completions —
  scoped into Phase 5 / post-v1.0.
- 2026-05-21T03:10:00Z — Completed P4-T4 (retrofits + parity
  report). Six artifacts landed:
  - `platforms/hermes/CHANGELOG.md` — Hermes `[0.1.0]` mirroring
    project `[0.3.0]` scoped content.
  - `platforms/claude-code-plugin/CHANGELOG.md` — plugin `[0.1.0]`
    mirroring project `[0.4.0]` scoped content.
  - `platforms/hermes/README.md` — expanded from 27-line
    placeholder to **113 lines** (mirrors P3-T3 plugin README
    structure: what's inside, install, MCP tool list, framework
    spec conformance section, platform info table, relationship-
    to-plugin section).
  - `LICENSE` at repo root — MIT, copyright `vladm3105` (matches
    plugin manifest `"license": "MIT"`).
  - `docs/PARITY.md` — 5-section capability comparison (matrix /
    operations / extras / known parity gap / choosing between).
    Honest about the **legacy-vs-new layer model gap**: plugin
    lacks `doc-tdd` + `doc-iplan`; has `doc-sys` / `doc-req` /
    `doc-ctr` / `doc-tspec` / `doc-tasks` from the legacy
    11-layer model. Hermes covers all 8 new-model layers via
    its generic `sdd_*` tools. Resolution deferred post-v1.0
    per P3-T1 §Deferred R2.
  - `docs/TAGGING.md` extended with an "In-container push
    restrictions" section documenting the tag + workflow
    restrictions symmetrically (per P4-T3 G15 recommendation).
  All 9 verify gates green; conformance still 31/31.

## Next steps

1. **P5-T2 — Remove `legacy/`** (`git rm -r legacy/`). **Destructive
   — confirm at execution.** Archive precondition met
   (`legacy-ucx-v3.2-read-only` protected). Then P5-T4 (finalize docs
   incl. CLAUDE.md rewrite + legacy-removal→archive-branch
   reconciliation), P5-T3 (remove root `.claude/` — **destructive +
   session-affecting, gated, LATE**), P5-T5 (verify), P5-T6 (close +
   cutover → `v1.0.0`).
2. **P5-T6 cutover is user-authorized:** `main` replacement =
   **force-replace** `main` with the working-branch tip (P5-T1 Q1 —
   FF impossible; lossless via the archive branch; lift main's branch
   protection, force-push, re-enable). Tags via user local-clone.

**Archive branch (done + protected):** `legacy-ucx-v3.2-read-only`
created off `main` (`491e8db`), read-only — preserves the pristine
pre-migration `ucx_framework` project. This is the precondition that
makes the P5-T2/T3 working-branch removals safe (verified: all 7
legacy trees + root `.claude/` present in the archive; caveat — the
archive's `.claude/` is the pre-migration one, the migration-era
hooks survive only in working-branch git history).

**Independent pending user actions** (carry-overs, do anytime):

- Relocate workflows: `git mv plans/workflows-pending/*.yml
  .github/workflows/` from a local clone (P4-T3; in-container
  can't push `.github/workflows/`).

**Plugin v0.2.0 launch — remaining user-only steps** (2026-05-23):

1. **Merge into `main`** — the migrated plugin (8-layer corpus, 9-agent
   roster, marketplace) lives only on `claude/multi-platform-migration-AamWB`,
   13+ commits ahead of `origin/main` (which is at the `v1.0.0` cutover). Until
   merged, `/plugin install` from the repo serves the **pre-migration** plugin.
2. **Push the release tag** from a local clone (in-container 403):

   ```sh
   git tag -a claude-code-plugin/v0.2.0 <release-commit> \
     -m "Claude Code plugin v0.2.0 — full 8-layer SDD model + marketplace install"
   git push origin claude-code-plugin/v0.2.0
   ```

3. **Relocate CI** (item above) so the plugin/conformance workflows actually run.
Verify the tag with `git ls-remote --tags origin`.

## Open questions

- None outstanding.

## Log

- 2026-05-18T00:00:00Z — Handoff record created.
- 2026-05-18T17:27:00Z — Added decision log + continuity hooks.
- 2026-05-18T17:45:00Z — Completed P1-T1 audit of `legacy/ucx_flow_v3/`.
- 2026-05-18T18:45:00Z — Added two-pass plan-review gate (D-0007).
- 2026-05-18T19:05:00Z — Completed P1-T2 layer extraction.
- 2026-05-18T19:40:00Z — Completed P1-T3 registry extraction.
- 2026-05-18T20:30:00Z — Completed P1-T4 governance + CHG extraction.
- 2026-05-18T21:25:00Z — Completed P1-T5 conformance suite; wrote
  `framework/README.md`.
- 2026-05-19T09:20:00Z — Completed P1-T6 `framework/VERSION` + tag convention.
- 2026-05-19T10:00:00Z — Completed P1-T7 root assembly; `framework/` fully
  assembled.
- 2026-05-19T10:45:00Z — P1-T8 Phase 1 close commit; release tags created
  locally.
- 2026-05-19T11:35:00Z — Tag push blocked (HTTP 403, `refs/tags/*`); added
  `docs/TAGGING.md`; corrected records — P1-T8/P0-T5 reopened.
- 2026-05-19T12:45:00Z — Recorded framework purpose + domain-profile
  direction (D-0012); project name set to `aidoc-flow`.
- 2026-05-19T13:10:00Z — Added D-0012 refinements R1 (IPLAN planned/executed
  states; criticality-scaled audit) and R2 (curated corpus as the unit of
  value; library/composition/freshness as post-v1.0 destination).
- 2026-05-19T13:50:00Z — Release tags `v0.1.0`, `framework/v0.1.0`, `v0.2.0`
  published from a local clone; Phase 1 closed; P0-T5 and P1-T8 done.
- 2026-05-19T14:25:00Z — Completed P2-T0 audit; mcp_ucx out of scope; P2-T1…T6
  defined and queued in `MIGRATION_TODO.md`.
- 2026-05-19T14:55:00Z — Completed P2-T1 design; D-0013 records the
  templates-single-source-of-truth rule.
- 2026-05-20T09:10:00Z — Completed P2-T2 port-verbatim copy (64 files,
  all verify gates green).
- 2026-05-20T09:25:00Z — P2-T0 audit scope-completeness correction (§5b):
  3 legacy-root Hermes files added to P2-T3 scope (`HERMES_UCX_RUNTIME_ENVIRONMENT.md`,
  `MULTI_PROJECT_QUICK_REFERENCE.md`, `MULTI_PROJECT_SETUP_GUIDE.md`);
  4 others classified drop / out-of-scope; Pass 4 retro recorded.
- 2026-05-20T10:15:00Z — Completed P2-T7: ported `hermes_agent_skills/`
  (181 files) into `platforms/hermes/agent-skills/`; §5b updated so the
  3 root-docs files are sourced via P2-T7, not double-ported via P2-T3;
  P2-T7 Pass 3 retro records implementation-time deviations.
- 2026-05-20T10:45:00Z — Remaining-tasks review: P2-T4 (spec-version
  declaration) folded into P2-T3; added P2-T8 (drop skill's template
  duplication, rewire to `framework/layers/`) to close D-0013 fully for
  the skill package. New order: T3 → T8 → T5 → T6.
- 2026-05-20T11:50:00Z — Drafted `plans/P2-T3-PLAN.md` (two review passes
  done). Plan recon surfaced an audit gap: 3 test files + 17 docs files
  carry `ucx_flow_v3` references that §3a/§3b missed. P2-T3 absorbs the
  scope (§3a-extension for tests; new §3c for docs, classified historical
  vs current-behavior per the P2-T7 G13 lesson) and lands the audit-doc
  correction inside its own step sequence. Awaiting approval to implement.
- 2026-05-20T12:50:00Z — Completed P2-T3 port-with-repoint: 200 files
  ported + 2 VERSION files; path-map applied across 18 edit-list files;
  11 historical docs preserved verbatim; pyproject + .mcp.json updated;
  audit §3a renamed and new §3c added. Conformance 25/25; Hermes tests
  397/447. Pass 3 retrospective records G18: plan's "no logic edits"
  Out-clause contradicted P2-T1 Q3 downstream which had pre-flagged
  required logic work. **Added P2-T9** to queue: rewire MCP scaffold
  runtime (`CANONICAL_SCAFFOLD_MAPPINGS`) to consume `framework/layers/`
  instead of the dropped `platforms/hermes/templates/`. Symmetric with
  P2-T8's skill-package rewire — could be merged.

## 2026-06-07 — LAYER-PLAYBOOKS-001 (BRD + PRD scope) shipped

Framework spec bumped to 0.14.0 (new artifact class: per-layer per-lens
playbooks). 11 playbook files across BRD (5 lenses) + PRD (6 lenses)
calibrate review-team findings; plugin v0.7.0 wires playbook injection
into doc-brd-audit + doc-prd-audit SKILLs.

Live BRD acceptance: PASS @ 93/100 with 5/7 (71%) findings citing
playbook checks. Chaos_engineer lens (lowest score 84) surfaced 3 new
gaps: capacity-exhaustion responses (C5), load-envelope completeness
(C2). Beyond-checklist captured 2 layer-specific concerns
(A2-assumption-capture, enumeration-abuse-case).

PR scope intentionally narrowed mid-execution from all 8 layers to
BRD + PRD only because 6 audit SKILLs (EARS/BDD/ADR/SPEC/TDD/IPLAN)
lack team-mode wiring. Each layer's team-mode + playbook injection
will land together in per-layer follow-up PRs.

Next: EARS-RT-001 (team-mode + 5 EARS playbooks), then BDD-RT-001,
ADR-RT-001, SPEC-RT-001, TDD-RT-001, IPLAN-RT-001 in sequence.

## 2026-06-08 — EARS-RT-001 shipped

Claude Code plugin 0.7.0 → 0.8.0 wires team-mode + playbook injection
into doc-ears-audit + doc-ears-fixer SKILLs. 5 EARS playbook files
landed (requirements_specialist 35, tech_lead 25, qa_lead 20,
chaos_engineer 12, security_engineer 8 — chaos-heavy 12:8 split per
REVIEW_CREWS.yaml).

Live EARS cascade ran 5 iterations. Two hand-fixes applied between
iterations to address P1 findings the playbook calibration surfaced:
(1) abuse-case event-driven + unwanted-pattern rule pairs (4 rules)
plus a metrics audit-log rule to satisfy security_engineer C1
(SE-001 resolved); (2) element-ID format normalization (5391a/5391b
→ 539a/539b) to satisfy the structural floor (STRUCT-001 resolved).

iter-5 terminal: score 84/100, blocking=0, security_engineer perfect
100/100, all P1s resolved. PARTIAL_TIMEOUT terminal at MAX_ITERATIONS;
the harness `timeout 3600s` (NOT internal SOFT_DEADLINE) caused the
initial iter-2 fixer to SIGKILL mid-execution; resumed manually via
saga.json edit + direct driver invocation; iter-3..5 ran via the
resumed driver. This validates the resume mechanism in two scenarios:
PARTIAL_TIMEOUT (iter-3 → iter-4) and BRANCH_COMPLETED (iter-2-fixer
SIGKILL recovery → iter-3 re-review).

playbook_coverage emitted for the first time in iter-4 + iter-5
verdicts: `{C1:2, C2:4, C3:1, C4:2, C5:6, beyond_checklist:1}`.

Next: BDD-RT-001 (next per-layer rollout). 4 more layer-RT-001 PRs
(ADR/SPEC/TDD/IPLAN) follow. Last one (likely IPLAN-RT-001) removes
the `@unittest.skip` from test_playbook_coverage.py per #258.

## 2026-06-08 — AUTO-REMEDIATE-001 shipped

`tests/scripts/test-acceptance.sh` extended to auto-remediate STY03
lint-smoke failures via `doc-<layer>-fixer` (single_pass mode) with a
synthetic audit verdict. 7 helper bash functions added (~80 lines),
plus a paired `tests/scripts/test-auto-remediate-helpers.sh` unit
test suite (13 tests, all passing).

Live validated end-to-end: EARS-01.md (2457 body words on main,
STY03-blocking) was auto-remediated by the framework's own fixer to
2250 body words (at the threshold; lint exit 0); cascade proceeded;
44/44 element IDs and 114/114 trace tags preserved per the fixer's
diff report. Total cascade runtime: 1114s (~18.5 min).

This work surfaced from BDD-RT-001 being blocked at lint-smoke
bootstrap on the post-EARS-RT-001 EARS-01.md state. The deeper
lesson — "Never hand-edit example artifacts; framework agents must
do remediation" — was codified into CLAUDE.md durable conventions

- memory entry `feedback_never_hand_edit_example_artifacts.md`.

Two follow-up items noted by the fixer:

- STY02 WARNING on EARS-01.md §3 Requirements (1420 words > 800
  target, < 1200 blocking) — out of scope for STY03-only run.
- `datetime.utcnow()` deprecation warning in `write_synthetic_verdict`
  — cosmetic; should migrate to `datetime.now(datetime.UTC)`.

BDD-RT-001 (#264) is now unblocked. Resuming: rebase `feat/bdd-rt-001`
onto current main + re-run the BDD cascade.

## 2026-06-08 — BDD-RT-001 + supporting fixes shipped

Three coordinated PRs landed in sequence:

- **PR #110 (STY03 fence-fix)** — `sdd_doc_lint` STY03 word-count now
  excludes code-fenced blocks (mirroring STY02 / AS3). BDD bodies are
  mostly fenced Gherkin (`doc-bdd` allows ~50k tokens of it) and would
  trip the blocking 2250-word threshold otherwise. Surfaced by
  `doc-bdd-autopilot` mid-cascade, which correctly diagnosed the
  framework workflow gap per the *Never hand-edit example artifacts*
  rule and refused to manually trim the BDD body.
- **PR #111 (SAGA-BUDGET-001)** — three coordinated constants bumped
  60 → 90 min: `ORCHESTRATOR_TIMEOUT` 3600→5400 (`test-acceptance.sh`),
  `SOFT_DEADLINE_SECONDS` 3300→5100 (`tools/saga_driver.py`, byte-parity
  synced via `tools/sync-plugin-framework.sh`), `MAX_LAYER_SEC`
  3600→5400. Preserves the 300s graceful-exit margin. BDD-RT-001 run #2
  converged to PASS in 58:38 — within 1:22 of the old 3600s ceiling —
  so future ADR/SPEC/TDD/IPLAN cascades (larger artifacts) needed the
  headroom.
- **PR (BDD-RT-001 itself)** — framework `0.14.1 → 0.14.2` + plugin
  `0.8.0 → 0.9.0`. 6 BDD playbooks at `framework/playbooks/04_BDD/`
  (qa_lead 35 / tech_lead 25 / chaos_engineer 14 / operator 10 /
  auditor 10 / security_engineer 6 = 100); `doc-bdd-audit` +
  `doc-bdd-fixer` SKILLs wired for team-mode dispatch + playbook
  injection + saga interaction (mirrors EARS-RT-001 / PRD-RT-001
  pattern). **Live BDD acceptance: PASS at score 95/100** (cascade-2
  verdict.json `combined_status: PASS`). Score trajectory: 80 → 88 →
  95 across 3 audit cycles; 2 clean fixer cycles (no regression P1
  introduced); 6/6 lens coverage quorum throughout; parallel
  fan-out confirmed in every audit cycle by saga journal.

Per-lens scores at iter 3:

  qa_lead 95 · tech_lead 100 · chaos_engineer 86 · operator 95 ·
  auditor 100 · security_engineer 92

Test evidence committed:
`examples/url-shortener/docs/04_BDD/BDD-01.md` (32 scenarios, 5 EARS
categories), `examples/url-shortener/.aidoc/review/04_BDD/BDD-01/`
(6 lens slots + verdict.json + report.md + saga.json with 44
transitions across 3 audit + 2 fixer cycles + 2 fix reports),
`examples/url-shortener/.aidoc/audit/04_BDD-audit.md` (combined
unified audit).

Next: per-layer rollouts ADR-RT-001, SPEC-RT-001, TDD-RT-001,
IPLAN-RT-001 (tasks #265-268). After those land, the final per-layer
PR removes the `@unittest.skip` from `test_playbook_coverage.py`
(task #258) to assert all 45 playbooks present.

## 2026-06-09 — ADR-RT-001 shipped

ADR layer team-mode + playbook injection landed. Framework spec
`0.14.2 → 0.14.3` (PATCH: 6 ADR playbooks under
`framework/playbooks/05_ADR/`). Plugin `0.9.0 → 0.10.0` (MINOR:
`doc-adr-{audit,fixer}/SKILL.md` wiring).

ADR crew is the first to weight security over chaos (12 > 8) per
the REVIEW_CREWS.yaml rationale — ADRs encode trust boundaries,
authn/authz choices, and crypto decisions. Lens→agent map binds
both `architect` and `tech_lead` to `solutions-architect`, with
the brief specifying which lens to apply at dispatch time
(established pattern from SPEC/TDD layers).

**Live ADR acceptance: PASS at score 90/100** (cascade-1, iter 2).
Wall-clock **43:48** — well within the SAGA-BUDGET-001 5400s
ceiling; saga reached `CLOSED` cleanly (no SIGTERM at the wire,
unlike BDD-RT-001 cascade-2 which finished mid-finalize). Faster
convergence than BDD-RT-001 too (2 audit + 1 fixer vs 3 audit + 2
fixer) — likely the security-heavy crew catches more on iter 1.

Per-lens scores at iter 2:

- architect 95
- tech_lead 85
- chaos_engineer 82
- security_engineer 91
- operator 82
- auditor 100

**First observed team-mode patch-validation cycle** across all
per-layer rollouts: the iter 1 fixer dispatched `security_engineer`
as a Task subagent in patch-validation mode, producing
`security_engineer.fix_1.json` per the SKILL's `BRANCH_COMPENSATING`
contract. BDD-RT-001 had no P0/P1s so the fixer ran fully
deterministic; ADR exercised the team-mode validation cycle
end-to-end.

Saga journal: 35 transitions, all 12 per-branch
`BRANCH_RUNNING`/`BRANCH_COMPLETED` pairs stamped same-second
(parallel fan-out × 2 iters).

Test evidence committed:
`examples/url-shortener/docs/05_ADR/ADR-01.md` (365 lines,
lint-clean), `examples/url-shortener/.aidoc/review/05_ADR/ADR-01/`
(6 per-lens slots + 1 fix-validation slot + verdict.json +
report.md + saga.json + F_fix_report_v001),
`examples/url-shortener/.aidoc/audit/05_ADR-audit.md`.

Next: SPEC-RT-001 (task #266) — SPEC layer crew is the
equal-weight split (chaos 10 / security 10), continuing the
per-layer rollout sequence.

## 2026-06-09 — SPEC-RT-001 shipped (+ three infrastructure PRs)

SPEC layer team-mode + playbook injection landed. Framework spec
`0.15.0 → 0.15.1` (PATCH: 5 SPEC playbooks under
`framework/playbooks/06_SPEC/`). Plugin `0.10.2 → 0.11.0` (MINOR:
`doc-spec-{audit,fixer}/SKILL.md` wiring).

SPEC crew is the smallest of any layer (5 lenses, no operator and no
auditor) and the first equal-weight chaos/security split (10 / 10) —
SPEC specifies both performance/resilience and security controls.
`integration_lead` first appears at SPEC, binding to
`solutions-architect` (third lens sharing that agent alongside
architect + tech_lead).

**Live SPEC acceptance: PASS at score 97/100** (cascade-4, iter 2).
Wall-clock 3042s (50:42). Saga reached `CLOSED` cleanly.
**Score trajectory 79 → 97 in one fixer cycle** (+18 points).
Per-lens at iter 2: architect 100 / tech_lead 95 / integration_lead 96 /
chaos_engineer 93 / security_engineer 100.

### Three infrastructure PRs surfaced and resolved during SPEC-RT-001

- **PR #110 (STY03 fence-fix)** — `sdd_doc_lint` STY03 now excludes
  code-fenced blocks, mirroring STY02 / AS3.
- **PR #111 (SAGA-BUDGET-001)** — saga driver wall-clock budget
  60 → 90 min (coordinated `ORCHESTRATOR_TIMEOUT` / `SOFT_DEADLINE_SECONDS` /
  `MAX_LAYER_SEC` bump preserving the 300s graceful-exit margin).
- **PR #115 (synthesizer check-schema + saga events)** — synthesizer
  contract now requires `check` per finding (new conformance test
  enforces); saga driver stamps `dispatch:<phase>` / `complete:<phase>`
  events to a new `saga.events[]` field.
- **PR #117 (SAGA-DETERMINISM-001)** — saga driver's new
  `reconcile_post_audit` walks `saga.status` deterministically when
  the audit SKILL's LLM stochastically skips per-branch transition
  stamping. Architecturally completes the cooperative→preemptive
  migration. 6 unit tests including regression on captured SPEC
  saga.json fixture.

All four PRs landed before the SPEC-RT-001 cascade-4 run, which
converged to PASS @ 97 with 10 reconciled transitions (PR #117
firing), 100% `findings[*].check` preservation (PR #115 contract),
8 saga.events (PR #115 instrumentation), clean fixer + team-mode
patch-validation slot (`chaos_engineer.fix_1.json` for the iter-1
P1).

### Worktree-isolation pattern

Mid-cascade branch confusion from a concurrent session was
hijacking SPEC cascade runs by switching the on-disk SKILL files.
Mitigation: cascade runs in a `git worktree add` worktree pinned to
`feat/spec-rt-001`. Git enforces the one-branch-one-worktree rule,
so the worktree's files are immune to primary-checkout branch
changes. Apply to all long-running cascade verifications going
forward.

### Test evidence committed

`examples/url-shortener/docs/06_SPEC/SPEC-01.md` (lint-clean);
`examples/url-shortener/.aidoc/review/06_SPEC/SPEC-01/` (5 per-lens
slots + chaos_engineer.fix_1.json patch-validation slot +
verdict.json + report.md + saga.json with 17 transitions including
10 reconciled + F_fix_report_v001);
`examples/url-shortener/.aidoc/audit/06_SPEC-audit.md`.

Next: TDD-RT-001 (task #267). TDD's crew is qa_lead / tech_lead /
chaos_engineer / security_engineer / operator / auditor (6 lenses,
mirrors BDD/ADR layout). Should be the cleanest per-layer rollout
yet — all the framework defects discovered during SPEC are now
fixed on main.

### 2026-06-11 — CLEANUP-PR-A (harness + lint workflow hygiene)

First child PR of FRAMEWORK-CLEANUP-001 (master plan PR #128, merged `528d6f23`).
Closes `plans/FRAMEWORK-TODO.md` items #1-4. Plugin PATCH 0.14.0 → 0.14.1.
Plumbing only — no spec change.

- Item 1: `--skip-lint-smoke` flag in `tests/scripts/test-acceptance.sh` (replaces deprecated env-var)
- Item 2: "Cleanup-then-cascade pattern" subsection in `tests/ACCEPTANCE.md`
- Item 3: DO-NOT-EDIT banners on canonical vendored Python modules + `_VENDORED.md` README
- Item 4: 18 audit + fixer SKILL prompts gain MD056 table-pipe-escape guidance

FRAMEWORK-CLEANUP-001 backlog: 13 open / 5 closed. Next: PR-C in parallel, then PR-B, then PR-D, then PR-E.

### 2026-06-11 — CLEANUP-PR-C (spec / registry / template hygiene)

Second child PR of FRAMEWORK-CLEANUP-001 (master plan PR #128, merged `528d6f23`).
Closes `plans/FRAMEWORK-TODO.md` items #11-14.
Framework MINOR 0.17.1 → 0.18.0; plugin MINOR 0.14.1 → 0.15.0.

- Item 11: iteration cap elevated to spec + project-tunable knob
- Item 12: `@threshold:` ID pattern in registry + strict TH01 lint
- Item 13: SPEC + IPLAN element-ID exemption formalized in ID_NAMING_STANDARDS
- Item 14: EARS `@bdd:` downstream slot formalized as optional + non-canonical

FRAMEWORK-CLEANUP-001 backlog: 9 open / 9 closed. Next: PR-B (review-quality calibration, 6 items) or PR-E (IPLAN subtypes, 1 item).

### 2026-06-11 — CLEANUP-PR-B (review-quality calibration, the heart)

Third child PR of FRAMEWORK-CLEANUP-001 (master plan PR #128, merged `528d6f23`).
Closes `plans/FRAMEWORK-TODO.md` items #5-10 — the highest-impact child PR.
Framework MINOR 0.18.0 → 0.19.0; plugin MINOR 0.15.0 → 0.16.0.

- Item 5/6: CLAUDE.md gains Corpus cross-check + Empirical pass-count guidance
- Item 7: TDD auditor playbook C4/C1/Reasoning frame updated to necessary-upstream
- Item 8 (HIGH): 13 playbooks gain No-findings rationale section (calibration fix)
- Item 9: 9 audit SKILLs strip self-claimed scores before lens fan-out
- Item 10: 9 audit SKILLs + synthesizer agent get fixer_introduced detection

FRAMEWORK-CLEANUP-001 backlog: 4 open / 15 closed. Next: PR-D (decomp + threshold gates; needs DECISION-GATE-D) and PR-E (IPLAN subtypes, smallest) and PR-F (doc-number independence; deferred per user).

### 2026-06-11 — CLEANUP-PR-E (IPLAN sub-types)

Fourth child PR of FRAMEWORK-CLEANUP-001 (master PR #128). Closes item #17.
Framework PATCH 0.19.0 → 0.19.1; plugin PATCH 0.16.0 → 0.16.1.
FRAMEWORK-CLEANUP-001 backlog: 3 open / 16 closed. Next: PR-D (decomp+threshold gates; needs DECISION-GATE-D) and PR-F (#18 doc-num; user-deferred).

### 2026-06-11 — CLEANUP-PR-D (decomp + threshold gates) — FINAL child PR

Fifth and final child PR of FRAMEWORK-CLEANUP-001 (master PR #128).
Closes items #15-16; opens #19 (Option B future). DECISION-GATE-D
resolved as Option A (subsection in PRD). Framework MINOR 0.19.1 → 0.20.0;
plugin MINOR 0.16.1 → 0.17.0.

FRAMEWORK-CLEANUP-001 backlog after PR-D: 2 open (item #18 doc-num user-deferred + item #19 Option B future) / 18 closed.
The workstream's planned 17 items are 100% addressed; items 18 + 19 are deferred follow-ups, not gaps in the original scope.

### 2026-06-11 — CLEANUP-PR-F (doc-number independence)

Single-item follow-up PR closing item #18. Framework PATCH 0.20.0 → 0.20.1; plugin PATCH 0.17.0 → 0.17.1.
FRAMEWORK-TODO state: 1 open (item #19 Option B 02b_DECOMP, user-deferred) / 19 closed.

### 2026-06-12 — CHG-RT-001 (CHG layer to per-layer parity)

CHG (Change Management overlay) brought to per-layer parity with the 8 SDD
layers, mirroring the EARS-RT-001 through IPLAN-RT-001 pattern. Framework
MINOR 0.20.1 → 0.21.0; plugin MINOR 0.17.1 → 0.18.0. Static work landed
(crew + 6 playbooks + 3 SKILL rewrites + saga driver + conformance
extensions); 120/120 conformance + 47/47 unit. Live CHG cascade
verification next.

### 2026-06-14 — SUPPORT.md go-live sync (operations IPLAN-0009 PR 3)

`docs/SUPPORT.md` updated to reflect that the Contact-us channel is **live**
with a Google Form ↔ Sheet ↔ Drive MCP architecture (replacing the prior
"stubbed / coming in v2" language). The simplified design — Forms + Sheet +
Drive MCP poll + Python prefilter + Haiku 4.5 LLM classifier; no
auto-acknowledgment; one-way form — is owned by the operations repo (PR
[#23](https://github.com/vladm3105/aidoc-flow-operations/pull/23) plan +
PR [#24](https://github.com/vladm3105/aidoc-flow-operations/pull/24) impl;
OPS-0039). This framework PR is the docs-only sync. No VERSION change
(documentation update only). No conformance impact.
