#!/usr/bin/env bash
# Upload screenshots for a pull request to the repository's dedicated
# screenshots branch, print the markdown that shows them, or remove a PR's
# folder. The branch shares no history with the default branch and is never
# merged. Works in a temporary clone, so the caller's checkout is untouched.
#
# Usage:
#   pr-screenshots.sh upload <pr-number> <file>... [--repo owner/name]
#   pr-screenshots.sh clean  <pr-number>           [--repo owner/name]
#
# PR_SCREENSHOTS_BRANCH overrides the branch name (default: pr-screenshots).
set -euo pipefail

branch="${PR_SCREENSHOTS_BRANCH:-pr-screenshots}"

fail() {
  printf 'pr-screenshots: %s\n' "$1" >&2
  exit 1
}

command -v gh >/dev/null || fail "gh is required"
command -v git >/dev/null || fail "git is required"

action="${1:-}"
pr="${2:-}"
[[ "$action" == "upload" || "$action" == "clean" ]] || fail "usage: pr-screenshots.sh upload|clean <pr-number> [files...] [--repo owner/name]"
[[ "$pr" =~ ^[0-9]+$ ]] || fail "expected a PR number, got '$pr'"
shift 2

repo=""
files=()
while (($#)); do
  case "$1" in
    --repo) repo="${2:-}"; shift 2 ;;
    *) files+=("$1"); shift ;;
  esac
done
[[ -n "$repo" ]] || repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner)" || fail "no --repo and not inside a GitHub checkout"

for file in "${files[@]+"${files[@]}"}"; do
  [[ -f "$file" ]] || fail "no such file: $file"
  [[ "$(basename "$file")" =~ ^[A-Za-z0-9._-]+$ ]] || fail "use only letters, digits, dots, hyphens and underscores in file names: $file"
done
[[ "$action" == "clean" || ${#files[@]} -gt 0 ]] || fail "upload needs at least one file"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
url="https://github.com/$repo.git"

if git ls-remote --exit-code --heads "$url" "$branch" >/dev/null 2>&1; then
  git clone --quiet --depth 1 --single-branch --branch "$branch" "$url" "$work/repo"
else
  [[ "$action" == "upload" ]] || fail "$repo has no $branch branch"
  git init --quiet --initial-branch "$branch" "$work/repo"
  git -C "$work/repo" remote add origin "$url"
  printf '# %s\n\nScreenshots for pull requests, one folder per PR number. This branch shares no history with the default branch and is never merged.\n' "$branch" >"$work/repo/README.md"
  git -C "$work/repo" add README.md
fi

cd "$work/repo"
if [[ "$action" == "clean" ]]; then
  [[ -d "$pr" ]] || { printf 'pr-screenshots: no folder for #%s on %s\n' "$pr" "$branch"; exit 0; }
  git rm --quiet -r "$pr"
  git commit --quiet -m "chore: remove the screenshots for #$pr"
  git push --quiet origin "HEAD:refs/heads/$branch"
  printf 'pr-screenshots: removed %s/ from %s\n' "$pr" "$branch"
  exit 0
fi

mkdir -p "$pr"
for file in "${files[@]}"; do
  cp "$file" "$pr/$(basename "$file")"
done
git add "$pr"
if git diff --cached --quiet; then
  printf 'pr-screenshots: the files are already on %s, unchanged\n' "$branch" >&2
else
  git commit --quiet -m "chore: add screenshots for #$pr"
  git push --quiet origin "HEAD:refs/heads/$branch"
fi

for file in "${files[@]}"; do
  name="$(basename "$file")"
  printf '![%s](https://github.com/%s/blob/%s/%s/%s?raw=true)\n' "${name%.*}" "$repo" "$branch" "$pr" "$name"
done
