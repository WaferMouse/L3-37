import Tkinter as tk
import ttk
from os import path
from config import config
from urlparse import urlparse
import webbrowser
import json
import urllib
import tkMessageBox

import os

import math

#settings_open = False

plugin_path = path.join(config.plugin_dir, "edmc-L3-37")

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
                        yscrollcommand=vscrollbar.set, height = 200, width = 500)#, background='grey4')
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas, background='grey4')
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

#        self.sub_frame = tk.Frame(self)
#        self.sub_frame.pack()
        #tk.Button(self, text = '', command = lambda x=i: select_layout(x))
        
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

class SystemFrame(tk.Frame):
    
    def __init__(self, parent, system_name, distance = 0, jumps = 1, is_neutron = False, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        
        self.system_name = system_name
        self.distance = distance
        self.jumps = jumps
        self.is_neutron = is_neutron
        
        self.name_lbl = tk.Label(self, text = system_name)
        self.name_lbl.pack(anchor = tk.W)
        
        if distance != 0:
            self.distance_lbl = tk.Label(self, text = distance_name)
            self.distance_lbl.pack(anchor = tk.W)
            
        if jumps != 1:
            self.jumps_lbl = tk.Label(self, text = jumps)
            self.jumps_lbl.pack(anchor = tk.W)

class WaferModule(tk.Frame):
    
    def __init__(self, parent, text = '', *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        
    def on_ED_event(self, event):
        """
        Handle events that are delegated to this module.
        """
        pass

class FleetMonitor(WaferModule):
    
    def __init__(self, parent, text = '', *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        pass

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
    #    self.lat_label.grid(row=1, column=0)
    #    self.target_lat.grid(row=1, column=1, sticky = "nsew")
    #    self.lon_label.grid(row=1, column=2)
    #    self.target_lon.grid(row=1, column=3, sticky = "nsew")
        self.bearing_frame.grid(row=0, column=1, sticky = "nsew")
        self.lbl_left.grid(row=0, column=0)
        self.bearing.grid(row=0, column=1)
        self.lbl_right.grid(row=0, column=2)
        self.set_btn.grid(row=0, column=2, sticky="e")
        
    def on_ED_event(self, event):
        if event['event'] == 'dashboard_entry':
            if "Latitude" in event['payload']:
                try:
                    current_lat_lon = (event['payload']["Latitude"], event['payload']["Longitude"])
                    target_lat_lon = (float(self.target_lat.get()), float(self.target_lon.get()))
                    bearing = calculate_initial_compass_bearing(current_lat_lon, target_lat_lon)
                    txt_bearing = "%.2f" % bearing
                    correction = (360 + (bearing - event['payload']['Heading'])) % 360
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

class NeutronNavigation(tk.Frame):
    
    def __init__(self, parent, text = '', *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(fill = tk.BOTH, expand = 1)
        
        self.paste_button = tk.Button(self.control_frame, text = 'Paste spansh URL', command = self.paste_spansh_url)
        
        self.copy_button = tk.Button(self.control_frame, text = 'Copy next system', command = self.copy_next_system)
        self.clear_route_button = tk.Button(self.control_frame, text = 'Clear route', command = self.user_clear_route)
        
        self.details_frame = ToggledFrame(self, text = 'Details')
        self.details_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        
        self.dyn_widgets = []
        
        self.clear_route()
        
        self.details_scroll = VerticalScrolledFrame(self.details_frame.sub_frame)
        self.details_scroll.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        
        try:
            with open(path.join(plugin_path, 'route.json')) as json_data:
                self.route = json.load(json_data)
            self.process_route()
            system_count = len(self.queued_systems)
            with open(path.join(plugin_path, 'queue.json')) as json_data:
                self.queued_systems = json.load(json_data)
            system_count = system_count - len(self.queued_systems)
            for i in range(system_count):
                self.dyn_widgets[0].destroy()
                del self.dyn_widgets[0]
            self.paste_button.forget()
            self.copy_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
            self.clear_route_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
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
        self.queued_systems = []
        self.route = {}
        self.next_waypoint_str = ''
        self.dyn_widgets = []
        self.clear_route_button.forget()
        self.copy_button.forget()
        self.paste_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

    def paste_spansh_url(self, event=''):
    #    global bigjson
        o = getclipboard()
        disassembled = urlparse(o)
        url, scrap = path.splitext(path.basename(disassembled.path))
        url = 'https://spansh.co.uk/api/results/' + url
        print(url)
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        print(data)
        
        self.route = data
        try:
            self.process_route()
            self.paste_button.forget()
            self.copy_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
            self.clear_route_button.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
            
            with open(path.join(plugin_path, 'route.json'), 'w') as fp:
                json.dump(self.route, fp, indent = 2, sort_keys=True)
            with open(path.join(plugin_path, 'queue.json'), 'w') as fp:
                json.dump(self.queued_systems, fp, indent = 2, sort_keys=True)
        except:
            tkMessageBox.showerror("Error", "Could not load route. You may need to request an updated route from spansh.")
                
    def process_route(self):
        
        for i in self.route['result']['system_jumps']:
            name = i['system']
            print(name)
            is_neutron = i['neutron_star']
            print(is_neutron)
            self.dyn_widgets.append(SystemFrame(self.details_scroll.interior, name, is_neutron = is_neutron))
            self.dyn_widgets[-1].pack(fill = tk.BOTH, expand = 1)
            self.queued_systems.append(name.lower())
            
        self.next_waypoint_str = self.queued_systems[0]
            
    def journal_entry(self, cmdr, system, station, entry):
        event = entry["event"]
        if event == 'FSDJump':
            starsystem = entry["StarSystem"]
            self.check_starsystem(starsystem)
            
                    
    def check_starsystem(self, system):
        if system.lower() in self.queued_systems:
            systems_to_delete = self.queued_systems.index(system.lower())+1
            for i in range(systems_to_delete):
                del self.queued_systems[0]
                self.dyn_widgets[0].destroy()
                del self.dyn_widgets[0]
            if self.queued_systems == []:
                self.clear_route()
                for i in ['route.json', 'queue.json']:
                    if os.path.exists(path.join(plugin_path, i)):
                        os.remove(path.join(plugin_path, i))
            else:
                self.next_waypoint_str = self.queued_systems[0]
                self.copy_next_system()
                with open(path.join(plugin_path, 'queue.json'), 'w') as fp:
                    json.dump(self.queued_systems, fp, indent = 2, sort_keys=True)
                
    def copy_next_system(self, event=''):
        setclipboard(self.next_waypoint_str)

def setclipboard(text):
      r = tk.Tk()
      r.clipboard_clear()
      r.clipboard_append(text)
      r.destroy()
        
#        for i in self.dyn_widgets:
#            i.grid()
    #    process_route(data)
    #    bigjson.append(data)
    #    with open(path.join(plugin_path, 'route.json'), 'w') as fp:
    #        json.dump(bigjson, fp, indent = 2, sort_keys=True)
    #    listicle = []
    #    for i in bigjson:
    #        viapoints = i["result"]["source_system"] + "->"
    #        try:
    #            for x in i["result"]["via"]:
    #                viapoints = viapoints + x + "->"
    #        except:
    #            pass
    #        viapoints = viapoints + i["result"]["destination_system"]
    #        listicle.append(viapoints)
    #  plugin_app.selectroute.configure(values = listicle)
    #  plugin_app.selectroute.current(len(listicle)-1)
        

def plugin_start():
    """
    Load this plugin into EDMC
    """
    print "L3-37 started"
    return "zz L3-37"

def plugin_app(parent):
    """
    Create a TK widget for the EDMC main window
    """
    plugin_app.frame = FakeNotebook(parent, text = 'L3-37')
#    plugin_app.surface_frame = tk.Frame(plugin_app.frame, relief = tk.SUNKEN, borderwidth = 1)
    plugin_app.surface_frame = SurfaceNavigation(plugin_app.frame, relief = tk.SUNKEN, borderwidth = 1)
    plugin_app.neutron_frame = NeutronNavigation(plugin_app.frame, relief = tk.SUNKEN, borderwidth = 1)
    plugin_app.frame.add(plugin_app.surface_frame, 'Surface navigation')
    plugin_app.frame.add(plugin_app.neutron_frame, 'Neutron navigation')
    '''
    plugin_app.lbl_frm = tk.Frame(plugin_app.surface_frame)
    plugin_app.lbl = tk.Label(plugin_app.lbl_frm, text="Bearing:", anchor=tk.W)
    plugin_app.target_lat = tk.Entry(plugin_app.surface_frame, width=1)
    plugin_app.lat_label = tk.Label(plugin_app.surface_frame, text='Lat:')
    plugin_app.target_lon = tk.Entry(plugin_app.surface_frame, width=1)
    plugin_app.lon_label = tk.Label(plugin_app.surface_frame, text='Lon:')
    plugin_app.bearing_frame = tk.Frame(plugin_app.lbl_frm)
    plugin_app.set_btn = tk.Button(plugin_app.lbl_frm, text='Set', command = toggle_settings)
    plugin_app.lbl_left = tk.Label(plugin_app.bearing_frame, text='<', width=1)
    plugin_app.lbl_right = tk.Label(plugin_app.bearing_frame, text='>', width=1)
    plugin_app.bearing = tk.Label(plugin_app.bearing_frame, text='', width=6)
    plugin_app.lbl_frm.grid(row=0,column=0, columnspan=4, sticky='nsew')
    plugin_app.lbl_frm.grid_columnconfigure(0, weight=1, uniform="fred")
    plugin_app.lbl_frm.grid_columnconfigure(1, weight=1, uniform="fred")
    plugin_app.lbl_frm.grid_columnconfigure(2, weight=1, uniform="fred")
    plugin_app.surface_frame.grid_columnconfigure(1, weight=1)
    plugin_app.surface_frame.grid_columnconfigure(3, weight=1)
    plugin_app.lbl.grid(sticky=tk.W)
#    plugin_app.lat_label.grid(row=1, column=0)
#    plugin_app.target_lat.grid(row=1, column=1, sticky = "nsew")
#    plugin_app.lon_label.grid(row=1, column=2)
#    plugin_app.target_lon.grid(row=1, column=3, sticky = "nsew")
    plugin_app.bearing_frame.grid(row=0, column=1, sticky = "nsew")
    plugin_app.lbl_left.grid(row=0, column=0)
    plugin_app.bearing.grid(row=0, column=1)
    plugin_app.lbl_right.grid(row=0, column=2)
    plugin_app.set_btn.grid(row=0, column=2, sticky="e")
    '''
    print "L3-37 loaded"
    return (plugin_app.frame)
'''
def toggle_settings():
    global settings_open
    if settings_open == False:
        plugin_app.lat_label.grid(row=1, column=0)
        plugin_app.target_lat.grid(row=1, column=1, sticky = "nsew")
        plugin_app.lon_label.grid(row=1, column=2)
        plugin_app.target_lon.grid(row=1, column=3, sticky = "nsew")
        plugin_app.set_btn.config(text='OK')
        settings_open = True
    else:
        plugin_app.lat_label.grid_forget()
        plugin_app.target_lat.grid_forget()
        plugin_app.lon_label.grid_forget()
        plugin_app.target_lon.grid_forget()
        plugin_app.set_btn.config(text='Set')
        settings_open = False
'''

def scrub_journal_entry(cmdr, system, station, entry, state):
    global settings_open
    if entry['event'] == 'Location':
        if 'Latitude' in entry:
            plugin_app.lbl_frm.grid(row=0,column=0, columnspan=4, sticky='nsew')
        else:
            settings_open = True
            toggle_settings()
            plugin_app.lbl_frm.grid_forget()
    elif entry['event'] == 'ApproachBody':
        plugin_app.lbl_frm.grid(row=0,column=0, columnspan=4, sticky='nsew')
    elif entry['event'] in ['LeaveBody','FSDJump']:
        settings_open = True
        toggle_settings()
        plugin_app.lbl_frm.grid_forget()

def scrub_dashboard_entry(cmdr, is_beta, entry):
    if "Latitude" in entry:
        try:
            current_lat_lon = (entry["Latitude"], entry["Longitude"])
            target_lat_lon = (float(plugin_app.target_lat.get()), float(plugin_app.target_lon.get()))
            bearing = calculate_initial_compass_bearing(current_lat_lon, target_lat_lon)
            txt_bearing = "%.2f" % bearing
            correction = (360 + (bearing - entry['Heading'])) % 360
            plugin_app.bearing.config(text=txt_bearing)
            if 1 < correction < 180:
                plugin_app.lbl_right.config(text=">")
            else:
                plugin_app.lbl_right.config(text="")
            if 180 < correction < 359:
                plugin_app.lbl_left.config(text="<")
            else:
                plugin_app.lbl_left.config(text="")
        except:
            plugin_app.bearing.config(text="!")
            plugin_app.lbl_left.config(text="<")
            plugin_app.lbl_right.config(text=">")
    else:
        plugin_app.bearing.config(text="")
        plugin_app.lbl_left.config(text="<")
        plugin_app.lbl_right.config(text=">")

def getclipboard():
    r = tk.Tk()
    clip_text = r.clipboard_get()
    r.destroy()
    return(clip_text)