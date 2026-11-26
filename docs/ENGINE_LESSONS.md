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

## Characters, skills, followers and special settlements (studied 2026-11-25)
Source: a published Workshop mod that gives the Cult of Pleasure Slaanesh lords/heroes (read-only
study of its pack; nothing copied). Patterns below are CA-style and reusable for any faction.

### New lords / heroes for a faction (e.g. a Supreme Sorceress / Sorceress with Lore of Slaanesh)
- **Make a new agent subtype** (`agent_subtypes`, key like `<vanilla>_<lore>_<mod>`) instead of
  editing the vanilla one: `associated_unit_override` -> its own `main_units` / `land_units` rows
  (one per mount variant: `_0` foot, `_1.._5` mounts), `is_caster`, `auto_generate` (appears in the
  lord/hero pool), voice actor group from the vanilla subtype.
- **Allow it per faction:** `faction_agent_permitted_subtypes` (agent type + faction + subtype).
  Add the faction's rebel/separatist factions too.
- **Looks:** new `campaign_character_art_sets` (unique `art_set_id`, `agent_subtype`, `is_male`) +
  `campaign_character_arts` (uniform/animations copied from the vanilla art sets) + portrait
  entries for the new ids in the mod's own portrait files
  `ui/portraits/portholes/portrait_settings__<modname>.bin` and
  `ui/portraits/units/portrait_settings__<modname>.bin` (note the **double underscore**: vanilla is
  `portrait_settings__.bin`). Format v4: u32 version, u32 count, entries = id, head camera (5 f32 +
  str), u8 has-body (+ 5 f32 + str), u32 variants x (filename, diffuse, mask1, mask2, mask3).
- **Gender comes from the culture's hero row** (`agent_culture_details`: agent type + culture +
  `gender`). Dark Elf `dignitary` is `f` (Death Hag), so a Slaanesh Cultist given to a Dark Elf
  faction is generated female and needs **`is_male = False`** art sets, otherwise the game finds no
  art set and shows default (dwarf-like) portraits. Vanilla Cultist art sets are `is_male = True`
  (the Slaanesh/Chaos rows are `m`), although the model looks female.
- **Hero group names** in the recruit panel are `agent_culture_details_onscreen_name_<key>`, one per
  culture (DEF dignitary = 610 "Death Hag", spy = 619). They can only be renamed culture-wide (the
  mod used neutral names: 610 "Hierophant", 619 "Martinet").
- **Mounts:** new mount ancillaries per subtype (`ancillaries`, `ancillary_to_included_agents`,
  `ancillaries_included_agent_subtypes`) granted by mount skills
  (`character_skill_level_to_ancillaries_junctions`).
- **Lore of magic = skills in the tree:** the subtype's own `character_skill_node_sets` row
  (`agent_key`, `agent_subtype_key`) with nodes for the vanilla spell skills (e.g.
  `wh3_main_skill_sla_magic_slaanesh_01_lash_of_slaanesh` .. `_07_phantasmagoria`, plus the
  generic `wh_main_skill_all_magic_all_*`) in one row; those skills enable the spells.
- **Don't override CA scripts to register subtypes.** The mod replaced the whole
  `script/campaign/wh_campaign_experience_triggers.lua` to add its subtypes to CA's hero XP lists;
  that is what breaks it after every game patch. Hook in with your own listeners instead.

### New skill lines for existing lords / heroes (faction-only)
- Add `character_skill_nodes` rows **to the vanilla node set** with `faction_key` = the faction
  (only that faction sees them). `indent` = row (0 = top row; vanilla trees use 0-8, 99 = hidden
  scaling node), `tier` = column. Faction nodes appended to an existing row used high tiers
  (355, 356, 357) so they sort after the vanilla ones; a whole new line used a free `indent`.
- Chain them with `character_skill_node_links` (`parent_key`/`child_key`, link positions,
  `initial_descent_tiers`), lock alternatives with `character_skill_nodes_skill_locks` (pick one of
  several), describe levels in `character_skill_level_details`, effects in
  `character_skill_level_to_effects_junctions` (ability unlocks = `effect_bonus_value_unit_ability_junctions`
  "enable" effects, scope `character_to_character_own`; army auras `character_to_force_own`).
- One row set per faction: the mod repeats every node for the Cult, its separatists and Ssildra
  Tor (node keys suffixed with the faction).

### Followers, magic items and banners from another race
- Who can get an ancillary is its `faction_set`. Copy the source sets (members + the faction,
  `faction_set_items` faction rows) and point the ancillaries at the copies. CA's follower triggers
  and post-battle item drops are global and filtered by the faction set, so they start dropping for
  the faction. The mod also covered the shared Chaos-god sets
  (`anc_set_multi_*_slaanesh`): items such as Banner of Hellfire, Standard of Chaos Glory, Torment
  Blade, Etherblade.

