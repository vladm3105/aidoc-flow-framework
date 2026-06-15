---
title: "Support — where to file what"
description: Channel directory for developers, evaluators, and contributors. Names the four channels, what each is for, and what to expect after submission.
tags:
  - reference
  - active
custom_fields:
  document_type: reference
  priority: shared
  development_status: active
---

# Support

Four channels. Different intents, same triage destination, transparent
trade-offs. Pick the one that matches what you're trying to do.

> **One thing to know up front:** the plugin **never auto-submits**
> anything. Every channel below ends at a form on `github.com` or in
> your Gmail — *you* click Submit. The AI Team handles filtering and
> drafting; humans handle authorship.

## The four channels

| When | Use this | Where it lands |
|---|---|---|
| Plugin is installed; the problem is right in front of you | `/aidoc-flow:bug-report <one-line description>` | LLM drafts a complete GitHub issue from your prompt + recent conversation context; you click the printed URL and Submit on github.com |
| Plugin is installed; you have an idea or comment | `/aidoc-flow:feedback <one-line summary>` | Same shape as `bug-report`, lands on the `feedback.md` template |
| You're on GitHub already; you know what's broken | [GitHub Issues](https://github.com/vladm3105/aidoc-flow-framework/issues/new/choose) — pick the **Bug Report** or **Feedback** template directly | Issue lands in the repo's triage queue |
| You're on the website; no GitHub account or you want to ask something open-ended | [`aidoc-flow.io/support`](https://aidoc-flow.io/support) — Bug-report and Feedback sections link out to GitHub; Contact-us is for everything else | Bug-report / Feedback → GitHub; Contact-us → AI Team intake (live; Google Forms → Sheet → Drive MCP poll) |

## Channel details

### 1. In-product `/aidoc-flow:bug-report`

You type one sentence about what broke; the plugin's LLM uses that
plus the recent conversation context (last command, the error message,
files referenced) and the environment stamp (plugin version, framework
spec, OS, Claude Code version) to **draft** a complete GitHub issue —
concise title + sectioned body matching
[`.github/ISSUE_TEMPLATE/bug_report.md`](../.github/ISSUE_TEMPLATE/bug_report.md).

The draft is URL-encoded into a `?title=&body=` GitHub `issues/new` URL.
The plugin prints a preview of the title + body in chat so you can
sanity-check before clicking through. Then it prints the link. You open
it, the GitHub form opens prefilled, you add anything that's missing,
and click Submit.

**Honest framing:** the plugin never submits the issue itself; it never
includes secrets it sees in the conversation (fragments matching
`token|secret|key|password|api[_-]?key` are replaced with `(redacted)`).
The drafted title and body are an LLM proposal you can edit on github.com.

### 2. In-product `/aidoc-flow:feedback`

Same shape as `bug-report` but lands on
[`.github/ISSUE_TEMPLATE/feedback.md`](../.github/ISSUE_TEMPLATE/feedback.md).
Use this for feature ideas, what worked / didn't work, and questions
that aren't bugs. The classifier on the GitHub side may further route
your feedback during triage.

### 3. Direct on GitHub

If you already know what's broken and you're comfortable with GitHub,
the fastest path is the Issues page. Click "New issue" and pick the
template that matches your intent:

- [Bug Report](https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=bug_report.md) — something is broken
- [Feedback](https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=feedback.md) — idea, comment, question

The templates carry the same section structure the in-product commands
draft into, so the issue reads the same whether you arrive via the
plugin or directly.

### 4. Web-site `/support` (`aidoc-flow.io/support`)

Three sections on one page:

- **Report a bug** — clicks through to GitHub Issues (zero-spam-exposure
  on the website; GitHub auth handles abuse).
- **Share feedback** — clicks through to GitHub Issues, feedback template.
- **Contact us** — for visitors who don't have a GitHub account or have
  a question that doesn't fit a template. The Contact-us form is a
  Google Form; submissions land in a Google Sheet that the AI Team
  polls via Google Drive MCP every ~15 minutes.

The Contact-us channel routes through the AI Team's intake workflow —
see
[`../../operations/docs/SUPPORT_INTAKE.md`](../../operations/docs/SUPPORT_INTAKE.md)
for the full design. Short version: a two-stage classifier (Python
prefilter then Claude Haiku 4.5 LLM) drops spam, then the AI Team
drafts a substantive reply for the maintainer to review and notifies
the maintainer via internal Slack + internal Telegram bot + an
optional Gmail draft. No spam reaches the maintainer's IM. No reply
goes out without human review (the Google Forms confirmation page is
the visitor's only auto-acknowledgment; founder composes a fresh
Gmail per reply).

## Architecture (live since 2026-06)

The Contact-us channel on `aidoc-flow.io/support` is a Google Form;
submissions auto-land in a linked Google Sheet that the AI Team's
`customer-success-manager` seat polls via Google Drive MCP every ~15
minutes. A two-stage classifier (Python prefilter → Claude Haiku 4.5
LLM) drops spam without notifying the maintainer; non-spam classes
produce a substantive-reply draft in `ops/inbox/` plus a notification
fan-out to internal Slack, internal Telegram bot, and an optional
Gmail draft for the maintainer to review.

Design and implementation are documented at:

- [`../../operations/docs/SUPPORT_INTAKE.md`](../../operations/docs/SUPPORT_INTAKE.md)
  — operations-side intake design (Forms→Sheet schema, classifier
  cascade, per-class routing, escalation rules, notification fan-out).
- [`../../operations/ops/iplans/IPLAN-0009_support-intake-implementation.md`](../../operations/ops/iplans/IPLAN-0009_support-intake-implementation.md)
  — the implementation plan (steps A4–C3, claim ledger, review log).
- [`../../operations/ops/iplans/IPLAN-0008_support-channels.md`](../../operations/ops/iplans/IPLAN-0008_support-channels.md)
  — the original cross-repo coordination IPLAN (Phase 1 design;
  superseded by IPLAN-0009 for Phase 2).
- [`../../business/docs/SUPPORT_STRATEGY.md`](../../business/docs/SUPPORT_STRATEGY.md)
  — channel × audience × SLA × pricing-tier policy.

There are no contractual SLAs — the intent windows in
[`../../business/docs/SUPPORT_STRATEGY.md`](../../business/docs/SUPPORT_STRATEGY.md)
§3 are best-effort. If you need a contact channel and don't have
GitHub, the form is the canonical path.

## What to expect after you submit

| Channel | When you'll hear back |
|---|---|
| GitHub Issues (any of channels 1–3) | Triage queue; aiming for a substantive reply per the windows in [`../../business/docs/SUPPORT_STRATEGY.md`](../../business/docs/SUPPORT_STRATEGY.md) §3 (bug: 2 business days; feature: 5 business days; chat: 3 business days) |
| Web-site Contact-us (Google Form) | Google Forms confirmation page is the visitor's only ack; substantive reply per the same windows (commercial inquiries `sales` class targeted at 1 business day) |

These are intent windows, not contractual SLAs. The OSS project runs
on best-effort; paid-tier SLAs are documented separately when paid
tiers ship.

## Out of scope (channels that don't exist today)

The following are explicitly NOT support channels — by design:

- **No public Slack workspace.** Internal Slack is a notification sink
  for the maintainer; it's not a place for external users to drop in.
- **No public Telegram bot.** Internal Telegram bot serves the same
  notification role; it's not public.
- **No `mailto:` link** anywhere on the public surface. Email crawlers
  harvest these and turn maintainer inboxes into spam.
- **No status page** (`status.aidoc-flow.io`) yet. Useful when uptime
  is meaningful; not now (no hosted service to monitor).

When any of these become useful enough to set up, the change ships
through a normal IPLAN — not unilaterally added to a doc.
