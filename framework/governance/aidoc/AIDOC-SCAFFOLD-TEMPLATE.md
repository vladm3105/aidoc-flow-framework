# `.aidoc/` — Project Override Layer and Profile

## Document Control

| Field | Value |
|-------|-------|
| Version | 2.0 |
| Status | Approved |
| Last Updated | YYYY-MM-DD |
| Author | <your name> |
| Framework Version | X.Y.Z |

This directory is the project customization layer for the aidoc-flow-framework.
It holds the project profile (adaptation knobs) and project-specific overrides
that take precedence over the framework's defaults.

## Directory structure

```
.aidoc/
├── profile.yaml             # project profile — adaptation knobs
├── framework → ...          # symlink to shared framework (canonical path)
├── project/                 # project-specific overrides
│   ├── governance/          # rule overrides (same structure as framework/)
│   │   └── ...
│   ├── layers/              # template overrides (same structure as framework/)
│   │   └── ...
│   └── playbooks/           # playbook overrides (same structure as framework/)
│       └── ...
└── README.md                # this file
```

## Discovery rule

When the agent reads a template, rule, or playbook:

1. Check `.aidoc/project/{same-path}` first
2. If the file exists there, use it (project override)
3. If not, fall back to `.aidoc/framework/{same-path}` (shared framework)

## Framework symlink

`.aidoc/framework/` is a symlink to the shared framework directory.
The canonical path is declared in `profile.yaml` as `framework_path`.

## Project profile

`.aidoc/profile.yaml` carries the project's adaptation-knob overrides. See
`framework/governance/ADAPTATION.md` for the full contract and
`framework/governance/ADAPTATION_SURFACE.yaml` for the closed knob registry.

## Project overrides

Project-specific files live in `.aidoc/project/` using the same directory
structure as the framework. See `framework/governance/ADAPTATION.md` §10 for
the override contract and constraints.

## Framework version

This project pins **aidoc-flow-framework X.Y.Z** (declared in
`profile.yaml` as `framework_version`).
