from random_airports import international_airports, airlines
import sqlite3
from faker import Faker
from faker.providers import DynamicProvider
import bcrypt
from datetime import datetime, timedelta
import numpy as np

international_airports = list(international_airports)[:10]
NUMBER_OF_PLANES = 10
DAYS = 20
NUMBER_OF_FLIGHTS = 2000

FIRST_CLASS_SEATS = 2
BUSINESS_CLASS_SEATS = 8
ECONOMY_CLASS_SEATS = 20

NUMBER_OF_EMPLOYEES = 200
NUMBER_OF_USERS = 200

flight_codes_to_seats = {}

print("Starting...")
fake = Faker()

# 90 airports from around the world (44 cities)

all_cities = {airport[2] for airport in international_airports}


con = sqlite3.connect("app/databases/sample_database.db")
cur = con.cursor()


def database_is_empty():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return not cur.fetchall()


def create_database():
    for table in open("app/schema.sql").read().split(";"):
        cur.execute(table)
        con.commit()


def create_cities():
    # City table -> city_id, city_name
    cur.executemany(
        "INSERT INTO City VALUES (?, ?);", [(hash(city), city) for city in all_cities]
    )
    con.commit()


def create_airports():
    # Airport table -> airport_id, airport_name, city_id
    cur.executemany(
        "INSERT INTO Airport VALUES (?, ?, ?);",
        [
            (airport[0], airport[1], hash(airport[2]))
            for airport in international_airports
        ],
    )
    con.commit()


def create_planes():
    fake.add_provider(DynamicProvider(provider_name="airlines", elements=airlines))
    cur.executemany(
        "INSERT INTO Airplane VALUES (?, ?, ?, ?, ?, ?);",
        [
            (
                i,
                fake.airlines(),
                0,
                FIRST_CLASS_SEATS,
                BUSINESS_CLASS_SEATS,
                ECONOMY_CLASS_SEATS,
            )
            for i in range(NUMBER_OF_PLANES)
        ],
    )
    con.commit()


def create_employees(n: int):
    cur.executemany(
        "INSERT INTO Employee VALUES (?, ?, ?) ",
        [
            (fake.unique.random_int(min=100_000_000, max=999_999_999), fake.name(), 0)
            for i in range(n)
        ],
    )
    fake.unique.clear()
    con.commit()


