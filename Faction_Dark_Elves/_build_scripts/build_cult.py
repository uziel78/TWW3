"""Write Druchii_Cult-of-Pleasure_MOD's DB tables and loc file into a pack source folder.

The pack also carries the campaign/frontend Lua (starting army + Druchii Anointed), which lives
in the source folder's script/ directory and isn't touched by this builder.

1. Faction effects: Morathi gets a new bundle (druchii_cult_faction_effects) via an override of
   the faction_starting_general_effects row keyed wh2_main_def_morathi, the same pointer swap as
   Druchii_Naggarond_MOD (overriding vanilla loc keys doesn't show on the faction screen, new
   keys do). For now it's the vanilla bundle's effects plus a "Cult Recruitment changes" line.
2. Cult recruitment: Devotees of Slaanesh (not the Crossbows version) can be recruited from the
   Den of Indulgence (Pleasure Cult tier 2) and House of Pleasure (tier 3) as well, so they're
   available from tier 2 up (vanilla: tiers 4-5). The rows are limited to the Cult of Pleasure
   with building_units_allowed.faction (as CA does for e.g. the Host of Nagash's port units).
3. Daemonette caps: 5 Daemonettes (+1 per Den of Indulgence) and 2 Exalted Daemonettes (+1 per
   Halls of Hedonism) faction-wide, and a per-army cap of 6 combined (bonuses/army cap scripted).
4. Mark of Slaanesh for the Cult's units (attributes + resistance + speed, faction-wide).

Usage: build_cult.py <pack source folder>
"""
import os, struct, sys, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twpack import Pack, DATA, table, encode_db, table_version

root = sys.argv[1]
FRAG = 'Druchii_Cult-of-Pleasure_MOD'
FACTION = 'wh2_main_def_cult_of_pleasure'

db = Pack(DATA + r'\db.pack')
out_tables, loc = {}, {}
import pickle
loc_vanilla = pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loc_en.pkl'), 'rb'))


def add(table_name, **row):
    out_tables.setdefault(table_name, []).append(row)


def new_key(text, taken):
    k = zlib.crc32(text.encode()) & 0x7fffffff
    while k in taken:
        k = (k + 1) & 0x7fffffff
    taken.add(k)
    return k


# --------------------------------------------------------------------------
# 1. Faction effects bundle (vanilla effects + the Cult Recruitment line)
# --------------------------------------------------------------------------
VANILLA_BUNDLE = 'wh2_main_lord_trait_def_morathi'
BUNDLE = 'druchii_cult_faction_effects'
RECRUITMENT_EFFECT = 'druchii_cult_effect_cult_recruitment'

add('faction_starting_general_effects_tables', agent_subtype='wh2_main_def_morathi', effect_bundle=BUNDLE)

vanilla = next(r for r in table(db, 'effect_bundles_tables') if r['key'] == VANILLA_BUNDLE)
add('effect_bundles_tables', **dict(vanilla, key=BUNDLE))
loc[f'effect_bundles_localised_title_{BUNDLE}'] = vanilla['localised_title']
loc[f'effect_bundles_localised_description_{BUNDLE}'] = vanilla['localised_description']
# Vanilla effects left out of the Cult's bundle (user, 2026-11-24): -25% construction cost for
# Sorcery buildings. The faction-select screen lists this bundle, so it's gone there too.
DROPPED_EFFECTS = {'wh_main_effect_building_construction_cost_mod_sorcery_def'}
for r in table(db, 'effect_bundles_to_effects_junctions_tables'):
    if r['effect_bundle_key'] == VANILLA_BUNDLE and r['effect_key'] not in DROPPED_EFFECTS:
        add('effect_bundles_to_effects_junctions_tables', **dict(r, effect_bundle_key=BUNDLE))

add('effects_tables', effect=RECRUITMENT_EFFECT, icon='edict_dae_slaanesh.png', priority=2, icon_negative='edict_dae_slaanesh.png',
    category='campaign', is_positive_value_good=True)
loc[f'effects_description_{RECRUITMENT_EFFECT}'] = 'Cult Recruitment changes'
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=BUNDLE, effect_key=RECRUITMENT_EFFECT,
    effect_scope='faction_to_faction_own_unseen', value=1.0, advancement_stage='start_turn_completed')

# --------------------------------------------------------------------------
# 2. Cult recruitment: Devotees of Slaanesh from tier 2 up, Cult of Pleasure only
# --------------------------------------------------------------------------
DEVOTEES = 'wh3_dlc27_sla_inf_devotees_of_slaanesh'
allowed = table(db, 'building_units_allowed_tables')
taken = {r['key'] for r in allowed}
template = next(r for r in allowed if r['building'] == 'wh2_main_def_pleasure_cult_4' and r['unit'] == DEVOTEES)
for building in ['wh2_main_def_pleasure_cult_2', 'wh2_main_def_pleasure_cult_3']:
    # enabled=True: every one of CA's faction-specific rows has it (all non-faction rows have False);
    # v1 copied False from the template and the rows did nothing in game.
    add('building_units_allowed_tables', **dict(template, building=building, faction=FACTION, enabled=True,
                                                key=new_key(building + DEVOTEES, taken)))

# --------------------------------------------------------------------------
# 2b. More Slaanesh recruits (user, 2026-11-25), Cult of Pleasure only (faction rows, as above):
#      Seekers of Slaanesh   House of Pleasure (Pleasure Cult tier 3) and up
#      Spawn of Slaanesh     Sorceress' Abode (the Sorcery building of settlement tier 3) and up
#    A level only offers the units it lists itself, so every level from the first one gets a row.
#    The units (and the Cultist hero's unit, section 17) also join the Cult roster, Morathi's
#    military group wh3_main_def_morathi (used by the Cult and its separatists only), which already
#    holds the Daemonettes, Devotees and the Druchii Anointed.
# --------------------------------------------------------------------------
SEEKERS = 'wh3_main_sla_cav_seekers_of_slaanesh_0'
SPAWN = 'wh3_main_sla_mon_spawn_of_slaanesh_0'
FURIES, PREYTON = 'wh3_main_sla_inf_chaos_furies_0', 'wh3_dlc27_sla_mon_preyton'   # Beastmasters, section 25b
COLD_ONE_KNIGHTS = 'wh2_main_def_cav_cold_one_knights_0'                                  # Dread Manse, section 25c
CHAOS_WARRIORS_SLA = 'wh3_dlc20_chs_inf_chaos_warriors_msla'    # hand weapon & shield
PLEASURESEEKERS = 'wh3_dlc27_sla_cav_pleasureseekers'
CHAOS_KNIGHTS_SLA = 'wh3_dlc20_chs_cav_chaos_knights_msla'
ROSTER_ADDITIONS = [SEEKERS, SPAWN, FURIES, PREYTON, 'wh3_main_sla_cha_cultist_0',
                    CHAOS_WARRIORS_SLA, PLEASURESEEKERS, CHAOS_KNIGHTS_SLA]
for unit, buildings in [(SEEKERS, ['wh2_main_def_pleasure_cult_3', 'wh2_main_def_pleasure_cult_4', 'wh2_main_def_pleasure_cult_5']),
                        (SPAWN, ['wh2_main_def_sorcery_1', 'wh2_main_def_sorcery_2'])]:
    for building in buildings:
        add('building_units_allowed_tables', **dict(template, building=building, unit=unit, faction=FACTION, enabled=True,
                                                    key=new_key(building + unit, taken)))
for unit in ROSTER_ADDITIONS:
    add('units_to_groupings_military_permissions_tables', unit=unit, military_group='wh3_main_def_morathi')

# --------------------------------------------------------------------------
# 3. Daemonette caps (faction-wide, separate per unit): 5 Daemonettes / 2 Exalted in the faction bundle. CA's own
#    unit-cap system (bonus value unit_cap on the unit record, as the Tomb Kings/Eltharion use).
#    +1 Daemonettes per Den of Indulgence (Pleasure Cult tier 2 and up) and +1 Exalted per Halls of
#    Hedonism (tier 4 and up) come from a second bundle
#    whose values the campaign script sets each turn (wh3_dlc23 Hellforge pattern); the per-army
#    cap of 6 combined is scripted too. (Replaced the Sorceress-based bonus, 2026-11-24.)
# --------------------------------------------------------------------------
DAEMONETTES = 'wh3_main_sla_inf_daemonette_0'
EXALTED = 'wh3_main_sla_inf_daemonette_1'
CAP_D = 'druchii_cult_effect_unit_cap_daemonettes'
CAP_E = 'druchii_cult_effect_unit_cap_exalted_daemonettes'
for effect, unit, name, base in [(CAP_D, DAEMONETTES, 'Daemonettes of Slaanesh', 5.0),
                                 (CAP_E, EXALTED, 'Exalted Daemonettes of Slaanesh', 2.0)]:
    add('effects_tables', effect=effect, icon='unit_capacity.png', priority=1, icon_negative='unit_capacity.png',
        category='campaign', is_positive_value_good=True)
    add('effect_bonus_value_unit_record_junctions_tables', bonus_value_id='unit_cap', effect=effect, unit_record_key=unit)
    loc[f'effects_description_{effect}'] = f'Unit capacity: %+n\n{name}'
    # The base (5 Daemonettes, 2 Exalted) is no longer in the faction bundle: the faction-select
    # screen lists every effect of that bundle, so the script puts base + bonus in DEN_BUNDLE.

