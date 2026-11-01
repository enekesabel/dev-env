---
name: review-pr
description: Review a PR, branch or diff with the Standards, Spec and ponytail combo. Use whenever the user asks for a code review.
---

Every review combines two skills:

- `code-review` (Matt Pocock): the **Standards** and **Spec** axes.
- `ponytail-review`: what to cut or simplify, applied alongside Standards.

## Reviewer

Run the reviewers on the latest GPT Sol model at `xhigh` effort. If you can't start that model, ask
the user which model and effort to use instead. Don't pick a fallback yourself.

## Split

Decide from the size and complexity of the change:

- **Small or simple:** one reviewer covers Standards, Spec and ponytail.
- **Otherwise:** two reviewers in parallel. One covers **Spec** only. The other covers **Standards
  plus ponytail**.

When split, tell each reviewer to run only its own axes, since `code-review` would otherwise start
its own sub-agents for both.
