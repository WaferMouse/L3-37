import copy
import sys
from urllib import quote_plus
import threading
import requests
import json
from Queue import Queue

from collections import OrderedDict

from os import path

from config import config

this = sys.modules[__name__]	# For holding module globals

this.edsm_session = None

starcache = OrderedDict()

starstore = []

this.edsm_queue = Queue()

plugin_path = path.join(config.plugin_dir, "edmc-L3-37")

try:
    with open(path.join(plugin_path, 'starcache.json')) as json_data:
        starcache = json.load(json_data, object_pairs_hook = OrderedDict)
except:
    pass
    
def set(frame):
    this.frame = frame

def credentials(cmdr):
    # Credentials for cmdr
    if not cmdr:
        return None

    cmdrs = config.get('edsm_cmdrs')

    if cmdr in cmdrs and config.get('edsm_usernames') and config.get('edsm_apikeys'):
        idx = cmdrs.index(cmdr)
        return (config.get('edsm_usernames')[idx], config.get('edsm_apikeys')[idx])
    else:
        return None
        
def update_user_ids():
    cmdrs = config.get('edsm_cmdrs')
    if not cmdrs:
        # Migrate from <= 2.25
        #cmdrs = [cmdr]
        #config.set('edsm_cmdrs', cmdrs)
        return()
        
    for cmdr in cmdrs:
        pass
        # wip
    
    return()
    
def edsm_query(system, query_type):
    thread = threading.Thread(target = edsm_worker, name = 'EDSM worker', args = (system, query_type))
    thread.daemon = True
    thread.start()
    
def edsm_worker(systemName, query_type):
#    print("EDSM worker going!")

    if not this.edsm_session:
        this.edsm_session = requests.Session()

    try:
        if query_type == 'stations':
            r = this.edsm_session.get('https://www.edsm.net/api-system-v1/stations?systemName=' + quote_plus(systemName), timeout=10)
        else:
            r = this.edsm_session.get('https://www.edsm.net/api-v1/system?systemName=' + quote_plus(systemName) + '&showCoordinates=1&showInformation=1&showPermit=1&showPrimaryStar=1&showId=1', timeout=10)
        r.raise_for_status()
        edsm_data = r.json() or {}	# Unknown system represented as empty list
#        print("EDSM worker finished!")
    except:
#        print("Error in EDSM worker!")
        edsm_data = {}
    edsm_data.update({'query_type': query_type})
    this.edsm_queue.put(edsm_data)

    # Tk is not thread-safe, so can't access widgets in this thread.
    # event_generate() is the only safe way to poke the main thread from this thread.
    this.frame.event_generate('<<SystemData>>', when='tail')
    
def edsm_handler(event):
#    print("Probably got some EDSM data!")
    while not this.edsm_queue.empty():
        edsm_data = this.edsm_queue.get()
        #print(edsm_data)
        
        if edsm_data['query_type'] == 'stations':
            new_dict = {}
            #edsm_data['stations'] = {}
            for station in edsm_data['stations']:
                new_dict[station['name']] = station
            del edsm_data['stations']
            edsm_data['stations'] = new_dict
        else:
            edsm_data = edsm_data
        del edsm_data['query_type']
        update_cache(edsm_data)

def update_cache(data):
    system_name = data['name'].lower()
    try:
        system_entry = starcache.pop(system_name)
    except:
        system_entry = {'name': data['name']}
        
    try:
        system_entry['starsystemInaraID'] = data['starsystemInaraID']
    except:
        pass
        
    if 'stations' in data:
        if 'stations' not in system_entry:
            system_entry['stations'] = {}
        for station, value in data['stations'].iteritems():
            if station in system_entry['stations']:
                system_entry['stations'][station].update(value)
            else:
                system_entry['stations'][station] = value
    else:
        system_entry.update(data)
        
    starcache[system_name] = system_entry
    '''
    if edsm_data['query_type'] == 'system':
        request_stations = False
        try:
            if edsm_data['information'] != [] and 'stations' not in starcache[system_name]: #best guess
                request_stations = True
        except:
#            print("WHOOPS!")
            pass
            
            
        if request_stations:
            thread = threading.Thread(target = edsm_worker, name = 'EDSM worker', args = (system_name, 'stations',))
            thread.daemon = True
            thread.start()
            '''

def inara_notify_location(system, station, eventData):
    data = {'name': system}
    if station and eventData.get('stationInaraID'):
        data['stations'] = {station: {'stationInaraID': eventData.get('stationInaraID'), 'name': station}}
    if eventData.get('starsystemInaraID'):
        data['starsystemInaraID'] = eventData.get('starsystemInaraID')
    update_cache(data)
        
def plugin_stop():
    for i in starstore:
        update_cache({'name': i})
    while len(starcache) > 1000:
        starcache.popitem(last = False)
    with open(path.join(plugin_path, 'starcache.json'), 'w') as fp:
        json.dump(starcache, fp, indent = 2)