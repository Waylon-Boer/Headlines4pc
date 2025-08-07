from tkinter import *
from tkinter.ttk import Entry, Button, Notebook, Style
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import *
from tkinter import font
from urllib.request import *
import re, html, webbrowser
import uuid, datetime
import xml.etree.ElementTree as ET

def open_rss():
    global rss_data
    try:
        filepath = askopenfilename(filetypes=[("Really Simple Syndication", ".rss"), ("eXtensible Markup Language", ".xml")])
        data = ET.parse(filepath)
    except:
        showerror("Headlines4pc", "An error occured when trying to access this feed.")
    xml_root = data.getroot()
    try:
        text_id = f"Local - {xml_root.findtext(".//channel/title")}"
        text_id = re.sub(r'[\\/:*?"<>|]', "", text_id)
    except:
        text_id = "Unknown Feed"
    num = 2
    if text_id in text_widgets:
        temp_id = f"{text_id} ({num})"
        while temp_id in text_widgets:
            num += 1
            temp_id = f"{text_id} ({num})"
        text_id = temp_id
    rss_data[text_id] = open(filepath, "r", encoding="utf8").read()
    url_dict[text_id] = ""
    load_rss(xml_root, text_id)

def open_rss_url():
    global rss_data
    try:
        data = urlopen(link_entry.get()).read().decode("utf8")
    except:
        showerror("Headlines4pc", "An error occured when trying to access this feed.")
    xml_root = ET.fromstring(data)
    try:
        text_id = xml_root.findtext(".//channel/title")
        text_id = re.sub(r'[\\/:*?"<>|]', "", text_id)
    except:
        text_id = "Unknown Feed"
    num = 2
    if text_id in text_widgets:
        temp_id = f"{text_id} ({num})"
        while temp_id in text_widgets:
            num += 1
            temp_id = f"{text_id} ({num})"
        text_id = temp_id
    rss_data[text_id] = data
    url_dict[text_id] = link_entry.get()
    load_rss(xml_root, text_id)
    link_entry.delete(0, END)

def load_rss(xml_root, text_id):
    text = ScrolledText(tabs, font=(font.nametofont("TkDefaultFont").actual()["family"], 11), bd=16, relief=FLAT, wrap=WORD, state=DISABLED, bg=new_bg, fg=new_fg)
    text.grid(row=0, column=0, sticky="nsew")
    text.tag_configure("title", font=(font.nametofont("TkDefaultFont").actual()["family"], 16, "bold"))
    text.tag_configure("bold", font=(font.nametofont("TkDefaultFont").actual()["family"], 11, "bold"))
    text_widgets[text_id] = text
    tabs.add(text, text=text_id)
    tabs.select(text)
    feed = xml_root.findall(".//item")
    text_widgets[text_id].configure(state=NORMAL)
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
            text_widgets[text_id].tag_bind(f"link{link_id}", "<Double-Button-1>", lambda event, url=link: webbrowser.open_new_tab(url))
            text_widgets[text_id].insert(END, f"{title}\n", ("title", f"link{link_id}"))
        if dt is not None:
            dt = re.sub(r"<[^>]*>", "", html.unescape(dt.text))
            text_widgets[text_id].insert(END, f"{dt}\n", "bold")
        if description is not None:
            description = re.sub(r"<[^>]*>", "", html.unescape(description.text))
            text_widgets[text_id].insert(END, f"{description}\n")
        text_widgets[text_id].insert(END, "\n")
    text_widgets[text_id].bind("<Button-3>", lambda event: menu_B3.tk_popup(event.x_root, event.y_root))
    text_widgets[text_id].configure(state=DISABLED)

def save_rss():
    filepath = asksaveasfilename(defaultextension=".rss", filetypes=[("Really Simple Syndication", ".rss")])
    if filepath != "" and filepath != None:
        open(filepath, "w", encoding="utf8").write(list(rss_data.values())[list(text_widgets.values()).index(tabs.select())])

def save_all():
    directory = askdirectory(title="Save All")
    for text_id in rss_data:
        open(f"{directory}/{text_id}.rss", "w", encoding="utf8").write(rss_data[text_id])

def help_window():
    window = Toplevel()
    try:
        window.iconbitmap("icon.ico")
    except:
        window.iconbitmap("")
    window.title("Help - Headlines4pc")
    window.geometry("700x510")
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
    help_tabs = Notebook(window, width=320)
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

def copy(text):
    text.clipboard_clear()
    try:
        text.clipboard_append(text.get(SEL_FIRST, SEL_LAST))
    except:
        text.clipboard_append(text.get(1.0, END))

def refresh():   
    tab = tabs.nametowidget(tabs.select())
    stack = [tab]
    texts = []
    while stack:
        w = stack.pop()
        if isinstance(w, (Text, ScrolledText)):
            texts.append(w)
        else:
            stack.extend(w.winfo_children())
    if not texts: return
    text = texts[0]
    text.delete(1.0, END)
    data = urlopen(url_dict[tabs.tab(tab, "text")]).read().decode("utf8")
    xml_root = ET.fromstring(data)
    feed = xml_root.findall(".//item")
    text.configure(state=NORMAL)
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

