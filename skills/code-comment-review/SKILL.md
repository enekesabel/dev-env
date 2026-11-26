---
name: code-comment-review
description: Use when reviewing, pruning or cleaning up the code comments in a diff, a file or a folder.
---

Sort every code comment in scope into one of the kinds below and act on it. For a diff, the scope is the comments it adds or changes.

Change comments only. When the fix is a code change, such as a rename, a type or a test, recommend it and keep the comment until it lands. When a comment reveals a bug, report the bug.

**When in doubt, keep the comment.** A comment deleted by mistake takes its reason with it, and the code cannot give it back; a comment kept by mistake costs one line. In one cleanup, reviewers restored 42 deleted comments on one PR and 12 on another, each because it gave a reason or said what a declaration means.

| Kind | Action |
| --- | --- |
| Gives a reason or a meaning no name, type or test can carry | Keep |
| A tool directive with its reason | Keep |
| Records a decision | Keep, unless it passes the ADR tests |
| Says what a name, a type or a test could say | Recommend that code change |
| Excuses a workaround | Propose the fix |
| Restates the code, narrates its history, or is stale | Delete |

## Keep

### Gives a reason or a meaning no name, type or test can carry

Usually the cause is outside the code, and no test can reproduce it at a sensible cost: a mocked dependency would only restate the assumption.

Keep:

```ts
// Read from the primary: replicas lag up to 2 s, and this runs right after the write.
const order = await primary.orders.find(id)
```

### A tool directive with its reason

Lint, type-check and mutation-testing suppressions, for example. When one lacks its reason, add the reason if the code or its history shows it; otherwise report it.

Keep:

```ts
// eslint-disable-next-line no-await-in-loop -- the API allows one request per connection at a time
```

### Records a decision

Check it against the tests in the `adr` skill. If it fails any of them, keep the comment: a local decision belongs beside its code. If it passes, propose an ADR with that skill, and once the user approves the ADR, replace the comment with a link to it.

## Act on

### Says what a name, a type or a test could say

Units, ranges, what an empty value means, or why the obvious alternative fails. Once the recommended change lands, delete the comment.

Bad:

```ts
// Seconds, not ms: the payment provider sends Unix time.
paidAt: number

// Not setInterval: a tick that runs long would pile up calls.
schedule(tick)
```

Good: `paidAt: UnixSeconds`, and a test named "a slow tick does not overlap the next", with no comments.

### Excuses a workaround

It says hack, temporary, or until something is fixed. Propose the fix. When the fix is out of scope, propose an issue with a title and a one-line body. Until the fix lands, the comment gives the reason and links the issue.

Bad:

```ts
// HACK: temporary
await sleep(500)
```

Good, when the fix is out of scope:

```ts
// Upstream drops events sent in the first 500 ms; remove once https://github.com/example/sdk/issues/123 is fixed.
await sleep(500)
```

### Restates the code, narrates its history, or is stale

Delete a comment when the code already says the same thing, when it tells what changed or moved, or when it no longer matches the code. Git and the PR keep the history. If a stale comment holds a reason that still applies, correct it instead. If a history comment also gives a reason, drop the history and sort the reason on its own.

Bad:

```ts
// Get the user by ID
function getUserById(id: string) {

// Moved from utils.ts and switched to the new client
export function fetchUser(id: string) {

// Throws if the user is not found
function findUser(id: string): User | undefined
```

## Done

Every comment in scope has a kind. Report what you deleted, what you changed, the code changes you recommend, the comments you kept because you were unsure, and the issues and ADRs you propose.
