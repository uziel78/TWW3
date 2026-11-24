-- NAGGAROND-FACTION_MOD
-- 1. Reshapes Malekith's starting army in Immortal Empires.
-- 2. Slave tribute: Naggarond receives 5% of the slaves other Dark Elf factions
--    capture from battles and raiding. The other factions keep all of theirs.

local FACTION_KEY = "wh2_main_def_naggarond"
local DARK_ELF_SUBCULTURE = "wh2_main_sc_def_dark_elves"

-- While true, tribute activity is written to naggarond_faction_mod_log.txt in the
-- game folder, so the mod can be checked without CA's script-debug tools.
-- Set to false once the tribute is confirmed to work.
local DEBUG_LOG = true
local LOG_FILE = "naggarond_faction_mod_log.txt"

local function log(msg)
	out("NAGGAROND-FACTION_MOD: " .. msg)
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
-- Starting armies live in the campaign startpos file, which can't be safely
-- edited for Immortal Empires, so units are swapped on the first tick of a new
-- campaign instead (the same approach CA's own custom starts use).
-- add_first_tick_callback_new only fires on a brand-new campaign, so loading
-- a save never touches the army again.

-- Vanilla army: 2 Darkshards, 2 Dreadspears, 2 Bleakswords, 1 Black Guard, 1 Cold One Chariots.
local UNITS_TO_REMOVE = {
	"wh2_main_def_inf_bleakswords_0",
	"wh2_main_def_inf_bleakswords_0",
	"wh2_main_def_cav_cold_one_chariot",
	"wh2_main_def_inf_darkshards_0",   -- replaced by the shield version below
	"wh2_main_def_inf_darkshards_0",
}

-- Result: 2 Darkshards (Shields), 3 Dreadspears, 2 Black Guard.
-- If this changes, update the faction-screen preview list in
-- script/frontend/mod/naggarond_faction_mod_frontend.lua too.
local UNITS_TO_ADD = {
	"wh2_main_def_inf_dreadspears_0",
	"wh2_main_def_inf_black_guard_0",
	"wh2_main_def_inf_darkshards_1",   -- Darkshards (Shields)
	"wh2_main_def_inf_darkshards_1",
}

cm:add_first_tick_callback_new(function()
	-- Only Immortal Empires; Realm of Chaos has no Malekith.
	if cm:get_campaign_name() ~= "main_warhammer" then
		return
	end

	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() then
		log("faction " .. FACTION_KEY .. " not found, army unchanged")
		return
	end

	local malekith = faction:faction_leader()
	if malekith:is_null_interface() or not malekith:has_military_force() then
		log("Malekith has no army at start, army unchanged")
		return
	end

	local char_str = cm:char_lookup_str(malekith)

	for _, unit_key in ipairs(UNITS_TO_REMOVE) do
		cm:remove_unit_from_character(char_str, unit_key)
	end

	for _, unit_key in ipairs(UNITS_TO_ADD) do
		cm:grant_unit_to_character(char_str, unit_key)
	end

	log("starting army updated")
end)


---------------------------------------------------------------------------
-- 2. Slave tribute
---------------------------------------------------------------------------
-- The tooltip line lives on Malekith's faction-effects bundle
-- (naggarond_mod_faction_effects); this script does the actual work.
--
-- PooledResourceChanged fires for every slave capture with its source ("factor")
-- and amount. Each capture by another Dark Elf faction adds a share to a pending
-- tribute, and the whole pending tribute is paid at the start of Naggarond's
-- next turn (the slaves have to be shipped there first).
--
-- Paying on Naggarond's own turn also keeps it visible: the game clears each
-- round's income lines before the next round, so tribute credited during the AI
-- turns always showed 0 by the time the player opened the slave tooltip.
--
-- Share per capture, decided at the moment of capture:
--   at war with Naggarond          -> 0%
--   trade agreement with Naggarond -> 15% (10% + 5% trade bonus)
--   any other Dark Elf faction     -> 10%
-- During the Decrees of the Witch King's Age of Debauchery (Tithe of Flesh): 25% / 20%.
-- Each share is rounded up to a whole slave.

local SLAVES_KEY = "def_slaves"

local RATE_STANDARD = 0.10
local RATE_TRADE_PARTNER = 0.15
local RATE_STANDARD_DEBAUCHERY = 0.20
local RATE_TRADE_PARTNER_DEBAUCHERY = 0.25

-- Decrees of the Witch King Age bundles (see section 3); defined here because the tribute reads one.
local AGE_DEBAUCHERY = "naggarond_mod_age_debauchery"
local AGE_VENGEANCE = "naggarond_mod_age_vengeance"
local AGE_GLORIOUS_TORMENT = "naggarond_mod_age_glorious_torment"
local AGE_HATEFUL_PEACE = "naggarond_mod_age_hateful_peace"

-- Income sources (pooled resource factors) that count as "captured".
local TRIBUTE_SOURCES = {
	battles = true,   -- slaves taken after winning a battle
	raiding = true,   -- slaves taken while in raiding stance
}

-- Our own factor, so Naggarond's slave tooltip shows the tribute as its own line.
-- Using a separate factor also means our grants never re-trigger the listener.
local TRIBUTE_FACTOR = "naggarond_slave_tribute"

-- Used only if crediting through TRIBUTE_FACTOR raises an error.
local FALLBACK_FACTOR = "missions"

-- Saved in the save game, so tribute collected during the AI turns survives a
-- save and reload before Naggarond's next turn.
local PENDING_KEY = "naggarond_faction_mod_pending_tribute"

local function naggarond()
	local faction = cm:get_faction(FACTION_KEY)
	if not faction or faction:is_null_interface() then
		return nil
	end
	return faction
end

local function naggarond_is_alive()
	local faction = naggarond()
	return faction ~= nil and not faction:is_dead()
end

local function is_other_dark_elf_faction(context)
	if not context:has_faction() then
		return false
	end
	local faction = context:faction()
	return not faction:is_null_interface()
		and faction:name() ~= FACTION_KEY
		and faction:subculture() == DARK_ELF_SUBCULTURE
end

local function factor_value(resource, factor_key)
	local factor = resource:factor_by_key(factor_key)
	if not factor or factor:is_null_interface() then
		return 0
	end
	return factor:value()
end

local function naggarond_slaves()
	return naggarond():pooled_resource_manager():resource(SLAVES_KEY)
end

-- Returns the tribute share for a capturing faction, and a label for the log.
local function tribute_rate(source)
	local overlord = naggarond()
	if overlord:at_war_with(source) then
		return 0, "at war"
	end
	local debauchery = overlord:has_effect_bundle(AGE_DEBAUCHERY)
	if overlord:trade_agreement_with(source) then
		if debauchery then
			return RATE_TRADE_PARTNER_DEBAUCHERY, "trade partner, Tithe of Flesh"
		end
		return RATE_TRADE_PARTNER, "trade partner"
	end
	if debauchery then
		return RATE_STANDARD_DEBAUCHERY, "Tithe of Flesh"
	end
	return RATE_STANDARD, "standard"
end

local function get_pending()
	return cm:get_saved_value(PENDING_KEY) or 0
end

local function set_pending(amount)
	cm:set_saved_value(PENDING_KEY, amount)
end

-- Credits Naggarond with `amount` slaves under the tribute factor. Script errors
-- inside listeners are otherwise swallowed silently, so every step is wrapped in
-- pcall and logged; if our custom factor is rejected, the Missions factor is used.
local function grant_tribute(amount)
	local ok, err = pcall(function()
		local resource = naggarond_slaves()
		local before = factor_value(resource, TRIBUTE_FACTOR)
		cm:pooled_resource_factor_transaction(resource, TRIBUTE_FACTOR, amount)
		local after = factor_value(naggarond_slaves(), TRIBUTE_FACTOR)
		log("PAID tribute +" .. amount .. " at Naggarond's turn start"
			.. " (tribute factor " .. tostring(before) .. " -> " .. tostring(after)
			.. ", slaves now " .. tostring(naggarond_slaves():value()) .. ")")
	end)
	if ok then
		return
	end

	log("ERROR crediting tribute via " .. TRIBUTE_FACTOR .. ": " .. tostring(err))
	local ok2, err2 = pcall(function()
		cm:faction_add_pooled_resource(FACTION_KEY, SLAVES_KEY, FALLBACK_FACTOR, amount)
	end)
	log(ok2 and ("fallback: +" .. amount .. " via " .. FALLBACK_FACTOR)
		or ("ERROR in fallback too: " .. tostring(err2)))
end

-- Listeners aren't saved with the game, so these register on every load.
cm:add_first_tick_callback(function()
	log("slave tribute listener active (pending " .. tostring(get_pending()) .. ")")

	-- Collect: each capture by another Dark Elf faction adds its share to the pending tribute.
	core:add_listener(
		"naggarond_faction_mod_slave_tribute",
		"PooledResourceChanged",
		function(context)
			if context:amount() <= 0 then
				return false
			end

			local resource = context:resource()
			if resource:is_null_interface() or resource:key() ~= SLAVES_KEY then
				return false
			end

			local factor = context:factor()
			if not factor or factor:is_null_interface() or not TRIBUTE_SOURCES[factor:key()] then
				return false
			end

			return is_other_dark_elf_faction(context)
		end,
		function(context)
			-- Stops for good once Naggarond is destroyed.
			if not naggarond_is_alive() then
				return
			end

			local ok, err = pcall(function()
				local source = context:faction()
				local amount = context:amount()
				local rate, label = tribute_rate(source)

				-- Rounded up, so any capture from a paying faction yields at least 1 slave.
				local share = math.ceil(amount * rate)
				if share > 0 then
					set_pending(get_pending() + share)
				end

				log("capture " .. source:name() .. ": " .. amount .. " (" .. label .. ", "
					.. (rate * 100) .. "%) -> +" .. share .. ", pending " .. get_pending())
			end)
			if not ok then
				log("ERROR collecting tribute: " .. tostring(err))
			end
		end,
		true
	)

	-- Pay: the pending tribute arrives at the start of Naggarond's turn.
	core:add_listener(
		"naggarond_faction_mod_slave_tribute_payout",
		"FactionTurnStart",
		function(context)
			return context:faction():name() == FACTION_KEY
		end,
		function(context)
			local pending = get_pending()
			if pending < 1 then
				return
			end
			-- Cleared first, so a failed payout can't be paid twice.
			set_pending(0)
			grant_tribute(pending)
		end,
		true
	)
end)

---------------------------------------------------------------------------
-- 3. Decrees of the Witch King (internal keys still say black_council)
---------------------------------------------------------------------------
-- On turn 7 and every 12 turns after, the Council is called and Naggarond picks
-- one of four Ages (dilemma naggarond_mod_dilemma_black_council). Each choice
-- applies its Age as a 12-turn faction bundle through the dilemma's payload.
--
-- Most Age effects live in those bundles. These parts need a script:
--   Age of Vengeance:         Malekith gets a character bundle (the "loyalty in his
--                             region" effect must come from a character).
--   Age of Glorious Torment:  every Black Ark gets a force bundle with +20% unit and
--                             character XP (a faction bundle can't single out Black Arks),
--                             and +30% slaves from Naggarond's own Raiding stance.
--   Age of Hateful Peace:     each turn, a 20% chance that one random Lord loses 1 loyalty.
-- (Age of Debauchery's Tithe of Flesh is handled by tribute_rate above.)
-- The active Age is read from the faction's bundles, never from the choice index.
--
-- The decree also binds every other living Dark Elf faction not at war with Naggarond, except
-- the Cult of Pleasure (DECREE_EXCLUDED):
-- they get the Age's "_decree" bundle (no Tithe of Flesh, no loyalty effects, no
-- Malekith aura), plus the Black Ark XP and Raiding-stance slave bonuses. Human players
-- among them also get an incident popup. Every Naggarond turn the list is re-checked:
-- factions now at war lose the decree, factions now at peace gain it for the rest of
-- the Age. Hateful Peace's loyalty roll is for Naggarond only.

local COUNCIL_DILEMMA = "naggarond_mod_dilemma_black_council"
local COUNCIL_FIRST_TURN = 7
local COUNCIL_INTERVAL = 12
local AGE_DURATION = 12
local LAST_COUNCIL_KEY = "naggarond_faction_mod_last_council_turn"

local VENGEANCE_MALEKITH_BUNDLE = "naggarond_mod_age_vengeance_malekith"
local TORMENT_BLACK_ARK_BUNDLE = "naggarond_mod_age_glorious_torment_black_ark"
local BLACK_ARK_FORCE_TYPE = "SEA_LOCKED_HORDE"
local MALEKITH_SUBTYPE = "wh2_main_def_malekith"

local TORMENT_RAID_RATE = 0.30
local TORMENT_RAID_FACTOR = "naggarond_torment_raiding"

local PEACE_DISLOYALTY_CHANCE = 20   -- percent per Naggarond turn
local PEACE_DISLOYALTY_POINTS = -1

local ALL_AGES = { AGE_DEBAUCHERY, AGE_VENGEANCE, AGE_GLORIOUS_TORMENT, AGE_HATEFUL_PEACE }
local DECREE_INCIDENTS = {
	[AGE_DEBAUCHERY] = "naggarond_mod_incident_decree_debauchery",
	[AGE_VENGEANCE] = "naggarond_mod_incident_decree_vengeance",
	[AGE_GLORIOUS_TORMENT] = "naggarond_mod_incident_decree_glorious_torment",
	[AGE_HATEFUL_PEACE] = "naggarond_mod_incident_decree_hateful_peace",
}
local DECREE_AGE_KEY = "naggarond_faction_mod_decree_age"
local DECREE_END_KEY = "naggarond_faction_mod_decree_end_turn"

local function is_council_turn(turn)
	return turn >= COUNCIL_FIRST_TURN and (turn - COUNCIL_FIRST_TURN) % COUNCIL_INTERVAL == 0
end

-- Dark Elf factions the decrees never bind (2026-11-24: the Cult of Pleasure, which has its own
-- reworked mechanics in Druchii_Cult-of-Pleasure_MOD). sync_decree lifts any decree they already
-- have, so the Black Ark XP aura and the Glorious Torment raiding bonus stop for them too.
local DECREE_EXCLUDED = {
	wh2_main_def_cult_of_pleasure = true,
}

-- The bundle the other Dark Elf factions get for an Age.
local function decree_bundle(age)
	return age .. "_decree"
end

-- Is this faction (Naggarond, or a Dark Elf faction bound by the decree) in an Age?
local function in_age(faction, age)
	if faction:name() == FACTION_KEY then
		return faction:has_effect_bundle(age)
	end
	return faction:has_effect_bundle(decree_bundle(age))
end

local function other_dark_elf_factions()
	local out = {}
	local factions = cm:model():world():faction_list()
	for i = 0, factions:num_items() - 1 do
		local faction = factions:item_at(i)
		if faction:name() ~= FACTION_KEY and faction:subculture() == DARK_ELF_SUBCULTURE and not faction:is_dead() then
			table.insert(out, faction)
		end
	end
	return out
end

-- Age of Hateful Peace: idle Dreadlords scheme. One roll per turn; on a hit, one
-- random Lord with an army (any Lord type, incl. High Sorceresses and Beastmasters,
-- never Malekith himself) loses a point of loyalty.
local function roll_peace_disloyalty(faction)
	if not faction:has_effect_bundle(AGE_HATEFUL_PEACE) then
		return
	end
	if cm:random_number(100) > PEACE_DISLOYALTY_CHANCE then
		log("Age of Hateful Peace: no Lord lost loyalty this turn")
		return
	end
	local lords = {}
	local characters = faction:character_list()
	for i = 0, characters:num_items() - 1 do
		local character = characters:item_at(i)
		if cm:char_is_general_with_army(character) and not character:is_faction_leader()
			and not character:military_force():is_armed_citizenry() then
			table.insert(lords, character)
		end
	end
	if #lords == 0 then
		log("Age of Hateful Peace: roll hit, but no Lord to lose loyalty")
		return
	end
	local lord = lords[cm:random_number(#lords)]
	cm:modify_character_personal_loyalty_factor(cm:char_lookup_str(lord), PEACE_DISLOYALTY_POINTS)
	log("Age of Hateful Peace: " .. lord:character_subtype_key() .. " (cqi " .. lord:cqi()
		.. ") lost 1 loyalty, now " .. tostring(lord:loyalty()))
end

local function find_malekith(faction)
	local characters = faction:character_list()
	for i = 0, characters:num_items() - 1 do
		local character = characters:item_at(i)
		if character:character_subtype(MALEKITH_SUBTYPE) and not character:is_wounded() then
			return character
		end
	end
	return nil
end

-- Re-applied every Naggarond turn while the Age lasts, so Black Arks built during
-- the Age get the XP bonus too; a 2-turn duration bridges the gap to the next refresh.
local function refresh_black_ark_auras(faction)
	if not in_age(faction, AGE_GLORIOUS_TORMENT) then
		return
	end
	local forces = faction:military_force_list()
	local count = 0
	for i = 0, forces:num_items() - 1 do
		local force = forces:item_at(i)
		if force:force_type():key() == BLACK_ARK_FORCE_TYPE then
			cm:apply_effect_bundle_to_force(TORMENT_BLACK_ARK_BUNDLE, force:command_queue_index(), 2)
			count = count + 1
		end
	end
	log("Age of Glorious Torment: XP bonus refreshed on " .. count .. " Black Ark(s) of " .. faction:name())
end

-- Bring every other Dark Elf faction in line with the current decree. With announce
-- (right after a new decree) every bound faction gets the Age afresh and human players
-- get the popup; otherwise only factions that just made peace get it (with the popup
-- for humans), and factions now at war, or whose Age has run out, lose it.
local function sync_decree(nag, announce)
	local age = cm:get_saved_value(DECREE_AGE_KEY)
	local remaining = (cm:get_saved_value(DECREE_END_KEY) or 0) - cm:model():turn_number()
	for _, faction in ipairs(other_dark_elf_factions()) do
		local key = faction:name()
		local bound = not DECREE_EXCLUDED[key] and age ~= nil and remaining > 0 and not nag:at_war_with(faction)
		for _, a in ipairs(ALL_AGES) do
			if faction:has_effect_bundle(decree_bundle(a)) and (not bound or a ~= age) then
				cm:remove_effect_bundle(decree_bundle(a), key)
				log("decree lifted from " .. key .. " (" .. a .. ")")
			end
		end
		if bound then
			if announce or not faction:has_effect_bundle(decree_bundle(age)) then
				cm:apply_effect_bundle(decree_bundle(age), key, remaining)
				local shown = false
				if faction:is_human() then
					-- The popup's payload is the same bundle; re-applying it only refreshes it,
					-- and any overshoot past the Age's end is lifted by the check above.
					shown = cm:trigger_incident(key, DECREE_INCIDENTS[age], true, true)
				end
				log("decree " .. age .. " bound on " .. key .. " for " .. remaining .. " turns"
					.. (faction:is_human() and (" (popup: " .. tostring(shown) .. ")") or ""))
			end
			refresh_black_ark_auras(faction)
		elseif announce and age ~= nil then
			log("decree " .. age .. " NOT bound on " .. key
				.. (DECREE_EXCLUDED[key] and " (excluded)" or " (at war with Naggarond)"))
		end
	end
end

-- Malekith's regional loyalty aura, for the rest of the Age of Vengeance.
local function apply_vengeance_aura(faction, turns)
	local malekith = find_malekith(faction)
	if malekith then
		cm:apply_effect_bundle_to_character(VENGEANCE_MALEKITH_BUNDLE, malekith, turns)
		log("Age of Vengeance: loyalty aura applied to Malekith for " .. turns .. " turns")
	else
		log("Age of Vengeance: Malekith not available, loyalty aura skipped")
	end
end

-- Once an Age's bundle is on Naggarond (chosen by the player, or picked for the AI): save it and
-- start its scripted parts.
local function start_chosen_age()
	local faction = naggarond()
	for _, age in ipairs(ALL_AGES) do
		if faction:has_effect_bundle(age) then
			log("the Witch King decrees: " .. age)
			cm:set_saved_value(DECREE_AGE_KEY, age)
			cm:set_saved_value(DECREE_END_KEY, cm:model():turn_number() + AGE_DURATION)
		end
	end
	if faction:has_effect_bundle(AGE_VENGEANCE) then
		apply_vengeance_aura(faction, AGE_DURATION)
	end
	refresh_black_ark_auras(faction)
	sync_decree(faction, true)
end

-- AI Naggarond: no dilemma. v1 triggered the dilemma for the AI too; it was left unanswered in
-- every campaign after the first, and the game stalled at Naggarond's next turn start (twice,
-- "faction 41 of 241"). Now the AI's Age is picked at random and applied directly (the same
-- 12-turn bundle the dilemma's choice gives).
local function decree_for_ai()
	local age = ALL_AGES[cm:random_number(#ALL_AGES)]
	cm:apply_effect_bundle(age, FACTION_KEY, AGE_DURATION)
	log("the Witch King (AI) issues a decree without a dilemma: " .. age)
	cm:callback(function()
		local ok, err = pcall(start_chosen_age)
		if not ok then
			log("ERROR applying the AI's Age: " .. tostring(err))
		end
	end, 0.5)
end

cm:add_first_tick_callback(function()
	log("Decrees of the Witch King active (last decree on turn " .. tostring(cm:get_saved_value(LAST_COUNCIL_KEY)) .. ")")

	-- Call the Council, and keep the Age's scripted parts going.
	core:add_listener(
		"naggarond_faction_mod_black_council",
		"FactionTurnStart",
		function(context)
			return context:faction():name() == FACTION_KEY
		end,
		function(context)
			local ok, err = pcall(function()
				local faction = context:faction()
				local turn = cm:model():turn_number()

				sync_decree(faction, false)
				refresh_black_ark_auras(faction)
				roll_peace_disloyalty(faction)

				if is_council_turn(turn) and cm:get_saved_value(LAST_COUNCIL_KEY) ~= turn then
					cm:set_saved_value(LAST_COUNCIL_KEY, turn)
					if faction:is_human() then
						cm:trigger_dilemma(FACTION_KEY, COUNCIL_DILEMMA)
						log("the Witch King issues a decree (turn " .. turn .. ")")
					else
						-- A moment later, outside the turn-start event.
						cm:callback(function()
							local ok2, err2 = pcall(decree_for_ai)
							if not ok2 then
								log("ERROR in the AI's decree: " .. tostring(err2))
							end
						end, 0.5)
					end
				end
			end)
			if not ok then
				log("ERROR in Decrees turn start: " .. tostring(err))
			end
		end,
		true
	)

	-- After the choice: start the scripted parts of the chosen Age straight away.
	core:add_listener(
		"naggarond_faction_mod_black_council_choice",
		"DilemmaChoiceMadeEvent",
		function(context)
			return context:dilemma() == COUNCIL_DILEMMA
		end,
		function(context)
			-- Short delay so the payload's bundle is in place before we read it.
			cm:callback(function()
				local ok, err = pcall(start_chosen_age)
				if not ok then
					log("ERROR applying the chosen Age: " .. tostring(err))
				end
			end, 0.5)
		end,
		true
	)

	-- Age of Glorious Torment: +30% slaves from Raiding stance (rounded up), for Naggarond
	-- and for every Dark Elf faction bound by the decree.
	core:add_listener(
		"naggarond_faction_mod_torment_raiding",
		"PooledResourceChanged",
		function(context)
			if context:amount() <= 0 or not context:has_faction() then
				return false
			end
			if context:faction():is_null_interface() or context:faction():subculture() ~= DARK_ELF_SUBCULTURE then
				return false
			end
			local resource = context:resource()
			local factor = context:factor()
			return not resource:is_null_interface() and resource:key() == SLAVES_KEY
				and factor and not factor:is_null_interface() and factor:key() == "raiding"
		end,
		function(context)
			local ok, err = pcall(function()
				local faction = context:faction()
				if not in_age(faction, AGE_GLORIOUS_TORMENT) then
					return
				end
				local bonus = math.ceil(context:amount() * TORMENT_RAID_RATE)
				-- Our own factor, so this grant never re-triggers this listener.
				cm:pooled_resource_factor_transaction(context:resource(), TORMENT_RAID_FACTOR, bonus)
				log("Age of Glorious Torment: " .. faction:name() .. " raided " .. context:amount()
					.. " slaves -> +" .. bonus)
			end)
			if not ok then
				log("ERROR in Glorious Torment raiding bonus: " .. tostring(err))
			end
		end,
		true
	)
end)
