"""Write Druchii_Malekith_MOD's DB tables and loc file into a pack source folder.

Malekith's innate lord skill ("Witch King of Naggaroth"):
  Control +8              -> Slaves to the Throne: slave income +15% and Control +3 in his province
  Construction cost -15%  -> Formation Attack for Bleakswords, Dreadspears and Darkshards
                             (incl. Darkshards with shields; no Regiments of Renown) in his army
  Enemy leadership -8     -> unchanged (enemy armies in his region, on the campaign map)
  New                     -> Malekith's army: non-character units in his army get physical
                             resistance +3%, plus +1% per rank (+12% at rank 9, gold chevron 3)

Why two skills:
  The vanilla key wh2_main_skill_innate_def_malekith is baked into the campaign startpos for
  his starting character, and the pre-game faction screen lists that skill's effects. So the
  vanilla skill's rows are edited too (rows are keyed on skill+effect+level: override or add,
  never delete), which leaves its construction row at 0 ("+0%"). In the campaign, the script
  (script/campaign/mod/druchii_malekith.lua) swaps his background skill for the clean copy
  druchii_malekith_skill_innate, the same way CA's wh3_campaign_innate_trait_reset.lua does,
  and the frontend script hides the "+0%" line on the faction screen.

The Legion bonus copies CA's own per-rank pattern (Archaon's innate, Tiger Warrior tech): ONE
effect linked to cumulative rank sets ("rank N and up"), so its value stacks once per rank.
Three copies of an all-ranks set give the +3% base; sets for rank 1+ ... 9+ add 1% each.

Usage: build_malekith.py <pack source folder>
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twpack import Pack, DATA, table, encode_db, table_version

root = sys.argv[1]
FRAG = 'Druchii_Malekith_MOD'

db = Pack(DATA + r'\db.pack')
out_tables, loc = {}, {}


def add(table_name, **row):
    out_tables.setdefault(table_name, []).append(row)


VANILLA_INNATE = 'wh2_main_skill_innate_def_malekith'
NEW_INNATE = 'druchii_malekith_skill_innate'
ARMY = 'general_to_force_own'


def new_effect(key, icon, priority, text, icon_negative=None):
    add('effects_tables', effect=key, icon=icon, priority=priority, icon_negative=icon_negative or icon,
        category='battle', is_positive_value_good=True)
    loc[f'effects_description_{key}'] = text


def unit_set(key, rows, min_level=None, max_level=None):
    add('unit_sets_tables', key=key, use_unit_exp_level_range=min_level is not None,
        min_unit_exp_level_inclusive=-1 if min_level is None else min_level,
        max_unit_exp_level_inclusive=-1 if max_level is None else max_level, special_category='')
    for r in rows:
        add('unit_set_to_unit_junctions_tables', **dict(r, unit_set=key))


# --------------------------------------------------------------------------
# Formation Attack (template: the vanilla Tomb Guard Formed Attack effect)
# --------------------------------------------------------------------------
FORMATION_SET = 'druchii_malekith_formation_units'
FORMATION_EFFECT = 'druchii_malekith_effect_enable_attribute_formed_attack'
unit_set(FORMATION_SET, [
    dict(exclude=False, unit_caste='', unit_category='', unit_class='', unit_record=u)
    for u in ['wh2_main_def_inf_bleakswords_0', 'wh2_main_def_inf_dreadspears_0',
              'wh2_main_def_inf_darkshards_0', 'wh2_main_def_inf_darkshards_1']
])
add('unit_set_unit_attribute_junctions_tables', key=FORMATION_EFFECT, unit_attribute='formed_attack',
    unit_set=FORMATION_SET)
add('effect_bonus_value_unit_set_unit_attribute_junctions_tables', bonus_value_id='enable', effect=FORMATION_EFFECT,
    unit_set_attribute=FORMATION_EFFECT)
new_effect(FORMATION_EFFECT, 'formed_attack.png', 1,
           'Attribute: Formation Attack for Bleakswords, Dreadspears and Darkshards units',
           icon_negative='formed_attack.png')

# --------------------------------------------------------------------------
# Malekith's army: physical resistance 3% + 1% per rank (one effect, cumulative rank sets)
# --------------------------------------------------------------------------
LEGION_EFFECT = 'druchii_malekith_effect_legion_physical_resistance'
no_characters = [dict(r) for r in table(db, 'unit_set_to_unit_junctions_tables')
                 if r['unit_set'] == 'dlc14_all_units_excluding_characters']
for r in no_characters:
    del r['unit_set']
legion_sets = [(f'druchii_malekith_legion_base_{i}', 0) for i in range(3)]          # +3% base
legion_sets += [(f'druchii_malekith_legion_rank{n}_up', n) for n in range(1, 10)]    # +1% per rank
for key, min_rank in legion_sets:
    unit_set(key, no_characters, min_level=min_rank, max_level=9)
    add('effect_bonus_value_ids_unit_sets_tables', bonus_value_id='unit_damage_resistance_physical_mod',
        effect=LEGION_EFFECT, unit_set=key)
new_effect(LEGION_EFFECT, 'resistance_physical.png', 582,
           "Physical resistance gained by Malekith's army based on experience: +3%, and %+n% more per rank "
           "(+12% at rank 9)")

# --------------------------------------------------------------------------
# The skills
# --------------------------------------------------------------------------
def skill_effect(skill, effect, scope, value):
    add('character_skill_level_to_effects_junctions_tables', character_skill_key=skill, effect_key=effect,
        effect_scope=scope, level=1, value=value)


def new_innate_effects(skill):
    skill_effect(skill, 'wh3_main_effect_economy_gdp_mod_slaves', 'character_to_region_own_provincewide', 15)
    skill_effect(skill, 'wh_main_effect_public_order_characters', 'character_to_province_own', 3)
    skill_effect(skill, FORMATION_EFFECT, ARMY, 1)
    skill_effect(skill, LEGION_EFFECT, ARMY, 1)


# Vanilla skill (faction screen, and any Malekith the script hasn't swapped yet):
# Control 8 -> 3 overrides the vanilla row, construction is neutralised, enemy leadership untouched.
new_innate_effects(VANILLA_INNATE)
skill_effect(VANILLA_INNATE, 'wh_main_effect_building_construction_cost_mod', 'character_to_region_own_provincewide', 0)

# Clean copy without the construction row, swapped in by the campaign script.
vanilla_skill = next(r for r in table(db, 'character_skills_tables') if r['key'] == VANILLA_INNATE)
add('character_skills_tables', **dict(vanilla_skill, key=NEW_INNATE))
loc[f'character_skills_localised_name_{NEW_INNATE}'] = vanilla_skill['localised_name']
loc[f'character_skills_localised_description_{NEW_INNATE}'] = vanilla_skill['localised_description']
new_innate_effects(NEW_INNATE)
skill_effect(NEW_INNATE, 'wh_main_effect_force_stat_leadership_enemy_unit', 'general_to_force_enemy_regionwide', -8)

# --------------------------------------------------------------------------
# Circlet of Iron (rows keyed on ancillary + effect: same effect overrides vanilla)
# --------------------------------------------------------------------------
CIRCLET = 'wh2_main_anc_arcane_item_circlet_of_iron'
add('ancillary_to_effects_tables', ancillary=CIRCLET, effect='wh_main_effect_character_mod_ancillary_drop',
    effect_scope='character_to_force_own_unseen', value=25)   # was +5%
add('ancillary_to_effects_tables', ancillary=CIRCLET, effect='wh3_main_effect_winds_of_magic_pool_cap',
    effect_scope='character_to_force_own_unseen', value=25)   # new (same effect/scope as Magical Reserves)

# --------------------------------------------------------------------------
# Write
# --------------------------------------------------------------------------
for table_name, rows in out_tables.items():
    path = os.path.join(root, 'db', table_name, FRAG)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(encode_db(table_name, table_version(db, table_name), rows))

d = b'\xff\xfeLOC\x00' + struct.pack('<II', 1, len(loc))
for k, v in loc.items():
    d += struct.pack('<H', len(k)) + k.encode('utf-16-le') + struct.pack('<H', len(v)) + v.encode('utf-16-le') + b'\x00'
os.makedirs(os.path.join(root, 'text', 'db'), exist_ok=True)
open(os.path.join(root, 'text', 'db', f'{FRAG}.loc'), 'wb').write(d)
print('malekith data:', {t: len(r) for t, r in out_tables.items()}, len(loc), 'loc entries')
