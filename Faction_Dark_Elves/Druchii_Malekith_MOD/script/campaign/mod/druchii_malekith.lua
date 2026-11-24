-- Druchii_Malekith_MOD: give Malekith the clean copy of his innate skill.
--
-- The vanilla innate skill (wh2_main_skill_innate_def_malekith) is baked into the campaign
-- startpos, and a mod can't delete its "Construction cost" row, only set it to 0. So once the
-- campaign is running, Malekith's background skill is swapped for druchii_malekith_skill_innate,
-- which has the same new effects without that row. The swap follows CA's own
-- wh3_campaign_innate_trait_reset.lua. It's checked on the first tick (covers new campaigns and
-- existing saves) and at the start of every Dark Elf faction's turn (covers a Malekith who
-- respawns or joins another faction).

local MALEKITH_SUBTYPE = "wh2_main_def_malekith"
local VANILLA_INNATE = "wh2_main_skill_innate_def_malekith"
local NEW_INNATE = "druchii_malekith_skill_innate"
local DARK_ELF_SUBCULTURE = "wh2_main_sc_def_dark_elves"

local function log(msg)
	if out then
		out("[Druchii_Malekith_MOD] " .. msg)
	end
end

local function swap_innate(character)
	if character:is_null_interface() or not character:character_subtype(MALEKITH_SUBTYPE) then
		return
	end
	local details = character:character_details()
	if details:background_skill() ~= VANILLA_INNATE then
		return
	end
	cm:remove_skill_point(cm:char_lookup_str(character), VANILLA_INNATE, false)
	cm:character_details_pick_background_skill(details, NEW_INNATE, false)
	cm:character_details_add_skill_point(details, NEW_INNATE)
	log("innate skill swapped for " .. character:faction():name() .. " (cqi " .. character:cqi() .. ")")
end

local function check_faction(faction)
	local characters = faction:character_list()
	for i = 0, characters:num_items() - 1 do
		swap_innate(characters:item_at(i))
	end
end

cm:add_first_tick_callback(function()
	local ok, err = pcall(function()
		local factions = cm:model():world():faction_list()
		for i = 0, factions:num_items() - 1 do
			local faction = factions:item_at(i)
			if faction:subculture() == DARK_ELF_SUBCULTURE then
				check_faction(faction)
			end
		end
	end)
	if not ok then
		log("ERROR on first tick: " .. tostring(err))
	end

	core:add_listener(
		"druchii_malekith_innate_swap",
		"FactionTurnStart",
		function(context)
			return context:faction():subculture() == DARK_ELF_SUBCULTURE
		end,
		function(context)
			local ok2, err2 = pcall(check_faction, context:faction())
			if not ok2 then
				log("ERROR on turn start: " .. tostring(err2))
			end
		end,
		true
	)
end)
