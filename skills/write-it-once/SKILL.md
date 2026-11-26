---
name: write-it-once
description: Use when writing or editing an AGENTS.md, a skill or a doc, or deciding where a rule, a reason or a fact belongs.
---

Write with the `mattpocock:writing-for-agents` skill, and add these rules.

## Where each statement lives

Before you write anything into an `AGENTS.md`, a skill or a doc, find its kind in this table and put it where that row says.

| Kind of statement | Where it lives |
| --- | --- |
| What the code does | Code, types, tests. Nowhere else. |
| A rule a check enforces | The check's config and its error message; guidance links to it |
| A rule nothing enforces yet | The `AGENTS.md` of the narrowest folder it applies to, with its reason on the same line |
| Why one line is odd | A code comment |
| Why the architecture has this shape | An ADR |
| How to do a rare task | A skill or a doc beside the thing |
| What moved when | Git and the PR |

## The reason goes on the same line

Put the reason on the same line as its rule or comment. A reason kept further down the file, or only in the PR, is lost the first time the line moves. A comment that says what a declaration means is its own reason.

## Examples

The names and paths are made up.

An `AGENTS.md` line without its reason, and with it:

Bad:

> - Never import from `legacy/`.

Good:

> - Import from `billing/`: `legacy/` is deleted once its last caller moves.

A retelling of code, and a link to the code:

Bad:

> Outbound calls retry three times, after 200, 400 and 800 ms, and give up on any 4xx response.

Good:

> Retry outbound calls with `retry()` in `http/retry.ts`; its tests give the schedule.

A rule a check enforces, restated in guidance:

Bad:

> - Keep functions under 50 lines.

Good: no line. The lint config enforces the limit, and its error message tells the agent when a function breaks it.

A comment that restates a name:

Bad:

```ts
// Get the user by ID
function getUserById(id: string) {
```

Good: no comment, or one that says what the name cannot:

```ts
// Reads the replica: a user created in the last second may be missing.
function getUserById(id: string) {
```
