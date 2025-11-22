from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter.messagebox import *
from tkinter import font
from urllib.request import *
import re, html, webbrowser, datetime
import xml.etree.ElementTree as ET

def toggle_sidebar():
    if sidebar.grid_info() == {}:
        sidebar.grid(row=0, column=1, sticky="nsew")
    else:
        sidebar.grid_forget()
       
def import_rss():
    global rss_data
    try:
        filepath = askopenfilename(title="Import", filetypes=[("Really Simple Syndication", ".rss"), ("eXtensible Markup Language", ".xml")])
        print(filepath)
        if filepath != "":
            try:
                feed_id = f"File - {filepath.split('/')[-1]}"
                feed_id = re.sub(r'[\\/:*?"<>|]', "", feed_id)
            except:
                feed_id = "Unknown Feed"
            num = 2
            if feed_id in list(rss_data.keys()):
                temp_id = f"{feed_id} ({num})"
                while temp_id in list(rss_data.keys()):
                    num += 1
                    temp_id = f"{feed_id} ({num})"
                feed_id = temp_id
            rss_data[feed_id] = open(filepath, "r", encoding="utf8").read()
            url_dict[feed_id] = ""
            load_rss(feed_id)
    except:
        showerror("Headlines4pc", "An error occured when trying to access this feed.")

def open_rss():
    global rss_data
    try:
        if url_bar.get() != "":
            data = urlopen(url_bar.get()).read().decode("utf8")
            xml_root = ET.fromstring(data)
            try:
                feed_id = xml_root.findtext(".//channel/title")
                feed_id = re.sub(r'[\\/:*?"<>|]', "", feed_id)
            except:
                feed_id = "Unknown Feed"
            num = 2
            if feed_id in list(rss_data.keys()):
                temp_id = f"{feed_id} ({num})"
                while temp_id in list(rss_data.keys()):
                    num += 1
                    temp_id = f"{feed_id} ({num})"
                feed_id = temp_id
            rss_data[feed_id] = data
            url_dict[feed_id] = url_bar.get()
            url_bar.delete(0, END)
            load_rss(feed_id)
    except:
        showerror("Headlines4pc", "An error occured when trying to access this feed.")

def load_rss(feed_id):
    global current_feed_id, current_item_id
    sidebar.delete(0, END)
    for i in rss_data:
        sidebar.insert(END, i)
    current_feed_id = feed_id
    data = rss_data[feed_id]
    xml_root = ET.fromstring(data)
    feed = xml_root.findall(".//item")
    processed_feed_data[feed_id] = []
    current_item_id = 0
    item_id = current_item_id
    for item in feed:
        title = item.find("title")
        dt = item.find("pubDate")
        link = item.find("link")
        description = item.find("description")
        if title is not None:
            title = re.sub(r"<[^>]*>", "", html.unescape(title.text))
            if link is not None:
                link = re.sub(r"<[^>]*>", "", html.unescape(link.text))
        if dt is not None:
            dt = re.sub(r"<[^>]*>", "", html.unescape(dt.text))
        if description is not None:
            description = re.sub(r"<[^>]*>", "", html.unescape(description.text))
        item_rss = {"title": title, "pubDate": dt, "link": link, "description": description}
        processed_feed_data[feed_id].append(item_rss)
    load_item(feed_id, item_id)

def load_item(feed_id, item_id):
    global current_url
    buttonActions.configure(text=f"{item_id+1}/{len(processed_feed_data[current_feed_id])}")
    title = processed_feed_data[feed_id][item_id]["title"]
    dt = processed_feed_data[feed_id][item_id]["pubDate"]
    link = processed_feed_data[feed_id][item_id]["link"]
    description = processed_feed_data[feed_id][item_id]["description"]
    text.configure(state=NORMAL)
    text.delete(1.0, END)
    titleLabel.configure(text=title)
    dtLabel.configure(text=dt)
    current_url = link
    if description is not None:
        text.insert(END, f"{description}\n")
    text.focus_set()
    text.configure(state=DISABLED)
   
def copy():
    text.clipboard_clear()
    try:
        text.clipboard_append(text.get(SEL_FIRST, SEL_LAST))
    except:
        text.clipboard_append(text.get(1.0, END))

