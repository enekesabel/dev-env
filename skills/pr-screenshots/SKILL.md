---
name: pr-screenshots
description: Upload screenshots to a GitHub pull request so they show in its comments or description, through a dedicated pr-screenshots branch in the same repository. Use when a PR needs images (UI changes, before/after, a dogfood or test run), or when cleaning up a merged PR's screenshots.
---

# PR screenshots

GitHub has no API for attaching images to a comment. This skill keeps them in one branch of the same repository, `pr-screenshots`, with one folder per PR number. The branch shares no history with the default branch and is never merged. Images load from `?raw=true` links, which render for anyone who can read the repository.

Use the bundled script for every upload and cleanup:

```text
<skill-directory>/scripts/pr-screenshots.sh upload <pr-number> <file>... [--repo owner/name]
<skill-directory>/scripts/pr-screenshots.sh clean <pr-number> [--repo owner/name]
```

The script works in a temporary clone, so it never touches the current checkout or its branch. It needs `gh` and `git` with push access. Without `--repo`, it uses the repository of the current directory. On first use in a repository it creates the branch with a README explaining it.

## Upload and post

1. Save the screenshots as PNG files with short descriptive names, such as `1-settings-before.png`. The name becomes the image's alt text and its path on the branch. Use only letters, digits, dots, hyphens and underscores.
2. Run `upload`. It prints one markdown image line per file. A file with the same name replaces the earlier one.
3. Post the images, each with a one-line caption saying what it shows. Put them in a new comment with `gh pr comment <pr> --body-file <file>`, or add them to the description when the user asks for that.
4. Report the comment URL.

Look at each screenshot before posting it. Don't upload anything that shows secrets, tokens, credentials or personal data.

## Clean up

Run `clean <pr-number>` after the PR merges or closes, when the user asks. It removes the PR's folder from the branch. Images in comments that pointed at it stop loading, so don't clean a PR whose comments still need them. Never delete the branch itself unless the user asks.

Done means the images render in the PR, or, for cleanup, the PR's folder is gone from the branch.
