import sqlite3
from datetime import datetime

con = sqlite3.connect("app/databases/sample_database.db")
cur = con.cursor()


def create_indexes():
    cur.execute("CREATE INDEX IF NOT EXISTS idx_flight_code ON Flight (Flight_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ticket_code ON Ticket (Ticket_code)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_cancels_ticket_code ON Cancels (Ticket_code)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_purchases_ticket_code ON Purchases (Ticket_code)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_purchases_flight_code ON Purchases (Flight_code)"
    )

    con.commit()


def get_all_cities():
    return cur.execute("SELECT Name FROM City").fetchall()


def get_all_flights(depart_city, arrival_city, depart_day):
    departure_city_code = cur.execute(
        "SELECT City_code FROM City WHERE Name = ?", (depart_city,)
    ).fetchone()[0]
    arrival_city_code = cur.execute(
        "SELECT City_code FROM City WHERE Name = ?", (arrival_city,)
    ).fetchone()[0]

    return cur.execute(
        """
		select *
		from flight
		where Departure_airport_code in (select Airport_Code from Airport where City_code == ?)
		and Arrival_airport_code in (select Airport_Code from Airport where City_code == ?)
		and date(Scheduled_departure_datetime) == date(?)
	""",
        (departure_city_code, arrival_city_code, depart_day),
    ).fetchall()


def get_available_seats(flight_id):
    return cur.execute(
        """
        select * 
        from seat
        where Flight_code = ?
        and seat.number not in (
            select Seat_number from purchases 
            where Flight_code = seat.Flight_code
            and Ticket_code not in (select Ticket_code from Cancels)
        )
    """,
        (flight_id,),
    ).fetchall()


def cancel_flight(flight_id, username, date):
    ticket = cur.execute(
        "SELECT Ticket_code FROM Purchases WHERE Flight_code = ? AND Username = ?",
        (flight_id, username),
    ).fetchone()
    cancel_ticket(ticket[0], username, date)


def cancel_ticket(ticket_code, username, date):
    cur.execute("INSERT INTO Cancels VALUES (?, ?, ?)", (ticket_code, username, date))
    # subtract points
    # can be abused by buying a ticket, spending the points, and then cancelling the ticket
    cur.execute(
        "UPDATE User SET Points = Points - (SELECT Price/10 FROM Ticket WHERE Ticket_code = ?) WHERE username = ?",
        (ticket_code, username),
    )
    con.commit()


