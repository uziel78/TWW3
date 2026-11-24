-- NAGGAROND-FACTION_MOD (frontend)
-- Shows Malekith's modded starting army on the campaign faction-select screen.
--
-- The vanilla screen reads the preview army straight from the campaign startpos
-- file, which this mod doesn't touch (the real army is swapped by the campaign
-- script). Mixu's Unlocker ships its own version of that screen with a hook for
-- overriding the preview per faction, so this only works while it is enabled.
-- Without it, mixer_add_starting_unit_list_for_faction doesn't exist, this does
-- nothing, and the screen keeps showing the vanilla army.
--
-- Mixu's screen shows one card per unit type, so the counts (2 / 3 / 2) aren't shown.

-- Keep in sync with the army in script/campaign/mod/naggarond_faction_mod.lua.
local FACTION_KEY = "wh2_main_def_naggarond"
local STARTING_UNITS = {
	"wh2_main_def_inf_darkshards_1",   -- Darkshards (Shields) x2
	"wh2_main_def_inf_darkshards_1",
	"wh2_main_def_inf_dreadspears_0",  -- Dreadspears x3
	"wh2_main_def_inf_dreadspears_0",
	"wh2_main_def_inf_dreadspears_0",
	"wh2_main_def_inf_black_guard_0",  -- Black Guard of Naggarond x2
	"wh2_main_def_inf_black_guard_0",
}

core:add_ui_created_callback(function()
	if type(mixer_add_starting_unit_list_for_faction) ~= "function" then
		out("NAGGAROND-FACTION_MOD: Mixu's Unlocker not loaded, faction screen keeps the vanilla army")
		return
	end

	mixer_add_starting_unit_list_for_faction(FACTION_KEY, STARTING_UNITS)
	out("NAGGAROND-FACTION_MOD: faction screen starting units overridden via Mixu's Unlocker")
end)