DEN_BUNDLE = 'druchii_cult_den_daemonette_caps'
template_bundle = next(r for r in table(db, 'effect_bundles_tables') if r['key'] == 'wh3_dlc23_bundle_chd_unit_cap_rituals')
add('effect_bundles_tables', **dict(template_bundle, key=DEN_BUNDLE, localised_title='Dens of Indulgence',
                                     localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{DEN_BUNDLE}'] = 'Temples of Excess'
loc[f'effect_bundles_localised_description_{DEN_BUNDLE}'] = (
    "The Cult's temples of excess draw the servants of the Dark Prince to its revels.")
# Legacy: the retired Sorceress bundle stays defined so saves that still carry it load cleanly
# (the script removes it from the faction on load).
OLD_SORC_BUNDLE = 'druchii_cult_sorceress_daemonette_caps'
add('effect_bundles_tables', **dict(template_bundle, key=OLD_SORC_BUNDLE, localised_title='Sorceresses of the Cult',
                                     localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{OLD_SORC_BUNDLE}'] = 'Sorceresses of the Cult'
for effect in [CAP_D, CAP_E]:
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=OLD_SORC_BUNDLE, effect_key=effect,
        effect_scope='faction_to_faction_own', value=0.0, advancement_stage='start_turn_completed')
# +1 Khainite Assassin per Executioner's Hall (wh2_main_def_murder_2), on top of its vanilla +1.
ASSASSIN_CAP = 'wh2_main_effect_agent_cap_increase_def_khainite_assassin'
for effect in [CAP_D, CAP_E, ASSASSIN_CAP]:
    # Values are overwritten by the script (cm:create_new_custom_effect_bundle + set_effect_value).
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=DEN_BUNDLE, effect_key=effect,
        effect_scope='faction_to_faction_own', value=1.0, advancement_stage='start_turn_completed')

# Event feed message when the script cancels a Daemonette unit queued past a limit.
loc['campaign_localised_strings_string_druchii_cult_cancel_title'] = 'Recruitment cancelled'
loc['campaign_localised_strings_string_druchii_cult_cancel_army'] = (
    'This army can hold no more Daemonette units (Daemonettes and Exalted Daemonettes together).')
loc['campaign_localised_strings_string_druchii_cult_cancel_temples'] = (
    "The Cult's temples can bind no more of these daemons. Build or upgrade Pleasure Cult temples to summon more.")
loc['campaign_localised_strings_string_druchii_cult_cancel_refunded'] = 'The unit was removed from the queue and refunded.'
# v21: levies (Bleakswords, Darkshards, Dreadspears) are cancelled and refunded too, like Daemonettes.
loc['campaign_localised_strings_string_druchii_cult_cancel_levies'] = (
    "The Cult's settlements have given all the levies of this regiment they can.")
loc['campaign_localised_strings_string_druchii_cult_cancel_halls'] = (
    'Dreadspears are only raised in provinces with Halls of Ravaging.')

# (v11, no longer used by the script: kept so older saves' tooltips still resolve.)
# Tooltip when the faction has as many as its Dens / Halls allow (script lock).
loc['campaign_localised_strings_string_druchii_cult_daemonette_cap_full'] = (
    '[[col:red]]The Cult\'s temples can bind no more of these daemons. '
    'Build or upgrade more Pleasure Cult temples to summon more.[[/col]]')
# Tooltip on the greyed-out unit cards when the selected army already has 6 (script).
loc['campaign_localised_strings_string_druchii_cult_army_daemonette_cap'] = (
    '[[col:red]]This army already has 6 Daemonette units (Daemonettes and Exalted Daemonettes '
    'together, including units in the recruitment queue).[[/col]]')

# --------------------------------------------------------------------------
# 4. Mark of Slaanesh for the Cult's units (as on the Devotees of Slaanesh): the mark_slaanesh,
#    immune_to_psychology and strider attributes, plus the stats CA builds into marked units
#    (+5% physical resistance like the Slaanesh Chaos Warriors, and +10% speed).
#    Units: the Cult's own roster (Morathi's military group), without lords, Regiments of Renown,
#    Daemons, and units that already have the Mark (the Devotees); plus the Dark Elf heroes
#    (every Sorceress lore, Master, Khainite Assassin; user 2026-11-24, which also reverses the
#    earlier Assassin exclusion; Death Hags taken out again 2026-11-25). An attribute a unit already has (Black Guard /
#    Executioners' / the Assassin's Immune to Psychology, the Assassin's Strider) isn't given again.
# --------------------------------------------------------------------------
groups = {}
for r in table(db, 'unit_attributes_to_groups_junctions_tables'):
    groups.setdefault(r['attribute_group'], set()).add(r['attribute'])
main_units = {r['unit']: r for r in table(db, 'main_units_tables')}
land_units = {r['key']: r for r in table(db, 'land_units_tables')}
mark_units = []
# Left out by the user's choice (2026-11-24), on top of the rules above.
NO_MARK = {
    'wh2_dlc10_def_cav_doomfire_warlocks_0',     # Doomfire Warlocks
    'wh2_main_def_mon_black_dragon',             # Black Dragon
    'wh2_dlc10_def_mon_kharibdyss_0',            # Kharibdyss
    'wh2_main_def_mon_war_hydra',                # War Hydra
    'wh2_dlc10_def_mon_feral_manticore_0',       # Feral Manticore
}
for r in table(db, 'units_to_groupings_military_permissions_tables'):
    if r['military_group'] != 'wh3_main_def_morathi':
        continue
    m = main_units[r['unit']]
    attrs = groups.get(land_units[m['land_unit']]['attribute_group'], set())
    # Regiments of Renown: is_renown, and "_ror" in the key as a backstop.
    if m['caste'] in ('lord', 'hero') or m['is_renown'] or '_ror' in r['unit'] or r['unit'] in NO_MARK \
            or 'mark_slaanesh' in attrs or 'daemonic' in attrs or '_sla_' in r['unit']:
        continue
    mark_units.append((r['unit'], attrs))
# All Dark Elf heroes (every variant/mount; the roster only lists some of them). The Druchii
# Anointed (a Slaanesh hero) already has the Mark.
for u, m in sorted(main_units.items()):
    # Death Hags left out again (user, 2026-11-25: the Cult recruits Cultists of Slaanesh instead).
    if m['caste'] == 'hero' and '_def_cha_' in u and '_death_hag' not in u and u not in NO_MARK and not m['is_renown']:
        attrs = groups.get(land_units[m['land_unit']]['attribute_group'], set())
        if 'mark_slaanesh' not in attrs and 'daemonic' not in attrs:
            mark_units.append((u, attrs))
mark_units.sort()


def unit_set(key, units):
    add('unit_sets_tables', key=key, use_unit_exp_level_range=False, min_unit_exp_level_inclusive=-1,
        max_unit_exp_level_inclusive=-1, special_category='')
    for u in units:
        add('unit_set_to_unit_junctions_tables', exclude=False, unit_caste='', unit_category='', unit_class='',
            unit_record=u, unit_set=key)


# Only the Mark of Slaanesh attribute line sits in the faction bundle (so the faction-select screen
# shows one Mark line). The other parts are in MARK_BUNDLE, applied to the faction by the script.
MARK_BUNDLE = 'druchii_cult_mark_of_slaanesh'
add('effect_bundles_tables', **dict(template_bundle, key=MARK_BUNDLE, localised_title='Mark of Slaanesh',
                                     localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{MARK_BUNDLE}'] = 'Mark of Slaanesh'
loc[f'effect_bundles_localised_description_{MARK_BUNDLE}'] = 'The Dark Prince has marked the Cult as his own.'
MARK_SET = 'druchii_cult_mark_units'
unit_set(MARK_SET, [u for u, _ in mark_units])
MARK_LINE = 'druchii_cult_effect_mark_of_slaanesh'
for attribute, effect, visible in [('mark_slaanesh', MARK_LINE, True),
                                   ('immune_to_psychology', 'druchii_cult_effect_mark_immune_to_psychology', False),
                                   ('strider', 'druchii_cult_effect_mark_strider', False)]:
    units = [u for u, attrs in mark_units if attribute not in attrs]
    set_key = MARK_SET if len(units) == len(mark_units) else f'druchii_cult_mark_units_{attribute}'
    if set_key != MARK_SET:
        unit_set(set_key, units)
    add('unit_set_unit_attribute_junctions_tables', key=effect, unit_attribute=attribute, unit_set=set_key)
    add('effect_bonus_value_unit_set_unit_attribute_junctions_tables', bonus_value_id='enable', effect=effect,
        unit_set_attribute=effect)
    add('effects_tables', effect=effect, icon='corruption_slaanesh.png', priority=3,
        icon_negative='corruption_slaanesh.png', category='battle', is_positive_value_good=True)
    loc[f'effects_description_{effect}'] = 'Mark of Slaanesh for all Cult units'
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=BUNDLE if visible else MARK_BUNDLE,
        effect_key=effect, effect_scope='faction_to_force_own' if visible else 'faction_to_force_own_unseen',
        value=1.0, advancement_stage='start_turn_completed')

for bonus_value, effect, icon, value in [
        ('unit_damage_resistance_physical_mod', 'druchii_cult_effect_mark_physical_resistance', 'resistance_physical.png', 5.0),
        ('mod_land_movement_battle', 'druchii_cult_effect_mark_speed', 'battle_movement.png', 10.0)]:
    add('effect_bonus_value_ids_unit_sets_tables', bonus_value_id=bonus_value, effect=effect, unit_set=MARK_SET)
    add('effects_tables', effect=effect, icon=icon, priority=3, icon_negative=icon, category='battle',
        is_positive_value_good=True)
    loc[f'effects_description_{effect}'] = 'Mark of Slaanesh: %+n%'
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=MARK_BUNDLE, effect_key=effect,
        effect_scope='faction_to_force_own_unseen', value=value, advancement_stage='start_turn_completed')
print('Mark of Slaanesh units:', len(mark_units))

# --------------------------------------------------------------------------
# 5. The Cult's own Conscription Halls chain. Vanilla rows can't be deleted and
#    building_units_allowed can only ADD units per faction, so the Cult gets a copy of the chain
#    (druchii_cult_barracks_1-3) with its own units, and the vanilla chain is disabled for the
#    Cult only (building_culture_variants: faction row with disables=True). The copy is disabled
#    for everyone else and enabled for the Cult (CA's pattern for the Gork & Mork idols).
#      Tier 1 Conscription Halls   Bleakswords
#      Tier 2 Halls of Mustering   + Darkshards (no Shields)
#      Tier 3 Halls of Ravaging    + Dreadspears, Sisters of Slaughter, the Master (hero)
#    The campaign script converts vanilla Halls in Cult settlements into the copy.
# --------------------------------------------------------------------------
VANILLA_CHAIN, CULT_CHAIN = 'wh2_main_def_barracks', 'druchii_cult_barracks'
lvl = lambda chain, n: f'{chain}_{n}'

# chain + levels (same building instance as vanilla, so still one Halls per settlement)
for r in table(db, 'building_chains_tables'):
    if r['key'] == VANILLA_CHAIN:
        add('building_chains_tables', **dict(r, key=CULT_CHAIN))
for r in table(db, 'building_levels_tables'):
    if r['chain'] == VANILLA_CHAIN:
        add('building_levels_tables', **dict(r, level_name=r['level_name'].replace(VANILLA_CHAIN, CULT_CHAIN),
                                             chain=CULT_CHAIN))
for r in table(db, 'building_upgrades_junction_tables'):
    if r['from'].startswith(VANILLA_CHAIN):
        add('building_upgrades_junction_tables', **{'from': r['from'].replace(VANILLA_CHAIN, CULT_CHAIN),
                                                    'to': r['to'].replace(VANILLA_CHAIN, CULT_CHAIN)})
for r in table(db, 'building_chain_availability_sets_tables'):
    if r['building_chain'] == VANILLA_CHAIN and r['id'] == 'wh2_main_bas_def':
        add('building_chain_availability_sets_tables', **dict(r, building_chain=CULT_CHAIN))
for r in table(db, 'building_chain_set_items_tables'):
    if r['chain'] == VANILLA_CHAIN:
        add('building_chain_set_items_tables', **dict(r, chain=CULT_CHAIN))
for r in table(db, 'building_set_to_building_junctions_tables'):
    if r['building_chain'] == VANILLA_CHAIN:
        add('building_set_to_building_junctions_tables', **dict(r, building_chain=CULT_CHAIN))
# AI: build and value it like the vanilla Halls
for r in table(db, 'cai_construction_system_building_values_tables'):
    if r['building_chain'] == VANILLA_CHAIN:
        add('cai_construction_system_building_values_tables', **dict(r, building_chain=CULT_CHAIN))
for r in table(db, 'cai_construction_system_synergies_tables'):
    if r['potential_buiding_chain_key'] == VANILLA_CHAIN:
        add('cai_construction_system_synergies_tables', **dict(
            r, potential_buiding_chain_key=CULT_CHAIN,
            potential_building_level_inclusive_start=r['potential_building_level_inclusive_start'].replace(VANILLA_CHAIN, CULT_CHAIN),
            potential_building_level_inclusive_end=r['potential_building_level_inclusive_end'].replace(VANILLA_CHAIN, CULT_CHAIN)))
for r in table(db, 'cai_construction_system_unblocking_buildings_tables'):
    if r['building_start'].startswith(VANILLA_CHAIN):
        add('cai_construction_system_unblocking_buildings_tables', **dict(
            r, building_start=r['building_start'].replace(VANILLA_CHAIN, CULT_CHAIN),
            building_end=r['building_end'].replace(VANILLA_CHAIN, CULT_CHAIN)))

# names, icons, availability per faction
for n in (1, 2, 3):
    v = next(r for r in table(db, 'building_culture_variants_tables')
             if r['building'] == lvl(VANILLA_CHAIN, n) and not r['faction'] and not r['culture'] and not r['subculture'])
    add('building_culture_variants_tables', **dict(v, building=lvl(CULT_CHAIN, n), disables=True))
    add('building_culture_variants_tables', **dict(v, building=lvl(CULT_CHAIN, n), faction=FACTION, disables=False))
    add('building_culture_variants_tables', **dict(v, building=lvl(VANILLA_CHAIN, n), faction=FACTION, disables=True))
    for key in (f'building_culture_variants_name_{lvl(CULT_CHAIN, n)}',
                f'building_culture_variants_name_{lvl(CULT_CHAIN, n)}{FACTION}'):
        loc[key] = ['Conscription Halls', 'Halls of Mustering', 'Halls of Ravaging'][n - 1]
loc[f'building_chains_chain_tooltip_{CULT_CHAIN}'] = 'Barracks'
loc[f'building_chains_encyclopedia_name_{CULT_CHAIN}'] = 'Barracks'

# units (each level lists everything it allows, as CA does)
BLEAKSWORDS, DARKSHARDS, DREADSPEARS = ('wh2_main_def_inf_bleakswords_0', 'wh2_main_def_inf_darkshards_0',
                                        'wh2_main_def_inf_dreadspears_0')
SISTERS = 'wh2_dlc10_def_inf_sisters_of_slaughter'
tier_units = {1: [BLEAKSWORDS], 2: [BLEAKSWORDS, DARKSHARDS], 3: [BLEAKSWORDS, DARKSHARDS, DREADSPEARS, SISTERS]}
unit_row = next(r for r in allowed if r['building'] == 'wh2_main_def_barracks_1' and r['unit'] == BLEAKSWORDS)
for n, units in tier_units.items():
    for u in units:
        add('building_units_allowed_tables', **dict(unit_row, building=lvl(CULT_CHAIN, n), unit=u,
                                                    key=new_key(lvl(CULT_CHAIN, n) + u, taken)))
# the Master: only from tier 3 (vanilla: tiers 2-3)
for r in table(db, 'building_effects_junction_tables'):
    if r['building'] == lvl(VANILLA_CHAIN, 3):
        add('building_effects_junction_tables', **dict(r, building=lvl(CULT_CHAIN, 3)))

# --------------------------------------------------------------------------
# 6. Levy caps (v17, user 2026-11-25; was 2/1/1 per whole province): 1 Bleaksword per settlement,
#    1 Darkshards per tier 2+ settlement, 1 Dreadspears per tier 3+ settlement (settlement tier =
#    level of the main settlement building). Values set by the campaign script on a custom copy of
#    this bundle; the limits themselves are the script's recruitment locks (section 5).
# --------------------------------------------------------------------------
PROV_BUNDLE = 'druchii_cult_province_unit_caps'
add('effect_bundles_tables', **dict(template_bundle, key=PROV_BUNDLE, localised_title='Cult Levies',
                                     localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{PROV_BUNDLE}'] = 'Cult Levies'
loc[f'effect_bundles_localised_description_{PROV_BUNDLE}'] = (
    'The Cult keeps only a few drilled regiments, raised from its settlements; greater settlements '
    'muster finer troops.')
for unit, name in [(BLEAKSWORDS, 'Bleakswords'), (DARKSHARDS, 'Darkshards'), (DREADSPEARS, 'Dreadspears')]:
    effect = f'druchii_cult_effect_unit_cap_{name.lower()}'
    add('effects_tables', effect=effect, icon='unit_capacity.png', priority=1, icon_negative='unit_capacity.png',
        category='campaign', is_positive_value_good=True)
    add('effect_bonus_value_unit_record_junctions_tables', bonus_value_id='unit_cap', effect=effect, unit_record_key=unit)
    loc[f'effects_description_{effect}'] = f'Unit capacity: %+n\n{name}'
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=PROV_BUNDLE, effect_key=effect,
        effect_scope='faction_to_faction_own', value=1.0, advancement_stage='start_turn_completed')
# Dreadspears also come from the Dark Elf settlement building itself (vanilla, every tier), so the
# script locks them unless the selected army's province has the Cult's Halls of Ravaging (tier 3).
loc['campaign_localised_strings_string_druchii_cult_requires_halls_of_ravaging'] = (
    '[[col:red]]Dreadspears are only raised in provinces with Halls of Ravaging.[[/col]]')
loc['campaign_localised_strings_string_druchii_cult_province_cap_full'] = (
    '[[col:red]]The Cult\'s settlements have given all the levies of this regiment they can. '
    'Take or grow more settlements to raise more.[[/col]]')
loc['campaign_localised_strings_string_druchii_cult_no_whole_province'] = (
    '[[col:red]]The Cult needs a greater settlement to raise this regiment.[[/col]]')

# --------------------------------------------------------------------------
# 7. (Removed 2026-11-25: v1-v13 disabled the Dread Manse / Palace of Dread Knights for the Cult;
#    the vanilla chain came back in v14; since v16 the Cult has its own copy, section 25c.)
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# 8. No Har Ganeth Executioners for the Cult (they'd come from the Executioner's Hall and the
#    Temple of Khaine). A faction-wide exclusion set (CA's table; CA only uses it for lords and
#    heroes), and the campaign script also locks the unit on every load (event restriction, the
#    same lock the province caps use), so it's blocked even if the exclusion doesn't cover units.
# --------------------------------------------------------------------------
EXCLUSION_SET = 'druchii_cult_exclusions'
add('factionwide_recruitment_unit_exclusions_sets_tables', set=EXCLUSION_SET)
add('factionwide_recruitment_unit_exclusions_units_sets_junctions_tables', set=EXCLUSION_SET,
    unit='wh2_main_def_inf_har_ganeth_executioners_0')
# Kharibdyss (user 2026-11-26): out of the Cult's roster (also dropped from its Beastmasters chain, and
# locked by the campaign script like the Executioners).
add('factionwide_recruitment_unit_exclusions_units_sets_junctions_tables', set=EXCLUSION_SET,
    unit='wh2_dlc10_def_mon_kharibdyss_0')
loc['campaign_localised_strings_string_druchii_cult_no_kharibdyss'] = (
    '[[col:red]]The Cult of Pleasure does not keep Kharibdysses.[[/col]]')
add('faction_factionwide_recruitment_unit_exclusions_set_junctions_tables', faction=FACTION, set=EXCLUSION_SET)
loc['campaign_localised_strings_string_druchii_cult_no_executioners'] = (
    '[[col:red]]The Cult of Pleasure does not raise Executioners.[[/col]]')

# --------------------------------------------------------------------------
# 9. The Cult's own House of Assassins chain (wh2_main_def_murder: House of Assassins, Executioner's
#    Hall), same method as the Conscription Halls. Vanilla, this chain only exists for the Cult and
#    its two offshoots (faction-only culture variant rows, no general row), so the copy gets a Cult
#    row only, and the vanilla Cult row is overridden with disables=True.
#      House of Assassins   unchanged
#      Executioner's Hall   no Har Ganeth Executioners; +2 Khainite Assassins (vanilla +1)
#    The campaign script converts vanilla ones the Cult owns. (The Temple of Khaine, the other
#    Executioner source, is already disabled for the Cult by CA.)
# --------------------------------------------------------------------------
VANILLA_MURDER, CULT_MURDER = 'wh2_main_def_murder', 'druchii_cult_murder'
murder_levels = [r for r in table(db, 'building_levels_tables') if r['chain'] == VANILLA_MURDER]
rn = lambda v: v.replace(VANILLA_MURDER, CULT_MURDER, 1) if isinstance(v, str) and v.startswith(VANILLA_MURDER + '_') else v
for r in table(db, 'building_chains_tables'):
    if r['key'] == VANILLA_MURDER:
        add('building_chains_tables', **dict(r, key=CULT_MURDER))
for r in murder_levels:
    add('building_levels_tables', **dict(r, level_name=rn(r['level_name']), chain=CULT_MURDER))
for r in table(db, 'building_upgrades_junction_tables'):
    if r['from'].startswith(VANILLA_MURDER + '_'):
        add('building_upgrades_junction_tables', **{'from': rn(r['from']), 'to': rn(r['to'])})
for r in table(db, 'building_chain_availability_sets_tables'):
    if r['building_chain'] == VANILLA_MURDER and r['id'] == 'wh2_main_bas_def':
        add('building_chain_availability_sets_tables', **dict(r, building_chain=CULT_MURDER))
for t, col in [('building_chain_set_items_tables', 'chain'), ('building_set_to_building_junctions_tables', 'building_chain'),
               ('cai_construction_system_building_values_tables', 'building_chain')]:
    for r in table(db, t):
        if r[col] == VANILLA_MURDER:
            add(t, **dict(r, **{col: CULT_MURDER}))
for r in table(db, 'building_culture_variants_tables'):
    if r['building'].startswith(VANILLA_MURDER + '_') and r['faction'] == FACTION:
        add('building_culture_variants_tables', **dict(r, building=rn(r['building'])))      # Cult-only copy
        add('building_culture_variants_tables', **dict(r, disables=True))                    # vanilla off for the Cult
        name = loc_vanilla.get(f"building_culture_variants_name_{r['building']}{FACTION}", '')
        loc[f"building_culture_variants_name_{rn(r['building'])}{FACTION}"] = name
        loc[f"building_culture_variants_name_{rn(r['building'])}"] = name
for r in table(db, 'building_units_allowed_tables'):
    if r['building'].startswith(VANILLA_MURDER + '_') and r['unit'] != 'wh2_main_def_inf_har_ganeth_executioners_0':
        add('building_units_allowed_tables', **dict(r, building=rn(r['building']), key=new_key(rn(r['building']) + r['unit'], taken)))
for r in table(db, 'building_effects_junction_tables'):
    if r['building'].startswith(VANILLA_MURDER + '_'):
        row = dict(r, building=rn(r['building']))
        if r['building'] == VANILLA_MURDER + '_2' and r['effect'] == 'wh2_main_effect_agent_cap_increase_def_khainite_assassin':
            row.update(value=2.0, value_damaged=2.0)
        add('building_effects_junction_tables', **row)

# --------------------------------------------------------------------------
# 10. The Cult's own rites: Sacrifice to Mathlann -> a Slaanesh rite (placeholder: no effects yet)
# --------------------------------------------------------------------------
# Each Dark Elf faction gets its rites from a campaign group (campaign_group_rituals) whose member
# names the faction. The Cult shares the default group wh2_main_ritual_def with Naggarond, so it
# gets its own group (Atharti, Hekarti, Khaine + the new rite) and its one member row
# (wh2_main_ritual_def_cult_of_pleasure, keyed on id) is overridden to point at it - the only
# vanilla row touched; Naggarond keeps the default group. The Cult's victory objectives don't use
# Mathlann (Har Ganeth's do). Probably needs a new campaign.
CULT_RITE_GROUP = 'druchii_cult_rites'
VANILLA_RITE_GROUP = 'wh2_main_ritual_def'
MATHLANN = 'wh2_main_ritual_def_mathlann'
SLAANESH_RITE = 'druchii_cult_ritual_slaanesh'
SLAANESH_RITE_SLAVES = 600

add('campaign_groups_tables', id=CULT_RITE_GROUP)
member = next(r for r in table(db, 'campaign_group_members_tables') if r['id'] == 'wh2_main_ritual_def_cult_of_pleasure')
add('campaign_group_members_tables', **dict(member, group=CULT_RITE_GROUP))
for r in table(db, 'campaign_group_rituals_tables'):
    if r['campaign_group'] == VANILLA_RITE_GROUP:
        ritual = SLAANESH_RITE if r['ritual'] == MATHLANN else r['ritual']
        add('campaign_group_rituals_tables', **dict(r, campaign_group=CULT_RITE_GROUP, ritual=ritual))
        unlock = loc_vanilla.get(f"campaign_group_rituals_unlock_text_{VANILLA_RITE_GROUP}{r['ritual']}")
        if unlock is not None and ritual != SLAANESH_RITE:
            loc[f'campaign_group_rituals_unlock_text_{CULT_RITE_GROUP}{ritual}'] = unlock

# The rite: Mathlann's row (cooldowns, category) with its own payload and cost.
# Icon: none (user, 2026-11-25). v1-v13 used N'Kari's faction symbol, which the rites panel drew
# behind the rite's effects. An empty icon is what CA leaves on many rituals (two STANDARD_RITUALs).
mathlann = next(r for r in table(db, 'rituals_tables') if r['key'] == MATHLANN)
add('rituals_tables', **dict(mathlann, key=SLAANESH_RITE, completion_payload=SLAANESH_RITE,
                             expended_resources=SLAANESH_RITE,
                             icon=''))
# Empty payload: no effects yet.
payload = next(r for r in table(db, 'ritual_payloads_tables') if r['key'] == MATHLANN)
add('ritual_payloads_tables', **dict(payload, key=SLAANESH_RITE))
# Cost: 600 slaves (Mathlann: 800), same resource and factor as the vanilla rites.
cost = next(r for r in table(db, 'resource_costs_tables') if r['id'] == MATHLANN)
add('resource_costs_tables', **dict(cost, id=SLAANESH_RITE))
cost_slaves = next(r for r in table(db, 'resource_cost_pooled_resource_junctions_tables') if r['resource_cost'] == MATHLANN)
add('resource_cost_pooled_resource_junctions_tables', **dict(cost_slaves, resource_cost=SLAANESH_RITE,
                                                              amount=-SLAANESH_RITE_SLAVES))
# Rite cost reductions (techs, skills, ...) apply to it like to the other rites; Rakarth's
# Mathlann-specific cooldown effect isn't copied.
for r in table(db, 'effect_bonus_value_ritual_junctions_tables'):
    if r['ritual'] == MATHLANN and r['effect'] in ('wh2_main_effect_def_rite_cost_mod', 'wh2_main_effect_rite_slave_cost_mod'):
        add('effect_bonus_value_ritual_junctions_tables', **dict(r, ritual=SLAANESH_RITE))
loc[f'rituals_display_name_{SLAANESH_RITE}'] = 'Sacrifice to Slaanesh'
# Locked until the Cult has a House of Pleasure (Pleasure Cult tier 3) or better (script, section 12,
# the way CA's wh2_campaign_rites.lua locks/unlocks the Dark Elf rites); CA's text format.
loc[f'campaign_group_rituals_unlock_text_{CULT_RITE_GROUP}{SLAANESH_RITE}'] = (
    '[[col:red]]This rite will unlock after constructing a House of Pleasure.[[/col]]')
loc[f'rituals_description_{SLAANESH_RITE}'] = (
    "The Cult organises massive gatherings to please the Dark Prince through sacrifice and debauchery.")

# --------------------------------------------------------------------------
# 11. The Cult's own Channelling stance: the Dark Elf one + 66% campaign line of sight
# --------------------------------------------------------------------------
# A stance's effects come from campaign_stance_effects_junctions, which can name a single
# faction (as CA does for Valkia's and the Masque of Slaanesh's Channelling, Rakarth's Raiding).
# The stance type, its button and icon stay vanilla. The vision effect is the one CA made for
# stances (the Lizardmen's Astromancy, +150%): "Campaign line of sight (subsequent turn)", scope
# force_to_general_own. Available to every Cult army, like the vanilla Dark Elf Channelling.
CHANNELLING = 'MILITARY_FORCE_ACTIVE_STANCE_TYPE_CHANNELING'
VANILLA_CHANNEL_BUNDLE = 'wh_main_bundle_stance_army_channelling_def'
CULT_CHANNEL_BUNDLE = 'druchii_cult_bundle_stance_channelling'
STANCE_SIGHT = 66

vanilla_channel = next(r for r in table(db, 'effect_bundles_tables') if r['key'] == VANILLA_CHANNEL_BUNDLE)
add('effect_bundles_tables', **dict(vanilla_channel, key=CULT_CHANNEL_BUNDLE))
loc[f'effect_bundles_localised_title_{CULT_CHANNEL_BUNDLE}'] = vanilla_channel['localised_title']
loc[f'effect_bundles_localised_description_{CULT_CHANNEL_BUNDLE}'] = (
    vanilla_channel['localised_description'][:-1] + ", lets the army see further across the land and improves "
    "the chance of finding magic items in battle.")
for r in table(db, 'effect_bundles_to_effects_junctions_tables'):
    if r['effect_bundle_key'] == VANILLA_CHANNEL_BUNDLE:
        add('effect_bundles_to_effects_junctions_tables', **dict(r, effect_bundle_key=CULT_CHANNEL_BUNDLE))
sight = next(r for r in table(db, 'effect_bundles_to_effects_junctions_tables')
             if r['effect_bundle_key'] == 'wh2_main_bundle_stance_army_astromancy'
             and r['effect_key'] == 'wh2_main_effect_stance_line_of_sight_mod')
add('effect_bundles_to_effects_junctions_tables', **dict(sight, effect_bundle_key=CULT_CHANNEL_BUNDLE, value=float(STANCE_SIGHT)))
# +15% magic item drop chance from battle (the effect lords/heroes and items like the Circlet of
# Iron give; in army bundles CA scopes it force_to_general_own).
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=CULT_CHANNEL_BUNDLE,
    effect_key='wh_main_effect_character_mod_ancillary_drop', effect_scope='force_to_general_own', value=15.0,
    advancement_stage='start_turn_completed')
add('campaign_stance_effects_junctions_tables', stance=CHANNELLING, effect_bundle=CULT_CHANNEL_BUNDLE, culture='',
    subculture='', faction=FACTION, force_type='', resource_cost='')

# --------------------------------------------------------------------------
# 12. The pact with N'Kari (Seducers of Slaanesh): relations and Allegiance (applied by script)
# --------------------------------------------------------------------------
# Relations: permanent "Diplomatic relations: +n with <faction>" effects (bonus value
# diplomatic_mod, effect_bonus_value_faction_junctions), the way faction traits do it (Harkon's
# +60 towards the Followers of Nagash). Both directions, since it isn't certain which side's
# attitude an effect moves: the Cult gets CA's own N'Kari effect, N'Kari a new one towards the
# Cult. They sit in their own bundles (applied by the script on a new campaign), not in the
# faction bundle, which the faction-select screen would list.
# Allegiance: there's no direct setter; CA grants it with the payload favour_points(faction, n),
# so the script sends this incident with it.
NKARI = 'wh3_main_sla_seducers_of_slaanesh'
PACT_RELATIONS = 75          # ~45 at the start -> ~120
PACT_CULT_BUNDLE = 'druchii_cult_pact_nkari'
PACT_NKARI_BUNDLE = 'druchii_cult_pact_nkari_seducers'
NKARI_DIPLO_EFFECT = 'wh3_main_ie_faction_political_diplomacy_mod_nkari'       # vanilla, towards the Seducers
CULT_DIPLO_EFFECT = 'druchii_cult_effect_diplomacy_mod_cult_of_pleasure'      # new, towards the Cult
PACT_INCIDENT = 'druchii_cult_incident_pact_nkari'

nkari_effect = next(r for r in table(db, 'effects_tables') if r['effect'] == NKARI_DIPLO_EFFECT)
add('effects_tables', **dict(nkari_effect, effect=CULT_DIPLO_EFFECT))
add('effect_bonus_value_faction_junctions_tables', bonus_value_id='diplomatic_mod', effect=CULT_DIPLO_EFFECT, faction=FACTION)
loc[f'effects_description_{CULT_DIPLO_EFFECT}'] = 'Diplomatic relations: %+n with the Cult of Pleasure'
for bundle, effect, title in [(PACT_CULT_BUNDLE, NKARI_DIPLO_EFFECT, "Pact with N'Kari"),
                              (PACT_NKARI_BUNDLE, CULT_DIPLO_EFFECT, 'Pact with the Cult of Pleasure')]:
    add('effect_bundles_tables', **dict(template_bundle, key=bundle, localised_title=title, localised_description='',
                                         ui_icon='diplomacy.png'))
    loc[f'effect_bundles_localised_title_{bundle}'] = title
    loc[f'effect_bundles_localised_description_{bundle}'] = 'Bound in worship of the Dark Prince.'
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=bundle, effect_key=effect,
        effect_scope='faction_to_faction_own', value=float(PACT_RELATIONS), advancement_stage='start_turn_completed')

# The Cult of Excess (Dark Elves) starts as the Cult's vassal with the same pact: relations +75
# both ways and +66 Allegiance both ways. No vanilla diplomacy effect targets it, so a new one.
EXCESS = 'wh2_main_def_cult_of_excess'
EXCESS_DIPLO_EFFECT = 'druchii_cult_effect_diplomacy_mod_cult_of_excess'   # new, towards the Cult of Excess
PACT_EXCESS_BUNDLE = 'druchii_cult_pact_excess'                            # on the Cult
PACT_EXCESS_VASSAL_BUNDLE = 'druchii_cult_pact_excess_vassal'              # on the Cult of Excess
add('effects_tables', **dict(nkari_effect, effect=EXCESS_DIPLO_EFFECT))
add('effect_bonus_value_faction_junctions_tables', bonus_value_id='diplomatic_mod', effect=EXCESS_DIPLO_EFFECT, faction=EXCESS)
loc[f'effects_description_{EXCESS_DIPLO_EFFECT}'] = 'Diplomatic relations: %+n with the Cult of Excess'
for bundle, effect, title in [(PACT_EXCESS_BUNDLE, EXCESS_DIPLO_EFFECT, 'Pact with the Cult of Excess'),
                              (PACT_EXCESS_VASSAL_BUNDLE, CULT_DIPLO_EFFECT, 'Pact with the Cult of Pleasure')]:
    add('effect_bundles_tables', **dict(template_bundle, key=bundle, localised_title=title, localised_description='',
                                         ui_icon='diplomacy.png'))
    loc[f'effect_bundles_localised_title_{bundle}'] = title
    loc[f'effect_bundles_localised_description_{bundle}'] = 'Bound in worship of the Dark Prince.'
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=bundle, effect_key=effect,
        effect_scope='faction_to_faction_own', value=float(PACT_RELATIONS), advancement_stage='start_turn_completed')

