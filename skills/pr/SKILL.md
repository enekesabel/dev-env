---
name: pr
description: Use when writing a PR body.
---

Write the PR body with the `mattpocock:pr` skill.

Decide whether the change gets a diagram. It gets one when a reviewer would grasp it faster from a picture: it moves data between components, crosses a boundary, or changes a schema. A small or mechanical change, such as a typo fix, a rename or a dependency bump, goes without one; say so in one line of your reply.

When it gets one, draw it yourself with the `pr-lens` skill and put the walkthrough in the PR description, following that skill's steps for attaching to a pull request. Keep the drawing local: push a canvas only when the user asks for one.

If the PR needs other images, upload them with the `pr-screenshots` skill and use the image lines it prints.
