# 08_IPLAN — Implementation Plan

## C4 Model Position

IPLAN is part of the **Implementation Bridge** (L7-L8, no C4 level). It is the execution bridge between TDD and source code. C4-L4 (Code) diagrams belong to the source code layer, not to IPLAN documents.

## Purpose

Mandatory execution layer bridging TDD (L7) to source code. One IPLAN per SPEC component. Each IPLAN declares the file creation order (test-first from TDD), provides executable bash commands, tracks session progress across stateless executor calls, and maintains an audit trail from specification to delivered files.

## Permanent vs Temporary Plans

| | Permanent IPLAN (`IPLAN-NN_{slug}.yaml`) | Temporary IPLAN (`tmp/TMP-IPLAN-*.yaml`) |
|---|---|---|
| **Purpose** | Implement a SPEC component via TDD test cases | Bugfix, correction, investigation — no new functionality |
| **Requires TDD** | Yes — one IPLAN per TDD | No — standalone |
| **Registered in index?** | Yes — `IPLAN-00_index.yaml` | No |
| **Triggers audit trail?** | Yes — code inventory, session log | No — disposable |
| **Deleted when?** | Never — historical record (use ABANDONED) | Within 7 days of DONE/ABANDONED |
| **Naming** | `IPLAN-NN_{slug}.yaml` (NN sequential, never reused) | `TMP-IPLAN-YYYY-MM-DD_{slug}.yaml` |

**Rule of thumb**: Does the work implement a TDD test contract? → permanent. Does it restore intended behavior or fix a bug? → temporary.

## Index registry vs document schema

The `08_IPLAN/` directory holds **two distinct schemas**, so a naive "validate
every `IPLAN-*.yaml`" glob will misfire:

- **`IPLAN-00_index.yaml`** — `document_type: iplan-registry`. A registry of the
  permanent IPLANs; it carries **no `document_control`** and declares no element
  IDs or trace tags.
- **`IPLAN-NN_{slug}.yaml`** — `document_type: iplan-document`. The execution
  manifests, with full `document_control` + `@spec`/`@tdd` lineage.

**Validation:** `sdd_doc_lint` already special-cases index docs — it exempts
`artifact_type: *-INDEX` from the document-schema, trace-resolution, and element
checks. So the registry is validated as a registry, the documents as documents;
do not apply the `iplan-document` schema to `IPLAN-00_index`.

## Development/Work Plans (markdown)

Distinct from BOTH YAML artifacts above is the **development/work plan** — the markdown plan-of-record an agent writes in a repository's `plans/` directory before a change, covering objective, scope, approach, task sequence, verification, and review trail. Its structure, the work-type applicability rules, and the review discipline are specified in [PLAN_STANDARD.md](PLAN_STANDARD.md); the copy-paste working instance is the repository's `plans/PLAN-TEMPLATE.md`.

A development plan is a *design-and-review record* read by a reviewer to approve a change; the two YAML IPLAN artifacts are *execution manifests* consumed by an agent step-by-step. A development plan may spawn a Permanent or Temporary IPLAN as one of its tasks, but the three are not interchangeable. Adding this standard changes neither YAML artifact.

## Design Decisions

- **Mandatory layer** — one IPLAN per TDD/SPEC component, created when TDD reaches IPLAN-Ready >=90/100.
- **Test-first file order** — file_manifest declares test files before implementation files (TDD principle inherited from L7).
- **Session handoff protocol** — solves the stateless executor problem: each session reads the previous session's state, identifies the next incomplete step, and continues without regenerating completed work.
- **Implementation contracts embedded** — Type interfaces, exception hierarchies, and state machines live in the IPLAN (no separate contract files).
- **Code inventory for audit trail** — one entry per `file_manifest` path, seeded `planned` at Draft, then set to `created` / `modified` with session attribution and verification status.
- **Temporary plans** for bugfixes only — no TDD upstream, disposable, live in `tmp/`.

## IPLAN Baseline

| Area | IPLAN |
|---|---|
| Upstream contract | TDD + SPEC |
| Execution tracking | File manifest with status markers |
| Scope ownership | Execution-only (business scope remains in upstream docs) |
| Sequencing model | File-by-file test-first creation order |
| Validation reporting | `validation_results` per session handoff entry |
| Planning model | Permanent + temporary plan split |

## TDD-case carrier (`tdd_ref`)

A file-manifest entry MAY name the TDD test cases it builds:

```yaml
- path: tests/unit/test_auth.py
  order: 1
  status: NOT_STARTED
  tdd_ref: "@tdd: TDD.01.04.aaaa | @tdd: TDD.01.04.bbbb"
```

Three rules govern it:

1. **The value is the tag, and it must be quoted.** YAML treats a leading `@` as a
   reserved indicator, so an unquoted value fails to parse. Several cases may share one
   scalar, pipe-delimited.
2. **The key and the tag share one line.** This mirrors the TDD layer's own
   `bdd_scenario:` / `bdd_ref:` carriers. A downstream check reads both from a single
   line, so **a citation listed only in the traceability block is not a build record** —
   that is the whole point of the carrier.
3. **Optional per entry.** A package initialiser or a config file legitimately realizes
   no test case. Completeness is judged from the TDD side — every declared test case
   should be named by some entry — not by requiring every entry to name a case.

The carrier is a field-name token, so it is not tied to one serialization: the same
rule applies wherever the manifest is rendered.

## Session Handoff Protocol

Each AI agent session reads the IPLAN in this order:

1. **Read session_handoff.sessions** — identify the last session's state
2. **Check file_manifest.files** — find next NOT_STARTED or PARTIAL file
3. **Read partial_work** description if resuming a PARTIAL step
4. **Continue from that point** — do NOT regenerate completed work
5. **Update file status** after completion or session end
6. **Append to session_handoff.sessions** with next_session_directive

**A Draft IPLAN carries `sessions: []`** — the trail is retrospective, appended by
each session as it ends, so at Draft there is nothing to record and step 1 falls
straight through to step 2. Writing a session entry while authoring asserts work
that has not happened. This is deliberately *unlike* the code inventory above,
which **is** seeded at Draft: that seed is derived from a set already known (one
entry per `file_manifest` path), whereas nobody knows the future sessions.

## Template

| File | Purpose |
|------|---------|
| `IPLAN-TEMPLATE.yaml` | **Default** — full template with embedded authoring guidance. Self-documenting for AI agents. |
| `IPLAN-MVP-TEMPLATE.yaml` | Skeleton — stripped-down structural form. Not standalone. See [BRD README](../01_BRD/README.md) for the template selection rule. |

## Registry

For the authoritative plan registry (statuses, execution path, deferred items, cross-plan obligations, status history), see [IPLAN-00_index.TEMPLATE.yaml](IPLAN-00_index.TEMPLATE.yaml).
