---
name: product-surfaces
description: List a product's consumers and the surfaces where they meet it.
disable-model-invocation: true
---

# Product surfaces

Look at a product from the outside: who consumes it, and where they meet it. Later steps will map a
set of changes onto these surfaces; they are not written yet.

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

## Steps

1. List the consumers and surfaces, following
   [references/consumers-and-surfaces.md](references/consumers-and-surfaces.md).

Then show the list to the user and discuss it. Their corrections come before anything else.
