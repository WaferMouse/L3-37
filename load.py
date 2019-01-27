import Tkinter as tk
import ttk
from os import path
from config import config
from urlparse import urlparse
import webbrowser
import json
import urllib
import tkMessageBox
import myNotebook as nb
import traceback

from ttkHyperlinkLabel import HyperlinkLabel

import sys

from companion import ship_map

import os

import math

this = sys.modules[__name__]	# For holding module globals

plugin_path = path.join(config.plugin_dir, "edmc-L3-37")

from web_handlers import *

from wafer_module import WaferModule

from chat_viewer import ChatViewer

from fsd_target import FSDTarget

from mats_helper import MatsHelper

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, height = 200, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set, height = height, width = 500)#, background='grey4')
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas, background=plugin_app.bg)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _bound_to_mousewheel(event):
          canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind('<FocusIn>', _bound_to_mousewheel)

        def _bound_to_mousewheel2(*args, **kw):
          canvas.bind_all("<MouseWheel>", _on_mousewheel)
          interior.focus_set()
          canvas.yview(*args, **kw)
        vscrollbar.config(command=_bound_to_mousewheel2)

        def _unbound_to_mousewheel(event):
          canvas.unbind_all("<MouseWheel>")
        canvas.bind('<FocusOut>', _unbound_to_mousewheel)

        def _on_mousewheel(event):
          canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
        interior.bind("<1>", lambda event: interior.focus_set())
        
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
        
        self.fake_combo = tk.Button(self.combo_frame, text = '', command = self.popup, padx = 0, pady = 0, relief = tk.FLAT)
        self.fake_combo2 = tk.Button(self.combo_frame, text = unichr(9660), command = self.popup, padx = 0, pady = 0) #unichr(9660)
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

class ToggledFrame(tk.Frame):

    def __init__(self, parent, text="", *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)

        self.show = tk.IntVar()
        self.show.set(1)
        self.text = text

        self.title_frame = tk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        self.toggle_button = tk.Label(self.title_frame,text= unichr(9654) + ' ' + text)
        self.toggle_button.pack(side="left")

        self.sub_frame = tk.Frame(self)

        def toggle(self):
            if bool(self.show.get()):
                self.sub_frame.pack(fill="x", expand=1)
                self.toggle_button.configure(text=unichr(9660) + ' ' + self.text)
                self.show.set(0)
            else:
                self.sub_frame.forget()
                self.toggle_button.configure(text= unichr(9654) + ' ' + self.text)
                self.show.set(1)

        def click(event):
          toggle(self)

        self.toggle_button.bind("<Button-1>",click)

class Dialog(tk.Toplevel):

    def __init__(self, parent, title = None):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override

class ModelFSDShip:
    def __init__(self):
        with open(path.join(plugin_path,'flat_modules.json')) as json_data:
            self.FLAT_MODULES = json.load(json_data)
        
    def update(self, ship_type, modules):
        self.guardian_boost = 0
        self.mass_capacities = {
            'mass': plugin_app.FLAT_SHIPS[ship_type.lower()]['hullMass'],
            'cargo': 0,
            'fuel': 0,
            }
        for k,v in modules.iteritems():
            item_name = v['Item']
            if item_name in self.FLAT_MODULES:
                for i in ['mass', 'cargo', 'fuel']:
                    if i in self.FLAT_MODULES[item_name]:
                        self.mass_capacities[i] = self.mass_capacities[i] + self.FLAT_MODULES[item_name][i]
                if 'grp' in self.FLAT_MODULES[item_name]:
                    if self.FLAT_MODULES[item_name]['grp'] == 'gfsb':
                        self.guardian_boost = self.FLAT_MODULES[item_name]['jumpboost']
                if 'Engineering' in v:
                    for mod in v['Engineering']['Modifiers']:
                        if mod['Label'] == 'Mass':
                            self.mass_capacities['mass'] = self.mass_capacities['mass'] + (mod['Value'] - mod['OriginalValue'])
        fsd_stats_list = [
            'fuelmul',
            'fuelpower',
            'maxfuel',
            'optmass',
            ]
        self.fsd_stats = {}
        FSD = modules['FrameShiftDrive']
        FSD_name = FSD['Item'].lower()
        FSD_model = self.FLAT_MODULES[FSD_name]
        for i in fsd_stats_list:
            self.fsd_stats[i] = FSD_model[i]
            
        if 'Engineering' in FSD:
            for mod in FSD['Engineering']['Modifiers']:
                if mod['Label'] == 'FSDOptimalMass':
                    self.fsd_stats['optmass'] = mod['Value']
                if mod['Label'] == 'FSDMaxFuelPerJump ':
                    self.fsd_stats['maxfuel'] = mod['Value']
                    
    def calc_max_distance(self, cargo_mass = 0, fuel_mass = -1):#, fuel_mass = self.mass_capacities['fuel']):
        if fuel_mass == -1:
            fuel_mass = self.mass_capacities['fuel']
        O = self.fsd_stats['optmass']
        M = fuel_mass + cargo_mass + self.mass_capacities['mass']
        C = self.fsd_stats['fuelpower'] #sizeconst
        R = self.fsd_stats['fuelmul'] #ratingconst
