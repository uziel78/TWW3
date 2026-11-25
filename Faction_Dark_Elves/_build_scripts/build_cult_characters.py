"""Write Druchii_Cult-Characters_MOD's DB tables, loc file and portrait settings into a pack source folder.

New characters for the Cult of Pleasure (wh2_main_def_cult_of_pleasure) only. Each character is a
new agent subtype copied from a vanilla one, so its skills, spells, mounts and looks can be edited
without touching the vanilla character other factions use.

1. Sorceress (Slaanesh)          hero  (wizard)   copy of the Sorceress (Dark Magic)
2. Supreme Sorceress (Slaanesh)  lord  (general)  copy of the Supreme Sorceress (Dark Magic)
   Both are extra lore options next to the vanilla lores (which the Cult keeps). The Lore of Dark
   Magic row of the copied skill tree is swapped for the Lore of Slaanesh, spell for spell, in
   CA's own order (heroes: the Alluress (Slaanesh) row; lords: the Sorcerer Lord of Slaanesh row:
   lords start with Lash of Slaanesh + Acquiescence like Dark lords start with Chillwind + Power
   of Darkness).
3. Cultist of Slaanesh          hero  (dignitary) copy of the Slaanesh Cultist, Cult only
   Female art sets (Dark Elf "dignitary" heroes are generated female: agent_culture_details 610 is
   the Death Hag), same Cultist models/portraits. The vanilla Cultist the Cult pack permits is
   disabled for the Cult here (this pack loads before Druchii_Cult-of-Pleasure_MOD, so its row wins;
   without this pack the Cult falls back to the vanilla Cultist). The Den of Indulgence effects
   (Cult pack section 17) need no change: cap and rank are per agent type (dignitary), and the
   recruitment effect gets a subtype link to the new Cultist by the copy.

How a copy is made (see docs/ENGINE_LESSONS.md, "Characters, skills ..."):
- every row of the tables in COPY_TABLES that names one of the character's keys (subtype, units,
  mount ancillaries, mount skills, subtype-specific skill nodes, skill tree, art sets) is copied
  with the keys renamed; shared skill nodes (immortality, mentor, ...) are reused as they are;
- permissions only for the Cult and its rebels; the military group is the Cult's own;
- art sets get new ids, so the mod ships portrait entries for them in
  ui/portraits/{portholes,units}/portrait_settings__druchii_cult_characters.bin (DOUBLE
  underscore, like vanilla's portrait_settings__.bin; v21 of the Cult mod used one underscore);
- loc: every vanilla loc entry of a copied key is copied, "(Dark)" -> "(Slaanesh)".

Usage: build_cult_characters.py <pack source folder>
"""
import os, pickle, struct, sys, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import re
import twpack
twpack.round = lambda x, n=None: x      # exact F32 values in copies (twpack rounds to 4 decimals for diffs)
from twpack import Pack, DATA, SCHEMA, table, encode_db, table_version

root = sys.argv[1]
FRAG = 'Druchii_Cult-Characters_MOD'
FACTION = 'wh2_main_def_cult_of_pleasure'
CULT_FACTIONS = [FACTION, 'wh2_main_def_cult_of_pleasure_separatists']
CULT_MILITARY_GROUP = 'wh3_main_def_morathi'

db = Pack(DATA + r'\db.pack')
ui_pack = Pack(DATA + r'\ui.pack')
loc_vanilla = pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loc_en.pkl'), 'rb'))
out_tables, loc = {}, {}
_cache = {}


def T(name):
    if name not in _cache:
        _cache[name] = table(db, name)
    return _cache[name]


def add(table_name, **row):
    out_tables.setdefault(table_name, []).append(row)


def new_key(text, taken):
    k = zlib.crc32(text.encode()) & 0x7fffffff
    while k in taken:
        k = (k + 1) & 0x7fffffff
    taken.add(k)
    return k


