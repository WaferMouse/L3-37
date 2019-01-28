#EngineerCraft
#ApplyExperimentalEffect

import Tkinter as tk
from wafer_module import WaferModule

import sys

from dialog import Dialog

from os import path

from config import config

from collections import OrderedDict

import json

this = sys.modules[__name__]

plugin_path = path.join(config.plugin_dir, "edmc-L3-37")

with open(path.join(plugin_path,'materials.json')) as json_data:
    materials = json.load(json_data)
    
with open(path.join(plugin_path,'mat_alias.json')) as json_data:
    mat_alias = json.load(json_data)
    
with open(path.join(plugin_path,'mat_trader.json')) as json_data:
    trader_map = json.load(json_data)
    
with open(path.join(plugin_path,'blueprints.json')) as json_data:
    blueprints = json.load(json_data, object_pairs_hook=OrderedDict)
    
with open(path.join(plugin_path,'coriolis-dist.json')) as json_data:
    coriolis_dist = json.load(json_data)
    
with open(path.join(plugin_path,'coriolis_module_cats.json')) as json_data:
    coriolis_module_cats = json.load(json_data)

trades = {}

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
        self.interior = interior = tk.Frame(canvas)#, background=plugin_app.bg)
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

class BlueprintFrame(tk.Frame):
    
    def __init__(self, parent, granny, name, int_name, components, foreground, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        self.background = self.cget('background')
        self.foreground = foreground
        self.granny = granny
        self.count = 0
        self.name = name
        self.int_name = int_name
        self.components = components
        self.label = tk.Label(self, text = name, wraplength = 160, background = self.background, foreground = self.foreground)
        self.label.pack(side = 'left')
        self.control_frm = tk.Frame(self, background = self.background)
        self.control_frm.pack(side = 'right', anchor = 'e', fill = 'y')
        self.minus_btn = tk.Button(self.control_frm, text = '-', command = self.sell_blueprint, state = tk.DISABLED, background = self.background, foreground = self.foreground)
        self.minus_btn.pack(side = 'left', fill = 'y')
        self.count_lbl = tk.Label(self.control_frm, text = '0', background = self.background, foreground = self.foreground)
        self.count_lbl.pack(side = 'left', fill = 'y')
        self.plus_btn = tk.Button(self.control_frm, text = '+', command = self.buy_blueprint, background = self.background, foreground = self.foreground)
        self.plus_btn.pack(side = 'left', fill = 'y')
        
    def sell_blueprint(self):
        self.apply_blueprint(-1)
    
    def buy_blueprint(self):
        self.apply_blueprint(1)
        
    def apply_blueprint(self, diff):
        self.count = self.count + diff
        self.count_lbl.config(text = self.count)
        if diff == 1:
            self.minus_btn.config(state = tk.NORMAL)
        for k, v in self.components.iteritems():
            for cat in materials:
                if k in materials[cat]:
                    materials[cat][k]['need'] = materials[cat][k]['need'] + (v * diff)
                    materials[cat][k]['simulated'] = materials[cat][k]['simulated'] - (v * diff)
        if self.count == 0:
            self.minus_btn.config(state = tk.DISABLED)
            
        self.granny.check_mats()

class MatFrame(tk.Frame):
    
    def __init__(self, parent, name_local, name, cat, subcat, grade, granny, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        self.selected = tk.IntVar()
        self.traded = 0
        self.granny = granny
        self.name = name
        self.cat = cat
        self.subcat = subcat
        self.grade = grade
        self.name_local = name_local
        self.label_btn = tk.Checkbutton(self, text = self.name_local, wraplength = 85, var = self.selected, indicatoron = False, command = self.toggle)
        self.label_btn.pack(fill='both', expand = 1)
        self.control_frm = tk.Frame(self)
        self.control_frm.pack()
        self.minus_btn = tk.Button(self.control_frm, text = u"\u23F5", state = tk.DISABLED, command = self.do_minus_btn)
        self.trade_lbl = tk.Label(self.control_frm, text = materials[cat][name]['simulated'])
        self.plus_btn = tk.Button(self.control_frm, text = u"\u23F4", state = tk.DISABLED, command = self.do_plus_btn)
        self.minus_btn.grid(row = 0, column = 0, sticky = 's')
        self.trade_lbl.grid(row = 0, column = 1, sticky = 's')
        self.plus_btn.grid(row = 0, column = 2, sticky = 's')
        if materials[cat][name]['simulated'] < 0:
            self.label_btn.config(foreground = 'red', disabledforeground = 'red')
        else:
            self.label_btn.config(foreground = 'black', disabledforeground = 'black')
        
    def toggle(self):
        if self.selected.get():
            self.granny.selected_mat((self.subcat, self.grade))
        else:
            self.granny.selected_mat(None)
            self.granny.end_trade()
            
    def find_power(self, grade, subcat):
        diff = grade - self.granny.selected[1]
        if subcat == self.granny.selected[0] and grade != self.granny.selected[1]:
            if diff > 0:
                power = 3**diff
            else:
                power = 6**(0 - diff)
        elif subcat != self.granny.selected[0]:
            if diff > 0:
                power = 3**(diff - 1)
            else:
                power = 6**((0 - diff) + 1)
        else:
            power = None
        return(power)
        
    def do_plus_btn(self):
        self.do_trade(1)
        
    def do_minus_btn(self):
        self.do_trade(-1)
    
    def do_trade(self, modifier):
        diff = self.grade - self.granny.selected[1]
        sim = materials[self.cat][self.name]['simulated']
        power = self.find_power(self.grade, self.subcat)
        if self.subcat == self.granny.selected[0]:
            small = 1
            out_subcat = self.subcat
        elif self.subcat != self.granny.selected[0]:
            small = 2
            out_subcat = self.granny.selected[0]
        if diff > 0:
            in_val = small
            out = power
        else:
            out = small
            in_val = power
        materials[self.cat][self.name]['simulated'] = sim + ((0 - modifier) * in_val)
        out_sim = materials[self.cat][trader_map[self.cat][out_subcat][self.granny.selected[1] - 1]]['simulated']
        materials[self.cat][trader_map[self.cat][out_subcat][self.granny.selected[1] - 1]]['simulated'] = out_sim + (modifier * out)
        self.traded = self.traded + (modifier * in_val)
        self.granny.prepare_trade()
            
    def prepare_trade(self):
        diff = self.grade - self.granny.selected[1]
        sim = materials[self.cat][self.name]['simulated']
        power = self.find_power(self.grade, self.subcat)
        if self.subcat == self.granny.selected[0]:
            min = 1
        else:
            min = 2
        if diff > 0:
            if sim >= min:
                self.plus_btn.config(state = tk.NORMAL)
            else:
                self.plus_btn.config(state = tk.DISABLED)
            self.selected.set(0)
        elif self.subcat == self.granny.selected[0] and self.grade == self.granny.selected[1]:
            pass
        else:
            if sim > power:
                self.plus_btn.config(state = tk.NORMAL)
            else:
                self.plus_btn.config(state = tk.DISABLED)
            self.selected.set(0)
        if self.traded > 0:
            self.minus_btn.config(state = tk.NORMAL)
        else:
            self.minus_btn.config(state = tk.DISABLED)
        self.trade_lbl.config(text = sim)
        if materials[self.cat][self.name]['simulated'] < 0:
            self.label_btn.config(foreground = 'red', disabledforeground = 'red')
        else:
            self.label_btn.config(foreground = 'black', disabledforeground = 'black')
            
    def end_trade(self):
        self.minus_btn.config(state = tk.DISABLED)
        self.plus_btn.config(state = tk.DISABLED)
        self.trade_lbl.config(text = materials[self.cat][self.name]['simulated'])
        self.traded = 0

class MatDialog(Dialog):
    def draw_mat_table(self, cat):
        self.selected = None
        self.trade_frame = VerticalScrolledFrame(self.main_frame)
        self.trade_frame.pack(fill='both', expand = 1)
        self.mat_frames = {}
        y = 0
        for subcat, v in trader_map[cat].iteritems():
            x = 0
            for i in v:
                self.mat_frames[i] = MatFrame(self.trade_frame.interior, materials[cat][i]['name_local'], i, cat, subcat, x + 1, self, highlightbackground='black', highlightcolor='black', highlightthickness = 1)
                self.mat_frames[i].grid(column = x, row = y, sticky = 'nsew')
                x = x + 1
            y = y + 1
        
    def selected_mat(self, mat):
        self.selected = mat
        self.prepare_trade()
        
    def prepare_trade(self):
        if self.selected != None:
            for k, v in self.mat_frames.iteritems():
                v.prepare_trade()
        
    def end_trade(self):
        for k, v in self.mat_frames.iteritems():
            v.end_trade()

    def buttonbox(self):
        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)

        box.pack()
        
    def apply(self):
        self.parent.check_mats()

class RawDialog(MatDialog):
    def body(self, master):
        self.main_frame = tk.Frame(master, )
        self.main_frame.pack(fill='both', expand = 1)
        self.draw_mat_table('raw')
        
class EncodedDialog(MatDialog):
    def body(self, master):
        self.main_frame = tk.Frame(master, )
        self.main_frame.pack(fill='both', expand = 1)
        self.draw_mat_table('encoded')
        
class ManufacturedDialog(MatDialog):
    def body(self, master):
        self.main_frame = tk.Frame(master, )
        self.main_frame.pack(fill='both', expand = 1)
        self.draw_mat_table('manufactured')

class MatsHelper(WaferModule):
    
    def __init__(self, parent, *args, **options):
        WaferModule.__init__(self, parent, *args, **options)
        self.parent = parent
        self.theme = config.getint('theme')
        self.fg = config.get('dark_text') if self.theme else 'black'
        self.hl = config.get('dark_highlight') if self.theme else 'blue'
        self.bg = 'grey4' if self.theme else 'grey'
        for cat in materials:
            for i in materials[cat]:
                materials[cat][i]['have'] = 0
                materials[cat][i]['simulated'] = 0
                materials[cat][i]['need'] = 0
        self.trader_frm_btns = {}
        self.tab_button_frm = tk.Frame(self)
        self.tab_button_frm.pack(fill = 'both', expand = 1)
        self.bp_frm = VerticalScrolledFrame(self)
        self.bps = []
        self.bp_frm.pack(fill='both', expand = 1)
        self.reset_btn = tk.Button(self, text = 'Reset', command = self.do_reset_btn)
        self.reset_btn.pack(fill='x', expand = 1)
        self.bpcats = []
        for cat in ['Encoded', 'Raw', 'Manufactured']:
            y = 0
            self.trader_frm_btns[cat] = tk.Button(self.tab_button_frm, text = cat, command = lambda x=cat: self.show_dialog(x))
            self.trader_frm_btns[cat].pack(side='left', fill = 'both', expand = 1)
        for slot in ['standard', 'internal', 'hardpoints']:
            for k, v in coriolis_dist['Modules'][slot].iteritems():
                cat_name = str(coriolis_module_cats[slot][k]).title()
                if k in coriolis_dist['Modifications']['modules']:
                    if len(coriolis_dist['Modifications']['modules'][k]['blueprints']) > 0:
                        self.bpcats.append(ToggledFrame(self.bp_frm.interior, text = cat_name, background = self.bg))
                        self.bpcats[-1].pack(fill = 'both', expand = 1)
                        self.bpcats[-1].title_frame.config(background = self.bg)
                        self.bpcats[-1].toggle_button.config(foreground = self.fg, background = self.bg)
                        self.bpcats[-1].sub_frame.config(background = self.bg)
                        for i in coriolis_dist['Modifications']['modules'][k]['blueprints']:
                            name = coriolis_dist['Modifications']['blueprints'][i]['name']
                            for grade in blueprints[i]['grades']:
                                int_name = i
                                friendly_name = name + ' G' + grade
                                components = coriolis_dist['Modifications']['blueprints'][i]['grades'][grade]['components']
                                self.bps.append(BlueprintFrame(self.bpcats[-1].sub_frame, self, friendly_name, int_name, components, foreground = self.fg, background = self.bg))
                                self.bps[-1].pack(fill = 'both', expand = 1)
                else:
                    print('{} is missing!'.format(cat_name))
        if self.theme:
            self.bp_frm.interior.config(background = self.bg)
            
    def do_reset_btn(self):
        for cat in materials:
            for i in materials[cat]:
                materials[cat][i]['simulated'] = materials[cat][i]['have']
                materials[cat][i]['need'] = 0
                
        for bp in self.bps:
            bp.count = 0
            bp.count_lbl.config(text = 0)
            
    def show_dialog(self, cat):
        if cat == 'Raw':
            self.dialog = RawDialog(self, title="Raw trade")
        elif cat == 'Encoded':
            self.dialog = EncodedDialog(self, title="Encoded trade")
        else:
            self.dialog = ManufacturedDialog(self, title="Manufactured trade")
            
        self.dialog = None
        
    def check_mats(self):
        for cat in materials:
            passed = True
            for i in materials[cat]:
                if materials[cat][i]['simulated'] < 0:
                    passed = False
            if passed == True:
                self.trader_frm_btns[cat.title()].config(foreground = self.fg)
            else:
                self.trader_frm_btns[cat.title()].config(foreground = 'red')
        
    def journal_entry(self, cmdr, system, station, entry, state):
        for cat in ['Encoded', 'Raw', 'Manufactured']:
            cat_lower = cat.lower()
            for k, v in state[cat].iteritems():
                mat = mat_alias[cat_lower][k]
                diff = v - materials[cat_lower][mat]['have']
                materials[cat_lower][mat]['have'] = v
                materials[cat_lower][mat]['simulated'] = materials[cat_lower][mat]['simulated'] + diff