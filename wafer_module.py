try:
    # Python 2
    import Tkinter as tk
except ModuleNotFoundError:
    # Python 3
    import tkinter as tk

class WaferModule(tk.Frame):
    
    def __init__(self, parent, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        
    def journal_entry(self, cmdr, system, station, entry, state):
        """
        Handle events that are delegated to this module.
        """
        pass
        
    def dashboard_entry(self, cmdr, is_beta, entry):
        """
        Handle events that are delegated to this module.
        """
        pass
        
    def cmdr_data(self, data, is_beta):
        """
        Handle events that are delegated to this module.
        """
        pass
        
    def update_theme(self):
        pass
        
    def inara_notify_location(self, eventData):
        pass
        
    def inara_notify_ship(self, eventData):
        pass