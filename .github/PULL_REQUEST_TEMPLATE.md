<!--
Canon structure per aidoc-flow-ci docs/REPO_STANDARDS.md §8, merged with this
repo's SDD traceability section (CANON-PARITY-001, D-0071). Canon ships this as
the lowercase `pull_request_template.md`; GitHub accepts either casing, and this
repo keeps the uppercase form — note that canon's manifest presence check is
case-sensitive and will read this file as absent.

Delete sections that don't apply. Keep Summary, Files touched, Multi-agent
review and Test plan.
-->

## Summary

<!-- 1-3 sentences: what changed and why. Reviewers read the diff for the
     "what" — spend the words on the "why". -->

## Linked issue

Closes #

## Files touched (OPS-0061 Rule 1 self-check)

<!--
Rule 1 caps a GOVERNANCE PR at ≤3 doc surfaces. This repo's governance-PR list
(CLAUDE.md § "Governance PR discipline" is the definition; this is a copy, so
check it there if the two ever disagree): CLAUDE.md, plans/*-PLAN.md and their
plans/*-DESIGN.md companions, plans/DECISIONS.md,
framework/governance/DECISIONS.md, .github/ai-review/,
.github/workflows/ai-review.yml, or a change that supersedes a locked decision.

The plan glob is a SUFFIX — every plan here is <NAME>-PLAN.md. The prefix form
plans/PLAN-*.md, which this template and CLAUDE.md both carried until
2026-07-30, matches only PLAN-TEMPLATE.md, i.e. no real plan.

Over 3 surfaces on a governance PR: SPLIT into sequential PRs, or record a
founder OK here AND as an audit-trail line in the commit message. Splitting is
the default — a carve-out is the exception.

Non-governance PRs (code, tests, docs-only) have no surface cap.
-->

| Surface | Change |
| --- | --- |
| `path/to/file` | brief note |

**Governance tier:** <!-- 🟢 non-governance / 🟡 governance / 🔴 spec-tier (GATE-SPEC) -->

## SDD traceability

<!-- Copy from the linked issue if `source:sdd`; otherwise delete this section. -->

| Tag | Reference |
|-----|-----------|
| @tasks | |
| @spec | |
| @req | |
| @brd | |

## Multi-agent self-review (OPS-0065 / OPS-0069)

<!--
The audit-trail phrase must appear in a COMMIT MESSAGE in the push range — not
in this body. `call / verify` greps for it literally (`grep -qF`), and it is a
REQUIRED context, so a missing phrase blocks the merge:

  Multi-agent self-review per OPS-0065 (<agents>): <verdict>

OR (founder OK required):

  Self-review skipped per founder OK — <reason>

Acceptable skip cases per the skip discipline: mechanical content (pin bumps
with no logic edits), review already done by a dispatched agent named in the
commit, or an explicit founder OK. Cap at 3 fold cycles per OPS-0066.
-->

**Agents dispatched:**

- `<agent>` — `<verdict>`

**Fold outcome:** <!-- e.g. "cycle 1 APPROVED, 0 findings" -->

## Test plan

<!-- What CI verifies vs what a human must verify. Check the boxes that apply;
     delete the rest. Unchecked boxes on a ready PR read as "not done". -->

- [ ] `pre-commit run --all-files` green (includes the conformance suite)
- [ ] `python -m pytest tests/conformance/` green
- [ ] platform tests green (`platforms/hermes/`, plugin)
- [ ] `python3 -m sdd_doc_lint examples/<name>/docs/` — zero *unexpected* findings
- [ ] `<domain-specific verification>`

## Cross-references

<!-- D-NNNN, GD-NN, PLAN files, issues, sibling-repo PRs. Delete if none. -->

-
