# Handoff: Faction_Dark_Elves

Last updated: 2026-11-25. Rewrite this file at the end of every session; history goes in
[MOD_HISTORY.md](MOD_HISTORY.md).

## State
- **Druchii_Morathi_MOD v2** (new, untested): two add-only rows on Morathi's innate skill
  `wh2_main_skill_innate_def_morathi` ("Dark Manipulator"); her 3 vanilla effects stay.
  - `wh2_dlc14_effect_upkeep_reduction_heroes` -50, scope `general_to_force_own` (Repanse's trait
    uses -50). Her tree has only army-wide upkeep (Absolute Devotion -30, Renowned & Feared -8,
    Quartermaster up to -10), which stacks with this.
  - `wh_main_effect_province_growth_characters` +20, scope `character_to_province_own` (Lord
    Kroak's innate uses +20; Malekith's Efforts Redoubled +25). Theme: sycophants flocking to her.
    The VC Banshee's +10 is a hero passive action, not used here.
  - Other second-effect ideas offered and not picked: leadership aura size, movement after a win,
    Chaos attrition immunity, unit XP gain.
- **Druchii_Cult-of-Pleasure_MOD**: builder sections 1-23 + Lua; confirmed in game: Daemonette
  auto-cancel, rite adjacent-province corruption, Devotees in garrisons, Ghrond relations, no
  turn-7 stall, rite upkeep reduction on unit cards. Lua `DEBUG_LOG` still on.
- **Druchii_Naggarond_MOD**: AI decree stall fixed (AI picks a random Age, no dilemma); Cult
  excluded from decrees.
- Repo created 2026-11-25; `twpack.py` now also finds `pylib/` and `schemas/` in `tools/`, and
  `make_loc_cache.py` rebuilds `loc_en.pkl` (verified identical to the old cache).

## Pending in-game tests
- Druchii_Morathi_MOD v2: faction screen shows the two new lines; Hero upkeep about half in her
  army; +20 growth in the growth breakdown of her current province (existing saves should work).
- Cult: +1 Sorceress capacity on major settlements tiers 2-5; Dreadspears lock (needs Halls of
  Ravaging `druchii_cult_barracks_3` in the selected army's province).

## Open questions for the author
- Results of the Morathi v2 test.

## Pick up here
Get the Morathi v2 test result and fix anything missing; then ask what's next (the planned
Morathi + Sorceress + Supreme Sorceress skills mod is the known next big item).
