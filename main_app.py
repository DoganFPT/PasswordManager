import sqlite3
from cryptography.fernet import Fernet
import getpass

def generate_key():
    return Fernet.generate_key()

def load_key():
    try:
        with open("secret.key" , "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        key = generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
        return key

def encrypt_password(password, key):
    token = Fernet(key)
    encrypted_password = token.encrypt(password.encode())
    return encrypted_password

def decrypt_password(encrypted_pw, key):
    token = Fernet(key)
    decrypted_pw = token.decrypt(encrypted_pw).decode()
    return decrypted_pw

def conn_db():
    return sqlite3.connect("password_manager.db")

def create_table():
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY,
        website TEXT,
        username TEXT,
        password BLOB
    )
    """)
    conn.commit()
    conn.close()

def add_pw(website, username, password, key):
    encrypted_password = encrypt_password(password, key)
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO passwords (website, username, password) VALUES (?,?,?)",
                   (website, username, encrypted_password))
    conn.commit()
    conn.close()

def get_pw(website,key):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM passwords WHERE website=?", (website,))
    data = cursor.fetchone()
    conn.close()
    if data:
        username, encrypted_password = data
        password = decrypt_password(encrypted_password, key)
        return f"Website: {website} \nUsername: {username} \nPassword: {password}"
    else:
        return "No password was found for this website"

def is_empty():
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM passwords LIMIT 1;")
    data=cursor.fetchone()
    if data is None:
        print("Database is empty")

def list_all_pw(key):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("SELECT website, username, password FROM passwords")
    data = cursor.fetchall()
    conn.close()
    for website, username, encrypted_password in data:
        if data is None:
            print("Keine eintrage")
        password = decrypt_password(encrypted_password, key)
        print(f"Website: {website},\nUsername: {username}, \nPassword: {password}\n")

def delete_password(website):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords WHERE website=?",(website,))
    conn.commit()
    conn.close()

def main():
    key = load_key()
    db = create_table()
    while True:
        print("\nPassword Manager")
        print("1 for add password")
        print("2 for get a password")
        print("3 for delete a password")
        print("4 for List all passwords")
        print("5 for exit")
        choice = input("What operation do you want to run:")

        if choice == "1":
            website = input("which website:")
            username = input("what is your username:")
            password = getpass.getpass("Enter password:")
            add_pw(website, username, password, key)
            print("Password added succesfully")
        elif choice == "2":
            website = input("Enter website:")
            print(get_pw(website,key))
        elif choice == "3":
            website = input("Enter website:")
            delete_password(website)
            print(f"Password for {website} deleted succesfully")
        elif choice == "4":
            is_empty()
            list_all_pw(key)
        elif choice == "5":
            print("Exit Menu")
            break
        else:
            print("Error,Invalid choice")



if __name__ == "__main__":
    main()

