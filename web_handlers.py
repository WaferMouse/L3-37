from config import config
import urllib
    
def get_system_url(system_name, provider = None):
    if not provider:
        provider = config.get('L3_system_provider')
        if provider == 'none':
            provider = config.get('system_provider')
    if provider == 'eddb':
        return('https://eddb.io/system/name/' + urllib.parse.quote_plus(system_name))
    elif provider == 'Inara':
        return('https://inara.cz/galaxy-starsystem/?search=' + urllib.parse.quote_plus(system_name))
    else:
        return('https://www.edsm.net/show-system?systemName=' + urllib.parse.quote_plus(system_name))
    
def get_nearest_url(system_name):
    return('https://inara.cz/galaxy-nearest-stations/?ps1=' + urllib.parse.quote_plus(system_name))
    
def get_station_url(system_name, station_name, provider = None, market_id = None):
    if not provider:
        provider = config.get('L3_station_provider')
        if provider == 'none':
            provider = config.get('station_provider')
    if provider == 'eddb':
        if market_id:
            return('https://eddb.io/station/market-id/' + urllib.parse.quote_plus(str(market_id)))
        else:
            return(get_system_url(system_name, provider = 'eddb'))
    elif provider == 'Inara':
        return('https://inara.cz/galaxy-station/?search={}%20[{}]'.format(urllib.parse.quote_plus(system_name), urllib.parse.quote_plus(station_name)))
    else:
        return('https://www.edsm.net/show-system?systemName={}&stationName={}'.format(urllib.parse.quote_plus(system_name), urllib.parse.quote_plus(station_name)))