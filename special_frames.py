import Tkinter as tk

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, height = 200, bg = None, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        
        self.bg = bg

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
        self.interior = interior = tk.Frame(canvas, background=self.bg)
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

        self.toggle_button = tk.Label(self.title_frame,text= unichr(11208) + ' ' + text)
        self.toggle_button.pack(side="left")

        self.sub_frame = tk.Frame(self)

        def toggle(self):
            if bool(self.show.get()):
                self.sub_frame.pack(fill="x", expand=1)
                self.toggle_button.configure(text=unichr(11206) + ' ' + self.text)
                self.show.set(0)
            else:
                self.sub_frame.forget()
                self.toggle_button.configure(text= unichr(11208) + ' ' + self.text)
                self.show.set(1)

        def click(event):
          toggle(self)

        self.toggle_button.bind("<Button-1>",click)