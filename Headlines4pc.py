from tkinter import *
from tkinter.ttk import Entry, Style, Notebook
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import *
from tkinter import font
from urllib.request import *
import re, html, webbrowser
import uuid, datetime
import xml.etree.ElementTree as ET

def toggle_sidebar():
    if sidebar.grid_info() == {}:
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)
        sidebar.grid(row=0, column=0, sticky="nsew")
        text.grid(row=0, column=1, sticky="nsew")
    else:
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        sidebar.grid_forget()
        text.grid(row=0, column=0, sticky="nsew")
        
def import_rss():
    global rss_data
    try:
        filepath = askopenfilename(filetypes=[("Really Simple Syndication", ".rss"), ("eXtensible Markup Language", ".xml")])
        if filepath != "":
            data = ET.parse(filepath)
            xml_root = data.getroot()
            try:
                feed_id = f"Local: {xml_root.findtext('.//channel/title')}"
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
    sidebar.delete(0, END)
    for i in rss_data:
        sidebar.insert(END, i)
    global current_feed_id
    current_feed_id = feed_id
    data = rss_data[feed_id]
    xml_root = ET.fromstring(data)
    feed = xml_root.findall(".//item")
    text.configure(state=NORMAL)
    text.delete(1.0, END)
    for item in feed:
        title = item.find("title")
        dt = item.find("pubDate")
        link = item.find("link")
        description = item.find("description")
        if title is not None:
            title = re.sub(r"<[^>]*>", "", html.unescape(title.text))
            if link is not None:
                link = re.sub(r"<[^>]*>", "", html.unescape(link.text))
            link_id = uuid.uuid1()
            text.tag_bind(f"link{link_id}", "<Double-Button-1>", lambda event, url=link: webbrowser.open_new_tab(url))
            text.insert(END, f"{title}\n", ("title", f"link{link_id}"))
        if dt is not None:
            dt = re.sub(r"<[^>]*>", "", html.unescape(dt.text))
            text.insert(END, f"{dt}\n", "bold")
        if description is not None:
            description = re.sub(r"<[^>]*>", "", html.unescape(description.text))
            text.insert(END, f"{description}\n")
        text.insert(END, "\n")
    text.configure(state=DISABLED)
    text.focus_set()

def toggle_menubar():
    if menubar.grid_info()["row"] == 0:
        root.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=0)
        content.grid(row=0, column=0, sticky="nsew")
        menubar.grid(row=1, column=0, sticky="nsew")
    else:
        root.rowconfigure(0, weight=0)
        root.rowconfigure(1, weight=1)
        menubar.grid(row=0, column=0, sticky="nsew")
        content.grid(row=1, column=0, sticky="nsew")
   
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
    help_tabs = Notebook(window)
    help_tabs.grid(row=0, column=0, sticky="nsew")
    about = Text(help_tabs, relief=FLAT, border=16, font=(font.nametofont("TkDefaultFont").actual()["family"], 12), wrap=WORD, background="#dcb")
    about.insert(INSERT, f"Headlines4pc\nCopyright (c) 2025-{str(datetime.datetime.now().year)}: Waylon Boer\n\nHeadlines4pc is a RSS Feed reader with tab support.")
    about.configure(state=DISABLED)
    help_tabs.add(about, text="About")
    mit_license = Text(help_tabs, relief=FLAT, border=16, font=(font.nametofont("TkDefaultFont").actual()["family"], 12), wrap=WORD, background="#dcb")
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
    window.mainloop()

def save_rss():
    filepath = asksaveasfilename(defaultextension=".rss", filetypes=[("Really Simple Syndication", ".rss")])
    if filepath != "":
        open(filepath, "w", encoding="utf8").write(rss_data[current_feed_id])

def open_from_sidebar():
    try:
        load_rss(sidebar.get(ACTIVE))
    except:
        text.focus_set()

def save_from_sidebar():
    try:
        filepath = asksaveasfilename(defaultextension=".rss", filetypes=[("Really Simple Syndication", ".rss")])
        if filepath != "":
            open(filepath, "w", encoding="utf8").write(rss_data[sidebar.get(ACTIVE)])
    except:
        text.focus_set()

def save_all():
    directory = askdirectory(title="Save All")
    for feed_id in rss_data:
        open(f"{directory}/{feed_id}.rss", "w", encoding="utf8").write(rss_data[feed_id])

def close_from_sidebar():
    global current_feed_id
    try:
        feed_id = sidebar.get(ACTIVE)
        if current_feed_id == feed_id:
            text.configure(state=NORMAL)
            text.delete(1.0, END)
            text.configure(state=DISABLED)
        rss_data.pop(feed_id, None)
        url_dict.pop(feed_id, None)
        sidebar.delete(0, END)
        for i in rss_data:
            sidebar.insert(END, i)
    except:
        text.focus_set()

def switch_theme():
    if text["bg"] == "#ffffff" or text["bg"] == "SystemWindow":
        bg, bg2, bg3, fg = "#111111", "#3c3c3c", "#2d2d2d", "#ffffff"
    else:
        bg, bg2, bg3, fg = "#ffffff", "#e1e1e1", "#f0f0f0", "#000000"
    text.configure(bg=bg, fg=fg)
    text.tag_configure("sel", background=bg2, foreground=fg)
    menubar.configure(bg=bg2)
    style.configure("TEntry", background=bg2)
    sidebar.configure(bg=bg3, fg=fg)
    for i in [buttonFeeds, buttonImport, buttonOpen, buttonMenu, buttonSearch]:
        i.configure(bg=bg2, fg=fg)
    for i in [menu_B3_sidebar, menu_B3_text]:
        if bg == "#111111":
            i.configure(background="#000", foreground="#fff", activebackground="#333", activeforeground="#fff")
        else:
            i.configure(background="#f0f0f0", foreground="#000", activebackground="#ccc", activeforeground="#000")