def buy_ticket(username, bank_details, seats, date):
    # seats = [(flight_id, seat_number), ...]
    # create ticket
    ticket_price = sum(
        cur.execute(
            "select price from seat where Flight_code = ? and number = ?", seat
        ).fetchone()[0]
        for seat in seats
    )
    ticket_code = hash(str(username) + str(bank_details) + str(seats) + str(date))
    ticket_code = [ticket_code] * len(seats)
    cur.execute(
        "INSERT INTO Ticket VALUES (?, ?, ?, ?)",
        (ticket_code[0], ticket_price, 0, bank_details),
    )

    # award points
    cur.execute(
        "UPDATE User SET Points = Points + ? WHERE username = ?",
        (ticket_price // 10, username),
    )

    # save purchase
    username = [username] * len(seats)
    date = [date] * len(seats)
    flights = [seat[0] for seat in seats]
    seat_numbers = [seat[1] for seat in seats]
    cur.executemany(
        "INSERT INTO Purchases VALUES (?, ?, ?, ?, ?)",
        zip(ticket_code, username, seat_numbers, flights, date),
    )
    con.commit()
    return ticket_price, ticket_price//10


def check_for_user(username):
    return (
        cur.execute("SELECT * FROM User WHERE Username = ?", (username,)).fetchone()
        is not None
    )


def get_last_flight(username):
    return cur.execute(
        """SELECT * FROM Flight WHERE Flight_code in (SELECT Flight_code 
        FROM Flight natural join Purchases
        WHERE Username = ?
        AND Ticket_code NOT IN (SELECT Ticket_code FROM Cancels WHERE Username = ?)
        AND Actual_arrival_datetime IS NOT NULL)
        ORDER BY Actual_arrival_datetime DESC LIMIT 1""",
        (username, username),
    ).fetchone()


def get_upcoming_flight(username):
    res = cur.execute(
        """SELECT * FROM Flight WHERE Flight_code in (SELECT Flight_code 
        FROM Flight natural join Purchases
        WHERE Username = ?
        AND Ticket_code NOT IN (SELECT Ticket_code FROM Cancels WHERE Username = ?)
        AND Actual_departure_datetime IS NULL)
        ORDER BY Actual_arrival_datetime DESC LIMIT 1""",
        (username, username),
    ).fetchall()
    if len(res) > 0:
        return res[0]
    else:
        return None


def check_for_city(name):
    return (
        cur.execute("SELECT * FROM City WHERE Name = ?", (name,)).fetchone() is not None
    )


def get_user_points(username):
    return cur.execute(
        "SELECT Points FROM User WHERE Username = ?", (username,)
    ).fetchone()


def create_new_user(username, password, salt, name, referred_by=None):
    cur.execute(
        "INSERT INTO User VALUES (?, ?, ?, ?, ?, ?)",
        (username, password, salt, 0, name, referred_by),
    )
    if referred_by is not None:
        cur.execute(
            "UPDATE User SET Points = Points + 10 WHERE Username = ?", (referred_by,)
        )
    con.commit()


def get_user_salt(username):
    return cur.execute(
        "SELECT Salt FROM User WHERE Username = ?", (username,)
    ).fetchone()[0]


def get_user_password(username):
    return cur.execute(
        "SELECT Password FROM User WHERE Username = ?", (username,)
    ).fetchone()[0]


def leave_review(username, flight_id, plane_rating, crew_rating, comment):
    cur.execute(
        "INSERT INTO Reviews VALUES (?, ?, ?, ?, ?)",
        (username, flight_id, plane_rating, crew_rating, comment),
    )
    airplane_id = cur.execute(
        "SELECT Airplane_code FROM Flight WHERE Flight_code = ?", (flight_id,)
    ).fetchone()[0]
    crew_on_flight = cur.execute(
        "SELECT AFM FROM Mans WHERE Flight_code = ?", (flight_id,)
    ).fetchall()

    # update airplane rating
    cur.execute(
        "UPDATE Airplane SET Review = (SELECT AVG(Airplane_score) FROM Reviews natural join Flight WHERE  Airplane_code= ?)",
        (airplane_id,),
    )
    # cur.executemany(
    #     "UPDATE Employee SET Review = (SELECT AVG(Employee_score) FROM Reviews WHERE AFM = ?)",
    #     crew_on_flight,
    # )
    con.commit()


def get_airplane_score(flight_id):
    airplane_id = cur.execute(
        "SELECT Airplane_code FROM Flight WHERE Flight_code = ?", (flight_id,)
    ).fetchone()[0]
    return cur.execute(
        "SELECT AVG(Airplane_score) FROM Reviews natural join Flight WHERE  Airplane_code= ?",
        (airplane_id,),).fetchone()[0]


def get_crew_score(flight_id):
    crew_ids = cur.execute(
        "SELECT AFM FROM Mans WHERE Flight_code = ?", (flight_id,)
    ).fetchall()
    out=0
    # print(crew_ids)
    crew_ids = [afm[0] for afm in crew_ids]
    for afm in crew_ids:
        employee_score = cur.execute(
        "SELECT AVG(Employee_score) FROM Reviews natural join Mans WHERE  AFM= ?",
        (afm,)).fetchone()[0]
        out+= int(employee_score if employee_score else 0)
    return out/len(crew_ids)


def get_seat_price(flight_id, seat_class):
    return cur.execute(
        "SELECT Price FROM Seat WHERE Flight_code = ? AND Class = ?",
        (flight_id, seat_class),
    ).fetchone()[0]


def get_available_seats_in_class(flight_id, seat_class):
    return cur.execute(
        """
        SELECT Number FROM Seat WHERE Flight_code = ? AND Class = ?
        AND Number NOT IN (SELECT Seat_number FROM Purchases WHERE Flight_code = ?)
        """,
        (flight_id, seat_class, flight_id),
    ).fetchall()


def create_flight(
    departure_airport_code,
    arrival_airport_code,
    scheduled_departure_datetime,
    scheduled_arrival_datetime,
    airplane_code,
):
    flight_code = abs(
        hash(
            f"{departure_airport_code}{arrival_airport_code}{scheduled_departure_datetime}{scheduled_arrival_datetime}{airplane_code}"
        )
    )
    cur.execute(
        "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            flight_code,
            1000,
            airplane_code,
            departure_airport_code,
            arrival_airport_code,
            scheduled_departure_datetime,
            None,
            scheduled_arrival_datetime,
            None,
        ),
    )

    seat_numbers = cur.execute(
        "SELECT First_class_seats, Business_class_seats, Economy_class_seats FROM Airplane WHERE Airplane_code = ?",
        (airplane_code,),
    ).fetchone()
    for seat_class, ind in zip(("First Class", "Business", "Economy"), (0, 1, 2)):
        for seat_number in range(1, seat_numbers[ind]):
            print(
                seat_class,
                f"{seat_class[0]}{seat_number:03}",
                50 * (3 - ind),
                flight_code,
            )
            cur.execute(
                "INSERT INTO Seat VALUES (?, ?, ?, ?)",
                (
                    seat_class,
                    f"{seat_class[0]}{seat_number:03}",
                    50 * (3 - ind),
                    flight_code,
                ),
            )

    con.commit()
    return


