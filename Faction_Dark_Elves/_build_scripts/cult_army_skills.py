"""The Cult of Pleasure's own versions of three Dark Elf red-line (army) lord skills (user 2026-11-26).

Used by build_morathi.py (Morathi's tree) and build_cult_characters.py (the Cult's Supreme Sorceress
and High Beastmaster trees). Both packs get identical rows under the same keys, so neither pack
depends on the other. The vanilla skills and effects are shared by every Dark Elf lord, so these are
copies with their own effects and unit sets:

  Line Breaker  Black Ark Corsairs -> Devotees of Slaanesh (both), + Witch Elves, Sisters of Slaughter
  Sheafmaster   Black Ark Corsairs (handbows) -> Devotees of Slaanesh (Crossbows)
  Lash Master   - Harpies, Black Dragon (the monster unit; mounted characters never had it), Kharibdyss,
                Feral Manticore; + Preyton (and Scourge of Arden), Chaos Furies, Spawn of Slaanesh
  Daemonologist (was Slaughterlord) every Daemon unit (non-characters with the Daemonic attribute, as the
                rite's upkeep set; the Summoned Daemon Prince isn't in it): level 1 melee attack +6,
                level 2 also speed +6%, level 3 speed +12% (user 2026-11-26)
"""

SKILLS = {   # vanilla skill -> Cult skill
    'wh2_main_skill_def_army_buff_basic_infantry': 'druchii_cult_skill_def_army_buff_basic_infantry',
    'wh2_main_skill_def_army_buff_missile': 'druchii_cult_skill_def_army_buff_missile',
    'wh2_main_skill_def_army_buff_beasts': 'druchii_cult_skill_def_army_buff_beasts',
}
DROP_SETS = {'def_corsairs', 'wh2_main_def_inf_black_ark_corsairs_1', 'def_dragons', 'def_feral_manticore',
             'def_harpies', 'def_kharibdyss'}
EXTRA_SETS = {   # vanilla skill -> (new unit set, units)
    'wh2_main_skill_def_army_buff_basic_infantry': ('druchii_cult_set_line_breaker', [
        'wh3_dlc27_sla_inf_devotees_of_slaanesh', 'wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows',
        'wh2_main_def_inf_witch_elves_0', 'wh2_dlc10_def_inf_sisters_of_slaughter']),
    'wh2_main_skill_def_army_buff_missile': ('druchii_cult_set_sheafmaster', [
        'wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows']),
    'wh2_main_skill_def_army_buff_beasts': ('druchii_cult_set_lash_master', [
        'wh3_dlc27_sla_mon_preyton', 'wh3_dlc27_sla_mon_preyton_ror', 'wh3_main_sla_inf_chaos_furies_0',
        'wh3_main_sla_mon_spawn_of_slaanesh_0']),
}
UNITS_TEXT = {
    'wh2_main_skill_def_army_buff_basic_infantry':
        'Dreadspears, Bleakswords, Darkshards, Devotees of Slaanesh, Witch Elves and Sisters of Slaughter units',
    'wh2_main_skill_def_army_buff_missile': 'Darkshards, Devotees of Slaanesh (Crossbows) and Reaper Bolt Thrower units',
    'wh2_main_skill_def_army_buff_beasts':
        'War Hydra, Bloodwrack Medusa, Bloodwrack Shrine, Preyton, Chaos Furies and Spawn of Slaanesh units',
}


