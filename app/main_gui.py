import tkinter as tk
from tkinter import ttk
import tkcalendar
from PIL import ImageTk, Image
import datetime

import login_handling
import database

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
            self.frame, self.switch_to_book_flight, user
        )
        self.book_flight_frame = BookFlightFrame(
            self.frame, self.switch_to_starting, user
        )

        self.book_flight_frame.hide()

    def switch_to_book_flight(self):
        self.starting_frame.hide()
        self.book_flight_frame.show()

    def switch_to_starting(self):
        self.book_flight_frame.hide()
        self.book_flight_frame.clear_data()
        self.starting_frame.clear()
        self.starting_frame.show()
        self.starting_frame.show_context()

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
    def __init__(self, master, book_flight_func, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.book_flight_func = book_flight_func
        self.show_context()

    def show_context(self):
        self.upcoming_flights_frame = ColoredFrame(
            self.frame,
            LIGHT_COLOR,
            bg=ACCENT_COLOR,
            border=2,
            borderwidth=3,
        )
        self.upcoming_flights_frame.pack(pady=(50, 5), padx=25, fill="x")
        sub_frame1 = tk.Frame(self.upcoming_flights_frame, bg=LIGHT_COLOR)
        sub_frame1.pack(fill="x")

        tk.Label(
            sub_frame1,
            text="Upcoming Flight:",
            bg=LIGHT_COLOR,
            font=("Helvetica", 16),
        ).pack(pady=(5, 5), padx=(10, 50), side="left")

        self.next_flight = database.get_upcoming_flight(self.user)
        if self.next_flight:
            FlightFrame(sub_frame1, self.next_flight).pack(
                pady=5, padx=10, side="right"
            )
            tk.Button(
                self.upcoming_flights_frame,
                text="Cancel it",
                command=self.cancel_flight_func,
                bg=DARK_COLOR,
                fg="white",
            ).pack(pady=(5, 5), padx=30, side="right")
        else:
            tk.Label(
                sub_frame1,
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
        sub_frame2 = tk.Frame(self.past_flights_frame, bg=LIGHT_COLOR)
        sub_frame2.pack(fill="x")
        tk.Label(
            sub_frame2,
            text="Past Flights:",
            bg=LIGHT_COLOR,
            font=("Helvetica", 16),
        ).pack(pady=(5, 5), padx=(10, 50), side="left")
        self.prev_flight = database.get_last_flight(self.user)
        if self.prev_flight:
            FlightFrame(sub_frame2, self.prev_flight).pack(
                pady=5, padx=10, side="right"
            )
            tk.Button(
                self.past_flights_frame,
                text="Leave a review",
                command=self.review_flight_func,
                bg=DARK_COLOR,
                fg="white",
            ).pack(pady=(5, 5), padx=30, side="right")
        else:
            tk.Label(
                sub_frame2,
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

    def clear(self):
        self.frame.destroy()
        self.frame = tk.Frame(self.master, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
        self.frame.pack(fill="both", expand=True)

    def update_user(self, user):
        self.user = user

    def cancel_flight_func(self):
        flight = self.next_flight
        popup = tk.Toplevel(self.master)
        popup.title("Cancel Flight")
        popup.config(bg=BG_COLOR)
        tk.Label(
            popup, text="Are you sure you want\nto cancel this flight?", bg=BG_COLOR
        ).pack(padx=10, pady=10)

        tk.Button(
            popup,
            text="Yes",
            command=lambda: self.cancel_flight(flight) or popup.destroy(),
        ).pack(padx=10, pady=10, side="left")
        tk.Button(popup, text="No", command=popup.destroy).pack(
            padx=10, pady=10, side="right"
        )

    def cancel_flight(self, flight):
        database.cancel_flight(flight[0], self.user, datetime.datetime.now())
        self.clear()
        self.show_context()

    def review_flight_func(self):
        flight = self.prev_flight
        if database.has_reviewed(self.user, self.prev_flight[0]):
            popup = tk.Toplevel(self.master)
            popup.title("Review")
            popup.config(bg=BG_COLOR)
            tk.Label(
                popup, text="You have already\nreviewed this flight", bg=BG_COLOR
            ).pack(padx=10, pady=10)
            tk.Button(popup, text="Ok", command=popup.destroy).pack(padx=10, pady=10)
        else:
            popup = tk.Toplevel(self.master)
            popup.title("Leave a review")
            popup.config(bg=BG_COLOR)
            airplane_score_frame = tk.Frame(popup, bg=BG_COLOR)
            airplane_score_frame.pack(padx=10, pady=10, fill="x")
            tk.Label(airplane_score_frame, text="Airplane Rating:", bg=BG_COLOR).pack(
                side="left"
            )
            airplane_stars = [
                tk.Label(airplane_score_frame, text="☆", bg=BG_COLOR, fg="black")
                for _ in range(5)
            ]
            tk.Button(
                airplane_score_frame,
                text="+",
                command=lambda: self.increase_stars(airplane_stars),
            ).pack(side="right")
            tk.Button(
                airplane_score_frame,
                text="-",
                command=lambda: self.decrease_stars(airplane_stars),
            ).pack(side="right")
            for star in reversed(airplane_stars):
                star.pack(side="right")

            crew_score_frame = tk.Frame(popup, bg=BG_COLOR)
            crew_score_frame.pack(padx=10, pady=10, fill="x")
            tk.Label(crew_score_frame, text="Crew Rating:", bg=BG_COLOR).pack(
                side="left"
            )
            crew_stars = [
                tk.Label(crew_score_frame, text="☆", bg=BG_COLOR, fg="black")
                for _ in range(5)
            ]
            tk.Button(
                crew_score_frame,
                text="+",
                command=lambda: self.increase_stars(crew_stars),
            ).pack(side="right")
            tk.Button(
                crew_score_frame,
                text="-",
                command=lambda: self.decrease_stars(crew_stars),
            ).pack(side="right")
            for star in reversed(crew_stars):
                star.pack(side="right")

            comment_frame = tk.Frame(popup, bg=BG_COLOR)
            comment_frame.pack(padx=10, pady=10, fill="x")
            tk.Label(comment_frame, text="Leave a comment:", bg=BG_COLOR).pack()
            comment_entry = tk.Entry(comment_frame, bg=BG_COLOR, width=20)
            comment_entry.pack(padx=10, pady=10, fill="x")

            tk.Button(
                popup,
                text="Submit",
                command=lambda: self.submit_review(
                    airplane_stars, crew_stars, comment_entry, popup, flight
                ),
                bg=DARK_COLOR,
            ).pack(padx=10, pady=10)

    def submit_review(self, airplane_stars, crew_stars, comment_entry, popup, flight):
        airplane_score = sum(star["text"] == "★" for star in airplane_stars)
        crew_score = sum(star["text"] == "★" for star in crew_stars)
        comment = comment_entry.get()
        if not comment:
            comment = None
        database.leave_review(self.user, flight[0], airplane_score, crew_score, comment)
        popup.destroy()

    def increase_stars(self, stars):
        for star in stars:
            if star["text"] == "☆":
                star.config(text="★", fg="yellow")
                break

    def decrease_stars(self, stars):
        for star in reversed(stars):
            if star["text"] == "★":
                star.config(text="☆", fg="black")
                break


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

        self.show_flights_frame = ShowFlightsFrame(self.frame, self.switch_to_purchase)
        self.show_flights_frame.hide()
        self.purchase_frame = PurcaseFrame(
            self.master, self.switch_to_book_flight, user, go_back_func
        )
        self.purchase_frame.hide()

        tk.Button(self.frame, text="Go back", command=go_back_func).pack(
            padx=5, pady=5, side="top", anchor="nw"
        )

        self.flight_data_frame = ColoredFrame(
            self.frame, LIGHT_COLOR, border=2, bg="black"
        )
        self.flight_data_frame.pack(pady=(10, 5), padx=5)

        self.date = None
        self.date_frame = ColoredFrame(
            self.flight_data_frame, BG_COLOR, bg=ACCENT_COLOR, border=2
        )
        self.date_frame.pack(pady=10, padx=10, side="left", fill="y")
        self.selected_date = tk.Label(
            self.date_frame, text="Select a date", bg=BG_COLOR
        )
        self.selected_date.pack(padx=5, side="left")

        self.calendar = Calendar(self.master, self.update_date)
        self.date_frame.bind("<Button-1>", self.show_calendar)
        self.selected_date.bind("<Button-1>", self.show_calendar)

        self.departure_city_frame = ColoredFrame(
            self.flight_data_frame, BG_COLOR, bg=ACCENT_COLOR, border=2
        )
        self.departure_city_frame.pack(pady=10, padx=10, side="left", fill="y")
        self.departure_city_entry = tk.Entry(
            self.departure_city_frame, bg=BG_COLOR, width=10, justify="center"
        )
        self.departure_city_entry.insert(0, "Departure")
        self.departure_city_entry.pack(pady=0, side="left")
        self.departure_city_entry.bind("<Button-1>", self.show_departure_cities)
        self.departure_city_search = CitiesSearch(self.frame, self.departure_city_entry)
        self.departure_city_search.listbox.bind(
            "<Double-Button-1>", self.update_departure_city
        )

        tk.Label(self.flight_data_frame, text="→", bg=LIGHT_COLOR).pack(
            pady=10, padx=2, side="left"
        )

        self.arrival_city_frame = ColoredFrame(
            self.flight_data_frame, BG_COLOR, bg=ACCENT_COLOR, border=2
        )
        self.arrival_city_frame.pack(pady=10, padx=10, side="left", fill="y")
        self.arrival_city_entry = tk.Entry(
            self.arrival_city_frame, bg=BG_COLOR, width=10, justify="center"
        )
        self.arrival_city_entry.insert(0, "Arrival")
        self.arrival_city_entry.pack(pady=0, side="left")
        self.arrival_city_entry.bind("<Button-1>", self.show_arrival_cities)
        self.arrival_city_search = CitiesSearch(self.frame, self.arrival_city_entry)
        self.arrival_city_search.listbox.bind(
            "<Double-Button-1>", self.update_arrival_city
        )

        self.seats_frame = tk.Frame(self.flight_data_frame, bg=LIGHT_COLOR)
        self.seats_frame.pack(pady=10, padx=5, fill="x")
        self.seats = 1
        tk.Button(
            self.seats_frame, text="-", command=self.decrease_seats, bg=BG_COLOR
        ).pack(padx=1, side="left")
        self.seats_label = tk.Label(
            self.seats_frame, text=f"{self.seats}", bg=LIGHT_COLOR
        )
        self.seats_label.pack(padx=1, side="left")
        tk.Button(
            self.seats_frame, text="+", command=self.increase_seats, bg=BG_COLOR
        ).pack(padx=1, side="left")

        tk.Button(
            self.frame,
            text="Search",
            command=self.search_flights,
            bg=DARK_COLOR,
            fg="white",
            font=("Helvetica", 16),
        ).pack(padx=1, pady=10, side="top", anchor="center")

    def search_flights(self):
        date = self.date
        departure_city = self.departure_city_entry.get()
        arrival_city = self.arrival_city_entry.get()
        if (
            not date
            or not departure_city
            or not arrival_city
            or departure_city == "Departure"
            or arrival_city == "Arrival"
        ):
            return
        all_flights = database.get_all_flights(departure_city, arrival_city, date)
        self.show_flights_frame.clear_data()
        self.show_flights_frame.show()
        self.show_flights_frame.show_flights(all_flights)

    def switch_to_purchase(self, flight):
        self.show_flights_frame.hide()
        self.hide()
        self.purchase_frame.show()
        self.purchase_frame.show_flight(flight, self.seats)
        return

    def switch_to_book_flight(self):
        self.purchase_frame.hide()
        self.purchase_frame.clear_data()
        self.show()
        return

    def increase_seats(self):
        self.seats += 1
        self.seats_label.config(text=f"{self.seats}")

    def decrease_seats(self):
        self.seats -= 1
        if self.seats < 1:
            self.seats = 1
        self.seats_label.config(text=f"{self.seats}")

    def show_arrival_cities(self, _event):
        self.arrival_city_search.listbox.place(x=260, y=85)
        self.arrival_city_search.listbox.lift()

    def update_arrival_city(self, _event):
        self.arrival_city_search.listbox.place_forget()
        self.arrival_city_entry.delete(0, "end")
        self.arrival_city_entry.insert(
            0,
            self.arrival_city_search.listbox.get(
                self.arrival_city_search.listbox.curselection()
            ),
        )

    def show_departure_cities(self, _event):
        self.departure_city_search.listbox.place(x=130, y=85)
        self.departure_city_search.listbox.lift()

    def update_departure_city(self, _event):
        self.departure_city_search.listbox.place_forget()
        self.departure_city_entry.delete(0, "end")
        self.departure_city_entry.insert(
            0,
            self.departure_city_search.listbox.get(
                self.departure_city_search.listbox.curselection()
            ),
        )

    def show_calendar(self, _event):
        self.calendar.calendar_frame.place(x=10, y=10)
        self.calendar.calendar_frame.lift()

    def clear_data(self):
        self.date = None
        self.selected_date.config(text="Select a date")
        self.arrival_city_entry.delete(0, "end")
        self.arrival_city_entry.insert(0, "Arrival")
        self.departure_city_entry.delete(0, "end")
        self.departure_city_entry.insert(0, "Departure")
        self.show_flights_frame.clear_data()

    def update_date(self):
        self.calendar.calendar_frame.place_forget()
        self.date = self.calendar.calendar.selection_get()
        self.selected_date.config(text=self.date)


class ShowFlightsFrame(MyFrame):
    def __init__(self, master, switch_to_purchase):
        super().__init__(master)
        self.master = master
        self.switch_to_purchase = switch_to_purchase
        self.clear_data()

    def clear_data(self):
        self.flights = []
        self.flight_frames = []
        self.frame.destroy()
        self.frame = tk.Frame(self.master, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
        self.frame.pack(fill="both", expand=True)

    def show_flights(self, flights):
        if not flights:
            tk.Label(self.frame, text="No flights found", bg=BG_COLOR).pack(pady=10)
            return
        self.flights = flights
        self.flight_frames = []
        for flight in self.flights:
            frame = ColoredFrame(self.frame, LIGHT_COLOR, border=2, bg="black")
            frame.pack(pady=(10, 5), padx=5, fill="x")
            self.flight_frames.append(
                AdvancedlightFrame(frame, flight, self.switch_to_purchase)
            )
            self.flight_frames[-1].pack(pady=10, padx=10, fill="x")
            self.flight_frames[-1].bind(
                "<Button-1>",
                lambda event, flight=flight: self.switch_to_purchase(flight),
            )


class PurcaseFrame(MyFrame):
    def __init__(self, master, switch_to_book_flight, user, go_back_func):
        super().__init__(master)
        self.master = master
        self.user = user
        self.switch_to_book_flight = switch_to_book_flight
        tk.Button(self.frame, text="Go back", command=switch_to_book_flight).pack()
        self.go_back_func = go_back_func

    def clear_data(self):
        self.flight = None
        self.flight_frame = None
        self.frame.destroy()
        self.frame = tk.Frame(self.master, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
        self.frame.pack(fill="both", expand=True)
        tk.Button(self.frame, text="Go back", command=self.switch_to_book_flight).pack()
        self.hide()

    def show_flight(self, flight, seats):
        self.flight = flight
        frame = ColoredFrame(self.frame, LIGHT_COLOR, border=2, bg="black")
        self.flight_frame = FlightFrame(frame, flight)
        self.flight_frame.pack(pady=10, padx=10, fill="x")
        frame.pack(pady=(10, 5), padx=5, side="top", anchor="w")

        seats_frame = tk.Frame(self.frame, bg=BG_COLOR)
        seats_frame.pack(pady=10, padx=5, fill="x")
        self.seats = []
        for i in range(seats):
            self.seats.append(SelectSeatFrame(seats_frame, flight[0], i))
            self.seats[-1].frame.pack(pady=10, padx=10, fill="x")

        self.bank_details = tk.Entry(
            self.frame, bg=BG_COLOR, width=20, justify="center"
        )
        self.bank_details.pack(pady=10, padx=10, fill="x")
        self.bank_details.insert(0, "Bank Details:")

        tk.Button(
            self.frame,
            text="Purchase",
            command=self.purchase,
            bg=DARK_COLOR,
            font=("Helvetica", 18),
        ).pack(padx=10, pady=10, side="bottom", anchor="center")

    def purchase(self):
        if not self.bank_details.get():
            return
        seats = [
            (self.flight[0], self.seats[i].seat_no.get())
            for i in range(len(self.seats))
        ]
        username = self.user
        bank_details = self.bank_details.get()
        date = datetime.datetime.now()
        database.buy_ticket(username, bank_details, seats, date)
        self.hide()
        self.clear_data()
        self.go_back_func()


class SelectSeatFrame(MyFrame):
    def __init__(self, master, flight_id, i):
        super().__init__(master)
        self.flight_id = flight_id

        tk.Label(
            self.frame, text=f"Seat {i+1}:", bg=BG_COLOR, font=("Helvetica", 16)
        ).pack(padx=15, side="left")
        tk.Label(self.frame, text="Class", bg=BG_COLOR).pack(side="left")
        self.seat_class = tk.StringVar()
        self.seat_class.set("Economy")
        self.seat_class.trace_add("write", self.update_price)

        seat_class_menu = tk.OptionMenu(
            self.frame, self.seat_class, "Economy", "Business", "First"
        )
        seat_class_menu.pack(side="left", padx=5)

        self.seat_price_label = tk.Label(
            self.frame,
            text=f'{database.get_seat_price(self.flight_id, f"{self.seat_class.get()}_Class")}€',
            bg=BG_COLOR,
        )
        self.seat_price_label.pack(side="right", padx=5)

        tk.Label(self.frame, text="Seat No.", bg=BG_COLOR).pack(side="left")
        self.seat_no = tk.StringVar()
        availabel_seats = database.get_available_seats_in_class(
            self.flight_id, f"{self.seat_class.get()}_Class"
        )
        self.seat_no_menu = ttk.Combobox(
            self.frame,
            textvariable=self.seat_no,
            values=availabel_seats,
            state="readonly",
        )
        self.seat_no_menu.pack(side="left", padx=5)

    def update_price(self, *args):
        self.price = database.get_seat_price(
            self.flight_id, f"{self.seat_class.get()}_Class"
        )
        self.seat_price_label.config(text=f"{self.price}€")
        availabel_seats = database.get_available_seats_in_class(
            self.flight_id, f"{self.seat_class.get()}_Class"
        )
        self.seat_no_menu.config(values=availabel_seats)

        self.seat_no.set("")


class AdvancedlightFrame(tk.Frame):
    def __init__(self, master, flight_info, command, color=LIGHT_COLOR):
        super().__init__(master)
        self.master = master
        self.config(bg=color)

        depart_airport = flight_info[3]
        arrival_airport = flight_info[4]
        date = flight_info[5].split(" ")[0]
        depart_time = flight_info[5].split(" ")[1].split(".")[0][:-3]
        arrival_time = flight_info[7].split(" ")[1].split(".")[0][:-3]

        date_label = tk.Label(self, text=date, bg=color, font=("Helvetica, 14"))
        date_label.pack(anchor="w")
        dep_time_label = tk.Label(self, text=depart_time, bg=color)
        flight_label = tk.Label(
            self,
            text=f"↑ {depart_airport} -> {arrival_airport} ↓",
            bg=color,
            font=("Helvetica", 16),
        )
        arr_time = tk.Label(self, text=arrival_time, bg=color)
        arr_time.pack(side="right", padx=(0, 10))
        flight_label.pack(padx=10, side="right")
        dep_time_label.pack(side="right")
        date_label.bind("<Button-1>", lambda _: command(flight_info))
        dep_time_label.bind("<Button-1>", lambda _: command(flight_info))
        flight_label.bind("<Button-1>", lambda _: command(flight_info))
        arr_time.bind("<Button-1>", lambda _: command(flight_info))


class Calendar:
    def __init__(self, master, update_date):
        self.master = master
        self.calendar_frame = ColoredFrame(self.master, BG_COLOR, border=2, bg="black")
        self.calendar = tkcalendar.Calendar(self.calendar_frame, selectmode="day")
        self.calendar.pack(fill="both", expand=True)
        tk.Button(self.calendar_frame, text="Select", command=update_date).pack()


class CitiesSearch:
    def __init__(self, master, search_box):
        self.master = master
        self.search_box = search_box
        self.search_box.bind("<KeyRelease>", self.update_listbox)

        self.all_cities = [city[0] for city in database.get_all_cities()]

        self.listbox = tk.Listbox(master, width=10, height=10)
        for item in self.all_cities:
            self.listbox.insert("end", item)

    def update_listbox(self, *args):
        val = self.search_box.get()
        if val == "":
            data = self.all_cities
        else:
            data = []
            for city in self.all_cities:
                if val.lower() in city.lower():
                    data.append(city)
        self.listbox.delete(0, "end")
        for item in data:
            self.listbox.insert("end", item)


def main():
    window = tk.Tk()
    app = App(window)
    window.mainloop()


if __name__ == "__main__":
    main()
