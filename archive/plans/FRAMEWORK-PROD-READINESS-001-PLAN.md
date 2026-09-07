# FRAMEWORK-PROD-READINESS-001 Plan — the 2 framework-side items from the production-readiness audit: scope the SHA-256 element-ID guarantee to reality + ratify GD-02…05

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | FRAMEWORK-PROD-READINESS-001                |
| Type           | fix (spec honesty + governance hygiene)     |
| Status         | READY — 2026-07-07 (Pass 2 independent; Pass 3 self) |
| Depends on     | none (the plugin-side audit items shipped in PLUGIN-PROD-READINESS-001 / #266) |
| Feeds          | the `framework/` spec is honest about the element-ID model + its governance decisions reflect their live status |
| Version impact | framework spec **PATCH** (`0.34.1 → 0.34.2`) — a doc-accuracy clarification (scope an over-claim to reality) + a governance-status flip; no rule/algorithm/structure change. Both `FRAMEWORK_SPEC_VERSION` pointers auto-re-match; plugin + Hermes **product** versions unchanged. |

## Objective

The 4-agent production-readiness audit found the framework spec internally consistent and clean
on dead-refs / stale-versions / rule-completeness, with **two framework-side items** (the
plugin-side BLOCKER + SHOULD-FIX already shipped in #266). Both are honesty/hygiene, not
correctness:

1. **SHA-256 element-ID over-claim.** `ID_NAMING_STANDARDS.md` §"Hash algorithm (normative)"
   states the hash is "computed **deterministically so any tool** — the plugin generator or a
   hand author — produces **byte-identical** IDs," and `id_state: canonical` means "the IDs
   **are** content hashes." The same claim recurs, uncaveated, across **12 more spec surfaces**
   (5 layer templates' `id_standard` block + 5 layer READMEs + the PRD-00/SPEC-00 index
   templates), all vendored into the plugin bundle. But **no engine produces true
   content-hashes** — the
   plugin (and Hermes) LLM-generate element IDs that *look* like 4-hex hashes but are not
   `SHA256(content)`, and **nothing verifies them**: D-0040 explicitly deferred
   canonical-correctness verification (`rehash --check`) to **PROVISIONAL-IDS-002**, which has
   not shipped. So the spec makes an enforceable-sounding determinism guarantee that is neither
   met nor checkable end-to-end. (This is a spec-vs-reality gap, **not** a framework-internal
   contradiction — the spec is uniform.)

2. **GD-02…05 statuses stale.** Four graduated governance decisions read `Status: Proposed —
   … (ratified on merge)` although their content is **live and enforced**: GD-05 (the
   author-self-claim strip, shipped this session), GD-03 (REFGRAN01, active in the corpus),
   GD-04 (IPLAN-ASSURANCE L1, a conformance requirement), GD-02 (independent pre-merge review).
   Only GD-01 reads "Accepted." The "ratified on merge" convention has no mechanism that
   actually flips the word, so status no longer reflects reality.

## Scope

**In:**

1. **Scope the SHA-256 guarantee to reality (the authority).** In
   `framework/governance/ID_NAMING_STANDARDS.md` §"Hash algorithm (normative)": reword the
   "produces byte-identical IDs" guarantee to state the SHA-256 form is the **canonicalization
   target / by-hand↔tool parity anchor** (per D-0040) — **not a currently-verified property**.
   Add one clause: until `rehash --check` (PROVISIONAL-IDS-002) ships, a produced element ID is
   an **opaque stable string** that *should* match the algorithm but is **not verified** to; a
   mismatch ("canonical leak") is not shape-detectable today. Reword the `id_state: canonical`
   definition from "the IDs **are** content hashes" → "the IDs are **intended as** content
   hashes (the canonicalization target; unverified until `rehash --check`)."
2. **Caveat EVERY repeating surface (completeness — Pass-2 LB).** The over-claim is not only in
   the authority + 5 templates; it recurs uncaveated in **7 more** vendored spec surfaces, so the
   fix is honest only if all are scoped. Append the same one-line scope + cross-ref — "(the
   canonicalization target; not verified end-to-end until `rehash --check` — see
   `ID_NAMING_STANDARDS.md`)" — to each:
   - **5 layer templates** (BRD/PRD/EARS/BDD/ADR `id_standard._guidance`): caveat the **whole
     block** — the "content-derived hashes" line, the `Properties: deterministic, stateless,
     stable, deduplicating` line, and the embedded `hashlib.sha256(...)` recipe are all the same
     over-claim (Pass-2 MINOR — the earlier draft caveated only one line).
   - **5 layer READMEs** — `01_BRD/README.md:94,101`, `02_PRD/README.md:35,42`,
     `03_EARS/README.md:51,58`, `04_BDD/README.md:49`, `05_ADR/README.md:50` ("Hash-based,
     content-derived IDs" + "Algorithm: SHA256 …").
   - **2 index templates** — `02_PRD/PRD-00_index.TEMPLATE.md:88` ("SHA256, 4-char hex") and
     `06_SPEC/SPEC-00_index.TEMPLATE.md:58` ("Hash-based element IDs").
   SPEC/TDD/IPLAN *layer* templates exempt element IDs, so they are untouched; the lighter
   checklist mentions ("cross-references use hash-based element IDs" in PRD-00/EARS-00) reference
   the target *form* and are left as-is (they don't assert verified determinism).
3. **Ratify GD-02…05.** In `framework/governance/DECISIONS.md`, flip
   `Status: Proposed — <date> (ratified on merge; …)` → `Status: Accepted — <date> (ratified on
   merge; …)` for GD-02, GD-03, GD-04, GD-05 (all merged + enforced; "ratified on merge"
   satisfied). Keep the parenthetical rationale. **GD-04 note:** it carries a "Merge
   precondition: founder tags `iplan/v0.4.0` first" — verified the tag exists on
   `aidoc-flow-iplan-standard`, so the flip records truth (Pass-2 NIT).
4. Bump `framework/VERSION` `0.34.1 → 0.34.2` (staged); re-vendor the plugin framework bundle
   (`sync-plugin-framework.sh`); `CHANGELOG.md`; `plans/DECISIONS.md` (D-0061 — records the
   framework honesty/hygiene fixes); `plans/HANDOFF.md`. Close the audit's 2 framework-side
   items.

**Out of scope — the deeper decision (framed for the founder, deferred):**

- **PROVISIONAL-IDS-002 — the element-ID model decision itself.** This plan makes the spec
  *honest* about the current (unverified) state; it does **not** decide the ID model, which is a
  genuine framework design fork the founder should own:
  - **(A) Enforce the hash** — build `rehash --check` (a `sdd_doc_lint` verifier that recomputes
    `SHA256(content)` per element and flags any `canonical` ID that doesn't match), and require
    the engines to emit true content-hashes (a real behavior change for the LLM generators). Makes
    the current normative promise TRUE.
  - **(B) Adopt stable strings** — formally drop the deterministic-hash claim; element IDs are
    LLM-generated stable opaque strings (unique + stable, not content-derived), and the
    `hash_algorithm: SHA256` field becomes advisory/removed.
  Either resolution is a separate, larger plan; the honesty-scoping here is correct and safe under
  **both** outcomes (it just states the present truth), so it does not pre-commit the decision.
- The remaining H-11a cosmetic `v3.2` string residue and H-11c (the Hermes-side element-ID
  SHA-256 mention) — the latter is unblocked by, and should follow, whichever PROVISIONAL-IDS-002
  resolution lands.

## Approach / Design (D-0061)

Two independent, low-risk doc changes; neither alters a rule, algorithm, or structure — the
element-ID *algorithm* stays exactly as written (it remains the canonicalization target), and the
GDs stay exactly as decided. The SHA-256 change corrects an **over-claim** (a verified-determinism
guarantee) down to the **actual** contract (an unverified target, per D-0040's own deferral of
`rehash --check`). The GD flip records already-true ratification. Because nothing behavioral
changes and no `sdd_doc_lint` rule reads these strings, the deterministic lint over the corpus is
byte-identical — this is prose/status only.

**Version reasoning.** Doc-accuracy clarification of an over-claim + a governance-status flip =
framework **PATCH** (`docs/PROJECT.md`: MAJOR = breaking contract change, MINOR = additive
feature; neither applies). Precedent: D54-F04 (rubric `_guidance` reconciliation, PATCH),
ENG-PLATFORM-ADR-TIMING (PATCH).

**Backward-compat.** Purely corrective: no ID that validated before fails now (the `ELEM_FORM` /
`HASH01` / `PROV01` rules are untouched); the spec simply stops promising a determinism it never
enforced. No consumer breaks.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `framework/governance/ID_NAMING_STANDARDS.md` | scope the "byte-identical / normative" guarantee + the `id_state: canonical` definition to "intended target, unverified until `rehash --check`" |
| `framework/layers/{01_BRD,02_PRD,03_EARS,04_BDD,05_ADR}/*-TEMPLATE.yaml` | caveat the whole `id_standard` block (content-hashes + `Properties: deterministic` + recipe) — 5 templates |
| `framework/layers/{01_BRD,02_PRD,03_EARS,04_BDD,05_ADR}/README.md` | one-line caveat + cross-ref on "Hash-based, content-derived IDs" / "Algorithm: SHA256" — 5 READMEs |
| `framework/layers/02_PRD/PRD-00_index.TEMPLATE.md` + `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md` | caveat the "SHA256 / Hash-based element IDs" claim — 2 index templates |
| `framework/governance/DECISIONS.md` | GD-02, GD-03, GD-04, GD-05 `Status: Proposed → Accepted` |
| `framework/VERSION` (→ `0.34.2`) + `CHANGELOG.md` | version + entry (GATE-SPEC E005+E008) |
| `platforms/claude-code-plugin/framework/**` | re-vendored by `sync-plugin-framework.sh` (not hand-edited) |
| `plans/DECISIONS.md` (D-0061) / `plans/HANDOFF.md` | docs |

## Implementation sequence

### Task 1: Scope the SHA-256 authority + the 5 template caveats

- Reword `ID_NAMING_STANDARDS.md` §"Hash algorithm (normative)" + the `id_state: canonical` line;
  add the caveat/cross-ref to the 5 templates' `id_standard` guidance.

### Task 2: Ratify GD-02…05

- Flip the four `Status:` lines to `Accepted` in `framework/governance/DECISIONS.md`.

### Task 3: Version + propagation + docs

- `framework/VERSION → 0.34.2` (staged); `sync-plugin-framework.sh`; `CHANGELOG.md`; D-0061;
  close the audit's 2 framework-side items; HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | grep `ID_NAMING_STANDARDS.md` for the reworded guarantee | states "canonicalization target"/"not verified until `rehash --check`"; no surviving unqualified "byte-identical … any tool" or "the IDs **are** content hashes" | SHA-256 authority |
| V2 | grep **all 13 surfaces** (authority + 5 templates + 5 READMEs + 2 index templates) for the strong content-hash/`SHA256`/`deterministic` claim | every occurrence is caveated with "not verified … see `ID_NAMING_STANDARDS.md`"; no uncaveated determinism claim survives in `framework/` (grep `framework/layers`+`framework/governance` for `content-derived\|deterministic.*hash\|Algorithm: SHA256\|byte-identical` → each hit is scoped) | completeness (Pass-2 LB) |
| V3 | grep `framework/governance/DECISIONS.md` for `Status: Proposed` | none among GD-02…05 (all `Accepted`); GD-01 unchanged | GD flip |
| V4 | `sdd_doc_lint` deterministic output over `examples/*/docs/` is **byte-identical** before vs after | unchanged — prose/status only, no gate/rule change | no behavior change |
| V5 | `python -m pytest tests/conformance -q` | green (incl. bundle drift guard) | propagation |
| V6 | `diff` canonical vs plugin-bundle `ID_NAMING_STANDARDS.md` + the 5 templates | identical (re-vendored) | Task 3 |
| V7 | `python tests/chg/spec_gate.py` | OK — VERSION + CHANGELOG present (E005+E008) | version |
| V8 | element-ID rules unchanged: `grep ELEM_FORM\|HASH01\|PROV01` still defined; `hash_algorithm: SHA256` field still present (scoped, not removed) | intact | backward-compat |

## Docs to update

- [ ] `CHANGELOG.md` — PATCH `0.34.1 → 0.34.2`, FRAMEWORK-PROD-READINESS-001
- [ ] `plans/DECISIONS.md` — D-0061 (scope the SHA-256 guarantee; ratify GD-02…05; PROVISIONAL-IDS-002 deferred with the (A)/(B) fork)
- [ ] `plans/HANDOFF.md` — progress; PROVISIONAL-IDS-002 fork surfaced for a future founder decision
- [ ] `plans/FRAMEWORK-TODO.md` — only if a tracked entry exists for these (else skip)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Scoping reads as "removing" the hash algorithm | low | the algorithm + `hash_algorithm: SHA256` field stay verbatim as the *target*; V8 confirms the rules/field intact — only the *verified-determinism guarantee* is scoped |
| R2 | Flipping GD statuses without a real ratification | low | "ratified on merge" is the recorded convention; each GD is merged + enforced (GD-05 this session, GD-03 corpus-active, etc.) — the flip records existing truth |
| R3 | PATCH vs MINOR | low | doc-accuracy/status clarification, no rule/behavior change — PATCH (D54-F04 / ENG-PLATFORM-ADR-TIMING precedent) |
| R4 | The scoping pre-commits PROVISIONAL-IDS-002 | low | worded as present-state truth ("unverified today"), safe under both (A) enforce and (B) adopt-strings; the decision is explicitly deferred |
| R5 | Bundle drift (edited canonical, not re-vendored) | low | Task 3 runs `sync-plugin-framework.sh`; V5 + V6 verify |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The authority over-claims byte-identical determinism | `computed deterministically so any tool` | framework/governance/ID_NAMING_STANDARDS.md:66 |
| 2  | `id_state: canonical` asserts the IDs ARE content hashes | `the IDs are content hashes` | framework/governance/ID_NAMING_STANDARDS.md:83 |
| 3  | D-0040 deferred verification to `rehash --check` (PROVISIONAL-IDS-002); algorithm normative | `The SHA-256 algorithm is now` | plans/DECISIONS.md:629 |
| 4  | The 5 templates repeat the content-hash claim (BRD example) | `All element IDs use content-derived hashes` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:129 |
| 5  | The BRD template asserts deterministic properties | `Properties: deterministic, stateless, stable, deduplicating` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:139 |
| 6  | GD-05 status is Proposed (to flip) | `**Status:** Proposed — 2026-07-04` | framework/governance/DECISIONS.md:18 |
| 7  | GD-04 status is Proposed (to flip) | `**Status:** Proposed — 2026-06-28` | framework/governance/DECISIONS.md:64 |
| 8  | GD-03 status is Proposed (to flip) | `**Status:** Proposed — 2026-06-27` | framework/governance/DECISIONS.md:106 |
| 9  | GD-02 status is Proposed (to flip) | `**Status:** Proposed — 2026-06-15` | framework/governance/DECISIONS.md:142 |
| 10 | GD-01 is already Accepted (the target form) | `**Status:** Accepted — 2026-05-23` | framework/governance/DECISIONS.md:177 |
| 11 | Current framework spec version 0.34.1 (PATCH target 0.34.2) | `0.34.1` | framework/VERSION:1 |
| 12 | GATE-SPEC-E005 requires a VERSION bump on any framework/** change | `failures.append("GATE-SPEC-E005")` | tests/chg/spec_gate.py:86 |
| 13 | GATE-SPEC-E008 requires CHANGELOG in the same diff | `CHANGELOG.md` | tests/chg/spec_gate.py:87 |
| 14 | The plugin re-vendors the framework bundle | `dest="$repo_root/platforms/claude-code-plugin/framework"` | tools/sync-plugin-framework.sh:21 |
| 15 | A layer README repeats the content-hash over-claim (Pass-2 LB surface) | `Hash-based, content-derived IDs` | framework/layers/01_BRD/README.md:94 |
| 16 | A layer README asserts the SHA256 algorithm as fact | `Algorithm: SHA256 of` | framework/layers/03_EARS/README.md:58 |
| 17 | An index template asserts SHA256 hash IDs (Pass-2 LB surface) | `(SHA256, 4-char hex)` | framework/layers/02_PRD/PRD-00_index.TEMPLATE.md:88 |

## Review log

### Pass 1 — 2026-07-07 — self-review

Drafted from the audit's 2 framework-side findings (the plugin items shipped in #266). Grounded
the SHA-256 landscape: D-0040 made the algorithm normative but explicitly deferred verification
(`rehash --check`) to PROVISIONAL-IDS-002 — so the "byte-identical determinism" guarantee is an
over-claim the engines don't meet (they LLM-generate). The honesty-scoping fix is safe under both
PROVISIONAL-IDS-002 outcomes and does not pre-commit the (A)/(B) fork, which is framed as a
deferred founder decision. GD-02…05 flip records existing ratification. Both are framework PATCH
(no rule/behavior change; deterministic lint byte-identical). Pending: independent Pass 2.

### Pass 2 — 2026-07-07 — independent (fresh-context adversarial)

All 14 (now 17) citations verified. D-0040 framing confirmed (algorithm normative + verification
deferred to `rehash --check`/PROVISIONAL-IDS-002); the over-claim quoted verbatim; GD-02…05 all
`Proposed (ratified on merge)` + in force (GD-04's `iplan/v0.4.0` merge-precondition tag confirmed
to exist); PATCH defensible; V4 byte-identical holds (no lint rule / conformance test parses
`hash_algorithm`/`id_state`/GD-status in an affected way — `id_state` is read only from corpus
frontmatter, not the edited templates). **Scoping-not-resolving judged the RIGHT call** (safe
under both PROVISIONAL-IDS-002 outcomes; the (A)/(B) fork is a real behavior decision for the
founder) — *provided* the completeness gap is closed. Findings folded:

- **[LOAD-BEARING] Scope incomplete — the over-claim survives in ~7 unlisted surfaces.** The 5
  layer READMEs (`01_BRD/README.md:94,101` … `05_ADR/README.md:50`) + the PRD-00/SPEC-00 index
  templates flatly promise content-derived SHA256 IDs; scoping only the authority + 5 templates
  would reproduce the exact "promise X but don't check it" state the audit flagged. → Added all
  7 to Scope #2 + the File-structure table + ledger rows 15-17; V2 rewritten to grep **all 13
  surfaces** + a `framework/`-wide sweep for any uncaveated determinism claim.
- **[MINOR] Ledger claim 5 identified but not remediated.** The template caveat touched only the
  "content-derived" line, leaving `Properties: deterministic …` + the `hashlib.sha256(...)` recipe
  uncaveated. → Scope #2 now caveats the **whole `id_standard` block**.
- **[NIT] GD-04 merge-precondition unstated.** → Recorded the `iplan/v0.4.0` tag-exists check in
  Scope #3.

### Pass 3 — 2026-07-07 — self-review (re-validate the Pass-2 fold)

Re-checked: Scope #2 + the File table + V2 now cover all 13 over-claim surfaces (authority + 5
templates' full block + 5 READMEs + 2 index templates); the checklist "hash-based element IDs"
mentions are correctly left (target-form, not a determinism claim); ledger rows 15-17 anchor the
new surfaces; GD-04's precondition is recorded. The (A)/(B) PROVISIONAL-IDS-002 fork stays
deferred and the scoping is neutral to it. D-0061 is the next free decision number (D-0060 =
PLUGIN-PROD-READINESS-001). No new gaps.

**Result:** ready
