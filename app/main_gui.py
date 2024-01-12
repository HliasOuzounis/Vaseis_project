import tkinter as tk
from PIL import ImageTk, Image

import login_handling
import database
import user

WIDTH = 500
HEIGHT = 500
bg_color = "#e6e6e6"


class MyFrame:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(master, width=WIDTH, height=HEIGHT, bg=bg_color)
        self.frame.pack(fill="both", expand=True)

    def show(self):
        self.frame.pack()

    def hide(self):
        self.frame.pack_forget()


class App:
    def __init__(self, master):
        self.master = master
        self.master.title("App")
        self.master.geometry(f"{WIDTH}x{HEIGHT}")
        self.master.resizable(False, False)
        self.master.config(bg=bg_color)

        self.login_frame = LoginFrame(
            self.master, self.switch_to_main_app, self.switch_to_register
        )
        self.register_frame = RegisterFrame(
            self.master, self.switch_to_main_app, self.switch_to_login
        )
        self.main_frame = MainFrame(self.master, self.switch_to_login)

        self.switch_to_login()

    def switch_to_register(self):
        self.master.title("Register")
        self.login_frame.hide()
        self.register_frame.show()

    def switch_to_login(self):
        self.master.title("Login")
        self.main_frame.hide()
        self.main_frame.set_user_in_session("None")
        self.register_frame.hide()
        self.login_frame.show()

    def switch_to_main_app(self, username):
        self.master.title(f"App - {username}")
        self.login_frame.hide()
        self.register_frame.hide()
        self.main_frame.show()
        self.main_frame.set_user_in_session(username)


class TopBar:
    def __init__(self, master, user=None, logout_func=None):
        self.master = master

        self.top_bar = tk.Frame(self.master, bg="#3399ff", height=40)
        self.top_bar.pack(fill="x")

        if user is not None:
            self.user = user
            self.user_frame = tk.Frame(self.top_bar, bg="#3399ff")
            self.user_icon = ImageTk.PhotoImage(
                Image.open("app/assets/user-icon.png").resize((40, 40))
            )
            self.user_icon_label = tk.Label(
                self.user_frame, image=self.user_icon, bg="#3399ff"
            )
            self.user_icon_label.pack(padx=(10, 5), side="left")
            self.username_label = tk.Label(
                self.user_frame,
                text=self.user,
                bg="#3399ff",
                fg="white",
                font=("Helvetica", 14),
            )
            self.username_label.pack(padx=(5, 5), side="left")

            user_points = database.get_user_points(self.user)
            self.points_label = tk.Label(
                self.user_frame,
                text=f"(Points: {user_points})",
                bg="#3399ff",
                fg="white",
                font=("Helvetica", 10),
            )
            self.points_label.pack(side="left")
            self.user_frame.place(x=0, y=0)

            self.show_logout = False
            self.username_label.bind("<Button-1>", self.toggle_logout)
            self.user_icon_label.bind("<Button-1>", self.toggle_logout)
            self.user_frame.bind("<Button-1>", self.toggle_logout)
            self.points_label.bind("<Button-1>", self.toggle_logout)
            self.logout = tk.Button(
                text="Logout",
                command=lambda: self.update_user("None")
                or self.logout.place_forget()
                or logout_func(),
                bg="#3399ff",
                fg="white",
            )

        self.plane_icon = ImageTk.PhotoImage(
            Image.open("app/assets/airplane-icon.png").resize((40, 40))
        )
        self.plane_icon_label = tk.Label(
            self.top_bar, image=self.plane_icon, bg="#3399ff"
        )
        self.plane_icon_label.pack(padx=(450, 10), side="right")

    def toggle_logout(self, event):
        if not self.show_logout:
            self.logout.place(x=5, y=40)
            self.show_logout = True
        else:
            self.logout.place_forget()
            self.show_logout = False

    def update_user(self, user):
        self.user = user
        self.username_label.config(text=self.user)
        user_points = database.get_user_points(self.user)
        user_points = user_points[0] if user_points else 0
        self.points_label.config(text=f"(Points: {user_points})")


class LoginFrame(MyFrame):
    def __init__(self, master, switch_to_main_app, switch_to_register):
        super().__init__(master)
        self.master = master

        self.switch_to_main_app = switch_to_main_app
        self.switch_to_register = switch_to_register

        self.top_bar = TopBar(self.frame)
        self.top_bar.top_bar.pack(fill="x")

        self.username_label = tk.Label(self.frame, text="Username", bg=bg_color)
        self.username_label.pack(pady=(50, 5), padx=(100, 270), anchor="center")
        self.username_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.username_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.password_label = tk.Label(self.frame, text="Password", bg=bg_color)
        self.password_label.pack(pady=(10, 5), padx=(100, 270), anchor="center")
        self.password_entry = tk.Entry(self.frame, show="*", font=("Helvetica", 16))
        self.password_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.wrong_credentials_label = tk.Label(
            self.frame, text="", bg=bg_color, fg="red"
        )
        self.wrong_credentials_label.pack(pady=10, fill="x", anchor="center")

        button_frames = tk.Frame(self.frame, bg=bg_color)
        self.login_button = tk.Button(
            button_frames,
            text="Login",
            command=self.login,
            bg="#3399ff",
            fg="white",
            width=7,
        )
        self.login_button.pack(padx=(150, 0), side=tk.LEFT)

        self.register_button = tk.Button(
            button_frames,
            text="Register",
            command=self.switch_to_register,
            bg="#f2f2f2",
            width=7,
        )
        self.register_button.pack(padx=(0, 150), side=tk.RIGHT)
        button_frames.pack(pady=5, fill="x", anchor="center")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            self.wrong_credentials_label.config(
                text="Please enter all the required fields"
            )
            return
        authenticate = login_handling.authenticate(username, password)
        if not authenticate:
            self.wrong_credentials_label.config(text="Wrong username or password")
            return
        else:
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.switch_to_main_app(username)


