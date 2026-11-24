# TW:WH3 engine lessons (all factions)

Facts learned from in-game tests and CA's data while building these mods. Each point says what
works, what doesn't, and the CA pattern to copy. Add new lessons with the date and the test that
proved them; mod-specific history belongs in `Faction_<Name>/docs/MOD_HISTORY.md`.

## Testing and crashes
- **Launcher "override" checkbox** (under savegames) broke loading during tests. When a mod
  crashes on load, check launcher/save settings first, then test a new campaign with only that
  mod enabled.
- **Never trigger script dilemmas for AI factions** (`cm:trigger_dilemma`): the AI never answers
  and the end turn stalls at that faction's next turn start. Apply the AI's choice directly.
  `cm:trigger_incident` is a no-op for AI factions.
- **Turn-1 load:** don't change characters (effect bundles, skills) and then read/kill/spawn
  characters in the same tick. Iterating `faction:character_list()` after `cm:kill_character` in
  the turn-1 load crashed natively. Turn-1 `FactionTurnStart` fires during loading, before
  Continue. New-campaign first-tick callbacks run before every-load ones.
- **`cm:apply_dilemma_diplomatic_bonus` from a `FactionTurnStart` callback crashed** (with an ally
  and a vassal present). Use data instead: a `diplomatic_mod` effect in a bundle.
- **Encamp (`SET_CAMP`) for Dark Elf armies crashes natively**, however it is granted.
- **Unit sets for attributes/abilities: use explicit unit records.** A class-based set with 68
  record excludes, given `expendable`, crashed after loading; an explicit 732-unit list worked.
- **Hero/army panels:** reading recruitment queues via UI context on every selection crashed when
  a hero panel opened. Skip non-army selections and defer the read (`cm:callback`, 0.1 s, pcall).

## DB data
- **Mod loc entries that replace vanilla keys don't show on the pre-game faction screen**; new
  keys do, and DB row overrides do. Give custom bundles/effects new keys.
- **The faction-select screen lists every effect of the starting bundle**, `_unseen` ones too. Keep
  it short and apply mechanical parts by script (`cm:apply_effect_bundle(..., 0)` on load).
- **Lord effects on the faction screen = the startpos's innate skill key.** Replacing the skill or
  the skill node never shows there. Edit the vanilla skill's rows
  (`character_skill_level_to_effects_junctions`, keyed on skill + effect + level). Rows can't be
  deleted, only overridden (a zeroed row shows as "+0%"); a campaign-side swap to a clean copy is
  `cm:remove_skill_point` + `cm:character_details_pick_background_skill`.
- **`unit_cap` bonus values only work on units with `main_units.campaign_cap >= 0`.** Most units
  have -1 and ignore it. Per-army or per-building limits need a script lock
  (`add/remove_event_restricted_unit_record_for_faction`).
- **Faction-specific `building_units_allowed` rows need `enabled = True`** (all CA faction rows have
  it; non-faction rows have False). These rows can only add units, never remove them.
- **Per-faction buildings:** a `building_culture_variants` row with `faction` set and
  `disables = True` removes a building for that faction (CA does this ~99 times). For a
  faction-only version of a chain: copy the chain, disable the copy generally, enable it for the
  faction, disable the vanilla chain for the faction. Culture-variant loc key:
  `building_culture_variants_name_<building><culture><subculture><faction>`.
- **Per-faction building effects without copies:** `building_effects_junction.context_requirement`
  with an expression from `building_effect_context_expressions` (e.g. `IsFactionMorathi`).
- **Garrisons:** `building_level_armed_citizenry_junctions` + `armed_citizenry_unit_groups` +
  `armed_citizenry_units_to_unit_groups_junctions`. No faction column and no effect adds
  garrison units, so shared chains (settlement, walls) can't be faction-specific.
- **Faction-specific skill trees:** `character_skill_node_sets.faction_key` + node set items.
- **Faction-specific stances:** a `campaign_stance_effects_junctions` row with a faction.
  Stance types are engine-fixed; allied recruitment per stance is engine behaviour, not data.
- **Rites:** come from campaign groups (`campaign_group_rituals` + `campaign_group_members`).
  Lock/unlock as CA's `wh2_campaign_rites.lua` does (`cm:lock_ritual` / `cm:unlock_ritual`).
- **Corruption is per province.** Neighbouring provinces: CA's `..._adjacent_provinces` effects.
- **Diplomacy direction:** an effect "Diplomatic relations +n with X" on faction A raises X's
  attitude towards A. `diplomatic_attitude_towards` ignores effect bonuses.
- **Variable effect values:** `cm:create_new_custom_effect_bundle` + `set_effect_value`.
- **Allegiance** is per ally (favour points); no setter, but an incident payload
  `favour_points(faction, n)` grants it.
- **Weapon stats** (e.g. Bonus vs Infantry) must come from the weapon. A hidden passive looks
  like a different stat in the UI. Copy the weapon and override the one land unit row.
- **Unit cards and building browsers show base unit data.** Effect-granted attributes/abilities
  appear on units in armies and in battle.
- Effect bundle icons must exist in ui.pack `ui/campaign ui/effect_bundles/` (`politics.png`
  doesn't).
- No faction-level flat income effect exists (`gdp_other` is region-scoped); use
  `cm:treasury_mod` from script.

## Frontend / UI
- Frontend scripts can't reach the lord-effects panel of `campaign_select_new` once the lord
  screen opens. Change the twui XML instead (a `!!`-prefixed pack loading ahead of Mixu's
  `!b_mixer`), and re-make it whenever Mixu updates his copy.
- UI component calls must be pcall-guarded; `UIComponent(nil)` from a vanished child gives a
  broken object. `ChildCount` at the UI root isn't a number: start walks from a named component.
- Mixu's Unlocker owns the starting-unit preview: `mixer_add_starting_unit_list_for_faction`.
- A queued unit card (`QueuedLandUnit N`) can be cancelled with `SimulateLClick` (refunds).
- UI context property list: ui.pack `ui/metadata.json`.

## Startpos
- Starting armies, characters and the faction screen's army preview are baked into
  `startpos.esf` (Mixu ships his own). Change starting armies by script on the first tick of a new
  campaign; the pre-game army preview stays vanilla.