# Ghrond (wh2_main_def_ghrond) less dismissive of the Cult. A "Diplomatic relations +n with X" effect
# on faction A raises X's attitude towards A (v1 put "with the Cult" on Ghrond, and the log showed the
# Cult's attitude towards Ghrond go to 60 while Ghrond's stayed at -10). So the bonus is on the Cult:
# "with Ghrond", a custom value set by the script so Ghrond lands at about 60.
# v1's bundle (on Ghrond) is kept defined so the script can remove it from older saves.
GHROND_BUNDLE = 'druchii_cult_ghrond_courtship'
add('effect_bundles_tables', **dict(template_bundle, key=GHROND_BUNDLE, localised_title='Courted by the Cult',
                                    localised_description='', ui_icon='diplomacy.png'))
loc[f'effect_bundles_localised_title_{GHROND_BUNDLE}'] = 'Courted by the Cult'
loc[f'effect_bundles_localised_description_{GHROND_BUNDLE}'] = "Morathi's agents have been whispering in Ghrond."
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=GHROND_BUNDLE, effect_key=CULT_DIPLO_EFFECT,
    effect_scope='faction_to_faction_own', value=40.0, advancement_stage='start_turn_completed')
GHROND_DIPLO_EFFECT = 'druchii_cult_effect_diplomacy_mod_ghrond'
CULT_GHROND_BUNDLE = 'druchii_cult_courting_ghrond'          # on the Cult
add('effects_tables', **dict(nkari_effect, effect=GHROND_DIPLO_EFFECT))
add('effect_bonus_value_faction_junctions_tables', bonus_value_id='diplomatic_mod', effect=GHROND_DIPLO_EFFECT,
    faction='wh2_main_def_ghrond')
