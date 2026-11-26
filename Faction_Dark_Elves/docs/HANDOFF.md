# Handoff: Faction_Dark_Elves

Last updated: 2026-11-26. Rewrite this file at the end of every session; history goes in
[MOD_HISTORY.md](MOD_HISTORY.md).

## State
- **Druchii_Cult-Characters_MOD v10** (builder `_build_scripts/build_cult_characters.py`; build the
  Cult pack first, this one reads its unit sets). Confirmed in game: loads; Sorceress (Slaanesh) and
  Supreme Sorceress (Slaanesh) with Lore of Slaanesh, spells cast in battle, own Lore of Slaanesh lord
  tab; Cultist of Slaanesh with the right portraits; Dark Elf hero tab "Priestess".
  v10 (building browser pictures for the new units) is untested.
- **Druchii_Cult-of-Pleasure_MOD v24** (data) + Lua section 16. Untested: Regiments of Renown set by
  script (needs a new campaign), N'Kari / Cult of Excess +600 gold per turn, Arathar's new extra
  units (3 Darkshards (Shields), 2 Reaper Bolt Throwers). The how-they-play popup text override works
  (to be rewritten once the faction changes are finished). Hero-label listeners stay off.
- **Druchii_Morathi_MOD v2**, **Druchii_Naggarond_MOD**, others: unchanged.
- Tools: `tools/refcheck.py` (run it on every new pack). Loc overrides of vanilla keys need a file
  that sorts before vanilla's (`!!` prefix); see docs/ENGINE_LESSONS.md.

## Pending in-game tests
- New Cult campaign: RoR screen (six removed ones gone or locked with "This regiment does not serve
  the Cult of Pleasure", Scourge of Arden and Bringers of Beguilement listed); Cult log lines
  "RoR pool before/after" and "N'Kari +600 gold" / "Cult of Excess +600 gold"; Arathar's army.
- Building browser: Den of Indulgence shows the Cultist picture, Sorceress' Abode the Sorceress one.
- Characters: Sorceress (Slaanesh) recruitable at the Abode, mounts change the model, Cultist cap and
  rank per Den tier.
- Cult v16-v21 features: Dread Manse / Palace of Pleasure, levy caps and auto-cancel, hidden
  Dreadspears card, 6 allied units, rite upkeep text.

## Open questions / known gaps
- If the RoR script can't remove the six from the list, they stay visible but locked; a real
  removal would then need the startpos (not possible from a DB/script mod) or a UI hide.
- CA's hero XP script (`wh_campaign_experience_triggers.lua`) has fixed subtype lists without the new
  subtypes (only that script's passive XP).
- Rewrite the how-they-play popup text when the Cult changes are complete.
- Cult copy of the Pleasure Cult chain to remove the inert Death Hag building rows: not done.

## Pick up here
Get the new-campaign results (RoR screen + the Cult log) and the building-browser pictures; fix the
RoR approach if the log shows the pool wasn't changed.
