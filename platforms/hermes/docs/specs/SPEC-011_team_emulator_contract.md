# SPEC-011 Team Emulator Contract

## Purpose

`sdd_team_plan` runs a lightweight AI employee planning council and writes
approval-ready team simulation artifacts. It mirrors the Claude plugin
`/team-plan` workflow.

## Inputs

- `project`: project root path.
- `supervisor_request`: task or desired outcome from the human supervisor.
- `slug`: short artifact folder slug.
- `roles_dir`: optional path to role profiles. Defaults to `<project>/.claude/agents`.
- `context`: optional context source or brief.
- `constraints`: optional list of constraints.
- `requested_roles`: optional explicit role ids; `ceo` is always included.

## Outputs

The tool returns selected roles, artifact paths, and the status message:

```text
Status: Awaiting supervisor approval
```

## Artifact Contract

```text
ops/team-simulations/YYYY-MM-DD_<slug>/
  00_intake.md
  01_council-transcript.md
  02_conflicts-and-risks.md
  03_implementation-plan.md
  04_approval-request.md
```

## Safety

The tool does not execute implementation work. It writes planning artifacts only.
Human approval is required before any implementation agent executes the plan.
Invalid role IDs or missing role profile files fail the tool call.
