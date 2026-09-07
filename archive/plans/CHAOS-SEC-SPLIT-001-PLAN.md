# CHAOS-SEC-SPLIT-001 — Split `adversary` lens into `chaos_engineer` + `security_engineer`

| Field      | Value                                       |
|------------|---------------------------------------------|
| Task       | CHAOS-SEC-SPLIT-001                         |
| Depends on | BRD-RT-001 → 004 (D-0024-0028, all merged); PRD-RT-001 (D-0029, planned) is independent and may land in either order |
| Status     | PLANNED — 2026-06-05T08:00:00Z              |
| Feeds      | EARS-RT, BDD-RT, ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT — every per-layer team-mode follow-up consumes the new crew composition |
| Scope flag | **Framework-spec change** — CHG-gated; framework spec bumps 0.11.3 → 0.12.0; plugin spec compat: 0.4.6 → 0.5.0 (breaking) |

## Objective

Partition the current `adversary` lens (which describes itself as "devil's-
advocate / chaos lens" and conflates internal stability concerns with
external attack concerns) into two narrowly-scoped review lenses:

- **`chaos_engineer`** — *internal stability* lens. Owns failure paths,
  edge cases, race conditions, resource exhaustion, recovery, missing
  error branches. Asks: "what breaks this system by accident?"
- **`security_engineer`** — *external threat* lens. Owns threat modeling,
  trust boundaries, abuse cases, missing authn/authz/integrity controls,
  attack surface. Asks: "what does a hostile actor exploit on purpose?"

The split aligns naming with intent per the chaos-engineering literature
(internal advocate / GameDays) vs adversary-engineering literature
(external attacker / stealth exploit). The agent file `adversary.md`
already self-describes as "chaos lens" — the partition makes that
honest. The existing `security-engineer.md` agent file is promoted from
a transitive auditor sub-role to a first-class crew lens.

## Background

### Current state (before this plan)

- `framework/governance/REVIEW_CREWS.yaml`: 7 layers (BRD..TDD) list
  `adversary` as a 15-20% review lens. IPLAN has **no** adversary at
  all (gap).
- `platforms/claude-code-plugin/agents/adversary.md`: self-described
  "devil's-advocate / chaos lens" — its own brief covers (1) failure
  paths, (2) edge cases, (3) unstated assumptions, (4) abuse/misuse,
  (5) diagram failure paths. Sections 1-3+5a are chaos; section 4+5b
  are security. Even the file defers "deep security to the
  auditor/security lens."
