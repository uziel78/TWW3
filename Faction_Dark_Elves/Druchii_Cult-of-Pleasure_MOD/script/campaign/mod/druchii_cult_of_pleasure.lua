-- Druchii_Cult-of-Pleasure_MOD (campaign): Morathi's faction, the Cult of Pleasure.
--
-- 1. Starting army: on the first tick of a new Immortal Empires campaign Morathi's army is
--    reshaped (vanilla: 2 Dreadspears, 2 Witch Elves, 1 Daemonettes, 2 Shades) into
--    2 Devotees of Slaanesh, 1 Devotees of Slaanesh (Crossbows), 1 Daemonettes of Slaanesh,
--    1 Dark Riders (Shields) and 1 Dark Riders (Repeater Crossbows).
-- 2. Starting hero: the Khainite Assassin she starts with is replaced by a Druchii Anointed
--    on the same spot.
-- 3. Starting building: the Conscription Halls at the Ancient City of Quintex is replaced by a
--    Den of Indulgence.
-- 4. Daemonette caps: 5 Daemonettes +1 per Den of Indulgence (tier 2+), 2 Exalted +1 per Halls
--    of Hedonism (tier 4+); +1 Khainite Assassin per Executioner's Hall. Mark of Slaanesh bundle.
-- 5. Unit limits (the units are uncapped in vanilla, so the game's own caps don't apply to them):
--    Daemonettes / Exalted past the Den/Hall caps or past 6 together in one army are cancelled
--    and refunded right after being queued, with a short message (no card locks); Bleakswords,
--    Darkshards and Dreadspears past their levy caps the same way (v21; v11-v20 locked their cards).
--    The Dreadspears card is hidden where they can't be raised (no Halls of Ravaging in the army's
--    province, or no tier 3+ settlement), since the vanilla settlement building offers them.
-- 6. Levy caps: 1 Bleaksword per settlement, 1 Darkshards per tier 2+ and 1 Dreadspears per tier 3+ settlement.
-- 7. The Cult's own Conscription Halls, House of Assassins, Slave Gate and Beastmasters chains
--    replace any vanilla ones it owns (same tier). (Dread Manses: own Slaanesh version, builder section 25c.)
-- 8. Har Ganeth Executioners are locked for the Cult on every load.
-- 9. New campaign: the Cult starts in a military alliance with N'Kari (Seducers of Slaanesh) and
--    with the Cult of Excess as its vassal, each with +75 relations both ways (permanent bundles)
--    and +66 Allegiance both ways (incident payloads). Extra starting heroes: a Sorceress (Lore
--    of Dark Magic) near the White Tower of Hoeth in Saphery, a Khainite Assassin near Ghrond.
--    Trade agreements with both, and the Cult of Excess leader (Arathar) gets +2 Bleakswords,
--    +1 Darkshards and +2 Dark Riders (Repeater Crossbows); N'Kari gets +2 Daemonettes and
--    +2 Devoted Marauders of Slaanesh, and +1000 gold at each of his turn starts. Ghrond's relations
--    towards the Cult start at about 60.
-- 10. Units from allies (outside the Cult roster) are Expendable (bundle applied on load).
-- 11. Witch Elves have Pleasure Through Pain instead of Frenzy (bundle applied on load).
-- 12. Sacrifice to Slaanesh (the Cult's rite, locked until a House of Pleasure is built):
--     a magic item and followers; and the Sacrifice Slaves choice when an army enters Channelling.
-- 13. Dreadspears have Guardian (bundle applied on load).
-- 14. The Cult's Open Markets diktat: +600 gold when performed and at each of the next 5 turn starts.
-- 15. Hero panel: the Dark Elf hero group "Death Hag" relabel (OFF: caused the turn-1 black screen).
-- 16. Regiments of Renown: Cult pool set by script (two Slaanesh RoR added, six Dark Elf ones zeroed + locked).
--
-- Starting armies and heroes live in the campaign startpos, which can't be safely edited for
-- Immortal Empires, so this is done by script, as Druchii_Naggarond_MOD does for Malekith.
-- add_first_tick_callback_new only fires on a brand-new campaign, so loading a save never
-- touches the army again.

local FACTION_KEY = "wh2_main_def_cult_of_pleasure"
local NKARI_FACTION_KEY = "wh3_main_sla_seducers_of_slaanesh"   -- N'Kari, Seducers of Slaanesh
local MORATHI_SUBTYPE = "wh2_main_def_morathi"
local ASSASSIN_SUBTYPE = "wh2_main_def_khainite_assassin"
local ANOINTED_TYPE = "runesmith"                       -- the Druchii Anointed's agent type in the DB
local ANOINTED_SUBTYPE = "wh3_dlc27_sla_druchii_anointed"

-- While true, what happens is written to druchii_cult_of_pleasure_log.txt in the game folder.
local DEBUG_LOG = true
local LOG_FILE = "druchii_cult_of_pleasure_log.txt"

local function log(msg)
	out("Druchii_Cult-of-Pleasure_MOD: " .. msg)
	if not DEBUG_LOG then
		return
	end
	local ok, file = pcall(io.open, LOG_FILE, "a")
	if ok and file then
		file:write("[turn " .. tostring(cm:model():turn_number()) .. "] " .. msg .. "\n")
		file:close()
	end
end

---------------------------------------------------------------------------
-- 1. Starting army
---------------------------------------------------------------------------
local UNITS_TO_REMOVE = {
	"wh2_main_def_inf_dreadspears_0",
	"wh2_main_def_inf_dreadspears_0",
	"wh2_main_def_inf_witch_elves_0",
	"wh2_main_def_inf_witch_elves_0",
	"wh2_main_def_inf_shades_0",
	"wh2_main_def_inf_shades_0",
}

-- Result (with the vanilla Daemonettes, which stay): see the header.
-- If this changes, update the faction-screen preview list in
-- script/frontend/mod/druchii_cult_of_pleasure_frontend.lua too.
local UNITS_TO_ADD = {
	"wh3_dlc27_sla_inf_devotees_of_slaanesh",
	"wh3_dlc27_sla_inf_devotees_of_slaanesh",
	"wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows",
	"wh2_main_def_cav_dark_riders_1",   -- Dark Riders (Shields)
	"wh2_main_def_cav_dark_riders_2",   -- Dark Riders (Repeater Crossbows)
}

local function find_morathi(faction)
	local leader = faction:faction_leader()
	if not leader:is_null_interface() and leader:character_subtype(MORATHI_SUBTYPE) then
		return leader
	end
	local characters = faction:character_list()
	for i = 0, characters:num_items() - 1 do
		local character = characters:item_at(i)
		if character:character_subtype(MORATHI_SUBTYPE) then
			return character
		end
	end
	return nil
end

local function reshape_army(morathi)
	if not morathi:has_military_force() then
		log("Morathi has no army at start, army unchanged")
		return
	end
	local char_str = cm:char_lookup_str(morathi)
	for _, unit_key in ipairs(UNITS_TO_REMOVE) do
		cm:remove_unit_from_character(char_str, unit_key)
	end
	for _, unit_key in ipairs(UNITS_TO_ADD) do
		cm:grant_unit_to_character(char_str, unit_key)
	end
	log("starting army updated")
end

---------------------------------------------------------------------------
-- 9. New campaign: the pacts with N'Kari and the Cult of Excess, and the extra starting heroes
--    (all called from the first tick)
---------------------------------------------------------------------------
local PACT_CULT_BUNDLE = "druchii_cult_pact_nkari"                    -- Cult: relations +75 towards the Seducers
local PACT_NKARI_BUNDLE = "druchii_cult_pact_nkari_seducers"          -- Seducers: relations +75 towards the Cult
local PACT_EXCESS_BUNDLE = "druchii_cult_pact_excess"                 -- Cult: relations +75 towards the Cult of Excess
local PACT_EXCESS_VASSAL_BUNDLE = "druchii_cult_pact_excess_vassal"   -- Cult of Excess: relations +75 towards the Cult
local EXCESS_FACTION_KEY = "wh2_main_def_cult_of_excess"              -- starts as the Cult's vassal
local PACT_INCIDENT = "druchii_cult_incident_pact_nkari"              -- to the Cult
local PACT_ALLY_INCIDENT = "druchii_cult_incident_pact_ally"          -- to N'Kari and to the Cult of Excess
local PACT_ALLEGIANCE = 66

-- Extra starting heroes: { region next to which it starts, agent type, subtype, name for the log }
local STARTING_HEROES = {
	{ "wh3_main_combi_region_white_tower_of_hoeth", "wizard", "wh2_main_def_sorceress_dark", "Sorceress (Dark) near the White Tower of Hoeth" },
	{ "wh3_main_combi_region_ghrond", "spy", ASSASSIN_SUBTYPE, "Khainite Assassin near Ghrond" },
}

local function spawn_hero_near(region_key, agent_type, subtype, label)
	-- A valid spot near the settlement, as CA's invasion scripts find one (in the region first).
	local x, y = cm:find_valid_spawn_location_for_character_from_settlement(FACTION_KEY, region_key, false, true, 9)
	if not x or x < 0 then
		x, y = cm:find_valid_spawn_location_for_character_from_settlement(FACTION_KEY, region_key, false, false, 9)
	end
	if not x or x < 0 then
		log("no valid spot found near " .. region_key .. ", no " .. label)
		return
	end
	local hero = cm:create_agent(FACTION_KEY, agent_type, subtype, x, y, true)
	if hero then
		log(label .. " spawned at " .. x .. ", " .. y)
	else
		log("ERROR: " .. label .. " could not be spawned at " .. x .. ", " .. y)
	end
end

local function spawn_starting_heroes()
	for _, hero in ipairs(STARTING_HEROES) do
		local ok, err = pcall(spawn_hero_near, hero[1], hero[2], hero[3], hero[4])
		if not ok then
			log("ERROR on first tick (" .. hero[4] .. "): " .. tostring(err))
		end
	end
end

-- The Cult of Excess becomes the Cult's vassal (peace first, as CA's Hellebron/Nakai scripts do
-- with force_make_vassal), with the same relations bonus both ways as the N'Kari pact.
-- Arathar (the Cult of Excess faction leader, a Dreadlord) starts with a stronger army.
-- (2026-11-26, author: was 2 Bleakswords, 1 Darkshards, 2 Dark Riders (Repeater Crossbows).)
local EXCESS_EXTRA_UNITS = {
	"wh2_main_def_inf_darkshards_1",          -- Darkshards (Shields) x3
	"wh2_main_def_inf_darkshards_1",
	"wh2_main_def_inf_darkshards_1",
	"wh2_main_def_art_reaper_bolt_thrower",   -- Reaper Bolt Throwers x2
	"wh2_main_def_art_reaper_bolt_thrower",
}
local ARMY_SIZE_MAX = 20

-- N'Kari (the Seducers of Slaanesh faction leader) too, so he survives the early turns.
local NKARI_EXTRA_UNITS = {
	"wh3_main_sla_inf_daemonette_0",      -- Daemonettes of Slaanesh x2
	"wh3_main_sla_inf_daemonette_0",
	"wh3_main_sla_inf_marauders_0",       -- Devoted Marauders of Slaanesh x2
	"wh3_main_sla_inf_marauders_0",
}

-- Adds units to a faction leader's army (up to the 20-unit limit).
local function reinforce_faction_leader(faction_key, units, label)
	local faction = cm:get_faction(faction_key)
	if not faction or faction:is_null_interface() or faction:is_dead() or not faction:has_faction_leader() then
		log(label .. " not found, army unchanged")
		return
	end
	local leader = faction:faction_leader()
	if leader:is_null_interface() or not leader:has_military_force() then
		log(label .. " has no army, army unchanged")
		return
	end
	local char_str = cm:char_lookup_str(leader)
	local size = leader:military_force():unit_list():num_items()
	local added = 0
	for _, unit_key in ipairs(units) do
		if size + added >= ARMY_SIZE_MAX then
			log(label .. "'s army is full, not all units added")
			break
		end
		cm:grant_unit_to_character(char_str, unit_key)
		added = added + 1
	end
	log(label .. "'s army: +" .. added .. " units (was " .. size .. ")")
end

