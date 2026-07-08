# PROVISIONAL-IDS-002 Plan — Model-2 content-hash enforcement, Phase 1: formalize the hash-input contract + build `rehash --check` (deterministic drift/mismatch verifier), advisory + round-trip-proven

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | PROVISIONAL-IDS-002 (Phase 1 of the Model-2 build) |
| Type           | feat (new deterministic verifier + spec contract) |
| Status         | DRAFT — 2026-07-07                          |
| Depends on     | D-0061 (the Model-2 decision + the honesty-scoping interim, framework 0.34.2) |
| Feeds          | element IDs gain a real content-drift signal (the payoff of Model 2); refines the D-0061 "unverified until `rehash --check`" scope to "**verifiable on demand** via the opt-in `rehash --check` command" — NOT "verified," since Phase 1 does not run the check on the corpus and the corpus IDs stay unreconciled until Phase 2 |
| Version impact | framework spec **MINOR** (`0.34.2 → 0.35.0`) — a new normative rule (`IDDRIFT01`) + the formalized hash-input contract. Verifier code in `tools/` (vendored); the `framework/**` GATE-SPEC change is the contract doc. Both `FRAMEWORK_SPEC_VERSION` pointers auto-re-match; plugin + Hermes product versions unchanged. |

## Objective

D-0061 chose **Model 2** — enforce the content-hash as a **content-drift identifier** with
stable IDs. The element ID embeds `SHA256("{doc_id}:{section_id}:{title}:{description}")[:4]`;
that hash **is** the mint-time content fingerprint, so a mismatch between the ID's hash and
`SHA256(current content)` = the element's content **drifted** since its ID was minted. The
honesty-scoping (D-0061) said IDs are "unverified until `rehash --check`." This builds
`rehash --check`.

**This is a large, multi-phase build.** Two facts make a big-bang risky and gate the phasing:

1. **The exact hash input is under-specified.** The authority (`ID_NAMING_STANDARDS.md`)
   documents the algorithm shape (`hashlib.sha256(input)[:4]`) but **not the normalization** —
   "title/description: first 100 chars, lowercased, special chars removed" lives only in the
   BRD *template*. A reproducible verifier needs the normalization formalized byte-exactly in
   the authority.
2. **The current corpus IDs are LLM-generated, not real hashes** — the corpus declares no
   `id_state` (defaults `canonical`), so it *claims* content-hashes it doesn't have. Running a
   verifier as a *gate* over it today would flag nearly every element. So enforcement + corpus
   reconciliation must be a **later phase**, not Phase 1.

**Phase 1 (this plan)** delivers the foundational, low-risk, verifiable core: the formalized
contract + `rehash --check` as an **explicit opt-in command** (NOT wired into the default lint
gate → zero corpus disruption, deterministic lint byte-identical), implemented for the **BRD
FR element form** as the reference, and **proven by round-trip fixtures** (compute a correct
hash → verify it passes; perturb the content → verify drift is detected). This proves the
mechanism + nails the contract; broad enforcement + reconciliation follow.

## Scope — Phase 1

**In:**

