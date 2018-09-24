import Tkinter as tk
import webbrowser
import json
from urllib import quote_plus
from os import path

from config import config
from companion import ship_map

plugin_path = path.join(config.plugin_dir, "edmc-ships-master")

ships = {}
current_system = ""
current_ship_id = None
current_station = ""
current_starpos = None

class ship_frame(tk.Frame):
  def __init__(self, parent, ship_data, *args, **options):
    tk.Frame.__init__(self, parent, *args, **options)
    self.ship_data = ship_data
    self.elements = []
    self.ship_lbl_txt = tk.StringVar()
    if 'shipName' in ship_data:
      self.ship_lbl_txt.set("{} ({})".format(ship_data['shipName'],ship_map[ship_data['name'].lower()]))
    else:
      self.ship_lbl_txt.set(ship_map[ship_data['name'].lower()])
    self.elements.append(tk.Label(self, textvariable = self.ship_lbl_txt, justify=tk.LEFT, anchor=tk.W, pady=0))
    self.sysname = ship_data['starsystem']['name']
    self.elements.append(tk.Label(self, text = 'System: {}'.format(self.sysname), justify=tk.LEFT, anchor=tk.W, pady=0))
    self.elements.append(tk.Label(self, text = 'Station: {}'.format(ship_data['station']['name']), justify=tk.LEFT, anchor=tk.W, pady=0))
    def click(event):
      webbrowser.open("https://www.edsm.net/show-system?systemName=" + quote_plus(self.sysname))
    self.bind("<Button-1>", click)
    self.menu = tk.Menu(plugin_app.collapser.sub_frame, tearoff=0)
    def copySystem(event=''):
      setclipboard(self.sysname)

    def copySystemLink(event=''):
      setclipboard("https://www.edsm.net/show-system?systemName=" + quote_plus(self.sysname))

    self.menu.add_command(label="Copy system name", command = copySystem)
    self.menu.add_command(label="Copy EDSM link", command = copySystemLink)
    def rightclick(event):
      self.menu.post(event.x_root, event.y_root)
    self.bind("<Button-3>", rightclick)
    for i in self.elements:
      i.pack(fill="x")
      i.bind("<Button-1>", click)
      i.bind("<Button-3>", rightclick)

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set, height = 200, width = 500)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
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

class ToggledFrame(tk.Frame):

    def __init__(self, parent, text="", *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)

        self.show = tk.IntVar()
        self.show.set(1)
        self.text = text

        self.title_frame = tk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        self.toggle_button = tk.Label(self.title_frame,text= unichr(8862) + ' ' + text)
        self.toggle_button.pack(side="left")

        self.sub_frame = tk.Frame(self, relief="groove", borderwidth=1)

        def toggle(self):
            if bool(self.show.get()):
                self.sub_frame.pack(fill="x", expand=1)
                self.toggle_button.configure(text=unichr(8863) + ' ' + self.text)
                self.show.set(0)
            else:
                self.sub_frame.forget()
                self.toggle_button.configure(text= unichr(8862) + ' ' + self.text)
                self.show.set(1)

        def click(event):
          toggle(self)

        self.toggle_button.bind("<Button-1>",click)

def setclipboard(text):
  r = tk.Tk()
  r.clipboard_clear()
  r.clipboard_append(text)
  r.destroy()

def plugin_start():
  """
  Load this plugin into EDMC
  """
  print "Ships started"
  return "zz Ships"

def plugin_app(parent):
  """
  Create a TK widget for the EDMC main window
  """
  global ships
  global current_ship_id
  plugin_app.frame = tk.Frame(parent)
  plugin_app.collapser = ToggledFrame(plugin_app.frame, text = "Ships")
  plugin_app.collapser.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
  plugin_app.scrolly = VerticalScrolledFrame(plugin_app.collapser.sub_frame)
  plugin_app.scrolly.grid(row=0, column = 0, columnspan = 2)
  temp_label = tk.Label(plugin_app.scrolly.interior, text = "Click 'Update' to see your ships.", justify=tk.LEFT, anchor=tk.W, pady=0)
  temp_label.pack()
  try:
    with open(path.join(plugin_path, 'ships.json')) as json_data:
      o = json.load(json_data)
    ships = o["ships"]
    current_ship_id = o["current_ship_id"]
  except:
    pass
  if ships != {}:
    update_gui()
  print "Ships loaded"
  return (plugin_app.frame)

