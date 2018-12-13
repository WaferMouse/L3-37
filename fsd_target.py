import Tkinter as tk
from urlparse import urlparse
import webbrowser
from urllib import quote_plus
from wafer_module import WaferModule
import threading
import requests

from os import path

import json
import urllib

from web_handlers import *

from ttkHyperlinkLabel import HyperlinkLabel
from config import config
from os.path import join
import cPickle
import sys

theme = config.getint('theme')
fg = config.get('dark_text') if theme else 'black'
hl = config.get('dark_highlight') if theme else 'blue'
bg = 'grey4' if theme else 'grey'

# https://www.edsm.net/api-v1/system?systemName=Shinrarta%20Dezhra&showCoordinates=1&showInformation=1&showPermit=1&showPrimaryStar=1
# https://www.edsm.net/api-system-v1/stations?systemName=Robigo
# https://www.edsm.net/api-system-v1/bodies?systemName=Shinrarta%20Dezhra

# https://github.com/EDSM-NET/EDDN-Events/blob/master/Station/Services.php et al
# https://github.com/EDSM-NET/Alias

plugin_path = path.join(config.plugin_dir, "edmc-L3-37")

this = sys.modules[__name__]	# For holding module globals

this.edsm_cache = {}

this.edsm_session = None
this.edsm_data = None

