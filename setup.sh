#!/bin/bash
# Setup for my coding agents, on any machine or cloud environment:
#   curl -fsSL https://raw.githubusercontent.com/enekesabel/dev-env/main/setup.sh | bash
#
# Re-run it to update, and to restore anything overridden with a symlink.
# Each step is independent: a failing step prints a warning and the rest still run.
set -uo pipefail

raw=https://raw.githubusercontent.com/enekesabel/dev-env/main
devflow="$HOME/.agents/dev-flow"
agents_md="$HOME/.agents/AGENTS.md"
settings="$HOME/.claude/settings.json"

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

install_skills() {
  local list entry
  list=$(curl -fsSL "$raw/skills.txt") || return 1
  while read -ra entry; do
    [ "${#entry[@]}" -gt 1 ] && [ "${entry[0]:0:1}" != "#" ] || continue
    # Naming a second agent is what puts skills in the shared ~/.agents/skills.
    npx -y skills add "${entry[0]}" --skill "${entry[@]:1}" -g -a claude-code codex -y </dev/null ||
      warn "${entry[0]} install failed"
  done <<<"$list"
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
  mkdir -p "$(dirname "$settings")"
  [ -s "$settings" ] || echo '{}' > "$settings"

  # Instructions: Claude only reads the shared file through an import
  local claude_md="$HOME/.claude/CLAUDE.md" import='@~/.agents/AGENTS.md'
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
  mkdir -p "$HOME/.codex"
  [ -e "$HOME/.codex/AGENTS.md" ] || ln -sfn ../.agents/AGENTS.md "$HOME/.codex/AGENTS.md" ||
    warn "Codex instructions link failed"
}

main() {
  install_devflow || warn "DevFlow clone failed"
  install_instructions || warn "instructions install failed"
  install_skills || warn "skill list failed"
  # A running session can't pick up harness changes, so a refresh leaves them alone.
  [ "${1:-}" != refresh ] || return 0
  if command -v claude >/dev/null; then setup_claude; fi
  if command -v codex >/dev/null; then setup_codex; fi
}

# The whole script is read before main runs, so nothing it starts can eat a piped script.
main "$@" </dev/null
exit 0
