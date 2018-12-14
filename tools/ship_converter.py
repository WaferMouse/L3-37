import json
from os import path
from os import listdir

flat_ships = {}

SHIP_FD_NAME_TO_CORIOLIS_NAME = {
    'Adder': 'adder',
    'Anaconda': 'anaconda',
    'Asp': 'asp',
    'Asp_Scout': 'asp_scout',
    'BelugaLiner': 'beluga',
    'CobraMkIII': 'cobra_mk_iii',
    'CobraMkIV': 'cobra_mk_iv',
    'Cutter': 'imperial_cutter',
    'DiamondBackXL': 'diamondback_explorer',
    'DiamondBack': 'diamondback',
    'Dolphin': 'dolphin',
    'Eagle': 'eagle',
    'Empire_Courier': 'imperial_courier',
    'Empire_Eagle': 'imperial_eagle',
    'Empire_Trader': 'imperial_clipper',
    'Federation_Corvette': 'federal_corvette',
    'Federation_Dropship': 'federal_dropship',
    'Federation_Dropship_MkII': 'federal_assault_ship',
    'Federation_Gunship': 'federal_gunship',
    'FerDeLance': 'fer_de_lance',
    'Hauler': 'hauler',
    'Independant_Trader': 'keelback',
    'Krait_MkII': 'krait_mkii',
    'Orca': 'orca',
    'Python': 'python',
    'SideWinder': 'sidewinder',
    'Type6': 'type_6_transporter',
    'Type7': 'type_7_transport',
    'Type9': 'type_9_heavy',
    'Type9_Military': 'type_10_defender',
    'TypeX': 'alliance_chieftain',
    'TypeX_2': 'alliance_crusader',
    'TypeX_3': 'alliance_challenger',
    'Viper': 'viper',
    'Viper_MkIV': 'viper_mk_iv',
    'Vulture': 'vulture',
    'krait_light': 'krait_phantom',
    'mamba': 'mamba',
}

SHIP_CORIOLIS_NAME_TO_FD_NAME = {v: k for k, v in SHIP_FD_NAME_TO_CORIOLIS_NAME.iteritems()}

for filename in listdir('ships'):
    if filename != 'index.js':
        with open(path.join('ships', filename)) as json_data:
            this_data = json.load(json_data)
        for ship in this_data:
            this_ship = this_data[ship]
            flat_ships.update({SHIP_CORIOLIS_NAME_TO_FD_NAME[ship].lower(): {
                'hullMass': this_ship['properties']['hullMass'],
                'edID': this_ship['edID'],
                }})
                    
with open('flat_ships.json', 'w') as fp:
    json.dump(flat_ships, fp, indent = 2, sort_keys = True)