def get_airports_from_city(city):
    return cur.execute(
        "SELECT Airport_code FROM Airport WHERE City_code = (SELECT City_code FROM City WHERE Name = ?)",
        (city,),
    ).fetchall()


def get_airport(airport_code):
    return cur.execute(
        "SELECT * FROM Airport WHERE Airport_code = ?",
        (airport_code,),
    ).fetchone()


def get_available_airplanes(scheduled_departure_datetime, scheduled_arrival_datetime):
    return cur.execute(
        """SELECT * FROM Airplane WHERE Airplane_code NOT IN (SELECT Airplane_code FROM Flight WHERE
        (Scheduled_departure_datetime BETWEEN ? AND ?) OR 
        (Scheduled_arrival_datetime BETWEEN ? AND ?) OR 
        (Scheduled_departure_datetime < ? AND Scheduled_arrival_datetime > ?) OR 
        (Scheduled_departure_datetime > ? AND Scheduled_arrival_datetime < ?))""",
        (
            scheduled_departure_datetime,
            scheduled_arrival_datetime,
            scheduled_departure_datetime,
            scheduled_arrival_datetime,
            scheduled_departure_datetime,
            scheduled_arrival_datetime,
            scheduled_departure_datetime,
            scheduled_arrival_datetime,
        ),
    ).fetchall()


def get_user_info(username):
    return cur.execute(
        "SELECT Username, Points, Name, Referred_by FROM User WHERE Username = ?",
        (username,),
    ).fetchone()


def get_number_of_purchases(username):
    return cur.execute(
        "SELECT COUNT(*) FROM Purchases WHERE Username = ?", (username,)
    ).fetchone()[0]


def get_number_of_cancels(username):
    return cur.execute(
        "SELECT COUNT(*) FROM Cancels WHERE Username = ?", (username,)
    ).fetchone()[0]


def get_number_of_reviews(username):
    return cur.execute(
        "SELECT COUNT(*) FROM Reviews WHERE Username = ?", (username,)
    ).fetchone()[0]


def flight_arrival(flight_code, actual_arrival_datetime):
    cur.execute(
        "UPDATE Flight SET Actual_arrival_datetime = ? WHERE Flight_code = ?",
        (actual_arrival_datetime, flight_code),
    )
    con.commit()


def flight_departure(flight_code, actual_departure_datetime):
    cur.execute(
        "UPDATE Flight SET Actual_departure_datetime = ? WHERE Flight_code = ?",
        (actual_departure_datetime, flight_code),
    )
    con.commit()


def get_connecting_flights(departure_city, arrival_city, date):
    departure_city_code = cur.execute(
        "SELECT City_code FROM City WHERE Name = ?", (departure_city,)
    ).fetchone()[0]
    arrival_city_code = cur.execute(
        "SELECT City_code FROM City WHERE Name = ?", (arrival_city,)
    ).fetchone()[0]

    return cur.execute(
        """
        select flight1.Flight_code, flight2.Flight_code
        from Flight as flight1, Flight as flight2
        where flight1.Departure_airport_code in (select Airport_Code from Airport where City_code == ?)
        and flight2.Arrival_airport_code in (select Airport_Code from Airport where City_code == ?)
        and flight1.Arrival_airport_code = flight2.Departure_airport_code
        and date(flight1.Scheduled_departure_datetime) = date(?)
        and date(flight2.Scheduled_departure_datetime) = date(flight1.Scheduled_arrival_datetime)
        and julianday(flight2.Scheduled_departure_datetime) - julianday(flight1.Scheduled_arrival_datetime) < 1
        
    """,
        (departure_city_code, arrival_city_code, date),
    ).fetchall()


def get_flight(flight_code):
    return cur.execute(
        "SELECT * FROM Flight WHERE Flight_code = ?", (flight_code,)
    ).fetchone()


def get_city_from_airport(airport_code):
    return cur.execute(
        "SELECT Name FROM City WHERE City_code = (SELECT City_code FROM Airport WHERE Airport_code = ?)",
        (airport_code,),
    ).fetchone()[0]


def has_reviewed(username, flight_code):
    return (
        cur.execute(
            "SELECT * FROM Reviews WHERE Username = ? AND Flight_code = ?",
            (username, flight_code),
        ).fetchone()
        is not None
    )

create_indexes()

# print(flight_id := get_all_flights('New York', 'Miami', '2024-01-06')[0][0])
# print(seats := get_available_seats(flight_id))
# create_flight('A001', 'A002', '2024-01-06 10:00:00', '2024-01-06 18:00:00', 'AP001')

# con.close()