"""Write Druchii_Naggarond_MOD's DB tables and loc file into a pack source folder.

Malekith gets his own faction-effects bundle built from new keys, instead of the mod
overriding rows and text of the vanilla bundle (wh2_main_lord_trait_malekith). Mod loc
entries that replaced vanilla keys didn't show up on the faction screen, while new keys
did, so everything shown here uses new keys. The only vanilla row overridden is the
one that decides which bundle Malekith starts with.
"""
import os, struct, sys, uuid

root = sys.argv[1]
FRAG = 'Druchii_Naggarond_MOD'

BUNDLE = 'naggarond_mod_faction_effects'
TRIBUTE_EFFECT = 'naggarond_mod_effect_slave_tribute'
UPKEEP_EFFECT = 'naggarond_mod_effect_upkeep_reduction'
UPKEEP_SET = 'naggarond_mod_upkeep_units'
FACTOR = 'naggarond_slave_tribute'

# Vanilla def_black_council members (Malekith's -25% upkeep units), plus the Master hero.
UPKEEP_UNITS = [
    'wh2_main_def_inf_black_guard_0',
    'wh2_main_def_inf_dreadspears_0',
    'wh2_main_def_inf_bleakswords_0',
    'wh2_main_def_inf_darkshards_0',
    'wh2_main_def_inf_darkshards_1',
    'wh2_dlc10_def_inf_the_bolt_fiends_ror_0',
    'wh2_dlc10_def_inf_the_hellebronai_ror_0',
] + [f'wh2_dlc14_def_cha_master_{i}' for i in range(5)]

# +10 armour: the Witch King's core regiments, all Cold One units, Reaper Bolt Throwers and
# the Master hero. Regiments of Renown of those types are included too.
ARMOUR_EFFECT = 'naggarond_mod_effect_armour_elite'
ARMOUR_SET = 'naggarond_mod_armour_units'
ARMOUR_UNITS = [
    'wh2_main_def_inf_black_guard_0',
    'wh2_main_def_inf_bleakswords_0',
    'wh2_main_def_inf_dreadspears_0',
    'wh2_dlc10_def_inf_the_hellebronai_ror_0',      # The Hellebronai (Dreadspears)
    'wh2_main_def_inf_darkshards_0',
    'wh2_main_def_inf_darkshards_1',
    'wh2_dlc10_def_inf_the_bolt_fiends_ror_0',      # The Bolt-fiends (Darkshards, Shields)
    'wh2_main_def_cav_cold_one_knights_0',
    'wh2_main_def_cav_cold_one_knights_1',          # Cold One Dread Knights
    'wh2_dlc10_def_cav_knights_of_the_ebon_claw_ror_0',  # Knights of the Ebon Claw (Dread Knights)
    'wh2_main_def_cav_cold_one_chariot',
    'wh2_main_def_art_reaper_bolt_thrower',
] + [f'wh2_dlc14_def_cha_master_{i}' for i in range(5)]

TITLE = 'Witch King of Naggaroth'
DESCRIPTION = ("The Witch King is the supreme ruler of Naggaroth, and the eternal enemy of the High "
               "Elves. Long ago, he sought to claim Ulthuan's crown, but the Flames of Asuryan left "
               "him scarred by fire and twisted with hatred.")


def s8(s):
    b = s.encode('utf-8')
    return struct.pack('<H', len(b)) + b


def s16(s):
    return struct.pack('<H', len(s)) + s.encode('utf-16-le')


def opt8(s):
    return b'\x01' + s8(s) if s else b'\x00'


def b(v):
    return b'\x01' if v else b'\x00'


def i32(v):
    return struct.pack('<i', v)


def f32(v):
    return struct.pack('<f', v)


def db_file(version, rows):
    g = str(uuid.uuid4())
    d = b'\xfd\xfe\xfc\xff' + struct.pack('<H', len(g)) + g.encode('utf-16-le')
    if version:
        d += b'\xfc\xfd\xfe\xff' + struct.pack('<I', version)
    return d + b'\x01' + struct.pack('<I', len(rows)) + b''.join(rows)


