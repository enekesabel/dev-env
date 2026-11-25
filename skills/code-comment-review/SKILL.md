---
name: code-comment-review
description: Use when reviewing, pruning or cleaning up the code comments in a diff, a file or a folder.
---

Sort every code comment in scope into one of the five kinds below and act on it. For a diff, the scope is the comments it adds or changes.

Change comments only. Code, tests and config stay as they are; when a comment reveals a bug, report the bug.

**When in doubt, keep the comment.** A comment deleted by mistake takes its reason with it, and the code cannot give it back; a comment kept by mistake costs one line. In one cleanup, reviewers restored 42 deleted comments on one PR and 12 on another, each because it gave a reason or said what a declaration means.

| Kind | Action |
| --- | --- |
| Says what a declaration means, or gives a reason | Keep |
| A tool directive with its reason | Keep |
| Records a decision | Keep, unless it passes the ADR tests |
| Excuses a workaround | Link the issue that tracks it, or propose one |
| Restates the code, or is stale | Delete |

## Keep

### Says what a declaration means, or gives a reason

The type gives the shape; the comment gives the meaning: units, ranges, invariants, what an empty value means. A reason says why a line is odd, why the obvious alternative fails, or what breaks if it changes.

```ts
/** Minor units: 1999 is 19.99 in the invoice's currency. */
amount: number

// Null until the customer confirms their email address.
verifiedAt: Date | null

// Sort before deduplicating: the API returns duplicates out of order.
const unique = dedupe(sortBy(items, 'id'))
```

### A tool directive with its reason

Lint, type-check and mutation-testing suppressions, for example. Keep them. When one lacks its reason, add the reason if the code or its history shows it; otherwise report it.

```ts
// eslint-disable-next-line no-await-in-loop -- the API allows one request per connection at a time
```

### Records a decision

Check it against the tests in the `adr` skill. If it fails any of them, keep the comment: a local decision belongs beside its code. If it passes, propose an ADR with that skill, and once the user approves the ADR, replace the comment with a link to it.

## Act on

### Excuses a workaround

It says hack, temporary, or until something is fixed. Link the issue that tracks the proper fix. If none exists, propose one to the user with a title and a one-line body, then link it once it is filed. Keep the reason in the comment.

```ts
// HACK: temporary
await sleep(500)
```

```ts
// Upstream drops events sent within 500 ms of connecting; remove once <issue link> is fixed.
await sleep(500)
```

### Restates the code, or is stale

Delete a comment when a name, a type or the code itself already says the same thing, or when it no longer matches the code. If a stale comment holds a reason that still applies, correct it instead.

```ts
// Increment the retry count
retries++

// Throws if the user is not found
function findUser(id: string): User | undefined
```

## Done

Every comment in scope has a kind. Report what you deleted, what you changed, the comments you kept because you were unsure, and the issues and ADRs you propose.
