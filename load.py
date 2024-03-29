try:
    # Python 2
    import Tkinter as tk
except ModuleNotFoundError:
    # Python 3
    import tkinter as tk
from config import config
import myNotebook as nb
import traceback

import sys

this = sys.modules[__name__]	# For holding module globals

from chat_viewer import ChatViewer
from fsd_target import FSDTarget
from mats_helper import MatsHelper
from fleet_monitor import FleetMonitor
from surface_navigation import SurfaceNavigation
from neutron_navigation import NeutronNavigation

class FakeNotebook(tk.Frame):
    
    def __init__(self, parent, text = '', *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        
        self.current = 0
        self.tabs = []
        
        self.menu = tk.Menu(self, tearoff=0)
        
        self.label_frame = tk.Frame(self)
        
        self.combo_frame = tk.Frame(self.label_frame, relief = tk.SUNKEN, borderwidth = 1)
        
        self.lbl = tk.Label(self.label_frame, text = text)
        self.lbl.pack(side=tk.LEFT)
        
        self.fake_combo = tk.Button(self.combo_frame, text = '', command = self.popup, padx = 0, pady = 0, relief = tk.FLAT, borderwidth=0)
        self.fake_combo2 = tk.Button(self.combo_frame, text = chr(11206), command = self.popup, padx = 0, pady = 0) #chr(9660)
        self.combo_frame.pack(fill=tk.BOTH)
        self.label_frame.pack(fill=tk.BOTH)
        self.fake_combo.pack(fill=tk.BOTH, side = tk.LEFT, expand = 1)
        self.fake_combo2.pack(side=tk.LEFT)
        
    def popup(self, event=''):
        self.menu.post(self.fake_combo.winfo_rootx(), self.fake_combo.winfo_rooty()+self.fake_combo.winfo_height())
        
    def add(self, tab, text):
        self.tabs.append([tab, text])
        if len(self.tabs) == 1:
            self.refresh()
            
        self.menu.delete(0, tk.END)
        n = 0
        for i in self.tabs:
            self.menu.add_command(label=i[1], command=lambda x=n: self.select_tab(x))
            n = n + 1
            
    def select_tab(self, tab):
        self.current = tab
        self.refresh()
            
    def refresh(self):
        self.fake_combo.config(text = self.tabs[self.current][1])
        for i in self.tabs:
            i[0].forget()
            
        self.tabs[self.current][0].pack(side=tk.LEFT, fill = tk.BOTH, expand = 1)

def plugin_start3(plugin_dir):
    """
    Load this plugin into EDMC
    """
    try:
        config.get_str('L3_shipyard_provider')
    except:
        config.set('L3_shipyard_provider','EDSM')
    try:
        config.get_str('L3_system_provider')
    except:
        config.set('L3_system_provider','none')
    try:
        config.get_str('L3_station_provider')
    except:
        config.set('L3_station_provider','none')
    try:
        config.get_str('EDSM_id')
    except:
        config.set('EDSM_id', '')
    print("L3-37 started")
    return "L3-37"

def plugin_app(parent):
    """
    Create a TK widget for the EDMC main window
    """
    plugin_app.wafer_module_classes = [
        ['Surface navigation', SurfaceNavigation],
        ['Neutron navigation', NeutronNavigation],
        ['Fleet', FleetMonitor],
        ['Chat', ChatViewer],
        ['Long range scanner', FSDTarget],
        ['Materials helper',MatsHelper],
        ]
    plugin_app.wafer_modules = {}
    plugin_app.frame = FakeNotebook(parent, text = 'L3-37')
    plugin_app.theme = config.get_int('theme')
    plugin_app.fg = config.get_str('dark_text') if plugin_app.theme else 'black'
    plugin_app.hl = config.get_str('dark_highlight') if plugin_app.theme else 'blue'
    plugin_app.bg = 'grey4' if plugin_app.theme else None
    for module in plugin_app.wafer_module_classes:
        plugin_app.wafer_modules[module[0]] = module[1](plugin_app.frame, highlightbackground=plugin_app.fg, highlightcolor=plugin_app.fg, highlightthickness = 1)#, relief = tk.SUNKEN, borderwidth = 1)
        plugin_app.frame.add(plugin_app.wafer_modules[module[0]], module[0])
    print("L3-37 loaded")
    return (plugin_app.frame)
    
def plugin_prefs(parent, cmdr, is_beta):
    service_providers = [
                        ['none', 'None'],
                        ['eddb', 'EDDB'],
                        ['edsm', 'EDSM'],
                        ['Inara', 'Inara'],
                        ]
    frame = nb.Frame(parent)
    row = 0
    system_frame = nb.Frame(frame, relief = tk.GROOVE)
    system_provider_label = nb.Label(system_frame, text="System information provider override: ", justify = tk.LEFT)
    system_provider_label.grid(column = 0, row = row, pady = 2, padx = 2)
    row = row + 1
    this.system_provider_select = tk.StringVar()
    for mode in service_providers:
        b = nb.Radiobutton(system_frame, text=mode[1], variable=this.system_provider_select, value=mode[0])
        b.grid(column = 0, row = row, sticky="W", padx = 1)
        row = row + 1
    b.grid_configure(pady = 2)
    try:
        this.system_provider_select.set(config.get_str('L3_system_provider'))
    except:
        this.system_provider_select.set("none")
    system_frame.grid(sticky = "nsew")
    row = 0
    station_frame = nb.Frame(frame, relief = tk.GROOVE)
    station_provider_label = nb.Label(station_frame, text="Station information provider override: ", justify = tk.LEFT)
    station_provider_label.grid(column = 0, row = row, pady = 2, padx = 2)
    row = row + 1
    this.station_provider_select = tk.StringVar()
    try:
        this.station_provider_select.set(config.get_str('L3_station_provider'))
    except:
        this.station_provider_select.set("none")
    for mode in service_providers:
        b = nb.Radiobutton(station_frame, text=mode[1], variable=this.station_provider_select, value=mode[0])
        b.grid(column = 0, row = row, sticky="W", padx = 1)
        row = row + 1
        b.grid_configure(pady = 2)
        station_frame.grid(sticky = "nsew")
        
    shipyard_frame = nb.Frame(frame, relief = tk.GROOVE)
    shipyard_provider_label = nb.Label(shipyard_frame, text="Fleet information provider: ", justify = tk.LEFT)
    shipyard_provider_label.grid(column = 2, row = 0, pady = 2)
    this.shipyard_provider_select = tk.StringVar()
    try:
        this.shipyard_provider_select.set(config.get_str('L3_shipyard_provider'))
    except:
        this.shipyard_provider_select.set("EDSM")
    modes = ['EDSM','Inara']
    row = 0
    for mode in modes:
        b = nb.Radiobutton(shipyard_frame, text=mode, variable=this.shipyard_provider_select, value=mode)
        b.grid(column = 3, row = row, sticky="W", padx = 1)
        row = row + 1
    b.grid_configure(pady = 2)
    EDSM_id_label = nb.Label(shipyard_frame, text="To view your ships in EDSM,\nenter the numbers that follow id/\nin the URL for your EDSM profile page: ", justify = tk.LEFT)
    EDSM_id_label.grid(column = 2, row = 2, pady = 2)
    this.EDSM_id_entry = nb.Entry(shipyard_frame)
    this.EDSM_id_entry.grid(column = 3, row = 2)
    try:
        this.EDSM_id_entry.delete(0, tk.END)
        this.EDSM_id_entry.insert(0, config.get_str('EDSM_id'))
    except:
        pass
    shipyard_frame.grid(column = 1, row = 1, sticky = "nsew")
    return frame
    
def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    config.set('EDSM_id', this.EDSM_id_entry.get())
    config.set('L3_shipyard_provider',this.shipyard_provider_select.get())
    try:
        config.set('L3_system_provider',this.system_provider_select.get())
        config.set('L3_station_provider',this.station_provider_select.get())
    except:
        pass

def journal_entry(cmdr, is_beta, system, station, entry, state):
    this.system = system
    this.station = station
    for key, module in plugin_app.wafer_modules.items():
        try:
            module.journal_entry(cmdr, system, station, entry, state)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)

def dashboard_entry(cmdr, is_beta, entry):
    for key, module in plugin_app.wafer_modules.items():
        try:
            module.dashboard_entry(cmdr, is_beta, entry)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)


def cmdr_data(data, is_beta):
    for key, module in plugin_app.wafer_modules.items():
        try:
            module.cmdr_data(data, is_beta)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)
            
def inara_notify_ship(eventData):
    for key, module in plugin_app.wafer_modules.items():
        try:
            module.inara_notify_ship(eventData)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)
            
def inara_notify_location(eventData):
    for key, module in plugin_app.wafer_modules.items():
        try:
            module.inara_notify_location(eventData)
        except Exception as exc:
            print('Error when updating module ' + module)
            print(traceback.format_exc())
            print(exc)