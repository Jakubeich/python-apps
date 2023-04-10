import socket
import threading
import tkinter as tk
from tkinter import simpledialog

SERVER_HOST = '127.0.0.1'  # IP adresa serveru
SERVER_PORT = 8000  # Port serveru

class ChatGUI(tk.Tk):
    def __init__(self, username):
        super().__init__()
        # po kliknutí na zavřít, tak se mi vypkne aplikace
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title(f"Chat - {username}")
        self.username = username

        # Vytvoření pole pro zobrazení zpráv
        self.messages_frame = tk.Frame(self)
        self.my_msg = tk.StringVar()  # pro uložení zprávy
        self.my_msg.set("")
        self.scrollbar = tk.Scrollbar(self.messages_frame)  # pro posouvání zpráv
        self.messages_list = tk.Listbox(self.messages_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.messages_frame.pack()

        # Vytvoření pole pro zadání zprávy
        self.message_entry = tk.Entry(self, textvariable=self.my_msg, width=50)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.pack(pady=10)

        # Vytvoření tlačítka pro odeslání zprávy
        self.send_button = tk.Button(self, text="Odeslat", command=self.send_message)
        self.send_button.pack()

        # Vytvoření socketu pro klienta a připojení k serveru
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_HOST, SERVER_PORT))
        self.client_socket.send(username.encode())

        # Vytvoření vlákna pro přijetí zpráv od serveru
        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.start()

    def send_message(self, event=None):
        """Odeslání zprávy na server a vymazání zprávy z pole pro zadání zprávy"""
        message = self.my_msg.get()
        self.client_socket.send(message.encode())
        self.my_msg.set("")
        
    def receive_message(self):
        """Přijetí zprávy od serveru"""
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                self.messages_list.insert(tk.END, message)
            except OSError:
                break
            
    # funkce pro zavření okna a ukončení aplikace
    def on_closing(self, event=None):
        self.client_socket.close()
        self.destroy()
        self.quit()

class LoginGUI(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Uživatelské jméno:").grid(row=0)
        self.username = tk.Entry(master)
        self.username.grid(row=0, column=1)
        
        # pokud je uzivatelske jmeno zadano, vrati se a tohle okno se zavre
        if self.username.get():
            self.apply()
            self.destroy()

    def apply(self):
        self.username = self.username.get()
            
if __name__ == "__main__":
    # Skrytí hlavního okna
    root = tk.Tk()
    root.withdraw()

    # Vytvoření instance LoginGUI pro zadání uživatelského jména
    login_gui = LoginGUI(root)
    
    # Pokud je uživatelské jméno zadáno, spustí se GUI pro chat a všechna ostatní okna se zavrou
    root.withdraw()

    # Spuštění GUI
    chat_gui = ChatGUI(login_gui.username)
    chat_gui.mainloop()
    
    root.destroy()