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
#    Daemons, and units that already have the Mark (the Devotees); plus all Dark Elf heroes
#    (every Sorceress lore, Master, Death Hag, Khainite Assassin; user 2026-11-24, which also
#    reverses the earlier Assassin exclusion). An attribute a unit already has (Black Guard /
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
    if m['caste'] == 'hero' and '_def_cha_' in u and u not in NO_MARK and not m['is_renown']:
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
# 6. Province caps: 2 Bleakswords, 1 Darkshards and 1 Dreadspears per whole province the Cult
#    owns. Values set by the campaign script on a custom copy of this bundle.
# --------------------------------------------------------------------------
PROV_BUNDLE = 'druchii_cult_province_unit_caps'
add('effect_bundles_tables', **dict(template_bundle, key=PROV_BUNDLE, localised_title='Cult Levies',
                                     localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{PROV_BUNDLE}'] = 'Cult Levies'
loc[f'effect_bundles_localised_description_{PROV_BUNDLE}'] = (
    'The Cult keeps only a few drilled regiments, raised from the provinces it rules outright.')
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
    '[[col:red]]The Cult\'s provinces have given all the levies of this regiment they can. '
    'Rule more whole provinces to raise more.[[/col]]')
loc['campaign_localised_strings_string_druchii_cult_no_whole_province'] = (
    '[[col:red]]The Cult must rule a whole province to raise this regiment.[[/col]]')

# --------------------------------------------------------------------------
# 7. No Dread Manse / Palace of Dread Knights (wh2_main_def_coldones: Black Guard, Cold One
#    Knights, Cold One Chariots) for the Cult: disabled per faction like the vanilla Halls above.
#    The campaign script dismantles any the Cult owns or captures.
# --------------------------------------------------------------------------
for n in (1, 2):
    v = next(r for r in table(db, 'building_culture_variants_tables')
             if r['building'] == f'wh2_main_def_coldones_{n}' and not r['faction'] and not r['culture'] and not r['subculture'])
    add('building_culture_variants_tables', **dict(v, faction=FACTION, disables=True))

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
# Icon: there's no Slaanesh rite picture (rite pictures are 320x320 in ui/skins/warhammer2);
# N'Kari's faction symbol (256x256) stands in for now.
mathlann = next(r for r in table(db, 'rituals_tables') if r['key'] == MATHLANN)
add('rituals_tables', **dict(mathlann, key=SLAANESH_RITE, completion_payload=SLAANESH_RITE,
                             expended_resources=SLAANESH_RITE,
                             icon='UI\\flags\\wh3_main_sla_seducers_of_slaanesh\\mon_256.png'))
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
# 14. Witch Elves and Death Hags: Frenzy -> Pleasure Through Pain (Slaangors' passive), Cult only
# --------------------------------------------------------------------------
# Frenzy is on the land units (land_units_to_unit_abilites_junctions has no faction column), so a
# Cult faction effect switches it off (bonus value 'disable', as CA disables Malus' Tzarkan or the
# High Elf passives) and switches Pleasure Through Pain on ('enable'), for an explicit unit set.
# No tech touches Frenzy for Dark Elves (theirs only change Witch Elf stats). The Witch Elves RoR
# (Sisters of the Singing Doom) keeps Frenzy. In its own bundle, applied by the script on load.
PTP_UNITS = ['wh2_main_def_inf_witch_elves_0', 'wh2_main_def_cha_death_hag_0', 'wh2_main_def_cha_death_hag_1']
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
loc[f'effects_description_{FRENZY_OFF}'] = 'Passive ability "Frenzy" removed for Witch Elves and Death Hags'
loc[f'effects_description_{PTP_ON}'] = 'Passive ability: "Pleasure Through Pain" for Witch Elves and Death Hags (instead of Frenzy)'
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
# 17. Death Hags without the Cauldron of Blood mount (Cult only)
# --------------------------------------------------------------------------
# The mount is a skill node in the Death Hag skill tree, which all Dark Elf factions share. CA gives
# single factions their own copy of a hero's tree with a faction_key set (the DLC27 "affinity"
# sets, e.g. Avelorn's Handmaidens). The Cult gets one: every node of the vanilla Death Hag tree
# except the mount (no links or locks point at it). Existing Hags keep a mount already learned.
HAG_SET = 'wh2_main_skill_node_set_def_death_hag'
HAG_MOUNT_NODE = 'wh2_main_skill_node_def_death_hag_mount_1'
CULT_HAG_SET = 'druchii_cult_skill_node_set_def_death_hag'
vanilla_set = next(r for r in table(db, 'character_skill_node_sets_tables') if r['key'] == HAG_SET)
add('character_skill_node_sets_tables', **dict(vanilla_set, key=CULT_HAG_SET, faction_key=FACTION))
hag_items = [r for r in table(db, 'character_skill_node_set_items_tables') if r['set'] == HAG_SET]
for r in hag_items:
    if r['item'] != HAG_MOUNT_NODE:
        add('character_skill_node_set_items_tables', **dict(r, set=CULT_HAG_SET))
print('Cult Death Hag skill tree:', len(hag_items) - 1, 'of', len(hag_items), 'nodes (no mount)')

# --------------------------------------------------------------------------
# 18. Sacrifice to Slaanesh: what the rite does
# --------------------------------------------------------------------------
# Like CA's Dark Elf rites (Atharti, Khaine...): the completion payload applies a faction bundle for
# a number of turns (ritual_payload_effect_bundles). In it: unit-set stat effects (the same bonus
# values CA uses, scope faction_to_force_own). The parts data can't do are scripted (Lua section
# 12) while the bundle is active: extra Winds only for armies in the Channelling stance (a force
# bundle), a chance of pleasure-themed followers for lords, and the permanent allied unit cap
# (+3 per rite). Those are shown as one text-only line. Relations are data (below).
RITE_BUNDLE = 'druchii_cult_rite_slaanesh_bundle'
RITE_TURNS = 6
RITE_CHANNEL_BUNDLE = 'druchii_cult_rite_slaanesh_channelling'   # force bundle, script
RITE_ALLIED_CAP_BUNDLE = 'druchii_cult_rite_slaanesh_allied_cap'  # permanent, script
RITE_UPKEEP_SET = 'druchii_cult_rite_upkeep_units'
RITE_UPKEEP_UNITS = ['wh2_main_def_inf_witch_elves_0', 'wh3_dlc27_sla_inf_devotees_of_slaanesh',
                     'wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows', 'wh3_main_sla_inf_daemonette_0',
                     'wh3_main_sla_inf_daemonette_1']
unit_set(RITE_UPKEEP_SET, sorted(set(RITE_UPKEEP_UNITS) | set(allied_units)))

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


rite_effect('druchii_cult_rite_upkeep', 'Upkeep: %+n% for Witch Elves, Devotees, Daemonettes and allied units',
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

# Permanent allied unit cap per army ("Allied unit cap in armies", bonus allied_recruitment_unit_cap_mod;
# v1 used wh3_main_effect_recruitment_cap_allied_units, a recruitment-source limit that didn't change
# the army's allied cap): +3 per rite performed (the script sets 3 x rites on a custom copy).
add('effect_bundles_tables', **dict(template_bundle, key=RITE_ALLIED_CAP_BUNDLE, localised_title="The Dark Prince's Host",
                                    localised_description='', ui_icon='slaanesh_points.png'))
loc[f'effect_bundles_localised_title_{RITE_ALLIED_CAP_BUNDLE}'] = "The Dark Prince's Host"
loc[f'effect_bundles_localised_description_{RITE_ALLIED_CAP_BUNDLE}'] = 'Granted by the Sacrifice to Slaanesh.'
add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=RITE_ALLIED_CAP_BUNDLE,
    effect_key='wh3_main_effect_allied_recruitment_unit_cap', effect_scope='faction_to_faction_own', value=3.0,
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
