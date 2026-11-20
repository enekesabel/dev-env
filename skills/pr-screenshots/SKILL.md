---
name: pr-screenshots
description: Add images or videos to a GitHub pull request's comments or description. Use when a PR needs images (UI changes, before/after, a dogfood or test run), or when cleaning up a merged PR's screenshots.
---

# PR screenshots

There are two ways to put images on a pull request:

- **`gh --attach`**, the default. It needs GitHub CLI 2.99 or later (`gh --version`). Files upload to GitHub's own storage, like an image dragged into the web editor, and nothing is pushed to the repository. Videos work too and show as a player. An uploaded file can't be deleted or replaced afterwards; to change one, edit the post.
- **The screenshots branch**, the fallback. Use it when `gh` is older than 2.99, or when the user wants images they can remove after the PR merges.

Either way:

1. Save the files with short descriptive names, such as `1-settings-before.png`. Use only letters, digits, dots, hyphens and underscores.
2. Look at each file before posting it. Don't upload anything that shows secrets, tokens, credentials or personal data.
3. Give each image a one-line caption saying what it shows. Post them in a new comment, or in the description when the user asks for that.
4. Report the comment or PR URL.

Done means the images render in the PR, or, for cleanup, the PR's folder is gone from the branch.

## With gh --attach

Write the body with a Markdown image line per file, `![caption](./1-settings-before.png)`, and pass each file with `--attach`. gh rewrites each line to the uploaded file and keeps the caption. A file the body doesn't reference is appended at the end. Paths in a `--body-file` resolve from that file's directory.

```text
gh pr comment <pr> --body-file <file> --attach <file> [--attach <file>...]
gh pr edit <pr> --attach <file>...
```

`gh pr edit` without a body flag keeps the description and appends the files to it. With `--body-file` it replaces the whole description, so read the current one first (`gh pr view <pr> --json body --jq .body`) and build on it.

## With the screenshots branch

GitHub has no API for attaching images, so this path keeps them in one branch of the same repository, `pr-screenshots`, with one folder per PR number. The branch shares no history with the default branch and is never merged. Images load from `?raw=true` links, which render for anyone who can read the repository.

Use the bundled script for every upload and cleanup:

```text
<skill-directory>/scripts/pr-screenshots.sh upload <pr-number> <file>... [--repo owner/name]
<skill-directory>/scripts/pr-screenshots.sh clean <pr-number> [--repo owner/name]
```

The script works in a temporary clone, so it never touches the current checkout or its branch. It needs `gh` and `git` with push access. Without `--repo`, it uses the repository of the current directory. On first use in a repository it creates the branch with a README explaining it.

`upload` prints one Markdown image line per file, with the file name as the alt text. A file with the same name replaces the earlier one. Post those lines, for example with `gh pr comment <pr> --body-file <file>`.

Run `clean <pr-number>` after the PR merges or closes, when the user asks. It removes the PR's folder from the branch. Images in comments that pointed at it stop loading, so don't clean a PR whose comments still need them. Never delete the branch itself unless the user asks.