def write(rel, data):
    path = os.path.join(root, *rel.split('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(data)


# faction_starting_general_effects_tables v0: agent_subtype (key), effect_bundle.
# Overrides the vanilla row, so Malekith starts with the new bundle instead of the old one.
write(f'db/faction_starting_general_effects_tables/{FRAG}', db_file(0, [
    s8('wh2_main_def_malekith') + s8(BUNDLE),
]))

# effect_bundles_tables v4: key, localised_description, localised_title, bundle_target,
# priority, ui_icon, is_global_effect, show_in_3d_space, owner_only (copied from vanilla).
write(f'db/effect_bundles_tables/{FRAG}', db_file(4, [
    s8(BUNDLE) + s8(DESCRIPTION) + s8(TITLE) + s8('faction') + i32(1) + s8('character.png')
    + b(False) + b(False) + b(True),
]))

# effect_bundles_to_effects_junctions_tables v3: bundle, effect, scope, value, advancement_stage.
# Vanilla minus Allegiance Points, Diplomacy and Loyalty, plus the tribute, the armour bonus
# and the Black Council line; upkeep uses the new effect.
FACTION_SCOPE = 'faction_to_faction_own_unseen'
FORCE_SCOPE = 'faction_to_force_own_unseen'
STAGE = 'start_turn_completed'
write(f'db/effect_bundles_to_effects_junctions_tables/{FRAG}', db_file(3, [
    s8(BUNDLE) + s8(TRIBUTE_EFFECT) + s8(FACTION_SCOPE) + f32(10.0) + s8(STAGE),
    s8(BUNDLE) + s8(ARMOUR_EFFECT) + s8(FORCE_SCOPE) + f32(10.0) + s8(STAGE),
    # Replaces Loyalty +2: display line for the Decrees of the Witch King (effect defined in build_black_council.py).
    s8(BUNDLE) + s8('naggarond_mod_effect_black_council') + s8(FACTION_SCOPE) + f32(1.0) + s8(STAGE),
    s8(BUNDLE) + s8(UPKEEP_EFFECT) + s8('faction_to_force_own_unseen') + f32(-25.0) + s8(STAGE),
]))

# effects_tables v0: effect, icon (opt), priority, icon_negative (opt), category, is_positive_value_good
write(f'db/effects_tables/{FRAG}', db_file(0, [
    # The tribute line is display-only; the script does the work.
    s8(TRIBUTE_EFFECT) + opt8('slaves.png') + i32(105) + opt8('slaves.png') + s8('campaign') + b(True),
    # Copied from the vanilla upkeep effect: a negative value is the good direction.
    s8(UPKEEP_EFFECT) + opt8('military_spending.png') + i32(105) + opt8('military_spending.png')
    + s8('campaign') + b(False),
    # Copied from vanilla unit-set armour effects (icon, priority 401, battle category).
    s8(ARMOUR_EFFECT) + opt8('armour.png') + i32(401) + opt8('armour.png') + s8('battle') + b(True),
]))

# effect_bonus_value_ids_unit_sets_tables v0: bonus_value_id, effect, unit_set
write(f'db/effect_bonus_value_ids_unit_sets_tables/{FRAG}', db_file(0, [
    s8('upkeep_mod') + s8(UPKEEP_EFFECT) + s8(UPKEEP_SET),
    s8('armour_mod') + s8(ARMOUR_EFFECT) + s8(ARMOUR_SET),
]))

# unit_sets_tables v2: key, use_unit_exp_level_range, min_level, max_level, special_category (opt)
write(f'db/unit_sets_tables/{FRAG}', db_file(2, [
    s8(UPKEEP_SET) + b(False) + i32(-1) + i32(-1) + opt8(''),
    s8(ARMOUR_SET) + b(False) + i32(-1) + i32(-1) + opt8(''),
]))

# unit_set_to_unit_junctions_tables v1: exclude, unit_caste, unit_category, unit_class,
# unit_record (all opt), unit_set
write(f'db/unit_set_to_unit_junctions_tables/{FRAG}', db_file(1, [
    b(False) + opt8('') + opt8('') + opt8('') + opt8(u) + s8(unit_set)
    for unit_set, units in ((UPKEEP_SET, UPKEEP_UNITS), (ARMOUR_SET, ARMOUR_UNITS))
    for u in units
]))

# The vanilla Black Council dilemma cooldown change (Naggarond only) and the new Black
# Council itself live in build_black_council.py.

# pooled_resource_factors_tables v5: key, is_hidden
write(f'db/pooled_resource_factors_tables/{FRAG}', db_file(5, [s8(FACTOR) + b(False)]))

# pooled_resource_factor_junctions_tables v3: unique_id, factor, resource, minimum, maximum,
# specific_faction_set (opt), sort_order
write(f'db/pooled_resource_factor_junctions_tables/{FRAG}', db_file(3, [
    s8('def_slaves_naggarond_tribute') + s8(FACTOR) + s8('def_slaves')
    + i32(0) + i32(2147483647) + opt8('') + i32(0),
]))

loc = {
    f'effect_bundles_localised_title_{BUNDLE}': TITLE,
    f'effect_bundles_localised_description_{BUNDLE}': DESCRIPTION,
    f'effects_description_{TRIBUTE_EFFECT}':
        'Slave tribute: %+n% of slaves captured by other Dark Elf factions in battle or by raiding, '
        'delivered at the start of each turn (15% from trade partners, none from factions at war '
        'with Naggarond)',
    f'effects_description_{ARMOUR_EFFECT}':
        'Armour: %+n for Black Guard of Naggarond, Bleakswords, Dreadspears, Darkshards, Cold One '
        'and Reaper Bolt Thrower units, and Master [[img:icon_hero]][[/img]]Heroes',
    f'effects_description_{UPKEEP_EFFECT}':
        'Upkeep: %+n% for Black Guard of Naggarond, Dreadspears, Bleakswords and Darkshards units, '
        'and Master [[img:icon_hero]][[/img]]Heroes',
    f'pooled_resource_factors_display_name_positive_{FACTOR}': 'Tribute to the Witch King',
    f'pooled_resource_factors_display_name_negative_{FACTOR}': 'Tribute to the Witch King',
}
d = b'\xff\xfeLOC\x00' + struct.pack('<II', 1, len(loc))
for k, v in loc.items():
    d += s16(k) + s16(v) + b'\x00'
write(f'text/db/{FRAG}.loc', d)
print('data written to', root)
