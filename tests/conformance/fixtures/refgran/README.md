# `refgran` fixtures — committed evidence, immutable

Three governance surfaces as they stood **immediately before** the GD-13
correction (#530). They are the regression subject of
`tests/conformance/test_ref_granularity_parity.py`.

## Provenance

Every file here is byte-identical to its source revision. Re-derive on demand:

```sh
for f in ID_NAMING_STANDARDS TRACEABILITY TAG_SYNTAX; do
  diff <(git show "8dccc315^:framework/governance/$f.md") \
       "tests/conformance/fixtures/refgran/pre530_$f.md"
done
```

`8dccc315` is `fix(spec): framework 0.41.3 — CHG overlay semantics and GD-03
citation-granularity errata (GD-13) (#530)`, so `8dccc315^` is the last commit
at which the drift was live.

| File | Document-level-permitted set it states | Role |
| --- | --- | --- |
| `pre530_ID_NAMING_STANDARDS.md` | `{ADR, SPEC, TDD, IPLAN}` | drifted — the primary regression subject |
| `pre530_TRACEABILITY.md` | `{ADR, SPEC, TDD, IPLAN}` | drifted — the second of GD-13's two prose surfaces |
| `pre530_TAG_SYNTAX.md` | `{SPEC, IPLAN}` | **negative control** — already correct at this revision, and must stay extractable as correct |

## Do not "fix" these files

They have never been style-linted and they must not be. Their whole value is
that they are the drift verbatim, so a hook or a contributor normalising
emphasis, whitespace or line endings destroys the evidence — and the suite would
then be green *because* the corruption ran.

**Three** surfaces protect them, and each covers a path the others do not:

| Surface | Protects against |
| --- | --- |
| the **global** `exclude:` in `.pre-commit-config.yaml` | every pre-commit hook, on commit |
| the `!tests/conformance/fixtures/refgran` glob in `.github/workflows/markdown-lint.yml` | CI markdownlint |
| `tests/conformance/fixtures/refgran/` in `.markdownlintignore` | a contributor running `markdownlint` directly — pre-commit passes explicit paths and ignores this file, so it is the only surface that covers this |

The pre-commit exclusion is **global** rather than markdownlint-scoped because
`trailing-whitespace`, `end-of-file-fixer` and `mixed-line-ending` rewrite
unconditionally and carry no exclude of their own, so a per-hook line would
leave three of the four live.

All three are scoped to `refgran/` and **not** to `fixtures/`. That is
deliberate and measured: the sibling `saga/` and `review/` fixtures are sample
reports and a JSON schema rather than extracted evidence, and a directory-wide
exclude silently dropped them — and every future fixture — out of `check-json`,
`detect-secrets`, `ruff` and `yamllint`, for a byte-faithfulness reason that
does not apply to them.

If an extractor rewrite makes a fixture fail, the extractor is wrong. That is
what the fixture is for.
