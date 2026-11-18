# Writing skills in this repo

## Machine setup

Some skills depend on what is installed on the machine: app data paths, local stores, file formats that
change between versions. Such a skill discovers that setup on first use and keeps it, instead of
hard-coding it.

- **Folder**: `~/.agents/dev-env/<skill-name>/`. `setup.sh` replaces installed skill folders on every
  update, so setup kept inside the skill folder is lost. `setup.sh` leaves `~/.agents/dev-env/` alone.
- **The skill holds instructions only**: the goal, what is easy to miss, and a done condition the agent
  can verify on its own. It names no tool, path or format as required; examples say "for example".
  Everything machine-specific is built on the machine, so a new or changed tool means a setup run, not
  a change to the skill.
- **The folder holds what setup built**, in whatever form fits, and a `README.md` index: what is
  covered, how to run it, what it can do, and when the done condition last held.
- **SKILL.md** names the folder and gives the agent three steps: read the index before use, run setup
  when it is missing, and redo setup for the part that no longer works.
- **Only what an agent would miss**: leave out anything an agent finds by looking, and write down what
  setup had to discover the hard way.

`skills/thread-locator` is the reference example.
