import Tkinter as tk
from config import config
import myNotebook as nb
import traceback

import api_store

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
        self.fake_combo2 = tk.Button(self.combo_frame, text = unichr(11206), command = self.popup, padx = 0, pady = 0) #unichr(9660)
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

def plugin_start():
    """
    Load this plugin into EDMC
    """
    try:
        config.get('L3_shipyard_provider')
    except:
        config.set('L3_shipyard_provider','EDSM')
    try:
        config.get('EDSM_id')
    except:
        config.set('EDSM_id', '')
    print "L3-37 started"
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
    plugin_app.theme = config.getint('theme')
    plugin_app.fg = config.get('dark_text') if plugin_app.theme else 'black'
    plugin_app.hl = config.get('dark_highlight') if plugin_app.theme else 'blue'
    plugin_app.bg = 'grey4' if plugin_app.theme else None
    for module in plugin_app.wafer_module_classes:
        plugin_app.wafer_modules[module[0]] = module[1](plugin_app.frame, highlightbackground=plugin_app.fg, highlightcolor=plugin_app.fg, highlightthickness = 1)#, relief = tk.SUNKEN, borderwidth = 1)
        plugin_app.frame.add(plugin_app.wafer_modules[module[0]], module[0])
    plugin_app.frame.bind('<<SystemData>>', api_store.edsm_handler)
    api_store.set(plugin_app.frame)
    print "L3-37 loaded"
    return (plugin_app.frame)
    
def plugin_prefs(parent):
    frame = nb.Frame(parent)
    shipyard_provider_label = nb.Label(frame, text="Fleet information provider: ", justify = tk.LEFT)
    shipyard_provider_label.grid(column = 0, row = 0)
    this.shipyard_provider_select = tk.StringVar()
    try:
        this.shipyard_provider_select.set(config.get('L3_shipyard_provider'))
    except:
        this.shipyard_provider_select.set("EDSM")
    modes = ['EDSM','Inara']
    row = 0
    for mode in modes:
        b = nb.Radiobutton(frame, text=mode, variable=this.shipyard_provider_select, value=mode)
        b.grid(column = 1, row = row)
        row = row + 1
    EDSM_id_label = nb.Label(frame, text="To view your ships in EDSM,\nenter the numbers that follow id/\nin the URL for your EDSM profile page: ", justify = tk.LEFT)
    EDSM_id_label.grid(column = 0, row = 2)
    this.EDSM_id_entry = nb.Entry(frame)
    this.EDSM_id_entry.grid(column = 1, row = 2)
    try:
        this.EDSM_id_entry.delete(0, tk.END)
        this.EDSM_id_entry.insert(0, config.get('EDSM_id'))
    except:
        pass
    return frame
    
def prefs_changed():
    """
    Save settings.
    """
    config.set('EDSM_id', this.EDSM_id_entry.get())
    config.set('L3_shipyard_provider',this.shipyard_provider_select.get())

def journal_entry(cmdr, system, station, entry, state):
    this.system = system
    this.station = station
    for key, module in plugin_app.wafer_modules.iteritems():
        try:
            module.journal_entry(cmdr, system, station, entry, state)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)

def dashboard_entry(cmdr, is_beta, entry):
    for key, module in plugin_app.wafer_modules.iteritems():
        try:
            module.dashboard_entry(cmdr, is_beta, entry)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)


def cmdr_data(data, is_beta):
    for key, module in plugin_app.wafer_modules.iteritems():
        try:
            module.cmdr_data(data, is_beta)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)
            
def inara_notify_ship(eventData):
    for key, module in plugin_app.wafer_modules.iteritems():
        try:
            module.inara_notify_ship(eventData)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)
            
def inara_notify_location(eventData):
    api_store.inara_notify_location(this.system, this.station, eventData)
    for key, module in plugin_app.wafer_modules.iteritems():
        try:
            module.inara_notify_location(this.system, this.station, eventData)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)
            
def plugin_stop():
    api_store.plugin_stop()