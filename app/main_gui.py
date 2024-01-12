import tkinter as tk
from PIL import ImageTk, Image

import login_handling
import database
import user
import datetime

WIDTH = 500
HEIGHT = 500
BG_COLOR = "#e6e6e6"
MAIN_COLOR = "#3399ff"
LIGHT_COLOR = "#a8dadc"
DARK_COLOR = "#1d3557"
ACCENT_COLOR = "#e63946"


class MyFrame:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(master, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
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
        self.master.config(bg=BG_COLOR)

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
        self.main_frame.clear()
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
        self.logout_func = logout_func

        self.top_bar = tk.Frame(self.master, bg=MAIN_COLOR, height=40)
        self.top_bar.pack(fill="x")

        if user is not None:
            self.user = user
            self.user_frame = tk.Frame(self.top_bar, bg=MAIN_COLOR)
            self.user_icon = ImageTk.PhotoImage(
                Image.open("app/assets/user-icon.png").resize((40, 40))
            )
            self.user_icon_label = tk.Label(
                self.user_frame, image=self.user_icon, bg=MAIN_COLOR
            )
            self.user_icon_label.pack(padx=(10, 5), side="left")
            self.username_label = tk.Label(
                self.user_frame,
                text=self.user,
                bg=MAIN_COLOR,
                fg="white",
                font=("Helvetica", 14),
            )
            self.username_label.pack(padx=(5, 5), side="left")

            user_points = database.get_user_points(self.user)
            self.points_label = tk.Label(
                self.user_frame,
                text=f"(Points: {user_points})",
                bg=MAIN_COLOR,
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
            self.logout_button = tk.Button(
                text="Logout",
                command=self.logout,
                bg=MAIN_COLOR,
                fg="white",
            )

        self.plane_icon = ImageTk.PhotoImage(
            Image.open("app/assets/airplane-icon.png").resize((40, 40))
        )
        self.plane_icon_label = tk.Label(
            self.top_bar, image=self.plane_icon, bg=MAIN_COLOR
        )
        self.plane_icon_label.pack(padx=(450, 10), side="right")

    def toggle_logout(self, event):
        if not self.show_logout:
            self.logout_button.place(x=5, y=45)
            self.show_logout = True
        else:
            self.logout_button.place_forget()
            self.show_logout = False

    def logout(self):
        self.update_user("None")
        self.logout_button.place_forget()
        self.logout_func()

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

        tk.Label(self.frame, text="Username", bg=BG_COLOR).pack(
            pady=(50, 5), padx=(100, 270), anchor="center"
        )
        self.username_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.username_entry.pack(pady=2, padx=(100, 100), anchor="center")

        tk.Label(self.frame, text="Password", bg=BG_COLOR).pack(
            pady=(10, 5), padx=(100, 270), anchor="center"
        )
        self.password_entry = tk.Entry(self.frame, show="*", font=("Helvetica", 16))
        self.password_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.wrong_credentials_label = tk.Label(
            self.frame, text="", bg=BG_COLOR, fg="red"
        )
        self.wrong_credentials_label.pack(pady=10, fill="x", anchor="center")

        button_frames = tk.Frame(self.frame, bg=BG_COLOR)
        tk.Button(
            button_frames,
            text="Login",
            command=self.login,
            bg=MAIN_COLOR,
            fg="white",
            width=7,
        ).pack(padx=(150, 0), side=tk.LEFT)

        tk.Button(
            button_frames,
            text="Register",
            command=self.switch_to_register,
            bg="white",
            width=7,
        ).pack(padx=(0, 150), side=tk.RIGHT)
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

        self.switch_to_main_app = switch_to_main_app
        self.switch_to_login = switch_to_login

        tk.Label(self.frame, text="Username", bg=BG_COLOR).pack(
            pady=(20, 5), padx=(100, 270), anchor="center"
        )
        self.username_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.username_entry.pack(pady=2, padx=(100, 100), anchor="center")

        tk.Label(self.frame, text="Password", bg=BG_COLOR).pack(
            pady=(7, 5), padx=(100, 270), anchor="center"
        )
        self.password_entry = tk.Entry(self.frame, show="*", font=("Helvetica", 16))
        self.password_entry.pack(pady=2, padx=(100, 100), anchor="center")

        tk.Label(self.frame, text="Confirm Password", bg=BG_COLOR).pack(
            pady=(7, 5), padx=(100, 220), anchor="center"
        )
        self.password_confirm_entry = tk.Entry(
            self.frame, show="*", font=("Helvetica", 16)
        )
        self.password_confirm_entry.pack(pady=2, padx=(100, 100), anchor="center")

        tk.Label(self.frame, text="Name", bg=BG_COLOR).pack(
            pady=(7, 5), padx=(100, 290), anchor="center"
        )
        self.name_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.name_entry.pack(pady=2, padx=(100, 100), anchor="center")

        tk.Label(self.frame, text="Referal Code (optional)", bg=BG_COLOR).pack(
            pady=(7, 5), padx=(100, 190), anchor="center"
        )
        self.refered_entry = tk.Entry(self.frame, font=("Helvetica", 16))
        self.refered_entry.pack(pady=2, padx=(100, 100), anchor="center")

        self.wrong_credentials_label = tk.Label(
            self.frame, text="", bg=BG_COLOR, fg="red"
        )
        self.wrong_credentials_label.pack(pady=5, fill="x", anchor="center")

        button_frames = tk.Frame(self.frame, bg=BG_COLOR)
        tk.Button(
            button_frames,
            text="Register",
            command=self.register_user,
            bg=MAIN_COLOR,
            fg="white",
            width=7,
        ).pack(padx=(150, 0), side=tk.LEFT)

        tk.Button(
            button_frames,
            text="Go Back",
            command=self.switch_to_login,
            bg="white",
            width=7,
        ).pack(padx=(0, 150), side=tk.RIGHT)
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

        self.starting_frame = MyFrame(self.frame)
        self.book_flight_frame = MyFrame(self.frame)

        self.top_bar = TopBar(self.frame, user="None", logout_func=switch_to_login)

    def set_user_in_session(self, user):
        self.user = user
        self.top_bar.update_user(user)
        self.starting_frame = StartingFrame(
            self.frame, self.switch_to_book_flight, self.switch_to_review_flight, user
        )
        self.book_flight_frame = BookFlightFrame(
            self.frame, self.switch_to_starting, user
        )
        self.review_flight_frame = ReviewFlightFrame(
            self.frame, self.switch_to_starting, user
        )

        self.book_flight_frame.hide()
        self.review_flight_frame.hide()

    def switch_to_book_flight(self):
        self.starting_frame.hide()
        self.book_flight_frame.show()

    def switch_to_starting(self):
        self.book_flight_frame.hide()
        self.review_flight_frame.hide()
        self.starting_frame.show()

    def switch_to_review_flight(self):
        self.starting_frame.hide()
        self.review_flight_frame.show()

    def clear(self):
        self.starting_frame.hide()
        self.book_flight_frame.hide()


class ColoredFrame(tk.Frame):
    def __init__(self, master=None, background_color=BG_COLOR, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        # Create a Label widget around the Frame for the border effect
        self.border_label = tk.Label(self, background=background_color)
        self.border_label.place(relwidth=1, relheight=1)


class StartingFrame(MyFrame):
    def __init__(self, master, book_flight_func, review_flight_func, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.book_flight_func = book_flight_func

        self.upcoming_flights_frame = ColoredFrame(
            self.frame,
            LIGHT_COLOR,
            bg=ACCENT_COLOR,
            border=2,
            borderwidth=3,
        )
        self.upcoming_flights_frame.pack(pady=(50, 5), padx=25, fill="x")

        tk.Label(
            self.upcoming_flights_frame,
            text="Upcoming Flight:",
            bg=LIGHT_COLOR,
            font=("Helvetica", 16),
        ).pack(pady=(5, 5), padx=(10, 50), side="left")

        flight = database.get_upcoming_flight(self.user)
        if flight:
            FlightFrame(self.upcoming_flights_frame, flight).pack(
                pady=5, padx=10, side="right"
            )
        else:
            tk.Label(
                self.upcoming_flights_frame,
                text="You have no\nupcoming flights",
                bg=LIGHT_COLOR,
                font=("Helvetica", 16),
            ).pack(pady=(5, 5), padx=(10, 50), side="right")

        self.past_flights_frame = ColoredFrame(
            self.frame,
            LIGHT_COLOR,
            bg=ACCENT_COLOR,
            border=2,
            borderwidth=3,
            width=WIDTH - 50,
        )
        self.past_flights_frame.pack(pady=(20, 5), padx=25, fill="x")
        sub_frame1 = tk.Frame(self.past_flights_frame, bg=LIGHT_COLOR)
        sub_frame1.pack(fill="x")
        tk.Label(
            sub_frame1,
            text="Past Flights:",
            bg=LIGHT_COLOR,
            font=("Helvetica", 16),
        ).pack(pady=(5, 5), padx=(10, 50), side="left")
        flight = database.get_last_flight(self.user)
        if flight:
            FlightFrame(sub_frame1, flight).pack(pady=5, padx=10, side="right")
            tk.Button(
                self.past_flights_frame,
                text="Leave a review",
                command=review_flight_func,
                bg=DARK_COLOR,
                fg="white",
            ).pack(pady=(5, 5), padx=30, side="right")
        else:
            tk.Label(
                sub_frame1,
                text="You have\nno past flights",
                bg=LIGHT_COLOR,
                font=("Helvetica", 16),
            ).pack(pady=(5, 5), padx=(10, 60), side="right")

        tk.Button(
            self.frame,
            text="Book a flight",
            command=self.book_flight_func,
            bg=DARK_COLOR,
            fg="white",
            width=20,
            height=3,
            font=("Helvetica", 24),
        ).pack(pady=(25, 10), side="top")

    def update_user(self, user):
        self.user = user


class FlightFrame(tk.Frame):
    def __init__(self, master, flight_info, color=LIGHT_COLOR):
        super().__init__(master)
        self.master = master
        self.config(bg=color)

        depart_airport = flight_info[3]
        arrival_airport = flight_info[4]
        date = flight_info[5].split(" ")[0]
        depart_time = flight_info[5].split(" ")[1].split(".")[0][:-3]
        arrival_time = flight_info[7].split(" ")[1].split(".")[0][:-3]

        tk.Label(self, text=date, bg=color, font=("Helvetica, 14")).pack(anchor="w")
        tk.Label(
            self,
            text=f"↑ {depart_airport} -> {arrival_airport} ↓",
            bg=color,
            font=("Helvetica", 16),
        ).pack(padx=(50, 0))
        tk.Label(self, text=depart_time, bg=color).pack(side="left", padx=(60, 0))
        tk.Label(self, text=arrival_time, bg=color).pack(side="right", padx=(0, 10))


class BookFlightFrame(MyFrame):
    def __init__(self, master, go_back_func, user):
        super().__init__(master)
        self.master = master
        self.user = user

        self.button = tk.Button(self.frame, text="Go back", command=go_back_func)
        self.button.pack()


class ReviewFlightFrame(MyFrame):
    def __init__(self, master, go_back_func, user):
        super().__init__(master)
        self.master = master
        self.user = user

        self.button = tk.Button(self.frame, text="Go back", command=go_back_func)
        self.button.pack()


def main():
    window = tk.Tk()
    app = App(window)
    window.mainloop()


if __name__ == "__main__":
    main()