def help_window():
    window = Toplevel()
    window.title("Help - Headlines4pc")
    window.geometry("700x510")
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
    help_tabs = ttk.Notebook(window)
    help_tabs.grid(row=0, column=0, sticky="nsew")
    about = Text(help_tabs, relief=FLAT, border=16, font=(font.nametofont("TkDefaultFont").actual()["family"], 12), wrap=WORD, background="#dedede")
    about.insert(INSERT, f"Headlines4pc\nCopyright (c) 2025-{str(datetime.datetime.now().year)}: Waylon Boer\n\nHeadlines4pc is an RSS Feed reader with an easy-to-use user interface.")
    about.configure(state=DISABLED)
    help_tabs.add(about, text="About")
    mit_license = Text(help_tabs, relief=FLAT, border=16, font=(font.nametofont("TkDefaultFont").actual()["family"], 12), wrap=WORD, background="#dedede")
    mit_license.insert(INSERT, """MIT License

Copyright (c) 2025 Waylon Boer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""")
    mit_license.configure(state=DISABLED)
    help_tabs.add(mit_license, text="License")

def export_rss():
    filepath = asksaveasfilename(title="Export", defaultextension=".rss", filetypes=[("Really Simple Syndication", ".rss")])
    if filepath != "":
        open(filepath, "w", encoding="utf8").write(rss_data[current_feed_id])

def open_from_sidebar():
    try:
        load_rss(sidebar.get(ACTIVE))
    except:
        text.focus_set()

def export_from_sidebar():
    try:
        filepath = asksaveasfilename(defaultextension=".rss", filetypes=[("Really Simple Syndication", ".rss")])
        if filepath != "":
            open(filepath, "w", encoding="utf8").write(rss_data[sidebar.get(ACTIVE)])
    except:
        text.focus_set()

def export_all():
    directory = askdirectory(title="Export All")
    for feed_id in rss_data:
        open(f"{directory}/{feed_id}.rss", "w", encoding="utf8").write(rss_data[feed_id])

def close_from_sidebar():
    global current_feed_id
    try:
        feed_id = sidebar.get(ACTIVE)
        if current_feed_id == feed_id:
            titleLabel.configure(text="")
            dtLabel.configure(text="")
            text.configure(state=NORMAL)
            text.delete(1.0, END)
            text.configure(state=DISABLED)
            buttonActions.configure(text="Actions")
            current_feed_id = ""
            current_item_id = 0
        rss_data.pop(feed_id, None)
        url_dict.pop(feed_id, None)
        processed_feed_data.pop(feed_id, None)
        sidebar.delete(0, END)
        for i in rss_data:
            sidebar.insert(END, i)
    except:
        text.focus_set()

def toggle_theme():
    if text["bg"] == "#ffffff":
        bg, bg2, bg3, fg = "#111111", "#2d2d2d", "#3c3c3c", "#ffffff"
    else:
        bg, bg2, bg3, fg = "#ffffff", "#f0f0f0", "#e1e1e1", "#000000"
    reader.configure(bg=bg)
    for i in [titleLabel, dtLabel, text]:
        i.configure(bg=bg, fg=fg)
    text.tag_configure("sel", background=bg, foreground=fg)
    menubar.configure(bg=bg2)
    style.configure("TEntry", background=bg2)
    style.configure("TButton", background=bg2)
    sidebar.configure(bg=bg3, fg=fg)
    for i in [menu_B3, menuActions]:
        if bg == "#111111":
            i.configure(background="#000", foreground="#fff", activebackground="#333", activeforeground="#fff")
        else:
            i.configure(background="#f0f0f0", foreground="#000", activebackground="#ccc", activeforeground="#000")

def toggle_touch_mode():
    if url_bar.grid_info()["ipady"] == 0:
        url_bar.grid(row=0, column=3, sticky="nse", ipady=5)
    else:
        url_bar.grid(row=0, column=3, sticky="nse", ipady=0)

def refresh():
    try:
        load_rss(current_feed_id)
    except:
        showerror("Headlines4pc", "An error occured when trying to access this feed.")

def previous_item():
    global current_item_id
    if current_feed_id != "":
        if current_item_id > 0:
            current_item_id -= 1
        load_item(current_feed_id, current_item_id)

def next_item():
    global current_item_id
    if current_feed_id != "":
        if current_item_id < len(processed_feed_data[current_feed_id]) - 1:
            current_item_id += 1
        load_item(current_feed_id, current_item_id)

def view_data():
    if current_feed_id != "":
        app = Toplevel()
        app.title(f"Headlines4pc")
        app.geometry("800x600")
        treeview = ttk.Treeview(app)
        treeview.pack(fill="both", expand=True)
        treeview.heading("#0", text=current_feed_id)
        def insert_item(predecessor, element):
            treeview_item_id = treeview.insert(predecessor, "end", text=element.tag)
            for key, value in element.attrib.items():
                treeview.insert(treeview_item_id, "end", text=f"@{key}={value}")
            if element.text and element.text.strip():
                treeview.insert(treeview_item_id, "end", text=element.text.strip())
            for successor in element:
                insert_item(treeview_item_id, successor)
        insert_item("", ET.fromstring(rss_data[current_feed_id]))

