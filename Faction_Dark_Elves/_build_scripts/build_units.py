"""Write Druchii_Units_MOD's DB tables and loc file into a pack source folder.

Druchii_Units_MOD replaces BlackGuard_MOD (2026-11-23) and gathers the user's Dark Elf unit
changes. Everything is add-only (new junction rows and new records) except one row: the
Bleakswords' land unit, which is re-copied from the game data on every build.

  Black Guard of Naggarond          Contempt (kept from BlackGuard_MOD); Guardian dropped;
                                    + Formation Attack (attribute formed_attack)
  Dark Riders, Dark Riders (Shields)+ Devastating Flanker (attribute devastating_flanker)
  Khainite Assassin                 + Snipe (attribute snipe)
  Bleakswords                       + Bonus vs Infantry +8, and the "Anti-Infantry" strength
  Shades (all three versions)       + Strider (attribute strider)
  Dark Riders (Repeater Crossbows)  +50% acceleration, deceleration and turn speed (own horse copy)

Bleakswords: Bonus vs Infantry sits on the melee weapon, and theirs (wh2_main_def_sword) is
shared with Black Ark Corsairs (Handbows). So they get their own copy of that sword with
bonus_v_infantry 8 (like the Corsairs' wh2_main_def_dual_swords), and their land_units row
points to it. Rebuild after a CA patch so that row stays current.

Dark Riders (Repeater Crossbows) had Fire Whilst Moving (mounted_fire_move) until 2026-11-24: removed
after a battle test (170-degree rider arc, crossbow animations without move-and-shoot).

Usage: build_units.py <pack source folder>
"""
import os, struct, sys, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twpack import Pack, DATA, table, encode_db, table_version

root = sys.argv[1]
FRAG = 'Druchii_Units_MOD'

db = Pack(DATA + r'\db.pack')
out_tables, loc = {}, {}


def add(table_name, **row):
    out_tables.setdefault(table_name, []).append(row)


def new_id(text):
    return zlib.crc32(text.encode()) & 0x7fffffff


# --------------------------------------------------------------------------
# Unit attributes (each of these units has its own attribute group, shared with no other unit)
# --------------------------------------------------------------------------
ATTRIBUTES = [
    ('contempt', 'wh2_main_def_inf_black_guard_0'),
    ('formed_attack', 'wh2_main_def_inf_black_guard_0'),
    ('devastating_flanker', 'wh2_main_def_cav_dark_riders_0'),
    ('devastating_flanker', 'wh2_main_def_cav_dark_riders_1'),
    ('snipe', 'wh2_main_def_cha_khainite_assassin_0'),
    ('strider', 'wh2_main_def_inf_shades_0'),
    ('strider', 'wh2_main_def_inf_shades_1'),
    ('strider', 'wh2_main_def_inf_shades_2'),
]
for attribute, group in ATTRIBUTES:
    add('unit_attributes_to_groups_junctions_tables', attribute=attribute, attribute_group=group)

# --------------------------------------------------------------------------
# Bleakswords: Bonus vs Infantry +8 (hidden always-on passive) and the Anti-Infantry strength
# --------------------------------------------------------------------------
BLEAKSWORDS = 'wh2_main_def_inf_bleakswords_0'
VANILLA_SWORD = 'wh2_main_def_sword'           # shared with Black Ark Corsairs (Handbows)
BLEAKSWORDS_SWORD = 'druchii_units_def_sword_bleakswords'

# Their own copy of the sword with Bonus vs Infantry 8, exactly like the Corsairs' weapon
# (v1 used a hidden passive instead; in game it didn't read as a weapon stat).
vanilla_sword = next(r for r in table(db, 'melee_weapons_tables') if r['key'] == VANILLA_SWORD)
add('melee_weapons_tables', **dict(vanilla_sword, key=BLEAKSWORDS_SWORD, bonus_v_infantry=8))

# The one overridden vanilla row: the Bleakswords' land unit, copied from the current game data
# on every build (so a rebuild after a CA patch picks up their changes) with only the weapon swapped.
vanilla_unit = next(r for r in table(db, 'land_units_tables') if r['key'] == BLEAKSWORDS)
add('land_units_tables', **dict(vanilla_unit, primary_melee_weapon=BLEAKSWORDS_SWORD))

add('ui_unit_bullet_point_unit_overrides_tables', bullet_point='anti_infantry', unit_key=BLEAKSWORDS)

# --------------------------------------------------------------------------
# Dark Riders (Repeater Crossbows): +50% acceleration, deceleration and turn speed (hit and run)
# --------------------------------------------------------------------------
# These are fixed values on the horse's battle entity, not something effects can change. The
# Dark Steed (mount wh2_main_def_mnt_dark_steed -> entity wh2_main_def_cavalry_fast_170_blood) is
# shared with the other Dark Riders, Doomfire Warlocks and the Slaanesh Harvesters RoR, so this
# unit gets its own copy of the entity and the mount, and its land_units row (overridden, like
# the Bleakswords' above; re-copied from the game data on every build) points to the copy.
# Applies to every faction that fields the unit.
DARK_RIDERS_XBOW = 'wh2_main_def_cav_dark_riders_2'
AGILITY = 1.5   # +50%
DR_MOUNT = 'druchii_units_def_mnt_dark_steed_agile'
DR_ENTITY = 'druchii_units_def_cavalry_fast_170_blood_agile'

dr_unit = next(r for r in table(db, 'land_units_tables') if r['key'] == DARK_RIDERS_XBOW)
vanilla_mount = next(r for r in table(db, 'mounts_tables') if r['key'] == dr_unit['mount'])
vanilla_entity = next(r for r in table(db, 'battle_entities_tables') if r['key'] == vanilla_mount['entity'])
add('battle_entities_tables', **dict(vanilla_entity, key=DR_ENTITY,
                                     acceleration=vanilla_entity['acceleration'] * AGILITY,
                                     deceleration=vanilla_entity['deceleration'] * AGILITY,
                                     turn_speed=vanilla_entity['turn_speed'] * AGILITY))
add('mounts_tables', **dict(vanilla_mount, key=DR_MOUNT, entity=DR_ENTITY))
add('land_units_tables', **dict(dr_unit, mount=DR_MOUNT))
print('Dark Riders (Repeater Crossbows) horse: acceleration', vanilla_entity['acceleration'], '->',
      vanilla_entity['acceleration'] * AGILITY, ', deceleration', vanilla_entity['deceleration'], '->',
      vanilla_entity['deceleration'] * AGILITY, ', turn speed', vanilla_entity['turn_speed'], '->',
      vanilla_entity['turn_speed'] * AGILITY)

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
print('units data:', {t: len(r) for t, r in out_tables.items()}, len(loc), 'loc entries')
