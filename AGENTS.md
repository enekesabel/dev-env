## Communication protocol
- Make every reference explicit and followable. When you refer to an issue, ticket, pull request, thread, document, or similar item, link it with a URL or URI I can open. If you have no such link, give its title and any identifier.
- Never refer to an item by number or ID alone, even if I do. On its first mention in a message, give its number and title, e.g. `#27 "Skeleton trunk: repo, lanes, boundaries, CI"`. After that, use a short descriptive name such as "the skeleton trunk PR".

## Delegating to sub-agents or background agents
- Delegate work to sub-agents or background agents when it helps.
- Before dispatching, recommend a model and effort level for each, including when you would use the default, and wait for my approval. One approval can cover a batch of agents dispatched together.

## When documentation and code disagree
- When a repository's documentation and its existing code disagree, follow the conventions used in the existing code, and in your final reply point out each inconsistency you found between the documentation and the code.

## Running tests and builds locally
- First check where you are running. On my own machine, several agents share it, so keep runs small. In a cloud sandbox or CI, where the machine is yours alone, heavy runs are fine. If you can't tell, assume my machine.
- On my machine, run only the tests that give you the feedback you need or prove the point at hand, such as the affected test file or package, not the whole repository. Leave heavy runs to CI: full suites, end-to-end matrices, mutation testing, builds of every app, and runs that bypass a build cache. Limit the parallelism of anything that runs many packages or workers at once. Do a heavy run here only when I ask for it.
- Stop every dev server, watcher or background process you start before you hand back.
- In your report, say which checks you ran and which you left to CI.