# Tables copied for a character, and how a row is picked: 'any' = any string value is a mapped key.
# NOT copied: main_unit_ownership_content_pack_junctions / agent_subtype_ownership_content_pack_junctions
# (DLC ownership). New rows there crash the game a few seconds after Play (ladder test 2e,
# 2026-11-25); modded units/subtypes without ownership rows are simply always available.
# Integer key columns that need fresh ids: {table: column}.
COPY_TABLES = [
    'agent_subtypes_tables', 'agent_subtype_set_items_tables', 'campaign_agent_subtype_factorial_effect_junctions_tables',
    'effect_bonus_value_agent_subtype_junctions_tables', 'ancillaries_included_agent_subtypes_tables',
    'campaign_character_art_sets_tables', 'campaign_character_arts_tables', 'character_skill_node_sets_tables',
    'faction_agent_permitted_subtypes_tables',
    'main_units_tables', 'land_units_tables', 'land_units_to_unit_abilites_junctions_tables',
    'campaign_mount_animation_set_overrides_tables', 'unit_variants_tables', 'ui_unit_bullet_point_unit_overrides_tables',
    'special_ability_groups_to_units_junctions_tables', 'unit_banner_unit_height_offsets_tables',
    'campaign_map_attrition_unit_immunities_tables', 'unit_set_to_unit_junctions_tables', 'unit_to_unit_list_junctions_tables',
    'units_to_groupings_military_permissions_tables', 'land_units_to_battle_personalities_junctions_tables',
    # Groups named after the unit / subtype (v2 renamed the references but not these rows -> the game
    # closed at the start-up logos): attribute groups, UI unit groups.
    'unit_attributes_groups_tables', 'unit_attributes_to_groups_junctions_tables', 'ui_unit_groupings_tables',
    # Rows every vanilla character unit has (v3 left them out; game closed a few seconds after Play):
    # battle-currency cost and the army generator's quality tier. Custom-battle permissions are left
    # out on purpose (they're per vanilla faction and these are campaign characters).
    'battle_currency_units_cost_values_tables', 'cdir_military_generator_unit_qualities_tables',
    'ancillaries_tables', 'ancillary_to_included_agents_tables', 'ancillary_to_effects_tables', 'ancillary_info_tables',
    'character_skills_tables', 'character_skill_level_details_tables', 'character_skill_level_to_ancillaries_junctions_tables',
    'character_skill_level_to_effects_junctions_tables', 'character_skill_utilization_hints_junctions_tables',
    'character_skills_to_level_reached_criterias_tables',
    'character_skill_nodes_tables', 'character_skill_node_set_items_tables', 'character_skill_node_links_tables',
    'character_skill_nodes_skill_locks_tables', 'character_skill_node_ancillary_locks_tables',
]
# Tables that define something: a row is copied only if its own key is one of the character's keys (a
# reference alone isn't enough: v5 copied, i.e. overrode, the vanilla Warshrine Cultist unit because its
# UI group was the vanilla Cultist's subtype key).
OWN_KEY = {'agent_subtypes_tables': 'key', 'main_units_tables': 'unit', 'land_units_tables': 'key',
           'ancillaries_tables': 'key', 'character_skills_tables': 'key', 'character_skill_nodes_tables': 'key',
           'character_skill_node_sets_tables': 'key', 'campaign_character_art_sets_tables': 'art_set_id',
           'unit_attributes_groups_tables': 'group_name', 'ui_unit_groupings_tables': 'key'}
INT_IDS = {'campaign_agent_subtype_factorial_effect_junctions_tables': 'key', 'campaign_character_arts_tables': 'id'}
taken_ids = {t: {r[c] for r in T(t)} for t, c in INT_IDS.items()}


_schema_txt = open(SCHEMA, encoding='utf-8').read()
_linked = {}


def linked_columns(t):
    """Columns that are keys or references in the schema (the only ones renamed in a copy; plain
    columns like icon or label names keep vanilla values: v3 renamed the Cultist's UI group icon)."""
    if t not in _linked:
        ver = table_version(db, t)
        m = re.search(r'^        "%s": \[\n(.*?)^        \],' % t, _schema_txt, re.S | re.M)
        vm = next(x for x in re.finditer(r'version: (\d+),\s*fields: \[(.*?)\n                \],', m.group(1), re.S)
                  if int(x.group(1)) == ver)
        _linked[t] = {fm.group(1) for fm in re.finditer(r'\(\s*name: "(\w+)",(.*?)\n                    \)', vm.group(2), re.S)
                      if 'is_key: true' in fm.group(2) or 'is_reference: Some' in fm.group(2)}
    return _linked[t]


