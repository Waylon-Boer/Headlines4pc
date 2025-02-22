from tkinter import *
from tkinter.ttk import Entry, Button, Style
from tkinter import Button as tkButton
from tkinter.filedialog import *
from urllib.request import *
import re, html

def load_headlines():
    data = urlopen(bar.get()).read().decode("utf8")
    news = re.findall(r'<title>(.*?)</title>', data)
    listbox.delete(0, END)
    for i in news:
        listbox.insert(END, html.unescape(i).replace("<![CDATA[", "").replace("]]>", ""))

def theme1():
    root["bg"] = "SystemButtonFace"
    style.configure("TEntry", background="SystemButtonFace")
    style.configure("TButton", background="SystemButtonFace")
    listbox.configure(bg="#fff", fg="#000")
    button5.configure(bg="SystemButtonFace", fg="#000")
    button6.configure(bg="SystemButtonFace", fg="#000")

def theme2():
    root["bg"] = "SystemButtonFace"
    style.configure("TEntry", background="SystemButtonFace")
    style.configure("TButton", background="SystemButtonFace")
    listbox.configure(bg="#dcb", fg="#000")
    button5.configure(bg="SystemButtonFace", fg="#000")
    button6.configure(bg="SystemButtonFace", fg="#000")

def theme3():
    root["bg"] = "#222"
    style.configure("TEntry", background="#222")
    style.configure("TButton", background="#222")
    listbox.configure(bg="#222", fg="#fff")
    button5.configure(bg="#222", fg="#fff")
    button6.configure(bg="#222", fg="#fff")

def theme4():
    root["bg"] = "#000"
    style.configure("TEntry", background="#000")
    style.configure("TButton", background="#000")
    listbox.configure(bg="#000", fg="#fff")
    button5.configure(bg="#222", fg="#fff")
    button6.configure(bg="#222", fg="#fff")

def save_as():
    data = urlopen(bar.get()).read().decode("utf8")
    filepath = asksaveasfilename(defaultextension=".rss", filetypes=[("Really Simple Syndication", "*.rss*")])
    open(filepath, "w", encoding='utf8').write(data)

root = Tk()
root.title("Headlines4pc")
root.geometry("800x600")
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
f = Frame(root)
f.grid(row=0, column=0, sticky="nsew", padx=64, pady=16)
f.columnconfigure(0, weight=1)
bar = Entry(f, font=("Segoe UI", 11))
bar.grid(row=0, column=0, sticky="nsew")
bar.bind("<Return>", lambda a: load_headlines())
action_button = Button(f, text="OK", command=load_headlines)
action_button.grid(row=0, column=1, sticky="nsew", ipady=4)
content = Frame(root, bd=0)
content.grid(row=1, column=0, sticky="nsew")
content.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)
listbox = Listbox(content, font=("Segoe UI", 12), relief=FLAT)
listbox.grid(row=0, column=0, sticky="nsew")
scrollbar = Scrollbar(content, orient=VERTICAL, command=listbox.yview)
scrollbar.grid(row=0, column=1, sticky="nsew")
listbox.configure(yscrollcommand=scrollbar.set)
toolbar = Frame(root)
toolbar.grid(row=2, column=0, sticky="nsew")
for i in range(0, 6):
    toolbar.columnconfigure(i, weight=1)
button1 = tkButton(toolbar, relief=FLAT, bg="#fff", fg="#000", font=("Segoe Fluent Icons", 13), text="", command=theme1)
button1.grid(row=0, column=0, sticky="nsew", ipady=4)
button2 = tkButton(toolbar, relief=FLAT, bg="#dcb", fg="#000", font=("Segoe Fluent Icons", 13), text="", command=theme2)
button2.grid(row=0, column=1, sticky="nsew")
button3 = tkButton(toolbar, relief=FLAT, bg="#222", fg="#fff", font=("Segoe Fluent Icons", 13), text="", command=theme3)
button3.grid(row=0, column=2, sticky="nsew")
button4 = tkButton(toolbar, relief=FLAT, bg="#000", fg="#fff", font=("Segoe Fluent Icons", 13), text="", command=theme4)
button4.grid(row=0, column=3, sticky="nsew")
button5 = tkButton(toolbar, relief=FLAT, font=("Segoe Fluent Icons", 13), text="", command=lambda: root.attributes("-fullscreen", not root.attributes("-fullscreen")))
button5.grid(row=0, column=4, sticky="nsew")
button6 = tkButton(toolbar, relief=FLAT, font=("Segoe Fluent Icons", 13), text="", command=save_as)
button6.grid(row=0, column=5, sticky="nsew")
style = Style()

root.mainloop()