def add_cult_army_skills(add, loc, db, table, loc_vanilla):
    """Adds the three Cult skills (rows, effects, unit sets, loc). Returns SKILLS."""
    skill_effects = table(db, 'character_skill_level_to_effects_junctions_tables')
    bonus = table(db, 'effect_bonus_value_ids_unit_sets_tables')
    effects = {r['effect']: r for r in table(db, 'effects_tables')}
    set_members = {}
    for r in table(db, 'unit_set_to_unit_junctions_tables'):
        set_members.setdefault(r['unit_set'], []).append(r['unit_record'])
    done = set()
    for src, new in SKILLS.items():
        new_set, units = EXTRA_SETS[src]
        add('unit_sets_tables', key=new_set, use_unit_exp_level_range=False, min_unit_exp_level_inclusive=-1,
            max_unit_exp_level_inclusive=-1, special_category='')
        for unit in units:
            add('unit_set_to_unit_junctions_tables', exclude=False, unit_caste='', unit_category='', unit_class='',
                unit_record=unit, unit_set=new_set)
        effect_map = {}
        for r in skill_effects:
            if r['character_skill_key'] != src:
                continue
            sets = [b for b in bonus if b['effect'] == r['effect_key']]
            if not any(b['unit_set'] in DROP_SETS for b in sets):
                effect_map[r['effect_key']] = r['effect_key']      # unchanged (e.g. Medusa reload): reuse
                continue
            new_effect = effect_map.setdefault(r['effect_key'], 'druchii_cult_' + r['effect_key'].split('_', 2)[2])
            if new_effect in done:
                continue
            done.add(new_effect)
            add('effects_tables', **dict(effects[r['effect_key']], effect=new_effect))
            bonus_ids = sorted({b['bonus_value_id'] for b in sets})
            for b in sets:
                if b['unit_set'] not in DROP_SETS:
                    add('effect_bonus_value_ids_unit_sets_tables', **dict(b, effect=new_effect))
            for bid in bonus_ids:
                add('effect_bonus_value_ids_unit_sets_tables', bonus_value_id=bid, effect=new_effect, unit_set=new_set)
            text = loc_vanilla.get(f'effects_description_{r["effect_key"]}', '')
            loc[f'effects_description_{new_effect}'] = text.split(' for ')[0] + ' for ' + UNITS_TEXT[src]
        for t, col in (('character_skills_tables', 'key'), ('character_skill_level_details_tables', 'skill_key'),
                       ('character_skill_utilization_hints_junctions_tables', 'key')):
            for r in table(db, t):
                if r[col] == src:
                    add(t, **dict(r, **{col: new}))
        for r in skill_effects:
            if r['character_skill_key'] == src:
                add('character_skill_level_to_effects_junctions_tables',
                    **dict(r, character_skill_key=new, effect_key=effect_map[r['effect_key']]))
        for kind in ('name', 'description'):
            loc[f'character_skills_localised_{kind}_{new}'] = loc_vanilla.get(f'character_skills_localised_{kind}_{src}', '')
    add_daemonologist(add, loc, db, table, loc_vanilla)
    add_rank7_skills(add, loc, db, table)
    three = add_three_level_skills(add, loc, db, table, loc_vanilla)
    return dict(SKILLS, **{ELITES: DAEMONOLOGIST}, **{src: spec['key'] for src, spec in RANK7.items()}, **three)


ELITES = 'wh2_main_skill_def_army_buff_elites'                  # Slaughterlord
DAEMONOLOGIST = 'druchii_cult_skill_def_army_buff_daemonologist'
DAEMON_SET = 'druchii_cult_set_daemonologist'


def add_daemonologist(add, loc, db, table, loc_vanilla):
    groups = {}
    for r in table(db, 'unit_attributes_to_groups_junctions_tables'):
        groups.setdefault(r['attribute_group'], set()).add(r['attribute'])
    land = {r['key']: r for r in table(db, 'land_units_tables')}
    daemons = sorted(r['unit'] for r in table(db, 'main_units_tables')
                     if r['caste'] not in ('lord', 'hero') and r['land_unit'] in land
                     and 'daemonic' in groups.get(land[r['land_unit']]['attribute_group'], set()))
    add('unit_sets_tables', key=DAEMON_SET, use_unit_exp_level_range=False, min_unit_exp_level_inclusive=-1,
        max_unit_exp_level_inclusive=-1, special_category='')
    for unit in daemons:
        add('unit_set_to_unit_junctions_tables', exclude=False, unit_caste='', unit_category='', unit_class='',
            unit_record=unit, unit_set=DAEMON_SET)
    effects = {r['effect']: r for r in table(db, 'effects_tables')}
    attack, speed = 'druchii_cult_effect_force_stat_melee_attack_daemons', 'druchii_cult_effect_force_stat_speed_daemons'
    for new, template, bonus_id, text in [
            (attack, 'wh2_main_effect_force_stat_melee_attack_witchelf_blackguard_executioner', 'melee_attack_mod',
             'Melee attack: %+n for Daemon units'),
            (speed, 'wh3_dlc27_effect_force_stat_speed_sla_infantry_def', 'mod_land_movement_battle',
             'Speed: %+n% for Daemon units')]:
        add('effects_tables', **dict(effects[template], effect=new))
        add('effect_bonus_value_ids_unit_sets_tables', bonus_value_id=bonus_id, effect=new, unit_set=DAEMON_SET)
        loc[f'effects_description_{new}'] = text
    for t, col in (('character_skills_tables', 'key'), ('character_skill_level_details_tables', 'skill_key'),
                   ('character_skill_utilization_hints_junctions_tables', 'key')):
        for r in table(db, t):
            if r[col] == ELITES:
                add(t, **dict(r, **{col: DAEMONOLOGIST}))
    for level, effect, value in [(1, attack, 6.0), (2, attack, 6.0), (2, speed, 6.0), (3, attack, 6.0), (3, speed, 12.0)]:
        add('character_skill_level_to_effects_junctions_tables', character_skill_key=DAEMONOLOGIST, effect_key=effect,
            effect_scope='general_to_force_own', level=level, value=value)
    loc[f'character_skills_localised_name_{DAEMONOLOGIST}'] = 'Daemonologist'
    loc[f'character_skills_localised_description_{DAEMONOLOGIST}'] = (
        "Versed in the true names and hungers of the Dark Prince's servants, this commander drives the daemons of "
        "the host to strike harder and move faster.")
    return len(daemons)


