-- Druchii_Cult-of-Pleasure_MOD (frontend)
-- Shows Morathi's modded starting army on the campaign faction-select screen.
--
-- The vanilla screen reads the preview army straight from the campaign startpos, which this
-- mod doesn't touch (the real army is swapped by the campaign script). Mixu's Unlocker ships
-- its own version of that screen with a hook for overriding the preview per faction, so this
-- only works while it is enabled; without it this does nothing and the screen keeps showing
-- the vanilla army. Mixu's screen shows one card per unit type, so counts aren't shown.

-- Keep in sync with the army in script/campaign/mod/druchii_cult_of_pleasure.lua.
local FACTION_KEY = "wh2_main_def_cult_of_pleasure"
local STARTING_UNITS = {
	"wh3_dlc27_sla_inf_devotees_of_slaanesh",            -- Devotees of Slaanesh x2
	"wh3_dlc27_sla_inf_devotees_of_slaanesh",
	"wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows",  -- Devotees of Slaanesh (Crossbows)
	"wh3_main_sla_inf_daemonette_0",                     -- Daemonettes of Slaanesh
	"wh2_main_def_cav_dark_riders_1",                    -- Dark Riders (Shields)
	"wh2_main_def_cav_dark_riders_2",                    -- Dark Riders (Repeater Crossbows)
}

core:add_ui_created_callback(function()
	if type(mixer_add_starting_unit_list_for_faction) ~= "function" then
		out("Druchii_Cult-of-Pleasure_MOD: Mixu's Unlocker not loaded, faction screen keeps the vanilla army")
		return
	end
	mixer_add_starting_unit_list_for_faction(FACTION_KEY, STARTING_UNITS)
	out("Druchii_Cult-of-Pleasure_MOD: faction screen starting units overridden via Mixu's Unlocker")
end)