def find_next(find):
    lc = text.search(find, text.index(INSERT))
    text.tag_remove(SEL, 1.0, END)
    text.tag_add(SEL, lc, "{}.{}".format(*lc.split(".")[:-1], int(lc.split(".")[-1])+len(find)))
    text.mark_set(INSERT, "{}.{}".format(*lc.split(".")[:-1], int(lc.split(".")[-1])+len(find)))
    text.focus_set()

def toggle_bar():
    if search_bar.grid_info() == {}:
        url_bar.grid_forget()
        buttonOpen.grid_forget()
        search_bar.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
        buttonSearch.grid(row=0, column=3, sticky="nsew", ipady=5)
    else:
        search_bar.grid_forget()
        buttonSearch.grid_forget()
        url_bar.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
        buttonOpen.grid(row=0, column=3, sticky="nsew", ipady=5)

def refresh():
    load_rss(current_feed_id)

rss_data = {}
url_dict = {}
current_feed_id = ""

root = Tk()
root.title("Headlines4pc")
root.geometry("900x600")
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

style = Style(root)
style.configure("TEntry", background="#e1e1e1")

menubar = Frame(root, bg="#e1e1e1")
menubar.grid(row=0, column=0, sticky="nsew")
menubar.columnconfigure(2, weight=1)
buttonFeeds = Button(menubar, relief=FLAT, bg="#e1e1e1", bd=0, width=8, text="Feeds", command=toggle_sidebar)
buttonFeeds.grid(row=0, column=0, sticky="nsew", ipady=5)
buttonImport = Button(menubar, relief=FLAT, bg="#e1e1e1", bd=0, width=8, text="Import", command=import_rss)
buttonImport.grid(row=0, column=1, sticky="nsew", ipady=5)
url_bar = Entry(menubar, justify="center")
url_bar.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
url_bar.bind("<Return>", lambda event: buttonOpen.invoke())
buttonOpen = Button(menubar, relief=FLAT, bg="#e1e1e1", bd=0, width=8, text="Open", command=open_rss)
buttonOpen.grid(row=0, column=3, sticky="nsew", ipady=5)
buttonMenu = Button(menubar, relief=FLAT, bg="#e1e1e1", bd=0, width=8, text="Menu", command=toggle_menubar)
buttonMenu.grid(row=0, column=4, sticky="nsew", ipady=5)
menubar.bind("<Double-Button-1>", lambda event: toggle_bar())
search_bar = Entry(menubar, justify="center")
search_bar.bind("<Return>", lambda event: buttonSearch.invoke())
buttonSearch = Button(menubar, relief=FLAT, bg="#e1e1e1", bd=0, width=8, text="Search", command=lambda: find_next(search_bar.get()))
url_bar.bind("<Double-Button-1>", lambda event: toggle_bar())
search_bar.bind("<Double-Button-1>", lambda event: toggle_bar())

content = Frame(root)
content.grid(row=1, column=0, sticky="nsew")
content.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)

sidebar = Listbox(content, width=25, bg="#f0f0f0", relief=FLAT, bd=12, font=(font.nametofont("TkDefaultFont").actual()["family"], 12))
sidebar.bind("<Double-Button-1>", lambda event: open_from_sidebar())

menu_B3_sidebar = Menu(root, tearoff=False, activeborderwidth=2.5)
menu_B3_sidebar.add_command(label="Open", command=open_from_sidebar)
menu_B3_sidebar.add_command(label="Save As", command=save_from_sidebar)
menu_B3_sidebar.add_command(label="Save All", command=save_all)
menu_B3_sidebar.add_separator()
menu_B3_sidebar.add_command(label="Close", command=close_from_sidebar)

sidebar.bind("<Button-3>", lambda event: menu_B3_sidebar.tk_popup(event.x_root, event.y_root))


text = ScrolledText(content, font=(font.nametofont("TkDefaultFont").actual()["family"], 11), bd=16, relief=FLAT, wrap=WORD, state=DISABLED)
text.grid(row=0, column=0, sticky="nsew")
text.tag_configure("title", font=(font.nametofont("TkDefaultFont").actual()["family"], 16, "bold"))
text.tag_configure("bold", font=(font.nametofont("TkDefaultFont").actual()["family"], 11, "bold"))

menu_B3_text = Menu(root, tearoff=False, activeborderwidth=2.5)
menu_B3_text.add_command(label="Copy", command=copy())
menu_B3_text.add_command(label="Find", command=toggle_bar)
menu_B3_text.add_command(label="Select All", command=lambda: text.tag_add(SEL, 1.0, END))
menu_B3_text.add_command(label="Refresh", command=refresh)
menu_B3_text.add_separator()
menu_B3_text.add_command(label="Help", command=help_window)
menu_B3_text.add_command(label="Switch Theme", command=switch_theme)
menu_B3_text.add_separator()
menu_B3_text.add_command(label="Full Screen", command=lambda: root.attributes("-fullscreen", not root.attributes("-fullscreen")))

url_bar.focus_set()

text.bind("<Button-3>", lambda event: menu_B3_text.tk_popup(event.x_root, event.y_root))

root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
root.bind("<F1>", lambda event: help_window())
root.bind("<F3>", lambda event: toggle_bar())
root.bind("<F5>", lambda event: refresh())
root.bind("<F11>", lambda event: root.attributes("-fullscreen", not root.attributes("-fullscreen")))
root.mainloop()
