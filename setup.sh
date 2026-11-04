#!/bin/bash
# Setup for my coding agents, on any machine or cloud environment:
#   curl -fsSL https://raw.githubusercontent.com/enekesabel/dev-env/main/setup.sh | bash
#
# Re-run it to update, and to restore anything overridden with a symlink.
# Invalid skill lists stop setup; other failing steps print a warning.
set -uo pipefail

raw=https://raw.githubusercontent.com/enekesabel/dev-env/main
devflow="$HOME/.agents/dev-flow"
agents_md="$HOME/.agents/AGENTS.md"
claude_config="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
codex_config="${CODEX_HOME:-$HOME/.codex}"
settings="$claude_config/settings.json"
plugin_root="$HOME/.agents/skill-plugins"
marketplace=dev-env-skills
skill_list=

warn() { echo "dev-env: $*" >&2; }

# One shared copy of DevFlow. A symlink here is an override, so it gets replaced, never pulled through.
install_devflow() {
  mkdir -p "$(dirname "$devflow")"
  [ ! -L "$devflow" ] || rm "$devflow"
  if [ -d "$devflow/.git" ]; then
    git -C "$devflow" pull -q --ff-only
  else
    git clone -q https://github.com/enekesabel/dev-flow.git "$devflow"
  fi
}

# One shared copy of the instructions. mv replaces a symlink here instead of writing through it.
install_instructions() {
  mkdir -p "$(dirname "$agents_md")"
  curl -fsSL "$raw/AGENTS.md" -o "$agents_md.tmp" && mv "$agents_md.tmp" "$agents_md"
}

# Stops on an invalid list (2) and not on a failed download (1). Identity includes the source: our wrappers
# share upstream names.
read_skill_list() {
  if [ -n "${DEV_ENV_SKILLS_FILE:-}" ]; then
    skill_list=$(cat "$DEV_ENV_SKILLS_FILE") || return 1
  else
    skill_list=$(curl -fsSL "$raw/skills.txt") || return 1
  fi
  awk '
    function fail(msg) { print "dev-env: " msg > "/dev/stderr"; exit 1 }
    /^[[:space:]]*#/ || NF < 2 { next }
    {
      source = $1; scope = "unscoped"
      if (split($1, part, "=") > 1) {
        if (part[1] !~ /^[a-z0-9-]+$/ || part[2] == "") fail("invalid prefix: " $1)
        if (part[1] in prefixes) fail("prefix listed twice: " part[1])
        prefixes[part[1]]; source = part[2]; scope = "scoped"
      }
      other = scope == "scoped" ? "unscoped" : "scoped"
      for (i = 2; i <= NF; i++) {
        if (seen[source, other, $i] || seen[source, other, "*"] || ($i == "*" && any[source, other]))
          fail("skill listed both scoped and unscoped: " source " " $i)
        seen[source, scope, $i] = 1; any[source, scope] = 1
      }
    }
  ' <<<"$skill_list" || return 2
}

# Build one prefix's plugin in staging, so a failed build keeps the previous one.
build_plugin() {
  local prefix=$1 source=$2 stage="$plugin_root/staging/$1"
  shift 2
  rm -rf "$stage" && mkdir -p "$stage" "$plugin_root/plugins" || return 1
  (cd "$stage" && npx -y skills add "$source" --skill "$@" -a claude-code codex -y </dev/null) || return 1
  # Real files: Codex drops symlinks when it copies a plugin into its cache.
  mkdir -p "$stage/plugin/.claude-plugin" && cp -RL "$stage/.agents/skills" "$stage/plugin/skills" &&
    printf '{"name": "%s", "version": "1.0.0"}\n' "$prefix" > "$stage/plugin/.claude-plugin/plugin.json" &&
    rm -rf "$plugin_root/plugins/$prefix" && mv "$stage/plugin" "$plugin_root/plugins/$prefix"
}

# The plugins folder is what every harness syncs to.
scoped_plugins() { ls "$plugin_root/plugins" 2>/dev/null; }

install_skills() {
  local entry prefix listed=" " entries= sep=
  while read -ra entry; do
    [ "${#entry[@]}" -gt 1 ] && [ "${entry[0]:0:1}" != "#" ] || continue
    if [[ "${entry[0]}" == *=* ]]; then
      prefix=${entry[0]%%=*}
      listed+="$prefix "
      build_plugin "$prefix" "${entry[0]#*=}" "${entry[@]:1}" || warn "$prefix plugin build failed"
      continue
    fi
    # Naming a second agent is what puts skills in the shared ~/.agents/skills.
    npx -y skills add "${entry[0]}" --skill "${entry[@]:1}" -g -a claude-code codex -y </dev/null ||
      warn "${entry[0]} install failed"
  done <<<"$skill_list"
  rm -rf "$plugin_root/staging"

  for prefix in $(scoped_plugins); do
    if [[ "$listed" == *" $prefix "* ]]; then
      entries+="$sep{\"name\": \"$prefix\", \"source\": \"./plugins/$prefix\"}"
      sep=", "
    else
      rm -rf "${plugin_root:?}/plugins/$prefix"
    fi
  done
  mkdir -p "$plugin_root/.claude-plugin" &&
    printf '{"name": "%s", "owner": {"name": "enekesabel"}, "plugins": [%s]}\n' "$marketplace" "$entries" \
      > "$plugin_root/.claude-plugin/marketplace.json"
}

# Apply a jq filter to the user settings, keeping everything else.
edit_settings() {
  jq "$@" "$settings" > "$settings.tmp" && mv "$settings.tmp" "$settings"
}

