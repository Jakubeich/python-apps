import random
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cv2
import os

import numpy as np
from PIL import Image

class BankAccountApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bankovní účet")
        self.root.geometry("300x300")

        self.username_label = tk.Label(self.root, text="Uživatelské jméno")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        self.password_label = tk.Label(self.root, text="Heslo")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        
        self.space = tk.Label(self.root, text="")
        self.space.pack()

        self.login_button = tk.Button(self.root, text="Přihlásit", command=self.login)
        self.login_button.pack()
        
        self.space = tk.Label(self.root, text="")
        self.space.pack()
        
        # tlačítko pro přihlášení obličejem
        self.face_login_button = tk.Button(self.root, text="Přihlásit obličejem", command=self.face_login)
        self.face_login_button.pack()
        
        self.space = tk.Label(self.root, text="")
        self.space.pack()

        self.register_button = tk.Button(self.root, text="Zaregistrovat", command=self.show_register)
        self.register_button.pack()

        self.conn = sqlite3.connect('bank.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                gender TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                balance REAL NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                account_number TEXT NOT NULL,
                FOREIGN KEY (account_number) REFERENCES accounts(account_number)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                face TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()
        
        self.faces_folder = "faces/"
        self.login_faces_folder = "login_faces/"
        self.login_face_path = "login_faces/login_face.jpg"
    
    ### functions for showing widgets ###
            
    def show_login(self):
        self.clear_widgets()

        self.username_label = tk.Label(self.root, text="Uživatelské jméno")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        self.password_label = tk.Label(self.root, text="Heslo")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.root, text="Přihlásit", command=self.login)
        self.login_button.pack()
        
        # tlačítko pro přihlášení obličejem
        self.face_login_button = tk.Button(self.root, text="Přihlásit obličejem", command=self.face_login)
        self.face_login_button.pack()

        self.register_button = tk.Button(self.root, text="Zaregistrovat", command=self.show_register)
        self.register_button.pack()

    def show_dashboard(self, account):
        self.clear_widgets()
    
        print("account tuple:", account)

        self.user_id = account[0]
        self.balance = account[2]
        self.account_number = account[1]  # Store account_number as an attribute

        # zustatek na učtě
        self.balance_label = tk.Label(self.root, text="Zůstatek: {} Kč".format(self.balance))
        self.balance_label.pack()

        # zobrazit detaily uživatele
        self.user_details_button = tk.Button(self.root, text="Detaily uživatele", command=self.show_user_details)
        self.user_details_button.pack()

        self.deposit_button = tk.Button(self.root, text="Vložit", command=self.show_deposit)
        self.deposit_button.pack()

        self.withdraw_button = tk.Button(self.root, text="Vybrat", command=self.show_withdraw)
        self.withdraw_button.pack()

        self.transactions_button = tk.Button(self.root, text="Transakce", command=self.show_transactions)
        self.transactions_button.pack()

        self.logout_button = tk.Button(self.root, text="Odhlásit", command=self.logout)
        self.logout_button.pack()
        
    def show_user_details(self):
        self.clear_widgets()
        
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (self.user_id,))
        user = self.cursor.fetchone()
        self.conn.commit()
        
        self.cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (self.user_id,))
        account = self.cursor.fetchone()
        self.conn.commit()
        
        self.name_label = tk.Label(self.root, text="Jméno: {}".format(user[1]))
        self.name_label.pack()
        
        self.dob_label = tk.Label(self.root, text="Datum narození: {}".format(user[2]))
        self.dob_label.pack()
        
        self.address_label = tk.Label(self.root, text="Adresa: {}".format(user[3]))
        self.address_label.pack()
        
        self.phone_label = tk.Label(self.root, text="Telefon: {}".format(user[4]))
        self.phone_label.pack()
        
        self.gender_label = tk.Label(self.root, text="Pohlaví: {}".format(user[5]))
        self.gender_label.pack()
        
        self.account_number_label = tk.Label(self.root, text="Číslo účtu: {}".format(account[0]))
        self.account_number_label.pack()
        
        self.back_button = tk.Button(self.root, text="Zpět", command=self.back_to_dashboard)
        self.back_button.pack()
        
    def show_deposit(self):
        self.clear_widgets()

        self.amount_label = tk.Label(self.root, text="Částka")
        self.amount_label.pack()

        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack()

        self.deposit_button = tk.Button(self.root, text="Vložit", command=self.deposit)
        self.deposit_button.pack()

        self.back_button = tk.Button(self.root, text="Zpět", command=self.back_to_dashboard)
        self.back_button.pack()
        
    def show_withdraw(self):
        self.clear_widgets()

        self.amount_label = tk.Label(self.root, text="Částka")
        self.amount_label.pack()

        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack()

        self.confirm_button = tk.Button(self.root, text="Potvrdit", command=self.withdraw)
        self.confirm_button.pack()

        self.back_button = tk.Button(self.root, text="Zpět", command=self.back_to_dashboard)
        self.back_button.pack()
        
    def show_transactions(self):
        self.clear_widgets()

        self.cursor.execute("SELECT * FROM transactions WHERE account_number = ?", (self.account_number,))
        transactions = self.cursor.fetchall()
        
        self.transactions_label = tk.Label(self.root, text="Transakce")
        self.transactions_label.pack()
         
        for transaction in transactions:
            self.transaction_label = tk.Label(self.root, text="Částka: {} Kč, Datum: {}".format(transaction[2], transaction[3]))
            self.transaction_label.pack()
        
        self.back_button = tk.Button(self.root, text="Zpět", command=self.back_to_dashboard)
        self.back_button.pack()
        
    def show_register(self):
        self.clear_widgets()
        
        self.name_label = tk.Label(self.root, text="Jméno")
        self.name_label.pack()
        
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()
        
        self.dob_label = tk.Label(self.root, text="Datum narození")
        self.dob_label.pack()
        
        self.dob_entry = tk.Entry(self.root)
        self.dob_entry.pack()
        
        self.address_label = tk.Label(self.root, text="Adresa")
        self.address_label.pack()
        
        self.address_entry = tk.Entry(self.root)
        self.address_entry.pack()
        
        self.phone_label = tk.Label(self.root, text="Telefon")
        self.phone_label.pack()
        
        self.phone_entry = tk.Entry(self.root)
        self.phone_entry.pack()
        
        self.gender_label = tk.Label(self.root, text="Pohlaví")
        self.gender_label.pack()
        
        self.gender_entry = tk.Entry(self.root) 
        self.gender_entry.pack()
        
        self.password_label = tk.Label(self.root, text="Heslo")
        self.password_label.pack()
        
        self.password_entry = tk.Entry(self.root)
        self.password_entry.pack()
        
        self.confirm_button = tk.Button(self.root, text="Potvrdit", command=self.register)
        self.confirm_button.pack()
        
        self.back_button = tk.Button(self.root, text="Zpět", command=self.back_to_login)
        self.back_button.pack()
        
    ### functions for clearing widgets and doing operations ###
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.cursor.execute("SELECT user_id, password, balance FROM accounts WHERE username=?", (username,))
        account = self.cursor.fetchone()
        self.conn.commit()

        if account:
            if account[1] == password:
                self.show_dashboard(account)
            else:
                messagebox.showerror("Chyba", "Chybné heslo.")
        else:
            messagebox.showerror("Chyba", "Účet s tímto uživatelským jménem neexistuje.")
            
    # funkce pro přihlášení obličejem uživatele do aplikace (přes knihovnu OpenCV)
    def face_login(self):
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        def get_images_and_labels(path):
            image_paths = [os.path.join(path, f) for f in os.listdir(path)]
            face_samples = []
            ids = []

            for image_path in image_paths:
                PIL_img = Image.open(image_path).convert('L')
                img_numpy = np.array(PIL_img, 'uint8')
                id = int(os.path.split(image_path)[-1].split('.')[0])
                faces = face_cascade.detectMultiScale(img_numpy)
                for (x, y, w, h) in faces:
                    face_samples.append(img_numpy[y:y + h, x:x + w])
                    ids.append(id)
            return face_samples, ids

        faces, ids = get_images_and_labels(self.faces_folder)
        recognizer.train(faces, np.array(ids))

        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                cv2.imwrite(self.login_face_path, roi_gray)
                user_id, confidence = recognizer.predict(roi_gray)

                if confidence >= 45 and confidence <= 85:
                    self.cursor.execute("SELECT user_id, password, balance, username, account_number FROM accounts WHERE user_id=?", (user_id,))
                    account = self.cursor.fetchone()
                    self.conn.commit()
                    if account:  # Add this check
                        self.show_dashboard(account)
                        cap.release()
                        cv2.destroyAllWindows()
                        break
                    else:
                        messagebox.showerror("Chyba", "Účet pro tohoto uživatele nebyl nalezen.")  # Show an error message if no account is found

            cv2.imshow("frame", frame)

            if cv2.waitKey(20) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        
    def deposit(self):
        amount = self.amount_entry.get()
        
        self.cursor.execute("SELECT account_number FROM accounts WHERE user_id=?", (self.user_id,))
        self.account_number = self.cursor.fetchone()[0]
        self.conn.commit()

        if amount.isdigit():
            amount = int(amount)

            self.balance += amount

            self.cursor.execute("UPDATE accounts SET balance=? WHERE user_id=?", (self.balance, self.user_id))
            self.conn.commit()

            self.cursor.execute("INSERT INTO transactions (amount, account_number) VALUES (?, ?)", (amount, self.account_number))
            self.conn.commit()

            messagebox.showinfo("Úspěch", "Vklad proběhl úspěšně.")
        else:
            messagebox.showerror("Chyba", "Částka musí být číslo.")
        
    def withdraw(self):
        amount = self.amount_entry.get()
        
        self.cursor.execute("SELECT account_number FROM accounts WHERE user_id=?", (self.user_id,))
        self.account_number = self.cursor.fetchone()[0]
        self.conn.commit()

        if amount.isdigit():
            amount = int(amount)

            if amount <= self.balance:
                self.balance -= amount

                self.cursor.execute("UPDATE accounts SET balance=? WHERE user_id=?", (self.balance, self.user_id))
                self.cursor.execute("INSERT INTO transactions (amount, account_number) VALUES (?, ?)", (-amount, self.account_number))
                
                self.conn.commit()

                messagebox.showinfo("Úspěch", "Výběr proběhl úspěšně.")
                self.show_dashboard((self, self.user_id, self.balance))
            else:
                messagebox.showerror("Chyba", "Nedostatek peněz na účtu.")
        else:
            messagebox.showerror("Chyba", "Částka musí být číslo.")
        
    def register(self):
        # zapnout kameru a získat obrázek obličeje uživatele pro přihlášení obličejem (přes knihovnu OpenCV)
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        # udělej při získání obrázku náhodné jméno a soubor ulož do složky faces v aktuálním adresáři a zároveň ulož toto jméno fotky do databáze
        face_name = str(random.randint(0, 100000000000))
        cv2.imwrite("faces/" + face_name + ".jpg", frame)
        cap.release()
        cv2.destroyAllWindows()
        
        name = self.name_entry.get()
        dob = self.dob_entry.get()
        address = self.address_entry.get()
        phone = self.phone_entry.get()
        gender = self.gender_entry.get()
        password = self.password_entry.get()
        
        username = self.generate_username(name)
        account_number = self.generate_account_number()

        self.cursor.execute("INSERT INTO users (name, dob, address, phone, gender) VALUES (?, ?, ?, ?, ?)", (name, dob, address, phone, gender))
        user_id = self.cursor.lastrowid
        self.conn.commit()
        
        self.cursor.execute("INSERT INTO accounts (username, password, balance, account_number, user_id) VALUES (?, ?, 0, ?, ?)", (username, password, account_number, user_id))
        self.conn.commit()
        
        self.cursor.execute("INSERT INTO faces (user_id, face) VALUES (?, ?)", (user_id, face_name + ".jpg"))
        self.conn.commit()

        messagebox.showinfo("Info", "Registrace byla úspěšná, vaše uživatelské jméno je: {}".format(username))
        self.back_to_login()
        
    def logout(self):
        self.clear_widgets()
        self.show_login()
        
    ### functions for generating data ###
    def generate_username(self, name):
        username = name.split()[0][0].upper() + name.split()[1][0].upper() + str(random.randint(100, 999)) + str(random.randint(0, 99))
        return username
    
    def generate_account_number(self):
        account_number = str(random.randint(1000000000, 9999999999))
        return account_number
    
    ### support functions ###
    def back_to_dashboard(self):
        self.clear_widgets()
        self.show_dashboard((self, self.user_id, self.balance))
        
    def back_to_login(self):
        self.clear_widgets()
        self.show_login()
        
    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
if __name__ == "__main__":
    root = tk.Tk()
    BankAccountApp(root)
    root.mainloop()