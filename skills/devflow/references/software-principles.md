# Software Development Principles

Software-specific theory. Each concept is established in literature and extends DevFlow's
Philosophy into the software domain.

## Value Identification

Before building, understand what the work creates and for whom. At the product level: what is
the premise, who are the users, what problems does it solve? At the task level: how does this
fit the project, what concrete outcome demonstrates it works, and which constraints are real
versus assumed?

Without this clarity, the system grows without becoming more valuable. Value framing is
convergence at the start — the first act of deciding what matters, before the space of
possibilities expands. Being present for this framing means the constraints passed through you,
not reconstructed after the fact.

## Domain Discovery

Software models a problem domain. The vocabulary the code uses should reflect the problem, not
the implementation. Understanding the domain — its concepts, boundaries, and relationships —
is what makes the code navigable and the team aligned.

The domain is the system the code models. Understanding its relationships — what depends on
what, where boundaries live — determines whether a change in one place stays local or
propagates. Before proposing new responsibilities or terminology, understand what already exists
and why.

## Strategic Design

Architecture decisions shape the system at a scale above individual modules. What components
exist, what their responsibilities are, how they integrate, and what to build versus reuse.

These decisions are convergence acts — commitments the system will defend over time. They should
focus on the complexity inherent in the problem and let the accidental complexity recede behind
boundaries. The simplest solution that satisfies the goal and its actual constraints is the one
that leaves the least accidental weight behind.

## Information Hiding

Each module hides a design decision. The interface reveals what others need; the implementation
hides what might change. This is how abstraction manages complexity — separating what matters
from what does not.

When boundaries hide what might change, the feedback loop tightens: each module can be
understood, tested, and changed without understanding everything around it. The measure is
whether another developer can easily find, understand, test, and change the behavior.
