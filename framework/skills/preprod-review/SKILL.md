---
name: preprod-review
description: >-
  Use before a release, rollout, deployment, or promotion that widens blast radius. Runs five independent read-only review lenses, verifies serious findings against source, and returns a ranked READY, SHIP-WITH-FIXES, or BLOCKER verdict.
---

# Pre-production review

> Framework adaptation — engine-agnostic copy of the canon global skill.
> Source: `aidoc-flow-claude-agents-config/skills/preprod-review/SKILL.md` (private, 2026-09-27).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Engine mapping: Claude Code `<skills-root>/<name>/`, Codex `<skills-root>/<name>/`, generic `<skills-root>/<name>/`.
> Where the canon names a Claude-specific agent type, use your engine's focused read-only subagent equivalent and keep the independence contract.


Reviewing something well before it ships is not one read — it is several
*independent* reads from angles that a single reviewer conflates and therefore
misses. A security lens and a docs lens hunting the same diff surface different
truths; fused into one pass they blur. This skill fixes the lenses, runs them in
parallel against real source, and forces every surviving finding through a
verification step so the verdict is evidence, not vibes.

Use it before anything that widens blast radius:

- cutting a release or version tag
- promoting a library, template or workflow to a team/company default
- rolling a change out to N consumer repos
- a deploy or infrastructure change that is hard to reverse
- handing an artifact to adopters who cannot see its internals

**Not for** ordinary in-flight review of a PR or a work-in-progress branch —
that is `/code-review`. This is for the ship/elevate/rollout decision, where the
cost of being wrong is paid by people who were not in the room.

## The shape

1. **Scope the surface** (you, inline — a few minutes). List every file the
   review must cover, then read the 2–3 most privileged or most load-bearing
   ones **yourself**, so you can spot-check findings later. What counts varies
   by artifact, but the shape is always *entry points, whatever they trust, and
   the surfaces adopters read*:

   | Artifact | Typically |
   |---|---|
   | CI / workflows | `.github/workflows/*.yml`, install or distribution templates, the scripts they invoke, adopter docs |
   | library / service | public API surface, config and defaults, migration steps, the release or deploy script |
   | infrastructure | the changed resources, IAM/permission boundaries, the state and rollback path |
   | **any of them** | the governance surfaces — CHANGELOG / ROADMAP / decisions log / handoff |
2. **Fan out five lenses in parallel** (one dispatch, five agents — see below).
   Each gets a *scoped* brief and returns a ranked report. Running them in one
   turn is the point: they finish together and don't inherit each other's
   framing.
3. **Synthesize + verify** (you, inline). Dedup across the five reports. For
   every BLOCKER and every HIGH, open the cited `file:line` and confirm the
   defect is real before it survives into your output. A plausible-sounding
   finding that doesn't reproduce against source is noise — cut it or mark it
   PLAUSIBLE with what would confirm it.
4. **Deliver one ranked verdict**: `BLOCKER` (do not ship), `SHIP-WITH-FIXES`
   (fixable, enumerated), or `READY`. Lead with the verdict, then the ranked
   findings, then strong positives to *not* regress.
5. **Promote surviving findings (you, inline — the orchestrator owns this).**
   Lenses must not file; their reports are raw synthesis input. Check every
   surviving BLOCKER and HIGH against the `submit-feedback` promotion bar and
   file the ones that clear it via `submit-feedback` (search-first,
   body contract, safe publication). Link the issue numbers from the verdict
   so no finding dies at the transcript boundary.

## The five lenses

Dispatch these as five parallel subagents in a single turn. Agent types are
**fixed** — never `general-purpose` (it silently inherits the session model;
match cost to the lens instead):

| # | Lens | Agent type | Why this tier |
|---|------|-----------|---------------|
| 1 | **Security** | `security-auditor` | judgment-bearing (opus) |
| 2 | **Correctness** | `code-reviewer` | judgment-bearing (opus) |
| 3 | **Docs** | `preprod-review-lens` | consistency-checking (sonnet) |
| 4 | **Portability** | `preprod-review-lens` | deployment/environment sweep (sonnet) |
| 5 | **Governance** | `preprod-review-lens` | cross-doc integrity (sonnet) |

**Pass the tier as an explicit `model` on every dispatch — the table above does
not enforce itself.** All three of these agent types carry `model: inherit`, so a
dispatch that omits `model` runs *every* lens at whatever the session is running
and the three sonnet rows are silently inert. The `Agent` tool's `model`
parameter takes precedence over agent frontmatter, which is what makes the tier
real: `{subagent_type: "preprod-review-lens", model: "sonnet", ...}`.