class RegisterFrame(MyFrame):
    def __init__(self, master, switch_to_main_app, switch_to_login):
        super().__init__(master)
        self.master = master

        self.top_bar = TopBar(self.frame)
        self.top_bar.top_bar.pack(fill="x")

        self.switch_to_main_app = switch_to_main_app
        self.switch_to_login = switch_to_login

        self.username_label = tk.Label(self.frame, text="Username", bg=bg_color)
        self.username_label.pack(pady=(20, 5), padx=(100, 270), anchor="center")
        self.username_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.username_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.password_label = tk.Label(self.frame, text="Password", bg=bg_color)
        self.password_label.pack(pady=(7, 5), padx=(100, 270), anchor="center")
        self.password_entry = tk.Entry(self.frame, show="*", font=("Helvetica", 16))
        self.password_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.password_confirm_label = tk.Label(
            self.frame, text="Confirm Password", bg=bg_color
        )
        self.password_confirm_label.pack(pady=(7, 5), padx=(100, 220), anchor="center")
        self.password_confirm_entry = tk.Entry(
            self.frame, show="*", font=("Helvetica", 16)
        )
        self.password_confirm_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.name_label = tk.Label(self.frame, text="Name", bg=bg_color)
        self.name_label.pack(pady=(7, 5), padx=(100, 290), anchor="center")
        self.name_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.name_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.refered_label = tk.Label(
            self.frame, text="Referal Code (optional)", bg=bg_color
        )
        self.refered_label.pack(pady=(7, 5), padx=(100, 190), anchor="center")
        self.refered_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.refered_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.wrong_credentials_label = tk.Label(
            self.frame, text="", bg=bg_color, fg="red"
        )
        self.wrong_credentials_label.pack(pady=5, fill="x", anchor="center")

        button_frames = tk.Frame(self.frame, bg=bg_color)
        self.register_button = tk.Button(
            button_frames,
            text="Register",
            command=self.register_user,
            bg="#3399ff",
            fg="white",
            width=7,
        )
        self.register_button.pack(padx=(150, 0), side=tk.LEFT)

        self.back_button = tk.Button(
            button_frames,
            text="Go Back",
            command=self.switch_to_login,
            bg="#f2f2f2",
            width=7,
        )
        self.back_button.pack(padx=(0, 150), side=tk.RIGHT)
        button_frames.pack(pady=5, fill="x", anchor="center")

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        password_confirm = self.password_confirm_entry.get()
        name = self.name_entry.get()
        if not username or not password or not password_confirm or not name:
            self.wrong_credentials_label.config(
                text="Please fill all the required fields"
            )
            return
        if password != password_confirm:
            self.wrong_credentials_label.config(text="Passwords do not match")
            return
        hashed_password, salt, success = login_handling.new_user(username, password)
        if not success:
            self.wrong_credentials_label.config(text="Username already exists")
            return

        refered_by = self.refered_entry.get()
        refered_by = refered_by if refered_by else None
        if refered_by is not None:
            if not database.check_for_user(refered_by):
                self.wrong_credentials_label.config(
                    text="Referal not found. Try again."
                )
                return
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.password_confirm_entry.delete(0, "end")
        self.refered_entry.delete(0, "end")
        database.create_new_user(username, hashed_password, salt, name, refered_by)
        self.switch_to_main_app(username)


class MainFrame(MyFrame):
    def __init__(self, master, switch_to_login):
        super().__init__(master)
        self.master = master
        self.user = "None"

        self.top_bar = TopBar(self.frame, user="None", logout_func=switch_to_login)
        self.starting_frame = StartingFrame(self.frame, self.switch_to_book_flight)
        self.book_flight_frame = BookFlightFrame(self.frame, self.switch_to_starting)
        
        self.starting_frame.show()
        self.book_flight_frame.hide()

    def set_user_in_session(self, user):
        self.user = user
        self.top_bar.update_user(user)
    
    def switch_to_book_flight(self):
        self.starting_frame.hide()
        self.book_flight_frame.show()
    
    def switch_to_starting(self):
        self.book_flight_frame.hide()
        self.starting_frame.show()


class StartingFrame(MyFrame):
    def __init__(self, master, book_flight_func):
        super().__init__(master)
        self.master = master
        
        self.button = tk.Button(self.frame, text="Book a flight", command=book_flight_func)
        self.button.pack()
    


class BookFlightFrame(MyFrame):
    def __init__(self, master, go_back_func):
        super().__init__(master)
        self.master = master
        
        self.button = tk.Button(self.frame, text="Go back", command=go_back_func)
        self.button.pack()


def main():
    window = tk.Tk()
    app = App(window)
    window.mainloop()


if __name__ == "__main__":
    main()
