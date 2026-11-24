-- Druchii_Malekith_MOD: hide the leftover "Construction cost: +0%" line on the faction screen.
--
-- The faction screen lists the effects of the innate skill baked into the startpos, i.e. the
-- vanilla skill, whose construction row can only be set to 0 (a mod can't delete it).
--
-- What earlier test logs established (see the _testN logs in the game folder):
--   * the rows are clones of "template_effect" inside "lord_effects_list", at
--     campaign_select_new > right_holder > tab_lord > lord_details_panel > lord_info >
--     tab_details > holder_lord_details > list_clip > list_box > lord_effects_list;
--     each row shows its effect text as its own state text (ContextTextLabel on the row);
--   * walking the UI tree generically doesn't work in the frontend (the root's ChildCount isn't
--     a number, and guarded child access came back empty), so this follows Mixu's working
--     pattern exactly: look the list up by its full path, and read rows with
--     UIComponent(list:Find(i)), right after a screen change or click.
-- After each screen change or click, the list is checked every 100 ms for 3 seconds (the rows
-- animate in), plus a slow background check. Only a row reading "Construction cost" with a
-- zero value is hidden; other rows and other lords are never touched.
--
-- While DEBUG_LOG is true, findings go to druchii_malekith_frontend_log.txt in the game folder.

local DEBUG_LOG = true
local LOG_FILE = "druchii_malekith_frontend_log.txt"
local LIST_PATH = { "campaign_select_new", "right_holder", "tab_lord", "lord_details_panel", "lord_info",
	"tab_details", "holder_lord_details", "list_clip", "list_box", "lord_effects_list" }

local function log(msg)
	if not DEBUG_LOG then
		return
	end
	local ok, file = pcall(io.open, LOG_FILE, "a")
	if ok and file then
		file:write(msg .. "\n")
		file:close()
	end
end

local logged = {}
local function log_once(msg)
	if not logged[msg] then
		logged[msg] = true
		log(msg)
	end
end

local function is_zero_construction(text)
	return string.find(text, "Construction cost", 1, true) ~= nil
		and (string.find(text, "+0%", 1, true) ~= nil or string.find(text, "[^%d%.]0%%") ~= nil)
end

local function get_list()
	return find_uicomponent(core:get_ui_root(), unpack(LIST_PATH))
		or find_uicomponent(core:get_ui_root(), "campaign_select_new", "lord_effects_list")
end

local function check_list(reason)
	local list = get_list()
	if not list then
		log_once("list not found (" .. reason .. ")")
		return
	end
	local rows = {}
	for i = 0, list:ChildCount() - 1 do
		local row = UIComponent(list:Find(i))
		local text = row:GetStateText() or ""
		table.insert(rows, row:Id() .. (row:Visible() and "" or "[hidden]") .. " = " .. text:gsub("%s+", " "))
		if row:Visible() and is_zero_construction(text) then
			row:SetVisible(false)
			log_once("hid: " .. row:Id() .. " = " .. text:gsub("%s+", " "))
		end
	end
	log_once("rows (" .. reason .. "): " .. table.concat(rows, " || "))
end

local burst = 0
local function start_burst(reason)
	burst = burst + 1
	local name = "druchii_malekith_burst_" .. burst
	local remaining = 30
	local function step()
		local ok, err = pcall(check_list, reason)
		if not ok then
			log_once("ERROR (" .. reason .. "): " .. tostring(err))
		end
		remaining = remaining - 1
		if remaining > 0 then
			core:get_tm():real_callback(step, 100, name)
		end
	end
	core:get_tm():real_callback(step, 100, name)
end

local ok_file, file = pcall(io.open, LOG_FILE, "w")
if ok_file and file and DEBUG_LOG then
	file:write("Druchii_Malekith_MOD frontend script loaded (v5: Mixu-style full-path lookup)\n")
	file:close()
end

core:add_listener(
	"druchii_malekith_screen_transition",
	"FrontendScreenTransition",
	function(context)
		return context.string == "campaign_select_new"
	end,
	function()
		start_burst("screen opened")
	end,
	true
)

core:add_listener(
	"druchii_malekith_click",
	"ComponentLClickUp",
	true,
	function(context)
		start_burst("click " .. tostring(context.string))
	end,
	true
)

core:add_ui_created_callback(function()
	log("ui created")
	core:get_tm():repeat_real_callback(function()
		local ok, err = pcall(check_list, "background")
		if not ok then
			log_once("ERROR (background): " .. tostring(err))
		end
	end, 500, "druchii_malekith_background_check")
end)