### Special settlements switching culture (Ulthuan gates, Empire forts, Ziggurat of the Dawn)
- A special settlement's slot is a **building set** (`building_chain_set_items`), e.g.
  `wh3_main_primary_core_special_fort_emp`, `..._fort_eagle_gate` / `_gryphon_gate` /
  `_phoenix_gate` / `_unicorn_gate`, landmark `wh3_main_secondary_addon_landmark_ziggurat_of_dawn_beacon`.
  The owner gets whichever chain in that set it may build; on capture the game converts it.
- To give one faction its own version: copy the closest vanilla variant chain (e.g. the `_chaos`
  one) as a new chain (`building_chains`, `building_levels`, upgrades/downgrades,
  `campaign_settlement_display_building_ids` -> same model, slot unlocks, cai values), put it in the
  same set (`building_chain_set_items`) and the culture's availability set
  (`building_chain_availability_sets`, e.g. `wh2_main_bas_def`), then `building_culture_variants`:
  the copy disabled for everyone and enabled for the faction, every other variant in that set
  disabled for the faction. Effects on the copy: e.g. `wh3_main_effect_corruption_slaanesh_buildings`
  (`region_to_region_own` or `region_to_province_own`). No script needed.

### Start-up crash from renamed group keys (2026-11-25)
- Copying units/subtypes with renamed keys: some vanilla groups are **named after the unit or
  subtype** (`land_units.attribute_group` = the land unit key, `main_units.ui_unit_group_land` = the
  subtype key for the Cultist, a `unit_sets` row named after a garrison unit). Renaming the
  reference without copying the group row made the game close at the start-up logos (no dump).
  Copy `unit_attributes_groups` + `unit_attributes_to_groups_junctions` and `ui_unit_groupings` too.
- `tools/refcheck.py <mod folder> [other packs]` checks every schema reference column of a mod's
  tables against vanilla + the given packs + the mod. Misses that point at engine enum tables (not in
  db.pack: campaign_anim_set_enums, audio_vo*, unit_training_level_enum, ...) are normal.
- **Never add rows to `main_unit_ownership_content_pack_junctions` (or
  `agent_subtype_ownership_content_pack_junctions`).** Copying a vanilla unit's DLC-ownership row
  for a new unit made the game close a few seconds after Play (no dump, no log), even for a single
  Sorceress copy; found by a cumulative table-by-table ladder of test packs (2026-11-25). Modded units
  and subtypes without ownership rows are always available.
- Bisecting a start-up crash: build cumulative test packs (each step self-contained, checked with
  `tools/refcheck.py`), enable exactly one per start, and confirm the active list in
  `%APPDATA%\The Creative Assembly\Warhammer3\logs\modified.log` ("Mod:" lines) after every run.
- **Overriding vanilla loc keys:** put them in a loc file whose name sorts before vanilla's
  (`text/db/<table>__.loc`), e.g. `text/db/!!<mod>_overrides.loc`. The first file defining a key
  wins, compared case-insensitively: `text/db/Druchii_<mod>.loc` lost to `agent_culture_details__.loc`
  (a < d) but beat `event_feed_strings__.loc` (d < e; the Cult's how-they-play text override works).
  A `!!` name beats every vanilla file (2026-11-26). New keys can live in any loc file.
- **Lore tabs in the lord recruitment list** come from **`agent_subtypes.magic_lore`** (lords only;
  heroes leave it empty), e.g. `wh2_main_lore_dark_magic`, `wh_main_lore_fire`,
  `wh3_main_lore_slaanesh`. Changing `main_units.ui_unit_group_land` (v6) or the unit's spell group
  `special_ability_groups_to_units_junctions.ability_group` (v8) did not move a copied lord out of the
  Dark Magic tab (2026-11-26). Set all three for a lore copy: magic_lore for the tab, the spell group
  for the battle spell bar, the UI group for unit grouping.
- **Regiments of Renown pools come from the campaign's starting state, not the DB pool tables.** For
  the Cult, neither `units_to_exclusive_faction_permissions` allowed=False nor moving the regiments'
  `mercenary_pool_to_groups_junctions` rows to another pool changed the list in a new campaign
  (2026-11-26). Change a faction's pool by script on the first tick:
  `cm:add_unit_to_faction_mercenary_pool(faction, unit, "wh3_main_regiments_of_renown_pool", count,
  replenish_chance, cap, max_per_turn, "", "", "", partial_replenishment, unit_group)` (CA's Imrik
  dragon script; there is no remove function, so unwanted ones get count 0 / cap 0 plus an event
  restriction lock). Untested result at the time of writing: see the Cult log's "RoR pool" lines.
- **Character pictures where no character exists yet** (building browser "recruits" icons) come from
  `units_custom_battle_permissions.general_portrait` of the unit; without a row the game shows the
  unit card (the vanilla Cultist's is literally `placeholder`; a card name with no image shows "?").
  A copied hero/lord unit needs a row; faction = the mod's own campaign faction keeps it out of
  custom battles (2026-11-26).