# Cloud sessions start from a snapshot up to about a week old, so refresh at the start of each one.
# It never runs locally, where it would restore a skill you are experimenting with.
add_cloud_refresh() {
  edit_settings --arg cmd "[ \"\$CLAUDE_CODE_REMOTE\" != true ] || curl -fsSL $raw/setup.sh | bash -s refresh" '
    .hooks.SessionStart = [(.hooks.SessionStart // [])[] | select(all(.hooks[]; .command != $cmd))]
      + [{hooks: [{type: "command", command: $cmd}]}]'
}

# Claude loads local plugins from their folder, so new content shows up in the next session.
claude_plugins() {
  local installed id prefix
  installed=$(claude plugin list --json | jq -r '.[].id') || return 1
  for id in $(grep "@$marketplace\$" <<<"$installed"); do
    [ -d "$plugin_root/plugins/${id%@*}" ] || claude plugin uninstall "$id" || warn "Claude uninstall $id failed"
  done
  [ -n "$(scoped_plugins)" ] || return 0
  claude plugin marketplace add "$plugin_root" || return 1
  for prefix in $(scoped_plugins); do
    grep -qxF "$prefix@$marketplace" <<<"$installed" || claude plugin install "$prefix@$marketplace" ||
      warn "Claude install $prefix failed"
  done
}

setup_claude() {
  mkdir -p "$(dirname "$settings")"
  [ -s "$settings" ] || echo '{}' > "$settings"

  # Instructions: Claude only reads the shared file through an import
  local claude_md="$claude_config/CLAUDE.md" import='@~/.agents/AGENTS.md'
  grep -qxF "$import" "$claude_md" 2>/dev/null || printf '\n%s\n' "$import" >> "$claude_md" ||
    warn "instructions import failed"

  # DevFlow plugin, with the Coordinator as the default output style
  if claude plugin marketplace add "$devflow" && claude plugin install dev-flow@dev-flow &&
    claude plugin marketplace update dev-flow && claude plugin update dev-flow@dev-flow; then
    edit_settings '. * {outputStyle: "dev-flow:devflow"}' || warn "DevFlow output style failed"
  else
    warn "DevFlow install failed"
  fi

  add_cloud_refresh || warn "cloud refresh failed"
}

# Codex only refreshes its cached copy when a plugin is added again, so add every one on each run.
codex_plugins() {
  local prefix
  # shortcut: reads Codex's cache folder to find installed plugins; switch if `codex plugin list` gains an installed filter.
  for prefix in $(ls "$codex_config/plugins/cache/$marketplace" 2>/dev/null); do
    [ -d "$plugin_root/plugins/$prefix" ] || codex plugin remove "$prefix@$marketplace" ||
      warn "Codex uninstall $prefix failed"
  done
  [ -n "$(scoped_plugins)" ] || return 0
  codex plugin marketplace add "$plugin_root" || return 1
  for prefix in $(scoped_plugins); do
    codex plugin add "$prefix@$marketplace" || warn "Codex install $prefix failed"
  done
}

# Instructions: Codex only reads its own folder. Instructions already there are kept.
setup_codex() {
  mkdir -p "$codex_config"
  [ -e "$codex_config/AGENTS.md" ] || ln -sfn "$agents_md" "$codex_config/AGENTS.md" ||
    warn "Codex instructions link failed"
}

# Cursor can't use a local marketplace or namespace plugin skills, so it gets copies with prefixed names.
# A marker file tells our folders apart from other local plugins.
cursor_plugins() {
  local local_dir="$HOME/.cursor/plugins/local" dir prefix skill name
  for dir in "$local_dir"/*/; do
    [ -e "$dir.dev-env" ] && [ ! -d "$plugin_root/plugins/$(basename "$dir")" ] && rm -rf "$dir"
  done
  for prefix in $(scoped_plugins); do
    dir="$local_dir/$prefix"
    rm -rf "$dir" && mkdir -p "$local_dir" && cp -R "$plugin_root/plugins/$prefix" "$dir" && touch "$dir/.dev-env" ||
      { warn "Cursor install $prefix failed"; continue; }
    for skill in "$dir"/skills/*/; do
      name="$prefix:$(basename "$skill")"
      # Only the frontmatter name changes; upstream text stays as it is.
      awk -v name="$name" 'NR == 1 && /^---/ { fm = 1 } fm && !done && /^name:/ { $0 = "name: " name; done = 1 }
        NR > 1 && /^---/ { fm = 0 } { print }' "$skill/SKILL.md" > "$skill/SKILL.md.tmp" &&
        mv "$skill/SKILL.md.tmp" "$skill/SKILL.md" && mv "${skill%/}" "$dir/skills/$name" ||
        warn "Cursor rename $name failed"
    done
  done
}

main() {
  local list_status=0
  read_skill_list || list_status=$?
  [ "$list_status" -ne 2 ] || return 1
  install_devflow || warn "DevFlow clone failed"
  install_instructions || warn "instructions install failed"
  if [ "$list_status" -eq 0 ]; then
    install_skills || warn "scoped plugin marketplace failed"
  else
    warn "skill list failed"
  fi
  # Plugins are for the next session, so a refresh syncs them too.
  if command -v claude >/dev/null; then claude_plugins || warn "Claude scoped plugins failed"; fi
  if command -v codex >/dev/null; then codex_plugins || warn "Codex scoped plugins failed"; fi
  if command -v cursor >/dev/null || command -v cursor-agent >/dev/null; then cursor_plugins; fi
  # A running session can't pick up the other harness changes, so a refresh leaves them alone.
  [ "${1:-}" != refresh ] || return 0
  if command -v claude >/dev/null; then setup_claude; fi
  if command -v codex >/dev/null; then setup_codex; fi
}

# The whole script is read before main runs, so nothing it starts can eat a piped script.
main "$@" </dev/null
