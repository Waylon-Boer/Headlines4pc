import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter.messagebox import *
from tkinter import font
from urllib.request import *
import re, html, webbrowser, datetime, csv
import xml.etree.ElementTree as ET

class Headlines4pc:
    def __init__(self):
        self.rss_data = {}
        self.url_dict = {}
        self.current_feed_id = ""
        self.current_item_id = 0
        self.processed_feed_data = {}
        self.current_url = ""
        self.favorites = {}

        self.root = tk.Tk()
        self.root.title("Headlines4pc")
        self.root.geometry("900x600")
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.save_favorites_and_exit())
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            try:
                self.root.iconbitmap("")
            except:
                pass

        self.style = ttk.Style(self.root)
        self.style.layout("Treeview", [
            ("Treeview.treearea", {"sticky": "nsew"})
        ])

        self.menuActions = tk.Menu(self.root, tearoff=False, activeborderwidth=2.5)
        self.menuActions.add_command(label="Copy", command=lambda: self.text.clipboard_append(self.text.get(1.0, tk.END)))
        self.menuActions.add_command(label="Open in browser", command=self.open_in_browser)
        self.menuActions.add_command(label="View XML", command=self.toggle_xml)
        self.menuActions.add_separator()
        self.menuActions.add_command(label="Switch theme", command=self.switch_theme)
        self.menuActions.add_command(label="Full screen", command=lambda: self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen")))
        self.menuActions.add_separator()
        self.menuActions.add_command(label="Help", command=self.help_window)

        self.toolbar = tk.Frame(self.root)
        self.toolbar.grid(row=0, column=0, sticky="nsew")
        self.toolbar.columnconfigure(3, weight=1)
        self.toolbar.columnconfigure(4, weight=1)
        self.buttonActions = tk.Button(self.toolbar, bd=0, width=10, text="Actions", command=lambda: self.menuActions.tk_popup(self.main.winfo_rootx(), self.main.winfo_rooty()))
        self.buttonActions.grid(row=0, column=0, sticky="nsw")
        self.buttonPrevious = tk.Button(self.toolbar, bd=0, width=10, text="Previous", command=self.previous_item)
        self.buttonPrevious.grid(row=0, column=1, sticky="nsw")
        self.buttonNext = tk.Button(self.toolbar, bd=0, width=10, text="Next", command=self.next_item)
        self.buttonNext.grid(row=0, column=2, sticky="nsw")
        self.url_bar = tk.Entry(self.toolbar, bd=2, relief=tk.FLAT, width=40, font=(font.nametofont("TkDefaultFont").actual()["family"], 11))
        self.url_bar.grid(row=0, column=3, sticky="nse", pady=5)
        self.url_bar.bind("<Return>", lambda event: self.buttonOK.invoke())
        self.buttonOK = tk.Button(self.toolbar, bd=0, width=5, text="OK", bg="#e1e1e1", command=self.open_rss)
        self.buttonOK.grid(row=0, column=4, sticky="nsw", pady=5)
        self.buttonRefresh = tk.Button(self.toolbar, bd=0, width=10, text="Refresh", command=self.refresh)
        self.buttonRefresh.grid(row=0, column=5, sticky="nse")
        self.buttonFavorites = tk.Button(self.toolbar, bd=0, width=10, text="Favorites", command=self.toggle_favorites)
        self.buttonFavorites.grid(row=0, column=6, sticky="nse")
        self.buttonTabs = tk.Button(self.toolbar, bd=0, width=10, text="Tabs", command=self.toggle_tabs)
        self.buttonTabs.grid(row=0, column=7, sticky="nse")

        self.menu_B3_url_bar = tk.Menu(self.root, tearoff=False, activeborderwidth=2.5)
        self.menu_B3_url_bar.add_command(label="Cut", command=lambda: self.url_bar.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        self.menu_B3_url_bar.add_command(label="Copy", command=lambda: self.url_bar.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        self.menu_B3_url_bar.add_command(label="Paste", command=lambda: self.url_bar.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        self.menu_B3_url_bar.add_separator()
        self.menu_B3_url_bar.add_command(label="Select All", command=lambda: self.url_bar.select_range(0, tk.END), accelerator="Ctrl+A")
        self.url_bar.bind("<Button-3>", lambda event: self.menu_B3_url_bar.tk_popup(event.x_root, event.y_root))

        self.main = tk.Frame(self.root)
        self.main.grid(row=1, column=0, sticky="nsew")
        self.main.rowconfigure(0, weight=1)
        self.main.columnconfigure(0, weight=1)

        self.content = ttk.PanedWindow(self.main, orient=tk.VERTICAL)
        self.content.grid(row=0, column=0, sticky="nsew")

        self.reader = tk.Frame(self.content, bd=48, bg="#ffffff")
        self.reader.rowconfigure(2, weight=1)
        self.reader.columnconfigure(0, weight=1)
        self.titleLabel = tk.Label(self.reader, font=(font.nametofont("TkDefaultFont").actual()["family"], 18, "bold"), justify="left", bg="#ffffff")
        self.titleLabel.grid(row=0, column=0, sticky="nw")
        self.titleLabel.bind("<Double-Button-1>", lambda event: self.open_in_browser())
        self.dtLabel = tk.Label(self.reader, font=(font.nametofont("TkDefaultFont").actual()["family"], 12), justify="left", bg="#ffffff")
        self.dtLabel.grid(row=1, column=0, sticky="nw", pady=(0, 8))
        self.text = tk.Text(self.reader, font=(font.nametofont("TkDefaultFont").actual()["family"], 11), relief=tk.FLAT, wrap=tk.WORD, state="disabled")
        self.text.grid(row=2, column=0, sticky="nsew")

        self.treeview = ttk.Treeview(self.content, show="tree")
        self.content.add(self.reader, weight=1)

        self.sidebar_favorites = tk.Frame(self.main)
        self.sidebar_favorites.rowconfigure(2, weight=1)
        self.sidebar_favorites.columnconfigure(0, weight=1)

        self.labelFavorites = tk.Label(self.sidebar_favorites, text="Favorites", relief=tk.FLAT, bd=12, font=(font.nametofont("TkDefaultFont").actual()["family"], 16))
        self.labelFavorites.grid(row=0, column=0, sticky="nsew")

        self.separatorFavorites1 = ttk.Separator(self.sidebar_favorites)
        self.separatorFavorites1.grid(row=1, column=0, sticky="nsew")

        self.listboxFavorites = tk.Listbox(self.sidebar_favorites, width=30, relief=tk.FLAT, bd=12, highlightthickness=0, font=(font.nametofont("TkDefaultFont").actual()["family"], 12))
        self.listboxFavorites.grid(row=2, column=0, sticky="nsew")
        self.listboxFavorites.bind("<Double-Button-1>", lambda event: self.open_favorite())

        self.menu_B3_favorites = tk.Menu(self.root, tearoff=False, activeborderwidth=2.5)
        self.menu_B3_favorites.add_command(label="Add", command=self.add_favorite)
        self.menu_B3_favorites.add_command(label="Remove", command=self.remove_favorite)
        self.menu_B3_favorites.add_separator()
        self.menu_B3_favorites.add_command(label="Import", command=self.import_favorites)
        self.menu_B3_favorites.add_command(label="Export", command=self.export_favorites)

        self.listboxFavorites.bind("<Button-3>", lambda event: self.menu_B3_favorites.tk_popup(event.x_root, event.y_root))

        self.separatorFavorites2 = ttk.Separator(self.sidebar_favorites)
        self.separatorFavorites2.grid(row=3, column=0, sticky="nsew")
        
        self.buttonFavorites1 = tk.Button(self.sidebar_favorites, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Add", command=self.add_favorite)
        self.buttonFavorites1.grid(row=4, column=0, sticky="nsew")
        self.buttonFavorites2 = tk.Button(self.sidebar_favorites, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Remove", command=self.remove_favorite)
        self.buttonFavorites2.grid(row=5, column=0, sticky="nsew")
        self.buttonFavorites3 = tk.Button(self.sidebar_favorites, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Import", command=self.import_favorites)
        self.buttonFavorites3.grid(row=6, column=0, sticky="nsew")
        self.buttonFavorites4 = tk.Button(self.sidebar_favorites, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Export", command=self.export_favorites)
        self.buttonFavorites4.grid(row=7, column=0, sticky="nsew")

        self.sidebar_tabs = tk.Frame(self.main)
        self.sidebar_tabs.rowconfigure(2, weight=1)
        self.sidebar_tabs.columnconfigure(0, weight=1)

        self.labelTabs = tk.Label(self.sidebar_tabs, text="Tabs", relief=tk.FLAT, bd=12, font=(font.nametofont("TkDefaultFont").actual()["family"], 16))
        self.labelTabs.grid(row=0, column=0, sticky="nsew")

        self.separatorTabs1 = ttk.Separator(self.sidebar_tabs)
        self.separatorTabs1.grid(row=1, column=0, sticky="nsew")
        
        self.listboxTabs = tk.Listbox(self.sidebar_tabs, width=30, bg="#e1e1e1", relief=tk.FLAT, bd=12, highlightthickness=0, font=(font.nametofont("TkDefaultFont").actual()["family"], 12))
        self.listboxTabs.grid(row=2, column=0, sticky="nsew")
        self.listboxTabs.bind("<Double-Button-1>", lambda event: self.open_from_tabs())

        self.menu_B3_tabs = tk.Menu(self.root, tearoff=False, activeborderwidth=2.5)
        self.menu_B3_tabs.add_command(label="Open", command=self.open_from_tabs)
        self.menu_B3_tabs.add_command(label="Close", command=self.close_tab)
        self.menu_B3_tabs.add_separator()
        self.menu_B3_tabs.add_command(label="Import", command=self.import_rss)
        self.menu_B3_tabs.add_command(label="Export", command=self.export_rss)
        self.menu_B3_tabs.add_command(label="Export All", command=self.export_all)

        self.listboxTabs.bind("<Button-3>", lambda event: self.menu_B3_tabs.tk_popup(event.x_root, event.y_root))

        self.separatorTabs2 = ttk.Separator(self.sidebar_tabs)
        self.separatorTabs2.grid(row=3, column=0, sticky="nsew")
        
        self.buttonTabs1 = tk.Button(self.sidebar_tabs, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Open", command=self.open_from_tabs)
        self.buttonTabs1.grid(row=4, column=0, sticky="nsew")
        self.buttonTabs2 = tk.Button(self.sidebar_tabs, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Close", command=self.close_tab)
        self.buttonTabs2.grid(row=5, column=0, sticky="nsew")
        self.buttonTabs3 = tk.Button(self.sidebar_tabs, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Import", command=self.import_rss)
        self.buttonTabs3.grid(row=6, column=0, sticky="nsew")
        self.buttonTabs4 = tk.Button(self.sidebar_tabs, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Export", command=self.export_rss)
        self.buttonTabs4.grid(row=7, column=0, sticky="nsew")
        self.buttonTabs5 = tk.Button(self.sidebar_tabs, bd=0, relief=tk.FLAT, height=2, width=10, anchor="w", text="    Export All", command=self.export_all)
        self.buttonTabs5.grid(row=8, column=0, sticky="nsew")

        self.url_bar.focus_set()
        self.switch_theme()
        self.load_favorites()

        self.root.bind("<Escape>", lambda event: self.root.attributes("-fullscreen", False))
        self.root.bind("<F1>", lambda event: self.help_window())
        self.root.bind("<F5>", lambda event: self.refresh())
        self.root.bind("<F10>", lambda event: self.menuActions.tk_popup(self.main.winfo_rootx(), self.main.winfo_rooty()))
        self.root.bind("<F11>", lambda event: self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen")))
        self.root.bind("<Control-b>", lambda event: self.open_in_browser())
        self.root.bind("<Control-B>", lambda event: self.open_in_browser())
        self.root.bind("<Control-Shift-b>", lambda event: self.toggle_favorites())
        self.root.bind("<Control-Shift-B>", lambda event: self.toggle_favorites())
        self.root.bind("<Control-d>", lambda event: self.add_favorite_menu())
        self.root.bind("<Control-D>", lambda event: self.add_favorite_menu())
        self.root.bind("<Control-e>", lambda event: self.toggle_xml())
        self.root.bind("<Control-E>", lambda event: self.toggle_xml())
        self.root.bind("<Control-n>", lambda event: self.url_bar.focus_set())
        self.root.bind("<Control-N>", lambda event: self.url_bar.focus_set())
        self.root.bind("<Control-o>", lambda event: self.import_rss_menu())
        self.root.bind("<Control-O>", lambda event: self.import_rss_menu())
        self.root.bind("<Control-Shift-o>", lambda event: self.toggle_favorites())
        self.root.bind("<Control-Shift-O>", lambda event: self.toggle_favorites())
        self.root.bind("<Control-q>", lambda event: self.save_favorites_and_exit())
        self.root.bind("<Control-Q>", lambda event: self.save_favorites_and_exit())
        self.root.bind("<Control-s>", lambda event: self.export_rss_menu())
        self.root.bind("<Control-S>", lambda event: self.export_rss_menu())
        self.root.bind("<Control-Shift-s>", lambda event: self.export_all_menu())
        self.root.bind("<Control-Shift-S>", lambda event: self.export_all_menu())
        self.root.bind("<Control-t>", lambda event: self.switch_theme())
        self.root.bind("<Control-T>", lambda event: self.switch_theme())
        self.root.bind("<Control-w>", lambda event: self.close_tab())
        self.root.bind("<Control-W>", lambda event: self.close_tab())
        self.root.bind("<Control-,>", lambda event: self.hide_sidebar())
        self.root.bind("<Control-.>", lambda event: self.toggle_favorites())
        self.root.bind("<Control-/>", lambda event: self.toggle_tabs())
        self.root.bind("<Control-Left>", lambda event: self.previous_item())
        self.root.bind("<Control-Right>", lambda event: self.next_item())
        self.root.bind("<Alt-Left>", lambda event: self.previous_item())
        self.root.bind("<Alt-Right>", lambda event: self.next_item())
        self.root.bind("<Alt-q>", lambda event: self.url_bar.focus_set())
        self.root.bind("<Alt-Q>", lambda event: self.url_bar.focus_set())
        self.root.bind("<Alt-s>", lambda event: self.url_bar.focus_set())
        self.root.bind("<Alt-S>", lambda event: self.url_bar.focus_set())
       
        self.root.mainloop()

    def open_rss(self):
        try:
            if self.url_bar.get() != "":
                data = urlopen(self.url_bar.get()).read().decode("utf8")
                xml_root = ET.fromstring(data)
                try:
                    feed_id = xml_root.findtext(".//channel/title")
                    feed_id = re.sub(r'[\\/:*?"<>|;]', "", feed_id)
                except:
                    feed_id = "Unknown Feed"
                num = 2
                if feed_id in list(self.rss_data.keys()):
                    temp_id = f"{feed_id} ({num})"
                    while temp_id in list(self.rss_data.keys()):
                        num += 1
                        temp_id = f"{feed_id} ({num})"
                    feed_id = temp_id
                self.rss_data[feed_id] = data
                self.url_dict[feed_id] = self.url_bar.get()
                self.url_bar.delete(0, tk.END)
                self.load_rss(feed_id)
        except:
            showerror("Headlines4pc", "An error occurred when trying to access this feed.")

    def load_rss(self, feed_id):
        self.listboxTabs.delete(0, tk.END)
        for i in self.rss_data:
            self.listboxTabs.insert(tk.END, i)
        self.current_feed_id = feed_id
        self.root.title(f"{self.current_feed_id} - Headlines4pc")
        data = self.rss_data[feed_id]
        xml_root = ET.fromstring(data)
        feed = xml_root.findall(".//item")
        self.processed_feed_data[feed_id] = []
        self.current_item_id = 0
        item_id = self.current_item_id
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
            self.processed_feed_data[feed_id].append(item_rss)
        self.load_item(feed_id, item_id)
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        self.insert_item("", ET.fromstring(self.rss_data[self.current_feed_id]))

    def load_item(self, feed_id, item_id):
        self.buttonActions.configure(text=f"{item_id+1}/{len(self.processed_feed_data[self.current_feed_id])}")
        title = self.processed_feed_data[feed_id][item_id]["title"]
        dt = self.processed_feed_data[feed_id][item_id]["pubDate"]
        link = self.processed_feed_data[feed_id][item_id]["link"]
        description = self.processed_feed_data[feed_id][item_id]["description"]
        self.text.configure(state="normal")
        self.text.delete(1.0, tk.END)
        self.titleLabel.configure(text=title)
        self.dtLabel.configure(text=dt)
        self.current_url = link
        if description is not None:
            self.text.insert(tk.END, f"{description}\n")
        self.text.focus_set()
        self.text.configure(state="disabled")

    def previous_item(self):
        if self.current_feed_id != "":
            if self.current_item_id > 0:
                self.current_item_id -= 1
            self.load_item(self.current_feed_id, self.current_item_id)

    def next_item(self):
        if self.current_feed_id != "":
            if self.current_item_id < len(self.processed_feed_data[self.current_feed_id]) - 1:
                self.current_item_id += 1
            self.load_item(self.current_feed_id, self.current_item_id)

    def refresh(self):
        if self.current_feed_id and self.url_dict[self.current_feed_id] != "":
            try:
                data = urlopen(self.url_dict[self.current_feed_id]).read().decode("utf8")
                self.rss_data[self.current_feed_id] = data
                self.load_rss(self.current_feed_id)
            except:
                showerror("Headlines4pc", "An error occurred when trying to refresh this feed.")

    def open_from_tabs(self):
        try:
            self.load_rss(self.listboxTabs.get(tk.ACTIVE))
        except:
            pass

    def close_tab(self):
        try:
            feed_id = self.listboxTabs.get(tk.ACTIVE)
            if self.current_feed_id == feed_id:
                self.titleLabel.configure(text="")
                self.dtLabel.configure(text="")
                self.text.configure(state="normal")
                self.text.delete(1.0, tk.END)
                self.text.configure(state="disabled")
                self.buttonActions.configure(text="Actions")
                self.current_feed_id = ""
                self.current_item_id = 0
                for i in self.treeview.get_children():
                    self.treeview.delete(i)
                self.root.title("Headlines4pc")
            self.rss_data.pop(feed_id, None)
            self.url_dict.pop(feed_id, None)
            self.processed_feed_data.pop(feed_id, None)
            self.listboxTabs.delete(0, tk.END)
            for i in self.rss_data:
                self.listboxTabs.insert(tk.END, i)
        except:
            pass

    def import_rss(self):
        try:
            filepath = askopenfilename(title="Import RSS", filetypes=[("Really Simple Syndication", ".rss"), ("eXtensible Markup Language", ".xml")])
            if filepath != "":
                try:
                    feed_id = f"File - {filepath.split('/')[-1]}"
                    feed_id = re.sub(r'[\\/:*?"<>|]', "", feed_id)
                except:
                    feed_id = "Unknown Feed"
                num = 2
                if feed_id in list(self.rss_data.keys()):
                    temp_id = f"{feed_id} ({num})"
                    while temp_id in list(self.rss_data.keys()):
                        num += 1
                        temp_id = f"{feed_id} ({num})"
                    feed_id = temp_id
                with open(filepath, "r", encoding="utf8") as file:
                    self.rss_data[feed_id] = file.read()
                self.url_dict[feed_id] = ""
                self.load_rss(feed_id)
        except:
            showerror("Headlines4pc", "An error occurred when trying to access this feed.")

    def export_rss(self):
        if self.current_feed_id != "":
            filepath = asksaveasfilename(defaultextension=".rss", filetypes=[("Really Simple Syndication", ".rss")])
            if filepath != "":
                with open(filepath, "w", encoding="utf8") as file:
                    file.write(self.rss_data[self.listboxTabs.get(tk.ACTIVE)])

    def export_all(self):
        if self.rss_data != {}:
            directory = askdirectory(title="Export All")
            for feed_id in self.rss_data:
                with open(f"{directory}/{feed_id}.rss", "w", encoding="utf8") as file:
                    file.write(self.rss_data[feed_id])

    def add_favorite(self):
        if self.current_feed_id != "":
            if self.url_dict[self.current_feed_id] == "":
                showerror("Headlines4pc", "You cannot add local feeds to favorites.")
            else:
                self.favorites[self.current_feed_id] = self.url_dict[self.current_feed_id]
                self.listboxFavorites.delete(0, "end")
                for i in list(self.favorites.keys()):
                    self.listboxFavorites.insert("end", i)

    def remove_favorite(self):
        try:
            feed_id = self.listboxFavorites.get(tk.ACTIVE)
            self.favorites.pop(feed_id, None)
            self.listboxFavorites.delete(0, "end")
            for i in list(self.favorites.keys()):
                self.listboxFavorites.insert("end", i)
        except:
            pass

    def import_favorites(self):
        filepath = askopenfilename(title="Import favorites", filetypes=[("Comma Separated Values", ".csv")])
        with open(filepath, "r", encoding="utf8", newline="") as file:
            csv_data = csv.reader(file, delimiter=";")
            for r in csv_data:
                if len(r) > 1:
                    self.favorites[r[0]] = r[1]
        self.listboxFavorites.delete(0, "end")
        for i in list(self.favorites.keys()):
            self.listboxFavorites.insert("end", i)

    def export_favorites(self):
        filepath = asksaveasfilename(title="Export favorites", defaultextension=".csv", filetypes=[("Comma Separated Values", ".csv")])
        with open(filepath, "w", encoding="utf8", newline="") as file:
            csv_writer = csv.writer(file, delimiter=";")
            for key, value in self.favorites.items():
                csv_writer.writerow([key, value])

    def open_favorite(self):
        try:
            url = self.favorites[self.listboxFavorites.get(tk.ACTIVE)]
            data = urlopen(url).read().decode("utf8")
            xml_root = ET.fromstring(data)
            try:
                feed_id = xml_root.findtext(".//channel/title")
                feed_id = re.sub(r'[\\/:*?"<>|;]', "", feed_id)
            except:
                feed_id = "Unknown Feed"
            num = 2
            if feed_id in list(self.rss_data.keys()):
                temp_id = f"{feed_id} ({num})"
                while temp_id in list(self.rss_data.keys()):
                    num += 1
                    temp_id = f"{feed_id} ({num})"
                feed_id = temp_id
            self.rss_data[feed_id] = data
            self.url_dict[feed_id] = url
            self.url_bar.delete(0, tk.END)
            self.load_rss(feed_id)
            self.toggle_tabs()
        except:
            showerror("Headlines4pc", "An error occurred when trying to access this feed.")

    def load_favorites(self):
        try:
            with open("favorites.csv", "r", encoding="utf8", newline="") as file:
                csv_data = csv.reader(file, delimiter=";")
                for r in csv_data:
                    if len(r) > 1:
                        self.favorites[r[0]] = r[1]
        except:
            self.favorites = {}
        self.listboxFavorites.delete(0, "end")
        for i in list(self.favorites.keys()):
            self.listboxFavorites.insert("end", i)

    def save_favorites_and_exit(self):
        try:
            with open("favorites.csv", "w", encoding="utf8", newline="") as file:
                csv_writer = csv.writer(file, delimiter=";")
                for key, value in self.favorites.items():
                    csv_writer.writerow([key, value])
        finally:
            self.root.destroy()

    def add_favorite_menu(self):
        if self.current_feed_id != "":
            if self.url_dict[self.current_feed_id] != "":
                if self.sidebar_favorites.grid_info() == {}:
                    if self.sidebar_tabs.grid_info() != {}:
                        self.sidebar_tabs.grid_forget()
                    self.sidebar_favorites.grid(row=0, column=1, sticky="nsew")
                self.add_favorite()

    def import_rss_menu(self):
        if self.sidebar_tabs.grid_info() == {}:
            if self.sidebar_favorites.grid_info() != {}:
                self.sidebar_favorites.grid_forget()
            self.sidebar_tabs.grid(row=0, column=1, sticky="nsew")
        self.import_rss()

    def export_rss_menu(self):
        if self.current_feed_id != "":
            if self.sidebar_tabs.grid_info() == {}:
                if self.sidebar_favorites.grid_info() != {}:
                    self.sidebar_favorites.grid_forget()
                self.sidebar_tabs.grid(row=0, column=1, sticky="nsew")
            self.export_rss()

    def export_all_menu(self):
        if self.rss_data != {}:
            if self.sidebar_tabs.grid_info() == {}:
                if self.sidebar_favorites.grid_info() != {}:
                    self.sidebar_favorites.grid_forget()
                self.sidebar_tabs.grid(row=0, column=1, sticky="nsew")
            self.export_all()

    def hide_sidebar(self):
        if self.sidebar_favorites.grid_info() != {}:
            self.sidebar_favorites.grid_forget()
        if self.sidebar_tabs.grid_info() != {}:
            self.sidebar_tabs.grid_forget()

    def toggle_tabs(self):
        if self.sidebar_tabs.grid_info() == {}:
            if self.sidebar_favorites.grid_info() != {}:
                self.sidebar_favorites.grid_forget()
            self.sidebar_tabs.grid(row=0, column=1, sticky="nsew")
        else:
            self.sidebar_tabs.grid_forget()

    def toggle_favorites(self):
        if self.sidebar_favorites.grid_info() == {}:
            if self.sidebar_tabs.grid_info() != {}:
                self.sidebar_tabs.grid_forget()
            self.sidebar_favorites.grid(row=0, column=1, sticky="nsew")
        else:
            self.sidebar_favorites.grid_forget()

    def open_in_browser(self):
        if self.current_url != "":
            webbrowser.open_new_tab(self.current_url)

    def toggle_xml(self):
        if str(self.treeview) in self.content.panes():
            self.content.forget(self.treeview)
            self.menuActions.entryconfigure(2, label="View XML")
        else:
            self.content.add(self.treeview, weight=1)
            self.menuActions.entryconfigure(2, label="Hide XML")

    def insert_item(self, predecessor, element):
        if element.tag == "rss" or element.tag == "channel":
            treeview_item_id = self.treeview.insert(predecessor, "end", text=element.tag, open=True)
        else:
            treeview_item_id = self.treeview.insert(predecessor, "end", text=element.tag)
        for key, value in element.attrib.items():
            self.treeview.insert(treeview_item_id, "end", text=f"@{key}={value}")
        if element.text and element.text.strip():
            self.treeview.insert(treeview_item_id, "end", text=element.text.strip())
        for successor in element:
            self.insert_item(treeview_item_id, successor)

    def switch_theme(self):
        if self.text["bg"] == "#ffffff":
            bg, bg2, bg3, bg4, bg5, fg = "#111111", "#2d2d2d", "#3c3c3c", "#4d4d4d", "#444444", "#ffffff"
        else:
            bg, bg2, bg3, bg4, bg5, fg = "#ffffff", "#f0f0f0", "#e1e1e1", "#ffffff", "#bbbbbb", "#000000"
        self.style.configure("TPanedwindow", background=bg2)
        self.style.configure("TSeparator", background=bg2)
        self.reader.configure(bg=bg)
        for i in [self.titleLabel, self.dtLabel, self.text]:
            i.configure(bg=bg, fg=fg)
        self.text.tag_configure("sel", background=bg, foreground=fg)
        self.style.configure("Treeview", background=bg, foreground=fg)
        for i in [self.buttonActions, self.buttonPrevious, self.buttonNext, self.buttonRefresh, self.buttonFavorites, self.buttonTabs]:
            i.configure(bg=bg2, fg=fg, activebackground=bg5, activeforeground=fg)
            i.unbind("<Enter>")
            i.unbind("<Leave>")
            i.bind("<Enter>", lambda event, widget=i: widget.configure(bg=bg3, fg=fg))
            i.bind("<Leave>", lambda event, widget=i: widget.configure(bg=bg2, fg=fg))
        self.url_bar.configure(bg=bg4, fg=fg, insertbackground=fg)
        self.buttonOK.configure(bg=bg3, fg=fg, activebackground=bg5, activeforeground=fg)
        self.toolbar.configure(bg=bg2)
        for i in [self.labelFavorites, self.listboxFavorites, self.labelTabs, self.listboxTabs]:
            i.configure(bg=bg2, fg=fg)
        for i in [self.buttonFavorites1, self.buttonFavorites2, self.buttonFavorites3, self.buttonFavorites4, self.buttonTabs1, self.buttonTabs2, self.buttonTabs3, self.buttonTabs4, self.buttonTabs5]:
            i.configure(bg=bg2, fg=fg, activebackground=bg5, activeforeground=fg)
            i.unbind("<Enter>")
            i.unbind("<Leave>")
            i.bind("<Enter>", lambda event, widget=i: widget.configure(bg=bg3, fg=fg))
            i.bind("<Leave>", lambda event, widget=i: widget.configure(bg=bg2, fg=fg))
        for i in [self.menuActions, self.menu_B3_url_bar, self.menu_B3_favorites, self.menu_B3_tabs]:
            if bg == "#111111":
                i.configure(background="#000", foreground="#fff", activebackground="#333", activeforeground="#fff")
            else:
                i.configure(background="#f0f0f0", foreground="#000", activebackground="#ccc", activeforeground="#000")

    def help_window(self):
        window = tk.Toplevel()
        window.title("Help - Headlines4pc")
        window.geometry("700x510")
        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)
        try:
            window.iconbitmap("icon.ico")
        except:
            try:
                window.iconbitmap("")
            except:
                pass
        help_tabs = ttk.Notebook(window)
        help_tabs.grid(row=0, column=0, sticky="nsew")
        about = tk.Text(help_tabs, relief=tk.FLAT, border=16, font=(font.nametofont("TkDefaultFont").actual()["family"], 12), wrap=tk.WORD, background="#dedede")
        about.insert(tk.INSERT, f"Headlines4pc\nCopyright (c) 2025-{str(datetime.datetime.now().year)}: Waylon Boer\n\nHeadlines4pc is an RSS Feed reader with an easy-to-use user interface.")
        about.configure(state="disabled")
        help_tabs.add(about, text="About")
        mit_license = tk.Text(help_tabs, relief=tk.FLAT, border=16, font=(font.nametofont("TkDefaultFont").actual()["family"], 12), wrap=tk.WORD, background="#dedede")
        mit_license.insert(tk.INSERT, """MIT License

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
        mit_license.configure(state="disabled")
        help_tabs.add(mit_license, text="License")

if __name__ == "__main__":
    Headlines4pc()
