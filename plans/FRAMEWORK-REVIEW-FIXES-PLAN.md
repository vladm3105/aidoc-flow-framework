# FRWK-REVIEW Plan — framework/ pre-production review fixes

| Field      | Value                          |
|------------|--------------------------------|
| Task       | FRWK-REVIEW                    |
| Depends on | GATE-SPEC / CHG-D1 (D-0020); framework spec `0.3.2` |
| Status     | REVIEWED (Pass 1–2) — awaiting decisions D1–D6 |
| Feeds      | a cleaner, security-hardened `framework/` spec; possible `framework/v0.4.0` |

## Objective

Resolve the 13 findings from the `framework/` pre-production review — broken
traceability tags, cross-doc drift (stale "5-gate", emergency-SLA contradiction,
enum/downstream/index inconsistencies), the missing GATE-SPEC approval surface,
the security-posture gaps (no untrusted-input / prompt-injection guidance,
warning-only CVE, unsanitized diagram handlers), and the off-charter bloat in
`THRESHOLD_NAMING_RULES.md`. Conformance is already green; these are the
human-eye issues it can't catch. Every `framework/` edit is a GATE-SPEC change,
so the work lands as versioned, CHANGELOG'd, conformance-gated batches.

## Scope

**In:** findings #1–#13 (numbering from the review), grouped into batches below.
A conformance guard is added (in `tests/`, not `framework/`) so the traceability
fix can't regress.

**Out (explicitly deferred unless promoted by a decision):**
- The larger BRD/PRD **trim** (#7 bloat side) — high-effort content edit, low
  risk; do the cheap SPEC *expansion* now, defer the BRD/PRD trim.
- Building branch-protection / repo-settings (the human half of any new gate) —
  repo settings, user-only.

## Approach

### Versioning & PR structure

Each batch touches `framework/` → GATE-SPEC requires a `framework/VERSION` bump +
`CHANGELOG` + both `FRAMEWORK_SPEC_VERSION` + the 54-skill `framework_spec_version`
ripple. To bound the ripple churn, **land in two PRs**:

- **PR-1 = Batch 1 + Batch 2** → one **minor** bump `0.3.2 → 0.4.0` (corrections +
  additive security guidance; backward-compatible).
- **PR-2 = Batch 3** (THRESHOLD de-bloat) → its own bump, **minor or major per
  decision D3** (removing content can be breaking), kept separate so its semver
  and any deprecation note stand alone.

### Batch 1 — correctness

- **#1 (headline) Traceability tags in SPEC/TDD/IPLAN.** Rewrite the trace-tag
  *examples* to the registry's 4-segment element convention
  (`DOC.NN.SS.xxxx`, matching `EARS-TEMPLATE.yaml:124`), replacing the
  document-level/malformed forms (`SPEC-TEMPLATE.yaml:71,119,165-176`;
  `TDD-TEMPLATE.yaml:114,134,254`; `IPLAN-TEMPLATE.yaml:36`). **Root-cause #K:**
  restore the `id_standard` (+ `lifecycle`, `_antipatterns`) blocks that layers
  1–5 carry but 6–8 dropped, so the convention is in-template.
- **#2** "5-Gate" → "6-gate" / "gate system" in `GATE_INTERACTION_DIAGRAM.md:15,20`
  and `GATE_ERROR_CATALOG.md:15` (catalog already lists GATE-SPEC in §6b).
- **#3** Emergency post-mortem SLA — **resolve to 48h** (the CHG-TEMPLATE mandate,
  decision D1): fix `GATE_ERROR_CATALOG.md:167` (EMG-E004 72h→48h) and
  `GATE_INTERACTION_DIAGRAM.md:201` ("24-72h" → "within 48h").
- **#4** Index/enum drift: standardize the PRD-index status enum + EARS-index
  syntax to match their templates; **document** the `08 .yaml` vs `01–07 .md`
  index split in `LAYER_REGISTRY.yaml` (decision D6: document vs unify).
- **#5** BDD downstream: add `TDD` to the BDD template's note as an explicit
  *cross-reference* (not a registry `downstream`) and keep registry
  `downstream: [ADR]`; fix the `BRD-XS-002 → 004` numbering gap.
