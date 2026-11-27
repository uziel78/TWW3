# Handoff: Faction_Dark_Elves

Last updated: 2026-11-27. Rewrite this file at the end of every session; history goes in
[MOD_HISTORY.md](MOD_HISTORY.md).

## State

- **Druchii_Cult-of-Pleasure_MOD v33.** Confirmed in game (2026-11-27): a new campaign loads and plays
  turn 1 with all three packs; "Offer to the Dark Prince" replaces Raze on the Cult's capture screen
  (captives enslaved, no gold). Untested: the offering's extras from turn 2 (+30 / +45 slaves per
  settlement level via the "The Dark Prince Is Pleased" incident, +10 +5 per level Slaanesh corruption),
  RoR batch 2, Summoned Daemon Prince, Seekers cap, Morathi's corruption sorcery and Morathi's Will
  (from turn 2), Kharibdyss and Feral Manticore removed (chain, exclusion, script lock), Morathi's
  starting-skill fallback (turn 2).
- **Script rule:** no character reads or changes during turn 1 except the first-tick setup itself (see
  MOD_HISTORY, CRASH 9). New character features start on turn 2 (or at PendingBattle).
- **Mark of Slaanesh** (Cult unit list): Sorceresses of Dark Magic and Slaanesh only; Supreme Sorceresses
  of Dark Magic and Slaanesh; the High Beastmaster; the Master and the Khainite Assassin. Morathi and the
  other lores don't have it; Preyton, War Hydra and Doomfire Warlocks stay unmarked (author's choice).
- **Druchii_Morathi_MOD v14.** Her tree: Doombolt, Hysterical Frenzy, own Blessed by Evil, own A Thousand
  & One Dark Blessings (barrier +222 / +444; her unit has 666 barrier), A Dark Dalliance daemons only,
  Student of the Dark Tower and the two Gates of Slaanesh on her top line, Cult red line, "Temptress
  Supreme" (her weaker copy of N'Kari's Harvester of Souls) for Stand or Die!. She starts with Hekarti's
  Blessing and The First Sorceress (points on creation; Cult script fallback at turn 2). Untested.
- **Druchii_Cult-Characters_MOD v18.** Cult-only skill trees (faction node sets) for every Sorceress and
  Supreme Sorceress lore and the High Beastmaster. Supreme Sorceresses: Dark Radiance (the Fiendish Musk
  aura) and Veil of Excess (barrier 600) in the red line. Cultist: Mistress of Debauchery, Maintain Slave
  Stock, no Establish Cult. Untested in game.
- **Cult red line** (`_build_scripts/cult_army_skills.py`, identical rows in the Morathi and characters
  packs): Line Breaker, Sheafmaster, Raid Leader, Lash Master, Champion of Excess, Daemonologist, then
  rank 7 Bound in Rapture, Morathi's Will, Chosen of Excess, Rapture of Blades. The High Beastmaster keeps
  Strength Through Spite and Kindle the Fury for now.
- Tools: `tools/refcheck.py` (run it on every new pack; engine-list misses and MIXER faction keys are
  normal). Build packs from the masters' mod folders, never from a scratch copy.

## Pending in-game tests

- Offer to the Dark Prince on turn 2+: the incident shows +N slaves, province corruption rises, Cult log
  line "Offer to the Dark Prince at ..." (or "settlement level not readable").
- New Cult campaign: Morathi starts with Hekarti's Blessing and The First Sorceress; her tree and texts
  (Temptress Supreme quote); barrier bar; Sorcery of Excess from turn 2.
- Supreme Sorceress, Sorceress and High Beastmaster trees and the Mark of Slaanesh on their unit cards;
  Dark Radiance and Veil of Excess in battle.
- Cultist skills, Daemon Prince at a tier 5 Pleasure Cult, Seekers cap, Beastmasters without Kharibdyss
  and Feral Manticore.

## Open questions / known gaps

- The Dark Elf Raze is regrouped to every Dark Elf faction except the Cult (base game + MIXER); a Dark Elf
  faction added by another mod would lose Raze. The Cult pack names MIXER's four Dark Elf factions.
- The percentage barrier effect in Morathi's Sorcery of Excess is defined by CA but unused; unproven.
- Later: High Beastmaster's two red-line slots, the Daemon Prince lord version, the how-they-play text
  once the Cult is finished, the Cult copy of the Pleasure Cult chain (inert Death Hag rows).

## Pick up here

Get the turn-2+ results for Offer to the Dark Prince and the new-campaign checks above; adjust numbers and
texts as the author asks.
