"""Write Druchii_Morathi_MOD's DB tables into a pack source folder.

Morathi's lord effects (what the faction-select screen lists): her innate skill
wh2_main_skill_innate_def_morathi ("Dark Manipulator"). Morathi only exists in the Cult of Pleasure,
so the vanilla skill is changed directly (no script swap as for Malekith). Rows are keyed on
skill + effect + level: new rows add effects, same keys would override (vanilla rows are never
deleted). Her skill tree (2026-11-26): Doombolt for Melkoth's Mystifying Miasma (own starting-spell
dummy), Hysterical Frenzy for Doom & Darkness, own copies of Blessed by Evil and A Thousand & One
Dark Blessings (barrier instead of spell resistance; her unit has a 666 barrier), A Dark Dalliance
also covers more Slaanesh daemons. No hard reference to the Cult of Pleasure pack (its Morathi
sorcery bundle only makes the text line true).

  Kept (vanilla):  regional loyalty chance +2; Sacrifice to Hekarti cooldown -5 turns and
                   slave cost -50%
  Added:           Upkeep -50% for embedded Heroes (Heroes in her army), CA's effect as used by
                   Repanse's trait (-50%) and lord skills (scope general_to_force_own)
                   Text line: spell range and intensity grow with Slaanesh corruption (the
                   effect is the Cult of Pleasure pack's scripted bundle). The +20 growth in her
                   province was removed (2026-11-26).

Usage: build_morathi.py <pack source folder>
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twpack import Pack, DATA, table, encode_db, table_version

root = sys.argv[1]
FRAG = 'Druchii_Morathi_MOD'

db = Pack(DATA + r'\db.pack')
out_tables, loc = {}, {}


def add(table_name, **row):
    out_tables.setdefault(table_name, []).append(row)


INNATE = 'wh2_main_skill_innate_def_morathi'
vanilla = [r for r in table(db, 'character_skill_level_to_effects_junctions_tables') if r['character_skill_key'] == INNATE]
assert vanilla, 'Morathi innate skill not found'

# Heroes in her army: -50% upkeep
add('character_skill_level_to_effects_junctions_tables', character_skill_key=INNATE,
    effect_key='wh2_dlc14_effect_upkeep_reduction_heroes', effect_scope='general_to_force_own', level=1, value=-50.0)

# (+20 growth in her province removed 2026-11-26, author.)
# Her sorcery grows with Slaanesh corruption: a text-only line on the faction-select screen. The
# effect itself is a bundle the Cult of Pleasure script keeps on her (Druchii_Cult-of-Pleasure_MOD,
# builder section 30 / Lua section 17), so it needs that pack too.
SORCERY_LINE = 'druchii_morathi_effect_corruption_sorcery'
add('effects_tables', effect=SORCERY_LINE, icon='magic_character.png', priority=1, icon_negative='magic_character.png',
    category='battle', is_positive_value_good=True)
loc[f'effects_description_{SORCERY_LINE}'] = (
    'Spell range and intensity grow with the Slaanesh corruption of the region she fights in')
add('character_skill_level_to_effects_junctions_tables', character_skill_key=INNATE,
    effect_key=SORCERY_LINE, effect_scope='character_to_character_own', level=1, value=1.0)

# --------------------------------------------------------------------------
# Her skill tree (user 2026-11-26). Vanilla rows can't be deleted, so a skill that loses an effect
# becomes a Morathi-only copy, and her tree's node (same node key, overridden) points at the copy.
# Skills only she has (A Dark Dalliance's effects) are extended in place.
# --------------------------------------------------------------------------
loc_vanilla = __import__('pickle').load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loc_en.pkl'), 'rb'))
skills = {r['key']: r for r in table(db, 'character_skills_tables')}
skill_effects = table(db, 'character_skill_level_to_effects_junctions_tables')
nodes = {r['key']: r for r in table(db, 'character_skill_nodes_tables')}
hints = table(db, 'character_skill_utilization_hints_junctions_tables')


def copy_skill(src, new, drop=(), swap=None, extra=(), name=None, description=None):
    """Morathi-only copy of a skill: its row, effects (minus `drop`, with effect keys in `swap`
    replaced as {old: (new, value)}), `extra` rows (level, effect, scope, value) and its hint."""
    add('character_skills_tables', **dict(skills[src], key=new))
    swap = swap or {}
    for r in skill_effects:
        if r['character_skill_key'] == src and r['effect_key'] not in drop:
            row = dict(r, character_skill_key=new)
            if r['effect_key'] in swap:
                row['effect_key'], row['value'] = swap[r['effect_key']]
            add('character_skill_level_to_effects_junctions_tables', **row)
    for level, effect, scope, value in extra:
        add('character_skill_level_to_effects_junctions_tables', character_skill_key=new, effect_key=effect,
            effect_scope=scope, level=level, value=value)
    for h in hints:
        if h['key'] == src:
            add('character_skill_utilization_hints_junctions_tables', **dict(h, key=new))
    loc[f'character_skills_localised_name_{new}'] = name or loc_vanilla.get(f'character_skills_localised_name_{src}', '')
    loc[f'character_skills_localised_description_{new}'] = description or loc_vanilla.get(
        f'character_skills_localised_description_{src}', '')


def set_node(node_key, skill_key):
    assert node_key in nodes, node_key
    add('character_skill_nodes_tables', **dict(nodes[node_key], character_skill_key=skill_key))


# 1. Melkoth's Mystifying Miasma -> Doombolt (the Supreme Sorceress' lord version, Lore of Dark
#    Magic). Her starting spells come from a hidden dummy (Miasma + Power of Darkness), shared with
#    Drycha and others, so she gets her own dummy: Doombolt + Power of Darkness.
DUMMY = 'druchii_morathi_skill_doombolt_power_of_darkness_dummy'
copy_skill('wh2_main_skill_magic_shadow_mystifying_miasma_power_of_darkness_dummy', DUMMY,
           swap={'wh_dlc05_effect_ability_enable_melkoths_mystifying_miasma': ('wh2_main_effect_ability_enable_doombolt', 1.0)},
           name='Doombolt [HIDDEN]', description=loc_vanilla.get('character_skills_localised_description_wh2_main_skill_magic_dark_doombolt_lord', ''))
set_node('wh2_main_skill_node_def_morathi_magic_dummy', DUMMY)
set_node('wh2_main_skill_node_def_morathi_magic_0', 'wh2_main_skill_magic_dark_doombolt_lord')
# 2. Doom & Darkness -> Hysterical Frenzy (lord version, Lore of Slaanesh).
set_node('wh2_main_skill_node_def_morathi_magic_1_2', 'wh3_main_skill_sla_magic_slaanesh_04_hysterical_frenzy_lord')
# Both spells join her spell bar group (only Morathi uses wh2_main_lore_morathi; CA lists the base
# spells there, the upgraded ones come with them).
for spell in ('wh2_main_spell_dark_magic_doombolt', 'wh3_main_spell_slaanesh_hysterical_frenzy'):
    add('special_ability_groups_to_unit_abilities_junctions_tables', special_ability_groups='wh2_main_lore_morathi',
        unit_special_abilities=spell)

# 3. Blessed by Evil: the Winds cost cuts for Miasma (upgraded) and Doom & Darkness (upgraded) now go
#    to Doombolt (upgraded) and Hysterical Frenzy (upgraded).
BLESSED = 'druchii_morathi_skill_blessed_by_evil'
copy_skill('wh2_main_skill_def_morathi_unique_4', BLESSED, swap={
    'wh2_main_effect_ability_wom_cost_melkoths_mystifying_miasma_upgraded': ('wh2_main_effect_ability_wom_cost_doombolt_upgraded', -2.0),
    'wh2_main_effect_ability_wom_cost_doom_and_darkness_upgraded': ('wh3_main_effect_ability_wom_cost_hysterical_frenzy_upgraded', -2.0),
})
set_node('wh2_main_skill_node_def_morathi_generic_4', BLESSED)

# 4. A Thousand & One Dark Blessings: spell resistance -> barrier hit points (+222 / +444), and her
#    own unit starts with a 666-point barrier (main_units.barrier_health; in WH3 the barrier is a
#    unit stat, as on the Tzeentch sorcerers, not an ability).
BLESSINGS = 'druchii_morathi_skill_1001_blessings'
BARRIER_EFFECT = 'wh3_main_effect_battle_barrier_health_add'
copy_skill('wh2_main_skill_def_morathi_1001_blessings', BLESSINGS, drop={'wh_main_effect_character_stat_magic_resistance'},
           extra=[(1, BARRIER_EFFECT, 'character_to_character_own', 222.0), (2, BARRIER_EFFECT, 'character_to_character_own', 444.0)],
           description="The Hag Sorceress' allegiance to the Ruinous Powers wraps her in a shimmering ward of a thousand "
                       "and one dark blessings.")
set_node('wh2_main_skill_node_def_morathi_combat_3_2', BLESSINGS)
for r in table(db, 'main_units_tables'):
    if r['unit'] in ('wh2_main_def_cha_morathi_0', 'wh2_main_def_cha_morathi_1'):
        add('main_units_tables', **dict(r, barrier_health=666.0))

# 5. A Dark Dalliance: its three effects (only this skill uses them) also cover the other Slaanesh
#    daemons the Cult fields: Chaos Furies, Seekers and Eternal Entourage (Bringers of Beguilement
#    is already in CA's sla_daemonettes set). The skill's unit cards come from the effects' unit
#    sets. The Summoned Daemon Prince is left out (author, 2026-11-26): it lives in the Cult of
#    Pleasure pack, and a reference to it here would tie this pack to that one.
DAEMON_SET = 'druchii_morathi_slaanesh_daemons'
add('unit_sets_tables', key=DAEMON_SET, use_unit_exp_level_range=False, min_unit_exp_level_inclusive=-1,
    max_unit_exp_level_inclusive=-1, special_category='')
for unit in ('wh3_main_sla_inf_chaos_furies_0', 'wh3_main_sla_cav_seekers_of_slaanesh_0',
             'wh3_twa07_sla_cav_heartseekers_of_slaanesh_ror_0'):
    add('unit_set_to_unit_junctions_tables', exclude=False, unit_caste='', unit_category='', unit_class='',
        unit_record=unit, unit_set=DAEMON_SET)
# Daemons only (author, 2026-11-26): the Devotees are out. CA's three effects carry the Devotees' set and
# rows can't be deleted, so the skill becomes a Morathi-only copy with its own effects: CA's Daemonette
# set (sla_daemonettes: Daemonettes, Exalted, Bringers of Beguilement, Dechala's Exalted) plus
# DAEMON_SET. Values, levels and scopes as CA's; the Slaanesh corruption rows are kept as they are.
DALLIANCE_SRC = 'wh3_dlc27_skill_def_morathi_unique_5'
DALLIANCE = 'druchii_morathi_skill_dark_dalliance'
dalliance_effects = {}
for effect, text in [('melee_attack', 'Melee attack: %+n'), ('speed', 'Speed: %+n%'),
                     ('physical_resistance', 'Physical resistance: %+n%')]:
    src_effect = f'wh3_dlc27_effect_force_stat_{effect}_sla_infantry_def'
    new_effect = f'druchii_morathi_effect_force_stat_{effect}_slaanesh_daemons'
    dalliance_effects[src_effect] = new_effect
    add('effects_tables', **dict(next(r for r in table(db, 'effects_tables') if r['effect'] == src_effect), effect=new_effect))
    for r in table(db, 'effect_bonus_value_ids_unit_sets_tables'):
        if r['effect'] == src_effect and r['unit_set'] == 'sla_daemonettes':
            add('effect_bonus_value_ids_unit_sets_tables', **dict(r, effect=new_effect))
            add('effect_bonus_value_ids_unit_sets_tables', **dict(r, effect=new_effect, unit_set=DAEMON_SET))
    loc[f'effects_description_{new_effect}'] = f'{text} for Slaanesh Daemon units'
add('character_skills_tables', **dict(skills[DALLIANCE_SRC], key=DALLIANCE))
for r in skill_effects:
    if r['character_skill_key'] == DALLIANCE_SRC:
        add('character_skill_level_to_effects_junctions_tables',
            **dict(r, character_skill_key=DALLIANCE, effect_key=dalliance_effects.get(r['effect_key'], r['effect_key'])))
for t, col in (('character_skill_level_details_tables', 'skill_key'), ('character_skill_utilization_hints_junctions_tables', 'key')):
    for r in table(db, t):
        if r[col] == DALLIANCE_SRC:
            add(t, **dict(r, **{col: DALLIANCE}))
for kind in ('name', 'description'):
    loc[f'character_skills_localised_{kind}_{DALLIANCE}'] = loc_vanilla.get(f'character_skills_localised_{kind}_{DALLIANCE_SRC}', '')
set_node('wh3_dlc27_skill_node_def_morathi_unique_5', DALLIANCE)

# 6. Student of the Dark Tower (the Supreme Sorceresses' skill, vanilla, unchanged) at the end of her
#    top line, standalone like Ward of Khaine and A Dark Dalliance (author's choice, 2026-11-26: no
#    character has a real 7th skill line, and Mentor stays).
STUDENT_NODE = 'druchii_morathi_skill_node_student_of_the_dark_tower'
add('character_skill_nodes_tables', campaign_key='', character_skill_key='wh2_twa03_skill_supreme_sorceress_unique_1',
    faction_key='', indent=0, key=STUDENT_NODE, tier=11, subculture='', points_on_creation=0,
    required_num_parents=0, visible_in_ui=True)
add('character_skill_node_set_items_tables', set='wh2_main_skill_node_set_def_morathi', item=STUDENT_NODE, mod_disabled=False)

# 7. Gate of Slaanesh and Greater Gate of Slaanesh (the Slaanesh Cultist's vanilla skills, unchanged)
#    after Student of the Dark Tower on her top line (user 2026-11-26). Copies of the Cultist's two
#    nodes, so Greater Gate keeps its requirement (link from Gate, SUBSET_REQUIRED). Battle UI: her tree
#    gives about 7 active abilities with these (CA's busiest trees give 13), so the ability bar has room.
GATE_NODES = {'wh3_main_skill_node_sla_cultist_unique_0': ('druchii_morathi_skill_node_gate_of_slaanesh', 12),
              'wh3_main_skill_node_sla_cultist_unique_1': ('druchii_morathi_skill_node_greater_gate_of_slaanesh', 13)}
for src, (key, tier) in GATE_NODES.items():
    add('character_skill_nodes_tables', **dict(nodes[src], key=key, indent=0, tier=tier, points_on_creation=0))
    add('character_skill_node_set_items_tables', set='wh2_main_skill_node_set_def_morathi', item=key, mod_disabled=False)
for r in table(db, 'character_skill_node_links_tables'):
    if r['parent_key'] in GATE_NODES and r['child_key'] in GATE_NODES:
        add('character_skill_node_links_tables', **dict(r, parent_key=GATE_NODES[r['parent_key']][0],
                                                         child_key=GATE_NODES[r['child_key']][0]))

# 8. Red line: the Cult's own Line Breaker, Sheafmaster and Lash Master (cult_army_skills.py, shared
#    with the characters pack; identical rows in both packs, so neither needs the other).
from cult_army_skills import add_cult_army_skills
ARMY_SKILLS = add_cult_army_skills(add, loc, db, table, loc_vanilla)
swapped = 0
for node in nodes.values():
    if node['key'].startswith('wh2_main_skill_node_def_morathi_') and node['character_skill_key'] in ARMY_SKILLS:
        set_node(node['key'], ARMY_SKILLS[node['character_skill_key']])
        swapped += 1
assert swapped == 10, swapped

# 9. Stand or Die! -> N'Kari's Harvester of Souls aura, weaker version (user 2026-11-26): when an enemy
#    dies within 30 m, friendly units nearby heal 0.4% per second and recover vigour for 21 seconds.
#    N'Kari's base version is innate to his unit (its enable effect also carries a disable row), and the
#    skill-granted one is the upgraded 0.8%, so Morathi gets her own copy: the upgraded ability's rows
#    (made to be granted by an effect) with the base version's phase (0.4%), own key, id and effect.
#    Same node: it still needs one of the rank-7 skills before it.
H_SRC = 'wh3_main_lord_passive_harvester_of_souls_upgraded'
H_ABILITY = 'druchii_morathi_lord_passive_harvester'
H_EFFECT = 'druchii_morathi_effect_ability_enable_harvester'
H_NAME = 'Intoxicating Allure'
add('unit_abilities_tables', **dict(next(r for r in table(db, 'unit_abilities_tables') if r['key'] == H_SRC),
                                    key=H_ABILITY, superseded_abilities_set=''))
taken_ids = {r['unique_id'] for r in table(db, 'unit_special_abilities_tables')}
h_id = __import__('zlib').crc32(H_ABILITY.encode()) & 0x7fffffff
while h_id in taken_ids:
    h_id += 1
add('unit_special_abilities_tables', **dict(next(r for r in table(db, 'unit_special_abilities_tables') if r['key'] == H_SRC),
                                            key=H_ABILITY, unique_id=h_id))
for r in table(db, 'special_ability_to_special_ability_phase_junctions_tables'):
    if r['special_ability'] == H_SRC:
        add('special_ability_to_special_ability_phase_junctions_tables',
            **dict(r, special_ability=H_ABILITY, phase='wh3_main_lord_passive_harvester_of_souls'))
for t, col in (('special_ability_to_auto_deactivate_flags_tables', 'special_ability'),
               ('unit_abilities_to_additional_ui_effects_juncs_tables', 'ability')):
    for r in table(db, t):
        if r[col] == H_SRC:
            add(t, **dict(r, **{col: H_ABILITY}))
add('effects_tables', **dict(next(r for r in table(db, 'effects_tables')
                                  if r['effect'] == 'wh3_main_effect_ability_enable_harvester_of_souls_upgraded'), effect=H_EFFECT))
add('effect_bonus_value_unit_ability_junctions_tables', effect=H_EFFECT, bonus_value_id='enable', unit_ability=H_ABILITY)
loc[f'unit_abilities_onscreen_name_{H_ABILITY}'] = H_NAME
H_QUOTE = '"Come closer, my darlings. Let their dying be your delight."'   # author, 2026-11-26
loc[f'unit_abilities_tooltip_text_{H_ABILITY}'] = H_QUOTE
loc[f'effects_description_{H_EFFECT}'] = f'Passive ability: "{H_NAME}"'
HARVESTER = 'druchii_morathi_skill_harvester_of_souls'
copy_skill('wh_main_skill_chs_lord_battle_stand_or_die', HARVESTER,
           drop={r['effect_key'] for r in skill_effects if r['character_skill_key'] == 'wh_main_skill_chs_lord_battle_stand_or_die'},
           extra=[(1, H_EFFECT, 'character_to_character_own', 1.0)],
           name=H_NAME,
           description=H_QUOTE + ' As the foe dies around her, Morathi '
                       'drinks in their suffering and lends its strength to her own warriors.')
set_node('wh2_main_skill_node_def_morathi_army_4', HARVESTER)

for table_name, rows in out_tables.items():
    path = os.path.join(root, 'db', table_name, FRAG)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(encode_db(table_name, table_version(db, table_name), rows))

if loc:
    d = b'\xff\xfeLOC\x00' + struct.pack('<II', 1, len(loc))
    for k, v in loc.items():
        d += struct.pack('<H', len(k)) + k.encode('utf-16-le') + struct.pack('<H', len(v)) + v.encode('utf-16-le') + b'\x00'
    os.makedirs(os.path.join(root, 'text', 'db'), exist_ok=True)
    open(os.path.join(root, 'text', 'db', f'{FRAG}.loc'), 'wb').write(d)
print('morathi data:', {t: len(r) for t, r in out_tables.items()}, len(loc), 'loc entries;',
      'vanilla innate rows kept:', len(vanilla))