loc[f'effects_description_{GHROND_DIPLO_EFFECT}'] = 'Diplomatic relations: %+n with Ghrond'
add('effect_bundles_tables', **dict(template_bundle, key=CULT_GHROND_BUNDLE, localised_title='Whispers in Ghrond',
                                    localised_description='', ui_icon='diplomacy.png'))
loc[f'effect_bundles_localised_title_{CULT_GHROND_BUNDLE}'] = 'Whispers in Ghrond'
loc[f'effect_bundles_localised_description_{CULT_GHROND_BUNDLE}'] = "Morathi's agents have been whispering in Ghrond."
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=CULT_GHROND_BUNDLE, effect_key=GHROND_DIPLO_EFFECT,
    effect_scope='faction_to_faction_own', value=40.0, advancement_stage='start_turn_completed')

# Incidents carrying the Allegiance (payload favour_points): one to the Cult (+66 with N'Kari and
# +66 with the Cult of Excess), and one sent to N'Kari and to the Cult of Excess (+66 with the
# Cult each), so the AI allies can use allied recruitment of Dark Elf units early on.
PACT_ALLY_INCIDENT = 'druchii_cult_incident_pact_ally'
incident_template = next(r for r in table(db, 'incidents_tables') if r['key'] == 'wh2_main_incident_intercontinental_diplomacy')
add('incidents_tables', **dict(incident_template, key=PACT_INCIDENT))
loc[f'incidents_localised_title_{PACT_INCIDENT}'] = "The Dark Prince's Pact"
loc[f'incidents_localised_description_{PACT_INCIDENT}'] = (
    "The Seducers of Slaanesh and the Cult of Excess stand with the Cult of Pleasure in the Dark Prince's name.")
add('incidents_tables', **dict(incident_template, key=PACT_ALLY_INCIDENT))
loc[f'incidents_localised_title_{PACT_ALLY_INCIDENT}'] = "The Dark Prince's Pact"
loc[f'incidents_localised_description_{PACT_ALLY_INCIDENT}'] = (
    "The Cult of Pleasure stands with us in the Dark Prince's name.")
loc[f'incidents_button_text_{PACT_ALLY_INCIDENT}'] = loc_vanilla.get(
    'incidents_button_text_wh2_main_incident_intercontinental_diplomacy', 'Continue')
loc[f'incidents_button_text_{PACT_INCIDENT}'] = loc_vanilla.get(
    'incidents_button_text_wh2_main_incident_intercontinental_diplomacy', 'Continue')

# --------------------------------------------------------------------------
# 13. Expendable for units the Cult gets from its allies (Allegiance)
# --------------------------------------------------------------------------
# The game has no "recruited with Allegiance" filter for effects. CA's own "for units recruited via
# allied recruitment" effects (Kislev's Ice Court) simply target every unit outside the faction's
# own roster (unit set all_units_excluding_kislev). Here: every unit allied recruitment can offer,
# minus the Cult's own roster (Morathi's military group, so Dark Elf units, Devotees and
# Daemonettes stay normal) and characters.
# Can't be told apart: allied units that are also in the Cult roster (N'Kari's Daemonettes, Dark
# Elf allies' units). In its own bundle, applied by the script on load (not on the faction screen).
EXPENDABLE_SET = 'druchii_cult_allied_units'
EXPENDABLE_EFFECT = 'druchii_cult_effect_allied_expendable'
EXPENDABLE_BUNDLE = 'druchii_cult_allied_expendable'
# v2: an explicit list of units (as 528 of CA's 559 attribute unit sets are). v1 used CA's
# all-classes set minus 68 exclusions; the game crashed after loading into turn 1.
# Source: the game's own list of units that allied recruitment can offer
# (allied_recruitment_unit_permissions), minus the Cult roster and characters.
cult_roster = {r['unit'] for r in table(db, 'units_to_groupings_military_permissions_tables')
               if r['military_group'] == 'wh3_main_def_morathi'}
# + the Slaanesh units added to the Cult roster (section 2b), so the Cult's own aren't Expendable.
cult_roster |= set(ROSTER_ADDITIONS)
castes = {r['unit']: r['caste'] for r in table(db, 'main_units_tables')}
allied_units = sorted(r['unit'] for r in table(db, 'allied_recruitment_unit_permissions_tables')
                      if r['unit'] not in cult_roster and castes.get(r['unit']) not in ('lord', 'hero', None))
unit_set(EXPENDABLE_SET, allied_units)
add('unit_set_unit_attribute_junctions_tables', key=EXPENDABLE_EFFECT, unit_attribute='expendable', unit_set=EXPENDABLE_SET)
add('effect_bonus_value_unit_set_unit_attribute_junctions_tables', bonus_value_id='enable', effect=EXPENDABLE_EFFECT,
    unit_set_attribute=EXPENDABLE_EFFECT)
add('effects_tables', effect=EXPENDABLE_EFFECT, icon='attribute_expendable.png', priority=3, icon_negative='attribute_expendable.png',
    category='battle', is_positive_value_good=True)
loc[f'effects_description_{EXPENDABLE_EFFECT}'] = 'Attribute: Expendable for units from allies'
add('effect_bundles_tables', **dict(template_bundle, key=EXPENDABLE_BUNDLE, localised_title='Borrowed Blades',
                                    localised_description='', ui_icon='attribute_expendable.png'))
loc[f'effect_bundles_localised_title_{EXPENDABLE_BUNDLE}'] = 'Borrowed Blades'
loc[f'effect_bundles_localised_description_{EXPENDABLE_BUNDLE}'] = "The Cult spends its allies' warriors freely."
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=EXPENDABLE_BUNDLE, effect_key=EXPENDABLE_EFFECT,
    effect_scope='faction_to_force_own', value=1.0, advancement_stage='start_turn_completed')
print('Expendable: allied-unit set lists', len(allied_units), 'units')

# --------------------------------------------------------------------------
# 14. Witch Elves: Frenzy -> Pleasure Through Pain (Slaangors' passive), Cult only
# --------------------------------------------------------------------------
# (Death Hags had it too until 2026-11-25; the user undid every Death Hag change.)
# Frenzy is on the land units (land_units_to_unit_abilites_junctions has no faction column), so a
# Cult faction effect switches it off (bonus value 'disable', as CA disables Malus' Tzarkan or the
# High Elf passives) and switches Pleasure Through Pain on ('enable'), for an explicit unit set.
# No tech touches Frenzy for Dark Elves (theirs only change Witch Elf stats). The Witch Elves RoR
# (Sisters of the Singing Doom) keeps Frenzy. In its own bundle, applied by the script on load.
PTP_UNITS = ['wh2_main_def_inf_witch_elves_0']
PTP_SET = 'druchii_cult_pleasure_through_pain_units'
PTP_BUNDLE = 'druchii_cult_pleasure_through_pain'
FRENZY_OFF = 'druchii_cult_effect_frenzy_off'
PTP_ON = 'druchii_cult_effect_pleasure_through_pain'
unit_set(PTP_SET, PTP_UNITS)
for effect, ability, bonus in [(FRENZY_OFF, 'wh_main_unit_passive_frenzy', 'disable'),
                               (PTP_ON, 'wh3_dlc27_unit_passive_pleasure_through_pain', 'enable')]:
    add('unit_set_unit_ability_junctions_tables', key=effect, unit_ability=ability, unit_set=PTP_SET)
    add('effect_bonus_value_unit_set_unit_ability_junctions_tables', bonus_value_id=bonus, effect=effect,
        unit_set_ability=effect)
    add('effects_tables', effect=effect, icon='general_ability.png', priority=3, icon_negative='general_ability.png',
        category='battle', is_positive_value_good=True)
