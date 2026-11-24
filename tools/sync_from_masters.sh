#!/usr/bin/env bash
# Mirror mod masters (RPFM MyMods, in Dropbox) into this repo, faction by faction.
#
#   tools/sync_from_masters.sh                  all Faction_* folders
#   tools/sync_from_masters.sh Faction_Dark_Elves
#
# Each faction folder has a .sync file (plain bash variables):
#   MASTERS_SUBDIR   folder under $TWW3_MASTERS holding that faction's mods
#   MOD_GLOBS        mod names (pack source folders + <name>.pack) belonging to the faction
#   BUILD_GLOBS      entries of the masters' _build_scripts/ belonging to the faction
#
# TWW3_MASTERS defaults to "$HOME/Dropbox/RPFM My Mods". Mod folders are replaced (so files
# deleted in the masters disappear here too); *.pkl caches are never copied.
# Review with `git status` / `git diff --stat` before committing.
set -euo pipefail
shopt -s nullglob
repo="$(cd "$(dirname "$0")/.." && pwd)"
masters_root="${TWW3_MASTERS:-$HOME/Dropbox/RPFM My Mods}"

factions=("$@")
if [ ${#factions[@]} -eq 0 ]; then
  for f in "$repo"/Faction_*/; do factions+=("$(basename "$f")"); done
fi

for faction in "${factions[@]}"; do
  conf="$repo/$faction/.sync"
  [ -f "$conf" ] || { echo "skip $faction: no .sync file"; continue; }
  MASTERS_SUBDIR=""; MOD_GLOBS=""; BUILD_GLOBS=""
  # shellcheck disable=SC1090
  source "$conf"
  src="$masters_root/$MASTERS_SUBDIR"
  dst="$repo/$faction"
  [ -d "$src" ] || { echo "skip $faction: $src not found"; continue; }

  # split on spaces/newlines without expanding the globs yet
  set -f; mod_globs=($MOD_GLOBS); build_globs=($BUILD_GLOBS); set +f
  for glob in "${mod_globs[@]}"; do
    for item in "$src"/$glob; do
      name="$(basename "$item")"
      case "$name" in *.pkl) continue ;; esac
      rm -rf "${dst:?}/$name"
      cp -r "$item" "$dst/$name"
      echo "  $faction <- $name"
    done
  done

  if [ -n "$BUILD_GLOBS" ]; then
    mkdir -p "$dst/_build_scripts"
    for glob in "${build_globs[@]}"; do
      for item in "$src/_build_scripts"/$glob; do
        name="$(basename "$item")"
        case "$name" in *.pkl|__pycache__) continue ;; esac
        rm -rf "${dst:?}/_build_scripts/$name"
        cp -r "$item" "$dst/_build_scripts/$name"
      done
    done
    echo "  $faction <- _build_scripts ($BUILD_GLOBS)"
  fi
done
echo "sync done; review with: git -C \"$repo\" status"