#        B = boostused
        G = self.guardian_boost
        F = self.fsd_stats['maxfuel']
        if fuel_mass < F:
            F = fuel_mass
        D = ((F/R)**(1/float(C)) * O / M) + G
        return(D)
        
        
    def calc_fuel_use(self, distance, fuel_mass, boostused = 1, cargo_mass = 0):
        O = self.fsd_stats['optmass']
        M = fuel_mass + cargo_mass + self.mass_capacities['mass']
        C = self.fsd_stats['fuelpower']
        R = self.fsd_stats['fuelmul']
        B = boostused
        G = self.guardian_boost
        D = distance
        F = self.fsd_stats['maxfuel']
        #fuelused = R * ((((D-G)/B) * M / O)**C)
        fuelused = F*((D/B)/(G + (O*(F/R)**(1/C))/M))**C
        #F = R * (((D/B) * M / O)**C)
        #F/R = ((D/B) * M / O)**C
        #(F/R)**(1/float(C)) = (D/B) * M / O
        #(F/R)**(1/float(C)) * O = (D/B) * M
        #(F/R)**(1/float(C)) * O / M = (D/B)
        #D = (F/R)**(1/float(C)) * O / M
        return(fuelused)

def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180 to + 180 which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

class JumpFuelWidget(tk.Frame):
    
    def __init__(self, parent, jumps = 1, is_neutron = False, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        self.canvas = tk.Canvas(self, height = 1, width = 16, bd=0, highlightthickness=0)
        if plugin_app.theme:
            self.canvas.config(background = plugin_app.bg)
        self.canvas.pack(fill = tk.BOTH, expand = 1)
        self.x0 = self.canvas.canvasx(0)
        self.y0 = self.canvas.canvasy(0)
        self.lines = []
        self.dashed_lines = []
        line1colour = ['orange','cyan'][is_neutron]
        line2colour = [line1colour,'orange'][jumps > 1]
        self.stub = self.canvas.create_line(self.x0+8,self.y0,self.x0+16,self.y0, fill=line1colour)
        self.lines.append(self.canvas.create_line(self.x0,self.y0,self.x0,self.y0, fill=line1colour, state = tk.HIDDEN))
        self.lines.append(self.canvas.create_line(self.x0,self.y0,self.x0,self.y0, fill=line2colour, state = tk.HIDDEN))
        self.dashed_lines.append(self.canvas.create_line(self.x0,self.y0,self.x0,self.y0, fill=line1colour, dash = (4, 4)))
        self.dashed_lines.append(self.canvas.create_line(self.x0,self.y0,self.x0,self.y0, fill=line2colour, dash = (4, 4)))
        self.bind("<Configure>", self.on_resize)
        
    def on_resize(self,event):
        height = int(self.winfo_height()/2)
        i = 0
        for line in self.lines:
            self.canvas.coords(line, (self.x0+8, self.y0+i*height, self.x0+8, self.y0+(i+1)*height))
            i += 1
        i = 0
        for line in self.dashed_lines:
            self.canvas.coords(line, (self.x0+8, self.y0+i*height, self.x0+8, self.y0+(i+1)*height))
            i += 1
            
    def update(self, line, fuel):
        if fuel:
            try:
                self.canvas.itemconfigure(self.lines[line], state = 'normal')
            except:
                pass
        else:
            self.canvas.itemconfigure(self.lines[line], state = tk.HIDDEN)

class SystemFrame(tk.Frame):
    
    def __init__(self, parent, system_name, distance = 0, jumps = '', is_neutron = False, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        
        self.system_name = system_name
        self.distance = distance
        self.jumps = jumps
        self.is_neutron = is_neutron
        
        self.dyn_widgets = []
            
        if jumps != '':
            self.jumps_lbl = tk.Label(self, text = jumps, anchor = tk.W, justify=tk.LEFT)
            self.jumps_lbl.pack(fill="x")
            self.dyn_widgets.append(self.jumps_lbl)
        
        self.name_lbl = tk.Label(self, text = system_name, anchor = tk.W, justify=tk.LEFT)
        self.name_lbl.pack(fill="x")
        self.dyn_widgets.append(self.name_lbl)
        self.menu = tk.Menu(self, tearoff=0)

        self.menu.add_command(label="Copy system name", command = self.copySystem)
#        self.menu.add_command(label="Copy EDSM link", command = self.copySystemLink)
        self.bind("<Button-3>", self.rightclick)
        self.bind("<Button-1>", self.click)
        
        if distance != 0:
            self.distance_lbl = tk.Label(self, text = distance_name, anchor = tk.W, justify=tk.LEFT)
            self.distance_lbl.pack(fill="x")
            self.dyn_widgets.append(self.distance_lbl)
            
        for widget in self.dyn_widgets:
            widget.bind("<Button-3>", self.rightclick)
            widget.bind("<Button-1>", self.click)
        if plugin_app.theme:
            for widget in self.dyn_widgets:
                widget.config(background = plugin_app.bg, foreground = plugin_app.hl)
    def copySystem(self):
        setclipboard(self.system_name)
    def copySystemLink(self):
        setclipboard("https://www.edsm.net/show-system?systemName=" + urllib.quote_plus(self.system_name))
    def click(self, event):
        webbrowser.open(get_system_url(self.system_name))
    def rightclick(self, event):
        self.menu.post(event.x_root, event.y_root)
        
class ShipFrame(tk.Frame):
    def __init__(self, parent, ship_data, edsm_username, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        self.edsm_username = edsm_username
        self.build_ui()
        self.update_ship(ship_data)
        if plugin_app.theme:
            for element in [self.ship_link, self.station_link, self.system_link]:
                element.config(background = plugin_app.bg, foreground = plugin_app.hl)
            for element in [self.sys_label, self.station_label]:
                element.config(background = plugin_app.bg, foreground = plugin_app.fg)
            self.sub_frame.config(background = plugin_app.bg)
        
    def update_ship(self, ship_data):
        self.ship_data = ship_data
        if 'shipName' in ship_data:
            self.ship_lbl_txt = u"{} ({})".format(ship_data['shipName'],ship_map[ship_data['name'].lower()])
        else:
            self.ship_lbl_txt = ship_map[ship_data['name'].lower()]
        self.sysname = ship_data['starsystem']['name']
        self.stationname = ship_data['station']['name']
        self.sys_url = get_system_url(self.sysname)
        self.station_url = get_station_url(self.sysname, self.stationname)
        self.system_link.configure(url = self.sys_url, text = self.sysname)
        edID = plugin_app.FLAT_SHIPS[self.ship_data['name'].lower()]['edID']
        self.ship_url = "https://www.edsm.net/en/user/fleet/id/{}/cmdr/{}/ship/sId/{}/sType/{}".format(config.get('EDSM_id'), self.edsm_username, self.ship_data['id'], edID)
        # https://inara.cz/cmdr-fleet/
        self.ship_link.configure(url = self.ship_url, text = self.ship_lbl_txt)
        self.station_link.configure(url = self.station_url, text = self.stationname)
        
    def build_ui(self):
        self.sub_frame = tk.Frame(self)
        self.ship_link = HyperlinkLabel(self, text = '', justify=tk.LEFT, anchor='w', url = None)
        self.system_link = HyperlinkLabel(self.sub_frame, text = '', justify=tk.LEFT, anchor='w', url = None)
        self.station_link = HyperlinkLabel(self.sub_frame, text = '', justify=tk.LEFT, anchor='w', url = None)
        self.ship_link.grid(column = 0, row = 0, sticky = 'w')
        self.sub_frame.grid(sticky = 'w')
        self.sys_label = tk.Label(self.sub_frame, text = 'System: ', justify=tk.LEFT, anchor=tk.W, pady=0)
        self.sys_label.grid(column = 0, row = 1, sticky = 'w')
        self.system_link.grid(column = 1, row = 1, sticky = 'w')
        self.station_label = tk.Label(self.sub_frame, text = 'Station: ', justify=tk.LEFT, anchor=tk.W, pady=0)
        self.station_label.grid(column = 0, row = 2, sticky = 'w')
        self.station_link.grid(column = 1, row = 2, sticky = 'w')
        self.menu = tk.Menu(self, tearoff=0)

        self.menu.add_command(label="Copy system name", command = self.copySystem)
        for i in [self.station_link, self.system_link]:
            i.bind("<Button-3>", self.rightclick)
    def copySystem(self):
        setclipboard(self.sysname)
    def rightclick(self, event):
        self.menu.post(event.x_root, event.y_root)
        
class FleetMonitor(WaferModule):
    
    def __init__(self, parent, *args, **options):
        WaferModule.__init__(self, parent, *args, **options)
        self.ships = {}
        self.bigjsonships = {}
        self.DeadShip = None
        self.ship_widgets = {}
        try:
            with open(path.join(plugin_path, 'ships.json')) as json_data:
                self.bigjsonships = json.load(json_data)
        except:
            pass
        self.ships_scroll = VerticalScrolledFrame(self)
        self.ships_scroll.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        
    def self_set(self, cmdr):
        self.cmdr = cmdr
        if cmdr in config.get('edsm_cmdrs') and config.get('edsm_usernames'):
            idx = config.get('edsm_cmdrs').index(cmdr)
            self.edsm_username = config.get('edsm_usernames')[idx]
        else:
            self.edsm_username = ''
        self.ships.clear()
        for widget in self.ship_widgets:
            widget.destroy()
        self.ship_widgets.clear()
        if self.cmdr in self.bigjsonships:
            self.ships.update(self.bigjsonships[self.cmdr])
        else:
            self.bigjsonships.update({self.cmdr:{}})
            self.ships.update({})
            
    def build_ui(self):
        for key, widget in self.ship_widgets.iteritems():
            if key not in self.ships:
                widget.forget()
            else:
                widget.update_ship(self.ships[key])
        for ship in self.ships:
            if ship not in self.ship_widgets:
                self.ship_widgets.update({ship: ShipFrame(self.ships_scroll.interior, self.ships[ship], urllib.quote_plus(self.cmdr), highlightthickness = 1)})
                if plugin_app.theme:
                    self.ship_widgets[ship].config(background = plugin_app.bg)
            self.ship_widgets[ship].pack(fill = tk.BOTH, expand = 1)
        for key, widget in self.ship_widgets.iteritems():
            widget.config(highlightbackground=plugin_app.fg, highlightcolor=plugin_app.fg)
            
        if plugin_app.theme:
            self.ships_scroll.interior.config(background = plugin_app.bg)
            
    def cmdr_data(self, data, is_beta):
        write_file = False
        do_build_ui = False
#        if event['event'] == 'cmdr_data':
        cmdr = data['commander']['name']
        if hasattr(self, 'cmdr') == False:
            self.self_set(cmdr)
            do_build_ui = True
        elif self.cmdr != cmdr:
            self.self_set(cmdr)
            do_build_ui = True
        scrub_list = []
        for ship in self.ships:
            if ship not in data["ships"]:
                scrub_list.append(ship)
            else:
                for i in ["shipID", "shipName"]:
                    try:
                        if self.ships[ship][i] != data["ships"][ship][i]:
                            self.ships[ship][i] = data["ships"][ship][i]
                            write_file = True
                            do_build_ui = True
                    except:
                        pass
        for ship in scrub_list:
            del self.ships[ship]
            write_file = True
            do_build_ui = True
        for ship in data["ships"]:
            if ship not in self.ships:
                self.ships[ship] = data["ships"][ship]
                del self.ships[ship]["starsystem"]["id"]
                del self.ships[ship]["starsystem"]["systemaddress"]
                del self.ships[ship]["station"]["id"]
                del self.ships[ship]["value"]
                del self.ships[ship]["free"]
                self.ships[ship].update({'localised_name': ship_map[self.ships[ship]['name'].lower()]})
                write_file = True
                do_build_ui = True
          
        if write_file:
            self.bigjsonships.update({self.cmdr: self.ships})
            with open(path.join(plugin_path, 'ships.json'), 'w') as fp:
                json.dump(self.bigjsonships, fp, indent = 2, sort_keys=True)
                
        if do_build_ui:
            self.build_ui()
        
    def journal_entry(self, cmdr, system, station, entry, state):
        write_file = False
        do_build_ui = False
        if hasattr(self, 'cmdr') == False:
            self.self_set(cmdr)
            do_build_ui = True
        elif self.cmdr != cmdr:
            self.self_set(cmdr)
            do_build_ui = True
            
        if (state['Captain'] == None) and (system != None):
            
            current_ship_id = state['ShipID']
            
            state_ship = {
                "id": current_ship_id,
                "name": state['ShipType'],
                "shipID": state['ShipIdent'],
                "shipName": state['ShipName'],
                "starsystem": {"name": system},
                "station": {"name": [station, 'In flight'][station == None]},
#                "starpos": state['StarPos'],
                'localised_name': ship_map[state['ShipType'].lower()]
                }
            
            if str(current_ship_id) not in self.ships:
                self.ships[str(current_ship_id)] = state_ship
                write_file = True
                do_build_ui = True
            elif self.ships[str(current_ship_id)] != state_ship:
                self.ships[str(current_ship_id)] = state_ship
                write_file = True
                do_build_ui = True
          
            if entry['event'] == "ShipyardTransfer":
                this_ship_id = str(entry["ShipID"])
                if this_ship_id not in self.ships:
                    self.ships[this_ship_id] = {
                        "id": entry["ShipID"],
                        "shipName": entry['ShipType'],
                        "name": entry['ShipType'],
                        'localised_name': ship_map[entry['ShipType'].lower()]
                        }
                self.ships[this_ship_id].update({
                    "starsystem": {"name": system},
                    "station": {"name": station},
#                    "starpos": state['StarPos'],
                    })
                write_file = True
                do_build_ui = True
            
            elif entry['event'] == 'Died':
                self.DeadShip = current_ship_id
            
            elif entry['event'] == "Resurrect":
                if entry["Option"] != "rebuy":
                    if self.DeadShip != None:
                        try:
                            del self.ships[str(self.DeadShip)]
                            write_file = True
                            do_build_ui = True
                        except:
                            pass
                        self.DeadShip = None
          
            if "SellShipID" in entry:
                try:
                    del self.ships[str(entry["SellShipID"])]
                    write_file = True
                    do_build_ui = True
                except:
                    pass
          
        if write_file:
            self.bigjsonships.update({self.cmdr: self.ships})
            with open(path.join(plugin_path, 'ships.json'), 'w') as fp:
                json.dump(self.bigjsonships, fp, indent = 2, sort_keys=True)
                
        if do_build_ui:
            self.build_ui()

class SurfaceNavigation(WaferModule):
    
    def __init__(self, parent, *args, **options):
        WaferModule.__init__(self, parent, *args, **options)
        
        self.settings_open = False
        
        self.lbl_frm = tk.Frame(self)
        self.lbl = tk.Label(self.lbl_frm, text="Bearing:", anchor=tk.W)
        self.target_lat = tk.Entry(self, width=1)
        self.lat_label = tk.Label(self, text='Lat:')
        self.target_lon = tk.Entry(self, width=1)
        self.lon_label = tk.Label(self, text='Lon:')
        self.bearing_frame = tk.Frame(self.lbl_frm)
        self.set_btn = tk.Button(self.lbl_frm, text='Set', command = self.toggle_settings)
        self.lbl_left = tk.Label(self.bearing_frame, text='<', width=1)
        self.lbl_right = tk.Label(self.bearing_frame, text='>', width=1)
        self.bearing = tk.Label(self.bearing_frame, text='', width=6)
        self.lbl_frm.grid(row=0,column=0, columnspan=4, sticky='nsew')
        self.lbl_frm.grid_columnconfigure(0, weight=1, uniform="fred")
        self.lbl_frm.grid_columnconfigure(1, weight=1, uniform="fred")
        self.lbl_frm.grid_columnconfigure(2, weight=1, uniform="fred")
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.lbl.grid(sticky=tk.W)
        self.bearing_frame.grid(row=0, column=1, sticky = "nsew")
        self.lbl_left.grid(row=0, column=0)
        self.bearing.grid(row=0, column=1)
        self.lbl_right.grid(row=0, column=2)
        self.set_btn.grid(row=0, column=2, sticky="e")
        
    def dashboard_entry(self, cmdr, is_beta, entry):
        if "Latitude" in entry:
            try:
                target_lat_lon = (float(self.target_lat.get()), float(self.target_lon.get()))
                current_lat_lon = (entry["Latitude"], entry["Longitude"])
                bearing = calculate_initial_compass_bearing(current_lat_lon, target_lat_lon)
                txt_bearing = "%.2f" % bearing
                correction = (360 + (bearing - entry['Heading'])) % 360
                self.bearing.config(text=txt_bearing)
                if 1 < correction < 180:
                    self.lbl_right.config(text=">")
                else:
                    self.lbl_right.config(text="")
                if 180 < correction < 359:
                    self.lbl_left.config(text="<")
                else:
                    self.lbl_left.config(text="")
            except:
                self.bearing.config(text="!")
                self.lbl_left.config(text="<")
                self.lbl_right.config(text=">")
        else:
            self.bearing.config(text="")
            self.lbl_left.config(text="<")
            self.lbl_right.config(text=">")
                
    def toggle_settings(self):
        if self.settings_open == False:
            self.lat_label.grid(row=1, column=0)
            self.target_lat.grid(row=1, column=1, sticky = "nsew")
            self.lon_label.grid(row=1, column=2)
            self.target_lon.grid(row=1, column=3, sticky = "nsew")
            self.set_btn.config(text='OK')
            self.settings_open = True
        else:
            self.lat_label.grid_forget()
            self.target_lat.grid_forget()
            self.lon_label.grid_forget()
            self.target_lon.grid_forget()
            self.set_btn.config(text='Set')
            self.settings_open = False

class NeutronNavigation(WaferModule):
    
    def __init__(self, parent, *args, **options):
        WaferModule.__init__(self, parent, *args, **options)
        
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(fill = tk.BOTH, expand = 1)
        
        self.jump_range_frm = tk.Frame(self.control_frame)
        self.jump_range_frm.pack(fill = tk.BOTH, expand = 1)
        
        self.jump_range_lbl = tk.Label(self.jump_range_frm, text = "Jump range:")
        self.jump_range_lbl.pack(side = tk.LEFT)
        
        self.jump_range_btn = tk.Button(self.jump_range_frm, text = 'Copy', command = self.copy_jump_range)
        self.jump_range_btn.pack(side = tk.LEFT)
        
        self.paste_frame = tk.Frame(self.control_frame)
        self.spansh_button = tk.Button(self.paste_frame, text='1. Visit spansh.co.uk/plotter.', justify = tk.LEFT, command = self.open_spansh)
        self.spansh_button.pack(anchor = 'w')
        self.paste_label = tk.Label(self.paste_frame, text='2. Calculate a route.\n3. Copy the URL.', anchor = tk.NE, justify = tk.LEFT)
        self.paste_label.pack(anchor = 'w')
        
        self.paste_button = tk.Button(self.paste_frame, text = '4. Click here.', command = self.paste_spansh_url, anchor = 'w')
        self.paste_button.pack(anchor = 'w')
        
        self.copy_button = tk.Button(self.control_frame, text = 'Copy next system', command = self.copy_next_system)
        self.clear_route_button = tk.Button(self.control_frame, text = 'Clear route', command = self.user_clear_route)
        
        self.details_frame = ToggledFrame(self, text = 'Details')
        
        self.fuellevel = 0
        self.dyn_widgets = []
        self.fuel_widgets = []
        self.jump_widgets = []
        self.current_starsystem = ''
        
        self.clear_route()
        
        self.details_scroll = VerticalScrolledFrame(self.details_frame.sub_frame, height = 100)
        self.details_scroll.pack(fill = tk.BOTH, expand = 1)
        
        self.details_scroll.interior.columnconfigure(1, weight = 1)
        
        self.LOADOUT_EVENTS = ['StartUp', 'Loadout', 'ModuleBuy', 'ModuleSell', 'ModuleRetrieve','ModuleStore']
        self.CARGO_EVENTS = ['StartUp', 'Cargo','CollectCargo', 'MarketBuy', 'MiningRefined','EjectCargo', 'MarketSell','MissionCompleted']
        self.FUEL_EVENTS = ['RefuelAll', 'FuelScoop', 'FSDJump', 'LoadGame',]# 'RefuelPartial'] #StartUp won't work because Fuel is not included in state
        self.model_ship = ModelFSDShip()
        
        try:
            with open(path.join(plugin_path, 'route.json')) as json_data:
                self.route = json.load(json_data)
            self.process_route()
            system_count = len(self.queued_systems)
            with open(path.join(plugin_path, 'queue.json')) as json_data:
                self.queued_systems = json.load(json_data)
            system_count = system_count - len(self.queued_systems)
            self.next_waypoint_str = self.queued_systems[1]
            for i in range(system_count):
                self.dyn_widgets[0].destroy()
                del self.dyn_widgets[0]
                self.fuel_widgets[0].destroy()
                del self.fuel_widgets[0]
                self.jump_widgets[0].destroy()
                del self.jump_widgets[0]
            self.paste_frame.forget()
            self.copy_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
            self.clear_route_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
            self.details_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        except:
            print("Failed to load route data")
        
    def user_clear_route(self, event = ''):
        if tkMessageBox.askyesno("Confirm", "Really clear the route?", default = tkMessageBox.NO):
            self.clear_route()
            for i in ['route.json', 'queue.json']:
                if os.path.exists(path.join(plugin_path, i)):
                    os.remove(path.join(plugin_path, i))
        
    def clear_route(self):
        for i in self.dyn_widgets:
            i.destroy()
        for i in self.fuel_widgets:
            i.destroy()
        for i in self.jump_widgets:
            i.destroy()
        self.queued_systems = []
        self.route = {}
        self.next_waypoint_str = ''
        self.dyn_widgets = []
        self.fuel_widgets = []
        self.jump_widgets = []
        self.clear_route_button.forget()
        self.copy_button.forget()
        self.details_frame.forget()
        self.paste_frame.pack(side = tk.LEFT)

    def paste_spansh_url(self, event=''):
        o = getclipboard()
        disassembled = urlparse(o)
        url, scrap = path.splitext(path.basename(disassembled.path))
        url = 'https://spansh.co.uk/api/results/' + url
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        
        self.route = data
        try:
            self.process_route()
            self.paste_frame.forget()
            self.copy_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
            self.clear_route_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
            self.details_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
            
            with open(path.join(plugin_path, 'route.json'), 'w') as fp:
                json.dump(self.route, fp, indent = 2, sort_keys=True)
            with open(path.join(plugin_path, 'queue.json'), 'w') as fp:
                json.dump(self.queued_systems, fp, indent = 2, sort_keys=True)
        except:
            tkMessageBox.showerror("Error", "Could not load route. You may need to request an updated route from spansh.")
            
    def open_spansh(self, event=''):
        webbrowser.open("http://www.spansh.co.uk/plotter")
                
    def process_route(self):
        widget_row = 0
        for i in self.route['result']['system_jumps']:
            name = i['system']
            is_neutron = i['neutron_star']
            self.dyn_widgets.append(SystemFrame(self.details_scroll.interior, name, is_neutron = is_neutron))
            self.dyn_widgets[-1].grid(row = widget_row*4, column = 1, sticky = 'nsew', rowspan = 2)
            try:
                jumps = self.route['result']['system_jumps'][widget_row + 1]['jumps']
                if is_neutron:
                    jump_text = '1 neutron jump{}.'.format(['', ' and {} other{}'.format(str(jumps - 1),['', 's'][jumps != 2])][jumps > 1])
                else:
                    jump_text = '{} jump{}.'.format(jumps, ['', 's'][jumps != 1])
                self.jump_widgets.append(tk.Label(self.details_scroll.interior, text = jump_text, anchor = tk.E))
                if plugin_app.theme:
                    self.jump_widgets[-1].config(bg = plugin_app.bg, fg = plugin_app.fg)
                self.jump_widgets[-1].grid(row = (widget_row*4)+2, column = 1, sticky = 'nsew', rowspan = 2)
                self.fuel_widgets.append(JumpFuelWidget(self.details_scroll.interior, jumps = jumps, is_neutron = is_neutron))
                self.fuel_widgets[-1].grid(row = (widget_row*4)+1, column = 0, sticky = 'nsew', rowspan = 4)
            except:
                pass
            widget_row += 1
            
            self.queued_systems.append(name.lower())
            
        self.next_waypoint_str = self.queued_systems[0]
        if self.next_waypoint_str.lower() == self.current_starsystem.lower():
            self.next_waypoint_str = self.queued_systems[1]
            
    def journal_entry(self, cmdr, system, station, entry, state):
        self.current_starsystem = system
        if self.current_starsystem == None:
            self.current_starsystem = ''
        if entry['event'] in self.LOADOUT_EVENTS:
            self.model_ship.update(state['ShipType'], state['Modules'])
            self.current_jump_range = self.model_ship.calc_max_distance()
            self.jump_range_lbl.config(text = 'Jump range: {}ly'.format(round(self.current_jump_range, 2)))
        if self.queued_systems != []:
            if entry['event'] == 'FSDJump':
                self.check_starsystem(self.current_starsystem)
            if entry['event'] in self.FUEL_EVENTS:
                if entry['event'] in ['LoadGame','FSDJump']:
                    self.fuellevel = entry['FuelLevel']
                elif entry['event'] == 'RefuelAll':
                    self.fuellevel = self.model_ship.mass_capacities['fuel']
                elif entry['event'] == 'FuelScoop':
                    self.fuellevel = entry['Total']
                    
                test_fuel = self.fuellevel
                route_offset = len(self.route['result']['system_jumps']) - len(self.queued_systems)
                for i in range(len(self.queued_systems) - 1):
                    if test_fuel > 0:
                        if i == 0 and self.current_starsystem.lower() != self.queued_systems[0]:
                            self.fuel_widgets[i].update(0, False)
                            self.fuel_widgets[i].update(1, False)
                        else:
                            this_jump = self.route['result']['system_jumps'][i + route_offset]
                            next_jump = self.route['result']['system_jumps'][i + 1 + route_offset]
                            remaining_jumps = next_jump['jumps']
                            remaining_distance = next_jump['distance_jumped']
                            if this_jump['neutron_star']:
                                if remaining_jumps > 1:
                                    jump_distance = self.model_ship.calc_max_distance(fuel_mass = test_fuel) * 4
                                    test_fuel = test_fuel - self.model_ship.calc_fuel_use(jump_distance, test_fuel, boostused = 4)
                                    remaining_distance = remaining_distance - jump_distance
                                else:
                                    test_fuel = test_fuel - self.model_ship.calc_fuel_use(next_jump['distance_jumped'], test_fuel, boostused = 4)
                                    remaining_distance = 0
                                remaining_jumps = remaining_jumps - 1
                                        
                            if test_fuel > 0:
                                self.fuel_widgets[i].update(0, True)
                            else:
                                self.fuel_widgets[i].update(0, False)
                                
                            while remaining_distance > 0 and test_fuel > 0:
                                jump_distance = self.model_ship.calc_max_distance(fuel_mass = test_fuel)
                                if jump_distance >= remaining_distance:
                                    test_fuel = test_fuel - self.model_ship.calc_fuel_use(remaining_distance, test_fuel, boostused = 1)
                                    remaining_distance = 0
                                else:
                                    test_fuel = test_fuel - self.model_ship.calc_fuel_use(jump_distance, test_fuel, boostused = 1)
                                    remaining_distance = remaining_distance - jump_distance
                                        
                            if test_fuel > 0:
                                self.fuel_widgets[i].update(1, True)
                            else:
                                self.fuel_widgets[i].update(1, False)
                    else:
                        self.fuel_widgets[i].update(0, False)
                        self.fuel_widgets[i].update(1, False)
                        
    def check_starsystem(self, system):
        if system.lower() in self.queued_systems:
            systems_to_delete = self.queued_systems.index(system.lower())
            for i in range(systems_to_delete):
                del self.queued_systems[0]
                self.dyn_widgets[0].destroy()
                del self.dyn_widgets[0]
                self.fuel_widgets[0].destroy()
                del self.fuel_widgets[0]
                self.jump_widgets[0].destroy()
                del self.jump_widgets[0]
            if len(self.queued_systems) == 1:
                self.clear_route()
                for i in ['route.json', 'queue.json']:
                    if os.path.exists(path.join(plugin_path, i)):
                        os.remove(path.join(plugin_path, i))
            else:
                self.next_waypoint_str = self.queued_systems[1]
                self.copy_next_system()
                with open(path.join(plugin_path, 'queue.json'), 'w') as fp:
                    json.dump(self.queued_systems, fp, indent = 2, sort_keys=True)
                
    def copy_next_system(self, event=''):
        setclipboard(self.next_waypoint_str)
    def copy_jump_range(self, event=''):
        setclipboard(str(round(self.current_jump_range, 2)))

def setclipboard(text):
      r = tk.Tk()
      r.clipboard_clear()
      r.clipboard_append(text)
      r.destroy()

def plugin_start():
    """
    Load this plugin into EDMC
    """
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
    plugin_app.bg = 'grey4' if plugin_app.theme else 'grey'
    for module in plugin_app.wafer_module_classes:
        plugin_app.wafer_modules[module[0]] = module[1](plugin_app.frame, highlightbackground=plugin_app.fg, highlightcolor=plugin_app.fg, highlightthickness = 1)#, relief = tk.SUNKEN, borderwidth = 1)
        plugin_app.frame.add(plugin_app.wafer_modules[module[0]], module[0])
    with open(path.join(plugin_path,'flat_ships.json')) as json_data:
        plugin_app.FLAT_SHIPS = json.load(json_data)
    print "L3-37 loaded"
    return (plugin_app.frame)
    
def plugin_prefs(parent):
    frame = nb.Frame(parent)
    EDSM_id_label = nb.Label(frame, text="To view your ships in EDSM,\nenter the numbers that follow id/\nin the URL for your EDSM profile page: ", justify = tk.LEFT)
    EDSM_id_label.grid(column = 0, row = 0)
    this.EDSM_id_entry = nb.Entry(frame)
    this.EDSM_id_entry.grid(column = 1, row = 0)
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

def journal_entry(cmdr, system, station, entry, state):
    for key, module in plugin_app.wafer_modules.iteritems():
        try:
            module.journal_entry(cmdr, system, station, entry, state)
        except Exception as exc:
            print(traceback.format_exc())
            print(exc)

def dashboard_entry(cmdr, is_beta, entry):
    for key, module in plugin_app.wafer_modules.iteritems():
        module.dashboard_entry(cmdr, is_beta, entry)


def cmdr_data(data, is_beta):
    for key, module in plugin_app.wafer_modules.iteritems():
        module.cmdr_data(data, is_beta)

def getclipboard():
    r = tk.Tk()
    clip_text = r.clipboard_get()
    r.destroy()
    return(clip_text)