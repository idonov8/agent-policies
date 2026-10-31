---
name: free-disk-space
description: Free up disk space on Ido's Mac. Use when asked to free up space, clean the disk, or find what is filling it, or when a full disk is blocking work. Surveys usage, proposes regenerable caches and duplicate node_modules to delete with the space each frees, and deletes only what Ido approves.
---

# Free disk space

Survey, propose a deletion plan, and delete nothing until Ido approves it.

## 1. Survey

Run `scripts/survey.sh`. It is read-only and prints free space, the largest
folders, Docker usage, dev caches, installers in Downloads, and `node_modules`
totals grouped by git repository. Drill into anything large it surfaces.

## 2. Propose a deletion plan

Show a table of where the space goes, then a plan with one row per item:

| What will be deleted | Why it is safe | Space freed |
| --- | --- | --- |

Name exact paths or commands, not categories ("5 old iOS DeviceSupport
versions, 26.1 to 27.0", not "Xcode stuff"). Measure each size before
proposing it. Give the total at the bottom.

Then ask for approval with one multi-select question, one option per row.
Delete only the rows Ido selects. If anything new turns up during cleanup,
add it to the plan and ask again.

## 3. What to propose

These were approved before and regenerate on their own:

- **Docker:** `docker container prune -f`, `docker image prune -a -f`,
  `docker builder prune -a -f`. Images download again when needed. Keep
  volumes: they can hold database data. Report unused volumes separately.
- **Old iOS DeviceSupport:** in `~/Library/Developer/Xcode/iOS DeviceSupport`,
  keep the newest version. Xcode rebuilds older ones when a device on that
  iOS is connected.
- **Dev caches:** `~/.cache/uv`, `~/.cache/puppeteer`,
  `~/Library/Caches/ms-playwright`, `~/Library/Caches/pip`, Xcode
  `DerivedData`, `npm cache clean --force`, `brew cleanup -s --prune=all`.
  Each refills on next use, at the cost of a slower first run.
- **Installers:** move `.dmg` files in `~/Downloads` to `~/.Trash`; don't
  delete them. The space returns once Ido empties the Trash.
- **Duplicate `node_modules` across worktrees:** agent worktrees each carry a
  full copy. Per repo, keep the copy in the main checkout and in worktrees
  with commits in the last day or two, and propose deleting the rest.
  `npm install` restores them. Leave a repo alone if all its checkouts are
  active.

Never propose deleting personal media or documents (Movies, Pictures,
Documents, Downloads exports), or removing worktrees themselves. Report
large personal folders and suggest moving them to an external drive.

## 4. Report

Measure free space before and after with `df -h /System/Volumes/Data`.
Report what was freed per item, what was kept and why, and what is left for
Ido (emptying the Trash, large personal folders). If duplicate
`node_modules` were large, suggest switching those repos to pnpm, which
shares one package store across worktrees.
