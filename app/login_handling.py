import json
import bcrypt
import database


def new_user(username, password):
    salt = bcrypt.gensalt(rounds=8)
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    if database.check_for_user(username):
        print("Username already exists")
        return hashed_password, salt, False
    return hashed_password, salt, True


def authenticate(username, password):
    if not database.check_for_user(username):
        print("Username does not exist")
        return False
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), database.get_user_salt(username))
    hashed_db_password = database.get_user_password(username)
    return hashed_password == hashed_db_password


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
    hashed_password, salt, success = new_user(username, password)
    if success:
        print("Registration successful")
    else:
        print("Registration failed")
        return
    print("Enter your name")
    name = input("Name: ")

    refered = input("Were you referred by another user? (y/n): ")
    if refered == "y":
        while True:
            referer = input(
                "Enter the name of the person who referred you (exit for exit): ")
            if referer == "exit":
                break
            if database.check_for_user(referer):
                database.create_new_user(
                    username, hashed_password, salt, name, referer)
                return username
            else:
                print("Name not found. Try again.")
    database.create_new_user(username, hashed_password, salt, name, None)
    return username


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
