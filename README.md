# dev-env

My coding agent setup. The same one line sets up a machine or a cloud environment:

```bash
curl -fsSL https://raw.githubusercontent.com/enekesabel/dev-env/main/setup.sh | bash
```

Run it again to update everything. It installs from `main`, so push changes first.

## What it installs

- **DevFlow**: cloned to `~/.agents/dev-flow`, the one shared copy. The `devflow` skill points at it, so
  any harness can start the Coordinator.
- **Instructions**: [`AGENTS.md`](AGENTS.md), to `~/.agents/AGENTS.md`, the one shared copy.
- **Skills**: [`skills.txt`](skills.txt) is the canonical list. Unmarked lines install into
  `~/.agents/skills`, with Claude linked to that folder. Prefixed lines become namespaced plugins,
  such as `matt:tdd`, in each installed harness (see below).
- **Harness extras**: anything only one harness understands, in its own section of
  [`setup.sh`](setup.sh). That section runs only if the harness is installed. Claude's imports the
  instructions into `~/.claude/CLAUDE.md`, sets the output style, and installs the DevFlow
  plugin from the shared copy. Codex's links `~/.codex/AGENTS.md` to the instructions. Claude,
  Codex and Cursor each install the scoped plugins in their own section.

Codex and Cursor read `~/.agents/skills` themselves. Cursor doesn't read the shared instructions yet.

## Add a skill

- **Mine**: add a folder to [`skills/`](skills/) and push.
- **Someone else's**: add it to [`skills.txt`](skills.txt) and push.

Then run the setup again.

Each line in [`skills.txt`](skills.txt) has this form:

```text
[<prefix>=]<github-source> <skill>...
```

`*` selects every skill in the source. Without a prefix, installation works as before. For example:

```text
enekesabel/dev-env *
matt=mattpocock/skills tdd pr code-review
```

Several lines can share a prefix; their skills form one plugin. Prefixes use lowercase letters,
digits and hyphens, starting with a letter or digit. Setup rejects the same source/skill listed both
scoped and unscoped, including `*` overlaps. Different sources may share names: this repo's `pr`
and `code-review` wrap `matt:pr` and `matt:code-review`.

## Scoped plugins and updates

Whenever [`setup.sh`](setup.sh) runs, it rebuilds scoped plugins from the current upstream skills
in `~/.agents/skill-plugins`, outside the shared skills folder. That folder contains the local
`dev-env-skills` marketplace, plugin files and ownership records. Generated copies stay on the
machine. Upstream text stays unchanged, except for Cursor's skill names.

- **Claude Code** registers the local marketplace and installs missing plugins. Local plugins load
  from their source folders, so rebuilt content appears in the next session without a plugin update.
- **Codex** registers the same marketplace and re-adds each plugin on every setup run to refresh
  its cached copy. Starting Codex alone does not refresh it.
- **Cursor** gets real files in `~/.cursor/plugins/local/<prefix>/`. Each skill folder and its
  frontmatter `name` use `<prefix>:<skill>`, because Cursor does not add the namespace itself.

Removing skills from a scoped line removes them on the next rebuild. Removing a prefix uninstalls
its plugins and deletes its generated folders. Setup tracks its own prefixes and leaves unrelated
plugins alone. An absent harness catches up when setup next runs with it installed. The first run
also removes the old unscoped Matt skills, preserving replacements from other sources.

For isolated tests, `DEV_ENV_SKILLS_FILE=/absolute/path/to/skills.txt bash setup.sh` reads a local
list instead of downloading it. Other downloads still use `main`.

## Try a change to a skill

Replace the installed copy with a link to your working copy:

```bash
rm -rf ~/.agents/skills/<name>
ln -s ~/path/to/skills/<name> ~/.agents/skills/<name>
```

For an unscoped skill, running the setup again removes the link and restores the published version.
Your working copy stays as it is. This restores every override at once. To work on DevFlow itself, link
`~/.agents/dev-flow` to your checkout the same way. `~/.agents/AGENTS.md` works the same.

## Cloud

Use the line above as the environment's setup script. Cloud sessions start from a snapshot that can be
about a week old, so the setup adds a session start hook that refreshes DevFlow, the instructions and
the skills in each cloud session, including rebuilding scoped plugins and refreshing their harness
installs for the next session. Other harness settings and the DevFlow plugin update when the snapshot
is rebuilt. The hook does nothing locally, so it can't restore a skill you're experimenting with.
