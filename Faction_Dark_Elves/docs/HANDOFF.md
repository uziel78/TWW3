# Handoff: Faction_Dark_Elves

Last updated: 2026-11-26. Rewrite this file at the end of every session; history goes in
[MOD_HISTORY.md](MOD_HISTORY.md).

## State
- **Druchii_Cult-Characters_MOD v9** (new pack, Cult-only characters; builder
  `_build_scripts/build_cult_characters.py`). Confirmed in game: loads, new Cult campaign plays,
  Supreme Sorceress (Slaanesh) has her own Lore of Slaanesh tab, Dark Elf hero tab reads "Priestess".
  - Sorceress (Slaanesh) hero, Supreme Sorceress (Slaanesh) lord: copies of the Dark Magic ones with
    the Lore of Slaanesh, extra lore options next to the vanilla lores.
  - Cultist of Slaanesh: own subtype, female art sets with the vanilla Cultist portraits, recruited
    from the Den of Indulgence (Cult pack section 17 effects apply to it).
  - Build the Cult pack first: this builder reads the installed Cult pack's unit sets.
- **Druchii_Cult-of-Pleasure_MOD v22** (data) / Lua v21d. Includes v16 Dread Manse / Palace of
  Pleasure, v17 levy caps per settlement tier, v18-v19 flat 6 allied units and the reworked rite
  upkeep, v20 Regiments of Renown, v21 levy auto-cancel and the hidden Dreadspears card. The hero
  label listeners (Lua section 15) stay off: they caused the turn-1 black screen.
- **Druchii_Morathi_MOD v2**, **Druchii_Naggarond_MOD**: unchanged this session.
- Tools: `tools/refcheck.py` checks every schema reference of a mod folder (run it on every new
  pack). `twpack.py` rounds F32 to 4 decimals when reading; the characters builder disables that.

## Pending in-game tests
- Characters: Cultist portraits (female art sets), Sorceress (Slaanesh) recruitable at the Abode,
  spells cast in battle, mounts change the model, Cultist cap/rank per Den tier.
- Cult v16-v21: Dread Manse / Palace of Pleasure units and corruption; levy caps and auto-cancel;
  Dreadspears card hidden without Halls of Ravaging; 6 allied units; rite upkeep text; RoR list.
- Older: Morathi v2, Cult Sorceress capacity on major settlements.

## Open questions / known gaps
- The Cult pack's other vanilla-key loc overrides (e.g. the how-they-play popup text, section 15 of
  the builder) are in `Druchii_Cult-of-Pleasure_MOD.loc`, which sorts after vanilla's files: they
  probably don't show. Fix = move them to a `!!` loc file (not done).
- CA's hero XP script (`wh_campaign_experience_triggers.lua`) has fixed subtype lists; the new
  subtypes aren't in them (only matters for that script's passive XP).
- Cult copy of the Pleasure Cult chain to remove the inert Death Hag building rows: not done.
- Purge the Mixu file from git history: not requested.

## Pick up here
Get the in-game results for the pending tests above (characters first), then fix the Cult pack's
vanilla-key loc overrides with a `!!` loc file.
