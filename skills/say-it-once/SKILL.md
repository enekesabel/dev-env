---
name: say-it-once
description: Use when writing or editing an AGENTS.md, a skill or a doc, or deciding where a rule, a reason or a fact belongs.
---

Write with the `mattpocock:writing-for-agents` skill, and add these rules.

## Where each statement lives

Say each thing once, in the one place that keeps it true:

| Kind of statement | Where it lives |
| --- | --- |
| What the code does | Code, types, tests. Nowhere else. |
| A rule a check enforces | The check's config and its error message; guidance links to it |
| A rule nothing enforces yet | The `AGENTS.md` of the narrowest folder it applies to, with its reason on the same line |
| Why one line is odd | A code comment |
| Why the architecture has this shape | An ADR |
| How to do a rare task | A skill or a doc beside the thing |
| What moved when | Git and the PR |

Before you add a line to a doc, find its row. If the row points elsewhere, put the statement there and link to it, or leave it out.

## The reason goes on the same line

Every rule nothing enforces, and every comment, carries its reason in the same sentence or bullet. The reason is what lets a later reader delete the line once it no longer holds. Without it, nobody can tell whether the line still matters, so it stays for good. A reason kept further down the file, or only in the PR, is lost the first time the line moves.

## Examples

The names and paths are made up.

An `AGENTS.md` line without its reason, then with it:

> - Never import from `legacy/`.

> - Import from `billing/`: `legacy/` is deleted once its last caller moves.

A retelling of code, replaced by a link:

> Outbound calls retry three times, after 200, 400 and 800 ms, and give up on any 4xx response.

> Retry outbound calls with `retry()` in `http/retry.ts`; its tests give the schedule.

A rule a check enforces, restated in guidance:

> - Keep functions under 50 lines.

After: the line is gone. The lint config enforces the limit, and its error message tells the agent when a function breaks it.

A comment that restates a name:

```ts
// Get the user by ID
function getUserById(id: string) {
```

After: the comment is gone, or replaced by what the name cannot say:

```ts
// Reads the replica: a user created in the last second may be missing.
function getUserById(id: string) {
```
