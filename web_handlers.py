from os import path
import sys
from config import config
import pickle
import urllib

this = sys.modules[__name__]	# For holding module globals

with open(path.join(config.respath, 'systems.p'),  'rb') as h:
    this.system_ids  = pickle.load(h)
    
with open(path.join(config.respath, 'stations.p'), 'rb') as h:
    this.station_ids = pickle.load(h)

def EDDB_system_url(system_name):
    if EDDB_system_id(system_name):
        return 'https://eddb.io/system/%d' % EDDB_system_id(system_name)
    else:
        return None

def EDDB_station_url(system_name, station_name):
    if EDDB_station_id(system_name, station_name):
        return 'https://eddb.io/station/%d' % EDDB_station_id(system_name, station_name)
    else:
        return EDDB_system_url(system_name)

def EDDB_system_id(system_name):
    return this.system_ids.get(system_name, [0, False])[0]
    
def EDDB_station_id(system_name, station_name):
    return this.station_ids.get((EDDB_system_id(system_name), station_name), 0)
    
def get_system_url(system_name):
    if config.get('system_provider') == 'eddb':
        system_url = EDDB_system_url(system_name)
    elif config.get('system_provider') == 'Inara':
        system_url = 'https://inara.cz/search/?searchglobal=' + urllib.parse.quote_plus(system_name)
    else:
        system_url = 'https://www.edsm.net/show-system?systemName=' + urllib.parse.quote_plus(system_name)
    return(system_url)
    
def get_station_url(system_name, station_name):
    if config.get('station_provider') == 'eddb':
        station_url = EDDB_station_url(system_name, station_name)
    elif config.get('station_provider') == 'Inara':
        station_url = 'https://inara.cz/search/?searchglobal=' + urllib.parse.quote_plus(station_name)
    else:
        station_url = 'https://www.edsm.net/show-system?systemName={}&stationName={}'.format(urllib.parse.quote_plus(system_name), urllib.parse.quote_plus(station_name))
    return(station_url)