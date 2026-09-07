# ELEMENT-ID-LAYER-CONTRACT-001 Plan — one hash contract, one source

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | ELEMENT-ID-LAYER-CONTRACT-001                                |
| Type           | documentation                                                |
| Status         | IMPLEMENTED — 2026-07-26 (see `## Implementation log`)        |
| Depends on     | D-0040, D-0061, D-0062 (PROVISIONAL-IDS-002 Phase 1)         |
| Feeds          | #342 (generator), PROVISIONAL-IDS-002 Phase 2                |
| Closes         | [#344](https://github.com/vladm3105/aidoc-flow-framework/issues/344) fully; [#343](https://github.com/vladm3105/aidoc-flow-framework/issues/343) after its two residual clauses are transferred (see D8) |
| Version impact | framework **MINOR** (`0.38.0` → `0.39.0`) only. **No platform product-version bump** — see D5 |
| Gate           | GATE-SPEC, `semver_impact: minor`, `change_level: C2`        |

## Objective

D-0062 made a six-step **normalization transform** normative for element-ID hash
inputs and made `governance/ID_NAMING_STANDARDS.md` its single source. Within the
framework spec that change reached exactly one surface — `BRD-TEMPLATE.yaml`.
**Seven other framework-spec surfaces** still publish the pre-normalization
string `"{doc_id}:{section_id}:{title}:{description}"`, so anyone following a
layer template or README computes a different hash than `compute_element_hash()`
does for the same content. An eighth surface, the TDD layer, publishes no
element-ID contract at all despite being one of six layers that MUST carry
element IDs.

This plan corrects those eight framework-spec surfaces by **deleting** the
per-layer re-specification rather than updating it, leaving
`ID_NAMING_STANDARDS.md` as the sole statement of the algorithm, and adds a
conformance test that locks the single-source property so this drift class
cannot recur silently in `framework/`.

**Census (corrected in Pass 1, recounted in Pass 2, completed in Pass 3).**
**Thirty** surfaces state an element-ID hash input or algorithm. This plan addresses the
eight owned by the framework spec. The rest are enumerated and routed, not
silently dropped:

| Surfaces | Where | Disposition |
|---|---|---|
| 1 | `BRD-TEMPLATE.yaml` | already correct — the pattern this plan propagates |
| **7** | 4 layer templates + 3 layer READMEs | **Part A/B — this plan** |
| **1** | `07_TDD` (no contract at all) | **Part C — this plan** |
| 12 | plugin `doc-*` + `doc-*-fixer` skills | **#342** — see D6 |
| 1 | plugin `doc-naming/SKILL.md:106` | **#342** (already in its entry) |
| 5 | Hermes `UCC_PROMPT_{BRD,PRD,EARS}` + `UCRem_PROMPT_{EARS,PRD}` | **#342** — 2 already in its entry, 3 new |
| 1 | Hermes `sdd-orchestrator/references/brd-validation-automation.md:179` — a **live, loaded** reference carrying a *fourth* normalization variant | **#342** — new, see D6 |
| 1 | `tests/acceptance/_id_coordinator.py` — a **live second implementation** | **[#351](https://github.com/vladm3105/aidoc-flow-framework/issues/351)** — see D7 |
| 1 | `tools/sdd_doc_lint/__init__.py:1132` AS11 docstring (+ 2 byte-identical vendored copies) — describes the input with no transform | folded into **#351** — same file class, doc-only, zero behavior |

Total 30 = 1 already-correct + 8 (this plan) + **19** (#342) + 2 (#351).
The linter docstring is documentation inside code: the real implementation
(`:922-935`) is correct, and `git diff HEAD --stat tools/` must stay empty in this
PR, so it rides along on D7's issue rather than being fixed here.

## Scope

**In:**

- **A — 4 framework layer templates** (PRD, EARS, BDD, ADR): replace the
  re-specified 3-step algorithm with the cross-reference pattern
  `BRD-TEMPLATE.yaml:134-142` already establishes, preserving each layer's own
  "from *this* layer's content, NOT upstream" scoping clause.
- **B — 3 framework layer READMEs** (BRD, PRD, EARS): correct the `Algorithm:`
  line to the `norm()` form + cross-reference.
- **C — the TDD layer contract** (#344): add `## Element IDs` to
  `07_TDD/README.md`; add the five `id_standard` keys
  (`format`/`hash_algorithm`/`hash_length`/`max_hash_length`/`placeholder`),
  the shape line, the cross-reference, **and an explicit Phase-2
  extraction-boundary clause** to `TDD-TEMPLATE.yaml`, appended to — not
  replacing — its existing two-ID-form guidance. The boundary clause is a
  required deliverable, not optional prose: without it Part C would replace
  silence with an instruction an author cannot execute (D3).
- **E — regression lock**: `tests/conformance/test_element_id_layer_contract.py`
  asserting, over `framework/layers/**` only: (1) no file publishes the raw
  pre-normalization input string; (2) each of the six element-ID-mandating layer
  templates declares the five `id_standard` keys **and** cross-references
  `ID_NAMING_STANDARDS.md`; (3) each of the six layer READMEs has an
  `## Element IDs` section.
  **Checks (2) and (3) must iterate a hardcoded list of the six canonical
  `(README.md, <TYPE>-TEMPLATE.yaml)` pairs — never a glob.** A template glob
  sweeps in the `*-MVP-TEMPLATE.yaml` and `*-00_index.TEMPLATE.*` files **and**
  `06_SPEC/SPEC-TEMPLATE.yaml` + `08_IPLAN/IPLAN-TEMPLATE.yaml` (the two exempt
  layers' main templates); a README glob likewise sweeps `06_SPEC` and `08_IPLAN`,
  which correctly have no `## Element IDs` — they are the documented exemptions
  (`ID_NAMING_STANDARDS.md:160-176`). Either would produce a double-digit count of
  spurious reds and misstate the red-state counts in step 1.
- **F — propagation**: bump `framework/VERSION` and both
  `FRAMEWORK_SPEC_VERSION` pins; run `scripts/sync-version-refs.sh`; **then**
  `tools/sync-plugin-framework.sh` (order is load-bearing — see step 5); update
  docs of record.

**Out of scope (deferred, each routed):**

- **The 19 platform surfaces** (12 plugin layer skills + `doc-naming` + 5 Hermes
  prompts + the loaded Hermes reference doc). Owned by #342; editing them here
  would be discarded by #342's own fix shape. Rationale in **D6**. Action: the
  enumeration is added as a **comment on #342** (not a new issue — the repo rule
  is to add evidence to the existing issue), and `FRAMEWORK-TODO.md`'s
  `IDGEN-NO-GENERATOR` entry goes from "9 surfaces" to **19 — the union with its
  existing list, never a replacement**. Its current 9 already include
  `doc-naming/SKILL.md:106`, `UCC_PROMPT_BRD.md:79` and `UCC_PROMPT_PRD.md:65`;
  posting a count that omits them would silently shrink #342's tracked scope.
- **`tests/acceptance/_id_coordinator.py` — a live second implementation of the
  hash that skips normalization.** Executable code, not spec text, with
  fixture-churn risk. Rationale in **D7**. **Filed as
  [#351](https://github.com/vladm3105/aidoc-flow-framework/issues/351)** +
  `IDCOORD-SECOND-HASH-IMPL` TODO entry, per GOV-TODO-ISSUE-SPLIT.
- **A TDD (or any non-BRD) field-extraction boundary.**
  `ID_NAMING_STANDARDS.md:118-122` defines byte-exact extraction for **BRD §7
  only**; PRD/EARS/BDD/ADR have none either. Naming which TDD test-case field is
  `title` and which is `description` would be a *new normative contract*, not a
  drift fix. See **D3**.
- **`placeholder: "0000"` semantics.** A real, unresolved inconsistency — but
  inert and separable. See **D4**. **Filed as
  [#352](https://github.com/vladm3105/aidoc-flow-framework/issues/352)** +
  `IDPLACEHOLDER-UNDEFINED` TODO entry.
  It meets the GOV-TODO-ISSUE-SPLIT bar on its own (reproducible at
  `BRD-TEMPLATE.yaml:147` vs `:153`, concrete fix shape), and a comment on a
  #343 that this same PR closes would not be a durable surface (D8).
- **#345, #348** — separate issues, unrelated surfaces.
- Corpus regeneration (the example corpus is regenerated wholesale; its IDs stay
  unverified until PROVISIONAL-IDS-002 Phase 2 reconciliation).

## Approach / Design

### D1 — Single-source, not re-sync

The available fix for #343 is either (a) update the stale algorithm text in each
layer, or (b) delete it and cross-reference the authority. **(b).** Re-stating a
corrected algorithm in seven places resets the drift clock rather than stopping
it — the *re-specification itself* is what let D-0062 reach one framework
surface out of eight. `BRD-TEMPLATE.yaml:137-140` already says so in its own
comment ("Do NOT re-specify the normalization here"); this plan makes that
instruction true across the spec.

Each corrected surface keeps exactly two things: the **shape line** (so a reader
sees `norm()` and knows normalization exists) and a **pointer** to the authority.

### D2 — Preserve the per-layer scoping clause

The four stale templates each carry a genuine per-layer semantic the standard
does not: *"from EARS content, NOT upstream PRD/BRD content"*
(`EARS-TEMPLATE.yaml:98` and siblings). That is not part of the algorithm — it
is a statement about which content the element owns — and it survives the edit,
re-anchored under the shape line.

Target form (EARS shown; the other three differ only in layer name):

```yaml
      Hash algorithm (SHA256, 4-char hex) — the byte-exact input assembly and the
      title/description normalization transform are the SINGLE SOURCE in
      `governance/ID_NAMING_STANDARDS.md` ("Hash algorithm" section,
      PROVISIONAL-IDS-002). Do NOT re-specify the normalization here — cross-ref
      the authority so the verifier (`rehash --check`), any future generator, and
      hand authors converge on one contract.
        Shape: hashlib.sha256("{doc_id}:{section_id}:{norm(title)}:{norm(description)}").hexdigest()[:4]
          - from EARS content, NOT upstream PRD/BRD content
        Collision: extend 4 -> 8 chars if duplicate detected.
```

### D3 — TDD gets the contract, and says what it does not define

`07_TDD/README.md` gains an `## Element IDs` section in its five siblings' form,
stating `TDD.{doc_id}.{section_id}.{hash}`, that test cases live in **Section 4**
(so authored case IDs carry `04`), and cross-referencing the standard.
`TDD-TEMPLATE.yaml`'s `id_standard` block gains the five keys and the shape line.

**Explicitly not defined:** which test-case field supplies `title` and which
supplies `description`. A TDD case declares `name` / `spec_ref` / `target` /
`test_file` / `test_function` (`TDD-TEMPLATE.yaml:133-137`) — no `title`, no
`description`. This is not a TDD peculiarity: EARS elements carry
`name`+`statement`, ADR elements `name`+`description`, and no layer but BRD §7
has a defined extraction boundary. Writing a mapping here would be a new
normative contract smuggled into a drift fix.

**But the non-definition must be *written down*, in the template.** Pass 2
caught that leaving it implicit makes Part C actively harmful: TDD's template
publishes no algorithm today, so adding a `norm(title)`/`norm(description)`
shape line without a boundary clause replaces silence with an instruction the
author cannot execute. The five sibling **READMEs** carry the mitigation
("extraction for this layer is Phase 2+" — `04_BDD/README.md:85`,
`03_EARS/README.md:53`); the sibling **templates** do not, so "exactly as
PRD/EARS/BDD/ADR do today" is true of the READMEs only. TDD's template
therefore carries the clause explicitly:

```yaml
      NOTE: this is the canonicalization TARGET, not a verified property — LLM
      engines emit stable opaque strings, unverified until `rehash --check`
      (PROVISIONAL-IDS-002; shipped for BRD §7 only — byte-exact field
      extraction for this layer is Phase 2+).
```

**Pass 3 corrected an overreach here.** The Pass-2 draft of this clause
additionally instructed authors to *"emit provisional ordinal IDs
(`TDD.NN.04.0001`, …) with `id_state: provisional`"*. That was wrong on three
counts and is dropped:

- **Self-contradictory.** The clause lands inside the `id_standard` block whose
  first key is `state: canonical` (`TDD-TEMPLATE.yaml:26`) — the very key the
  linter names as the convention's authority
  (`tools/sdd_doc_lint/__init__.py:556-562`). The artifact would declare
  `canonical` and instruct `provisional` three lines apart.
- **It proves too much.** PRD/EARS/BDD/ADR are in the *identical* position — no
  defined extraction boundary — and all four declare `state: canonical` and
  instruct nothing of the sort. The directive would make TDD the only layer with
  a different default ID class, on a rationale that would equally rewrite four
  siblings.
- **Unacknowledged consequences.** A standing doc-level `PROV01` advisory on
  every TDD; on the next wholesale corpus regen every TDD element ID would turn
  ordinal, breaking the hash-form IDs IPLAN cites at
  `examples/url-shortener/docs/07_TDD/TDD-01.md:72-79`; and it would put the
  spec in direct conflict with `doc-tdd/SKILL.md:119`, a surface this plan
  deliberately defers to #342.

The retained wording is exactly the caveat **four** sibling READMEs already
carry (`02_PRD/README.md:37`, `03_EARS/README.md:53`, `04_BDD/README.md:85`,
`05_ADR/README.md:52`). Four, not five: `01_BRD/README.md:142` deliberately says
*"verifiable on demand via `rehash --check`"* instead, because BRD §7 extraction
is the one that shipped. All five sibling *templates* already carry the
canonicalization-TARGET NOTE (`BRD:130`, `PRD:102`, `EARS:92`, `BDD:87`,
`ADR:97`); what they lack is the extraction-boundary parenthetical. The drafted
TDD block is that same NOTE with the parenthetical grafted in — so it is
self-consistent with `TDD-TEMPLATE.yaml:26`'s `state: canonical` (the caveat says
nothing about ID state). It states the boundary without inventing a contract —
which was the whole point of D3.

### D4 — `placeholder: "0000"` — a real inconsistency, deferred honestly

Issue #343 raises as a "secondary observation" that all five templates declare

`placeholder: "0000"` while their in-body examples use `.xxxx`. **An earlier
draft of this plan rejected that as a non-defect on the grounds that
`placeholder` governs produced documents. That reasoning is wrong** and was
corrected in Pass 1:

- The templates label the key as the **template** placeholder — `Template
  placeholder: "0000" represents the hash suffix.` (`BRD-TEMPLATE.yaml:147` and
  four siblings). Under that plain reading `BRD-TEMPLATE.yaml` contradicts
  itself: it declares `placeholder: "0000"` at `:153` and uses `xxxx` throughout
  its own body.
- The string `0000` appears **nowhere** in `framework/governance/` (whole-tree
  grep, zero hits), so no governance text assigns it any meaning.
- The documented *provisional* form is section-ordinal `0001`, `.0002`, … —
  **not** `0000` (`ID_NAMING_STANDARDS.md:152-155`), and that same passage says
  "Do NOT use `xxxx`" for produced documents.

So the key matches neither reading. It is nevertheless **inert**: no code reads
`id_standard.placeholder` (grep over `tools/`, `platforms/hermes/src/`, `tests/`
returns no consumer), and `xxxx` inside a *template* is separately sanctioned as
pattern notation (`ID_NAMING_STANDARDS.md:212-220`), so nothing is currently
broken by the mismatch. Resolving what `placeholder` means is a governance
question, not a drift fix.

**Disposition:** deferred with the true rationale recorded — TODO entry plus a
correction comment on #343 stating that the observation is *valid* and why it is
not actioned here. Part C still adds `placeholder: "0000"` to TDD **for
uniformity with its five siblings** — a sixth instance of an inert key is
preferable to a TDD-shaped exception that the Part E test would have to
special-case, and it keeps the eventual resolution a single uniform edit.

### D5 — Version impact

`framework` **MINOR**. Parts A/B are drift correction (PATCH-shaped, no normative
change — the standard was always authoritative). Part C **adds** five
`id_standard` keys to `TDD-TEMPLATE.yaml` that a platform may read, and a new
documented layer contract — additive and non-breaking, so MINOR by
`GATE-SPEC_FRAMEWORK.md:94-96`. A founder could defensibly call the whole change
PATCH on the grounds that the TDD keys document an already-mandated obligation
(`ID_NAMING_STANDARDS.md:162-164`); MINOR is proposed as the safer signal.

**No platform product-version bump.** An earlier draft bumped the plugin to
`0.23.5` to cover the regenerated bundle. Pass 2 showed that is against repo
precedent and self-defeating:

- `D54-F04-EARS-RUBRIC-PLAN.md:10` is the same situation (framework-only change,
  bundle re-vendored) and states *"plugin + Hermes **product** versions
  unchanged"*; every `claude-code-plugin/vX.Y.Z` row in `docs/TAGGING.md`
  corresponds to real plugin *content*, never a bundle refresh.
- A plugin bump would turn the suite red. `test_plugin_release_metadata.py:135`
  asserts `docs/TAGGING.md` contains `claude-code-plugin/v<VERSION>`, and
  `sync-version-refs.sh:52` deliberately excludes `TAGGING.md` as
  human-authored — so the bump would require hand-adding a TAGGING release row
  and a plugin `CHANGELOG.md` entry for a release with no plugin content.

Only `framework/VERSION` moves; both `FRAMEWORK_SPEC_VERSION` pins re-match it.

### D6 — Why the 19 platform surfaces are excluded

An earlier draft included the 12 plugin skill surfaces on the reasoning that
this plan fixes *what the input is* while #342 fixes *who computes it*, making
them orthogonal. **Pass 1 disproved the orthogonality**, on two grounds:

1. **#342 already owns the exact lines.** Its TODO entry names
   `doc-brd-fixer/SKILL.md:239,245` (`FRAMEWORK-TODO.md:46`) — line 245 is the
   raw-input line. And its fix shape is *"correct the nine surfaces to emit
   provisional ordinal IDs + `id_state: provisional`"*, i.e. **delete** the
   SHA-256 instruction, not re-point its input. Every edit made here to those
   ten lines would be discarded when #342 lands.
2. **Input and compute are one construct, so they cannot be separated.**
   `doc-brd-fixer/SKILL.md:245-246` reads ``key = "…"`` then ``SHA256(key)``;
   `doc-tdd-fixer/SKILL.md:251` has **no** key clause at all
   (``SHA256(case content)``), so "correcting the input" there necessarily
   rewrites the compute expression — precisely the wording #342 will replace.

The same reasoning covers the Hermes surfaces. Excluding all nineteen keeps this
plan sized to its problem (CLAUDE.md "minimal-and-realistic") and leaves #342 a
clean surface.

**New evidence for #342, found in Pass 2 and worth its own emphasis:**
`sdd-orchestrator/references/brd-validation-automation.md:179` is not a prompt
but a **loaded reference** (`sdd-orchestrator/SKILL.md:836` points agents at it
for "the complete" procedure), and it ships a *fourth* normalization variant —
`re.sub(r'[^a-z0-9:]', '', inp.lower())[:200]` — applied to the **assembled**
string rather than per-field, using `lower()` not `casefold()`, with **no NFC**,
**deleting spaces entirely** (the character class omits the space the standard
keeps), and truncating at **200** not 100. It disagrees with
`ID_NAMING_STANDARDS.md:88-93` on five of six steps. This is the closest thing
in the repo to the ad-hoc script the founder observed an agent write, and it is
the highest-value single item in #342's backlog.

**The cost of the exclusion is stated plainly:** until #342 lands, the plugin
and Hermes authoring surfaces continue to publish hash inputs that disagree with
the spec. Step 7 does not hide this — the full enumeration goes onto #342.

### D7 — The one executable defect goes to its own issue

`tests/acceptance/_id_coordinator.py:17-19` implements `element_hash()` as
`sha256(f"{doc_id}:{section_id}:{title}:{description}")[:4]` with **no**
normalization, and mints element IDs for acceptance fixtures via `element_id()`.
Its smoke test checks determinism and format only
(`test_id_coordinator.py:22-36`) — never parity with `compute_element_hash()` —
so the divergence is both live and untested. It also uses a *string* section_id
(`"project_scope"`), unlike the standard's two-digit form, which is a second
open question.

This is categorically different from the eight surfaces above: it is executable
code that silently produces wrong IDs rather than documentation that describes
them, and fixing it may shift committed fixture IDs. Bundling a golden-churn risk
into a documentation plan would be exactly the over-scoping CLAUDE.md warns
against. **Action:** new GitHub issue + `FRAMEWORK-TODO.md` entry per
GOV-TODO-ISSUE-SPLIT (it is actionable by a non-finder, reproducible at
`file:line`, and consumer-visible).

### D8 — #343 closes only after its residual clauses are transferred

Issue #343's fix shape has three clauses (`FRAMEWORK-TODO.md:115-119`): (1) delete the

re-specified algorithm in the 4 templates + 3 READMEs; (2) same for
`doc-tdd-fixer/SKILL.md`'s divergent `SHA256(case content)`; (3) secondary —
align `.xxxx` examples to `placeholder: "0000"`. This plan implements (1) and
defers (2) → #342 and (3) → its own issue.

A bare `Closes #343` would therefore be a false claim: a future reader of the
closed issue would believe all three were resolved. And a comment posted on an
issue **this same PR closes** is not a durable surface. So the close is
sequenced:

1. Open the `placeholder`-semantics issue (clause 3).
2. Comment on #343 naming **#342** as the new owner of clause 2 and the new
   issue as the owner of clause 3, with the reason for each transfer.
3. Only then close #343 on the merge SHA.

`#344` closes outright — Part C implements its fix shape in full.

## File structure

### Modified — framework spec (spec-tier)

| File | Change |
|---|---|
| `framework/layers/02_PRD/PRD-TEMPLATE.yaml` | A — cross-ref form |
| `framework/layers/03_EARS/EARS-TEMPLATE.yaml` | A |
| `framework/layers/04_BDD/BDD-TEMPLATE.yaml` | A |
| `framework/layers/05_ADR/ADR-TEMPLATE.yaml` | A |
| `framework/layers/01_BRD/README.md` | B — `Algorithm:` → `norm()` + cross-ref |
| `framework/layers/02_PRD/README.md` | B |
| `framework/layers/03_EARS/README.md` | B |
| `framework/layers/07_TDD/README.md` | C — new `## Element IDs` |
| `framework/layers/07_TDD/TDD-TEMPLATE.yaml` | C — 5 keys + shape line + Phase-2 boundary clause |
| `framework/VERSION` | `0.38.0` → `0.39.0` |
| `framework/playbooks/*/*.md` (**51 files**) | F — `framework_spec_version` fanned out by `sync-version-refs.sh:288-299`; mechanical, not hand-edited |

The hand-authored spec diff is 9 files; the **declared** `framework/**` diff at
GATE-SPEC is ~60, because the version fanout rewrites 51 playbooks. Pass 2
caught this understatement — a spec-tier reviewer seeing 60 changed files
against a 9-file plan would reasonably block.

### Modified — propagation

| File | Change |
|---|---|
| `platforms/{hermes,claude-code-plugin}/FRAMEWORK_SPEC_VERSION` | `0.39.0` |
| `platforms/claude-code-plugin/framework/**` | F — regenerated by `tools/sync-plugin-framework.sh` (includes the 51 bundled playbook copies) |
| 52 × plugin `skills/*/SKILL.md` frontmatter | F — `framework_spec_version` fanned out by the sync hook |
| `README.md`, `docs/PARITY.md` | F — `sync-version-refs.sh:202,204` |
| `platforms/claude-code-plugin/README.md`, `platforms/hermes/README.md` | F — `sync-version-refs.sh:214-242` (prose + `cat FRAMEWORK_SPEC_VERSION` blocks) |
| `platforms/claude-code-plugin/docs/SKILL_AUTHORING.md` | F — `sync-version-refs.sh:279-281` |
| `CLAUDE.md` (current-state `framework spec \`X.Y.Z\`` literal) | F — `sync-version-refs.sh:200`. **Script-owned, not manual** — see step 5's warning; step 8 need only verify it |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | F — `sync-version-refs.sh:249-251` rewrites the hardcoded `assertEqual(_plugin_framework_spec_version(), "0.38.0")` tripwire at `:146`. **Mechanical, script-owned — flag it in the PR body**, or a spec reviewer will (reasonably) stop at a version-assertion test modified by a "documentation" PR |

No plugin **skill body**, no Hermes **prompt**, and no platform **product
version** is edited (D5, D6).

### Created

| File | Purpose |
|---|---|
| `tests/conformance/test_element_id_layer_contract.py` | E — the regression lock |

## Implementation sequence

1. **Test first** — write `test_element_id_layer_contract.py`; confirm it fails
   red on current `main` with **7** raw-input hits under `framework/layers/**`
   (PRD/EARS/BDD/ADR templates + BRD/PRD/EARS READMEs) and **1** missing
   `## Element IDs` section (TDD) and **1** template missing the five
   `id_standard` keys (TDD). A test that passes before the fix proves nothing.
2. **A + B** — the four templates and three READMEs.
3. **C** — TDD README section + template keys.
4. Re-run the test → green.
5. **F — propagation, in this exact order.** The ordering is load-bearing:
   `sync-version-refs.sh` rewrites `framework/playbooks/*/*.md` but its globs
   never reach the bundle, while `test_plugin_framework_bundle.py:61-72` asserts
   byte identity over the bundled `playbooks` subtree. Syncing the bundle
   *before* the version fanout lands 51 drifted copies and a red guard.
   **Do not hand-edit `CLAUDE.md`, `README.md`, `docs/PARITY.md`, or either
   platform `README.md` before 5.2 — they are script-owned.** Lines 198-252 of
   the fanout are gated on `fw_prev`, which the script detects *from CLAUDE.md's
   literal* (`sync-version-refs.sh:195-198`). If CLAUDE.md already reads
   `0.39.0`, then `fw_prev == fw_ver` and that block is **skipped silently,
   exit 0** (the rest of the script — `:254-299`, both `FRAMEWORK_SPEC_VERSION`
   pins, 52 SKILL.md, 51 playbooks — runs on its own detected prevs and is
   unaffected) — leaving README/PARITY/both platform READMEs and the
   conformance tripwire at `0.38.0`, surfacing much later as a red suite whose
   symptom names neither cause nor owner. `sync-version-refs.sh:200` **writes
   CLAUDE.md's version literal for you** — step 8 only verifies it, never
   authors it.
   1. Bump `framework/VERSION` → `0.39.0` and both `FRAMEWORK_SPEC_VERSION`.
   2. Run `scripts/sync-version-refs.sh` (or let the pre-commit hook fire) —
      fans the version into the 51 playbooks + 52 SKILL.md frontmatters.
   3. **Then** run `tools/sync-plugin-framework.sh`.
   4. Confirm `platforms/claude-code-plugin/framework/` is byte-identical to
      `framework/`, and `git status` is clean after a second sync run.
6. **Verify** — full conformance suite, Hermes pytest, corpus lint cross-check,
   GATE-SPEC pre-gate checklist + W003.
7. **Route the deferrals.** ✅ **Done 2026-07-26, ahead of the PR** — these are
   durable regardless of what happens to this plan:
   - [x] comment on #342 with the 19-surface union enumeration (D6), flagging
     `brd-validation-automation.md:179` as its highest-value item —
     [comment](https://github.com/vladm3105/aidoc-flow-framework/issues/342#issuecomment-5084448384);
   - [x] `FRAMEWORK-TODO.md` `IDGEN-NO-GENERATOR` count corrected 9 → 19 (union);
   - [x] [#351](https://github.com/vladm3105/aidoc-flow-framework/issues/351)
     (`_id_coordinator.py`, D7) + `IDCOORD-SECOND-HASH-IMPL` TODO entry, with the
     `sdd_doc_lint` AS11 docstring folded in;
   - [x] [#352](https://github.com/vladm3105/aidoc-flow-framework/issues/352)
     (`placeholder: "0000"`, D4) + `IDPLACEHOLDER-UNDEFINED` TODO entry;
   - [ ] comment on #343 transferring clauses 2 and 3, **then** close it (D8) —
     at merge, since the close is tied to the merge SHA.
8. **Docs of record** — `CHANGELOG.md`, `ROADMAP.md`, `plans/DECISIONS.md`
   (new D-number), `plans/FRAMEWORK-TODO.md` (two entries → Closed, one
   corrected, two added), `plans/HANDOFF.md`, `CLAUDE.md` current-state line
   (framework `0.38.0` → `0.39.0`; plugin/Hermes versions unchanged).

## Verification

| Check | Command | Expected |
|---|---|---|
| Regression lock | `python3 -m pytest tests/conformance/test_element_id_layer_contract.py` | green (red before step 2) |
| Conformance suite | `python3 -m pytest tests/conformance/` | ≥ 239 pass, no regressions |
| Hermes | `python3 -m pytest platforms/hermes/tests/` | no regressions |
| Bundle parity | `git add -A && bash tools/sync-plugin-framework.sh && git diff --name-only` | empty — a second sync run must be a no-op (catches the step-5 ordering trap). **Read the mechanic:** `git add -A` stages everything, then the re-sync writes the bundle again; `git diff` (worktree-vs-index) therefore shows *exactly what the second run changed*, and nothing else. Do **not** use `git status --porcelain` here — after staging it still prints `M`/`A` for all ~180 changed paths (index-vs-HEAD column), so it can never be empty and reads as false drift. Verified empirically. |
| Plugin release metadata | `python3 -m pytest tests/conformance/platforms/test_plugin_release_metadata.py` | green — plugin `VERSION` is unchanged, so `docs/TAGGING.md` needs no new row (D5) |
| Corpus cross-check (CLEANUP-PR-B item 5) | `python3 -m sdd_doc_lint examples/url-shortener/docs/` | unchanged from the pinned baseline (16 COV02 / 16 ACC01 / 6 STY02 / 5 REFGRAN01 / 1 TH-RES-001) |
| No behavior change | `git diff HEAD --stat tools/ tests/acceptance/` | empty — no linter and no fixture-minting code is touched. **`HEAD` is required:** the row above stages the tree, and a bare `git diff --stat` is worktree-vs-index, so it would report empty unconditionally and the guard would be vacuous. This guard is what the census's deferral of the 30th surface rests on. |
| GATE-SPEC pre-gate | `GATE-SPEC_FRAMEWORK.md:65-72` checklist | E001–E008 pass; `semver_impact: minor`, `change_level: C2` recorded |
| GATE-SPEC W003 | `framework/governance/SECURITY_REVIEW.md` checklist | assessment recorded — every edit in A/B/C is agent-facing template/README guidance |

The corpus check is expected **unchanged**, not improved: this plan alters no
lint rule and mints no IDs. A changed corpus finding count would mean the change
leaked into behavior and must be investigated before the PR opens.

## Risks

| # | Risk | Mitigation |
|---|---|---|
| 1 | Part E's scan locks only `framework/layers/**`, leaving the 19 platform surfaces unguarded | Accepted and stated (D6). Those surfaces belong to #342, which must add its own lock. The test's docstring says so, so a future reader does not mistake its green for full coverage. |
| 2 | Part C reads as a new contract, pushing the change to C3 | Framed as documenting an obligation `ID_NAMING_STANDARDS.md:162-164` already mandates. Founder ratifies at GATE-SPEC; MINOR/C2 proposed, not assumed. |
| 3 | The raw-string scan false-fires on prose that legitimately quotes the old form | Scoped to `framework/layers/**`. Post-fix the only residue in that tree is the `norm()` form (`BRD-TEMPLATE.yaml:141`), which does not contain the raw string. `ID_NAMING_STANDARDS.md:71` legitimately carries it (the transform is stated in the same sentence) and lives in `framework/governance/`, outside the scan. |
| 4 | Bundle drift if the sync script is forgotten | Step 5 is explicit and `tests/conformance/platforms/test_plugin_framework_bundle.py` fails the suite if missed. |
| 5 | Deferred items (D6/D7) get lost | Step 7 routes each to a durable surface — an issue comment, a new issue, TODO entries — before the PR opens, per GOV-TODO-ISSUE-SPLIT. |

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | The normalization transform is normative and is the load-bearing single-source contract | `Normalization transform (normative — PROVISIONAL-IDS-002)` | framework/governance/ID_NAMING_STANDARDS.md:81 |
| 2 | The standard states the raw input string but qualifies it with the transform in the same sentence, so it is correct in context | `are each passed through the` | framework/governance/ID_NAMING_STANDARDS.md:72 |
| 3 | BRD's template already uses the cross-reference pattern this plan propagates | `Do NOT re-specify the` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:137 |
| 4 | BRD's template shows the `norm()` shape line | `norm(title)` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:141 |
| 5 | PRD's template re-specifies the pre-normalization 3-step algorithm | `1. Build input:` | framework/layers/02_PRD/PRD-TEMPLATE.yaml:107 |
| 6 | EARS's template does likewise, with a per-layer scoping clause on the next line | `NOT upstream PRD/BRD content` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:98 |
| 7 | BDD's template does likewise | `1. Build input:` | framework/layers/04_BDD/BDD-TEMPLATE.yaml:92 |
| 8 | ADR's template does likewise | `1. Build input:` | framework/layers/05_ADR/ADR-TEMPLATE.yaml:102 |
| 9 | BRD's README publishes the raw input string | `Algorithm: SHA256 of` | framework/layers/01_BRD/README.md:142 |
| 10 | PRD's README publishes the raw input string | `Algorithm: SHA256 of` | framework/layers/02_PRD/README.md:44 |
| 11 | EARS's README publishes the raw input string | `Algorithm: SHA256 of` | framework/layers/03_EARS/README.md:60 |
| 12 | TDD's README has no Element IDs section (its headings end at Template) | `## Template` | framework/layers/07_TDD/README.md:32 |
| 13 | TDD's template has an `id_standard` block but no format/hash keys — only `state` + two-ID-form guidance | `id_standard:` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:25 |
| 14 | TDD test cases live in Section 4, so authored case IDs carry `04` | `test_cases:` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:117 |
| 15 | A TDD test case declares `name`, not `title`/`description` — basis for D3's refusal to invent a mapping | `name: "[Descriptive test name]"` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:133 |
| 16 | TDD is one of six layers that MUST carry element IDs | `Six of the eight layers` | framework/governance/ID_NAMING_STANDARDS.md:162 |
| 17 | SPEC and IPLAN are the two documented element-ID exemptions | `Element-ID exemptions` | framework/governance/ID_NAMING_STANDARDS.md:160 |
| 18 | The plugin's TDD fixer publishes a divergent input with no separate key clause, so input and compute cannot be split (D6 ground 2) | `SHA256(case content)` | platforms/claude-code-plugin/skills/doc-tdd-fixer/SKILL.md:251 |
| 19 | The plugin's TDD authoring skill publishes the same divergent input | `first 4 hex of SHA256 of the case content` | platforms/claude-code-plugin/skills/doc-tdd/SKILL.md:119 |
| 20 | Plugin fixer skills bind input and compute in one construct | `key = "{doc_id}:{section_id}:{title}:{description}"` | platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md:245 |
| 21 | Plugin authoring skills publish the raw input string | `"{doc_id}:{section_id}:{title}:{description}"` | platforms/claude-code-plugin/skills/doc-prd/SKILL.md:116 |
| 22 | #342's TODO entry already claims `doc-brd-fixer/SKILL.md:245` — the same line (D6 ground 1) | `doc-brd-fixer/SKILL.md:239,245` | plans/FRAMEWORK-TODO.md:46 |
| 23 | #342's fix shape deletes the SHA-256 instruction rather than re-pointing its input (count updated to 19 by this plan's step 7) | `to emit provisional ordinal IDs +` | plans/FRAMEWORK-TODO.md:62 |
| 24 | A Hermes creation prompt publishes the divergent `SHA256 of content` input | `- Hash: SHA256 of content` | platforms/hermes/prompts/templates/creation/UCC_PROMPT_EARS.md:74 |
| 25 | A Hermes remediation prompt does likewise | `- Hash: SHA256 of content` | platforms/hermes/prompts/templates/remediation/UCRem_PROMPT_EARS.md:186 |
| 26 | A second Hermes remediation prompt does likewise | `- Hash: SHA256 of content` | platforms/hermes/prompts/templates/remediation/UCRem_PROMPT_PRD.md:199 |
| 27 | `tests/acceptance/_id_coordinator.py` is a live second implementation that skips normalization (D7) | `def element_hash` | tests/acceptance/_id_coordinator.py:17 |
| 28 | It mints element IDs for fixtures, so a fix risks golden churn | `def element_id` | tests/acceptance/_id_coordinator.py:22 |
| 29 | Its smoke test checks determinism/format only — never parity with the canonical hash | `def test_element_hash_is_deterministic` | tests/acceptance/deterministic/test_id_coordinator.py:22 |
| 30 | The canonical implementation applies the transform to both fields before assembly | `_normalize_hash_field` | `tools/sdd_doc_lint/__init__.py:933` |
| 31 | `compute_element_hash` is the canonical entry point | `def compute_element_hash` | `tools/sdd_doc_lint/__init__.py:922` |
| 32 | The templates label the key as the **template** placeholder, contradicting their own `xxxx` bodies (D4) | `Template placeholder: "0000" represents the hash suffix.` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:147 |
| 33 | The declared placeholder key itself | `placeholder: "0000"` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:153 |
| 34 | The documented *provisional* form is `0001`, not `0000`, and forbids `xxxx` in produced docs (D4) | `Provisional ID form:` | framework/governance/ID_NAMING_STANDARDS.md:152 |
| 35 | Templated `xxxx` is separately sanctioned as pattern notation inside templates, so the mismatch breaks nothing today (D4) | `is a template-only placeholder.` | framework/governance/ID_NAMING_STANDARDS.md:212 |
| 36 | The registry's element pattern accepts 4–8 lowercase hex, consistent with the collision rule | `element:` | framework/registry/LAYER_REGISTRY.yaml:216 |
| 37 | The plugin bundles a byte-identical copy of `framework/`, so template edits require a re-sync | `class PluginFrameworkBundle` | tests/conformance/platforms/test_plugin_framework_bundle.py:31 |
| 38 | The only existing check over bundled layer files is a byte-equality diff — nothing reads `id_standard` content, so this drift had zero semantic coverage | `def _rel_files` | tests/conformance/platforms/test_plugin_framework_bundle.py:27 |
| 39 | The sync script propagates `layers` and `governance`, so template AND README edits reach the bundle | `SUBTREES=(layers governance registry playbooks)` | tools/sync-plugin-framework.sh:24 |
| 40 | A framework-spec change is never C1 and `major` ⇒ C3; minor/patch may be C2 | `GATE-SPEC-E003` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:87 |
| 41 | W003 requires a SECURITY_REVIEW assessment for agent-facing template/governance guidance | `GATE-SPEC-W003` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:105 |
| 42 | The in-repo precedent for a framework-MINOR/C2 plan carries the W003 assessment | `(GATE-SPEC W003) for T1/T2/T6 agent-facing wording.` | plans/SEED-ABSORPTION-001-PLAN.md:387 |
| 43 | MVP templates carry only bare metadata and publish no hash algorithm, so they carry no drift | `document_type: "tdd"` | framework/layers/07_TDD/TDD-MVP-TEMPLATE.yaml:14 |
| 44 | `TRACEABILITY.md` already shows the corrected `norm()` form | `norm(title)` | framework/governance/TRACEABILITY.md:85 |
| 45 | Current framework spec version is 0.38.0 | `0.38.0` | framework/VERSION:1 |
| 46 | Current plugin version is 0.23.4 | `0.23.4` | platforms/claude-code-plugin/VERSION:1 |
| 47 | A live, loaded Hermes reference ships a fourth normalization variant disagreeing with the standard on 5 of 6 steps (D6) | `re.sub(r'[^a-z0-9:]', '', inp.lower())[:200]` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/references/brd-validation-automation.md:179 |
| 48 | That reference is loaded by the orchestrator skill, so it is not orphaned | `references/brd-validation-automation.md` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:836 |
| 49 | A conformance test requires `docs/TAGGING.md` to carry a row for the current plugin version (D5) | `def test_tagging_doc_lists_current_plugin_release` | tests/conformance/platforms/test_plugin_release_metadata.py:135 |
| 50 | The version-sync script deliberately excludes `docs/TAGGING.md` as human-authored, so a plugin bump needs a hand-added row (D5) | `docs/TAGGING.md new release rows (human-authored)` | scripts/sync-version-refs.sh:52 |
| 51 | Repo precedent for a framework-only change with a re-vendored bundle leaves platform product versions unchanged (D5) | `plugin + Hermes **product** versions unchanged` | plans/D54-F04-EARS-RUBRIC-PLAN.md:10 |
| 52 | The version-sync script fans `framework_spec_version` into every playbook, but its globs never reach the bundle (step 5 ordering) | `for pb in framework/playbooks/*/*.md; do` | scripts/sync-version-refs.sh:293 |
| 53 | The bundle guard asserts byte identity over the synced subtrees, so an out-of-order sync lands 51 drifted playbook copies | `class PluginFrameworkBundle` | tests/conformance/platforms/test_plugin_framework_bundle.py:31 |
| 54 | #343's fix shape has three clauses; this plan implements one and transfers two (D8) | `IDHASH-NORM-TEMPLATE-DRIFT` | plans/FRAMEWORK-TODO.md:105 |
| 55 | The sibling READMEs carry the Phase-2 extraction caveat that the sibling templates lack — so D3's clause must be written into TDD's template (D3) | `extraction for this layer is Phase 2+` | framework/layers/04_BDD/README.md:85 |
| 56 | Lines 198-252 of the fanout are gated on a literal detected **from CLAUDE.md**, so hand-editing it first silently skips that block (step 5 warning) | `fw_prev="$(detect_version_in CLAUDE.md \` | scripts/sync-version-refs.sh:195 |
| 57 | The sync script rewrites a hardcoded version assertion inside a conformance test | `replace_in_file tests/conformance/platforms/test_plugin_release_metadata.py \` | scripts/sync-version-refs.sh:249 |
| 58 | That assertion is the tripwire the script edits | `self.assertEqual(_plugin_framework_spec_version(), "0.38.0")` | tests/conformance/platforms/test_plugin_release_metadata.py:146 |
| 59 | The linter names the template's `id_standard.state` as the authority for the ID-state convention — basis for D3's self-contradiction finding | `PROVISIONAL-IDS-001: doc-level ID-state. Authored docs declare` | `tools/sdd_doc_lint/__init__.py:556` |
| 60 | A linter docstring also states the pre-normalization input (30th census row, routed to #351) | `its ``{doc_id}:{section_id}:{title}:{description}`` content. A canonical` | `tools/sdd_doc_lint/__init__.py:1132` |
| 61 | The corpus's TDD elements carry hash-form IDs that downstream layers cite — the churn a provisional directive would have caused (D3) | `TDD.01.04.1a2c` | examples/url-shortener/docs/07_TDD/TDD-01.md:72 |
| 62 | The bundle sync is a destructive `rm -rf` + recopy, so bundle-after-fanout is correct and a re-run is a no-op | `rm -rf "$dest"` | tools/sync-plugin-framework.sh:46 |

## Docs to update

`CHANGELOG.md` · `ROADMAP.md` · `plans/DECISIONS.md` (new D-number) ·
`plans/FRAMEWORK-TODO.md` (two entries → Closed; `IDGEN-NO-GENERATOR` surface
count corrected; two entries added for D4 and D7) · `plans/HANDOFF.md` ·
`CLAUDE.md` current-state line — **framework `0.38.0` → `0.39.0` only; plugin
and Hermes product versions are unchanged (D5)**. The version literal itself is
**script-written** (`sync-version-refs.sh:200`), so this is a *verify*, not an
edit; any surrounding prose that needs rewording is the manual part.

The `FRAMEWORK-TODO.md` and issue-routing work in step 7 is **already done**
(2026-07-26) — what remains for the PR is the two entries → Closed and the #343
transfer-then-close sequence (D8).

## Implementation log

### 2026-07-26 — implemented; one founder-directed deviation from D4

All of Parts A/B/C/E/F shipped as planned. The four verification rows the plan
called out as traps all behaved as predicted:

- **Step-5 ordering held.** `framework/VERSION` + both `FRAMEWORK_SPEC_VERSION`
  → `scripts/sync-version-refs.sh` → **then** `tools/sync-plugin-framework.sh`.
  `CLAUDE.md` was left alone before the fanout, so the `fw_prev` detection at
  `sync-version-refs.sh:195-198` fired and the `:198-252` block ran: the
  current-state literal moved `0.38.0` → `0.39.0`, and the hardcoded tripwire at
  `test_plugin_release_metadata.py:146` was rewritten by the script, not by hand.
- **Second sync is a no-op.** `git add -A && bash tools/sync-plugin-framework.sh
  && git diff --name-only` → empty.
- **Corpus is unchanged from the pinned baseline** — 16 COV02 / 16 ACC01 /
  6 STY02 / 5 REFGRAN01 / 1 TH-RES-001, exactly as the plan predicted. The
  change did not leak into behavior.
- **`git diff HEAD --stat tools/ tests/acceptance/` is empty**, which is what the
  census's deferral of the 30th surface (#351) rests on.

Suites: conformance **243 passed / 670 subtests**; Hermes **570 passed**. The new
`test_element_id_layer_contract.py` was confirmed **red on pre-fix `main`** —
all four test methods failing (7 raw-input hits, TDD missing both its README
section and its `id_standard` keys, 5 `placeholder` hits) — before it went green.

**Deviation — D4 (`placeholder: "0000"`) overridden by founder decision.**

The plan deferred the key to [#352](https://github.com/vladm3105/aidoc-flow-framework/issues/352)
and had Part C add a sixth inert copy to TDD "for uniformity with its five
siblings." The founder instead chose **option (a) — delete the key** (2026-07-26),
so this PR:

- deletes `placeholder: "0000"` and its `Template placeholder: …` prose line from
  all five templates that carried it (BRD, PRD, EARS, BDD, ADR);
- does **not** add it to TDD, so no sixth copy is ever minted;
- reduces the plan's "five `id_standard` keys" to **four**
  (`format`/`hash_algorithm`/`hash_length`/`max_hash_length`) everywhere,
  including Part E's assertion;
- adds a **fourth** Part-E check — `test_no_template_reintroduces_the_placeholder_key`
  — so the deletion is locked rather than merely done.

The deferral was correct as written (a merged plan should not unilaterally settle
a governance question mid-drift-fix) and so was the override (once the owner
ruled, shipping it here avoided creating the sixth copy). Recorded as **D-0067**
and ratified in the spec register as **GD-09**. #352 closes on this PR's merge
SHA rather than surviving as a follow-up.

**One unplanned fix.** `test_spec_hygiene.py::test_no_engine_tokens` (the GD-06
engine-agnosticism guard) failed on the first draft of the GD-09 entry, which
named a platform and a platform file path inside `framework/governance/`. The
guard was right: the spec register is engine-agnostic like the rest of the spec.
Both references were reworded to "platform authoring surface(s)" — the
engine-specific detail lives in this plan and in `CHANGELOG.md`, which are
project surfaces, not spec surfaces.

### GATE-SPEC record

**Pre-gate checklist (§2.1)** — all items satisfied:

| Item | Status |
|---|---|
| Change edits `framework/` | ✅ templates, READMEs, governance register, `VERSION` |
| `change_description.why` / `.trigger` populated | ✅ GD-09 *Context* (why) + issues #343/#344/#352 (trigger) |
| `semver_impact` set | ✅ `minor` |
| `change_level` proposed (≥ C2) | ✅ **C2** |
| `CHANGELOG.md` entry drafted | ✅ |
| C3 platform-owner notification | n/a — not C3 |

**Error checks:** E001 provenance ✅ · E002 `minor`/C2 ✅ · E003 ≥ C2 ✅ ·
E004 n/a (not C3) · E005 `framework/VERSION` bumped ✅ · E006 both
`FRAMEWORK_SPEC_VERSION` == `0.39.0` ✅ · E007 conformance green ✅ ·
E008 `CHANGELOG.md` changed ✅.

**W003 — `SECURITY_REVIEW.md` assessment** (agent-facing template/governance
guidance, so the check applies):

| Threat | Assessment |
|---|---|
| T1 — credentials / tokens / personal data | ✅ none. The diff adds no literals beyond version strings and a synthetic example ID (`TDD.01.04.f19c`). |
| T2 — instruction from external/untrusted content acted on | ✅ none. Every change traces to `ID_NAMING_STANDARDS.md`, D-0062, or the three issues; no external content was ingested. |
| T3 — promoted rule/threshold cites a traceable source | ✅ the entire change *removes* per-layer rule statements in favour of citing one authority; the new TDD text cites the same standard rather than introducing a threshold. |
| T4 — generated commands / paths stay in scope | ✅ no command or path is generated. The one executable artifact added, `test_element_id_layer_contract.py`, only reads under `framework/layers/**`. |
| Links / inline markup sanitized | ✅ no new links or click handlers; added markup is plain fenced text and backticked paths. |

**Net security posture: improved.** Deleting six divergent statements of one
algorithm reduces the chance an agent follows a stale instruction — which is the
concrete failure this plan exists to fix.

## Review log

### Pass 1 — 2026-07-26 — independent (`verified-planning-reviewer`, fresh context)

Seven load-bearing findings, all reproduced against source before folding.

1. **Part E could not produce the red result step 1 demanded, and locked none of
   the plugin surfaces.** The scan is scoped to `framework/layers/**`, which
   holds 7 raw-string hits, not the 19 the draft claimed; the other 12 lived
   under `platforms/*/skills/`. *Resolved:* step 1 now states 7, and Risk 1
   states plainly that the lock does not cover platform surfaces.
2. **The Hermes census was wrong.** The draft asserted the only Hermes surfaces
   state output form and "never publish an input string". Three others publish
   the divergent `SHA256 of content` form (`UCC_PROMPT_EARS.md:74`,
   `UCRem_PROMPT_EARS.md:186`, `UCRem_PROMPT_PRD.md:199`). *Resolved:* full
   23-surface census table added; the false justification is deleted; the three
   are routed to #342.
3. **The claimed orthogonality with #342 was false.** #342's TODO entry already
   names `doc-brd-fixer/SKILL.md:245` and its fix shape *deletes* the SHA-256
   instruction; and on the TDD surfaces input and compute are a single
   expression that cannot be edited separately. *Resolved:* Part D dropped
   entirely; D6 records both grounds and the accepted cost.
4. **D4's rejection of #343's secondary observation rested on a false premise.**
   The templates label the key "Template placeholder"; `0000` appears nowhere in
   `framework/governance/`; the documented provisional form is `0001`.
   *Resolved:* D4 rewritten — the observation is valid, deferred because the key
   is inert and its meaning is an unresolved governance question, not because it
   is a non-defect. The wrong reasoning will not be posted to #343.
5. **A 21st surface, and the only executable one, was missing:**
   `tests/acceptance/_id_coordinator.py:17-19` hashes without normalization and
   mints fixture IDs; its smoke test never checks parity. *Resolved:* D7 — new
   issue + TODO entry, out of scope with stated rationale (golden-churn risk).
6. **GATE-SPEC pre-gate and W003 were declared in the header but absent from
   Verification.** *Resolved:* two rows added, matching the
   SEED-ABSORPTION-001 precedent.
7. **Part D would have replaced a concrete-but-wrong TDD instruction with an
   unexecutable one**, since TDD cases carry no `title`/`description` while the
   plan refused to define the mapping. *Resolved:* moot — Part D dropped (F3);
   D3 now states the non-definition explicitly for the framework surfaces.

Reviewer also verified sound, so as not to be re-litigated: no *framework-layer*
surface was missed (BDD/ADR READMEs carry `## Element IDs` with no `Algorithm:`
line; MVP templates publish nothing; `PRD-00_index.TEMPLATE.md:88` is output-form
plus cross-ref); Part E check (2) is satisfiable today for PRD/EARS/BDD/ADR;
Risk 3's false-positive analysis holds; MINOR/C2 is correctly classified; the
corpus baseline and "unchanged" expectation are right.

**Result:** 7 findings folded; scope reduced from 19 surfaces to 8; two
deferrals newly routed.

### Pass 2 — 2026-07-26 — independent (`verified-planning-reviewer`, fresh context)

Dispatched to attack the **fold**, not to re-find Pass 1's items. Six
load-bearing findings, all reproduced against source before folding. Pass 1's
patches did introduce new defects — three of the six are consequences of the
fold itself, which is the case for running a second cycle.

1. **The plugin `VERSION` bump would have turned the suite red.**
   `test_plugin_release_metadata.py:135` requires `docs/TAGGING.md` to carry a
   row for the current plugin version, and `sync-version-refs.sh:52` excludes
   that file as human-authored. Neither `TAGGING.md` nor the plugin `CHANGELOG`
   was in the plan's file tables. *Resolved:* dissolved by finding 2.
2. **The plugin bump was against precedent anyway.**
   `D54-F04-EARS-RUBRIC-PLAN.md:10` is the same case (framework-only change,
   bundle re-vendored) and states *"plugin + Hermes product versions
   unchanged"*. *Resolved:* D5 rewritten — framework `VERSION` is the only
   version that moves; a Verification row now asserts the release-metadata test
   stays green.
3. **Step 5's ordering guaranteed a red bundle-drift guard.** The framework
   version bump fans out to **51** `framework/playbooks/*/*.md` files
   (`sync-version-refs.sh:293`) whose 51 bundled copies the hook never touches,
   while the bundle guard asserts byte identity. The draft synced the bundle
   *first*. *Resolved:* step 5 is now an explicit 4-step order (bump → version
   sync → bundle sync → confirm), with the reason inline; the file table
   declares the 51 playbooks so the ~60-file spec diff is not a surprise at
   GATE-SPEC.
4. **`Closes #343` was a false claim.** #343 has three fix clauses; this plan
   implements one and defers two, and the draft proposed to record one deferral
   as a comment on the very issue it closes. *Resolved:* new **D8** — clause 3
   gets its own issue, clause 2 transfers to #342 by explicit comment, and #343
   closes only after both transfers are recorded. Header downgraded to a
   sequenced close.
5. **The census was wrong twice, and step 7 would have shrunk #342's scope.**
   The table summed to 25 against a stated 23; and posting "15 surfaces" to
   #342 would have replaced its existing 9 — which already include
   `doc-naming/SKILL.md:106` and both `UCC_PROMPT_{BRD,PRD}` — with a set that
   omits all three. *Resolved:* census recounted to **29** with a stated sum;
   step 7 posts the **union (19)**, never a replacement. Pass 2 also surfaced a
   genuinely new surface: `brd-validation-automation.md:179`, a *loaded*
   reference (`sdd-orchestrator/SKILL.md:836`) carrying a **fourth**
   normalization variant that disagrees with `ID_NAMING_STANDARDS.md:88-93` on
   five of six steps — now flagged as #342's highest-value item.
6. **Pass 1's finding 7 was declared "moot" but had only moved.** Dropping
   Part D removed the unexecutable TDD instruction from the plugin skills, but
   Part C was still going to add a `norm(title)`/`norm(description)` shape line
   to a template whose test cases have neither field — replacing silence with an
   instruction no author can follow. *Resolved:* D3 now makes an explicit
   Phase-2 extraction-boundary clause a **required deliverable** of Part C, with
   the drafted YAML, directing authors to provisional ordinal IDs (the form
   D-0040 already sanctions) instead of a guessed mapping.

Also fixed: the `doc-tdd-fixer/SKILL.md` line-number inconsistency between D6
(`:250`) and ledger claim 18 (`:251`) — both now `:251`.

**Result:** 6 findings folded. Pass 3 required — findings 3, 5 and 6 changed
load-bearing deliverables (sequence, durable-surface content, template text),
so the fold needs independent re-validation before this plan is called ready.

### Pass 3 — 2026-07-26 — independent (`verified-planning-reviewer`, fresh context)

Dispatched to validate Pass 2's never-reviewed deliverables and return a
ready/not-ready verdict. **Verdict returned: NOT READY**, with 6 load-bearing +
2 minor findings. All eight are folded below; three were direct consequences of
Pass 2's own fold.

1. **The reversed plugin bump survived in "Docs to update".** D5 and step 8 said
   "no platform version bump"; the trailing checklist — the section an
   implementer works from last — still ordered `plugin 0.23.4 → 0.23.5`,
   re-creating the red Pass 2 finding 1 had eliminated. *Resolved:* struck.
2. **The census decomposition was off by one and would have written a wrong
   number to two durable surfaces.** `29 = 8 + 20 + 1` dropped the
   already-correct `BRD-TEMPLATE.yaml` row and inflated #342 by one; #342's rows
   are 12+1+5+1 = **19**. *Resolved:* decomposition corrected, all six "20"
   occurrences → 19. This is the second time the census has been wrong; it is
   now stated with an explicit sum so the next reader can check it.
3. **`sync-version-refs.sh` rewrites six more files than declared** — including
   a **hardcoded version assertion inside a conformance test**
   (`:249-251` → `test_plugin_release_metadata.py:146`). Declared diff was ~60
   files; it is ~66, and one of them is a modified test. *Resolved:* six rows
   added to the propagation table, with a note to flag the auto-edited test in
   the PR body so a spec reviewer does not stop at it.
4. **A second ordering trap in step 5.** The entire framework fanout is gated on
   `fw_prev`, detected *from CLAUDE.md's literal* (`:195-198`). Hand-editing
   CLAUDE.md first makes `fw_prev == fw_ver`, silently skipping lines 198-252
   and exiting 0 — leaving README/PARITY/both platform READMEs and the tripwire
   stale, surfacing later as a red suite naming neither cause nor owner. The
   plan invited exactly that by listing CLAUDE.md as a manual step-8 edit.
   *Resolved:* explicit script-ownership warning at the head of step 5.
5. **The bundle-parity command could not pass where it runs.** At step 6 the
   tree holds ~66 uncommitted files, so a bare `git status --porcelain` is
   necessarily non-empty and reads as bundle drift. *Resolved:* `git add -A &&`
   prefix, with the reason stated.
6. **D3's Pass-2 clause was an overreach and is withdrawn.** Instructing TDD
   authors to emit provisional ordinal IDs with `id_state: provisional` was
   (a) self-contradictory — it lands inside a block declaring
   `state: canonical` (`TDD-TEMPLATE.yaml:26`), the key the linter names as the
   convention's authority (`sdd_doc_lint/__init__.py:556-562`); (b) proving too
   much — PRD/EARS/BDD/ADR are in the identical position and instruct nothing of
   the sort; (c) carrying unstated consequences — a standing `PROV01` on every
   TDD, ordinal IDs replacing the hash-form IDs IPLAN cites at
   `examples/url-shortener/docs/07_TDD/TDD-01.md:72-79` on the next corpus regen,
   and a direct spec-vs-plugin conflict with `doc-tdd/SKILL.md:119`.
   *Resolved:* the directive is dropped; TDD carries the same Phase-2 caveat its
   five siblings already use. Pass 2's real insight — that the boundary must be
   *written down* — is kept.
7. **(minor) A 30th surface:** the AS11 docstring in the canonical linter
   (`tools/sdd_doc_lint/__init__.py:1131`) plus its two vendored copies state
   the input with no transform. *Resolved:* added to the census, folded into
   D7's issue — not fixed here, since `git diff --stat tools/` must stay empty.
8. **(minor) Part E needs an allow-list, not a glob.** A template glob sweeps in
   MVP/index templates; a README glob sweeps `06_SPEC`/`08_IPLAN`, the two
   documented exemptions — 3–5 spurious reds either way. *Resolved:* Part E now
   requires a hardcoded list of the six canonical pairs.

Reviewer independently confirmed sound, and these are not to be re-litigated:
D5's no-plugin-bump reversal (the only version couplings run through
`FRAMEWORK_SPEC_VERSION`); step 5's bundle-after-fanout order; the 51-playbook /
52-skill counts; Part E's red-state counts (7 / 1 / 1) and the fact that all four
Part-A templates already carry the `ID_NAMING_STANDARDS.md` cross-reference so
check (2) adds no reds; `[a-f0-9]{4,8}` accepting ordinal IDs; GATE-SPEC
E001–E008 + W003 coverage.

**Result:** 8 findings folded. **The 3-pass circuit-breaker (OPS-0066) is now
reached.** Per that rule a fourth independent pass is not dispatched; the fold
above is surfaced to the founder for a go/no-go instead. Nothing is known to be
outstanding, but the Pass-3 fold — like Pass 2's — has not itself been
independently validated, and the last two passes each found real defects in the
preceding fold. **Founder decision required before the plan PR opens.**

### Pass 4 — 2026-07-26 — independent (`verified-planning-reviewer`, fresh context)

Dispatched by **explicit founder override of the OPS-0066 circuit-breaker**,
scoped narrowly to validating the Pass-3 fold. Verdict: NOT READY — 4 blocking +
6 minor. Two of the four blockers were defects *introduced by* the Pass-3 fold,
which is exactly what the override was bought to find.

1. **The Pass-3 fix to the bundle-parity command did not work.** `git add -A &&
   … && git status --porcelain` still cannot return empty: `--porcelain` reports
   the index-vs-HEAD column too, so every staged path prints `M`/`A`. The fix
   moved the failure from column Y to column X. *Verified empirically in a
   throwaway repo before folding.* *Resolved:* the check is now
   `git add -A && bash tools/sync-plugin-framework.sh && git diff --name-only` —
   staging first means a plain `git diff` shows exactly what the re-sync changed
   and nothing else. Also confirmed empirically.
2. **That same `git add -A` silently voided the "No behavior change" guard.**
   `git diff --stat tools/` is worktree-vs-index, so after staging it reports
   empty unconditionally — and the census's rationale for deferring the 30th
   surface (`git diff --stat tools/` must stay empty) rested on it. *Resolved:*
   `git diff HEAD --stat`, with the dependency spelled out in the row.
3. **A stale surface count survived the Pass-3 recount** — Risk 1 still said "15
   platform surfaces" against 19 everywhere else. Load-bearing because Risk 1's
   mitigation routes that figure into the new conformance test's docstring, a
   durable code surface. *Resolved:* → 19.
4. **Step 7's own execution invalidated two citations into
   `FRAMEWORK-TODO.md`.** Rewriting the `IDGEN-NO-GENERATOR` entry shifted claim
   22 / D6 ground 1 (`:45` → `:46`) and D8 (`:67-71` → `:115-119`). *Resolved:*
   both re-pointed; gate re-run clean.

Minor, all folded: `CLAUDE.md` added to the propagation table (it is
**script-written** at `sync-version-refs.sh:200`, so step 8 verifies rather than
authors it); "~66 uncommitted files" → ~180 (the bundle doubles every synced
path); D3's "five sibling READMEs" → **four** (`01_BRD/README.md:142`
deliberately differs — BRD §7 extraction is the one that shipped); D4/D7/D8
prose refreshed with the now-filed #351/#352; ledger row 60 / census row
harmonized on `:1132`; Part E's glob rationale extended to `SPEC-TEMPLATE.yaml`
and `IPLAN-TEMPLATE.yaml`; the step-5 warning's "the entire framework fanout is
gated" narrowed to lines 198-252 (`:254-299` runs on its own detected prevs).

Pass 4 independently **confirmed correct** — not to be re-opened: the versioning
fold is consistent end to end (no section orders a platform bump); the census
sums to 30 and decomposes `1 + 8 + 19 + 2`; D3's withdrawal is right, and the
withdrawn directive's third consequence is *worse* than Pass 3 stated —
`examples/url-shortener/docs/08_IPLAN/IPLAN-01.md` cites `TDD.01.04.*` **14
times**, so ordinal IDs would have broken live downstream citations; Part E's
six pairs are the right six; ledger rows 56-62 all mean what they are cited for;
and the 7-hit red-state count re-verified independently.

**Result:** 10 findings folded. All four blockers were mechanical (two
verification commands, one stale integer, two line numbers) — no design defect
was found, and every substantive Pass-2/Pass-3 decision was confirmed. The fold
above is again unvalidated, and the founder override covered one extra pass, so
this is surfaced rather than escalated to a Pass 5.
