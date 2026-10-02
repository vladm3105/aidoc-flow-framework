# verified-planning — committed gate only

This directory holds the **gate**, not the skill. `check_plan.py` and
`plan-gate.yml` live here because CI and the pre-commit hook run inside this
repo and need them in the checked-out tree.

**Do not add a `SKILL.md` here.** The skill is available in every repo from
`~/.agents/skills/verified-planning/`. A local `SKILL.md` does not
supplement that copy — the user skill masks it, so the local file can drift
while appearing authoritative.

Refresh this directory with `~/.agents/skills/verified-planning/install.sh <repo>`.
