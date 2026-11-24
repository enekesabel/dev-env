---
name: adr
description: Use when recording, changing or retiring an ADR.
---

Work on ADRs with the `mattpocock:domain-modeling` skill, and add these rules.

## The repository's rules

The repository decides where ADRs live, how a replaced or retired ADR is kept, and who approves one. Find its rules before you write, for example in a guide beside the ADRs or in the root guidance, and follow them. Where it says nothing, follow `mattpocock:domain-modeling`.

## When to write one

Apply the three tests of `mattpocock:domain-modeling`, reading "surprising without context" as "cannot be read from the code". A decision that fails a test goes where it belongs instead: a local reason in a comment beside the code, a migration plan in the issue.

## What it holds

An ADR holds the decision, the reason, the options rejected and the consequences, and names each thing by its term in the repository's glossary. Leave out API names and signatures, file counts, versions, sizes, PR numbers and migration steps: the code, the docs, the issue and git hold those and keep them current.

Test each sentence: keep it only if it would still be true after the code is rewritten under the same decision.

Before:

> Billing no longer calls `OrderService.getOrder()`. Eleven files under `billing/` imported Ordering's internals; PR #412 replaced them with `OrderPlaced` handlers in `InvoiceProjector`.

After:

> Billing learns about an Order only from Ordering's events, so Ordering can change how it stores Orders without breaking Billing. We rejected direct calls, which made Billing fail whenever Ordering was down.

Before:

> Invoices are rendered to PDF on the server with headless Chromium (checked on version 126). The server image grows by about 180 MB.

After:

> Invoices are rendered on the server, so every Customer gets the same document whatever their device. We rejected rendering in the browser, where layout differed between devices. The cost is a browser engine in the server image.

Before:

> The migration runs in four steps: add the `currency` column, backfill it from the Customer's country, switch reads to it, then drop `amount_usd`.

After:

> Every amount of Money carries its currency, so an Invoice is billed in the Customer's currency. We rejected one base currency converted on read, because rates change after an Invoice is sent.

## How to change or retire one

To change a decision, even by one sentence, write a new ADR that states the whole decision now in force, and mark the old one replaced the way the repository does. Done when the new ADR reads alone: a reader learns the decision without opening another ADR.

To drop a decision with nothing in its place, mark it retired the way the repository does.
