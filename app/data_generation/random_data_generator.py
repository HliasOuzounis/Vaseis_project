from random_airports import international_airports, airlines
import sqlite3
from faker import Faker
from faker.providers import DynamicProvider
import bcrypt
from datetime import datetime, timedelta

NUMBER_OF_PLANES = 1_000
DAYS = 20
NUMBER_OF_FLIGHTS = NUMBER_OF_PLANES * 3 * DAYS

FIRST_CLASS_SEATS = 10
BUSINESS_CLASS_SEATS = 30
ECONOMY_CLASS_SEATS = 110

NUMBER_OF_EMPLOYEES = 10_000
NUMBER_OF_USERS = 10_000


fake = Faker()

# 90 airports from around the world (44 cities)

all_cities = {airport[2] for airport in international_airports}


con = sqlite3.connect('app/databases/big_database.db')
cur = con.cursor()


def database_is_empty():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return not cur.fetchall()


def create_database():
    for table in open('app/schema.sql').read().split(';'):
        cur.execute(table)
        con.commit()


def create_cities():
    # City table -> city_id, city_name
    cur.executemany("INSERT INTO City VALUES (?, ?);",
                    [(hash(city), city) for city in all_cities])
    con.commit()


def create_airports():
    # Airport table -> airport_id, airport_name, city_id
    cur.executemany("INSERT INTO Airport VALUES (?, ?, ?);",
                    [(airport[0], airport[1], hash(airport[2])) for airport in international_airports])
    con.commit()


def create_planes():
    fake.add_provider(DynamicProvider(
        provider_name='airlines', elements=airlines))
    cur.executemany(
        "INSERT INTO Airplane VALUES (?, ?, ?, ?, ?, ?);",
        [(i, fake.airlines(), 0, FIRST_CLASS_SEATS, BUSINESS_CLASS_SEATS, ECONOMY_CLASS_SEATS) for i in range(NUMBER_OF_PLANES)])
    con.commit()


def create_employees(n: int):
    cur.executemany(
        "INSERT INTO Employee VALUES (?, ?, ?) ",
        [(fake.unique.random_int(min=100_000_000, max=999_999_999), fake.name(), 0) for i in range(n)])
    fake.unique.clear()
    con.commit()


def create_pilots_and_crew():
    all_employees = cur.execute("SELECT AFM FROM Employee;").fetchall()
    pilots, crew = all_employees[:len(
        all_employees) // 5], all_employees[len(all_employees) * 4 // 5:]
    cur.executemany(
        "INSERT INTO Pilot VALUES (?, ?);",
        [(fake.pystr(min_chars=10, max_chars=10), pilot[0]) for pilot in pilots])
    cur.executemany(
        "INSERT INTO Flight_attendant VALUES (?);",
        [(crew_member[0],) for crew_member in crew])
    con.commit()


def create_flights():
    fake.add_provider(DynamicProvider(provider_name='airports', elements=[
                      airport[0] for airport in international_airports]))
    for i in range(0, NUMBER_OF_FLIGHTS, 2):
        start_airport = fake.airports()
        end_airport = fake.airports()
        while start_airport == end_airport:
            end_airport = fake.airports()

        start_time = fake.date_time_between(
            start_date=datetime.now() - timedelta(days=5), end_date=datetime.now() + timedelta(days=DAYS))
        distance = fake.random_int(min=100, max=9000)
        flight_time = distance / 800
        end_time = start_time + timedelta(hours=flight_time)

        cur.execute(
            "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
            (i, distance, fake.random_int(min=1, max=NUMBER_OF_PLANES),
             start_airport, end_airport, start_time, None, end_time, None))
        cur.execute(
            "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ",
            (i + 1, distance, fake.random_int(min=1, max=NUMBER_OF_PLANES),
             end_airport, start_airport, start_time + timedelta(days=2), None, end_time + timedelta(days=2), None))
    con.commit()


def create_mans():
    fake.add_provider(DynamicProvider(provider_name='pilot', elements=[
                      pilot[0] for pilot in cur.execute("SELECT AFM FROM Pilot;").fetchall()]))
    fake.add_provider(DynamicProvider(provider_name='flight_attendant', elements=[
                      flight_attendant[0] for flight_attendant in cur.execute("SELECT AFM FROM Flight_Attendant;").fetchall()]))

    for i in range(NUMBER_OF_FLIGHTS):
        cur.executemany("INSERT INTO MANS VALUES (?, ?)",
                        [(fake.unique.pilot(), i) for j in range(2)])
        cur.executemany("INSERT INTO MANS VALUES (?, ?)",
                        [(fake.unique.flight_attendant(), i) for j in range(10)])
        fake.unique.clear()
    con.commit()


def create_seats():
    for i in range(NUMBER_OF_FLIGHTS):
        price = fake.random_int(min=100, max=500)
        cur.executemany(
            "INSERT INTO Seat VALUES (?, ?, ?, ?);",
            [("First_Class", j, 5 * price, i) for j in range(FIRST_CLASS_SEATS)])
        cur.executemany(
            "INSERT INTO Seat VALUES (?, ?, ?, ?);",
            [("Business_Class", j + FIRST_CLASS_SEATS, 3 * price, i) for j in range(BUSINESS_CLASS_SEATS)])
        cur.executemany(
            "INSERT INTO Seat VALUES (?, ?, ?, ?);",
            [("Economy_Class", j + FIRST_CLASS_SEATS + BUSINESS_CLASS_SEATS, price, i) for j in range(ECONOMY_CLASS_SEATS)])
    con.commit()


def create_users(n: int):
    cur.executemany(
        "INSERT INTO User VALUES (?, ?, ?, ?, ?, ?);",
        [(fake.unique.user_name(), bcrypt.hashpw(fake.password().encode("utf-8"), salt := bcrypt.gensalt(8)),
          salt, fake.random_int(min=0, max=100), fake.name(), None) for i in range(n)])
    con.commit()

def create_purchases():
    pass

def create_tickets():
    pass

def create_cancelations(percentage: float):
    fake.add_provider(DynamicProvider(provider_name='user', elements=[
                      user[0] for user in cur.execute("SELECT username FROM User;").fetchall()]))
    for i in range(n):
        user = fake.user()
        tickets_purchased = cur.execute(
            "SELECT distinct Ticket_code FROM Purchases WHERE Username = ?;", (user,)).fetchall()
        tickets_to_cancel = tickets_purchased[:len(tickets_purchased) * percentage]
        cur.executemany(
            "INSERT INTO Cancels VALUES (?, ?, ?);",
            [(ticket[0], user, datetime.now()) for ticket in tickets_to_cancel])

def create_reviews():
    pass


if __name__ == "__main__":
    if not database_is_empty():
        print("Detected existing database. Clearing...")
        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()

        # Drop each table
        for table in tables:
            cur.execute(f"DROP TABLE IF EXISTS {table[0]}")

    create_database()

    create_cities()
    create_airports()
    print("Airports and cities created")

    create_planes()

    create_flights()
    create_seats()
    print("Airplanes, flights and seats created")

    create_employees(NUMBER_OF_EMPLOYEES)
    create_pilots_and_crew()
    create_mans()
    print("Employees created")

    create_users(NUMBER_OF_USERS)
    print("Users created")
    
    create_purchases()
    create_tickets()
    
    create_cancelations()
    create_reviews()

    con.close()
