import random
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

######################### Functions #########################
def generate_account_number():
    return str(random.randint(1000000000, 9999999999))

def generate_username(name):
    username = name.split()[0][0].upper() + name.split()[1][0].upper() + str(random.randint(100, 999)) + str(random.randint(0, 99))
    return username
    
def login(connection, cursor):
    username = input("Zadejte uživatelské jméno: ")
    password = input("Zadejte heslo: ")
    cursor.execute("SELECT user_id, password, balance FROM accounts WHERE username=?", (username,))
    account = cursor.fetchone()
    connection.commit()
    if account:
        if account[1] == password:
            return account
        else:
            print("Chybné heslo.")
    else:
        print("Účet s tímto uživatelským jménem neexistuje.")
        
def register(connection, cursor):
    name = input("Zadejte jméno: ")
    dob = input("Zadejte datum narození (YYYY-MM-DD): ")
    address = input("Zadejte adresu: ")
    phone = input("Zadejte telefonní číslo: ")
    gender = input("Zadejte pohlaví (muž/žena): ")
    
    cursor.execute("INSERT INTO users (name, dob, address, phone, gender) VALUES (?, ?, ?, ?, ?)", (name, dob, address, phone, gender))
    user_id = cursor.lastrowid
    
    username = generate_username(name)
    password = input("Zadejte heslo: ")
    account_number = generate_account_number()
    cursor.execute("INSERT INTO accounts (username, password, balance, account_number, user_id) VALUES (?, ?, 0, ?, ?)", (username, password, account_number, user_id))
    connection.commit()
    
    print(f"Váš účet byl úspěšně vytvořen. Uživatelské jméno: {username}, číslo účtu: {account_number}")
    
def check_balance(connection, cursor, account):
    cursor.execute("SELECT balance FROM accounts WHERE user_id=?", (account[0],))
    balance = cursor.fetchone()
    connection.commit()
    print(f"Váš zůstatek je: {balance[0]} Kč")
    
def withdraw(connection, cursor, account):
    cursor.execute("SELECT balance FROM accounts WHERE user_id=?", (account[0],))
    balance = cursor.fetchone()
    connection.commit()
     
    amount = float(input("Zadejte částku k výběru: "))
    if balance[0] >= amount:
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE user_id=?", (amount, account[0]))
        connection.commit()
        print(f"Úspěšně jste vybrali {amount} Kč")  
        print(f"Nyní mátw zůstatek na účtu: {balance[0] - amount} Kč")
    else:
        print("Nedostatečný zůstatek na účtu.")
        
def deposit(connection, cursor, account):
    amount = float(input("Zadejte částku k vložení: "))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE user_id=?", (amount, account[0]))
    connection.commit()
    print(f"Úspěšně jste vložili {amount} Kč")
    
######################### Main App #########################

def main():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            gender TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_number TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            balance REAL NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    while True:
        print("\nVýběr z možností:")
        print("1. Přihlásit se")
        print("2. Registrovat se")
        print("3. Ukončit")
        
        choice = int(input("\nVyberte možnost: "))
        
        if choice == 1:
            account = login(conn, cursor)
            if account:
                while True:
                    print("\nVýběr z možností:")
                    print("1. Zobrazit zůstatek na účtu")
                    print("2. Vybrat peníze")
                    print("3. Vložit peníze")
                    print("4. Odhlásit se")
                    action = int(input("\nVyberte možnost: "))
                    if action == 1:
                        check_balance(conn, cursor, account)
                    elif action == 2:
                        withdraw(conn, cursor, account)
                    elif action == 3:
                        deposit(conn, cursor, account)
                    elif action == 4:
                        break
                        
        elif choice == 2:
            register(conn, cursor)
            
        elif choice == 3:
            conn.commit()
            conn.close()
            break

if __name__ == '__main__':
    main()