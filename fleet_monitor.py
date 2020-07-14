import json
import urllib

try:
    # Python 2
    import Tkinter as tk
except ModuleNotFoundError:
    # Python 3
    import tkinter as tk

from os import path

from companion import ship_map

from special_frames import *

from web_handlers import *

from wafer_module import WaferModule

from ttkHyperlinkLabel import HyperlinkLabel

from config import config

plugin_path = path.join(config.plugin_dir, "edmc-L3-37")

with open(path.join(plugin_path,'coriolis-dist.json')) as json_data:
    coriolis_dist = json.load(json_data)

with open(path.join(plugin_path,'flat_ships.json')) as json_data:
    FLAT_SHIPS = json.load(json_data)

def setclipboard(text):
    r = tk.Tk()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.destroy()
    
class ShipFrame(tk.Frame):
    def __init__(self, parent, ship_data, cmdr, bg = None, fg = 'black', hl = 'blue', *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        self.cmdr = cmdr
        self.grid_columnconfigure(0, weight = 1)
        self.build_ui()
        self.update_ship(ship_data, self.cmdr)
#        if self.theme:
        for element in [self.ship_link, self.station_link, self.system_link]:
            element.config(background = bg, foreground = hl)
        for element in [self.sys_label, self.station_label]:
            element.config(background = bg, foreground = fg)
        self.sub_frame.config(background = bg)
        
    def update_ship(self, ship_data, cmdr):
        self.cmdr = cmdr
        self.ship_data = ship_data
        if 'shipName' in ship_data:
            self.ship_lbl_txt = u"{} ({})".format(ship_data['shipName'],ship_map[ship_data['name'].lower()])
        else:
            self.ship_lbl_txt = ship_map[ship_data['name'].lower()]
        self.sysname = ship_data['starsystem']['name']
        self.stationname = ship_data['station']['name']
        self.sys_url = get_system_url(self.sysname)
        self.station_url = get_station_url(self.sysname, self.stationname)
        self.system_link.set_system(self.sysname)
        self.station_link.set_station(self.sysname, self.stationname)
        edID = FLAT_SHIPS[self.ship_data['name'].lower()]['edID']
        if config.get('L3_shipyard_provider') == 'Inara':
            self.ship_url = ship_data["shipInaraURL"]
        else:
            self.ship_url = "https://www.edsm.net/en/user/fleet/id/{}/cmdr/{}/ship/sId/{}/sType/{}".format(config.get('EDSM_id'), urllib.parse.quote_plus(self.cmdr), self.ship_data['id'], edID)
        # https://inara.cz/cmdr-fleet/
        self.ship_link.configure(url = self.ship_url, text = self.ship_lbl_txt)
        #self.station_link.configure(url = self.station_url, text = self.stationname)
        
    def build_ui(self):
        self.sub_frame = tk.Frame(self)
        self.ship_link = HyperlinkLabel(self, text = '', justify=tk.LEFT, anchor='w', url = None)
        self.system_link = SystemLinkLabel(self.sub_frame, text = '', justify=tk.LEFT, anchor='w', url = None)
        self.station_link = StationLinkLabel(self.sub_frame, text = '', justify=tk.LEFT, anchor='w', url = None)
        self.ship_link.grid(column = 0, row = 0, sticky = 'we')
        self.sub_frame.grid(sticky = 'we')
        self.sys_label = tk.Label(self.sub_frame, text = 'System: ', justify=tk.LEFT, anchor=tk.W, pady=0)
        self.sys_label.grid(column = 0, row = 1, sticky = 'we')
        self.system_link.grid(column = 1, row = 1, sticky = 'we')
        self.station_label = tk.Label(self.sub_frame, text = 'Station: ', justify=tk.LEFT, anchor=tk.W, pady=0)
        self.station_label.grid(column = 0, row = 2, sticky = 'we')
        self.station_link.grid(column = 1, row = 2, sticky = 'we')
        self.menu = tk.Menu(self, tearoff=0)

        self.menu.add_command(label="Copy system name", command = self.copySystem)
#        for i in [self.station_link, self.system_link]:
#            i.bind("<Button-3>", self.rightclick)
    def copySystem(self):
        setclipboard(self.sysname)
    def rightclick(self, event):
        self.menu.post(event.x_root, event.y_root)
        
class FleetMonitor(WaferModule):
    
    def __init__(self, parent, *args, **options):
        WaferModule.__init__(self, parent, *args, **options)
        self.theme = config.getint('theme')
        self.fg = config.get('dark_text') if self.theme else 'black'
        self.hl = config.get('dark_highlight') if self.theme else 'blue'
        self.bg = 'grey4' if self.theme else None
        self.ships = {}
        self.bigjsonships = {}
        self.DeadShip = None
        self.ship_widgets = {}
        try:
            with open(path.join(plugin_path, 'ships.json')) as json_data:
                self.bigjsonships = json.load(json_data)
        except:
            pass
        self.ships_scroll = VerticalScrolledFrame(self, bg = self.bg)
        self.ships_scroll.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        self.last_market_id = None
        
    def self_set(self, cmdr):
        self.cmdr = cmdr
        self.ships.clear()
        for widget in self.ship_widgets:
            widget.destroy()
        self.ship_widgets.clear()
        if self.cmdr in self.bigjsonships:
            for key, ship in self.bigjsonships[self.cmdr].items():
                if 'shipInaraURL' not in ship:
                    self.bigjsonships[self.cmdr][key]['shipInaraURL'] = 'https://inara.cz/cmdr-fleet/'
                for location in ['starsystem','station']:
                    if 'InaraURL' not in ship[location]:
                        self.bigjsonships[self.cmdr][key][location]['InaraURL'] = 'https://inara.cz/search/?searchglobal=' + urllib.parse.quote_plus(self.bigjsonships[self.cmdr][key][location]['name'])
                
            self.ships.update(self.bigjsonships[self.cmdr])
        else:
            self.bigjsonships.update({self.cmdr:{}})
            self.ships.update({})
            
    def build_ui(self):
        for key, widget in self.ship_widgets.items():
            if key not in self.ships:
                widget.forget()
            else:
                widget.update_ship(self.ships[key], self.cmdr)
        for ship in self.ships:
            if ship not in self.ship_widgets:
                self.ship_widgets.update({ship: ShipFrame(self.ships_scroll.interior, self.ships[ship], self.cmdr, highlightthickness = 1, bg = self.bg, fg = self.fg, hl = self.hl)})
                if self.theme:
                    self.ship_widgets[ship].config(background = self.bg)
            self.ship_widgets[ship].pack(fill = tk.BOTH, expand = 1)
        for key, widget in self.ship_widgets.items():
            widget.config(highlightbackground=self.fg, highlightcolor=self.fg)
            
        if self.theme:
            self.ships_scroll.interior.config(background = self.bg)
            
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
                #del self.ships[ship]["station"]["id"]
                del self.ships[ship]["value"]
                del self.ships[ship]["free"]
                self.ships[ship]["shipInaraURL"] = 'https://inara.cz/cmdr-fleet/'
                for location in ['starsystem','station']:
                    self.ships[ship][location]["InaraURL"] ='https://inara.cz/search/?searchglobal=' + urllib.parse.quote_plus(self.ships[ship][location]['name'])
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
            
        if entry['event'] == 'Docked':
            self.last_market_id = entry['MarketID']
        elif entry['event'] == 'Undocked':
            self.last_market_id = None
        if (state['Captain'] == None) and (system != None) and state['ShipType']:
            
            current_ship_id = state['ShipID']
            self.current_ship_id = current_ship_id
            
            state_ship = {
                "id": current_ship_id,
                "name": state['ShipType'],
                "shipID": state['ShipIdent'],
                "shipName": state['ShipName'],
                "starsystem": {"name": system},
                "station": {"name": [station, 'In flight'][station == None],
                    'id': self.last_market_id
                    },
#                "starpos": state['StarPos'],
                'localised_name': ship_map[state['ShipType'].lower()]
                }
                
            state_ship["shipInaraURL"] = self.ships[str(current_ship_id)]["shipInaraURL"]
            for location in ['starsystem','station']:
                try:
                    state_ship[location]["InaraURL"] = self.ships[str(current_ship_id)][location]["InaraURL"]
                except:
                    state_ship[location]["InaraURL"] = 'https://inara.cz/search/?searchglobal=' + urllib.parse.quote_plus(self.ships[ship][location]['name'])
            
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
                    "station": {"name": station,
                        'id': self.last_market_id,
                        },
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
            
    def inara_notify_ship(self, eventData):
        if eventData.get('shipInaraURL'):
            if self.ships[str(self.current_ship_id)]["shipInaraURL"] != eventData['shipInaraURL']:
                self.ships[str(self.current_ship_id)]["shipInaraURL"] = eventData['shipInaraURL']
                self.build_ui()
                self.bigjsonships.update({self.cmdr: self.ships})
                with open(path.join(plugin_path, 'ships.json'), 'w') as fp:
                    json.dump(self.bigjsonships, fp, indent = 2, sort_keys=True)
            
    def inara_notify_location(self, eventData):
        write_file = False
        for location in ['starsystem','station']:
            if eventData.get(location + 'InaraURL'):
                if self.ships[str(self.current_ship_id)][location]['InaraURL'] != eventData[location + 'InaraURL']:
                    self.ships[str(self.current_ship_id)][location]['InaraURL'] = eventData[location + 'InaraURL']
                    write_file = True
        if write_file:
            self.build_ui()
            self.bigjsonships.update({self.cmdr: self.ships})
            with open(path.join(plugin_path, 'ships.json'), 'w') as fp:
                json.dump(self.bigjsonships, fp, indent = 2, sort_keys=True)