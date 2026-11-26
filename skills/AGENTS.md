# Writing skills in this repo

## Setup

Some skills discover their setup on first use instead of hard-coding it. That setup lives with what it
depends on: the machine or a repository.

For both:

- **The skill holds instructions only**: the goal, what is easy to miss, and a done condition the agent
  can verify on its own. It names no tool, path or format as required; examples say "for example".
  The setup holds the rest, so a new or changed tool means a setup run, not a change to the skill.
- **Only what an agent would miss**: leave out anything an agent finds by looking, and write down what
  setup had to discover the hard way.

### Depends on the machine

App data paths, local stores, file formats that change between versions.

- **Folder**: `~/.agents/dev-env/<skill-name>/`. `setup.sh` replaces installed skill folders on every
  update, so setup kept inside the skill folder is lost. `setup.sh` leaves `~/.agents/dev-env/` alone.
- **The folder holds what setup built**, in whatever form fits, and a `README.md` index: what is
  covered, how to run it, what it can do, and when the done condition last held.
- **SKILL.md** names the folder and gives the agent three steps: read the index before use, run setup
  when it is missing, and redo setup for the part that no longer works.

`skills/thread-locator` is the reference example.

### Depends on a repository

How to run its product, its conventions. This setup belongs in the repository itself, such as its
README or agent instructions, where everyone who works in it finds it.

- **The user decides**: the skill proposes the addition to the user, showing what it would add and
  where, and writes it once they agree.