rss_data = {}
url_dict = {}
current_feed_id = ""
current_item_id = 0
processed_feed_data = {}
current_url = ""

root = Tk()
root.title("Headlines4pc")
root.geometry("1000x600")
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

style = ttk.Style(root)
style.configure("TEntry", background="#e1e1e1")

menubar = Frame(root, bd=4)
menubar.grid(row=0, column=0, sticky="nsew")
menubar.columnconfigure(3, weight=1)
menubar.columnconfigure(4, weight=1)
buttonActions = ttk.Menubutton(menubar, text="Actions", style="TButton")
buttonActions.grid(row=0, column=0, sticky="nsw")
menuActions = Menu(buttonActions, tearoff=False, activeborderwidth=2.5)
menuActions.add_command(label="Copy", command=lambda: text.clipboard_append(text.get(1.0, END)))
menuActions.add_command(label="Open in browser", command=lambda: webbrowser.open_new_tab(current_url))
menuActions.add_command(label="View data", command=view_data)
menuActions.add_separator()
menuActions.add_command(label="Switch theme", command=toggle_theme)
menuActions.add_command(label="Full screen", command=lambda: root.attributes("-fullscreen", not root.attributes("-fullscreen")))
menuActions.add_separator()
menuActions.add_command(label="Help", command=help_window)
buttonActions.configure(menu=menuActions)
buttonPrevious = ttk.Button(menubar, text="Previous", command=previous_item)
buttonPrevious.grid(row=0, column=1, sticky="nsw")
buttonNext = ttk.Button(menubar, text="Next", command=next_item)
buttonNext.grid(row=0, column=2, sticky="nsw")

url_bar = ttk.Entry(menubar, width=40)
url_bar.grid(row=0, column=3, sticky="nse")
url_bar.bind("<Return>", lambda event: buttonOpen.invoke())
buttonOpen = ttk.Button(menubar, text="OK", command=open_rss)
buttonOpen.grid(row=0, column=4, sticky="nsw")

buttonRefresh = ttk.Button(menubar, text="Refresh", command=refresh)
buttonRefresh.grid(row=0, column=5, sticky="nse")
buttonTouchMode = ttk.Button(menubar, text="Menu", command=toggle_touch_mode)
buttonTouchMode.grid(row=0, column=6, sticky="nse")
buttonTabs = ttk.Button(menubar, text="Tabs", command=toggle_sidebar)
buttonTabs.grid(row=0, column=7, sticky="nse")

content = Frame(root)
content.grid(row=1, column=0, sticky="nsew")
content.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)

sidebar = Listbox(content, width=30, bg="#e1e1e1", relief=FLAT, bd=12, font=(font.nametofont("TkDefaultFont").actual()["family"], 12))
sidebar.bind("<Double-Button-1>", lambda event: open_from_sidebar())

menu_B3 = Menu(root, tearoff=False, activeborderwidth=2.5)
menu_B3.add_command(label="Open", command=open_from_sidebar)
menu_B3.add_command(label="Close", command=close_from_sidebar)
menu_B3.add_separator()
menu_B3.add_command(label="Import", command=import_rss)
menu_B3.add_command(label="Export", command=export_from_sidebar)
menu_B3.add_command(label="Export All", command=export_all)

sidebar.bind("<Button-3>", lambda event: menu_B3.tk_popup(event.x_root, event.y_root))

reader = Frame(content, bd=48, bg="#ffffff")
reader.grid(row=0, column=0, sticky="nsew")
reader.rowconfigure(2, weight=1)
reader.columnconfigure(0, weight=1)
titleLabel = Label(reader, font=("Segoe UI", 18, "bold"), justify="left", bg="#ffffff")
titleLabel.grid(row=0, column=0, sticky="nw")
titleLabel.bind("<Double-Button-1>", lambda event: webbrowser.open_new_tab(current_url))
dtLabel = Label(reader, font=("Segoe UI", 12), justify="left", bg="#ffffff")
dtLabel.grid(row=1, column=0, sticky="nw", pady=(0, 8))
text = Text(reader, font=(font.nametofont("TkDefaultFont").actual()["family"], 11), relief=FLAT, wrap=WORD, state=DISABLED)
text.grid(row=2, column=0, sticky="nsew")

url_bar.focus_set()
toggle_theme()

root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
root.bind("<F1>", lambda event: help_window())
root.bind("<F5>", lambda event: refresh())
root.bind("<F11>", lambda event: root.attributes("-fullscreen", not root.attributes("-fullscreen")))
root.bind("<Control-d>", lambda event: view_data())
root.bind("<Control-D>", lambda event: view_data())
root.mainloop()
