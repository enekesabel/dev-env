# Architecture document

An architecture document captures what the code cannot easily show: the system's structure at
a level above any single codebase. Document the Context and Containers. Components are
inferable from code; documenting them adds maintenance burden for limited value.

The document is the normalized source of truth: state each fact once, in one place, and refer
to other facts by name. Whatever can be derived from it, such as the visualization, stays out
of it.

Leave scenarios out of the document: architecture is structure, scenarios are behavior and
change with every feature. Use them to test the picture instead. A scenario that cannot be traced
through the containers and the relevant lenses means the picture is incomplete.

## Evidence

Write down what actually runs, not what the code implies. Mark each element and connection
**verified** when backed by a source you read that defines or performs it (deployment or
infrastructure config, or the code making the call), and **inferred** when deduced from
indirect signals (names, comments, conventions) or from a part whose defining source you
could not see.

## Template

Angle brackets are placeholders. Every claim gets its own `Evidence:` line, and every
`<evidence>` is either ``verified: `<path>` ``, the source you read that defines or performs
it, or `inferred: <why>`, the indirect signal it rests on.

```markdown
# Architecture

## Context

<What the system does, in one or two sentences: the premise, not the feature list.>

### Actors
- **<actor>**: <role>
  - Goal: <what they come to the system for>
  - Evidence: <evidence>

### External systems
- **<system>**
  - Provides: <the capability the system relies on it for>
  - Evidence: <evidence>

## Containers

### <container>
- Responsibility: <what it owns>
- Technology: <what it is built with, the same in every environment>
- Evidence: <evidence>

## Communication
- **<initiator> → <target>**
  - Flows:
    - → <what moves with the call>
    - ← <what comes back>
  - Evidence: <evidence>

## Environments

### <environment>
- Purpose: <what it is for>
- Evidence: <evidence>
- Containers:
  - **<container>**: <how it runs here>
    - Deployment node: <the specific instance it runs on>
    - Evidence: <evidence>
- External systems:
  - **<system>**: <how it is represented here>
    - Evidence: <evidence>
```

A container's Technology holds only what is the same in every environment; leave it out when
nothing is.

Communication lists every connection that involves a container. Either end can be an actor, an
external system, or a container. A connection is one initiator and one target. Its flows are
the data it carries: `→` moves with the initiator's call, `←` comes back to it. List each
connection once, grouped by its initiator: actors first, then external systems, then
containers, each in the order the document defines them. Within one initiator, order the
targets the same way.

Every environment lists every container and every external system. A deployment node is the
specific instance a container runs on (C4), such as a cluster, a server, or a project, not a
kind of technology; containers that share an instance use the same name. A container that does
not run in an environment says so and has no deployment node.

Describe how a container runs in an environment by what actually runs there, such as an image
or a managed service, without repeating its Technology or its deployment node.

See [architecture-document-example.md](architecture-document-example.md) for a filled-in
example.

## Before you finish

Check the document against itself. A failed check is a finding to raise with the user, with
what you found and where, not something to resolve on your own.

- Every actor, external system and container takes part in at least one connection.
- Every connection has an actor, external system or container at each end.
- Every element and connection carries evidence, verified or inferred.
- Every environment lists every container and every external system.