# --------------------------------------------------------------------------
# Rank 7 skills of the red line (user 2026-11-26). Like CA's, each lists the Regiments of Renown
# versions of its units. Effects are new keys (CA's are shared); "{{tr:rank7}}" is CA's
# "(Rank 7 and above)" suffix.
# --------------------------------------------------------------------------
SET_WILL = 'druchii_cult_set_morathis_will'              # all of Morathi's Will
SET_WILL_MISSILE = 'druchii_cult_set_morathis_will_missile'
SET_CHOSEN = 'druchii_cult_set_chosen_of_excess'
SET_BLADES = 'druchii_cult_set_rapture_of_blades'
RANK7_SETS = {
    SET_WILL: ['wh2_main_def_cav_dark_riders_0', 'wh2_main_def_cav_dark_riders_1', 'wh2_main_def_cav_dark_riders_2',
               'wh2_main_def_inf_shades_0', 'wh2_main_def_inf_shades_1', 'wh2_main_def_inf_shades_2',
               'wh2_dlc10_def_cav_doomfire_warlocks_0', 'wh2_dlc14_def_cav_scourgerunner_chariot_0',
               'wh2_dlc10_def_cav_raven_heralds_ror_0', 'wh2_dlc10_def_cav_slaanesh_harvesters_ror_0',
               'wh2_dlc14_def_cav_scourgerunner_chariot_ror_0', 'wh3_dlc27_nor_cav_marauder_horsemen_ror'],
    SET_WILL_MISSILE: ['wh2_main_def_cav_dark_riders_2', 'wh2_main_def_inf_shades_0', 'wh2_main_def_inf_shades_1',
                       'wh2_main_def_inf_shades_2', 'wh2_dlc14_def_cav_scourgerunner_chariot_0',
                       'wh2_dlc10_def_cav_raven_heralds_ror_0', 'wh2_dlc14_def_cav_scourgerunner_chariot_ror_0',
                       'wh3_dlc27_nor_cav_marauder_horsemen_ror'],
    # No Regiments of Renown exist for these four units.
    SET_CHOSEN: ['wh3_dlc20_chs_inf_chaos_warriors_msla', 'wh3_dlc20_chs_cav_chaos_knights_msla',
                 'wh2_main_def_cav_cold_one_knights_0', 'wh3_dlc27_sla_cav_pleasureseekers'],
    # Sisters of the Singing Doom is the Witch Elves' regiment (not in the Cult's pool; listed as CA does).
    SET_BLADES: ['wh3_dlc27_sla_inf_devotees_of_slaanesh', 'wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows',
                 'wh2_main_def_inf_witch_elves_0', 'wh2_dlc10_def_inf_sisters_of_slaughter',
                 'wh2_dlc10_def_inf_sisters_of_the_singing_doom_ror_0'],
}
DAEMONS_TXT = 'Daemon units'
WILL_TXT = 'Dark Riders, Shades, Doomfire Warlocks and Scourgerunner Chariot units'
WILL_MISSILE_TXT = 'Dark Riders (Repeater Crossbows), Shades and Scourgerunner Chariot units'
CHOSEN_TXT = 'Chaos Warriors of Slaanesh, Chaos Knights of Slaanesh, Cold One Knights and Pleasureseekers units'
BLADES_TXT = 'Devotees of Slaanesh, Witch Elves and Sisters of Slaughter units'
WS = ('melee_damage_mod_mult', 'melee_damage_ap_mod_mult')
RANK7 = {   # vanilla skill -> new skill; effects: (effect, template, bonus ids, unit set, value, text)
    'wh2_main_skill_def_army_buff_cull_the_unworthy': dict(
        key='druchii_cult_skill_def_army_buff_bound_in_rapture', name='Bound in Rapture',
        description="Bound by pacts sealed in pleasure, the Dark Prince's daemons hold firm and strike true at "
                    "this commander's call.",
        effects=[('druchii_cult_effect_force_stat_leadership_daemons_rank7', 'wh2_dlc09_effect_force_stat_leadership_tmb_monster_rank7',
                  ('morale',), DAEMON_SET, 8.0, f'Leadership: %+n for {DAEMONS_TXT}'),
                 ('druchii_cult_effect_force_stat_weapon_strength_daemons_rank7', 'wh2_main_effect_force_stat_weapon_strength_def_militia_boltthrower_rank7',
                  WS, DAEMON_SET, 12.0, f'Weapon strength: %+n% for {DAEMONS_TXT}'),
                 ('druchii_cult_effect_force_stat_ward_save_daemons_rank7',
                  'wh2_dlc11_effect_force_stat_ward_save_knights_corpse_cart_mortis_engine_black_coach_hexwraiths_rank7',
                  ('unit_damage_resistance_all_mod',), DAEMON_SET, 5.0, f'Ward save: %+n% for {DAEMONS_TXT}')]),
    'wh2_main_skill_def_army_buff_rewards_for_ravagers': dict(
        key='druchii_cult_skill_def_army_buff_morathis_will', name="Morathi's Will",
        description="The Hag Sorceress' eyes and knives roam far ahead of the host, striking from the shadows "
                    "before the enemy knows they are seen.",
        effects=[('druchii_cult_effect_force_stat_speed_morathis_will_rank7', 'wh2_main_effect_force_stat_speed_corsairs_shades_riders_rank7',
                  ('mod_land_movement_battle',), SET_WILL, 10.0, f'Speed: %+n% for {WILL_TXT}'),
                 ('druchii_cult_effect_force_stat_range_morathis_will_rank7', 'wh2_main_effect_force_stat_range_def_corsairs_shades_riders_rank7',
                  ('range_mod',), SET_WILL_MISSILE, 15.0, f'Range: %+n% for {WILL_MISSILE_TXT}')],
        attribute=('snipe', 'druchii_cult_effect_attribute_snipe_morathis_will_rank7', SET_WILL_MISSILE,
                   f'Attribute: "Snipe" for {WILL_MISSILE_TXT}'),
        # Text line for the campaign script's line-of-sight bonus (Cult of Pleasure pack, Lua section 18).
        display=('druchii_cult_effect_morathis_will_sight_display',
                 'Campaign line of sight: %+n% for each of these units in the army (up to +100%)', 6.0)),
    'wh2_main_skill_def_army_buff_favour_the_fortunate': dict(
        key='druchii_cult_skill_def_army_buff_chosen_of_excess', name='Chosen of Excess',
        description="Only the most exquisite warriors earn the Dark Prince's favour; the sweet musk that clings to "
                    "them dulls the senses of all who face them.",
        effects=[('druchii_cult_effect_force_stat_charge_chosen_of_excess_rank7',
                  'wh2_main_effect_force_stat_charge_bonus_add_def_blackguard_executioner_coldones_rank7',
                  ('charge_add',), SET_CHOSEN, 12.0, f'Charge bonus: %+n for {CHOSEN_TXT}'),
                 ('druchii_cult_effect_force_stat_weapon_strength_chosen_of_excess_rank7',
                  'wh2_main_effect_force_stat_weapon_strength_def_blackguard_executioner_coldones_rank7',
                  WS, SET_CHOSEN, 12.0, f'Weapon strength: %+n% for {CHOSEN_TXT}')],
        ability=('wh3_main_daemon_body_passive_soporific_musk', 'druchii_cult_effect_ability_soporific_musk_chosen_rank7',
                 SET_CHOSEN, f'Passive ability: "Fiendish Musk" for {CHOSEN_TXT}')),
    'wh2_main_skill_def_army_buff_confer_bloodlust': dict(
        key='druchii_cult_skill_def_army_buff_rapture_of_blades', name='Rapture of Blades',
        description="Lost in the ecstasy of the dance of blades, the Cult's devoted throw themselves upon the foe.",
        effects=[('druchii_cult_effect_force_stat_physical_resistance_blades_rank7',
                  'wh2_main_effect_force_stat_physical_resistance_def_beasts_witchelfs_rank7',
                  ('unit_damage_resistance_physical_mod',), SET_BLADES, 6.0, f'Physical resistance: %n% for {BLADES_TXT}'),
                 ('druchii_cult_effect_force_stat_speed_blades_rank7', 'wh2_main_effect_force_stat_speed_def_beasts_witchelfs_rank7',
                  ('mod_land_movement_battle',), SET_BLADES, 12.0, f'Speed: %+n% for {BLADES_TXT}'),
                 ('druchii_cult_effect_force_stat_weapon_strength_blades_rank7',
                  'wh2_main_effect_force_stat_weapon_strength_def_beasts_witchelfs_rank7',
                  WS, SET_BLADES, 12.0, f'Weapon strength: %+n% for {BLADES_TXT}')]),
}
RANK7_SUFFIX = ' {{tr:rank7}}'