def strip_prefix(key):
    """wh2_main_def_cha_sorceress_dark_0 -> def_cha_sorceress_dark_0 (drop the wh*_<pack>_ prefix)."""
    parts = key.split('_', 2)
    return parts[2] if len(parts) == 3 and parts[0].startswith('wh') else key


def copy_character(src_subtype, new_subtype, src_token, new_token, lore_map, names, small_icon=None, female=None,
                   ui_group=None, ability_groups=None, magic_lore=None):
    """Copy a vanilla subtype and everything that belongs to it; returns the key map."""
    rename = lambda k: 'druchii_cult_' + strip_prefix(k).replace(src_token, new_token)
    M = {src_subtype: new_subtype}
    sub = next(r for r in T('agent_subtypes_tables') if r['key'] == src_subtype)
    base_unit = sub['associated_unit_override']
    unit_prefix = base_unit.rsplit('_', 1)[0] + '_'              # ..._sorceress_dark_
    for r in T('main_units_tables'):
        if r['unit'].startswith(unit_prefix) and r['unit'][len(unit_prefix):].isdigit():
            M[r['unit']] = rename(r['unit'])
            M[r['land_unit']] = rename(r['land_unit'])
    mounts = [r['ancillary'] for r in T('ancillaries_included_agent_subtypes_tables') if r['agent_subtype'] == src_subtype]
    for a in mounts:
        M[a] = rename(a)
    for r in T('character_skill_level_to_ancillaries_junctions_tables'):
        if r['granted_ancillary'] in mounts:
            M[r['skill']] = rename(r['skill'])
    node_set = next(r['key'] for r in T('character_skill_node_sets_tables') if r['agent_subtype_key'] == src_subtype)
    M[node_set] = rename(node_set)
    for r in T('character_skill_node_set_items_tables'):
        if r['set'] == node_set and src_token in r['item']:      # subtype-specific nodes; shared ones are reused
            M[r['item']] = rename(r['item'])
    for r in T('campaign_character_art_sets_tables'):
        if r['agent_subtype'] == src_subtype:
            M[r['art_set_id']] = rename(r['art_set_id'])
    assert len(set(M.values())) == len(M), 'duplicate new keys'

    for t in COPY_TABLES:
        for r in T(t):
            if t == 'character_skill_node_set_items_tables':
                hit = r['set'] == node_set
            else:
                hit = any(isinstance(v, str) and v in M for v in r.values())
            if not hit or (t in OWN_KEY and r[OWN_KEY[t]] not in M):
                continue
            linked = linked_columns(t)
            row = {k: (M.get(v, v) if isinstance(v, str) and k in linked else v) for k, v in r.items()}
            if t == 'faction_agent_permitted_subtypes_tables':
                if r['faction'] != FACTION:
                    continue
                for f in CULT_FACTIONS:
                    add(t, **dict(row, faction=f, mod_disabled=False))
                continue
            if t == 'units_to_groupings_military_permissions_tables':
                continue                                          # added below, Cult group only
            if t == 'unit_set_to_unit_junctions_tables' and r['unit_set'] in M:
                # A set named after a unit (wh2_main_def_cha_sorceress_dark_0) gives garrison
                # Sorceresses their Dark spells; not for recruited characters, and a renamed set
                # would have no unit_sets row.
                continue
            if t in INT_IDS:
                col = INT_IDS[t]
                row[col] = new_key(f'{new_subtype}_{r[col]}', taken_ids[t])
            if t == 'character_skill_nodes_tables' and row['character_skill_key'] in lore_map:
                row['character_skill_key'] = lore_map[row['character_skill_key']]
            if t == 'main_units_tables' and ui_group:
                row['ui_unit_group_land'] = ui_group        # unit group (not the lore tab, see below)
            if t == 'special_ability_groups_to_units_junctions_tables' and ability_groups:
                # The spell group is the lore tab in the lord recruitment list ("Lore of Dark Magic" =
                # special_ability_groups_name_wh2_main_lore_dark_magic) and the spell bar group in battle.
                row['ability_group'] = ability_groups.get(row['ability_group'], row['ability_group'])
            if t == 'agent_subtypes_tables' and magic_lore:
                # The lord recruitment list groups lords into lore tabs by this column (v8 still had
                # wh2_main_lore_dark_magic and sat in the Dark Magic tab). Heroes leave it empty.
                row['magic_lore'] = magic_lore
            if t == 'agent_subtypes_tables' and small_icon:
                row['small_icon'] = small_icon
            if t == 'campaign_character_art_sets_tables' and female is not None:
                row['is_male'] = not female
            add(t, **row)
    # Permitted for the Cult and its rebels even if vanilla never permitted the source subtype for the
    # Cult (the Slaanesh Cultist: the Cult pack added that one).
    agent = next(r['agent'] for r in T('faction_agent_permitted_subtypes_tables') if r['subtype'] == src_subtype)
    permitted = {(r['faction'], r['subtype']) for r in out_tables.get('faction_agent_permitted_subtypes_tables', [])}
    for f in CULT_FACTIONS:
        if (f, new_subtype) not in permitted:
            add('faction_agent_permitted_subtypes_tables', agent=agent, faction=f, subtype=new_subtype, mod_disabled=False)
    for old, new in M.items():
        if old in {r['unit'] for r in T('main_units_tables')}:
            add('units_to_groupings_military_permissions_tables', unit=new, military_group=CULT_MILITARY_GROUP)

    # Loc: every vanilla entry of a copied key (<table>_<column>_<key>), names fixed up.
    suffixes = sorted(M, key=len, reverse=True)
    for k, v in loc_vanilla.items():
        for old in suffixes:
            if k.endswith('_' + old):
                loc[k[:-len(old)] + M[old]] = v.replace('(Dark)', '(Slaanesh)').replace('Lore of Dark Magic', 'Lore of Slaanesh')
                break
    for key, text in names.items():
        loc[key] = text
    return M


