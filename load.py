import Tkinter as tk
from os import path
from config import config
from urlparse import urlparse
import webbrowser
import json
import urllib
import tkMessageBox
import myNotebook as nb
import traceback

from special_frames import *

import sys

import os

this = sys.modules[__name__]	# For holding module globals

plugin_path = path.join(config.plugin_dir, "edmc-L3-37")

from web_handlers import *

from wafer_module import WaferModule

from chat_viewer import ChatViewer

from fsd_target import FSDTarget

from mats_helper import MatsHelper

from fleet_monitor import FleetMonitor

from surface_navigation import SurfaceNavigation
        
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
        
        self.details_scroll = VerticalScrolledFrame(self.details_frame.sub_frame, height = 100, bg = plugin_app.bg)
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

def getclipboard():
    r = tk.Tk()
    clip_text = r.clipboard_get()
    r.destroy()
    return(clip_text)