**All three are read-only by frontmatter** (`tools: Read, Grep, Glob`), which is
the only place that constraint can live — there is no per-dispatch `tools`
parameter to match the `model` one. Lenses 3–5 run `preprod-review-lens` rather
than the persona agents whose domains they cover, because
`documentation-specialist` authors elsewhere, while `cloud-devops-expert` has a
different build-design prompt. A dedicated lens keeps the review rubric fixed
and prevents either persona from judging with an authoring-oriented prompt.

If a listed agent type doesn't exist in the current harness, fall back to the
`Agent` tool with an explicit `model` matching the tier above — still never an
untier-ed default. **A fallback loses the frontmatter guarantee**, since `tools`
cannot be set at dispatch: say so in the synthesis, and treat that lens's
read-only contract as honored rather than enforced. Do not substitute a persona
agent (`documentation-specialist`, `cloud-devops-expert`) for a missing
`preprod-review-lens` — that reinstates write access on a review lens, which is
the defect the dedicated agent exists to close.

## Domain checklists

Lenses 1 and 2 hunt better when they start knowing where the bugs hide for this
*kind* of artifact. `references/` ships one checklist today:

| Artifact type | Checklist |
|---|---|
| GitHub Actions workflows | `references/github-actions-review.md` |
| anything else | none yet — the lens hunts its generic list and **says in its report that no domain checklist existed** |

**Never invent a checklist mid-run and present it as shipped.** If a domain
earns one, write it into `references/` as its own change, so the next run is
deterministic too.

## Dispatching the briefs

The briefs are **shipped, not re-authored** — `references/lens-briefs.md` holds
the five fixed briefs (hunt lists, verdict contract, failure-scenario demand,
positives, length cap). Each dispatch prompt is three lines; the agent reads its
own brief. Do **not** paste the brief or a domain checklist into the prompt —
agents have `Read`, and the briefs tell them what to open.

```
You are lens <N> (<name>) of a pre-prod review. Read
<ABSOLUTE-PATH-TO-THIS-SKILL>/references/lens-briefs.md and follow the
"Lens <N>" section exactly. Artifact: <X>. Goal: <ship | tag | elevate |
roll out>. Your files: <file list from step 1>.
```

**Expand that path before dispatching.** A subagent handed a literal
`<ABSOLUTE-PATH-TO-THIS-SKILL>` cannot read anything, and a lens that cannot
read its brief will improvise one — which is precisely the variance the shipped
briefs exist to remove. It resolves to `<skills-root>/preprod-review/` unless
a repo declares an override.

Deviate from a shipped brief only when the artifact genuinely demands it, and
say so in the synthesis — ad-hoc briefs are variance, and variance is how
lenses silently weaken. The underlying contract (judge ≠ generator, shipped
prompts over re-authored ones) is owned by the `second-opinion` skill; the five
lenses are that contract applied to a ship decision.

## Synthesis discipline

- **Verify before you report.** Open the cited line for every BLOCKER/HIGH. The
  reviewers are fallible in both directions — they invent plausible bugs and
  they mischaracterize real code. One session's Pass caught three "blockers"
  that were real *and* one reviewer's proposed safeguard that would have broken
  every install; only reading source separates them.
- **Dedup by file+symbol**, not by wording — the same bug surfaces under
  different names across lenses.
- **Rank by exploitability/impact**, not by which lens found it.
- **Map every finding to a disposition.** If the review will produce a fix
  plan, ensure no finding silently vanishes — each is either a deliverable or
  an explicit, reasoned deferral. Silent truncation of a findings list reads as
  "covered everything" when it didn't.

## Output template

```
# Pre-prod review — <artifact>

## Verdict
<BLOCKER | SHIP-WITH-FIXES | READY> — one paragraph on why, framed against the
actual goal (ship / tag / elevate / roll out), not against the artifact in the
abstract.

## BLOCKERS
<each: file:line · defect · failure scenario · fix>

## HIGH / MEDIUM / LOW
<ranked, same shape>

## Strong positives (do not regress)
<patterns already correct>
```

## When the review feeds a plan

If findings become a fix plan, hand off to the plan-authoring workflow
(`verified-planning` where present) rather than free-forming — a CI-canon fix
plan is load-bearing across every consumer and benefits from a cited Claim
ledger + independent review. Keep the *review* (this skill) and the *plan*
(that skill) as separate artifacts.
