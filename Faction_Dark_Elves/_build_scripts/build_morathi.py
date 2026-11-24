"""Write Druchii_Morathi_MOD's DB tables into a pack source folder.

Morathi's lord effects (what the faction-select screen lists): her innate skill
wh2_main_skill_innate_def_morathi ("Dark Manipulator"). Morathi only exists in the Cult of Pleasure,
so the vanilla skill is changed directly (no script swap as for Malekith). Rows are keyed on
skill + effect + level: new rows add effects, same keys would override (vanilla rows are never
deleted). Her skill tree itself is left alone (planned for a separate Morathi / Sorceress mod).

  Kept (vanilla):  regional loyalty chance +2; Sacrifice to Hekarti cooldown -5 turns and
                   slave cost -50%
  Added:           Upkeep -50% for embedded Heroes (Heroes in her army), CA's effect as used by
                   Repanse's trait (-50%) and lord skills (scope general_to_force_own)
                   Growth +20 in the province she is in (sycophants flocking to her)

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

# Sycophants flocking to her: +20 growth in the province she is in. CA's character growth effect
# with the same scope and value as Lord Kroak's innate skill (Malekith's Efforts Redoubled: +25).
add('character_skill_level_to_effects_junctions_tables', character_skill_key=INNATE,
    effect_key='wh_main_effect_province_growth_characters', effect_scope='character_to_province_own', level=1, value=20.0)

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
