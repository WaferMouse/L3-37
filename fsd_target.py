import Tkinter as tk
from urlparse import urlparse
import webbrowser
from urllib import quote_plus
from wafer_module import WaferModule

from ttkHyperlinkLabel import HyperlinkLabel
from config import config
from os.path import join
import cPickle
import sys

# https://www.edsm.net/api-v1/system?systemName=Shinrarta%20Dezhra&showCoordinates=1&showInformation=1&showPermit=1&showPrimaryStar=1
# https://www.edsm.net/api-system-v1/stations?systemName=Robigo

this = sys.modules[__name__]	# For holding module globals

with open(join(config.respath, 'systems.p'),  'rb') as h:
    this.system_ids  = cPickle.load(h)

def EDDB_system_url(system_name):
    if EDDB_system_id(system_name):
        return 'https://eddb.io/system/%d' % EDDB_system_id(system_name)
    else:
        return None

def EDDB_system_id(system_name):
    return this.system_ids.get(system_name, [0, False])[0]
    
def setclipboard(text):
    r = tk.Tk()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.destroy()

class FSDTarget(WaferModule):
    
    def __init__(self, parent, *args, **options):
        WaferModule.__init__(self, parent, *args, **options)
        self.system_url = None
        self.system_string = ''
        self.system_lbl = tk.Label(self, text = 'Targeted system: ')
        self.system_lbl.pack(side = tk.LEFT)
        self.system_hyperlink = HyperlinkLabel(self, compound=tk.RIGHT, url = self.system_url, name = 'system', text = '')
        self.system_hyperlink.pack(side=tk.LEFT)
        self.system_hyperlink.bind("<Button-3>", self.rightclick)
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Copy", command = self.copy_system)

    def journal_entry(self, cmdr, system, station, entry, state):
        if entry['event'] == 'FSDTarget':
            self.system_string = entry['Name']
            self.system_hyperlink.config(text = self.system_string)
            self.update_link()

    def update_link(self):
        if config.get('system_provider') == 'eddb':
            self.system_url = EDDB_system_url(self.system_string)
        else:
            self.system_url = 'https://www.edsm.net/show-system?systemName=' + quote_plus(self.system_string)
        self.system_hyperlink.configure(url = self.system_url)
        
    def rightclick(self, event):
        self.menu.post(event.x_root, event.y_root)
        
    def copy_system(self):
        setclipboard(self.system_string)