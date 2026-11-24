# TWW3 mods

Campaign and unit mods for **Total War: WARHAMMER III**, grouped by faction. Each faction
folder holds the ready-to-use `.pack` files, their source folders and the Python builders that
generate the DB tables.

| Faction | Folder | Mods |
|---|---|---|
| Dark Elves | [Faction_Dark_Elves](Faction_Dark_Elves) | Units, Naggarond (Malekith), Malekith lord effects + faction screen, Cult of Pleasure (Morathi), Morathi lord effects |

## Using a mod
1. Copy the `.pack` file into the game's `data` folder.
2. Enable it in the launcher's mod manager.
3. Start a new campaign unless the mod's notes say an existing save works.

The mods are built and tested with **Mixu's Unlocker** enabled. Most mods need the Immortal
Empires campaign.

## Building from source
Requires Python 3.12 and a local game install.
```
bash tools/setup.sh                     # zstandard + RPFM's schema_wh3.ron into tools/
cd Faction_Dark_Elves/_build_scripts
python -I build_morathi.py ../Druchii_Morathi_MOD
python -I build_pack.py ../Druchii_Morathi_MOD ../Druchii_Morathi_MOD.pack
```
Per-mod commands are in each faction's `CLAUDE.md`. `twpack.py` reads the game data from the
default Steam path; set `TWW3_DATA` to your `.../Total War WARHAMMER III/data` if it differs.

Game data and text belong to Creative Assembly / Games Workshop. This repo holds only the mod
changes and the tools that produce them.
