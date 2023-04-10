import socket
import threading
import tkinter as tk

SERVER_HOST = '0.0.0.0'  # IP adresa serveru
SERVER_PORT = 8000  # Port serveru

# Vytvoření socketu pro server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Přiřazení IP adresy a portu k serverovému socketu
server_socket.bind((SERVER_HOST, SERVER_PORT))

# Poslouchání připojení od klientů
server_socket.listen()

# Seznam připojení klientů a jejich uživatelských jmen
clients = {}
# Seznam připojení klientů, kteří se budou odpojovat
disconnecting_clients = []

def broadcast_message(message, sender):
    """Odeslat zprávu všem připojeným klientům"""
    sender_username = clients[sender]
    for client_socket in clients:
        # Přidání jména odesílatele k zprávě
        if client_socket != sender:
            client_socket.send(f"{sender_username}: {message}".encode())

def handle_client_connection(client_socket, client_address):
    """Obsluha připojení od klienta"""
    print(f"Nové připojení od klienta: {client_address}")
    
    # Přihlášení uživatele
    username = client_socket.recv(1024).decode().strip()
    clients[client_socket] = username
    print(f"{username} se připojil k chatu.")

    # Přijímání zpráv od klienta a odesílání všem připojeným klientům
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                print(f"{username}: {message.decode().strip()}")
                broadcast_message(message, client_socket)
            else:
                # Pokud klient ukončí spojení
                disconnecting_clients.append(client_socket)
                client_socket.close()
                del clients[client_socket]
                print(f"{username} se odpojil.")
                break
        except ConnectionResetError:
            # Pokud dojde k neočekávanému ukončení spojení klienta
            disconnecting_clients.append(client_socket)
            client_socket.close()
            del clients[client_socket]
            print(f"{username} se odpojil.")
            break

# Spuštění vlákna pro přijímání a odesílání zpráv
while True:
    client_socket, client_address = server_socket.accept()
    receive_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address))
    receive_thread.daemon = True
    receive_thread.start()