# --------------------------------------------------------------------------
# 1. Sorceress (Slaanesh), hero
# --------------------------------------------------------------------------
LORE_ICON = 'ui/campaign ui/agents/wh3_main_lore_slaanesh.png'
HERO_LORE = {
    'wh2_main_skill_magic_dark_chillwind': 'wh3_main_skill_sla_magic_slaanesh_01_lash_of_slaanesh',
    'wh2_main_skill_magic_dark_lore_attribute': 'wh3_main_skill_sla_magic_slaanesh_05_blissful_rapture',
    'wh2_main_skill_magic_dark_power_of_darkness': 'wh3_main_skill_sla_magic_slaanesh_02_acquiescence',
    'wh2_main_skill_magic_dark_word_of_pain': 'wh3_main_skill_sla_magic_slaanesh_03_pavane_of_slaanesh',
    'wh2_main_skill_magic_dark_bladewind': 'wh3_main_skill_sla_magic_slaanesh_04_hysterical_frenzy',
    'wh2_main_skill_magic_dark_doombolt': 'wh3_main_skill_sla_magic_slaanesh_06_slicing_shards',
    'wh2_main_skill_magic_dark_soul_stealer': 'wh3_main_skill_sla_magic_slaanesh_07_phantasmagoria',
    'wh2_main_skill_magic_dark_chillwind_dummy': 'wh3_main_skill_sla_magic_slaanesh_dummy_lash_of_slaanesh',
}
SORC = 'druchii_cult_sorceress_slaanesh'
M_SORC = copy_character('wh2_main_def_sorceress_dark', SORC, 'sorceress_dark', 'sorceress_slaanesh', HERO_LORE,
                        {f'agent_subtypes_onscreen_name_override_{SORC}': 'Sorceress (Slaanesh)'}, LORE_ICON,
                        ui_group='wh3_main_wizard_slaanesh',   # vanilla Slaanesh hero group (Alluress)
                        ability_groups={'wh2_main_lore_dark_magic': 'wh3_main_lore_slaanesh'})

