import json
from os import path
from os import listdir

flat_modules = {}

for type in ['hardpoints', 'internal', 'standard']:
    for filename in listdir(type):
        with open(path.join(type, filename)) as json_data:
            this_data = json.load(json_data)
        for module_type in this_data:
            for imodule in this_data[module_type]:
                if module_type in ['fsd', 'gfsb']:
                    flat_modules.update({imodule['symbol'].lower(): imodule})
                else:
                    if 'mass' in imodule:
                        flat_modules.update({imodule['symbol'].lower(): {'mass': imodule['mass']}})
                    if 'fuel' in imodule:
                        flat_modules.update({imodule['symbol'].lower(): {'fuel': imodule['fuel']}})
                    if 'cargo' in imodule:
                        flat_modules.update({imodule['symbol'].lower(): {'cargo': imodule['cargo']}})
                    
with open('flat_modules.json', 'w') as fp:
    json.dump(flat_modules, fp, indent = 2, sort_keys = True)