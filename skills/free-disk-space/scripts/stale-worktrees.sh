#!/usr/bin/env bash
# Read-only. For each dirty worktree of a repo, report how many changed files
# already exist as blobs in git history. Usage: stale-worktrees.sh <repo-path>
set -euo pipefail
repo="${1:?usage: stale-worktrees.sh <repo-path>}"
main=$(git -C "$repo" rev-parse --show-toplevel)
blobs=$(mktemp); trap 'rm -f "$blobs"' EXIT
git -C "$repo" rev-list --all --objects | awk '{print $1}' | sort -u > "$blobs"

git -C "$repo" worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
  [ -d "$wt" ] || continue
  status=$(git -C "$wt" status --porcelain --untracked-files=all)
  [ -n "$status" ] || continue
  branch=$(git -C "$wt" branch --show-current); branch=${branch:-detached}
  last=$(git -C "$wt" log -1 --format=%cs)
  [ "$wt" = "$main" ] && label="$wt (main checkout, keep)" || label="$wt"

  total=0; known=0; new=""
  # Modified, added or untracked files that still exist on disk.
  while IFS= read -r f; do
    [ -f "$wt/$f" ] || continue
    total=$((total + 1))
    if grep -qx "$(git -C "$wt" hash-object -- "$f")" "$blobs"; then known=$((known + 1)); else new="$new $f"; fi
  done < <(printf '%s\n' "$status" | grep -v '^ D\|^D ' | cut -c4- | sed 's/.* -> //')
  deleted=$(printf '%s\n' "$status" | grep -c '^ D\|^D ' || true)

  printf '%s [%s] last commit %s: %d/%d files in history, %d deleted\n' "$label" "$branch" "$last" "$known" "$total" "$deleted"
  [ -z "$new" ] || printf '  not in history:%s\n' "$new"
done
