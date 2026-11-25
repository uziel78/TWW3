# Handoff: Faction_Dark_Elves

Last updated: 2026-11-25. Rewrite this file at the end of every session; history goes in
[MOD_HISTORY.md](MOD_HISTORY.md).

## State
- **Druchii_Cult-of-Pleasure_MOD v15b** ("COP"): builder sections 1-26 + Lua sections 1-14.
  Confirmed: a new campaign loads past turn 1 (CRASH 8 fixed). Everything else in v14/v15 is
  untested in game:
  - Sacrifice to Slaanesh rite tile without the N'Kari flag behind the effects.
  - Dread Manse back to vanilla.
  - Slave Gate copy `druchii_cult_defence_major_1-3`: garrison Devotees / Devotees (Repeater
    Crossbows) instead of Shades.
  - Death Hag gone for the Cult; Slaanesh Cultist recruitable from Pleasure Cult tier 2 (Den of
    Indulgence), cap +1 per tier, rank +2 at tier 3, +4 at tiers 4-5.
  - Slave diktats: all 6 turns at vanilla cost; Open Markets +600 per turn for 6 turns (script).
  - Seekers of Slaanesh at Pleasure Cult 3-5; Spawn of Slaanesh at the Sorceress' Abode / Tower.
  - Beastmasters copy `druchii_cult_beasts_1-3`: Chaos Furies instead of Harpies ("Furies'
    Roost"), Preyton instead of the Black Dragon ("Preyton's Pen"); Beastmaster follower still
    drops.
  - 20 Slaanesh followers and magic items available to the Cult.
  - Lua `DEBUG_LOG` still on.
- **Druchii_Morathi_MOD v2**: two add-only rows on Morathi's innate skill (Hero upkeep -50 in her
  army, +20 growth in her province). Untested.
- **Druchii_Naggarond_MOD**: AI decree stall fixed; Cult excluded from decrees.
- `!!Druchii_Malekith_MOD_faction_screen` (edited copy of Mixu's UI file) stays out of this public
  repo; it is still in the first commit's history (8026a4e).

## Pending in-game tests
- Cult v14/v15 items listed above.
- Morathi v2: faction screen shows the two new lines; Hero upkeep about half; +20 growth.
- Cult: +1 Sorceress capacity on major settlements tiers 2-5; Dreadspears lock (needs Halls of
  Ravaging `druchii_cult_barracks_3` in the selected army's province).

## Open questions for the author
- Cult copy of the Pleasure Cult chain to remove the inert Death Hag building rows entirely? Big
  change (Daemonette caps, rite unlock, garrisons); not done.
- Purge the Mixu file from git history too? (rewrite + force push; not done)

## Pick up here
Get the v15b in-game test results and fix anything missing; then the Morathi v2 result. The
Morathi + Sorceress + Supreme Sorceress skills mod is the known next big item.
