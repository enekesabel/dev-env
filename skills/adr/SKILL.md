---
name: adr
description: Use when deciding whether to record an architecture decision, drafting an ADR, or replacing or retiring a decision.
---

Work on ADRs with the `mattpocock:domain-modeling` skill, and add these rules.

## When to write one

Write an ADR only for a decision that passes the three tests of `mattpocock:domain-modeling`, with its second test, "surprising without context", replaced by this one: its reason cannot be read from the code. The first and third stand as that skill states them. A decision that fails a test goes where it belongs instead: a local reason in a comment beside the code, a migration plan in the issue.

## What it holds

An ADR holds the decision, the reason, the options rejected and the consequences, and names each thing by its glossary term. Leave out detail that the code, the docs, the issue or git already hold and keep current, such as API names, versions and migration steps.

To spot such detail, ask of each sentence whether it would still be true after the code is rewritten under the same decision. If it would not, cut it, or link to the code or doc that states it. The test finds detail only: keep the reasons and trade-offs that drove the choice.

In each example the decision, the reason and the rejected option stay, and only the detail goes.

Before:

> Billing no longer calls `OrderService.getOrder()`: it learns about an Order only from Ordering's events, so Ordering can change how it stores Orders without breaking Billing. Eleven files under `billing/` imported Ordering's internals; PR #412 replaced them with `OrderPlaced` handlers in `InvoiceProjector`. We rejected direct calls, which made Billing fail whenever Ordering was down.

After:

> Billing learns about an Order only from Ordering's events, so Ordering can change how it stores Orders without breaking Billing. We rejected direct calls, which made Billing fail whenever Ordering was down.

Before:

> Invoices are rendered to PDF on the server with headless Chromium (checked on version 126), so every Customer gets the same document whatever their device. We rejected rendering in the browser, where layout differed between devices. The server image grows by about 180 MB.

After:

> Invoices are rendered to PDF on the server, so every Customer gets the same document whatever their device. We rejected rendering in the browser, where layout differed between devices. The cost is that the server does the rendering work.

## Approval

Show the user the complete ADR and wait for an explicit yes to it before you commit. Agreement with a plan does not count. One yes covers a replacement: the new ADR, the old one's status and its move.

## How to change or retire one

Edit an ADR in place when the decision stays the same: clearer wording, a renamed glossary term, a fixed link, detail cut out.

When the decision itself changes, even in one choice, reason or rejected option, write a new ADR that states the whole decision now in force, with `status: accepted` and `supersedes: ADR-NNNN`. Done when the new ADR reads alone: a reader learns the decision without opening another ADR.

Retire the old one: set its status to `superseded by ADR-NNNN`, or to `deprecated` when nothing replaces it, and `git mv` it into a `retired/` folder beside the ADRs, its text otherwise unchanged. Every ADR outside `retired/` is then in force. Its number and file name stay, so citations by number stay right; update every link to its old path in the same change.