-- Allies' extra income at the start of each of their turns (cm:treasury_mod, as CA's scripts add
-- gold; the game has no faction-wide flat income effect). 2026-11-26, author: N'Kari 1000 -> 600,
-- and the Cult of Excess gets the same.
local ALLY_INCOME = {
	[NKARI_FACTION_KEY] = { gold = 600, label = "N'Kari" },
	[EXCESS_FACTION_KEY] = { gold = 600, label = "Cult of Excess" },
}
core:add_listener("druchii_cult_nkari_income", "FactionTurnStart",
	function(context) return ALLY_INCOME[context:faction():name()] ~= nil end,
	function(context)
		local faction_key = context:faction():name()
		local income = ALLY_INCOME[faction_key]
		local ok, err = pcall(function() cm:treasury_mod(faction_key, income.gold) end)
		if not ok then
			log("ERROR adding " .. income.label .. "'s income: " .. tostring(err))
		else
			log(income.label .. " +" .. income.gold .. " gold")
		end
	end, true)

local function make_excess_vassal()
	local excess = cm:get_faction(EXCESS_FACTION_KEY)
	if not excess or excess:is_null_interface() or excess:is_dead() then
		log("Cult of Excess not found, no vassal")
		return
	end
	cm:force_make_peace(FACTION_KEY, EXCESS_FACTION_KEY)
	cm:force_make_vassal(FACTION_KEY, EXCESS_FACTION_KEY)
	log("Cult of Excess made a vassal (" .. EXCESS_FACTION_KEY .. ")")
	cm:apply_effect_bundle(PACT_EXCESS_BUNDLE, FACTION_KEY, 0)
	cm:apply_effect_bundle(PACT_EXCESS_VASSAL_BUNDLE, EXCESS_FACTION_KEY, 0)
	log("Cult of Excess relations bundles applied")
end

-- Ghrond's relations towards the Cult raised to about 60. A "relations +n with X" effect on faction
-- A raises X's attitude towards A, so the bonus is on the Cult ("with Ghrond"; v1 put it on Ghrond,
-- which raised the Cult's attitude instead and left Ghrond at -10). Ghrond's attitude is measured
-- and the difference set on a custom copy of druchii_cult_courting_ghrond. Done once per campaign
-- (any save; a load step), and v1's bundle is removed from Ghrond.
local GHROND_FACTION_KEY = "wh2_main_def_ghrond"
local GHROND_OLD_BUNDLE = "druchii_cult_ghrond_courtship"   -- v1, on Ghrond
local CULT_GHROND_BUNDLE = "druchii_cult_courting_ghrond"   -- on the Cult
local GHROND_TARGET = 60
local GHROND_FALLBACK = 70   -- if the attitude can't be read (Ghrond starts at -10)
local GHROND_DONE_KEY = "druchii_cult_ghrond_v2"

local function court_ghrond()
	if cm:get_saved_value(GHROND_DONE_KEY) then
		return
	end
	local ghrond = cm:get_faction(GHROND_FACTION_KEY)
	local cult = cm:get_faction(FACTION_KEY)
	if not ghrond or ghrond:is_null_interface() or ghrond:is_dead() then
		log("Ghrond not found, relations unchanged")
		return
	end
	if ghrond:has_effect_bundle(GHROND_OLD_BUNDLE) then
		cm:remove_effect_bundle(GHROND_OLD_BUNDLE, GHROND_FACTION_KEY)
		log("Ghrond: old (wrong-way) relations bundle removed")
	end
	local start = nil
	pcall(function() start = ghrond:diplomatic_attitude_towards(FACTION_KEY) end)
	local bonus = GHROND_FALLBACK
	if type(start) == "number" then
		bonus = math.floor(GHROND_TARGET - start + 0.5)
	end
	cm:set_saved_value(GHROND_DONE_KEY, true)
	cm:set_saved_value("druchii_cult_ghrond_start", start)
	cm:set_saved_value("druchii_cult_ghrond_check_turns", 2)
	if bonus <= 0 then
		log("Ghrond already at " .. tostring(start) .. " towards the Cult, no bonus")
		return
	end
	local bundle = cm:create_new_custom_effect_bundle(CULT_GHROND_BUNDLE)
	local effects = bundle:effects()
	for i = 0, effects:num_items() - 1 do
		bundle:set_effect_value(effects:item_at(i), bonus)
	end
	bundle:set_duration(0)
	cm:apply_custom_effect_bundle_to_faction(bundle, cult)
	log("Ghrond towards the Cult: " .. tostring(start) .. ", Cult gets relations +" .. bonus
		.. " with Ghrond (target " .. GHROND_TARGET .. ")")
end

-- Check at the next two Cult turn starts after it was applied (log only).
core:add_listener("druchii_cult_ghrond_check", "FactionTurnStart",
	function(context)
		return context:faction():name() == FACTION_KEY and (cm:get_saved_value("druchii_cult_ghrond_check_turns") or 0) > 0
	end,
	function()
		pcall(function()
			cm:set_saved_value("druchii_cult_ghrond_check_turns", cm:get_saved_value("druchii_cult_ghrond_check_turns") - 1)
			local ghrond = cm:get_faction(GHROND_FACTION_KEY)
			local cult = cm:get_faction(FACTION_KEY)
			log("Ghrond towards the Cult now " .. tostring(ghrond:diplomatic_attitude_towards(FACTION_KEY))
				.. ", Cult towards Ghrond " .. tostring(cult:diplomatic_attitude_towards(GHROND_FACTION_KEY))
				.. " (start " .. tostring(cm:get_saved_value("druchii_cult_ghrond_start")) .. ")")
		end)
	end, true)

-- Trade agreements with both pact partners.
local function make_pact_trade_agreements()
	for _, key in ipairs({ NKARI_FACTION_KEY, EXCESS_FACTION_KEY }) do
		local other = cm:get_faction(key)
		if other and not other:is_null_interface() and not other:is_dead() then
			cm:force_make_trade_agreement(FACTION_KEY, key)
			log("trade agreement with " .. key)
		end
	end
end

