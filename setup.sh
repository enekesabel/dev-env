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

# Validate before installing anything. Identity includes the source: our wrappers may share upstream names.
read_skill_list() {
  if [ -n "${DEV_ENV_SKILLS_FILE:-}" ]; then
    skill_list=$(cat "$DEV_ENV_SKILLS_FILE") || return 1
  else
    skill_list=$(curl -fsSL "$raw/skills.txt") || return 1
  fi
  awk '
    /^[[:space:]]*#/ || NF == 0 { next }
    {
      source = $1; scope = "unscoped"
      if (index(source, "=")) {
        scope = substr(source, 1, index(source, "=") - 1)
        source = substr(source, index(source, "=") + 1)
        if (scope !~ /^[a-z0-9][a-z0-9-]*$/ || source == "" || index(source, "=")) {
          print "dev-env: invalid skill prefix/source: " $1 > "/dev/stderr"; exit 1
        }
        scope = "scoped"
      }
      if (NF < 2) { print "dev-env: missing skills for " $1 > "/dev/stderr"; exit 1 }
      for (i = 2; i <= NF; i++) {
        other = scope == "scoped" ? "unscoped" : "scoped"
        if (seen[source, other, $i] || seen[source, other, "*"] || ($i == "*" && any[source, other])) {
          print "dev-env: skill listed both scoped and unscoped: " source " " $i > "/dev/stderr"; exit 1
        }
        seen[source, scope, $i] = 1; any[source, scope] = 1
      }
    }
  ' <<<"$skill_list"
}

# One-time migration; drop this step once machines have moved to the scoped plugin.
remove_old_matt_skills() {
  [ ! -e "$plugin_root/matt-migrated" ] || return 0
  local skill source lock="$HOME/.agents/.skill-lock.json" remove=()
  [ -z "${XDG_STATE_HOME:-}" ] || lock="$XDG_STATE_HOME/skills/.skill-lock.json"
  for skill in ask-matt code-review codebase-design diagnosing-bugs domain-modeling grill-me grill-with-docs \
    grilling handoff implement implement-spec improve-codebase-architecture pr prototype research retro \
    setup-matt-pocock-skills setup-ts-deep-modules tdd to-spec to-tickets triage wayfinder writing-for-agents; do
    [ -e "$HOME/.agents/skills/$skill" ] || [ -L "$HOME/.agents/skills/$skill" ] || continue
    source=$(jq -r --arg skill "$skill" '.skills[$skill].source // empty' "$lock" 2>/dev/null) || source=
    # Preserve replacements, especially this repo's pr and code-review wrappers.
    [ -z "$source" ] || [ "$source" = mattpocock/skills ] || continue
    if [ -z "$source" ] && { [ "$skill" = pr ] || [ "$skill" = code-review ]; }; then continue; fi
    remove+=("$skill")
  done
  if [ "${#remove[@]}" -gt 0 ]; then
    npx -y skills remove "${remove[@]}" -g -y </dev/null || return 1
  fi
  touch "$plugin_root/matt-migrated"
}

install_skills() {
  local entry prefix source path old
  mkdir -p "$plugin_root/plugins" "$plugin_root/.claude-plugin" || return 1
  remove_old_matt_skills || return 1
  rm -rf "$plugin_root/staging"
  mkdir -p "$plugin_root/staging" || return 1
  : > "$plugin_root/prefixes.next"
  # Collect prefixes first so multiple sources can contribute to one clean build.
  while read -ra entry; do
    [ "${#entry[@]}" -gt 1 ] && [ "${entry[0]:0:1}" != "#" ] || continue
    case "${entry[0]}" in
      *=*) printf '%s\n' "${entry[0]%%=*}" ;;
    esac
  done <<<"$skill_list" | sort -u > "$plugin_root/prefixes.next"

  while read -r prefix; do
    mkdir -p "$plugin_root/staging/$prefix" || return 1
  done < "$plugin_root/prefixes.next"
  while read -ra entry; do
    [ "${#entry[@]}" -gt 1 ] && [ "${entry[0]:0:1}" != "#" ] || continue
    source=${entry[0]}
    if [[ "$source" == *=* ]]; then
      prefix=${source%%=*}; source=${source#*=}
      (cd "$plugin_root/staging/$prefix" &&
        npx -y skills add "$source" --skill "${entry[@]:1}" -a claude-code codex -y </dev/null) || return 1
      continue
    fi
    # Naming a second agent is what puts skills in the shared ~/.agents/skills.
    npx -y skills add "$source" --skill "${entry[@]:1}" -g -a claude-code codex -y </dev/null ||
      warn "$source install failed"
  done <<<"$skill_list"

  while read -r prefix; do
    path="$plugin_root/staging/$prefix"
    mkdir -p "$path/plugin/skills" "$path/plugin/.claude-plugin" || return 1
    # Dereference every link: Codex drops symlinks when copying plugins into its cache.
    cp -RL "$path/.agents/skills/." "$path/plugin/skills/" || return 1
    jq -n --arg name "$prefix" '{name: $name, version: "1.0.0"}' > "$path/plugin/.claude-plugin/plugin.json" || return 1
  done < "$plugin_root/prefixes.next"
  while read -r prefix; do
    rm -rf "$plugin_root/plugins/$prefix"
    mv "$plugin_root/staging/$prefix/plugin" "$plugin_root/plugins/$prefix" || return 1
  done < "$plugin_root/prefixes.next"
  while read -r old; do
    grep -qxF "$old" "$plugin_root/prefixes.next" && continue
    rm -rf "$plugin_root/plugins/$old"
  done < <(cat "$plugin_root/prefixes" 2>/dev/null)
  jq -Rn --arg name "$marketplace" '{name: $name, owner: {name: "enekesabel"},
    plugins: [inputs | {name: ., source: ("./plugins/" + .)}]}' \
    < "$plugin_root/prefixes.next" > "$plugin_root/.claude-plugin/marketplace.json" || return 1
  mv "$plugin_root/prefixes.next" "$plugin_root/prefixes" || return 1
  rm -rf "$plugin_root/staging"
}

