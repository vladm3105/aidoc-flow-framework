# Plugin P2 Deploy Runbook — local-CLI validation & publish

> **Why this exists.** Every automated gate the dev container can run is
> green (conformance 129, `plm_lint` clean, zero bundle drift, spec sync
> `0.23.0`, release tag `claude-code-plugin/v0.20.1` pushed). What is *not*
> proven is that an **installed** copy runs correctly on a real Claude Code
> CLI — specifically risk **R2** from `PLUGIN-MARKETPLACE-PLAN.md`:
> `${CLAUDE_PLUGIN_ROOT}` provably expands in `hooks.json` / `.mcp.json`
> `command` fields but is *unconfirmed* inside SKILL / agent **body prose**.
> Until a live cascade runs from an install, "tested end-to-end" is false.
>
> These steps need the Claude Code CLI, which the dev sandbox does not have.
> Run them on your machine. In a Claude Code session you can run a shell
> command inline by prefixing it with `!` (e.g. `! git status`); the native
> `/plugin …` and `/model …` commands are typed directly at the prompt.
>
> **Pass bar:** the plugin is "tested / ready to publish" only after **Step 3**
> (a live skill run produces a gate-passing artifact). Steps 1–2 are
> structural; Step 3 is the real gate; Steps 4–5 publish.

| Field | Value |
| --- | --- |
| Plugin version | `0.20.1` |
| Framework spec | `0.23.0` |
| Marketplace | `aidoc-flow-framework` → plugin `aidoc-flow` |
| Source of record | `plans/PLUGIN-MARKETPLACE-PLAN.md` (P2 section) |

---

## Step 0 — Fresh clone (clean-room install conditions)

Validate against a clean checkout, not your working tree, so vendored-bundle
drift or uncommitted edits can't mask a problem.

```sh
git clone https://github.com/vladm3105/aidoc-flow-framework.git /tmp/aidoc-p2
cd /tmp/aidoc-p2
git checkout v1 2>/dev/null || true   # or the latest released ref
cat platforms/claude-code-plugin/VERSION                 # expect 0.20.1
cat platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION   # expect 0.23.0
```

## Step 1 — `claude plugin validate`

Static/structural validation of the plugin manifest + skill/agent/command
frontmatter.

```sh
cd /tmp/aidoc-p2/platforms/claude-code-plugin
claude plugin validate .
```

**Expect:** no errors. If it complains about `plugin.json`, `marketplace.json`,
or a skill's frontmatter, that is a real blocker — capture the message and
stop.

## Step 2 — Install smoke test

```text
/plugin marketplace add vladm3105/aidoc-flow-framework
/plugin install aidoc-flow@aidoc-flow-framework
```

**Expect:** install succeeds; the 12 commands appear under `/aidoc-flow:…`
(e.g. `/aidoc-flow:help`, `/aidoc-flow:status`, `/aidoc-flow:model`). Confirm:

```text
/aidoc-flow:help
```

## Step 3 — Live skill run (the real gate — R2)

This is the step that makes "tested" true. Drive a real layer authoring from
the installed plugin and confirm two things: (a) the model resolves the
bundled `${CLAUDE_PLUGIN_ROOT}/framework/…` template paths it reads in SKILL
**prose**, and (b) the produced artifact passes its audit gate.

1. Start a session in a scratch project dir (NOT the framework repo):

   ```sh
   mkdir -p /tmp/p2-cascade && cd /tmp/p2-cascade
   ```

2. Seed it from the example fixtures so the run has reference input:

   ```sh
   # copy the url-shortener seed as the authoring input
   cp -r /tmp/aidoc-p2/examples/url-shortener/seed ./seed
   ```

3. In the Claude Code session, run a single-layer authoring skill, e.g.:

   ```text
   Use doc-brd to draft a BRD from ./seed
   ```

   **R2 watch:** confirm the skill actually *reads* the template at
   `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml`. If the
   model reports it cannot find the path / the variable is literal, R2 has
   materialized — apply the documented fallback (a short "resolve
   `${CLAUDE_PLUGIN_ROOT}` via the env / `echo`" note in the orchestrator
   skill, or inject the resolved root via a hook). The bundle ships
   regardless; the fix is reference-form only.

4. Audit the produced artifact:

   ```text
   Use doc-brd-audit on the drafted BRD
   ```

   **Expect:** a gate-passing score (≥ 90) or a converging audit→fix loop.

**Pass criteria for Step 3:** the template paths resolved AND the artifact
reached a passing gate. Record the outcome in `plans/HANDOFF.md`.

## Step 4 — (Deferred) public mirror + community submission

Only after Step 3 passes and the org/domain identity is settled
(`PLUGIN-MARKETPLACE-PLAN.md` §E). The one-way mirror generator already
exists:

```sh
cd /tmp/aidoc-p2
bash tools/build-plugin-mirror.sh    # writes the mirror tree under dist/ (git-ignored)
```

Then create the public mirror repo, push `dist/`, and submit to the community
marketplace. Open input: the GitHub **org/namespace** for the mirror.

## Step 5 — Record the outcome

- Update `plans/HANDOFF.md` with the Step 3 result (R2 resolved or fallback
  applied) — this flips the plugin from "release-ready" to "deploy-verified".
- If R2 needed a fallback, that is real new work → open a NEW plan + impl PR
  (not a retroactive amendment), per CLAUDE.md §"Durable conventions".

---

## Quick reference — what's already done (do NOT redo)

| Gate | State |
| --- | --- |
| Conformance suite | ✅ 129 passed (dev container) |
| `plm_lint --all` | ✅ clean |
| Framework bundle drift | ✅ 0 (byte-identical) |
| Spec version sync | ✅ `0.23.0` == `0.23.0` |
| Release tag pushed | ✅ `claude-code-plugin/v0.20.1` on remote |
| BYO-marketplace install path | ✅ live (`marketplace.json` valid) |