def journal_entry(cmdr, system, station, entry):
  global current_system
  global current_ship_id
  global current_station
  global current_starpos
  
  event = entry["event"]
  write_file = False
  
  if "ShipID" in entry:
    this_ship_id = str(entry["ShipID"])
  
  if "StarPos" in entry:
    if entry["StarPos"] != current_starpos:
      current_starpos = entry["StarPos"]
      write_file = True
    ships[str(current_ship_id)]["starpos"] = current_starpos
  
  if event in ["FSDJump", "Location", "Docked"]:
    if "StationName" in entry:
      if entry["StationName"] != current_station:
        current_station = entry["StationName"]
        write_file = True
    elif current_station != "???":
      current_station = "???"
      write_file = True
    ships[str(current_ship_id)]["station"]["name"] = current_station
    
    if entry["StarSystem"] != current_system:
      current_system = entry["StarSystem"]
      write_file = True
    ships[str(current_ship_id)]["starsystem"]["name"] = current_system
  
  elif event == "SetUserShipName":
    ships[this_ship_id]["shipName"] = entry["UserShipName"]
    ships[this_ship_id]["shipID"] = entry["UserShipId"]
    update_gui()
    update_file()
  
  elif event == "ShipyardNew":
    ships[this_ship_id] = {
      "id": entry["ShipID"],
      "name": entry["ShipType"],
      "starsystem": {"name": current_system }, 
      "station": {"name": current_station},
      "starpos": current_starpos,
    }
    update_gui()
    update_file()
  
  elif event == "ShipyardTransfer":
    ships[this_ship_id]["starsystem"]["name"] = current_system
    ships[this_ship_id]["station"]["name"] = current_station
    if current_starpos != None:
      ships[this_ship_id]["starpos"] = current_starpos
    update_gui()
    update_file()
  
  elif event == "ShipyardSwap":
    current_ship_id = entry["ShipID"]
    if current_starpos != None:
      ships[this_ship_id]["starpos"] = current_starpos
    write_file = True
    update_gui()
  
  elif event == "Resurrect":
    if entry["Option"] != "rebuy":
      del ships[str(current_ship_id)]
      write_file = True
  
  if "SellShipID" in entry:
    del ships[str(entry["SellShipID"])]
    write_file = True
    update_gui()
  
  if write_file:
    update_file()

def cmdr_data(data, is_beta):
  global ships
  global current_ship_id
  write_file = False
  if current_ship_id != data['ship']['id']:
    current_ship_id = data['ship']['id']
    write_file = True
  scrub_list = []
  for ship in ships:
    if ship not in data["ships"]:
      scrub_list.append[ship]
    else:
      for i in ["shipID", "shipName"]:
        try:
          if ships[ship][i] != data["ships"][ship][i]:
            ships[ship][i] = data["ships"][ship][i]
            write_file = True
        except:
          pass
  for ship in scrub_list:
    del ships[ship]
    write_file = True
  for ship in data["ships"]:
    if ship not in ships:
      ships[ship] = data["ships"][ship]
      del ships[ship]["starsystem"]["id"]
      del ships[ship]["starsystem"]["systemaddress"]
      del ships[ship]["station"]["id"]
      del ships[ship]["value"]
      del ships[ship]["free"]
      write_file = True
  if write_file:
    update_gui()
    update_file()

def update_file():
  with open(path.join(plugin_path, 'ships.json'), 'w') as fp:
    json.dump({"ships": ships, "current_ship_id":  current_ship_id}, fp, indent = 2, sort_keys=True)

def update_gui():
  plugin_app.scrolly.destroy()
  plugin_app.scrolly = VerticalScrolledFrame(plugin_app.collapser.sub_frame)
  plugin_app.scrolly.grid(row=0, column = 0, columnspan = 2)
  r = 0
  for ship in ships:
    this_ship = ships[ship]
    if this_ship["id"] != current_ship_id:
      this_ship_frame = ship_frame(plugin_app.scrolly.interior, this_ship, relief = tk.GROOVE, borderwidth = 2)
      this_ship_frame.grid(row = r, column = 0, sticky = tk.NE + tk.SW)
      r = r + 1