def close_tab():
    tab = tabs.select()
    text = tabs.tab(tab, "text")
    text_widgets.pop(text, None)
    rss_data.pop(text, None)
    url_dict.pop(text, None)
    tabs.forget(tab)
    tab_widget = tabs.nametowidget(tab)
    tab_widget.destroy()

def set_theme(bg, bg2, fg):
    global new_bg, new_fg
    new_bg = bg
    new_fg = fg
    for i in [root, home, frameLink, frameActions, frameThemes]:
        i.configure(bg=bg)
    for i in ["TButton", "TEntry"]:
        style.configure(i, background=bg)
    style.configure("TNotebook", background=bg2)
    for text in text_widgets:
        text_widgets[text].configure(bg=bg, fg=fg)
    for i in [link_label, label_actions, label_themes]:
        i.configure(bg=bg, fg=fg)

root = Tk()
root.title("Headlines4pc")
root.geometry("900x600")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

style = Style(root)

new_bg = "#ffffff"
new_fg = "#000000"
text_widgets = {}
rss_data = {}
url_dict = {}

tabs = Notebook(root)
tabs.grid(row=0, column=0, sticky="nsew")

home = Frame(tabs, bg="#fff")
home.grid(row=0, column=0, sticky="nsew")
home.columnconfigure(0, weight=1)

frameLink = Frame(home, bg="#fff")
frameLink.grid(row=0, column=0, sticky="nsew", padx=128, pady=(32, 5))
frameLink.columnconfigure(0, weight=1)
link_label = Label(frameLink, text="URL", bg="#fff", fg="#000", font=(font.nametofont("TkDefaultFont").actual()["family"], 15))
link_label.grid(row=0, column=0, sticky="w")
link_entry = Entry(frameLink, font=(font.nametofont("TkDefaultFont").actual()["family"], 13))
link_entry.grid(row=1, column=0, sticky="nsew", ipady=2)
link_entry.bind("<Return>", lambda event: link_button.invoke())
link_button = Button(frameLink, text="OK", command=open_rss_url)
link_button.grid(row=1, column=1, sticky="nsew")

frameActions = Frame(home, bg="#fff")
frameActions.grid(row=1, column=0, sticky="nsew", padx=128, pady=(5, 0))
for i in range(0, 3):
    frameActions.columnconfigure(i, weight=1)
label_actions = Label(frameActions, text="Actions", bg="#fff", fg="#000", font=(font.nametofont("TkDefaultFont").actual()["family"], 15))
label_actions.grid(row=0, column=0, sticky="w")
button_action_1 = Button(frameActions, text="Import RSS", command=open_rss)
button_action_1.grid(row=1, column=0, sticky="nsew", pady=5, ipady=8)
button_action_2 = Button(frameActions, text="Save All", command=save_all)
button_action_2.grid(row=1, column=1, sticky="nsew", pady=5)
button_action_3 = Button(frameActions, text="Help", command=help_window)
button_action_3.grid(row=1, column=2, sticky="nsew", pady=5)

frameThemes = Frame(home, bg="#fff")
frameThemes.grid(row=2, column=0, sticky="nsew", padx=128, pady=(5, 0))
for i in range(0, 5):
    frameThemes.columnconfigure(i, weight=1)
label_themes = Label(frameThemes, text="Themes", bg="#fff", fg="#000", font=(font.nametofont("TkDefaultFont").actual()["family"], 15))
label_themes.grid(row=0, column=0, sticky="w")
button_theme_1 = Button(frameThemes, text="Light", command=lambda: set_theme("#ffffff", "#f0f0f0", "#000000"))
button_theme_1.grid(row=1, column=0, sticky="nsew", pady=5)
button_theme_2 = Button(frameThemes, text="Paper", command=lambda: set_theme("#ddccbb", "#f0f0f0", "#000000"))
button_theme_2.grid(row=1, column=1, sticky="nsew", pady=5)
button_theme_3 = Button(frameThemes, text="Blue", command=lambda: set_theme("#bbccdd", "#f0f0f0", "#000000"))
button_theme_3.grid(row=1, column=2, sticky="nsew", pady=5)
button_theme_4 = Button(frameThemes, text="Green", command=lambda: set_theme("#bbddbb", "#f0f0f0", "#000000"))
button_theme_4.grid(row=1, column=3, sticky="nsew", pady=5)
button_theme_5 = Button(frameThemes, text="Dark", command=lambda: set_theme("#1e1e1e", "#1e1e1e", "#ffffff"))
button_theme_5.grid(row=1, column=4, sticky="nsew", pady=5)

tabs.add(home, text="Home")

menu_B3 = Menu(root, tearoff=False, activeborderwidth=2.5)
menu_B3.add_command(label="Home", command=lambda: tabs.select(home))
menu_B3.add_separator()
menu_B3.add_command(label="Copy", command=lambda: copy(tabs.select()))
menu_B3.add_command(label="Select All", command=lambda: tabs.nametowidget(tabs.select()).tag_add(SEL, 1.0, END))
menu_B3.add_command(label="Save RSS", command=save_rss)
menu_B3.add_separator()
menu_B3.add_command(label="Refresh", command=refresh)
menu_B3.add_command(label="Close Tab", command=close_tab)

set_theme("#ffffff", "#f0f0f0", "#000000")

root.bind("<F11>", lambda event: root.attributes("-fullscreen", not root.attributes("-fullscreen")))
root.mainloop()
