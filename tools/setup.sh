#!/usr/bin/env bash
# One-time setup of the shared build dependencies (not committed, see .gitignore):
#   tools/pylib/   zstandard, to read CA's compressed packs
#   tools/schemas/ schema_wh3.ron from RPFM's rpfm-schemas, to decode DB tables
# twpack.py in each faction's _build_scripts/ finds both here (../../tools).
# Re-run after a big game patch to get the current schema.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"

python -m pip install --upgrade --target "$here/pylib" "zstandard==0.25.0"

mkdir -p "$here/schemas"
curl -fsSL -o "$here/schemas/schema_wh3.ron" \
  "https://raw.githubusercontent.com/Frodo45127/rpfm-schemas/master/schema_wh3.ron"

echo "setup done: $here/pylib, $here/schemas/schema_wh3.ron"
echo "next: python Faction_<X>/_build_scripts/make_loc_cache.py  (only if a builder needs loc_en.pkl)"
