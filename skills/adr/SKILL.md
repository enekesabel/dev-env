---
name: adr
description: Use when deciding whether to record an architecture decision, drafting an ADR, or replacing or retiring a decision.
---

Work on ADRs with the `mattpocock:domain-modeling` skill, and add these rules.

## The repository's rules

The repository decides where ADRs live, how a replaced or retired ADR is kept, and who approves one. Find its rules before you write, for example in a guide beside the ADRs or in the root guidance, and follow them.

## When to write one

Write an ADR only for a decision that passes the three tests of `mattpocock:domain-modeling`, with its second test, "surprising without context", replaced by this one: the decision itself cannot be read from the code. The first and third stand as that skill states them. A decision that fails a test goes where it belongs instead: a local reason in a comment beside the code, a migration plan in the issue.

## What it holds

An ADR holds the decision, the reason, the options rejected and the consequences, and names each thing by its term in the repository's glossary. Leave out API names and signatures, file counts, versions, sizes, PR numbers and migration steps: the code, the docs, the issue and git hold those and keep them current.

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

Before:

> Each Invoice stores its amount with the currency it was billed in. We rejected one base currency converted on read, because a later exchange rate would change an Invoice already sent. The migration runs in four steps: add the `currency` column, backfill it from the Customer's country, switch reads to it, then drop `amount_usd`.

After:

> Each Invoice stores its amount with the currency it was billed in. We rejected one base currency converted on read, because a later exchange rate would change an Invoice already sent.

## How to change or retire one

To change a decision, even by one sentence, write a new ADR that states the whole decision now in force, and mark the old one replaced the way the repository does. Done when the new ADR reads alone: a reader learns the decision without opening another ADR.

To drop a decision with nothing in its place, mark it retired the way the repository does.
