# IDGEN-NO-GENERATOR Plan — ship the generator, then stop asking LLMs to hash

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | IDGEN-NO-GENERATOR                                           |
| Type           | tooling + platform surfaces                                  |
| Status         | PLANNED — 2026-07-26                                         |
| Depends on     | D-0040, D-0061, D-0062, **D-0067 / GD-09** (the spec-side single-source fix must land first) |
| Closes         | [#342](https://github.com/vladm3105/aidoc-flow-framework/issues/342); clause 2 of [#343](https://github.com/vladm3105/aidoc-flow-framework/issues/343) |
| Version impact | **plugin MINOR**, **Hermes MINOR**, **no `framework/` change** and no spec bump — see D5 |
| Gate           | Not GATE-SPEC (nothing under `framework/` is touched)        |

## Objective

The framework ships a correct element-ID hash implementation
(`compute_element_hash()`, `tools/sdd_doc_lint/__init__.py:922`) but exposes it
**only as a verifier**. Meanwhile **19 authoring surfaces instruct an LLM to
compute SHA-256 by hand** — an instruction that is unexecutable correctly and
that contradicts PROVISIONAL-IDS-002's own ratified position
(`plans/PROVISIONAL-IDS-002-PLAN.md:112-114`: *"LLMs can't compute SHA-256
reliably, so real hashes come from the deterministic `rehash --fix` pass, not
from prompting"*).

This plan ships the generator side and then rewrites all 19 surfaces so no
surface asks an engine to hash anything.

## The tension this plan has to resolve honestly

The obvious fix — "point the skills at the generator" — **does not work for five
of the six layers**, and a plan that pretends otherwise would ship an instruction
authors cannot follow.

`ID_NAMING_STANDARDS.md` defines byte-exact **field extraction** for **BRD §7
only** (PROVISIONAL-IDS-002 Phase 1). GD-09 has just re-affirmed that PRD, EARS,
BDD, ADR and TDD have no defined extraction boundary and that inventing one is a
new normative contract, not a documentation fix. A generator is a pure function
of `(doc_id, section_id, title, description)`; if a layer does not define which
content supplies `title` and `description`, **there is nothing correct to pass
it.**

So the 19 surfaces split by what is actually available to them:

| Surface class | What it can do today | Instruction after this plan |
| --- | --- | --- |
| BRD §7 (extraction defined) | call the generator | **call the tool**; never hash in-prompt |
| PRD / EARS / BDD / ADR / TDD | nothing correct | **emit provisional ordinal IDs** (`0001`, `0002`, …) + `id_state: provisional`, and state that canonicalization is a deterministic tool pass that has not shipped for this layer yet |

That second row is exactly what D-0040 and `ID_NAMING_STANDARDS.md:152-155`
already prescribe. This plan does not invent it; it makes 19 surfaces stop
contradicting it.

## Scope

**In:**

- **A — `--compute`.** A subcommand exposing `compute_element_hash()` so a caller
  has something to call:
  `python -m sdd_doc_lint.rehash --compute --doc-id BRD-01 --section-id 07
  --title "…" --description "…"` → the 4-char hash on stdout (`--length 8` for
  the collision form). Layer-agnostic: the caller supplies the fields, so it
  serves any layer whose extraction boundary is defined — today, BRD §7.
- **B — `--fix`.** Rewrites a canonical BRD's §7 FR element IDs in place to their
  computed hashes, reusing the extraction `rehash_check` already performs. This
  is the deterministic pass PROVISIONAL-IDS-002 named. **BRD §7 only**, and the
  CLI says so when pointed at anything else rather than silently doing nothing.
- **C — the 19 surfaces**, rewritten per the table above. Enumerated in
  **D6** so none is silently dropped.
- **D — the fourth normalization variant.**
  `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/references/brd-validation-automation.md:179`
  ships **runnable** `generate_hash()` code, reachable via a loaded reference
  (`sdd-orchestrator/SKILL.md:836`). It disagrees with the standard on five of
  six transform steps — `lower()` not `casefold()`, no NFC, applied to the
  **assembled** string not per-field, deletes spaces entirely, truncates at 200
  not 100. Replaced by a call to A. **This is the highest-value single item**:
  it is the closest thing in the repo to the ad-hoc script an agent was observed
  writing.
- **E — regression lock.** A conformance test asserting no platform authoring
  surface instructs in-prompt SHA-256 — the platform-side counterpart to
  `test_element_id_layer_contract.py`, whose docstring explicitly says it does
  not cover these files.

**Out of scope:**

- **Defining a field-extraction boundary for any non-BRD layer.** That is
  PROVISIONAL-IDS-002 Phase 2 and a normative spec change (GATE-SPEC + a
  `framework/VERSION` bump). Doing it here would make this a spec plan.
- **Corpus reconciliation** — regenerating example-corpus IDs through `--fix`.
  Phase 2+; the corpus is regenerated wholesale.
- **`tests/acceptance/_id_coordinator.py`** — [#351](https://github.com/vladm3105/aidoc-flow-framework/issues/351),
  its own plan.
- **Any `framework/` edit.** GD-09 has just settled the spec side; this plan
  consumes that contract rather than re-opening it.

## Approach / Design

### D1 — `--compute` before `--fix`, and both in `rehash.py`

`--compute` is the smaller, more broadly useful half: it is layer-agnostic, has
no file I/O, and is what a skill or a human can call directly. `--fix` is
narrower (BRD §7 only) but is the piece that makes "canonicalization is a tool
pass" true rather than aspirational.

Both land in `rehash.py` rather than a new module: it already owns the
element-ID CLI surface, already imports `rehash_check`, and a second entry point
would be a third place to look. The existing `parser.error("nothing to do: pass
--check")` becomes a mutually-exclusive group over the three modes.

**`--fix` writes only `id_state: canonical` docs.** `rehash_check` already skips
`provisional` docs (`rehash.py:10-11`); `--fix` must inherit that skip, or it
would canonicalize IDs the author deliberately marked as placeholders.

### D2 — `--fix` must be honest about its scope in the CLI, not just the docs

A `--fix` that silently no-ops on a PRD is the same failure class this whole arc
exists to fix: a tool that returns a plausible non-answer instead of an error.
Pointed at a non-BRD document, or at a BRD with no §7, it **exits non-zero with a
message naming the layer, the reason (no defined extraction boundary), and the
issue tracking Phase 2**. Silence is the bug.

### D3 — The skills call the tool; they never inline the algorithm

Where a surface currently says *"`key = "{doc_id}:{section_id}:{title}:{description}"`
→ first 4 hex of SHA256(key)"*, the replacement is a **command**, not a corrected
formula:

```
python -m sdd_doc_lint.rehash --compute --doc-id <ID> --section-id <SS> \
    --title <title> --description <description>
```

Re-stating a *corrected* algorithm in 19 places is the mistake GD-09 just
finished undoing on the spec side. The surfaces get a call and a cross-reference
to `governance/ID_NAMING_STANDARDS.md`; none of them gets the algorithm.

### D4 — Provisional ordinals for the five layers without an extraction boundary

Those surfaces are instructed to emit `TYPE.NN.SS.0001`, `.0002`, … plus
`id_state: provisional`, per `ID_NAMING_STANDARDS.md:152-155`.

**Two consequences must be stated in the surfaces, not discovered later:**

1. **`PROV01` will fire** — one doc-level advisory per artifact. That is the
   designed signal, not a regression, and the surfaces say so.
2. **`HASH01` uniqueness still applies**, so ordinals must be distinct within a
   section (`ID_NAMING_STANDARDS.md`). A surface that says "use `0001`" without
   saying "distinct per element" invites a duplicate-ID artifact.

**Open question for the founder, flagged not answered:** the layer templates
declare `state: canonical` in `id_standard`. If the authoring surfaces now emit
`provisional`, the template default and the authoring instruction disagree.
GD-09 declined to change `state:` for TDD on the grounds that it would make TDD
the only layer with a different default. That reasoning now applies to *five*
layers at once, which is a materially different question and is the one part of
this plan that may need a spec change after all. **This must be resolved before
implementation**, and if the answer is "change the template default," this plan
gains a `framework/` dependency and a GATE-SPEC gate.

### D5 — Version impact

**Plugin MINOR** — 13 skills change their authoring instructions, which changes
what the engine produces. **Hermes MINOR** — 6 prompts plus the loaded reference,
same reasoning. **`tools/` gains two CLI modes**, additive, and re-vendors into
both platforms.

**No `framework/` change and no spec bump** — unless D4's open question is
answered "change the template default," in which case this becomes a spec plan
and must be re-scoped. That conditional is why D4 is a blocker rather than a
note.

### D6 — The 19 surfaces, enumerated

Verified by live grep, not copied from the issue (which listed 9 before the
2026-07-26 correction to 19):

| # | Surface | Class |
| --- | --- | --- |
| 1-6 | plugin `doc-{brd,prd,ears,bdd,adr,tdd}/SKILL.md` | creation |
| 7-12 | plugin `doc-{brd,prd,ears,bdd,adr,tdd}-fixer/SKILL.md` | fixer |
| 13 | plugin `doc-naming/SKILL.md` | migration |
| 14-16 | Hermes `prompts/templates/creation/UCC_PROMPT_{BRD,PRD,EARS}.md` | creation |
| 17-18 | Hermes `prompts/templates/remediation/UCRem_PROMPT_{PRD,EARS}.md` | remediation |
| 19 | Hermes `prompts/templates/review/UCR_PROMPT_BRD.md` | review |
| + | Hermes `.../sdd-orchestrator/references/brd-validation-automation.md` | **runnable code — item D** |

BRD surfaces (1, 7, 14, 19) take the **call-the-tool** instruction; the rest take
**provisional ordinals**. `doc-naming` (13) is a migration surface and takes
both, branching on layer.

### D7 — Why this plan waits for GD-09

`doc-tdd-fixer/SKILL.md` specifies `SHA256(case content)` — a *different input
shape* from every other surface. GD-09 gave TDD a framework-side element-ID
contract for the first time, so there is now something to reconcile that surface
*against*. Doing this work first would have meant correcting it against nothing.

## Implementation sequence

1. **Resolve D4's open question with the founder.** If the answer changes
   `state:` in the layer templates, stop and re-scope as a spec plan.
2. **A — `--compute`**, with unit tests including the transform's edge cases
   (uppercase, punctuation, non-NFC, whitespace runs, >100-char truncation) and a
   parity assertion against `compute_element_hash()` directly.
3. **B — `--fix`**, test-first: a fixture BRD with drifted §7 IDs, `--check` red
   → `--fix` → `--check` green; plus the D2 refusal cases (non-BRD, no §7,
   `provisional`) asserting non-zero exit and a message naming the reason.
4. **E — the regression lock**, confirmed **red** against the 19 unfixed
   surfaces before any of them is edited. The count it reports is the work list.
5. **D — the runnable fourth variant.** First, because it is the highest-value
   item and the only one shipping executable wrong code.
6. **C — the 19 surfaces**, BRD-class first (they get the simpler instruction),
   then the five provisional-ordinal layers.
7. **Re-run E → green.** Then `bash tools/sync-plugin-framework.sh` for the
   re-vendored `tools/`.
8. **Verify** — table below.
9. **Docs of record** + close #342 and #343 (clause 2).

## Verification

| Check | Command | Expected |
| --- | --- | --- |
| Generator parity | `python3 -m pytest tests/` (new unit tests) | `--compute` output == `compute_element_hash(...)[:4]` on every case |
| `--fix` round-trip | `rehash --check` → `--fix` → `--check` | red → green on a drifted fixture |
| `--fix` refuses out of scope | `rehash --fix <PRD>` | **non-zero**, message names the layer + Phase 2 |
| Regression lock | the new conformance test | red before step 5, green after step 7 |
| Conformance | `python3 -m pytest tests/conformance/` | no regressions |
| Hermes | `python3 -m pytest platforms/hermes/tests/` | no regressions |
| Vendoring | `md5sum tools/sdd_doc_lint/*.py platforms/*/sdd_doc_lint/*.py` | identical per file |
| **Corpus unchanged** | `python3 -m sdd_doc_lint examples/url-shortener/docs/` | 16 COV02 / 16 ACC01 / 6 STY02 / 5 REFGRAN01 / 1 TH-RES-001 — `--fix` is opt-in and is NOT run over the corpus here |
| No spec change | `git diff --stat framework/` | empty (unless D4 says otherwise) |

## Risks

| # | Risk | Mitigation |
| --- | --- | --- |
| 1 | **D4's open question turns this into a spec plan mid-implementation** | Step 1 forces it first. This is the plan's main scheduling risk, not a detail |
| 2 | `--fix` is run over the example corpus and churns it | `--fix` is opt-in, never in the default lint, and the verification table pins the corpus baseline. The corpus is regenerated wholesale anyway |
| 3 | Rewriting 19 surfaces drifts them apart again | E locks the negative property (no in-prompt SHA-256). It cannot lock that each says the *right* thing — stated plainly, as GD-09 stated its own scope limit |
| 4 | The provisional-ordinal instruction makes every new artifact carry `PROV01` | Designed behaviour, surfaced in D4 so it is not mistaken for a regression. If the advisory noise is unacceptable, that is D4's question again |
| 5 | Plugin MINOR requires a `docs/TAGGING.md` row + plugin `CHANGELOG.md` entry | Unlike ELEMENT-ID-LAYER-CONTRACT-001 this *is* real plugin content, so the row is legitimate. `test_plugin_release_metadata.py:135` enforces it |

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | The canonical hash exists and returns the full digest for callers to slice | `def compute_element_hash` | `tools/sdd_doc_lint/__init__.py`:922 |
| 2 | The transform is implemented in the documented order | `def _normalize_hash_field` | `tools/sdd_doc_lint/__init__.py`:908 |
| 3 | The CLI has only `--check` and `--format`; there is no generator | `parser.error("nothing to do: pass --check")` | tools/sdd_doc_lint/rehash.py:52 |
| 4 | `--check` is opt-in, advisory, and skips `provisional` docs | `a ``provisional`` doc is exempt` | tools/sdd_doc_lint/rehash.py:11 |
| 5 | PROVISIONAL-IDS-002 already ruled that hashes come from a tool pass, not prompting | `LLMs can't compute SHA-256 reliably` | plans/PROVISIONAL-IDS-002-PLAN.md:112 |
| 6 | A fixer surface instructs in-prompt SHA-256 over a colon-joined key | `first 4 hex of SHA256(key)` | platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md:246 |
| 7 | A creation surface does likewise | `SHA256(` | platforms/claude-code-plugin/skills/doc-brd/SKILL.md:125 |
| 8 | The loaded reference ships runnable code with a fourth normalization variant | `def generate_hash` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/references/brd-validation-automation.md:177 |
| 9 | …whose transform disagrees on five of six steps | `re.sub(r'[^a-z0-9:]', '', inp.lower())[:200]` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/references/brd-validation-automation.md:180 |
| 10 | The provisional form is section-ordinal hex, explicitly not `xxxx` | `Do NOT use ``xxxx``` | framework/governance/ID_NAMING_STANDARDS.md:155 |
| 11 | `HASH01` uniqueness applies regardless of `id_state`, so ordinals must differ | `distinct ordinals are required` | framework/governance/ID_NAMING_STANDARDS.md:157 |
| 12 | The spec-side lock deliberately excludes these platform surfaces | `Scope is` + `only` | tests/conformance/test_element_id_layer_contract.py:24 — **forward reference**: the file lands with PR #357 (GD-09), which this plan depends on |

## Docs to update

`CHANGELOG.md` · `platforms/claude-code-plugin/CHANGELOG.md` + `VERSION` +
`docs/TAGGING.md` row · `platforms/hermes/CHANGELOG.md` + `VERSION` ·
`plans/DECISIONS.md` · `plans/FRAMEWORK-TODO.md` (`IDGEN-NO-GENERATOR` → Closed) ·
`plans/HANDOFF.md` · `ROADMAP.md`. **No** `framework/` docs — unless D4 changes
that.

## Review log

### Pass 1 — 2026-07-26 — self-review against source

1. **The first draft said "point all 19 surfaces at the generator."** That is
   wrong for five of six layers: a generator needs `title`/`description`, and
   GD-09 has just re-affirmed that only BRD §7 defines which content supplies
   them. **Folded** — promoted to its own "tension" section and the two-class
   split table, because it is the plan's central constraint, not a footnote.
2. **`--fix` scope was left implicit.** It can only work where extraction is
   defined, so pointed at a PRD it would silently no-op — the exact
   default-instead-of-error failure that CI-0014 and this whole arc exist to
   fix. **Folded** as D2: refuse loudly with a message naming the reason.
3. **The `state: canonical` conflict was missed entirely.** Instructing five
   layers to emit `provisional` contradicts their own template default. GD-09
   declined to change it for TDD *because* it would make TDD unique; at five
   layers that argument inverts. **Folded** as D4's open question and Risk 1,
   and made step 1 — because the answer decides whether this is a spec plan.
4. **The surface count was taken from the issue title (19) without checking.**
   Re-derived by live grep: 13 plugin + 6 Hermes prompts, plus the reference
   doc. **Folded** as D6, with the enumeration and the per-class assignment.

### Pass 2 — 2026-07-26 — re-review of the Pass-1 patches

1. **Pass 1 created an unstated dependency.** The plan now leans on GD-09 for the
   TDD reconciliation, but the header still listed only D-0040/61/62.
   **Patched** — `Depends on` names D-0067/GD-09 as a hard prerequisite, and D7
   says why doing this first would have meant correcting `doc-tdd-fixer` against
   nothing.
2. **The provisional instruction was incomplete.** Saying "emit `0001`" without
   "distinct per element" invites a duplicate-ID artifact, since `HASH01`
   uniqueness applies regardless of `id_state`. **Patched** into D4 as a stated
   consequence, alongside the `PROV01` advisory it will raise.
3. **Version impact contradicted itself.** The draft claimed plugin MINOR while
   also citing ELEMENT-ID-LAYER-CONTRACT-001's "no platform bump" precedent —
   but that precedent covered a *bundle refresh*, whereas this changes real
   skill content. **Patched** — D5 states the distinction, and Risk 5 records
   that a plugin MINOR does require a `TAGGING.md` row here, legitimately.
4. **`--fix` could canonicalize deliberately-provisional docs.** `--check` skips
   them; nothing said `--fix` must. **Patched** into D1.

### Pass 3 — 2026-07-26 — re-review of the Pass-2 patches

No new substantive gaps. Two additions: the verification table gained the pinned
corpus baseline with an explicit note that `--fix` is **not** run over the corpus
in this plan (Pass 2 left that to inference, and an implementer could reasonably
have run it), and Risk 3 now states what the regression lock **cannot** do — it
locks the absence of in-prompt SHA-256, not the correctness of what replaced it —
mirroring the scope honesty GD-09's own lock adopted. Converged.