loc[f'effects_description_{FRENZY_OFF}'] = 'Passive ability "Frenzy" removed for Witch Elves'
loc[f'effects_description_{PTP_ON}'] = 'Passive ability: "Pleasure Through Pain" for Witch Elves (instead of Frenzy)'
add('effect_bundles_tables', **dict(template_bundle, key=PTP_BUNDLE, localised_title='Pleasure Through Pain',
                                    localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{PTP_BUNDLE}'] = 'Pleasure Through Pain'
loc[f'effect_bundles_localised_description_{PTP_BUNDLE}'] = "The Cult's Witch Elves revel in pain rather than rage."
for effect, scope in [(FRENZY_OFF, 'faction_to_force_own_unseen'), (PTP_ON, 'faction_to_force_own')]:
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=PTP_BUNDLE, effect_key=effect,
        effect_scope=scope, value=1.0, advancement_stage='start_turn_completed')

# --------------------------------------------------------------------------
# 15. The Cult's "How they play" popup without the Black Ark paragraph
# --------------------------------------------------------------------------
# The popup's text for the Cult has its own key (Morathi's part + the shared Dark Elf part). The
# Cult can't summon Black Arks (no Sacrifice to Mathlann), so the Cult's version inlines the shared
# part minus that paragraph; other Dark Elf factions keep the shared text.
HTP_KEY = 'event_feed_strings_text_wh2_scripted_event_how_they_play_cult_of_pleasure_secondary_detail'
shared = loc_vanilla['ui_text_replacements_localised_text_how_they_play_dark_elves']
paragraphs = [p for p in shared.split('\n\n') if 'black_ark' not in p.lower()]
assert len(paragraphs) == len(shared.split('\n\n')) - 1, 'expected exactly one Black Ark paragraph'
loc[HTP_KEY] = '{{tr:how_they_play_dark_elves_morathi}}' + '\n\n'.join(paragraphs)

# The faction's mechanics list (faction-select screen and the campaign loading screen; user
# 2026-11-26): vanilla lists Black Arks, Slaves and Murderous Prowess. The Cult's own version: no
# Black Arks, limited Druchii levies filled out with daemons and allied units, stronger sorcery and
# the Sacrifice to Slaanesh rite, the pact with N'Kari and the Cult of Excess, agents abroad. Same
# "[[img:bullet_...]][[/img]]Title: text" items joined by "||" as CA's; icons are CA's bullets. The
# file sorts before frontend_factions__.loc, so the vanilla key is overridden from this loc file.
loc['frontend_factions_localised_mechanics_wh2_main_def_cult_of_pleasure'] = '||'.join([
    "[[img:bullet_sla_promise_of_perfection]][[/img]]Cult of the Dark Prince: No Black Arks sail for Morathi. "
    "Her power lies in the temples of Slaanesh, which spread corruption and draw daemons to the Cult.",
    "[[img:bullet_sla_summon_disciple_armies]][[/img]]Daemons and Allies: Druchii regiments are levied in limited "
    "numbers. Fill your hosts with Daemons of Slaanesh, the Devoted and the warriors of your allies.",
    "[[img:bullet_tze_grimoires]][[/img]]Sorcery of Excess: The Cult's sorceresses wield potent magic, and the "
    "Sacrifice to Slaanesh rite pours the Dark Prince's favour into your armies.",
    "[[img:bullet_dae_daemonic_gifts]][[/img]]Pact of Pleasure: Begin allied with N'Kari and the Seducers of "
    "Slaanesh, with the Cult of Excess sworn to you as vassals.",
    "[[img:bullet_hef_espionage]][[/img]]Agents Abroad: Morathi's servants already walk distant lands, from the "
    "towers of Saphery to the shadows of Ghrond.",
])

# --------------------------------------------------------------------------
# 16. No Dreadlords (Sword & Crossbow, and the female Sword & Shield) as Cult lords
# --------------------------------------------------------------------------
# Lord types a faction can recruit are its faction_agent_permitted_subtypes rows (agent general).
# The table has a mod_disabled column for exactly this; the Cult's two Dreadlord rows are
# overridden with it set. Their captain (colonel) and politics (minister) rows stay.
for r in table(db, 'faction_agent_permitted_subtypes_tables'):
    if r['faction'] == FACTION and r['agent'] == 'general' and r['subtype'] in ('wh2_main_def_dreadlord', 'wh2_main_def_dreadlord_fem'):
        add('faction_agent_permitted_subtypes_tables', **dict(r, mod_disabled=True))

# --------------------------------------------------------------------------
# 17. Cultist of Slaanesh instead of the Death Hag (Cult only)
# --------------------------------------------------------------------------
# Both are the dignitary agent type. The Cult's Death Hag row in faction_agent_permitted_subtypes is
# overridden with mod_disabled (as section 16 does for the Dreadlords) and the Slaanesh Cultist gets
# a Cult row. (v1-v13 gave the Cult's Death Hags a skill tree without the Cauldron of Blood mount;
# undone 2026-11-25 with the Hags' Mark of Slaanesh and Pleasure Through Pain.)
# Recruitment in the Pleasure Cult chain, the Death Hag's building, one tier earlier: Death Hag
# capacity +1 at tiers 3-5 and recruit rank +2 (tier 4) / +4 (tier 5) -> Cultist capacity +1 at
# tiers 2-5, rank +2 at tier 3 and +4 at tiers 4-5. The Cultist also needs CA's per-province
# "enable recruitment" effect (as on the Slaanesh Devotee buildings). Same effects and scopes as
# CA's rows. The Cultist's own unit goes into the Cult roster (section 2b) like the Druchii Anointed.
# Druchii_Cult-Characters_MOD replaces this vanilla Cultist with the Cult's own (female art sets,
# own skill tree) and disables this permission; the Den effects below then apply to that one.
CULTIST = 'wh3_main_sla_cultist'
for r in table(db, 'faction_agent_permitted_subtypes_tables'):
    if r['faction'] == FACTION and r['subtype'] == 'wh2_main_def_death_hag':
        add('faction_agent_permitted_subtypes_tables', **dict(r, mod_disabled=True))
        add('faction_agent_permitted_subtypes_tables', **dict(r, subtype=CULTIST, mod_disabled=False))
hag_cap = next(r for r in table(db, 'building_effects_junction_tables')
               if r['building'] == 'wh2_main_def_pleasure_cult_3' and r['effect'] == 'wh2_main_effect_agent_cap_increase_def_death_hag')
hag_xp = next(r for r in table(db, 'building_effects_junction_tables')
              if r['building'] == 'wh2_main_def_pleasure_cult_4' and r['effect'] == 'wh2_main_effect_agent_recruitment_xp_def_death_hag')
CULTIST_RANK = {3: 2.0, 4: 4.0, 5: 4.0}
for tier in (2, 3, 4, 5):
    building = f'wh2_main_def_pleasure_cult_{tier}'
    add('building_effects_junction_tables', **dict(hag_cap, building=building, effect='wh3_main_effect_agent_cap_increase_sla_cultist'))
    add('building_effects_junction_tables', **dict(hag_cap, building=building, effect='wh3_main_effect_agent_enable_recruitment_sla_cultist',
                                                   effect_scope='province_to_province_own_unseen'))
    if tier in CULTIST_RANK:
        rank = CULTIST_RANK[tier]
        add('building_effects_junction_tables', **dict(hag_xp, building=building, effect='wh3_main_effect_agent_recruitment_xp_sla_cultist',
                                                       value=rank, value_damaged=rank / 2))

# --------------------------------------------------------------------------
# 18. Sacrifice to Slaanesh: what the rite does
# --------------------------------------------------------------------------
# Like CA's Dark Elf rites (Atharti, Khaine...): the completion payload applies a faction bundle for
# a number of turns (ritual_payload_effect_bundles). In it: unit-set stat effects (the same bonus
# values CA uses, scope faction_to_force_own). The parts data can't do are scripted (Lua section
# 12) while the bundle is active: extra Winds only for armies in the Channelling stance (a force
# bundle) and a chance of pleasure-themed followers for lords, shown as one text-only line.
# Relations are data (below). (The +3 allied units per rite was removed in v19, user 2026-11-25:
# the Cult has a flat 6 allied units per army instead, ALLIED_HOST_BUNDLE.)
RITE_BUNDLE = 'druchii_cult_rite_slaanesh_bundle'
RITE_TURNS = 6
RITE_CHANNEL_BUNDLE = 'druchii_cult_rite_slaanesh_channelling'   # force bundle, script
RITE_ALLIED_CAP_BUNDLE = 'druchii_cult_rite_slaanesh_allied_cap'  # legacy (v5-v18): script removes it from saves
RITE_UPKEEP_SET = 'druchii_cult_rite_upkeep_units'
# v19 (user 2026-11-25): only Devotees of Slaanesh (both) and every Daemonic unit (attribute
# "daemonic", non-characters, any faction's version: allied Daemons count too).
DAEMONIC_UNITS = [u for u, m in main_units.items() if m['caste'] not in ('lord', 'hero')
                  and 'daemonic' in groups.get(land_units[m['land_unit']]['attribute_group'], set())]
RITE_UPKEEP_UNITS = ['wh3_dlc27_sla_inf_devotees_of_slaanesh', 'wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows']
unit_set(RITE_UPKEEP_SET, sorted(set(RITE_UPKEEP_UNITS) | set(DAEMONIC_UNITS)))
print('Rite upkeep set:', len(RITE_UPKEEP_UNITS), 'Devotees +', len(DAEMONIC_UNITS), 'Daemonic units')

add('effect_bundles_tables', **dict(template_bundle, key=RITE_BUNDLE, localised_title='Sacrifice to Slaanesh',
                                    localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{RITE_BUNDLE}'] = 'Sacrifice to Slaanesh'
loc[f'effect_bundles_localised_description_{RITE_BUNDLE}'] = 'The Dark Prince is pleased with his Cult.'
add('ritual_payload_effect_bundles_tables', effect_bundle=RITE_BUNDLE, payload=SLAANESH_RITE, duration=RITE_TURNS,
    scale_effects_by_ritual_uses=0.0)


def rite_effect(key, text, icon, unit_set_key=None, bonus=None, value=1.0, category='battle'):
    add('effects_tables', effect=key, icon=icon, priority=2, icon_negative=icon, category=category,
        is_positive_value_good=True)
    loc[f'effects_description_{key}'] = text
    if bonus:
        add('effect_bonus_value_ids_unit_sets_tables', bonus_value_id=bonus, effect=key, unit_set=unit_set_key)
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=RITE_BUNDLE, effect_key=key,
        effect_scope='faction_to_force_own' if bonus else 'faction_to_faction_own', value=float(value),
        advancement_stage='start_turn_completed')


rite_effect('druchii_cult_rite_upkeep', 'Upkeep: %+n% for Devotees of Slaanesh and Daemonic units',
            'military_spending.png', RITE_UPKEEP_SET, 'upkeep_mod', -50, 'campaign')
# Slaanesh corruption: +10 in the Cult's provinces, +5 in provinces adjacent to them (corruption is
# per province). The adjacent part is CA's "Slaanesh corruption in adjacent provinces" effect, which
# 39 Slaanesh buildings use; the own-province part CA's event/seduction corruption effect.
for effect, value in [('wh3_main_effect_corruption_slaanesh_events', 10.0),
                      ('wh3_main_effect_corruption_slaanesh_adjacent_provinces', 5.0)]:
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=RITE_BUNDLE, effect_key=effect,
        effect_scope='faction_to_province_own', value=value, advancement_stage='start_turn_completed')
# Text-only lines for the scripted parts (no bonus value).
rite_effect('druchii_cult_rite_channelling_text', 'Lords may attract followers; Morathi receives a gift',
            'slaanesh_points.png', category='campaign')

# Relations while the rite lasts, as data (diplomatic_mod, like Mannfred's "Vampiric factions and
# Followers of Nagash": one effect with subculture and faction junctions). v1 scripted them per turn
# with apply_dilemma_diplomatic_bonus and the game crashed at the Cult's turn-2 start, twice.
RITE_DIPLOMACY = [
    ('druchii_cult_rite_diplomacy_slaanesh', 10, 'Diplomatic relations: %+n with Slaanesh factions',
     ['wh3_main_sc_sla_slaanesh'], ['wh3_dlc20_chs_sigvald', 'wh3_dlc20_chs_azazel']),
    ('druchii_cult_rite_diplomacy_others', 5, 'Diplomatic relations: %+n with Elves, Chaos and Norsca',
     ['wh2_main_sc_def_dark_elves', 'wh2_main_sc_hef_high_elves', 'wh_main_sc_chs_chaos', 'wh3_main_sc_dae_daemons',
      'wh3_main_sc_kho_khorne', 'wh3_main_sc_nur_nurgle', 'wh3_main_sc_tze_tzeentch', 'wh_dlc08_sc_nor_norsca'], []),
]
for effect, value, text, subcultures, factions in RITE_DIPLOMACY:
    add('effects_tables', **dict(nkari_effect, effect=effect))
    loc[f'effects_description_{effect}'] = text
    for sc in subcultures:
        add('effect_bonus_value_subculture_junctions_tables', bonus_value_id='diplomatic_mod', effect=effect, subculture=sc)
    for f in factions:
        add('effect_bonus_value_faction_junctions_tables', bonus_value_id='diplomatic_mod', effect=effect, faction=f)
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=RITE_BUNDLE, effect_key=effect,
        effect_scope='faction_to_faction_own', value=float(value), advancement_stage='start_turn_completed')

# Force bundle from the "Sacrifice Slaves" dilemma (section 20): +15 Winds for one turn on top of
# the Channelling stance's own +15 (the stance effect is a per-army reserve). The key still says
# "rite" (v1 gave it for the rite's duration).
add('effect_bundles_tables', **dict(vanilla_channel, key=RITE_CHANNEL_BUNDLE))
loc[f'effect_bundles_localised_title_{RITE_CHANNEL_BUNDLE}'] = 'Sacrifice of Slaves'
loc[f'effect_bundles_localised_description_{RITE_CHANNEL_BUNDLE}'] = 'Slaves were sacrificed to strengthen the Channelling.'
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=RITE_CHANNEL_BUNDLE,
    effect_key='wh3_main_effect_winds_of_magic_channelling_stance', effect_scope='force_to_force_own', value=15.0,
    advancement_stage='start_turn_completed')

