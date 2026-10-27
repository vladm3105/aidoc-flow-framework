# CHG Request Flows — Flow selector (normative router)

Every artifact change MUST be classified into exactly one flow — or into a governed non-flow path (Emergency,
Type-R) that yields to its own section — before a CHG is authored. Classify in this order — the first matching
row wins:

| Code | Flow Identifier | Traversal Path | Trigger | `change_source` | `change_level` | Entry Gate | SDD Cascade? | IPLAN Shape | Verification |
|:---:|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **HOTFIX** | `hotfix` | `Code` $\rightarrow$ `Prod` (post-hoc `Doc`) | Critical production issue requiring fix before authorization | `Emergency` level | Emergency | Post-hoc | None (retroactive document within 48h + post-mortem) | Fix IPLAN post-hoc per `09_CHG/README.md` + `POST_MORTEM-TEMPLATE.md` | Post-mortem verification; deployable fixes close live (§3.3 rule 10) |
| **CODE2S** | `code_to_sdd` | `Code` $\rightarrow$ `IPLAN` $\rightarrow$ `SDD` | Verified working codebase preceding its specs (non-emergency empirical work) | `reconciliation` | C2 typical | GATE-CODE | Reverse — Code→TDD→SPEC→BDD→EARS per §3.1.2 | Reverse-authored (ground truth from code) | §3.1.2 Phase-3 battery; runtime touches close live (§3.3 rule 10) |
| **CODE2C** | `code_to_code` | `Defect` $\rightarrow$ `IPLAN` $\rightarrow$ `Code` | Defect found in EVAL, manual test, or field use, traceable to a `Completed`/`Verified` parent IPLAN | `feedback` | C1 CHG (CHG-05 vehicle) | GATE-CODE | No (parent SDD stands; fix-IPLAN carries `validation_findings`) | Bugfix-subtype (`parent_iplan` + `source_chg`, repair-scoped manifest, rollback) | Regression suite + parent revision entry; runtime fixes close live (§3.3 rule 10) |
| **SEED2C** | `seed_to_code` | `Seed` $\rightarrow$ `Module` $\rightarrow$ `SDD` $\rightarrow$ `Code` | Product design or behavior change to an implemented product (Full Multi-Tier Chain) | `upstream` / `midstream` / `design` / `spec` | C2 / C3 (C3 if cross-layer or new requirements) | GATE-01 / 03 / 06 / GATE-SPEC | Yes — modules-first restart per §4 (0a seed_scope, 0b affected-module sync + review checkpoint, 0c SDD cascade over affected layers and everything below) | Full, referencing NEW SDD versions (authored only after checkpoint passes) | EVAL cycles + live closeout (deployable — §3.3 rule 10) |
| **DIR2C** | `iplan_to_code` | `IPLAN` $\rightarrow$ `Code` / `Docs` | Human or AI-agent request, unrelated to any prior IPLAN, no product-behavior change (docs, scripts, hooks, small tooling) | `direct` | C1 (every C1: C1 CHG + scoped IPLAN per F2.2, every author; sole exception seed-phase drafting pre-first-BRD) | GATE-CODE | No (`sdd_lifecycle: []`) | Scoped (manifest + steps only, §3.3) | Covering tests + verification commands in scoped IPLAN; static closeout (non-deployable — §3.3 rule 10) |
| **SDD2C** | `sdd_to_code` | `BRD` $\rightarrow$ `PRD` $\rightarrow$ ... $\rightarrow$ `Code` | New product / new layer chain, no prior implementation (SDD Layer Chain) | `upstream` | C3 | GATE-01 | Yes — full 10-layer authoring per §3.1.1 (BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN→Code→EVAL) | Full (all code steps, full manifest) | EVAL cycles + live closeout (deployable — §3.3 rule 10) |

*(Legacy Aliases: `HOTFIX` $\leftrightarrow$ Emergency, `CODE2S` $\leftrightarrow$ Type-R, `CODE2C` $\leftrightarrow$ F4, `SEED2C` $\leftrightarrow$ F3, `DIR2C` $\leftrightarrow$ F2, `SDD2C` $\leftrightarrow$ F1).*

## Source → Entry Gate

| Source | Entry Gate |
|--------|-----------|
| Upstream | GATE-01 |
| Midstream | GATE-03 |
| Design | GATE-06 |
| Execution | GATE-08 |
| External (business) | GATE-01 |
| External (technical) | GATE-03 |
| Feedback | GATE-CODE |
| Reconciliation (Backward) | GATE-CODE |
| Direct | GATE-CODE |
| Spec | GATE-SPEC |

Classify-then-route detail across dual-layer graph flows: `framework/governance/CHG_REQUEST_FLOWS.md` (canonical). Router order:
`HOTFIX` (`hotfix`) → `CODE2S` (`code_to_sdd`) → `CODE2C` (`code_to_code`) → `SEED2C` (`seed_to_code`) → `DIR2C` (`iplan_to_code`) → `SDD2C` (`sdd_to_code`).
