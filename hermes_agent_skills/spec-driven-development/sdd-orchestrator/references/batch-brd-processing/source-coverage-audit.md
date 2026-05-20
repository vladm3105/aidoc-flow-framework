# Source-to-BRD Coverage Audit

Before extracting BRDs from a large source document, verify that every section has
an explicit BRD home or a deliberate exclusion with rationale.

## Step 1: Extract All Section Headers

For markdown source documents:

```bash
grep -n '^# ' CC_Delta_Unified_Rulebook.md
```

Output format:
```
     1|# TradeGent CC — Delta-Unified Covered Call Strategy
    23|# Section 1: Stock Selection Criteria
   152|# Section 2: Strategy Philosophy
   ...
```

The regex `^# ` will:
- Match `# ` lines (H1)
- NOT double-match `## ` lines (H2)
- NOT count blank H1s

## Step 2: Build Coverage Matrix

| Source Section | Lines | Proposed BRD | Rationale | Status |
|---|---|---|---|---|
| §1 Stock Selection | 23–151 | BRD-02 | 4-gate screening rules | Assigned |
| §2 Strategy Philosophy | 152–223 | BRD-01 | Umbrella thesis concept | Assigned |
| §3 Strike Selection | 224–341 | BRD-03 | Option strike mechanics | Assigned |
| §4 Roll Trigger | 342–467 | BRD-03 | Roll rules, same BRD | Combined |
| §5 Weekly Calendar | 468–502 | BRD-04 | Timing schedule | Assigned |
| §6 Earnings Override | 503–558 | BRD-04 | Earnings rules, same BRD | Combined |
| §7 Three-Scenario PnL | 559–603 | BRD-06 | PnL simulation | Assigned |
| §8 Hard Stops | 604–724 | BRD-05 | Risk management | Assigned |
| §9 Position Sizing | 725–832 | BRD-05 | Risk rules, same BRD | Combined |
| §10 Order Types | 833–888 | BRD-04 | Execution rules, same BRD | Combined |
| §11 Performance Review | 889–999 | BRD-08 | Review cadence | Assigned |
| §12 Cheat Sheet | 1000–1200 | EXCLUDED | Reference material; BRD-01 appendix | Excluded |
| §13 Bad News Protocol | 1201–1300 | BRD-07 | Market state framework | Assigned |
| §14 Portfolio OS | 1301–1800 | BRD-09 | Portfolio coordination | Assigned |
| §15 AI Agent Model | 1801–1900 | BRD-01 | Agent execution model | Combined |
| §16 Formalisation Specs | 1901–2029 | BRD-01 | Spec definitions | Combined |

### Gap Detection Rules

1. **No unassigned H1**. Every `# ` line must appear in the coverage matrix.
2. **No orphan content**. Content between two H1 boundaries that doesn't belong
to either header is an orphan. Check:
   - Tables spanning sections
   - Code blocks between headers
   - Footnotes at document end
3. **Deliberate exclusions must have rationale**. "Reference material" or
"Already in BRD-01 appendix" are valid. "Not needed" is NOT valid.
4. **Combined sections must share a domain**. §3+§4 are both "option strategy",
so combining is correct. §1+§12 do NOT share a domain.

## Step 3: Human Approval

The coverage matrix must be presented in a plan document with an explicit human
approval gate. Do NOT start extraction before the human has:
1. Confirmed the section → BRD mapping
2. Approved combined sections (some users want each section as its own BRD)
3. Approved exclusions (some users want cheat sheet as a BRD for completeness)
4. Approved the naming convention (`BRD-NN_slug.yaml` or `BRD-NN.yaml`)

## Step 4: Check for Missing BRD Architecture

If any section has no natural BRD home, it may indicate a missing BRD in the
architecture — NOT an exclusion. Before excluding, ask:
- Does this section introduce a new capability not covered by existing BRDs?
- Would this section need its own EARS requirements?
- Would this section generate its own test cases?

If yes to any — create a new BRD, don't exclude.
