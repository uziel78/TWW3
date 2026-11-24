# Faction_Dark_Elves: rules for Claude

Read the repo-root CLAUDE.md first; everything there applies here. Current state and the next
step: [docs/HANDOFF.md](docs/HANDOFF.md). Full dated design/test log: [docs/MOD_HISTORY.md](docs/MOD_HISTORY.md).

- Mod prefix: `Druchii_` (packs, source folders, DB/loc fragment names). `!!Druchii_` loads ahead
  of Mixu's `!b_mixer`.
- Masters: `<MASTERS>/warhammer_3/` (mods) and `<MASTERS>/warhammer_3/_build_scripts/`.

## Mods
| Mod | What it changes | Builder(s) | Status |
|---|---|---|---|
| `Druchii_Units_MOD` | Dark Elf unit abilities/attributes (all factions); Bleakswords weapon copy; Dark Riders 2 agile mount | `build_units.py` | Bleakswords confirmed; rest untested |
| `Druchii_Naggarond_MOD` | Malekith's faction: starting army, slave tribute, faction effects, Decrees of the Witch King (Ages) | `build_naggarond_data.py`, `build_black_council.py` + Lua | Tribute and decrees confirmed; latest tweaks untested |
| `Druchii_Malekith_MOD` | Malekith's lord effects (innate skill), Malekith's Legion, Circlet of Iron | `build_malekith.py` + `malekith_scripts/` | Untested (v4) |
| `!!Druchii_Malekith_MOD_faction_screen` | Mixu's `campaign_select_new.twui.xml` copy that hides Malekith's "+0%" lord-effect row. **`<MASTERS>` only, not in this repo** (Mixu's file) | hand-edited XML | Untested; re-make when Mixu updates (`malekith_ui_mixu_source.txt`) |
| `Druchii_Cult-of-Pleasure_MOD` | Morathi's faction: army, buildings, Mark of Slaanesh, caps, rite, pacts, garrisons, stance | `build_cult.py` (needs `loc_en.pkl`) + Lua | Mostly confirmed; see HANDOFF for pending tests |
| `Druchii_Morathi_MOD` | Morathi's lord effects only: hero upkeep -50% in her army, growth +20 in her province | `build_morathi.py` | Untested (v2) |

Planned: a Morathi + Sorceress + Supreme Sorceress **skills** mod (separate from Druchii_Morathi_MOD;
don't touch her skill tree elsewhere). `build_bg.py` is the retired BlackGuard_MOD builder (kept
for reference; replaced by Druchii_Units_MOD).

## Build commands
From `_build_scripts/` (run `bash ../../tools/setup.sh` once). For each mod: delete `../<Mod>/db`
and `../<Mod>/text/db`, run the builder(s), then pack:
```
python -I build_units.py ../Druchii_Units_MOD
python -I build_naggarond_data.py ../Druchii_Naggarond_MOD && python -I build_black_council.py ../Druchii_Naggarond_MOD
python -I build_malekith.py ../Druchii_Malekith_MOD && cp -r malekith_scripts/script ../Druchii_Malekith_MOD/
python -I make_loc_cache.py   # once, for build_cult.py
python -I build_cult.py ../Druchii_Cult-of-Pleasure_MOD
python -I build_morathi.py ../Druchii_Morathi_MOD
python -I build_pack.py ../<Mod> ../<Mod>.pack
```
`!!Druchii_Malekith_MOD_faction_screen` has no builder and lives only in `<MASTERS>/warhammer_3/`:
edit its XML there and run `build_pack.py` on that folder.
Lua lives in each mod's `script/` folder (Malekith's in `_build_scripts/malekith_scripts/`).
Units and Cult builders re-copy overridden vanilla rows from the game data: **rebuild after
CA patches.**

## Faction keys and facts
- Naggarond: faction `wh2_main_def_naggarond`, Malekith innate `wh2_main_skill_innate_def_malekith`,
  faction-effects override row `wh2_main_def_malekith` in `faction_starting_general_effects`.
- Cult of Pleasure: faction `wh2_main_def_cult_of_pleasure`, Morathi innate
  `wh2_main_skill_innate_def_morathi`, skill set `wh2_main_skill_node_set_def_morathi`, starting
  bundle override `wh2_main_def_morathi` → `druchii_cult_faction_effects`.
- CA context expression for Cult-only building effects: `IsFactionMorathi`.
- Allies used by the Cult: N'Kari `wh3_main_sla_seducers_of_slaanesh`, vassal Cult of Excess
  `wh2_main_def_cult_of_excess`; Ghrond `wh2_main_def_ghrond`.
- Script logs (in `<GAME>`): `naggarond_faction_mod_log.txt`, `druchii_cult_of_pleasure_log.txt`
  (`DEBUG_LOG` flag in each script).
- Author decisions not to re-ask: Raven Heralds RoR get no Devastating Flanker; Dark Riders 2
  360-degree fire arc declined; Cult keeps Naggarond's tribute and Age diplomacy lines.
