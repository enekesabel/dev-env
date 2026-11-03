#!/bin/bash
# Merge upstream changes into the forked skills listed in forks.txt. Run from the repo root.
# A file changed on both sides gets conflict markers to resolve by hand. Prints a Markdown report.
set -euo pipefail

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

while read -r skill repo path base; do
  [ -n "$skill" ] && [ "${skill:0:1}" != "#" ] || continue
  up="$tmp/${repo//\//_}"
  [ -d "$up" ] || git clone -q --filter=blob:none "https://github.com/$repo.git" "$up"
  head=$(git -C "$up" rev-parse HEAD)
  git -C "$up" diff --quiet "$base" "$head" -- "$path" && continue

  echo "### \`$skill\`: [upstream changes](https://github.com/$repo/compare/${base:0:7}...${head:0:7})"
  ours="skills/$skill"
  for f in $(git -C "$up" diff --name-only "$base" "$head" -- "$path"); do
    rel=${f#"$path"/}
    old="$tmp/old" new="$tmp/new"
    git -C "$up" show "$base:$f" > "$old" 2>/dev/null || : > "$old"
    if ! git -C "$up" show "$head:$f" > "$new" 2>/dev/null; then
      # Deleted upstream: follow only if we never changed it.
      if cmp -s "$old" "$ours/$rel"; then rm "$ours/$rel"; echo "- removed \`$rel\`"
      else echo "- **check** \`$rel\`: deleted upstream, kept because we changed it"; fi
    elif [ ! -e "$ours/$rel" ]; then
      mkdir -p "$(dirname "$ours/$rel")"; cp "$new" "$ours/$rel"; echo "- added \`$rel\`"
    elif git merge-file -L ours -L "upstream ${base:0:7}" -L "upstream ${head:0:7}" "$ours/$rel" "$old" "$new"; then
      echo "- merged \`$rel\`"
    else
      echo "- **conflict** \`$rel\`: resolve the markers"
    fi
  done
  sed -i.bak "s/ $base\$/ $head/" forks.txt && rm forks.txt.bak
done < forks.txt