# Legacy (v5-v18) allied cap bundle, +3 per rite performed; no longer applied, kept in the DB only so
# the script can remove it from older saves ("Allied unit cap in armies", allied_recruitment_unit_cap_mod).
add('effect_bundles_tables', **dict(template_bundle, key=RITE_ALLIED_CAP_BUNDLE, localised_title="The Dark Prince's Host",
                                    localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{RITE_ALLIED_CAP_BUNDLE}'] = "The Dark Prince's Host"
loc[f'effect_bundles_localised_description_{RITE_ALLIED_CAP_BUNDLE}'] = 'Granted by the Sacrifice to Slaanesh.'
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=RITE_ALLIED_CAP_BUNDLE,
    effect_key='wh3_main_effect_allied_recruitment_unit_cap', effect_scope='faction_to_faction_own', value=3.0,
    advancement_stage='start_turn_completed')
# Base allied units per army 4 -> 6 for the Cult (user 2026-11-25): +2 with the same effect, a DB bundle
# the script applies on every load (not in the starting bundle, so the faction screen stays as it is).
ALLIED_HOST_BUNDLE = 'druchii_cult_allied_host'
add('effect_bundles_tables', **dict(template_bundle, key=ALLIED_HOST_BUNDLE, localised_title='Sworn Allies',
                                    localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{ALLIED_HOST_BUNDLE}'] = 'Sworn Allies'
loc[f'effect_bundles_localised_description_{ALLIED_HOST_BUNDLE}'] = (
    "The Cult's allies march gladly beside its armies.")
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=ALLIED_HOST_BUNDLE,
    effect_key='wh3_main_effect_allied_recruitment_unit_cap', effect_scope='faction_to_faction_own', value=2.0,
    advancement_stage='start_turn_completed')

# --------------------------------------------------------------------------
# 19. Dreadspears get Guardian (Cult only)
# --------------------------------------------------------------------------
# Same 'enable' unit-set ability effect CA uses to give Guardian to Orion, Greatswords and Marauder
# Champions. In its own bundle, applied by the script on load (not on the faction-select screen).
GUARDIAN_SET = 'druchii_cult_guardian_units'
GUARDIAN_EFFECT = 'druchii_cult_effect_guardian_dreadspears'
GUARDIAN_BUNDLE = 'druchii_cult_guardian'
unit_set(GUARDIAN_SET, ['wh2_main_def_inf_dreadspears_0'])
add('unit_set_unit_ability_junctions_tables', key=GUARDIAN_EFFECT, unit_ability='wh2_dlc09_unit_passive_guardian',
    unit_set=GUARDIAN_SET)
add('effect_bonus_value_unit_set_unit_ability_junctions_tables', bonus_value_id='enable', effect=GUARDIAN_EFFECT,
    unit_set_ability=GUARDIAN_EFFECT)
add('effects_tables', effect=GUARDIAN_EFFECT, icon='general_ability.png', priority=3, icon_negative='general_ability.png',
    category='battle', is_positive_value_good=True)
loc[f'effects_description_{GUARDIAN_EFFECT}'] = 'Passive ability: "Guardian" for Dreadspears'
add('effect_bundles_tables', **dict(template_bundle, key=GUARDIAN_BUNDLE, localised_title='Shieldwall of the Cult',
                                    localised_description='', ui_icon='general_ability.png'))
loc[f'effect_bundles_localised_title_{GUARDIAN_BUNDLE}'] = 'Shieldwall of the Cult'
loc[f'effect_bundles_localised_description_{GUARDIAN_BUNDLE}'] = "The Cult's spearmen guard its revels."
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=GUARDIAN_BUNDLE, effect_key=GUARDIAN_EFFECT,
    effect_scope='faction_to_force_own', value=1.0, advancement_stage='start_turn_completed')

# --------------------------------------------------------------------------
# 20. "Sacrifice Slaves" when a Cult army enters the Channelling stance (dilemma, script-triggered)
# --------------------------------------------------------------------------
# Same footprint as the Naggarond mod's Decrees dilemma (which works in game). The first choice's
# payload takes the 36 slaves (FACTION_POOLED_RESOURCE_TRANSACTION, as CA's dilemmas do it) and
# shows what it does; the script then gives that army the Sacrifice of Slaves bundle for a turn.
SACRIFICE_DILEMMA = 'druchii_cult_dilemma_channelling_sacrifice'
SACRIFICE_SLAVES = 36
title = 'Sacrifice Slaves'
desc = ('The army has begun Channelling. The Cult could offer slaves to the Dark Prince to draw the Winds of '
        'Magic more strongly for a turn.')
add('dilemmas_tables', generate=False, key=SACRIFICE_DILEMMA, localised_description=desc, localised_title=title,
    ui_image='politics', prioritized=False, event_category='Event', sound_popup_override='UI_CAM_EVENT_Dilemma',
    sound_click_override='', override_icon='', is_large_dilemma=False)
loc[f'dilemmas_localised_title_{SACRIFICE_DILEMMA}'] = title
loc[f'dilemmas_localised_description_{SACRIFICE_DILEMMA}'] = desc
for component, text, state in [('dummy_druchii_cult_sacrifice_winds', 'This army: +15 Winds of Magic next turn (+30 in total)', 'positive'),
                               ('dummy_druchii_cult_sacrifice_decline', 'The slaves are spared', 'default')]:
    add('campaign_payload_ui_details_tables', component=component, icon='ui/campaign ui/effect_bundles/wizard.png',
        state=state, sort_order=0)
    loc[f'campaign_payload_ui_details_description_{component}'] = text
CHOICES = [
    ('FIRST', 'Sacrifice', 'Let their blood feed the Winds.',
     [('FACTION_POOLED_RESOURCE_TRANSACTION', f'RESOURCE[def_slaves];FACTOR[rites];AMOUNT[-{SACRIFICE_SLAVES}];CONTEXT[absolute]'),
      ('TEXT_DISPLAY', 'LOOKUP[dummy_druchii_cult_sacrifice_winds]')]),
    ('SECOND', 'Spare them', 'The slaves have other uses.',
     [('TEXT_DISPLAY', 'LOOKUP[dummy_druchii_cult_sacrifice_decline]')]),
]
for choice, label, text, payloads in CHOICES:
    add('cdir_events_dilemma_choice_details_tables', choice_key=choice, dilemma_key=SACRIFICE_DILEMMA,
        audio_event_hover='', audio_choice_vo='')
    for n, (payload_key, value) in enumerate(payloads):
        add('cdir_events_dilemma_payloads_tables', choice_key=choice, dilemma_key=SACRIFICE_DILEMMA,
            id=zlib.crc32((SACRIFICE_DILEMMA + choice + str(n)).encode()) & 0x7fffffff, payload_key=payload_key,
            value=value, target_key='default')
    loc[f'cdir_events_dilemma_choice_details_localised_choice_label_{SACRIFICE_DILEMMA}{choice}'] = label
    loc[f'cdir_events_dilemma_choice_details_localised_choice_title_{SACRIFICE_DILEMMA}{choice}'] = text
for option, value in [('VAR_CHANCE', '100'), ('GEN_TARGET_NONE', '')]:
    add('cdir_events_dilemma_option_junctions_tables', dilemma_key=SACRIFICE_DILEMMA,
        id=zlib.crc32((SACRIFICE_DILEMMA + option).encode()) & 0x7fffffff, option_key=option, value=value,
        target='default')

# --------------------------------------------------------------------------
# 21. Cultist garrisons: Pleasure Cult buildings add Devotees, Witch Elves and Daemonettes
# --------------------------------------------------------------------------
# Settlement garrisons come from the shared Dark Elf settlement and walls chains (no faction column,
# and no effect can add garrison units), so those stay. The Pleasure Cult chain is in practice the
# Cult's own (plus its separatists and Ssildra Tor), so its levels get cultist garrison units on top
# (add-only rows). The Conscription Halls and the Dread Manse give no garrison units in vanilla.
def garrison_group(key, unit):
    add('armed_citizenry_unit_groups_tables', unit_group=key)
    add('armed_citizenry_units_to_unit_groups_junctions_tables', id=zlib.crc32(key.encode()) & 0x7fffffff,
        priority=450, unit=unit, unit_group=key)
    return key


G_DEVOTEES = garrison_group('druchii_cult_garrison_devotees', 'wh3_dlc27_sla_inf_devotees_of_slaanesh')
G_DEVOTEES_XBOW = garrison_group('druchii_cult_garrison_devotees_crossbows', 'wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows')
G_WITCH_ELVES = 'wh2_main_def_inf_witch_elves_0'        # vanilla groups
G_DAEMONETTES = 'wh3_main_sla_inf_daemonette_0'
CULT_GARRISONS = {
    1: [G_DEVOTEES],
    2: [G_DEVOTEES, G_DEVOTEES],
    3: [G_DEVOTEES, G_DEVOTEES, G_WITCH_ELVES],
    4: [G_DEVOTEES, G_DEVOTEES, G_DEVOTEES_XBOW, G_WITCH_ELVES],
    5: [G_DEVOTEES, G_DEVOTEES, G_DEVOTEES_XBOW, G_DEVOTEES_XBOW, G_WITCH_ELVES, G_DAEMONETTES],
}
for tier, groups_list in CULT_GARRISONS.items():
    level = f'wh2_main_def_pleasure_cult_{tier}'
    for n, group in enumerate(groups_list):
        add('building_level_armed_citizenry_junctions_tables', building_level=level,
            id=zlib.crc32(f'druchii_cult_garrison_{level}_{n}'.encode()) & 0x7fffffff, unit_group=group)

# --------------------------------------------------------------------------
# 22. The Cult's own allied outpost (in allied settlements): Devotees instead of Corsairs / Black Guard
# --------------------------------------------------------------------------
# wh3_main_def_allied_outpost is an ordinary chain in the allied foreign-slot set, offered to Dark
# Elves through the chain availability set. Same method as the Conscription Halls: a copy
# (druchii_cult_allied_outpost_1-3) disabled for everyone but the Cult, and the vanilla chain
# disabled for the Cult (culture variant faction rows). Everything else is copied as is (allied
# recruitment, effects, settlement types, diplomatic stance requirements); in the garrison
# Black Ark Corsairs -> Devotees of Slaanesh, Black Guard -> Devotees (Crossbows), Bleakswords stay.
# Outposts the Cult built before keep the vanilla garrison.
VANILLA_OUTPOST, CULT_OUTPOST = 'wh3_main_def_allied_outpost', 'druchii_cult_allied_outpost'
ro = lambda v: v.replace(VANILLA_OUTPOST, CULT_OUTPOST, 1) if isinstance(v, str) and v.startswith(VANILLA_OUTPOST) else v
for r in table(db, 'building_chains_tables'):
    if r['key'] == VANILLA_OUTPOST:
        add('building_chains_tables', **dict(r, key=CULT_OUTPOST))
for r in table(db, 'building_levels_tables'):
    if r['chain'] == VANILLA_OUTPOST:
        add('building_levels_tables', **dict(r, level_name=ro(r['level_name']), chain=CULT_OUTPOST))
for r in table(db, 'building_upgrades_junction_tables'):
    if r['from'].startswith(VANILLA_OUTPOST + '_'):
        add('building_upgrades_junction_tables', **{'from': ro(r['from']), 'to': ro(r['to'])})
for t_name, col in [('building_chain_availability_sets_tables', 'building_chain'), ('building_chain_set_items_tables', 'chain'),
                    ('building_set_to_building_junctions_tables', 'building_chain'),
                    ('cai_construction_system_building_values_tables', 'building_chain'),
                    ('settlement_type_to_building_chains_junctions_tables', 'building_chain')]:
    for r in table(db, t_name):
        if r[col] == VANILLA_OUTPOST and (t_name != 'building_chain_availability_sets_tables' or r['id'] == 'wh2_main_bas_def'):
            add(t_name, **dict(r, **{col: CULT_OUTPOST}))
for t_name, col in [('building_effects_junction_tables', 'building'), ('building_allied_units_tables', 'building'),
                    ('foreign_building_level_diplomatic_stance_requirements_tables', 'building_level')]:
    for r in table(db, t_name):
        if r[col].startswith(VANILLA_OUTPOST + '_'):
            add(t_name, **dict(r, **{col: ro(r[col])}))
OUTPOST_SWAP = {'wh2_main_def_inf_black_ark_corsairs_0': G_DEVOTEES, 'wh2_main_def_inf_black_guard_0': G_DEVOTEES_XBOW}
for r in table(db, 'building_level_armed_citizenry_junctions_tables'):
    if r['building_level'].startswith(VANILLA_OUTPOST + '_'):
        add('building_level_armed_citizenry_junctions_tables', building_level=ro(r['building_level']),
            id=zlib.crc32(f"druchii_cult_outpost_{r['id']}".encode()) & 0x7fffffff,
            unit_group=OUTPOST_SWAP.get(r['unit_group'], r['unit_group']))
for r in table(db, 'building_culture_variants_tables'):
    if r['building'].startswith(VANILLA_OUTPOST + '_') and not r['faction']:
        add('building_culture_variants_tables', **dict(r, building=ro(r['building']), disables=True))
        add('building_culture_variants_tables', **dict(r, building=ro(r['building']), faction=FACTION, disables=False))
        add('building_culture_variants_tables', **dict(r, faction=FACTION, disables=True))
        name = loc_vanilla.get(f"building_culture_variants_name_{r['building']}{r['culture']}{r['subculture']}", '')
        for key in (f"building_culture_variants_name_{ro(r['building'])}{r['culture']}{r['subculture']}",
                    f"building_culture_variants_name_{ro(r['building'])}{r['culture']}{r['subculture']}{FACTION}"):
            loc[key] = name
        for f in ('description', 'short_description'):
            src = f"building_culture_variants_{f}_{r['building']}{r['culture']}{r['subculture']}"
            if src in loc_vanilla:
                for suffix in ('', FACTION):
                    loc[f"building_culture_variants_{f}_{ro(r['building'])}{r['culture']}{r['subculture']}{suffix}"] = loc_vanilla[src]

# --------------------------------------------------------------------------
# 23. +1 Sorceress capacity from the Cult's major settlements (tier 2 and up), Cult only
# --------------------------------------------------------------------------
# Only the capacity (v1 also unlocked recruitment, like the Sorceress' Abode; the user undid that,
# so the Abode / Tower stay the way to unlock it, and Morathi's skill The First Sorceress unlocks it
# in all provinces). Effect rows with CA's context requirement IsFactionMorathi (Owner is the Cult),
# so other Dark Elves are unaffected. On tiers 2-5 so it stays after upgrading (a building's effects
# belong to its current tier); minor settlements get nothing.
abode_cap = next(r for r in table(db, 'building_effects_junction_tables')
                 if r['building'] == 'wh2_main_def_sorcery_1' and r['effect'] == 'wh2_main_effect_agent_cap_increase_def_sorceress')
for tier in (2, 3, 4, 5):
    add('building_effects_junction_tables', **dict(abode_cap, building=f'wh2_main_def_settlement_major_{tier}',
                                                   context_requirement='IsFactionMorathi'))

# --------------------------------------------------------------------------
# 24. The Cult's own slave diktats: all last 6 turns; Open Markets gives gold per turn (user, 2026-11-25)
# --------------------------------------------------------------------------
# Same method as the rites (section 10): the diktats come from the campaign group
# wh3_main_feature_dark_elves_not_lokhir, which has one member row per faction; the Cult's row
# (keyed on id) is pointed at the Cult's own group with copies of the three diktats. The province
# panel lists a faction's rituals by category (SLAVE_RITUAL), and the "other diktats cannot be
# performed" effect blocks by category too, so the copies behave like the originals.
# Costs stay the same (the vanilla resource costs are reused, and the diktat cost effects are copied).
#   Fights to the Death   +10 public order, 6 turns (vanilla 5)
#   Slave-Drive           +50 growth, 6 turns (vanilla 5)
#   Open Markets          +600 gold per turn for 6 turns (vanilla: 1500 once). There's no flat
#                         income effect for a region bundle in CA's data, so the bundle carries a
#                         text line and the campaign script pays the gold (section 14 of the Lua).
DIKTAT_GROUP_VANILLA = 'wh3_main_feature_dark_elves_not_lokhir'
CULT_DIKTAT_GROUP = 'druchii_cult_slave_diktats'
DIKTAT_TURNS = 6
OPEN_MARKETS = 'druchii_cult_ritual_slave_c'
OPEN_MARKETS_BUNDLE = 'druchii_cult_slave_open_markets'
OPEN_MARKETS_GOLD = 600
OPEN_MARKETS_TEXT = 'druchii_cult_effect_open_markets_income'
add('campaign_groups_tables', id=CULT_DIKTAT_GROUP)
diktat_member = next(r for r in table(db, 'campaign_group_members_tables')
                     if r['id'] == DIKTAT_GROUP_VANILLA + '_def_cult_of_pleasure')
add('campaign_group_members_tables', **dict(diktat_member, group=CULT_DIKTAT_GROUP))
rituals_by_key = {r['key']: r for r in table(db, 'rituals_tables')}
payload_bundles = table(db, 'ritual_payload_effect_bundles_tables')
for gr in table(db, 'campaign_group_rituals_tables'):
    if gr['campaign_group'] != DIKTAT_GROUP_VANILLA:
        continue
    vanilla_key = gr['ritual']                                   # wh3_main_ritual_def_slave_a/b/c
    letter = vanilla_key[-1]
    key = f'druchii_cult_ritual_slave_{letter}'
    v = rituals_by_key[vanilla_key]
    payload_key = f'druchii_cult_slave_action_{letter}'
    add('campaign_group_rituals_tables', **dict(gr, campaign_group=CULT_DIKTAT_GROUP, ritual=key))
    loc[f'campaign_group_rituals_unlock_text_{CULT_DIKTAT_GROUP}{key}'] = ''
    add('rituals_tables', **dict(v, key=key, completion_payload=payload_key))      # same cost (expended_resources)
    add('ritual_payloads_tables', key=payload_key, human_only=False, payload_base='')
    loc[f'rituals_display_name_{key}'] = loc_vanilla[f'rituals_display_name_{vanilla_key}']
    loc[f'rituals_description_{key}'] = loc_vanilla[f'rituals_description_{vanilla_key}']
    for r in table(db, 'effect_bonus_value_ritual_junctions_tables'):
        if r['ritual'] == vanilla_key:
            add('effect_bonus_value_ritual_junctions_tables', **dict(r, ritual=key))
    vanilla_bundle = next(r['effect_bundle'] for r in payload_bundles if r['payload'] == v['completion_payload'])
    if key != OPEN_MARKETS:
        # The vanilla bundle (its own effects and text), just for 6 turns. The vanilla payload has no
        # other parts (Open Markets' 1500 gold is a resource transaction, not copied).
        add('ritual_payload_effect_bundles_tables', effect_bundle=vanilla_bundle, payload=payload_key,
            duration=DIKTAT_TURNS, scale_effects_by_ritual_uses=0.0)
        continue
    vb = next(r for r in table(db, 'effect_bundles_tables') if r['key'] == vanilla_bundle)
    add('effect_bundles_tables', **dict(vb, key=OPEN_MARKETS_BUNDLE))
    loc[f'effect_bundles_localised_title_{OPEN_MARKETS_BUNDLE}'] = loc_vanilla[f'rituals_display_name_{vanilla_key}']
    loc[f'effect_bundles_localised_description_{OPEN_MARKETS_BUNDLE}'] = loc_vanilla[f'rituals_description_{vanilla_key}']
    add('ritual_payload_effect_bundles_tables', effect_bundle=OPEN_MARKETS_BUNDLE, payload=payload_key,
        duration=DIKTAT_TURNS, scale_effects_by_ritual_uses=0.0)
    for r in table(db, 'effect_bundles_to_effects_junctions_tables'):
        if r['effect_bundle_key'] == vanilla_bundle and r['effect_key'] == 'wh3_main_ritual_target_block_slave_actions':
            add('effect_bundles_to_effects_junctions_tables', **dict(r, effect_bundle_key=OPEN_MARKETS_BUNDLE))
    dummy = next(r for r in table(db, 'effects_tables') if r['effect'] == 'wh3_main_ritual_def_slave_action_1_reward_dummy')
    add('effects_tables', **dict(dummy, effect=OPEN_MARKETS_TEXT))
    loc[f'effects_description_{OPEN_MARKETS_TEXT}'] = (
        f'Generates [[img:icon_treasury]][[/img]] {OPEN_MARKETS_GOLD} for the treasury each turn while active')
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=OPEN_MARKETS_BUNDLE, effect_key=OPEN_MARKETS_TEXT,
        effect_scope='region_to_region_own', value=1.0, advancement_stage='start_turn_completed')

