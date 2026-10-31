# dev-env

My coding agent setup. The same one line sets up a machine or a cloud environment:

```bash
curl -fsSL https://raw.githubusercontent.com/enekesabel/dev-env/main/setup.sh | bash
```

Run it again to update everything. It installs from `main`, so push changes first.

## What it installs

- **DevFlow**: cloned to `~/.agents/dev-flow`, the one shared copy. The `devflow` skill points at it, so
  any harness can start the Coordinator.
- **Skills**: everything in [`skills.txt`](skills.txt), into `~/.agents/skills`, with Claude linked to
  that folder. It only touches skills on the list, and never deletes anything else.
- **Harness extras**: anything only one harness understands, in its own section of
  [`setup.sh`](setup.sh). That section runs only if the harness is installed. Claude's sets the advisor
  and output style, and installs the DevFlow plugin from the shared copy.

## Add a skill

- **Mine**: add a folder to [`skills/`](skills/) and push.
- **Someone else's**: add it to [`skills.txt`](skills.txt) and push.

Then run the setup again.

## Try a change to a skill

Replace the installed copy with a link to your working copy:

```bash
rm -rf ~/.agents/skills/<name>
ln -s ~/path/to/skills/<name> ~/.agents/skills/<name>
```

Running the setup again removes the link and restores the published version, and your working copy
stays as it is. This restores every override at once. To work on DevFlow itself, link
`~/.agents/dev-flow` to your checkout the same way.

## Cloud

Use the line above as the environment's setup script. Cloud sessions start from a snapshot that can be
about a week old, so the setup adds a session start hook that refreshes DevFlow and the skills in each
cloud session. Settings and plugins update when the snapshot is rebuilt. The hook does nothing locally,
so it can't restore a skill you're experimenting with.