def add_rank7_skills(add, loc, db, table):
    effects = {r['effect']: r for r in table(db, 'effects_tables')}
    for set_key, units in RANK7_SETS.items():
        add('unit_sets_tables', key=set_key, use_unit_exp_level_range=False, min_unit_exp_level_inclusive=-1,
            max_unit_exp_level_inclusive=-1, special_category='')
        for unit in units:
            add('unit_set_to_unit_junctions_tables', exclude=False, unit_caste='', unit_category='', unit_class='',
                unit_record=unit, unit_set=set_key)
    for src, spec in RANK7.items():
        new = spec['key']
        for t, col in (('character_skills_tables', 'key'), ('character_skill_level_details_tables', 'skill_key'),
                       ('character_skill_utilization_hints_junctions_tables', 'key')):
            for r in table(db, t):
                if r[col] == src:
                    add(t, **dict(r, **{col: new}))
        loc[f'character_skills_localised_name_{new}'] = spec['name']
        loc[f'character_skills_localised_description_{new}'] = spec['description']
        lines = []
        for effect, template, bonus_ids, set_key, value, text in spec['effects']:
            add('effects_tables', **dict(effects[template], effect=effect))
            for bid in bonus_ids:
                add('effect_bonus_value_ids_unit_sets_tables', bonus_value_id=bid, effect=effect, unit_set=set_key)
            loc[f'effects_description_{effect}'] = text + RANK7_SUFFIX
            lines.append((effect, value))
        if 'attribute' in spec:
            attribute, effect, set_key, text = spec['attribute']
            add('unit_set_unit_attribute_junctions_tables', key=effect, unit_attribute=attribute, unit_set=set_key)
            add('effect_bonus_value_unit_set_unit_attribute_junctions_tables', bonus_value_id='enable', effect=effect,
                unit_set_attribute=effect)
            add('effects_tables', effect=effect, icon='general_ability.png', priority=3, icon_negative='general_ability.png',
                category='battle', is_positive_value_good=True)
            loc[f'effects_description_{effect}'] = text + RANK7_SUFFIX
            lines.append((effect, 1.0))
        if 'ability' in spec:
            ability, effect, set_key, text = spec['ability']
            add('unit_set_unit_ability_junctions_tables', key=effect, unit_ability=ability, unit_set=set_key)
            add('effect_bonus_value_unit_set_unit_ability_junctions_tables', bonus_value_id='enable', effect=effect,
                unit_set_ability=effect)
            add('effects_tables', effect=effect, icon='general_ability.png', priority=3, icon_negative='general_ability.png',
                category='battle', is_positive_value_good=True)
            loc[f'effects_description_{effect}'] = text + RANK7_SUFFIX
            lines.append((effect, 1.0))
        if 'display' in spec:
            effect, text, value = spec['display']
            add('effects_tables', effect=effect, icon='agent.png', priority=4,
                icon_negative='agent.png', category='campaign', is_positive_value_good=True)
            loc[f'effects_description_{effect}'] = text + RANK7_SUFFIX
            add('character_skill_level_to_effects_junctions_tables', character_skill_key=new, effect_key=effect,
                effect_scope='character_to_character_own', level=1, value=value)
        for effect, value in lines:
            add('character_skill_level_to_effects_junctions_tables', character_skill_key=new, effect_key=effect,
                effect_scope='general_to_force_own', level=1, value=value)


