---
name: product-surface-review
description: Review a set of changes by the product surfaces they change and what their consumers will notice.
disable-model-invocation: true
---

# Product surface review

Review a set of changes from the outside: which surfaces of the product they change, and what the
consumers on each surface will notice. The input is a before and an after state of the product, such
as a commit range, a branch against its base or a pull request. When the user gives none, ask for one.

## Words

**Product**:
What the user's team builds and ships. It can span several repositories.

**Consumer**:
A person, an agent or another piece of software that comes to the product with a goal and meets it
on a surface. A consumer would notice a change on that surface without reading the code.

**Surface**:
A place where a consumer meets the product: something they call, run, read or receive. One surface
per interface the consumer relies on, such as a UI, an API, a CLI, each message channel, a file
format or a set of docs. An interface is one specific thing the product exposes: two separate apps
in a browser are two interfaces. Group by interface alone: places that share an interface are one
surface, whatever their consumers, entry points or features. A third party's interface is a surface
of its own when consumers meet it as a step in a user flow the product owns.

**Behind the curtain**:
The changed files that made no change on any surface.

## Steps

1. Read the changes between the two states and find the surfaces they affect.
2. For each affected surface, name the consumers who meet it, and show each change on it, before and
   after, with the `show-me` skill.
3. Under each change, list the files that made it, tests included, in a collapsible block: one line
   per file, with links to the ranges that made this change. Link on the repository's host, pinned
   to the commit: the after state, or the before state for removed lines. Without a host, write
   `path:line`.

   ```markdown
   <details>
   <summary>Files (2)</summary>

   - [src/home/page.ts:12-40](<link>)
   - [tests/home.test.ts:8-31](<link>)

   </details>
   ```

4. Close with what is behind the curtain, in the same collapsible form, grouped as fits the changes.
   Leave it out when it is empty.

The review is done when every changed file sits under a change or behind the curtain.
