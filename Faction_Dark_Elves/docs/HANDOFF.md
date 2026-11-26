# Handoff: Faction_Dark_Elves

Last updated: 2026-11-26. Rewrite this file at the end of every session; history goes in
[MOD_HISTORY.md](MOD_HISTORY.md).

## State
- **Druchii_Cult-of-Pleasure_MOD v29.** Confirmed in game: v25 loads, Regiments of Renown list as
  agreed, the faction mechanics list (no Black Arks) and the pact popup is gone. Untested: RoR batch 2,
  Summoned Daemon Prince (2000 / 500, bound spells), Seekers cap, Morathi's corruption sorcery (Lua
  section 17), Kharibdyss removed (chain, exclusion, script lock), Morathi's Will line of sight (Lua
  section 18).
- **Druchii_Morathi_MOD v12.** Her tree: Doombolt for Melkoth's Mystifying Miasma (own starting-spell
  dummy), Hysterical Frenzy for Doom & Darkness, own Blessed by Evil, own A Thousand & One Dark
  Blessings (barrier +222 / +444; her unit has 666 barrier), A Dark Dalliance daemons only (own effects),
  Student of the Dark Tower and the two Gates of Slaanesh on her top line, Cult red line,
  "Intoxicating Allure" (her weaker copy of N'Kari's Harvester of Souls) for Stand or Die!. Untested.
- **Druchii_Cult-Characters_MOD v16.** Cult-only skill trees (faction node sets) for every Sorceress
  and Supreme Sorceress lore and the High Beastmaster; Slaanesh copies changed in place. Sorceresses:
  no Cold One, one-level Gate of Slaanesh. Supreme Sorceresses: no Cold One / Manticore, Student and
  Gate of Slaanesh on the top line, Soporific Musk and Veil of Excess (barrier 600) in the red line.
  Cultist: Mistress of Debauchery, Maintain Slave Stock (with a visible text line), no Establish Cult.
  Untested in game (the skill-screen crash seen once stopped after the next update).
- **Cult red line** (`_build_scripts/cult_army_skills.py`, identical rows in the Morathi and characters
  packs): Line Breaker, Sheafmaster, Raid Leader, Lash Master, Champion of Excess, Daemonologist, then
  rank 7 Bound in Rapture, Morathi's Will, Chosen of Excess, Rapture of Blades. The High Beastmaster
  keeps Strength Through Spite and Kindle the Fury for now.
- Tools: `tools/refcheck.py` (run it on every new pack; engine-list misses such as bonus value ids are
  normal). Build packs from the masters' mod folders, never from a scratch copy.

## Pending in-game tests
- New Cult campaign: Morathi's tree and skill texts (Doombolt, Hysterical Frenzy, Gates, Student,
  daemons-only Dark Dalliance, Intoxicating Allure quote); barrier bar in battle; Morathi's Sorcery of
  Excess values in her effects panel; Cult log lines "Morathi's sorcery" and "Morathi's Will".
- Supreme Sorceress, Sorceress and High Beastmaster trees: mounts, top lines, the new red-line skills
  and their unit cards; Soporific Musk and Veil of Excess in battle.
- Cultist: Maintain Slave Stock adds slaves; Mistress of Debauchery growth; warshrine mount.
- Daemon Prince at a tier 5 Pleasure Cult, Seekers cap, Kharibdyss gone from the Beastmasters.

## Open questions / known gaps
- The percentage barrier effect in Morathi's Sorcery of Excess is defined by CA but unused; unproven.
- No character has a real 7th skill line; Morathi's extra skills sit on her top line.
- Later: High Beastmaster's two red-line slots, the Daemon Prince lord version, the how-they-play text
  once the Cult is finished, the Cult copy of the Pleasure Cult chain (inert Death Hag rows).

## Pick up here
Get the new-campaign test results for the skill trees and the Morathi features; adjust numbers and texts
as the author asks.
