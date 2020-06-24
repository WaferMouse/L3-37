from os import path
import sys
from config import config
import cPickle
import urllib

from api_store import starcache

this = sys.modules[__name__]	# For holding module globals

with open(path.join(config.respath, 'systems.p'),  'rb') as h:
    this.system_ids  = cPickle.load(h)
    
with open(path.join(config.respath, 'stations.p'), 'rb') as h:
    this.station_ids = cPickle.load(h)

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
    
def get_system_url(system_name, provider = None):
    if not provider:
        provider = config.get('system_provider')
    if provider == 'eddb':
        system_url = EDDB_system_url(system_name)
    elif provider == 'Inara':
        try:
            system_url = 'https://inara.cz/galaxy-starsystem/' + str(starcache[system_name.lower()]['starsystemInaraID']) + '/'
        except:
            system_url = 'https://inara.cz/search/?searchglobal=' + urllib.quote_plus(system_name)
    else:
        system_url = 'https://www.edsm.net/show-system?systemName=' + urllib.quote_plus(system_name)
    return(system_url)
    
def get_station_url(system_name, station_name, provider = None):
    if not provider:
        provider = config.get('station_provider')
    if provider == 'eddb':
        station_url = EDDB_station_url(system_name, station_name)
    elif provider == 'Inara':
        try:
            station_url = 'https://inara.cz/galaxy-station/' + str(starcache[system_name.lower()]['stations'][station_name]['stationInaraID']) + '/'
        except:
            try:
                station_url = 'https://inara.cz/galaxy-starsystem/' + str(starcache[system_name.lower()]['starsystemInaraID']) + '/'
            except:
                station_url = 'https://inara.cz/search/?searchglobal=' + urllib.quote_plus(station_name)
    else:
        station_url = 'https://www.edsm.net/show-system?systemName={}&stationName={}'.format(urllib.quote_plus(system_name), urllib.quote_plus(station_name))
    return(station_url)