# Supreme Sorceresses only (user 2026-11-26): Strength Through Spite -> Soporific Musk (the Daemon
# Prince's "Fiendish Musk" aura on the character, CA's enable effect). Kindle the Fury stays for now.
STRENGTH_THROUGH_SPITE = 'wh2_main_skill_def_strength_through_spite'
SOPORIFIC_MUSK_SKILL = 'druchii_cult_skill_def_soporific_musk'


def add_soporific_musk_skill(add, loc, db, table):
    for t, col in (('character_skills_tables', 'key'), ('character_skill_level_details_tables', 'skill_key'),
                   ('character_skill_utilization_hints_junctions_tables', 'key')):
        for r in table(db, t):
            if r[col] == STRENGTH_THROUGH_SPITE:
                add(t, **dict(r, **{col: SOPORIFIC_MUSK_SKILL}))
    add('character_skill_level_to_effects_junctions_tables', character_skill_key=SOPORIFIC_MUSK_SKILL,
        effect_key='wh3_main_effect_ability_enable_soporific_musk', effect_scope='character_to_character_own', level=1, value=1.0)
    loc[f'character_skills_localised_name_{SOPORIFIC_MUSK_SKILL}'] = 'Dark Radiance'   # author, 2026-11-27 (was Soporific Musk)
    loc[f'character_skills_localised_description_{SOPORIFIC_MUSK_SKILL}'] = (
        'A cloying, sleep-heavy perfume clings to the Sorceress, dulling the blades and slowing the steps of all '
        'foes who come near.')
    return {STRENGTH_THROUGH_SPITE: SOPORIFIC_MUSK_SKILL}


