# Software Development Practice

Operational guidelines for software work — planning, discussion, implementation, and review.
These enact the concepts in [Software Development Principles](software-principles.md) and
DevFlow's Philosophy.

## Understand the product

- What is the product's premise and goal?
- Who are its target users?
- Is it already in production?
- Does it have existing users?

## Understand the task

- How does it fit the project?
- What is its goal, and who benefits?
- What concrete example demonstrates the desired outcome?
- What observable result would show that the task is done?
- Which requirements and constraints are established, and which are assumptions?

## Understand the system

- Understand existing responsibilities and terminology before proposing new ones.
- Identify the relevant inputs, outputs, dependencies, and responsibility owners.
- Understand the reasons behind existing design choices before replacing them.
- Consider how the proposed change affects the surrounding system.

## Focus on essential complexity

- What complexity is inherent in the problem?
- Why is the proposed solution necessary?
- What is the simplest solution that satisfies the goal and its actual constraints?
- Reuse existing mechanisms where they fit.

## Design for understanding and change

- Can another developer easily find, understand, test, and change this behavior?
- Give each abstraction a clear purpose and responsibility.
- Keep implementation details behind the boundary that owns them.

## Work in small feedback loops

- Identify the uncertainty that matters most to the next decision.
- Take the smallest useful step that tests it.
- Define the behavior being verified and where its outcome can be observed.
- Choose checks that demonstrate the intended outcome.
- For new capabilities, prefer a small working flow through the system that exposes
  integration problems early.
- Check the result before building further on the assumption.
