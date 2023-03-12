import socket
import webbrowser
import folium
import tkinter as tk
from geopy.geocoders import Nominatim

# dotaz jestli chcete zadat ip adresu a získat polohu nebo jenom ip adresu z doménového jména
def get_choice():
    print("1. Get IP address from a domain name or URL")
    print("2. Get location from an IP address")
    print("3. Exit")
    choice = input("Enter your choice: ")
    return choice

choice = get_choice()
while choice != "3":
    if choice == "1":
        # získat ip adresu z daného doménového jména nebo webu
        def get_ip_address(url):
            try:
                ip_address_from_domain = socket.gethostbyname(url)
                return ip_address_from_domain
            except socket.gaierror:
                print("Invalid URL. Please check the URL and try again.")
                return None
            
        domain_name = input("Enter the domain name or URL: ")
        ip_address_from_domain = get_ip_address(domain_name)
        print(f"IP address for {domain_name} is {ip_address_from_domain}")
    elif choice == "2":
        # získat polohu zadané ip adresy
        def get_location(ip):
            geolocator = Nominatim(user_agent="geoapiExercises", timeout=10)
            location = geolocator.geocode(ip)
            if location is None:
                print("Geolocation not successful. Please check the IP address and try again.")
                return None
            map = folium.Map(location=[location.latitude, location.longitude], zoom_start=10)
            folium.Marker(location=[location.latitude, location.longitude]).add_to(map)
            return map
        
        ip_address = input("Enter the IP address: ")
        map = get_location(ip_address)
        
        # uložení mapy do html souboru a otevření v prohlížeči
        if map is not None:
            file_name = input("Enter the name of the file to save the map: ")
            file_name += ".html"
            map.save(file_name)
            webbrowser.open(file_name)
            
        # získání souřadnic a země zadané ip adresy
        geolocator = Nominatim(user_agent="geoapiExercises", timeout=10)
        location = geolocator.geocode(ip_address)
        if location is not None:
            print(f"Latitude: {location.latitude}")
            print(f"Longitude: {location.longitude}")
            print(f"Country: {location.address.split(',')[-1]}")
        
    else:
        print("Invalid choice. Please try again.")
    choice = get_choice()