# Framework skills

Engine-agnostic agent skills shipped with the SDD framework. Adapted 2026-09-27 from the private canon `aidoc-flow-claude-agents-config/skills/` (12 skills).

## Why these live here

`AGENTS.md` prescribes dispatching "the framework's own skills" for example-artifact remediation. Until this directory, none shipped (#719). These 12 close that gap: the remedy is now dispatchable without leaving the framework tree.

## Index

| Skill | Use when | Canon source |
|---|---|---|
| `approval-gate/` | before external/irreversible action — classify, prepare challenge-and-response, never self-approve | canon `approval-gate/SKILL.md` |
| `context-handoff/` | context ending mid-task — capture resume state on the declared work item | canon `context-handoff/SKILL.md` |
| `memory-hygiene/` | repair memory-store drift — index 1:1, links, hooks; `lint.py` gate | canon `memory-hygiene/` + `lint.py` (MIT GlassOnTin) |
| `preprod-review/` | before release/rollout widening blast radius — 5 parallel lenses + verify + verdict | canon `preprod-review/` + `references/` |
| `recall/` | retrieve task-relevant memories via read-only subagent, not full-store read | canon `recall/SKILL.md` |
| `second-opinion/` | independent fresh-context judgment before high-stakes output ships | canon `second-opinion/` + judge in `_shared/agents/` |
| `self-learn/` | capture/consolidate/apply durable lessons — apply/capture/consolidate modes | canon `self-learn/SKILL.md` |
| `ship-it/` | watch a PR you opened to merge-on-green — required checks, carve-outs, cleanup | canon `ship-it/SKILL.md` (mined netresearch) |
| `start-session/` | session open — reconstruct ground truth, verify, select one bounded task | canon `start-session/SKILL.md` |
| `submit-feedback/` | capture defect on owning tracker — Origin real-use/review, search-first, safe body-file | canon `submit-feedback/SKILL.md` |
| `verified-planning/` | implementation/design plans — Claim ledger + `check_plan.py` gate + ≥2 passes, final independent zero-findings | canon `verified-planning/` + gate + tests |
| `wrap-session/` | thread finished — update only declared handoff/tracker/changelog/memory surfaces | canon `wrap-session/SKILL.md` |

Shared: `_shared/agents/` (judge + reviewers, engine-agnostic copies), `_shared/scripts/` (shadowing check).

## Engine mapping

- `<skills-root>` = this `framework/skills/` directory.
- Each engine loads `<skill>/SKILL.md` from its own user skill directory (or per-repo skill directory); agents from its agent directory; scripts from its script directory. See your engine's docs for the concrete paths.
- Other engines: consume `framework/skills/<skill>/SKILL.md` directly; where canon names an engine-specific agent type, use your engine's focused read-only subagent and keep the independence contract (judge ≠ generator, shipped briefs over re-authored prompts).

## Adaptation notes (canon → framework)

- Hard user-config paths rewritten to `<skills-root>/...` or `framework/skills/_shared/...`.
- Memory-store slug replaced by repo-declared store; `recall` §1 + `memory-hygiene` §Resolve own the derivation.
- Workspace specifics generalized to "owning repo declares".
- `verified-planning/install.sh` here installs the gate from `framework/skills/verified-planning/`; CI/hook run the in-tree `check_plan.py`.
- Provenance kept per skill header; MIT/mined-from lines preserved (`memory-hygiene/lint.py`, `ship-it`).

## Verification

- `python3 framework/skills/verified-planning/check_plan.py <plan>` for plan gates.
- `python3 framework/skills/memory-hygiene/lint.py <memdir> --brief` read-only; `--fix` only per skill gate.
- `bash framework/skills/_shared/scripts/check-skill-shadowing.sh <repo>` for name collisions.
- Repo gates: conformance + acceptance + `sdd_doc_lint` stay green; no platform names in `framework/`.