class TwoPartLabel(tk.Frame):
    
    def __init__(self, parent, label_name, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        self.label = tk.Label(self, text = label_name)
        self.label.pack(side = 'left')
        self.inner = tk.Frame()
        self.inner.pack(side = 'left')

with open(join(config.respath, 'systems.p'),  'rb') as h:
    this.system_ids  = cPickle.load(h)

def test_stuff():
    o = 'Shinrarta Dezhra'
#    disassembled = urlparse(o)
#    url, scrap = path.splitext(path.basename(disassembled.path))
    url = 'https://www.edsm.net/api-system-v1/stations?systemName=' + quote_plus(o)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    with open(path.join(plugin_path, 'TEST_OUT.json'), 'w') as fp:
        json.dump(data, fp, indent = 2, sort_keys=True)
        
def edsm_worker(systemName, query_type):
#    print("EDSM worker going!")

    if not this.edsm_session:
        this.edsm_session = requests.Session()

    try:
        if query_type == 'stations':
            r = this.edsm_session.get('https://www.edsm.net/api-system-v1/stations?systemName=' + quote_plus(systemName), timeout=10)
        else:
            r = this.edsm_session.get('https://www.edsm.net/api-v1/system?systemName=' + quote_plus(systemName) + '&showCoordinates=1&showInformation=1&showPermit=1&showPrimaryStar=1', timeout=10)
        r.raise_for_status()
        this.edsm_data = r.json() or {}	# Unknown system represented as empty list
        if this.edsm_data == {}:
            this.edsm_data.update({
                'name': systemName,
                'result': 'unknown system'
                })
        this.edsm_data.update({'query_type': query_type})
#        print("EDSM worker finished!")
    except:
#        print("Error in EDSM worker!")
        this.edsm_data = None

    # Tk is not thread-safe, so can't access widgets in this thread.
    # event_generate() is the only safe way to poke the main thread from this thread.
    this.frame.event_generate('<<FSDData>>', when='tail')
    
def setclipboard(text):
    r = tk.Tk()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.destroy()

def get_edsm_data(system_name):
    this.loading.pack()
    thread = threading.Thread(target = edsm_worker, name = 'EDSM worker', args = (system_name, 'stations',)) #will need to change this later
    thread.daemon = True
    thread.start()

def edsm_handler(event):
#    print("Probably got some EDSM data!")
    if this.edsm_data is None:
        # error
        return()
    data = this.edsm_data
    system_name = data['name']
        
    if system_name not in this.edsm_cache:
        this.edsm_cache[system_name] = {}
            
    if data['query_type'] == 'system':
        this.edsm_cache[system_name].update(data)
        request_stations = False
        try:
            if data['information'] != []: #best guess
                request_stations = True
        except:
#            print("WHOOPS!")
            pass
            
        if request_stations:
            thread = threading.Thread(target = edsm_worker, name = 'EDSM worker', args = (system_name, 'stations',))
            thread.daemon = True
            thread.start()
        else:
            this.loading.forget()
            
    if data['query_type'] == 'stations':
        this.edsm_cache[system_name]['stations'] = data['stations']
#        print("EDSM download complete!")
        this.loading.forget()
        if this.system_string == system_name:
            display_results(system_name)

class StationFrame(tk.Frame):
    
    def __init__(self, parent, station_data, system_name, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        
        self.config(background = bg)
        self.station_data = station_data
        
        if 'Planetary' in station_data['type']:
            type_abr = '[P]'
        elif 'outpost' in station_data['type'].lower():
            type_abr = '[O]'
        else:
            type_abr = ''
        
        facilities_abr = type_abr + ['','M'][station_data['haveMarket']] + ['','S'][station_data['haveShipyard']] + ['','O'][station_data['haveOutfitting']]
        facilities_abr = facilities_abr + '+{}'.format(len(station_data['otherServices']))
        label_text = '{} ({}ls) {}'.format(station_data['name'], int(station_data['distanceToArrival']), facilities_abr)
        self.name_lbl = HyperlinkLabel(self, compound=tk.RIGHT, url = get_station_url(system_name, station_data['name']), text = label_text, background = bg, foreground = hl)
        self.name_lbl.pack(side = 'left')

def display_results(system_string):
    try:
        this.edsm_data_frame.destroy()
    except:
        pass
    this.edsm_data_frame = tk.Frame(this.frame)
    this.edsm_data_frame.config(background = bg)
    this.edsm_data_frame.pack(fill = tk.Y, anchor = 'w')
    data = this.edsm_cache[system_string]
    for i in data['stations']:
        StationFrame(this.edsm_data_frame, i, system_string, background = bg).pack(fill = tk.Y, anchor = 'w')

class FSDTarget(WaferModule):
    
    def __init__(self, parent, *args, **options):
        WaferModule.__init__(self, parent, *args, **options)
        #test_stuff()
        self.system_url = None
        self.system_string = ''
        self.system_frm = tk.Frame(self)
        self.system_frm.pack(fill = tk.Y, anchor = 'w')
        self.system_lbl = tk.Label(self.system_frm, text = 'Target system: ')
        self.system_lbl.pack(side = 'left')
        self.system_hyperlink = HyperlinkLabel(self.system_frm, compound=tk.RIGHT, url = self.system_url, name = 'system', text = '')
        self.system_hyperlink.pack(side = 'left')
        self.system_hyperlink.bind("<Button-3>", self.rightclick)
        this.frame = tk.Frame(self)
        this.frame.bind('<<FSDData>>', edsm_handler)
        this.frame.pack(fill=tk.Y, anchor = 'w')
        this.edsm_button = tk.Button(this.frame, text = 'Request data', command = self.get_data)
#        this.edsm_button.pack()
        this.loading = tk.Label(this.frame, text = "Contacting EDSM...")
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Copy", command = self.copy_system)
        this.system_string = self.system_string
        # more test stuff
        #self.system_hyperlink.config(text = 'Shinrarta Dezhra')
        #self.system_string = 'Shinrarta Dezhra'
        #self.update_link()
        
    def get_data(self):
        this.edsm_button.forget()
        get_edsm_data(self.system_string)

    def journal_entry(self, cmdr, system, station, entry, state):
        if entry['event'] == 'FSDTarget':
            if entry['Name'] != self.system_string:
                try:
                    this.edsm_data_frame.destroy()
                except:
                    pass
                self.system_string = entry['Name']
                this.system_string = self.system_string
                self.system_hyperlink.config(text = self.system_string)
                self.update_link()
                if self.system_string not in this.edsm_cache:
                    try:
                        this.edsm_button.pack()
                    except:
                        pass
                else:
                    try:
                        this.edsm_button.forget()
                    except:
                        pass
                    display_results(self.system_string)
                    

    def update_link(self):
        self.system_url = get_system_url(self.system_string)
        self.system_hyperlink.configure(url = self.system_url)
        
    def rightclick(self, event):
        self.menu.post(event.x_root, event.y_root)
        
    def copy_system(self):
        setclipboard(self.system_string)