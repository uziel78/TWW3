# TWW3 mods: working rules for Claude

Total War: WARHAMMER III mods, one folder per faction. Read this file, then the faction's own
`Faction_<Name>/CLAUDE.md` and `Faction_<Name>/docs/HANDOFF.md`, before changing anything.
[docs/ENGINE_LESSONS.md](docs/ENGINE_LESSONS.md) holds engine facts that apply to every faction:
check it before designing a feature, and add to it when a test teaches something new.

## Hard rules (from the mod author)
- **Never modify or delete vanilla game files.** Reading the game folder is fine. Every change is
  a mod pack the author enables in the launcher / Steam mod manager.
- **Ask before bigger changes** (new systems, overriding vanilla rows, reworking a mod's design,
  restructuring this repo). Small, add-only changes inside the agreed design can go ahead.
- **Effect descriptions stay vague**: no specific numbers in custom effect or bundle text.
- **Mixu's Unlocker is always loaded** (`!b_mixer.pack`). Frontend/UI work must fit around it.
- Prefer **add-only DB rows** (new junction rows, new records) over overriding vanilla rows; when
  an override is unavoidable, override one row and re-copy it from vanilla on every build.
- **This repo is public: no files from other modders** (e.g. edited copies of Mixu's UI files).
  Such packs stay in `<MASTERS>` only: leave them out of `.sync` and list them in `.gitignore`.
- Nothing is "working" until the author confirms it in game. Mark changes "untested" in the
  faction docs until then, and record confirmations with the date.

## Repo layout
```
CLAUDE.md                  this file (repo-wide rules)
docs/ENGINE_LESSONS.md     cross-faction engine knowledge, crash causes, CA patterns
tools/setup.sh             one-time: shared build deps into tools/pylib, tools/schemas (gitignored)
tools/sync_from_masters.sh mirror the mod masters (RPFM MyMods in Dropbox) into the repo
tools/new_faction.sh       scaffold a new Faction_<Name>/ folder
Faction_<Name>/
  CLAUDE.md                faction rules: prefix, mod list, build commands, faction-specific keys
  README.md                player-facing mod list
  .sync                    which master folders/files belong to this faction
  docs/HANDOFF.md          current state + next step (rewrite at the end of every session)
  docs/MOD_HISTORY.md      dated design/test log per mod (append, don't rewrite)
  _build_scripts/          builders (Python) + twpack.py/build_pack.py + hand-written script sources
  <Mod>/                   pack source folder (db/, text/db/, script/, ui/)
  <Mod>.pack               built pack, as installed in the game's data/ folder
```

## Where things live on the author's machine
Placeholders, so no personal paths land in this public repo:
- `<GAME>`: the Total War WARHAMMER III install; local mods go in `<GAME>/data/`.
- `<MASTERS>`: the RPFM MyMods folder in Dropbox (`$TWW3_MASTERS`, default
  `$HOME/Dropbox/RPFM My Mods`). Masters are the source of truth; `<MASTERS>/warhammer_3/` holds
  `<Mod>/`, `<Mod>.pack` and `_build_scripts/`.
- This repo: a git clone kept **outside Dropbox** (Dropbox and .git folders don't mix well).

## Build and release workflow
1. One time per machine: `bash tools/setup.sh`; for builders that read vanilla text also
   `python -I Faction_<Name>/_build_scripts/make_loc_cache.py`.
2. Edit the builder (DB/loc data) or the hand-written Lua/XML in the mod's source folder.
3. Build: delete the source folder's `db/` and `text/db/` (builder output; keep `script/`, `ui/`),
   run the mod's builder(s) into it, then `python -I build_pack.py <Mod> <Mod>.pack`.
   Exact commands per mod are in the faction CLAUDE.md. Builders need no network; they read
   `<GAME>/data/db.pack` (override with `$TWW3_DATA`).
4. Install: copy `<Mod>.pack` into `<GAME>/data/`. Save the source folder, pack and builder to
   `<MASTERS>/warhammer_3/` (and `_build_scripts/`). Verify both copies with `cmp`.
5. Repo: `bash tools/sync_from_masters.sh`, review `git status`, commit, push. Commit per mod
   change with a message naming the mod and version (e.g. `Druchii_Morathi_MOD v2: growth +20`).
6. Update `Faction_<Name>/docs/MOD_HISTORY.md` (what changed, untested/confirmed) and rewrite
   `docs/HANDOFF.md`.

Tips that keep sessions cheap and safe:
- Probe the game data with a small throwaway Python script using `twpack` (`table(db, name)`,
  `parse_loc`) instead of guessing keys; check CA's own uses of an effect/scope before reusing it.
- Write patch scripts with the Write tool; bash heredocs mangle backslashes in Lua/Python.
- DB fragments carry a random GUID, so rebuilt files differ byte-wise even when the rows are
  equal; compare parsed rows (`parse_db`) instead.
- Game script logs (`*_log.txt` in `<GAME>`) are the main test evidence; read them before
  theorising about crashes, and archive a copy with a `_testN_<topic>` suffix when useful.

## Adding a faction or a mod
- New faction: `bash tools/new_faction.sh <Name> <Prefix>` (e.g. `High_Elves Asur_`), then fill in
  its CLAUDE.md, set `.sync` globs, and add a row to the faction table in [README.md](README.md).
  If the faction's builders sit in the same `<MASTERS>/warhammer_3/_build_scripts/` as another
  faction, give each faction explicit `BUILD_GLOBS` so files aren't mirrored twice.
- New mod: name it `<Prefix><Subject>_MOD` (pack and source folder share the name; DB/loc
  fragments use the same name). Add a builder `build_<subject>.py` with a docstring that lists
  every change, add it to the faction's `.sync` `BUILD_GLOBS`, a row in the faction CLAUDE.md mod
  table, the player README, and a MOD_HISTORY section.
- Windows clones: DB fragment paths are long; clone into a short folder (e.g. `D:\Programming\TWW3`)
  or set `git config core.longpaths true`.
- Load order: a pack must out-prioritise another (e.g. Mixu's `!b_mixer`)? Prefix it `!!`. If it
  contains another modder's file, keep it out of the repo (see the hard rules).
