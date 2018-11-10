from os import path
import sys
from config import config
import cPickle

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