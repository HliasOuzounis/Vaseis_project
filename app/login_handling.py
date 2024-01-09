import json
import bcrypt
import database





def new_user(username, password, passwords):
    if username in passwords:
        print("Username already exists")
        return False
    salt = bcrypt.gensalt(rounds = 14)
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    passwords[username] = (hashed_password.decode("utf-8"), salt.decode("utf-8"))
    with open(passwords_filename, "w") as f:
        json.dump(passwords, f)
    return True
    
def authenticate(username, password, passwords):
    if username not in passwords:
        print("Username does not exist")
        return False
    stored_hashed_password, salt = passwords[username]
    stored_hashed_password = stored_hashed_password
    salt = salt.encode("utf-8")
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


    if stored_hashed_password!= hashed_password:
        print("Incorrect password")
        return False
    return 

def login():
    print("Enter your username and password")
    username = input("Username: ")
    password = input("Password: ")
    if authenticate(username, password):
        print("Login successful")
        return username
    else:
        print("Login failed")
        return

def register():

    print("Enter your username and password")
    username = input("Username: ")
    password = input("Password: ")
    password_confirm = input("Confirm password: ")
    if password != password_confirm:
        print("Passwords do not match")
        return
    if new_user(username, password):
        print("Registration successful")
        return username
    else:
        print("Registration failed")
        return
    
    refered = input("Were you referred by another user? (y/n): ")
    if refered == "y":
        while True:
            referer = input("Enter the name of the person who referred you (exit for exit): ")
            if referer == "exit":
                break
            if database.check_for_user(referer):
                database.create_new_user(username, referer)
                return
            else:
                print("Name not found. Try again.")
    database.create_new_user(username)

def main():
    print("Welcome to the app, select an option:")
    print("1. Login")
    print("2. Register")
    choice = input("Enter your choice: ")
    if choice == "1":
        login()
    elif choice == "2":
        register()
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    passwords_filename = "passwords.json"

    try:
        with open(passwords_filename, "r") as f:
            passwords = json.load(f)
    except FileNotFoundError:
        passwords = {}

    main()
    