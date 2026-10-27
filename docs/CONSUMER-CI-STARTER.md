# Consumer CI Starter

Minimal copy-paste gate workflow for a new consumer project. `.github/` is
deliberately excluded from the consumer copy (`PROJECT.md` §7.1), so adopt
this file as `.github/workflows/sdd-gate.yml` — otherwise the first PR
ships with zero gate enforcement.

## The workflow

```yaml
# .github/workflows/sdd-gate.yml — minimal SDD structural gate (CHG-128).
# Works with both attachment models: pinned copy and submodule resolve
# sdd_doc_lint at .aidoc/framework/sdd_doc_lint/ either way.
name: SDD structural gate

# No `paths:` filter on this workflow: a required check with trigger
# filtering deadlocks PRs outside those paths (anti-deadlock invariant,
# ADAPTATION-GUIDE.md §4.1 / CI_SMART_ROUTING).
on:
  pull_request:

permissions:
  contents: read

jobs:
  sdd-gate:
    name: SDD structural gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - name: Set up Python 3.12
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: '3.12'
      - name: Install linter runtime
        run: pip install pyyaml jsonschema
      - name: Validate adaptation profile
        run: PYTHONPATH=.aidoc/framework python3 -m sdd_doc_lint.profile_lint .aidoc/profile.yaml
      - name: Lint SDD tree
        run: PYTHONPATH=.aidoc/framework python3 -m sdd_doc_lint docs/sdd
      - name: Lint change requests
        run: |
          shopt -s nullglob
          chgs=(docs/sdd/09_CHG/CHG-*.yaml)
          if [ ${#chgs[@]} -gt 0 ]; then
            PYTHONPATH=.aidoc/framework python3 -m sdd_doc_lint.chg_lint "${chgs[@]}"
          else
            echo "no CHG files yet — skip"
          fi
```

## After adopting

1. Push the file on the first PR — the gate runs before any SDD content
   exists (empty tree lints clean).
2. Make `SDD structural gate` a **required** status check (branch
   protection on the default branch). A non-required gate verifies
   nothing.
3. Extend from here, never by trigger filtering: add `swf_lint` over
   declarative workflows, `graph-check` over `docs/sdd/graph/`, and the
   project's own test suites as further jobs.
4. Add a scheduled pin-currency check (no push signal ships with the
   framework): weekly, compare `.aidoc/profile.yaml` `framework_version`
   against the latest canon release (`gh release view --repo
   vladm3105/aidoc-flow-framework --json tagName`) and open the
   re-adoption work per `UPGRADE-RUNBOOK.md` on lag.
