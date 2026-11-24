"""Decrees of the Witch King data for Druchii_Naggarond_MOD, written into the pack source folder.
(Internal keys still say black_council, the feature's old name; only display text was renamed.)

1. Naggarond's own Decrees of the Witch King dilemma: every 12 turns from turn 7 (triggered by
   script), choose one of four Ages, each a 12-turn faction bundle.
2. (Removed 2026-11-23.) The vanilla lord-loyalty "Black Council" dilemmas are left
   untouched, with CA's default 10-round cooldown for every Dark Elf faction.

Usage: build_black_council.py <pack source folder>
"""
import os, struct, sys, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twpack import Pack, DATA, table, encode_db, table_version, parse_loc

root = sys.argv[1]
FRAG = 'Druchii_Naggarond_MOD_decrees'
FACTION = 'wh2_main_def_naggarond'
DILEMMA = 'naggarond_mod_dilemma_black_council'

db = Pack(DATA + r'\db.pack')
loc_pack = Pack(DATA + r'\local_en.pack')
VANILLA_LOC = {}
for fn in loc_pack.files:
    if fn.endswith('.loc'):
        VANILLA_LOC.update(parse_loc(loc_pack.read(fn)))

out_tables = {}   # table name -> list of rows
loc = {}


def add(table_name, **row):
    out_tables.setdefault(table_name, []).append(row)


def new_id(text):
    """Stable 64-bit id far above vanilla's 32-bit range, so it can't collide."""
    return 7_000_000_000 + zlib.crc32(text.encode())


# --------------------------------------------------------------------------
# Effects (new display-only effects; the script does the work behind them)
# --------------------------------------------------------------------------
def effect(key, icon, priority, category, positive, text):
    add('effects_tables', effect=key, icon=icon, priority=priority, icon_negative=icon,
        category=category, is_positive_value_good=positive)
    loc[f'effects_description_{key}'] = text


effect('naggarond_mod_effect_black_council', 'loyalty.png', 99, 'campaign', True,
       'Decrees of the Witch King: from time to time, the Witch King decrees a new Age for Naggaroth, and its blessings hold for a time. Every Dark Elf faction not at war with Naggarond shares in it')
effect('naggarond_mod_effect_tithe_of_flesh', 'slaves.png', 105, 'campaign', True,
       'Tithe of Flesh: slave tribute from other Dark Elf factions raised to %n% (25% from trade partners)')
effect('naggarond_mod_effect_vengeance_loyalty', 'loyalty.png', 6, 'campaign', True,
       'On turn start, Lords in the same region as Malekith have a chance to gain loyalty')
effect('naggarond_mod_effect_torment_black_ark_xp', 'experience.png', 10, 'campaign', True,
       'Experience gain: %+n% for Black Arks and the units and characters aboard them')
effect('naggarond_mod_effect_torment_raid_slaves', 'slaves.png', 105, 'campaign', True,
       'Slaves captured while in Raiding stance: %+n%')
# Negative is the bad direction here: shown in red.
effect('naggarond_mod_effect_peace_disloyalty', 'loyalty.png', 6, 'campaign', False,
       'Each turn, %n% chance that one of your [[img:icon_general]][[/img]]Lords loses 1 loyalty')

# --------------------------------------------------------------------------
# Bundles
# --------------------------------------------------------------------------
STAGE = 'start_turn_completed'


def bundle(key, title, description, target, icon, effects, is_global=True):
    add('effect_bundles_tables', key=key, localised_description=description, localised_title=title,
        bundle_target=target, priority=1, ui_icon=icon, is_global_effect=is_global,
        show_in_3d_space=False, owner_only=True)
    loc[f'effect_bundles_localised_title_{key}'] = title
    loc[f'effect_bundles_localised_description_{key}'] = description
    for effect_key, scope, value in effects:
        add('effect_bundles_to_effects_junctions_tables', effect_bundle_key=key, effect_key=effect_key,
            effect_scope=scope, value=value, advancement_stage=STAGE)


