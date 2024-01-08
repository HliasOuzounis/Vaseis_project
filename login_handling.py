import json
import bcrypt





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
    return True

def login():
    print("Enter your username and password")
    username = input("Username: ")
    password = input("Password: ")
    if authenticate(username, password):
        print("Login successful")
    else:
        print("Login failed")

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
    else:
        print("Registration failed")

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
    