- **#6** `GATE_APPROVAL_FORM.md`: add a **GATE-SPEC** validation block (E001–E008),
  the `spec` change-source, and `semver_impact` (`:29` Entry-Gate row + a §2.6).
  `POST_MORTEM-TEMPLATE.md:117`: add "spec" as a root-cause locus.
- **#7 (cheap half)** Expand `SPEC-TEMPLATE.yaml`: add an `_antipatterns` block, a
  `diagram:` stub, and multi-interface/versioning guidance — bring the
  contract layer up to the depth of its peers.

### Batch 2 — security

- **#8** New `framework/governance/SECURITY_REVIEW.md` (engine-agnostic): rules
  for agent-authored artifacts/profiles — secret-leakage scan, injected-instruction
  / prompt-injection review, provenance. Referenced from `DOC_GOVERNANCE_CORE.md`
  and the gates. *(Adding a governance file ⇒ update `test_governance.py`
  `EXPECTED_FILES` and confirm it passes `test_spec_hygiene` — engine-agnostic.)*
- **#9** Strengthen external-dependency **CVE enforcement** — decision D2. Default:
  add a **new blocking** `GATE-03-E008` for *external* changes (keep `W001`).
  Note this *tightens* the gate (a previously-passing external change now needs a
  CVE ref), so it's borderline-breaking; documented as a strengthened check.
- **#10** `DIAGRAM_STANDARDS.md`: add a sanitization rule for mermaid
  `click "<path>"` handlers + inline HTML (`:159-168`).
- **#11** Add a **GATE-SPEC** security/abuse-review check (W or E) — spec changes
  reach both platforms.

### Batch 3 — THRESHOLD de-bloat + minor

- **#12** Trim `THRESHOLD_NAMING_RULES.md` (909→~350) to the engine-agnostic
  naming/tag/boundary core. Per decision D3: **genericize** the domain-specific
  financial examples (KYC tiers, B2B/B2C → neutral placeholders) *in place*, and
  **delete** the runtime/ops machinery (env-override matrices, "60-seconds"
  propagation, approver-role tables) — out-of-charter for a spec that "ships no
  runtime", with a CHANGELOG note that such policy belongs in a consuming
  project's own config (there is no in-repo profile to relocate it to). Fix the
  stale "UCX Flow Team" / 2025-12-16 provenance.
- **#13** Drop or footnote the drift-prone `total_sections` counters; align the
  P0/P1 vs P1-only severity vocabulary.

### Conformance guard (tests/, no bump)