AGES = [
    ('naggarond_mod_age_debauchery', 'An Age of Debauchery',
     'Naggaroth drowns in excess. The tribute of the lesser cities flows into Naggarond, and its '
     'cities swell with slaves, courtiers and supplicants hungry for the Witch King\'s favour.',
     'slaves.png', [
         ('naggarond_mod_effect_tithe_of_flesh', 'faction_to_faction_own_unseen', 20),
         ('wh_main_effect_province_growth_events', 'faction_to_province_own', 20),
         ('wh_main_effect_agent_action_cost_mod', 'faction_to_character_own_unseen', -25),
         ('wh3_main_effect_corruption_slaanesh_events', 'faction_to_province_own', 3),
         ('wh2_main_faction_political_diplomacy_mod_dark_elves', 'faction_to_faction_own_unseen', -10),
     ]),
    ('naggarond_mod_age_vengeance', 'An Age of Vengeance',
     'Ulthuan will burn. The Witch King\'s hatred for the usurpers of his throne sharpens every blade '
     'in Naggaroth, and those who fight at his side rise swiftly in his esteem.',
     'military_spending.png', [
         ('wh2_main_effect_force_stat_melee_attack_vs_high_elves', 'faction_to_force_own', 6),
         ('wh2_dlc10_effect_force_stat_weapon_strength_vs_high_elves', 'faction_to_force_own', 10),
         ('wh2_main_effect_force_stat_leadership_vs_high_elves', 'faction_to_force_own', 10),
         ('wh3_main_effect_character_campaign_experience_mod', 'faction_to_character_own', 25),
         ('naggarond_mod_effect_vengeance_loyalty', 'faction_to_faction_own_unseen', 2),
         # Naggarond only (left out of the decree bundles below).
         ('wh2_main_faction_political_diplomacy_mod_dark_elves', 'faction_to_faction_own_unseen', 10),
     ]),
    ('naggarond_mod_age_glorious_torment', 'An Age of Glorious Torment',
     'The Black Arks sail forth from Naggaroth, and their holds fill with screaming cargo. Let the '
     'coasts of the world know the terror of the Druchii.',
     'slaves.png', [
         ('wh_main_effect_force_all_campaign_raid_income', 'faction_to_force_own_unseen', 30),
         ('naggarond_mod_effect_torment_raid_slaves', 'faction_to_faction_own_unseen', 30),
         ('naggarond_mod_effect_torment_black_ark_xp', 'faction_to_faction_own_unseen', 20),
         ('wh2_dlc11_effect_blackark_growth_char', 'faction_to_force_own_unseen', 5),
         ('wh3_dlc27_effect_force_army_campaign_movement_range_at_sea', 'faction_to_force_own', 10),
     ]),
    ('naggarond_mod_age_hateful_peace', 'An Age of Hateful Peace',
     'The war-drums fall silent, for now. Slaves raise new towers across Naggaroth and the coffers '
     'swell, but idle Dreadlords begin to scheme against the throne.',
     'treasury.png', [
         ('wh_main_effect_building_construction_cost_mod', 'faction_to_region_own_unseen', -15),
         ('wh2_main_effect_building_construction_time_mod_all', 'faction_to_region_own_unseen', -25),
         ('wh_main_effect_economy_gdp_mod_all', 'faction_to_region_own', 15),
         ('wh_main_effect_economy_trade_tariff_mod', 'faction_to_faction_own', 15),
         ('wh_main_effect_province_growth_events', 'faction_to_province_own', 10),
         ('naggarond_mod_effect_peace_disloyalty', 'faction_to_faction_own_unseen', 20),
     ]),
]
effect('naggarond_mod_effect_decree_shared', 'diplomacy.png', 1, 'campaign', True,
       'This Age is also decreed to every Dark Elf faction not at war with Naggarond')
for key, title, description, icon, effects in AGES:
    bundle(key, title, description, 'faction', icon,
           effects + [('naggarond_mod_effect_decree_shared', 'faction_to_faction_own_unseen', 1)])

# --------------------------------------------------------------------------
# The same Ages as decreed to the other Dark Elf factions not at war with Naggarond
# (applied by script; human players also get an incident popup listing the effects).
# Left out for them: the Tithe of Flesh, every loyalty effect, Malekith's aura (never
# applied to them by the script) and Vengeance's Naggarond-only diplomacy bonus.
# --------------------------------------------------------------------------
NAGGAROND_ONLY = {
    ('naggarond_mod_age_debauchery', 'naggarond_mod_effect_tithe_of_flesh'),
    ('naggarond_mod_age_debauchery', 'wh2_main_faction_political_diplomacy_mod_dark_elves'),
    ('naggarond_mod_age_vengeance', 'naggarond_mod_effect_vengeance_loyalty'),
    ('naggarond_mod_age_vengeance', 'wh2_main_faction_political_diplomacy_mod_dark_elves'),
    ('naggarond_mod_age_hateful_peace', 'naggarond_mod_effect_peace_disloyalty'),
}
INCIDENT_IMAGES = {
    'naggarond_mod_age_debauchery': 'celebration',
    'naggarond_mod_age_vengeance': 'army_morale_up',
    'naggarond_mod_age_glorious_torment': 'politics',
    'naggarond_mod_age_hateful_peace': 'court_intrigue_1',
}
for key, title, description, icon, effects in AGES:
    decree = key + '_decree'
    bundle(decree, f'Decree of the Witch King: {title}',
           f'By decree of the Witch King, all Druchii loyal to Naggarond enter {title[0].lower() + title[1:]}. '
           + description, 'faction', icon,
           [e for e in effects if (key, e[0]) not in NAGGAROND_ONLY])

    incident = 'naggarond_mod_incident_decree_' + key.replace('naggarond_mod_age_', '')
    add('incidents_tables', generate=False, key=incident, ui_image=INCIDENT_IMAGES[key], prioritised=False,
        event_category='Event', override_icon='', is_large_incident=False, additional_sound_event='',
        sepia_fade=1.0, use_revealing_text=False)
    loc[f'incidents_localised_title_{incident}'] = 'Decree of the Witch King'
    loc[f'incidents_localised_description_{incident}'] = (
        f'The Black Council has knelt before the throne of Naggarond, and the Witch King has spoken: '
        f'Naggaroth shall enter {title[0].lower() + title[1:]}. All Druchii not at war with Naggarond '
        f'are bound by his decree.')
    loc[f'incidents_button_text_{incident}'] = 'As the Witch King commands'
    add('cdir_events_incident_payloads_tables', id=new_id(incident + 'payload'), incident_key=incident,
        payload_key='EFFECT_BUNDLE', value=f'KEY[{decree}];DURATION[12]', target_key='default')
    for option, value in [('GEN_TARGET_NONE', ''), ('VAR_CHANCE', '100')]:
        add('cdir_events_incident_option_junctions_tables', id=new_id(incident + option), incident_key=incident,
            option_key=option, value=value, target='default')

