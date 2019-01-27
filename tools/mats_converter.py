import json
from os import path

from collections import OrderedDict

with open('weirdo.json') as json_data:
    weirdo = json.load(json_data)
    
with open('mat_trader.json') as json_data:
    trader_map = json.load(json_data, object_pairs_hook=OrderedDict)
    
with open('mat_trader.json', 'w') as fp:
    json.dump(trader_map, fp, indent = 2)
    
with open('blueprints.json') as json_data:
    blueprints = json.load(json_data)
    
output = {}

def list_of_pairs_to_dict(thislist):
    output = {}
    for i in thislist:
        output.update({str(i[0]): i[1]})
    return(output)
        
def reverse_dict(thisdict):
    return({v: k for k, v in thisdict.iteritems()})

manufactured_ids = []

for i in weirdo['mat']['mat_isManufactured']:
    manufactured_ids.append(str(i[0]))
    
print(manufactured_ids)

materials = {}
mat_aliases = {}

for cat in ['encoded', 'raw', 'manufactured']:
    materials[cat] = {}
    mat_aliases[cat] = {}

for EDSM_cat in ['data', 'mat']:
    id_to_names = list_of_pairs_to_dict(weirdo[EDSM_cat][EDSM_cat+'_name'])
    names_to_id = reverse_dict(id_to_names)
    aliases_to_id = list_of_pairs_to_dict(weirdo[EDSM_cat][EDSM_cat+'_alias'])
    grades = list_of_pairs_to_dict(weirdo[EDSM_cat][EDSM_cat+'_grade'])
    for k, v in names_to_id.iteritems():
        if EDSM_cat == 'data':
            cat = 'encoded'
        else:
            cat = 'manufactured' if v in manufactured_ids else 'raw'
        materials[cat][k] = {
            'name_local': k, #future-proof-ish
            'grade': grades[v],
            'subcat': None,
            'tradeable': False,
            'aliases': [],
            }
    for k, v in aliases_to_id.iteritems():
        if EDSM_cat == 'data':
            cat = 'encoded'
        else:
            cat = 'manufactured' if str(v) in manufactured_ids else 'raw'
        name = id_to_names[str(v)]
        materials[cat][name]['aliases'].append(k)
        mat_aliases[cat][k] = name
        
for cat in ['encoded', 'raw', 'manufactured']:
    for k, v in trader_map[cat].iteritems():
        print(k.upper())
        grade = 0
        for i in v:
            name = i
            materials[cat][name].update({
                'subcat': k,
                'tradeable': True
                })
    for k, v in materials[cat].iteritems():
        if v['tradeable'] == False: print(k+' '+str(v['grade']))
    print(materials[cat])
    print()
    print()
    
for k, bp in blueprints.iteritems():
    for k1, grade in bp['grades'].iteritems():
        for k2, v in grade['components'].iteritems():
            found = False
            for cat in ['encoded', 'raw', 'manufactured']:
                if k2 in materials[cat]:
                    found = True
            if not found:
                print('{} is missing!'.format(k2))
                
with open('materials.json', 'w') as fp:
    json.dump(materials, fp, indent = 2)
    
with open('mat_alias.json', 'w') as fp:
    json.dump(mat_aliases, fp, indent = 2)