-- Allegiance comes only through payloads (favour_points), so it's sent as incidents:
-- the Cult gets +66 with N'Kari and +66 with the Cult of Excess (one incident), and N'Kari and
-- the Cult of Excess each get +66 with the Cult (an incident each; AI factions see no message).
local function send_allegiance(incident_key, receiver_key, towards_keys)
	local receiver = cm:get_faction(receiver_key)
	if not receiver or receiver:is_null_interface() or receiver:is_dead() then
		return
	end
	local incident_builder = cm:create_incident_builder(incident_key)
	local payload_builder = cm:create_payload()
	local names = {}
	for _, key in ipairs(towards_keys) do
		local towards = cm:get_faction(key)
		if towards and not towards:is_null_interface() and not towards:is_dead() then
			payload_builder:favour_points(towards, PACT_ALLEGIANCE)
			names[#names + 1] = key
		end
	end
	if #names == 0 then
		return
	end
	incident_builder:set_payload(payload_builder)
	cm:launch_custom_incident_from_builder(incident_builder, receiver)
	payload_builder:clear()
	log("Allegiance +" .. PACT_ALLEGIANCE .. " for " .. receiver_key .. " with " .. table.concat(names, ", ")
		.. " sent (incident " .. incident_key .. ")")
end

local function grant_pact_allegiance()
	local steps = {
		{ PACT_INCIDENT, FACTION_KEY, { NKARI_FACTION_KEY, EXCESS_FACTION_KEY } },
		{ PACT_ALLY_INCIDENT, NKARI_FACTION_KEY, { FACTION_KEY } },
		{ PACT_ALLY_INCIDENT, EXCESS_FACTION_KEY, { FACTION_KEY } },
	}
	for _, step in ipairs(steps) do
		local ok, err = pcall(send_allegiance, step[1], step[2], step[3])
		if not ok then
			log("ERROR granting Allegiance (" .. step[2] .. "): " .. tostring(err))
		end
	end
end

---------------------------------------------------------------------------
-- 12. Sacrifice to Slaanesh (the rite) and the Sacrifice Slaves choice (Channelling)
---------------------------------------------------------------------------
-- The rite's payload applies druchii_cult_rite_slaanesh_bundle (DB) for 6 turns: upkeep, character
-- corruption and relations (+10 Slaanesh, +5 Elves/Chaos/Norsca) are all data. This script adds:
--   - each rite performed (no allied cap since v19):
--     a high-quality magic item for Morathi (or whoever leads the Cult) she doesn't have yet;
--   - each Cult turn start while the rite lasts: every lord has a small chance to attract a
--     pleasure-themed Dark Elf follower.
-- Sacrifice Slaves: when one of the player's Cult armies enters the Channelling stance (and the
-- Cult has at least 36 slaves), a dilemma offers to sacrifice 36 slaves (the dilemma's payload takes
-- them) for +15 more Winds of Magic for that army for a turn (force bundle, removed at the next Cult
-- turn start once that turn's Winds are in, or when the army leaves the stance).
-- Lessons kept: cm:apply_dilemma_diplomatic_bonus from a turn-start callback crashed the game, so
-- relations are data; nothing here reads characters during the turn-1 load.
local RITE_KEY = "druchii_cult_ritual_slaanesh"
local RITE_BUNDLE = "druchii_cult_rite_slaanesh_bundle"
local RITE_ALLIED_CAP_BUNDLE = "druchii_cult_rite_slaanesh_allied_cap"
local RITE_ALLIED_CAP_PER_RITE = 3
local RITE_FOLLOWER_CHANCE = 10   -- % per lord per turn while the rite lasts (about one in two lords over 6 turns)
local RITE_FOLLOWERS = {
	"wh2_main_anc_follower_def_cultist",               -- Pleasure Cultist
	"wh2_main_anc_follower_def_daemon_whisperer",      -- Daemon Whisperer
	"wh2_main_anc_follower_def_diplomat_slaanesh",     -- Dark Prince's Envoy
	"wh2_main_anc_follower_def_harem_keeper",          -- Harem Keeper
	"wh2_main_anc_follower_def_musician_choirmaster",  -- Evil Choirmaster
	"wh2_main_anc_follower_def_musician_drum",         -- Degenerate Kettle Drummer
	"wh2_main_anc_follower_def_musician_flute",        -- Deviant Flautist
}
-- The rite's gift: legendary (200) and rare (130-150) items Dark Elves can use.
local RITE_GIFTS = {
	"wh3_main_anc_weapon_slaaneshs_blade",               -- Slaanesh's Blade (legendary)
	"wh3_main_anc_enchanted_item_dreamwine",             -- Jug of Dreamwine (legendary)
	"wh2_main_anc_armour_armour_of_eternal_servitude",   -- Armour of Eternal Servitude (rare, Dark Elf)
	"wh2_main_anc_armour_armour_of_living_death",        -- Armour of Living Death (rare, Dark Elf)
	"wh2_main_anc_enchanted_item_black_dragon_egg",      -- Black Dragon Egg (rare, Dark Elf)
	"wh2_main_anc_enchanted_item_cloak_of_twilight",     -- Cloak of Twilight (rare, Dark Elf)
	"wh2_main_anc_weapon_blade_of_ruin",                 -- Blade of Ruin (rare, Dark Elf)
	"wh2_main_anc_weapon_chillblade",                    -- Chillblade (rare, Dark Elf)
	"wh_main_anc_armour_tricksters_helm",                -- Trickster's Helm (rare)
	"wh_main_anc_talisman_talisman_of_preservation",     -- Talisman of Preservation (rare)
}
local CHANNELLING_STANCE = "MILITARY_FORCE_ACTIVE_STANCE_TYPE_CHANNELING"
local SACRIFICE_DILEMMA = "druchii_cult_dilemma_channelling_sacrifice"
local SACRIFICE_BUNDLE = "druchii_cult_rite_slaanesh_channelling"   -- +15 Winds (key from v1)
local SACRIFICE_SLAVES = 36
local SACRIFICE_SAVED = "druchii_cult_sacrifice_armies"             -- { [cqi] = turn applied }
local sacrifice_pending_cqi = nil

local function rite_active(faction)
	return faction and not faction:is_null_interface() and faction:has_effect_bundle(RITE_BUNDLE)
end

local function rite_step(name, fn)
	log("rite step: " .. name)
	local ok, result = pcall(fn)
	if not ok then
		log("ERROR in rite step " .. name .. ": " .. tostring(result))
		return nil
	end
	return result
end

-- (Unused since v19: the rite no longer raises the allied unit cap. Kept for reference.)
-- The permanent allied unit cap: 3 per rite performed (saved count), on a custom bundle.
local function apply_rite_allied_cap()
	local rites = cm:get_saved_value("druchii_cult_rites_performed") or 0
	if rites <= 0 then
		return
	end
	local faction = cm:get_faction(FACTION_KEY)
	cm:remove_effect_bundle(RITE_ALLIED_CAP_BUNDLE, FACTION_KEY)
	local bundle = cm:create_new_custom_effect_bundle(RITE_ALLIED_CAP_BUNDLE)
	local effects = bundle:effects()
	for i = 0, effects:num_items() - 1 do
		bundle:set_effect_value(effects:item_at(i), RITE_ALLIED_CAP_PER_RITE * rites)
	end
	bundle:set_duration(0)
	cm:apply_custom_effect_bundle_to_faction(bundle, faction)
	log("rite: allied unit capacity +" .. RITE_ALLIED_CAP_PER_RITE * rites .. " (" .. rites .. " rites)")
end

-- The rite's gift: one item from RITE_GIFTS that the faction leader doesn't have yet.
local function give_rite_gift(faction)
	if not faction:has_faction_leader() then
		log("rite: no faction leader, no gift")
		return
	end
	local leader = faction:faction_leader()
	local options = {}
	for _, key in ipairs(RITE_GIFTS) do
		if not leader:has_ancillary(key) then
			options[#options + 1] = key
		end
	end
	if #options == 0 then
		log("rite: the faction leader has every gift already")
		return
	end
	local key = options[cm:random_number(#options)]
	cm:force_add_ancillary(leader, key, false, false)
	log("rite: gift " .. key .. " for " .. leader:character_subtype_key())
end

-- A small chance per lord to attract one pleasure-themed follower they don't have yet.
local function rite_followers(faction)
	local characters = faction:character_list()
	local gained = 0
	for i = 0, characters:num_items() - 1 do
		local character = characters:item_at(i)
		if not character:is_null_interface() and character:has_military_force()
			and not character:military_force():is_armed_citizenry()
			and cm:random_number(100) <= RITE_FOLLOWER_CHANCE then
			local options = {}
			for _, key in ipairs(RITE_FOLLOWERS) do
				if not character:has_ancillary(key) then
					options[#options + 1] = key
				end
			end
			if #options > 0 then
				local key = options[cm:random_number(#options)]
				cm:force_add_ancillary(character, key, false, false)
				gained = gained + 1
				log("rite: " .. character:character_subtype_key() .. " (cqi " .. character:command_queue_index()
					.. ") attracted follower " .. key)
			end
		end
	end
	return gained
end

local function remove_sacrifice(cqi, reason)
	local saved = cm:get_saved_value(SACRIFICE_SAVED) or {}
	saved[tostring(cqi)] = nil
	cm:set_saved_value(SACRIFICE_SAVED, saved)
	local force = cm:model():military_force_for_command_queue_index(cqi)
	if force and not force:is_null_interface() and force:has_effect_bundle(SACRIFICE_BUNDLE) then
		local winds = "?"
		pcall(function() winds = force:pooled_resource_manager():resource("wh3_main_winds_of_magic"):value() end)
		cm:remove_effect_bundle_from_force(SACRIFICE_BUNDLE, cqi)
		log("sacrifice: bonus removed from army " .. cqi .. " (" .. reason .. "), Winds of Magic now " .. tostring(winds))
	end
end

-- Cult turn start: sacrifices from an earlier turn have paid out (the Winds came in with the turn).
local function expire_sacrifices()
	local turn = cm:model():turn_number()
	local saved = cm:get_saved_value(SACRIFICE_SAVED) or {}
	for cqi, applied in pairs(saved) do
		if applied < turn then
			remove_sacrifice(tonumber(cqi), "turn passed")
		end
	end
end

local function rite_turn_start()
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() then
		return
	end
	rite_step("sacrifices", expire_sacrifices)
	if not rite_active(faction) then
		return
	end
	-- Followers: characters are only read from turn 2 (nothing reads characters in the turn-1 load).
	local followers = 0
	if cm:model():turn_number() >= 2 then
		followers = rite_step("followers", function() return rite_followers(faction) end) or 0
	end
	log("rite active: " .. followers .. " followers attracted")
end

core:add_listener("druchii_cult_rite_turn", "FactionTurnStart",
	function(context) return context:faction():name() == FACTION_KEY end,
	function()
		-- A moment after the turn starts (so that turn's Winds are in), outside the turn-start event.
		cm:callback(function()
			local ok, err = pcall(rite_turn_start)
			if not ok then
				log("ERROR in the Sacrifice to Slaanesh turn update: " .. tostring(err))
			end
		end, 0.5)
	end, true)

-- Entering Channelling: offer the sacrifice (player only, enough slaves, not already boosted).
-- Leaving it: the boost goes.
core:add_listener("druchii_cult_sacrifice_stance", "ForceAdoptsStance",
	function(context) return context:military_force():faction():name() == FACTION_KEY end,
	function(context)
		local ok, err = pcall(function()
			local force = context:military_force()
			local cqi = force:command_queue_index()
			if force:active_stance() ~= CHANNELLING_STANCE then
				if force:has_effect_bundle(SACRIFICE_BUNDLE) then
					remove_sacrifice(cqi, "left the Channelling stance")
				end
				return
			end
			local faction = force:faction()
			if not faction:is_human() or cm:get_local_faction_name(true) ~= FACTION_KEY
				or force:is_armed_citizenry() or force:has_effect_bundle(SACRIFICE_BUNDLE) then
				return
			end
			local slaves = 0
			pcall(function() slaves = faction:pooled_resource_manager():resource("def_slaves"):value() end)
			if slaves < SACRIFICE_SLAVES then
				log("sacrifice: army " .. cqi .. " entered Channelling, only " .. slaves .. " slaves, no offer")
				return
			end
			sacrifice_pending_cqi = cqi
			-- A moment later, outside the stance event.
			cm:callback(function()
				local ok2, err2 = pcall(function() cm:trigger_dilemma(FACTION_KEY, SACRIFICE_DILEMMA) end)
				if ok2 then
					log("sacrifice: offered for army " .. cqi)
				else
					log("ERROR offering the sacrifice: " .. tostring(err2))
				end
			end, 0.3)
		end)
		if not ok then
			log("ERROR in the Channelling stance check: " .. tostring(err))
		end
	end, true)

core:add_listener("druchii_cult_sacrifice_choice", "DilemmaChoiceMadeEvent",
	function(context) return context:dilemma() == SACRIFICE_DILEMMA end,
	function(context)
		local choice = context:choice()
		local cqi = sacrifice_pending_cqi
		sacrifice_pending_cqi = nil
		if choice ~= 0 or not cqi then
			log("sacrifice: declined")
			return
		end
		-- The payload has taken the slaves; give that army the boost a moment later.
		cm:callback(function()
			local ok, err = pcall(function()
				local force = cm:model():military_force_for_command_queue_index(cqi)
				if not force or force:is_null_interface() then
					log("sacrifice: army " .. cqi .. " is gone, no boost")
					return
				end
				cm:apply_effect_bundle_to_force(SACRIFICE_BUNDLE, cqi, 0)
				local saved = cm:get_saved_value(SACRIFICE_SAVED) or {}
				saved[tostring(cqi)] = cm:model():turn_number()
				cm:set_saved_value(SACRIFICE_SAVED, saved)
				local winds = "?"
				pcall(function() winds = force:pooled_resource_manager():resource("wh3_main_winds_of_magic"):value() end)
				log("sacrifice: +15 Winds for army " .. cqi .. " this turn (Winds of Magic now " .. tostring(winds) .. ")")
			end)
			if not ok then
				log("ERROR applying the sacrifice: " .. tostring(err))
			end
		end, 0.3)
	end, true)

-- The rite is locked until the Cult has a House of Pleasure (Pleasure Cult tier 3) or better, the
-- way CA's wh2_campaign_rites.lua handles the Dark Elf rites: locked for the human player on load,
-- unlocked (and saved as unlocked, with CA's "Rite unlocked" message) when one is completed or a
-- settlement with one is captured. A check of the Cult's own settlements on load and at each turn
-- start covers saves where one already stands.
local RITE_UNLOCKED_KEY = "druchii_cult_ritual_slaanesh_unlocked"
-- (Its own list: section 4's PLEASURE_CULT_TIER is defined further down the file.)
local RITE_BUILDINGS = {
	wh2_main_def_pleasure_cult_3 = true,   -- House of Pleasure
	wh2_main_def_pleasure_cult_4 = true,   -- Halls of Hedonism
	wh2_main_def_pleasure_cult_5 = true,
}

local function is_rite_building(name)
	return RITE_BUILDINGS[name] == true
end

local function cult_has_rite_building(faction)
	local regions = faction:region_list()
	for i = 0, regions:num_items() - 1 do
		local slots = regions:item_at(i):slot_list()
		for j = 0, slots:num_items() - 1 do
			local slot = slots:item_at(j)
			if slot:has_building() and is_rite_building(slot:building():name()) then
				return true
			end
		end
	end
	return false
end

local function unlock_cult_rite(show_message)
	local faction = cm:get_faction(FACTION_KEY)
	cm:unlock_ritual(faction, RITE_KEY)
	if not cm:get_saved_value(RITE_UNLOCKED_KEY) then
		cm:set_saved_value(RITE_UNLOCKED_KEY, true)
		log("Sacrifice to Slaanesh unlocked")
		if show_message and type(show_rite_unlocked_event) == "function" then
			pcall(show_rite_unlocked_event, FACTION_KEY, RITE_KEY)
		end
	end
end

-- On load: unlocked already, or a House of Pleasure already stands -> unlocked; else locked.
local function setup_cult_rite_lock()
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() or not faction:is_human() then
		return
	end
	if cm:get_saved_value(RITE_UNLOCKED_KEY) then
		cm:unlock_ritual(faction, RITE_KEY)
	elseif cult_has_rite_building(faction) then
		unlock_cult_rite(true)
	else
		cm:lock_ritual(faction, RITE_KEY)
		log("Sacrifice to Slaanesh locked until a House of Pleasure is built")
	end
end

core:add_listener("druchii_cult_rite_unlock_building", "BuildingCompleted",
	function(context)
		local building = context:building()
		return not cm:get_saved_value(RITE_UNLOCKED_KEY) and building:faction():name() == FACTION_KEY
			and is_rite_building(building:name())
	end,
	function()
		local ok, err = pcall(unlock_cult_rite, true)
		if not ok then
			log("ERROR unlocking the rite: " .. tostring(err))
		end
	end, true)

core:add_listener("druchii_cult_rite_unlock_capture", "GarrisonOccupiedEvent",
	function(context)
		if cm:get_saved_value(RITE_UNLOCKED_KEY) or context:character():faction():name() ~= FACTION_KEY then
			return false
		end
		local region = context:garrison_residence():region()
		for name in pairs(RITE_BUILDINGS) do
			if region:building_exists(name) then
				return true
			end
		end
		return false
	end,
	function()
		local ok, err = pcall(unlock_cult_rite, true)
		if not ok then
			log("ERROR unlocking the rite: " .. tostring(err))
		end
	end, true)

core:add_listener("druchii_cult_rite_unlock_turn", "FactionTurnStart",
	function(context) return context:faction():name() == FACTION_KEY and not cm:get_saved_value(RITE_UNLOCKED_KEY) end,
	function(context)
		local ok, err = pcall(function()
			if context:faction():is_human() and cult_has_rite_building(context:faction()) then
				unlock_cult_rite(true)
			end
		end)
		if not ok then
			log("ERROR checking the rite unlock: " .. tostring(err))
		end
	end, true)

-- Right after the rite is performed: the gift at once (followers start at
-- the next turn start).
core:add_listener("druchii_cult_rite_performed", "RitualCompletedEvent",
	function(context)
		local ok, yes = pcall(function()
			return context:performing_faction():name() == FACTION_KEY and context:ritual():ritual_key() == RITE_KEY
		end)
		return ok and yes
	end,
	function()
		cm:callback(function()
			local faction = cm:get_faction(FACTION_KEY)
			if not rite_active(faction) then
				return
			end
			log("Sacrifice to Slaanesh performed")
			cm:set_saved_value("druchii_cult_rites_performed", (cm:get_saved_value("druchii_cult_rites_performed") or 0) + 1)
			rite_step("gift", function() give_rite_gift(faction) end)
		end, 0.5)
	end, true)

---------------------------------------------------------------------------
-- 2. Starting hero: Khainite Assassin -> Druchii Anointed
---------------------------------------------------------------------------
local function replace_assassin(faction, morathi)
	-- The starting assassin closest to Morathi (there is normally just the one).
	local assassin, best = nil, nil
	local characters = faction:character_list()
	for i = 0, characters:num_items() - 1 do
		local character = characters:item_at(i)
		if character:character_subtype(ASSASSIN_SUBTYPE) then
			local dx = character:logical_position_x() - morathi:logical_position_x()
			local dy = character:logical_position_y() - morathi:logical_position_y()
			local distance = dx * dx + dy * dy
			if not best or distance < best then
				assassin, best = character, distance
			end
		end
	end
	if not assassin then
		log("no starting Khainite Assassin found, nothing replaced")
		return
	end

	local x, y = assassin:logical_position_x(), assassin:logical_position_y()
	log("step: removing the starting Khainite Assassin at " .. x .. ", " .. y)
	cm:kill_character(cm:char_lookup_str(assassin), false, true)
	log("step: Assassin removed, finding a spot for the Druchii Anointed")

	-- Spawn on the freed spot, or the nearest valid one.
	local sx, sy = x, y
	local ok, vx, vy = pcall(function()
		return cm:find_valid_spawn_location_for_character_from_position(FACTION_KEY, x, y, false)
	end)
	if ok and type(vx) == "number" and vx >= 0 and type(vy) == "number" and vy >= 0 then
		sx, sy = vx, vy
	end
	log("step: creating the Druchii Anointed at " .. sx .. ", " .. sy)
	local anointed = cm:create_agent(FACTION_KEY, ANOINTED_TYPE, ANOINTED_SUBTYPE, sx, sy, true)
	if anointed then
		log("Khainite Assassin at " .. x .. ", " .. y .. " replaced by a Druchii Anointed at " .. sx .. ", " .. sy)
	else
		log("ERROR: the Druchii Anointed could not be spawned at " .. sx .. ", " .. sy)
	end
end

---------------------------------------------------------------------------
-- 3. Starting building: Conscription Halls -> Den of Indulgence at Quintex
---------------------------------------------------------------------------
-- Same instant swap CA uses (wh3_dlc27_nor_generic.lua): dismantle the slot, then place the
-- new building in it. Only if the Cult of Pleasure owns Quintex at the start.
local QUINTEX = "wh3_main_combi_region_ancient_city_of_quintex"
local OLD_BUILDING = "wh2_main_def_barracks_1"        -- Conscription Halls
local NEW_BUILDING = "wh2_main_def_pleasure_cult_2"   -- Den of Indulgence

local function swap_quintex_building()
	local region = cm:get_region(QUINTEX)
	if not region or region:is_null_interface() or region:owning_faction():name() ~= FACTION_KEY then
		log("Quintex not owned by the Cult of Pleasure at start, building unchanged")
		return
	end
	local slots = region:slot_list()
	for i = 0, slots:num_items() - 1 do
		local slot = slots:item_at(i)
		-- Either version of the Halls: the conversion in section 7 may already have run.
		if slot:has_building() and (slot:building():name() == OLD_BUILDING
				or slot:building():name() == "druchii_cult_barracks_1") then
			cm:region_slot_instantly_dismantle_building(slot)
			cm:region_slot_instantly_upgrade_building(slot, NEW_BUILDING)
			local now = slot:has_building() and slot:building():name() or "nothing"
			log("Quintex slot " .. i .. ": " .. OLD_BUILDING .. " replaced, now holds " .. now)
			return
		end
	end
	log("no " .. OLD_BUILDING .. " found at Quintex, building unchanged")
end

---------------------------------------------------------------------------
-- 4. Daemonette caps from Dens of Indulgence
---------------------------------------------------------------------------
-- Base cap of 5 Daemonettes and 2 Exalted Daemonettes (set here, in DEN_BUNDLE). On top:
-- +1 Daemonettes for every Den of Indulgence (Pleasure Cult tier 2) and +1 Exalted Daemonettes
-- for every Halls of Hedonism (tier 4). Higher tiers keep counting (a Den upgraded to a House
-- still counts as a Den), so upgrading never loses a bonus. Recounted at the start of every Cult
-- turn and on load. Only region slots are read (no characters: see the crash notes below).
local DEN_BUNDLE = "druchii_cult_den_daemonette_caps"
local CAP_DAEMONETTES = "druchii_cult_effect_unit_cap_daemonettes"
local CAP_EXALTED = "druchii_cult_effect_unit_cap_exalted_daemonettes"
local PLEASURE_CULT_TIER = {
	wh2_main_def_pleasure_cult_1 = 1,
	wh2_main_def_pleasure_cult_2 = 2,
	wh2_main_def_pleasure_cult_3 = 3,
	wh2_main_def_pleasure_cult_4 = 4,
	wh2_main_def_pleasure_cult_5 = 5,
}

local BASE_DAEMONETTES, BASE_EXALTED = 5, 2
local ASSASSIN_CAP = "wh2_main_effect_agent_cap_increase_def_khainite_assassin"
local EXECUTIONERS_HALL = "druchii_cult_murder_2"   -- only counted for the log

-- Returns the number of Dens (tier 2+), Halls of Hedonism (tier 4+) and Executioner's Halls.
local function count_dens(faction)
	local dens, halls, executioners = 0, 0, 0
	local regions = faction:region_list()
	for i = 0, regions:num_items() - 1 do
		local slots = regions:item_at(i):slot_list()
		for j = 0, slots:num_items() - 1 do
			local slot = slots:item_at(j)
			local tier = slot:has_building() and PLEASURE_CULT_TIER[slot:building():name()]
			if tier and tier >= 2 then
				dens = dens + 1
			end
			if tier and tier >= 4 then
				halls = halls + 1
			end
			if slot:has_building() and slot:building():name() == EXECUTIONERS_HALL then
				executioners = executioners + 1
			end
		end
	end
	return dens, halls, executioners
end

local refresh_locks   -- section 5: province-cap card locks
local set_recruit_cards_hidden   -- section 5b

-- The caps the Dens/Halls allow (saved by update_den_caps).
local function base_caps()
	local saved = cm:get_saved_value("druchii_cult_den_caps_base")
	if type(saved) == "table" and saved.d and saved.e then
		return saved.d, saved.e
	end
	return BASE_DAEMONETTES, BASE_EXALTED
end

-- Writes the caps onto the custom bundle (shown in the faction effects; the limit itself is
-- enforced by the auto-cancel in section 5); does nothing if they're already applied.
local function apply_caps(daemonette_cap, exalted_cap)
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() then
		return false
	end
	local current = daemonette_cap .. "/" .. exalted_cap
	if cm:get_saved_value("druchii_cult_den_caps_applied") == current and faction:has_effect_bundle(DEN_BUNDLE) then
		return false
	end
	local values = {
		[CAP_DAEMONETTES] = daemonette_cap,
		[CAP_EXALTED] = exalted_cap,
		-- The Executioner's Hall's +2 Assassins is now on the Cult's own building (DB), so 0 here.
		[ASSASSIN_CAP] = 0,
	}
	cm:remove_effect_bundle(DEN_BUNDLE, FACTION_KEY)
	local bundle = cm:create_new_custom_effect_bundle(DEN_BUNDLE)
	local effects = bundle:effects()
	for i = 0, effects:num_items() - 1 do
		local effect = effects:item_at(i)
		bundle:set_effect_value(effect, values[effect:key()] or 0)
	end
	bundle:set_duration(0)
	cm:apply_custom_effect_bundle_to_faction(bundle, faction)
	cm:set_saved_value("druchii_cult_den_caps_applied", current)
	return true
end

local function update_den_caps()
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() then
		return
	end
	local dens, halls, executioners = count_dens(faction)
	local d, e = BASE_DAEMONETTES + dens, BASE_EXALTED + halls
	local old = cm:get_saved_value("druchii_cult_den_caps_base")
	if not (type(old) == "table" and old.d == d and old.e == e) then
		cm:set_saved_value("druchii_cult_den_caps_base", { d = d, e = e })
		log("Dens of Indulgence: " .. dens .. ", Halls of Hedonism: " .. halls .. ", Executioner's Halls: " .. executioners
			.. " -> Daemonettes cap " .. d .. ", Exalted Daemonettes cap " .. e
			.. " (Executioner's Hall gives its +2 Assassins itself)")
	end
	apply_caps(d, e)
	refresh_locks()
end

core:add_listener("druchii_cult_den_caps_turn", "FactionTurnStart",
	function(context) return context:faction():name() == FACTION_KEY end,
	function() update_den_caps() end, true)

-- Saves from the Sorceress version: drop its bundle (it would otherwise stay applied).
local OLD_SORC_BUNDLE = "druchii_cult_sorceress_daemonette_caps"

---------------------------------------------------------------------------
-- 5. Unit limits: Den/Hall caps and 6 per army for Daemonettes (auto-cancel), province caps (locks)
---------------------------------------------------------------------------
-- These units are "never capped" in vanilla (main_units campaign_cap -1), and the game ignores
-- unit_cap bonuses on such units, so the cap bundles only show the numbers. The limits are
-- enforced here (human player only):
--   Daemonettes / Exalted: never locked (v11's locks greyed out every Daemonette card, queued
--     ones too). Instead, a moment after one is queued, if the faction now has more than the
--     Dens / Halls allow, or the army more than 6 of the two together, the newest queued one is
--     cancelled by clicking its queued card (the game refunds it) and a short message is shown.
--     Only units queued past a limit are cancelled, never ones the army/faction already had when
--     the army was selected.
--   Bleakswords, Darkshards, Dreadspears (v21): handled like Daemonettes. One queued past its levy
--     cap (section 6) is cancelled and refunded; so is a Dreadspears queued in a province without
--     Halls of Ravaging. The Dreadspears card is also hidden there (it would otherwise show, as the
--     vanilla settlement building offers them). No card locks (v11-v20 locked them; cleared on load).
-- Counts include the recruitment queues, read from each army's UI context
-- (PendingRecruitmentUnitList, what the army panel shows), so cancels can't drift them.
-- AI armies aren't limited per army.
local DAEMONETTE = "wh3_main_sla_inf_daemonette_0"
local EXALTED = "wh3_main_sla_inf_daemonette_1"
local DAEMONETTE_UNITS = {
	[DAEMONETTE] = true,
	[EXALTED] = true,
}
local ARMY_CAP = 6
-- Levy units: 1 allowed per owned settlement of at least this tier (section 6).
local PROVINCE_UNITS = {
	wh2_main_def_inf_bleakswords_0 = 1,
	wh2_main_def_inf_darkshards_0 = 2,
	wh2_main_def_inf_dreadspears_0 = 3,
}
local COUNTED_UNITS = {}
for key in pairs(DAEMONETTE_UNITS) do COUNTED_UNITS[key] = true end
for key in pairs(PROVINCE_UNITS) do COUNTED_UNITS[key] = true end

local TOOLTIP_NO_PROVINCE = "druchii_cult_no_whole_province"
local TOOLTIP_LEVIES = "druchii_cult_province_cap_full"
local TOOLTIP_NO_HALLS = "druchii_cult_requires_halls_of_ravaging"
-- Units that need a building in the selected army's province, on top of the province caps.
-- Dreadspears: the Dark Elf settlement building offers them too (vanilla, every tier), so without
-- this they could be raised with only tier-1 Conscription Halls.
local HALLS_REQUIRED = {
	wh2_main_def_inf_dreadspears_0 = { druchii_cult_barracks_3 = true },   -- Halls of Ravaging
}

-- Does the selected army's province (the Cult's own regions in it) have one of these buildings?
local function army_province_has(force, buildings)
	if not force or force:is_null_interface() or not force:has_general() then
		return false
	end
	local general = force:general_character()
	if not general:has_region() then
		return false
	end
	local province = general:region():province_name()
	local regions = force:faction():region_list()
	for i = 0, regions:num_items() - 1 do
		local region = regions:item_at(i)
		if region:province_name() == province then
			local slots = region:slot_list()
			for j = 0, slots:num_items() - 1 do
				local slot = slots:item_at(j)
				if slot:has_building() and buildings[slot:building():name()] then
					return true
				end
			end
		end
	end
	return false
end

-- Event feed message (campaign_localised_strings in the loc file).
local MSG_PREFIX = "campaign_localised_strings_string_"
local MSG_TITLE = MSG_PREFIX .. "druchii_cult_cancel_title"
local MSG_ARMY = MSG_PREFIX .. "druchii_cult_cancel_army"
local MSG_TEMPLES = MSG_PREFIX .. "druchii_cult_cancel_temples"
local MSG_REFUNDED = MSG_PREFIX .. "druchii_cult_cancel_refunded"
local MSG_LEVIES = MSG_PREFIX .. "druchii_cult_cancel_levies"
local MSG_HALLS = MSG_PREFIX .. "druchii_cult_cancel_halls"
local MSG_PICTURE = 703   -- event picture index (a vanilla scripted event's)

local selected_force_cqi = nil
local last_army = nil      -- counts of the selected army at the last check
local lock_state = {}      -- unit key -> tooltip it's locked with, false if unlocked (nil: unknown)

local queue_source_logged = nil   -- which path last worked (0 = none)

local function new_counts()
	local counts = {}
	for key in pairs(COUNTED_UNITS) do counts[key] = 0 end
	return counts
end

-- The army's recruitment queue read from the UI context: counted units per key, and the unit
-- key of every queued unit in queue order (nil, nil if it can't be read).
local function read_queue(force)
	if not force:has_general() then
		return {}, {}
	end
	local cqi = force:command_queue_index()
	local general_cqi = force:general_character():command_queue_index()
	-- Ways to reach the army's queue in the UI context system; the first is the one that works
	-- (v10/v11 logs), the others are kept in case a patch changes that. The first that works is logged.
	local paths = {
		{ "CcoCampaignCharacter", general_cqi, "MilitaryForceContext.PendingRecruitmentUnitList" },
		{ "CcoCampaignCharacter", tostring(general_cqi), "MilitaryForceContext.PendingRecruitmentUnitList" },
		{ "CcoCampaignMilitaryForce", cqi, "PendingRecruitmentUnitList" },
		{ "CcoCampaignMilitaryForce", tostring(cqi), "PendingRecruitmentUnitList" },
	}
	for n, path in ipairs(paths) do
		local context_type, id, list = path[1], path[2], path[3]
		local ok, queued, order = pcall(function()
			local size = common.get_context_value(context_type, id, list .. ".Size")
			if type(size) ~= "number" then
				return nil
			end
			local queued, order = {}, {}
			for i = 0, size - 1 do
				local key = common.get_context_value(context_type, id, list .. ".At(" .. i .. ").First.UnitRecordContext.Key")
				order[#order + 1] = key or ""
				if COUNTED_UNITS[key] then
					queued[key] = (queued[key] or 0) + 1
				end
			end
			return queued, order
		end)
		if ok and type(queued) == "table" then
			if queue_source_logged ~= n then
				queue_source_logged = n
				log("recruitment queue read from the army panel (path " .. n .. ")")
			end
			return queued, order
		end
	end
	if queue_source_logged ~= 0 then
		queue_source_logged = 0
		log("WARNING: recruitment queue not readable from the UI, counting only recruited units")
	end
	return nil, nil
end

-- Counted units in the army, recruited + queued.
local function count_in_force(force)
	local counts = new_counts()
	local units = force:unit_list()
	for i = 0, units:num_items() - 1 do
		local key = units:item_at(i):unit_key()
		if COUNTED_UNITS[key] then
			counts[key] = counts[key] + 1
		end
	end
	for key, n in pairs((read_queue(force)) or {}) do
		counts[key] = counts[key] + n
	end
	return counts
end

-- Counted units across all the Cult's armies, recruited + queued; also returns the selected
-- army's own counts.
local function count_in_faction(faction)
	local totals, army = new_counts(), nil
	local forces = faction:military_force_list()
	for i = 0, forces:num_items() - 1 do
		local force = forces:item_at(i)
		if not force:is_armed_citizenry() then
			local counts = count_in_force(force)
			for key, n in pairs(counts) do
				totals[key] = totals[key] + n
			end
			if force:command_queue_index() == selected_force_cqi then
				army = counts
			end
		end
	end
	return totals, army
end

local function set_lock(unit_key, tooltip)
	if lock_state[unit_key] == tooltip then
		return
	end
	if lock_state[unit_key] then
		-- Switching tooltip: drop the old restriction first.
		cm:remove_event_restricted_unit_record_for_faction(unit_key, FACTION_KEY)
	end
	if tooltip then
		cm:add_event_restricted_unit_record_for_faction(unit_key, FACTION_KEY, tooltip)
	elseif lock_state[unit_key] == nil then
		-- First check since load: clear any restriction an older version saved.
		cm:remove_event_restricted_unit_record_for_faction(unit_key, FACTION_KEY)
	end
	lock_state[unit_key] = tooltip
	log(unit_key .. (tooltip and (" locked (" .. tooltip .. ")") or " unlocked"))
end

-- Levy limit for a unit: owned settlements of its minimum tier or higher (saved by section 6).
local function levy_cap(unit_key)
	return cm:get_saved_value("druchii_cult_levy_cap_" .. unit_key) or 0
end

---------------------------------------------------------------------------
-- 5a. Counts, levy log line, Dreadspears card visibility (no locks since v21)
---------------------------------------------------------------------------
-- hint_key/hint_delta: the unit just queued (+1) or cancelled (-1). The UI queue can lag a
-- moment behind the event, so the count is taken as at least / at most the last count +/- 1
-- (and checked again 0.2s later), so a quick second click can't slip past the limit.
refresh_locks = function(hint_key, hint_delta)
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() then
		return
	end
	local totals, army = count_in_faction(faction)
	if hint_key and PROVINCE_UNITS[hint_key] and army and last_army then
		local expected = last_army[hint_key] + hint_delta
		local adjusted
		if hint_delta > 0 then
			adjusted = math.max(army[hint_key], expected)
		else
			adjusted = math.max(0, math.min(army[hint_key], expected))
		end
		totals[hint_key] = totals[hint_key] + adjusted - army[hint_key]
		army[hint_key] = adjusted
	end
	last_army = army

	-- Daemonettes are never locked (auto-cancel instead, 5b); this also clears v11's locks.
	for key in pairs(DAEMONETTE_UNITS) do
		set_lock(key, false)
	end
	-- Levies are never locked either (auto-cancel, 5b); this clears v11-v20's locks.
	local force = selected_force_cqi and cm:model():military_force_for_command_queue_index(selected_force_cqi)
	for key in pairs(PROVINCE_UNITS) do
		set_lock(key, false)
	end
	-- Dreadspears card: hidden where they can't be raised.
	if army then
		local hide = {}
		for key, buildings in pairs(HALLS_REQUIRED) do
			hide[key] = levy_cap(key) == 0 or not army_province_has(force, buildings)
		end
		cm:callback(function() set_recruit_cards_hidden(hide) end, 0.1)
	end

	local d_cap, e_cap = base_caps()
	local line = "faction " .. totals[DAEMONETTE] .. "/" .. d_cap .. " Daemonettes, " .. totals[EXALTED] .. "/" .. e_cap
		.. " Exalted"
	if army then
		line = "army " .. selected_force_cqi .. ": " .. (army[DAEMONETTE] + army[EXALTED]) .. "/" .. ARMY_CAP
			.. " Daemonette units; " .. line
	end
	log(line .. "; levies "
		.. totals.wh2_main_def_inf_bleakswords_0 .. "/" .. levy_cap("wh2_main_def_inf_bleakswords_0") .. " Bleakswords, "
		.. totals.wh2_main_def_inf_darkshards_0 .. "/" .. levy_cap("wh2_main_def_inf_darkshards_0") .. " Darkshards, "
		.. totals.wh2_main_def_inf_dreadspears_0 .. "/" .. levy_cap("wh2_main_def_inf_dreadspears_0") .. " Dreadspears (incl. queued)")
end

---------------------------------------------------------------------------
-- 5b. Daemonette caps: cancel and refund what's queued past a limit
---------------------------------------------------------------------------
-- The queued unit cards on the army panel, in panel order (CA's lib_campaign_ui finds them the
-- same way: children of units_panel > main_units_panel > units named "QueuedLandUnit ...").
local function queued_cards()
	local cards = {}
	local uic_units = find_uicomponent(core:get_ui_root(), "units_panel", "main_units_panel", "units")
	if not uic_units then
		return cards
	end
	for i = 0, uic_units:ChildCount() - 1 do
		local uic_child = UIComponent(uic_units:Find(i))
		if string.sub(uic_child:Id(), 1, 14) == "QueuedLandUnit" then
			cards[#cards + 1] = uic_child
		end
	end
	return cards
end

-- The unit key behind a queued card, if the card's UI context gives it (nil if not).
local function card_unit_key(uic)
	local tries = {
		{ "CcoUnitDetails", "UnitRecordContext.Key" },
		{ "CcoCampaignUnit", "UnitRecordContext.Key" },
		{ "CcoMainUnitRecord", "Key" },
	}
	for _, try in ipairs(tries) do
		local ok, key = pcall(function()
			local id = uic:GetContextObjectId(try[1])
			if id and id ~= "" then
				return common.get_context_value(try[1], id, try[2])
			end
		end)
		if ok and type(key) == "string" and key ~= "" then
			return key
		end
	end
	return nil
end

-- Clicks the newest queued card of unit_key in the selected army (the game cancels and refunds
-- it). The card is found by the card's own unit key, or else by its position in the queue.
local function cancel_newest_queued(force, unit_key)
	local _, order = read_queue(force)
	local cards = queued_cards()
	-- 1. By the card's own unit key (newest = last).
	for i = #cards, 1, -1 do
		if card_unit_key(cards[i]) == unit_key then
			log("cancelling queued " .. unit_key .. " (card " .. cards[i]:Id() .. ", matched by unit)")
			cards[i]:SimulateLClick()
			return true
		end
	end
	-- 2. By queue position: the n-th queued unit is the n-th queued card.
	if order and #order == #cards then
		for i = #order, 1, -1 do
			if order[i] == unit_key then
				log("cancelling queued " .. unit_key .. " (card " .. cards[i]:Id() .. ", matched by queue position "
					.. i .. " of " .. #order .. ")")
				cards[i]:SimulateLClick()
				return true
			end
		end
	end
	log("WARNING: couldn't find the queued " .. unit_key .. " card to cancel (" .. #cards .. " queued cards, queue "
		.. (order and #order or "unreadable") .. ")")
	return false
end

local function show_cancel_message(detail_key)
	local ok, err = pcall(function()
		cm:show_message_event(FACTION_KEY, MSG_TITLE, detail_key, MSG_REFUNDED, false, MSG_PICTURE)
	end)
	if not ok then
		log("WARNING: cancel message not shown: " .. tostring(err))
	end
end

-- Recruitment option cards (not queued ones) whose id contains a unit key: hidden or shown.
-- hide = { unit_key = true/false }. The recruitment list is rebuilt when the panel refreshes, so
-- this runs again after each recruit/cancel and when the panel opens.
local hidden_logged = {}
set_recruit_cards_hidden = function(hide)
	local ok, err = pcall(function()
		local panel = find_uicomponent(core:get_ui_root(), "units_recruitment")
		if not panel or not panel:Visible() then
			return
		end
		local found = {}
		local function walk(uic, depth)
			local id = uic:Id()
			if string.sub(id, 1, 14) ~= "QueuedLandUnit" then
				for key, want_hidden in pairs(hide) do
					if string.find(id, key, 1, true) then
						found[key] = (found[key] or 0) + 1
						if want_hidden == uic:Visible() then
							uic:SetVisible(not want_hidden)
						end
					end
				end
			end
			if depth < 30 then
				for i = 0, uic:ChildCount() - 1 do
					walk(UIComponent(uic:Find(i)), depth + 1)
				end
			end
		end
		walk(panel, 0)
		for key, want_hidden in pairs(hide) do
			local state = tostring(want_hidden) .. "/" .. tostring(found[key] or 0)
			if hidden_logged[key] ~= state then
				hidden_logged[key] = state
				log(key .. " card " .. (want_hidden and "hidden" or "shown") .. " (" .. (found[key] or 0) .. " card(s) found)")
			end
		end
	end)
	if not ok then
		log("WARNING: recruitment card visibility: " .. tostring(err))
	end
end

local enforce_attempts = 0
-- What the selected army / faction already had before you started queuing (taken when the army
-- is selected, and lowered whenever a check finds less). Units are only cancelled down to
-- max(limit, this), so units queued or recruited earlier are never touched (e.g. if the army got
-- past 6 by a transfer, or the faction is over its cap after losing a Den).
-- v12 tracked each click instead; a click the panel hadn't shown yet could be forgotten and stay
-- queued past the limit.
local before = nil   -- { army = n, [DAEMONETTE] = n, [EXALTED] = n }
-- True between a cancel click and its follow-up check: checks from other clicks wait for it
-- (they retry a moment later), so a cancel the panel hasn't shown yet isn't counted twice.
local cancel_pending = false

local function take_baseline()
	before = nil
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() or not selected_force_cqi then
		return
	end
	local totals, army = count_in_faction(faction)
	if army then
		before = { army = army[DAEMONETTE] + army[EXALTED], [DAEMONETTE] = totals[DAEMONETTE], [EXALTED] = totals[EXALTED] }
		for key in pairs(PROVINCE_UNITS) do
			before[key] = totals[key]
		end
	end
end

-- Checks the selected army after a Daemonette was queued; cancels one unit per pass and checks
-- again until it's within the limits (several can be queued by fast clicking).
local function enforce_daemonette_caps(issued_key, is_follow_up)
	if is_follow_up then
		cancel_pending = false
	elseif cancel_pending then
		cm:callback(function() enforce_daemonette_caps(issued_key) end, 0.3)
		return
	end
	local faction = cm:get_faction(FACTION_KEY)
	local force = selected_force_cqi and cm:model():military_force_for_command_queue_index(selected_force_cqi)
	if not faction or faction:is_null_interface() or not force or force:is_null_interface()
		or force:faction():name() ~= FACTION_KEY then
		return
	end
	local totals, army = count_in_faction(faction)
	if not army then
		return
	end
	local queued = read_queue(force) or {}
	local army_total = army[DAEMONETTE] + army[EXALTED]
	local d_cap, e_cap = base_caps()
	local b = before or { army = 0, [DAEMONETTE] = 0, [EXALTED] = 0 }
	local limit = {
		army = math.max(ARMY_CAP, b.army),
		[DAEMONETTE] = math.max(d_cap, b[DAEMONETTE]),
		[EXALTED] = math.max(e_cap, b[EXALTED]),
	}
	local function has_queued(key)
		return key and DAEMONETTE_UNITS[key] and (queued[key] or 0) > 0
	end

	-- What to cancel: a unit over its Den/Hall cap first, else (army over 6) the one just queued.
	local cancel_key, reason = nil, nil
	for _, key in ipairs({ issued_key, DAEMONETTE, EXALTED }) do
		if has_queued(key) and totals[key] > limit[key] then
			cancel_key, reason = key, MSG_TEMPLES
			break
		end
	end
	if not cancel_key and army_total > limit.army then
		for _, key in ipairs({ issued_key, EXALTED, DAEMONETTE }) do
			if has_queued(key) then
				cancel_key, reason = key, MSG_ARMY
				break
			end
		end
	end
	-- Levies (v21): past the levy cap (or what the faction already had), or a Dreadspears queued
	-- where there are no Halls of Ravaging in the army's province.
	if not cancel_key then
		local order = { issued_key }
		for key in pairs(PROVINCE_UNITS) do order[#order + 1] = key end
		for _, key in ipairs(order) do
			if key and PROVINCE_UNITS[key] and (queued[key] or 0) > 0 then
				if HALLS_REQUIRED[key] and not army_province_has(force, HALLS_REQUIRED[key]) then
					cancel_key, reason = key, MSG_HALLS
					break
				elseif totals[key] > math.max(levy_cap(key), b[key] or 0) then
					cancel_key, reason = key, MSG_LEVIES
					break
				end
			end
		end
		if cancel_key then
			log("Levy check, army " .. selected_force_cqi .. ": " .. totals[cancel_key] .. "/" .. levy_cap(cancel_key)
				.. " " .. cancel_key .. " (incl. queued) -> cancelling one (" .. reason .. ")")
		end
	end
	log("Daemonette check, army " .. selected_force_cqi .. ": " .. army_total .. "/" .. limit.army
		.. "; faction " .. totals[DAEMONETTE] .. "/" .. limit[DAEMONETTE] .. " Daemonettes, " .. totals[EXALTED] .. "/"
		.. limit[EXALTED] .. " Exalted (incl. queued)" .. (cancel_key and (" -> over the limit, cancelling a " .. cancel_key) or ""))
	if not cancel_key then
		enforce_attempts = 0
		-- Within the limits: if the army/faction has fewer than before (cancelled or lost units),
		-- that's the new "before", so the old excess can't be refilled.
		if before then
			before.army = math.min(before.army, army_total)
			before[DAEMONETTE] = math.min(before[DAEMONETTE], totals[DAEMONETTE])
			before[EXALTED] = math.min(before[EXALTED], totals[EXALTED])
			for key in pairs(PROVINCE_UNITS) do
				before[key] = math.min(before[key] or 0, totals[key])
			end
		end
		return
	end
	enforce_attempts = enforce_attempts + 1
	if enforce_attempts > 8 then
		log("WARNING: gave up cancelling after 8 tries")
		enforce_attempts = 0
		return
	end
	if cancel_newest_queued(force, cancel_key) then
		show_cancel_message(reason)
	end
	-- Check again once the panel has caught up (more may have been queued, or the click failed).
	cancel_pending = true
	cm:callback(function() enforce_daemonette_caps(nil, true) end, 0.3)
end

---------------------------------------------------------------------------
-- 5c. Listeners
---------------------------------------------------------------------------
-- The unit key of a recruit/cancel event (pcall: in case the context doesn't offer it).
local function event_unit_key(context)
	local ok, key = pcall(function() return context:main_unit_record() end)
	if ok and type(key) == "string" then
		return key
	end
	if ok and key and type(key) ~= "string" then
		local ok2, k2 = pcall(function() return key:key() end)
		if ok2 then
			return k2
		end
	end
	log("WARNING: recruitment event without a readable unit key")
	return nil
end

local function is_local_cult(faction)
	return faction:name() == FACTION_KEY and faction:is_human() and cm:get_local_faction_name(true) == FACTION_KEY
end

local function refresh_locks_later()
	cm:callback(function() refresh_locks() end, 0.2)
end

core:add_listener("druchii_cult_locks_selected", "CharacterSelected",
	function(context) return is_local_cult(context:character():faction()) end,
	function(context)
		local character = context:character()
		last_army = nil
		if character:has_military_force() and not character:military_force():is_armed_citizenry() then
			selected_force_cqi = character:military_force():command_queue_index()
		else
			-- A hero or a lord without an army: nothing can be recruited, so no check. v12 checked
			-- here too (reading every army's queue from the UI while a hero's panel opened), and
			-- the game crashed when the Anointed's panel popped up.
			selected_force_cqi = nil
			before = nil
			return
		end
		-- A moment later, outside the game's own selection/UI event.
		local cqi = selected_force_cqi
		cm:callback(function()
			if selected_force_cqi ~= cqi then
				return
			end
			local ok, err = pcall(function()
				refresh_locks()
				take_baseline()
			end)
			if not ok then
				log("ERROR in the army-selected check: " .. tostring(err))
			end
		end, 0.1)
	end, true)

core:add_listener("druchii_cult_locks_settlement", "SettlementSelected",
	function() return cm:get_local_faction_name(true) == FACTION_KEY end,
	function()
		-- Nothing can be recruited with a settlement selected, so no check (see above).
		selected_force_cqi = nil
		last_army = nil
		before = nil
	end, true)

core:add_listener("druchii_cult_locks_issued", "RecruitmentItemIssuedByPlayer",
	function(context) return is_local_cult(context:faction()) end,
	function(context)
		local key = event_unit_key(context)
		if key and (DAEMONETTE_UNITS[key] or PROVINCE_UNITS[key]) then
			-- Wait until the queued card is on the army panel, then check the limits.
			cm:callback(function() enforce_daemonette_caps(key) end, 0.2)
		end
		-- The recruitment list is rebuilt after a click: re-apply the Dreadspears card visibility.
		refresh_locks_later()
	end, true)

core:add_listener("druchii_cult_locks_cancelled", "RecruitmentItemCancelledByPlayer",
	function(context) return is_local_cult(context:faction()) end,
	function(context)
		local key = event_unit_key(context)
		if key and PROVINCE_UNITS[key] then
			refresh_locks(key, -1)
		end
		refresh_locks_later()
	end, true)

-- Moving units between armies, disbanding or losing units changes the counts: recheck the
-- province locks at turn start and whenever the recruitment panel opens.
core:add_listener("druchii_cult_locks_turn", "FactionTurnStart",
	function(context) return context:faction():name() == FACTION_KEY end,
	function()
		selected_force_cqi = nil
		last_army = nil
		refresh_locks()
	end, true)
core:add_listener("druchii_cult_locks_panel", "PanelOpenedCampaign",
	function(context)
		return context.string == "units_recruitment" and cm:get_local_faction_name(true) == FACTION_KEY
			and selected_force_cqi ~= nil
	end,
	function()
		cm:callback(function()
			local ok, err = pcall(refresh_locks)
			if not ok then
				log("ERROR in the recruitment-panel check: " .. tostring(err))
			end
		end, 0.1)
	end, true)

---------------------------------------------------------------------------
-- 6. Levy caps: 1 Bleaksword per settlement, 1 Darkshards per tier 2+, 1 Dreadspears per tier 3+
---------------------------------------------------------------------------
-- (v17; until v16: 2/1/1 per whole province.) Settlement tier = the number at the end of the
-- main settlement building (wh2_main_def_settlement_minor_2 -> 2, ..._major_4 -> 4). Values go on
-- a custom copy of the DB bundle druchii_cult_province_unit_caps (shown in the faction effects);
-- the limits are enforced by the locks in section 5, which read the saved caps. Counted at load,
-- at the Cult's turn start, when it gains or loses a settlement and when a settlement upgrade
-- completes.
local PROV_BUNDLE = "druchii_cult_province_unit_caps"
local LEVY_EFFECTS = {
	druchii_cult_effect_unit_cap_bleakswords = "wh2_main_def_inf_bleakswords_0",
	druchii_cult_effect_unit_cap_darkshards = "wh2_main_def_inf_darkshards_0",
	druchii_cult_effect_unit_cap_dreadspears = "wh2_main_def_inf_dreadspears_0",
}

local function settlement_tier(region)
	local ok, tier = pcall(function()
		local slot = region:settlement():primary_slot()
		if slot:is_null_interface() or not slot:has_building() then
			return 0
		end
		return tonumber(string.match(slot:building():name(), "_(%d+)$")) or 0
	end)
	return ok and tier or 0
end

-- {unit key = number of owned settlements of at least its tier}
local function count_levy_caps(faction)
	local caps = {}
	for key in pairs(PROVINCE_UNITS) do
		caps[key] = 0
	end
	local regions = faction:region_list()
	for i = 0, regions:num_items() - 1 do
		local tier = settlement_tier(regions:item_at(i))
		for key, min_tier in pairs(PROVINCE_UNITS) do
			if tier >= min_tier then
				caps[key] = caps[key] + 1
			end
		end
	end
	return caps
end

local function update_province_caps()
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() then
		return
	end
	log("step: counting settlements by tier")
	local caps = count_levy_caps(faction)
	local changed = false
	for key, cap in pairs(caps) do
		if cm:get_saved_value("druchii_cult_levy_cap_" .. key) ~= cap then
			changed = true
		end
	end
	if not changed and faction:has_effect_bundle(PROV_BUNDLE) then
		refresh_locks()
		return
	end
	log("step: levy caps, creating bundle")
	cm:remove_effect_bundle(PROV_BUNDLE, FACTION_KEY)
	local bundle = cm:create_new_custom_effect_bundle(PROV_BUNDLE)
	local effects = bundle:effects()
	for i = 0, effects:num_items() - 1 do
		local effect = effects:item_at(i)
		local unit_key = LEVY_EFFECTS[effect:key()]
		bundle:set_effect_value(effect, unit_key and caps[unit_key] or 0)
	end
	bundle:set_duration(0)
	log("step: levy caps, applying bundle")
	cm:apply_custom_effect_bundle_to_faction(bundle, faction)
	for key, cap in pairs(caps) do
		cm:set_saved_value("druchii_cult_levy_cap_" .. key, cap)
	end
	log("levy caps: Bleakswords " .. caps.wh2_main_def_inf_bleakswords_0 .. ", Darkshards "
		.. caps.wh2_main_def_inf_darkshards_0 .. ", Dreadspears " .. caps.wh2_main_def_inf_dreadspears_0)
	refresh_locks()
end

core:add_listener("druchii_cult_province_caps_turn", "FactionTurnStart",
	function(context) return context:faction():name() == FACTION_KEY end,
	function() update_province_caps() end, true)
core:add_listener("druchii_cult_province_caps_region", "RegionFactionChangeEvent",
	function(context)
		local new_owner = context:region():owning_faction()
		local previous = context:previous_faction()
		return (not new_owner:is_null_interface() and new_owner:name() == FACTION_KEY)
			or (not previous:is_null_interface() and previous:name() == FACTION_KEY)
	end,
	function() cm:callback(update_province_caps, 0.2) end, true)
-- A settlement upgrade changes its tier. Only from turn 2 (turn-1 load crash lesson); building
-- reads inside pcall.
core:add_listener("druchii_cult_province_caps_building", "BuildingCompleted",
	function(context)
		if cm:model():turn_number() < 2 then
			return false
		end
		local ok, result = pcall(function()
			local building = context:building()
			return building:faction():name() == FACTION_KEY and string.find(building:name(), "_settlement_") ~= nil
		end)
		return ok and result
	end,
	function() cm:callback(update_province_caps, 0.2) end, true)

---------------------------------------------------------------------------
-- 7. Vanilla Conscription Halls / House of Assassins / Slave Gate / Beastmasters -> the Cult's own (same tier)
---------------------------------------------------------------------------
-- The vanilla chains are disabled for the Cult in the DB; any vanilla one it owns (at the start,
-- or in a captured settlement) is swapped for the Cult version of the same tier.
local function convert_barracks(region)
	local slots = region:slot_list()
	for i = 0, slots:num_items() - 1 do
		local slot = slots:item_at(i)
		if slot:has_building() then
			local name = slot:building():name()
			local tier = string.match(name, "^wh2_main_def_barracks_(%d)$")
			local murder_tier = string.match(name, "^wh2_main_def_murder_(%d)$")
			local gate_tier = string.match(name, "^wh2_main_def_defence_major_(%d)$")
			local beasts_tier = string.match(name, "^wh2_main_def_beasts_(%d)$")
			local manse_tier = string.match(name, "^wh2_main_def_coldones_(%d)$")
			if manse_tier then
				log("step: converting Dread Manse tier " .. manse_tier .. " at " .. region:name())
				cm:region_slot_instantly_dismantle_building(slot)
				cm:region_slot_instantly_upgrade_building(slot, "druchii_cult_coldones_" .. manse_tier)
				log(region:name() .. ": Dread Manse tier " .. manse_tier .. " converted to the Cult version")
			elseif beasts_tier then
				log("step: converting Beastmasters tier " .. beasts_tier .. " at " .. region:name())
				cm:region_slot_instantly_dismantle_building(slot)
				cm:region_slot_instantly_upgrade_building(slot, "druchii_cult_beasts_" .. beasts_tier)
				log(region:name() .. ": Beastmasters tier " .. beasts_tier .. " converted to the Cult version")
			elseif gate_tier then
				log("step: converting Slave Gate tier " .. gate_tier .. " at " .. region:name())
				cm:region_slot_instantly_dismantle_building(slot)
				cm:region_slot_instantly_upgrade_building(slot, "druchii_cult_defence_major_" .. gate_tier)
				log(region:name() .. ": Slave Gate tier " .. gate_tier .. " converted to the Cult version")
			elseif murder_tier then
				log("step: converting House of Assassins tier " .. murder_tier .. " at " .. region:name())
				cm:region_slot_instantly_dismantle_building(slot)
				cm:region_slot_instantly_upgrade_building(slot, "druchii_cult_murder_" .. murder_tier)
				log(region:name() .. ": House of Assassins tier " .. murder_tier .. " converted to the Cult version")
			elseif tier then
				log("step: converting Halls tier " .. tier .. " at " .. region:name())
				cm:region_slot_instantly_dismantle_building(slot)
				cm:region_slot_instantly_upgrade_building(slot, "druchii_cult_barracks_" .. tier)
				log(region:name() .. ": Conscription Halls tier " .. tier .. " converted to the Cult version")
			end
		end
	end
end

-- CA's Beastmaster follower (wh3_campaign_followers.lua) checks for the vanilla chain key, which the
-- Cult no longer has; the same trigger for the Cult's copy: a lord or hero who has spent a turn in
-- a Cult region with a Beastmasters building, every 5th turn, 25% chance.
core:add_listener("druchii_cult_beastmaster_follower", "CharacterTurnStart",
	function(context)
		-- Turn check first, before touching the character: turn-1 CharacterTurnStart fires during
		-- loading, after the first tick has killed the starting Assassin, and reading characters
		-- then crashed natively before (see CRASH LESSON). v15 read character:faction() here first
		-- and the game crashed on turn 1 (2026-11-25), so turn 1 never gets past this line now.
		local turn = cm:model():turn_number()
		if turn < 2 or turn % 5 ~= 0 then
			return false
		end
		local ok, result = pcall(function()
			local character = context:character()
			return not character:character_type("colonel") and character:faction():name() == FACTION_KEY
				and character:has_region() and character:turns_in_own_regions() >= 1
				and cm:region_has_chain_or_superchain(character:region(), "druchii_cult_beasts")
				and not character:has_ancillary("wh2_main_anc_follower_def_beastmaster")
		end)
		return ok and result
	end,
	function(context)
		if cm:model():random_percent(25) then
			cm:force_add_ancillary(context:character(), "wh2_main_anc_follower_def_beastmaster", false, false)
			log("Beastmaster follower for " .. context:character():character_subtype_key())
		end
	end, true)

local function convert_all_barracks()
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() then
		return
	end
	local regions = faction:region_list()
	for i = 0, regions:num_items() - 1 do
		convert_barracks(regions:item_at(i))
	end
end

core:add_listener("druchii_cult_barracks_captured", "RegionFactionChangeEvent",
	function(context)
		local owner = context:region():owning_faction()
		return not owner:is_null_interface() and owner:name() == FACTION_KEY
	end,
	function(context)
		local region_key = context:region():name()
		cm:callback(function()
			local region = cm:get_region(region_key)
			if region and not region:is_null_interface() and region:owning_faction():name() == FACTION_KEY then
				convert_barracks(region)
			end
		end, 0.3)
	end, true)
core:add_listener("druchii_cult_barracks_turn", "FactionTurnStart",
	function(context) return context:faction():name() == FACTION_KEY end,
	function() convert_all_barracks() end, true)

---------------------------------------------------------------------------
-- 14. Open Markets (the Cult's copy of the slave diktat): +600 gold per turn for 6 turns
---------------------------------------------------------------------------
-- The DB bundle lasts 6 turns and shows the line; there's no flat income effect for a region
-- bundle, so the gold is paid here with cm:treasury_mod (as for N'Kari): once when the diktat is
-- performed, then at each of the Cult's next 5 turn starts. Pending payments per region are kept
-- in a saved string ("region=n;region=n"), so the count survives saving and loading.
local OPEN_MARKETS_RITUAL = "druchii_cult_ritual_slave_c"
local OPEN_MARKETS_GOLD = 600
local OPEN_MARKETS_PAYMENTS = 6
local OPEN_MARKETS_SAVE = "druchii_cult_open_markets_pending"

local function read_open_markets()
	local pending = {}
	for region_key, n in string.gmatch(cm:get_saved_value(OPEN_MARKETS_SAVE) or "", "([^=;]+)=(%d+)") do
		pending[region_key] = tonumber(n)
	end
	return pending
end

local function write_open_markets(pending)
	local parts = {}
	for region_key, n in pairs(pending) do
		if n > 0 then
			table.insert(parts, region_key .. "=" .. n)
		end
	end
	cm:set_saved_value(OPEN_MARKETS_SAVE, table.concat(parts, ";"))
end

local function pay_open_markets(region_key, pending)
	cm:treasury_mod(FACTION_KEY, OPEN_MARKETS_GOLD)
	pending[region_key] = (pending[region_key] or 0) - 1
	log("Open Markets (" .. region_key .. "): +" .. OPEN_MARKETS_GOLD .. " gold, " .. pending[region_key] .. " payments left")
end

core:add_listener("druchii_cult_open_markets_performed", "RitualCompletedEvent",
	function(context)
		return context:succeeded() and context:ritual():ritual_key() == OPEN_MARKETS_RITUAL
			and context:performing_faction():name() == FACTION_KEY
	end,
	function(context)
		local ok, err = pcall(function()
			local region_key = context:ritual():ritual_target():get_target_region():name()
			local pending = read_open_markets()
			pending[region_key] = OPEN_MARKETS_PAYMENTS
			pay_open_markets(region_key, pending)
			write_open_markets(pending)
		end)
		if not ok then
			log("ERROR paying Open Markets: " .. tostring(err))
		end
	end, true)

core:add_listener("druchii_cult_open_markets_turn", "FactionTurnStart",
	function(context) return context:faction():name() == FACTION_KEY end,
	function()
		local ok, err = pcall(function()
			local pending = read_open_markets()
			local any = false
			for region_key, n in pairs(pending) do
				if n > 0 then
					pay_open_markets(region_key, pending)
					any = true
				end
			end
			if any then
				write_open_markets(pending)
			end
		end)
		if not ok then
			log("ERROR paying Open Markets: " .. tostring(err))
		end
	end, true)

-- Every load (new or saved game): the province caps, the building conversions (so
-- existing saves pick them up) and the Den caps.
-- Crash notes: reading the character list in the turn-1 load (after the starting Assassin is
-- killed) crashed the game, so nothing here touches characters.
local function run_step(name, fn)
	log("load step: " .. name)
	local ok, err = pcall(fn)
	if not ok then
		log("ERROR on load (" .. name .. "): " .. tostring(err))
	end
end

---------------------------------------------------------------------------
-- 15. Hero panel: "Death Hag" -> "Cultist of Slaanesh" (Cult only)
---------------------------------------------------------------------------
-- The hero group's name comes from the Dark Elf culture's "dignitary" row (agent_culture_details
-- 610), shared by every Dark Elf faction, so it can't be changed in the data for the Cult alone.
-- Instead, while the Cult is the local player, texts reading "Death Hag" in open panels are
-- rewritten a moment after a panel opens or something is clicked. The Cult has no Death Hags.
local HAG_NAME, CULTIST_NAME = nil, nil
local open_panels = {}
local relabel_logged = {}

local function relabel_panel(panel_name)
	local ok, err = pcall(function()
		HAG_NAME = HAG_NAME or common.get_localised_string("agent_culture_details_onscreen_name_610")
		CULTIST_NAME = CULTIST_NAME or common.get_localised_string("agent_subtypes_onscreen_name_override_wh3_main_sla_cultist")
		if not HAG_NAME or HAG_NAME == "" or not CULTIST_NAME or CULTIST_NAME == "" then
			return
		end
		local panel = find_uicomponent(core:get_ui_root(), panel_name)
		if not panel then
			return
		end
		local count = 0
		local function walk(uic, depth)
			local ok_text, text = pcall(function() return uic:GetStateText() end)
			if ok_text and type(text) == "string" and string.find(text, HAG_NAME, 1, true) then
				local new_text = string.gsub(text, HAG_NAME, CULTIST_NAME)
				uic:SetStateText(new_text)
				count = count + 1
			end
			if depth < 30 then
				for i = 0, uic:ChildCount() - 1 do
					walk(UIComponent(uic:Find(i)), depth + 1)
				end
			end
		end
		walk(panel, 0)
		if count > 0 and not relabel_logged[panel_name] then
			relabel_logged[panel_name] = true
			log("hero label: " .. count .. " '" .. HAG_NAME .. "' text(s) relabelled in panel " .. panel_name)
		end
	end)
	if not ok then
		log("WARNING: hero label: " .. tostring(err))
	end
end

-- After a click (a tab or list refresh), only the open panels that had the label before.
local function relabel_open_panels()
	for panel_name in pairs(open_panels) do
		if relabel_logged[panel_name] then
			relabel_panel(panel_name)
		end
	end
end

-- v21d (2026-11-25): listeners OFF while testing the turn-1 intro black screen (v21, v21b and
-- v21c went black; v20, without this section, didn't). The functions above are kept.
local RELABEL_ENABLED = false
if RELABEL_ENABLED then
core:add_listener("druchii_cult_relabel_opened", "PanelOpenedCampaign",
	function() return cm:get_local_faction_name(true) == FACTION_KEY end,
	function(context)
		local panel_name = context.string
		if not panel_name or panel_name == "" then
			return
		end
		if open_panels[panel_name] == nil and not relabel_logged["seen_" .. panel_name] then
			relabel_logged["seen_" .. panel_name] = false   -- diagnostic: which panels open
			log("panel opened: " .. panel_name)
		end
		-- v21b: only the hero recruitment panel (CA's "character_panel"; any "agent" panel too).
		-- v21 rewrote texts in every panel, and the game went black during the turn-1 intro right
		-- after it walked the "events" panel.
		if not (string.find(panel_name, "character", 1, true) or string.find(panel_name, "agent", 1, true)) then
			return
		end
		open_panels[panel_name] = true
		cm:callback(function() relabel_panel(panel_name) end, 0.1)
		cm:callback(function() relabel_panel(panel_name) end, 0.4)
	end, true)
core:add_listener("druchii_cult_relabel_closed", "PanelClosedCampaign",
	function() return cm:get_local_faction_name(true) == FACTION_KEY end,
	function(context)
		if context.string then
			open_panels[context.string] = nil
		end
	end, true)
core:add_listener("druchii_cult_relabel_click", "ComponentLClickUp",
	function() return next(relabel_logged) ~= nil and cm:get_local_faction_name(true) == FACTION_KEY end,
	function()
		cm:callback(relabel_open_panels, 0.1)
	end, true)
end

---------------------------------------------------------------------------
-- 16. Regiments of Renown for the Cult (2026-11-26)
---------------------------------------------------------------------------
-- The Cult's RoR pool comes from the campaign's starting state, not from the DB pool tables
-- (Cult v20 "allowed=False" rows and v23's moved pool rows changed nothing in a new campaign). So:
--   - once per campaign: add Scourge of Arden + Bringers of Beguilement to the Cult's pool, and set
--     the six unwanted ones to 0 units / cap 0 (CA's cm:add_unit_to_faction_mercenary_pool, the
--     Imrik dragon script's call; there is no remove function);
--   - every load: lock the six unwanted ones for the Cult (event restriction, tooltip), as a
--     backstop if the pool still lists them.
-- The pool is logged before and after the first change, to see what the game did.
local ROR_SOURCE = "wh3_main_regiments_of_renown_pool"
local ROR_REMOVED = {
	"wh2_dlc10_def_inf_the_hellebronai_ror_0",
	"wh2_dlc10_def_inf_sisters_of_the_singing_doom_ror_0",
	"wh2_dlc10_def_inf_the_bolt_fiends_ror_0",
	"wh2_dlc14_def_inf_harpies_ror_0",
	"wh2_dlc10_def_cav_knights_of_the_ebon_claw_ror_0",
	"wh2_dlc10_def_inf_blades_of_the_blood_queen_ror_0",
}
local ROR_ADDED = {
	"wh3_dlc27_sla_mon_preyton_ror",        -- Scourge of Arden
	"wh3_twa06_sla_inf_daemonette_ror_0",   -- Bringers of Beguilement
}
local ROR_TOOLTIP = "druchii_cult_ror_not_for_cult"
local ROR_SAVE = "druchii_cult_ror_pool_v1"

local function log_ror_pool(faction, when)
	local ok, err = pcall(function()
		local units = faction:mercenary_pool():mercenary_pool_units()
		local keys = {}
		for i = 0, units:num_items() - 1 do
			local unit = units:item_at(i)
			local key = unit:unit_record():key()
			if string.find(key, "_ror", 1, true) then
				local count = "?"
				pcall(function() count = tostring(unit:count()) end)
				keys[#keys + 1] = key .. "=" .. count
			end
		end
		log("RoR pool " .. when .. " (" .. #keys .. "): " .. table.concat(keys, ", "))
	end)
	if not ok then
		log("RoR pool " .. when .. ": couldn't read the faction pool (" .. tostring(err) .. ")")
	end
end

local function setup_cult_ror()
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() or faction:is_dead() then
		return
	end
	if not cm:get_saved_value(ROR_SAVE) then
		log_ror_pool(faction, "before")
		for _, unit_key in ipairs(ROR_ADDED) do
			local ok, err = pcall(function()
				cm:add_unit_to_faction_mercenary_pool(faction, unit_key, ROR_SOURCE, 1, 100, 1, 0.1, "", "", "", true, unit_key)
			end)
			log("RoR added " .. unit_key .. (ok and "" or (" FAILED: " .. tostring(err))))
		end
		for _, unit_key in ipairs(ROR_REMOVED) do
			local ok, err = pcall(function()
				cm:add_unit_to_faction_mercenary_pool(faction, unit_key, ROR_SOURCE, 0, 0, 0, 0, "", "", "", false, unit_key)
			end)
			log("RoR zeroed " .. unit_key .. (ok and "" or (" FAILED: " .. tostring(err))))
		end
		cm:set_saved_value(ROR_SAVE, true)
		log_ror_pool(faction, "after")
	end
	for _, unit_key in ipairs(ROR_REMOVED) do
		pcall(function()
			cm:remove_event_restricted_unit_record_for_faction(unit_key, FACTION_KEY)
			cm:add_event_restricted_unit_record_for_faction(unit_key, FACTION_KEY, ROR_TOOLTIP)
		end)
	end
end

cm:add_first_tick_callback(function()
	run_step("province_caps", update_province_caps)
	run_step("barracks", convert_all_barracks)
	run_step("no_executioners", function()
		-- Har Ganeth Executioners are never recruitable by the Cult (also excluded in the DB).
		cm:add_event_restricted_unit_record_for_faction("wh2_main_def_inf_har_ganeth_executioners_0", FACTION_KEY,
			"druchii_cult_no_executioners")
	end)
	run_step("mark_of_slaanesh", function()
		-- The Mark's attributes/stats, applied to the faction (kept out of the faction bundle so the
		-- faction-select screen shows one Mark line). Permanent; only added if missing.
		if not cm:get_faction(FACTION_KEY):has_effect_bundle("druchii_cult_mark_of_slaanesh") then
			cm:apply_effect_bundle("druchii_cult_mark_of_slaanesh", FACTION_KEY, 0)
			log("Mark of Slaanesh bundle applied")
		end
	end)
	run_step("allied_expendable", function()
		-- Expendable for units from allies (units outside the Cult roster; DB bundle, permanent).
		if not cm:get_faction(FACTION_KEY):has_effect_bundle("druchii_cult_allied_expendable") then
			cm:apply_effect_bundle("druchii_cult_allied_expendable", FACTION_KEY, 0)
			log("allied Expendable bundle applied")
		end
	end)
	run_step("pleasure_through_pain", function()
		-- Witch Elves: Frenzy -> Pleasure Through Pain (DB bundle, permanent; the Death Hags were
		-- dropped from it in the DB, 2026-11-25, so the same bundle key just covers less).
		if not cm:get_faction(FACTION_KEY):has_effect_bundle("druchii_cult_pleasure_through_pain") then
			cm:apply_effect_bundle("druchii_cult_pleasure_through_pain", FACTION_KEY, 0)
			log("Pleasure Through Pain bundle applied")
		end
	end)
	run_step("regiments_of_renown", setup_cult_ror)
	run_step("allied_host", function()
		-- Base allied units per army 4 -> 6 (DB bundle, permanent).
		if not cm:get_faction(FACTION_KEY):has_effect_bundle("druchii_cult_allied_host") then
			cm:apply_effect_bundle("druchii_cult_allied_host", FACTION_KEY, 0)
			log("Sworn Allies bundle applied (+2 allied units per army)")
		end
	end)
	run_step("rite_allied_cap", function()
		-- v19: the rite no longer adds allied units (flat 6 per army from Sworn Allies); remove the old
		-- +3-per-rite bundle from saves made with v5-v18.
		if cm:get_faction(FACTION_KEY):has_effect_bundle(RITE_ALLIED_CAP_BUNDLE) then
			cm:remove_effect_bundle(RITE_ALLIED_CAP_BUNDLE, FACTION_KEY)
			log("old rite allied cap bundle removed")
		end
	end)
	run_step("guardian", function()
		-- Dreadspears: Guardian (DB bundle, permanent).
		if not cm:get_faction(FACTION_KEY):has_effect_bundle("druchii_cult_guardian") then
			cm:apply_effect_bundle("druchii_cult_guardian", FACTION_KEY, 0)
			log("Guardian bundle applied")
		end
	end)
	run_step("sacrifice_cleanup", function()
		-- The Sacrifice of Slaves bundle was the rite's Channelling bonus in older versions (on armies
		-- for the whole rite): remove it from any army the sacrifice didn't put it on.
		local saved = cm:get_saved_value("druchii_cult_sacrifice_armies") or {}
		local forces = cm:get_faction(FACTION_KEY):military_force_list()
		for i = 0, forces:num_items() - 1 do
			local force = forces:item_at(i)
			local cqi = force:command_queue_index()
			if force:has_effect_bundle("druchii_cult_rite_slaanesh_channelling") and not saved[tostring(cqi)] then
				cm:remove_effect_bundle_from_force("druchii_cult_rite_slaanesh_channelling", cqi)
				log("old rite Channelling bonus removed from army " .. cqi)
			end
		end
	end)
	run_step("rite_lock", setup_cult_rite_lock)
	run_step("ghrond_relations", court_ghrond)
	run_step("den_caps", function()
		if cm:get_faction(FACTION_KEY):has_effect_bundle(OLD_SORC_BUNDLE) then
			cm:remove_effect_bundle(OLD_SORC_BUNDLE, FACTION_KEY)
		end
		update_den_caps()
	end)
end)

cm:add_first_tick_callback_new(function()
	-- Only Immortal Empires.
	if cm:get_campaign_name() ~= "main_warhammer" then
		return
	end
	local ok, err = pcall(function()
		local faction = cm:get_faction(FACTION_KEY)
		if not faction or faction:is_null_interface() or faction:is_dead() then
			log("faction " .. FACTION_KEY .. " not found, nothing changed")
			return
		end
		local morathi = find_morathi(faction)
		if not morathi then
			log("Morathi not found, nothing changed")
			return
		end
		reshape_army(morathi)
		replace_assassin(faction, morathi)
		swap_quintex_building()
	end)
	if not ok then
		log("ERROR on first tick: " .. tostring(err))
	end
	-- Start allied with N'Kari (Seducers of Slaanesh): peace first, then a military alliance,
	-- the way CA's Chaos invasion episode allies factions.
	ok, err = pcall(function()
		local nkari = cm:get_faction(NKARI_FACTION_KEY)
		if not nkari or nkari:is_null_interface() or nkari:is_dead() then
			log("N'Kari's faction not found, no alliance")
			return
		end
		cm:force_make_peace(FACTION_KEY, NKARI_FACTION_KEY)
		cm:force_alliance(FACTION_KEY, NKARI_FACTION_KEY, true)
		log("allied with N'Kari (" .. NKARI_FACTION_KEY .. ")")
		-- Permanent relations bonus both ways (+75 each, DB bundles), so the alliance holds.
		cm:apply_effect_bundle(PACT_CULT_BUNDLE, FACTION_KEY, 0)
		cm:apply_effect_bundle(PACT_NKARI_BUNDLE, NKARI_FACTION_KEY, 0)
		log("pact relations bundles applied")
	end)
	if not ok then
		log("ERROR on first tick (N'Kari pact): " .. tostring(err))
	end
	-- The Cult of Excess starts as the Cult's vassal.
	ok, err = pcall(make_excess_vassal)
	if not ok then
		log("ERROR on first tick (Cult of Excess vassal): " .. tostring(err))
	end
	-- Arathar's army: +2 Bleakswords, +1 Darkshards, +2 Dark Riders (Repeater Crossbows).
	ok, err = pcall(reinforce_faction_leader, EXCESS_FACTION_KEY, EXCESS_EXTRA_UNITS, "Cult of Excess leader")
	if not ok then
		log("ERROR on first tick (Cult of Excess army): " .. tostring(err))
	end
	-- N'Kari's army: +2 Daemonettes, +2 Devoted Marauders of Slaanesh.
	ok, err = pcall(reinforce_faction_leader, NKARI_FACTION_KEY, NKARI_EXTRA_UNITS, "N'Kari")
	if not ok then
		log("ERROR on first tick (N'Kari's army): " .. tostring(err))
	end
	-- Trade agreements with N'Kari and the Cult of Excess.
	ok, err = pcall(make_pact_trade_agreements)
	if not ok then
		log("ERROR on first tick (trade agreements): " .. tostring(err))
	end
	-- Extra starting heroes: a Sorceress (Dark) in Saphery, a Khainite Assassin near Ghrond.
	spawn_starting_heroes()
	-- Starting Allegiance both ways with N'Kari and the Cult of Excess: CA grants Allegiance only
	-- through payloads, so it comes as incidents. A moment after the first tick, once the
	-- alliance and vassalage are in place.
	cm:callback(function()
		local ok2, err2 = pcall(grant_pact_allegiance)
		if not ok2 then
			log("ERROR granting Allegiance: " .. tostring(err2))
		end
	end, 1)
end)