# --------------------------------------------------------------------------
# 25. Cult-only copies of vanilla chains (same method as the allied outpost, section 22): a copy
#     (druchii_cult_<name>_n, same building instance as vanilla) disabled for everyone but the
#     Cult, the vanilla chain disabled for the Cult (culture variant faction rows), and every other
#     row copied as is (effects, tower visuals, AI values, slots, units). The campaign script
#     converts the vanilla ones the Cult owns or captures (same tier).
#   25a Slave Gate (wh2_main_def_defence_major: Slave Gate, Blackstone Walls, Dread Bulwark):
#       garrison Shades -> Devotees of Slaanesh, Shades (Additional Hand Weapons) -> Devotees of
#       Slaanesh (Crossbows); the Darkshards and Dark Riders stay.
#   25b Beastmasters (wh2_main_def_beasts, user 2026-11-25): Harpies -> Chaos Furies (Slaanesh) at
#       every level, Black Dragon -> Preyton (Slaanesh) at the top level; tier 1 "Furies' Roost"
#       (was Harpy Roost), tier 3 "Preyton's Pen" (was Dragon Hatchery), with new short texts.
#   25c Dread Manse (wh2_main_def_coldones, user 2026-11-25): Control +3/+5 -> Slaanesh corruption
#       +3/+5; tier 4 Dread Manse recruits Cold One Knights + Chaos Warriors of Slaanesh (hand
#       weapon & shield), tier 5 "Palace of Pleasure" (was Palace of Dread Knights) adds
#       Pleasureseekers + Chaos Knights of Slaanesh. Chariots, Dread Knights, Black Guard dropped.
#   units = {level: [unit, ...]} replaces a level's whole vanilla unit list;
#   effect_swap = {vanilla effect: (new effect, new scope)} keeps the value.
# --------------------------------------------------------------------------
def cult_chain_copy(vanilla, cult, garrison_swap=None, unit_swap=None, names=None, short_texts=None,
                    units=None, effect_swap=None):
    rc = lambda v: v.replace(vanilla, cult, 1) if isinstance(v, str) and v.startswith(vanilla + '_') else v
    for r in table(db, 'building_chains_tables'):
        if r['key'] == vanilla:
            add('building_chains_tables', **dict(r, key=cult))
    for r in table(db, 'building_levels_tables'):
        if r['chain'] == vanilla:
            add('building_levels_tables', **dict(r, level_name=rc(r['level_name']), chain=cult))
    for r in table(db, 'building_upgrades_junction_tables'):
        if r['from'].startswith(vanilla + '_'):
            add('building_upgrades_junction_tables', **{'from': rc(r['from']), 'to': rc(r['to'])})
    for t_name, col in [('building_chain_availability_sets_tables', 'building_chain'), ('building_chain_set_items_tables', 'chain'),
                        ('building_set_to_building_junctions_tables', 'building_chain'),
                        ('cai_construction_system_building_values_tables', 'building_chain')]:
        for r in table(db, t_name):
            if r[col] == vanilla and (t_name != 'building_chain_availability_sets_tables' or r['id'] == 'wh2_main_bas_def'):
                add(t_name, **dict(r, **{col: cult}))
    for r in table(db, 'cai_construction_system_synergies_tables'):
        if r['potential_buiding_chain_key'] == vanilla:
            add('cai_construction_system_synergies_tables', **dict(
                r, potential_buiding_chain_key=cult,
                potential_building_level_inclusive_start=rc(r['potential_building_level_inclusive_start']),
                potential_building_level_inclusive_end=rc(r['potential_building_level_inclusive_end'])))
    for t_name, col in [('building_effects_junction_tables', 'building'),
                        ('building_levels_campaign_bmd_layer_group_junctions_tables', 'building_level')]:
        for r in table(db, t_name):
            if r[col].startswith(vanilla + '_'):
                row = dict(r, **{col: rc(r[col])})
                if t_name == 'building_effects_junction_tables' and r['effect'] in (effect_swap or {}):
                    row['effect'], row['effect_scope'] = effect_swap[r['effect']]
                add(t_name, **row)
    seen = set()
    if units:
        template = next(r for r in table(db, 'building_units_allowed_tables')
                        if r['building'].startswith(vanilla + '_') and not r['faction'])
        for building, unit_list in units.items():
            for unit in unit_list:
                add('building_units_allowed_tables', **dict(template, building=building, unit=unit,
                                                             key=new_key(building + unit, taken)))
    for r in table(db, 'building_units_allowed_tables'):
        if units:
            break
        if r['building'].startswith(vanilla + '_') and not r['faction']:
            building, unit = rc(r['building']), (unit_swap or {}).get(r['unit'], r['unit'])
            if unit is None:                      # unit_swap value None: dropped from the Cult's chain
                continue
            if (building, unit) not in seen:      # CA lists a few units twice on one level
                seen.add((building, unit))
                add('building_units_allowed_tables', **dict(r, building=building, unit=unit, key=new_key(building + unit, taken)))
    for r in table(db, 'building_level_armed_citizenry_junctions_tables'):
        if r['building_level'].startswith(vanilla + '_'):
            group = rc(r['unit_group'])
            if group == r['unit_group']:          # a shared group (not named after the level): keep it
                add('building_level_armed_citizenry_junctions_tables', building_level=rc(r['building_level']),
                    id=zlib.crc32(f"druchii_cult_{cult}_{r['id']}".encode()) & 0x7fffffff, unit_group=group)
                continue
            add('armed_citizenry_unit_groups_tables', unit_group=group)
            # (ids: "druchii_cult_gate_..." kept from the first version so the Slave Gate rows don't change)
            tag = 'gate' if vanilla == 'wh2_main_def_defence_major' else cult
            add('building_level_armed_citizenry_junctions_tables', building_level=rc(r['building_level']),
                id=zlib.crc32(f"druchii_cult_{tag}_{r['id']}".encode()) & 0x7fffffff, unit_group=group)
            for u in table(db, 'armed_citizenry_units_to_unit_groups_junctions_tables'):
                if u['unit_group'] == r['unit_group']:
                    add('armed_citizenry_units_to_unit_groups_junctions_tables', **dict(
                        u, unit_group=group, unit=(garrison_swap or {}).get(u['unit'], u['unit']),
                        id=zlib.crc32(f"druchii_cult_{tag}_unit_{u['id']}".encode()) & 0x7fffffff))
    for r in table(db, 'building_culture_variants_tables'):
        if r['building'].startswith(vanilla + '_') and not r['faction']:
            new_building = rc(r['building'])
            row = dict(r, building=new_building)
            if short_texts and new_building in short_texts:
                row['short_description'] = new_building
                loc[f'building_short_description_texts_short_description_{new_building}'] = short_texts[new_building]
            add('building_culture_variants_tables', **dict(row, disables=True))
            add('building_culture_variants_tables', **dict(row, faction=FACTION, disables=False))
            add('building_culture_variants_tables', **dict(r, faction=FACTION, disables=True))
            suffix_key = f"{r['culture']}{r['subculture']}"
            name = (names or {}).get(new_building) or loc_vanilla.get(f"building_culture_variants_name_{r['building']}{suffix_key}", '')
            for suffix in ('', FACTION):
                loc[f"building_culture_variants_name_{new_building}{suffix_key}{suffix}"] = name
            for f in ('description', 'short_description'):
                src = f"building_culture_variants_{f}_{r['building']}{suffix_key}"
                if src in loc_vanilla:
                    for suffix in ('', FACTION):
                        loc[f"building_culture_variants_{f}_{new_building}{suffix_key}{suffix}"] = loc_vanilla[src]
    for f in ('chain_tooltip', 'encyclopedia_name'):
        src = f'building_chains_{f}_{vanilla}'
        if src in loc_vanilla:
            loc[f'building_chains_{f}_{cult}'] = loc_vanilla[src]


cult_chain_copy('wh2_main_def_defence_major', 'druchii_cult_defence_major',
                garrison_swap={'wh2_main_def_inf_shades_0': 'wh3_dlc27_sla_inf_devotees_of_slaanesh',
                               'wh2_main_def_inf_shades_1': 'wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows'})
cult_chain_copy('wh2_main_def_beasts', 'druchii_cult_beasts',
                # Kharibdyss dropped (user 2026-11-26: not in the Cult's roster; also excluded, section 8).
                unit_swap={'wh2_main_def_inf_harpies': FURIES, 'wh2_main_def_mon_black_dragon': PREYTON,
                           'wh2_dlc10_def_mon_kharibdyss_0': None},
                names={'druchii_cult_beasts_1': "Furies' Roost", 'druchii_cult_beasts_3': "Preyton's Pen"},
                short_texts={
                    'druchii_cult_beasts_1': "Daemonic Furies of the Dark Prince gather to roost above the Cult's temples.",
                    'druchii_cult_beasts_3': "The Cult's Beastmasters break the monstrous Preytons to Slaanesh's will."})
SLAANESH_CORRUPTION = ('wh3_main_effect_corruption_slaanesh_buildings', 'region_to_region_own')
cult_chain_copy('wh2_main_def_coldones', 'druchii_cult_coldones',
                effect_swap={'wh_main_effect_public_order_base': SLAANESH_CORRUPTION},
                units={'druchii_cult_coldones_1': [COLD_ONE_KNIGHTS, CHAOS_WARRIORS_SLA],
                       'druchii_cult_coldones_2': [COLD_ONE_KNIGHTS, CHAOS_WARRIORS_SLA, PLEASURESEEKERS, CHAOS_KNIGHTS_SLA]},
                names={'druchii_cult_coldones_2': 'Palace of Pleasure'},
                short_texts={
                    'druchii_cult_coldones_2': "Cold-blooded knights and Chaos-sworn champions revel in the Dark Prince's palace."})

# --------------------------------------------------------------------------
# 26. Slaanesh followers and items for the Cult (user, 2026-11-25)
# --------------------------------------------------------------------------
# Who can get an ancillary is its faction_set. CA's follower triggers (wh3_campaign_followers.lua)
# listen for every faction and only grant what the character's faction may have (drop chance from
# the faction set), and magic items drop the same way. So the Cult gets copies of the Slaanesh
# sets (same members + the Cult) and the ancillaries below are pointed at the copies; everyone who
# had them keeps them. Left out on purpose:
#  - anything tied to one character (N'Kari's Witstealer Sword, Dechala's / the Masque's / Styrkaar's
#    items, the Slaanesh mounts of Chaos heroes): quest items and subtype-locked ancillaries;
#  - followers that only work with Slaanesh's own mechanics: Dominatrix (Disciple armies), Enticer
#    and Great Tempter (Seduce Units);
#  - the Banner of Depravity (no way to get it outside its owner's skill/quest);
#  - shared Chaos-gods sets (Khorne/Nurgle/Tzeentch too): not Slaanesh's own.
CULT_SLAANESH_ANCILLARIES = [
    # magic items (randomly dropped)
    'wh3_main_anc_arcane_item_rod_of_command', 'wh3_main_anc_talisman_jewel_of_denial',
    'wh3_main_anc_talisman_ring_of_sensation', 'wh3_main_anc_weapon_lash_of_despair',
    'wh3_main_anc_magic_standard_banner_of_ecstacy', 'wh3_main_anc_magic_standard_siren_standard',
    # followers (CA's triggers)
    'wh3_main_anc_follower_sla_agent_of_temptation', 'wh3_main_anc_follower_sla_card_shark',
    'wh3_main_anc_follower_sla_courtesan', 'wh3_main_anc_follower_sla_cult_neophyte',
    'wh3_main_anc_follower_sla_cult_treasurer', 'wh3_main_anc_follower_sla_epicurean',
    'wh3_main_anc_follower_sla_gourmand', 'wh3_main_anc_follower_sla_master_musician',
    'wh3_main_anc_follower_sla_master_painter', 'wh3_main_anc_follower_sla_master_poet',
    'wh3_main_anc_follower_sla_paramour', 'wh3_main_anc_follower_sla_slaaneshi_familiar',
    'wh3_main_anc_follower_sla_slaaneshi_mutant', 'wh3_main_anc_follower_sla_slaaneshi_zealot',
]
set_items = table(db, 'faction_set_items_tables')
taken_set_ids = {r['id'] for r in set_items}
cult_sets = {}
for r in table(db, 'ancillaries_tables'):
    if r['key'] not in CULT_SLAANESH_ANCILLARIES:
        continue
    old_set = r['faction_set']
    if old_set not in cult_sets:
        new_set = f'druchii_cult_{old_set}'
        cult_sets[old_set] = new_set
        add('faction_sets_tables', key=new_set)
        for it in set_items:
            if it['set'] == old_set:
                add('faction_set_items_tables', **dict(it, set=new_set, id=new_key(new_set + str(it['id']), taken_set_ids)))
        add('faction_set_items_tables', culture='', faction=FACTION, remove=False, set=new_set, subculture='',
            id=new_key(new_set + FACTION, taken_set_ids))
    add('ancillaries_tables', **dict(r, faction_set=cult_sets[old_set]))
assert len(out_tables['ancillaries_tables']) == len(CULT_SLAANESH_ANCILLARIES), 'an ancillary key is missing'
print('Slaanesh ancillaries for the Cult:', len(CULT_SLAANESH_ANCILLARIES), 'via sets', sorted(cult_sets))

