# Adapting the Framework to a New Project

How to consume `aidoc-flow-framework` in a real project without forking
it: link (or clone) the framework, declare adaptation knobs in a profile,
and add project-local overrides. Based on the layout proven in a live
consumer (`.aidoc/` override layer with project profile and mirrored
overrides).

This guide is non-normative. The binding contract is
`framework/governance/ADAPTATION.md` (human-readable) plus
`framework/governance/ADAPTATION_SURFACE.yaml` (machine-readable knob
registry); the `.aidoc/` tier contract is
`framework/governance/aidoc/AIDOC.md`, and the per-project starting point
is `framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md`. Where this
guide and those files disagree, they win.

## 1. Scaffold `.aidoc/`

Copy `AIDOC-SCAFFOLD-TEMPLATE.md` to `<project>/.aidoc/README.md` and
follow it. The resulting shape:

```text
.aidoc/
├── profile.yaml             # project profile — adaptation knobs
├── framework/               # shared framework (symlink, canonical)
├── project/                 # project-specific overrides
│   ├── governance/          # rule overrides
│   ├── layers/              # template overrides
│   ├── playbooks/           # playbook overrides
│   ├── scripts/             # script overrides
│   ├── templates/           # template overrides
│   └── registry/            # registry overrides
└── README.md                # this file (from the scaffold template)
```

## 2. Attach the framework

Canonical form: `.aidoc/framework/` is a symlink to the shared framework
checkout (`AIDOC.md` § "Symlink convention"). One project in the wild
instead keeps a version-pinned copy. A pinned copy carries only the consumer
allowlist (`docs/PROJECT.md` §7.1: `framework/`, `docs/`, `hooks/`,
`sdd_doc_lint/`, `tests/`, minus `framework/archive/`) — never the whole
canon tree — and is refreshed by repeating that copy, never by pulling
inside `.aidoc/framework/`. Either form works if
you keep these invariants:

- Exactly one framework source per project; never copy framework files
  into `project/` unchanged.
- Record the pinned version in `.aidoc/profile.yaml` and keep it matching
  `framework/VERSION`.
- After an update, re-check every file under `project/` against its new
  upstream counterpart before adopting.

## 3. Declare knobs in `profile.yaml`

Start from `framework/governance/PROFILE-TEMPLATE.yaml`. Every key must
resolve to a knob in `ADAPTATION_SURFACE.yaml` — the surface is closed,
unknown keys are ignored, and no knob may relax a blocking quality gate
(a threshold knob may only go stricter). No profile means framework
defaults; adaptation is purely additive. Precedence:
framework defaults < user-global seed (`~/.aidoc/profile.yaml`,
authoring-time only) < project profile.

## 4. Add overrides that mirror the framework

`project/` MUST mirror the framework's directory structure (`governance/`,
`layers/`, `playbooks/`, `scripts/`, `templates/`, `registry/`) so the
discovery rule resolves: when an agent reads a template, rule, or
playbook, it checks `.aidoc/project/{same-path}` first and falls back to
`.aidoc/framework/{same-path}`. Override only what the project genuinely
changes; each override should cite the upstream file and the reason it
diverges.

## 5. What never goes where

- Project data (profiles, learnings, overrides) never lands under
  `framework/` — the spec ships the contract, never project content
  (enforced by `tests/conformance/test_governance.py`, D-0013).
- Overrides stay declarative (switches, bounds, terms). They never carry
  logic and never rewrite how a skill works.
- Overrides stay engine-agnostic: no stack, tool, path, or port choices
  leak into framework-shaped files.

## 6. Updating the framework

1. Advance the framework source (pull the shared checkout, or `git pull`
   inside a pinned clone).
2. Diff the new `framework/VERSION` against the pin in `profile.yaml`;
   bump the pin deliberately, never silently.
3. Re-diff each `project/` override against its upstream counterpart;
   retire overrides the new framework version made redundant.
4. Re-run the project's gates before treating the bump as adopted.

## 7. Green linters do not equal governed (#813)

A green lint run means every *emitted* rule passed — not that every
governance contract holds. `framework/governance/LINT_RULES.md` carries
Reserved rows (18: EVAL ×6, GOV-008/009/010/013/015 ×5, IPLAN01, REG01,
TDD-SYNC-A–E ×5) — documented contracts with deliberately no emitting
code. Checklist-gate or IPLAN-substance violations in that set pass
silently; the backstop is reviewer judgment (the review crews and lenses),
not a second lint pass. Do not invent emitters or reclassify Reserved
rows to close this gap — the reservation is the contract.
