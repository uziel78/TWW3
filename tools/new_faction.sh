#!/usr/bin/env bash
# Scaffold a new faction folder:  tools/new_faction.sh <Name> <ModPrefix> [masters_subdir]
#   e.g. tools/new_faction.sh High_Elves Asur_
# Creates Faction_<Name>/ with CLAUDE.md, README.md, .sync and docs/ templates, plus
# _build_scripts/ seeded with the shared pack tools from Faction_Dark_Elves.
set -euo pipefail
[ $# -ge 2 ] || { echo "usage: $0 <Name> <ModPrefix> [masters_subdir]"; exit 1; }
name="$1"; prefix="$2"; sub="${3:-warhammer_3}"
repo="$(cd "$(dirname "$0")/.." && pwd)"
dir="$repo/Faction_$name"
[ -e "$dir" ] && { echo "$dir already exists"; exit 1; }
mkdir -p "$dir/docs" "$dir/_build_scripts"
for f in twpack.py build_pack.py make_loc_cache.py; do
  cp "$repo/Faction_Dark_Elves/_build_scripts/$f" "$dir/_build_scripts/"
done
today="$(date +%F)"

cat > "$dir/.sync" <<EOF
# Read by tools/sync_from_masters.sh (bash). Paths are relative to \$TWW3_MASTERS.
MASTERS_SUBDIR="$sub"
MOD_GLOBS="${prefix}*"
# List this faction's builders explicitly if _build_scripts is shared with another faction.
BUILD_GLOBS="build_${prefix,,}*.py"
EOF

cat > "$dir/CLAUDE.md" <<EOF
# Faction_$name: rules for Claude

Read the repo-root CLAUDE.md first; everything there applies here.

- Mod prefix: \`$prefix\` (packs, source folders, DB/loc fragment names).
- Masters: \`<MASTERS>/$sub/\`.

## Mods
| Mod | What it changes | Builder | Status |
|---|---|---|---|

## Build commands
(from \`_build_scripts/\`, one block per mod)

## Faction keys and facts
(faction keys, subculture, lord/hero subtypes, skill sets, chains this faction touches)
EOF

cat > "$dir/README.md" <<EOF
# $name mods

| Pack | What it does | New campaign? |
|---|---|---|
EOF

cat > "$dir/docs/HANDOFF.md" <<EOF
# Handoff: Faction_$name

Last updated: $today

## State
## Pending in-game tests
## Open questions for the author
## Pick up here
EOF

cat > "$dir/docs/MOD_HISTORY.md" <<EOF
# Faction_$name mod history

Dated log per mod: what changed, why, and what the author confirmed in game.
EOF

echo "created $dir; add a row to the faction table in README.md"