1. **Formalize the hash-input contract (the authority) — two byte-exact halves.** In
   `framework/governance/ID_NAMING_STANDARDS.md`, pin BOTH the **input assembly** and the
   **field normalization** as **normative, ordered, testable** operations (not examples — this
   is the load-bearing spec; the verifier and any future generator/`--fix` MUST apply it
   identically):
   - **(1a) Normalization transform (pinned, supersedes the ambiguous template prose "special
     chars removed").** Each of `title` and `description` is normalized by this exact ordered
     transform: **NFC → casefold(lowercase) → strip every char not in `[a-z0-9 ]` → collapse
     runs of whitespace to one space → trim ends → take the first 100 characters.** *(Anglocentric
     limitation acknowledged: this deletes non-Latin scripts entirely, so two distinct non-ASCII
     titles can normalize to the same string and collide on the 4-hex prefix — the collision rule
     `[:8]` and MINOR-1's edge fixture make that behavior explicit and intended for Phase 1; a
     Unicode-category strip is a Phase-2 option.)*
   - **(1b) Description extraction boundary (byte-exact).** A BRD §7 FR bullet is
     `- **<ID> — <Title>** (band): <description…>` and the description **wraps across
     continuation lines**. Define the captured `description` precisely: text after the closing
     `**` (and after an optional `(band):` prefix — the band token and its colon are stripped),
     then **accumulate continuation lines until the next FR bullet, a blank line, or a
     lower-level label** (e.g. `Acceptance criteria:`), joining with single spaces. The captured
     `title` is the text between `—` and the closing `**`. This boundary IS part of the
     contract — an implementation that stops at the first line vs. the wrapped body produces a
     different hash. Migrate the normalization out of the BRD template into the authority; the
     templates cross-ref it.
2. **Build `rehash --check` (deterministic verifier).** In `tools/sdd_doc_lint/` (vendored) or a
   `tools/rehash.py` invoked as an explicit command: for each **BRD §7 FR element**, extend the
   FR scanner to **capture the `title` and multi-line `description` per Scope 1b** (`_FR_BULLET`
   today captures only the ID — the title is matched but not captured, and the description is not
   in its match at all, so this is a genuine new multi-line parse, not a one-line tweak),
   recompute the normalized hash, and compare to the ID's embedded hash. On mismatch emit
   **`IDDRIFT01`** — "element `<ID>`'s content no longer matches its ID hash (drift, or a
   canonical leak); re-canonicalize or mark `id_state: provisional`." **Advisory** (warning).
   **Gated to `id_state: canonical` docs** (a `provisional` doc's IDs aren't claimed to be
   hashes → exempt) and **only run on the explicit `rehash --check` command — NOT part of the
   default `sdd_doc_lint <docs>` pass**, so the default gate + corpus lint are byte-identical.
   **Scope of coverage within a BRD (stated, not silent):** `scan_fr_elements` sees **only §7
   Functional-Requirement bullets** — other element-bearing BRD sections (e.g. §4 constraints
   carrying `BRD.NN.SS.xxxx` IDs) are **NOT** verified in Phase 1 and remain unverified; the
   authority wording (Scope 4) must say so.
3. **Round-trip + extraction fixtures + tests** (`tools/sdd_doc_lint/tests/` + `tests/conformance/`):
   (a) a BRD fixture whose §7 FR IDs are the **correctly-computed** hashes (`rehash --check` →
   clean); (b) a perturbed copy (title/description edited, ID unchanged) → **`IDDRIFT01`**;
   (c) a `provisional` doc → exempt; (d) a **normalization-edge** fixture (unicode/special
   chars/>100 chars) proving the transform is byte-stable **and** that the anglocentric strip
   behaves as documented; (e) an **extraction** fixture (multi-line wrapped description, band
   vs. no-band prefix, a colon inside the description) asserting the exact `(title, description)`
   bytes captured — this is distinct from (d): (d) proves the *transform* is deterministic given
   an input, (e) proves the *extraction* yields the correct input bytes. These are the contract's
   executable spec.
4. **Document `IDDRIFT01`** in `TRACEABILITY.md`/`ID_NAMING_STANDARDS.md`; bump `framework/VERSION`
   `0.34.2 → 0.35.0`; re-vendor (`sync-plugin-framework.sh` + `sync-vendored.sh`); `CHANGELOG.md`;
   `plans/DECISIONS.md` (D-0062); `plans/HANDOFF.md`.