# --------------------------------------------------------------------------
# 27. Regiments of Renown (user 2026-11-25, list cult_ror_list.md)
# --------------------------------------------------------------------------
# RoR are hired from mercenary pools (the Dark Elf pool wh2_main_def_units_of_renown_pool is offered
# by subculture) and every RoR has units_to_exclusive_faction_permissions rows (key + faction):
# only the listed factions may hire it. Removed for the Cult: its own allowed=True row overridden
# to allowed=False. Added: a Cult row in the Dark Elf pool (faction_requirement), an allowed row and
# the Cult's military group. Lord level requirements stay vanilla.
CULT_ROR_REMOVED = [
    'wh2_dlc10_def_inf_the_hellebronai_ror_0',            # The Hellebronai (Dreadspears)
    'wh2_dlc10_def_inf_sisters_of_the_singing_doom_ror_0',  # Sisters of the Singing Doom (Witch Elves)
    'wh2_dlc10_def_inf_the_bolt_fiends_ror_0',            # The Bolt-fiends (Darkshards, Shields)
    'wh2_dlc14_def_inf_harpies_ror_0',                    # The Crows of Khaine (Harpies)
    'wh2_dlc10_def_cav_knights_of_the_ebon_claw_ror_0',   # Knights of the Ebon Claw (Dread Knights)
    'wh2_dlc10_def_inf_blades_of_the_blood_queen_ror_0',  # Blades of the Blood Queen (Executioners)
]
CULT_ROR_ADDED = [
    'wh3_dlc27_sla_mon_preyton_ror',        # Scourge of Arden (Preyton)
    'wh3_twa06_sla_inf_daemonette_ror_0',   # Bringers of Beguilement (Exalted Daemonettes)
    # 2026-11-26 (user): four more from the Slaanesh pool (Lua section 16, second batch).
    'wh3_dlc27_sla_mon_champions_of_slaanesh_ror',      # Pleasure Guard (Champions of Slaanesh)
    'wh3_twa10_sla_inf_marauders_spears_ror',           # The Princes of Perfection (Devoted Marauders, Spears)
    'wh3_dlc27_nor_cav_marauder_horsemen_ror',          # Riders of the Mighty Serpent (Marauder Horsemen)
    'wh3_twa07_sla_cav_heartseekers_of_slaanesh_ror_0', # Eternal Entourage (Heartseekers of Slaanesh)
]
CULT_ROR_POOL = 'wh2_main_def_units_of_renown_pool'
exclusive = table(db, 'units_to_exclusive_faction_permissions_tables')
for u in CULT_ROR_REMOVED:
    assert any(r['key'] == u and r['faction'] == FACTION for r in exclusive), u
    add('units_to_exclusive_faction_permissions_tables', key=u, faction=FACTION, allowed=False)
pool_rows = table(db, 'mercenary_pool_to_groups_junctions_tables')
taken_pool_keys = {r['key'] for r in pool_rows}
groups_by_unit = {r['unit_record']: r['key'] for r in table(db, 'mercenary_unit_groups_tables')}
for u in CULT_ROR_ADDED:
    template = next(r for r in pool_rows if r['group'] == groups_by_unit[u])
    add('mercenary_pool_to_groups_junctions_tables', **dict(
        template, pool=CULT_ROR_POOL, faction_requirement=FACTION, subculture_requirement='', tech_requirement='',
        key=new_key(f'druchii_cult_ror_{u}', taken_pool_keys)))
    add('units_to_exclusive_faction_permissions_tables', key=u, faction=FACTION, allowed=True)
    add('units_to_groupings_military_permissions_tables', military_group='wh3_main_def_morathi', unit=u)
# v23 moved the removed regiments' pool rows to a second pool: no effect in a new campaign either (the
# Cult's pool comes from the campaign's starting state), so it was taken out again in v24. The pool is
# now set by the campaign script (Lua section 16); these rows only add the lock tooltip text.
loc['campaign_localised_strings_string_druchii_cult_ror_not_for_cult'] = (
    '[[col:red]]This regiment does not serve the Cult of Pleasure.[[/col]]')
print('Regiments of Renown: removed', len(CULT_ROR_REMOVED), 'added', len(CULT_ROR_ADDED), '(pool set by script)')

# --------------------------------------------------------------------------
# 28. (Removed 2026-11-25.) v21 tried female Cultist art sets here (portrait file named with one
#     underscore, so likely never loaded). The Cult's Cultist is now its own subtype in
#     Druchii_Cult-Characters_MOD (build_cult_characters.py), which also disables the vanilla
#     Cultist permitted below (section 17) for the Cult; without that pack it stays as a fallback.
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# 29. Summoned Daemon Prince of Slaanesh (user 2026-11-26): a monster unit, not a lord
# --------------------------------------------------------------------------
# A non-character copy of the custom-battle Daemon Prince of Slaanesh (the Champions of Chaos lord
# unit wh3_dlc20_chs_cha_daemon_prince_msla): same model (look 3, as the Slaanesh custom-battle
# roster), stats, attributes and unit abilities, but caste monster / class inf_mel like the Preyton,
# no spells, skills or items, and it gains unit ranks. Key named "summoned" so a lord version can
# be added later under its own key. Recruited at the Pleasure Cult tier 5 (Cult only, faction row),
# cap 1 per Pleasure Cult tier 5 the Cult owns (scripted like the Daemonettes, Lua section 4/5).
# Card picture: the lord's own 60x130 card picture (ui/portraits/units/...msla 3), copied to
# ui/units/icons. No ownership rows (they crash the game at startup; see ENGINE_LESSONS).
# Seekers of Slaanesh get a cap line here too (scripted: 3 +1 per House of Pleasure, tier 3+).
PRINCE_SRC = 'wh3_dlc20_chs_cha_daemon_prince_msla'
PRINCE = 'druchii_cult_mon_daemon_prince_slaanesh_summoned'
PRINCE_VARIANT = 'wh3_dlc20_chs_cha_daemon_prince_msla_3'
PRINCE_CARD_SRC = 'ui/portraits/units/no_culture/dae_sla_daemon_prince_3_0.png'
preyton_mu = main_units['wh3_dlc27_sla_mon_preyton']
add('land_units_tables', **dict(land_units[PRINCE_SRC], key=PRINCE, **{'class': 'inf_mel'}))
add('main_units_tables', **dict(main_units[PRINCE_SRC], unit=PRINCE, land_unit=PRINCE, caste='monster',
                                 ui_unit_group_land=preyton_mu['ui_unit_group_land'], tier=4,
                                 create_time=preyton_mu['create_time'], restrict_xp_gain_in_campaign=False,
                                 campaign_cap=-1, in_encyclopedia=False, is_renown=False,
                                 # 2026-11-26 (user): 2000 / 500, a Keeper of Secrets' cost (briefly
                                 # 2600 / 550; the lord unit is 2000 / 400).
                                 recruitment_cost=2000, multiplayer_cost=2000, upkeep_cost=500))
add('unit_variants_tables', faction='', name=PRINCE, unit=PRINCE, variant=PRINCE_VARIANT, unit_card=PRINCE)
for r in table(db, 'land_units_to_unit_abilites_junctions_tables'):
    if r['land_unit'] == PRINCE_SRC:
        add('land_units_to_unit_abilites_junctions_tables', **dict(r, land_unit=PRINCE))
# 2026-11-26 (user): + Obsessive Adoration (Eternal Entourage), Feasting on Fear (Pleasureseekers), and
# two bound spells as on regular units (2 uses each, no Winds cost): Okkam's Mindrazor (the Lahmian
# Handmaidens' version) and The Enfeebling Foe (the Keeper of Secrets RoR's version). Fiendish Musk
# (key ..._soporific_musk) comes with the lord unit. Blissful Rapture is a Lore of Slaanesh skill
# of the lord, so this unit never had it.
for ability in ['wh3_twa07_unit_passive_obsessive_adoration', 'wh3_main_unit_passive_feasting_on_fear',
                'wh3_dlc29_spell_bound_okkams_mindrazor', 'wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror']:
    add('land_units_to_unit_abilites_junctions_tables', ability=ability, land_unit=PRINCE, culture='*')
loc[f'land_units_onscreen_name_{PRINCE}'] = 'Summoned Daemon Prince of Slaanesh'
prince_row = next(r for r in allowed if r['building'] == 'wh2_main_def_pleasure_cult_4' and r['unit'] == DEVOTEES)
add('building_units_allowed_tables', **dict(prince_row, building='wh2_main_def_pleasure_cult_5', unit=PRINCE,
                                            faction=FACTION, enabled=True,
                                            key=new_key('wh2_main_def_pleasure_cult_5' + PRINCE, taken)))
add('units_to_groupings_military_permissions_tables', unit=PRINCE, military_group='wh3_main_def_morathi')
# Daemonic: the rite's upkeep cut covers it like the other Daemonic units.
add('unit_set_to_unit_junctions_tables', exclude=False, unit_caste='', unit_category='', unit_class='',
    unit_record=PRINCE, unit_set=RITE_UPKEEP_SET)
# Cap lines in the Temples of Excess bundle (the values are set by the script).
CAP_S = 'druchii_cult_effect_unit_cap_seekers'
CAP_P = 'druchii_cult_effect_unit_cap_daemon_prince'
for effect, unit, name in [(CAP_S, SEEKERS, 'Seekers of Slaanesh'), (CAP_P, PRINCE, 'Summoned Daemon Prince of Slaanesh')]:
    add('effects_tables', effect=effect, icon='unit_capacity.png', priority=1, icon_negative='unit_capacity.png',
        category='campaign', is_positive_value_good=True)
    add('effect_bonus_value_unit_record_junctions_tables', bonus_value_id='unit_cap', effect=effect, unit_record_key=unit)
    loc[f'effects_description_{effect}'] = f'Unit capacity: %+n\n{name}'
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=DEN_BUNDLE, effect_key=effect,
        effect_scope='faction_to_faction_own', value=1.0, advancement_stage='start_turn_completed')
# The army cap now counts Seekers too (Lua section 5).
loc['campaign_localised_strings_string_druchii_cult_cancel_army'] = (
    'This army can hold no more daemon units (Daemonettes, Exalted Daemonettes and Seekers of Slaanesh together).')
ui_pack = Pack(DATA + r'\ui.pack')
card_file = next(f for f in ui_pack.files if f.lower() == PRINCE_CARD_SRC)
card_out = os.path.join(root, 'ui', 'units', 'icons', f'{PRINCE}.png')
os.makedirs(os.path.dirname(card_out), exist_ok=True)
open(card_out, 'wb').write(ui_pack.read(card_file))
print('Summoned Daemon Prince of Slaanesh:', PRINCE, '(card', card_out, ')')

# --------------------------------------------------------------------------
# 30. Morathi's sorcery grows with Slaanesh corruption (user 2026-11-26)
# --------------------------------------------------------------------------
# A character bundle on Morathi whose values the campaign script sets (Lua section 17) to half the
# Slaanesh corruption of the region she's in: spell targeting range %, spell intensity % and barrier
# hit points %. Refreshed at turn start, after she moves and at every PendingBattle she's in (then
# cm:update_pending_battle(), as CA's chaos invasion script does after changing effects there).
# Own effects, because CA's "all spells" targeting-range effect lists every lore group except
# Morathi's own (wh2_main_lore_morathi). The barrier effect uses battle_barrier_health_mod (CA defines
# it but never uses it, so whether it's a percentage is unproven; Morathi has no barrier now).
M_RANGE = 'druchii_cult_effect_morathi_spell_range'
M_INTENSITY = 'druchii_cult_effect_morathi_spell_intensity'
M_BARRIER = 'druchii_cult_effect_morathi_barrier'
M_BUNDLE = 'druchii_cult_morathi_corruption_sorcery'
effects_by_key = {r['effect']: r for r in table(db, 'effects_tables')}
add('effects_tables', **dict(effects_by_key['wh3_main_effect_spell_targeting_range_all'], effect=M_RANGE))
add('effects_tables', **dict(effects_by_key['wh3_main_effect_spell_mastery'], effect=M_INTENSITY))
add('effects_tables', **dict(effects_by_key['wh3_dlc27_effect_force_stat_barrier'], effect=M_BARRIER))
range_groups = {r['special_ability_group'] for r in table(db, 'effect_bonus_value_special_ability_group_junctions_tables')
                if r['effect'] == 'wh3_main_effect_spell_targeting_range_all'} | {'wh2_main_lore_morathi'}
for group in sorted(range_groups):
    add('effect_bonus_value_special_ability_group_junctions_tables', bonus_value_id='target_intercept_range_mod',
        effect=M_RANGE, special_ability_group=group)
add('effect_bonus_value_basic_junction_tables', effect=M_INTENSITY, bonus_value_id='spell_mastery_percentage_mod')
add('effect_bonus_value_basic_junction_tables', effect=M_BARRIER, bonus_value_id='battle_barrier_health_mod')
loc[f'effects_description_{M_RANGE}'] = 'Targeting range: %+n% for spells (Slaanesh corruption)'
loc[f'effects_description_{M_INTENSITY}'] = 'Spell intensity: %+n% (Slaanesh corruption)'
loc[f'effects_description_{M_BARRIER}'] = 'Barrier hit points: %+n% (Slaanesh corruption)'
char_bundle_template = next(r for r in table(db, 'effect_bundles_tables')
                            if r['key'] == 'wh2_dlc09_bundle_anc_magic_standard_banner_of_the_hidden_dead')
add('effect_bundles_tables', **dict(char_bundle_template, key=M_BUNDLE, localised_title='Sorcery of Excess',
                                     localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{M_BUNDLE}'] = 'Sorcery of Excess'
loc[f'effect_bundles_localised_description_{M_BUNDLE}'] = (
    "The more the land surrenders to the Dark Prince, the further and fiercer Morathi's sorcery reaches.")
for effect in (M_RANGE, M_INTENSITY, M_BARRIER):
    add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=M_BUNDLE, effect_key=effect,
        effect_scope='character_to_character_own', value=0.0, advancement_stage='start_turn_completed')
print("Morathi's corruption sorcery:", len(range_groups), 'lore groups for the range effect')

# --------------------------------------------------------------------------
# 31. Morathi's Will: campaign line of sight per unit (user 2026-11-26)
# --------------------------------------------------------------------------
# The red-line skill Morathi's Will (cult_army_skills.py, in the Morathi and characters packs) shows a
# text line; the bonus itself is this character bundle, which the campaign script (Lua section 18) keeps
# on every Cult general with that skill: +6% campaign line of sight per Morathi's Will unit in the army,
# up to +100% (an army sees as far as its general; CA's character line-of-sight effect).
WILL_SIGHT_BUNDLE = 'druchii_cult_morathis_will_sight'
add('effect_bundles_tables', **dict(char_bundle_template, key=WILL_SIGHT_BUNDLE, localised_title="Morathi's Will",
                                     localised_description='', ui_icon='agent.png'))
loc[f'effect_bundles_localised_title_{WILL_SIGHT_BUNDLE}'] = "Morathi's Will"
loc[f'effect_bundles_localised_description_{WILL_SIGHT_BUNDLE}'] = (
    "Morathi's scouts and raiders range far ahead of the host.")
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=WILL_SIGHT_BUNDLE,
    effect_key='wh_main_effect_agent_field_line_of_sight_mod', effect_scope='character_to_character_own', value=0.0,
    advancement_stage='start_turn_completed')

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
print('cult data:', {t: len(r) for t, r in out_tables.items()}, len(loc), 'loc entries')
