import sys
from urllib import quote_plus
import threading
import requests
import json
from Queue import Queue

from os import path

from config import config

this = sys.modules[__name__]	# For holding module globals

starcache = {}

this.edsm_queue = Queue()

plugin_path = path.join(config.plugin_dir, "edmc-L3-37")

try:
    with open(path.join(plugin_path, 'starcache.json')) as json_data:
        starcache = json.load(json_data)
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
    
def edsm_query(system):
    thread = threading.Thread(target = edsm_worker, name = 'EDSM worker', args = (system_name, 'system',))
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
        data = this.edsm_queue.get()
        system_name = data['name'].lower()
        
        if data['query_type'] == 'stations':
            edsm_data = data
            del edsm_data['stations']
            edsm_data['stations'] = {}
            for station in data['stations']:
                edsm_data['stations'][station['name']] = station
        else:
            edsm_data = data
        del edsm_data['query_type']
            
        if system_name not in starcache:
            starcache[system_name] = edsm_data
        else:
            starcache[system_name].update(edsm_data)
                
        if data['query_type'] == 'system':
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
        
def inara_notify_location(system, station, eventData):
    if system.lower() not in starcache:
        starcache[system.lower()] = {}
    if station != None and eventData.get('stationInaraURL'):
        if 'stations' not in starcache[system.lower()]:
            starcache[system.lower()]['stations'] = {}
        if station not in starcache[system.lower()]['stations']:
            starcache[system.lower()]['stations'][station] = {}
        starcache[system.lower()]['stations'][station]['stationInaraURL'] = eventData.get('stationInaraURL')
    if eventData.get('starsystemInaraURL'):
        starcache[system.lower()]['starsystemInaraURL'] = eventData.get('starsystemInaraURL')
        
def plugin_stop():
    with open(path.join(plugin_path, 'starcache.json'), 'w') as fp:
        json.dump(starcache, fp, indent = 2, sort_keys=True)