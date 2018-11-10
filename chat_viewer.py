import Tkinter as tk
from urlparse import urlparse
import webbrowser
from urllib import quote_plus
from wafer_module import WaferModule

from config import config

from web_handlers import *

debugoutput = False
links = []
linkcount = 0
lastsender = ""
systemlinks = []
systemcount = 0

idx = ''

tag_to_handle = ''

from datetime import datetime
import time

def on_tag_click(event, tag):
    global tag_to_handle
    tag_to_handle = tag

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

def setclipboard(text):
    r = tk.Tk()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.destroy()

def showLink(event):
    idx = int(event.widget.tag_names(tk.CURRENT)[1])
    webbrowser.open(links[idx])

def copyLink(event=''):
    setclipboard(links[idx])

def showSystem(event):
    idx = int(event.widget.tag_names(tk.CURRENT)[1])
    if config.get('system_provider') == 'eddb':
        webbrowser.open(EDDB_system_url(systemlinks[idx]))
    else:
        webbrowser.open('https://www.edsm.net/show-system?systemName=' + quote_plus(systemlinks[idx]))
#    webbrowser.open("https://www.edsm.net/show-system?systemName=" + quote_plus(systemlinks[idx]))

def copySystem(event=''):
    setclipboard(systemlinks[idx])

def copySystemLink(event=''):
    setclipboard("https://www.edsm.net/show-system?systemName=" + quote_plus(systemlinks[idx]))

class ChatViewer(WaferModule):
    
    def __init__(self, parent, *args, **options):
        WaferModule.__init__(self, parent, *args, **options)
        """
        Create a TK widget for the EDMC main window
        """
        self.status = tk.Text(self)
        self.chatcopy = tk.Button(self, text = "Copy", command = self.copy_button3)
        self.chatcopy.grid(row = 1, column = 0, columnspan = 4)
        self.status['width'] = 1
        self.status.grid(row=0, column = 0, columnspan = 3, sticky='nswe')
        for i in range(3):
            self.grid_columnconfigure(i, weight = 1)
        self.status.insert(tk.END,"Chat viewer loaded")
        self.status.config(state=tk.DISABLED)
        self.status.config(height=10, wrap='word')
        self.status.see(tk.END)
        self.status.bind('<Button-3>', lambda e, w='textwidget': self.on_click(e, w))
        self.status.bind('Control-x', self.copy_button3)
        self.status.tag_config('link', underline=1)
        self.status.tag_bind('link', '<Button-1>', showLink)
        self.status.tag_bind('link', '<Button-3>', lambda e, w='link': on_tag_click(e, w))
        self.status.tag_config('systemlink', underline=1)
        self.status.tag_bind('systemlink', '<Button-1>', showSystem)
        self.status.tag_bind('systemlink', '<Button-3>', lambda e, w='systemlink': on_tag_click(e, w))
        self.freeze = tk.IntVar(self)
        self.freezebutton = tk.Checkbutton(self, text="Freeze", variable = self.freeze)
        self.freezebutton.grid(row=2, column = 0, columnspan = 4)
        self.scroll = tk.Scrollbar(self, command=self.status.yview)
        self.scroll.grid(row=0, column=4, sticky='nsew')
        self.status['yscrollcommand'] = self.scroll.set
        self.systemMenu = tk.Menu(self, tearoff=0)
        self.systemMenu.add_command(label="Copy system name", command = copySystem)
#        self.systemMenu.add_command(label="Copy EDSM link", command = copySystemLink)
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Copy text (Ctrl x)", command = self.copy_button3)
        self.linkMenu = tk.Menu(self, tearoff=0)
        self.linkMenu.add_command(label="Copy link", command = copyLink)
        print "Chat Viewer loaded"

    def journal_entry(self, cmdr, system, station, entry, state):
        global links
        global linkcount
        global systemlinks
        global systemcount
        global lastsender
        eventtimestamp = datetime.strptime(entry["timestamp"], '%Y-%m-%dT%H:%M:%SZ')
        localeventtime = datetime_from_utc_to_local(eventtimestamp)
        localtimestamp = localeventtime.strftime('%H:%M')
        if debugoutput == True:
            self.status.config(state=tk.NORMAL)
            self.status.insert(tk.END, "\n{}".format(entry))
            self.status.see(tk.END)
            self.status.config(state=tk.DISABLED)
        event = entry["event"]
        display = False
        if event == "SendText":
            sender = cmdr
            display = True
            if entry['To'] in ["wing","voicechat","local"]:
                channel = entry['To'][0].upper()
            else:
                channel = entry['To']
        elif event == "ReceiveText":
            sender = entry["From"]
            try:
                if entry["Channel"] != "npc":
                    display = True
                    if entry["Channel"] == "player":
                        channel = "D"
                    else:
                        channel = entry["Channel"][0].upper()
            except:
                channel = "L"
                display = True
            
        elif event == "FSDJump" or event == "StartJump":
            formtext = {"FSDJump": "Arrived at",
                        "StartJump": "Jumping to",
                        }
            try:
                systemlinks.append(entry["StarSystem"])
                self.status.config(state=tk.NORMAL)
                self.status.insert(tk.END, "\n[{}] * {} ".format(localtimestamp,formtext[event]))
                self.status.insert(tk.END, "{}".format(entry["StarSystem"]), ('systemlink', systemcount))
                self.status.insert(tk.END, " *")
                systemcount = systemcount + 1
                if self.freeze.get() != 1:
                    self.status.see(tk.END)
                self.status.config(state=tk.DISABLED)
                if lastsender != cmdr:
                    lastsender = ''
            except:
                pass
        if display == True:
            self.status.config(state=tk.NORMAL)
            if sender != lastsender:
                self.status.insert(tk.END, "\nCMDR {}:".format(sender))
            self.status.insert(tk.END, "\n[{}][{}] ".format(localtimestamp, channel.upper()))
            for word in entry["Message"].split(' '):
                thing = urlparse(word.strip())
                if thing.scheme:
                    links.append(word)
                    self.status.insert(tk.END, "{} ".format(word), ('link', linkcount))
                    linkcount = linkcount + 1
                else:
                    self.status.insert(tk.END, "{} ".format(word))
            if self.freeze.get() != 1:
                self.status.see(tk.END)
            self.status.config(state=tk.DISABLED)
            lastsender = sender
            
    def systempopup(self, event):
        global idx
        idx = int(event.widget.tag_names(tk.CURRENT)[1])
        self.systemMenu.post(event.x_root, event.y_root)
        
    def linkpopup(self, event):
        global idx
        idx = int(event.widget.tag_names(tk.CURRENT)[1])
        self.linkMenu.post(event.x_root, event.y_root)
        
    def popup(self, event):
        self.menu.post(event.x_root, event.y_root)
        
    def on_click(self, event, widget_origin='?'):
        global tag_to_handle
        if tag_to_handle:
            if tag_to_handle == "systemlink":
              self.systempopup(event)
            elif tag_to_handle =="link":
              self.linkpopup(event)
            tag_to_handle = ''
        else:
            self.popup(event)

    def copy_button3(self, event=''):
        try:
            setclipboard(self.status.selection_get())
        except:
            pass