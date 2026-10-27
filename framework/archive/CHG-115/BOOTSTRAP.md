# `.aidoc/` Bootstrap — new-project procedure + shape validation

## Document Control

| Field | Value |
|---|---|
| Version | 1.4 |
| Status | Approved |
| Last Updated | 2026-10-17 |
| Author | Framework Maintainer |
| Framework Version | 0.96.1 |
| Authority | [Decision D-0013 / GD-13](../DECISIONS.md), [`AIDOC_WORKSTATION_STANDARD.md`](../../../docs/AIDOC_WORKSTATION_STANDARD.md), [`AIDOC.md`](AIDOC.md) |

---

This is the ordered procedure for deploying `.aidoc/` on a new project (#786). The contract lives in `AIDOC.md` and `docs/AIDOC_WORKSTATION_STANDARD.md`; the profile semantics in `ADAPTATION.md` + `ADAPTATION_SURFACE.yaml`. Follow the steps in order — each step's check must pass before moving on.

## Procedure

Steps 1–5 are automated by `framework/scripts/install.sh` (pinned copy) or the ecosystem onboarding tool `aidoc-project-onboarding` (`onboard greenfield`) — the steps below are the procedure performed.

Prerequisites: `git`, `bash` 4+, `python3` (for the closed-key check and linting), and a POSIX `sed`.

### 0. Clone the canon

```bash
git clone --depth 1 --branch framework/vX.Y.Z \
  https://github.com/vladm3105/aidoc-flow-framework.git canon
```

Use the adopted release tag (`docs/PROJECT.md` §7.1); the `AIDOC_CANON_URL` env var overrides the URL in air-gapped setups. Verify the clone against the tag's commit SHA when supply-chain matters (`install.sh --canon-sha <40-hex>` refuses a mismatch). Run steps 1–5 from the clone root.

### 1. Copy the scaffold README

Run from the framework repository root (the step-0 clone):

```bash
mkdir -p <project>/.aidoc
cp framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md <project>/.aidoc/README.md
```

Fill the `YYYY-MM-DD`, author, and `X.Y.Z` placeholders in the copied file.

### 2. Copy the profile template and fill the knobs

```bash
cp framework/governance/PROFILE-TEMPLATE.yaml <project>/.aidoc/profile.yaml
```

Uncomment and fill only the knobs the project overrides. Keys must come from the closed set in `ADAPTATION_SURFACE.yaml` — engines IGNORE any other key. Per-layer review crews and persona weights are framework-defined (`REVIEW_CREWS.yaml`) and are not project-overridable through this surface.

### 3. Attach the framework (pinned copy or git submodule)

> [!IMPORTANT]
> **Raw filesystem symlinks in version control are strictly forbidden** per [`docs/AIDOC_WORKSTATION_STANDARD.md`](../../../docs/AIDOC_WORKSTATION_STANDARD.md) §8.

Sanctioned attachment mechanisms:
1. **Pinned allowlist copy (default):** What `install.sh --kind pin` scaffolds (self-contained).
2. **Git submodule:** Attached directly under `.aidoc/framework/`:
   ```bash
   git submodule add https://github.com/vladm3105/aidoc-flow-framework.git <project>/.aidoc/framework
   ```

`.aidoc/framework` is the canonical path engines resolve. A pinned copy MUST be refreshed on every upgrade (see `UPGRADE-RUNBOOK.md`) — a stale copy is silent drift.

### 4. Pin the framework version & scaffold workstation components

1. Set `framework_version` in `<project>/.aidoc/profile.yaml` `metadata` to the canon `framework/VERSION` the project adopts (exact `X.Y.Z`, never a range).
2. Scaffold `.aidoc/Taskfile.yml` from `framework/templates/TASKFILE-TEMPLATE.yml`.
3. Scaffold `.aidoc/engine/engine.yaml` from `framework/templates/ENGINE-CONFIG-TEMPLATE.yaml`.
4. Scaffold `stack-policy.yaml` from `framework/templates/STACK-POLICY-TEMPLATE.yaml`.
5. Scaffold working agreement `<project>/AGENTS.md` from `framework/templates/AGENTS-TEMPLATE.md`.
6. Initialize graph repository directory: `mkdir -p docs/sdd/graph`.
7. Initialize local workstation cache directory with gitignore (ensuring zero binary bloat in version control per GD-13):
   ```bash
   mkdir -p <project>/.aidoc/cache
   echo "*" > <project>/.aidoc/cache/.gitignore
   echo "!.gitignore" >> <project>/.aidoc/cache/.gitignore
   ```

### 5. Smoke-verify the shape

The fresh `.aidoc/` passes when ALL of these hold:

- [ ] `.aidoc/README.md`, `.aidoc/profile.yaml`, and `.aidoc/Taskfile.yml` are present.
- [ ] `.aidoc/framework` exists as a valid directory or Git submodule (not a broken link).
- [ ] `metadata.project_name` in `profile.yaml` is non-empty and matches the project.
- [ ] Every key in `profile.yaml` is in the `ADAPTATION_SURFACE.yaml` closed set (no unknown keys).
- [ ] `stack-policy.yaml` is established at project root (or explicitly opted out).
- [ ] `.aidoc/engine/engine.yaml` is present declaring active engine and operating mode.
- [ ] Behavior-changing project docs live under `.aidoc/project/` (mirroring `framework/` paths per the discovery rule) — never loose at `.aidoc/` root.
- [ ] `framework_version` in `profile.yaml` equals the adopted canon `framework/VERSION`.
- [ ] Architecture decisions are anchored in Layer 05 (`docs/sdd/05_ADR/ADR-00_index.yaml` initialized from `ADR-00_index.TEMPLATE.yaml`).
- [ ] `docs/sdd/graph/` directory is present for SDD-GRAPH v2.0 manifests.
- [ ] `.aidoc/cache/` exists and is gitignored (ensures zero binary bloat per GD-13).
- [ ] Working agreement `<project>/AGENTS.md` is established (from `framework/templates/AGENTS-TEMPLATE.md`) instructing `task sdd:lint` and `task sdd:check`.
- [ ] Zero forbidden monolithic files exist at repository root or `docs/`: no loose `DECISIONS.md`, `ROADMAP.md`, `CHANGELOG.md`, or `docs/HANDOFF.md`.

## What is NOT part of the contract

Extra top-level directories (e.g. a `knowledge/` dir) are not read by engines and are not a sanctioned tier member — project knowledge belongs under `.aidoc/project/` or the project's own docs. Overrides never modify the shared `framework/` directory.

Monolithic markdown logs (`DECISIONS.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/HANDOFF.md`) are retired anti-patterns per CHG-40, CHG-80, CHG-94, CHG-95, GD-71, and GD-78. All state belongs in structured SDD layers, Change Requests, and GitHub milestones/issues.

## See also

- [`AIDOC.md`](AIDOC.md) — workstation contract, discovery rule, and Quad-Pillar topology
- [`docs/AIDOC_WORKSTATION_STANDARD.md`](../../../docs/AIDOC_WORKSTATION_STANDARD.md) — workstation directory standard and dual-control architecture
- [`ADAPTATION.md`](../ADAPTATION.md) §10 — the override contract and constraints
- [`UPGRADE-RUNBOOK.md`](UPGRADE-RUNBOOK.md) — moving an adopted project to a new canon version