Add `tests/conformance/` checks: (a) every `@tag:` *example* in a layer template
has the right **segment structure** for its level — element-level tags carry 4
dot-segments like the lower layers, **placeholder-aware** (normalize `NN`/`SS`/
`xxxx` tokens before matching, since the literal registry regex requires real
digits/hex and would false-fail on template placeholders) — so SPEC/TDD/IPLAN
can't regress to document-level tags (catches #1); (b) no `5-gate`/`five-gate`
string remains in `framework/governance/chg/` (catches #2); (c) the emergency
post-mortem SLA value is identical across the CHG docs (catches #3).

## Step sequence

1. **Plan + review** (this doc; ≥2 passes) and resolve open decisions D1–D6.
2. **Batch 1** edits → add conformance guards → run conformance + `spec_gate`
   (VERSION+CHANGELOG bumped) → commit per logical change.
3. **Batch 2** edits → conformance → commit.
4. **Close PR-1:** bump `0.3.2 → 0.4.0` (VERSION + 2 FSV + 54 skills) + CHANGELOG;
   verify GATE-SPEC green; push; PR.
5. **Batch 3** on a second branch **cut from `main` after PR-1 merges** (so the
   shared VERSION / FSV / CHANGELOG / 54-skill files don't collide with PR-1) →
   bump per D3 + CHANGELOG; verify; PR-2.
6. **Land**; refresh `framework/governance/DECISIONS.md` (a GD entry for the
   security-review addition if warranted) + HANDOFF.

## Verification

- `python3 -m unittest discover -s tests/conformance` green at every step
  (+ the 3 new guards).
- `python3 tests/chg/spec_gate.py --base origin/main` passes per PR (framework
  changed ⇒ VERSION + CHANGELOG bumped).
- `pre-commit run --all-files` clean (note: `framework/` is excluded from the
  style hooks; the skill-frontmatter ripple is frontmatter-only).
- Versions aligned: `framework/VERSION` == both `FRAMEWORK_SPEC_VERSION`.
- Manual: trace-tag examples in SPEC/TDD/IPLAN now match `EARS`/registry; the
  GATE_APPROVAL_FORM can document a `spec`/GATE-SPEC change end-to-end.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | #1 trace-tag rewrite introduces a different inconsistency | Add the conformance guard *first*; diff SPEC/TDD/IPLAN tags against the EARS/ADR exemplars. |
| R2 | #9 (CVE warning→blocking) is a breaking governance-rule change | Add a *new* blocking code for external deps rather than reclassifying W001; flag as decision D2; document in CHANGELOG. |
| R3 | #12 THRESHOLD trim removes content a platform consumes | Decision D3: relocate (not delete) domain/ops content; grep both platforms for `@threshold`/KYC usage before cutting; deprecation note. |
| R4 | Engine-token hygiene — new security/THRESHOLD text must stay engine-agnostic | No platform names; run `test_spec_hygiene` after each edit. |
| R5 | 54-skill ripple churn across two PRs | Bound to two bumps (1+2 combined, 3 separate); scripted ripple. |
| R6 | GATE-SPEC self-gating — these framework PRs must themselves pass GATE-SPEC | Each PR bumps VERSION + CHANGELOG (E005/E008) by construction. |
| R7 | PR-2 conflicts with PR-1 on the shared version/CHANGELOG/skill files | Cut PR-2's branch from `main` *after* PR-1 merges (sequenced, not parallel). |

## Open decisions (need a steer before implementing)

- **D1 — Emergency SLA:** standardize on **48h** (template mandate). *(default: yes)*
- **D2 — CVE enforcement:** add a **new blocking** `GATE-03-E008` for external-dep
  changes. It *tightens* the gate (borderline-breaking) — accept as a documented
  strengthened check (default), or keep CVE a warning?
- **D3 — THRESHOLD content:** **genericize** the financial examples in place +
  **delete** the runtime/ops sections (default) — vs keep them. (No in-repo
  profile exists to relocate to.)
- **D4 — #7 scope:** expand SPEC now (cheap), **defer** the BRD/PRD trim. *(default)*
- **D5 — PR/bump structure:** PR-1 = Batches 1+2 at `0.4.0`; PR-2 = Batch 3
  separate (sequenced). *(default)*
- **D6 — Index extension:** **document** the `08 .yaml` split in the registry
  (vs converting IPLAN's index to `.md`). *(default: document)*

## Review log

### Pass 1 — 2026-05-24

- **Conformance guard would false-fail on placeholders.** The naive "match the
  registry element regex" check rejects valid template placeholders
  (`BRD.NN.07.xxxx` — `NN`/`xxxx` aren't digits/hex). Rewrote guard (a) to be
  placeholder-aware / segment-structure-based.
- **New governance file has conformance ripples.** #8's `SECURITY_REVIEW.md`
  must be added to `test_governance.py` `EXPECTED_FILES` (exact-set check) and
  pass `test_spec_hygiene`. Noted.
- **"Relocate to a consuming-project profile" had no target** — there is no
  in-repo consuming project. Reframed #12/D3 to genericize-in-place + delete the
  ops sections with a CHANGELOG pointer.
- **PR ordering.** PR-2 shares the version/CHANGELOG/skill files with PR-1; cut
  PR-2 from `main` after PR-1 merges (added step 5 wording + R7).
- **D2 honesty.** A new blocking check still tightens the gate (borderline
  breaking); reflected in the decision text rather than calling it purely additive.

### Pass 2 — 2026-05-24

- **Semver in 0.x.** `0.3.2 → 0.4.0` (minor) is right for corrections + additive
  guidance; the only items that could argue "breaking" (D2 CVE-blocking, D3
  content removal) are isolated to PR-2 / flagged decisions, so PR-1 stays a
  clean minor. No change.
- **Trace-tag fix vs existing artifacts.** `framework/` ships only templates (no
  instance artifacts), so rewriting trace-tag *examples* breaks nothing already
  generated; the guard is added *after* the fix so the suite stays green. No change.
- **Skill ripple.** Kept (consistent with prior bumps; scripted) — bounded to two
  bumps total. No change.
- No further findings — plan is implementable pending decisions D1–D6.