# Supreme Sorceresses only (user 2026-11-26): Kindle the Fury -> a 600-point barrier for the Sorceress
# (CA's flat barrier effect, as Tzeentch characters' skills use). The node keeps its place and its link
# from the Soporific Musk node (the former Strength Through Spite slot).
KINDLE_THE_FURY = 'wh2_main_skill_def_kindle_the_fury'
VEIL_SKILL = 'druchii_cult_skill_def_veil_of_excess'


def add_veil_skill(add, loc, db, table):
    for t, col in (('character_skills_tables', 'key'), ('character_skill_level_details_tables', 'skill_key'),
                   ('character_skill_utilization_hints_junctions_tables', 'key')):
        for r in table(db, t):
            if r[col] == KINDLE_THE_FURY:
                add(t, **dict(r, **{col: VEIL_SKILL}))
    add('character_skill_level_to_effects_junctions_tables', character_skill_key=VEIL_SKILL,
        effect_key='wh3_main_effect_battle_barrier_health_add', effect_scope='character_to_character_own', level=1, value=600.0)
    loc[f'character_skills_localised_name_{VEIL_SKILL}'] = 'Veil of Excess'
    loc[f'character_skills_localised_description_{VEIL_SKILL}'] = (
        "A shimmering veil of the Dark Prince's favour turns aside blades and sorcery alike before they reach the Sorceress.")
    return {KINDLE_THE_FURY: VEIL_SKILL}


