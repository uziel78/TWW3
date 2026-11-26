# Handoff: Faction_Dark_Elves

Last updated: 2026-11-26. Rewrite this file at the end of every session; history goes in
[MOD_HISTORY.md](MOD_HISTORY.md).

## State
- **Druchii_Cult-Characters_MOD v10** (builder `_build_scripts/build_cult_characters.py`; build the
  Cult pack first, this one reads its unit sets). Confirmed in game: loads; Sorceress (Slaanesh) and
  Supreme Sorceress (Slaanesh) with Lore of Slaanesh, spells cast in battle, own Lore of Slaanesh lord
  tab; Cultist of Slaanesh with the right portraits; Dark Elf hero tab "Priestess".
  v10 (building browser pictures for the new units) is untested.
- **Druchii_Cult-of-Pleasure_MOD v26.** Confirmed in game (v25, new campaign): loads; Regiments of
  Renown list is the agreed one (Raven Heralds, Bringers of Beguilement, Ravagers of Rakarth,
  Slaanesh's Harvesters, Scourge of Arden, Chill of Sontar, Siren of Red Ruin).
  Untested:
  - v26 RoR batch 2 (Pleasure Guard, Princes of Perfection, Riders of the Mighty Serpent, Eternal
    Entourage), added on the next load of any campaign (own saved flag).
  - Summoned Daemon Prince of Slaanesh (Pleasure Cult tier 5, 1 per tier 5 temple, 2000 / 500,
    bound Okkam's Mindrazor + Enfeebling Foe, Obsessive Adoration, Feasting on Fear).
  - Seekers of Slaanesh cap (3 +1 per House of Pleasure; count in the 6 daemon units per army).
  - Pact popup hidden at the start; Cult of Excess veterans (units rank 1-4, lords/heroes level 6).
  - N'Kari's extra units and income removed (left for a later N'Kari mod); alliance, relations,
    trade and Allegiance kept.
- **Druchii_Morathi_MOD v2**, **Druchii_Naggarond_MOD**, others: unchanged.
- Tools: `tools/refcheck.py` (run it on every new pack). Build packs from the masters' mod folder,
  never from a scratch copy (a stale copy dropped five tables once).

## Pending in-game tests
- Cult campaign load: the four new RoR in an army's Regiments of Renown list.
- A tier 5 Pleasure Cult: Daemon Prince card, abilities, two uses of each bound spell, cap; Seekers
  queued past the cap or past 6 daemon units per army are cancelled and refunded.
- New campaign turn 1: no "Dark Prince's Pact" popup but Allegiance with N'Kari / Cult of Excess in
  diplomacy; Arathar's units ranked; Cult log line "Cult of Excess veterans: ...".
- Building browser: Den of Indulgence shows the Cultist picture, Sorceress' Abode the Sorceress one.
- Characters: Sorceress (Slaanesh) at the Abode, mounts, Cultist cap and rank per Den tier.
- Cult v16-v21 features: Dread Manse / Palace of Pleasure, levy caps and auto-cancel, hidden
  Dreadspears card, 6 allied units, rite upkeep text.

## Open questions / known gaps
- The six removed RoR are zeroed and locked by script; the in-game list no longer showed them (v25).
- Never read a faction's mercenary pool from script (`faction:mercenary_pool()` crashed the load).
- CA's hero XP script (`wh_campaign_experience_triggers.lua`) has fixed subtype lists without the new
  subtypes (only that script's passive XP).
- Rewrite the how-they-play popup text when the Cult changes are complete.
- Cult copy of the Pleasure Cult chain to remove the inert Death Hag building rows: not done.
- A lord version of the Daemon Prince of Slaanesh may come later (the unit key says "summoned").

## Pick up here
Get the results for the v26 RoR batch and the Daemon Prince / Seekers caps; adjust numbers as the
author asks.