**Out of scope — Phase 2+ (framed; the rollout decisions are the founder's):**

- **Extend content-extraction to all 8 layers.** BRD FRs are the reference; EARS/BDD/SPEC/TDD/
  ADR/PRD/IPLAN element forms (YAML `id:`+`name:`+`description:`, headings, scenarios) each need
  a format-specific extractor + fixtures. Phase 2.
- **`rehash --fix` (canonicalize + citation cascade).** Deterministically recompute an element's
  ID *and rewrite every downstream `@`-tag citation to it* (the controlled, opt-in Model-2
  cascade). The citation-rewrite across the trace graph is the riskiest piece. Phase 3.
- **Corpus reconciliation — the load-bearing rollout decision.** The corpus IDs are LLM-generated
  (not real hashes); options, for the founder: **(a) canonicalize at the next wholesale regen**
  (the generator emits provisional ordinal IDs → a deterministic `rehash --fix` pass canonicalizes
  → the corpus becomes verifiable) — aligns with the "examples regenerated wholesale" convention;
  **(b) grandfather** existing IDs (mark the corpus `id_state: provisional` so `IDDRIFT01` exempts
  it) and enforce only on new/re-authored docs. Decide before promoting the advisory to a gate.
- **Promote `IDDRIFT01` advisory → gate** (wire into the default lint at `gate-code`, blocking) —
  only after all-layer extraction + a reconciled corpus.
- **Generator change.** LLMs can't compute SHA-256 reliably, so real hashes come from the
  deterministic `rehash --fix` pass, not from prompting — the generator emits `provisional`
  ordinal IDs (`0001`, per D-0040) and `--fix` canonicalizes. Design in Phase 3.

## Approach / Design (D-0062)

**The ID's hash is the mint-time fingerprint — drift = "does current content still hash to the
ID?".** `rehash --check` recomputes `SHA256(normalize(title)+normalize(description) …)[:4]` and
compares to `id.hash`; equal ⇒ no drift; unequal ⇒ drift (content changed) or a canonical leak
(the ID was never the real hash). Both mean the `canonical` claim is false → `IDDRIFT01`.

**Why explicit-command + advisory + BRD-§7-only + `canonical`-gated for Phase 1:** each dimension
removes a risk — explicit command (not default lint) ⇒ zero corpus/gate disruption + lint
byte-identical; advisory ⇒ never blocks; BRD-§7-only ⇒ one extractor (`scan_fr_elements`, extended
per Scope 1b) proven before generalizing; `canonical`-gated ⇒ a `provisional` doc (honest about
un-canonicalized IDs) is exempt. The **two** load-bearing risks are the **normalization contract**
(Scope 1a — if it isn't byte-exact every recompute is wrong) **and the description-extraction
boundary** (Scope 1b — `_FR_BULLET` today captures only the ID, and the description wraps across
lines, so getting the input *bytes* right is as load-bearing as the transform); both are formalized

- fixture-pinned first (Scope 1+3, fixtures (d) and (e)).

**Versioning.** The MINOR driver is the **new normative content in `framework/governance/`** — the
formalized hash-input contract (Scope 1a/1b) added to the spec authority, which trips GATE-SPEC.
`IDDRIFT01` itself is an opt-in advisory that never runs in the default gate, so it is closer to
tooling than the COV01/02/03 gated-rule precedent (kept as a secondary, imperfect analogy). New
normative spec content = framework **MINOR** (`0.34.2 → 0.35.0`). Verifier code in `tools/`
(vendored to both mirrors).

**Backward-compat.** Additive: the default `sdd_doc_lint` pass is unchanged (Phase-1 `IDDRIFT01`
runs only on the explicit `rehash --check` command), so no existing corpus/gate behavior moves;
the deterministic lint over the corpus is byte-identical.

## File structure

### Modified / Added

| Path | Change |
| ---- | ------ |
| `framework/governance/ID_NAMING_STANDARDS.md` | formalize the byte-exact hash-input normalization + extraction boundary (Scope 1a/1b) + document `IDDRIFT01`; refine the D-0061 scope note from "unverified" → "**verifiable on demand** via the opt-in `rehash --check` command (not run by the default pipeline; the corpus remains unverified until Phase-2 reconciliation)" — never write "verified," which would re-introduce the exact over-claim D-0061 removed. Also state that Phase-1 coverage is **§7 FR elements only** |
| `framework/layers/01_BRD/BRD-TEMPLATE.yaml` (+ the 4 other id-bearing templates) | replace the inline normalization with a cross-ref to the authority (single source) |
| `tools/sdd_doc_lint/__init__.py` (or new `tools/rehash.py`) | `rehash --check`: FR title/description capture + normalize + recompute + compare → `IDDRIFT01` (advisory, `canonical`-gated, explicit-command-only) |
| `platforms/{hermes,claude-code-plugin}/sdd_doc_lint/__init__.py` | regenerated by `sync-vendored.sh` (byte-identical) |
| `tools/sdd_doc_lint/tests/` + `tests/conformance/` | round-trip + drift + provisional-exempt + normalization-edge fixtures/tests |
| `framework/VERSION` (→ `0.35.0`) + `CHANGELOG.md` | version + entry (GATE-SPEC E005+E008) |
| `platforms/claude-code-plugin/framework/**` | re-vendored (`sync-plugin-framework.sh`) |
| `plans/DECISIONS.md` (D-0062) / `plans/HANDOFF.md` | docs |

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | round-trip fixture: BRD with correctly-hashed FR IDs → `rehash --check` | clean (no `IDDRIFT01`) | verifier correctness |
| V2 | perturbed fixture: edit an FR's title/description, keep the ID → `rehash --check` | `IDDRIFT01` on that FR | drift detection |
| V3 | `provisional` fixture → `rehash --check` | exempt (no `IDDRIFT01`) | `canonical`-gating |
| V4 | normalization-edge fixture (unicode/special/>100 chars) hashed twice | byte-stable hash (deterministic); non-Latin strip behaves as documented | the load-bearing transform (Scope 1a) |
| V4b | extraction fixture (multi-line wrapped description, band vs no-band, colon-in-desc) | captured `(title, description)` bytes exactly match the asserted values | the load-bearing extraction boundary (Scope 1b) |
| V4c | §7-only scope: a BRD element ID **outside** §7 whose content is perturbed | NOT flagged (out of Phase-1 scope — documents the coverage boundary honestly) | scope claim (Scope 4) is truthful |
| V5 | default `sdd_doc_lint examples/*/docs/` output is **byte-identical** before vs after | unchanged (Phase-1 rule is explicit-command-only) | no gate/corpus disruption |
| V6 | `diff` canonical vs both `platforms/*/sdd_doc_lint/` | byte-identical | vendoring |
| V7 | `python -m pytest tests/conformance -q` | green | no regression |
| V8 | `python tests/chg/spec_gate.py` | OK — VERSION + CHANGELOG (E005+E008) | version |

## Docs to update

- [ ] `CHANGELOG.md` — MINOR `0.34.2 → 0.35.0`, PROVISIONAL-IDS-002 Phase 1
- [ ] `plans/DECISIONS.md` — D-0062 (the hash-input contract + `IDDRIFT01`; Phase-2+ rollout decisions parked)
- [ ] `plans/HANDOFF.md` — progress; the Phase-2+ decisions (all-layer, `--fix`, corpus reconcile, gate-promote)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | The normalization isn't byte-exact → false drift everywhere | med | Scope 1 formalizes it as an ordered transform; V4 pins it with an edge fixture; the contract is the plan's core, not an afterthought |
| R2 | Wiring `IDDRIFT01` into the default lint would flag the whole corpus | high (if done) | Phase 1 keeps it **explicit-command-only + advisory**; V5 asserts the default lint is byte-identical; corpus reconciliation is deferred with a stated decision |
| R3 | FR title/description extraction misparses the multi-line bullet (wrong description boundary → false/missed drift) | **high** | Scope 1b defines the boundary byte-exactly; extraction fixture V4b asserts exact captured bytes (multi-line, band, colon-in-desc) — this is the review's MAJOR-2 finding, promoted to a first-class risk |
| R4 | Scope creep into `--fix`/all-layers/gate | med | explicitly Phase 2+; Phase 1 is verify-only, BRD-only, advisory |
| R5 | MINOR vs PATCH | low | new normative rule = MINOR (COV01/02/03 precedent) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The hash input is `{doc_id}:{section_id}:{title}:{description}` | `Build input: "{doc_id}:{section_id}:{title}:{description}"` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:135 |
| 2  | The normalization lives only in the template (to formalize in the authority) | `first 100 chars, lowercased, special chars removed` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:136 |
| 3  | The `id_state: canonical` claim (what `IDDRIFT01` verifies) — now scoped by D-0061 | `id_state: canonical` | framework/governance/ID_NAMING_STANDARDS.md:94 |
| 4  | HASH01 checks uniqueness only — NOT hash-vs-content (the new rule is separate) | `def _check_id_uniqueness` | `tools/sdd_doc_lint/__init__.py:866` |
| 5  | The FR scanner captures id/band but NOT title/description (needs extension) | `class FRElement` | `tools/sdd_doc_lint/__init__.py:732` |
| 6  | `_FR_BULLET` captures only the ID (group 1); title is matched-not-captured, description not in the match at all → Scope 1b is a genuine new multi-line parse | `_FR_BULLET = re.compile` | `tools/sdd_doc_lint/__init__.py:710` |
| 7  | `scan_fr_elements` is the BRD FR extractor to extend | `def scan_fr_elements` | `tools/sdd_doc_lint/__init__.py:749` |
| 8  | The default corpus checks dispatch behind `skip_coverage` (Phase-1 rule stays OUT of this) | `if not skip_coverage:` | `tools/sdd_doc_lint/__init__.py:2071` |
| 9  | The vendor sync copies canonical → each mirror | `cp "$canonical/__init__.py" "$dest/__init__.py"` | tools/sdd_doc_lint/sync-vendored.sh:16 |
| 10 | Model 2 (stable ID + drift fingerprint) is the ratified decision | `RESOLVED as Model 2` | plans/DECISIONS.md:35 |
| 11 | Current framework spec version 0.34.2 (MINOR target 0.35.0) | `0.34.2` | framework/VERSION:1 |
| 12 | GATE-SPEC-E005 requires a VERSION bump on any framework/** change | `failures.append("GATE-SPEC-E005")` | tests/chg/spec_gate.py:86 |
| 13 | GATE-SPEC-E008 requires CHANGELOG in the same diff | `CHANGELOG.md` | tests/chg/spec_gate.py:87 |

## Review log

### Pass 1 — 2026-07-07 — self-review

Drafted after grounding the feasibility of Model-2 enforcement. Two facts forced the phasing:
the exact hash-input normalization is under-specified (only in the BRD template, not the
authority) and the corpus IDs are LLM-generated (would flag wholesale under a gate). Phase 1 is
therefore scoped to the low-risk foundational core — formalize the contract + build
`rehash --check` as an explicit-command, advisory, `canonical`-gated, BRD-only verifier proven
by round-trip fixtures — keeping the default lint byte-identical and deferring `--fix`,
all-layer extraction, corpus reconciliation, and gate-promotion to Phase 2+ with the rollout
decisions surfaced for the founder. Pending: independent Pass 2.

### Pass 2 — 2026-07-07 — independent adversarial review (fresh-context code-reviewer agent)

An independent agent reviewed the plan against the authority, the templates, the linter source,
D-0061, and the real BRD corpus. Confirmed SOUND: minimal-and-realistic scoping (no speculative
scope), the byte-identical-default-lint claim (dispatch behind `if not skip_coverage:` at
`__init__.py:2071`), and the `FRAMEWORK_SPEC_VERSION` auto-re-match. Four MAJOR + three MINOR
gaps found and folded:

- **MAJOR-1 (authority over-claim).** The draft flipped `ID_NAMING_STANDARDS.md` to "verified for
  `canonical` docs" — but Phase 1 never runs the check on the corpus and the corpus IDs stay
  LLM-generated non-hashes, so "verified" would re-introduce the exact over-claim D-0061 removed
  across 13 surfaces. **Fixed:** `Feeds` row + File-structure row 1 now say "**verifiable on
  demand** via the opt-in command; corpus unverified until Phase-2," and the plan forbids writing
  "verified."
- **MAJOR-2 (description bytes undefined).** `_FR_BULLET` captures only the ID; the title is
  matched-not-captured and the description wraps across continuation lines with no defined stop
  boundary — so V4 (transform determinism) never proved the *extraction* yields the right input
  bytes. **Fixed:** new Scope 1b pins the extraction boundary byte-exactly; new fixture V4b
  asserts exact captured `(title, description)` bytes; R3 promoted to high.
- **MAJOR-3 (normalization was an "e.g.").** The load-bearing transform was illustrative, not
  pinned. **Fixed:** Scope 1a states it as a normative ordered transform (NFC → casefold → strip
  to `[a-z0-9 ]` → collapse ws → trim → first 100 chars), explicitly superseding the ambiguous
  template prose.
- **MAJOR-4 (§7-only coverage was silent).** `scan_fr_elements` sees only §7 FR bullets; other
  element-bearing BRD sections would return a false clean. **Fixed:** Scope 2/4 + V4c state the
  §7-only boundary explicitly; the authority wording must too.
- **MINOR-1 (anglocentric strip):** acknowledged in Scope 1a + V4 as intended-for-Phase-1 with a
  Unicode-category strip parked to Phase 2. **MINOR-2 (version driver):** Versioning paragraph now
  leads with the GATE-SPEC governance-content driver, COV precedent demoted to secondary.
  **MINOR-3 (ledger 13 off-by-one):** the `CHANGELOG.md` symbol resolves on :87 (the append is
  :88); citation left as-is since the symbol is authoritative.

### Pass 3 — 2026-07-07 — re-review of the folded plan (self, codebase cross-check)

Re-validated that the Pass-2 patches introduced no new inconsistency: (a) the "verifiable" wording
is now consistent across `Feeds`, File-structure row 1, and the Objective; (b) Scope 1a/1b, the
Approach "two load-bearing risks" paragraph, V4/V4b/V4c, and R3 all agree on the transform-vs-
extraction split; (c) the §7-only boundary is stated in Scope 2, Scope 4, and V4c consistently;
(d) all 13 ledger citations re-verified against source (symbols resolve; lines advisory). No new
substantive gaps. The plan is minimal (contract + BRD-§7 advisory verifier + fixtures + docs),
with `--fix`, all-layer extraction, corpus reconciliation, and gate-promotion cleanly parked as
founder-decided Phase 2+.

**Result:** ready