# --------------------------------------------------------------------------
# Champion of Excess (was Knight Lord) and Raid Leader (user 2026-11-26): copies of the vanilla 3-level
# skills with the same values and their own effects. Champion of Excess covers only its new unit set
# (Knight Lord's Cold One sets carry Dread Knights and Cold One Chariots, not in the Cult roster); Raid
# Leader keeps all of CA's sets and adds Riders of the Mighty Serpent, matching Morathi's Will.
# --------------------------------------------------------------------------
KNIGHT_LORD = 'wh2_main_skill_def_army_buff_coldones'
RAID_LEADER = 'wh2_main_skill_def_army_buff_shades_riders'
THREE_LEVEL = {
    KNIGHT_LORD: dict(key='druchii_cult_skill_def_army_buff_champion_of_excess', name='Champion of Excess',
                      description="Steel, beast and daemon-steed alike answer this commander's call to glorious, "
                                  "perfect slaughter.",
                      keep_vanilla_sets=False, set='druchii_cult_set_champion_of_excess',
                      units=['wh3_dlc20_chs_inf_chaos_warriors_msla', 'wh3_dlc20_chs_cav_chaos_knights_msla',
                             'wh2_main_def_cav_cold_one_knights_0', 'wh3_dlc27_sla_cav_pleasureseekers'],
                      text='Chaos Warriors of Slaanesh, Chaos Knights of Slaanesh, Cold One Knights and Pleasureseekers units'),
    RAID_LEADER: dict(key='druchii_cult_skill_def_army_buff_raid_leader', name=None, description=None,
                      keep_vanilla_sets=True, set='druchii_cult_set_raid_leader',
                      units=['wh3_dlc27_nor_cav_marauder_horsemen_ror'], text=None),
}


def add_three_level_skills(add, loc, db, table, loc_vanilla):
    skill_effects = table(db, 'character_skill_level_to_effects_junctions_tables')
    bonus = table(db, 'effect_bonus_value_ids_unit_sets_tables')
    effects = {r['effect']: r for r in table(db, 'effects_tables')}
    out = {}
    for src, spec in THREE_LEVEL.items():
        new = spec['key']
        out[src] = new
        add('unit_sets_tables', key=spec['set'], use_unit_exp_level_range=False, min_unit_exp_level_inclusive=-1,
            max_unit_exp_level_inclusive=-1, special_category='')
        for unit in spec['units']:
            add('unit_set_to_unit_junctions_tables', exclude=False, unit_caste='', unit_category='', unit_class='',
                unit_record=unit, unit_set=spec['set'])
        effect_map = {}
        for r in skill_effects:
            if r['character_skill_key'] != src or r['effect_key'] in effect_map:
                continue
            new_effect = 'druchii_cult_' + r['effect_key'].split('_', 2)[2] + ('_champion' if src == KNIGHT_LORD else '_raid')
            effect_map[r['effect_key']] = new_effect
            add('effects_tables', **dict(effects[r['effect_key']], effect=new_effect))
            rows = [b for b in bonus if b['effect'] == r['effect_key']]
            if spec['keep_vanilla_sets']:
                for b in rows:
                    add('effect_bonus_value_ids_unit_sets_tables', **dict(b, effect=new_effect))
            for bid in sorted({b['bonus_value_id'] for b in rows}):
                add('effect_bonus_value_ids_unit_sets_tables', bonus_value_id=bid, effect=new_effect, unit_set=spec['set'])
            text = loc_vanilla.get(f'effects_description_{r["effect_key"]}', '')
            if spec['text']:
                text = text.split(' for ')[0] + ' for ' + spec['text']
            loc[f'effects_description_{new_effect}'] = text
        for t, col in (('character_skills_tables', 'key'), ('character_skill_level_details_tables', 'skill_key'),
                       ('character_skill_utilization_hints_junctions_tables', 'key')):
            for r in table(db, t):
                if r[col] == src:
                    add(t, **dict(r, **{col: new}))
        for r in skill_effects:
            if r['character_skill_key'] == src:
                add('character_skill_level_to_effects_junctions_tables',
                    **dict(r, character_skill_key=new, effect_key=effect_map[r['effect_key']]))
        loc[f'character_skills_localised_name_{new}'] = spec['name'] or loc_vanilla.get(f'character_skills_localised_name_{src}', '')
        loc[f'character_skills_localised_description_{new}'] = spec['description'] or loc_vanilla.get(
            f'character_skills_localised_description_{src}', '')
    return out