# --------------------------------------------------------------------------
# 2. Supreme Sorceress (Slaanesh), lord
# --------------------------------------------------------------------------
LORD_LORE = {
    'wh2_main_skill_magic_dark_chillwind': 'wh3_main_skill_sla_magic_slaanesh_01_lash_of_slaanesh_lord',
    'wh2_main_skill_magic_dark_lore_attribute': 'wh3_main_skill_sla_magic_slaanesh_05_blissful_rapture',
    'wh2_main_skill_magic_dark_power_of_darkness_lord': 'wh3_main_skill_sla_magic_slaanesh_02_acquiescence_lord',
    'wh2_main_skill_magic_dark_word_of_pain_lord': 'wh3_main_skill_sla_magic_slaanesh_03_pavane_of_slaanesh_lord',
    'wh2_main_skill_magic_dark_bladewind_lord': 'wh3_main_skill_sla_magic_slaanesh_04_hysterical_frenzy_lord',
    'wh2_main_skill_magic_dark_doombolt_lord': 'wh3_main_skill_sla_magic_slaanesh_06_slicing_shards_lord',
    'wh2_main_skill_magic_dark_soul_stealer_lord': 'wh3_main_skill_sla_magic_slaanesh_07_phantasmagoria_lord',
    'wh2_main_skill_magic_dark_chillwind_power_of_darkness_dummy': 'wh3_main_skill_sla_magic_slaanesh_dummy_lash_of_slaanesh_acquiescence',
}
SUPREME = 'druchii_cult_supreme_sorceress_slaanesh'
M_SUPREME = copy_character('wh2_dlc10_def_supreme_sorceress_dark', SUPREME, 'supreme_sorceress_dark', 'supreme_sorceress_slaanesh',
                           LORD_LORE, {f'agent_subtypes_onscreen_name_override_{SUPREME}': 'Supreme Sorceress (Slaanesh)'}, LORE_ICON,
                           ui_group='wh3_lord_wizard_slaanesh',   # vanilla Slaanesh lord group
                           ability_groups={'wh2_main_lore_dark_magic': 'wh3_main_lore_slaanesh'},
                           magic_lore='wh3_main_lore_slaanesh')   # lore tab in the lord list

# --------------------------------------------------------------------------
# 3. Cultist of Slaanesh (Cult only, female art sets)
# --------------------------------------------------------------------------
CULTIST = 'druchii_cult_cultist_slaanesh'
VANILLA_CULTIST = 'wh3_main_sla_cultist'
M_CULTIST = copy_character(VANILLA_CULTIST, CULTIST, 'cultist', 'cultist', {}, {}, female=True)
for f in CULT_FACTIONS:
    # Overrides the Cult pack's permitted row for the vanilla Cultist (same key: agent+faction+subtype).
    add('faction_agent_permitted_subtypes_tables', agent='dignitary', faction=f, subtype=VANILLA_CULTIST, mod_disabled=True)
assert any(r['effect'] == 'wh3_main_effect_agent_enable_recruitment_sla_cultist' and r['subtype'] == CULTIST
           for r in out_tables['effect_bonus_value_agent_subtype_junctions_tables']), 'recruitment link not copied'
CHARACTER_MAPS = (M_SORC, M_SUPREME, M_CULTIST)

# The Cult of Pleasure pack's own unit sets (Mark of Slaanesh for heroes, rite upkeep, ...): each new
# unit joins the same sets as the vanilla unit it was copied from. Read from the installed Cult pack,
# so build Druchii_Cult-of-Pleasure_MOD first.
cult_pack = Pack(os.path.join(DATA, 'Druchii_Cult-of-Pleasure_MOD.pack'))
cult_sets = table(cult_pack, 'unit_set_to_unit_junctions_tables')
unit_map = {old: new for M in CHARACTER_MAPS for old, new in M.items()
            if old in {r['unit'] for r in T('main_units_tables')}}
joined = 0
for r in cult_sets:
    if r['unit_record'] in unit_map:
        add('unit_set_to_unit_junctions_tables', **dict(r, unit_record=unit_map[r['unit_record']]))
        joined += 1
print('Cult unit sets joined by the new units:', joined)

# Every renamed key that is used must also be defined (an orphan reference can crash the game).
DEFINING = {'agent_subtypes_tables': 'key', 'main_units_tables': 'unit', 'land_units_tables': 'key',
            'ancillaries_tables': 'key', 'character_skills_tables': 'key', 'character_skill_nodes_tables': 'key',
            'character_skill_node_sets_tables': 'key', 'campaign_character_art_sets_tables': 'art_set_id',
            'unit_attributes_groups_tables': 'group_name', 'ui_unit_groupings_tables': 'key',
            'unit_sets_tables': 'key'}
defined = {r[c] for t, c in DEFINING.items() for r in out_tables.get(t, [])}
new_keys = {v for M in CHARACTER_MAPS for v in M.values()}
used = {v for rows in out_tables.values() for r in rows for v in r.values() if isinstance(v, str) and v in new_keys}
assert used <= defined, sorted(used - defined)