- `platforms/claude-code-plugin/agents/security-engineer.md`: exists,
  is `read-only` review-capable, but **is not a crew lens** in any
  layer. The `review-team/SKILL.md` lens-to-agent table dispatches it
  only as a sub-tool of `auditor` (line 60: "`traceability-auditor`
  (+ `security-engineer` for security/compliance)").
- No `chaos_engineer` agent exists; no `chaos` lens exists.

### Why the partition matters

The single `adversary` lens produces findings without distinguishing
**intent** (accidental vs malicious). The synthesizer reduces by score
but the verdict.json doesn't tell a downstream consumer whether the
remaining blocking finding is a "this might break under load" or "this
exposes us to attackers." The fixer applies the same patch shape to
both, but the validation step is different (chaos validates with stress
scenarios; security validates with threat models). Splitting the lens
gives:

1. **Traceable findings** — `findings[].lens` becomes `chaos_engineer`
   or `security_engineer`; verdict.json's `lens_scores` exposes which
   axis is failing.
2. **Targeted fixer dispatch** — multi-lens dispatch rules from
   BRD-RT-003 already partition validation per lens; this PR creates
   two distinct validation paths instead of one ambiguous one.
3. **Better persona prompts** — each lens gets a focused brief instead
   of the current 5-bucket grab-bag that explicitly defers half its
   own scope back to "the auditor/security lens."

## Scope

**In**:

- `framework/governance/REVIEW_CREWS.yaml` — personas registry +
  all 8 crews' weights (the redistribution table below).
- `framework/governance/REVIEW_TEAM.md` — prose mentions of adversary
  updated to reference both lenses.
- `framework/VERSION` — 0.11.3 → 0.12.0.
- `platforms/claude-code-plugin/agents/adversary.md` →
  **rename** to `agents/chaos-engineer.md`; rewrite brief to be
  chaos-only (drop abuse/misuse + trust-boundary content).
- `platforms/claude-code-plugin/agents/security-engineer.md` —
  add `## Review-Team Lens Role` section (mirroring
  `requirements-analyst.md`'s pattern from BRD-RT-001), declaring
  the binding to the new `security_engineer` lens; tighten the
  existing description to cover the partition's external-attacker
  scope (it already does, mostly).
- `platforms/claude-code-plugin/skills/review-team/SKILL.md` —
  update the lens→agent mapping table: `chaos_engineer →
  chaos-engineer`, `security_engineer → security-engineer`, remove
  the parenthetical "(+ security-engineer for security/compliance)"
  from the auditor row.
- `platforms/claude-code-plugin/agents/synthesizer.md` — update the
  hardcoded `"adversary": 62` example in the `lens_scores` block
  (line ~95) to reference the new lens names. The agent's reduce
  logic is lens-agnostic, but the *documentation example* an LLM
  reads must show the new keys.
- `tests/conformance/fixtures/review/plugin_BRD-01_report.json` +
  `tests/conformance/fixtures/review/hermes_BRD-01_report.json` —
  fixture data hardcodes `"ran": ["adversary", "architect", ...]`.
  Update to the new lens names per the BRD crew composition.
- `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` — bump to
  0.12.0.
- `platforms/claude-code-plugin/VERSION` — 0.4.6 → 0.5.0
  (breaking-naming change).
- `platforms/claude-code-plugin/.claude-plugin/plugin.json` +
  `.claude-plugin/marketplace.json` — 0.5.0.
- Plugin CHANGELOG entry under `[Unreleased]` documenting the
  breaking lens rename + new crew composition.
- `plans/DECISIONS.md` — D-0030 capturing the intent partition
  rationale and the weight-allocation method.
- `tests/conformance/` — add one assertion that the personas
  registry contains both new lenses and does **not** contain
  `adversary`; assert crew weights still sum to 100 per layer
  (existing test probably already does — verify and tighten if
  needed).

**Out** (deferred / cross-layer / not applicable):

- BRD/PRD/EARS/.../IPLAN SKILL.md text that references `adversary`
  by name in pseudo-prompts — only `doc-brd-*` skills currently have
  team-mode pseudo-text (BRD-RT-001 through 004). They mention the
  BRD crew as a whole and dispatch from REVIEW_CREWS.yaml at run
  time; if any explicit `adversary.json` slot reference exists, it
  must update. Mechanical find-and-replace, verified in Step 7.
- PRD-RT-001 (the parallel plan still on todo) **continues unchanged**.
  When PRD-RT-001 lands after this PR, its skill text references the
  PRD crew via REVIEW_CREWS.yaml — the new composition is picked up
  automatically. If PRD-RT-001 lands first, this PR rebases on top
  and updates its skill text in Step 7.
- Per-layer team-mode wirings for EARS..IPLAN — separate
  `<layer>-RT-001` plans, each unblocked by this PR landing.
- Live verification with new crew composition — covered by Step 8
  of this plan (one cheap BRD-only live run as proof).
- Hermes platform's parallel implementation in
  `platforms/hermes/src/`. Hermes' runtime persona names are
  already `chaos_engineer` and `chairperson` per
  `review_scoring.py:35` (it carries a translation layer mapping
  back to the framework's `adversary`/`synthesizer`). This PR's
  spec change aligns Hermes' internal name with the framework's
  public name — Hermes' migration is removing the translation
  layer + adding the new `security_engineer` lens. Tracked in R2.

## Approach

### Crew composition (the redistribution)

Allocation principle: `adversary`'s current weight (15-20% per layer)
splits between `chaos_engineer` and `security_engineer`, **biased by
where each concern actually lands** at that layer. Auditor weights stay
untouched (the lost "+security" sub-role is a thin parenthetical, not
worth rebalancing). IPLAN currently has no adversary — both new lenses
introduced by trimming `operator` / `integration_lead`.

| Layer | Current (4-5 lenses) | Proposed (5-6 lenses) | Rationale |
|---|---|---|---|
| BRD | `architect:30 / business_analyst:30 / auditor:20 / adversary:20` | `architect:30 / business_analyst:30 / auditor:20 / chaos:12 / security:8` | Reliability NFRs > threat-modeling at business-requirements level |
| PRD | `product_owner:30 / architect:25 / tech_lead:20 / adversary:15 / auditor:10` | `product_owner:30 / architect:25 / tech_lead:20 / chaos:8 / security:7 / auditor:10` | Roughly even — PRD has both reliability and security NFRs |
| EARS | `requirements_specialist:35 / tech_lead:25 / qa_lead:20 / adversary:20` | `requirements_specialist:35 / tech_lead:25 / qa_lead:20 / chaos:12 / security:8` | Failure-mode acceptance criteria more common than abuse-case ACs |
| BDD | `qa_lead:35 / tech_lead:25 / adversary:20 / operator:10 / auditor:10` | `qa_lead:35 / tech_lead:25 / chaos:14 / security:6 / operator:10 / auditor:10` | Failure scenarios dominate; abuse scenarios secondary |
| ADR | `architect:35 / tech_lead:25 / adversary:20 / operator:10 / auditor:10` | `architect:35 / tech_lead:25 / chaos:8 / security:12 / operator:10 / auditor:10` | **Security-heavy** — ADRs set trust boundaries, authz, crypto choices |
| SPEC | `architect:30 / tech_lead:30 / integration_lead:20 / adversary:20` | `architect:30 / tech_lead:30 / integration_lead:20 / chaos:10 / security:10` | Equal — SPEC specifies both perf and controls |
| TDD | `qa_lead:35 / tech_lead:25 / adversary:20 / operator:10 / auditor:10` | `qa_lead:35 / tech_lead:25 / chaos:10 / security:10 / operator:10 / auditor:10` | Equal — `security_engineer` co-owns SECTEST per its agent file |
| IPLAN | `tech_lead:30 / architect:25 / operator:20 / integration_lead:15 / auditor:10` (no adversary) | `tech_lead:30 / architect:25 / operator:15 / integration_lead:12 / auditor:10 / chaos:8` | **Chaos only** — IPLAN is deploy procedure; security lives upstream in ADR/SPEC; chaos covers rollback/recovery |

All sums verified = 100 per layer.

### Rationale propagation (who carries the *why* into the artifacts)

The numbers in the table above are useless without the *why* — a
dispatched lens agent needs to know "this is BRD; you carry chaos weight 12;
reliability NFRs > threat-modeling at this layer" so its review output
calibrates to the layer's concerns. The rationale must surface in **five
places** that consumers read at different times:

1. **`REVIEW_CREWS.yaml` crew blocks (governance)** — add a `# rationale:`
   comment line per crew explaining the chaos-vs-security bias for that
   layer. Authoritative; everything else cites this:

   ```yaml
   BRD:
     author: business_analyst
     # rationale: Reliability NFRs > threat-modeling at business-requirements
     # level; chaos-heavy (12) over security (8). Auditor untouched.
     review: {architect: 30, business_analyst: 30, auditor: 20,
              chaos_engineer: 12, security_engineer: 8}
   # ... same pattern for PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN
   ```

2. **`REVIEW_TEAM.md` (engine-agnostic spec)** — add a new
   `## Weight allocation rules` subsection right after the existing
   crew description, codifying the allocation method as a stable
   protocol (not just this PR's per-layer choices):

   ```
   ## Weight allocation rules

   For each layer's review crew, the chaos_engineer + security_engineer
   weights are biased by where each concern naturally lands:

   - **Chaos-heavy** (chaos > security): layers where the dominant risk
     is accidental failure under normal operation — reliability NFRs,
     failure-mode acceptance criteria, deploy/rollback procedures.
     Examples: BRD, EARS, BDD, IPLAN.
   - **Security-heavy** (security > chaos): layers where the dominant
     risk is exploitable design — architectural trust boundaries, authn/
     authz choices, crypto. Examples: ADR.
   - **Equal split**: layers where both axes matter equally — cross-
     functional specs, test cases. Examples: PRD, SPEC, TDD.
   - **Chaos-only**: layers where the security concern lives strictly
     upstream — procedural deploy steps whose threat surface was
     decided in ADR/SPEC. Examples: IPLAN.

   The author lens weight is preserved; the auditor lens weight stays
   untouched (its prior "+security" sub-role moves out to the dedicated
   security_engineer lens). Total weights must sum to 100 per crew.
   Rebalancing happens through a follow-up CHG, not silently.
   ```

3. **Agent briefs — `chaos-engineer.md` + `security-engineer.md`** —
   each agent's `## Review-Team Lens Role` section embeds the full
   per-layer weight + rationale table for THAT lens. So when dispatched
   the agent reads its own brief and knows what weight it carries at
   the current layer:

   ```markdown
   ## Review-Team Lens Role

   This agent serves the `chaos_engineer` lens. Per-layer weights and
   rationale (from REVIEW_CREWS.yaml):

   | Layer | Weight | Rationale (why chaos at this weight) |
   |---|---:|---|
   | BRD   | 12 | Reliability NFRs > threat-modeling at business-requirements level |
   | PRD   | 8  | Roughly even with security — both reliability and security NFRs |
   | EARS  | 12 | Failure-mode acceptance criteria more common than abuse-case ACs |
   | BDD   | 14 | Failure scenarios dominate Gherkin coverage |
   | ADR   | 8  | Security-heavy layer; chaos secondary to trust-boundary decisions |
   | SPEC  | 10 | Equal split — SPEC specifies both perf and controls |
   | TDD   | 10 | Equal split — failure-test cases balance security tests |
   | IPLAN | 8  | Sole non-author non-procedural lens; covers rollback/recovery |

   When dispatched, the brief includes the current layer + your weight +
   slot path. Use weight to calibrate finding-priority floor: a P1 at
   weight 14 is high-priority for the synthesizer's reduce; a P2 at
   weight 8 may not survive the threshold.
   ```

   Same shape for `security-engineer.md`'s table (BRD:8 / PRD:7 / EARS:8
   / BDD:6 / ADR:12 / SPEC:10 / TDD:10 — no IPLAN row, with footnote
   "IPLAN has no security lens; threat-model lives upstream in ADR/SPEC").

4. **Skill text — `doc-<layer>-audit/SKILL.md` Review Mode pseudo-text**
   — the per-skill enumeration of "Read the crew from REVIEW_CREWS.yaml
   — {…}" must show the layer's new lens distribution AND cite the
   one-line rationale. Example for `doc-brd-audit/SKILL.md`:

   ```
   1. Read the BRD crew from REVIEW_CREWS.yaml —
      {architect:30, business_analyst:30, auditor:20,
       chaos_engineer:12, security_engineer:8}.
      Rationale: chaos-heavy at BRD because reliability NFRs outweigh
      threat-modeling at this layer; see REVIEW_TEAM.md §Weight
      allocation rules.
   ```

   Currently only `doc-brd-*` skills carry team-mode pseudo-text (BRD-RT-001
   → 004). Each PRD-RT, EARS-RT, etc. follow-up plan inherits the same
   "cite the rationale in pseudo-text" requirement.

5. **Plugin CHANGELOG entry (Step 8)** — the BREAKING entry includes a
   one-line per-layer summary of the weight bias so consumers diffing
   their `.aidoc/review/` outputs understand why a finding now lands
   at chaos vs security weight.

The single source of truth is **REVIEW_CREWS.yaml** (Place 1) — the
other four read or cite it. If the numbers diverge between places, the
conformance test (Step 10) fails because it parses REVIEW_CREWS.yaml
and asserts the agent briefs' tables match.

### Personas registry change (`REVIEW_CREWS.yaml` lines 24-39)

```diff
 personas:
   - requirements_specialist
   - tech_lead
   - qa_lead
-  - adversary                      # devil's-advocate / failure modes / edge cases
+  - chaos_engineer                 # internal stability — failure paths, edge cases, resource exhaustion, recovery
+  - security_engineer              # external threats — threat model, trust boundaries, abuse cases, controls
   - integration_lead
   - architect
   - product_owner
   - business_analyst
   - operator
   - auditor
   - drafter
   - fixer
   - synthesizer
```

### Lens-to-agent mapping (`review-team/SKILL.md`)

```diff
 | `requirements_specialist`, `business_analyst`, `product_owner` | `requirements-analyst` |
 | `architect`, `tech_lead`, `integration_lead` | `solutions-architect` |
 | `qa_lead` | `test-architect` |
 | `operator` | `release-engineer` |
-| `auditor` | `traceability-auditor` (+ `security-engineer` for security/compliance) |
-| `adversary` | `adversary` |
+| `auditor` | `traceability-auditor` |
+| `chaos_engineer` | `chaos-engineer` |
+| `security_engineer` | `security-engineer` |
 | `synthesizer` | `synthesizer` |
```

### Agent file changes

**Rename + rewrite**: `agents/adversary.md` → `agents/chaos-engineer.md`.

- Frontmatter `name: adversary` → `name: chaos-engineer`.
- Title "Adversary Agent" → "Chaos Engineer Agent".
- Description: drop "adversary" framing; describe as "internal
  stability lens — failure modes, edge cases, race conditions,
  resource exhaustion, recovery". Cite the partition: "for external
  attack surface, see `security-engineer.md`."
- Brief sections:
  - Keep sections 1 (failure & error paths), 2 (edge & boundary
    cases), 3 (unstated assumptions), 5a (diagram error branches).
  - **Remove** section 4 (abuse / misuse) — moves to
    `security-engineer.md`.
  - **Remove** the trust-boundary half of section 5 (5b) — moves to
    `security-engineer.md`.
  - Add explicit "overlap note": "rate-limits, TOCTOU races, and
    DoS-by-malicious-input live in both lenses' scope; report them
    here when triggered by accidental conditions; expect parallel
    findings from `security_engineer` for the malicious-actor view;
    the synthesizer dedupes by location."
- Output slot path: `.aidoc/review/<artifact-id>/chaos_engineer.json`
  (was `adversary.json`).
- Color: `orange` → `cyan` (visual differentiation from
  security-engineer's `red`).

**Augment**: `agents/security-engineer.md`.

- Keep existing scope (threat modeling, vulnerability assessment,
  secure-design review, SECTEST authoring).
- Add `## Review-Team Lens Role` section (mirroring the BRD-RT-001
  pattern in `requirements-analyst.md`): "In the framework
  review-team model, this agent serves the `security_engineer` lens
  in BRD/PRD/EARS/BDD/ADR/SPEC/TDD crews per the mapping table in
  `../skills/review-team/SKILL.md`. When dispatched as a `Task`
  subagent by `review-team`, the brief carries the lens name +
  weight + slot path; produce the framework persona-output record
  (persona, findings[], lens_score) and return it. The structural
  test-authoring scope (SECTEST co-ownership with Test Architect)
  remains its own non-review-lens responsibility."
- Brief expansion: explicit ownership of (1) threat modeling, (2)
  trust boundaries, (3) abuse/misuse cases, (4) missing
  authn/authz/integrity controls, (5) attack surface, (6) crypto
  choices, (7) data-flow trust crossings.
- Add the same overlap note as chaos-engineer (rate-limits/TOCTOU/
  resource-DoS overlap acknowledged; synthesizer dedupes).
- Output slot path: `.aidoc/review/<artifact-id>/security_engineer.json`.

### Slot naming convention

Slots use the **lens name** (snake_case) as filename — `chaos_engineer.json`
and `security_engineer.json`. This matches the existing pattern
(`business_analyst.json`, `product_owner.json`). Verdict.json's
`lens_scores` field uses the same keys.

## Step sequence

1. **Framework spec edits** (CHG-gated):
   - `framework/governance/REVIEW_CREWS.yaml`:
     - Replace `adversary` line in `personas:` with two new lines.
     - Rewrite all 8 crew `review:` blocks per the table above.
     - **Add `# rationale:` comment line per crew** (Place 1 of the
       rationale propagation — see Approach §Rationale propagation).
       This is the authoritative source; all downstream artifacts
       cite it.
   - `framework/governance/REVIEW_TEAM.md`:
     - Replace prose mentions of "adversary" with "chaos_engineer +
       security_engineer" where contextually appropriate.
     - **Add new `## Weight allocation rules` subsection** (Place 2)
       with the four-category protocol (chaos-heavy / security-heavy
       / equal / chaos-only). Defines the *rules* — not this PR's
       specific allocations.
   - `framework/governance/REVIEW_REMEDIATION_FLOW.md`: replace
     adversary references with the appropriate new lens per intent
     (per G12 from Pass 3).
   - `framework/VERSION`: 0.11.3 → 0.12.0.

2. **Plugin agent rename + rewrite** — use **two commits** to
   preserve git rename detection (G27):
   - **Commit A**: pure rename (no content change):
     `git mv platforms/claude-code-plugin/agents/adversary.md
        platforms/claude-code-plugin/agents/chaos-engineer.md`
   - **Commit B**: content rewrite per "Agent file changes" above
     (remove section 4 abuse/misuse, remove section 5b trust
     boundaries, retitle, recolour, add overlap note, update slot
     path, add per-layer weight + rationale table).
   - Add the **per-layer weight + rationale table** to the
     `## Review-Team Lens Role` section (Place 3 of rationale
     propagation; G21 decision: per-layer table is the right
     shape here because this agent serves *one* lens across *many*
     layers — different from `requirements-analyst.md` which serves
     *multiple* lenses, *one* per layer, hence bullet-per-lens
     there). 8 rows: BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN. Each row
     carries weight + one-line "why chaos at this weight" rationale.
     Cite REVIEW_CREWS.yaml as source of truth.

3. **Plugin agent augment**:
   - Edit `platforms/claude-code-plugin/agents/security-engineer.md`
     per "Agent file changes" above.
   - **Add per-layer weight + rationale table** to the
     `## Review-Team Lens Role` section (Place 3 of rationale
     propagation). 7 rows: BRD/PRD/EARS/BDD/ADR/SPEC/TDD (no IPLAN
     row; footnote: "IPLAN has no security_engineer lens — threat
     model lives upstream in ADR/SPEC"). Cite REVIEW_CREWS.yaml as
     source of truth.

3b. **Synthesizer agent example output** (G15):

- Edit `platforms/claude-code-plugin/agents/synthesizer.md`
     around line 95 (the example `lens_scores` block). Replace
     the hardcoded `"adversary": 62` with the new lens names
     consistent with a BRD-crew example (e.g.,
     `"chaos_engineer": 62, "security_engineer": 71`). Update the
     adjacent `coverage.expected` if the example was 4 lenses (BRD
     now has 5).

3c. **Conformance fixtures** (G16):

- Edit `tests/conformance/fixtures/review/plugin_BRD-01_report.json`
     — replace `"ran": ["adversary", ...]` with the new BRD crew
     lens names (`["chaos_engineer", "security_engineer",
     "architect", "auditor", "business_analyst"]`).
- Same for `tests/conformance/fixtures/review/hermes_BRD-01_report.json`.
- Verify all schema fields referenced in
     `review_report.schema.json` still pass.

4. **Plugin mapping table**:
   - Edit `platforms/claude-code-plugin/skills/review-team/SKILL.md`
     lens→agent mapping per the diff above. Remove the parenthetical
     `(+ security-engineer for security/compliance)`.

5. **Plugin spec-version compat**:
   - `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION`: 0.11.3 → 0.12.0.

6. **Plugin version bump** 0.4.6 → 0.5.0:
   - Standard 9-place fanout: `VERSION`, `.claude-plugin/plugin.json`
     (×2: plugin's own + marketplace), root `README.md`, plugin
     `README.md`, `docs/PARITY.md`, `docs/TAGGING.md`, SKILL_AUTHORING
     references (×3 if present).
   - Per-skill `version:` frontmatter — 52 skills × `0.4.6` → `0.5.0`.
     Use the atomic sed pattern (G25) instead of 52 hand edits:

     ```sh
     grep -rl '^version: 0.4.6' platforms/claude-code-plugin/skills/ \
       | xargs sed -i 's/^version: 0.4.6/version: 0.5.0/'
     ```

     Then verify count: `grep -r '^version: 0.5.0' platforms/claude-code-plugin/skills/ | wc -l` should equal the count of `^version:` lines pre-edit.

7. **Skill pseudo-text sweep** — two passes:

   **7a. Mechanical rename + array-entry split** (per G13/G14/G23
   from Pass 3+5; cover all relevant file types, not just markdown):

   ```sh
   grep -rn 'adversary' \
        platforms/claude-code-plugin/skills/ \
        platforms/claude-code-plugin/agents/ \
        platforms/claude-code-plugin/*.json \
        platforms/claude-code-plugin/.claude-plugin/*.json \
        tests/scripts/ \
        tests/conformance/fixtures/ \
        framework/governance/
   ```

   For each match — most are single-lens references; **two require
   special handling**:

   - **Single-lens references** (default): if it's a lens reference,
     update to `chaos_engineer` or `security_engineer` per context
     (failure-mode talk → chaos; abuse/threat talk → security). If
     it references the old slot filename `adversary.json`, update
     to the new slot.

   - **`tests/scripts/test-acceptance.sh:1448` is an ARRAY-ENTRY
     SPLIT, not a rename** (G17). The line currently reads:

     ```
     "adversary|.|produce adversarial findings via the review-team crew|50"
     ```

     This is one entry in the cascade-dispatch array (agent | path |
     description | token-budget). After this PR it becomes **two**
     entries:

     ```
     "chaos-engineer|.|produce internal-stability findings (failure paths, edge cases, race conditions) via the review-team crew|50"
     "security-engineer|.|produce external-threat findings (abuse cases, trust boundaries, controls) via the review-team crew|50"
     ```

     Total token-budget allotted to chaos+security in the array
     doubles (50→100). This is intentional — two distinct
     dispatches, each with the previous adversary budget.

   - **`tests/scripts/test-acceptance.sh:1892`** has `adversary` in
     the agent-type whitelist; replace with `chaos-engineer` and add
     `security-engineer` to the same whitelist set.

   **7b. Rationale citation** (Place 4 of rationale propagation):
   for each `doc-<layer>-audit/SKILL.md` that has a `## Review Mode`
   section enumerating the crew, append a one-line rationale citation
   pointing at REVIEW_TEAM.md §Weight allocation rules. Currently
   only `doc-brd-audit/SKILL.md` has this section (BRD-RT-001 → 004);
   PRD-RT-001 and later per-layer follow-ups inherit the same
   requirement. Example diff for BRD:

   ```diff
    1. Read the BRD crew from REVIEW_CREWS.yaml —
       {architect:30, business_analyst:30, auditor:20,
   -    adversary:20}.
   +    chaos_engineer:12, security_engineer:8}.
   +   Rationale: chaos-heavy at BRD because reliability NFRs
   +   outweigh threat-modeling at this layer; see
   +   REVIEW_TEAM.md §Weight allocation rules.
   ```

8. **Plugin CHANGELOG** (Place 5 of rationale propagation):
   `[Unreleased] → Changed` (BREAKING) entry documenting:
   - Lens partition rationale (intent: accidental vs malicious).
   - **Per-layer weight bias one-liner per layer** (e.g., "BRD:
     chaos-heavy 12:8 — reliability NFRs > threat-modeling"). 8
     bullet points, one per layer. Lets consumers diffing their
     `.aidoc/review/` outputs understand why findings now route to
     chaos vs security weight.
   - Agent file rename (`adversary.md` → `chaos-engineer.md`).
   - Slot filename change (`adversary.json` → `chaos_engineer.json`
     - new `security_engineer.json`).
   - Migration step: `rm -rf .aidoc/review/` on first 0.5.0 run
     (no shim).

9. **`plans/DECISIONS.md` D-0030** — "Lens partition: intent-based
   (accidental vs malicious) outweighs single-lens simplicity at
   verdict-traceability time. Weight allocation favors security in
   ADR/SPEC, chaos in BDD/IPLAN; equal split where both matter (PRD/
   SPEC/TDD); chaos-only in IPLAN (security lives upstream)."

10. **Conformance test additions** — touch two files (G22):

    - **`tests/conformance/test_review_team.py`** (existing 4 tests:
      `test_personas_unique_and_nonempty`,
      `test_default_mode_valid`,
      `test_crews_cover_exactly_the_eight_layers`,
      `test_each_crew_is_well_formed`):
      - The first test catches `adversary` removal from the
        personas registry automatically once the rename lands.
      - Verify `test_each_crew_is_well_formed` already asserts
        weights sum to 100 (almost certainly does; tighten if not).
      - Add new `test_chaos_security_lens_presence` — every crew
        except IPLAN has both `chaos_engineer` AND `security_engineer`;
        IPLAN has `chaos_engineer` only. Catches G8's asymmetric
        choice from regressing silently.
      - Add new `test_lens_to_agent_mapping_has_both_new_rows` —
        parses `review-team/SKILL.md` mapping table; asserts
        `chaos_engineer` and `security_engineer` rows present and
        adversary row absent.

    - **`tests/conformance/test_governance.py`** (companion file):
      - Verify it has no hardcoded `adversary` reference; if any,
        update to the new lens names per Step 7a's grep coverage.
      - Verify plugin version uniformity assertion exists (catches
        R3's missed-version-fanout risk). If absent, add it.

    - **Cross-place rationale consistency check** (new test in
      `test_review_team.py`) — the load-bearing one. Parse
      `REVIEW_CREWS.yaml` for each crew's chaos + security weights;
      parse the per-layer weight tables in `chaos-engineer.md` and
      `security-engineer.md`; assert the numbers match exactly.
      Catches the failure mode where REVIEW_CREWS.yaml is updated
      but the agent briefs' tables drift (the
      single-source-of-truth invariant from Approach §Rationale
      propagation).

11. **Verify + land** (see Verification ladder below).

## Verification

Cheap-to-expensive. Steps 1-5 are free. Step 6 spends ~$3 (BRD-only
live run, smaller because BRD's new crew is 5 lenses vs. PRD's 6).

1. **Static lint** (free, <30s):

   ```sh
   env -u LD_LIBRARY_PATH pre-commit run --files \
     framework/governance/REVIEW_CREWS.yaml \
     framework/governance/REVIEW_TEAM.md \
     framework/VERSION \
     platforms/claude-code-plugin/agents/chaos-engineer.md \
     platforms/claude-code-plugin/agents/security-engineer.md \
     platforms/claude-code-plugin/skills/review-team/SKILL.md \
     platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION \
     platforms/claude-code-plugin/VERSION \
     platforms/claude-code-plugin/CHANGELOG.md \
     plans/DECISIONS.md
   ```

   Pass: green.

2. **Full conformance suite** (free, <1 min):

   ```sh
   python3 -m unittest discover -s tests/conformance -v
   ```

   Pass: 96/96 pre-existing + new assertions (Step 10) pass. The
   weights-sum-to-100 check is the load-bearing one — if any crew
   miscounted, this catches it cold.

3. **Greppable invariants** (free, <5s):

   ```sh
   ! grep -rn '\<adversary\>' framework/ platforms/claude-code-plugin/ \
        --include='*.yaml' --include='*.md' \
        | grep -v 'plans/' | grep -v 'CHANGELOG' | grep -v 'DECISIONS'
   ```

   Pass: zero matches outside changelog/decisions/plans context (`! ...`
   negates).

4. **Mock-mode acceptance** (free, <1 min):

   ```sh
   bash tests/scripts/test-acceptance.sh url-shortener --no-live
   ```

   Pass: outcome PASS, no regression.

5. **Verdict-schema inspection** (free): grep `agents/synthesizer.md`
   for any hardcoded `adversary` reference. Pass: zero matches (the
   synthesizer's `lens_scores: {<name>: <int>}` is lens-agnostic by
   design).

6. **Live BRD cascade** (~$3, ~30 min):

   ```sh
   bash tests/scripts/test-acceptance.sh url-shortener --live \
        --phase=cascade --from-layer=brd --to-layer=brd --force
   ```

   Pass criteria (mirroring BRD-RT-004's 6/6):
   - `verdict.json` at `.aidoc/review/01_BRD/<BRD-id>/verdict.json`
     present, with `coverage.expected: 5` (BRD's new crew is 5
     lenses: architect / business_analyst / auditor / chaos_engineer
     / security_engineer).
   - **5 slot files** including `chaos_engineer.json` AND
     `security_engineer.json`. Both contain non-trivial findings
     specific to their lens (chaos: failure modes / edge cases;
     security: abuse cases / trust boundaries / controls).
   - `verdict.json:lens_scores` map contains both new lens keys, no
     `adversary` key.
   - Driver-vs-synthesizer score agreement (BRD-RT-002 invariant).
   - Autopilot iterates on FAIL.
   - No per-layer-cap timeout (3600s cap should be untouched —
     adding one lens adds ~10% wall-clock, well within budget).

7. **Full cascade verification** (~$20-30, deferred to a follow-up
   PR after Step 6 passes). Mock-mode reaches all 8 layers; live
   verification of all 8 layers' new crew compositions costs more
   than this PR justifies on its own.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Lens-scope overlap (rate-limits, TOCTOU, resource-DoS) produces duplicate findings from chaos + security on the same line | Synthesizer already dedupes by `(file, line, finding-id)`. Both agent briefs explicitly tell the lens NOT to suppress findings to avoid duplication — let the reduce step handle it. Verified in Step 6 by inspecting `verdict.json:findings[].personas` array (if a dedup folded both lenses' findings, `personas` will contain both names) |
| R2 | Hermes platform's spec-0.12.0 conformance lags | **Easier migration than first thought (G18).** Hermes already uses `chaos_engineer` as its runtime persona name (`platforms/hermes/src/mcp_server/review/review_scoring.py:35` maps `"chaos_engineer": "adversary"`). This PR removes the need for that translation layer — Hermes' runtime name becomes the framework's public name. The remaining Hermes work is: (a) drop the `chaos_engineer→adversary` translation in `review_scoring.py`, (b) add `security_engineer` as a new runtime persona + crew lens. Tracked as a separate PR in `platforms/hermes/` after this lands. CHANGELOG notes Hermes-side update required before tagging `framework/v0.12.0` on a shared release |
| R3 | Per-skill `version:` frontmatter fanout missed (52 skills × 1 bump) | Step 6 includes an explicit `sed` one-liner to bump all matching frontmatters atomically (`grep -rl 'version: 0.4.6' .../skills/ \| xargs sed -i ...`). Conformance test in Step 10 asserts all skills declare the same plugin version (existing test_governance.py likely already enforces version uniformity — verify and tighten if missing) |
| R4 | Existing url-shortener BRD audit history references `adversary` slot → old runs unreadable | Acceptance: this is fresh-start data. The example's prior `logs/` are gitignored; the canonical `.aidoc/review/01_BRD/<BRD-id>/` is regenerated on every run. The acceptance criterion is "fresh live run produces correct new-format outputs" — no historical migration concern |
| R5 | Renaming `adversary.md` → `chaos-engineer.md` breaks git blame continuity | `git mv` preserves rename detection at git's default 50% similarity threshold, but the agent's content rewrite (remove sections 4+5b, add overlap note + per-layer table) may drop similarity below 50%, making git classify the change as delete+add. Step 2 uses **two commits** (commit A: pure rename; commit B: content rewrite) so rename detection always succeeds (G27). The agent's prior history surfaces via `git log --follow chaos-engineer.md` |
| R6 | Plugin version bump 0.4.6 → 0.5.0 (breaking) signals to consumers a bigger change than just lens rename | The breaking-naming change is real: blackboard slot filenames change (`adversary.json` → `chaos_engineer.json`), verdict.json `lens_scores` keys change. Any consumer parsing those files will break. 0.5.0 SemVer-major is correct. CHANGELOG documents the migration path (regenerate `.aidoc/review/` directories on first run) |
| R7 | BDD/TDD security weight of 6/10 (respectively) is too low to surface meaningful findings, leading to "PASS by absence" | If Step 6 (BRD-only) shows the chaos:security ratio works for BRD (12:8), extrapolation to other layers is mechanical. If, in EARS/BDD verification later, security findings consistently land below the threshold needed to be P1, rebalance via a follow-up `CHAOS-SEC-WEIGHT-002` plan. Not a blocker for this PR |
| R8 | Existing BRD-RT-001..004 skill text references `adversary` by name → out-of-sync after this PR lands | Step 7 (grep sweep) catches and updates all references. Failure mode: if a reference is in markdown that the grep misses (e.g., escaped), the live run in Step 6 surfaces it (the dispatched skill produces wrong slot path or fails to find the lens in REVIEW_CREWS.yaml) |
| R9 | IPLAN layer gets only chaos lens — if a real security concern lives in deploy procedure (e.g., secret-leak in IPLAN steps), no security review catches it | IPLAN's upstream (ADR/SPEC) already has security_engineer at 12% / 10% — the threat-model surface is reviewed there. IPLAN's structural lint catches `@security: SEC-NN` traceability gaps. If real-world use shows IPLAN-level security gaps slipping through, add security:5 to IPLAN in a follow-up by trimming integration_lead 12 → 7 |

## Review log

### Pass 1 — 2026-06-05T08:00:00Z

Initial draft. Findings folded in:

- BRD-RT-001 → 004 are pre-requisites for this work to land cleanly
  (the team-mode wiring + multi-lens dispatch rules need to exist
  before splitting the lens). All merged — no blocker.
- PRD-RT-001 is **independent** of this PR. Either ordering works.
  If this PR lands first: PRD-RT-001's text rebases trivially to use
  the new lens names. If PRD-RT-001 lands first: this PR rebases on
  top and Step 7's grep sweep catches its references.
- Framework spec change → CHG-gated → spec bump to 0.12.0 → plugin
  spec-compat-version bump to match → plugin version bump 0.4.6 →
  0.5.0 (SemVer-major because slot filenames are part of the public
  contract).
- Personas registry (lines 25-39 of REVIEW_CREWS.yaml) is the entry
  point — every crew references it; one bad change cascades.
  Conformance test in Step 10 enforces the closed-set invariant.

### Pass 2 — 2026-06-05T08:00:00Z

Re-read. Findings:

- **G1 — Hermes platform impact**. Hermes consumes the framework
  spec independently. When spec → 0.12.0, Hermes' conformance fails
  until it adopts the same lens partition. This is structurally OK
  (the two platforms have independent version streams per PROJECT.md
  §2) but the project-level `v1.0.0` cutover will need both
  platforms aligned. Captured as R2.
- **G2 — Color collision**. Adversary agent was orange; security-
  engineer is red. Chaos-engineer needs its own color. Chose cyan
  (distinct from any existing agent). Codified in Step 2.
- **G3 — Existing BRD blackboard data**. The blackboard at
  `.aidoc/review/01_BRD/<BRD-id>/adversary.json` from BRD-RT-004's
  live run exists in `examples/url-shortener/.aidoc/`. After this PR
  lands, that path is wrong. Acceptable per R4 — `.aidoc/review/`
  is regenerated every run; the on-disk artifact is provenance, not
  contract. Step 6's live run overwrites with new layout.
- **G4 — Synthesizer template hardcoding**. Need to verify the
  synthesizer agent's prompt text doesn't hardcode `adversary` in
  example output. Step 5 (free grep) catches it; if found, add a
  prompt update to Step 3's scope.
- **G5 — `find` for SKILL.md `adversary.json` references in
  `doc-brd-audit/SKILL.md`**. BRD-RT-002 added pseudo-text showing
  the slot index format. Need to verify whether it lists
  `adversary.json` verbatim or refers to lenses abstractly. Step 7
  is the catch-net.
- **G6 — Plugin marketplace.json reference**. Outside this repo's
  control if it ships externally; within-repo `.claude-plugin/
  marketplace.json` lists the plugin with a version field. Standard
  fanout in Step 6.
- **G7 — `tests/conformance/` already has a weights-sum check?**.
  Probably — needs verification at Step 10 time. If yes, the new
  test only needs the personas-registry-membership check. If no, add
  both.

Folding G1-G7: added R2 (Hermes), R4 (blackboard data), refined
Step 5 (free grep includes synthesizer), refined Step 7 (catch-net
language), Step 10 (conditional on existing tests).

### Pass 3 — 2026-06-05T08:00:00Z (gap-review)

Deliberate gap-hunt of the Pass 1+2 plan.

- **G8 — IPLAN's "chaos-only" choice is asymmetric vs every other
  layer**. Every other layer gets BOTH new lenses; IPLAN gets only
  chaos. This is a deliberate choice (rationale: IPLAN is procedural
  deploy, security lives in ADR/SPEC). Defensible, but worth a
  one-line note in the CHANGELOG so consumers expecting symmetric
  treatment understand the rationale. Added to Step 8's CHANGELOG
  shape. Also captured as R9 with an explicit upgrade path.
- **G9 — Weight allocation method**. The per-layer table uses my
  judgement (BRD chaos-heavy because reliability NFRs > threat
  modeling at business-requirements; ADR security-heavy because
  architectural decisions encode trust boundaries). User has
  reviewed and acknowledged. Codify in D-0030 (Step 9) so future
  rebalances have a starting point.
- **G10 — What if a layer's overall budget is exhausted?** Adding
  two lenses to PRD/BDD/ADR/TDD/IPLAN increases per-layer cost by
  ~25%. BRD-RT-004's ORCHESTRATOR_TIMEOUT (1800s) and MAX_LAYER_SEC
  (3600s) accommodate this comfortably. No script change needed.
- **G11 — Backward-compatibility shim?** None planned (rejected).
  Per the project's "no backwards-compatibility hacks" rule, just
  break it cleanly at 0.5.0 and require fresh `.aidoc/review/`
  regeneration. CHANGELOG documents the one-step migration ("rm -rf
  .aidoc/review/ before first run on 0.5.0"). Cleaner than aliasing
  `adversary` to `chaos_engineer` indefinitely.
- **G12 — REVIEW_REMEDIATION_FLOW.md references**. Probably
  references `adversary` as a lens in the remediation flow doc.
  Add to Step 1's `REVIEW_TEAM.md`/`REVIEW_REMEDIATION_FLOW.md`
  edit scope. Update Step 1 to include this file.
- **G13 — `tests/scripts/test-acceptance.sh` slot-presence check?**
  The BRD-RT-001 plan referenced the script asserting persona slot
  presence (lines 1240-1276). Need to verify this script doesn't
  hardcode `adversary.json` in its enumeration. If it iterates the
  crew from REVIEW_CREWS.yaml at runtime, fine. If hardcoded, add to
  Step scope. Step 7's grep includes `tests/scripts/` to catch.
- **G14 — Conformance test for the *renamed* file**. The plugin's
  `agents/` directory is enumerated somewhere (probably in the
  marketplace listing or a manifest). If a manifest hardcodes
  `adversary.md`, the rename breaks it. Step 7's grep over
  `platforms/claude-code-plugin/` (extended to include `.json`)
  catches it.

Folding G8-G14:

- R9 + CHANGELOG note (G8 covered).
- D-0030 codifies the allocation method (G9 covered).
- Step 1 expanded to include `REVIEW_REMEDIATION_FLOW.md` (G12).
- Step 7's grep extended: cover `*.yaml`, `*.json`, `*.sh`, `*.py`
  files too, not just markdown.

### Pass 4 — 2026-06-05T08:30:00Z (rationale-propagation expansion)

Per user feedback ("update the plan to add the new weight
distribution and rationale to the team description if missing").

The numbers were in the plan but the *why* wasn't propagating into
the artifacts that consume them at run-time. A dispatched lens
agent reading its own brief shouldn't have to chase REVIEW_CREWS.yaml
to know "why am I weighted 12 at BRD vs 8 at ADR?" — that calibration
must live in the brief itself. Similarly, the audit skill's Review
Mode enumeration shouldn't show bare numbers without the layer-
specific reason.

Added new **§Rationale propagation** subsection to Approach defining
five places the *why* surfaces:

1. **REVIEW_CREWS.yaml** crew blocks — `# rationale:` comment per
   crew (authoritative).
2. **REVIEW_TEAM.md** — new `## Weight allocation rules`
   subsection (the 4-category protocol: chaos-heavy / security-
   heavy / equal / chaos-only) — the *rules*, not the numbers.
3. **Agent briefs** — per-layer weight + rationale tables embedded
   in each agent's `## Review-Team Lens Role` section, so dispatched
   subagents read their own calibration without external lookup.
4. **Skill pseudo-text** — `doc-<layer>-audit/SKILL.md` Review Mode
   enumerates `{chaos:N, security:M}` AND cites the layer's
   rationale, pointing at REVIEW_TEAM.md §Weight allocation rules.
5. **Plugin CHANGELOG** — per-layer bias one-liners so consumers
   diffing `.aidoc/review/` outputs understand the routing.

Expanded Steps 1, 2, 3, 7, 8, and 10 to cover these five places.
Added the cross-place rationale consistency conformance check to
Step 10 — REVIEW_CREWS.yaml is the single source of truth; the
test fails if the agent briefs' tables drift from it.

No new risks added — the rationale-propagation surface is
mechanical text inclusion, no semantic concerns.

### Pass 5 — 2026-06-05T09:00:00Z (deliberate gap-review against the codebase)

Cross-checked every plan assumption against actual file contents
(grep over `framework/`, `platforms/`, `tests/`). Found 9 gaps in
the original scope inventory — 3 blocking, 4 medium, 2 cosmetic.
**All gaps folded in place** (per user direction: no separate
plan; the gaps are scope holes in *this* plan, not standalone
bugs).

**Blocking gaps fixed:**

- **G15 — `synthesizer.md:95` has hardcoded `"adversary": 62`** in
  the example `lens_scores` block. The plan's "Out > synthesizer
  no edit needed" claim was wrong: schema is lens-agnostic but the
  documentation example isn't. Fixed: moved synthesizer.md to
  Scope > In; added Step 3b with explicit example-output edit.
- **G16 — Conformance fixtures hardcode `adversary`** in
  `tests/conformance/fixtures/review/plugin_BRD-01_report.json`
  (and likely `hermes_BRD-01_report.json`). Plan never mentioned
  these. Fixed: added Step 3c for fixture updates; expanded
  Step 7a grep to include `tests/conformance/fixtures/`.
- **G17 — `tests/scripts/test-acceptance.sh:1448` is an
  array-entry SPLIT, not a rename.** That line is one row in a
  structured `agent|path|description|tokens` cascade-dispatch
  array. After this PR it must become **two** rows (one for
  chaos-engineer, one for security-engineer). Step 7a's
  "mechanical rename" instruction would have produced wrong work.
  Fixed: Step 7a now distinguishes single-lens references from
  array-entry splits, shows the before/after for line 1448
  explicitly, and calls out line 1892's whitelist additions.

**Medium gaps fixed:**

- **G18 — R2 (Hermes) understates current alignment.** Hermes'
  runtime persona is **already** `chaos_engineer` per
  `review_scoring.py:35` (with a translation layer back to
  framework's `adversary`). This PR's spec change *removes* the
  translation. Reframed R2: easier migration than originally
  written.
- **G20 — R3 cited non-existent `scripts/check_versions.py`.** The
  script doesn't exist; the mitigation was fabricated. Fixed:
  Step 6 now includes a concrete sed one-liner for the 52-skill
  version bump; R3 mitigation references the conformance test in
  Step 10 (verifies version uniformity) rather than a phantom
  script.
- **G23 — Step 7a grep missed `tests/conformance/fixtures/`** —
  the location of G16's hardcoded fixture data. Fixed in Step 7a.
- **G25 — Per-skill version-bump fanout had no automation** —
  52-file manual edit risk. Fixed in Step 6 with the sed
  one-liner.

**Cosmetic gaps fixed:**

- **G21 — `## Review-Team Lens Role` table-vs-bullet pattern
  inconsistency** — existing `requirements-analyst.md` uses
  bullet-per-lens (one bullet per lens served); plan proposed
  per-layer table for the new agents. Different *shape* of agent
  (single-lens-many-layers vs many-lenses-one-layer-each)
  justifies the different format. Decision codified in Step 2
  with explanatory note.
- **G22 — Conformance tests live in two files** (`test_review_team.py`
  AND `test_governance.py`) — plan generically said
  `tests/conformance/`. Fixed: Step 10 now enumerates both files
  explicitly with the existing test names from `test_review_team.py`
  and the version-uniformity expectation in `test_governance.py`.
- **G27 — `git mv` + content rewrite in one commit may defeat
  rename detection** below git's default 50% similarity. Fixed:
  Step 2 now uses two commits (rename in A, rewrite in B); R5
  updated accordingly.

**Not fixed (deferred per Pass 3):**

- G10 cost extrapolation refinement — cosmetic only.
- G19, G24, G26, G28-G30 — covered by existing risks/notes;
  no plan change needed.

No new structural risks emerge from the amendments. All gap fixes
are mechanical scope-expansions of the existing plan, not
architectural changes.

Plan ready for implementation. Updated estimated effort:
3-4 hours wall-clock (added Steps 3b + 3c + expanded Step 7a +
Step 10's additional test functions), 30 min lint/conformance,
30 min live verification. Total ~$3 for the live BRD run
(unchanged).

## Cross-references

- BRD-RT-001 plan: `plans/BRD-REVIEW-TEAM-PLAN.md`
- BRD-RT-002 plan: `plans/BRD-RT-002-VERDICT-CHAIN-PLAN.md`
- PROFILE-DELTA-001: `plans/PROFILE-DELTA-OVERRIDE-PLAN.md`
- PRD-RT-001 plan: `plans/PRD-RT-001-PLAN.md` (still on todo, independent)
- Framework review-team contract: `framework/governance/REVIEW_TEAM.md`
- Crews: `framework/governance/REVIEW_CREWS.yaml`
- Lens → agent mapping: `platforms/claude-code-plugin/skills/review-team/SKILL.md`
- Adversary agent (pre-rename): `platforms/claude-code-plugin/agents/adversary.md`
- Security agent (pre-promotion): `platforms/claude-code-plugin/agents/security-engineer.md`
- Decision register: D-0024 / D-0025 / D-0026 / D-0027 / D-0028 / D-0029 in `plans/DECISIONS.md`; D-0030 added by this plan
- Project versioning policy: `docs/PROJECT.md` §2 (independent version streams)
- CHG process (post-cutover): `docs/PROJECT.md` §6
