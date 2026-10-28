# docs/ — Reading Map

Start here. Read order for a new team: kickoff → adaptation → workstation
standard → the one contract section → the rest only as needed.

## Live — read in this order

| # | Doc | What it is |
|---|---|---|
| 1 | [`STARTUP_HANDOFF.md`](STARTUP_HANDOFF.md) | Project kickoff quickstart (§0): installer, profile, blueprints, seed, verification |
| 2 | [`ADAPTATION-GUIDE.md`](ADAPTATION-GUIDE.md) | Consuming the framework without forking it: scaffold, attach, knobs, overrides, blueprints |
| 3 | [`AIDOC_WORKSTATION_STANDARD.md`](AIDOC_WORKSTATION_STANDARD.md) | Canonical `.aidoc/` workstation: discovery, gate floor, dual-control review, Taskfile tasks |
| 4 | [`CONSUMER-CI-STARTER.md`](CONSUMER-CI-STARTER.md) | Copy-paste minimal CI gate for new consumer repos |
| 5 | [`CONSUMER-DEPLOYMENT-STANDARD.md`](CONSUMER-DEPLOYMENT-STANDARD.md) | Deployment standard: Compose for dev, OpenTofu Day-0/Day-2 for stage/prod |
| 6 | [`AUTHENTICATION-STANDARD.md`](AUTHENTICATION-STANDARD.md) | Universal authentication standard: Authentik OIDC, Forward-Auth, and agent delegation |
| 7 | [`PROJECT.md`](PROJECT.md) §7 | Integration contract: consumer allowlist, directory shape, pinning (the rest of the file is frozen migration history) |
| 8 | [`SUPPORT.md`](SUPPORT.md) | Where to file what — only **Direct on GitHub** is live; the plugin/website channels are retired |

## Canon-repo process (not consumer kickoff)

| Doc | What it is |
|---|---|
| [`TAGGING.md`](TAGGING.md) | Live git-tag policy + release inventory for this repo; re-derive high-water marks with `git tag -l` rather than trusting the snapshot |
| [`history/STARTUP-BRIEF-2026-05-20.md`](history/STARTUP-BRIEF-2026-05-20.md) | The 2026-05 migration brief, moved verbatim out of the kickoff guide (CHG-128); history, not instruction |
| [`REPO_STRUCTURE.md`](REPO_STRUCTURE.md) | Migration-era layout record; the live layout is the repo root |

## Enterprise / point-in-time (not day-1 reading)

| Doc | What it is |
|---|---|
| [`FEDERATED_READ_LAKE_PATTERN.md`](FEDERATED_READ_LAKE_PATTERN.md) | Multi-project graph topology (edge Kùzu → central read lake); adopt after single-project flow works |
| [`audit and suggestions conclusion.md`](audit%20and%20suggestions%20conclusion.md) + `audit and suggestions.pdf` | 2026-10-15 architecture audit + ROI evaluation; the ratified output lives in `framework/governance/` |