# Every lore skill must exist (a typo would leave an empty node).
skill_keys = {r['key'] for r in T('character_skills_tables')}
for lore in (HERO_LORE, LORD_LORE):
    missing = [v for v in lore.values() if v not in skill_keys]
    assert not missing, missing
    swapped = [r for r in out_tables['character_skill_nodes_tables'] if r['character_skill_key'] in lore.values()]
    assert swapped, 'no lore node swapped'

# --------------------------------------------------------------------------
# 4. Dark Elf hero tab "Death Hag" -> "Priestess" (user, 2026-11-25)
# --------------------------------------------------------------------------
# The tab name and description are the Dark Elf culture's dignitary row (agent_culture_details 610),
# shared by every Dark Elf faction, so this renames it for all of them (text only; the heroes keep
# their own names: Death Hag, Cultist of Slaanesh). A script rewrite of the panel text caused the
# turn-1 black screen (Cult mod v21), so it's done in the loc.
# Vanilla keys must be in a loc file that sorts BEFORE vanilla's (text/db/agent_culture_details__.loc):
# the first file defining a key wins, so they go in text/db/!!druchii_cult_characters_overrides.loc
# (v7 had them in Druchii_Cult-Characters_MOD.loc, which sorts after, and the tab didn't change).
override_loc = {
    'agent_culture_details_onscreen_name_610': 'Priestess',
    'agent_culture_details_description_text_610': "Priestesses of the Druchii's chthonic cults",
}

# --------------------------------------------------------------------------
# Portrait settings for the new art sets (v4 format, entries copied from vanilla, ids renamed)
# --------------------------------------------------------------------------
def ps_entries(b):
    o = [8]
    def u8():
        o[0] += 1; return b[o[0] - 1]
    def u32():
        o[0] += 4; return struct.unpack_from('<I', b, o[0] - 4)[0]
    def st():
        n = struct.unpack_from('<H', b, o[0])[0]; o[0] += 2 + n; return b[o[0] - n:o[0]].decode()
    assert struct.unpack_from('<I', b, 0)[0] == 4
    out = []
    for _ in range(struct.unpack_from('<I', b, 4)[0]):
        start = o[0]
        key = st(); o[0] += 20; st()
        if u8():
            o[0] += 20; st()
        for _ in range(u32()):
            for _ in range(5):
                st()
        out.append((key, b[start:o[0]]))
    assert o[0] == len(b)
    return out


art_map = {old: new for M in CHARACTER_MAPS for old, new in M.items() if '_art_set_' in old}
for kind in ('portholes', 'units'):
    new = []
    for key, blob in ps_entries(ui_pack.read(f'ui/portraits/{kind}/portrait_settings__.bin')):
        if key in art_map:
            nid = art_map[key].encode()
            new.append(struct.pack('<H', len(nid)) + nid + blob[2 + len(key):])
    assert len(new) == len(art_map), (kind, len(new), len(art_map))
    path = os.path.join(root, 'ui', 'portraits', kind, 'portrait_settings__druchii_cult_characters.bin')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(struct.pack('<II', 4, len(new)) + b''.join(new))

# --------------------------------------------------------------------------
# Write
# --------------------------------------------------------------------------
for table_name, rows in out_tables.items():
    path = os.path.join(root, 'db', table_name, FRAG)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(encode_db(table_name, table_version(db, table_name), rows))

def write_loc(entries, name):
    d = b'\xff\xfeLOC\x00' + struct.pack('<II', 1, len(entries))
    for k, v in entries.items():
        d += struct.pack('<H', len(k)) + k.encode('utf-16-le') + struct.pack('<H', len(v)) + v.encode('utf-16-le') + b'\x00'
    os.makedirs(os.path.join(root, 'text', 'db'), exist_ok=True)
    open(os.path.join(root, 'text', 'db', name), 'wb').write(d)


write_loc(loc, f'{FRAG}.loc')
write_loc(override_loc, '!!druchii_cult_characters_overrides.loc')
print('characters:', {'sorceress keys': len(M_SORC), 'supreme keys': len(M_SUPREME), 'cultist keys': len(M_CULTIST), 'art sets': len(art_map)})
print('tables:', {t: len(r) for t, r in out_tables.items()}, len(loc), 'loc entries')