def create_pilots_and_crew():
    all_employees = cur.execute("SELECT AFM FROM Employee;").fetchall()
    pilots, crew = (
        all_employees[: len(all_employees) // 5],
        all_employees[len(all_employees) * 4 // 5 :],
    )
    cur.executemany(
        "INSERT INTO Pilot VALUES (?, ?);",
        [(fake.pystr(min_chars=10, max_chars=10), pilot[0]) for pilot in pilots],
    )
    cur.executemany(
        "INSERT INTO Flight_attendant VALUES (?);",
        [(crew_member[0],) for crew_member in crew],
    )
    con.commit()


def create_flights():
    fake.add_provider(
        DynamicProvider(
            provider_name="airports",
            elements=[airport[0] for airport in international_airports],
        )
    )
    for i in range(0, NUMBER_OF_FLIGHTS, 2):
        start_airport = fake.airports()
        end_airport = fake.airports()
        while start_airport == end_airport:
            end_airport = fake.airports()

        start_time = fake.date_time_between(
            start_date=datetime.now() - timedelta(days=5),
            end_date=datetime.now() + timedelta(days=DAYS),
        )
        distance = fake.random_int(min=100, max=9000)
        flight_time = distance / 800
        end_time = start_time + timedelta(hours=flight_time)

        actual_arrival_time = None if start_time > datetime.now() else start_time
        actual_departure_time = None if end_time > datetime.now() else end_time
        actual_return_arrival_time = (
            None
            if end_time + timedelta(days=2) > datetime.now()
            else end_time + timedelta(days=2)
        )
        actual_return_departure_time = (
            None
            if start_time + timedelta(days=2) > datetime.now()
            else start_time + timedelta(days=2)
        )

        cur.execute(
            "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
            (
                i,
                distance,
                fake.random_int(min=1, max=NUMBER_OF_PLANES),
                start_airport,
                end_airport,
                start_time,
                actual_departure_time,
                end_time,
                actual_arrival_time,
            ),
        )
        cur.execute(
            "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ",
            (
                i + 1,
                distance,
                fake.random_int(min=1, max=NUMBER_OF_PLANES),
                end_airport,
                start_airport,
                start_time + timedelta(days=2),
                actual_return_departure_time,
                end_time + timedelta(days=2),
                actual_return_arrival_time,
            ),
        )

    con.commit()


def create_all_flights():
    i = 0
    for airport1 in international_airports:
        for airport2 in international_airports:
            for day in range(DAYS):
                start_time = fake.date_time_between(
                    start_date=datetime.now() + timedelta(days=day),
                    end_date=datetime.now() + timedelta(days=day + 1),
                )
                distance = fake.random_int(min=100, max=9000)
                flight_time = distance / 800
                end_time = start_time + timedelta(hours=flight_time)

                actual_arrival_time = None if start_time > datetime.now() else start_time
                actual_departure_time = None if end_time > datetime.now() else end_time

                cur.execute(
                    "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    (
                        i,
                        distance,
                        fake.random_int(min=1, max=NUMBER_OF_PLANES),
                        airport1[0],
                        airport2[0],
                        start_time,
                        actual_departure_time,
                        end_time,
                        actual_arrival_time,
                    ),
                )
                i += 1


def create_mans():
    fake.add_provider(
        DynamicProvider(
            provider_name="pilot",
            elements=[
                pilot[0] for pilot in cur.execute("SELECT AFM FROM Pilot;").fetchall()
            ],
        )
    )
    fake.add_provider(
        DynamicProvider(
            provider_name="flight_attendant",
            elements=[
                flight_attendant[0]
                for flight_attendant in cur.execute(
                    "SELECT AFM FROM Flight_Attendant;"
                ).fetchall()
            ],
        )
    )

    for i in range(NUMBER_OF_FLIGHTS):
        cur.executemany(
            "INSERT INTO MANS VALUES (?, ?)",
            [(fake.unique.pilot(), i) for j in range(2)],
        )
        cur.executemany(
            "INSERT INTO MANS VALUES (?, ?)",
            [(fake.unique.flight_attendant(), i) for j in range(10)],
        )
        fake.unique.clear()
    con.commit()


def create_seats():
    for i in range(NUMBER_OF_FLIGHTS):
        price = fake.random_int(min=100, max=500)
        flight_codes_to_seats[i] = []

        for j in range(FIRST_CLASS_SEATS):
            flight_codes_to_seats[i].append(("First_Class", j, 5 * price, i))
        for j in range(BUSINESS_CLASS_SEATS):
            flight_codes_to_seats[i].append(
                ("Business_Class", j + FIRST_CLASS_SEATS, 3 * price, i)
            )
        for j in range(ECONOMY_CLASS_SEATS):
            flight_codes_to_seats[i].append(
                (
                    "Economy_Class",
                    j + FIRST_CLASS_SEATS + BUSINESS_CLASS_SEATS,
                    price,
                    i,
                )
            )
        cur.executemany(
            "INSERT INTO Seat VALUES (?, ?, ?, ?);",
            [("First_Class", j, 5 * price, i) for j in range(FIRST_CLASS_SEATS)],
        )
        cur.executemany(
            "INSERT INTO Seat VALUES (?, ?, ?, ?);",
            [
                ("Business_Class", j + FIRST_CLASS_SEATS, 3 * price, i)
                for j in range(BUSINESS_CLASS_SEATS)
            ],
        )
        cur.executemany(
            "INSERT INTO Seat VALUES (?, ?, ?, ?);",
            [
                (
                    "Economy_Class",
                    j + FIRST_CLASS_SEATS + BUSINESS_CLASS_SEATS,
                    price,
                    i,
                )
                for j in range(ECONOMY_CLASS_SEATS)
            ],
        )
    con.commit()


def create_users(n: int):
    cur.executemany(
        "INSERT INTO User VALUES (?, ?, ?, ?, ?, ?);",
        [
            (
                fake.unique.user_name(),
                bcrypt.hashpw(
                    fake.password().encode("utf-8"), salt := bcrypt.gensalt(6)
                ),
                salt,
                fake.random_int(min=0, max=100),
                fake.name(),
                None,
            )
            for i in range(n)
        ],
    )
    con.commit()


def create_purchases(n: int):
    all_usernames = [
        str(username[0])
        for username in cur.execute("SELECT Username FROM User;").fetchall()
    ]
    all_flights = cur.execute("SELECT * FROM Flight;").fetchall()
    # flight_codes_to_seats = {flight_code: cur.execute("SELECT * FROM Seat WHERE Flight_code = ?;", (flight_code,)).fetchall() for flight_code in all_flight_codes}
    purchased_seats = {}
    all_seats = cur.execute("SELECT * FROM Seat;").fetchall()
    if not n:
        n = len(all_seats) // 7
        # n=1000
    six_months_ago = datetime.now() - timedelta(days=6 * 30)

    for i in range(n):
        if i % 100 == 0:
            print(i, "/", n)
        username = np.random.choice(all_usernames)
        for j in range(1000):
            flight = all_flights[np.random.randint(0, len(all_flights))]
            flight_code = flight[0]
            available_flight_seats = [
                seat
                for seat in flight_codes_to_seats[int(flight_code)]
                if (seat[1], flight_code) not in purchased_seats
            ]
            if len(available_flight_seats) > 0:
                break
        else:
            print("Cant find empty seats!")
            con.commit()
            return
        available_seat_numbers = [seat[1] for seat in available_flight_seats]
        seats = []
        number_of_seats_to_be_purchased = np.random.randint(
            1, 5 if len(available_seat_numbers) > 5 else len(available_seat_numbers) + 1
        )
        picked_numbers = {}
        for j in range(number_of_seats_to_be_purchased):
            random_index = np.random.randint(0, len(available_seat_numbers))
            while random_index in picked_numbers:
                random_index = np.random.randint(0, len(available_seat_numbers))
            picked_numbers[random_index] = True
            seats.append(available_flight_seats[random_index])

        for seat in seats:
            purchased_seats[(seat[1], flight_code)] = True
        ticket_code = i
        credit_card_number = fake.credit_card_number()
        purchase_datetime = fake.date_time_between(
            start_date=six_months_ago,
            end_date=datetime.strptime(flight[5], "%Y-%m-%d %H:%M:%S.%f"),
        )

        cur.executemany(
            "INSERT INTO Purchases VALUES (?, ?, ?, ?, ?);",
            [
                (ticket_code, username, seat[1], flight[0], purchase_datetime)
                for seat in seats
            ],
        )
        cur.execute(
            "INSERT INTO Ticket VALUES (?, ?, ?, ?);",
            (ticket_code, seat[2], 0, credit_card_number),
        )
        cur.execute(
            "UPDATE User SET Points = Points + ? WHERE username = ?",
            (len(seats) // 10, username),
        )
    con.commit()


def create_tickets():
    # created in create_purchases
    pass


def create_cancelations(percentage: float):
    all_purchases = cur.execute(
        "SELECT * FROM Purchases WHERE Ticket_code NOT IN (SELECT Ticket_code FROM Cancels) AND Flight_code IN (SELECT Flight_code FROM Flight WHERE Scheduled_departure_datetime > datetime('now'));"
    ).fetchall()
    number_of_cancelations = int(len(all_purchases) * percentage)
    cancelled = {}

    for i in range(number_of_cancelations):
        if i % 1000 == 0:
            print(i, "/", number_of_cancelations)
        while True:
            purchase = all_purchases[np.random.randint(0, len(all_purchases))]
            if purchase[0] not in cancelled:
                break

        ticket_code = purchase[0]
        cancelled[ticket_code] = True
        username = purchase[1]
        purchase_datetime = purchase[4]
        cancel_datetime = fake.date_time_between(
            start_date=datetime.strptime(purchase_datetime, "%Y-%m-%d %H:%M:%S.%f"),
            end_date=datetime.now(),
        )

        cur.execute(
            "INSERT INTO Cancels VALUES (?, ?, ?);",
            (ticket_code, username, cancel_datetime),
        )

    con.commit()


def create_reviews(percentage: float):
    fake_crew_review_text = {
        0: "The crew was very rude and unhelpful.",
        1: "The crew was rude and unhelpful.",
        2: "The crew was okay.",
        3: "The crew was helpful and nice.",
        4: "The crew was very helpful and nice.",
    }
    fake_airplane_review_text = {
        0: "The airplane was very dirty and uncomfortable.",
        1: "The airplane was dirty and uncomfortable.",
        2: "The airplane was okay.",
        3: "The airplane was clean and comfortable.",
        4: "The airplane was very clean and comfortable.",
    }

    reviewed = {}
    all_purchases = cur.execute(
        "SELECT * FROM Purchases WHERE Ticket_code NOT IN (SELECT Ticket_code FROM Cancels) AND Flight_code IN (SELECT Flight_code FROM Flight WHERE Scheduled_departure_datetime < datetime('now'));"
    ).fetchall()
    number_of_reviews = int(len(all_purchases) * percentage)
    for i in range(number_of_reviews):
        if i % 100 == 0:
            print(i, "/", number_of_reviews)
        while True:
            purchase = all_purchases[np.random.randint(0, len(all_purchases))]
            if (purchase[1], purchase[3]) not in reviewed:
                break
        reviewed[(purchase[1], purchase[3])] = True

        user = purchase[1]
        flight_code = purchase[3]
        airplane_score = np.random.randint(0, 5)
        crew_score = np.random.randint(0, 5)
        comments = f"{fake_airplane_review_text[airplane_score]},{fake_crew_review_text[crew_score]}"
        cur.execute(
            "INSERT INTO Reviews VALUES (?, ?, ?, ?, ?);",
            (user, flight_code, airplane_score, crew_score, comments),
        )
    con.commit()


def create_referals(percentage: float):
    all_users = cur.execute("SELECT Username FROM User;").fetchall()
    number_of_referals = int(len(all_users) * percentage)
    referred = {}
    for i in range(number_of_referals):
        if i % 100 == 0:
            print(i, "/", number_of_referals)
        while True:
            user = all_users[np.random.randint(0, len(all_users))]
            if user[0] not in referred:
                break
        referred_username = user[0]
        referred[user[0]] = True
        while True:
            referrer = all_users[np.random.randint(0, len(all_users))]
            if referrer[0] not in referred:
                break
        referrer_username = referrer[0]
        cur.execute(
            "UPDATE User SET Points = Points + 10 WHERE Username = ?",
            (referrer_username,),
        )
        cur.execute(
            "UPDATE User SET Referred_by = ? WHERE Username = ?",
            (referrer_username, referred_username),
        )

    con.commit()


if __name__ == "__main__":
    if not database_is_empty():
        print("Detected existing database. Clearing...")
        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()

        # Drop each table
        for table in tables:
            cur.execute(f"DROP TABLE IF EXISTS {table[0]}")

    create_database()

    create_cities()
    create_airports()
    print("Airports and cities created")

    create_planes()

    # create_flights()
    create_all_flights()
    create_seats()
    print("Airplanes, flights and seats created")

    create_employees(NUMBER_OF_EMPLOYEES)
    create_pilots_and_crew()
    create_mans()
    print("Employees created")

    create_users(NUMBER_OF_USERS)
    print("Users created")

    create_purchases(0)
    create_tickets()

    create_cancelations(0.1)
    create_reviews(0.2)

    create_referals(0.2)

    con.close()