install_cursor_plugin() {
  local prefix=$1 target="$HOME/.cursor/plugins/local/$1" skill name
  mkdir -p "$(dirname "$target")" || return 1
  rm -rf "$target"
  cp -RL "$plugin_root/plugins/$prefix" "$target" || return 1
  for skill in "$target"/skills/*; do
    [ -f "$skill/SKILL.md" ] || continue
    name=$(basename "$skill")
    # Change only the frontmatter name; upstream prose and references stay verbatim.
    node - "$skill/SKILL.md" "$prefix:$name" <<'JS' || return 1
const fs = require('node:fs');
const [file, name] = process.argv.slice(2);
const text = fs.readFileSync(file, 'utf8');
const frontmatter = text.match(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/)?.[0];
if (!frontmatter || !/^name:[^\r\n]*$/m.test(frontmatter)) throw new Error(`Missing skill name: ${file}`);
fs.writeFileSync(file, frontmatter.replace(/^name:[^\r\n]*/m, `name: ${name}`) + text.slice(frontmatter.length));
JS
    mv "$skill" "$target/skills/$prefix:$name" || return 1
  done
}

# Separate ownership records let an absent harness catch up, and retry failed uninstalls later.
sync_plugins() {
  local harness=$1 prefix id installed state="$plugin_root/$1-prefixes" failed=0
  : > "$state.next"
  while read -r prefix; do
    if grep -qxF "$prefix" "$plugin_root/prefixes"; then
      printf '%s\n' "$prefix" >> "$state.next"
      continue
    fi
    id="$prefix@$marketplace"
    case "$harness" in
      claude) claude plugin uninstall "$id" ;;
      codex) codex plugin remove "$id" ;;
      cursor) rm -rf "$HOME/.cursor/plugins/local/$prefix" ;;
    esac || { printf '%s\n' "$prefix" >> "$state.next"; failed=1; warn "$harness uninstall $id failed"; }
  done < <(cat "$state" 2>/dev/null)
  mv "$state.next" "$state" || return 1

  if [ -s "$plugin_root/prefixes" ]; then
    case "$harness" in
      claude|codex) "$harness" plugin marketplace add "$plugin_root" || return 1 ;;
    esac
  fi
  if [ "$harness" = claude ] && [ -s "$plugin_root/prefixes" ]; then
    installed=$(claude plugin list --json) || return 1
  fi
  while read -r prefix; do
    id="$prefix@$marketplace"
    # Record ownership before trying an install that could partially succeed.
    grep -qxF "$prefix" "$state" || printf '%s\n' "$prefix" >> "$state"
    case "$harness" in
      claude)
        if ! jq -e --arg id "$id" 'any(.[]; .id == $id)' <<<"$installed" >/dev/null; then
          claude plugin install "$id"
        fi ;;
      # Re-add even at the same version: startup alone does not refresh Codex's cache.
      codex) codex plugin add "$id" ;;
      cursor) install_cursor_plugin "$prefix" ;;
    esac
    if [ "$?" -ne 0 ]; then
      failed=1; warn "$harness install $id failed"
    fi
  done < "$plugin_root/prefixes"
  return "$failed"
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

setup_claude() {
  sync_plugins claude || warn "Claude scoped plugins failed"
  [ "${1:-}" != refresh ] || return 0
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

# Instructions: Codex only reads its own folder. Instructions already there are kept.
setup_codex() {
  sync_plugins codex || warn "Codex scoped plugins failed"
  [ "${1:-}" != refresh ] || return 0
  mkdir -p "$codex_config"
  [ -e "$codex_config/AGENTS.md" ] || ln -sfn "$agents_md" "$codex_config/AGENTS.md" ||
    warn "Codex instructions link failed"
}

setup_cursor() {
  sync_plugins cursor || warn "Cursor scoped plugins failed"
}

main() {
  read_skill_list || return 1
  install_devflow || warn "DevFlow clone failed"
  install_instructions || warn "instructions install failed"
  install_skills || { warn "skill install failed"; return 1; }
  if command -v claude >/dev/null; then setup_claude "${1:-}"; fi
  if command -v codex >/dev/null; then setup_codex "${1:-}"; fi
  if command -v cursor >/dev/null || command -v cursor-agent >/dev/null; then setup_cursor; fi
}

# The whole script is read before main runs, so nothing it starts can eat a piped script.
main "$@" </dev/null
