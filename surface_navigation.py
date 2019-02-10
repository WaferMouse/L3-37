import Tkinter as tk

from wafer_module import WaferModule

import math

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