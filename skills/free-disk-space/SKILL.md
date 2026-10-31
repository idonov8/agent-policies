---
name: free-disk-space
description: Free up disk space on Ido's Mac. Use when asked to free up space, clean the disk, or find what is filling it, or when a full disk is blocking work. Surveys usage, then clears regenerable caches and duplicate node_modules across git worktrees once the user approves.
---

# Free disk space

Survey first and delete nothing until the user picks what to clean.

## 1. Survey

Run `scripts/survey.sh`. It is read-only and prints free space, the largest
folders, Docker usage, dev caches, installers in Downloads, and `node_modules`
totals grouped by git repository. Drill into anything large it surfaces.

Present a table of where the space goes. Then ask with one multi-select
question, giving each option's estimated size and noting that it regenerates.

## 2. What to offer

These were approved before and regenerate on their own:

- **Docker:** `docker container prune -f`, `docker image prune -a -f`,
  `docker builder prune -a -f`. Keep volumes: they can hold database data.
  Mention unused volumes separately and leave them.
- **Old iOS DeviceSupport:** in `~/Library/Developer/Xcode/iOS DeviceSupport`,
  keep the newest version and remove the rest.
- **Dev caches:** `~/.cache/uv`, `~/.cache/puppeteer`,
  `~/Library/Caches/ms-playwright`, `~/Library/Caches/pip`, Xcode
  `DerivedData`, `npm cache clean --force`, `brew cleanup -s --prune=all`.
- **Installers:** move `.dmg` files in `~/Downloads` to `~/.Trash`; don't
  delete them. The user empties the Trash.

Never offer to delete personal media or documents (Movies, Pictures,
Documents, Downloads exports). Report their size and suggest moving them to
an external drive.

## 3. Duplicate node_modules across worktrees

Agent worktrees each carry a full `node_modules`; this is often the largest
dev cost. Per repo:

- Keep `node_modules` in the main checkout and in worktrees with commits in
  the last day or two. Leave a repo alone if all its checkouts are active.
- Delete `node_modules` in the older worktrees. `npm install` restores it.

## 4. Stale worktrees with uncommitted changes

Agent worktrees often share a branch. When one moves the branch forward, the
others show its newer files as "modified" without holding any new work.
Before calling such a worktree unfinished, run
`scripts/stale-worktrees.sh <repo>`. For each dirty worktree it reports how
many changed files match a blob already in git history, and lists the rest.

- If every file is in history, the worktree is stale.
- For files listed as new, diff them against `HEAD` and `origin/main`. If the
  diff only removes code that `main` has, the worktree is still stale.
  Anything that adds code is real work: show it to the user and keep it.

Removing stale worktrees with `git worktree remove --force` keeps their
branches. The permission classifier may block it as irreversible. If it
does, give the user the exact command to run and verify afterwards with
`git worktree list`. Never touch the main checkout's own changes.

## 5. Report

Measure free space before and after with `df -h /System/Volumes/Data`.
Report what was freed per category, what was kept and why, and what is left
for the user (emptying the Trash, large personal folders). If duplicate
`node_modules` were large, suggest switching those repos to pnpm, which
shares one package store across worktrees.