# Applied by script to Malekith while the Age of Vengeance lasts (the effect needs a character source).
bundle('naggarond_mod_age_vengeance_malekith', 'An Age of Vengeance',
       'Those who fight at the Witch King\'s side rise swiftly in his esteem.', 'character', 'character.png',
       [('wh2_main_effect_character_mod_loyalty_regional', 'character_to_character_regionwide_local_region', 2)],
       is_global=False)
# Applied by script to each Black Ark while the Age of Glorious Torment lasts (so only Black Arks get the XP).
bundle('naggarond_mod_age_glorious_torment_black_ark', 'An Age of Glorious Torment',
       'Those who sail aboard the Black Ark learn the arts of war and torment swiftly.', 'force',
       'experience.png',
       [('wh3_dlc20_effect_xp_gain_all_units', 'force_to_force_own', 20),
        ('wh3_main_effect_character_campaign_experience_mod', 'force_to_character_own', 20)],
       is_global=False)

# --------------------------------------------------------------------------
# The Decrees of the Witch King dilemma (script-triggered, same footprint as CA's scripted dilemmas)
# --------------------------------------------------------------------------
TITLE = 'Decrees of the Witch King'
DESCRIPTION = ('Dreadlords, Sorceresses and Beastmasters kneel before the throne of Naggarond, and await '
               'the Witch King\'s decree. What Age shall Naggaroth enter?')
add('dilemmas_tables', generate=False, key=DILEMMA, localised_description=DESCRIPTION, localised_title=TITLE,
    ui_image='politics', prioritized=False, event_category='Event', sound_popup_override='UI_CAM_EVENT_Dilemma',
    sound_click_override='', override_icon='', is_large_dilemma=False)
loc[f'dilemmas_localised_title_{DILEMMA}'] = TITLE
loc[f'dilemmas_localised_description_{DILEMMA}'] = DESCRIPTION

CHOICE_TEXT = [
    'Let the lesser cities send their tithe of flesh, and let the court feast on it.',
    'Ulthuan must fall! Every blade in Naggaroth shall be turned against the usurpers.',
    'Launch the Black Arks! Let the coasts of the world fill their holds with slaves.',
    'Let the slaves build and the raiders take their due, while the armies rest.',
]
for choice, (key, title, _desc, _icon, _effects), text in zip(['FIRST', 'SECOND', 'THIRD', 'FOURTH'], AGES, CHOICE_TEXT):
    add('cdir_events_dilemma_choice_details_tables', choice_key=choice, dilemma_key=DILEMMA,
        audio_event_hover='', audio_choice_vo='')
    add('cdir_events_dilemma_payloads_tables', choice_key=choice, dilemma_key=DILEMMA,
        id=new_id(DILEMMA + choice), payload_key='EFFECT_BUNDLE', value=f'KEY[{key}];DURATION[12]',
        target_key='default')
    loc[f'cdir_events_dilemma_choice_details_localised_choice_label_{DILEMMA}{choice}'] = title
    loc[f'cdir_events_dilemma_choice_details_localised_choice_title_{DILEMMA}{choice}'] = text

for option, value in [('VAR_CHANCE', '100'), ('GEN_TARGET_NONE', '')]:
    add('cdir_events_dilemma_option_junctions_tables', dilemma_key=DILEMMA, id=new_id(DILEMMA + option),
        option_key=option, value=value, target='default')

# --------------------------------------------------------------------------
# Custom slave factor for the Age of Glorious Torment raiding bonus
# --------------------------------------------------------------------------
add('pooled_resource_factors_tables', key='naggarond_torment_raiding', is_hidden=False)
add('pooled_resource_factor_junctions_tables', unique_id='def_slaves_naggarond_torment_raiding',
    factor='naggarond_torment_raiding', resource='def_slaves', minimum=0, maximum=2147483647,
    specific_faction_set='', sort_order=0)
for sign in ['positive', 'negative']:
    loc[f'pooled_resource_factors_display_name_{sign}_naggarond_torment_raiding'] = 'Raiding (Age of Glorious Torment)'

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
print('black council data:', {t: len(r) for t, r in out_tables.items()}, len(loc), 'loc entries')
