#!/usr/bin/env bash
# Read-only disk usage survey. Usage: survey.sh [code-dir]
CODE_DIR="${1:-$HOME/Code}"

section() { printf '\n== %s\n' "$1"; }
top() { du -xhd1 "$1" 2>/dev/null | sort -hr | sed -n "2,${2:-9}p"; }

section "Free space"
df -h /System/Volumes/Data 2>/dev/null || df -h /

section "Home"
top "$HOME" 16

for d in Library/Containers "Library/Application Support" Library/Developer Library/Developer/Xcode Library/Caches .cache; do
  [ -d "$HOME/$d" ] && { section "$d"; top "$HOME/$d"; }
done

section "Docker"
if command -v docker >/dev/null && docker info >/dev/null 2>&1; then docker system df; else echo "not running"; fi

section "iOS DeviceSupport"
ls "$HOME/Library/Developer/Xcode/iOS DeviceSupport" 2>/dev/null || echo "none"

section "Package caches"
du -sh "$HOME/.npm" "$HOME/Library/Caches/pip" "$HOME/Library/Caches/ms-playwright" \
  "$HOME/.cache/uv" "$HOME/.cache/puppeteer" "$(brew --cache 2>/dev/null)" 2>/dev/null | sort -hr

section "Installers in Downloads (>100M)"
find "$HOME/Downloads" -maxdepth 1 \( -name '*.dmg' -o -name '*.pkg' -o -name '*.zip' \) -size +100M \
  -exec du -h {} + 2>/dev/null | sort -hr

section "node_modules by repo under $CODE_DIR (size, folders, checkouts, repo)"
find "$CODE_DIR" -type d -name node_modules -prune 2>/dev/null | while IFS= read -r nm; do
  p=$(dirname "$nm")
  # Worktrees of one repo share a common git dir; older git lacks --path-format.
  common=$(cd "$p" && cd "$(git rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd -P) || common=none
  checkout=$(git -C "$p" rev-parse --show-toplevel 2>/dev/null || echo "$p")
  printf '%s|%s|%s\n' "$(du -sk "$nm" | cut -f1)" "$common" "$checkout"
done | awk -F'|' '{s[$2]+=$1; n[$2]++; if (!seen[$2 SUBSEP $3]++) c[$2]++}
  END {for (r in s) printf "%6.1f GB  %3d  %3d  %s\n", s[r]/1048576, n[r], c[r], r}' | sort -hr | head -15
