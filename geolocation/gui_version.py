import tkinter as tk
from geopy.geocoders import Nominatim
import folium
import socket
import webbrowser
import os
import sqlite3

# vytvoření databáze pro historii vyhledávání
def create_history_table():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY, address TEXT)''')
    conn.commit()
    conn.close()

# uložení adresy do databáze
def save_to_history(address):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (address) VALUES (?)", (address,))
    conn.commit()
    conn.close()

# získání historie z databáze
def get_history():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("SELECT address FROM history")
    history = c.fetchall()
    conn.close()
    return history

def show_history():
    history = get_history()
    history_listbox.delete(0, tk.END)
    for item in history:
        history_listbox.insert(tk.END, item)
        
def show_history_details():
    selected_item = history_listbox.get(history_listbox.curselection())
    geolocator = Nominatim(user_agent="geoapiExercises", timeout=10)
    location = geolocator.geocode(selected_item)
    if location is None:
        output_label.config(text="Geolocation not successful. Please check the IP address and try again.")
    else:
        details_frame = tk.Frame(root)
        details_frame.pack(side=tk.LEFT, padx=10)
        details_label = tk.Label(details_frame, text=f"IP Address: { selected_item }\nLatitude: {location.latitude}\nLongitude: {location.longitude}\nCountry: {location.address.split(',')[-1]}", bg="white", wraplength=300)
        details_label.pack()
        copy_button = tk.Button(details_frame, text="Copy", command=lambda: copy_to_clipboard(details_label.cget("text")))
        copy_button.pack()
        
def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)

def get_ip_address():
    url = entry_domain.get()
    try:
        ip_address_from_domain = socket.gethostbyname(url)
        output_label.config(text=f"IP address for {url} is {ip_address_from_domain}")
        save_to_history(url)
    except socket.gaierror:
        output_label.config(text="Invalid URL. Please check the URL and try again.")

def get_location():
    ip = entry_ip.get()
    geolocator = Nominatim(user_agent="geoapiExercises", timeout=10)
    location = geolocator.geocode(ip)
    if location is None:
        output_label.config(text="Geolocation not successful. Please check the IP address and try again.")
    else:
        map = folium.Map(location=[location.latitude, location.longitude], zoom_start=10)
        folium.Marker(location=[location.latitude, location.longitude]).add_to(map)
        file_name = entry_file.get()
        file_name += ".html"
        map.save(file_name)
        webbrowser.open(file_name)
        output_label.config(text=f"IP Address: { ip }\nLatitude: {location.latitude}\nLongitude: {location.longitude}\nCountry: {location.address.split(',')[-1]}")
        
def open_map():
    file_name = map_listbox.get(map_listbox.curselection())
    webbrowser.open(file_name)

def show_maps():
    map_files = [f for f in os.listdir() if f.endswith(".html")]
    map_listbox.delete(0, tk.END)
    for file in map_files:
        map_listbox.insert(tk.END, file)
    if map_listbox.size()>0:
        open_map_button.config(state=tk.NORMAL)
        rename_map_button.config(state=tk.NORMAL)
        delete_map_button.config(state=tk.NORMAL)
    else:
        open_map_button.config(state=tk.DISABLED)
        rename_map_button.config(state=tk.DISABLED)
        delete_map_button.config(state=tk.DISABLED)
        
def rename_map():
    selected_map = map_listbox.get(map_listbox.curselection())
    new_name = entry_new_name.get()
    if not new_name.endswith(".html"):
        new_name += ".html"
    os.rename(selected_map, new_name)
    show_maps()

def delete_map():
    selected_map = map_listbox.get(map_listbox.curselection())
    os.remove(selected_map)
    show_maps()

# vytvoření databáze pro historii vyhledávání
create_history_table()

root = tk.Tk()
root.title("IP Address and Location Finder")
root.geometry("420x750")
root.configure(bg="white")

# Vytvoření rámce pro zobrazování seznamu map
map_frame = tk.Frame(root, bg="white")
map_frame.pack(fill=tk.BOTH, expand=True)

# Tlačítko pro zobrazení seznamu map
show_maps_button = tk.Button(map_frame, text="Show maps in directory", command=show_maps)
show_maps_button.grid(row=0, column=0, padx=5, pady=5)

# Seznam map
map_listbox = tk.Listbox(map_frame)
map_listbox.grid(row=1, column=0, padx=5, pady=5, rowspan=5, columnspan=2, sticky="nsew")

# Tlačítko pro otevření vybrané mapy
open_map_button = tk.Button(map_frame, text="Open map", command=open_map, state=tk.DISABLED)
open_map_button.grid(row=6, column=0, padx=5, pady=5)

# Tlačítko pro smazání mapy
delete_map_button = tk.delete_map_button = tk.Button(map_frame, text="Delete map", command=delete_map, state=tk.DISABLED)
delete_map_button.grid(row=6, column=1, padx=5, pady=5)

# Input pro zadání nového jména mapy
label = tk.Label(map_frame, text="Enter the new name:")
label.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")

entry_new_name = tk.Entry(map_frame)
entry_new_name.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Tlačítko pro přejmenování mapy
rename_map_button = tk.Button(map_frame, text="Rename map", command=rename_map, state=tk.DISABLED)
rename_map_button.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

# Tlačítko pro zobrazení historie vyhledávaných adres
show_history_button = tk.Button(root, text="Show search history", command=show_history)
show_history_button.pack()

# Seznam historie vyhledávaných adres
history_listbox = tk.Listbox(root)
history_listbox.pack()

# Tlačítko pro zobrazení specifikace vyhledávání
show_history_details_button = tk.Button(root, text="Show details", command=show_history_details, state=tk.DISABLED)
show_history_details_button.pack()

history_listbox.bind('<<ListboxSelect>>', lambda event: show_history_details_button.config(state=tk.NORMAL))

# vytvoření rámce pro zobrazení výstupu
input_frame = tk.Frame(root, bg="white")
input_frame.pack(fill=tk.X, pady=5)

# input pro zadání doménového jména nebo IP adresy
label = tk.Label(input_frame, text="Enter the domain name or URL:")
label.pack(side=tk.LEFT, padx=5)

entry_domain = tk.Entry(input_frame)
entry_domain.pack(side=tk.LEFT, padx=5)

# tlačítko pro získání IP adresy
button_ip = tk.Button(input_frame, text="Get IP address", command=get_ip_address)
button_ip.pack(side=tk.LEFT, padx=5)

# vytvoření rámce pro zobrazení výstupu
input_frame = tk.Frame(root, bg="white")
input_frame.pack(fill=tk.X, pady=10)

# input pro zadání IP adresy
label = tk.Label(input_frame, text="Enter the IP address:")
label.pack(side=tk.LEFT, padx=5)

entry_ip = tk.Entry(input_frame)
entry_ip.pack(side=tk.LEFT, padx=5)

# tlačítko pro získání polohy
button_location = tk.Button(input_frame, text="Get location", command=get_location)
button_location.pack(side=tk.LEFT, padx=5)

# vytvoření rámce pro zobrazení výstupu
input_frame = tk.Frame(root, bg="white")
input_frame.pack(fill=tk.X, pady=10)

# input pro zadání názvu souboru pro uložení mapy
label = tk.Label(input_frame, text="Enter the name of the file to save the map:")
label.pack(side=tk.LEFT, padx=5)

entry_file = tk.Entry(input_frame)
entry_file.pack(side=tk.LEFT, padx=5)

# textové pole pro výpis informací
output_label = tk.Label(root, bg="white", wraplength=300)
output_label.pack(fill=tk.X, pady=10)

root.mainloop()